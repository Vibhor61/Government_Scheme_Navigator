import React, { useState } from 'react';
import { ExternalLink, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';

export default function SourceCitations({ sources = [], isHindi = false }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  // Deduplicate sources by URL
  const uniqueSources = [];
  const seenUrls = new Set();
  for (const src of sources) {
    const url = typeof src === 'string' ? src : (src.url || src.link || '');
    if (url && !seenUrls.has(url)) {
      seenUrls.add(url);
      uniqueSources.push({
        url,
        title: src.title || src.name || url.replace(/^https?:\/\//, '').split('/')[0]
      });
    }
  }

  if (uniqueSources.length === 0) return null;

  const displaySources = isExpanded ? uniqueSources : uniqueSources.slice(0, 3);

  return (
    <div className="mb-3.5 flex flex-wrap items-center gap-2">
      <span className="flex items-center gap-1 text-[11px] font-semibold text-charcoal-400">
        <ShieldCheck className="h-3.5 w-3.5 text-forest-600" />
        <span>{isHindi ? 'आधिकारिक स्रोत:' : 'Sources:'}</span>
      </span>

      <div className="flex flex-wrap items-center gap-1.5">
        {displaySources.map((s, idx) => {
          let domain = 'gov.in';
          try {
            domain = new URL(s.url).hostname.replace('www.', '');
          } catch (e) {
            domain = s.url;
          }

          return (
            <a
              key={idx}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-1 rounded-md border border-border bg-white px-2 py-0.5 text-[11px] font-medium text-charcoal-700 transition hover:border-forest-400 hover:bg-forest-50 hover:text-forest-800"
              title={s.title}
            >
              <span className="flex h-1.5 w-1.5 rounded-full bg-forest-600" />
              <span className="max-w-[130px] truncate">{domain}</span>
              <ExternalLink className="h-2.5 w-2.5 opacity-60 group-hover:opacity-100" />
            </a>
          );
        })}

        {uniqueSources.length > 3 && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center gap-0.5 rounded-md border border-border bg-sand-100/60 px-1.5 py-0.5 text-[11px] font-medium text-charcoal-500 hover:text-charcoal-800 transition"
          >
            <span>{isExpanded ? (isHindi ? 'कम दिखाएं' : 'Less') : `+${uniqueSources.length - 3} ${isHindi ? 'और' : 'more'}`}</span>
            {isExpanded ? <ChevronUp className="h-2.5 w-2.5" /> : <ChevronDown className="h-2.5 w-2.5" />}
          </button>
        )}
      </div>
    </div>
  );
}
