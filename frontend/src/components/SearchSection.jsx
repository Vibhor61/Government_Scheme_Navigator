import React, { useState } from 'react';
import { Search, Sparkles, Filter, ArrowRight, Lightbulb } from 'lucide-react';
import GroundedAnswerCard from './GroundedAnswerCard';
import { askQuestion } from '../services/api';

const SAMPLE_QUERIES = [
  {
    label: "🌾 Small Farmer Support",
    text: "I am a small farmer with 2 acres of land. Are there direct cash assistance schemes for buying seeds and fertilizers?"
  },
  {
    label: "🏥 Elderly Health Coverage",
    text: "My grandmother is 72 years old. Does Ayushman Bharat cover senior citizens for free hospital surgeries?"
  },
  {
    label: "🎓 Girl Child Scholarship",
    text: "My daughter is studying in 1st year B.Tech in an AICTE approved college. Is there any scholarship for girl students?"
  },
  {
    label: "🏪 Street Vendor Loan",
    text: "I run a small vegetable vending cart. How can I get a collateral-free loan with interest subsidy?"
  },
  {
    label: "🔨 Traditional Artisan Grant",
    text: "I work as a carpenter. Is there any scheme offering free modern toolkits and concessional loan?"
  },
  {
    label: "💰 Girl Child Savings",
    text: "How to open a high interest, tax-free savings deposit for my 5 year old daughter?"
  }
];

const CATEGORIES = ["All", "Agriculture", "Healthcare", "Education", "Employment", "Social Security", "Women & Child"];

export default function SearchSection() {
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (textToSearch = query) => {
    const q = textToSearch.trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    try {
      const categoryParam = selectedCategory === 'All' ? null : selectedCategory;
      const res = await askQuestion(q, categoryParam, true);
      setResult(res);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Error communicating with assistant.');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleClick = (sampleText) => {
    setQuery(sampleText);
    handleSearch(sampleText);
  };

  return (
    <div className="space-y-10">
      {/* Hero Intro */}
      <div className="text-center max-w-4xl mx-auto space-y-4 pt-2 sm:pt-4">
        <div className="inline-flex items-center space-x-2 bg-[#e1eee2] text-[#285b43] px-4 py-2 rounded-full text-sm font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
          <span>Hybrid Retrieval-Augmented Generation (RAG)</span>
        </div>
        <h2 className="text-4xl sm:text-5xl font-semibold text-[#1b3027] leading-[1.08]">
          Find Government Schemes in Plain Language
        </h2>
        <p className="text-lg text-slate-600 leading-relaxed max-w-3xl mx-auto">
          Describe your occupation, family situation, or requirement in simple words. Our AI verifies official eligibility guidelines and delivers source-grounded answers.
        </p>
      </div>

      {/* Main Search Bar Card */}
      <div className="bg-white rounded-2xl p-4 sm:p-7 border border-[#dce5dc] shadow-[0_18px_50px_-32px_rgba(28,66,45,0.38)] space-y-5 max-w-5xl mx-auto">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="relative flex items-center"
        >
          <Search className="w-5 h-5 text-[#557361] absolute left-4 pointer-events-none" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Tell us about your situation, family, or the support you need..."
            className="w-full pl-12 pr-32 py-4 sm:py-5 rounded-xl text-base border border-[#d9e3da] focus:outline-none focus:ring-2 focus:ring-emerald-600/30 focus:border-emerald-700 transition bg-[#f8faf7]"
          />
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="absolute right-2.5 px-5 py-3 bg-[#246344] hover:bg-[#194e35] disabled:bg-slate-300 text-white text-sm font-semibold rounded-lg shadow-sm transition flex items-center space-x-1.5 cursor-pointer disabled:cursor-not-allowed"
          >
            <span>{loading ? 'Searching...' : 'Explore'}</span>
            {!loading && <ArrowRight className="w-4 h-4 ml-0.5" />}
          </button>
        </form>

        {/* Category Filters */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-1 pt-1 custom-scrollbar">
          <span className="text-sm font-semibold text-slate-600 flex items-center space-x-1.5 shrink-0 mr-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Category:</span>
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3.5 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition ${
                selectedCategory === cat
                  ? 'bg-[#214b38] text-white shadow-sm'
                  : 'bg-[#f0f4ef] text-slate-700 hover:bg-[#e4ece3]'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Suggested Queries */}
        <div className="pt-4 border-t border-slate-100 space-y-3">
          <div className="flex items-center space-x-1.5 text-sm text-slate-600 font-semibold">
            <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
            <span>Try sample citizen queries:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUERIES.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSampleClick(sample.text)}
                className="text-sm bg-white hover:bg-[#edf5ed] hover:text-[#285b43] hover:border-[#b5ceb8] text-slate-700 border border-slate-200 px-3.5 py-2 rounded-lg transition text-left cursor-pointer"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-4xl mx-auto bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
          {error}
        </div>
      )}

      {/* Grounded Answer Card */}
      <div className="max-w-4xl mx-auto">
        <GroundedAnswerCard result={result} loading={loading} />
      </div>
    </div>
  );
}
