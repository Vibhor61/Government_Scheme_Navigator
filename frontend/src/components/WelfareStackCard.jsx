import React, { useState } from 'react';
import {
  Sparkles,
  Layers,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  ExternalLink
} from 'lucide-react';

export default function WelfareStackCard({ stack, isHindi = false }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!stack) return null;

  const {
    bundle_title,
    bundle_type,
    badge,
    description,
    total_financial_impact,
    schemes = [],
    application_sequence = []
  } = stack;

  return (
    <div className="relative overflow-hidden rounded-2xl border-2 border-emerald-300 dark:border-emerald-700/60 bg-gradient-to-br from-emerald-50/95 via-white to-teal-50/80 dark:from-[#0E1B15] dark:via-[#101F18] dark:to-[#091510] p-5 shadow-sm transition-all duration-200 hover:shadow-md animate-fadeIn">
      {/* Background subtle watermark icon */}
      <div className="pointer-events-none absolute -right-6 -bottom-6 text-emerald-100 opacity-60 dark:text-emerald-950/40">
        <Layers className="h-44 w-44" />
      </div>

      <div className="relative z-10 space-y-4">
        {/* Header Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-200/60 pb-3 dark:border-emerald-800/40">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-700 px-2.5 py-1 text-xs font-bold uppercase tracking-wider text-white shadow-xs dark:bg-emerald-600">
              <Sparkles className="h-3.5 w-3.5 text-amber-300 animate-pulse" />
              <span>{isHindi ? 'सरकारी योजना कॉम्बो' : 'Synergistic Welfare Stack'}</span>
            </span>
            {badge && (
              <span className="rounded-md bg-emerald-100 px-2 py-0.5 text-[11px] font-semibold text-emerald-800 border border-emerald-200 dark:border-emerald-800/60 dark:bg-emerald-950/80 dark:text-emerald-300">
                {badge}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-1 text-xs font-medium text-emerald-800 hover:text-emerald-950 transition dark:text-emerald-300 dark:hover:text-emerald-100"
          >
            <span>{isExpanded ? (isHindi ? 'संक्षिप्त करें' : 'Collapse') : (isHindi ? 'विस्तार देखें' : 'View Full Roadmap')}</span>
            {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
          </button>
        </div>

        {/* Bundle Title & Rationale */}
        <div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-sand-50 tracking-tight">
            {bundle_title}
          </h3>
          <p className="mt-1 text-xs sm:text-sm text-slate-600 dark:text-emerald-100/80 leading-relaxed">
            {description}
          </p>
        </div>

        {/* Total Cumulative Financial Impact Banner */}
        {total_financial_impact && (
          <div className="rounded-xl bg-gradient-to-r from-emerald-900 to-teal-900 dark:from-[#0a2319] dark:to-[#071d15] dark:border dark:border-emerald-800/50 p-3.5 text-white shadow-xs">
            <div className="flex items-start gap-3">
              <div className="rounded-lg bg-emerald-500/20 p-2 text-emerald-300 border border-emerald-400/30 shrink-0">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-emerald-300">
                  {isHindi ? 'कुल संचयी सहायता (Total Combined Impact):' : 'Total Combined Benefit Package:'}
                </p>
                <p className="text-sm sm:text-base font-extrabold text-white dark:text-emerald-100 mt-0.5">
                  {total_financial_impact}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Participating Schemes Pills */}
        {schemes.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-charcoal-400">
              {isHindi ? 'सम्मिलित योजनाएं (Combined Schemes):' : 'Schemes Combined In This Stack:'}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {schemes.map((s, idx) => (
                <div
                  key={idx}
                  className="rounded-xl border border-emerald-200 bg-white/90 dark:border-emerald-800/50 dark:bg-[#132019] p-3 shadow-2xs hover:border-emerald-400 dark:hover:border-emerald-600 transition"
                >
                  <div className="flex items-center justify-between gap-1">
                    <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px] font-bold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                      {s.role || `Component #${idx + 1}`}
                    </span>
                    {s.url && (
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-slate-400 hover:text-emerald-700 dark:text-charcoal-400 dark:hover:text-emerald-300 transition"
                        title="View official portal"
                      >
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                  <h5 className="mt-1.5 text-xs font-bold text-slate-900 dark:text-sand-50 line-clamp-1">
                    {s.name}
                  </h5>
                  {s.benefit_summary && (
                    <p className="mt-1 text-[11px] text-slate-600 dark:text-slate-300 line-clamp-2">
                      {s.benefit_summary}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Expandable Step-by-Step Application Sequence */}
        {isExpanded && application_sequence.length > 0 && (
          <div className="rounded-xl border border-emerald-200 bg-white dark:border-emerald-800/50 dark:bg-[#132019] p-4 space-y-3">
            <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-950 dark:text-emerald-300 uppercase tracking-wider">
              <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              <span>{isHindi ? 'अनुशंसित आवेदन क्रम (Application Sequence):' : 'Optimal Sequential Application Order:'}</span>
            </div>
            <div className="space-y-2.5">
              {application_sequence.map((step, sIdx) => (
                <div key={sIdx} className="flex items-start gap-3 text-xs">
                  <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-700 dark:bg-emerald-600 text-white font-bold text-[11px]">
                    {step.step || sIdx + 1}
                  </div>
                  <div className="space-y-0.5">
                    <h6 className="font-bold text-slate-900 dark:text-sand-50">
                      {step.title || `Step ${sIdx + 1}`}
                    </h6>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                      {step.instruction}
                    </p>
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
