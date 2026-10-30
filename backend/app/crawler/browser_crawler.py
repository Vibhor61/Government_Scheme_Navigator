"""JavaScript-rendered fallback for registered portal pages."""

from threading import BoundedSemaphore
from typing import Any, Dict, List
from urllib.parse import urlparse

from .whitelist import is_whitelisted_domain

_BROWSER_SLOT = BoundedSemaphore(1)
MAX_DISCOVERED_LINKS = 100

ALLOWED_CDNS = {
    "cdnjs.cloudflare.com",
    "cdn.jsdelivr.net",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "ajax.googleapis.com",
    "code.jquery.com",
    "unpkg.com",
    "maxcdn.bootstrapcdn.com",
    "stackpath.bootstrapcdn.com",
}


def is_allowed_browser_request(url: str) -> bool:
    """Allow browser navigation only to authentic HTTPS government portals."""
    allowed, _, _ = is_whitelisted_domain(url)
    return allowed and urlparse(url).scheme.casefold() == "https"


def is_allowed_browser_asset_request(url: str) -> bool:
    """Allow static assets (CSS, JS bundles, fonts) from government domains or reputable CDNs."""
    parsed = urlparse(url)
    scheme = parsed.scheme.casefold()
    if scheme in {"about", "blob", "data", "chrome-error"}:
        return True
    if scheme not in {"http", "https"}:
        return False
    host = (parsed.hostname or "").casefold().rstrip(".")
    if not host:
        return False
    if host.endswith(".gov.in") or host.endswith(".nic.in") or host in {"gov.in", "nic.in"}:
        return True
    if host in ALLOWED_CDNS or any(host.endswith("." + cdn) for cdn in ALLOWED_CDNS):
        return True
    return False


def render_registered_portal(
    url: str,
    user_agent: str,
    timeout_ms: int = 15000,
) -> Dict[str, Any]:
    """Render a government portal with headless Chromium, allowing SPA script execution."""
    allowed, domain, reason = is_whitelisted_domain(url)
    if not is_allowed_browser_request(url):
        return {
            "success": False,
            "error": reason if not allowed else "Browser rendering requires HTTPS.",
            "security_status": "BLOCKED",
            "blocked_hosts": [],
        }

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "success": False,
            "error": "Playwright is not installed in this environment; falling back to direct HTTP extraction.",
            "security_status": "SKIPPED",
            "blocked_hosts": [],
        }

    blocked_hosts: List[str] = []

    def guard_request(route) -> None:
        request_url = route.request.url
        if is_allowed_browser_asset_request(request_url):
            route.continue_()
            return

        request_domain = urlparse(request_url).hostname or "unknown"
        blocked_hosts.append(request_domain)
        route.abort()

    try:
        with _BROWSER_SLOT:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                try:
                    context = browser.new_context(
                        user_agent=user_agent,
                        service_workers="block",
                    )
                    page = context.new_page()
                    page.route("**/*", guard_request)
                    response = page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=timeout_ms,
                    )
                    try:
                        page.wait_for_load_state("networkidle", timeout=3000)
                    except Exception:
                        pass
                    page.wait_for_timeout(1000)
                    status_code = response.status if response else None
                    content_type = (
                        response.headers.get("content-type", "unknown")
                        if response
                        else "unknown"
                    )

                    try:
                        extracted_text = page.locator("body").inner_text(timeout=4000).strip()
                    except Exception:
                        extracted_text = ""

                    if len(extracted_text) < 150:
                        try:
                            page.wait_for_timeout(1500)
                            page.evaluate("window.scrollBy(0, 400)")
                            refreshed_text = page.locator("body").inner_text(timeout=3000).strip()
                            if refreshed_text:
                                extracted_text = refreshed_text
                        except Exception:
                            pass

                    title = page.title().strip()
                    links = page.locator("a[href]").evaluate_all(
                        "elements => elements.map(element => ({url: element.href, text: (element.innerText || element.textContent || '').trim()}))"
                    )
                    registered_links = []
                    registered_link_context = []
                    for link in links:
                        link_url = link.get("url", "")
                        link_allowed, _, _ = is_whitelisted_domain(link_url)
                        if link_allowed and link_url not in registered_links:
                            registered_links.append(link_url)
                            registered_link_context.append({
                                "url": link_url,
                                "text": str(link.get("text", ""))[:500],
                            })

                    successful_status = status_code is None or 200 <= status_code < 300
                    error = None
                    if not successful_status:
                        error = f"Browser rendering received HTTP {status_code}."
                    elif not extracted_text:
                        error = "Browser rendering completed, but the page contains no visible text."

                    return {
                        "success": bool(extracted_text) and successful_status,
                        "url": page.url,
                        "domain": urlparse(page.url).hostname or domain,
                        "title": title,
                        "status_code": status_code,
                        "content_type": content_type,
                        "extracted_text": extracted_text[:12000],
                        "content_length": len(extracted_text),
                        "discovered_whitelisted_links": registered_links[:MAX_DISCOVERED_LINKS],
                        "discovered_link_context": registered_link_context[:MAX_DISCOVERED_LINKS],
                        "error": error,
                        "security_status": (
                            "REGISTERED_OFFICIAL_PORTAL"
                            if extracted_text and successful_status
                            else "REGISTERED_PORTAL_CONTENT_UNREADABLE"
                        ),
                        "blocked_hosts": sorted(set(blocked_hosts)),
                        "extractor": "playwright_html",
                        "rendered": True,
                    }
                finally:
                    browser.close()
    except PlaywrightError as error:
        return {
            "success": False,
            "error": f"Browser rendering failed: {error}",
            "security_status": "REGISTERED_PORTAL_RENDER_FAILED",
            "blocked_hosts": sorted(set(blocked_hosts)),
            "extractor": "playwright_html",
        }
