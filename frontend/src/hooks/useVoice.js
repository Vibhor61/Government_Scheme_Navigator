/**
 * useVoice.js
 * Custom hook for voice input (Speech Recognition) and read-aloud (Speech Synthesis).
 * Supports all major Indian languages with proper locale codes.
 */
import { useState, useRef, useEffect, useCallback } from 'react';

export const LANGUAGE_CONFIG = {
  auto: { locale: 'hi-IN',  label: 'Auto (Hinglish/All)', nativeLabel: 'ऑटो' },
  hi:   { locale: 'hi-IN',  label: 'Hindi',      nativeLabel: 'हिंदी' },
  en:   { locale: 'en-IN',  label: 'English',    nativeLabel: 'English' },
  bn:   { locale: 'bn-IN',  label: 'Bengali',    nativeLabel: 'বাংলা' },
  mr:   { locale: 'mr-IN',  label: 'Marathi',    nativeLabel: 'मराठी' },
  ta:   { locale: 'ta-IN',  label: 'Tamil',      nativeLabel: 'தமிழ்' },
  te:   { locale: 'te-IN',  label: 'Telugu',     nativeLabel: 'తెలుగు' },
  gu:   { locale: 'gu-IN',  label: 'Gujarati',   nativeLabel: 'ગુજરાતી' },
  kn:   { locale: 'kn-IN',  label: 'Kannada',    nativeLabel: 'ಕನ್ನಡ' },
  pa:   { locale: 'pa-IN',  label: 'Punjabi',    nativeLabel: 'ਪੰਜਾਬੀ' },
  or:   { locale: 'or-IN',  label: 'Odia',       nativeLabel: 'ଓଡ଼ିଆ' },
  ml:   { locale: 'ml-IN',  label: 'Malayalam',  nativeLabel: 'മലയാളം' },
};

function getLocale(lang) {
  if (!lang || lang === 'auto') {
    // hi-IN recognition in Chromium handles both Hindi, Hinglish, and English accents reliably
    return 'hi-IN';
  }
  return LANGUAGE_CONFIG[lang]?.locale || 'hi-IN';
}

