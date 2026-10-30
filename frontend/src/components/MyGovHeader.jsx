import React from 'react';
import { Bot, CheckCircle, Sparkles, Languages, Shield, ExternalLink, HelpCircle } from 'lucide-react';

export default function MyGovHeader({ activeTab, setActiveTab, language, setLanguage, fontSize, setFontSize }) {
  const isHindi = language === 'hi';

  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm border-b border-slate-200">
      {/* 1. Indian Tricolor Accent Strip */}
      <div className="h-1.5 w-full flex">
        <div className="h-full w-1/3 bg-[#FF9933]" title="Saffron" />
        <div className="h-full w-1/3 bg-white border-y border-slate-200" title="White" />
        <div className="h-full w-1/3 bg-[#138808]" title="India Green" />
      </div>

      {/* 2. Official Government of India Top Banner */}
      <div className="bg-[#f8fafc] border-b border-slate-200 px-4 py-1.5 text-xs text-slate-600">
        <div className="mx-auto max-w-7xl flex items-center justify-between">
          <div className="flex items-center gap-2">
            {/* National Emblem SVG */}
            <svg viewBox="0 0 24 24" className="w-5 h-5 text-amber-700" fill="currentColor">
              <path d="M12 2L14.5 7H19.5L15.5 10.5L17 15.5L12 12.5L7 15.5L8.5 10.5L4.5 7H9.5L12 2Z" />
            </svg>
            <span className="font-semibold text-slate-800">
              {isHindi ? 'भारत सरकार' : 'GOVERNMENT OF INDIA'}
            </span>
            <span className="text-slate-300">|</span>
            <span className="hidden sm:inline text-slate-500">
              {isHindi ? 'राष्ट्रीय योजना खोज और पात्रता मंच' : 'Ministry of Electronics & Information Technology'}
            </span>
          </div>

          <div className="flex items-center gap-3">
            {/* Font size adjustments */}
            <div className="hidden sm:flex items-center border border-slate-300 rounded px-1.5 py-0.5 bg-white text-[11px] font-medium text-slate-600 gap-1">
              <button
                type="button"
                onClick={() => setFontSize('sm')}
                className={`px-1 rounded hover:bg-slate-100 ${fontSize === 'sm' ? 'text-emerald-700 font-bold' : ''}`}
                title="Small font"
              >
                A-
              </button>
              <span>|</span>
              <button
                type="button"
                onClick={() => setFontSize('md')}
                className={`px-1 rounded hover:bg-slate-100 ${fontSize === 'md' ? 'text-emerald-700 font-bold' : ''}`}
                title="Normal font"
              >
                A
              </button>
              <span>|</span>
              <button
                type="button"
                onClick={() => setFontSize('lg')}
                className={`px-1 rounded hover:bg-slate-100 ${fontSize === 'lg' ? 'text-emerald-700 font-bold' : ''}`}
                title="Large font"
              >
                A+
              </button>
            </div>

            {/* Language Switcher */}
            <button
              type="button"
              onClick={() => setLanguage(isHindi ? 'en' : 'hi')}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border border-emerald-600 bg-emerald-50 text-emerald-800 hover:bg-emerald-100 font-semibold transition text-xs"
              title="Toggle Language"
            >
              <Languages className="w-3.5 h-3.5 text-emerald-700" />
              <span>{isHindi ? 'English' : 'हिन्दी'}</span>
            </button>

            {/* Official Portal Link */}
            <a
              href="https://www.myscheme.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden md:inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-emerald-700 font-medium"
              title="Official portal"
            >
              <span>myscheme.gov.in</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>

      {/* 3. Main Header & Navigation */}
      <div className="mx-auto max-w-7xl px-4 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Logo Section */}
        <div className="flex items-center gap-3">
          <div className="flex items-center">
            <span className="text-3xl font-extrabold tracking-tight text-[#0F2C59] font-sans">
              my
            </span>
            <span className="text-3xl font-extrabold tracking-tight text-[#16A34A] font-sans">
              Scheme
            </span>
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300 uppercase tracking-wider">
              Portal Wrapper
            </span>
          </div>

          <div className="hidden lg:block border-l border-slate-300 pl-3">
            <p className="text-xs font-semibold text-slate-700 leading-tight">
              {isHindi ? 'योजना खोज एवं पात्रता सहायक' : 'One-stop Scheme Discovery & Eligibility Engine'}
            </p>
            <p className="text-[11px] text-slate-500">
              {isHindi ? 'केंद्रीय एवं राज्य सरकार की योजनाएं' : 'Central & State Government Schemes'}
            </p>
          </div>
        </div>

        {/* 2 Exclusive Action Tabs */}
        <nav className="relative z-10 flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button
            type="button"
            onClick={() => setActiveTab('ai-assistant')}
            className={`cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-xs ${
              activeTab === 'ai-assistant'
                ? 'bg-emerald-700 text-white shadow-md'
                : 'text-slate-700 hover:bg-white/80 hover:text-slate-900'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span>{isHindi ? 'myScheme AI सहायक' : 'myScheme AI Assistant'}</span>
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
              activeTab === 'ai-assistant' ? 'bg-emerald-800 text-emerald-100' : 'bg-slate-200 text-slate-700'
            }`}>
              AI
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('eligibility')}
            className={`cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all shadow-xs ${
              activeTab === 'eligibility'
                ? 'bg-[#0F2C59] text-white shadow-md'
                : 'text-slate-700 hover:bg-white/80 hover:text-slate-900'
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            <span>{isHindi ? 'पात्रता जांचें (5-स्टेप)' : 'Check Eligibility (5-Step Wizard)'}</span>
            <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
              activeTab === 'eligibility' ? 'bg-blue-900 text-blue-100' : 'bg-slate-200 text-slate-700'
            }`}>
              {isHindi ? 'खोजें' : 'Wizard'}
            </span>
          </button>
        </nav>
      </div>
    </header>
  );
}
