import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Pause,
  Play,
  Copy,
  Check,
  Sparkles,
  User,
  ArrowUp,
  RefreshCw,
  CheckCircle2,
  Headphones,
} from 'lucide-react';
import { queryCrawlerAgent } from '../services/api';
import EmptyState from './EmptyState';
import SourceCitations from './SourceCitations';
import MarkdownMessage from './MarkdownMessage';
import DynamicQuestionnaireCard from './DynamicQuestionnaireCard';
import EligibilityEvaluationCard from './EligibilityEvaluationCard';
import SchemeBentoCard from './SchemeBentoCard';
import WelfareStackCard from './WelfareStackCard';
import CrossSchemeConflictAlert from './CrossSchemeConflictAlert';
import VoicePopup from './VoicePopup';
import useVoice from '../hooks/useVoice';

export default function AIAssistantSection({
  initialQuery = '',
  initialProfile = null,
  language = 'en',
  onLanguageChange,
  onSaveScheme,
  savedSchemes = [],
  onUpdateConversationTitle,
  onUpdateConversation,
  initialMessages = [],
  conversationId = 'default'
}) {
  const isHindi = language === 'hi';

  const [messages, setMessages] = useState(initialMessages);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const [userProfile, setUserProfile] = useState(initialProfile || {});
  const [isVoicePopupOpen, setIsVoicePopupOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const textareaRef = useRef(null);

  // ── Voice hook ─────────────────────────────────────────────────────────
  const {
    isListening,
    transcript,
    interimTranscript,
    speechSupported,
    micError,
    toggleListening,
    clearTranscript,
    speakingId,
    isPaused,
    ttsSupported,
    autoRead,
    toggleAutoRead,
    speak,
    stopSpeaking,
    autoSpeak,
  } = useVoice(language);

  // Auto-read the latest assistant message when it arrives
  const prevMsgCountRef = useRef(initialMessages.length);
  useEffect(() => {
    if (messages.length > prevMsgCountRef.current) {
      const latest = messages[messages.length - 1];
      if (latest?.role === 'assistant' && latest.content) {
        autoSpeak(latest.id, latest.content, latest.data?.detected_language);
      }
    }
    prevMsgCountRef.current = messages.length;
  }, [messages, autoSpeak]);

  // ── Persist conversation ───────────────────────────────────────────────
  useEffect(() => {
    if (messages.length > 0) {
      onUpdateConversation?.(conversationId, messages, userProfile);
    }
  }, [conversationId, messages, onUpdateConversation, userProfile]);

  // ── Auto-scroll ────────────────────────────────────────────────────────
  useEffect(() => {
    if (messages.length === 0) {
      scrollContainerRef.current?.scrollTo({ top: 0 });
      return;
    }
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // ── Handle initial query ───────────────────────────────────────────────
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      handleSend(initialQuery);
    }
  }, [initialQuery]);

  // ── Textarea auto-height ───────────────────────────────────────────────
  const handleTextareaInput = (e) => {
    setInputQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  // ── Voice popup handlers ──────────────────────────────────────────────
  const handleOpenVoicePopup = () => {
    clearTranscript();
    setIsVoicePopupOpen(true);
  };

  const handleVoiceConfirm = (text) => {
    if (text.trim()) {
      setInputQuery(text.trim());
      setIsVoicePopupOpen(false);
      clearTranscript();
      // Auto-send after voice input
      setTimeout(() => handleSend(text.trim()), 50);
    }
  };

  const handleVoiceRetry = () => {
    clearTranscript();
    // If currently listening, stop first; next tap will restart
    if (isListening) toggleListening();
  };

  // ── TTS toggle per message ────────────────────────────────────────────
  const handleToggleSpeech = (msgId, text, msgLang) => {
    if (speakingId === msgId) {
      stopSpeaking();
    } else {
      speak(msgId, text, msgLang);
    }
  };

  // ── Copy text ─────────────────────────────────────────────────────────
  const handleCopyText = (msgId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // ── Send message ──────────────────────────────────────────────────────
  const handleSend = async (textToSend = inputQuery, clarificationOption = null, additionalProfile = null) => {
    const rawText = typeof textToSend === 'string' ? textToSend.trim() : '';
    const q = rawText || (typeof inputQuery === 'string' ? inputQuery.trim() : '') || (clarificationOption ? String(clarificationOption).trim() : '');
    if (!q && !clarificationOption) return;

    const userMessageText = clarificationOption ? String(clarificationOption) : q;
    const updatedProfile = { ...userProfile, ...(additionalProfile || {}) };
    if (additionalProfile) setUserProfile(updatedProfile);

    if (messages.length === 0 && onUpdateConversationTitle) {
      const title = userMessageText.length > 32 ? `${userMessageText.slice(0, 32)}...` : userMessageText;
      onUpdateConversationTitle(conversationId, title);
    }

    const newUserMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userMessageText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputQuery('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsLoading(true);

    try {
      const conversationHistory = messages
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const response = await queryCrawlerAgent(
        q || userMessageText,
        false,
        clarificationOption,
        conversationHistory,
        updatedProfile,
        language
      );

      const newAssistantMsg = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer || (isHindi ? 'कोई जानकारी नहीं मिली।' : 'No answer generated.'),
        data: response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, newAssistantMsg]);
    } catch (err) {
      console.error('JanSahayak Assistant query failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          role: 'assistant',
          content: isHindi
            ? 'क्षमा करें, आधिकारिक सरकारी रिपॉजिटरी से जुड़ने में समस्या हुई। कृपया पुनः प्रयास करें।'
            : 'Sorry, I encountered an issue connecting to the official government repository. Please try again.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const isBookmarked = (scheme) => {
    const sName = scheme?.name || scheme?.scheme_name;
    return savedSchemes.some(s => (s.name || s.scheme_name) === sName);
  };

  // ── Placeholder text by language ──────────────────────────────────────
  const placeholderText = {
    kn: 'ನಿಮ್ಮ ಅಗತ್ಯತೆ ಅಥವಾ ಯೋಜನೆಯ ಹೆಸರು ಕೇಳಿ...',
    hi: 'अपनी स्थिति या योजना का नाम पूछें...',
    bn: 'আপনার প্রয়োজন বা যোজনার নাম জিজ্ঞেস করুন...',
    ta: 'உங்கள் தேவை அல்லது திட்டத்தின் பெயரைக் கேளுங்கள்...',
    te: 'మీ అవసరం లేదా పథకం పేరు అడగండి...',
    mr: 'तुमची गरज किंवा योजनेचे नाव विचारा...',
    gu: 'તમારી જરૂરિયાત અથવા યોજનાનું નામ પૂછો...',
    en: 'Ask about your situation or scheme (e.g., B.Tech scholarship, farmer income, solar panels)...',
  }[language] || 'Ask about a government scheme...';

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-sand-50 dark:bg-[#0B130F] transition-colors duration-200">

      {/* Voice Input Popup */}
      <VoicePopup
        isOpen={isVoicePopupOpen}
        onClose={() => { setIsVoicePopupOpen(false); if (isListening) toggleListening(); }}
        language={language}
        onLanguageChange={onLanguageChange}
        isListening={isListening}
        transcript={transcript}
        interimTranscript={interimTranscript}
        micError={micError}
        speechSupported={speechSupported}
        onToggleListening={toggleListening}
        onRetry={handleVoiceRetry}
        onConfirm={handleVoiceConfirm}
      />

      {/* Scrollable Conversation Stream */}
      <div ref={scrollContainerRef} className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6">
        {messages.length === 0 ? (
          <EmptyState
            onSelectPrompt={(promptQuery) => handleSend(promptQuery)}
            language={language}
          />
        ) : (
          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              const data = msg.data;
              const isSpeaking = speakingId === msg.id;

              return (
                <div
                  key={msg.id}
                  className={`flex gap-3 sm:gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {/* Assistant Avatar */}
                  {!isUser && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-forest-600 dark:bg-emerald-700 text-white shadow-2xs mt-1">
                      <Sparkles className="h-4 w-4" />
                    </div>
                  )}

                  {/* Message Body */}
                  <div
                    className={`max-w-2xl ${
                      isUser
                        ? 'rounded-2xl rounded-tr-xs bg-forest-600 dark:bg-emerald-700 px-4 py-3 text-sm text-white shadow-subtle'
                        : `w-full rounded-2xl rounded-tl-xs border border-border bg-white dark:border-charcoal-800 dark:bg-[#111A15] p-4 sm:p-5 shadow-subtle transition-all ${isSpeaking ? 'ring-2 ring-forest-400 dark:ring-emerald-500' : ''}`
                    }`}
                  >
                    {/* Assistant Header */}
                    {!isUser && (
                      <div className="mb-3 flex items-center justify-between border-b border-border/60 pb-2 dark:border-charcoal-800/80">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-charcoal-900 dark:text-sand-50">
                            JanSahayak
                          </span>
                          <span className="rounded bg-forest-50 px-1.5 py-0.5 text-[10px] font-semibold text-forest-700 border border-forest-100 dark:border-forest-900/60 dark:bg-forest-950/60 dark:text-emerald-300">
                            {isHindi ? 'सत्यापित उत्तर' : 'Evidence Grounded'}
                          </span>
                          {/* Speaking indicator badge */}
                          {isSpeaking && (
                            <span className="flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-900/40 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 animate-pulse">
                              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              {isHindi ? 'पढ़ रहे हैं' : 'Reading'}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-1">
                          {/* Read Aloud / TTS Button */}
                          {ttsSupported && (
                            <button
                              type="button"
                              onClick={() => handleToggleSpeech(msg.id, msg.content, msg.data?.detected_language)}
                              className={`rounded p-1.5 transition ${
                                isSpeaking
                                  ? 'bg-forest-100 text-forest-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                                  : 'text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100'
                              }`}
                              title={isSpeaking ? (isHindi ? 'रोकें' : 'Stop reading') : (isHindi ? 'ज़ोर से पढ़ें' : 'Read aloud')}
                              aria-label={isSpeaking ? 'Stop reading' : 'Read aloud'}
                            >
                              {isSpeaking ? (
                                <VolumeX className="h-3.5 w-3.5" />
                              ) : (
                                <Volume2 className="h-3.5 w-3.5" />
                              )}
                            </button>
                          )}

                          {/* Copy Button */}
                          <button
                            type="button"
                            onClick={() => handleCopyText(msg.id, msg.content)}
                            className="rounded p-1.5 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 transition dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100"
                            title={isHindi ? 'कॉपी करें' : 'Copy response'}
                            aria-label="Copy response"
                          >
                            {copiedId === msg.id ? (
                              <Check className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
                            ) : (
                              <Copy className="h-3.5 w-3.5" />
                            )}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Sources */}
                    {!isUser && data && data.crawled_sources && data.crawled_sources.length > 0 && (
                      <SourceCitations sources={data.crawled_sources} isHindi={isHindi} />
                    )}

                    {/* Message Content */}
                    {isUser ? (
                      <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    ) : (
                      <div className="text-charcoal-800 dark:text-slate-200 leading-relaxed">
                        <MarkdownMessage content={msg.content} />
                      </div>
                    )}

                    {/* Key Takeaways */}
                    {!isUser && data && data.key_takeaways && data.key_takeaways.length > 0 && (
                      <div className="mt-4 rounded-xl border border-forest-100 bg-forest-50/60 p-3 text-xs dark:border-forest-900/60 dark:bg-forest-950/40">
                        <p className="font-bold text-forest-900 dark:text-emerald-300 mb-1 flex items-center gap-1.5">
                          <CheckCircle2 className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
                          <span>{isHindi ? 'मुख्य बिंदु (Key Takeaways):' : 'Key Takeaways:'}</span>
                        </p>
                        <ul className="list-disc list-outside pl-4 space-y-0.5 text-forest-950 dark:text-emerald-100/90">
                          {data.key_takeaways.map((point, pIdx) => (
                            <li key={pIdx}>{point}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Eligibility Evaluation Card */}
                    {!isUser && data && data.eligibility_matrix && data.eligibility_matrix.some(s => (s.eligibility_matrix && s.eligibility_matrix.length > 0) || s.eligibility_status) && (
                      <div className="mt-4">
                        <EligibilityEvaluationCard schemes={data.eligibility_matrix} isHindi={isHindi} />
                      </div>
                    )}

                    {/* Dynamic Questionnaire */}
                    {!isUser && data && data.profiler_questions && data.profiler_questions.length > 0 && (
                      <DynamicQuestionnaireCard
                        questions={data.profiler_questions}
                        isHindi={isHindi}
                        isSubmitting={isLoading}
                        onSubmitBatch={(batchAnswers) => {
                          const summaryParts = Object.entries(batchAnswers)
                            .filter(([_, v]) => v !== undefined && v !== '')
                            .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`);
                          const userText = summaryParts.join(', ');
                          const displayMsg = isHindi
                            ? `पात्रता विवरण: ${userText} (मेरी पात्रता का मूल्यांकन करें)`
                            : `Eligibility Details: ${userText} (Evaluate my eligibility)`;
                          handleSend(userText, displayMsg, batchAnswers);
                        }}
                      />
                    )}

                    {/* Cross-Scheme Conflict Alert */}
                    {!isUser && data && data.conflict_alert && (
                      <div className="mt-4">
                        <CrossSchemeConflictAlert
                          conflict={data.conflict_alert}
                          onSelectOption={(opt) => handleSend(opt)}
                          query={data.query || ''}
                          isHindi={isHindi}
                        />
                      </div>
                    )}

                    {/* Welfare Stack Card */}
                    {!isUser && data && data.welfare_stack && (
                      <div className="mt-4">
                        <WelfareStackCard stack={data.welfare_stack} isHindi={isHindi} />
                      </div>
                    )}

                    {/* Scheme Bento Cards */}
                    {!isUser && data && data.extracted_schemes && data.extracted_schemes.length > 0 && (
                      <div className="mt-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <h5 className="text-xs font-bold uppercase tracking-wider text-charcoal-400">
                            {isHindi ? 'संबंधित सरकारी योजनाएं' : 'Discovered Government Schemes'}
                          </h5>
                          <span className="text-[11px] font-semibold text-forest-700">
                            {data.extracted_schemes.length} {isHindi ? 'योजनाएं मिलीं' : 'Schemes found'}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                          {data.extracted_schemes.map((scheme, sIdx) => (
                            <SchemeBentoCard
                              key={sIdx}
                              scheme={scheme}
                              onAskAi={(name) => handleSend(isHindi ? `"${name}" योजना की पात्रता व लाभ बताएं` : `Explain detailed eligibility and benefits for "${name}"`)}
                              onToggleBookmark={onSaveScheme}
                              isBookmarked={isBookmarked(scheme)}
                              isHindi={isHindi}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Timestamp */}
                    <div className="mt-2 text-right">
                      <span className={`text-[10px] ${isUser ? 'text-forest-100' : 'text-charcoal-400'}`}>
                        {msg.timestamp}
                      </span>
                    </div>
                  </div>

                  {/* User Avatar */}
                  {isUser && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-sand-200 text-charcoal-700 shadow-2xs mt-1 dark:bg-charcoal-800 dark:text-sand-100">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Thinking / Loading Bubble */}
            {isLoading && (
              <div className="flex gap-3 sm:gap-4 items-start">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-forest-600 dark:bg-emerald-700 text-white shadow-2xs mt-1">
                  <Sparkles className="h-4 w-4 animate-spin" />
                </div>
                <div className="rounded-2xl rounded-tl-xs border border-border bg-white px-4 py-3 shadow-subtle flex items-center gap-2 text-xs font-medium text-charcoal-600 dark:border-charcoal-800 dark:bg-[#111A15] dark:text-charcoal-300">
                  <RefreshCw className="h-3.5 w-3.5 animate-spin text-forest-600 dark:text-emerald-400" />
                  <span>
                    {isHindi
                      ? 'आधिकारिक रिपॉजिटरी में पात्रता नियमों का विश्लेषण किया जा रहा है...'
                      : 'Searching official repositories and evaluating eligibility rules...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* ── Bottom Input Bar ─────────────────────────────────────────────── */}
      <div className="border-t border-border bg-sand-50/95 px-4 py-3 sm:px-6 dark:border-charcoal-800 dark:bg-[#0E1712]">
        <div className="mx-auto max-w-5xl space-y-2">

          {/* Auto-read toggle strip */}
          {ttsSupported && (
            <div className="flex items-center justify-between px-1">
              <button
                type="button"
                onClick={toggleAutoRead}
                className={`flex items-center gap-2 rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                  autoRead
                    ? 'bg-forest-100 text-forest-700 dark:bg-emerald-900/40 dark:text-emerald-300'
                    : 'text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-600 dark:text-charcoal-500 dark:hover:bg-charcoal-800 dark:hover:text-charcoal-300'
                }`}
                title={autoRead
                  ? (isHindi ? 'स्वतः पढ़ना बंद करें' : 'Disable auto read-aloud')
                  : (isHindi ? 'स्वतः पढ़ना चालू करें' : 'Enable auto read-aloud')}
                aria-pressed={autoRead}
              >
                <Headphones className="h-3.5 w-3.5" />
                <span>
                  {autoRead
                    ? (isHindi ? 'स्वतः पढ़ना: चालू' : 'Auto read-aloud: On')
                    : (isHindi ? 'स्वतः पढ़ना' : 'Auto read-aloud')}
                </span>
              </button>

              {/* Stop speaking button (when active) */}
              {speakingId && (
                <button
                  type="button"
                  onClick={stopSpeaking}
                  className="flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-950/40 dark:text-red-400 dark:hover:bg-red-900/40 transition animate-pulse"
                >
                  <VolumeX className="h-3.5 w-3.5" />
                  {isHindi ? 'रोकें' : 'Stop reading'}
                </button>
              )}
            </div>
          )}

          {/* Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="relative flex items-end rounded-2xl border border-border bg-white p-2.5 shadow-card transition-all focus-within:border-forest-500 focus-within:ring-2 focus-within:ring-forest-100 dark:border-charcoal-800 dark:bg-[#15201A] dark:focus-within:border-emerald-600 dark:focus-within:ring-emerald-950"
          >
            {/* Auto-expanding Textarea */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputQuery}
              onChange={handleTextareaInput}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder={placeholderText}
              className="max-h-44 min-h-[48px] w-full resize-none bg-transparent px-3 py-2 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none dark:text-sand-50 dark:placeholder:text-charcoal-500"
              aria-label={isHindi ? 'अपना प्रश्न लिखें' : 'Type your question'}
            />

            {/* Actions: Voice & Send */}
            <div className="flex items-center gap-1.5 shrink-0 pb-1 pr-1">
              {/* Voice Input Button → opens popup */}
              <button
                type="button"
                onClick={handleOpenVoicePopup}
                className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                  isListening
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'text-charcoal-400 hover:bg-sand-200 hover:text-charcoal-700 dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100'
                }`}
                title={isHindi ? 'आवाज़ से बोलें' : 'Speak your query'}
                aria-label={isHindi ? 'आवाज़ से बोलें' : 'Voice input'}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={isLoading || !inputQuery.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-forest-600 text-white shadow-2xs transition hover:bg-forest-700 active:scale-95 disabled:opacity-40 disabled:hover:bg-forest-600 cursor-pointer dark:bg-emerald-600 dark:hover:bg-emerald-500"
                title={isHindi ? 'भेजें' : 'Send message'}
                aria-label="Send"
              >
                <ArrowUp className="h-4 w-4 stroke-[2.5]" />
              </button>
            </div>
          </form>

          {/* Disclaimer */}
          <p className="text-center text-[11px] text-charcoal-400 dark:text-charcoal-500">
            {isHindi
              ? 'जनसहायक आधिकारिक भारत सरकार पोर्टल्स (*.gov.in) से सत्यापित करता है। हमेशा अंतिम सरकारी सर्कुलर अवश्य देखें।'
              : 'JanSahayak verifies eligibility against official Government of India portals (*.gov.in, *.nic.in). Always confirm with official guidelines.'}
          </p>
        </div>
      </div>
    </div>
  );
}
