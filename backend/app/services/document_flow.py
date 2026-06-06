"""
Document preparation walk-through flow.
Guides users through each required document one at a time.
Tracks readiness. Gives a score.
"""
import logging
from typing import Optional

# Document guide   what each document looks like and how to get it
DOCUMENT_GUIDE = {
    "valid_id": {
        "name": "Valid Government-Issued ID",
        "what_it_looks_like": "A photo ID with your name, photo, and a government stamp. Must not be expired. Acceptable: NIN slip, voter card, passport, driver license.",
        "how_to_get": "Fastest option: Go to any NIMC office with one passport photo. Get your NIN slip same day. FREE.",
        "time_to_get": "Same day (NIN slip)",
        "cost": "FREE for NIN slip",
        "common_problems": "Expired IDs are not accepted. Temporary voter cards are not accepted.",
    },
    "passport_photo": {
        "name": "Recent Passport Photograph",
        "what_it_looks_like": "2x2 inch color photo, white or light blue background, plain clothing, no hat, taken within 6 months.",
        "how_to_get": "Any photo studio near a market. Ask for passport photo, white background.",
        "time_to_get": "Same day, 30 minutes",
        "cost": "N200-N500",
        "common_problems": "Must be recent. Old phone photos not acceptable.",
    },
    "cac_certificate": {
        "name": "CAC Certificate of Registration",
        "what_it_looks_like": "Printed certificate with CAC logo, your business name, registration number, and date.",
        "how_to_get": "Register at cac.gov.ng. Business Name costs N10-15k, takes 5-7 working days online.",
        "time_to_get": "5-7 working days",
        "cost": "N10,000-N15,000 (Business Name)",
        "common_problems": "CAC portal can be slow   try early morning. Remita payment may take 24h to reflect.",
    },
    "bank_statement": {
        "name": "Bank Statement (3-6 months)",
        "what_it_looks_like": "Printed or PDF document from your bank showing transactions. Must be stamped by bank or official download.",
        "how_to_get": "Walk into your bank and request a printed statement, or download from internet banking.",
        "time_to_get": "Same day at bank. Instant online.",
        "cost": "Usually free",
        "advice": "Open a business account TODAY. The 6-month clock starts when you open it.",
    },
    "bvn": {
        "name": "Bank Verification Number (BVN)",
        "what_it_looks_like": "11-digit number. You provide it on application forms   no physical document needed.",
        "how_to_get": "Dial *565*0# on your bank-registered phone. Shows immediately.",
        "time_to_get": "Instant",
        "cost": "FREE",
        "common_problems": "No BVN means no bank account. Open one first.",
    },
    "tin": {
        "name": "Tax Identification Number (TIN)",
        "what_it_looks_like": "A unique number from FIRS. Download TIN Certificate from taxpromax.firs.gov.ng.",
        "how_to_get": "Online: taxpromax.firs.gov.ng   register and get TIN immediately. Or walk into any FIRS office.",
        "time_to_get": "Instant online",
        "cost": "FREE",
    },
    "business_plan": {
        "name": "Business Plan",
        "what_it_looks_like": "A document describing your business, customers, revenue model, and financial projections.",
        "how_to_get": "Write it using TEF free template at tefconnect.com. For micro-level, 5 pages is enough.",
        "time_to_get": "3-7 days with focus",
        "cost": "FREE if you write it yourself",
        "tips": "For TEF and SMEDAN, 5 pages is enough. For BOI, you need 15+ pages with financial projections.",
    },
    "utility_bill": {
        "name": "Utility Bill or Proof of Address",
        "what_it_looks_like": "Recent electricity, water, or DSTV bill showing your name and address. Or a tenancy agreement.",
        "how_to_get": "Use your NEPA/electricity bill or ask landlord for address confirmation letter.",
        "time_to_get": "Immediate if you have a recent bill",
        "cost": "FREE",
        "common_problems": "Must be recent (within 3 months).",
    },
}

logger = logging.getLogger(__name__)

# Document keys per opportunity
OPPORTUNITY_DOCUMENTS = {
    "tef-2026": ["valid_id", "passport_photo", "business_plan", "bvn"],
    "boi-msme-2026": ["valid_id", "passport_photo", "cac_certificate", "bank_statement", "bvn", "tin", "business_plan", "utility_bill"],
    "smedan-grant-2026": ["valid_id", "passport_photo", "bvn", "utility_bill"],
    "nirsal-agsmeis-2026": ["valid_id", "passport_photo", "bvn", "bank_statement"],
    "youwin-connect-2026": ["valid_id", "passport_photo", "business_plan", "utility_bill", "bvn"],
    "lsetf-loan-2026": ["valid_id", "passport_photo", "bvn", "bank_statement", "utility_bill"],
    "vc4a-programmes-2026": ["valid_id", "business_plan"],
    "cartier-womens-2027": ["valid_id", "business_plan", "bank_statement"],
    "fidelity-sme-loan-2026": ["valid_id", "cac_certificate", "bank_statement", "bvn", "tin", "business_plan", "utility_bill"],
    "cbn-msmdf-2026": ["valid_id", "bvn", "passport_photo", "bank_statement"],
}

# User document readiness stored in memory (also persisted via profile notes)
_readiness_cache: dict[str, dict] = {}  # phone -> {opp_id -> {doc_key -> bool}}


def get_user_readiness(phone_number: str, opp_id: str) -> dict:
    """Get the readiness state for a user + opportunity."""
    return _readiness_cache.get(phone_number, {}).get(opp_id, {})