/** Strip markdown symbols for clean TTS output */
function stripMarkdown(text) {
  return text
    .replace(/#{1,6}\s+/g, '')       // headings
    .replace(/\*\*(.+?)\*\*/g, '$1') // bold
    .replace(/\*(.+?)\*/g, '$1')     // italic
    .replace(/_(.+?)_/g, '$1')       // italic underscore
    .replace(/`(.+?)`/g, '$1')       // inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links → label only
    .replace(/^[-*•]\s+/gm, '')      // bullet points
    .replace(/^\d+\.\s+/gm, '')      // numbered lists
    .replace(/^>\s+/gm, '')          // blockquotes
    .replace(/[-_*]{3,}/g, '')       // horizontal rules
    .replace(/\|/g, ' ')             // table pipes
    .replace(/\s{2,}/g, ' ')         // collapse extra whitespace
    .trim();
}

export default function useVoice(language = 'en') {
  // ── Voice Input State ────────────────────────────────────────────────────
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [speechSupported, setSpeechSupported] = useState(false);
  const [micError, setMicError] = useState(null);
  const recognitionRef = useRef(null);

  // ── TTS State ─────────────────────────────────────────────────────────────
  const [speakingId, setSpeakingId] = useState(null);
  const [isPaused, setIsPaused] = useState(false);
  const [ttsSupported, setTtsSupported] = useState(false);
  const [autoRead, setAutoRead] = useState(() => {
    try { return localStorage.getItem('jansahayak_autoread') === 'true'; } catch { return false; }
  });
  const utteranceRef = useRef(null);

  // ── Init checks ───────────────────────────────────────────────────────────
  useEffect(() => {
    setTtsSupported('speechSynthesis' in window);
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setSpeechSupported(!!SpeechRecognition);
  }, []);

  // ── Re-build recognition whenever language changes ─────────────────────
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    // Tear down previous instance
    if (recognitionRef.current) {
      try { recognitionRef.current.abort(); } catch {}
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;      // keep listening until user stops
    recognition.interimResults = true;  // show partial results live
    recognition.lang = getLocale(language);
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setMicError(null);
      setTranscript('');
      setInterimTranscript('');
    };

    recognition.onresult = (event) => {
      let finalText = '';
      let interimText = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript;
        } else {
          interimText += result[0].transcript;
        }
      }
      if (finalText) setTranscript(prev => prev + finalText);
      setInterimTranscript(interimText);
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      setInterimTranscript('');
      if (event.error !== 'aborted') {
        const msgs = {
          'not-allowed':    'Microphone permission denied. Please allow microphone access in your browser settings.',
          'no-speech':      'No speech detected. Please speak clearly into your mic.',
          'network':        'Network error. If using Brave browser, enable "Use Google services for speech recognition" in brave://settings/privacy, or try Google Chrome / Edge.',
          'audio-capture':  'No microphone found. Please connect a microphone.',
        };
        setMicError(msgs[event.error] || `Speech recognition error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      try { recognition.abort(); } catch {}
    };
  }, [language]);

  // ── Voice Input Controls ──────────────────────────────────────────────────
  const startListening = useCallback(() => {
    if (!recognitionRef.current || isListening) return;
    setMicError(null);
    setTranscript('');
    setInterimTranscript('');
    try {
      recognitionRef.current.lang = getLocale(language);
      recognitionRef.current.start();
    } catch (err) {
      console.error('Recognition start failed:', err);
    }
  }, [isListening, language]);

  const stopListening = useCallback(() => {
    if (!recognitionRef.current || !isListening) return;
    try { recognitionRef.current.stop(); } catch {}
  }, [isListening]);

  const toggleListening = useCallback(() => {
    if (isListening) stopListening();
    else startListening();
  }, [isListening, startListening, stopListening]);

  const clearTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
  }, []);

  // ── TTS Controls ──────────────────────────────────────────────────────────
  const speak = useCallback((id, text, msgLang) => {
    if (!ttsSupported) return;

    // If same message, toggle pause/resume
    if (speakingId === id) {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
        setIsPaused(false);
      } else {
        window.speechSynthesis.pause();
        setIsPaused(true);
      }
      return;
    }

    // Stop any ongoing speech
    window.speechSynthesis.cancel();
    setIsPaused(false);

    const cleanText = stripMarkdown(text);
    if (!cleanText) return;

    // Chrome bug: speechSynthesis.speak() stops after ~15 seconds on long texts
    // Workaround: chunk into sentences and speak sequentially
    const sentences = cleanText.match(/[^.!?।]+[.!?।]?/g) || [cleanText];
    const targetLocale = getLocale(msgLang || language);

    let idx = 0;
    const speakNext = () => {
      if (idx >= sentences.length) {
        setSpeakingId(null);
        setIsPaused(false);
        return;
      }
      const utter = new SpeechSynthesisUtterance(sentences[idx].trim());
      utter.lang = targetLocale;
      utter.rate = 0.9;   // slightly slower for accessibility
      utter.pitch = 1.0;
      utter.volume = 1.0;

      // Pick best matching voice for locale
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(v => v.lang === targetLocale)
        || voices.find(v => v.lang.startsWith(targetLocale.split('-')[0]))
        || null;
      if (preferred) utter.voice = preferred;

      utter.onend = () => {
        idx++;
        speakNext();
      };
      utter.onerror = () => {
        setSpeakingId(null);
        setIsPaused(false);
      };

      utteranceRef.current = utter;
      window.speechSynthesis.speak(utter);
    };

    setSpeakingId(id);
    speakNext();
  }, [ttsSupported, speakingId, language]);

  const stopSpeaking = useCallback(() => {
    if (ttsSupported) window.speechSynthesis.cancel();
    setSpeakingId(null);
    setIsPaused(false);
  }, [ttsSupported]);

  const toggleAutoRead = useCallback(() => {
    setAutoRead(prev => {
      const next = !prev;
      try { localStorage.setItem('jansahayak_autoread', String(next)); } catch {}
      return next;
    });
  }, []);

  // Auto-read new messages
  const autoSpeak = useCallback((id, text, msgLang) => {
    if (autoRead && text) speak(id, text, msgLang);
  }, [autoRead, speak]);

  return {
    // Voice Input
    isListening,
    transcript,
    interimTranscript,
    speechSupported,
    micError,
    startListening,
    stopListening,
    toggleListening,
    clearTranscript,

    // TTS
    speakingId,
    isPaused,
    ttsSupported,
    autoRead,
    toggleAutoRead,
    speak,
    stopSpeaking,
    autoSpeak,
  };
}
