import React from 'react';
import {
  ArrowRight,
  BadgeCheck,
  Briefcase,
  GraduationCap,
  Landmark,
  ShieldCheck,
  Sparkles,
  Sun,
  Wheat
} from 'lucide-react';

export default function EmptyState({ onSelectPrompt, language = 'en' }) {
  const isHindi = language === 'hi';

  const prompts = [
    {
      id: 'agriculture',
      icon: Wheat,
      number: '01',
      accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
      tag: isHindi ? 'कृषि एवं किसान' : 'Agriculture & farmers',
      title: isHindi
        ? 'किसान आय सहायता एवं सौर पंप सब्सिडी'
        : 'Income support & solar pumps',
      description: isHindi
        ? 'PM-KISAN ₹6,000 वार्षिक सहायता एवं PM-KUSUM सौर कृषि पंप अनुदान।'
        : 'Explore PM-KISAN income support and PM-KUSUM solar irrigation subsidies.',
      query: isHindi
        ? 'किसानों के लिए पीएम-किसान आय सहायता और पीएम-कुसुम सोलर पंप सब्सिडी योजनाओं की पात्रता और आवेदन प्रक्रिया बताएं।'
        : 'What are the eligibility criteria and application steps for PM-KISAN income support and PM-KUSUM solar irrigation pump subsidies?'
    },
    {
      id: 'education',
      icon: GraduationCap,
      number: '02',
      accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
      tag: isHindi ? 'उच्च शिक्षा एवं छात्रवृत्ति' : 'Education & scholarships',
      title: isHindi
        ? 'इंजीनियरिंग एवं उच्च शिक्षा छात्रवृत्ति'
        : 'Scholarships for higher education',
      description: isHindi
        ? 'PM-USP केंद्रीय क्षेत्र छात्रवृत्ति एवं ब्याज अनुदान शिक्षा ऋण योजनाएं।'
        : 'Explore PM-USP scholarships and interest-subsidized higher education loans.',
      query: isHindi
        ? 'बीटेक इंजीनियरिंग और कॉलेज छात्रों के लिए पीएम-यूएसपी छात्रवृत्ति और सरकारी शिक्षा ऋण की पात्रता बताएं।'
        : 'Find scholarship and education loan subsidy schemes for B.Tech engineering college students, such as PM-USP.'
    },
    {
      id: 'solar',
      icon: Sun,
      number: '03',
      accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
      tag: isHindi ? 'स्वच्छ ऊर्जा' : 'Clean energy',
      title: isHindi
        ? 'पीएम सूर्य घर मुफ्त बिजली योजना'
        : 'Rooftop solar with PM Surya Ghar',
      description: isHindi
        ? 'छत पर सोलर पैनल लगाने हेतु ₹78,000 तक की केंद्रीय सब्सिडी व शून्य बिजली बिल।'
        : 'Explore rooftop solar support, including the PM Surya Ghar subsidy.',
      query: isHindi
        ? 'पीएम सूर्य घर मुफ्त बिजली योजना के तहत छत पर सोलर पैनल लगाने की सब्सिडी, पात्रता और आवेदन प्रक्रिया क्या है?'
        : 'How do I apply for the PM Surya Ghar Muft Bijli Yojana rooftop solar subsidy, and what are the exact subsidy slabs?'
    },
    {
      id: 'enterprise',
      icon: Briefcase,
      number: '04',
      accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
      tag: isHindi ? 'महिला एवं लघु उद्योग' : 'Women & enterprise',
      title: isHindi
        ? 'मुद्रा ऋण एवं लखपति दीदी योजनाएं'
        : 'Loans for small businesses',
      description: isHindi
        ? 'बिना गारंटी ₹10 लाख तक का मुद्रा व्यापार ऋण एवं महिला आजीविका सहायता।'
        : 'Explore Mudra business loans and support for women-led enterprises.',
      query: isHindi
        ? 'नया छोटा व्यापार शुरू करने के लिए मुद्रा लोन और महिला स्वयं सहायता समूहों के लिए लखपति दीदी योजना की जानकारी दें।'
        : 'What government loan schemes exist for small startups and women entrepreneurs, like Mudra Yojana and Lakhpati Didi?'
    }
  ];

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-5 sm:px-7 sm:py-7 lg:px-10">
      <section className="navigator-hero relative overflow-hidden rounded-[1.75rem] text-white shadow-elevated">
        <div className="navigator-hero-art pointer-events-none absolute inset-0" aria-hidden="true" />
        <div className="relative grid gap-6 p-6 sm:p-9 md:grid-cols-[minmax(0,1.2fr)_minmax(250px,0.8fr)] md:items-center md:gap-5 lg:grid-cols-[1.3fr_0.7fr] lg:gap-8 lg:items-end lg:p-11">
          <div className="max-w-2xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-semibold text-emerald-50 backdrop-blur-sm">
              <Landmark className="h-4 w-4 text-amber-300" aria-hidden="true" />
              <span>{isHindi ? 'भारत की योजनाओं के लिए आपका मार्गदर्शक' : 'YOUR GUIDE TO INDIA’S PUBLIC BENEFITS'}</span>
            </div>

            <h2 className="max-w-xl text-3xl font-semibold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
              {isHindi
                ? 'सही सरकारी सहायता, आपके जीवन के लिए।'
                : 'Find support that fits your life.'}
            </h2>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-emerald-50/85 sm:text-base">
              {isHindi
                ? 'अपनी जरूरत बताएं। पात्रता समझें, लाभ जानें और आधिकारिक आवेदन तक पहुंचें।'
                : 'Tell us what you need. Understand eligibility, compare benefits, and find the official next step.'}
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs font-medium text-emerald-50/90 sm:text-sm">
              <span className="inline-flex items-center gap-2">
                <BadgeCheck className="h-4 w-4 text-amber-300" aria-hidden="true" />
                {isHindi ? 'आधिकारिक स्रोत' : 'Official sources'}
              </span>
              <span className="inline-flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-amber-300" aria-hidden="true" />
                {isHindi ? 'पात्रता पर स्पष्टता' : 'Eligibility, made clear'}
              </span>
            </div>
          </div>

          <div className="relative hidden min-h-48 items-center justify-center md:flex">
            <div className="absolute h-48 w-48 rounded-full border border-white/10" />
            <div className="absolute h-36 w-36 rounded-full border border-white/15" />
            <div className="relative w-full rounded-2xl border border-white/20 bg-white/10 p-4 shadow-2xl backdrop-blur-md sm:p-5">
              <div className="flex items-center justify-between border-b border-white/15 pb-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.16em] text-emerald-100/70">
                    {isHindi ? 'आपकी अगली शुरुआत' : 'A clearer way forward'}
                  </p>
                  <p className="mt-1 text-lg font-semibold">
                    {isHindi ? 'योजना से आवेदन तक' : 'Your path to support'}
                  </p>
                </div>
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-300 text-forest-950">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-4 space-y-3">
                {[
                  isHindi ? 'अपनी जरूरत साझा करें' : 'Share what you need',
                  isHindi ? 'योजनाएं और आधिकारिक जानकारी पाएं' : 'Find schemes and official next steps'
                ].map((step, index) => (
                  <div key={step} className="flex items-center gap-3 text-sm text-emerald-50">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-white/25 text-xs font-semibold text-amber-200">
                      {index + 1}
                    </span>
                    <span>{step}</span>
                    {index === 1 && <ArrowRight className="ml-auto h-4 w-4 text-amber-300" aria-hidden="true" />}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="relative h-1.5 w-full bg-gradient-to-r from-[#FF9933] via-white to-[#138808]" />
      </section>

      <section className="pb-3 pt-7 sm:pt-9" aria-labelledby="starting-points-title">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-forest-700 dark:text-emerald-400">
              {isHindi ? 'लोकप्रिय श्रेणियां' : 'A GOOD PLACE TO START'}
            </p>
            <h3 id="starting-points-title" className="mt-1 text-xl font-semibold tracking-tight text-charcoal-900 dark:text-sand-50 sm:text-2xl">
              {isHindi ? 'आपके लिए क्या महत्वपूर्ण है?' : 'What matters to you?'}
            </h3>
          </div>
          <p className="max-w-sm text-sm text-charcoal-500 dark:text-charcoal-300">
            {isHindi ? 'एक विषय चुनें या नीचे अपनी बात लिखें।' : 'Choose a topic, or describe your situation below.'}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {prompts.map((prompt) => {
            const Icon = prompt.icon;
            return (
              <button
                key={prompt.id}
                type="button"
                onClick={() => onSelectPrompt(prompt.query)}
                className="group flex min-h-36 items-start gap-4 rounded-2xl border border-border bg-white p-4 text-left shadow-subtle transition-all duration-200 hover:-translate-y-0.5 hover:border-forest-300 hover:shadow-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-forest-600 focus-visible:ring-offset-2 dark:border-charcoal-800 dark:bg-[#111A15] dark:hover:border-emerald-700 sm:p-5"
              >
                <span className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border ${prompt.accent}`}>
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold uppercase tracking-wide text-charcoal-500 dark:text-charcoal-300">
                      {prompt.tag}
                    </span>
                    <span className="text-xs font-semibold tabular-nums text-charcoal-400 dark:text-charcoal-500">{prompt.number}</span>
                  </span>
                  <span className="mt-2 block text-base font-semibold leading-snug text-charcoal-900 transition-colors group-hover:text-forest-700 dark:text-sand-50 dark:group-hover:text-emerald-300">
                    {prompt.title}
                  </span>
                  <span className="mt-1.5 block text-sm leading-relaxed text-charcoal-500 dark:text-charcoal-300">
                    {prompt.description}
                  </span>
                  <span className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-forest-700 dark:text-emerald-400">
                    {isHindi ? 'योजनाएं जानें' : 'Explore schemes'}
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" aria-hidden="true" />
                  </span>
                </span>
              </button>
            );
          })}
        </div>

        <div className="mt-5 flex items-center gap-2 border-t border-border/70 pt-4 text-sm text-charcoal-500 dark:border-charcoal-800 dark:text-charcoal-300">
          <ShieldCheck className="h-4 w-4 shrink-0 text-forest-600 dark:text-emerald-400" aria-hidden="true" />
          <span>
            {isHindi
              ? 'आधिकारिक सरकारी स्रोतों से जानकारी — अंतिम नियम संबंधित विभाग से जांचें।'
              : 'Information grounded in official government sources. Confirm final rules with the relevant department.'}
          </span>
        </div>
      </section>
    </div>
  );
}
