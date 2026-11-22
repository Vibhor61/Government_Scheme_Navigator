import React from 'react';
import {
  ArrowRight,
  BadgeCheck,
  Briefcase,
  GraduationCap,
  Landmark,
  Mic,
  ShieldCheck,
  Sparkles,
  Sun,
  Wheat
} from 'lucide-react';
import { t } from '../utils/i18n';

export default function EmptyState({ onSelectPrompt, language = 'en', onOpenVoice }) {
  const isHindi = language === 'hi';

  const getPromptsByLanguage = (lang) => {
    switch (lang) {
      case 'kn':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'ಕೃಷಿ ಮತ್ತು ರೈತರು',
            title: 'ರೈತರ ಆದಾಯ ಬೆಂಬಲ & ಸೌರ ಪಂಪ್ ಸಬ್ಸಿಡಿ',
            description: 'PM-KISAN ₹6,000 ವಾರ್ಷಿಕ ನೆರವು ಮತ್ತು PM-KUSUM ಸೌರ ಕೃಷಿ ಪಂಪ್ ಸಹಾಯಧನ.',
            query: 'ರೈತರಿಗಾಗಿ ಪಿಎಂ-ಕಿಸಾನ್ ಆದಾಯ ಬೆಂಬಲ ಮತ್ತು ಪಿಎಂ-ಕುಸುಮ್ ಸೌರ ಪಂಪ್ ಸಬ್ಸಿಡಿ ಯೋಜನೆಗಳ ಅರ್ಹತೆ ಮತ್ತು ಅರ್ಜಿ ವಿಧಾನ ತಿಳಿಸಿ.'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'ಉನ್ನತ ಶಿಕ್ಷಣ & ವಿದ್ಯಾರ್ಥಿವೇತನ',
            title: 'ಎಂಜಿನಿಯರಿಂಗ್ ಮತ್ತು ಉನ್ನತ ಶಿಕ್ಷಣ ವಿದ್ಯಾರ್ಥಿವೇತನ',
            description: 'PM-USP ಕೇಂದ್ರ ವಲಯದ ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಬಡ್ಡಿ ಸಹಾಯಧನದ ಶಿಕ್ಷಣ ಸಾಲಗಳು.',
            query: 'ಬಿಟೆಕ್ ಎಂಜಿನಿಯರಿಂಗ್ ಮತ್ತು ಕಾಲೇಜು ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಪಿಎಂ-ಯುಎಸ್ಪಿ ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು ಶೈಕ್ಷಣಿಕ ಸಾಲದ ಅರ್ಹತೆಯನ್ನು ತಿಳಿಸಿ.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'ಸ್ವಚ್ಛ ಇಂಧನ',
            title: 'ಪಿಎಂ ಸೂರ್ಯ ಘರ್ ಉಚಿತ ವಿದ್ಯುತ್ ಯೋಜನೆ',
            description: 'ರೂಫ್‌ಟಾಪ್ ಸೌರ ಅಳವಡಿಕೆಗೆ ₹78,000 ವರೆಗೆ ಕೇಂದ್ರ ಸಬ್ಸಿಡಿ ಮತ್ತು ಶೂನ್ಯ ವಿದ್ಯುತ್ ಬಿಲ್.',
            query: 'ಪಿಎಂ ಸೂರ್ಯ ಘರ್ ಮುಫ್ಟ್ ಬಿಜ್ಲಿ ಯೋಜನೆಯಡಿ ಸೌರ ಫಲಕಗಳ ಸಬ್ಸಿಡಿ, ಅರ್ಹತೆ ಮತ್ತು ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆ ಏನು?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'ಮಹಿಳೆ ಮತ್ತು ಸಣ್ಣ ಉದ್ಯಮ',
            title: 'ಮುದ್ರಾ ಸಾಲ ಮತ್ತು ಲಖಪತಿ ದೀದಿ ಯೋಜನೆಗಳು',
            description: 'ಖಾತರಿಯಿಲ್ಲದೆ ₹10 ಲಕ್ಷದವರೆಗೆ ಮುದ್ರಾ ವ್ಯಾಪಾರ ಸಾಲ ಮತ್ತು ಮಹಿಳಾ ಜೀವನೋಪಾಯ ಬೆಂಬಲ.',
            query: 'ಹೊಸ ಸಣ್ಣ ವ್ಯಾಪಾರ ಆರಂಭಿಸಲು ಮುದ್ರಾ ಸಾಲ ಮತ್ತು ಮಹಿಳಾ ಸ್ವಸಹಾಯ ಗುಂಪುಗಳಿಗೆ ಲಖಪತಿ ದೀದಿ ಯೋಜನೆಯ ವಿವರಗಳನ್ನು ನೀಡಿ.'
          }
        ];
      case 'bn':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'কৃষি ও কৃষক',
            title: 'কৃষক আয় সহায়তা এবং সৌর পাম্প ভর্তুকি',
            description: 'PM-KISAN বার্ষিক ₹৬,০০০ সহায়তা এবং PM-KUSUM সৌর সেচ পাম্প অনুদান।',
            query: 'কৃষকদের জন্য পিএম-কিসান আয় সহায়তা এবং পিএম-কুসুম সৌর পাম্প ভর্তুকি প্রকল্পের যোগ্যতা এবং আবেদন পদ্ধতি জানান।'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'উচ্চ শিক্ষা ও বৃত্তি',
            title: 'ইঞ্জিনিয়ারিং ও উচ্চ শিক্ষার জন্য বৃত্তি',
            description: 'PM-USP কেন্দ্রীয় খাতের বৃত্তি এবং সুদ ভর্তুকিযুক্ত শিক্ষা ঋণ প্রকল্প।',
            query: 'বিটেক ইঞ্জিনিয়ারিং এবং কলেজ শিক্ষার্থীদের জন্য পিএম-ইউএসপি বৃত্তি এবং সরকারি শিক্ষা ঋণের যোগ্যতা জানান।'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'পরিচ্ছন্ন শক্তি',
            title: 'পিএম সূর্য ঘর বিনামূল্যে বিদ্যুৎ যোজনা',
            description: 'ছাদে সোলার প্যানেল স্থাপনের জন্য ₹৭৮,০০০ পর্যন্ত সরকারি অনুদান।',
            query: 'পিএম সূর্য ঘর বিনামূল্যে বিদ্যুৎ যোজনার আওতায় ছাদে সোলার প্যানেল বসানোর অনুদান, যোগ্যতা ও আবেদন পদ্ধতি কী?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'নারী ও ক্ষুদ্র উদ্যোগ',
            title: 'মুদ্রা ঋণ ও লাখপতি দিদি যোজনা',
            description: 'গ্যারান্টি ছাড়া ₹১০ লাখ পর্যন্ত মুদ্রা ব্যবসা ঋণ ও নারীদের জীবিকা সহায়তা।',
            query: 'নতুন ছোট ব্যবসা শুরুর জন্য মুদ্রা ঋণ এবং মহিলা স্বনির্ভর দলের লাখপতি দিদি যোজনার তথ্য দিন।'
          }
        ];
      case 'hi':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'कृषि एवं किसान',
            title: 'किसान आय सहायता एवं सौर पंप सब्सिडी',
            description: 'PM-KISAN ₹6,000 वार्षिक सहायता एवं PM-KUSUM सौर कृषि पंप अनुदान।',
            query: 'किसानों के लिए पीएम-किसान आय सहायता और पीएम-कुसुम सोलर पंप सब्सिडी योजनाओं की पात्रता और आवेदन प्रक्रिया बताएं।'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'उच्च शिक्षा एवं छात्रवृत्ति',
            title: 'इंजीनियरिंग एवं उच्च शिक्षा छात्रवृत्ति',
            description: 'PM-USP केंद्रीय क्षेत्र छात्रवृत्ति एवं ब्याज अनुदान शिक्षा ऋण योजनाएं।',
            query: 'बीटेक इंजीनियरिंग और कॉलेज छात्रों के लिए पीएम-यूएसपी छात्रवृत्ति और सरकारी शिक्षा ऋण की पात्रता बताएं।'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'स्वच्छ ऊर्जा',
            title: 'पीएम सूर्य घर मुफ्त बिजली योजना',
            description: 'छत पर सोलर पैनल लगाने हेतु ₹78,000 तक की केंद्रीय सब्सिडी व शून्य बिजली बिल।',
            query: 'पीएम सूर्य घर मुफ्त बिजली योजना के तहत छत पर सोलर पैनल लगाने की सब्सिडी, पात्रता और आवेदन प्रक्रिया क्या है?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'महिला एवं लघु उद्योग',
            title: 'मुद्रा ऋण एवं लखपति दीदी योजनाएं',
            description: 'बिना गारंटी ₹10 लाख तक का मुद्रा व्यापार ऋण एवं महिला आजीविका सहायता।',
            query: 'नया छोटा व्यापार शुरू करने के लिए मुद्रा लोन और महिला स्वयं सहायता समूहों के लिए लखपति दीदी योजना की जानकारी दें।'
          }
        ];
      case 'mr':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'कृषी आणि शेतकरी',
            title: 'शेतकरी उत्पन्न सहाय्य आणि सौर पंप सबसिडी',
            description: 'PM-KISAN ₹६,००० वार्षिक सहाय्य आणि PM-KUSUM सौर कृषी पंप अनुदान.',
            query: 'शेतकऱ्यांसाठी पीएम-किसान उत्पन्न सहाय्य आणि पीएम-कुसुम सौर पंप सबसिडी योजनांची पात्रता आणि अर्ज प्रक्रिया सांगा.'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'उच्च शिक्षण आणि शिष्यवृत्ती',
            title: 'अभियांत्रिकी आणि उच्च शिक्षण शिष्यवृत्ती',
            description: 'PM-USP केंद्रीय क्षेत्रातील शिष्यवृत्ती आणि व्याज अनुदानित शैक्षणिक कर्ज योजना.',
            query: 'बीटेक अभियांत्रिकी आणि महाविद्यालयीन विद्यार्थ्यांसाठी पीएम-यूएसपी शिष्यवृत्ती आणि शैक्षणिक कर्जाची पात्रता सांगा.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'स्वच्छ ऊर्जा',
            title: 'पीएम सूर्य घर मोफत वीज योजना',
            description: 'छतावर सौर पॅनेल बसवण्यासाठी ₹७८,००० पर्यंत केंद्रीय सबसिडी आणि शून्य वीज बिल.',
            query: 'पीएम सूर्य घर मोफत वीज योजनेअंतर्गत छतावर सोलर पॅनेल बसवण्याची सबसिडी, पात्रता आणि अर्ज प्रक्रिया काय आहे?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'महिला आणि सूक्ष्म उद्योग',
            title: 'मुद्रा कर्ज आणि लखपती दीदी योजना',
            description: 'विनाहमी ₹१० लाखांपर्यंत मुद्रा व्यवसाय कर्ज आणि महिला उपजीविका सहाय्य.',
            query: 'नवीन छोटा व्यवसाय सुरू करण्यासाठी मुद्रा कर्ज आणि महिला बचत गटांसाठी लखपती दीदी योजनेची माहिती द्या.'
          }
        ];
      case 'ta':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'விவசாயம் & விவசாயிகள்',
            title: 'விவசாயிகள் வருமான ஆதரவு & சோலார் பம்ப் மானியம்',
            description: 'PM-KISAN ₹6,000 ஆண்டு உதவி மற்றும் PM-KUSUM சோலார் பம்ப் மானியம்.',
            query: 'விவசாயிகளுக்கான பிஎம்-கிசான் உதவி மற்றும் பிஎம்-குசும் சோலார் பம்ப் மானிய திட்டங்களின் தகுதி மற்றும் விண்ணப்ப முறையைக் கூறவும்.'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'உயர் கல்வி & உதவித்தொகை',
            title: 'பொறியியல் & உயர் கல்வி உதவித்தொகை',
            description: 'PM-USP மத்திய துறை உதவித்தொகை மற்றும் வட்டி மானியத்துடன் கூடிய கல்வி கடன்கள்.',
            query: 'பி.டெக் மற்றும் கல்லூரி மாணவர்களுக்கான கல்வி உதவித்தொகை மற்றும் கல்வி கடன் தகுதியை விளக்குங்கள்.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'சுத்தமான ஆற்றல்',
            title: 'பிஎம் சூர்ய கர் இலவச மின்சார திட்டம்',
            description: 'வீட்டுக்கூரை சோலார் பேனல்களுக்கு ₹78,000 வரை மானியம் மற்றும் பூஜ்ஜிய மின்கட்டணம்.',
            query: 'பிஎம் சூர்ய கர் சோலார் மானியத்தின் தகுதி, சலுகைகள் மற்றும் விண்ணப்பிக்கும் நடைமுறைகள் என்ன?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'பெண்கள் & சிறுதொழில்',
            title: 'முத்ரா கடன் & லக்பதி தீதி திட்டங்கள்',
            description: 'பிணையற்ற ₹10 லட்சம் வரை முத்ரா வணிகக் கடன் மற்றும் மகளிர் வாழ்வாதார உதவி.',
            query: 'புதிய சிறுதொழில் தொடங்க முத்ரா கடன் மற்றும் மகளிர் சுயஉதவி குழுக்களுக்கான லக் பதி தீதி திட்டம் பற்றி கூறவும்.'
          }
        ];
      case 'te':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'వ్యవసాయం & రైతులు',
            title: 'రైతు ఆదాయ సహాయం & సోలార్ పంప్ సబ్సిడీ',
            description: 'PM-KISAN ₹6,000 వార్షిక సహాయం మరియు PM-KUSUM సోలార్ పంప్ సబ్సిడీ.',
            query: 'రైతుల కోసం పీఎం-కిసాన్ ఆదాయ సహాయం మరియు పీఎం-కుసుమ్ సోలార్ పంప్ సబ్సిడీ పథకాల అర్హత మరియు దరఖాస్తు విధానం చెప్పండి.'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'ఉన్నత విద్య & స్కాలర్‌షిప్‌లు',
            title: 'ఇంజనీరింగ్ మరియు ఉన్నత విద్య స్కాలర్‌షిప్‌లు',
            description: 'PM-USP కేంద్ర రంగ స్కాలర్‌షిప్‌లు మరియు వడ్డీ సబ్సిడీ గల విద్యా రుణాలు.',
            query: 'బీటెక్ ఇంజనీరింగ్ మరియు కాలేజీ విద్యార్థుల కోసం స్కాలర్‌షిప్ మరియు విద్యా రుణ పథకాల అర్హతను వివరించండి.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'స్వచ్ఛమైన శక్తి',
            title: 'పీఎం సూర్య ఘర్ ఉచిత విద్యుత్ యోజన',
            description: 'పైకప్పు సోలార్ ప్యానెల్లకు ₹78,000 వరకు కేంద్ర సబ్సిడీ మరియు సున్నా విద్యుత్ బిల్లు.',
            query: 'పీఎం సూర్య ఘర్ ఉచిత విద్యుత్ యోజన కింద సోలార్ ప్యానెల్ సబ్సిడీ, అర్హత మరియు దరఖాస్తు విధానం ఏమిటి?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'మహిళలు & చిన్న వ్యాపారాలు',
            title: 'ముద్రా రుణాలు & లఖ్‌పతి దీదీ పథకాలు',
            description: 'ఎటువంటి పూచీకత్తు లేకుండా ₹10 లక్షల వరకు ముద్రా వ్యాపార రుణాలు మరియు మహిళా జీవనోపాధి.',
            query: 'కొత్త చిన్న వ్యాపారం ప్రారంభించడానికి ముద్రా రుణం మరియు మహిళల స్వయం సహాయక బృందాల లఖపతి దీదీ పథకం సమాచారం ఇవ్వండి.'
          }
        ];
      case 'gu':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'કૃષિ અને ખેડૂત',
            title: 'ખેડૂત આવક સહાય અને સોલર પંપ સબસિડી',
            description: 'PM-KISAN ₹6,000 વાર્ષિક સહાય અને PM-KUSUM સોલર પંપ અનુદાન.',
            query: 'ખેડૂતો માટે પીએમ-કિસાન આવક સહાય અને પીએમ-કુસુમ સોલર પંપ સબસિડી યોજનાઓની પાત્રતા અને અરજી પ્રક્રિયા જણાવો.'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'ઉચ્ચ શિક્ષણ અને શિષ્યવૃત્તિ',
            title: 'એન્જિનિયરિંગ અને ઉચ્ચ શિક્ષણ શિષ્યવૃત્તિ',
            description: 'PM-USP કેન્દ્રીય ક્ષેત્ર શિષ્યવૃત્તિ અને વ્યાજ સબસિડીવાળી એજ્યુકેશન લોન યોજનાઓ.',
            query: 'બીટેક એન્જિનિયરિંગ અને કોલેજના વિદ્યાર્થીઓ માટે પીએમ-યુએસપી સ્કોલરશીપ અને એજ્યુકેશન લોનની પાત્રતા જણાવો.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'સ્વચ્છ ઊર્જા',
            title: 'પીએમ સૂર્ય ઘર મફત વીજળી યોજના',
            description: 'ધાબા પર સોલર પેનલ લગાવવા માટે ₹78,000 સુધીની સબસિડી અને શૂન્ય વીજળી બિલ.',
            query: 'પીએમ સૂર્ય ઘર મફત વીજળી યોજના હેઠળ સોલાર પેનલ સબસિડી, પાત્રતા અને અરજી પ્રક્રિયા શું છે?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'મહિલા અને લઘુ ઉદ્યોગ',
            title: 'મુદ્રા લોન અને લખપતિ દીદી યોજના',
            description: 'ગેરંટી વિના ₹10 લાખ સુધીની મુદ્રા બિઝનેસ લોન અને મહિલા આજીવિકા સહાય.',
            query: 'નવો નાનો વ્યવસાય શરૂ કરવા માટે મુદ્રા લોન અને મહિલા સ્વ-સહાય જૂથો માટે લખપતિ દીદી યોજનાની માહિતી આપો.'
          }
        ];
      case 'pa':
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'ਖੇਤੀਬਾੜੀ ਅਤੇ ਕਿਸਾਨ',
            title: 'ਕਿਸਾਨ ਆਮਦਨ ਸਹਾਇਤਾ ਅਤੇ ਸੋਲਰ ਪੰਪ ਸਬਸਿਡੀ',
            description: 'PM-KISAN ₹6,000 ਸਾਲਾਨਾ ਸਹਾਇਤਾ ਅਤੇ PM-KUSUM ਸੋਲਰ ਪੰਪ ਗ੍ਰਾਂਟ।',
            query: 'ਕਿਸਾਨਾਂ ਲਈ ਪੀਐਮ-ਕਿਸਾਨ ਆਮਦਨ ਸਹਾਇਤਾ ਅਤੇ ਪੀਐਮ-ਕੁਸੁਮ ਸੋਲਰ ਪੰਪ ਸਬਸਿਡੀ ਯੋਜਨਾਵਾਂ ਦੀ ਯੋਗਤਾ ਅਤੇ ਅਰਜ਼ੀ ਪ੍ਰਕਿਰਿਆ ਦੱਸੋ।'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'ਉੱਚ ਸਿੱਖਿਆ ਅਤੇ ਵਜ਼ੀਫ਼ੇ',
            title: 'ਇੰਜੀਨੀਅਰਿੰਗ ਅਤੇ ਉੱਚ ਸਿੱਖਿਆ ਵਜ਼ੀਫ਼ੇ',
            description: 'PM-USP ਕੇਂਦਰੀ ਖੇਤਰ ਵਜ਼ੀਫ਼ਾ ਅਤੇ ਵਿਆਜ ਸਬਸਿਡੀ ਵਾਲੇ ਸਿੱਖਿਆ ਕਰਜ਼ੇ।',
            query: 'ਬੀਟੈੱਕ ਇੰਜੀਨੀਅਰਿੰਗ ਅਤੇ ਕਾਲਜ ਦੇ ਵਿਦਿਆਰਥੀਆਂ ਲਈ ਵਜ਼ੀਫ਼ੇ ਅਤੇ ਸਿੱਖਿਆ ਕਰਜ਼ਾ ਯੋਜਨਾਵਾਂ ਦੀ ਯੋਗਤਾ ਦੱਸੋ।'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'ਸਵੱਛ ਊਰਜਾ',
            title: 'ਪੀਐਮ ਸੂਰਜ ਘਰ ਮੁਫ਼ਤ ਬਿਜਲੀ ਯੋਜਨਾ',
            description: 'ਛੱਤ ਉੱਤੇ ਸੋਲਰ ਪੈਨਲ ਲਗਾਉਣ ਲਈ ₹78,000 ਤੱਕ ਦੀ ਕੇਂਦਰੀ ਸਬਸਿਡੀ ਅਤੇ ਜ਼ੀਰੋ ਬਿਜਲੀ ਬਿੱਲ।',
            query: 'ਪੀਐਮ ਸੂਰਜ ਘਰ ਮੁਫ਼ਤ ਬਿਜਲੀ ਯੋਜਨਾ ਤਹਿਤ ਸੋਲਰ ਪੈਨਲ ਸਬਸਿਡੀ, ਯੋਗਤਾ ਅਤੇ ਅਰਜ਼ੀ ਪ੍ਰਕਿਰਿਆ ਕੀ ਹੈ?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'ਔਰਤਾਂ ਅਤੇ ਛੋਟੇ ਕਾਰੋਬਾਰ',
            title: 'ਮੁਦਰਾ ਕਰਜ਼ਾ ਅਤੇ ਲਖਪਤੀ ਦੀਦੀ ਯੋਜਨਾਵਾਂ',
            description: 'ਬਿਨਾਂ ਗਾਰੰਟੀ ₹10 ਲੱਖ ਤੱਕ ਦਾ ਮੁਦਰਾ ਵਪਾਰ ਕਰਜ਼ਾ ਅਤੇ ਔਰਤਾਂ ਦੀ ਰੋਜ਼ੀ-ਰੋਟੀ ਸਹਾਇਤਾ।',
            query: 'ਨਵਾਂ ਛੋਟਾ ਕਾਰੋਬਾਰ ਸ਼ੁਰੂ ਕਰਨ ਲਈ ਮੁਦਰਾ ਲੋਨ ਅਤੇ ਲਖਪਤੀ ਦੀਦੀ ਯੋਜਨਾ ਦੀ ਜਾਣਕਾਰੀ ਦਿਓ।'
          }
        ];
      default:
        return [
          {
            id: 'agriculture',
            icon: Wheat,
            number: '01',
            accent: 'bg-forest-50 text-forest-700 border-forest-100 dark:bg-forest-950/60 dark:text-emerald-300 dark:border-forest-900',
            tag: 'Agriculture & farmers',
            title: 'Income support & solar pumps',
            description: 'Explore PM-KISAN income support and PM-KUSUM solar irrigation subsidies.',
            query: 'What are the eligibility criteria and application steps for PM-KISAN income support and PM-KUSUM solar irrigation pump subsidies?'
          },
          {
            id: 'education',
            icon: GraduationCap,
            number: '02',
            accent: 'bg-sky-50 text-sky-800 border-sky-100 dark:bg-sky-950/40 dark:text-sky-300 dark:border-sky-900/70',
            tag: 'Education & scholarships',
            title: 'Scholarships for higher education',
            description: 'Explore PM-USP scholarships and interest-subsidized higher education loans.',
            query: 'Find scholarship and education loan subsidy schemes for B.Tech engineering college students, such as PM-USP.'
          },
          {
            id: 'solar',
            icon: Sun,
            number: '03',
            accent: 'bg-amber-50 text-amber-800 border-amber-100 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900/70',
            tag: 'Clean energy',
            title: 'Rooftop solar with PM Surya Ghar',
            description: 'Explore rooftop solar support, including the PM Surya Ghar subsidy.',
            query: 'How do I apply for the PM Surya Ghar Muft Bijli Yojana rooftop solar subsidy, and what are the exact subsidy slabs?'
          },
          {
            id: 'enterprise',
            icon: Briefcase,
            number: '04',
            accent: 'bg-orange-50 text-orange-800 border-orange-100 dark:bg-orange-950/40 dark:text-orange-300 dark:border-orange-900/70',
            tag: 'Women & enterprise',
            title: 'Loans for small businesses',
            description: 'Explore Mudra business loans and support for women-led enterprises.',
            query: 'What government loan schemes exist for small startups and women entrepreneurs, like Mudra Yojana and Lakhpati Didi?'
          }
        ];
    }
  };

  const prompts = getPromptsByLanguage(language);

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-5 sm:px-7 sm:py-7 lg:px-10">
      <section className="navigator-hero relative overflow-hidden rounded-[1.75rem] text-white shadow-elevated">
        <div className="navigator-hero-art pointer-events-none absolute inset-0" aria-hidden="true" />
        <div className="relative grid gap-6 p-6 sm:p-9 md:grid-cols-[minmax(0,1.2fr)_minmax(250px,0.8fr)] md:items-center md:gap-5 lg:grid-cols-[1.3fr_0.7fr] lg:gap-8 lg:items-end lg:p-11">
          <div className="max-w-2xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-semibold text-emerald-50 backdrop-blur-sm">
              <Landmark className="h-4 w-4 text-amber-300" aria-hidden="true" />
              <span>{t('portal_subtitle', language)}</span>
            </div>

            <h2 className="max-w-xl text-3xl font-semibold leading-[1.08] tracking-tight sm:text-4xl lg:text-5xl">
              {t('hero_title', language)}
            </h2>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-emerald-50/85 sm:text-base">
              {t('hero_subtitle', language)}
            </p>

            {/* Primary Voice Action for Easy Access */}
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={onOpenVoice}
                className="group relative inline-flex items-center gap-3.5 rounded-2xl bg-gradient-to-r from-amber-400 via-amber-300 to-amber-400 px-6 py-3.5 text-forest-950 shadow-xl shadow-amber-950/25 transition-all hover:scale-[1.03] active:scale-95 cursor-pointer border border-amber-200"
              >
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-forest-900 text-amber-300 shadow-inner group-hover:bg-forest-950 transition">
                  <Mic className="h-5 w-5 animate-pulse" />
                </span>
                <span className="flex flex-col text-left">
                  <span className="text-base font-extrabold tracking-tight">
                    {t('hero_voice_btn', language)}
                  </span>
                  <span className="text-[11px] font-semibold text-forest-800">
                    {t('tap_to_speak', language)}
                  </span>
                </span>
              </button>
            </div>

            <div className="mt-6 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs font-medium text-emerald-50/90 sm:text-sm">
              <span className="inline-flex items-center gap-2">
                <BadgeCheck className="h-4 w-4 text-amber-300" aria-hidden="true" />
                {t('official_sources_badge', language)}
              </span>
              <span className="inline-flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-amber-300" aria-hidden="true" />
                {t('eligibility_made_clear', language)}
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
                    {t('a_clearer_way_forward', language)}
                  </p>
                  <p className="mt-1 text-lg font-semibold">
                    {t('your_path_to_support', language)}
                  </p>
                </div>
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-300 text-forest-950">
                  <Sparkles className="h-5 w-5" aria-hidden="true" />
                </span>
              </div>
              <div className="mt-4 space-y-3">
                {[
                  t('step_share_need', language),
                  t('step_find_schemes', language)
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
              {t('suggested_heading', language)}
            </p>
            <h3 id="starting-points-title" className="mt-1 text-xl font-semibold tracking-tight text-charcoal-900 dark:text-sand-50 sm:text-2xl">
              {t('hero_title', language)}
            </h3>
          </div>
          <p className="max-w-sm text-sm text-charcoal-500 dark:text-charcoal-300">
            {t('hero_subtitle', language)}
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
                    {t('explore_schemes', language)}
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
            {t('grounded_footnote', language)}
          </span>
        </div>
      </section>
    </div>
  );
}
