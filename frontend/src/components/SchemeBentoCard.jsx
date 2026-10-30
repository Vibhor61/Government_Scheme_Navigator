import React from 'react';
import {
  ExternalLink,
  Bookmark,
  Sparkles,
  CheckCircle2,
  Building2,
  MapPin,
  Coins
} from 'lucide-react';

export default function SchemeBentoCard({
  scheme,
  onAskAi,
  onToggleBookmark,
  isBookmarked = false,
  isHindi = false
}) {
  if (!scheme) return null;

  const schemeName = scheme.name || scheme.scheme_name || 'Government Welfare Scheme';
  const ministry = scheme.ministry || scheme.department || 'Government of India';
  const level = scheme.level || scheme.jurisdiction || 'Central';
  const state = scheme.state || (level === 'Central' ? 'All India' : '');
  const category = scheme.category || 'Welfare Scheme';
  const brief = scheme.brief || scheme.repository_summary || scheme.benefit || '';
  const url = scheme.url || (scheme.sources && scheme.sources[0]?.url) || 'https://www.myscheme.gov.in';

  // Extract financial highlight if available
  const benefitHighlight =
    scheme.financial_benefit ||
    scheme.subsidy_amount ||
    (Array.isArray(scheme.benefits) && scheme.benefits[0]) ||
    scheme.benefit ||
    null;

  return (
    <div className="group relative flex flex-col justify-between rounded-xl border border-border bg-white p-4 shadow-subtle transition-all duration-150 hover:border-forest-300 hover:shadow-card dark:border-charcoal-800 dark:bg-[#111A15] dark:hover:border-emerald-600/70">
      <div>
        {/* Top Badges & Bookmark */}
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="rounded-md bg-forest-50 px-2 py-0.5 text-[10px] font-bold text-forest-700 border border-forest-100 dark:bg-forest-950/80 dark:text-emerald-300 dark:border-forest-800/80">
              {level === 'Central' ? (isHindi ? 'केंद्रीय' : 'Central') : state}
            </span>
            <span className="rounded-md bg-sand-100 px-2 py-0.5 text-[10px] font-semibold text-charcoal-600 dark:bg-charcoal-800 dark:text-charcoal-300">
              {category}
            </span>
          </div>

          {onToggleBookmark && (
            <button
              onClick={() => onToggleBookmark(scheme)}
              className={`rounded-lg p-1.5 transition ${
                isBookmarked
                  ? 'text-forest-600 bg-forest-50 dark:bg-forest-950 dark:text-emerald-400'
                  : 'text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 dark:text-charcoal-500 dark:hover:bg-charcoal-800 dark:hover:text-sand-100'
              }`}
              title={isBookmarked ? 'Remove bookmark' : 'Bookmark scheme'}
            >
              <Bookmark className={`h-3.5 w-3.5 ${isBookmarked ? 'fill-forest-600 dark:fill-emerald-400' : ''}`} />
            </button>
          )}
        </div>

        {/* Scheme Name */}
        <h4 className="text-sm font-bold text-charcoal-900 group-hover:text-forest-700 transition-colors leading-snug dark:text-sand-50 dark:group-hover:text-emerald-300">
          {schemeName}
        </h4>

        {/* Ministry / Nodal Department */}
        <p className="mt-0.5 text-[11px] font-medium text-charcoal-500 dark:text-charcoal-400 flex items-center gap-1">
          <Building2 className="h-3 w-3 shrink-0" />
          <span className="truncate">{ministry}</span>
        </p>

        {/* Financial Benefit Callout if available */}
        {benefitHighlight && (
          <div className="mt-2.5 flex items-center gap-1.5 rounded-lg bg-forest-50/70 px-2.5 py-1.5 text-xs font-semibold text-forest-900 border border-forest-100/60 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900/50">
            <Coins className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400 shrink-0" />
            <span className="truncate">
              {typeof benefitHighlight === 'string' ? benefitHighlight : benefitHighlight.text || 'Financial Assistance'}
            </span>
          </div>
        )}

        {/* Brief Overview */}
        {brief && (
          <p className="mt-2 text-xs text-charcoal-600 dark:text-charcoal-300 leading-relaxed line-clamp-2">
            {brief}
          </p>
        )}
      </div>

      {/* Action Footer */}
      <div className="mt-4 flex items-center justify-between gap-2 border-t border-border/60 pt-3 dark:border-charcoal-800/80">
        {onAskAi && (
          <button
            type="button"
            onClick={() => onAskAi(schemeName)}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-forest-700 hover:text-forest-800 transition dark:text-emerald-400 dark:hover:text-emerald-300"
          >
            <Sparkles className="h-3 w-3" />
            <span>{isHindi ? 'पात्रता व आवेदन पूछें' : 'Check Eligibility & Details'}</span>
          </button>
        )}

        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs font-medium text-charcoal-500 hover:text-charcoal-900 dark:text-charcoal-400 dark:hover:text-sand-100 transition"
          title="Visit official portal"
        >
          <span>myScheme</span>
          <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
}
