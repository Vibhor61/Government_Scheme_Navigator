import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  Sparkles,
  Bookmark,
  ExternalLink,
  Building2,
  Coins,
  RefreshCw,
  Layers,
  ArrowRight
} from 'lucide-react';
import { fetchSchemesCatalog } from '../services/api';
import SchemeBentoCard from './SchemeBentoCard';

export default function DiscoverSchemesView({
  onAskAi,
  onToggleBookmark,
  savedSchemes = [],
  language = 'en'
}) {
  const isHindi = language === 'hi';

  const [schemes, setSchemes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedLevel, setSelectedLevel] = useState('All');
  const [isLoading, setIsLoading] = useState(true);

  const categories = [
    { id: 'All', label: isHindi ? 'सभी श्रेणियां' : 'All Categories' },
    { id: 'Agriculture', label: isHindi ? 'कृषि एवं किसान' : 'Agriculture' },
    { id: 'Education', label: isHindi ? 'शिक्षा एवं छात्रवृत्ति' : 'Education' },
    { id: 'Business & Entrepreneurship', label: isHindi ? 'व्यापार व ऋण' : 'Business & Loans' },
    { id: 'Health & Wellness', label: isHindi ? 'स्वास्थ्य एवं बीमा' : 'Health' },
    { id: 'Energy & Environment', label: isHindi ? 'सौर व स्वच्छ ऊर्जा' : 'Energy & Solar' },
    { id: 'Social Welfare & Empowerment', label: isHindi ? 'महिला व सामाजिक कल्याण' : 'Social Welfare' }
  ];

  useEffect(() => {
    async function loadCatalog() {
      try {
        setIsLoading(true);
        const data = await fetchSchemesCatalog();
        if (data && data.schemes) {
          setSchemes(data.schemes);
        }
      } catch (err) {
        console.error("Failed to load catalog:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadCatalog();
  }, []);

  const isBookmarked = (scheme) => {
    const sName = scheme?.name || scheme?.scheme_name;
    return savedSchemes.some(s => (s.name || s.scheme_name) === sName);
  };

  // Filter schemes
  const filteredSchemes = schemes.filter(s => {
    const name = (s.name || s.scheme_name || '').toLowerCase();
    const brief = (s.brief || s.repository_summary || '').toLowerCase();
    const ministry = (s.ministry || s.department || '').toLowerCase();
    const category = s.category || '';
    const level = s.level || 'Central';

    // Search query match
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchesSearch = name.includes(q) || brief.includes(q) || ministry.includes(q);
      if (!matchesSearch) return false;
    }

    // Category filter
    if (selectedCategory !== 'All' && !category.toLowerCase().includes(selectedCategory.toLowerCase())) {
      return false;
    }

    // Level filter
    if (selectedLevel !== 'All' && level.toLowerCase() !== selectedLevel.toLowerCase()) {
      return false;
    }

    return true;
  });

  return (
    <div className="flex-1 overflow-y-auto bg-sand-50 dark:bg-[#0B130F] px-4 py-8 sm:px-8 transition-colors duration-200">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-forest-200 dark:border-forest-800/60 bg-forest-50 dark:bg-forest-950/40 px-3 py-1 text-xs font-semibold text-forest-800 dark:text-forest-300 mb-2">
            <Layers className="h-3.5 w-3.5 text-forest-600 dark:text-forest-400" />
            <span>{isHindi ? 'आधिकारिक रिपॉजिटरी निर्देशिका' : 'Official Schemes Repository'}</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-charcoal-900 dark:text-sand-50 sm:text-3xl">
            {isHindi ? 'सरकारी योजनाएं खोजें' : 'Discover Government Schemes'}
          </h2>
          <p className="mt-1.5 text-sm text-charcoal-500 dark:text-sand-400 max-w-2xl">
            {isHindi
              ? 'केंद्रीय और राज्य सरकारों द्वारा संचालित योजनाओं का अन्वेषण करें, पात्रता नियम समझें और सीधे आवेदन करें।'
              : 'Browse flagship Central and State welfare programs, check eligibility requirements, and evaluate with JanSahayak AI.'}
          </p>
        </div>

        {/* Filter & Search Bar */}
        <div className="mb-6 space-y-3.5 rounded-2xl border border-border dark:border-[#22332A] bg-white dark:bg-[#111A15] p-4 shadow-subtle">
          <div className="flex flex-col sm:flex-row gap-3">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3.5 top-3 h-4 w-4 text-charcoal-400 dark:text-sand-400/60" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder={isHindi ? 'योजना का नाम या उद्देश्य खोजें...' : 'Search by scheme name, keywords, or ministry...'}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] pl-10 pr-4 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 placeholder:text-charcoal-400 dark:placeholder:text-sand-400/50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none focus:ring-1 focus:ring-forest-600"
              />
            </div>

            {/* Level Toggle */}
            <div className="flex items-center rounded-xl border border-border dark:border-[#273B30] bg-sand-50 dark:bg-[#15201A] p-1 text-xs font-semibold shrink-0">
              {['All', 'Central', 'State'].map((lvl) => (
                <button
                  key={lvl}
                  onClick={() => setSelectedLevel(lvl)}
                  className={`rounded-lg px-3 py-1.5 transition ${
                    selectedLevel === lvl
                      ? 'bg-white dark:bg-[#203127] text-forest-700 dark:text-emerald-300 shadow-2xs'
                      : 'text-charcoal-500 dark:text-sand-400 hover:text-charcoal-900 dark:hover:text-sand-100'
                  }`}
                >
                  {lvl === 'All' ? (isHindi ? 'सभी स्तर' : 'All') : lvl === 'Central' ? (isHindi ? 'केंद्रीय' : 'Central') : (isHindi ? 'राज्य' : 'State')}
                </button>
              ))}
            </div>
          </div>

          {/* Category Pills */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-border/60 dark:border-[#22332A]/60">
            {categories.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                  selectedCategory === cat.id
                    ? 'bg-forest-600 text-white shadow-2xs'
                    : 'bg-sand-50 dark:bg-[#15201A] text-charcoal-700 dark:text-sand-300 hover:bg-sand-100 dark:hover:bg-[#1E2E25] hover:text-charcoal-900 dark:hover:text-sand-100 border border-border dark:border-[#22332A]'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results Counter */}
        <div className="mb-4 flex items-center justify-between text-xs text-charcoal-500 dark:text-sand-400">
          <span>
            {isHindi
              ? `${filteredSchemes.length} योजनाएं प्रदर्शित`
              : `Showing ${filteredSchemes.length} government schemes`}
          </span>
          {searchTerm && (
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedCategory('All');
                setSelectedLevel('All');
              }}
              className="text-forest-700 dark:text-emerald-400 hover:underline font-semibold"
            >
              {isHindi ? 'फ़िल्टर हटाएं' : 'Clear filters'}
            </button>
          )}
        </div>

        {/* Schemes Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20 text-charcoal-400 dark:text-sand-400">
            <RefreshCw className="h-6 w-6 animate-spin text-forest-600 dark:text-forest-400" />
          </div>
        ) : filteredSchemes.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border dark:border-[#22332A] bg-white dark:bg-[#111A15] p-12 text-center">
            <p className="text-sm font-semibold text-charcoal-800 dark:text-sand-100">
              {isHindi ? 'कोई योजना नहीं मिली' : 'No matching schemes found'}
            </p>
            <p className="mt-1 text-xs text-charcoal-500 dark:text-sand-400">
              {isHindi ? 'कृपया अन्य खोज शब्द या फ़िल्टर का चयन करें।' : 'Try adjusting your search terms or filter criteria.'}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredSchemes.map((scheme, idx) => (
              <SchemeBentoCard
                key={idx}
                scheme={scheme}
                onAskAi={onAskAi}
                onToggleBookmark={onToggleBookmark}
                isBookmarked={isBookmarked(scheme)}
                isHindi={isHindi}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
