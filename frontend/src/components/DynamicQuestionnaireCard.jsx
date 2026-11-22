import React, { useState } from 'react';
import { HelpCircle, ArrowRight, CheckCircle2, ChevronDown, Check } from 'lucide-react';

const QUESTIONNAIRE_I18N = {
  en: {
    header: "Confirm Your Eligibility Details",
    subtitle: "Select or enter all applicable details below to calculate your exact benefits:",
    answered: "answered",
    submittedNotice: "Eligibility details submitted - Full evaluation generated below",
    editAnswers: "Edit Answers",
    required: "Required",
    selectOption: "-- Select an option --",
    enterNumber: "Enter amount or value (e.g. 200000)...",
    answerAllPrompt: (total) => `Please answer all ${total} questions for full accuracy`,
    readyPrompt: "All required details ready",
    submitButton: (answered, total) => `Submit Details & Evaluate (${answered}/${total})`
  },
  hi: {
    header: "पात्रता निर्धारण हेतु विवरण दर्ज करें",
    subtitle: "सटीक सब्सिडी राशि व पात्रता की पुष्टि हेतु कृपया नीचे दिए गए प्रश्नों का उत्तर दें:",
    answered: "उत्तर दिए",
    submittedNotice: "विवरण सफलतापूर्वक जमा किए गए - नीचे पात्रता मूल्यांकन देखें",
    editAnswers: "संशोधन करें",
    required: "अनिवार्य",
    selectOption: "-- विकल्प चुनें --",
    enterNumber: "संख्या या वार्षिक राशि (₹) दर्ज करें...",
    answerAllPrompt: (total) => `कृपया सभी ${total} प्रश्नों के उत्तर दें`,
    readyPrompt: "सभी विवरण तैयार हैं",
    submitButton: (answered, total) => `पात्रता की पुष्टि करें (${answered}/${total})`
  },
  bn: {
    header: "যোগ্যতা যাচাইয়ের বিবরণ প্রদান করুন",
    subtitle: "সঠিক ভর্তুকি ও সুবিধা পাওয়ার জন্য নিচের প্রশ্নগুলির উত্তর দিন:",
    answered: "উত্তর দেওয়া হয়েছে",
    submittedNotice: "বিবরণ জমা দেওয়া হয়েছে - নিচে সম্পূর্ণ মূল্যায়ন দেখুন",
    editAnswers: "পরিবর্তন করুন",
    required: "বাধ্যতামূলক",
    selectOption: "-- একটি বিকল্প বেছে নিন --",
    enterNumber: "পরিমাণ বা মান লিখুন (যেমন ২০০০০০)...",
    answerAllPrompt: (total) => `সম্পূর্ণ ফলাফলের জন্য সমস্ত ${total}টি প্রশ্নের উত্তর দিন`,
    readyPrompt: "সমস্ত বিবরণ প্রস্তুত",
    submitButton: (answered, total) => `বিবরণ জমা দিন ও যাচাই করুন (${answered}/${total})`
  },
  kn: {
    header: "ಅರ್ಹತಾ ವಿವರಗಳನ್ನು ದೃಢೀಕರಿಸಿ",
    subtitle: "ನಿಖರವಾದ ಸೌಲಭ್ಯಗಳನ್ನು ಲೆಕ್ಕಹಾಕಲು ಕೆಳಗಿನ ವಿವರಗಳನ್ನು ನಮೂದಿಸಿ:",
    answered: "ಉತ್ತರಿಸಲಾಗಿದೆ",
    submittedNotice: "ವಿವರಗಳನ್ನು ಸಲ್ಲಿಸಲಾಗಿದೆ - ಕೆಳಗೆ ಪೂರ್ಣ ಮೌಲ್ಯಮಾಪನ ನೋಡಿ",
    editAnswers: "ಬದಲಾಯಿಸಿ",
    required: "ಕಡ್ಡಾಯ",
    selectOption: "-- ಆಯ್ಕೆಯನ್ನು ಆರಿಸಿ --",
    enterNumber: "ಮೊತ್ತ ಅಥವಾ ಮೌಲ್ಯ ನಮೂದಿಸಿ (ಉದಾ. 200000)...",
    answerAllPrompt: (total) => `ಪೂರ್ಣ ನಿಖರತೆಗಾಗಿ ಎಲ್ಲಾ ${total} ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ`,
    readyPrompt: "ಎಲ್ಲಾ ವಿವರಗಳು ಸಿದ್ಧವಾಗಿವೆ",
    submitButton: (answered, total) => `ವಿವರಗಳನ್ನು ಸಲ್ಲಿಸಿ ಪರಿಶೀಲಿಸಿ (${answered}/${total})`
  },
  mr: {
    header: "पात्रतेसाठी आवश्यक तपशील प्रविष्ट करा",
    subtitle: "अचूक लाभ व सबसिडी जाणून घेण्यासाठी खालील प्रश्नांची उत्तरे द्या:",
    answered: "उत्तरे दिली",
    submittedNotice: "तपशील यशस्वीरित्या सादर केले - खाली पात्रता मूल्यांकन पहा",
    editAnswers: "बदल करा",
    required: "अनिवार्य",
    selectOption: "-- पर्याय निवडा --",
    enterNumber: "रक्कम किंवा संख्या प्रविष्ट करा (उदा. 200000)...",
    answerAllPrompt: (total) => `अचूकतेसाठी सर्व ${total} प्रश्नांची उत्तरे द्या`,
    readyPrompt: "सर्व तपशील तयार आहेत",
    submitButton: (answered, total) => `तपशील सादर करा व तपासा (${answered}/${total})`
  },
  ta: {
    header: "தகுதி விவரங்களை உறுதிப்படுத்தவும்",
    subtitle: "துல்லியமான பலன்களைக் கணக்கிட கீழே உள்ள விவரங்களை உள்ளிடவும்:",
    answered: "பதிலளிக்கப்பட்டது",
    submittedNotice: "விவரங்கள் சமர்ப்பிக்கப்பட்டன - கீழே முழு மதிப்பீட்டைக் காண்க",
    editAnswers: "திருத்தவும்",
    required: "கட்டாயம்",
    selectOption: "-- ஒரு விருப்பத்தைத் தேர்வுசெய்க --",
    enterNumber: "தொகை அல்லது மதிப்பை உள்ளிடவும் (எ.கா. 200000)...",
    answerAllPrompt: (total) => `துல்லியத்திற்காக அனைத்து ${total} கேள்விகளுக்கும் பதிலளிக்கவும்`,
    readyPrompt: "அனைத்து விவரங்களும் தயாராக உள்ளன",
    submitButton: (answered, total) => `விவரங்களைச் சமர்ப்பித்து சரிபார்க்கவும் (${answered}/${total})`
  },
  te: {
    header: "అర్హత వివరాలను నిర్ధారించండి",
    subtitle: "ఖచ్చితమైన ప్రయోజనాలను లెక్కించడానికి క్రింది వివరాలను ఎంచుకోండి:",
    answered: "సమాధానమిచ్చారు",
    submittedNotice: "వివరాలు సమర్పించబడ్డాయి - పూర్తి మూల్యాంకనాన్ని క్రింద చూడండి",
    editAnswers: "సవరించు",
    required: "తప్పనిసరి",
    selectOption: "-- ఒక ఎంపికను ఎంచుకోండి --",
    enterNumber: "మొత్తం లేదా విలువను నమోదు చేయండి (ఉదా. 200000)...",
    answerAllPrompt: (total) => `పూర్తి ఖచ్చితత్వం కోసం మొత్తం ${total} ప్రశ్నలకు సమాధానం ఇవ్వండి`,
    readyPrompt: "అన్ని వివరాలు సిద్ధంగా ఉన్నాయి",
    submitButton: (answered, total) => `వివరాలను సమర్పించి ధృవీకరించండి (${answered}/${total})`
  },
  gu: {
    header: "પાત્રતા વિગતોની પુષ્ટિ કરો",
    subtitle: "ચોક્કસ લાભો મેળવવા માટે કૃપા કરીને નીચેની વિગતો દાખલ કરો:",
    answered: "જવાબ આપ્યા",
    submittedNotice: "વિગતો સબમિટ થઈ ગઈ છે - નીચે સંપૂર્ણ મૂલ્યાંકન જુઓ",
    editAnswers: "સુધારો કરો",
    required: "જરૂરી",
    selectOption: "-- વિકલ્પ પસંદ કરો --",
    enterNumber: "રકમ અથવા મૂલ્ય દાખલ કરો (દા.ત. 200000)...",
    answerAllPrompt: (total) => `સંપૂર્ણ ચોકસાઈ માટે તમામ ${total} પ્રશ્નોના જવાબ આપો`,
    readyPrompt: "તમામ વિગતો તૈયાર છે",
    submitButton: (answered, total) => `વિગતો સબમિટ કરો અને ચકાસો (${answered}/${total})`
  },
  pa: {
    header: "ਯੋਗਤਾ ਦੇ ਵੇਰਵਿਆਂ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ",
    subtitle: "ਸਹੀ ਲਾਭ ਜਾਣਨ ਲਈ ਕਿਰਪਾ ਕਰਕੇ ਹੇਠਾਂ ਦਿੱਤੇ ਵੇਰਵੇ ਦਰਜ ਕਰੋ:",
    answered: "ਜਵਾਬ ਦਿੱਤੇ",
    submittedNotice: "ਵੇਰਵੇ ਜਮ੍ਹਾਂ ਕੀਤੇ ਗਏ ਹਨ - ਹੇਠਾਂ ਪੂਰਾ ਮੁਲਾਂਕਣ ਦੇਖੋ",
    editAnswers: "ਸੋਧ ਕਰੋ",
    required: "ਲਾਜ਼ਮੀ",
    selectOption: "-- ਇੱਕ ਵਿਕਲਪ ਚੁਣੋ --",
    enterNumber: "ਰਕਮ ਜਾਂ ਮੁੱਲ ਦਰਜ ਕਰੋ (ਜਿਵੇਂ 200000)...",
    answerAllPrompt: (total) => `ਸਹੀ ਜਾਣਕਾਰੀ ਲਈ ਸਾਰੇ ${total} ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ`,
    readyPrompt: "ਸਾਰੇ ਵੇਰਵੇ ਤਿਆਰ ਹਨ",
    submitButton: (answered, total) => `ਵੇਰਵੇ ਜਮ੍ਹਾਂ ਕਰੋ ਅਤੇ ਜਾਂਚੋ (${answered}/${total})`
  }
};

