const API_BASE = '/api';

export async function askQuestion(query, category = null, evaluate = true) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, category, evaluate }),
  });
  if (!response.ok) {
    throw new Error(`Failed to query assistant: ${response.statusText}`);
  }
  return response.json();
}

export async function searchSchemes(query, category = null, top_k = 5) {
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, category, top_k }),
  });
  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchAllSchemes(category = null, search = '') {
  const params = new URLSearchParams();
  if (category && category !== 'All') params.append('category', category);
  if (search) params.append('search', search);

  const response = await fetch(`${API_BASE}/schemes?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch schemes: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchSystemStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }
  return response.json();
}

export async function runEvaluationBenchmark() {
  const response = await fetch(`${API_BASE}/evaluate/benchmark`);
  if (!response.ok) {
    throw new Error(`Failed to run benchmark: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchEvaluationHistory() {
  const response = await fetch(`${API_BASE}/evaluation/history`);
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }
  return response.json();
}
