import React, { useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  Coins,
  Building2,
  Sparkles
} from 'lucide-react';

export default function EligibilityEvaluationCard({ schemes = [], isHindi = false }) {
  const [expandedSchemes, setExpandedSchemes] = useState({});

  if (!schemes || schemes.length === 0) return null;

  // Filter schemes that have evaluated rules or status
  const evaluatedSchemes = schemes.filter(
    (s) => (s.eligibility_matrix && s.eligibility_matrix.length > 0) || s.eligibility_status
  );

  if (evaluatedSchemes.length === 0) return null;

  const toggleExpand = (idx) => {
    setExpandedSchemes((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const eligibleCount = evaluatedSchemes.filter(
    (s) => s.eligibility_status === 'meets_captured_rules'
  ).length;

  return (
    <div className="my-4 overflow-hidden rounded-2xl border-2 border-emerald-300 dark:border-emerald-700/60 bg-gradient-to-br from-emerald-50/90 via-white to-teal-50/70 dark:from-[#0D1C16] dark:via-[#11231B] dark:to-[#0A1813] p-4 sm:p-5 shadow-subtle transition-all animate-fadeIn">
      {/* Header Bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-200/80 pb-3 dark:border-emerald-800/60">
        <div className="flex items-center gap-2.5">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 text-white shadow-xs dark:bg-emerald-700">
            <ShieldCheck className="h-4 w-4" />
          </span>
          <div>
            <h4 className="text-sm font-bold text-charcoal-900 dark:text-emerald-50">
              {isHindi ? 'सरकारी योजना पात्रता मूल्यांकन रिपोर्ट' : 'Official Scheme Eligibility Evaluation'}
            </h4>
            <p className="text-[11px] text-charcoal-500 dark:text-emerald-200/80">
              {isHindi
                ? 'आपके द्वारा दर्ज किए गए विवरणों के आधार पर आधिकारिक नियमों का मिलान:'
                : 'Deterministic criteria evaluation against authentic government guidelines:'}
            </p>
          </div>
        </div>

        {/* Summary Pill */}
        <span className="rounded-full bg-emerald-100 dark:bg-emerald-950/80 px-3 py-1 text-xs font-bold text-emerald-900 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
          {eligibleCount > 0
            ? (isHindi ? `🎉 ${eligibleCount} योजना हेतु पात्र` : `🎉 Eligible for ${eligibleCount} Scheme${eligibleCount > 1 ? 's' : ''}`)
            : (isHindi ? 'सशर्त / समीक्षाधीन' : 'Criteria Assessment Ready')}
        </span>
      </div>

      {/* Evaluated Scheme Cards */}
      <div className="mt-4 space-y-3.5">
        {evaluatedSchemes.map((scheme, idx) => {
          const sName = scheme.name || scheme.scheme_name || 'Government Scheme';
          const sLevel = scheme.jurisdiction || scheme.level || 'Central';
          const sMinistry = scheme.ministry || '';
          const sBenefit = scheme.benefit || (scheme.benefits && scheme.benefits[0]) || 'Official welfare assistance';
          const sUrl = scheme.url || 'https://www.myscheme.gov.in';
          const rules = scheme.eligibility_matrix || [];
          const status = scheme.eligibility_status || 'meets_captured_rules';
          const isExpanded = expandedSchemes[idx] !== false; // expanded by default

          const isEligible = status === 'meets_captured_rules';
          const isIneligible = status === 'ineligible';

          const metRulesCount = rules.filter((r) => r.status === 'MET').length;
          const totalRulesCount = rules.length;

          return (
            <div
              key={idx}
              className={`rounded-xl border transition-all ${
                isEligible
                  ? 'border-emerald-200 bg-white dark:border-emerald-800/80 dark:bg-[#12221A]'
                  : isIneligible
                  ? 'border-red-200 bg-white dark:border-red-900/60 dark:bg-[#1C1515]'
                  : 'border-amber-200 bg-white dark:border-amber-900/60 dark:bg-[#1C1A14]'
              } p-4 shadow-2xs`}
            >
              {/* Scheme Header & Verdict Badge */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2.5 border-b border-border/50 dark:border-charcoal-700/50">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-charcoal-500 dark:text-charcoal-400 bg-sand-100 dark:bg-charcoal-800 px-2 py-0.5 rounded">
                      {sLevel}
                    </span>
                    {sMinistry && (
                      <span className="text-[10px] text-charcoal-500 dark:text-charcoal-400 truncate max-w-xs">
                        {sMinistry}
                      </span>
                    )}
                  </div>
                  <h5 className="text-sm font-bold text-charcoal-900 dark:text-sand-50 mt-1">
                    {sName}
                  </h5>
                </div>

                {/* Verdict Badge */}
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-bold shadow-2xs ${
                      isEligible
                        ? 'bg-emerald-600 text-white dark:bg-emerald-600'
                        : isIneligible
                        ? 'bg-red-600 text-white dark:bg-red-700'
                        : 'bg-amber-500 text-white dark:bg-amber-600'
                    }`}
                  >
                    {isEligible ? (
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    ) : isIneligible ? (
                      <XCircle className="h-3.5 w-3.5" />
                    ) : (
                      <HelpCircle className="h-3.5 w-3.5" />
                    )}
                    <span>
                      {isEligible
                        ? (isHindi ? 'पात्र (Eligible)' : 'Eligible - Meets Criteria')
                        : isIneligible
                        ? (isHindi ? 'अपात्र (Ineligible)' : 'Not Eligible')
                        : (isHindi ? 'सशर्त / अतिरिक्त विवरण' : 'Conditional / Needs Details')}
                    </span>
                  </span>

                  <button
                    type="button"
                    onClick={() => toggleExpand(idx)}
                    className="p-1 rounded-lg hover:bg-sand-100 dark:hover:bg-charcoal-800 text-charcoal-500 transition cursor-pointer"
                    aria-label="Toggle criteria details"
                  >
                    {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              {/* Benefit Highlight Box */}
              <div className="mt-3 flex items-start gap-2.5 rounded-lg bg-emerald-50/70 p-2.5 text-xs text-emerald-950 dark:bg-emerald-950/40 dark:text-emerald-100 border border-emerald-100 dark:border-emerald-900/40">
                <Coins className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">{isHindi ? 'पात्रता लाभ व वित्तीय सहायता:' : 'Entitlement & Financial Assistance:'} </span>
                  <span>{sBenefit}</span>
                </div>
              </div>

              {/* Expandable Criteria Verification Checklist */}
              {isExpanded && rules.length > 0 && (
                <div className="mt-3.5 space-y-2">
                  <div className="flex items-center justify-between text-[11px] font-semibold text-charcoal-500 dark:text-charcoal-400">
                    <span>{isHindi ? 'मापदंड सत्यापन विवरण (Criteria Breakdown):' : 'Criteria Verification Breakdown:'}</span>
                    <span className="text-emerald-700 dark:text-emerald-400 font-bold">
                      {metRulesCount}/{totalRulesCount} {isHindi ? 'सत्यापित' : 'Passed'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                    {rules.map((rule, rIdx) => {
                      const rLabel = rule.label || rule.rule_text || `${rule.field}: ${rule.value}`;
                      const isMet = rule.status === 'MET';
                      const isNotMet = rule.status === 'NOT_MET';

                      return (
                        <div
                          key={rIdx}
                          className={`flex items-start gap-2 rounded-lg p-2 text-xs border ${
                            isMet
                              ? 'bg-emerald-50/50 border-emerald-200/70 text-emerald-950 dark:bg-emerald-950/20 dark:border-emerald-800/40 dark:text-emerald-100'
                              : isNotMet
                              ? 'bg-red-50/50 border-red-200/70 text-red-950 dark:bg-red-950/20 dark:border-red-800/40 dark:text-red-100'
                              : 'bg-sand-50 border-border text-charcoal-700 dark:bg-charcoal-800/40 dark:border-charcoal-700 dark:text-charcoal-300'
                          }`}
                        >
                          <span className="mt-0.5 shrink-0">
                            {isMet ? (
                              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                            ) : isNotMet ? (
                              <XCircle className="h-3.5 w-3.5 text-red-600 dark:text-red-400" />
                            ) : (
                              <HelpCircle className="h-3.5 w-3.5 text-amber-500 dark:text-amber-400" />
                            )}
                          </span>
                          <span className="leading-snug flex-1">
                            {rLabel}
                          </span>
                          <span className="text-[10px] font-bold uppercase tracking-wider shrink-0 opacity-80">
                            {isMet ? 'Passed' : isNotMet ? 'Failed' : 'Pending'}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="mt-3.5 pt-3 border-t border-border/40 dark:border-charcoal-700/40 flex flex-wrap items-center justify-between gap-2">
                {scheme.documents && scheme.documents.length > 0 && (
                  <div className="flex items-center gap-1.5 text-[11px] text-charcoal-500 dark:text-charcoal-400">
                    <FileText className="h-3.5 w-3.5 text-charcoal-400 shrink-0" />
                    <span className="truncate max-w-xs">
                      {isHindi ? 'दस्तावेज: ' : 'Required: '}
                      {scheme.documents.slice(0, 3).join(', ')}
                    </span>
                  </div>
                )}

                <a
                  href={sUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-700 dark:bg-emerald-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-2xs hover:bg-emerald-800 dark:hover:bg-emerald-500 transition ml-auto"
                >
                  <span>{isHindi ? 'आधिकारिक पोर्टल पर आवेदन करें' : 'Apply on Official Portal'}</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
