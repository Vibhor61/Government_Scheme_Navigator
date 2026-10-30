import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatHeader from './components/ChatHeader';
import AIAssistantSection from './components/AIAssistantSection';
import DiscoverSchemesView from './components/DiscoverSchemesView';
import CheckEligibilityView from './components/CheckEligibilityView';
import SavedSchemesView from './components/SavedSchemesView';
import { HelpModal, AboutModal } from './components/InfoModals';

const readStoredConversations = () => {
  try {
    const stored = localStorage.getItem('jansahayak_conversations');
    const parsed = stored ? JSON.parse(stored) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    console.error('Failed to load saved conversations:', error);
    return [];
  }
};

export default function App() {
  const [activeView, setActiveView] = useState('chat');
  const [language, setLanguage] = useState(() => localStorage.getItem('jansahayak_lang') || 'en');
  const [theme, setTheme] = useState(() => {
    try {
      const stored = localStorage.getItem('jansahayak_theme');
      if (stored) return stored;
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } catch (e) {
      return 'light';
    }
  });
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  // Saved / Bookmarked Schemes (Persisted in localStorage)
  const [savedSchemes, setSavedSchemes] = useState(() => {
    try {
      const stored = localStorage.getItem('jansahayak_saved_schemes');
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      return [];
    }
  });

  // Recent Conversations (Persisted in localStorage)
  const [conversations, setConversations] = useState(readStoredConversations);

  const [activeConversationId, setActiveConversationId] = useState(
    () => readStoredConversations()[0]?.id || `conv-${Date.now()}`
  );
  const [chatInitialQuery, setChatInitialQuery] = useState('');
  const [chatInitialProfile, setChatInitialProfile] = useState(null);

  // Sync state to localStorage
  useEffect(() => {
    localStorage.setItem('jansahayak_lang', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('jansahayak_saved_schemes', JSON.stringify(savedSchemes));
  }, [savedSchemes]);

  useEffect(() => {
    localStorage.setItem('jansahayak_conversations', JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    try {
      localStorage.setItem('jansahayak_theme', theme);
      if (theme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    } catch (e) {
      // ignore
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  // Toggle bookmark
  const handleToggleBookmark = (scheme) => {
    if (!scheme) return;
    const sName = scheme.name || scheme.scheme_name;
    setSavedSchemes(prev => {
      const exists = prev.some(s => (s.name || s.scheme_name) === sName);
      if (exists) {
        return prev.filter(s => (s.name || s.scheme_name) !== sName);
      } else {
        return [scheme, ...prev];
      }
    });
  };

  // Start a new conversation
  const handleNewConversation = () => {
    const newId = `conv-${Date.now()}`;
    setActiveConversationId(newId);
    setChatInitialQuery('');
    setChatInitialProfile(null);
    setActiveView('chat');
  };

  // Update conversation title on first message
  const handleUpdateConversationTitle = (id, title) => {
    setConversations(prev => {
      const existing = prev.find(c => c.id === id);
      if (existing) {
        return prev.map(c => c.id === id ? { ...c, title } : c);
      } else {
        return [{ id, title, timestamp: 'Just now' }, ...prev];
      }
    });
  };

  const handleUpdateConversation = useCallback((id, messages, userProfile) => {
    setConversations(prev => prev.map(conversation => (
      conversation.id === id
        ? { ...conversation, messages, userProfile }
        : conversation
    )));
  }, []);

  // Delete conversation
  const handleDeleteConversation = (id) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeConversationId === id) {
      handleNewConversation();
    }
  };

  // Switch to chat with scheme inquiry
  const handleAskAiAboutScheme = (schemeName) => {
    setChatInitialQuery(
      language === 'hi'
        ? `कृपया "${schemeName}" योजना के लाभ, पात्रता नियम व आवश्यक दस्तावेजों की जानकारी दें।`
        : `Please explain the benefits, eligibility criteria, and required documents for "${schemeName}".`
    );
    setActiveView('chat');
  };

  // Switch to chat with profile evaluation
  const handleAskAiWithProfile = (profile) => {
    setChatInitialProfile(profile);
    const summary = language === 'hi'
      ? `मेरा प्रोफाइल: लिंग: ${profile.gender}, आयु: ${profile.age}, राज्य: ${profile.state}, क्षेत्र: ${profile.rural_urban}, वर्ग: ${profile.social_category}, व्यवसाय: ${profile.occupation}, आय: ₹${profile.annual_family_income}। मैं किन केंद्रीय व राज्य योजनाओं का पात्र हूँ?`
      : `Based on my profile: Gender: ${profile.gender}, Age: ${profile.age}, State: ${profile.state}, Area: ${profile.rural_urban}, Category: ${profile.social_category}, Occupation: ${profile.occupation}, Income: ₹${profile.annual_family_income}. Which central and state schemes am I eligible for?`;

    setChatInitialQuery(summary);
    setActiveView('chat');
  };

  const getPageTitle = () => {
    if (activeView === 'discover') return language === 'hi' ? 'योजनाएं खोजें' : 'Discover Schemes';
    if (activeView === 'eligibility') return language === 'hi' ? 'पात्रता जांच' : 'Check Eligibility';
    if (activeView === 'saved') return language === 'hi' ? 'सहेजी गई योजनाएं' : 'Saved Schemes';
    return language === 'hi' ? 'योजना मार्गदर्शक' : 'Benefit navigator';
  };

  const activeConversation = conversations.find(item => item.id === activeConversationId);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-sand-50 dark:bg-[#0B130F] font-sans text-charcoal-900 dark:text-[#F0F5F2] transition-colors duration-200">
      {/* Left Navigation Sidebar */}
      <Sidebar
        activeView={activeView}
        setActiveView={setActiveView}
        language={language}
        setLanguage={setLanguage}
        theme={theme}
        toggleTheme={toggleTheme}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={(id) => {
          setActiveConversationId(id);
          setChatInitialQuery('');
          setChatInitialProfile(null);
          setActiveView('chat');
        }}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        savedSchemesCount={savedSchemes.length}
        isOpen={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        onOpenHelp={() => setIsHelpOpen(true)}
        onOpenAbout={() => setIsAboutOpen(true)}
      />

      {/* Main Screen Area */}
      <div className="flex flex-1 flex-col overflow-hidden bg-sand-50 dark:bg-[#0B130F] transition-colors duration-200">
        {/* Top Header Bar */}
        <ChatHeader
          title={getPageTitle()}
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          onNewConversation={handleNewConversation}
          language={language}
          setLanguage={setLanguage}
          theme={theme}
          toggleTheme={toggleTheme}
          savedSchemesCount={savedSchemes.length}
          onOpenSaved={() => setActiveView('saved')}
        />

        {/* View Switcher */}
        <main className="flex-1 overflow-hidden">
          {activeView === 'chat' && (
            <AIAssistantSection
              key={activeConversationId}
              conversationId={activeConversationId}
              initialQuery={chatInitialQuery}
              initialMessages={activeConversation?.messages || []}
              initialProfile={chatInitialProfile || activeConversation?.userProfile || null}
              language={language}
              onSaveScheme={handleToggleBookmark}
              savedSchemes={savedSchemes}
              onUpdateConversationTitle={handleUpdateConversationTitle}
              onUpdateConversation={handleUpdateConversation}
            />
          )}

          {activeView === 'discover' && (
            <DiscoverSchemesView
              onAskAi={handleAskAiAboutScheme}
              onToggleBookmark={handleToggleBookmark}
              savedSchemes={savedSchemes}
              language={language}
            />
          )}

          {activeView === 'eligibility' && (
            <CheckEligibilityView
              onAskAiWithProfile={handleAskAiWithProfile}
              onAskAi={handleAskAiAboutScheme}
              onToggleBookmark={handleToggleBookmark}
              savedSchemes={savedSchemes}
              language={language}
            />
          )}

          {activeView === 'saved' && (
            <SavedSchemesView
              savedSchemes={savedSchemes}
              onAskAi={handleAskAiAboutScheme}
              onToggleBookmark={handleToggleBookmark}
              onNavigateToDiscover={() => setActiveView('discover')}
              language={language}
            />
          )}
        </main>
      </div>

      {/* Modals */}
      <HelpModal
        isOpen={isHelpOpen}
        onClose={() => setIsHelpOpen(false)}
        isHindi={language === 'hi'}
      />
      <AboutModal
        isOpen={isAboutOpen}
        onClose={() => setIsAboutOpen(false)}
        isHindi={language === 'hi'}
      />
    </div>
  );
}
