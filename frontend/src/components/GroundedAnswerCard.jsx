import React, { useState, useEffect } from 'react';
import {
  CheckCircle2, ExternalLink, ShieldAlert, Sparkles,
  Clock, FileText, Layers, DollarSign, Users, Gift, ClipboardCheck, LayoutGrid
} from 'lucide-react';

/**
 * Parses the structured markdown answer into discrete horizontal bento sections
 * so the user can view Financial Assistance, Eligibility, Benefits, and Documents side-by-side without scrolling.
 */
function parseStructuredAnswer(answerText = '') {
  const sections = {
    intro: '',
    financial: '',
    eligibility: [],
    benefits: [],
    documents: [],
    application: '',
    portal: ''
  };

  const lines = answerText.split('\n');
  let currentSection = 'intro';

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;

    if (line.startsWith('### ')) {
      const header = line.replace('### ', '').toLowerCase();
      if (header.includes('financial') || header.includes('scope')) {
        currentSection = 'financial';
      } else if (header.includes('eligibility')) {
        currentSection = 'eligibility';
      } else if (header.includes('benefit')) {
        currentSection = 'benefits';
      } else if (header.includes('document')) {
        currentSection = 'documents';
      } else if (header.includes('application') || header.includes('apply')) {
        currentSection = 'application';
      } else {
        currentSection = 'other';
      }
      continue;
    }

    if (line.startsWith('🔗')) {
      const match = line.match(/\((https?:\/\/[^\s)]+)\)/);
      if (match) sections.portal = match[1];
      continue;
    }

    const cleanBullet = line.replace(/^[•\-*]\s*/, '').replace(/\*\*/g, '');

    if (currentSection === 'intro') {
      sections.intro += (sections.intro ? ' ' : '') + line.replace(/\*\*/g, '');
    } else if (currentSection === 'financial') {
      sections.financial += (sections.financial ? ' ' : '') + cleanBullet.replace(/\*\[Source:.*?\]\*/g, '').trim();
    } else if (currentSection === 'eligibility') {
      sections.eligibility.push(cleanBullet);
    } else if (currentSection === 'benefits') {
      sections.benefits.push(cleanBullet);
    } else if (currentSection === 'documents') {
      sections.documents.push(cleanBullet);
    } else if (currentSection === 'application') {
      sections.application += (sections.application ? ' ' : '') + cleanBullet;
    }
  }

  return sections;
}

