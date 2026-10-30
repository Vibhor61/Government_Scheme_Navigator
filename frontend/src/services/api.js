const API_BASE = '/api';

// =========================================================================
// AUTONOMOUS CRAWLER AGENT API CLIENT
// =========================================================================

export async function queryCrawlerAgent(query, force_live_crawl = false, user_clarification = null, conversation_history = null, user_profile = null) {
  const response = await fetch(`${API_BASE}/agent/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, force_live_crawl, user_clarification, conversation_history, user_profile }),
  });
  if (!response.ok) {
    throw new Error(`Agent query failed: ${response.statusText}`);
  }
  return response.json();
}

export async function checkEligibility(profile) {
  const response = await fetch(`${API_BASE}/eligibility/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profile),
  });
  if (!response.ok) {
    throw new Error(`Eligibility check failed: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchSchemesCatalog() {
  const response = await fetch(`${API_BASE}/schemes/catalog`);
  if (!response.ok) {
    throw new Error(`Failed to fetch scheme catalog: ${response.statusText}`);
  }
  return response.json();
}

export async function crawlPortalDirect(url, force_refresh = false) {
  const response = await fetch(`${API_BASE}/crawler/crawl`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, force_refresh }),
  });
  if (!response.ok) {
    throw new Error(`Crawler request failed: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCrawlerDashboard() {
  const response = await fetch(`${API_BASE}/crawler/dashboard`);
  if (!response.ok) {
    throw new Error(`Failed to fetch crawler dashboard: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCrawlerCache() {
  const response = await fetch(`${API_BASE}/crawler/cache`);
  if (!response.ok) {
    throw new Error(`Failed to fetch crawler cache: ${response.statusText}`);
  }
  return response.json();
}

export async function clearCrawlerCache() {
  const response = await fetch(`${API_BASE}/crawler/cache/clear`, {
    method: 'POST'
  });
  if (!response.ok) {
    throw new Error(`Failed to clear crawler cache: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCrawlerWhitelist(params = {}) {
  const query = new URLSearchParams();
  if (params.jurisdiction) query.append('jurisdiction', params.jurisdiction);
  if (params.state) query.append('state', params.state);
  if (params.category) query.append('category', params.category);
  const qs = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(`${API_BASE}/crawler/whitelist${qs}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch whitelist: ${response.statusText}`);
  }
  return response.json();
}

// =========================================================================
// SCHEME DIRECTORY & SYSTEM STATS
// =========================================================================


export async function fetchSystemStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }
  return response.json();
}
