import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(
    resume_embedding: np.ndarray,
    jd_embedding: np.ndarray,
) -> float:
    """
    Calculate cosine similarity between two embeddings.
    Returns a percentage score (0–100), rounded to 2 decimal places.
    Since embeddings are normalised, dot product == cosine similarity.
    """
    score = float(np.dot(resume_embedding, jd_embedding))
    # Clamp to [0, 1] in case of floating-point overshoot
    score = max(0.0, min(1.0, score))
    return round(score * 100, 2)
