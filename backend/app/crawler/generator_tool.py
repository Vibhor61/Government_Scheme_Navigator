"""
Response Generator Tool: Adaptive, Free-Form Response Synthesizer.
Crafts natural, citizen-centered, cite-grounded Markdown responses.
Adapts freely to the exact conversational stage:
  - Middle Stage (questions pending): Introduces matching schemes and guides citizen on the interactive card.
  - Final Stage (criteria complete): Issues grounded verdict, benefits breakdown, required documents, and official links.
  - Comparison: Side-by-side comparative analysis.
  - Procedural: Step-by-step application process walkthrough.
  - Multilingual: Synthesizes responses natively in citizen's preferred language & script (Kannada, Hindi, Bengali, Tamil, etc.).
"""

import json
import logging
from typing import Any, Dict, List, Optional
from ..config import settings
from .llm_service import llm_service
from .observability import observe
from .domain_guard import generate_service_unavailable_response

logger = logging.getLogger("gov_scheme.tools.generator")

GENERATOR_SYSTEM_PROMPT = """You are the official myScheme Indian Government Welfare Scheme AI Assistant.
Your mission is to provide clear, empathetic, citizen-centric, and 100% evidence-grounded answers.

CRITICAL RULES ON QUESTIONS & FORMATTING (STRICTLY ENFORCED):
- NEVER WRITE QUESTIONS, CHECKLISTS OF OPTIONS, OR QUESTIONNAIRES IN YOUR TEXT RESPONSE.
- The web application automatically renders a dedicated interactive questionnaire card below your response for any missing criteria.
- In the text response, your role during the Middle Stage is ONLY to:
  * Warmly introduce the candidate schemes discovered.
  * Highlight their financial assistance amounts and key benefits.
  * Politely invite the citizen to fill in the interactive questions card shown below.
- Do NOT write things like "Please answer the following questions:", "[ ] Yes", "[ ] No", "Enter amount:", or bulleted lists of questions. Doing so is redundant and strictly forbidden.

GUIDING PRINCIPLES:
1. ADAPTIVE TO CONVERSATIONAL STAGE:
   - If Citizen has submitted questionnaire answers or query is an ELIGIBILITY EVALUATION:
     * PRIMARY MANDATE: YOUR MAIN FOCUS MUST BE DELIVERING A FULL, AUTHORITATIVE ELIGIBILITY EVALUATION FOR EACH SCHEME.
     * Deliver an Executive Verdict for each scheme in the citizen's target language (e.g. "✅ पात्र / ELIGIBLE", "⚠️ सशर्त / CONDITIONAL", or "❌ अपात्र / INELIGIBLE").
     * Include a Markdown Criteria Evaluation Table with column headers fully translated into the target language.
     * Translate all table column headers ("Rule / Condition", "Required Criteria", "Your Detail", "Status"), statuses ("MET", "UNKNOWN", "NOT MET"), verdicts, and section headers ("Financial Assistance", "Document Checklist", "Official Portal", "Next Steps") strictly into the target language.
     * Calculate and clearly state the exact Financial Assistance / Subsidy amount they are entitled to receive.
     * Provide the mandatory Document Checklist required for submission.
     * Provide step-by-step application directions and direct link to the verified official portal (*.gov.in / *.nic.in).
     * DO NOT treat this as an initial discovery search; DO NOT ask the user to fill out the questionnaire again. Focus 100% on the evaluation.
   - If questions are being asked (Middle Stage - only if initial inquiry with zero profile):
     * Warmly introduce the candidate schemes discovered.
     * Highlight their key financial benefits and who they are designed for.
     * Politely explain that to confirm their exact eligibility tier or subsidy amount, they should answer the quick interactive questions presented on the card below.
   - If profile is complete (Final Stage):
     * Deliver a clear eligibility verdict based on the criteria.
     * Clearly summarize the financial assistance / subsidy / grant amount.
     * Provide an official Document Checklist required for application.
     * Provide the authentic official portal link (*.gov.in / *.nic.in) to apply.
   - If Workflow is COMPARISON:
     * Provide a clear side-by-side comparison table (benefits, eligibility limits, interest rates/subsidies, nodal ministry).
   - If Workflow is PROCEDURAL_GUIDE:
     * Provide a numbered, step-by-step application walkthrough (Online DigiLocker/Aadhaar registration vs Offline CSC center).
   - If Candidate Schemes list is EMPTY:
     * State clearly, politely, and transparently that no direct scheme matching this exact query was found in the official national repository.
     * Guide the citizen on which nodal ministry (e.g., Ministry of Agriculture, Ministry of MSME, State Department) or district office to contact for local or unindexed grants.
     * DO NOT invent fake schemes. Provide actionable next steps.

2. GROUNDING & HONESTY:
   - Ground all claims in the provided scheme guidelines and quotes.
   - Do not invent non-existent benefits or guarantee approvals.
   - Use clean, readable GitHub Markdown with emojis, bullet points, and bold section headers.

3. MULTILINGUAL & VERNACULAR SCRIPT SYNTHESIS:
   - When Target Language is NOT English (e.g., Kannada 'kn', Hindi 'hi', Bengali 'bn', Marathi 'mr', Tamil 'ta', Telugu 'te', Gujarati 'gu'):
     * Write the ENTIRE text response ('answer_markdown') and all 'key_takeaways' in authentic regional script (e.g., Kannada script ಕನ್ನಡ for Kannada, Devanagari script देवनागरी for Hindi/Marathi, Bengali script বাংলা, etc.).
     * Never generate transliterated English/Latin sentences when a regional language is requested (e.g., do not write 'nimma aayushya'; write 'ನಿಮ್ಮ ವಯಸ್ಸು').
     * PRESERVE OFFICIAL TECHNICAL ENTITIES:
       - Keep official scheme names identifiable: e.g. in Kannada: "ಕಿಸಾನ್ ಕ್ರೆಡಿಟ್ ಕಾರ್ಡ್ (PM-KCC Scheme)" or "ರೈತ ವಿದ್ಯಾನಿಧಿ ಯೋಜನೆ (Raita Vidyanidhi)".
       - Keep official URLs unchanged: e.g. [myScheme ಅಧಿಕೃತ ಪೋರ್ಟಲ್](https://www.myscheme.gov.in)
       - Keep Markdown table syntax (|---|) and status icons (✅, ⚠️, ❌) clean and intact.

Respond with JSON:
{
  "answer_markdown": "Full adaptive Markdown response for the citizen...",
  "key_takeaways": [
    "Key takeaway point 1",
    "Key takeaway point 2",
    "Key takeaway point 3"
  ]
}"""


