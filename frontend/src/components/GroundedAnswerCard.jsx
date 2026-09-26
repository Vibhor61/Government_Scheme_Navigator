import React, { useState } from 'react';
import { 
  CheckCircle2, AlertCircle, ExternalLink, ShieldAlert, Sparkles, 
  Clock, FileText, ChevronDown, ChevronUp, Layers, Check 
} from 'lucide-react';

export default function GroundedAnswerCard({ result, loading }) {
  const [showChunks, setShowChunks] = useState(false);
  const [showClaims, setShowClaims] = useState(false);

  if (loading) {
    return (
      <div className="bg-white rounded-2xl p-8 border border-slate-200 shadow-sm animate-pulse space-y-4">
        <div className="flex items-center space-x-3">
          <div className="w-6 h-6 bg-emerald-200 rounded-full"></div>
          <div className="h-5 bg-slate-200 rounded w-1/3"></div>
        </div>
        <div className="space-y-2.5 pt-2">
          <div className="h-4 bg-slate-200 rounded w-full"></div>
          <div className="h-4 bg-slate-200 rounded w-5/6"></div>
          <div className="h-4 bg-slate-200 rounded w-4/6"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4">
          <div className="h-24 bg-slate-100 rounded-xl"></div>
          <div className="h-24 bg-slate-100 rounded-xl"></div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  const {
    query,
    answer,
    key_takeaways = [],
    eligibility_assessment = [],
    citations = [],
    retrieved_chunks = [],
    faithfulness_score = 1.0,
    relevancy_score = 1.0,
    claims_breakdown = [],
    latency_ms = 0
  } = result;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all">
      {/* Top Banner with RAG Metrics */}
      <div className="bg-slate-900 text-white px-6 py-4 flex flex-wrap items-center justify-between gap-4 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <span className="font-semibold text-base tracking-wide">Grounded Response Generated</span>
        </div>
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-1.5 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="text-slate-400">Faithfulness:</span>
            <span className={`font-bold ${faithfulness_score >= 0.8 ? 'text-emerald-400' : 'text-amber-400'}`}>
              {(faithfulness_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <span className="text-slate-400">Relevancy:</span>
            <span className={`font-bold ${relevancy_score >= 0.8 ? 'text-emerald-400' : 'text-sky-400'}`}>
              {(relevancy_score * 100).toFixed(0)}%
            </span>
          </div>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>{latency_ms} ms</span>
          </div>
        </div>
      </div>

      <div className="p-6 sm:p-8 space-y-6">
        {/* Key Takeaway Highlights */}
        {key_takeaways.length > 0 && (
          <div className="bg-emerald-50/80 border border-emerald-200/80 rounded-xl p-4.5 space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Key Eligibility Summary</span>
            </h4>
            <div className="space-y-2 text-base text-emerald-950 font-medium leading-relaxed">
              {key_takeaways.map((takeaway, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-emerald-500 font-bold">•</span>
                  <span>{takeaway}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Structured Grounded Markdown Content */}
        <div className="prose prose-slate max-w-none text-slate-800 text-base leading-relaxed space-y-4">
          {answer.split('\n\n').map((paragraph, pIdx) => {
            if (paragraph.startsWith('### ')) {
              return (
                <h3 key={pIdx} className="text-base font-bold text-slate-900 mt-5 mb-2 border-b border-slate-100 pb-1">
                  {paragraph.replace('### ', '')}
                </h3>
              );
            }
            if (paragraph.startsWith('• ') || paragraph.startsWith('- ')) {
              const bullets = paragraph.split('\n');
              return (
                <ul key={pIdx} className="space-y-1.5 my-2">
                  {bullets.map((b, bIdx) => (
                    <li key={bIdx} className="flex items-start space-x-2 text-sm text-slate-700">
                      <span className="text-emerald-500 mt-1">✔</span>
                      <span>{b.replace(/^[•\-*]\s*/, '')}</span>
                    </li>
                  ))}
                </ul>
              );
            }
            return (
              <p key={pIdx} className="text-base sm:text-lg text-slate-700 leading-relaxed">
                {paragraph}
              </p>
            );
          })}
        </div>

        {/* Official Sources & Citations */}
        {citations.length > 0 && (
          <div className="pt-4 border-t border-slate-100">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-slate-400" />
              <span>Official Sourced Documents</span>
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {citations.map((cite, idx) => (
                <div 
                  key={idx} 
                  className="bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl p-3.5 transition flex items-center justify-between"
                >
                  <div className="pr-2">
                    <p className="font-semibold text-xs text-slate-900 line-clamp-1">{cite.title}</p>
                    <p className="text-[11px] text-slate-500 line-clamp-1">{cite.ministry}</p>
                  </div>
                  {cite.official_portal && (
                    <a
                      href={cite.official_portal}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium text-emerald-600 hover:text-emerald-700 flex items-center space-x-1 shrink-0 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200 shadow-2xs"
                    >
                      <span>Apply / Portal</span>
                      <ExternalLink className="w-3 h-3 ml-0.5" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Claim Verification Breakdown Toggle */}
        <div className="pt-2 border-t border-slate-100 space-y-3">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowClaims(!showClaims)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center space-x-1.5 transition"
            >
              <ShieldAlert className="w-4 h-4 text-emerald-600" />
              <span>RAGAS Fact Grounding & Claims Breakdown ({claims_breakdown.length} Claims)</span>
              {showClaims ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            <button
              onClick={() => setShowChunks(!showChunks)}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center space-x-1.5 transition"
            >
              <Layers className="w-4 h-4 text-blue-600" />
              <span>Retrieved Chunks & RRF Ranks ({retrieved_chunks.length})</span>
              {showChunks ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          </div>

          {/* Claims View */}
          {showClaims && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2.5">
              <p className="text-xs text-slate-500 font-medium">
                Each propositional statement in the generated answer is checked against official retrieved chunks for fact verification.
              </p>
              <div className="space-y-2 pt-1">
                {claims_breakdown.map((item, idx) => (
                  <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200/80 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800">Claim #{idx+1}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.is_grounded ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {item.is_grounded ? 'Grounded in Source' : 'Unverified'}
                      </span>
                    </div>
                    <p className="text-slate-700 italic">"{item.claim}"</p>
                    {item.evidence_snippet && (
                      <p className="text-[11px] text-slate-500 pt-1 border-t border-slate-100">
                        <strong className="text-slate-600">Source Evidence:</strong> {item.evidence_snippet}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Retrieved Chunks View */}
          {showChunks && (
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-3">
              <p className="text-xs text-slate-500 font-medium">
                Hybrid Retrieval outputs: Ranked by Reciprocal Rank Fusion (RRF = 0.4 / (60 + LexRank) + 0.6 / (60 + DenseRank)).
              </p>
              <div className="space-y-2.5">
                {retrieved_chunks.map((chunk, idx) => (
                  <div key={idx} className="bg-white p-3.5 rounded-lg border border-slate-200 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-900">{chunk.chunk_title}</span>
                      <div className="flex space-x-2 text-[10px]">
                        <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded font-mono">Lex: {chunk.lexical_score}</span>
                        <span className="bg-purple-50 text-purple-700 px-1.5 py-0.5 rounded font-mono">Dense: {chunk.dense_score}</span>
                        <span className="bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded font-bold font-mono">RRF: {chunk.rrf_score}</span>
                      </div>
                    </div>
                    <p className="text-slate-600 leading-relaxed">{chunk.content}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
