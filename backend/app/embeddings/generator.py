import logging
from sentence_transformers import SentenceTransformer
from app.config import settings
import numpy as np

logger = logging.getLogger(__name__)

_model = None

def load_embedding_model():
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")

def generate_embeddings(texts: list[str]) -> np.ndarray:
    if _model is None:
        load_embedding_model()
    return _model.encode(texts)

def generate_embedding(text: str) -> np.ndarray:
    return generate_embeddings([text])
