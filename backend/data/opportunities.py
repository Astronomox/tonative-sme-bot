"""
Curated Nigerian SME funding opportunities.
Sources: TEF, BOI, SMEDAN, NIRSAL, YouWiN, VC4A, Fidelity Bank, Cartier, CBN.
Each opportunity includes a document checklist for fund-readiness guidance.
"""

FUNDING_OPPORTUNITIES = [
    {
        "id": "tef-2026",
        "name": "Tony Elumelu Foundation Entrepreneurship Programme",
        "description": (
            "The TEF Programme provides $5,000 seed capital, mentorship, "
            "and business training to African entrepreneurs. No repayment required. "
            "Open to early-stage entrepreneurs across all 54 African countries."
        ),
        "amount": "$5,000 non-refundable seed capital (approx. 4M naira)",
        "deadline": "Applications open January each year, close March 31",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k"],
        "requires_cac": False,
        "application_link": "https://tefconnect.com",
        "required_documents": [
            "Valid government-issued ID (NIN slip, voter's card, or passport)",
            "Passport photograph",
            "Business plan (TEF provides a downloadable template)",
            "Proof of business activity (photos, receipts, social media page)",
            "Bank account number (for fund disbursement)",
        ],
        "application_steps": [
            "Visit tefconnect.com and create a free account",
            "Download the TEF business plan template and complete it",
            "Fill out the online application form (business overview, impact, goals)",
            "Record and upload a 2-minute video pitch about your business",
            "Submit before March 31",
            "Selected applicants attend a 12-week training programme",
        ],
    },
    {
        "id": "boi-msme-2026",
        "name": "Bank of Industry MSME Loan Facility",
        "description": (
            "BOI provides single-digit interest rate loans to micro, small, and medium "
            "enterprises across Nigeria. Loans range from N500,000 to N500 million depending "
            "on the facility type. Agribusiness, manufacturing, and technology businesses "
            "are prioritised."
        ),
        "amount": "N500,000 to N500 million at 9% interest per annum",
        "deadline": "Rolling applications   always open",
        "eligibility_sectors": ["agriculture", "manufacturing", "technology", "food", "textile", "all"],
        "eligibility_stages": ["early", "growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["100k_500k", "500k_2m", "2m_10m", "above_10m"],
        "requires_cac": True,
        "application_link": "https://www.boi.ng/apply",
        "required_documents": [
            "CAC certificate of incorporation",
            "Memorandum and Articles of Association (for Ltd companies)",
            "Business plan with financial projections (3 years)",
            "6-month bank statement",
            "BVN of all directors",
            "Valid ID of all directors",
            "Passport photographs of all directors",
            "Evidence of collateral (property documents, asset list)",
            "Tax Identification Number (TIN) certificate",
            "Utility bill (proof of business address)",
            "Audited accounts if business is over 2 years old",
        ],
        "application_steps": [
            "Visit boi.ng and select the appropriate loan facility for your business size",
            "Download and complete the BOI application form",
            "Prepare your business plan and all required documents",
            "Submit application to the nearest BOI state office or online",
            "BOI credit team reviews and may request additional documents",
            "Site visit and verification by BOI officers",
            "Loan approval and disbursement to your business account",
        ],
    },
    {
        "id": "smedan-grant-2026",
        "name": "SMEDAN Enterprise Development Programme",
        "description": (
            "The Small and Medium Enterprises Development Agency of Nigeria (SMEDAN) "
            "provides grants, equipment support, and business development services to "
            "Nigerian MSMEs. Includes the National MSME Collaborative Survey support, "
            "cluster development, and market access programmes."
        ),
        "amount": "Grants up to N2 million; Equipment support valued at N500k-N5M",
        "deadline": "Rolling   check smedan.gov.ng for current windows",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://smedan.gov.ng/our-programs/",
        "required_documents": [
            "Valid government-issued ID",
            "Proof of business activity (photos, receipts)",
            "CAC certificate (if registered) or intention to register",
            "BVN",
            "Passport photograph",
            "Business profile (1-2 pages describing what you do)",
            "Bank account details",
        ],
        "application_steps": [
            "Visit smedan.gov.ng/our-programs to see current open programmes",
            "Download the relevant application form",
            "Complete the form with your business details",
            "Attach required documents",
            "Submit to the nearest SMEDAN state office or via their portal",
            "Attend any required interviews or enterprise development training",
        ],
    },
    {
        "id": "nirsal-agsmeis-2026",
        "name": "NIRSAL Microfinance Bank AGSMEIS Loan",
        "description": (
            "The Agricultural, Small and Medium Enterprise Investment Scheme (AGSMEIS) "
            "is a Central Bank of Nigeria initiative implemented by NIRSAL Microfinance Bank. "
            "It provides low-interest loans to support agriculture and SME development."
        ),
        "amount": "Up to N10 million at 5% interest per annum",
        "deadline": "Rolling applications",
        "eligibility_sectors": ["agriculture", "food", "manufacturing", "services", "all"],
        "eligibility_stages": ["early", "growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://nmfb.com.ng",
        "required_documents": [
            "Valid government-issued ID (NIN slip, voter's card, or passport)",
            "BVN",
            "Passport photograph",
            "Proof of business/farm activity",
            "Letter of introduction from LGA or community leader (recommended)",
            "Business plan or project proposal",
            "Bank account details",
            "CAC certificate (if registered   not mandatory for micro level)",
        ],
        "application_steps": [
            "Register on the NIRSAL Microfinance Bank portal at nmfb.com.ng",
            "Complete the AGSMEIS loan application form",
            "Provide your business/farm details and loan purpose",
            "Attend mandatory entrepreneurship training (3-5 days, free of charge)",
            "Submit all required documents to nearest NIRSAL branch",
            "Await credit appraisal and disbursement",
        ],
    },
    {
        "id": "youwin-connect-2026",
        "name": "YouWiN Connect Business Plan Competition",
        "description": (
            "YouWiN! Connect (Youth Enterprise With Innovation in Nigeria) is a Federal "
            "Government programme providing business plan competition grants to young "
            "entrepreneurs aged 18-45. Winners receive grants, training, and mentorship."
        ),
        "amount": "N1 million to N10 million (non-repayable grants)",
        "deadline": "Announced annually by the Federal Ministry of Finance",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://youwin.org.ng",
        "required_documents": [
            "Valid government-issued ID",
            "Passport photograph",
            "Detailed business plan (YouWiN provides a template)",
            "Proof of residence (utility bill or tenancy agreement)",
            "BVN",
            "Educational certificates (optional but helpful)",
            "Evidence of any existing business activity",
        ],
        "application_steps": [
            "Visit youwin.org.ng and register during the open application window",
            "Download the YouWiN business plan template",
            "Prepare a compelling business plan with financials",
            "Submit your application and business plan online",
            "Shortlisted applicants attend a 5-day entrepreneurship training",
            "Submit refined business plan post-training",
            "Winners announced and grants disbursed",
        ],
    },
    {
        "id": "lsetf-loan-2026",
        "name": "Lagos State Employment Trust Fund (LSETF)",
        "description": (
            "The LSETF provides affordable loans and grants to Lagos-based entrepreneurs "
            "and MSMEs to create jobs and grow businesses. Interest rate starts at 5% per annum. "
            "Open to both registered and unregistered businesses."
        ),
        "amount": "N50,000 to N5 million at 5%-10% per annum",
        "deadline": "Rolling applications   Lagos residents only",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["Lagos"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://lsetf.ng",
        "required_documents": [
            "Lagos State residency proof (utility bill, rent agreement)",
            "Valid government-issued ID",
            "BVN",
            "Passport photograph",
            "Bank statement (3-6 months)",
            "Business plan or description",
            "CAC certificate (if registered)",
            "Evidence of business activity",
        ],
        "application_steps": [
            "Visit lsetf.ng and create an account",
            "Select the appropriate loan type (individual, group, or enterprise)",
            "Complete the online application form",
            "Submit required documents online or at an LSETF office",
            "Attend credit interview if shortlisted",
            "Loan disbursed to your account upon approval",
        ],
    },
    {
        "id": "vc4a-programmes-2026",
        "name": "VC4A Startup Programmes & Funding",
        "description": (
            "VC4A (Venture Capital for Africa) connects African startups and SMEs with "
            "investors, accelerators, and funding programmes. The platform lists hundreds "
            "of active funding opportunities, competitions, and accelerator programmes "
            "relevant to Nigerian businesses."
        ),
        "amount": "Varies by programme   from grants to equity investments up to $500,000",
        "deadline": "Multiple deadlines throughout the year",
        "eligibility_sectors": ["technology", "agriculture", "health", "education", "fintech", "all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://vc4a.com/programs/",
        "required_documents": [
            "Business registration documents (if available)",
            "Pitch deck (8-12 slides)",
            "Executive summary (1-2 pages)",
            "Financial projections (12-24 months)",
            "Team profiles/CVs",
            "Evidence of traction (users, revenue, partnerships)",
        ],
        "application_steps": [
            "Visit vc4a.com/programs and filter by your sector and stage",
            "Create a free VC4A profile for your business",
            "Prepare a compelling pitch deck and executive summary",
            "Apply to programmes that match your business",
            "Selected startups receive mentorship, funding, or investor connections",
        ],
    },
    {
        "id": "cartier-womens-2027",
        "name": "Cartier Women's Initiative Award",
        "description": (
            "The Cartier Women's Initiative supports women entrepreneurs worldwide with "
            "funding, coaching, and global visibility. The programme awards women-led "
            "businesses with impact in their communities."
        ),
        "amount": "$100,000 for regional winners; $30,000 for finalists",
        "deadline": "Applications open annually   check vc4a.com/cartier-womens-initiative",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://vc4a.com/cartier-womens-initiative/",
        "required_documents": [
            "Valid ID",
            "Proof that business is woman-led (founder documents)",
            "Business plan with social/environmental impact section",
            "Financial statements or projections",
            "Evidence of at least 1 year of business activity",
            "Two recommendation letters",
        ],
        "application_steps": [
            "Visit the Cartier Women's Initiative page on vc4a.com",
            "Confirm your business is woman-founded or woman-led",
            "Prepare your application showing business impact and growth",
            "Submit during the application window (usually September-November)",
            "Finalists attend the Cartier Summit for mentorship and visibility",
        ],
    },
    {
        "id": "fidelity-sme-loan-2026",
        "name": "Fidelity Bank SME Loans and Advances",
        "description": (
            "Fidelity Bank offers tailored loan products for SMEs including working capital loans, "
            "asset financing, and trade finance. The bank has specific products for women "
            "entrepreneurs and agribusiness operators."
        ),
        "amount": "N500,000 to N50 million depending on product",
        "deadline": "Always open   walk into any Fidelity Bank branch",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["100k_500k", "500k_2m", "2m_10m", "above_10m"],
        "requires_cac": True,
        "application_link": "https://www.fidelitybank.ng/sme-banking/sme-loans-and-advances/",
        "required_documents": [
            "CAC certificate and Form CAC 2 (particulars of directors)",
            "6-12 months bank statement",
            "BVN of all directors/signatories",
            "Valid ID of all directors",
            "Passport photographs",
            "Audited financial statements (if over 2 years operating)",
            "Business plan with financials",
            "Collateral documents (property, equipment, or guarantor)",
            "Tax Identification Number (TIN)",
            "Utility bill (business address)",
        ],
        "application_steps": [
            "Visit fidelitybank.ng/sme-banking or walk into any Fidelity branch",
            "Request the SME loan product information",
            "Complete the loan application form",
            "Submit with all required documents to your relationship manager",
            "Credit assessment and verification",
            "Loan approval and disbursement",
        ],
    },
    {
        "id": "cbn-msmdf-2026",
        "name": "CBN Micro, Small and Medium Enterprises Development Fund",
        "description": (
            "The CBN MSMEDF provides affordable finance to micro, small, and medium "
            "enterprises through participating financial institutions. Funds are channelled "
            "through microfinance banks, development finance institutions, and cooperatives."
        ),
        "amount": "N50,000 to N500,000 (micro) / up to N10M (SME tier)",
        "deadline": "Rolling   apply through participating microfinance banks",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://www.cbn.gov.ng/devfin/msmedf.asp",
        "required_documents": [
            "Valid government-issued ID",
            "BVN",
            "Passport photograph",
            "Proof of business activity",
            "Bank account details (active account at a microfinance bank)",
            "CAC certificate (for SME tier   not required for micro tier)",
            "Business plan or loan purpose statement",
        ],
        "application_steps": [
            "Identify a CBN-participating microfinance bank near you",
            "Visit the microfinance bank and request MSMEDF information",
            "Complete their application form",
            "Submit required documents",
            "Loan assessment and disbursement through the MFB",
        ],
    },
]


def get_all_opportunities() -> list[dict]:
    return FUNDING_OPPORTUNITIES


def get_opportunities_text() -> str:
    """Format opportunities for LLM matching prompt."""
    lines = []
    for opp in FUNDING_OPPORTUNITIES:
        lines.append(f"ID: {opp['id']}")
        lines.append(f"Name: {opp['name']}")
        lines.append(f"Amount: {opp['amount']}")
        lines.append(f"Deadline: {opp['deadline']}")
        lines.append(f"Sectors: {', '.join(opp['eligibility_sectors'])}")
        lines.append(f"Stages: {', '.join(opp['eligibility_stages'])}")
        lines.append(f"Locations: {', '.join(opp['eligibility_locations'])}")
        lines.append(f"CAC Required: {'Yes' if opp['requires_cac'] else 'No'}")
        lines.append(f"Description: {opp['description'][:200]}")
        lines.append("")
    return "\n".join(lines)
