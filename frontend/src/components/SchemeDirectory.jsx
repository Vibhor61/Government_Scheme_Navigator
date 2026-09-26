import React, { useState, useEffect } from 'react';
import { BookOpen, Search, ExternalLink, X, CheckCircle, FileText, Building2, Tag } from 'lucide-react';
import { fetchAllSchemes } from '../services/api';

const CATEGORIES = ["All", "Agriculture", "Healthcare", "Education", "Employment", "Social Security", "Women & Child"];

export default function SchemeDirectory() {
  const [schemes, setSchemes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [selectedScheme, setSelectedScheme] = useState(null);

  useEffect(() => {
    loadSchemes();
  }, [category, search]);

  const loadSchemes = async () => {
    setLoading(true);
    try {
      const data = await fetchAllSchemes(category, search);
      setSchemes(data);
    } catch (err) {
      console.error("Failed to load schemes:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-3xl font-semibold text-slate-900">Government Schemes Knowledge Base</h2>
          <p className="text-base text-slate-600 mt-1">
            Official central and state welfare programs indexed with chunked vectors and full-text metadata.
          </p>
        </div>

        {/* Search input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by title, keywords..."
            className="w-full pl-10 pr-4 py-3 text-base bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 custom-scrollbar">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition ${
              category === cat
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Scheme Cards Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="bg-white rounded-xl p-6 border border-slate-200 shadow-xs animate-pulse space-y-3">
              <div className="h-4 bg-slate-200 rounded w-1/3"></div>
              <div className="h-6 bg-slate-200 rounded w-3/4"></div>
              <div className="h-16 bg-slate-100 rounded"></div>
            </div>
          ))}
        </div>
      ) : schemes.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-2xl border border-slate-200">
          <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-600 font-medium">No schemes found matching your filter criteria.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              onClick={() => setSelectedScheme(scheme)}
              className="bg-white rounded-xl p-6 border border-slate-200 hover:border-emerald-300 hover:shadow-lg hover:shadow-emerald-950/5 transition cursor-pointer flex flex-col justify-between space-y-5 group"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-semibold uppercase px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {scheme.category}
                  </span>
                  {scheme.short_name && (
                    <span className="text-xs font-mono font-bold text-slate-400">
                      {scheme.short_name}
                    </span>
                  )}
                </div>

                <h3 className="font-semibold text-slate-900 group-hover:text-emerald-700 transition line-clamp-2 text-xl leading-snug">
                  {scheme.title}
                </h3>

                <div className="flex items-center space-x-1.5 text-sm text-slate-600">
                  <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="line-clamp-1">{scheme.ministry}</span>
                </div>

                <p className="text-sm text-slate-700 leading-relaxed line-clamp-3 bg-slate-50 p-3 rounded-lg border border-slate-100">
                  {scheme.financial_assistance || scheme.target_beneficiaries}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-sm">
                <span className="text-emerald-600 font-medium group-hover:underline">View Full Details →</span>
                <span className="text-slate-400 text-[11px]">{scheme.tags?.slice(0, 2).join(', ')}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Scheme Detail Modal */}
      {selectedScheme && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6 sm:p-8 space-y-6 shadow-2xl relative custom-scrollbar">
            <button
              onClick={() => setSelectedScheme(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 bg-slate-100 hover:bg-slate-200 p-1.5 rounded-full transition"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Scheme Header */}
            <div className="space-y-2 pr-8">
              <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-emerald-100 text-emerald-800">
                {selectedScheme.category}
              </span>
              <h2 className="text-2xl sm:text-3xl font-semibold text-slate-900">{selectedScheme.title}</h2>
              <p className="text-xs text-slate-500 flex items-center space-x-1.5">
                <Building2 className="w-4 h-4 text-slate-400" />
                <span>{selectedScheme.ministry}</span>
              </p>
            </div>

            {/* Financial Assistance */}
            <div className="bg-emerald-50/80 border border-emerald-200 rounded-xl p-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-1">
                Financial Assistance & Scope
              </h4>
              <p className="text-base font-medium text-emerald-950 leading-relaxed">
                {selectedScheme.financial_assistance}
              </p>
            </div>

            {/* Eligibility Criteria */}
            <div className="space-y-2">
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center space-x-1.5">
                <CheckCircle className="w-4 h-4 text-emerald-600" />
                <span>Eligibility Criteria & Exclusions</span>
              </h4>
              <ul className="space-y-1.5 pl-1">
                {selectedScheme.eligibility_criteria?.map((item, idx) => (
                  <li key={idx} className="text-xs sm:text-sm text-slate-700 flex items-start space-x-2">
                    <span className="text-emerald-500 font-bold">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Benefits */}
            <div className="space-y-2">
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-blue-600" />
                <span>Benefits Delivered</span>
              </h4>
              <ul className="space-y-1.5 pl-1">
                {selectedScheme.benefits?.map((item, idx) => (
                  <li key={idx} className="text-xs sm:text-sm text-slate-700 flex items-start space-x-2">
                    <span className="text-blue-500 font-bold">✔</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Documents Required */}
            {selectedScheme.documents_required?.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  Required Documents
                </h4>
                <div className="flex flex-wrap gap-2">
                  {selectedScheme.documents_required.map((doc, idx) => (
                    <span key={idx} className="text-xs bg-slate-100 text-slate-800 px-3 py-1 rounded-md border border-slate-200">
                      📄 {doc}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Application Process */}
            <div className="space-y-2">
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                How to Apply
              </h4>
              <p className="text-xs sm:text-sm text-slate-700 bg-slate-50 p-3.5 rounded-xl border border-slate-200 leading-relaxed">
                {selectedScheme.application_process}
              </p>
            </div>

            {/* Official Portal Button */}
            {selectedScheme.official_portal && (
              <div className="pt-2 border-t border-slate-200 flex justify-end">
                <a
                  href={selectedScheme.official_portal}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold flex items-center space-x-2 shadow-sm transition"
                >
                  <span>Visit Official Government Portal</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