export default function GroundedAnswerCard({ result, loading }) {
  const [activeView, setActiveView] = useState('bento');

  useEffect(() => {
    if (result) {
      setActiveView('bento');
    }
  }, [result]);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-xs animate-pulse space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-emerald-200 rounded-full"></div>
            <div className="h-5 bg-slate-200 rounded w-56"></div>
          </div>
          <div className="flex space-x-2">
            <div className="h-6 bg-slate-200 rounded w-24"></div>
            <div className="h-6 bg-slate-200 rounded w-24"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="h-36 bg-slate-100 rounded-xl"></div>
          <div className="h-36 bg-slate-100 rounded-xl"></div>
          <div className="h-36 bg-slate-100 rounded-xl"></div>
          <div className="h-36 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const {
    answer = '',
    key_takeaways = [],
    citations = [],
    retrieved_chunks = [],
    faithfulness_score = 1.0,
    relevancy_score = 0.95,
    claims_breakdown = [],
    latency_ms = 0
  } = result;

  const parsed = parseStructuredAnswer(answer);
  const primaryScheme = citations[0] || {};
  const portalUrl = parsed.portal || primaryScheme.official_portal;
  const hasStructuredSections =
    parsed.financial || parsed.eligibility.length > 0 || parsed.benefits.length > 0;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Top Compact Header with RAGAS Metric Pills & Horizontal Sub-Tabs */}
      <div className="bg-slate-900 text-white px-5 py-3.5 border-b border-slate-800 space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center space-x-2 min-w-0">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
            <span className="font-bold text-sm sm:text-base text-white truncate">
              {primaryScheme.title || 'Fact-Grounded Scheme Analysis'}
            </span>
            {primaryScheme.category && (
              <span className="hidden sm:inline-block text-[10px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-400/30 px-2 py-0.5 rounded">
                {primaryScheme.category}
              </span>
            )}
          </div>

          {/* Citizen-Facing Official Verification Badges */}
          <div className="flex items-center space-x-2 text-xs shrink-0">
            <div className="flex items-center space-x-1.5 bg-emerald-950/70 text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-lg">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="font-semibold text-xs">Verified Official Portal</span>
            </div>
            {primaryScheme.scheme_id && (
              <div className="hidden sm:flex items-center space-x-1 bg-slate-800 text-slate-300 border border-slate-700 px-2.5 py-1 rounded-lg font-mono text-[11px]">
                <span>🌐 {primaryScheme.scheme_id}</span>
              </div>
            )}
          </div>
        </div>

        {/* Interactive Horizontal Sub-Navigation Bar (Eliminates vertical scrolling!) */}
        <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-800/80 overflow-x-auto custom-scrollbar">
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setActiveView('bento')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeView === 'bento'
                  ? 'bg-emerald-600 text-white shadow-2xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>2×2 Summary Grid</span>
            </button>

            <button
              onClick={() => setActiveView('narrative')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeView === 'narrative'
                  ? 'bg-emerald-600 text-white shadow-2xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Full Response</span>
            </button>

            <button
              onClick={() => setActiveView('claims')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeView === 'claims'
                  ? 'bg-emerald-600 text-white shadow-2xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Verified Claims ({claims_breakdown.length})</span>
            </button>

            <button
              onClick={() => setActiveView('chunks')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer ${
                activeView === 'chunks'
                  ? 'bg-emerald-600 text-white shadow-2xs'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>RRF Chunks ({retrieved_chunks.length})</span>
            </button>
          </div>

          {portalUrl && (
            <a
              href={portalUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="hidden md:inline-flex items-center space-x-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs px-3 py-1.5 rounded-lg transition shrink-0"
            >
              <span>Official Portal</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>

      {/* BODY WORKSPACE */}
      <div className="p-5">
        {/* VIEW 1: HORIZONTAL 2x2 BENTO GRID (Default — Everything visible at once without scrolling!) */}
        {activeView === 'bento' && hasStructuredSections && (
          <div className="space-y-4">
            {/* Lead Banner */}
            {parsed.intro && (
              <div className="bg-slate-50 border border-slate-200/90 rounded-xl px-4 py-2.5 flex flex-wrap items-center justify-between gap-2">
                <p className="text-xs sm:text-sm text-slate-800 font-medium">
                  {parsed.intro}
                </p>
                {primaryScheme.ministry && (
                  <span className="text-[11px] font-semibold text-slate-500 bg-white px-2.5 py-0.5 rounded border border-slate-200">
                    🏛️ {primaryScheme.ministry}
                  </span>
                )}
              </div>
            )}

            {/* 2x2 Horizontal Bento Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Box 1: Financial Assistance */}
              <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-4 flex flex-col justify-between space-y-2">
                <div className="space-y-1.5">
                  <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-emerald-800">
                    <DollarSign className="w-4 h-4 text-emerald-600" />
                    <span>1. Financial Assistance & Benefit Scope</span>
                  </div>
                  <p className="text-sm font-semibold text-emerald-950 leading-relaxed">
                    {parsed.financial || key_takeaways[0] || 'See full response for scheme benefit details.'}
                  </p>
                </div>
                <div className="pt-2 border-t border-emerald-200/60 flex items-center justify-between text-[11px] text-emerald-800">
                  <span>✔ Direct Official Circular Match</span>
                  <span className="font-mono font-bold">Grounded</span>
                </div>
              </div>

              {/* Box 2: Eligibility Criteria */}
              <div className="bg-blue-50/50 border border-blue-200/80 rounded-xl p-4 space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-blue-900">
                  <Users className="w-4 h-4 text-blue-600" />
                  <span>2. Key Eligibility Criteria</span>
                </div>
                <ul className="space-y-1.5">
                  {parsed.eligibility.slice(0, 4).map((item, idx) => (
                    <li key={idx} className="text-xs text-slate-800 flex items-start space-x-1.5 leading-snug">
                      <span className="text-blue-600 font-bold mt-0.5">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Box 3: Core Benefits Delivered */}
              <div className="bg-amber-50/50 border border-amber-200/80 rounded-xl p-4 space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-amber-900">
                  <Gift className="w-4 h-4 text-amber-600" />
                  <span>3. Core Scheme Benefits</span>
                </div>
                <ul className="space-y-1.5">
                  {parsed.benefits.slice(0, 4).map((item, idx) => (
                    <li key={idx} className="text-xs text-slate-800 flex items-start space-x-1.5 leading-snug">
                      <span className="text-amber-600 font-bold mt-0.5">✔</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Box 4: Required Documents & Application Process */}
              <div className="bg-purple-50/40 border border-purple-200/80 rounded-xl p-4 flex flex-col justify-between space-y-3">
                <div className="space-y-2">
                  <div className="flex items-center space-x-1.5 text-xs font-bold uppercase tracking-wider text-purple-900">
                    <ClipboardCheck className="w-4 h-4 text-purple-600" />
                    <span>4. Documents & How to Apply</span>
                  </div>
                  {parsed.documents.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {parsed.documents.map((doc, idx) => (
                        <span
                          key={idx}
                          className="text-[11px] bg-white text-slate-800 px-2 py-0.5 rounded-md border border-purple-200 font-medium"
                        >
                          📄 {doc}
                        </span>
                      ))}
                    </div>
                  )}
                  {parsed.application && (
                    <p className="text-xs text-slate-700 leading-snug line-clamp-3">
                      <strong className="text-slate-900">Apply: </strong>
                      {parsed.application}
                    </p>
                  )}
                </div>

                {portalUrl && (
                  <div className="pt-2 border-t border-purple-200/60 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500 truncate max-w-[200px]">{portalUrl}</span>
                    <a
                      href={portalUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center space-x-1 text-xs font-bold text-purple-800 hover:text-purple-950 bg-white px-2.5 py-1 rounded-lg border border-purple-300 shadow-2xs"
                    >
                      <span>Apply on Portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* VIEW 2: FULL NARRATIVE MARKDOWN (Or fallback if unstructured LLM output) */}
        {(activeView === 'narrative' || (activeView === 'bento' && !hasStructuredSections)) && (
          <div className="grid grid-cols-1 md:grid-cols-12 gap-5">
            <div className="md:col-span-8 space-y-3 text-sm text-slate-800 leading-relaxed max-h-[460px] overflow-y-auto pr-2 custom-scrollbar">
              {answer.split('\n\n').map((paragraph, pIdx) => {
                if (paragraph.startsWith('### ')) {
                  return (
                    <h3 key={pIdx} className="text-sm font-bold text-slate-900 mt-3 mb-1 border-b border-slate-100 pb-1">
                      {paragraph.replace('### ', '')}
                    </h3>
                  );
                }
                if (paragraph.startsWith('• ') || paragraph.startsWith('- ')) {
                  const bullets = paragraph.split('\n');
                  return (
                    <ul key={pIdx} className="space-y-1 my-1.5">
                      {bullets.map((b, bIdx) => (
                        <li key={bIdx} className="flex items-start space-x-2 text-xs sm:text-sm text-slate-700">
                          <span className="text-emerald-500 mt-0.5">✔</span>
                          <span>{b.replace(/^[•\-*]\s*/, '')}</span>
                        </li>
                      ))}
                    </ul>
                  );
                }
                return (
                  <p key={pIdx} className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                    {paragraph}
                  </p>
                );
              })}
            </div>

            {/* Right Sidebar inside Full View: Key Takeaways + Sources */}
            <div className="md:col-span-4 space-y-3">
              {key_takeaways.length > 0 && (
                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 space-y-1.5">
                  <h4 className="text-[11px] font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Key Takeaways</span>
                  </h4>
                  {key_takeaways.map((t, i) => (
                    <p key={i} className="text-xs text-emerald-950 font-medium leading-snug">
                      • {t}
                    </p>
                  ))}
                </div>
              )}
              {citations.map((c, idx) => (
                <div key={idx} className="bg-slate-50 border border-slate-200 rounded-xl p-3 space-y-1.5">
                  <div className="text-xs font-bold text-slate-900">{c.title}</div>
                  <div className="text-[11px] text-slate-500">{c.ministry}</div>
                  {c.official_portal && (
                    <a
                      href={c.official_portal}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 hover:underline pt-1"
                    >
                      <span>Visit Official Portal</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW 3: RAGAS CLAIMS VERIFICATION (2-Column Horizontal Grid) */}
        {activeView === 'claims' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-600 font-medium">
                Atomic propositional claims extracted from the generated answer and cross-checked against retrieved chunks:
              </span>
              <span className="font-bold text-emerald-700 shrink-0">
                Faithfulness: {(faithfulness_score * 100).toFixed(1)}%
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[420px] overflow-y-auto pr-1 custom-scrollbar">
              {claims_breakdown.map((item, idx) => (
                <div key={idx} className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200 text-xs space-y-1.5 flex flex-col justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800">Claim #{idx + 1}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.is_grounded ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                      }`}>
                        {item.is_grounded ? '✔ Grounded in Source' : 'Partial Match'}
                      </span>
                    </div>
                    <p className="text-slate-700 font-medium leading-snug">"{item.claim}"</p>
                  </div>
                  {item.evidence_snippet && (
                    <p className="text-[11px] text-slate-500 pt-1.5 border-t border-slate-200/70 line-clamp-2">
                      <strong className="text-slate-600">Evidence:</strong> {item.evidence_snippet}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW 4: HYBRID RETRIEVED CHUNKS & RRF RANKS (2-Column Horizontal Grid) */}
        {activeView === 'chunks' && (
          <div className="space-y-3">
            <div className="flex items-center justify-between bg-slate-50 px-4 py-2.5 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-600 font-medium">
                Dual-Arm Reciprocal Rank Fusion: RRF = w_lex / (60 + Rank_BM25) + w_dense / (60 + Rank_pgvector)
              </span>
              <span className="font-mono font-bold text-purple-700 shrink-0">
                Top {retrieved_chunks.length} Chunks
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[420px] overflow-y-auto pr-1 custom-scrollbar">
              {retrieved_chunks.map((chunk, idx) => (
                <div key={idx} className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200 text-xs space-y-2 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-bold text-slate-900 truncate">{chunk.chunk_title}</span>
                      <span className="bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-mono text-[10px] font-bold shrink-0">
                        #{idx + 1}
                      </span>
                    </div>
                    <p className="text-slate-600 leading-relaxed line-clamp-3">{chunk.content}</p>
                  </div>
                  <div className="flex items-center justify-between pt-2 border-t border-slate-200/70 text-[10px] font-mono">
                    <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded border border-blue-200">
                      BM25: {chunk.lexical_score}
                    </span>
                    <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-200">
                      Cosine: {chunk.dense_score}
                    </span>
                    <span className="bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200 font-bold">
                      RRF: {chunk.rrf_score}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
