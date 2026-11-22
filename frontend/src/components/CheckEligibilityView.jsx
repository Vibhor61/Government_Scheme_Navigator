import React, { useState } from 'react';
import {
  CheckCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  User,
  MapPin,
  Briefcase,
  Coins,
  RefreshCw,
  ExternalLink
} from 'lucide-react';
import { checkEligibility } from '../services/api';
import SchemeBentoCard from './SchemeBentoCard';
import { t } from '../utils/i18n';

export default function CheckEligibilityView({
  onAskAiWithProfile,
  onAskAi,
  onToggleBookmark,
  savedSchemes = [],
  language = 'en'
}) {
  const isHindi = language === 'hi';

  const [profile, setProfile] = useState({
    gender: 'Male',
    age: 28,
    state: 'Uttar Pradesh',
    rural_urban: 'Rural',
    social_category: 'OBC',
    occupation: 'Farmer',
    annual_family_income: 150000
  });

  const [matchedSchemes, setMatchedSchemes] = useState([]);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [hasEvaluated, setHasEvaluated] = useState(false);

  const states = [
    'Andhra Pradesh', 'Assam', 'Bihar', 'Delhi', 'Gujarat', 'Haryana',
    'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Odisha',
    'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh',
    'West Bengal', 'All India'
  ];

  const occupations = [
    { id: 'Farmer', label: t('occ_farmer', language) },
    { id: 'Student', label: t('occ_student', language) },
    { id: 'Self Employed / Micro-Business', label: t('occ_self_employed', language) },
    { id: 'Artisan / Traditional Craftsman', label: t('occ_artisan', language) },
    { id: 'Unemployed Youth', label: t('occ_unemployed', language) },
    { id: 'Salaried Employee', label: t('occ_salaried', language) }
  ];

  const handleRunEvaluation = async (e) => {
    if (e) e.preventDefault();
    try {
      setIsEvaluating(true);
      const res = await checkEligibility(profile);
      if (res && res.schemes) {
        setMatchedSchemes(res.schemes);
      }
      setHasEvaluated(true);
    } catch (err) {
      console.error("Eligibility check failed:", err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const isBookmarked = (scheme) => {
    const sName = scheme?.name || scheme?.scheme_name;
    return savedSchemes.some(s => (s.name || s.scheme_name) === sName);
  };

  return (
    <div className="flex-1 overflow-y-auto bg-sand-50 dark:bg-[#0B130F] px-4 py-8 sm:px-8 transition-colors duration-200">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-forest-200 dark:border-forest-800/60 bg-forest-50 dark:bg-forest-950/40 px-3 py-1 text-xs font-semibold text-forest-800 dark:text-forest-300 mb-2">
            <CheckCircle className="h-3.5 w-3.5 text-forest-600 dark:text-forest-400" />
            <span>{t('portal_subtitle', language)}</span>
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-charcoal-900 dark:text-sand-50 sm:text-3xl">
            {t('nav_eligibility', language)}
          </h2>
          <p className="mt-1.5 text-sm text-charcoal-500 dark:text-sand-400 max-w-2xl">
            {t('hero_subtitle', language)}
          </p>
        </div>

        {/* Profiler Form */}
        <form
          onSubmit={handleRunEvaluation}
          className="mb-8 rounded-2xl border border-border dark:border-[#22332A] bg-white dark:bg-[#111A15] p-5 sm:p-6 shadow-subtle"
        >
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Gender */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_gender', language)}
              </label>
              <select
                value={profile.gender}
                onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              >
                <option value="Male" className="dark:bg-[#15201A]">{t('gender_male', language)}</option>
                <option value="Female" className="dark:bg-[#15201A]">{t('gender_female', language)}</option>
                <option value="Other" className="dark:bg-[#15201A]">{t('gender_other', language)}</option>
              </select>
            </div>

            {/* Age */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_age', language)}
              </label>
              <input
                type="number"
                min="14"
                max="100"
                value={profile.age}
                onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) || 18 })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              />
            </div>

            {/* State */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_state', language)}
              </label>
              <select
                value={profile.state}
                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              >
                {states.map((st) => (
                  <option key={st} value={st} className="dark:bg-[#15201A]">{st}</option>
                ))}
              </select>
            </div>

            {/* Area */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_area', language)}
              </label>
              <select
                value={profile.rural_urban}
                onChange={(e) => setProfile({ ...profile, rural_urban: e.target.value })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              >
                <option value="Rural" className="dark:bg-[#15201A]">{t('area_rural', language)}</option>
                <option value="Urban" className="dark:bg-[#15201A]">{t('area_urban', language)}</option>
              </select>
            </div>

            {/* Social Category */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_social_category', language)}
              </label>
              <select
                value={profile.social_category}
                onChange={(e) => setProfile({ ...profile, social_category: e.target.value })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              >
                <option value="General" className="dark:bg-[#15201A]">General</option>
                <option value="OBC" className="dark:bg-[#15201A]">OBC</option>
                <option value="SC" className="dark:bg-[#15201A]">SC</option>
                <option value="ST" className="dark:bg-[#15201A]">ST</option>
                <option value="EWS" className="dark:bg-[#15201A]">EWS</option>
              </select>
            </div>

            {/* Occupation */}
            <div>
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_occupation', language)}
              </label>
              <select
                value={profile.occupation}
                onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              >
                {occupations.map((occ) => (
                  <option key={occ.id} value={occ.id} className="dark:bg-[#15201A]">{occ.label}</option>
                ))}
              </select>
            </div>

            {/* Annual Income */}
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-charcoal-900 dark:text-sand-200 mb-1.5">
                {t('field_annual_income', language)}
              </label>
              <input
                type="number"
                step="10000"
                value={profile.annual_family_income}
                onChange={(e) => setProfile({ ...profile, annual_family_income: parseInt(e.target.value) || 0 })}
                className="w-full rounded-xl border border-border dark:border-[#273B30] bg-sand-50/50 dark:bg-[#15201A] px-3 py-2 text-xs font-medium text-charcoal-900 dark:text-sand-50 focus:border-forest-600 focus:bg-white dark:focus:bg-[#192720] focus:outline-none"
              />
            </div>
          </div>

          {/* Form Actions */}
          <div className="mt-6 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-border/80 dark:border-[#22332A]/80 pt-4">
            <div className="flex items-center gap-2 text-xs text-charcoal-500 dark:text-sand-400">
              <ShieldCheck className="h-4 w-4 text-forest-600 dark:text-emerald-400" />
              <span>{t('verified_myscheme', language)}</span>
            </div>

            <div className="flex items-center gap-2.5 w-full sm:w-auto">
              <button
                type="submit"
                disabled={isEvaluating}
                className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 rounded-xl bg-forest-600 px-5 py-2.5 text-xs font-semibold text-white shadow-subtle hover:bg-forest-700 transition active:scale-95 disabled:opacity-50 cursor-pointer"
              >
                {isEvaluating ? (
                  <>
                    <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                    <span>{t('evaluating', language)}</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-3.5 w-3.5" />
                    <span>{t('btn_evaluate_eligibility', language)}</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => onAskAiWithProfile(profile)}
                className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 rounded-xl border border-forest-300 dark:border-forest-700/60 bg-forest-50 dark:bg-forest-950/40 px-5 py-2.5 text-xs font-semibold text-forest-800 dark:text-forest-200 hover:bg-forest-100 dark:hover:bg-forest-900/50 transition active:scale-95 cursor-pointer"
              >
                <Sparkles className="h-3.5 w-3.5 text-forest-600 dark:text-forest-400" />
                <span>{t('discuss_with_ai', language)}</span>
              </button>
            </div>
          </div>
        </form>

        {/* Results Section */}
        {hasEvaluated && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-charcoal-900 dark:text-sand-50">
                  {t('matched_schemes_profile', language)}
                </h3>
                <p className="text-xs text-charcoal-500 dark:text-sand-400">
                  {`${matchedSchemes.length} ${t('schemes_found', language)}`}
                </p>
              </div>

              <button
                onClick={() => onAskAiWithProfile(profile)}
                className="inline-flex items-center gap-1.5 text-xs font-semibold text-forest-700 dark:text-emerald-400 hover:text-forest-900 dark:hover:text-emerald-300 transition"
              >
                <span>{t('get_full_ai_report', language)}</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>

            {matchedSchemes.length === 0 ? (
              <div className="rounded-2xl border border-border dark:border-[#22332A] bg-white dark:bg-[#111A15] p-8 text-center text-xs text-charcoal-500 dark:text-sand-400">
                {t('no_direct_matches', language)}
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {matchedSchemes.map((scheme, idx) => (
                  <SchemeBentoCard
                    key={idx}
                    scheme={scheme}
                    onAskAi={onAskAi}
                    onToggleBookmark={onToggleBookmark}
                    isBookmarked={isBookmarked(scheme)}
                    isHindi={isHindi}
                    language={language}
                  />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
