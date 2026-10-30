import React from 'react';
import { ExternalLink, CheckCircle2 } from 'lucide-react';

/**
 * Clean, lightweight Markdown renderer for JanSahayak AI.
 * Styled with Claude-like typography, crisp spacing, and government source links.
 */
export default function MarkdownMessage({ content }) {
  if (!content) return null;

  // Helper to parse inline markdown (bold, italic, code, links)
  const renderInline = (text) => {
    if (!text) return null;

    // Pattern for links [text](url) or <url>
    const linkRegex = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|<(https?:\/\/[^\s>]+)>/g;
    const parts = [];
    let lastIdx = 0;
    let match;

    while ((match = linkRegex.exec(text)) !== null) {
      if (match.index > lastIdx) {
        parts.push(renderFormatting(text.substring(lastIdx, match.index)));
      }
      const label = match[1] || match[3];
      const url = match[2] || match[3];
      parts.push(
        <a
          key={`link-${match.index}`}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-medium text-forest-700 underline underline-offset-2 decoration-forest-300 hover:decoration-forest-700 hover:text-forest-900 transition"
        >
          <span>{label}</span>
          <ExternalLink className="w-3 h-3 shrink-0 opacity-70" />
        </a>
      );
      lastIdx = linkRegex.lastIndex;
    }

    if (lastIdx < text.length) {
      parts.push(renderFormatting(text.substring(lastIdx)));
    }

    return parts.length > 0 ? parts : renderFormatting(text);
  };

  // Helper for bold, code, and status badges
  const renderFormatting = (text) => {
    const codeParts = text.split(/(`[^`]+`)/g);
    return codeParts.map((part, pIdx) => {
      if (part.startsWith('`') && part.endsWith('`')) {
        return (
          <code key={pIdx} className="rounded bg-sand-100 px-1.5 py-0.5 font-mono text-[11px] text-charcoal-800 border border-border">
            {part.slice(1, -1)}
          </code>
        );
      }

      // Split bold **...**
      const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
      return boldParts.map((bPart, bIdx) => {
        if (bPart.startsWith('**') && bPart.endsWith('**')) {
          const inner = bPart.slice(2, -2);
          const upper = inner.toUpperCase();
          if (upper === 'MET' || upper === 'QUALIFIED' || upper === 'VERIFIED' || upper === 'ELIGIBLE') {
            return (
              <span key={`${pIdx}-${bIdx}`} className="inline-flex items-center gap-1 rounded-full bg-forest-100 px-2 py-0.5 text-xs font-bold text-forest-800">
                <CheckCircle2 className="w-3 h-3 text-forest-600" />
                {inner}
              </span>
            );
          }
          return (
            <strong key={`${pIdx}-${bIdx}`} className="font-semibold text-charcoal-900">
              {inner}
            </strong>
          );
        }
        return bPart;
      });
    });
  };

  // Parse lines into block elements
  const lines = content.split('\n');
  const elements = [];
  let currentList = [];
  let isNumberedList = false;
  let currentTable = [];

  const flushList = () => {
    if (currentList.length > 0) {
      if (isNumberedList) {
        elements.push(
          <ol key={`ol-${elements.length}`} className="my-2.5 list-decimal list-outside pl-5 space-y-1.5 text-sm text-charcoal-700">
            {currentList.map((item, idx) => (
              <li key={idx} className="leading-relaxed">{renderInline(item)}</li>
            ))}
          </ol>
        );
      } else {
        elements.push(
          <ul key={`ul-${elements.length}`} className="my-2.5 list-disc list-outside pl-5 space-y-1.5 text-sm text-charcoal-700">
            {currentList.map((item, idx) => (
              <li key={idx} className="leading-relaxed">{renderInline(item)}</li>
            ))}
          </ul>
        );
      }
      currentList = [];
    }
  };

  const flushTable = () => {
    if (currentTable.length > 0) {
      const headerRow = currentTable[0];
      const dataRows = currentTable.slice(1).filter(r => !r.every(cell => /^[-: ]+$/.test(cell)));

      elements.push(
        <div key={`table-${elements.length}`} className="my-3 overflow-x-auto rounded-xl border border-border bg-white shadow-2xs">
          <table className="w-full text-left text-xs text-charcoal-800">
            {headerRow && (
              <thead className="border-b border-border bg-sand-50/80 font-semibold text-charcoal-900">
                <tr>
                  {headerRow.map((cell, cIdx) => (
                    <th key={cIdx} className="px-3.5 py-2.5">{renderInline(cell)}</th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody className="divide-y divide-border/60">
              {dataRows.map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-sand-50/50 transition-colors">
                  {row.map((cell, cIdx) => (
                    <td key={cIdx} className="px-3.5 py-2">{renderInline(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      currentTable = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const line = rawLine.trim();

    // Table rows
    if (line.startsWith('|') && line.endsWith('|')) {
      flushList();
      const cells = line.slice(1, -1).split('|').map(c => c.trim());
      currentTable.push(cells);
      continue;
    } else {
      flushTable();
    }

    // Numbered list
    const numMatch = line.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      if (currentList.length > 0 && !isNumberedList) flushList();
      isNumberedList = true;
      currentList.push(numMatch[2]);
      continue;
    }

    // Bullet list
    const bulletMatch = line.match(/^[-*•]\s+(.*)/);
    if (bulletMatch) {
      if (currentList.length > 0 && isNumberedList) flushList();
      isNumberedList = false;
      currentList.push(bulletMatch[1]);
      continue;
    }

    // End of lists
    flushList();

    // Headings
    if (line.startsWith('### ')) {
      elements.push(
        <h4 key={`h4-${i}`} className="mt-4 mb-2 text-sm font-bold text-charcoal-900 tracking-tight">
          {renderInline(line.slice(4))}
        </h4>
      );
      continue;
    }
    if (line.startsWith('## ')) {
      elements.push(
        <h3 key={`h3-${i}`} className="mt-5 mb-2.5 text-base font-bold text-charcoal-900 tracking-tight">
          {renderInline(line.slice(3))}
        </h3>
      );
      continue;
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h2 key={`h2-${i}`} className="mt-6 mb-3 text-lg font-bold text-charcoal-900 tracking-tight">
          {renderInline(line.slice(2))}
        </h2>
      );
      continue;
    }

    // Blockquote
    if (line.startsWith('> ')) {
      elements.push(
        <blockquote key={`bq-${i}`} className="my-3 border-l-2 border-forest-600 bg-forest-50/50 pl-3.5 py-1.5 text-xs text-charcoal-700 italic rounded-r-md">
          {renderInline(line.slice(2))}
        </blockquote>
      );
      continue;
    }

    // Horizontal Rule
    if (/^[-*_]{3,}$/.test(line)) {
      elements.push(<hr key={`hr-${i}`} className="my-4 border-t border-border/80" />);
      continue;
    }

    // Normal Paragraph
    if (line.length > 0) {
      elements.push(
        <p key={`p-${i}`} className="my-2 text-sm leading-relaxed text-charcoal-800">
          {renderInline(line)}
        </p>
      );
    }
  }

  flushList();
  flushTable();

  return <div className="space-y-1">{elements}</div>;
}