const STANDARD_FIELD_MAP = {
  annual_family_income: {
    en: "What is your family's annual income (in ₹)?",
    hi: "आपके परिवार की वार्षिक आय कितनी है (₹ में)?",
    bn: "আপনার পরিবারের বার্ষিক আয় কত (টাকায়)?",
    kn: "ನಿಮ್ಮ ಕುಟುಂಬದ ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು (ರೂಗಳಲ್ಲಿ)?",
    mr: "तुमच्या कुटुंबाचे वार्षिक उत्पन्न किती आहे (₹ मध्ये)?",
    ta: "உங்கள் குடும்பத்தின் ஆண்டு வருமானம் என்ன (₹)?",
    te: "మీ కుటుంబ వార్షిక ఆదాయం ఎంత (రూ.లలో)?",
    gu: "તમારા પરિવારની વાર્ષિક આવક કેટલી છે (રૂ.માં)?",
    pa: "ਤੁਹਾਡੇ ਪਰਿਵਾਰ ਦੀ ਸਾਲਾਨਾ ਆਮਦਨ ਕਿੰਨੀ ਹੈ (₹ ਵਿੱਚ)?"
  },
  state: {
    en: "Which State or Union Territory do you live in?",
    hi: "आप किस राज्य या केंद्र शासित प्रदेश में रहते हैं?",
    bn: "আপনি কোন রাজ্য বা কেন্দ্রশাসিত অঞ্চলে বাস করেন?",
    kn: "ನೀವು ಯಾವ ರಾಜ್ಯ ಅಥವಾ ಕೇಂದ್ರಾಡಳಿತ ಪ್ರದೇಶದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಿ?",
    mr: "तुम्ही कोणत्या राज्यात किंवा केंद्रशासित प्रदेशात राहता?",
    ta: "நீங்கள் எந்த மாநிலம் அல்லது யூனியன் பிரதேசத்தில் வசிக்கிறீர்கள்?",
    te: "మీరు ఏ రాష్ట్రం లేదా కేంద్రపాలిత ప్రాంతంలో నివసిస్తున్నారు?",
    gu: "તમે કયા રાજ્ય અથવા કેન્દ્રશાસિત પ્રદેશમાં રહો છો?",
    pa: "ਤੁਸੀਂ ਕਿਸ ਰਾਜ ਜਾਂ ਕੇਂਦਰ ਸ਼ਾਸਤ ਪ੍ਰਦੇਸ਼ ਵਿੱਚ ਰਹਿੰਦੇ ਹੋ?"
  },
  social_category: {
    en: "Which social category applies to you?",
    hi: "आप किस सामाजिक वर्ग से संबंधित हैं?",
    bn: "আপনি কোন সামাজিক বিভাগের অন্তর্ভুক্ত?",
    kn: "ನೀವು ಯಾವ ಸಾಮಾಜಿಕ ವರ್ಗಕ್ಕೆ ಸೇರಿದವರು?",
    mr: "तुम्ही कोणत्या सामाजिक वर्गात मोडता?",
    ta: "நீங்கள் எந்த சமூகப் பிரிவைச் சேர்ந்தவர்?",
    te: "మీరు ఏ సామాజిక వర్గానికి చెందినవారు?",
    gu: "તમે કયા સામાજિક વર્ગમાં આવો છો?",
    pa: "ਤੁਸੀਂ ਕਿਸ ਸਮਾਜਿਕ ਸ਼੍ਰੇਣੀ ਨਾਲ ਸੰਬੰਧਿਤ ਹੋ?"
  },
  age: {
    en: "What is your age in completed years?",
    hi: "आपकी वर्तमान आयु (वर्ष) कितनी है?",
    bn: "আপনার বয়স কত (বছর)?",
    kn: "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?",
    mr: "तुमचे वय किती वर्षे आहे?",
    ta: "உங்கள் வயது என்ன?",
    te: "మీ వయస్సు ఎంత?",
    gu: "તમારી ઉંમર કેટલી છે?",
    pa: "ਤੁਹਾਡੀ ਉਮਰ ਕਿੰਨੀ ਹੈ?"
  },
  gender: {
    en: "What is your gender?",
    hi: "आपका लिंग क्या है?",
    bn: "আপনার লিঙ্গ কি?",
    kn: "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು?",
    mr: "तुमचे लिंग काय आहे?",
    ta: "உங்கள் பாலினம் என்ன?",
    te: "మీ లింగం ఏమిటి?",
    gu: "તમારું લિંગ શું છે?",
    pa: "ਤੁਹਾਡਾ ਲਿੰਗ ਕੀ ਹੈ?"
  },
  occupation: {
    en: "What is your primary occupation?",
    hi: "आपका मुख्य व्यवसाय क्या है?",
    bn: "আপনার প্রধান পেশা কি?",
    kn: "ನಿಮ್ಮ ಮುಖ್ಯ ವೃತ್ತಿ ಏನು?",
    mr: "तुमचा मुख्य व्यवसाय काय आहे?",
    ta: "உங்கள் முதன்மை தொழில் என்ன?",
    te: "మీ ప్రధాన వృత్తి ఏమిటి?",
    gu: "તમારો મુખ્ય વ્યવસાય શું છે?",
    pa: "ਤੁਹਾਡਾ ਮੁੱਖ ਕਿੱਤਾ ਕੀ ਹੈ?"
  },
  landholding: {
    en: "Do you own agricultural land?",
    hi: "क्या आपके पास कृषि भूमि या जमीन है?",
    bn: "আপনার কি নিজস্ব কৃষি জমি রয়েছে?",
    kn: "ನಿಮ್ಮ ಬಳಿ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೇ?",
    mr: "तुमच्याकडे शेतजमीन आहे का?",
    ta: "உங்களுக்கு விவசாய நிலம் உள்ளதா?",
    te: "మీకు వ్యవసాయ భూమి ఉందా?",
    gu: "શું તમારી પાસે ખેતીની જમીન છે?",
    pa: "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਖੇਤੀਬਾੜੀ ਜ਼ਮੀਨ ਹੈ?"
  },
  cultivable_land: {
    en: "Do you own cultivable agricultural land?",
    hi: "क्या आपके पास खेती योग्य कृषि भूमि है?",
    bn: "আপনার কি চাষযোগ্য কৃষি জমি আছে?",
    kn: "ನಿಮ್ಮ ಬಳಿ ಸಾಗುವಳಿ ಮಾಡಬಹುದಾದ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೆ?",
    mr: "तुमच्याकडे लागवडीयोग्य शेतजमीन आहे का?",
    ta: "உங்களுக்கு சாகுபடி செய்யக்கூடிய விவசாய நிலம் உள்ளதா?",
    te: "మీ వద్ద సాగు చేయదగిన వ్యవసాయ భూమి ఉందా?",
    gu: "શું તમારી પાસે ખેતીલાયક જમીન છે?",
    pa: "ਕੀ ਤੁਹਾਡੇ ਕੋਲ ਖੇਤੀਯੋਗ ਜ਼ਮੀਨ ਹੈ?"
  },
  farmer_status: {
    en: "Are you a farmer or cultivator?",
    hi: "क्या आपका परिवार किसान या काश्तकार है?",
    bn: "আপনার পরিবার কি কৃষক বা চাষী পরিবার?",
    kn: "ನಿಮ್ಮ ಕುಟುಂಬವು ರೈತರ ಕುಟುಂಬವೇ?",
    mr: "तुम्ही शेतकरी किंवा कास्तकार आहात का?",
    ta: "நீங்கள் விவசாயி குடும்பத்தைச் சேர்ந்தவரா?",
    te: "మీరు రైతు కుటుంబానికి చెందినవారా?",
    gu: "શું તમે ખેડૂત પરિવારમાંથી છો?",
    pa: "ਕੀ ਤੁਸੀਂ ਕਿਸਾਨ ਜਾਂ ਕਾਸ਼ਤਕਾਰ ਪਰਿਵਾਰ ਤੋਂ ਹੋ?"
  },
  rural_urban: {
    en: "Do you reside in a rural or urban area?",
    hi: "क्या आप ग्रामीण या शहरी क्षेत्र में रहते हैं?",
    bn: "আপনি কি গ্রামীণ বা শহরাঞ্চলে বাস করেন?",
    kn: "ನೀವು ಗ್ರಾಮೀಣ ಅಥವಾ ನಗರ ಪ್ರದೇಶದಲ್ಲಿ ವಾಸಿಸುತ್ತೀರಾ?",
    mr: "तुम्ही ग्रामीण की शहरी भागात राहता?",
    ta: "நீங்கள் கிராமப்புறத்தில் வசிக்கிறீர்களா அல்லது நகர்ப்புறத்திலா?",
    te: "మీరు గ్రామీణ లేదా పట్టణ ప్రాంతంలో నివసిస్తున్నారా?",
    gu: "તમે ગ્રામીણ કે શહેરી વિસ્તારમાં રહો છો?",
    pa: "ਕੀ ਤੁਸੀਂ ਪੇਂਡੂ ਜਾਂ ਸ਼ਹਿਰੀ ਖੇਤਰ ਵਿੱਚ ਰਹਿੰਦੇ ਹੋ?"
  }
};

