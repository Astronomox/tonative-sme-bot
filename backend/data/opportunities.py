FUNDING_OPPORTUNITIES = [
    {
        "id": "ng-youwin-2026",
        "name": "YouWiN! Connect Programme",
        "description": "Federal Government of Nigeria enterprise support programme providing grants and business development support to young entrepreneurs across Nigeria.",
        "amount": "Up to NGN 10,000,000",
        "deadline": "Rolling applications",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["early", "growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m", "2m_10m"],
        "requires_cac": True,
        "application_link": "https://youwin.org.ng",
        "application_steps": [
            "Visit youwin.org.ng and create an account",
            "Complete the online business plan template",
            "Upload your CAC registration certificate",
            "Submit your application before the deadline",
            "Attend the business training if shortlisted"
        ]
    },
    {
        "id": "tony-elumelu-2026",
        "name": "Tony Elumelu Foundation Entrepreneurship Programme (TEF)",
        "description": "Annual programme providing $5,000 seed capital, mentorship, and training to African entrepreneurs. Open to businesses in all sectors across all 54 African countries.",
        "amount": "$5,000 (approx NGN 4,000,000)",
        "deadline": "March 31, 2026 (annual cycle)",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://tefconnect.com",
        "application_steps": [
            "Create an account on TEFConnect.com",
            "Complete the online application form with your business idea",
            "Record a 60-second pitch video explaining your business",
            "Submit before March 31",
            "If selected, complete the 12-week online training before receiving funds"
        ]
    },
    {
        "id": "boi-grow",
        "name": "Bank of Industry (BOI) SME Loan",
        "description": "Low-interest loans from the Bank of Industry for small and medium enterprises in manufacturing, agro-processing, solid minerals, services, and ICT sectors.",
        "amount": "NGN 500,000 to NGN 500,000,000",
        "deadline": "Always open",
        "eligibility_sectors": ["manufacturing", "agriculture", "technology", "services", "food"],
        "eligibility_stages": ["growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["500k_2m", "2m_10m", "above_10m"],
        "requires_cac": True,
        "application_link": "https://boi.ng",
        "application_steps": [
            "Visit boi.ng and click Apply for Loan",
            "Register and complete the online application",
            "Prepare your business plan and financial statements",
            "Provide your CAC certificate and tax clearance",
            "Submit and wait for the credit assessment team to contact you"
        ]
    },
    {
        "id": "nirsal-agro",
        "name": "NIRSAL Microfinance Bank Agribusiness Loan",
        "description": "Specialized agricultural loans for farmers, agro-processors, and agricultural input dealers across Nigeria at single-digit interest rates.",
        "amount": "NGN 100,000 to NGN 5,000,000",
        "deadline": "Always open",
        "eligibility_sectors": ["agriculture", "food"],
        "eligibility_stages": ["early", "growing", "established"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://nirsal.com",
        "application_steps": [
            "Visit any NIRSAL Microfinance Bank branch near you",
            "Fill the loan application form",
            "Provide a valid ID (NIN, voter's card, or driver's license)",
            "Show proof of your farming or agribusiness activity",
            "Provide a guarantor if required"
        ]
    },
    {
        "id": "ng-grants-women",
        "name": "WOTCLEF Women Empowerment Grant",
        "description": "Women Trafficking and Child Labour Eradication Foundation grant supporting women-owned businesses with capital and skills training.",
        "amount": "Up to NGN 500,000",
        "deadline": "Quarterly applications",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k"],
        "requires_cac": False,
        "application_link": "https://wotclef.org",
        "application_steps": [
            "Contact your state WOTCLEF office for the application form",
            "Fill out the form with your business details",
            "Attach passport photographs and a valid ID",
            "Describe your business plan in 500 words or less",
            "Submit and attend the interview when invited"
        ]
    },
    {
        "id": "smedan-grant",
        "name": "SMEDAN Conditional Grant Scheme",
        "description": "Small and Medium Enterprises Development Agency of Nigeria provides conditional grants and business development services to micro and small enterprises.",
        "amount": "NGN 50,000 to NGN 3,000,000",
        "deadline": "Rolling (state-based cycles)",
        "eligibility_sectors": ["all"],
        "eligibility_stages": ["idea", "early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://smedan.gov.ng",
        "application_steps": [
            "Visit smedan.gov.ng or your state SMEDAN office",
            "Register your business on the SMEDAN portal",
            "Complete the enterprise registration form",
            "Attend the mandatory business development training",
            "Submit your application after completing the training"
        ]
    },
    {
        "id": "afdb-youth",
        "name": "African Development Bank Youth Entrepreneurship Investment Programme",
        "description": "AfDB-backed programme providing financing and technical assistance to young entrepreneurs aged 18-35 across Africa with innovative business ideas.",
        "amount": "$10,000 to $50,000",
        "deadline": "Annual application window (check website)",
        "eligibility_sectors": ["technology", "agriculture", "manufacturing", "services"],
        "eligibility_stages": ["early", "growing"],
        "eligibility_locations": ["all"],
        "eligibility_revenue": ["under_100k", "100k_500k", "500k_2m"],
        "requires_cac": False,
        "application_link": "https://afdb.org/en/topics-and-sectors/initiatives-partnerships/jobs-for-youth-in-africa",
        "application_steps": [
            "Visit the AfDB Jobs for Youth portal",
            "Check for the current application window",
            "Prepare a detailed business plan with financial projections",
            "Complete the online application form",
            "Submit supporting documents including ID and business registration if available"
        ]
    }
]


def get_opportunities_text() -> str:
    lines = []
    for opp in FUNDING_OPPORTUNITIES:
        lines.append(f"NAME: {opp['name']}")
        lines.append(f"AMOUNT: {opp['amount']}")
        lines.append(f"DEADLINE: {opp['deadline']}")
        lines.append(f"SECTORS: {', '.join(opp['eligibility_sectors'])}")
        lines.append(f"STAGES: {', '.join(opp['eligibility_stages'])}")
        lines.append(f"REQUIRES CAC: {'Yes' if opp['requires_cac'] else 'No'}")
        lines.append(f"LINK: {opp['application_link']}")
        lines.append(f"DESCRIPTION: {opp['description']}")
        lines.append("")
    return "\n".join(lines)
