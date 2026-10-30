import React, { useState } from 'react';
import { HelpCircle, ArrowRight, CheckCircle2, ChevronDown, Check } from 'lucide-react';

export default function DynamicQuestionnaireCard({
  questions = [],
  onSubmitBatch,
  isHindi = false,
  isSubmitting = false
}) {
  const [formValues, setFormValues] = useState({});
  const [hasSubmitted, setHasSubmitted] = useState(false);

  if (!questions || questions.length === 0) return null;

  const totalQuestions = questions.length;
  const answeredCount = Object.keys(formValues).filter(k => formValues[k] !== undefined && formValues[k] !== '').length;

  const handleSelectOption = (fieldKey, value) => {
    setFormValues(prev => ({ ...prev, [fieldKey]: value }));
  };

  const handleSubmitAll = (e) => {
    if (e) e.preventDefault();
    if (answeredCount === 0 || isSubmitting) return;
    setHasSubmitted(true);
    if (onSubmitBatch) {
      onSubmitBatch(formValues);
    }
  };

  if (hasSubmitted) {
    return (
      <div className="my-3 rounded-xl border border-emerald-300 dark:border-emerald-800/80 bg-emerald-50/70 dark:bg-[#0E1E16] p-3 text-xs flex items-center justify-between gap-2 shadow-2xs animate-fadeIn">
        <div className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span className="font-semibold">
            {isHindi ? 'विवरण सफलतापूर्वक जमा किए गए - नीचे पात्रता मूल्यांकन देखें' : 'Eligibility details submitted - Full evaluation generated below'}
          </span>
        </div>
        <button
          type="button"
          onClick={() => setHasSubmitted(false)}
          className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 hover:underline shrink-0 cursor-pointer"
        >
          {isHindi ? 'संशोधन करें' : 'Edit Answers'}
        </button>
      </div>
    );
  }

  return (
    <div className="my-4 rounded-2xl border border-amber-200/90 dark:border-amber-800/60 bg-amber-50/40 dark:bg-[#1A1409]/80 p-4 sm:p-5 shadow-subtle">
      {/* Header */}
      <div className="flex items-start justify-between gap-2.5 mb-3.5">
        <div className="flex items-start gap-2.5">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 shrink-0 mt-0.5">
            <HelpCircle className="h-4 w-4 text-amber-700 dark:text-amber-400" />
          </span>
          <div>
            <h4 className="text-sm font-bold text-charcoal-900 dark:text-amber-100">
              {isHindi ? 'पात्रता निर्धारण हेतु विवरण दर्ज करें' : 'Confirm Your Eligibility Details'}
            </h4>
            <p className="text-xs text-charcoal-500 dark:text-amber-200/80">
              {isHindi
                ? 'सटीक सब्सिडी राशि व पात्रता की पुष्टि हेतु कृपया नीचे दिए गए प्रश्नों का उत्तर दें:'
                : 'Select or enter all applicable details below to calculate your exact benefits:'}
            </p>
          </div>
        </div>

        {/* Progress Pill */}
        <span className="shrink-0 rounded-full bg-amber-100/80 dark:bg-amber-950 px-2.5 py-0.5 text-[11px] font-bold text-amber-900 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          {answeredCount}/{totalQuestions} {isHindi ? 'उत्तर दिए' : 'answered'}
        </span>
      </div>

      {/* Dynamic Questions Form */}
      <form onSubmit={handleSubmitAll} className="space-y-3.5">
        {questions.map((q, idx) => {
          const fieldKey = q.id || q.field || `field_${idx}`;
          const isDropdown = q.input_type === 'dropdown' || (q.options && q.options.length > 4);
          const isNumber = q.input_type === 'number' || (!isDropdown && (!q.options || q.options.length === 0));
          const currentValue = formValues[fieldKey];

          return (
            <div
              key={fieldKey}
              className={`rounded-xl border p-3.5 shadow-2xs transition-all ${
                currentValue !== undefined && currentValue !== ''
                  ? 'border-forest-200 bg-white dark:border-forest-800/80 dark:bg-[#121E18]'
                  : 'border-amber-200/60 bg-white dark:border-amber-900/60 dark:bg-[#151D18]'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <label className="text-xs font-semibold text-charcoal-900 dark:text-sand-50 flex items-center gap-1.5">
                  {currentValue !== undefined && currentValue !== '' && (
                    <Check className="h-3.5 w-3.5 text-forest-600 dark:text-emerald-400 stroke-[3]" />
                  )}
                  <span>{q.question || q.label}</span>
                </label>
                {q.required && (
                  <span className="text-[10px] font-medium text-amber-800 bg-amber-100/70 dark:bg-amber-950 dark:text-amber-300 px-1.5 py-0.2 rounded">
                    {isHindi ? 'अनिवार्य' : 'Required'}
                  </span>
                )}
              </div>

              {q.hint && (
                <p className="text-[11px] text-charcoal-500 dark:text-charcoal-400 mb-2.5">
                  {q.hint}
                </p>
              )}

              {/* 1. Dropdown for > 4 options */}
              {isDropdown ? (
                <div className="relative mt-1">
                  <select
                    disabled={isSubmitting}
                    value={currentValue || ''}
                    onChange={(e) => handleSelectOption(fieldKey, e.target.value)}
                    className="w-full appearance-none rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium text-charcoal-900 shadow-2xs focus:border-forest-600 focus:outline-none focus:ring-1 focus:ring-forest-600 cursor-pointer disabled:opacity-50 dark:border-charcoal-700 dark:bg-[#111A15] dark:text-sand-50 dark:focus:border-emerald-500"
                  >
                    <option value="" disabled>
                      {isHindi ? '-- विकल्प चुनें --' : '-- Select an option --'}
                    </option>
                    {q.options && q.options.map((opt, oIdx) => (
                      <option key={oIdx} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-2.5 h-3.5 w-3.5 text-charcoal-400 dark:text-charcoal-500" />
                </div>
              ) : isNumber ? (
                /* 2. Number input for monetary or numerical values */
                <div className="mt-1 flex items-center gap-2">
                  <input
                    type="number"
                    disabled={isSubmitting}
                    placeholder={isHindi ? 'संख्या या वार्षिक राशि (₹) दर्ज करें...' : 'Enter amount or value (e.g. 200000)...'}
                    value={currentValue || ''}
                    onChange={(e) => handleSelectOption(fieldKey, e.target.value)}
                    className="flex-1 rounded-lg border border-border bg-white px-3 py-2 text-xs font-medium text-charcoal-900 shadow-2xs focus:border-forest-600 focus:outline-none focus:ring-1 focus:ring-forest-600 disabled:opacity-50 dark:border-charcoal-700 dark:bg-[#111A15] dark:text-sand-50 dark:focus:border-emerald-500"
                  />
                </div>
              ) : (
                /* 3. Pill buttons for <= 4 choices */
                <div className="mt-1 flex flex-wrap gap-2">
                  {q.options && q.options.map((opt, oIdx) => {
                    const isSelected = currentValue === opt;
                    return (
                      <button
                        key={oIdx}
                        type="button"
                        disabled={isSubmitting}
                        onClick={() => handleSelectOption(fieldKey, opt)}
                        className={`cursor-pointer rounded-lg px-3 py-1.5 text-xs font-medium transition active:scale-95 disabled:opacity-50 flex items-center gap-1.5 ${
                          isSelected
                            ? 'bg-forest-600 text-white font-semibold shadow-2xs dark:bg-emerald-600'
                            : 'border border-border bg-sand-50/70 text-charcoal-800 hover:border-forest-400 hover:bg-forest-50 hover:text-forest-900 dark:border-charcoal-700 dark:bg-[#111A15] dark:text-charcoal-300 dark:hover:bg-[#18261F] dark:hover:text-sand-100'
                        }`}
                      >
                        {isSelected && <Check className="h-3 w-3 stroke-[3]" />}
                        <span>{opt}</span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}

        {/* Unified Submit Button */}
        <div className="pt-2 flex items-center justify-between gap-3 border-t border-amber-200/80 dark:border-amber-900/60">
          <p className="text-[11px] text-charcoal-500 dark:text-charcoal-400">
            {answeredCount < totalQuestions
              ? (isHindi ? `कृपया सभी ${totalQuestions} प्रश्नों के उत्तर दें` : `Answer remaining fields for full accuracy`)
              : (isHindi ? 'सभी विवरण तैयार हैं' : 'All required details ready')}
          </p>

          <button
            type="submit"
            disabled={answeredCount === 0 || isSubmitting}
            className="inline-flex items-center gap-2 rounded-xl bg-forest-600 px-5 py-2.5 text-xs font-semibold text-white shadow-subtle hover:bg-forest-700 transition active:scale-95 disabled:opacity-40 disabled:hover:bg-forest-600 cursor-pointer dark:bg-emerald-600 dark:hover:bg-emerald-500"
          >
            <span>
              {isHindi
                ? `पात्रता की पुष्टि करें (${answeredCount}/${totalQuestions})`
                : `Submit Details & Evaluate (${answeredCount}/${totalQuestions})`}
            </span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
}