const STANDARD_OPTION_MAP = {
  yes: {
    en: "Yes", hi: "हाँ", bn: "হ্যাঁ", kn: "ಹೌದು", mr: "होय", ta: "ஆம்", te: "అవును", gu: "હા", pa: "ਹਾਂ"
  },
  no: {
    en: "No", hi: "नहीं", bn: "না", kn: "ಇಲ್ಲ", mr: "नाही", ta: "இல்லை", te: "కాదు", gu: "ના", pa: "ਨਹੀਂ"
  },
  "not sure": {
    en: "Not sure", hi: "निश्चित नहीं", bn: "নিশ্চিত নই", kn: "ಖಚಿತವಿಲ್ಲ", mr: "नक्की माहीत नाही", ta: "நிச்சயமில்லை", te: "ఖచ్చితంగా తెలియదు", gu: "ખાતરી નથી", pa: "ਪੱਕਾ ਨਹੀਂ"
  },
  rural: {
    en: "Rural", hi: "ग्रामीण", bn: "গ্রামীণ", kn: "ಗ್ರಾಮೀಣ", mr: "ग्रामीण", ta: "கிராமப்புறம்", te: "గ్రామీణ", gu: "ગ્રામીણ", pa: "ਪੇਂਡੂ"
  },
  urban: {
    en: "Urban", hi: "शहरी", bn: "শহুরে", kn: "ನಗರ", mr: "शहरी", ta: "நகர்ப்புறம்", te: "పట్టణ", gu: "શહેરી", pa: "ਸ਼ਹਿਰੀ"
  },
  male: {
    en: "Male", hi: "पुरुष", bn: "পুরুষ", kn: "ಪುರುಷ", mr: "पुरुष", ta: "ஆண்", te: "పురుషుడు", gu: "પુરુષ", pa: "ਪੁਰਸ਼"
  },
  female: {
    en: "Female", hi: "महिला", bn: "মহিলা", kn: "ಮಹಿಳೆ", mr: "महिला", ta: "பெண்", te: "మహిళ", gu: "મહિલા", pa: "ਮਹਿਲਾ"
  },
  other: {
    en: "Other", hi: "अन्य", bn: "অন্যান্য", kn: "ಇತರೆ", mr: "इतर", ta: "மற்றவை", te: "ఇతర", gu: "અન્ય", pa: "ਹੋਰ"
  },
  general: {
    en: "General", hi: "सामान्य (General)", bn: "সাধারণ (General)", kn: "ಸಾಮಾನ್ಯ (General)", mr: "सामान्य (General)", ta: "பொதுப்பிரிவு (General)", te: "జనరల్ (General)", gu: "સામાન્ય (General)", pa: "ਜਨਰਲ"
  },
  obc: {
    en: "OBC", hi: "ओबीसी (OBC)", bn: "ওবিসি (OBC)", kn: "ಒಬಿಸಿ (OBC)", mr: "ओबीसी (OBC)", ta: "ஓபிசி (OBC)", te: "ఓబీసీ (OBC)", gu: "ઓબીસી (OBC)", pa: "ਓਬੀਸੀ"
  },
  sc: {
    en: "SC", hi: "अनुसूचित जाति (SC)", bn: "তপশিলি জাতি (SC)", kn: "ಪರಿಶಿಷ್ಟ ಜಾತಿ (SC)", mr: "अनुसूचित जाती (SC)", ta: "பட்டியல் இனம் (SC)", te: "ఎస్సీ (SC)", gu: "અનુસૂચિત જાતિ (SC)", pa: "ਐਸਸੀ"
  },
  st: {
    en: "ST", hi: "अनुसूचित जनजाति (ST)", bn: "তপশিলি উপজাতি (ST)", kn: "ಪರಿಶಿಷ್ಟ ಪಂಗಡ (ST)", mr: "अनुसूचित जमाती (ST)", ta: "பழங்குடியினர் (ST)", te: "ఎస్టీ (ST)", gu: "અનુસૂચિત જનજાતિ (ST)", pa: "ਐਸਟੀ"
  },
  farmer: {
    en: "Farmer", hi: "किसान", bn: "কৃষক", kn: "ರೈತ", mr: "शेतकरी", ta: "விவசாயி", te: "రైతు", gu: "ખેડૂત", pa: "ਕਿਸਾਨ"
  },
  student: {
    en: "Student", hi: "विद्यार्थी", bn: "শিক্ষার্থী", kn: "ವಿದ್ಯಾರ್ಥಿ", mr: "विद्यार्थी", ta: "மாணவர்", te: "విద్యార్థి", gu: "વિદ્યાર્થી", pa: "ਵਿਦਿਆਰਥੀ"
  }
};

