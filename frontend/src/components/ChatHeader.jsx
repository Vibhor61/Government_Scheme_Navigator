import React, { useState, useRef, useEffect } from 'react';
import { Menu, Plus, Sparkles, Globe, Bookmark, ShieldCheck, Sun, Moon, ChevronDown, Check } from 'lucide-react';
import { t } from '../utils/i18n';

export const SUPPORTED_LANGUAGES = [
  { code: 'auto', label: 'Auto-Detect', native: 'ಸ್ವಯಂ / स्वतः', flag: '🌐' },
  { code: 'en', label: 'English', native: 'English', flag: '🇮🇳' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳' },
  { code: 'hi', label: 'Hindi', native: 'हिंदी', flag: '🇮🇳' },
  { code: 'bn', label: 'Bengali', native: 'বাংলা', flag: '🇮🇳' },
  { code: 'mr', label: 'Marathi', native: 'मराठी', flag: '🇮🇳' },
  { code: 'ta', label: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
  { code: 'te', label: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' },
  { code: 'gu', label: 'Gujarati', native: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'pa', label: 'Punjabi', native: 'ਪੰਜਾਬੀ', flag: '🇮🇳' },
];

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
  const [isLangOpen, setIsLangOpen] = useState(false);
  const langDropdownRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (langDropdownRef.current && !langDropdownRef.current.contains(event.target)) {
        setIsLangOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentLangObj = SUPPORTED_LANGUAGES.find(l => l.code === language) || SUPPORTED_LANGUAGES[0];

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
            {title || (language === 'kn' ? 'ಜನಸಹಾಯಕ AI' : (isHindi ? 'जनसहायक AI' : 'JanSahayak AI'))}
          </h1>

          {/* Tasteful Assistant Live Indicator */}
          <div className="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-forest-200 bg-forest-50 px-2 py-0.5 text-[11px] font-medium text-forest-800 dark:border-forest-800/80 dark:bg-forest-950/60 dark:text-emerald-300">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-forest-400 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-forest-600 dark:bg-emerald-400" />
            </span>
            <span>
              {t('official_scheme_sources', language)}
            </span>
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
          title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
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
            <span>{savedSchemesCount} {t('nav_saved', language)}</span>
          </button>
        )}

        {/* Multilingual Selector Dropdown */}
        <div className="relative" ref={langDropdownRef}>
          <button
            type="button"
            onClick={() => setIsLangOpen(!isLangOpen)}
            className="flex items-center gap-1.5 rounded-lg border border-border bg-white px-2.5 py-1.5 text-xs font-semibold text-charcoal-700 shadow-2xs hover:border-forest-300 hover:text-forest-700 transition dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-sand-100 dark:hover:border-emerald-600"
            title="Change conversational language"
          >
            <Globe className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
            <span className="font-medium">{currentLangObj.native}</span>
            <ChevronDown className="h-3 w-3 text-charcoal-400" />
          </button>

          {isLangOpen && (
            <div className="absolute right-0 top-full mt-1.5 w-52 rounded-xl border border-border bg-white p-1.5 shadow-xl dark:border-charcoal-800 dark:bg-charcoal-900 z-50 animate-in fade-in zoom-in-95 duration-100">
              <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-charcoal-400 dark:text-charcoal-500">
                Choose Language / ಭಾಷೆ
              </div>
              <div className="max-h-60 overflow-y-auto space-y-0.5">
                {SUPPORTED_LANGUAGES.map((lang) => {
                  const isSelected = language === lang.code;
                  return (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setLanguage(lang.code);
                        setIsLangOpen(false);
                      }}
                      className={`flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-xs text-left transition ${
                        isSelected
                          ? 'bg-forest-50 font-semibold text-forest-800 dark:bg-forest-950/70 dark:text-emerald-300'
                          : 'text-charcoal-700 hover:bg-sand-100 dark:text-charcoal-200 dark:hover:bg-charcoal-800'
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <span>{lang.flag}</span>
                        <span className="font-medium">{lang.native}</span>
                        <span className="text-[10px] text-charcoal-400 dark:text-charcoal-500">({lang.label})</span>
                      </span>
                      {isSelected && <Check className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* New Conversation Button */}
        <button
          onClick={onNewConversation}
          className="hidden items-center gap-1.5 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium text-charcoal-700 transition hover:bg-sand-50 hover:text-charcoal-900 dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-charcoal-300 dark:hover:bg-charcoal-800 dark:hover:text-sand-50 sm:inline-flex"
          title="Start fresh conversation"
        >
          <Plus className="h-3.5 w-3.5 text-charcoal-500 dark:text-charcoal-400" />
          <span className="hidden sm:inline">
            {t('btn_new_chat', language)}
          </span>
        </button>
      </div>
    </header>
  );
}
