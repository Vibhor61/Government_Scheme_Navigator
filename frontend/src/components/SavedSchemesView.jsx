import React from 'react';
import { Bookmark, Sparkles, Trash2, ArrowRight } from 'lucide-react';
import SchemeBentoCard from './SchemeBentoCard';

export default function SavedSchemesView({
  savedSchemes = [],
  onAskAi,
  onToggleBookmark,
  onNavigateToDiscover,
  language = 'en'
}) {
  const isHindi = language === 'hi';

  return (
    <div className="flex-1 overflow-y-auto bg-sand-50 dark:bg-[#0B130F] px-4 py-8 sm:px-8 transition-colors duration-200">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-forest-200 bg-forest-50 px-3 py-1 text-xs font-semibold text-forest-800 dark:border-forest-800 dark:bg-forest-950 dark:text-emerald-300 mb-2">
            <Bookmark className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
            <span>{isHindi ? 'सहेजी गई सूची' : 'Saved Collection'}</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-charcoal-900 dark:text-sand-50 sm:text-3xl">
            {isHindi ? 'सहेजी गई सरकारी योजनाएं' : 'Saved Government Schemes'}
          </h2>
          <p className="mt-1.5 text-sm text-charcoal-500 dark:text-charcoal-300 max-w-2xl">
            {isHindi
              ? 'आपकी बुकमार्क की गई योजनाएं यहां सुरक्षित हैं ताकि आप कभी भी पात्रता व आवेदन स्थिति देख सकें।'
              : 'Your bookmarked welfare programs are stored here for easy reference, document checklists, and application links.'}
          </p>
        </div>

        {savedSchemes.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-white dark:border-charcoal-800 dark:bg-[#111A15] p-12 text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-sand-100 dark:bg-charcoal-800 text-charcoal-400">
              <Bookmark className="h-6 w-6" />
            </div>
            <h3 className="text-sm font-semibold text-charcoal-800 dark:text-sand-50">
              {isHindi ? 'कोई सहेजी गई योजना नहीं' : 'No saved schemes yet'}
            </h3>
            <p className="mt-1 text-xs text-charcoal-500 dark:text-charcoal-400 max-w-md mx-auto">
              {isHindi
                ? 'योजनाएं खोजते समय या AI चैट में बुकमार्क आइकन पर क्लिक करके योजनाओं को यहां सहेजें।'
                : 'Bookmark schemes while browsing the catalog or chatting with JanSahayak AI to quickly access them later.'}
            </p>
            {onNavigateToDiscover && (
              <button
                onClick={onNavigateToDiscover}
                className="mt-5 inline-flex items-center gap-2 rounded-xl bg-forest-600 dark:bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-subtle hover:bg-forest-700 dark:hover:bg-emerald-500 transition"
              >
                <span>{isHindi ? 'योजनाएं खोजें' : 'Discover Schemes'}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {savedSchemes.map((scheme, idx) => (
              <SchemeBentoCard
                key={idx}
                scheme={scheme}
                onAskAi={onAskAi}
                onToggleBookmark={onToggleBookmark}
                isBookmarked={true}
                isHindi={isHindi}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
