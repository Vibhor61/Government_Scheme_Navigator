"""
Government Scheme Web Crawler Engine
Executes fast, polite HTTP requests exclusively against whitelisted official government portals.
Features:
- Strict domain guardrail enforcement
- Multi-tier cache integration (< 2ms on hit)
- Robust HTML text extraction & link filtering
- In-memory event stream for real-time dashboard monitoring
- Explicit unavailable response when an official portal cannot be reached
"""

import json
import re
import ssl
import time
from io import BytesIO
from xml.etree import ElementTree

import httpx
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from typing import Dict, Any, List, Optional

from .whitelist import is_whitelisted_domain, sanitize_gov_url
from .cache import crawler_cache
from .browser_crawler import render_registered_portal

EXTRACTOR_VERSION = 5
MAX_DISCOVERED_LINKS = 100
MAX_JSON_EXTRACTED_CHARS = 250_000
MAX_TEXT_EXTRACTED_CHARS = 12_000


def _result_extracted_text(extracted_text: str, extractor: str) -> str:
    """Preserve complete bounded JSON documents; keep representative text samples bounded."""
    if extractor == "json":
        if len(extracted_text) > MAX_JSON_EXTRACTED_CHARS:
            raise ValueError(
                f"JSON response exceeds the {MAX_JSON_EXTRACTED_CHARS}-character extraction limit."
            )
        return extracted_text
    return extracted_text[:MAX_TEXT_EXTRACTED_CHARS]


class SimpleHTMLTextExtractor(HTMLParser):
    """Extract visible HTML text and links while preserving structural spacing."""

    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    }
    BLOCK_TAGS = {
        "p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "div",
        "section", "article", "header", "footer", "blockquote", "table", "td", "th"
    }

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.text_chunks: List[str] = []
        self.links: List[str] = []
        self.link_context: List[Dict[str, str]] = []
        self.active_anchor_index: Optional[int] = None
        self.title: str = ""
        self.skip_tags = {"script", "style", "noscript", "svg", "template"}
        self.tag_stack: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID_TAGS:
            self.tag_stack.append(tag)
        if tag in self.BLOCK_TAGS:
            if self.text_chunks and not self.text_chunks[-1].endswith("\n"):
                self.text_chunks.append("\n")
        if tag == "a":
            for attr_name, attr_val in attrs:
                if attr_name == "href" and attr_val:
                    full_url = urljoin(self.base_url, attr_val.strip())
                    if urlparse(full_url).scheme in {"http", "https"}:
                        self.links.append(full_url)
                        self.link_context.append({"url": full_url, "text": ""})
                        self.active_anchor_index = len(self.link_context) - 1

    def handle_endtag(self, tag):
        if tag == "a":
            self.active_anchor_index = None
        if tag in self.BLOCK_TAGS:
            if self.text_chunks and not self.text_chunks[-1].endswith("\n"):
                self.text_chunks.append("\n")
        for index in range(len(self.tag_stack) - 1, -1, -1):
            if self.tag_stack[index] == tag:
                del self.tag_stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data):
        data_clean = data.strip()
        if not data_clean:
            return

        if "title" in self.tag_stack:
            self.title += " " + data_clean
            return

        if any(tag in self.skip_tags for tag in self.tag_stack):
            return

        self.text_chunks.append(data_clean + " ")
        if self.active_anchor_index is not None:
            link = self.link_context[self.active_anchor_index]
            link["text"] = f"{link['text']} {data_clean}".strip()

    def get_text(self) -> str:
        raw = "".join(self.text_chunks)
        cleaned = re.sub(r"\n\s*\n+", "\n\n", raw)
        return cleaned.strip()


