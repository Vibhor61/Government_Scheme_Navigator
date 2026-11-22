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
import { t } from '../utils/i18n';

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
        content: response.answer || t('no_answer', language),
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
          content: t('connection_error', language),
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

  // ── Mid-conversation language switch notification ──────────────────────
  const [langSwitchNotice, setLangSwitchNotice] = useState(null);
  const prevLangRef = useRef(language);

  useEffect(() => {
    if (prevLangRef.current !== language) {
      prevLangRef.current = language;
      if (messages.length > 0) {
        setLangSwitchNotice(t('language_switched_banner', language));
        const timer = setTimeout(() => setLangSwitchNotice(null), 4500);
        return () => clearTimeout(timer);
      }
    }
  }, [language, messages.length]);

  // ── Placeholder text by language ──────────────────────────────────────
  const placeholderText = t('input_placeholder', language);

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
            onOpenVoice={handleOpenVoicePopup}
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
                            {t('evidence_grounded', language)}
                          </span>
                          {/* Speaking indicator badge */}
                          {isSpeaking && (
                            <span className="flex items-center gap-1 rounded-full bg-emerald-100 dark:bg-emerald-900/40 px-2 py-0.5 text-[10px] font-semibold text-emerald-700 dark:text-emerald-300 animate-pulse">
                              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              {t('reading_aloud', language)}
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
                              title={isSpeaking ? t('stop_reading', language) : t('read_aloud', language)}
                              aria-label={isSpeaking ? t('stop_reading', language) : t('read_aloud', language)}
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
                            title={t('copy_response', language)}
                            aria-label={t('copy_response', language)}
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
                          <span>{t('key_takeaways_label', data.detected_language || language)}</span>
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
                        <EligibilityEvaluationCard schemes={data.eligibility_matrix} isHindi={isHindi} language={data.detected_language || language} />
                      </div>
                    )}

                    {/* Dynamic Questionnaire */}
                    {!isUser && data && data.profiler_questions && data.profiler_questions.length > 0 && (
                      <DynamicQuestionnaireCard
                        questions={data.profiler_questions}
                        language={data.detected_language || language}
                        isHindi={isHindi}
                        isSubmitting={isLoading}
                        onSubmitBatch={(batchAnswers) => {
                          const summaryParts = Object.entries(batchAnswers)
                            .filter(([_, v]) => v !== undefined && v !== '')
                            .map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`);
                          const userText = summaryParts.join(', ');
                          const activeLang = data.detected_language || language;
                          const displayMsg = `${t('submitted_details_prefix', activeLang)}: ${userText} (${t('evaluate_my_eligibility', activeLang)})`;
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
                        <WelfareStackCard stack={data.welfare_stack} isHindi={isHindi} language={data.detected_language || language} />
                      </div>
                    )}

                    {/* Scheme Bento Cards */}
                    {!isUser && data && data.extracted_schemes && data.extracted_schemes.length > 0 && (
                      <div className="mt-5 space-y-3">
                        <div className="flex items-center justify-between">
                          <h5 className="text-xs font-bold uppercase tracking-wider text-charcoal-400">
                            {t('discovered_schemes_heading', data.detected_language || language)}
                          </h5>
                          <span className="text-[11px] font-semibold text-forest-700 dark:text-emerald-400">
                            {data.extracted_schemes.length} {t('schemes_found', data.detected_language || language)}
                          </span>
                        </div>
                        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                          {data.extracted_schemes.map((scheme, sIdx) => (
                            <SchemeBentoCard
                              key={sIdx}
                              scheme={scheme}
                              onAskAi={(name) => handleSend(language === 'hi' ? `"${name}" योजना की पात्रता व लाभ बताएं` : (language === 'kn' ? `"${name}" ಯೋಜನೆಯ ಅರ್ಹತೆ ಮತ್ತು ಪ್ರಯೋಜನಗಳನ್ನು ವಿವರಿಸಿ` : `Explain detailed eligibility and benefits for "${name}"`))}
                              onToggleBookmark={onSaveScheme}
                              isBookmarked={isBookmarked(scheme)}
                              isHindi={isHindi}
                              language={data.detected_language || language}
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
                    {t('analyzing_eligibility', language)}
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
        <div className="mx-auto max-w-4xl space-y-2.5">

          {/* Mid-conversation language switch notification */}
          {langSwitchNotice && (
            <div className="flex items-center justify-center animate-fadeIn">
              <span className="rounded-full bg-emerald-100 dark:bg-emerald-950/80 border border-emerald-300 dark:border-emerald-700/80 px-3.5 py-1 text-xs font-semibold text-emerald-900 dark:text-emerald-200 shadow-2xs">
                🌐 {langSwitchNotice}
              </span>
            </div>
          )}

          {/* Symmetrical Chat Input Card */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="relative rounded-2xl border border-border bg-white p-3 shadow-card transition-all duration-200 focus-within:border-forest-500 focus-within:ring-2 focus-within:ring-forest-100 dark:border-charcoal-800 dark:bg-[#15201A] dark:focus-within:border-emerald-600 dark:focus-within:ring-emerald-950 sm:p-3.5"
          >
            {/* Auto-expanding Textarea - full width, symmetric padding */}
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
              className="max-h-44 min-h-[46px] w-full resize-none bg-transparent px-2.5 py-1 text-sm sm:text-base leading-relaxed text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none dark:text-sand-50 dark:placeholder:text-charcoal-500"
              aria-label={t('input_placeholder', language)}
            />

            {/* Symmetrical Bottom Action Bar */}
            <div className="flex items-center justify-between pt-2.5 mt-1 border-t border-border/50 dark:border-charcoal-800/70">
              {/* Left Action Group: Voice Input & Auto Read-Aloud */}
              <div className="flex items-center gap-2">
                {/* Voice Input Button */}
                <button
                  type="button"
                  onClick={handleOpenVoicePopup}
                  className={`flex h-9 items-center gap-1.5 px-3 rounded-xl text-xs font-semibold transition border cursor-pointer ${
                    isListening
                      ? 'bg-red-500 border-red-600 text-white animate-pulse'
                      : 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800 text-forest-700 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 active:scale-95'
                  }`}
                  title={t('tap_to_speak', language)}
                  aria-label={t('tap_to_speak', language)}
                >
                  {isListening ? (
                    <MicOff className="h-3.5 w-3.5" />
                  ) : (
                    <Mic className="h-3.5 w-3.5 animate-pulse text-emerald-600 dark:text-emerald-400" />
                  )}
                  <span className="whitespace-nowrap font-medium">
                    {t('tap_to_speak', language)}
                  </span>
                </button>

                {/* Auto Read-aloud Toggle (Default Open / Active) */}
                {ttsSupported && (
                  <button
                    type="button"
                    onClick={toggleAutoRead}
                    className={`flex h-9 items-center gap-1.5 px-3 rounded-xl text-xs font-medium transition border cursor-pointer ${
                      autoRead
                        ? 'bg-forest-50 border-forest-200 text-forest-700 dark:bg-emerald-950/50 dark:border-emerald-800/80 dark:text-emerald-300 shadow-2xs'
                        : 'border-border/70 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-600 dark:border-charcoal-800 dark:text-charcoal-500 dark:hover:bg-charcoal-800 dark:hover:text-charcoal-300'
                    }`}
                    title={autoRead ? 'Disable auto read-aloud' : 'Enable auto read-aloud'}
                    aria-pressed={autoRead}
                  >
                    <Headphones className={`h-3.5 w-3.5 ${autoRead ? 'text-forest-600 dark:text-emerald-400' : ''}`} />
                    <span className="whitespace-nowrap">
                      {autoRead ? t('auto_read_aloud_on', language) : t('auto_read_aloud_off', language)}
                    </span>
                    {autoRead && (
                      <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400" />
                    )}
                  </button>
                )}
              </div>

              {/* Right Action Group: Stop Speaking & Send */}
              <div className="flex items-center gap-2">
                {/* Stop speaking button (when TTS active) */}
                {speakingId && (
                  <button
                    type="button"
                    onClick={stopSpeaking}
                    className="flex h-9 items-center gap-1.5 rounded-xl px-3 text-xs font-semibold bg-red-50 text-red-600 hover:bg-red-100 dark:bg-red-950/40 dark:text-red-400 dark:hover:bg-red-900/40 transition border border-red-200 dark:border-red-900/60 animate-pulse cursor-pointer"
                    title={t('stop_reading', language)}
                  >
                    <VolumeX className="h-3.5 w-3.5" />
                    <span>{t('stop_reading', language)}</span>
                  </button>
                )}

                {/* Send Button */}
                <button
                  type="submit"
                  disabled={isLoading || !inputQuery.trim()}
                  className="flex h-9 w-9 items-center justify-center rounded-xl bg-forest-600 text-white shadow-2xs transition hover:bg-forest-700 active:scale-95 disabled:opacity-40 disabled:hover:bg-forest-600 cursor-pointer dark:bg-emerald-600 dark:hover:bg-emerald-500"
                  title={t('btn_send', language)}
                  aria-label={t('btn_send', language)}
                >
                  <ArrowUp className="h-4 w-4 stroke-[2.5]" />
                </button>
              </div>
            </div>
          </form>

          {/* Disclaimer */}
          <p className="text-center text-[11px] text-charcoal-400 dark:text-charcoal-500">
            {t('disclaimer', language)}
          </p>
        </div>
      </div>
    </div>
  );
}
