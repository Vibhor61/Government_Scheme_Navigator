"""Authentic myScheme portal scheme repository for national and state welfare programs."""

from typing import Any, Dict, List

MYSCHEME_FLAGSHIP_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "pm-kisan",
        "slug": "pmkisan",
        "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "category": "Agriculture & Rural",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmkisan",
        "brief": "Direct income support of ₹6,000 per year transferred in three equal installments of ₹2,000 directly into the bank accounts of farmer families.",
        "benefits": [
            "Financial benefit of ₹6,000 per year directly credited to Aadhaar-linked bank accounts",
            "Paid in three 4-monthly installments of ₹2,000 each via DBT",
            "Covers all landholding farmer families across rural and urban India"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Farmer", "label": "Must be an active cultivator or farmer family"},
            {"field": "farmer_status", "operator": "eq", "value": "Farmer family", "label": "Farmer family owning cultivable land"},
        ],
        "documents": [
            "Aadhaar Card",
            "Land ownership records / Khatauni / Khasra",
            "Aadhaar-seeded Bank Account Passbook",
            "Mobile number linked to Aadhaar"
        ]
    },
    {
        "id": "smam",
        "slug": "smam",
        "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "category": "Agriculture & Rural",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/smam",
        "brief": "Direct subsidy of 40% to 50% for farmers on purchase of agricultural equipment, tractors, power tillers, rotavators, and establishment of Custom Hiring Centers (CHC).",
        "benefits": [
            "40% to 50% direct subsidy on tractors, power tillers, rotavators, and harvesting machinery",
            "Financial assistance up to ₹10 Lakh (40% project subsidy) for establishing village Custom Hiring Centers",
            "Additional 10% special subsidy incentive for small, marginal, SC/ST, and women farmers"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Farmer", "label": "Individual farmer, rural youth, or agricultural entrepreneur"},
            {"field": "landholding_category", "operator": "in", "value": ["Small Farmer (1-2 Hectares)", "Marginal Farmer (< 1 Hectare)", "Large / Medium Farmer (> 2 Hectares)"], "label": "Must possess cultivable land record (Khasra/Khatauni)"}
        ],
        "documents": [
            "Aadhaar Card",
            "Land Records / Record of Rights (RoR / 7/12 extract)",
            "Bank Account Passbook (Aadhaar linked)",
            "Authorized tractor / equipment dealer quotation"
        ]
    },
    {
        "id": "pm-kusum",
        "slug": "pm-kusum",
        "name": "PM-KUSUM (Subsidized Solar Agriculture Pumps Scheme)",
        "ministry": "Ministry of New and Renewable Energy",
        "category": "Agriculture & Rural",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pm-kusum",
        "brief": "Up to 60% direct subsidy for standalone solar agricultural irrigation pumps and solarization of existing grid-connected agriculture pumps.",
        "benefits": [
            "60% financial subsidy (30% Central Government + 30% State Government) on solar water pumps",
            "Farmer contributes only 10% of benchmark cost; 30% available as bank loan",
            "Daytime dependable irrigation with zero electricity or diesel fuel bill"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Farmer", "label": "Farmer, Water User Association, or Farmer Producer Organization (FPO)"},
            {"field": "cultivable_land", "operator": "eq", "value": "Yes", "label": "Must own cultivable agricultural land"}
        ],
        "documents": [
            "Aadhaar Card",
            "Land revenue record / Jamabandi",
            "Bank passbook",
            "Passport size photograph"
        ]
    },
    {
        "id": "pm-vidyalaxmi",
        "slug": "pm-vidyalaxmi",
        "name": "PM Vidyalaxmi Scheme",
        "ministry": "Ministry of Education",
        "category": "Education & Learning",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pm-vidyalaxmi",
        "brief": "Collateral-free, guarantor-free education loan up to ₹7.5 Lakh with 3% interest subvention for students securing admission to top 860 Higher Educational Institutions.",
        "benefits": [
            "Collateral-free and guarantor-free education loan up to ₹7.5 Lakh",
            "3% interest subvention on education loans for students with annual family income up to ₹8 Lakh",
            "75% credit guarantee by Government of India for defaults up to ₹7.5 Lakh",
            "Unified digital portal for transparent student loan processing"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Student", "label": "Currently enrolled student"},
            {"field": "course_type", "operator": "in", "value": ["Engineering / B.Tech", "Medical", "Higher Education / University", "Vocational / Technical"], "label": "Enrolled in quality higher education or technical program"},
            {"field": "annual_family_income", "operator": "lte", "value": 800000, "label": "Annual family income up to ₹8 Lakh for interest subvention"}
        ],
        "documents": [
            "Aadhaar Card of student and parents",
            "Admission confirmation letter / Offer letter from eligible HEI",
            "Family Income Certificate issued by competent revenue authority",
            "Class 10, 12, and graduation marksheets"
        ]
    },
    {
        "id": "post-matric-obc-sc",
        "slug": "post-matric-scholarship",
        "name": "Post-Matric Scholarship Scheme for SC / ST / OBC Students",
        "ministry": "Ministry of Social Justice and Empowerment",
        "category": "Education & Learning",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pms-sc",
        "brief": "Comprehensive financial assistance covering full tuition fees and monthly living maintenance allowances for post-matriculation and post-secondary studies.",
        "benefits": [
            "100% tuition fee reimbursement and compulsory non-refundable fees",
            "Monthly maintenance allowance up to ₹13,500 per year for hostellers and ₹7,000 for day scholars",
            "Book allowance, study tour charges, and thesis typing charges for professional courses"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Student", "label": "Student studying post-matric / college degree"},
            {"field": "social_category", "operator": "in", "value": ["OBC", "SC", "ST"], "label": "Belongs to SC, ST, or OBC category"},
            {"field": "annual_family_income", "operator": "lte", "value": 250000, "label": "Annual family income does not exceed ₹2.5 Lakh"}
        ],
        "documents": [
            "Aadhaar Card",
            "Caste Certificate (SC/ST/OBC) verified online",
            "Annual Family Income Certificate",
            "College Fee Receipt & Bonafide Certificate",
            "Bank Passbook seeded with NPCI / Aadhaar"
        ]
    },
    {
        "id": "pm-mudra",
        "slug": "pmmy",
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "ministry": "Ministry of Finance",
        "category": "Business & Entrepreneurship",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmmy",
        "brief": "Collateral-free institutional loans up to ₹20 Lakh to micro and small non-corporate enterprises across Shishu, Kishore, and Tarun loan tiers.",
        "benefits": [
            "Collateral-free business loans: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 Lakh), Tarun (₹5 Lakh to ₹10 Lakh), Tarun Plus (up to ₹20 Lakh)",
            "No processing charges for loans up to ₹50,000",
            "Mudra Card with RuPay debit facility for working capital drawdowns"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "in", "value": ["Self-Employed / Business", "Unemployed / Jobseeker", "Daily Wage / Artisan"], "label": "Micro-entrepreneur, artisan, or aspiring business owner"},
            {"field": "age", "operator": "gte", "value": 18, "label": "Minimum age of 18 years"}
        ],
        "documents": [
            "Proof of Identity (Aadhaar / Voter ID / PAN)",
            "Proof of Residence",
            "Business registration / Udyam Certificate (if existing)",
            "Project report / Business proposal",
            "Bank statement for last 6 months"
        ]
    },
    {
        "id": "pm-svanidhi",
        "slug": "pmsvanidhi",
        "name": "PM Street Vendor's AtmaNirbhar Nidhi (PM SVANidhi)",
        "ministry": "Ministry of Housing and Urban Affairs",
        "category": "Business & Entrepreneurship",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmsvanidhi",
        "brief": "Collateral-free micro-credit facility starting with ₹10,000 working capital loan with 7% interest subsidy and cashback rewards for digital transactions.",
        "benefits": [
            "First tranche collateral-free loan of ₹10,000; scalable to ₹20,000 and ₹50,000 upon timely repayment",
            "7% per annum interest subsidy directly credited via DBT",
            "Cashback up to ₹1,200 per year on digital sales transactions"
        ],
        "eligibility_rules": [
            {"field": "rural_urban", "operator": "eq", "value": "Urban", "label": "Vending in urban, peri-urban, or semi-urban areas"},
            {"field": "occupation", "operator": "in", "value": ["Self-Employed / Business", "Daily Wage / Artisan", "Unemployed / Jobseeker"], "label": "Street vendor or small independent trader"}
        ],
        "documents": [
            "Aadhaar Card",
            "Vending Certificate / Identity Card issued by Urban Local Body (ULB)",
            "Bank Account details",
            "Active mobile number"
        ]
    },
    {
        "id": "pm-jay",
        "slug": "ayushman-bharat-pmjay",
        "name": "Ayushman Bharat - Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
        "ministry": "Ministry of Health and Family Welfare / NHA",
        "category": "Healthcare & Wellness",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/ab-pmjay",
        "brief": "World's largest government-funded health assurance scheme providing cashless hospitalisation cover of ₹5 Lakh per family per year for secondary and tertiary healthcare.",
        "benefits": [
            "Cashless & paperless access to healthcare up to ₹5 Lakh per eligible family per year",
            "Covers 1,949 medical procedures including pre- and post-hospitalisation expenses for 3 and 15 days",
            "Portability across India: Treatment available at any empanelled public or private hospital nationwide"
        ],
        "eligibility_rules": [
            {"field": "bpl_status", "operator": "eq", "value": "Yes", "label": "Identified as economically vulnerable / BPL / SECC database"},
            {"field": "annual_family_income", "operator": "lte", "value": 250000, "label": "Low-income household or Antyodaya Anna Yojana (AAY) beneficiary"}
        ],
        "documents": [
            "Aadhaar Card / Ration Card",
            "Ayushman Card (generated with OTP authentication)",
            "Government photo identity proof"
        ]
    },
    {
        "id": "ayushman-vay-vandana",
        "slug": "ayushman-vay-vandana",
        "name": "Ayushman Bharat PM-JAY Senior Citizens (70+ Years Health Cover)",
        "ministry": "Ministry of Health and Family Welfare / NHA",
        "category": "Healthcare & Wellness",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/ab-pmjay",
        "brief": "Universal health insurance cover of ₹5 Lakh per year for all senior citizens aged 70 years and above, irrespective of family income or economic status.",
        "benefits": [
            "Dedicated ₹5 Lakh annual health insurance cover exclusively for senior citizens aged 70+",
            "Universal coverage: No income ceiling or BPL criteria required for 70+ seniors",
            "Cashless hospitalization, surgical care, and geriatric illness treatment across 29,000 empanelled hospitals"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "gte", "value": 70, "label": "Senior citizen must be aged 70 years or above"}
        ],
        "documents": [
            "Aadhaar Card (for age and identity verification)",
            "Ayushman Vay Vandana Card (generated via PMJAY portal)"
        ]
    },
    {
        "id": "pmegp",
        "slug": "pmegp",
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "category": "Business & Entrepreneurship",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmegp",
        "brief": "Credit-linked capital subsidy up to 35% for establishing new manufacturing business projects up to ₹50 Lakh and service units up to ₹20 Lakh.",
        "benefits": [
            "15% to 35% government capital subsidy on bank loan for setting up manufacturing businesses up to ₹50 Lakh",
            "Beneficiary contributes only 5% to 10% own equity; remaining funded by institutional bank loan",
            "Special 35% subsidy rate for rural areas, SC/ST, women, and minority entrepreneurs"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "gte", "value": 18, "label": "Any individual aged 18 years or above"},
            {"field": "education_qualification", "operator": "in", "value": ["8th Pass or Above", "10th / 12th / Graduate", "Below 8th (for projects < ₹10 Lakh)"], "label": "Minimum 8th pass for manufacturing projects above ₹10 Lakh"}
        ],
        "documents": [
            "Aadhaar Card",
            "Detailed Project Report (DPR) for manufacturing unit",
            "Educational certificate (8th/10th mark sheet)",
            "Caste/Special Category certificate"
        ]
    },
    {
        "id": "cbse-single-girl-child",
        "slug": "cbse-single-girl-child",
        "name": "CBSE Single Girl Child Merit Scholarship Scheme",
        "ministry": "Ministry of Education",
        "category": "Education & Learning",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/cbse-sgc",
        "brief": "Merit scholarship of ₹500 per month for two years for girl students who are the only single child in the family and passed Class 10 with 60% or more marks.",
        "benefits": [
            "Monthly scholarship of ₹500 directly credited for Class 11 and 12 studies",
            "Encourages and rewards higher secondary education for single girl children"
        ],
        "eligibility_rules": [
            {"field": "single_girl_child", "operator": "eq", "value": "Yes", "label": "Must be an only child of their parents (single girl child without siblings)"},
            {"field": "class_10_marks_pct", "operator": "gte", "value": 60, "label": "Scored 60% or more marks in CBSE Class 10 board exam"}
        ],
        "documents": [
            "Aadhaar Card",
            "Class 10 CBSE Marksheet",
            "Affidavit on stamp paper declaring single girl child status",
            "Class 11 school bonafide certificate"
        ]
    },
    {
        "id": "jssk",
        "slug": "jssk",
        "name": "Janani Shishu Suraksha Karyakram (JSSK Female Healthcare)",
        "ministry": "Ministry of Health and Family Welfare",
        "category": "Healthcare & Wellness",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/jssk",
        "brief": "100% free and cashless healthcare entitlement for women and female reproductive disease treatment, institutional deliveries, C-sections, and treatment of complications.",
        "benefits": [
            "Completely free and cashless treatment for women during pregnancy, childbirth, and postnatal complications",
            "Free drugs, consumables, diagnostic tests (blood, urine, ultrasound), blood transfusions, and free diet",
            "Free transport from home to health facility and drop-back home"
        ],
        "eligibility_rules": [
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Female patients seeking maternal, reproductive, or female disease healthcare in public facilities"}
        ],
        "documents": [
            "Aadhaar Card",
            "Mother & Child Protection (MCP) card"
        ]
    },
    {
        "id": "pm-surya-ghar",
        "slug": "pmsuryaghar",
        "name": "PM Surya Ghar: Muft Bijli Yojana",
        "ministry": "Ministry of New and Renewable Energy",
        "category": "Housing & Energy",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmsuryaghar",
        "brief": "Rooftop solar subsidy providing up to ₹78,000 direct central financial assistance and 300 units of free electricity every month for 1 Crore Indian households.",
        "benefits": [
            "Direct subsidy of ₹30,000 for 1 kW, ₹60,000 for 2 kW, and ₹78,000 for 3 kW or above rooftop solar",
            "Up to 300 units of free electricity per month, drastically slashing electricity bills",
            "Low-interest collateral-free bank loans at ~7% for installing rooftop panels"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "gte", "value": 18, "label": "Adult citizen owning residential rooftop premises"},
        ],
        "documents": [
            "Electricity Consumer Account Bill (latest 6 months)",
            "Aadhaar Card",
            "Bank Account Passbook (cancelled cheque)",
            "Roof ownership proof"
        ]
    },
    {
        "id": "pm-vishwakarma",
        "slug": "pmvishwakarma",
        "name": "PM Vishwakarma Scheme",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "category": "Business & Entrepreneurship",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmvishwakarma",
        "brief": "Holistic support for 18 traditional trades and craftspeople: recognized PM Vishwakarma certificate, ₹15,000 toolkit incentive, skill training, and collateral-free credit at 5%.",
        "benefits": [
            "Recognition as Vishwakarma through PM Vishwakarma Certificate & ID card",
            "Skill upgradation: 5–7 days basic training with ₹500/day stipend",
            "Toolkit incentive of ₹15,000 modern toolkit grant",
            "Collateral-free enterprise credit: ₹1 Lakh (1st tranche) & ₹2 Lakh (2nd tranche) at concessional 5% interest"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "gte", "value": 18, "label": "Minimum age 18 years on registration date"},
            {"field": "occupation", "operator": "in", "value": ["Daily Wage / Artisan", "Self-Employed / Business"], "label": "Engaged in one of 18 traditional crafts (carpenter, blacksmith, potter, tailor, etc.)"}
        ],
        "documents": [
            "Aadhaar Card",
            "Mobile number linked to Aadhaar",
            "Bank details",
            "Ration Card for family verification"
        ]
    },
    {
        "id": "lakhpati-didi",
        "slug": "lakhpati-didi",
        "name": "Lakhpati Didi Initiative",
        "ministry": "Ministry of Rural Development",
        "category": "Women & Child",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/lakhpati-didi",
        "brief": "Flagship livelihood mission empowering women members of Deendayal Antyodaya Yojana - NRLM Self Help Groups to earn a sustainable income of at least ₹1 Lakh per year.",
        "benefits": [
            "Technical skill training in entrepreneurship, agriculture, LED manufacturing, and drone operations",
            "Access to community investment fund, revolving fund, and micro-credit linkages",
            "Market linkage through Saras Melas, Government e-Marketplace (GeM), and e-commerce portals"
        ],
        "eligibility_rules": [
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Women citizens only"},
            {"field": "rural_urban", "operator": "eq", "value": "Rural", "label": "Resident of rural area"},
            {"field": "occupation", "operator": "in", "value": ["Self-Employed / Business", "Unemployed / Jobseeker", "Farmer", "Daily Wage / Artisan"], "label": "Member of an active Women Self-Help Group (SHG)"}
        ],
        "documents": [
            "Aadhaar Card",
            "SHG Membership proof / Passbook",
            "Bank Account Passbook",
            "Passport size photographs"
        ]
    },
    {
        "id": "pm-awas-yojana",
        "slug": "pmay-urban-gramin",
        "name": "Pradhan Mantri Awas Yojana (PMAY - Urban & Gramin)",
        "ministry": "Ministry of Housing and Urban Affairs & MoRD",
        "category": "Housing & Energy",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmay-u",
        "brief": "Housing for All initiative providing financial assistance and interest subsidies to construct durable pucca houses equipped with electricity, LPG, and tap water.",
        "benefits": [
            "Direct financial assistance of ₹1.20 Lakh to ₹1.30 Lakh in rural areas for pucca house construction",
            "Credit Linked Subsidy Scheme (CLSS) interest subsidy up to 6.5% for EWS/LIG home loans in urban areas",
            "Mandatory house ownership or co-ownership in the name of the female head of household"
        ],
        "eligibility_rules": [
            {"field": "annual_family_income", "operator": "lte", "value": 300000, "label": "Annual family income does not exceed ₹3 Lakh for EWS category"},
            {"field": "property_ownership", "operator": "eq", "value": "No pucca house", "label": "Beneficiary family must not own a pucca house anywhere in India"}
        ],
        "documents": [
            "Aadhaar Card of all family members",
            "Affidavit proving non-ownership of pucca house",
            "Bank Account details",
            "Income and Caste Certificate"
        ]
    },
    {
        "id": "sukanya-samriddhi",
        "slug": "sukanya-samriddhi-yojana",
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "ministry": "Ministry of Finance",
        "category": "Women & Child",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/ssy",
        "brief": "Small deposit savings scheme for girl children with an attractive interest rate of 8.2% and triple tax exemption (EEE) under Section 80C.",
        "benefits": [
            "High sovereign-backed interest rate (currently 8.2% p.a.) compounded annually",
            "Triple tax exemption: Investment, interest earned, and maturity proceeds are 100% tax-free",
            "Partial withdrawal allowed up to 50% for higher education upon reaching age 18"
        ],
        "eligibility_rules": [
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Girl child beneficiary"},
            {"field": "age", "operator": "lte", "value": 10, "label": "Account opened before child attains age of 10 years"}
        ],
        "documents": [
            "Birth Certificate of girl child",
            "Identity and Address proof of guardian (Aadhaar / PAN)",
            "Passport size photos of child and parent"
        ]
    },
    {
        "id": "pm-fasal-bima",
        "slug": "pmfby",
        "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "category": "Agriculture & Rural",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pmfby",
        "brief": "Affordable comprehensive crop insurance against non-preventable natural risks, pest attacks, post-harvest losses, and localized weather calamities.",
        "benefits": [
            "Minimal premium paid by farmer: 2% for Kharif, 1.5% for Rabi, and 5% for commercial/horticultural crops",
            "Balance premium heavily subsidized equally by Central and State Governments",
            "Direct claim settlement to farmer bank accounts using satellite and drone remote sensing"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Farmer", "label": "Farmer cultivating notified crops in notified areas"},
        ],
        "documents": [
            "Land Record (Khasra / Khatauni) / Tenant agreement",
            "Aadhaar Card",
            "Sowing Certificate issued by Patwari / Village Agriculture Officer",
            "Bank Passbook"
        ]
    },
    {
        "id": "pm-shri",
        "slug": "pm-shri-schools",
        "name": "PM SHRI (PM Schools for Rising India)",
        "ministry": "Ministry of Education",
        "category": "Education & Learning",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/pm-shri",
        "brief": "Transforming 14,500 schools into model exemplars showcasing the National Education Policy (NEP 2020) with smart classrooms, experiential learning, and STEM labs.",
        "benefits": [
            "State-of-the-art smart classrooms, vocational labs, and digital libraries",
            "Experiential, inquiry-driven pedagogy fostering 21st-century skills and creativity",
            "Green school infrastructure with solar panels, rainwater harvesting, and waste management"
        ],
        "eligibility_rules": [
            {"field": "occupation", "operator": "eq", "value": "Student", "label": "School students enrolled in public elementary or secondary schools"},
        ],
        "documents": [
            "School admission record",
            "Aadhaar Card",
            "Birth Certificate"
        ]
    },
    {
        "id": "atal-pension",
        "slug": "apy",
        "name": "Atal Pension Yojana (APY)",
        "ministry": "Ministry of Finance / PFRDA",
        "category": "Social Welfare",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/apy",
        "brief": "Government-backed guaranteed minimum monthly pension of ₹1,000 to ₹5,000 for unorganized sector workers starting from the age of 60.",
        "benefits": [
            "Guaranteed minimum pension of ₹1,000, ₹2,000, ₹3,000, ₹4,000, or ₹5,000 per month from age 60",
            "Spouse receives the exact same pension upon subscriber's demise",
            "Nominee receives complete pension corpus accumulated up to age 60"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "between", "value": {"min": 18, "max": 40}, "label": "Age between 18 and 40 years at time of joining"},
            {"field": "occupation", "operator": "in", "value": ["Unemployed / Jobseeker", "Daily Wage / Artisan", "Self-Employed / Business", "Farmer"], "label": "Worker in unorganized sector (non-income tax payer)"}
        ],
        "documents": [
            "Aadhaar Card",
            "Savings Bank Account / Post Office Account",
            "Active mobile number"
        ]
    },
    {
        "id": "stand-up-india",
        "slug": "standupindia",
        "name": "Stand-Up India Scheme",
        "ministry": "Ministry of Finance",
        "category": "Business & Entrepreneurship",
        "level": "Central",
        "state": "All India",
        "url": "https://www.myscheme.gov.in/schemes/standupindia",
        "brief": "Bank loans between ₹10 Lakh and ₹1 Crore to at least one Scheduled Caste (SC) or Scheduled Tribe (ST) borrower and at least one woman borrower per bank branch.",
        "benefits": [
            "Composite loan (term loan + working capital) between ₹10 Lakh and ₹100 Lakh for greenfield projects",
            "Concessional interest rate not exceeding base rate + 3% + tenor premium",
            "Credit Guarantee Scheme for Stand-Up India (CGSUI) coverage"
        ],
        "eligibility_rules": [
            {"field": "age", "operator": "gte", "value": 18, "label": "Minimum age of 18 years"},
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Woman entrepreneur OR SC/ST citizen"},
            {"field": "occupation", "operator": "in", "value": ["Self-Employed / Business", "Unemployed / Jobseeker"], "label": "Setting up greenfield manufacturing, service, agri-allied, or trading enterprise"}
        ],
        "documents": [
            "Aadhaar / Voter ID / PAN Card",
            "Caste Certificate (for SC/ST) if applicable",
            "Detailed Project Report with machinery and cost estimates",
            "Proof of business address and lease/ownership deed"
        ]
    },
    {
        "id": "up-kanya-sumangala",
        "slug": "mksy",
        "name": "Mukhyamantri Kanya Sumangala Yojana",
        "ministry": "Government of Uttar Pradesh",
        "category": "Women & Child",
        "level": "State",
        "state": "Uttar Pradesh",
        "url": "https://www.myscheme.gov.in/schemes/mksy",
        "brief": "Conditional cash transfer of ₹25,000 paid in 6 phases from birth to graduation to ensure girl child education and eliminate female foeticide in Uttar Pradesh.",
        "benefits": [
            "Direct cash assistance of ₹25,000 distributed across 6 educational and developmental stages",
            "₹5,000 at birth, ₹2,000 on vaccination, ₹3,000 on Class 1 admission, ₹3,000 on Class 6, ₹5,000 on Class 9, and ₹7,000 on Degree/Diploma admission"
        ],
        "eligibility_rules": [
            {"field": "state", "operator": "eq", "value": "Uttar Pradesh", "label": "Resident and domicile of Uttar Pradesh"},
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Beneficiary must be a girl child"},
            {"field": "annual_family_income", "operator": "lte", "value": 300000, "label": "Annual family income does not exceed ₹3 Lakh"}
        ],
        "documents": [
            "UP Domicile Certificate",
            "Birth Certificate of girl child",
            "Family Income Certificate (< ₹3 Lakh)",
            "Aadhaar Card of Parents",
            "School / College admission certificate"
        ]
    },
    {
        "id": "delhi-ladli",
        "slug": "delhi-ladli-scheme",
        "name": "Delhi Ladli Scheme",
        "ministry": "Government of NCT of Delhi",
        "category": "Women & Child",
        "level": "State",
        "state": "Delhi (NCT)",
        "url": "https://www.myscheme.gov.in/schemes/delhi-ladli",
        "brief": "Financial assistance of up to ₹35,000 deposited in the name of the girl child to empower girls in Delhi and support school retention up to Class 12.",
        "benefits": [
            "₹11,000 if born in hospital / ₹10,000 if born at home",
            "₹5,000 each on admission to Class 1, Class 6, Class 9, Class 10, and Class 12",
            "Maturity amount disbursed to girl upon turning 18 and clearing Class 10"
        ],
        "eligibility_rules": [
            {"field": "state", "operator": "eq", "value": "Delhi (NCT)", "label": "Resident of Delhi for at least 3 continuous years"},
            {"field": "gender", "operator": "eq", "value": "Female", "label": "Girl child born in Delhi"},
            {"field": "annual_family_income", "operator": "lte", "value": 100000, "label": "Family income not exceeding ₹1 Lakh per year"}
        ],
        "documents": [
            "3 years continuous Delhi residence proof (Ration card / Electricity bill)",
            "Birth Certificate of girl child issued by MCD / NDMC",
            "Income certificate issued by SDM",
            "School admission bonafide certificate"
        ]
    }
]


