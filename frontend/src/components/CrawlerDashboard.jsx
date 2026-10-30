import React, { useState, useEffect } from 'react';
import {
  Globe, ShieldCheck, Zap, Activity, ShieldAlert,
  RefreshCw, Play, Trash2, ExternalLink, CheckCircle2, AlertTriangle, Layers,
  Search, MapPin, Building2, Filter
} from 'lucide-react';
import {
  fetchCrawlerDashboard, fetchCrawlerCache, clearCrawlerCache, crawlPortalDirect, fetchCrawlerWhitelist
} from '../services/api';

const QUICK_PRESETS = [
  { name: '🌾 PM-KISAN (Centre)', domain: 'pmkisan.gov.in', url: 'https://pmkisan.gov.in' },
  { name: '🏥 Ayushman Bharat (Centre)', domain: 'pmjay.gov.in', url: 'https://pmjay.gov.in' },
  { name: '👩 Maharashtra: Ladki Bahin', domain: 'ladkibahin.maharashtra.gov.in', url: 'https://ladkibahin.maharashtra.gov.in' },
  { name: '🏠 Karnataka: Seva Sindhu', domain: 'sevasindhu.karnataka.gov.in', url: 'https://sevasindhu.karnataka.gov.in' },
  { name: '👧 UP: Kanya Sumangala', domain: 'kanya.up.gov.in', url: 'https://kanya.up.gov.in' },
  { name: '📋 Rajasthan: Jan Soochna', domain: 'jansoochna.rajasthan.gov.in', url: 'https://jansoochna.rajasthan.gov.in' },
  { name: '💰 WB: Lakshmir Bhandar', domain: 'lakshmirbhandar.wb.gov.in', url: 'https://lakshmirbhandar.wb.gov.in' },
  { name: '🚫 Disallowed Non-Gov', domain: 'fake-scam-site.com', url: 'https://fake-scam-site.com', isDangerous: true }
];

const ALL_STATES_AND_UTS = [
  "All India / Centre",
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
  "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Delhi (NCT)", "Jammu & Kashmir", "Ladakh", "Chandigarh", "Puducherry",
  "Andaman & Nicobar Islands", "Dadra & Nagar Haveli and Daman & Diu", "Lakshadweep"
];

