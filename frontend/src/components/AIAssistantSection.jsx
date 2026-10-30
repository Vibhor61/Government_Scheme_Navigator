import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Copy,
  Check,
  Sparkles,
  User,
  ArrowUp,
  RefreshCw,
  ShieldCheck,
  CheckCircle2,
  AlertCircle
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

export default function AIAssistantSection({
  initialQuery = '',
  initialProfile = null,
  language = 'en',
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
  const [isListening, setIsListening] = useState(false);
  const [speakingId, setSpeakingId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [userProfile, setUserProfile] = useState(initialProfile || {});

  const messagesEndRef = useRef(null);
  const scrollContainerRef = useRef(null);
  const textareaRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    if (messages.length > 0) {
      onUpdateConversation?.(conversationId, messages, userProfile);
    }
  }, [conversationId, messages, onUpdateConversation, userProfile]);

  // Auto-scroll to bottom of conversation
  useEffect(() => {
    if (messages.length === 0) {
      scrollContainerRef.current?.scrollTo({ top: 0 });
      return;
    }

    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Handle incoming initialQuery
  useEffect(() => {
    if (initialQuery && initialQuery.trim()) {
      handleSend(initialQuery);
    }
  }, [initialQuery]);

  // Adjust textarea height dynamically
  const handleTextareaInput = (e) => {
    setInputQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  };

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = isHindi ? 'hi-IN' : 'en-IN';

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = () => setIsListening(false);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInputQuery(transcript);
        }
      };

      recognitionRef.current = recognition;
    }
  }, [isHindi]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert(isHindi ? 'आपका ब्राउज़र वाक् पहचान का समर्थन नहीं करता।' : 'Speech recognition is not supported in this browser.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.lang = isHindi ? 'hi-IN' : 'en-IN';
        recognitionRef.current.start();
      } catch (err) {
        console.error("Speech recognition start failed:", err);
      }
    }
  };

  // Text to Speech
  const toggleSpeech = (msgId, text) => {
    if (!('speechSynthesis' in window)) return;

    if (speakingId === msgId) {
      window.speechSynthesis.cancel();
      setSpeakingId(null);
      return;
    }

    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*_#`[\]()]/g, '').slice(0, 400);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = isHindi ? 'hi-IN' : 'en-IN';
    utterance.rate = 1.0;
    utterance.onend = () => setSpeakingId(null);
    utterance.onerror = () => setSpeakingId(null);

    setSpeakingId(msgId);
    window.speechSynthesis.speak(utterance);
  };

  // Copy message text
  const handleCopyText = (msgId, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(msgId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Send citizen message to Central Planner
  const handleSend = async (textToSend = inputQuery, clarificationOption = null, additionalProfile = null) => {
    const rawText = typeof textToSend === 'string' ? textToSend.trim() : '';
    const q = rawText || (typeof inputQuery === 'string' ? inputQuery.trim() : '') || (clarificationOption ? String(clarificationOption).trim() : '');
    if (!q && !clarificationOption) return;

    const userMessageText = clarificationOption ? String(clarificationOption) : q;
    const updatedProfile = { ...userProfile, ...(additionalProfile || {}) };
    if (additionalProfile) {
      setUserProfile(updatedProfile);
    }

    // Set conversation title if it's the first message
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
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setIsLoading(true);

    try {
      const conversationHistory = messages
        .slice(-6)
        .map((m) => ({
          role: m.role,
          content: m.content
        }));

      const response = await queryCrawlerAgent(
        q || userMessageText,
        false,
        clarificationOption,
        conversationHistory,
        updatedProfile
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
      console.error("JanSahayak Assistant query failed:", err);
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

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-sand-50 dark:bg-[#0B130F] transition-colors duration-200">
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

                  {/* Message Body Container */}
                  <div
                    className={`max-w-2xl ${
                      isUser
                        ? 'rounded-2xl rounded-tr-xs bg-forest-600 dark:bg-emerald-700 px-4 py-3 text-sm text-white shadow-subtle'
                        : 'w-full rounded-2xl rounded-tl-xs border border-border bg-white dark:border-charcoal-800 dark:bg-[#111A15] p-4 sm:p-5 shadow-subtle'
                    }`}
                  >
                    {/* Assistant Header Actions */}
                    {!isUser && (
                      <div className="mb-3 flex items-center justify-between border-b border-border/60 pb-2 dark:border-charcoal-800/80">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-charcoal-900 dark:text-sand-50">
                            JanSahayak
                          </span>
                          <span className="rounded bg-forest-50 px-1.5 py-0.5 text-[10px] font-semibold text-forest-700 border border-forest-100 dark:border-forest-900/60 dark:bg-forest-950/60 dark:text-emerald-300">
                            {isHindi ? 'सत्यापित उत्तर' : 'Evidence Grounded'}
                          </span>
                        </div>

                        <div className="flex items-center gap-1">
                          {/* Audio TTS Button */}
                          <button
                            type="button"
                            onClick={() => toggleSpeech(msg.id, msg.content)}
                            className="rounded p-1 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 transition dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100"
                            title={speakingId === msg.id ? "Stop voice reading" : "Read aloud"}
                          >
                            {speakingId === msg.id ? (
                              <VolumeX className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400" />
                            ) : (
                              <Volume2 className="h-3.5 w-3.5" />
                            )}
                          </button>

                          {/* Copy Button */}
                          <button
                            type="button"
                            onClick={() => handleCopyText(msg.id, msg.content)}
                            className="rounded p-1 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 transition dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100"
                            title="Copy response"
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

                    {/* Perplexity-style Sources Citations */}
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

                    {/* Key Takeaways Callout if provided */}
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

                    {/* Full Scheme Eligibility Evaluation Card */}
                    {!isUser && data && data.eligibility_matrix && data.eligibility_matrix.some(s => (s.eligibility_matrix && s.eligibility_matrix.length > 0) || s.eligibility_status) && (
                      <div className="mt-4">
                        <EligibilityEvaluationCard
                          schemes={data.eligibility_matrix}
                          isHindi={isHindi}
                        />
                      </div>
                    )}

                    {/* Dynamic Questionnaire Card (LLM Generated Questions) */}
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

                    {/* Cross-Scheme Policy Conflict Warning */}
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

                    {/* Synergistic Welfare Stacking Card */}
                    {!isUser && data && data.welfare_stack && (
                      <div className="mt-4">
                        <WelfareStackCard
                          stack={data.welfare_stack}
                          isHindi={isHindi}
                        />
                      </div>
                    )}

                    {/* Discovered Scheme Bento Cards */}
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

            {/* Assistant Thinking/Loading Bubble */}
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

      {/* Floating Bottom Input Area */}
      <div className="border-t border-border bg-sand-50/95 px-4 py-3 sm:px-6 dark:border-charcoal-800 dark:bg-[#0E1712]">
        <div className="mx-auto max-w-5xl">
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
              placeholder={
                isHindi
                  ? 'अपनी स्थिति या योजना का नाम पूछें (उदा. बीटेक छात्रवृत्ति, किसान आय सहायता, सोलर पैनल)...'
                  : "Ask about your situation or scheme (e.g., B.Tech scholarship, farmer income, rooftop solar)..."
              }
              className="max-h-44 min-h-[48px] w-full resize-none bg-transparent px-3 py-2 text-sm text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none dark:text-sand-50 dark:placeholder:text-charcoal-500"
            />

            {/* Actions: Voice & Send */}
            <div className="flex items-center gap-1.5 shrink-0 pb-1 pr-1">
              {/* Mic Dictation */}
              <button
                type="button"
                onClick={toggleListening}
                className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                  isListening
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'text-charcoal-400 hover:bg-sand-200 hover:text-charcoal-700 dark:text-charcoal-400 dark:hover:bg-charcoal-800 dark:hover:text-sand-100'
                }`}
                title={isListening ? "Stop listening" : "Speak your query"}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>

              {/* Send Button */}
              <button
                type="submit"
                disabled={isLoading || !inputQuery.trim()}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-forest-600 text-white shadow-2xs transition hover:bg-forest-700 active:scale-95 disabled:opacity-40 disabled:hover:bg-forest-600 cursor-pointer dark:bg-emerald-600 dark:hover:bg-emerald-500"
                title="Send message"
              >
                <ArrowUp className="h-4 w-4 stroke-[2.5]" />
              </button>
            </div>
          </form>

          {/* Sub-caption Disclaimer */}
          <p className="mt-2 text-center text-[11px] text-charcoal-400 dark:text-charcoal-500">
            {isHindi
              ? 'जनसहायक आधिकारिक भारत सरकार पोर्टल्स (*.gov.in) से सत्यापित करता है। हमेशा अंतिम सरकारी सर्कुलर अवश्य देखें।'
              : 'JanSahayak verifies eligibility against official Government of India portals (*.gov.in, *.nic.in). Always confirm with official guidelines.'}
          </p>
        </div>
      </div>
    </div>
  );
}
