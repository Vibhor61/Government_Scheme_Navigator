/**
 * VoicePopup.jsx
 * Full-screen voice input modal with animated waveform, live transcript,
 * and language-aware UI strings. Designed for low-literacy users.
 */
import React, { useEffect, useRef, useState } from 'react';
import { Mic, MicOff, X, Check, RefreshCw } from 'lucide-react';

const UI_STRINGS = {
  en: {
    title: 'Listening…',
    idle: 'Tap the mic and speak your question',
    speak: 'Tap to speak',
    stop: 'Tap to stop',
    done: 'Use this',
    retry: 'Retry',
    close: 'Close',
    interim: 'Listening…',
    placeholder: 'Your words will appear here…',
    hint: 'Speak in any language (English, Hindi, Kannada, Tamil, Telugu, etc.)',
  },
  hi: {
    title: 'सुन रहे हैं…',
    idle: 'माइक दबाएं और अपना सवाल बोलें',
    speak: 'बोलने के लिए दबाएं',
    stop: 'रोकने के लिए दबाएं',
    done: 'उपयोग करें',
    retry: 'दोबारा बोलें',
    close: 'बंद करें',
    interim: 'सुन रहे हैं…',
    placeholder: 'आपके शब्द यहाँ दिखेंगे…',
    hint: 'अपनी भाषा में बोलें (हिंदी, हिंग्लिश या कोई भी भारतीय भाषा)',
  },
  kn: {
    title: 'ಕೇಳುತ್ತಿದ್ದೇನೆ…',
    idle: 'ಮೈಕ್ ಒತ್ತಿ ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಹೇಳಿ',
    speak: 'ಮಾತಾಡಲು ಒತ್ತಿ',
    stop: 'ನಿಲ್ಲಿಸಲು ಒತ್ತಿ',
    done: 'ಬಳಸಿ',
    retry: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ',
    close: 'ಮುಚ್ಚಿ',
    interim: 'ಕೇಳುತ್ತಿದ್ದೇನೆ…',
    placeholder: 'ನಿಮ್ಮ ಮಾತು ಇಲ್ಲಿ ಕಾಣಿಸುತ್ತದೆ…',
    hint: 'ಕನ್ನಡದಲ್ಲಿ ಅಥವಾ ಕಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ಮಾತನಾಡಿ',
  },
  bn: {
    title: 'শুনছি…',
    idle: 'মাইক চাপুন এবং আপনার প্রশ্ন বলুন',
    speak: 'বলতে চাপুন',
    stop: 'থামাতে চাপুন',
    done: 'ব্যবহার করুন',
    retry: 'আবার চেষ্টা করুন',
    close: 'বন্ধ করুন',
    interim: 'শুনছি…',
    placeholder: 'আপনার কথা এখানে দেখাবে…',
    hint: 'বাংলায় বা বাংলিশে স্পষ্ট করে বলুন',
  },
  ta: {
    title: 'கேட்கிறேன்…',
    idle: 'மைக்கை அழுத்தி உங்கள் கேள்வியை சொல்லுங்கள்',
    speak: 'பேச அழுத்துங்கள்',
    stop: 'நிறுத்த அழுத்துங்கள்',
    done: 'பயன்படுத்து',
    retry: 'மீண்டும் முயற்சிக்கவும்',
    close: 'மூடு',
    interim: 'கேட்கிறேன்…',
    placeholder: 'உங்கள் வார்த்தைகள் இங்கே தோன்றும்…',
    hint: 'தமிழில் அல்லது ஆங்கிலத்தில் தெளிவாகப் பேசுங்கள்',
  },
  te: {
    title: 'వింటున్నాను…',
    idle: 'మైక్ నొక్కి మీ ప్రశ్న చెప్పండి',
    speak: 'మాట్లాడటానికి నొక్కండి',
    stop: 'ఆపడానికి నొక్కండి',
    done: 'ఉపయోగించండి',
    retry: 'మళ్ళీ ప్రయత్నించండి',
    close: 'మూసివేయి',
    interim: 'వింటున్నాను…',
    placeholder: 'మీ మాటలు ఇక్కడ కనిపిస్తాయి…',
    hint: 'తెలుగులో లేదా ఇంగ్లీషులో స్పష్టంగా మాట్లాడండి',
  },
  mr: {
    title: 'ऐकत आहे…',
    idle: 'मायक्रोफोन दाबा आणि प्रश्न विचारा',
    speak: 'बोलण्यासाठी दाबा',
    stop: 'थांबण्यासाठी दाबा',
    done: 'वापरा',
    retry: 'पुन्हा प्रयत्न करा',
    close: 'बंद करा',
    interim: 'ऐकत आहे…',
    placeholder: 'तुमचे शब्द येथे दिसतील…',
    hint: 'मराठीत किंवा हिंग्लिशमध्ये स्पष्ट बोला',
  },
  gu: {
    title: 'સાંભળી રહ્યો છું…',
    idle: 'માઇક દબાવો અને સવાલ પૂછો',
    speak: 'બોલવા માટે દબાવો',
    stop: 'રોકવા માટે દબાવો',
    done: 'ઉપયોગ કરો',
    retry: 'ફરી પ્રયત્ન કરો',
    close: 'બંધ કરો',
    interim: 'સાંભળી રહ્યો છું…',
    placeholder: 'તમારા શબ્દો અહીં દેખાશે…',
    hint: 'ગુજરાતીમાં અથવા અંગ્રેજીમાં સ્પષ્ટ બોલો',
  },
};