class ResponseGeneratorTool:
    """
    Agentic Tool for Adaptive Free-Form Response Generation.
    Tool Name: 'response_generator_tool'
    """

    name: str = "response_generator_tool"
    description: str = (
        "Synthesizes natural, context-adaptive Markdown responses for citizens across all stages: "
        "introducing candidate schemes during clarification, issuing verdicts on completion, or comparing programs."
    )

    def __init__(self):
        self.llm = llm_service

    @observe(name="ResponseGeneratorTool.execute")
    def execute(
        self,
        user_query: str,
        workflow: str,
        candidate_schemes: List[Dict[str, Any]],
        questionnaire_status: Dict[str, Any],
        beneficiary_context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        known_criteria: Optional[Dict[str, Any]] = None,
        evaluated_schemes: Optional[List[Dict[str, Any]]] = None,
        is_evaluation_turn: bool = False,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """
        Executes adaptive free-form response generation with cross-lingual synthesis.
        """
        has_questions = bool(questionnaire_status.get("questions"))
        is_eval = is_evaluation_turn or workflow == "ELIGIBILITY_CHECK" or bool(evaluated_schemes and any(s.get("eligibility_matrix") for s in evaluated_schemes))

        if is_eval:
            stage_desc = (
                "ELIGIBILITY EVALUATION STAGE: The citizen has filled in their profile details / questionnaire. "
                "YOUR MAIN FOCUS MUST BE GIVING A FULL, RIGOROUS ELIGIBILITY EVALUATION FOR EACH SCHEME."
            )
        elif has_questions:
            stage_desc = (
                "MIDDLE STAGE (questions are being presented to the user to resolve remaining eligibility criteria)"
            )
        else:
            stage_desc = "FINAL STAGE (all criteria are resolved; deliver complete eligibility assessment)"

        compact_schemes = []
        for s in candidate_schemes[:4]:
            compact_schemes.append({
                "name": s.get("scheme_name") or s.get("name"),
                "jurisdiction": s.get("jurisdiction") or s.get("level") or "Central",
                "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance",
                "eligibility_rules_summary": [
                    r.get("rule_text") or f"{r.get('field')} {r.get('operator')} {r.get('value')}"
                    for r in s.get("eligibility_rules", [])[:6] if isinstance(r, dict)
                ],
                "documents": s.get("documents", [])[:4],
                "application_steps": s.get("application_steps", [])[:3],
                "official_url": s.get("url") or (s.get("sources") and s["sources"][0].get("url")),
            })

        eval_summary = []
        if evaluated_schemes:
            for s in evaluated_schemes[:4]:
                s_name = s.get("scheme_name") or s.get("name")
                verdict = s.get("eligibility_status", "unknown")
                rule_checks = []
                for chk in s.get("eligibility_matrix", []):
                    rule_checks.append({
                        "rule": chk.get("label") or chk.get("rule_text") or f"{chk.get('field')} {chk.get('operator')} {chk.get('value')}",
                        "status": chk.get("status", "UNKNOWN"),
                    })
                eval_summary.append({
                    "scheme_name": s_name,
                    "overall_verdict": verdict,
                    "rule_evaluations": rule_checks,
                    "benefit": s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance",
                    "documents": s.get("documents", [])[:4],
                    "official_url": s.get("url"),
                })

        schemes_str = json.dumps(compact_schemes, ensure_ascii=False)
        eval_str = json.dumps(eval_summary, ensure_ascii=False, indent=2)
        q_status_str = json.dumps(questionnaire_status, ensure_ascii=False)
        criteria_str = json.dumps(known_criteria or {}, ensure_ascii=False)
        beneficiary_str = json.dumps(beneficiary_context or {}, ensure_ascii=False)

        lang_formatting_directive = ""
        if target_language and target_language != "en":
            spec = LANGUAGE_FORMAT_SPECS.get(target_language, LANGUAGE_FORMAT_SPECS.get("hi", LANGUAGE_FORMAT_SPECS["en"]))
            lang_formatting_directive = (
                f"\nCRITICAL ZERO-ENGLISH REQUIREMENT FOR {language_name.upper()} (Language Code: '{target_language}'):\n"
                f"- The citizen is interacting in {language_name}. DO NOT USE ANY ENGLISH for table headers, verdicts, status labels, or section headings.\n"
                f"- Every heading and label MUST be in authentic native {language_name} script.\n"
                f"- Table headers MUST EXACTLY BE: {spec['table_header']}\n"
                f"- Status column values MUST ONLY BE: {spec['met']} (for MET), {spec['unknown']} (for UNKNOWN), or {spec['not_met']} (for NOT MET).\n"
                f"- Verdicts MUST USE: {spec['verdict_eligible']}, {spec['verdict_conditional']}, or {spec['verdict_ineligible']}.\n"
                f"- Section headings MUST BE: {spec['financial_assistance']}, {spec['doc_checklist']}, {spec['official_portal']}, and {spec['next_steps']}.\n"
                f"- Retain only official scheme acronyms (e.g. PM-KISAN, PM-KUSUM) and URLs in Latin script. All other characters, words, sentences, and table cells MUST be in native {language_name} script!\n"
            )

        prompt = f"""Current Conversational Stage: {stage_desc}
Workflow Type: {workflow}
User Query: "{user_query}"
Target Beneficiary: {beneficiary_str}
Known Criteria So Far: {criteria_str}

Candidate Schemes:
{schemes_str}

Deterministic Eligibility Evaluation Matrix:
{eval_str}

Questionnaire Status:
{q_status_str}

TARGET CITIZEN LANGUAGE: {language_name} (code: '{target_language}')
{lang_formatting_directive}
IMPORTANT LANGUAGE INSTRUCTIONS:
- Generate the entire Markdown response and all key takeaways in authentic {language_name} using native {language_name} script (e.g. Kannada script ಕನ್ನಡ for Kannada, Devanagari script for Hindi/Marathi, Bengali script for Bengali).
- Maintain an empathetic, culturally respectful, and clear government counselor tone.
- PRESERVE: Keep official scheme acronyms (e.g. PM-KISAN, Ayushman Bharat, Raita Vidyanidhi), official portal URLs (*.gov.in / *.nic.in), and Markdown table structure intact.

Generate a helpful, empathetic, beautifully structured Markdown response for the citizen."""

        result = self.llm._call_groq_json(
            prompt=prompt,
            system_prompt=GENERATOR_SYSTEM_PROMPT,
            timeout=settings.LLM_TIMEOUT_SECONDS,
        )

        if result and isinstance(result, dict) and "answer_markdown" in result:
            return result

        logger.warning("ResponseGeneratorTool LLM call returned invalid response or hit rate limit; returning authentic service notice.")
        unavailable_msg = generate_service_unavailable_response(target_language)
        return {
            "answer_markdown": unavailable_msg,
            "key_takeaways": [
                "Upstream AI reasoning capacity reached (Groq API Rate Limit / HTTP 429). Please retry in 30 seconds."
            ],
        }

    def _fallback_generation(
        self,
        user_query: str,
        candidate_schemes: List[Dict[str, Any]],
        questionnaire_status: Dict[str, Any],
        evaluated_schemes: Optional[List[Dict[str, Any]]] = None,
        is_evaluation_turn: bool = False,
        known_criteria: Optional[Dict[str, Any]] = None,
        target_language: str = "en",
        language_name: str = "English",
    ) -> Dict[str, Any]:
        """Deterministic safety fallback for response synthesis."""
        has_questions = bool(questionnaire_status.get("questions"))
        lines = []

        HEADERS_MAP = {
            "kn": {
                "title": "## 📋 ಅಧಿಕೃತ ಅರ್ಹತಾ ಮೌಲ್ಯಮಾಪನ ವರದಿ\n",
                "desc": "ನೀವು ಸಲ್ಲಿಸಿದ ಅರ್ಹತಾ ವಿವರಗಳ ಆಧಾರದ ಮೇಲೆ, ಸರ್ಕಾರದ ಮಾರ್ಗಸೂಚಿಗಳ ಪರಿಶೀಲನೆ ಇಲ್ಲಿದೆ:\n",
                "intro": "🙏 **ನಿಮ್ಮ ಅಗತ್ಯಕ್ಕೆ ಹೊಂದಿಕೆಯಾಗುವ ಅಧಿಕೃತ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು:**\n",
                "benefit": "ಸೌಲಭ್ಯ ಮತ್ತು ಸಹಾಯಧನ:",
                "docs": "ಅಗತ್ಯ ದಾಖಲೆಗಳು:",
                "portal": "ಅಧಿಕೃತ ಪೋರ್ಟಲ್:",
                "q_prompt": "📋 **ಸಂಪೂರ್ಣ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಲು ದಯವಿಟ್ಟು ಕೆಳಗಿನ ತ್ವರಿತ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ.**",
                "eligible": "✅ **ನೀವು ಒದಗಿಸಿದ ವಿವರಗಳ ಪ್ರಕಾರ ಈ ಕಾರ್ಯಕ್ರಮಗಳಿಗೆ ನೀವು ಅರ್ಹರಾಗಿದ್ದೀರಿ.**"
            },
            "hi": {
                "title": "## 📋 आधिकारिक पात्रता मूल्यांकन रिपोर्ट\n",
                "desc": "आपके द्वारा दिए गए पात्रता विवरण के आधार पर आधिकारिक मूल्यांकन:\n",
                "intro": "🙏 **आपकी आवश्यकता के अनुसार आधिकारिक सरकारी कल्याणकारी योजनाएं:**\n",
                "benefit": "लाभ एवं वित्तीय सहायता:",
                "docs": "आवश्यक दस्तावेज:",
                "portal": "आधिकारिक पोर्टल:",
                "q_prompt": "📋 **अपनी पूर्ण पात्रता जांचने के लिए कृपया नीचे दिए गए त्वरित प्रश्नों के उत्तर दें।**",
                "eligible": "✅ **प्रदान किए गए विवरण के आधार पर आप इन योजनाओं के लिए पात्र हैं।**"
            },
            "bn": {
                "title": "## 📋 অফিসিয়াল যোগ্যতা মূল্যায়ন রিপোর্ট\n",
                "desc": "আপনার প্রদত্ত বিবরণের ভিত্তিতে সরকারি নির্দেশিকা অনুযায়ী যাচাইকৃত মূল্যায়ন:\n",
                "intro": "🙏 **আপনার অনুরোধের সাথে মিলে যাওয়া অফিসিয়াল সরকারি কল্যাণ প্রকল্পসমূহ:**\n",
                "benefit": "সুবিধা ও আর্থিক সহায়তা:",
                "docs": "প্রয়োজনীয় নথিপত্র:",
                "portal": "অফিসিয়াল পোর্টাল:",
                "q_prompt": "📋 **আপনার সম্পূর্ণ যোগ্যতা যাচাই করতে অনুগ্রহ করে নিচের প্রশ্নগুলির উত্তর দিন।**",
                "eligible": "✅ **প্রদত্ত মানদণ্ডের ভিত্তিতে আপনি এই প্রকল্পগুলির জন্য যোগ্য।**"
            },
            "mr": {
                "title": "## 📋 अधिकृत पात्रता मूल्यमापन अहवाल\n",
                "desc": "तुम्ही दिलेल्या तपशिलांवर आधारित सरकारी मार्गदर्शक तत्त्वांनुसार मूल्यमापन:\n",
                "intro": "🙏 **तुमच्या गरजेनुसार अधिकृत सरकारी कल्याणकारी योजना:**\n",
                "benefit": "लाभ आणि आर्थिक मदत:",
                "docs": "आवश्यक कागदपत्रे:",
                "portal": "अधिकृत पोर्टल:",
                "q_prompt": "📋 **तुमची पूर्ण पात्रता तपासण्यासाठी कृपया खालील प्रश्नांची उत्तरे द्या.**",
                "eligible": "✅ **दिलेल्या तपशिलानुसार तुम्ही या योजनांसाठी पात्र आहात.**"
            },
            "ta": {
                "title": "## 📋 அதிகாரப்பூர்வ தகுதி மதிப்பீட்டு அறிக்கை\n",
                "desc": "நீங்கள் சமர்ப்பித்த விவரங்களின் அடிப்படையில் அரசு வழிகாட்டுதல்களின்படி சரிபார்க்கப்பட்ட அறிக்கை:\n",
                "intro": "🙏 **உங்கள் கோரிக்கைக்குப் பொருந்தும் அதிகாரப்பூர்வ அரசு நலத்திட்டங்கள்:**\n",
                "benefit": "பலன் & நிதி உதவி:",
                "docs": "தேவையான ஆவணங்கள்:",
                "portal": "அதிகாரப்பூர்வ தளம்:",
                "q_prompt": "📋 **உங்கள் தகுதியை முழுமையாகச் சரிபார்க்க கீழே உள்ள கேள்விகளுக்குப் பதிலளிக்கவும்.**",
                "eligible": "✅ **வழங்கப்பட்ட விவரங்களின்படி நீங்கள் இத்திட்டங்களுக்குத் தகுதியானவர்.**"
            },
            "te": {
                "title": "## 📋 అధికారిక అర్హత మూల్యాంకన నివేదిక\n",
                "desc": "మీరు సమర్పించిన వివరాల ఆధారంగా ప్రభుత్వ మార్గదర్శకాల ప్రకారం ధృవీకరించబడిన నివేదిక:\n",
                "intro": "🙏 **మీ అభ్యర్థనకు సరిపోయే అధికారిక ప్రభుత్వ సంక్షేమ పథకాలు:**\n",
                "benefit": "ప్రయోజనం & ఆర్థిక సహాయం:",
                "docs": "అవసరమైన పత్రాలు:",
                "portal": "అధికారిక పోర్టల్:",
                "q_prompt": "📋 **మీ పూర్తి అర్హతను నిర్ధారించడానికి దయచేసి క్రింది ప్రశ్నలకు సమాధానం ఇవ్వండి.**",
                "eligible": "✅ **అందించిన ప్రమాణాల ప్రకారం మీరు ఈ పథకాలకు అర్హులు.**"
            },
            "gu": {
                "title": "## 📋 સત્તાવાર પાત્રતા મૂલ્યાંકન અહેવાલ\n",
                "desc": "તમે સબમિટ કરેલી વિગતોના આધારે સરકારી માર્ગદર્શિકા અનુસાર મૂલ્યાંકન:\n",
                "intro": "🙏 **તમારી વિનંતી સાથે મેળ ખાતી સત્તાવાર સરકારી કલ્યાણ યોજનાઓ:**\n",
                "benefit": "લાભ અને નાણાકીય સહાય:",
                "docs": "જરૂરી દસ્તાવેજો:",
                "portal": "સત્તાવાર પોર્ટલ:",
                "q_prompt": "📋 **તમારી સંપૂર્ણ પાત્રતા ચકાસવા માટે કૃપા કરીને નીચેના પ્રશ્નોના જવાબ આપો.**",
                "eligible": "✅ **આપેલી વિગતો અનુસાર તમે આ યોજનાઓ માટે પાત્ર છો.**"
            },
            "pa": {
                "title": "## 📋 ਅਧਿਕਾਰਤ ਯੋਗਤਾ ਮੁਲਾਂਕਣ ਰਿਪੋਰਟ\n",
                "desc": "ਤੁਹਾਡੇ ਵੇਰਵਿਆਂ ਦੇ ਆਧਾਰ 'ਤੇ ਸਰਕਾਰੀ ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼ਾਂ ਅਨੁਸਾਰ ਮੁਲਾਂਕਣ:\n",
                "intro": "🙏 **ਤੁਹਾਡੀ ਬੇਨਤੀ ਅਨੁਸਾਰ ਸਰਕਾਰੀ ਭਲਾਈ ਯੋਜਨਾਵਾਂ:**\n",
                "benefit": "ਲਾਭ ਅਤੇ ਵਿੱਤੀ ਸਹਾਇਤਾ:",
                "docs": "ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼:",
                "portal": "ਅਧਿਕਾਰਤ ਪੋਰਟਲ:",
                "q_prompt": "📋 **ਆਪਣੀ ਪੂਰੀ ਯੋਗਤਾ ਦੀ ਜਾਂਚ ਕਰਨ ਲਈ ਹੇਠਾਂ ਦਿੱਤੇ ਸਵਾਲਾਂ ਦੇ ਜਵਾਬ ਦਿਓ।**",
                "eligible": "✅ **ਦਿੱਤੇ ਗਏ ਵੇਰਵਿਆਂ ਅਨੁਸਾਰ ਤੁਸੀਂ ਇਹਨਾਂ ਯੋਜਨਾਵਾਂ ਲਈ ਯੋਗ ਹੋ।**"
            },
            "en": {
                "title": "## 📋 Official Eligibility Evaluation Report\n",
                "desc": "Based on the eligibility details you submitted, here is your verified evaluation against official government guidelines:\n",
                "intro": "🙏 **Here are the official Government welfare schemes matching your request:**\n",
                "benefit": "Entitlement & Benefit:",
                "docs": "Required Documents:",
                "portal": "Official Portal:",
                "q_prompt": "📋 **Please answer the quick questions below** to verify your complete eligibility tier.",
                "eligible": "✅ **Based on the criteria provided, you meet the captured requirements for these programs.**"
            }
        }

        labels = HEADERS_MAP.get(target_language, HEADERS_MAP["en"])
        title_eval = labels["title"]
        desc_eval = labels["desc"]
        benefit_lbl = labels["benefit"]
        docs_lbl = labels["docs"]
        portal_lbl = labels["portal"]

        # If this is an eligibility evaluation query, output full evaluation report
        if (is_evaluation_turn or evaluated_schemes) and candidate_schemes:
            lines.append(title_eval)
            lines.append(desc_eval)

            schemes_to_render = evaluated_schemes if evaluated_schemes else candidate_schemes
            spec = LANGUAGE_FORMAT_SPECS.get(target_language, LANGUAGE_FORMAT_SPECS["en"])
            for idx, s in enumerate(schemes_to_render[:4], 1):
                s_name = s.get("scheme_name") or s.get("name")
                s_level = s.get("jurisdiction") or s.get("level") or "Central"
                s_benefit = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance"
                s_url = s.get("url") or "https://www.myscheme.gov.in"
                verdict = s.get("eligibility_status", "meets_captured_rules")
                rules_matrix = s.get("eligibility_matrix", [])

                if verdict == "meets_captured_rules":
                    verdict_badge = spec["verdict_eligible"]
                elif verdict == "ineligible":
                    verdict_badge = spec["verdict_ineligible"]
                else:
                    verdict_badge = spec["verdict_conditional"]

                lines.append(f"### {idx}. **{s_name}** ({s_level})")
                lines.append(f"{verdict_badge}\n")
                lines.append(f"- **{benefit_lbl}** {s_benefit}")

                if rules_matrix:
                    lines.append(f"\n**{spec['criteria_breakdown']}**")
                    header_cols = [c.strip() for c in spec["table_header"].split("|") if c.strip()]
                    cond_col = header_cols[0] if header_cols else "Condition"
                    stat_col = header_cols[-1] if len(header_cols) > 1 else "Status"
                    lines.append(f"| {cond_col} | {stat_col} |")
                    lines.append("| :--- | :--- |")
                    for rule in rules_matrix[:6]:
                        r_label = rule.get("label") or rule.get("rule_text") or f"{rule.get('field')} {rule.get('operator')} {rule.get('value')}"
                        st = rule.get("status", "MET")
                        st_icon = spec["met"] if st == "MET" else (spec["not_met"] if st == "NOT_MET" else spec["unknown"])
                        lines.append(f"| {r_label} | {st_icon} |")

                docs = s.get("documents", [])
                if docs:
                    lines.append(f"\n- **{docs_lbl}** {', '.join(docs[:4])}")

                lines.append(f"- **{portal_lbl}** [{spec['apply_cta']}]({s_url})\n")

            return {
                "answer_markdown": "\n".join(lines),
                "key_takeaways": [
                    spec["completed_eval_takeaway"],
                    spec["review_takeaway"],
                ],
            }

        spec = LANGUAGE_FORMAT_SPECS.get(target_language, LANGUAGE_FORMAT_SPECS["en"])
        if candidate_schemes:
            lines.append(labels["intro"])

            for idx, s in enumerate(candidate_schemes[:4], 1):
                s_name = s.get("scheme_name") or s.get("name")
                s_level = s.get("jurisdiction") or s.get("level") or "Central"
                s_benefit = s.get("benefit") or (s.get("benefits") and s["benefits"][0]) or "Financial assistance"
                s_url = s.get("url") or "https://www.myscheme.gov.in"

                lines.append(f"### {idx}. **{s_name}** ({s_level})")
                lines.append(f"- **{benefit_lbl}** {s_benefit}")
                lines.append(f"- **{portal_lbl}** [{spec['apply_cta']}]({s_url})\n")

            if has_questions:
                lines.append(labels["q_prompt"])
            else:
                lines.append(labels["eligible"])
        else:
            # When candidate schemes are empty and LLM is unavailable, return official localized service notice
            unavailable_msg = generate_service_unavailable_response(target_language)
            return {
                "answer_markdown": unavailable_msg,
                "key_takeaways": [
                    spec["completed_eval_takeaway"]
                ],
            }

        return {
            "answer_markdown": "\n".join(lines),
            "key_takeaways": [
                spec["completed_eval_takeaway"],
            ],
        }

    def run(self, **kwargs) -> Dict[str, Any]:
        """Convenience alias for execute."""
        return self.execute(**kwargs)


LANGUAGE_FORMAT_SPECS = {
    "en": {
        "table_header": "| Rule / Condition | Required Criteria | Your Detail | Status |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ MET",
        "unknown": "⚠️ UNKNOWN",
        "not_met": "❌ NOT MET",
        "verdict_eligible": "✅ **ELIGIBLE: Meets Captured Criteria**",
        "verdict_conditional": "⚠️ **CONDITIONAL: Additional Details Required**",
        "verdict_ineligible": "❌ **NOT ELIGIBLE: Criteria Not Satisfied**",
        "financial_assistance": "💰 Financial Assistance:",
        "doc_checklist": "📄 Document Checklist:",
        "official_portal": "🔗 Official Portal:",
        "next_steps": "📝 Next Steps:",
        "criteria_breakdown": "Criteria Verification Breakdown:",
        "apply_cta": "Apply on verified myScheme portal",
        "completed_eval_takeaway": "Completed full eligibility evaluation across official schemes.",
        "review_takeaway": "Review the criteria checklist and document list above before submitting your application.",
    },
    "hi": {
        "table_header": "| नियम / शर्त | आवश्यक मानदंड | आपका विवरण | स्थिति |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ पूरा हुआ",
        "unknown": "⚠️ अज्ञात",
        "not_met": "❌ अपूर्ण",
        "verdict_eligible": "✅ **पात्र: दर्ज मानदंडों के अनुसार पात्र**",
        "verdict_conditional": "⚠️ **सशर्त: अतिरिक्त विवरण आवश्यक**",
        "verdict_ineligible": "❌ **अपात्र: मानदंड पूरे नहीं हुए**",
        "financial_assistance": "💰 वित्तीय सहायता:",
        "doc_checklist": "📄 आवश्यक दस्तावेज सूची:",
        "official_portal": "🔗 आधिकारिक पोर्टल:",
        "next_steps": "📝 अगला कदम:",
        "criteria_breakdown": "मापदंड सत्यापन विवरण:",
        "apply_cta": "सत्यापित myScheme पोर्टल पर आवेदन करें",
        "completed_eval_takeaway": "आधिकारिक योजनाओं के लिए पूर्ण पात्रता मूल्यांकन पूरा हुआ।",
        "review_takeaway": "आवेदन जमा करने से पहले ऊपर दी गई दस्तावेज सूची और मापदंडों की समीक्षा करें।",
    },
    "kn": {
        "table_header": "| ನಿಯಮ / ಷರತ್ತು | ಅಗತ್ಯ ಮಾನದಂಡ | ನಿಮ್ಮ ವಿವರ | ಸ್ಥಿತಿ |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ ಪೂರೈಸಿದೆ",
        "unknown": "⚠️ ತಿಳಿದಿಲ್ಲ",
        "not_met": "❌ ಅಪೂರ್ಣ",
        "verdict_eligible": "✅ **ಅರ್ಹರು: ದಾಖಲಾದ ಮಾನದಂಡಗಳ ಪ್ರಕಾರ ಅರ್ಹರು**",
        "verdict_conditional": "⚠️ **ಷರತ್ತುಬದ್ಧ: ಹೆಚ್ಚುವರಿ ವಿವರಗಳು ಅಗತ್ಯವಿದೆ**",
        "verdict_ineligible": "❌ **ಅನರ್ಹರು: ಮಾನದಂಡಗಳನ್ನು ಪೂರೈಸಲಾಗಿಲ್ಲ**",
        "financial_assistance": "💰 ಆರ್ಥಿಕ ನೆರವು:",
        "doc_checklist": "📄 ಅಗತ್ಯ ದಾಖಲೆಗಳ ಪಟ್ಟಿ:",
        "official_portal": "🔗 ಅಧಿಕೃತ ಪೋರ್ಟಲ್:",
        "next_steps": "📝 ಮುಂದಿನ ಹಂತಗಳು:",
        "criteria_breakdown": "ಮಾನದಂಡ ಪರಿಶೀಲನೆ ವಿವರ:",
        "apply_cta": "ಅಧಿಕೃತ myScheme ಪೋರ್ಟಲ್‌ನಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ",
        "completed_eval_takeaway": "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಸಂಪೂರ್ಣ ಅರ್ಹತಾ ಮೌಲ್ಯಮಾಪನ ಪೂರ್ಣಗೊಂಡಿದೆ.",
        "review_takeaway": "ಅರ್ಜಿ ಸಲ್ಲಿಸುವ ಮೊದಲು ಮೇಲಿನ ದಾಖಲೆಗಳು ಮತ್ತು ಮಾನದಂಡಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
    },
    "bn": {
        "table_header": "| নিয়ম / শর্ত | প্রয়োজনীয় মানদণ্ড | আপনার বিবরণ | স্থিতি |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ পূরণ হয়েছে",
        "unknown": "⚠️ অজানা",
        "not_met": "❌ অপূর্ণ",
        "verdict_eligible": "✅ **যোগ্য: প্রদত্ত মানদণ্ড অনুযায়ী যোগ্য**",
        "verdict_conditional": "⚠️ **শর্তসাপেক্ষ: অতিরিক্ত যাচাইকরণ প্রয়োজন**",
        "verdict_ineligible": "❌ **অযোগ্য: মানদণ্ড পূরণ হয়নি**",
        "financial_assistance": "💰 আর্থিক সহায়তা:",
        "doc_checklist": "📄 প্রয়োজনীয় নথিপত্রের তালিকা:",
        "official_portal": "🔗 অফিসিয়াল পোর্টাল:",
        "next_steps": "📝 পরবর্তী পদক্ষেপ:",
        "criteria_breakdown": "মানদণ্ড যাচাইকরণ বিবরণ:",
        "apply_cta": "যাচাইকৃত myScheme পোর্টালে আবেদন করুন",
        "completed_eval_takeaway": "সরকারি প্রকল্পগুলির সম্পূর্ণ যোগ্যতা মূল্যায়ন সম্পন্ন হয়েছে।",
        "review_takeaway": "আবেদন জমা দেওয়ার আগে প্রয়োজনীয় নথিপত্র এবং শর্তাবলী পর্যালোচনা করুন।",
    },
    "mr": {
        "table_header": "| नियम / अट | आवश्यक निकष | तुमचा तपशील | स्थिती |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ पूर्ण झाले",
        "unknown": "⚠️ अज्ञात",
        "not_met": "❌ अपूर्ण",
        "verdict_eligible": "✅ **पात्र: नोंदवलेल्या निकषांनुसार पात्र**",
        "verdict_conditional": "⚠️ **सशर्त: अतिरिक्त पडताळणी आवश्यक**",
        "verdict_ineligible": "❌ **अपात्र: निकष पूर्ण झाले नाहीत**",
        "financial_assistance": "💰 आर्थिक सहाय्य:",
        "doc_checklist": "📄 आवश्यक कागदपत्रांची यादी:",
        "official_portal": "🔗 अधिकृत पोर्टल:",
        "next_steps": "📝 पुढील पायऱ्या:",
        "criteria_breakdown": "निकष पडताळणी तपशील:",
        "apply_cta": "अधिकृत myScheme पोर्टलवर अर्ज करा",
        "completed_eval_takeaway": "अधिकृत योजनांचे संपूर्ण पात्रता मूल्यांकन पूर्ण झाले आहे.",
        "review_takeaway": "अर्ज सादर करण्यापूर्वी कागदपत्रे आणि निकष तपासा.",
    },
    "ta": {
        "table_header": "| விதி / நிபந்தனை | தேவையான அளவுகோல் | உங்கள் விவரம் | நிலை |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ பூர்த்தி செய்யப்பட்டது",
        "unknown": "⚠️ தெரியவில்லை",
        "not_met": "❌ பூர்த்தியாகவில்லை",
        "verdict_eligible": "✅ **தகுதியுடையவர்: அளவுகோல்களின்படி தகுதிபெற்றுள்ளீர்கள்**",
        "verdict_conditional": "⚠️ **நிபந்தனைக்குட்பட்டது: கூடுதல் விவரங்கள் தேவை**",
        "verdict_ineligible": "❌ **தகுதியற்றவர்: அளவுகோல்கள் பூர்த்தி செய்யப்படவில்லை**",
        "financial_assistance": "💰 நிதி உதவி:",
        "doc_checklist": "📄 தேவையான ஆவணங்கள் பட்டியல்:",
        "official_portal": "🔗 அதிகாரப்பூர்வ தளம்:",
        "next_steps": "📝 அடுத்த கட்டங்கள்:",
        "criteria_breakdown": "அளவுகோல் சரிபார்ப்பு விவரம்:",
        "apply_cta": "சரிபார்க்கப்பட்ட myScheme தளத்தில் விண்ணப்பிக்கவும்",
        "completed_eval_takeaway": "அரசு நலத்திட்டங்களுக்கான முழு தகுதி மதிப்பீடு முடிவடைந்தது.",
        "review_takeaway": "விண்ணப்பிக்கும் முன் தேவையான ஆவணங்கள் மற்றும் நிபந்தனைகளைச் சரிபார்க்கவும்.",
    },
    "te": {
        "table_header": "| నిబంధన / షరతు | అవసరమైన ప్రమాణాలు | మీ వివరాలు | స్థితి |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ పూర్తయింది",
        "unknown": "⚠️ తెలియదు",
        "not_met": "❌ పూర్తికాలేదు",
        "verdict_eligible": "✅ **అర్హులు: అందించిన ప్రమాణాల ప్రకారం అర్హత పొందారు**",
        "verdict_conditional": "⚠️ **షరతులతో కూడినది: అదనపు వివరాలు అవసరం**",
        "verdict_ineligible": "❌ **అనర్హులు: ప్రమాణాలు నెరవేరలేదు**",
        "financial_assistance": "💰 ఆర్థిక సహాయం:",
        "doc_checklist": "📄 అవసరమైన పత్రాల జాబితా:",
        "official_portal": "🔗 అధికారిక పోర్టల్:",
        "next_steps": "📝 తదుపరి దశలు:",
        "criteria_breakdown": "ప్రమాణాల ధృవీకరణ వివరాలు:",
        "apply_cta": "ధృవీకరించబడిన myScheme పోర్టల్‌లో దరఖాస్తు చేసుకోండి",
        "completed_eval_takeaway": "ప్రభుత్వ పథకాల సమగ్ర అర్హత మూల్యాంకనం పూర్తయింది.",
        "review_takeaway": "దరఖాస్తు చేయడానికి ముందు అవసరమైన పత్రాలు మరియు ప్రమాణాలను సమీక్షించండి.",
    },
    "gu": {
        "table_header": "| નિયમ / શરત | જરૂરી માપદંડ | તમારી વિગત | સ્થિતિ |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ પૂર્ણ થયેલ",
        "unknown": "⚠️ અજ્ઞાત",
        "not_met": "❌ અપૂર્ણ",
        "verdict_eligible": "✅ **પાત્ર: આપેલી વિગતો અનુસાર યોગ્ય**",
        "verdict_conditional": "⚠️ **શરતી: વધારાની વિગતો જરૂરી**",
        "verdict_ineligible": "❌ **અપાત્ર: માપદંડ પૂર્ણ નથી**",
        "financial_assistance": "💰 નાણાકીય સહાય:",
        "doc_checklist": "📄 જરૂરી દસ્તાવેજોની યાદી:",
        "official_portal": "🔗 સત્તાવાર પોર્ટલ:",
        "next_steps": "📝 આગળનાં પગલાં:",
        "criteria_breakdown": "માપદંડ ચકાસણી વિગતો:",
        "apply_cta": "સત્તાવાર myScheme પોર્ટલ પર અરજી કરો",
        "completed_eval_takeaway": "સરકારી યોજનાઓ માટે સંપૂર્ણ પાત્રતા મૂલ્યાંકન પૂર્ણ થયું છે.",
        "review_takeaway": "અરજી સબમિટ કરતા પહેલા દસ્તાવેજોની યાદੀ અને માપદંડ તપાસો.",
    },
    "pa": {
        "table_header": "| ਨਿਯਮ / ਸ਼ਰਤ | ਲੋੜੀਂਦੇ ਮਾਪਦੰਡ | ਤੁਹਾਡਾ ਵੇਰਵਾ | ਸਥਿਤੀ |",
        "table_separator": "| :--- | :--- | :--- | :--- |",
        "met": "✅ ਪੂਰਾ ਹੋਇਆ",
        "unknown": "⚠️ ਅਣਜਾਣ",
        "not_met": "❌ ਅਧੂਰਾ",
        "verdict_eligible": "✅ **ਯੋਗ: ਦਿੱਤੇ ਗਏ ਮਾਪਦੰਡਾਂ ਅਨੁਸਾਰ ਯੋਗ**",
        "verdict_conditional": "⚠️ **ਸ਼ਰਤ ਅਧੀਨ: ਵਾਧੂ ਵੇਰਵੇ ਲੋੜੀਂਦੇ ਹਨ**",
        "verdict_ineligible": "❌ **ਅਯੋਗ: ਮਾਪਦੰਡ ਪੂਰੇ ਨਹੀਂ ਹੋਏ**",
        "financial_assistance": "💰 ਵਿੱਤੀ ਸਹਾਇਤਾ:",
        "doc_checklist": "📄 ਲੋੜੀਂਦੇ ਦਸਤਾਵੇਜ਼ਾਂ ਦੀ ਸੂਚੀ:",
        "official_portal": "🔗 ਅਧਿਕਾਰਤ ਪੋਰਟਲ:",
        "next_steps": "📝 ਅਗਲੇ ਕਦਮ:",
        "criteria_breakdown": "ਮਾਪਦੰਡ ਪੁਸ਼ਟੀਕਰਨ ਵੇਰਵਾ:",
        "apply_cta": "ਪ੍ਰਮਾਣਿਤ myScheme ਪੋਰਟਲ 'ਤੇ ਅਰਜ਼ੀ ਦਿਓ",
        "completed_eval_takeaway": "ਸਰਕਾਰੀ ਸਕੀਮਾਂ ਲਈ ਪੂਰਾ ਯੋਗਤਾ ਮੁਲਾਂਕਣ ਮੁਕੰਮਲ ਹੋ ਗਿਆ ਹੈ।",
        "review_takeaway": "ਅਰਜ਼ੀ ਜਮ੍ਹਾ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਦਸਤਾਵੇਜ਼ ਸੂਚੀ ਅਤੇ ਮਾਪਦੰਡਾਂ ਦੀ ਜਾਂਚ ਕਰੋ।",
    }
}


# Global singleton instance
response_generator_tool = ResponseGeneratorTool()
