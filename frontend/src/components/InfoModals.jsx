import React from 'react';
import { X, ShieldCheck, Sparkles, ExternalLink, HelpCircle, Building2 } from 'lucide-react';

export function HelpModal({ isOpen, onClose, isHindi = false }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/50 backdrop-blur-xs">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-white p-6 shadow-elevated">
        <div className="flex items-center justify-between border-b border-border/80 pb-3">
          <div className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5 text-forest-600" />
            <h3 className="text-base font-bold text-charcoal-900">
              {isHindi ? 'जनसहायक AI का उपयोग कैसे करें' : 'How to Use JanSahayak AI'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 space-y-4 text-xs text-charcoal-700 leading-relaxed">
          <div className="rounded-xl bg-forest-50 p-3.5 border border-forest-100">
            <h4 className="font-bold text-forest-900 mb-1">
              {isHindi ? '1. अपनी आवश्यकता स्वाभाविक भाषा में बताएं' : '1. Describe your need in plain language'}
            </h4>
            <p>
              {isHindi
                ? 'उदाहरण: "मैं बीटेक का छात्र हूँ, मुझे छात्रवृत्ति चाहिए", या "छत पर सोलर पैनल लगवाने की सब्सिडी क्या है?"'
                : 'Example: "I am a B.Tech student needing an education scholarship", or "How to get a solar rooftop subsidy?"'}
            </p>
          </div>

          <div className="rounded-xl bg-sand-50 p-3.5 border border-border">
            <h4 className="font-bold text-charcoal-900 mb-1">
              {isHindi ? '2. परस्पर संवादात्मक प्रश्नों के उत्तर दें' : '2. Answer dynamic eligibility cards'}
            </h4>
            <p>
              {isHindi
                ? 'यदि योजना के लिए आपकी आय, राज्य, या श्रेणी की जानकारी आवश्यक है, तो AI केवल छूटे हुए विवरण पूछेगा।'
                : 'If a candidate scheme requires your income tier or state, the AI dynamically prompts only the missing fields.'}
            </p>
          </div>

          <div className="rounded-xl bg-sand-50 p-3.5 border border-border">
            <h4 className="font-bold text-charcoal-900 mb-1">
              {isHindi ? '3. आधिकारिक सरकारी पोर्टल पर आवेदन करें' : '3. Apply directly on verified portals'}
            </h4>
            <p>
              {isHindi
                ? 'दस्तावेज चेकलिस्ट प्राप्त करने के बाद, दिए गए आधिकारिक *.gov.in लिंक पर जाकर आवेदन पूरा करें।'
                : 'After reviewing required documents and benefit breakdowns, click the verified *.gov.in link to apply.'}
            </p>
          </div>
        </div>

        <div className="mt-6 border-t border-border/80 pt-3 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-xl bg-forest-600 px-4 py-2 text-xs font-semibold text-white hover:bg-forest-700 transition"
          >
            {isHindi ? 'समझ गया' : 'Got it'}
          </button>
        </div>
      </div>
    </div>
  );
}

export function AboutModal({ isOpen, onClose, isHindi = false }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal-900/50 backdrop-blur-xs">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-white p-6 shadow-elevated">
        <div className="flex items-center justify-between border-b border-border/80 pb-3">
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-forest-600" />
            <h3 className="text-base font-bold text-charcoal-900">
              {isHindi ? 'जनसहायक के बारे में' : 'About JanSahayak'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-charcoal-400 hover:bg-sand-100 hover:text-charcoal-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 space-y-3.5 text-xs text-charcoal-700 leading-relaxed">
          <p>
            <strong>JanSahayak</strong> {isHindi
              ? 'भारतीय नागरिकों के लिए एक उन्नत स्वायत्त कल्याण सहायक है, जो केंद्रीय एवं राज्य सरकार की योजनाओं को खोजने, पात्रता की पुष्टि करने एवं आवेदन प्रक्रिया को सरल बनाने हेतु डिज़ाइन किया गया है।'
              : 'is a premium AI welfare navigator engineered for Indian citizens. It bridges the gap between complex government gazettes and citizens seeking financial assistance, education loans, healthcare, and subsidies.'}
          </p>

          <div className="rounded-xl bg-forest-50 p-3 border border-forest-100 text-forest-900">
            <div className="flex items-center gap-2 font-bold mb-1">
              <ShieldCheck className="h-4 w-4 text-forest-600" />
              <span>{isHindi ? '100% आधिकारिक डेटा प्रतिबद्धता' : '100% Official Source Grounding'}</span>
            </div>
            <p>
              {isHindi
                ? 'सभी पात्रता नियम एवं सब्सिडी विवरण myScheme.gov.in एवं भारत सरकार के आधिकारिक डोमेन (*.gov.in, *.nic.in) से सत्यापित किए जाते हैं।'
                : 'All eligibility criteria, benefit amounts, and procedural steps are strictly verified against myScheme.gov.in and official Government of India domains.'}
            </p>
          </div>

          <p className="text-[11px] text-charcoal-400">
            {isHindi
              ? 'अस्वीकरण: जनसहायक एक सूचना सहायक है। अंतिम स्वीकृति संबंधित मंत्रालय या नोडल विभाग के नियमों के अधीन है।'
              : 'Disclaimer: JanSahayak provides informational navigation. Official approvals and disbursement remain subject to nodal ministry rules.'}
          </p>
        </div>

        <div className="mt-6 border-t border-border/80 pt-3 flex items-center justify-between">
          <a
            href="https://www.myscheme.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-semibold text-forest-700 hover:underline flex items-center gap-1"
          >
            <span>myScheme.gov.in</span>
            <ExternalLink className="h-3 w-3" />
          </a>

          <button
            onClick={onClose}
            className="rounded-xl bg-forest-600 px-4 py-2 text-xs font-semibold text-white hover:bg-forest-700 transition"
          >
            {isHindi ? 'बंद करें' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
}
