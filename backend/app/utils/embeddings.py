import logging
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"

# Module-level singleton — loaded once, reused for every request
_model: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"⏳ Loading sentence-transformer model '{MODEL_NAME}'...")
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("✅ Model loaded.")
    return _model


def get_embedding(text: str) -> np.ndarray:
    """Return a unit-normalised sentence embedding for the given text."""
    model = _load_model()
    # encode returns a numpy array
    embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return embedding