def rank_scheme_links(
    base_url: str,
    links: List[str],
    link_context: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """
    Score and prioritize discovered hyperlinks to find scheme guidelines,
    eligibility criteria, circulars, and PDF documents for 2-hop deep crawling.
    """
    scored: List[Dict[str, Any]] = []
    seen_urls = set()
    context_map = {item.get("url"): item.get("text", "") for item in link_context if item.get("url")}
    base_domain = urlparse(base_url).hostname or ""

    exclude_keywords = [
        "login", "signin", "sign-in", "register", "signup", "sign-up",
        "tender", "tenders", "procurement", "gallery", "photo", "video",
        "contact", "contact-us", "feedback", "rti", "sitemap", "disclaimer",
        "copyright", "terms-of-use", "privacy", "web-policies", "screen-reader",
        "skip to main", "javascript:", "#", "mailto:", "tel:"
    ]

    for link in links:
        if not link or link in seen_urls:
            continue
        parsed = urlparse(link)
        if parsed.scheme.casefold() not in {"http", "https"}:
            continue
        allowed, _, _ = is_whitelisted_domain(link)
        if not allowed:
            continue

        path_and_query = (parsed.path + " " + parsed.query).casefold()
        anchor_text = context_map.get(link, "").casefold()
        combined_text = f"{path_and_query} {anchor_text}"

        # Skip exclude links unless strong guideline keyword is explicitly present
        if any(ex in combined_text for ex in exclude_keywords):
            if not any(k in combined_text for k in ["guideline", "eligib", "criteria", "norm"]):
                continue

        score = 0
        if link.casefold().endswith(".pdf"):
            score += 6
        if any(k in anchor_text for k in ["guideline", "eligib", "criteria", "norm", "rule"]):
            score += 7
        if any(k in anchor_text for k in ["about the scheme", "about scheme", "exclusion", "benefit"]):
            score += 5
        if any(k in path_and_query for k in ["guideline", "eligib", "criteria", "scheme", "detail"]):
            score += 3
        if parsed.hostname == base_domain:
            score += 1

        if score >= 3:
            seen_urls.add(link)
            scored.append({
                "url": link,
                "anchor_text": context_map.get(link, "").strip() or parsed.path.split("/")[-1],
                "score": score,
                "is_pdf": link.casefold().endswith(".pdf"),
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


class GovCrawlerEngine:
    def __init__(self, request_timeout: float = 12.0):
        self.timeout = request_timeout
        self.recent_logs: List[Dict[str, Any]] = []
        self.max_logs: int = 150
        self.active_jobs: int = 0
        self.total_crawls: int = 0
        self.security_blocks: int = 0

    @staticmethod
    def _extract_response_content(
        response: httpx.Response,
        base_url: str,
    ) -> Dict[str, Any]:
        content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
        raw_content = response.content
        title = ""
        links: List[str] = []

        if content_type == "application/pdf" or raw_content.startswith(b"%PDF-") or base_url.casefold().endswith(".pdf"):
            from pypdf import PdfReader

            reader = PdfReader(BytesIO(raw_content))
            pages_text = []
            for i, page in enumerate(reader.pages[:25]):
                page_t = (page.extract_text() or "").strip()
                if page_t:
                    pages_text.append(f"--- Page {i+1} ---\n{page_t}")
            text = "\n\n".join(pages_text).strip()
            extractor = "pdf"
            pdf_name = urlparse(base_url).path.split("/")[-1] or "circular.pdf"
            title = f"Official Circular Document ({pdf_name})"
        else:
            decoded = response.text
            if content_type in {"application/json", "text/json"} or (
                not content_type and decoded.lstrip().startswith(("{", "["))
            ):
                try:
                    text = json.dumps(json.loads(decoded), ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    text = decoded.strip()
                extractor = "json"
            elif content_type in {"application/xml", "text/xml"} or content_type.endswith("+xml"):
                try:
                    root = ElementTree.fromstring(decoded)
                    text = " ".join(part.strip() for part in root.itertext() if part.strip())
                except ElementTree.ParseError:
                    text = decoded.strip()
                extractor = "xml"
            elif content_type in {"text/html", "application/xhtml+xml"} or "<html" in decoded[:1000].casefold():
                parser = SimpleHTMLTextExtractor(base_url=base_url)
                parser.feed(decoded)
                parser.close()
                text = parser.get_text()
                title = parser.title.strip()
                links = parser.links
                extractor = "html"
            elif content_type.startswith("text/") or not content_type:
                text = re.sub(r"\s+", " ", decoded).strip()
                extractor = "text"
            else:
                raise ValueError(f"Unsupported portal content type: {content_type or 'unknown'}")

        return {
            "title": title,
            "extracted_text": text,
            "links": links,
            "link_context": parser.link_context if extractor == "html" else [],
            "content_type": content_type or "unknown",
            "extractor": extractor,
            "response_bytes": len(raw_content),
        }

    def _log_event(self, level: str, message: str, url: str = "", metadata: Optional[Dict[str, Any]] = None):
        """Append to in-memory real-time event log for visual dashboard."""
        event = {
            "timestamp": time.time(),
            "level": level,  # INFO, SUCCESS, CACHE, WARN, SECURITY_BLOCK
            "message": message,
            "url": url,
            "metadata": metadata or {}
        }
        self.recent_logs.append(event)
        if len(self.recent_logs) > self.max_logs:
            self.recent_logs.pop(0)

    def crawl_url(
        self,
        target_url: str,
        force_refresh: bool = False,
        deep_crawl: bool = True,
        max_subpages: int = 2,
    ) -> Dict[str, Any]:
        """
        Crawls an official government URL with security whitelist verification,
        SSL fallback tolerance, 2-hop deep link following, and structured text extraction.
        """
        start_time = time.time()
        target_url = sanitize_gov_url(target_url)

        # 1. Security Whitelist Check
        is_allowed, domain, reason = is_whitelisted_domain(target_url)
        if not is_allowed:
            self.security_blocks += 1
            self._log_event(
                level="SECURITY_BLOCK",
                message=f"Access blocked for unauthorized domain: {domain}. {reason}",
                url=target_url
            )
            return {
                "success": False,
                "url": target_url,
                "domain": domain,
                "error": f"Security Policy Violation: {reason}",
                "security_status": "BLOCKED",
                "cache_hit": False,
                "latency_ms": round((time.time() - start_time) * 1000, 2)
            }

        # 2. High-Speed Cache Check
        if not force_refresh:
            cached_data = crawler_cache.get(target_url)
            if cached_data and cached_data.get("extractor_version") == EXTRACTOR_VERSION:
                lat = round((time.time() - start_time) * 1000, 2)
                self._log_event(
                    level="CACHE_HIT",
                    message=f"High-speed cache hit for {domain} (0ms network overhead)",
                    url=target_url,
                    metadata={"latency_ms": lat}
                )
                cached_data["cache_hit"] = True
                cached_data["latency_ms"] = lat
                return cached_data

        # 3. Live HTTP Request
        self.active_jobs += 1
        self.total_crawls += 1
        self._log_event(
            level="FETCH",
            message=f"Dispatching live HTTP GET request to official portal: {domain}",
            url=target_url
        )

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-IN,en-US,en;q=0.9,hi;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        try:
            current_url = target_url
            res = None
            verify_ssl = True
            for attempt in range(2):
                try:
                    with httpx.Client(timeout=self.timeout, follow_redirects=False, verify=verify_ssl) as client:
                        for redirect_count in range(6):
                            res = client.get(current_url, headers=headers)
                            if not res.is_redirect:
                                break
                            redirect_location = res.headers.get("location")
                            if not redirect_location:
                                return self._generate_unavailable_portal_response(
                                    target_url,
                                    domain,
                                    res.status_code,
                                    round((time.time() - start_time) * 1000, 2),
                                    "Official portal returned a redirect without a Location header.",
                                )
                            next_url = urljoin(current_url, redirect_location)
                            current_parsed = urlparse(current_url)
                            next_parsed = urlparse(next_url)
                            if current_parsed.scheme == "https" and next_parsed.scheme != "https":
                                self.security_blocks += 1
                                self._log_event(
                                    level="SECURITY_BLOCK",
                                    message="Blocked HTTPS-to-HTTP redirect downgrade.",
                                    url=next_url,
                                )
                                return {
                                    "success": False,
                                    "url": target_url,
                                    "domain": domain,
                                    "error": "Redirect blocked because it downgrades HTTPS to HTTP.",
                                    "security_status": "BLOCKED",
                                    "cache_hit": False,
                                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                                }
                            redirect_allowed, redirect_domain, redirect_reason = is_whitelisted_domain(next_url)
                            if not redirect_allowed:
                                self.security_blocks += 1
                                self._log_event(
                                    level="SECURITY_BLOCK",
                                    message=f"Blocked redirect to unregistered host {redirect_domain}. {redirect_reason}",
                                    url=next_url,
                                )
                                return {
                                    "success": False,
                                    "url": target_url,
                                    "domain": domain,
                                    "error": f"Redirect blocked by official portal registry: {redirect_reason}",
                                    "security_status": "BLOCKED",
                                    "cache_hit": False,
                                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                                }
                            if redirect_count == 5:
                                return self._generate_unavailable_portal_response(
                                    target_url,
                                    domain,
                                    res.status_code,
                                    round((time.time() - start_time) * 1000, 2),
                                    "Official portal exceeded the maximum redirect count.",
                                )
                            current_url = next_url
                    break
                except (httpx.ConnectError, ssl.SSLError) as net_err:
                    if attempt == 0:
                        verify_ssl = False
                        self._log_event(
                            level="WARN",
                            message=f"Standard SSL verification failed for {domain} ({net_err}). Retrying with departmental SSL tolerance.",
                            url=target_url,
                        )
                    else:
                        raise


            if res is None:
                raise RuntimeError("Crawler made no HTTP request.")
            status_code = res.status_code

            if 200 <= status_code < 300:
                try:
                    content = self._extract_response_content(res, current_url)
                except Exception as error:
                    lat = round((time.time() - start_time) * 1000, 2)
                    unavailable = self._generate_unavailable_portal_response(
                        current_url,
                        redirect_domain if current_url != target_url else domain,
                        status_code,
                        lat,
                        f"Could not extract {res.headers.get('content-type', 'unknown')} response: {error}",
                    )
                    unavailable["security_status"] = "REGISTERED_PORTAL_EXTRACTION_FAILED"
                    unavailable["content_type"] = res.headers.get("content-type", "unknown")
                    unavailable["response_bytes"] = len(res.content)
                    return unavailable
                extracted_text = content["extracted_text"]
                title = content["title"] or f"Official Portal - {domain}"
                try:
                    result_text = _result_extracted_text(
                        extracted_text,
                        content["extractor"],
                    )
                except ValueError as error:
                    unavailable = self._generate_unavailable_portal_response(
                        current_url,
                        redirect_domain if current_url != target_url else domain,
                        status_code,
                        round((time.time() - start_time) * 1000, 2),
                        str(error),
                    )
                    unavailable.update({
                        "security_status": "REGISTERED_PORTAL_RESPONSE_TOO_LARGE",
                        "content_type": content["content_type"],
                        "response_bytes": content["response_bytes"],
                    })
                    return unavailable

                # Filter discovered links: only keep whitelisted internal/official links
                whitelisted_links = []
                whitelisted_link_context = []
                allowed_links = set()
                for link in content["links"]:
                    ok, _, _ = is_whitelisted_domain(link)
                    if ok and link not in whitelisted_links:
                        whitelisted_links.append(link)
                        allowed_links.add(link)
                for link in content.get("link_context", []):
                    if link["url"] in allowed_links:
                        whitelisted_link_context.append(link)

                lat = round((time.time() - start_time) * 1000, 2)
                if not extracted_text:
                    rendered = {}
                    if content["extractor"] == "html":
                        rendered = render_registered_portal(
                            current_url,
                            headers["User-Agent"],
                        )
                        if rendered.get("success"):
                            result_payload = {
                                **rendered,
                                "response_bytes": content["response_bytes"],
                                "discovered_whitelisted_links": whitelisted_links[:MAX_DISCOVERED_LINKS],
                                "discovered_link_context": whitelisted_link_context[:MAX_DISCOVERED_LINKS],
                                "extractor_version": EXTRACTOR_VERSION,
                                "cache_hit": False,
                                "latency_ms": round((time.time() - start_time) * 1000, 2),
                            }
                            crawler_cache.set(
                                url_or_key=target_url,
                                data=result_payload,
                                metadata={
                                    "title": result_payload["title"],
                                    "domain": result_payload["domain"],
                                },
                            )
                            self._log_event(
                                level="SUCCESS",
                                message=(
                                    f"Rendered registered portal {result_payload['domain']} "
                                    f"and extracted {result_payload['content_length']} chars."
                                ),
                                url=current_url,
                                metadata={
                                    "extractor": result_payload["extractor"],
                                    "latency_ms": result_payload["latency_ms"],
                                },
                            )
                            return result_payload

                        if rendered.get("security_status") == "BLOCKED":
                            rendered.update({
                                "url": current_url,
                                "domain": domain,
                                "response_bytes": content["response_bytes"],
                                "cache_hit": False,
                                "latency_ms": round((time.time() - start_time) * 1000, 2),
                            })
                            return rendered

                    message = (
                        "The portal returned a successful HTTP response, but no readable "
                        "text was extracted by either the static or browser crawler. "
                        "It may require JavaScript rendering, be image-only, or require a portal-specific adapter."
                    )
                    if rendered.get("error"):
                        message = f"{message} Browser fallback: {rendered['error']}"
                    if rendered.get("blocked_hosts"):
                        blocked_hosts = ", ".join(rendered["blocked_hosts"])
                        message = (
                            f"{message} Requests to unregistered embedded hosts were "
                            f"blocked: {blocked_hosts}."
                        )
                    self._log_event(
                        level="WARN",
                        message=message,
                        url=current_url,
                        metadata={"content_type": content["content_type"]},
                    )
                    return {
                        "success": False,
                        "url": current_url,
                        "domain": redirect_domain if current_url != target_url else domain,
                        "title": title,
                        "status_code": status_code,
                        "content_length": 0,
                        "extracted_text": "",
                        "discovered_whitelisted_links": whitelisted_links[:MAX_DISCOVERED_LINKS],
                        "discovered_link_context": whitelisted_link_context[:MAX_DISCOVERED_LINKS],
                        "content_type": content["content_type"],
                        "response_bytes": content["response_bytes"],
                        "extractor": content["extractor"],
                        "browser_status_code": rendered.get("status_code"),
                        "browser_blocked_hosts": rendered.get("blocked_hosts", []),
                        "error": message,
                        "security_status": "REGISTERED_PORTAL_CONTENT_UNREADABLE",
                        "cache_hit": False,
                        "latency_ms": lat,
                    }

                deep_crawled_subpages: List[Dict[str, Any]] = []
                if deep_crawl and whitelisted_links:
                    top_subpages = rank_scheme_links(
                        current_url,
                        whitelisted_links,
                        whitelisted_link_context,
                    )[:max_subpages]
                    if top_subpages:
                        self._log_event(
                            level="INFO",
                            message=f"Deep crawler following {len(top_subpages)} priority scheme guidelines on {domain}",
                            url=current_url,
                            metadata={"candidate_count": len(top_subpages)},
                        )
                        for sub in top_subpages:
                            sub_url = sub["url"]
                            if sub_url == current_url:
                                continue
                            try:
                                with httpx.Client(timeout=8.0, follow_redirects=True, verify=False) as sub_client:
                                    sub_res = sub_client.get(sub_url, headers=headers)
                                if sub_res and 200 <= sub_res.status_code < 300:
                                    sub_content = self._extract_response_content(sub_res, sub_url)
                                    sub_text = sub_content.get("extracted_text", "").strip()
                                    if len(sub_text) > 80:
                                        deep_crawled_subpages.append({
                                            "url": sub_url,
                                            "anchor_text": sub["anchor_text"],
                                            "title": sub_content.get("title") or sub["anchor_text"],
                                            "extractor": sub_content["extractor"],
                                            "content_length": len(sub_text),
                                            "sample": sub_text[:800],
                                        })
                                        result_text += (
                                            f"\n\n{'=' * 70}\n"
                                            f"[DEEP CRAWL EVIDENCE: {sub['anchor_text']}] ({sub_url})\n"
                                            f"{'=' * 70}\n"
                                            f"{sub_text[:12000]}\n"
                                        )
                                        self._log_event(
                                            level="SUCCESS",
                                            message=f"Deep crawl (Hop 2) fetched {sub['anchor_text']} ({sub_content['extractor']}) - {len(sub_text)} chars",
                                            url=sub_url,
                                        )
                            except Exception as sub_err:
                                self._log_event(
                                    level="WARN",
                                    message=f"Deep crawl subpage fetch skipped for {sub_url}: {sub_err}",
                                    url=sub_url,
                                )

                result_payload = {
                    "success": True,
                    "url": current_url,
                    "domain": redirect_domain if current_url != target_url else domain,
                    "title": title,
                    "status_code": status_code,
                    "content_length": len(result_text),
                    "extracted_text": result_text,
                    "discovered_whitelisted_links": whitelisted_links[:MAX_DISCOVERED_LINKS],
                    "discovered_link_context": whitelisted_link_context[:MAX_DISCOVERED_LINKS],
                    "deep_crawled_subpages": deep_crawled_subpages,
                    "content_type": content["content_type"],
                    "response_bytes": content["response_bytes"],
                    "extractor": content["extractor"],
                    "extractor_version": EXTRACTOR_VERSION,
                    "security_status": "AUTHENTIC_GOVERNMENT_PORTAL",
                    "cache_hit": False,
                    "latency_ms": lat
                }

                # Store in cache
                crawler_cache.set(
                    url_or_key=target_url,
                    data=result_payload,
                    metadata={"title": title, "domain": result_payload["domain"]}
                )

                self._log_event(
                    level="SUCCESS",
                    message=f"Successfully crawled registered portal {result_payload['domain']} [{status_code} OK] in {lat}ms. Extracted {len(extracted_text)} chars.",
                    url=target_url,
                    metadata={"status_code": status_code, "latency_ms": lat}
                )

                return result_payload
            else:
                lat = round((time.time() - start_time) * 1000, 2)
                self._log_event(
                    level="WARN",
                    message=f"Official portal returned HTTP {status_code}",
                    url=target_url
                )
                return self._generate_unavailable_portal_response(
                    target_url, domain, status_code, lat
                )

        except Exception as e:
            lat = round((time.time() - start_time) * 1000, 2)
            self._log_event(
                level="WARN",
                message=f"Live fetch exception for {domain}: {str(e)[:120]}. No verified content is available.",
                url=target_url
            )
            return self._generate_unavailable_portal_response(
                target_url, domain, 503, lat, str(e)
            )
        finally:
            self.active_jobs = max(0, self.active_jobs - 1)

    def _generate_unavailable_portal_response(
        self,
        url: str,
        domain: str,
        status_code: int,
        latency_ms: float,
        err_msg: str = "",
    ) -> Dict[str, Any]:
        """Report a failed fetch without fabricating official source content."""
        return {
            "success": False,
            "url": url,
            "domain": domain,
            "error": err_msg or f"Official portal returned HTTP {status_code}",
            "status_code": status_code,
            "content_length": 0,
            "extracted_text": "",
            "discovered_whitelisted_links": [],
            "content_type": "unknown",
            "response_bytes": 0,
            "extractor": "none",
            "security_status": "OFFICIAL_PORTAL_UNAVAILABLE",
            "cache_hit": False,
            "latency_ms": latency_ms,
            "note": "No live page or verified cached source content was available; eligibility was not assessed.",
        }

    def get_crawler_metrics(self) -> Dict[str, Any]:
        """Returns consolidated live metrics for dashboard."""
        cache_stats = crawler_cache.get_stats()
        return {
            "total_crawls_dispatched": self.total_crawls,
            "active_crawlers": self.active_jobs,
            "security_blocks_enforced": self.security_blocks,
            "cache_stats": cache_stats,
            "recent_event_count": len(self.recent_logs)
        }

# Global crawler instance
gov_crawler = GovCrawlerEngine()
