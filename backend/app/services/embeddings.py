"""
Embeddings stub - sentence-transformers removed to keep deployment lightweight.
Semantic scoring falls back to 0.5 (neutral) so keyword matching handles everything.
"""

def is_available() -> bool:
    return False

def semantic_score(profile_text: str, opportunity_text: str) -> float:
    return 0.5
