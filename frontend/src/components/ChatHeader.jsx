import React from 'react';
import { Menu, Plus, Sparkles, Globe, Bookmark, ShieldCheck, Sun, Moon } from 'lucide-react';

export default function ChatHeader({
  onOpenMobileSidebar,
  onNewConversation,
  language,
  setLanguage,
  theme = 'light',
  toggleTheme,
  savedSchemesCount = 0,
  onOpenSaved,
  title
}) {
  const isHindi = language === 'hi';
  const isDark = theme === 'dark';

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-white/95 px-3 backdrop-blur-md sm:px-6 dark:border-charcoal-800/80 dark:bg-[#0E1712]/90 transition-colors duration-200">
      {/* Left: Mobile Menu & Title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobileSidebar}
          className="rounded-lg p-1.5 text-charcoal-500 hover:bg-sand-100 hover:text-charcoal-900 lg:hidden dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100"
          aria-label="Open sidebar menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-2.5">
          <h1 className="whitespace-nowrap text-sm font-semibold tracking-tight text-charcoal-900 dark:text-sand-50">
            {title || (isHindi ? 'जनसहायक AI' : 'JanSahayak AI')}
          </h1>

          {/* Tasteful Assistant Live Indicator */}
          <div className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-forest-200 bg-forest-50 px-2 py-0.5 text-[11px] font-medium text-forest-800 dark:border-forest-800/80 dark:bg-forest-950/60 dark:text-emerald-300">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-forest-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-forest-600 dark:bg-emerald-400" />
            </span>
            <span>{isHindi ? 'आधिकारिक योजना स्रोत' : 'Official scheme sources'}</span>
          </div>
        </div>
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-1 sm:gap-2">
        {/* Dark / Light Mode Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-white text-charcoal-600 transition-all duration-200 hover:border-forest-300 hover:bg-sand-100 hover:text-charcoal-900 dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-amber-300 dark:hover:border-emerald-600 dark:hover:bg-charcoal-800 sm:h-10 sm:w-10"
          aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          title={isDark ? (isHindi ? 'लाइट मोड चालू करें' : 'Switch to Light Mode') : (isHindi ? 'डार्क मोड चालू करें' : 'Switch to Dark Mode')}
        >
          {isDark ? (
            <Sun className="h-4 w-4 transition-transform hover:rotate-45" />
          ) : (
            <Moon className="h-4 w-4 transition-transform hover:-rotate-12" />
          )}
        </button>

        {/* Saved Schemes Quick Pill */}
        {savedSchemesCount > 0 && (
          <button
            onClick={onOpenSaved}
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-border bg-white px-2.5 py-1.5 text-xs font-medium text-charcoal-700 hover:border-forest-300 hover:text-forest-700 transition dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-charcoal-300 dark:hover:border-forest-600 dark:hover:text-emerald-400"
          >
            <Bookmark className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
            <span>{savedSchemesCount} {isHindi ? 'सहेजी गई' : 'Saved'}</span>
          </button>
        )}

        {/* Language Pill */}
        <div className="flex items-center rounded-lg border border-border bg-sand-50 p-0.5 text-xs font-semibold dark:border-charcoal-800 dark:bg-charcoal-900">
          <button
            onClick={() => setLanguage('en')}
            className={`rounded px-2 py-0.5 transition ${
              language === 'en'
                ? 'bg-white text-forest-700 shadow-2xs dark:bg-charcoal-800 dark:text-emerald-400'
                : 'text-charcoal-500 hover:text-charcoal-900 dark:text-charcoal-400 dark:hover:text-sand-100'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLanguage('hi')}
            className={`rounded px-2 py-0.5 transition ${
              language === 'hi'
                ? 'bg-white text-forest-700 shadow-2xs dark:bg-charcoal-800 dark:text-emerald-400'
                : 'text-charcoal-500 hover:text-charcoal-900 dark:text-charcoal-400 dark:hover:text-sand-100'
            }`}
          >
            हिं
          </button>
        </div>

        {/* New Conversation Button */}
        <button
          onClick={onNewConversation}
          className="hidden items-center gap-1.5 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium text-charcoal-700 transition hover:bg-sand-50 hover:text-charcoal-900 dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-charcoal-300 dark:hover:bg-charcoal-800 dark:hover:text-sand-50 sm:inline-flex"
          title="Start fresh conversation"
        >
          <Plus className="h-3.5 w-3.5 text-charcoal-500 dark:text-charcoal-400" />
          <span className="hidden sm:inline">{isHindi ? 'नई चैट' : 'New chat'}</span>
        </button>
      </div>
    </header>
  );
}
