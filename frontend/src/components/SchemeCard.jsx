import React, { useState } from 'react';
import {
  CheckCircle2, XCircle, HelpCircle, ExternalLink, MessageSquare,
  FileText, ShieldCheck, ChevronRight, Award, Info, Sparkles, Check
} from 'lucide-react';

export default function SchemeCard({ scheme, onAskAi, isHindi = false }) {
  // Tabs: 'overview', 'eligibility', 'documents', 'apply', 'check'
  const [activeCardTab, setActiveCardTab] = useState('overview');

  // Interactive self-check state for the 'check' tab
  const [selfCheckAnswers, setSelfCheckAnswers] = useState({});

  if (!scheme) return null;

  const schemeName = scheme.name || scheme.scheme_name || 'Government Scheme';
  const ministry = scheme.ministry || scheme.department || 'Government of India';
  const level = scheme.level || scheme.jurisdiction || 'Central';
  const state = scheme.state || (level === 'Central' ? 'All India' : '');
  const category = scheme.category || 'Welfare Scheme';
  const brief = scheme.brief || scheme.repository_summary || scheme.benefit || '';
  const url = scheme.url || (scheme.sources && scheme.sources[0]?.url) || 'https://www.myscheme.gov.in';

  // Normalize benefits
  const benefitsList = Array.isArray(scheme.benefits)
    ? scheme.benefits.map(b => (typeof b === 'string' ? b : b.text || b.benefit || ''))
    : (scheme.benefit ? [scheme.benefit] : []);

  // Normalize eligibility rules
  const rulesList = Array.isArray(scheme.eligibility_rules)
    ? scheme.eligibility_rules
    : (Array.isArray(scheme.rules_checked) ? scheme.rules_checked : []);

  // Normalize documents
  const docsList = Array.isArray(scheme.documents) && scheme.documents.length > 0
    ? scheme.documents
    : [
        'Aadhaar Card (identity proof)',
        'Bank Account Passbook seeded with Aadhaar / NPCI',
        'Residence / Domicile Certificate',
        'Income Certificate / Ration Card (if applicable)'
      ];

  // Normalize application steps
  const stepsList = Array.isArray(scheme.application_steps) && scheme.application_steps.length > 0
    ? scheme.application_steps.map(s => (typeof s === 'string' ? s : s.text || s.step || ''))
    : [
        'Visit the official scheme / department portal via myScheme.',
        'Authenticate using your Aadhaar number or DigiLocker account.',
        'Complete the online registration form with personal and bank details.',
        'Upload verified copies of required documents.',
        'Submit application and save the DBT acknowledgement number for tracking.'
      ];

  // Self-check evaluator
  const handleToggleCheck = (ruleIdx, val) => {
    setSelfCheckAnswers(prev => ({ ...prev, [ruleIdx]: val }));
  };

  const totalChecks = rulesList.length;
  const answeredCount = Object.keys(selfCheckAnswers).length;
  const yesCount = Object.values(selfCheckAnswers).filter(v => v === 'YES').length;
  const noCount = Object.values(selfCheckAnswers).filter(v => v === 'NO').length;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 hover:border-emerald-300 shadow-xs hover:shadow-md transition-all overflow-hidden flex flex-col">
      {/* Header Bar */}
      <div className="p-4 sm:p-5 border-b border-slate-100 bg-slate-50/50">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
          <div className="space-y-1.5 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-blue-50 text-blue-800 border border-blue-200">
                {level === 'Central' ? (isHindi ? 'केंद्रीय सरकार' : 'Central Government') : (state || 'State')}
              </span>
              <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                {category}
              </span>
              {scheme.match_percentage !== undefined && (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 inline-flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{scheme.match_percentage}% {isHindi ? 'मिलान' : 'Match'}</span>
                </span>
              )}
            </div>

            <h4 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
              {schemeName}
            </h4>
            <p className="text-xs font-semibold text-slate-500">
              {ministry}
            </p>
          </div>

          {/* Ask AI button */}
          {onAskAi && (
            <button
              type="button"
              onClick={() => onAskAi(schemeName)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold text-xs border border-emerald-200 transition shrink-0 self-start"
              title="Ask AI Assistant about this scheme"
            >
              <MessageSquare className="w-3.5 h-3.5 text-emerald-700" />
              <span>{isHindi ? 'AI से पूछें' : 'Ask AI'}</span>
            </button>
          )}
        </div>
      </div>

      {/* 5 Interactive Tabs Header */}
      <div className="flex items-center border-b border-slate-200 bg-slate-100/70 px-2 sm:px-4 gap-1 overflow-x-auto custom-scrollbar">
        {[
          { id: 'overview', label: isHindi ? 'विवरण एवं लाभ' : 'Overview & Benefits', icon: '📋' },
          { id: 'eligibility', label: isHindi ? 'पात्रता मापदंड' : 'Eligibility Criteria', icon: '🛡️' },
          { id: 'documents', label: isHindi ? 'दस्तावेज़' : 'Documents', icon: '📄' },
          { id: 'apply', label: isHindi ? 'आवेदन प्रक्रिया' : 'How to Apply', icon: '📝' },
          { id: 'check', label: isHindi ? 'पात्रता जांचें' : 'Check Eligibility', icon: '✅' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveCardTab(tab.id)}
            className={`cursor-pointer px-3 py-2.5 text-xs font-bold transition-all whitespace-nowrap flex items-center gap-1.5 border-b-2 ${
              activeCardTab === tab.id
                ? 'border-emerald-700 text-emerald-800 bg-white shadow-2xs'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      <div className="p-4 sm:p-5 flex-1">
        {/* TAB 1: OVERVIEW & BENEFITS */}
        {activeCardTab === 'overview' && (
          <div className="space-y-4">
            {brief && (
              <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                {brief}
              </p>
            )}

            {benefitsList.length > 0 && (
              <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200/80 space-y-2">
                <span className="text-xs font-bold text-emerald-950 uppercase tracking-wider block">
                  {isHindi ? 'प्रमुख वित्तीय एवं कल्याणकारी लाभ' : 'Key Financial & Welfare Benefits'}
                </span>
                <ul className="space-y-1.5">
                  {benefitsList.map((b, idx) => (
                    <li key={idx} className="text-xs text-slate-800 flex items-start gap-2">
                      <span className="text-emerald-700 font-bold shrink-0">✓</span>
                      <span>{b}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ELIGIBILITY CRITERIA */}
        {activeCardTab === 'eligibility' && (
          <div className="space-y-3">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
              {isHindi ? 'आधिकारिक पात्रता नियम एवं शर्तें' : 'Official Eligibility Criteria & Rules'}
            </span>

            {rulesList.length > 0 ? (
              <div className="grid grid-cols-1 gap-2">
                {rulesList.map((rule, rIdx) => {
                  const ruleText = rule.rule_label || rule.rule_text || rule.label || (rule.field ? `${rule.field}: ${rule.value}` : 'Eligible citizen');
                  const evidence = rule.evidence_quote || '';
                  const status = rule.status || 'PASS';

                  return (
                    <div
                      key={rIdx}
                      className="p-3 rounded-xl border border-slate-200 bg-slate-50/60 flex items-start justify-between gap-3"
                    >
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                          <span className="text-xs font-bold text-slate-900">{ruleText}</span>
                        </div>
                        {evidence && (
                          <p className="text-[11px] text-slate-500 italic pl-6">
                            "{evidence}"
                          </p>
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 shrink-0">
                        Verified
                      </span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                {isHindi ? 'सभी भारतीय नागरिक इस योजना के सामान्य दिशानिर्देशों के तहत पात्र हैं।' : 'Open to all eligible citizens fulfilling standard government guidelines.'}
              </p>
            )}
          </div>
        )}

        {/* TAB 3: DOCUMENTS REQUIRED */}
        {activeCardTab === 'documents' && (
          <div className="space-y-3">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
              {isHindi ? 'आवेदन हेतु आवश्यक दस्तावेज़' : 'Mandatory Documents Checklist'}
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {docsList.map((doc, dIdx) => (
                <div
                  key={dIdx}
                  className="p-3 rounded-xl border border-slate-200 bg-slate-50/50 flex items-center gap-2.5 text-xs font-medium text-slate-800"
                >
                  <FileText className="w-4 h-4 text-emerald-700 shrink-0" />
                  <span>{doc}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: HOW TO APPLY */}
        {activeCardTab === 'apply' && (
          <div className="space-y-3">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
              {isHindi ? 'चरण-दर-चरण आवेदन प्रक्रिया' : 'Step-by-Step Application Process'}
            </span>
            <div className="space-y-2">
              {stepsList.map((step, sIdx) => (
                <div
                  key={sIdx}
                  className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 bg-slate-50/60 text-xs text-slate-800"
                >
                  <span className="w-5 h-5 rounded-full bg-emerald-700 text-white font-bold text-[11px] flex items-center justify-center shrink-0">
                    {sIdx + 1}
                  </span>
                  <span className="flex-1 leading-relaxed">{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: CHECK ELIGIBILITY (INTERACTIVE QUESTIONNAIRE) */}
        {activeCardTab === 'check' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold text-slate-800 uppercase tracking-wider block">
                  {isHindi ? 'स्वयं पात्रता जांच (Self-Eligibility Questionnaire)' : 'Interactive Eligibility Self-Check'}
                </span>
                <p className="text-[11px] text-slate-500">
                  {isHindi ? 'प्रत्येक नियम के लिए हाँ या नहीं चुनें और तुरंत अपनी पात्रता देखें:' : 'Answer Yes/No for each rule to verify if you qualify:'}
                </p>
              </div>

              {answeredCount > 0 && (
                <button
                  type="button"
                  onClick={() => setSelfCheckAnswers({})}
                  className="text-[11px] text-emerald-700 hover:underline font-semibold"
                >
                  {isHindi ? 'रीसेट' : 'Reset'}
                </button>
              )}
            </div>

            {/* Checklist of rules with Yes/No toggle buttons */}
            <div className="space-y-2.5">
              {(rulesList.length > 0 ? rulesList : [
                { rule_label: 'Resident citizen of India' },
                { rule_label: 'Meets targeted demographic category' }
              ]).map((rule, idx) => {
                const label = rule.rule_label || rule.rule_text || rule.label || (rule.field ? `${rule.field}: ${rule.value}` : `Condition ${idx + 1}`);
                const userAns = selfCheckAnswers[idx];

                return (
                  <div
                    key={idx}
                    className="p-3 rounded-xl border border-slate-200 bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <span className="text-xs font-medium text-slate-800 flex-1">
                      {label}
                    </span>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        type="button"
                        onClick={() => handleToggleCheck(idx, 'YES')}
                        className={`cursor-pointer px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ${
                          userAns === 'YES'
                            ? 'bg-emerald-600 text-white shadow-xs'
                            : 'bg-white border border-slate-300 text-slate-700 hover:bg-emerald-50 hover:border-emerald-500'
                        }`}
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>{isHindi ? 'हाँ' : 'Yes'}</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => handleToggleCheck(idx, 'NO')}
                        className={`cursor-pointer px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ${
                          userAns === 'NO'
                            ? 'bg-red-600 text-white shadow-xs'
                            : 'bg-white border border-slate-300 text-slate-700 hover:bg-red-50 hover:border-red-400'
                        }`}
                      >
                        <XCircle className="w-3.5 h-3.5" />
                        <span>{isHindi ? 'नहीं' : 'No'}</span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Live Verdict Banner */}
            {answeredCount > 0 && (
              <div className={`p-4 rounded-xl border transition-all ${
                noCount > 0
                  ? 'bg-amber-50 border-amber-300 text-amber-900'
                  : yesCount === Math.max(rulesList.length, 1)
                  ? 'bg-emerald-50 border-emerald-300 text-emerald-950'
                  : 'bg-blue-50 border-blue-200 text-blue-900'
              }`}>
                <div className="flex items-center gap-2">
                  {noCount > 0 ? (
                    <HelpCircle className="w-5 h-5 text-amber-700 shrink-0" />
                  ) : yesCount === Math.max(rulesList.length, 1) ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                  ) : (
                    <Info className="w-5 h-5 text-blue-600 shrink-0" />
                  )}

                  <div>
                    <h5 className="text-xs font-bold">
                      {noCount > 0
                        ? (isHindi ? 'आप कुछ मापदंड पूरे नहीं करते' : 'May Not Fully Qualify')
                        : yesCount === Math.max(rulesList.length, 1)
                        ? (isHindi ? '🎉 बधाई! आप इस योजना के पूर्णतः पात्र प्रतीत होते हैं' : '🎉 Eligible: You appear to meet all criteria!')
                        : (isHindi ? 'शेष प्रश्नों के उत्तर दें' : 'Answer all conditions to get your final verdict')}
                    </h5>
                    <p className="text-[11px] mt-0.5 opacity-90">
                      {noCount > 0
                        ? (isHindi ? 'कृपया अन्य संबंधित योजनाओं की जांच करें या छूट नियमों की पुष्टि हेतु पोर्टल देखें।' : 'You marked No on at least one mandatory rule. You can still apply if relaxations exist.')
                        : yesCount === Math.max(rulesList.length, 1)
                        ? (isHindi ? 'आप नीचे दिए गए लिंक से आधिकारिक पोर्टल पर सीधा आवेदन कर सकते हैं।' : 'Click the button below to visit myScheme and start your application.')
                        : `${answeredCount} of ${Math.max(rulesList.length, 1)} conditions answered.`}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Card Action Footer */}
      <div className="p-3 sm:px-5 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-3 text-xs">
        <span className="text-[11px] text-slate-500 font-medium">
          {isHindi ? 'सत्यापित आधिकारिक पोर्टल' : 'Official National Repository'}
        </span>

        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 hover:bg-emerald-800 text-white font-bold text-xs shadow-xs transition"
        >
          <span>{isHindi ? 'myScheme पर देखें' : 'View on myScheme.gov.in'}</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    </div>
  );
}
