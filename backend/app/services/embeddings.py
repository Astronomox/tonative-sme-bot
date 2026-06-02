"""
Semantic matching using sentence embeddings.
Uses a lightweight model (all-MiniLM-L6-v2) via the sentence-transformers library.
Falls back to keyword matching if embeddings are unavailable.
"""
import logging
import math
from typing import Optional

logger = logging.getLogger(__name__)

_model = None
_embeddings_available = False


def _get_model():
    global _model, _embeddings_available
    if _model is not None:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        _embeddings_available = True
        logger.info("Sentence transformer model loaded")
    except Exception as e:
        logger.warning(f"Sentence transformers unavailable, using keyword fallback: {e}")
        _model = None
    return _model


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def embed_text(text: str) -> Optional[list[float]]:
    model = _get_model()
    if not model:
        return None
    try:
        embedding = model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    except Exception as e:
        logger.warning(f"Embedding failed: {e}")
        return None


def semantic_score(profile_text: str, opportunity_text: str) -> float:
    """
    Returns a semantic similarity score between 0.0 and 1.0.
    Falls back to 0.5 (neutral) if embeddings are unavailable.
    """
    profile_vec = embed_text(profile_text)
    opp_vec = embed_text(opportunity_text)

    if profile_vec is None or opp_vec is None:
        return 0.5  # neutral fallback

    return cosine_similarity(profile_vec, opp_vec)


def is_available() -> bool:
    _get_model()
    return _embeddings_available