const getLocalizedQuestion = (q, lang) => {
  if (lang !== 'en' && q.question && /[^\u0000-\u007F]/.test(q.question)) {
    return q.question;
  }
  const fieldKey = (q.id || q.field || '').toLowerCase().replace(/[^a-z0-9_]/g, '');
  if (STANDARD_FIELD_MAP[fieldKey]?.[lang]) {
    return STANDARD_FIELD_MAP[fieldKey][lang];
  }
  return q.question || q.label;
};

const getLocalizedOption = (opt, lang) => {
  if (typeof opt !== 'string') return opt;
  if (lang !== 'en' && /[^\u0000-\u007F]/.test(opt)) {
    return opt;
  }
  const cleanKey = opt.trim().toLowerCase();
  if (STANDARD_OPTION_MAP[cleanKey]?.[lang]) {
    return STANDARD_OPTION_MAP[cleanKey][lang];
  }
  return opt;
};

export default function DynamicQuestionnaireCard({
  questions = [],
  onSubmitBatch,
  onSubmit,
  language = 'en',
  isHindi = false,
  isSubmitting = false
}) {
  const [formValues, setFormValues] = useState({});
  const [hasSubmitted, setHasSubmitted] = useState(false);

  if (!questions || questions.length === 0) return null;

  // Resolve active language dictionary
  const langKey = (language && QUESTIONNAIRE_I18N[language]) ? language : (isHindi ? 'hi' : 'en');
  const t = QUESTIONNAIRE_I18N[langKey] || QUESTIONNAIRE_I18N.en;

  const totalQuestions = questions.length;
  const answeredCount = Object.keys(formValues).filter(k => formValues[k] !== undefined && formValues[k] !== '').length;

  const handleSelectOption = (fieldKey, value) => {
    setFormValues(prev => ({ ...prev, [fieldKey]: value }));
  };

  const handleSubmitAll = (e) => {
    if (e) e.preventDefault();
    if (answeredCount === 0 || isSubmitting) return;
    setHasSubmitted(true);
    const submitFn = onSubmitBatch || onSubmit;
    if (submitFn) {
      submitFn(formValues);
    }
  };

  if (hasSubmitted) {
    return (
      <div className="my-3 rounded-xl border border-emerald-300 dark:border-emerald-800/80 bg-emerald-50/70 dark:bg-[#0E1E16] p-3 text-xs flex items-center justify-between gap-2 shadow-2xs animate-fadeIn">
        <div className="flex items-center gap-2 text-emerald-900 dark:text-emerald-200">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span className="font-semibold">{t.submittedNotice}</span>
        </div>
        <button
          type="button"
          onClick={() => setHasSubmitted(false)}
          className="text-[11px] font-bold text-emerald-700 dark:text-emerald-300 hover:underline shrink-0 cursor-pointer"
        >
          {t.editAnswers}
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
              {t.header}
            </h4>
            <p className="text-xs text-charcoal-500 dark:text-amber-200/80">
              {t.subtitle}
            </p>
          </div>
        </div>

        {/* Progress Pill */}
        <span className="shrink-0 rounded-full bg-amber-100/80 dark:bg-amber-950 px-2.5 py-0.5 text-[11px] font-bold text-amber-900 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          {answeredCount}/{totalQuestions} {t.answered}
        </span>
      </div>

      {/* Dynamic Questions Form */}
      <form onSubmit={handleSubmitAll} className="space-y-3.5">
        {questions.map((q, idx) => {
          const fieldKey = q.id || q.field || `field_${idx}`;
          const isDropdown = q.input_type === 'dropdown' || (q.options && q.options.length > 4);
          const isNumber = q.input_type === 'number' || (!isDropdown && (!q.options || q.options.length === 0));
          const currentValue = formValues[fieldKey];
          const localizedQuestionText = getLocalizedQuestion(q, langKey);

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
                  <span>{localizedQuestionText}</span>
                </label>
                {q.required && (
                  <span className="text-[10px] font-medium text-amber-800 bg-amber-100/70 dark:bg-amber-950 dark:text-amber-300 px-1.5 py-0.2 rounded">
                    {t.required}
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
                      {t.selectOption}
                    </option>
                    {q.options && q.options.map((opt, oIdx) => (
                      <option key={oIdx} value={opt}>
                        {getLocalizedOption(opt, langKey)}
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
                    placeholder={t.enterNumber}
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
                    const localizedOptionText = getLocalizedOption(opt, langKey);
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
                        <span>{localizedOptionText}</span>
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
              ? t.answerAllPrompt(totalQuestions)
              : t.readyPrompt}
          </p>

          <button
            type="submit"
            disabled={answeredCount === 0 || isSubmitting}
            className="inline-flex items-center gap-2 rounded-xl bg-forest-600 px-5 py-2.5 text-xs font-semibold text-white shadow-subtle hover:bg-forest-700 transition active:scale-95 disabled:opacity-40 disabled:hover:bg-forest-600 cursor-pointer dark:bg-emerald-600 dark:hover:bg-emerald-500"
          >
            <span>{t.submitButton(answeredCount, totalQuestions)}</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>
      </form>
    </div>
  );
}
