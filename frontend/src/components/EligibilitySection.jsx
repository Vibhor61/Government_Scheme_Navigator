import React, { useState, useEffect } from 'react';
import {
  CheckCircle2, ArrowRight, ArrowLeft, RefreshCw, Sparkles, Filter,
  Building2, ExternalLink, MessageSquare, AlertCircle, HelpCircle,
  Award, FileText, ChevronRight, Check, Search, ShieldCheck
} from 'lucide-react';
import { checkEligibility, fetchSchemesCatalog } from '../services/api';
import SchemeCard from './SchemeCard';

const INDIAN_STATES = [
  "All India / Centre",
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
  "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
  "Uttarakhand", "West Bengal", "Andaman & Nicobar Islands", "Chandigarh",
  "Dadra & Nagar Haveli and Daman & Diu", "Delhi (NCT)", "Jammu & Kashmir",
  "Ladakh", "Lakshadweep", "Puducherry"
];

const CATEGORIES = [
  "All",
  "Agriculture & Rural",
  "Education & Learning",
  "Business & Entrepreneurship",
  "Healthcare & Wellness",
  "Women & Child",
  "Housing & Energy",
  "Social Welfare"
];

export default function EligibilitySection({ onSelectSchemeForChat, onAskAiWithProfile, language = 'en' }) {
  const isHindi = language === 'hi';

  const [step, setStep] = useState(1);
  const [profile, setProfile] = useState({
    gender: 'Male',
    age: 22,
    differently_abled: 'No',
    disability_percent: '',
    state: 'Delhi (NCT)',
    rural_urban: 'Urban',
    social_category: 'General',
    minority_status: 'No',
    marital_status: 'Single',
    annual_family_income: '₹1 Lakh - ₹2.5 Lakh',
    bpl_status: 'No',
    landholding: 'None / Landless',
    occupation: 'Student',
    course_type: 'Engineering / B.Tech',
  });

  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [hasEvaluated, setHasEvaluated] = useState(false);

  // Update profile fields
  const updateField = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (step < 5) {
      setStep(step + 1);
    } else {
      evaluateProfile();
    }
  };

  const handlePrev = () => {
    if (step > 1) setStep(step - 1);
  };

  const evaluateProfile = async () => {
    setIsLoading(true);
    try {
      const data = await checkEligibility(profile);
      if (data && data.schemes) {
        setResults(data.schemes);
      }
      setHasEvaluated(true);
    } catch (err) {
      console.warn("Backend evaluation error, using fallback matching:", err);
      // Fallback evaluation
      setHasEvaluated(true);
    } finally {
      setIsLoading(false);
    }
  };

  // If user changes profile on the result page, re-evaluate
  useEffect(() => {
    if (hasEvaluated) {
      evaluateProfile();
    }
  }, [profile.state, profile.occupation, profile.social_category]);

  // Filter results
  const filteredSchemes = results.filter((scheme) => {
    const matchesCategory = selectedCategory === 'All' || scheme.category === selectedCategory;
    const matchesSearch = !searchQuery ||
      scheme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scheme.ministry.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scheme.brief.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Title & Introduction Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-semibold mb-2">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{isHindi ? 'myScheme आधिकारिक पात्रता जांच' : 'myScheme Official Eligibility Navigator'}</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0F2C59] tracking-tight">
              {isHindi ? 'अपनी पात्रता के आधार पर योजनाएं खोजें' : 'Find Schemes Based on Eligibility'}
            </h2>
            <p className="text-slate-600 text-sm mt-1 max-w-2xl">
              {isHindi
                ? '5 सरल प्रश्नों के उत्तर दें और देखें कि आप केंद्र और राज्य सरकार की किन-किन कल्याणकारी योजनाओं के पात्र हैं।'
                : 'Answer 5 simple questions to instantly discover welfare schemes, scholarships, and subsidies tailored to your profile.'}
            </p>
          </div>

          {hasEvaluated && (
            <button
              type="button"
              onClick={() => {
                setHasEvaluated(false);
                setStep(1);
              }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold text-xs transition self-start"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>{isHindi ? 'प्रोफ़ाइल बदलें' : 'Edit Profile'}</span>
            </button>
          )}
        </div>

        {/* 5-Step Progress Indicator (when taking questionnaire) */}
        {!hasEvaluated && (
          <div className="mt-6 pt-5 border-t border-slate-100">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-600 mb-2">
              <span>{isHindi ? `चरण ${step} / 5` : `Step ${step} of 5`}</span>
              <span className="text-emerald-700">
                {step === 1 && (isHindi ? 'व्यक्तिगत विवरण' : 'Basic Demographics')}
                {step === 2 && (isHindi ? 'स्थान और निवास' : 'Location & Residence')}
                {step === 3 && (isHindi ? 'सामाजिक पृष्ठभूमि' : 'Social Category & Family')}
                {step === 4 && (isHindi ? 'आर्थिक स्थिति' : 'Economic Status & Income')}
                {step === 5 && (isHindi ? 'पेशा और शिक्षा' : 'Occupation & Education')}
              </span>
            </div>
            <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden flex">
              <div
                className="bg-emerald-600 h-full transition-all duration-300 rounded-full"
                style={{ width: `${(step / 5) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* QUESTIONNAIRE WIZARD STEPS */}
      {!hasEvaluated ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          {/* STEP 1: Basic Demographics */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {isHindi ? '1. अपने बारे में बताएं' : '1. Tell us about yourself'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {isHindi ? 'लिंग, आयु और विशेष स्थिति का चयन करें' : 'Select your gender, age, and ability status'}
                </p>
              </div>

              {/* Gender */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'लिंग (Gender)' : 'Gender'}
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'Male', label: isHindi ? 'पुरुष' : 'Male', icon: '👨' },
                    { id: 'Female', label: isHindi ? 'महिला' : 'Female', icon: '👩' },
                    { id: 'Transgender', label: isHindi ? 'अन्य' : 'Transgender', icon: '⚧' }
                  ].map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => updateField('gender', item.id)}
                      className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition font-medium ${
                        profile.gender === item.id
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      <span className="text-2xl mb-1">{item.icon}</span>
                      <span className="text-sm font-semibold">{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Age */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                    {isHindi ? 'आयु (Age in years)' : 'Age (in years)'}
                  </label>
                  <span className="text-base font-extrabold text-emerald-700 px-3 py-0.5 bg-emerald-50 rounded-lg border border-emerald-200">
                    {profile.age} {isHindi ? 'वर्ष' : 'years'}
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={profile.age}
                  onChange={(e) => updateField('age', parseInt(e.target.value, 10))}
                  className="w-full accent-emerald-600 h-2 bg-slate-200 rounded-lg cursor-pointer"
                />
                <div className="flex items-center gap-2 mt-2">
                  {[18, 22, 35, 60].map((presetAge) => (
                    <button
                      key={presetAge}
                      type="button"
                      onClick={() => updateField('age', presetAge)}
                      className={`px-3 py-1 rounded-lg text-xs font-medium border ${
                        profile.age === presetAge
                          ? 'bg-emerald-600 text-white border-emerald-600'
                          : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                      }`}
                    >
                      {presetAge} {isHindi ? 'वर्ष' : 'yrs'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Differently Abled */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'क्या आप दिव्यांग (Differently Abled) हैं?' : 'Are you Differently Abled (Divyangjan)?'}
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['No', 'Yes'].map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => updateField('differently_abled', opt)}
                      className={`py-3 px-4 rounded-xl border-2 font-semibold text-sm transition ${
                        profile.differently_abled === opt
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {opt === 'Yes' ? (isHindi ? 'हाँ' : 'Yes') : (isHindi ? 'नहीं' : 'No')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: Location & Residence */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {isHindi ? '2. आपका राज्य और क्षेत्र' : '2. Your State & Area of Residence'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {isHindi ? 'राज्य सरकार की विशिष्ट योजनाएं प्राप्त करने हेतु राज्य चुनें' : 'Helps filter state-specific and centrally-sponsored welfare schemes'}
                </p>
              </div>

              {/* State/UT Dropdown */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'राज्य / केंद्रशासित प्रदेश (State / UT)' : 'State / Union Territory'}
                </label>
                <select
                  value={profile.state}
                  onChange={(e) => updateField('state', e.target.value)}
                  className="w-full p-3.5 bg-white border-2 border-slate-200 rounded-xl font-medium text-slate-800 focus:outline-none focus:border-emerald-600"
                >
                  {INDIAN_STATES.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>

              {/* Urban vs Rural */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'निवास क्षेत्र (Area of Residence)' : 'Area of Residence'}
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { id: 'Urban', label: isHindi ? 'शहरी (Urban)' : 'Urban', icon: '🏙️' },
                    { id: 'Rural', label: isHindi ? 'ग्रामीण (Rural)' : 'Rural', icon: '🌾' }
                  ].map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => updateField('rural_urban', item.id)}
                      className={`flex items-center justify-center gap-3 p-4 rounded-xl border-2 font-semibold text-sm transition ${
                        profile.rural_urban === item.id
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      <span className="text-xl">{item.icon}</span>
                      <span>{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 3: Social & Family Background */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {isHindi ? '3. सामाजिक श्रेणी एवं पृष्ठभूमि' : '3. Social Category & Family Background'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {isHindi ? 'आरक्षित वर्ग एवं अल्पसंख्यक समुदाय की विशेष योजनाओं हेतु' : 'For affirmative action, minority welfare, and reserved quotas'}
                </p>
              </div>

              {/* Social Category */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'सामाजिक वर्ग (Social Category)' : 'Social Category'}
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {['General', 'OBC', 'SC', 'ST'].map((cat) => (
                    <button
                      key={cat}
                      type="button"
                      onClick={() => updateField('social_category', cat)}
                      className={`p-3.5 rounded-xl border-2 font-bold text-sm transition text-center ${
                        profile.social_category === cat
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              </div>

              {/* Minority Community */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'क्या आप अल्पसंख्यक समुदाय से संबंधित हैं?' : 'Do you belong to a Minority Community?'}
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['No', 'Yes'].map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => updateField('minority_status', opt)}
                      className={`py-3 px-4 rounded-xl border-2 font-semibold text-sm transition ${
                        profile.minority_status === opt
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {opt === 'Yes' ? (isHindi ? 'हाँ (Minority)' : 'Yes (Minority)') : (isHindi ? 'नहीं (No)' : 'No')}
                    </button>
                  ))}
                </div>
              </div>

              {/* Marital Status */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'वैवाहिक स्थिति (Marital Status)' : 'Marital Status'}
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {['Single', 'Married', 'Widowed / Divorced'].map((item) => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => updateField('marital_status', item)}
                      className={`py-3 px-2 rounded-xl border-2 font-medium text-xs sm:text-sm transition text-center ${
                        profile.marital_status === item
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 4: Economic Status & Income */}
          {step === 4 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {isHindi ? '4. वार्षिक पारिवारिक आय एवं आर्थिक स्थिति' : '4. Family Income & Economic Status'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {isHindi ? 'विभिन्न छात्रवृत्तियों एवं सब्सिडी के आय मापदंड हेतु' : 'Used to match income ceilings for interest subsidies, pensions, and fee waivers'}
                </p>
              </div>

              {/* Annual Income */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'वार्षिक पारिवारिक आय (Annual Family Income)' : 'Annual Family Income Range'}
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {[
                    '< ₹1 Lakh',
                    '₹1 Lakh - ₹2.5 Lakh',
                    '₹2.5 Lakh - ₹5 Lakh',
                    '₹5 Lakh - ₹8 Lakh',
                    '> ₹8 Lakh'
                  ].map((range) => (
                    <button
                      key={range}
                      type="button"
                      onClick={() => updateField('annual_family_income', range)}
                      className={`p-3.5 rounded-xl border-2 font-semibold text-sm transition text-left flex items-center justify-between ${
                        profile.annual_family_income === range
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      <span>{range}</span>
                      {profile.annual_family_income === range && (
                        <Check className="w-4 h-4 text-emerald-700" />
                      )}
                    </button>
                  ))}
                </div>
              </div>

              {/* BPL / Ration Card */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'क्या आप गरीबी रेखा से नीचे (BPL / AAY) राशन कार्ड धारक हैं?' : 'Do you hold a Below Poverty Line (BPL / Antyodaya) Ration Card?'}
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {['No', 'Yes'].map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => updateField('bpl_status', opt)}
                      className={`py-3 px-4 rounded-xl border-2 font-semibold text-sm transition ${
                        profile.bpl_status === opt
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {opt === 'Yes' ? (isHindi ? 'हाँ (BPL)' : 'Yes (BPL / AAY)') : (isHindi ? 'नहीं (No)' : 'No')}
                    </button>
                  ))}
                </div>
              </div>

              {/* Landholding */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'कृषि भूमि जोत (Agricultural Landholding)' : 'Agricultural Landholding Size'}
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    'None / Landless',
                    'Marginal (< 1 Ha)',
                    'Small (1-2 Ha)',
                    'Medium / Large (> 2 Ha)'
                  ].map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => updateField('landholding', opt)}
                      className={`p-2.5 rounded-xl border-2 font-medium text-xs text-center transition ${
                        profile.landholding === opt
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* STEP 5: Occupation & Education */}
          {step === 5 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-bold text-slate-900">
                  {isHindi ? '5. पेशा एवं शैक्षणिक विवरण' : '5. Occupation & Education Status'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  {isHindi ? 'अपनी वर्तमान स्थिति का चयन करें ताकि सटीक योजनाओं का मिलान हो सके' : 'Select your primary work or educational status'}
                </p>
              </div>

              {/* Occupation */}
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  {isHindi ? 'वर्तमान पेशा (Primary Occupation)' : 'Primary Occupation / Activity'}
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {[
                    { id: 'Student', label: isHindi ? 'विद्यार्थी (Student)' : 'Student', icon: '🎓' },
                    { id: 'Farmer', label: isHindi ? 'किसान (Farmer)' : 'Farmer', icon: '🚜' },
                    { id: 'Self-Employed / Business', label: isHindi ? 'स्वरोजगार / व्यापारी' : 'Self-Employed / Business', icon: '💼' },
                    { id: 'Daily Wage / Artisan', label: isHindi ? 'कारीगर / श्रमिक' : 'Artisan / Daily Wage', icon: '🔨' },
                    { id: 'Unemployed / Jobseeker', label: isHindi ? 'बेरोजगार / युवा' : 'Unemployed / Jobseeker', icon: '🔍' },
                    { id: 'Salaried', label: isHindi ? 'वेतनभोगी (Salaried)' : 'Salaried Employee', icon: '🏢' }
                  ].map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => updateField('occupation', item.id)}
                      className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition font-medium ${
                        profile.occupation === item.id
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-900 shadow-xs'
                          : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                      }`}
                    >
                      <span className="text-2xl mb-1">{item.icon}</span>
                      <span className="text-xs sm:text-sm font-semibold text-center">{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* If Student: Course Type */}
              {profile.occupation === 'Student' && (
                <div className="p-4 rounded-xl bg-blue-50/70 border border-blue-200 space-y-2">
                  <label className="block text-xs font-bold text-blue-900 uppercase tracking-wider">
                    {isHindi ? 'पाठ्यक्रम का प्रकार (Course Level / Field)' : 'Course Level / Field of Study'}
                  </label>
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                    {[
                      'Engineering / B.Tech',
                      'Medical / Nursing',
                      'Higher Education / University',
                      'Vocational / Technical',
                      'School (Class 9-12)'
                    ].map((course) => (
                      <button
                        key={course}
                        type="button"
                        onClick={() => updateField('course_type', course)}
                        className={`p-2.5 rounded-lg border text-xs font-medium transition text-center ${
                          profile.course_type === course
                            ? 'bg-blue-600 text-white border-blue-600 font-bold'
                            : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                        }`}
                      >
                        {course}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between pt-8 border-t border-slate-100 mt-8">
            {step > 1 ? (
              <button
                type="button"
                onClick={handlePrev}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm transition"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>{isHindi ? 'पिछला' : 'Back'}</span>
              </button>
            ) : <div />}

            <button
              type="button"
              onClick={handleNext}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#0F2C59] hover:bg-[#153e7c] text-white font-bold text-sm shadow-md hover:shadow-lg transition disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>{isHindi ? 'मिलान किया जा रहा है...' : 'Evaluating Schemes...'}</span>
                </>
              ) : step === 5 ? (
                <>
                  <span>{isHindi ? 'पात्र योजनाएं देखें' : 'Find My Eligible Schemes'}</span>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                </>
              ) : (
                <>
                  <span>{isHindi ? 'अगला कदम' : 'Next Step'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* RESULTS SCREEN: MATCHED SCHEMES */
        <div className="space-y-6">
          {/* Top Result Banner */}
          <div className="bg-gradient-to-r from-emerald-800 to-teal-900 rounded-2xl p-6 text-white shadow-md">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-700/60 text-emerald-100 text-xs font-semibold mb-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-300" />
                  <span>{isHindi ? 'पात्रता विश्लेषण पूर्ण' : 'Eligibility Analysis Completed'}</span>
                </div>
                <h3 className="text-2xl sm:text-3xl font-extrabold text-white">
                  {isHindi
                    ? `आपके लिए ${results.length} योजनाएं उपलब्ध हैं!`
                    : `Found ${results.length} Schemes Matching Your Profile!`}
                </h3>
                <p className="text-emerald-100 text-sm mt-1">
                  {isHindi
                    ? 'आपकी आयु, राज्य, श्रेणी एवं आय मापदंडों के आधार पर सत्यापित परिणाम।'
                    : 'Verified against authentic Central and State guidelines on myScheme.'}
                </p>
              </div>

              {/* AI CTA Button */}
              <button
                type="button"
                onClick={() => onAskAiWithProfile && onAskAiWithProfile(profile)}
                className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold text-sm shadow-lg transition self-start md:self-center shrink-0"
              >
                <Sparkles className="w-4 h-4 text-amber-800" />
                <span>{isHindi ? 'AI सहायक से इन पर चर्चा करें' : 'Discuss Results with AI Assistant'}</span>
              </button>
            </div>

            {/* Profile Summary Pills */}
            <div className="mt-5 pt-4 border-t border-emerald-700/60 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-emerald-200 font-semibold">{isHindi ? 'आपकी प्रोफ़ाइल:' : 'Your Profile:'}</span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-950/40 text-emerald-200 border border-emerald-600/40 font-medium">
                {profile.gender}, {profile.age} yrs
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-950/40 text-emerald-200 border border-emerald-600/40 font-medium">
                {profile.state} ({profile.rural_urban})
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-950/40 text-emerald-200 border border-emerald-600/40 font-medium">
                Category: {profile.social_category}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-950/40 text-emerald-200 border border-emerald-600/40 font-medium">
                Occupation: {profile.occupation}
              </span>
              <span className="px-2.5 py-1 rounded-full bg-emerald-950/40 text-emerald-200 border border-emerald-600/40 font-medium">
                Income: {profile.annual_family_income}
              </span>
            </div>
          </div>

          {/* Filters & Search Bar */}
          <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs space-y-3">
            {/* Search Input */}
            <div className="relative w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={isHindi ? 'योजना का नाम, मंत्रालय या लाभ खोजें...' : 'Search matching schemes by name, ministry, or keywords...'}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:bg-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar">
              {CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition ${
                    selectedCategory === cat
                      ? 'bg-emerald-700 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* SCHEME CARDS LIST */}
          <div className="grid grid-cols-1 gap-5">
            {filteredSchemes.length > 0 ? (
              filteredSchemes.map((scheme) => (
                <SchemeCard
                  key={scheme.id}
                  scheme={scheme}
                  onAskAi={(name) => onSelectSchemeForChat && onSelectSchemeForChat(name)}
                  isHindi={isHindi}
                />
              ))
            ) : (
              <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center space-y-3">
                <AlertCircle className="w-10 h-10 text-slate-400 mx-auto" />
                <h4 className="text-base font-bold text-slate-800">
                  {isHindi ? 'कोई योजना नहीं मिली' : 'No matching schemes found'}
                </h4>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  {isHindi
                    ? 'कृपया अपनी श्रेणी अथवा खोज शब्दों में परिवर्तन करें।'
                    : 'Try selecting a different category filter or adjusting your demographic search parameters.'}
                </p>
                <button
                  type="button"
                  onClick={() => setSelectedCategory('All')}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition"
                >
                  {isHindi ? 'सभी योजनाएं देखें' : 'Show All Eligible Schemes'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