export default function CrawlerDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [cacheEntries, setCacheEntries] = useState([]);
  const [targetUrl, setTargetUrl] = useState('https://pmkisan.gov.in');
  const [bypassCache, setBypassCache] = useState(false);
  const [crawling, setCrawling] = useState(false);
  const [crawlResult, setCrawlResult] = useState(null);
  const [loading, setLoading] = useState(true);

  // Whitelist Directory Filters
  const [stateFilter, setStateFilter] = useState('ALL');
  const [levelFilter, setLevelFilter] = useState('ALL');
  const [searchFilter, setSearchFilter] = useState('');

  const loadData = async () => {
    try {
      const [dash, cache] = await Promise.all([
        fetchCrawlerDashboard(),
        fetchCrawlerCache()
      ]);
      setDashboardData(dash);
      setCacheEntries(cache.entries || []);
    } catch (err) {
      console.error('Failed to load crawler dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 10000); // 10s auto refresh
    return () => clearInterval(interval);
  }, []);

  const handleRunCrawl = async (e) => {
    if (e) e.preventDefault();
    if (!targetUrl.trim()) return;

    setCrawling(true);
    setCrawlResult(null);
    try {
      const res = await crawlPortalDirect(targetUrl.trim(), bypassCache);
      setCrawlResult(res);
      await loadData();
    } catch (err) {
      setCrawlResult({
        success: false,
        url: targetUrl,
        error: err.message || 'Crawl failed',
        security_status: 'ERROR'
      });
    } finally {
      setCrawling(false);
    }
  };

  const handleClearCache = async () => {
    if (!window.confirm('Clear crawler multi-tier cache?')) return;
    try {
      await clearCrawlerCache();
      await loadData();
    } catch (err) {
      alert('Failed to clear cache: ' + err.message);
    }
  };

  const metrics = dashboardData?.metrics || {};
  const cacheStats = metrics.cache_stats || {};
  const whitelist = dashboardData?.whitelist || [];
  const whitelistStats = dashboardData?.whitelist_stats || {};
  const logs = dashboardData?.recent_logs || [];

  // Filter whitelist items
  const filteredWhitelist = whitelist.filter((item) => {
    // Level filter
    if (levelFilter !== 'ALL' && item.level !== levelFilter) {
      return false;
    }
    // State filter
    if (stateFilter !== 'ALL') {
      if (stateFilter === 'All India / Centre' && item.level !== 'Central') return false;
      if (stateFilter !== 'All India / Centre' && item.state !== stateFilter) return false;
    }
    // Search query filter
    if (searchFilter.trim()) {
      const q = searchFilter.toLowerCase();
      const match =
        (item.name && item.name.toLowerCase().includes(q)) ||
        (item.domain && item.domain.toLowerCase().includes(q)) ||
        (item.state && item.state.toLowerCase().includes(q)) ||
        (item.category && item.category.toLowerCase().includes(q));
      if (!match) return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">

      {/* 1. TOP METRICS CARDS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold uppercase text-slate-500">Government Whitelist</div>
            <div className="text-2xl font-black text-slate-900 mt-0.5">{whitelist.length} Portals</div>
            <div className="text-[11px] text-emerald-600 font-semibold mt-0.5 flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 inline" />
              <span>All 28 States, 8 UTs & Centre</span>
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
            <Globe className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold uppercase text-slate-500">Cache Acceleration</div>
            <div className="text-2xl font-black text-emerald-700 mt-0.5">{cacheStats.hit_ratio_percent || 0}%</div>
            <div className="text-[11px] text-slate-500 font-semibold mt-0.5">
              {cacheStats.saved_bandwidth_kb || 0} KB Saved | Sub-2ms
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
            <Zap className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold uppercase text-slate-500">Crawls Dispatched</div>
            <div className="text-2xl font-black text-sky-700 mt-0.5">{metrics.total_crawls || 0}</div>
            <div className="text-[11px] text-slate-500 font-semibold mt-0.5">
              {metrics.cache_hits || 0} Cached • {metrics.live_crawls || 0} Live
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center font-bold">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <div className="text-[11px] font-bold uppercase text-slate-500">Security Guard</div>
            <div className="text-2xl font-black text-red-600 mt-0.5">{metrics.security_blocked || 0}</div>
            <div className="text-[11px] text-slate-500 font-semibold mt-0.5">
              Non-Gov URLs Blocked
            </div>
          </div>
          <div className="w-10 h-10 rounded-xl bg-red-50 text-red-700 flex items-center justify-center font-bold">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* 2. CRAWLER MISSION CONTROL + TERMINAL */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT COLUMN (Cols 1-5): Manual Dispatch & Cache Manager */}
        <div className="lg:col-span-5 space-y-5">

          {/* On-Demand URL Crawler Dispatch Box */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                <Play className="w-4 h-4 text-emerald-600 fill-current" />
                <span>On-Demand Official Portal Crawler</span>
              </h3>
              <span className="text-[11px] bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-mono font-semibold">
                Strict *.gov.in Whitelist
              </span>
            </div>

            <form onSubmit={handleRunCrawl} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-slate-600 mb-1 block">
                  Target Government Portal URL
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    placeholder="e.g. https://pmkisan.gov.in or https://sevasindhu.karnataka.gov.in"
                    className="w-full text-xs font-mono px-3 py-2.5 bg-slate-50 border border-slate-300 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500 pr-10 text-slate-900"
                  />
                  <Globe className="w-4 h-4 text-slate-400 absolute right-3 top-3" />
                </div>
              </div>

              {/* Quick Presets for Demo */}
              <div>
                <div className="text-[10px] uppercase font-bold text-slate-500 mb-1.5">
                  1-Click Presets (Central & State Portals)
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {QUICK_PRESETS.map((p, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setTargetUrl(p.url)}
                      className={`text-[10px] px-2 py-1 rounded-lg border font-medium cursor-pointer transition ${
                        p.isDangerous
                          ? 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100'
                          : 'bg-slate-100 hover:bg-emerald-50 text-slate-700 hover:text-emerald-800 border-slate-200'
                      }`}
                    >
                      {p.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center space-x-2 text-xs text-slate-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={bypassCache}
                    onChange={(e) => setBypassCache(e.target.checked)}
                    className="rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                  />
                  <span>Bypass Cache (Force Fresh Live Crawl)</span>
                </label>

                <button
                  type="submit"
                  disabled={crawling}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-sm cursor-pointer disabled:cursor-not-allowed"
                >
                  {crawling ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Crawling...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Dispatch Crawl</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Cache Analytics & Management */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                <Layers className="w-4 h-4 text-emerald-600" />
                <span>Persistent SQLite Cached Pages ({cacheEntries.length})</span>
              </h3>
              <button
                onClick={handleClearCache}
                className="text-[11px] text-red-600 hover:text-red-700 font-semibold flex items-center space-x-1 cursor-pointer"
              >
                <Trash2 className="w-3 h-3" />
                <span>Flush Cache</span>
              </button>
            </div>

            <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
              {cacheEntries.length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-400">
                  Cache is empty. Crawl an official URL above or ask a query in Search to populate cache.
                </div>
              ) : (
                cacheEntries.map((e, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between">
                    <div className="truncate max-w-[240px]">
                      <div className="font-mono font-bold text-slate-800 text-[11px] truncate">{e.key}</div>
                      <div className="text-[10px] text-slate-500">
                        {e.metadata?.title || ''} • {e.size_kb} KB
                      </div>
                    </div>
                    <span className="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded">
                      Hit: {e.access_count}x
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

        {/* RIGHT COLUMN (Cols 6-12): Live Console & Crawl Result */}
        <div className="lg:col-span-7 space-y-5">

          {/* Live Terminal */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 shadow-md overflow-hidden flex flex-col">
            <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-amber-500"></div>
                <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                <span className="text-xs font-mono font-bold text-slate-300 ml-2">GovCrawler Daemon Live Activity Stream</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400">● LIVE</span>
            </div>

            <div className="p-4 font-mono text-xs text-slate-300 h-64 overflow-y-auto space-y-1.5 bg-[#0b0f19]">
              <div className="text-emerald-400 font-bold">[READY] GovCrawler Agent Daemon active. Official domain whitelist enforcement ON.</div>
              {logs.map((log, idx) => {
                let color = 'text-slate-300';
                if (log.level === 'SECURITY_BLOCK') color = 'text-red-400 font-bold';
                else if (log.level === 'CACHE_HIT') color = 'text-amber-300 font-bold';
                else if (log.level === 'SUCCESS') color = 'text-emerald-400';
                else if (log.level === 'FETCH') color = 'text-sky-300';

                const timeStr = new Date(log.timestamp * 1000).toLocaleTimeString();
                return (
                  <div key={idx}>
                    <span className="text-slate-500">[{timeStr}]</span>{' '}
                    <span className={color}>[{log.level}]</span> {log.message}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Crawl Result Box */}
          {crawlResult && (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-5 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">
                    {crawlResult.title || (crawlResult.success ? 'Official Portal Document' : 'Access Blocked')}
                  </h3>
                  <p className="text-xs font-mono text-slate-500 truncate max-w-md">{crawlResult.url}</p>
                </div>
                <div className="flex items-center space-x-2 text-xs">
                  {crawlResult.success ? (
                    <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">
                      HTTP {crawlResult.status_code || 200} OK
                    </span>
                  ) : crawlResult.status_code >= 200 && crawlResult.status_code < 300 ? (
                    <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-bold">
                      HTTP {crawlResult.status_code} · CONTENT NOT EXTRACTED
                    </span>
                  ) : (
                    <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded-full font-bold">
                      🛡️ {crawlResult.security_status || 'BLOCKED'}
                    </span>
                  )}

                  {crawlResult.cache_hit ? (
                    <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-bold">
                      ⚡ CACHED (0ms)
                    </span>
                  ) : (
                    <span className="bg-sky-100 text-sky-800 px-2 py-0.5 rounded-full font-bold">
                      🌐 LIVE CRAWL ({crawlResult.latency_ms}ms)
                    </span>
                  )}
                </div>
              </div>

              <div className="space-y-3">
                <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
                  <div className="text-[11px] font-bold uppercase text-slate-500 mb-1">
                    Extracted {crawlResult.extractor || 'portal'} content
                    {crawlResult.content_type ? ` · ${crawlResult.content_type}` : ''}
                  </div>
                  <p className="text-xs text-slate-700 leading-relaxed max-h-36 overflow-y-auto font-mono">
                    {crawlResult.extracted_text || crawlResult.error || 'No content.'}
                  </p>
                </div>

                {crawlResult.discovered_whitelisted_links && crawlResult.discovered_whitelisted_links.length > 0 && (
                  <div>
                    <div className="text-[11px] font-bold uppercase text-slate-500 mb-1.5">
                      Discovered Whitelisted Internal Links
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {crawlResult.discovered_whitelisted_links.map((link, idx) => (
                        <a
                          key={idx}
                          href={link}
                          target="_blank"
                          rel="noreferrer"
                          className="bg-slate-100 hover:bg-emerald-100 text-slate-800 hover:text-emerald-900 px-2 py-0.5 rounded border border-slate-200 text-[10px] font-mono truncate max-w-xs block"
                        >
                          🔗 {link}
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>

      </div>

      {/* 3. COMPREHENSIVE OFFICIAL SCHEMES WHITELIST DIRECTORY (CENTRE + 28 STATES + 8 UTS) */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-emerald-600" />
              <span>Registered Government & Citizen Portal Directory</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Comprehensive security whitelist protecting citizens by allowing exclusively authentic Indian National & State Government portals ({filteredWhitelist.length} of {whitelist.length} portals shown).
            </p>
          </div>

          {/* Filter Controls */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                placeholder="Search state, domain, category..."
                className="text-xs px-3 py-1.5 pl-8 bg-slate-50 border border-slate-300 rounded-lg text-slate-800 focus:outline-none focus:ring-1 focus:ring-emerald-500 w-48"
              />
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            </div>

            {/* Jurisdiction / Level Filter */}
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="text-xs px-3 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-700 focus:outline-none font-medium"
            >
              <option value="ALL">All Levels</option>
              <option value="Central">Central Govt</option>
              <option value="State">State Govt</option>
              <option value="UT">Union Territory</option>
            </select>

            {/* State Filter Dropdown */}
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="text-xs px-3 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-700 focus:outline-none font-medium max-w-[180px]"
            >
              <option value="ALL">All States & UTs (36)</option>
              {ALL_STATES_AND_UTS.map((st, idx) => (
                <option key={idx} value={st}>{st}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Portal Table */}
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="sticky top-0 bg-slate-100/95 backdrop-blur-xs border-b border-slate-200 z-10">
              <tr className="text-slate-600 uppercase font-bold text-[10px]">
                <th className="py-2.5 px-3">Portal Name</th>
                <th className="py-2.5 px-3">Jurisdiction / State</th>
                <th className="py-2.5 px-3 font-mono">Official Domain</th>
                <th className="py-2.5 px-3">Scheme Category</th>
                <th className="py-2.5 px-3 text-center">Trust Status</th>
                <th className="py-2.5 px-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {filteredWhitelist.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-8 text-xs text-slate-400">
                    No portals found matching your search and filter criteria.
                  </td>
                </tr>
              ) : (
                filteredWhitelist.map((w, idx) => {
                  let badgeColor = 'bg-blue-100 text-blue-800';
                  if (w.level === 'State') badgeColor = 'bg-emerald-100 text-emerald-800';
                  else if (w.level === 'UT') badgeColor = 'bg-purple-100 text-purple-800';

                  return (
                    <tr key={idx} className="hover:bg-slate-50 transition">
                      <td className="py-2.5 px-3 font-semibold text-slate-900">{w.name}</td>
                      <td className="py-2.5 px-3">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${badgeColor}`}>
                          {w.state}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-emerald-800 font-medium">{w.domain}</td>
                      <td className="py-2.5 px-3 text-slate-600">{w.category}</td>
                      <td className="py-2.5 px-3 text-center">
                        <span className="bg-emerald-100 text-emerald-800 font-bold text-[10px] px-2 py-0.5 rounded-full">
                          ✔ Registered Host
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-center">
                        <button
                          type="button"
                          onClick={() => {
                            setTargetUrl(`https://${w.domain}`);
                            window.scrollTo({ top: 120, behavior: 'smooth' });
                          }}
                          className="text-[10px] font-bold bg-slate-100 hover:bg-emerald-600 hover:text-white text-slate-700 px-2 py-1 rounded transition cursor-pointer"
                        >
                          Test Crawl
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