function getStrings(lang) {
  return UI_STRINGS[lang] || UI_STRINGS.en;
}

/** Animated sound-wave bars */
function WaveformBars({ active }) {
  const bars = [0.4, 0.7, 1.0, 0.8, 0.5, 0.9, 0.6, 1.0, 0.7, 0.4];
  return (
    <div className="flex items-center justify-center gap-[3px] h-12" aria-hidden="true">
      {bars.map((height, i) => (
        <span
          key={i}
          className={`w-1.5 rounded-full transition-all ${
            active
              ? 'bg-emerald-500 dark:bg-emerald-400'
              : 'bg-charcoal-200 dark:bg-charcoal-700'
          }`}
          style={{
            height: active ? `${height * 48}px` : '8px',
            animationName: active ? 'voiceBar' : 'none',
            animationDuration: `${0.6 + i * 0.08}s`,
            animationIterationCount: 'infinite',
            animationDirection: 'alternate',
            animationTimingFunction: 'ease-in-out',
            animationDelay: `${i * 0.07}s`,
          }}
        />
      ))}
      <style>{`
        @keyframes voiceBar {
          from { transform: scaleY(0.3); }
          to   { transform: scaleY(1); }
        }
      `}</style>
    </div>
  );
}

const QUICK_VOICE_LANGS = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिंदी' },
  { code: 'kn', label: 'ಕನ್ನಡ' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'mr', label: 'मराठी' },
  { code: 'gu', label: 'ગુજરાતી' },
];

