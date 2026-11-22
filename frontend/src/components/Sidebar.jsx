import React from 'react';
import {
  Sparkles,
  Compass,
  CheckCircle,
  Bookmark,
  Plus,
  MessageSquare,
  Globe,
  HelpCircle,
  ShieldCheck,
  Trash2,
  X,
  ExternalLink,
  Sun,
  Moon
} from 'lucide-react';
import { t } from '../utils/i18n';

export default function Sidebar({
  activeView,
  setActiveView,
  language,
  setLanguage,
  theme = 'light',
  toggleTheme,
  conversations = [],
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  savedSchemesCount = 0,
  isOpen = false,
  onCloseMobile,
  onOpenHelp,
  onOpenAbout
}) {
  const isDark = theme === 'dark';
  const isHindi = language === 'hi';

  const navItems = [
    {
      id: 'chat',
      label: t('nav_chat', language),
      icon: Sparkles,
      badge: null,
    },
    {
      id: 'discover',
      label: t('nav_discover', language),
      icon: Compass,
      badge: null,
    },
    {
      id: 'eligibility',
      label: t('nav_eligibility', language),
      icon: CheckCircle,
      badge: null,
    },
    {
      id: 'saved',
      label: t('nav_saved', language),
      icon: Bookmark,
      badge: savedSchemesCount > 0 ? savedSchemesCount : null,
    },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onCloseMobile}
          className="fixed inset-0 z-40 bg-charcoal-900/60 backdrop-blur-xs lg:hidden"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-border bg-white transition-all duration-200 ease-in-out lg:static lg:translate-x-0 dark:border-charcoal-800 dark:bg-[#0E1712] ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between border-b border-border/80 px-5 dark:border-charcoal-800/80">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-forest-600 text-white shadow-subtle dark:bg-emerald-700">
              <span className="text-base font-bold leading-none">जन</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-bold tracking-tight text-charcoal-900 dark:text-sand-50">
                  JanSahayak
                </span>
                <span className="rounded bg-forest-100 px-1.5 py-0.5 text-[10px] font-semibold text-forest-700 dark:bg-forest-950 dark:text-emerald-300 dark:border dark:border-forest-800">
                  GovTech
                </span>
              </div>
              <p className="text-[11px] font-medium text-charcoal-500 dark:text-charcoal-400">
                {t('portal_subtitle', language)}
              </p>
            </div>
          </div>

          <button
            onClick={onCloseMobile}
            className="rounded-lg p-1.5 text-charcoal-500 hover:bg-sand-100 hover:text-charcoal-900 lg:hidden dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100"
            aria-label="Close sidebar"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* New Conversation Button */}
        <div className="p-3.5 pb-2">
          <button
            onClick={() => {
              onNewConversation();
              if (onCloseMobile) onCloseMobile();
            }}
            className="group flex w-full items-center justify-center gap-2 rounded-xl bg-forest-600 px-4 py-2.5 text-xs font-semibold text-white shadow-subtle transition-all duration-150 hover:bg-forest-700 active:scale-[0.99] dark:bg-emerald-700 dark:hover:bg-emerald-600"
          >
            <Plus className="h-4 w-4 transition-transform group-hover:rotate-90" />
            <span>{t('btn_new_chat', language)}</span>
          </button>
        </div>

        {/* Core Navigation Items */}
        <div className="px-3 py-2">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveView(item.id);
                    if (onCloseMobile) onCloseMobile();
                  }}
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-forest-50 text-forest-800 font-semibold dark:bg-forest-950/80 dark:text-emerald-300 dark:border dark:border-forest-800/60'
                      : 'text-charcoal-700 hover:bg-sand-100 hover:text-charcoal-900 dark:text-charcoal-300 dark:hover:bg-charcoal-800/60 dark:hover:text-sand-50'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className={`h-4 w-4 ${isActive ? 'text-forest-600 dark:text-emerald-400' : 'text-charcoal-500 dark:text-charcoal-400'}`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge !== null && (
                    <span className="rounded-full bg-forest-100 px-2 py-0.5 text-[10px] font-bold text-forest-700 dark:bg-emerald-950 dark:text-emerald-300 dark:border dark:border-emerald-800">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Recent Conversations */}
        <div className="flex-1 overflow-y-auto px-3 py-3">
          <div className="mb-2 flex items-center justify-between px-2">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-charcoal-400 dark:text-charcoal-500">
              {t('recent_conversations', language)}
            </span>
          </div>

          {conversations.length === 0 ? (
            <div className="px-2 py-4 text-center">
              <p className="text-xs text-charcoal-400 dark:text-charcoal-500">
                {t('no_conversations', language)}
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              {conversations.slice(0, 10).map((conv) => {
                const isSelected = activeConversationId === conv.id && activeView === 'chat';
                return (
                  <div
                    key={conv.id}
                    className={`group relative flex items-center justify-between rounded-lg px-2.5 py-2 text-xs transition-colors ${
                      isSelected
                        ? 'bg-forest-50/70 text-forest-900 font-medium dark:bg-charcoal-800/80 dark:text-emerald-300 dark:border dark:border-charcoal-700'
                        : 'text-charcoal-700 hover:bg-sand-100 hover:text-charcoal-900 dark:text-charcoal-300 dark:hover:bg-charcoal-800/50 dark:hover:text-sand-100'
                    }`}
                  >
                    <button
                      onClick={() => {
                        onSelectConversation(conv.id);
                        setActiveView('chat');
                        if (onCloseMobile) onCloseMobile();
                      }}
                      className="flex min-w-0 flex-1 items-center gap-2 text-left"
                    >
                      <MessageSquare className="h-3.5 w-3.5 shrink-0 text-charcoal-400 group-hover:text-forest-600 dark:text-charcoal-500 dark:group-hover:text-emerald-400" />
                      <span className="truncate">{conv.title || 'Conversation'}</span>
                    </button>

                    {onDeleteConversation && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteConversation(conv.id);
                        }}
                        className="ml-1 opacity-0 group-hover:opacity-100 text-charcoal-400 hover:text-red-500 transition-opacity p-0.5 dark:text-charcoal-500 dark:hover:text-red-400"
                        title="Delete conversation"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Bottom Section: Theme, Language Selector & Footer */}
        <div className="border-t border-border/80 p-3 space-y-2.5 dark:border-charcoal-800">
          {/* Theme Quick Switcher in Sidebar */}
          {toggleTheme && (
            <button
              type="button"
              onClick={toggleTheme}
              className="flex w-full items-center justify-between rounded-lg border border-border bg-sand-50/80 px-2.5 py-1.5 text-xs text-charcoal-700 transition hover:bg-sand-100 dark:border-charcoal-800 dark:bg-charcoal-900 dark:text-charcoal-300 dark:hover:bg-charcoal-800"
            >
              <div className="flex items-center gap-2">
                {isDark ? (
                  <Sun className="h-3.5 w-3.5 text-amber-400" />
                ) : (
                  <Moon className="h-3.5 w-3.5 text-charcoal-500" />
                )}
                <span>{t(isDark ? 'theme_dark' : 'theme_light', language)}</span>
              </div>
              <span className="text-[10px] font-semibold uppercase text-charcoal-400 dark:text-charcoal-500">
                {isDark ? 'Switch to Light' : 'Switch to Dark'}
              </span>
            </button>
          )}

          {/* Multilingual Selector Dropdown in Sidebar */}
          <div className="rounded-lg border border-border bg-sand-50/80 p-2 dark:border-charcoal-800 dark:bg-charcoal-900">
            <div className="flex items-center justify-between mb-1.5 px-0.5">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-charcoal-700 dark:text-charcoal-300">
                <Globe className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
                <span>{t('select_language', language)}</span>
              </div>
              <span className="text-[10px] uppercase font-bold text-forest-700 dark:text-emerald-400">
                {language.toUpperCase()}
              </span>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full rounded-md border border-border bg-white px-2 py-1.5 text-xs font-medium text-charcoal-800 shadow-2xs focus:border-forest-500 focus:outline-none dark:border-charcoal-700 dark:bg-charcoal-800 dark:text-sand-100 cursor-pointer"
              aria-label="Select Interface Language"
            >
              <option value="auto">🌐 Auto-Detect (ಸ್ವಯಂ / स्वतः)</option>
              <option value="en">🇮🇳 English</option>
              <option value="hi">🇮🇳 हिन्दी (Hindi)</option>
              <option value="kn">🇮🇳 ಕನ್ನಡ (Kannada)</option>
              <option value="bn">🇮🇳 বাংলা (Bengali)</option>
              <option value="mr">🇮🇳 मराठी (Marathi)</option>
              <option value="ta">🇮🇳 தமிழ் (Tamil)</option>
              <option value="te">🇮🇳 తెలుగు (Telugu)</option>
              <option value="gu">🇮🇳 ગુજરાતી (Gujarati)</option>
              <option value="pa">🇮🇳 ਪੰਜਾਬੀ (Punjabi)</option>
            </select>
          </div>

          {/* Official Verification Footnote */}
          <div className="flex items-center gap-2 rounded-lg bg-forest-50/60 px-2.5 py-2 text-[11px] text-forest-900 dark:bg-forest-950/40 dark:text-emerald-300 dark:border dark:border-forest-900/60">
            <ShieldCheck className="h-4 w-4 shrink-0 text-forest-600 dark:text-emerald-400" />
            <span className="leading-tight">
              {t('verified_myscheme', language)}
            </span>
          </div>

          {/* Secondary Footer Links */}
          <div className="flex items-center justify-between px-1 text-[11px] text-charcoal-400 dark:text-charcoal-500">
            <button
              onClick={onOpenHelp}
              className="hover:text-charcoal-700 dark:hover:text-sand-200 transition"
            >
              {t('help', language)}
            </button>
            <span>•</span>
            <button
              onClick={onOpenAbout}
              className="hover:text-charcoal-700 dark:hover:text-sand-200 transition"
            >
              {t('about', language)}
            </button>
            <span>•</span>
            <a
              href="https://www.myscheme.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-charcoal-700 dark:hover:text-sand-200 transition flex items-center gap-0.5"
            >
              <span>myScheme</span>
              <ExternalLink className="h-2.5 w-2.5" />
            </a>
          </div>
        </div>
      </aside>
    </>
  );
}