def set_document_status(phone_number: str, opp_id: str, doc_key: str, has_it: bool):
    """Mark a document as available or not."""
    if phone_number not in _readiness_cache:
        _readiness_cache[phone_number] = {}
    if opp_id not in _readiness_cache[phone_number]:
        _readiness_cache[phone_number][opp_id] = {}
    _readiness_cache[phone_number][opp_id][doc_key] = has_it


def calculate_readiness_score(phone_number: str, opp_id: str) -> tuple[int, list[str]]:
    """
    Returns (score_percentage, list_of_missing_doc_names).
    """
    required_docs = OPPORTUNITY_DOCUMENTS.get(opp_id, [])
    if not required_docs:
        return 0, []

    readiness = get_user_readiness(phone_number, opp_id)
    have_count = sum(1 for doc in required_docs if readiness.get(doc) is True)
    missing = [doc for doc in required_docs if readiness.get(doc) is not True]
    missing_names = [DOCUMENT_GUIDE.get(doc, {}).get("name", doc) for doc in missing]

    score = int((have_count / len(required_docs)) * 100)
    return score, missing_names


def get_next_unchecked_document(phone_number: str, opp_id: str) -> Optional[str]:
    """Get the next document that hasn't been asked about yet."""
    required_docs = OPPORTUNITY_DOCUMENTS.get(opp_id, [])
    readiness = get_user_readiness(phone_number, opp_id)
    for doc in required_docs:
        if doc not in readiness:  # not yet asked
            return doc
    return None


def build_document_question(doc_key: str, lang: str = "en") -> str:
    """Build a conversational question about a specific document."""
    doc = DOCUMENT_GUIDE.get(doc_key, {})
    name = doc.get("name", doc_key)
    what = doc.get("what_it_looks_like", "")

    questions = {
        "en": f"Do you have a *{name}*?\n\n{what}\n\nReply *yes* or *no*.",
        "pcm": f"You get *{name}*?\n\n{what}\n\nSay *yes* or *no*.",
        "yo": f"Nje o ni *{name}*?\n\n{what}\n\nSo *beeni* tabi *rara*.",
        "ha": f"Kana da *{name}*?\n\n{what}\n\nSa *eh* ko *a'a*.",
        "fr": f"Avez-vous *{name}*?\n\n{what}\n\nRépondez *oui* ou *non*.",
    }
    return questions.get(lang, questions["en"])


def build_how_to_get(doc_key: str, lang: str = "en") -> str:
    """Build instructions for getting a missing document."""
    doc = DOCUMENT_GUIDE.get(doc_key, {})
    name = doc.get("name", doc_key)
    how = doc.get("how_to_get", "")
    time_to_get = doc.get("time_to_get", "")
    cost = doc.get("cost", "")
    problems = doc.get("common_problems", "")
    advice = doc.get("advice", "")

    text = f"No problem. Here is how to get your *{name}*:\n\n"
    if how:
        text += f"{how}\n\n"
    if time_to_get:
        text += f"Time: {time_to_get}\n"
    if cost:
        text += f"Cost: {cost}\n"
    if problems:
        text += f"\nNote: {problems}"
    if advice:
        text += f"\n\n{advice}"

    text += "\n\nOnce you have it, come back and we continue."
    return text


def build_readiness_summary(phone_number: str, opp_id: str, opp_name: str, lang: str = "en") -> str:
    """Build the readiness summary message."""
    score, missing = calculate_readiness_score(phone_number, opp_id)
    required_docs = OPPORTUNITY_DOCUMENTS.get(opp_id, [])
    have_count = len(required_docs) - len(missing)

    if score == 100:
        summaries = {
            "en": f"You are *100% ready* to apply for {opp_name}.\n\nYou have all {len(required_docs)} required documents.\n\nGo to the application link and apply now. You are ready.",
            "pcm": f"You don ready 100% to apply for {opp_name}.\n\nYou get all {len(required_docs)} documents wey dem need.\n\nGo apply now. You ready!",
            "fr": f"Vous êtes *prêt à 100%* pour postuler à {opp_name}.\n\nVous avez tous les {len(required_docs)} documents requis.\n\nPostulez maintenant.",
        }
        return summaries.get(lang, summaries["en"])

    missing_list = "\n".join(f"• {m}" for m in missing)
    summaries = {
        "en": (
            f"*Readiness check for {opp_name}*\n\n"
            f"You have {have_count} of {len(required_docs)} documents ready.\n"
            f"Your readiness score: *{score}%*\n\n"
            f"Still missing:\n{missing_list}\n\n"
            f"Want me to help you get each of these? Just say *continue* and we go through them one by one."
        ),
        "pcm": (
            f"*{opp_name}   how ready you be*\n\n"
            f"You get {have_count} out of {len(required_docs)} documents.\n"
            f"Your score: *{score}%*\n\n"
            f"You still need:\n{missing_list}\n\n"
            f"You wan make I help you get dem one by one? Say *continue*."
        ),
        "fr": (
            f"*Préparation pour {opp_name}*\n\n"
            f"Vous avez {have_count} sur {len(required_docs)} documents.\n"
            f"Score de préparation: *{score}%*\n\n"
            f"Il vous manque:\n{missing_list}\n\n"
            f"Voulez-vous que je vous aide à les obtenir? Dites *continuer*."
        ),
    }
    return summaries.get(lang, summaries["en"])


def get_all_readiness_scores(phone_number: str) -> dict:
    """Get readiness scores across all opportunities for a user."""
    scores = {}
    for opp_id in OPPORTUNITY_DOCUMENTS:
        score, missing = calculate_readiness_score(phone_number, opp_id)
        if score > 0:
            scores[opp_id] = {"score": score, "missing_count": len(missing)}
    return scores