export default function VoicePopup({
  isOpen,
  onClose,
  language = 'en',
  onLanguageChange,
  isListening,
  transcript,
  interimTranscript,
  micError,
  speechSupported,
  onToggleListening,
  onRetry,
  onConfirm,
}) {
  const strings = getStrings(language);
  const hasText = transcript.trim().length > 0;
  const displayText = transcript + (interimTranscript ? ` ${interimTranscript}` : '');

  // Keyboard: Escape closes
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label="Voice input"
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
    >
      {/* Panel */}
      <div className="relative w-full max-w-sm mx-4 mb-4 sm:mb-0 rounded-3xl bg-white dark:bg-[#111A15] border border-border dark:border-charcoal-800 shadow-2xl overflow-hidden animate-slideUp">

        {/* Top handle bar */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 rounded-full bg-charcoal-200 dark:bg-charcoal-700" />
        </div>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-full text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700 dark:hover:bg-charcoal-800 dark:hover:text-sand-100 transition"
          aria-label={strings.close}
        >
          <X className="w-5 h-5" />
        </button>

        <div className="px-6 pb-7 pt-2 flex flex-col items-center gap-4">
          {/* Title */}
          <div className="text-center">
            <p className="text-lg font-bold text-charcoal-900 dark:text-sand-50">
              {isListening ? strings.title : strings.speak}
            </p>
            <p className="text-xs text-charcoal-500 dark:text-charcoal-400 mt-0.5">
              {strings.hint}
            </p>
          </div>

          {/* Language selector chips */}
          <div className="flex flex-wrap justify-center gap-1.5 w-full">
            {QUICK_VOICE_LANGS.map((l) => {
              const active = language === l.code;
              return (
                <button
                  key={l.code}
                  type="button"
                  onClick={() => onLanguageChange && onLanguageChange(l.code)}
                  className={`px-2.5 py-1 rounded-full text-xs font-semibold transition ${
                    active
                      ? 'bg-forest-600 text-white shadow-2xs dark:bg-emerald-600'
                      : 'bg-sand-100 dark:bg-charcoal-800 text-charcoal-600 dark:text-charcoal-300 hover:bg-sand-200 dark:hover:bg-charcoal-700'
                  }`}
                >
                  {l.label}
                </button>
              );
            })}
          </div>

          {/* Waveform */}
          <WaveformBars active={isListening} />

          {/* Big Mic Button */}
          {speechSupported ? (
            <button
              onClick={onToggleListening}
              className={`relative flex h-20 w-20 items-center justify-center rounded-full shadow-xl transition-all duration-200 focus:outline-none focus:ring-4 ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600 focus:ring-red-300 scale-110'
                  : 'bg-forest-600 hover:bg-forest-700 focus:ring-forest-200 dark:bg-emerald-600 dark:hover:bg-emerald-500'
              }`}
              aria-label={isListening ? strings.stop : strings.speak}
              aria-pressed={isListening}
            >
              {isListening ? (
                <MicOff className="w-8 h-8 text-white" />
              ) : (
                <Mic className="w-8 h-8 text-white" />
              )}
              {/* Pulse ring when active */}
              {isListening && (
                <span className="absolute inset-0 rounded-full border-4 border-red-400 animate-ping opacity-60" />
              )}
            </button>
          ) : (
            <div className="text-center px-4">
              <p className="text-sm text-red-600 dark:text-red-400 font-medium">
                Voice input is not supported in this browser.
              </p>
              <p className="text-xs text-charcoal-400 mt-1">
                Try Chrome or Edge on Android/Desktop.
              </p>
            </div>
          )}

          {/* Error state */}
          {micError && (
            <div className="w-full rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 px-4 py-3 text-sm text-red-700 dark:text-red-400 text-center">
              {micError}
            </div>
          )}

          {/* Live transcript display */}
          <div
            className={`w-full min-h-[64px] rounded-2xl border px-4 py-3 text-sm transition-all ${
              hasText
                ? 'border-forest-300 bg-forest-50 dark:border-emerald-800 dark:bg-emerald-950/30 text-charcoal-900 dark:text-sand-50'
                : 'border-dashed border-charcoal-200 dark:border-charcoal-700 text-charcoal-400 dark:text-charcoal-500'
            }`}
          >
            {displayText || strings.placeholder}
            {interimTranscript && (
              <span className="text-charcoal-400 dark:text-charcoal-500 italic"> {strings.interim}</span>
            )}
          </div>

          {/* Action buttons */}
          <div className="flex w-full gap-3">
            {hasText && (
              <button
                onClick={onRetry}
                className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-charcoal-200 dark:border-charcoal-700 bg-white dark:bg-[#15201A] py-3 text-sm font-semibold text-charcoal-700 dark:text-charcoal-200 hover:bg-sand-50 dark:hover:bg-charcoal-800 transition"
              >
                <RefreshCw className="w-4 h-4" />
                {strings.retry}
              </button>
            )}
            <button
              onClick={() => onConfirm(transcript.trim())}
              disabled={!hasText}
              className={`flex flex-1 items-center justify-center gap-2 rounded-xl py-3 text-sm font-bold shadow-sm transition ${
                hasText
                  ? 'bg-forest-600 hover:bg-forest-700 dark:bg-emerald-600 dark:hover:bg-emerald-500 text-white cursor-pointer'
                  : 'bg-charcoal-100 dark:bg-charcoal-800 text-charcoal-400 cursor-not-allowed'
              }`}
            >
              <Check className="w-4 h-4" />
              {strings.done}
            </button>
          </div>
        </div>
      </div>

      {/* Slide-up animation */}
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(60px); opacity: 0; }
          to   { transform: translateY(0);    opacity: 1; }
        }
        .animate-slideUp { animation: slideUp 0.25s cubic-bezier(0.16,1,0.3,1) forwards; }
      `}</style>
    </div>
  );
}