def match_schemes_for_profile(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evaluates flagship schemes against a citizen profile and returns
    scored, categorized, and status-annotated scheme records.
    """
    results: List[Dict[str, Any]] = []

    profile_gender = profile.get("gender")
    profile_age = profile.get("age")
    profile_state = profile.get("state")
    profile_income = profile.get("annual_family_income")
    profile_cat = profile.get("social_category")
    profile_occ = profile.get("occupation")
    profile_area = profile.get("rural_urban")
    profile_bpl = profile.get("bpl_status")

    for scheme in MYSCHEME_FLAGSHIP_CATALOG:
        matched_rules = 0
        total_rules = len(scheme.get("eligibility_rules", []))
        rule_evaluations = []
        is_hard_disqualified = False

        # State check: If scheme is state-specific, verify state match
        scheme_state = scheme.get("state", "All India")
        if scheme.get("level") == "State" and scheme_state != "All India":
            if profile_state and profile_state != "All India / Centre" and profile_state.lower() not in scheme_state.lower():
                continue

        for rule in scheme.get("eligibility_rules", []):
            field = rule["field"]
            op = rule["operator"]
            val = rule["value"]
            label = rule.get("label", field)

            passed = False
            status = "UNKNOWN"

            if field == "gender":
                if not profile_gender or profile_gender == "Prefer not to say":
                    status = "UNKNOWN"
                elif op == "eq":
                    passed = (profile_gender.lower() == val.lower() or val.lower() in ("man", "woman") and profile_gender.lower() in ("male", "female"))
                    status = "PASS" if passed else "FAIL"
                if status == "FAIL":
                    is_hard_disqualified = True

            elif field == "age":
                if profile_age is None:
                    status = "UNKNOWN"
                else:
                    try:
                        age_num = float(profile_age)
                        if op == "gte":
                            passed = age_num >= float(val)
                        elif op == "lte":
                            passed = age_num <= float(val)
                        elif op == "between":
                            passed = float(val["min"]) <= age_num <= float(val["max"])
                        status = "PASS" if passed else "FAIL"
                    except (ValueError, TypeError):
                        status = "UNKNOWN"
                if status == "FAIL":
                    is_hard_disqualified = True

            elif field == "social_category":
                if not profile_cat or profile_cat == "All":
                    status = "UNKNOWN"
                elif op == "in" and isinstance(val, list):
                    passed = any(profile_cat.lower() == item.lower() for item in val)
                    status = "PASS" if passed else "FAIL"
                elif op == "eq":
                    passed = profile_cat.lower() == str(val).lower()
                    status = "PASS" if passed else "FAIL"
                if status == "FAIL":
                    is_hard_disqualified = True

            elif field == "occupation":
                if not profile_occ or profile_occ == "All":
                    status = "UNKNOWN"
                elif op == "eq":
                    passed = profile_occ.lower() == str(val).lower()
                    status = "PASS" if passed else "FAIL"
                elif op == "in" and isinstance(val, list):
                    passed = any(profile_occ.lower() == item.lower() for item in val)
                    status = "PASS" if passed else "FAIL"
                if status == "FAIL":
                    is_hard_disqualified = True

            elif field == "annual_family_income":
                if profile_income is None:
                    status = "UNKNOWN"
                else:
                    try:
                        # Extract income numeric
                        inc_num = None
                        if isinstance(profile_income, (int, float)):
                            inc_num = float(profile_income)
                        elif isinstance(profile_income, str):
                            if "< 1" in profile_income or "1 lakh" in profile_income.lower():
                                inc_num = 100000
                            elif "2.5" in profile_income:
                                inc_num = 250000
                            elif "5" in profile_income:
                                inc_num = 500000
                            elif "8" in profile_income:
                                inc_num = 800000
                            else:
                                digits = "".join(c for c in profile_income if c.isdigit())
                                if digits:
                                    inc_num = float(digits)

                        if inc_num is not None and op == "lte":
                            passed = inc_num <= float(val)
                            status = "PASS" if passed else "FAIL"
                        else:
                            status = "UNKNOWN"
                    except (ValueError, TypeError):
                        status = "UNKNOWN"

            elif field == "rural_urban":
                if not profile_area:
                    status = "UNKNOWN"
                elif op == "eq":
                    passed = profile_area.lower() == str(val).lower()
                    status = "PASS" if passed else "FAIL"

            elif field == "bpl_status":
                if not profile_bpl:
                    status = "UNKNOWN"
                elif op == "eq":
                    passed = profile_bpl.lower() == str(val).lower()
                    status = "PASS" if passed else "FAIL"

            else:
                status = "PASS"
                passed = True

            if passed:
                matched_rules += 1

            rule_evaluations.append({
                "rule_label": label,
                "status": status,
                "field": field
            })

        if is_hard_disqualified:
            continue

        match_pct = int((matched_rules / max(total_rules, 1)) * 100)
        overall_status = "eligible" if match_pct == 100 else "partial" if match_pct >= 50 else "unknown"

        results.append({
            **scheme,
            "match_percentage": match_pct,
            "overall_status": overall_status,
            "rules_checked": rule_evaluations,
            "matched_rules_count": matched_rules,
            "total_rules_count": total_rules
        })

    # Sort: Higher match percentage first, then central/state
    results.sort(key=lambda s: (s["match_percentage"], s.get("level") == "Central"), reverse=True)
    return results
