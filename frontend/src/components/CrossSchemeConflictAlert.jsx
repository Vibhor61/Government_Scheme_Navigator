import React from 'react';
import {
  AlertTriangle,
  Scale,
  CheckCircle2,
  XCircle,
  ExternalLink,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

export default function CrossSchemeConflictAlert({
  conflict,
  onSelectOption,
  query = '',
  isHindi = false
}) {
  if (!conflict) return null;

  const {
    title,
    discrepancy_field,
    explanation,
    source_a,
    source_b,
    scheme_a,
    scheme_b,
    recommendation,
    clarification_prompt,
    options = []
  } = conflict;

  return (
    <div className="relative overflow-hidden rounded-2xl border-2 border-amber-300 dark:border-amber-700/60 bg-amber-50/95 dark:bg-[#1C160B]/90 p-5 shadow-xs space-y-4 animate-fadeIn">
      {/* Header Badge */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-amber-200/80 dark:border-amber-800/40 pb-2.5">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-md bg-amber-600 px-2 py-0.5 text-[10px] font-black uppercase tracking-wider text-white">
            <AlertTriangle className="h-3 w-3" />
            <span>{isHindi ? 'योजना नीति टकराव चेतावनी' : 'Policy Exclusion Warning'}</span>
          </span>
          <span className="text-xs font-bold text-amber-950 dark:text-amber-300 font-mono">
            {discrepancy_field || 'Mutual Exclusion / Dual Subsidy Bar'}
          </span>
        </div>
        <span className="rounded bg-amber-100 dark:bg-amber-950/80 dark:text-amber-300 px-2 py-0.5 text-[10px] font-semibold text-amber-800">
          {isHindi ? 'दोहरा लाभ निषेध' : 'Anti-Duplicate Policy'}
        </span>
      </div>

      {/* Main Title & Explanation */}
      <div>
        <h4 className="text-sm sm:text-base font-bold text-slate-900 dark:text-amber-100 leading-snug">
          {title}
        </h4>
        <p className="mt-1.5 text-xs text-slate-700 dark:text-amber-200/90 leading-relaxed">
          {explanation}
        </p>
      </div>

      {/* Side-by-Side Scheme Comparison */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        {/* Scheme A */}
        <div className="rounded-xl border border-amber-200 dark:border-amber-900/60 bg-white/95 dark:bg-[#141F18] p-3.5 space-y-2 shadow-2xs">
          <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-200 border-b border-slate-100 dark:border-charcoal-800 pb-1.5">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
              <span className="truncate max-w-[160px]">{source_a?.portal || scheme_a?.name || 'Scheme A'}</span>
            </span>
            <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 dark:bg-emerald-950/80 dark:text-emerald-300 px-1.5 py-0.5 rounded">
              {scheme_a?.level || 'Portal A'}
            </span>
          </div>
          <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
            {source_a?.rule || 'Official guidelines stipulate single allotment per household.'}
          </p>
        </div>

        {/* Scheme B */}
        <div className="rounded-xl border border-amber-200 dark:border-amber-900/60 bg-white/95 dark:bg-[#141F18] p-3.5 space-y-2 shadow-2xs">
          <div className="flex items-center justify-between font-bold text-slate-800 dark:text-slate-200 border-b border-slate-100 dark:border-charcoal-800 pb-1.5">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-amber-500"></span>
              <span className="truncate max-w-[160px]">{source_b?.portal || scheme_b?.name || 'Scheme B'}</span>
            </span>
            <span className="text-[10px] font-mono text-amber-800 bg-amber-50 dark:bg-amber-950/80 dark:text-amber-300 px-1.5 py-0.5 rounded">
              {scheme_b?.level || 'Portal B'}
            </span>
          </div>
          <p className="text-slate-600 dark:text-slate-300 text-[11px] leading-relaxed">
            {source_b?.rule || 'Concurrent subsidy barred under state DBT de-duplication.'}
          </p>
        </div>
      </div>

      {/* Recommendation Card */}
      {recommendation && (
        <div className="rounded-xl border border-emerald-300 dark:border-emerald-800/60 bg-emerald-50/90 dark:bg-[#0E2018] p-3.5 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950 dark:text-emerald-300">
            <CheckCircle2 className="h-4 w-4 text-emerald-700 dark:text-emerald-400" />
            <span>{isHindi ? 'विशेषज्ञ सलाह (Recommended Action):' : 'Expert Policy Recommendation:'}</span>
          </div>
          <p className="text-xs text-emerald-900 dark:text-emerald-200 leading-relaxed font-medium">
            <strong className="text-emerald-950 dark:text-sand-50 font-bold">{recommendation.preferred_scheme}:</strong> {recommendation.reason}
          </p>
          {recommendation.action && (
            <p className="text-[11px] text-emerald-800 dark:text-emerald-300/90 pt-0.5">
              👉 {recommendation.action}
            </p>
          )}
        </div>
      )}

      {/* Interactive Options if provided */}
      {clarification_prompt && options.length > 0 && onSelectOption && (
        <div className="rounded-xl border border-amber-300 dark:border-amber-800/50 bg-white dark:bg-[#141F18] p-3.5 space-y-2">
          <div className="text-xs font-bold text-slate-900 dark:text-sand-50">
            👉 {clarification_prompt}
          </div>
          <div className="space-y-1.5">
            {options.map((opt, oIdx) => (
              <button
                key={oIdx}
                type="button"
                onClick={() => onSelectOption(opt, query)}
                className="w-full text-left p-2.5 rounded-lg text-xs border border-slate-200 dark:border-charcoal-700 bg-white dark:bg-[#101914] hover:border-emerald-500 hover:bg-emerald-50 dark:hover:bg-[#16271E] transition flex items-center justify-between cursor-pointer group"
              >
                <span className="text-slate-800 dark:text-slate-200 group-hover:text-emerald-950 dark:group-hover:text-emerald-300 font-medium">
                  {opt}
                </span>
                <span className="text-emerald-700 dark:text-emerald-400 font-bold text-[11px] ml-2 shrink-0 group-hover:translate-x-0.5 transition-transform flex items-center gap-1">
                  <span>Select</span>
                  <ArrowRight className="h-3 w-3" />
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
