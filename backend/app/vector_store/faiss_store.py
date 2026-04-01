import faiss
import numpy as np
import os
import pickle
import logging
from app.config import settings
from app.ingestion.parser import ingest_documents
from app.embeddings.generator import generate_embeddings

logger = logging.getLogger(__name__)

_index = None
_metadata = []

def initialize_index():
    global _index, _metadata
    metadata_path = settings.INDEX_PATH + ".meta"
    
    if os.path.exists(settings.INDEX_PATH) and os.path.exists(metadata_path):
        logger.info(f"Loading existing FAISS index from {settings.INDEX_PATH}")
        _index = faiss.read_index(settings.INDEX_PATH)
        with open(metadata_path, "rb") as f:
            _metadata = pickle.load(f)
    else:
        logger.info("No persistent index found. Ingesting documents and building new index...")
        chunks, metas = ingest_documents(settings.DATA_PATH)
        if chunks:
            embeddings = generate_embeddings(chunks)
            dimension = embeddings.shape[1]
            _index = faiss.IndexFlatL2(dimension)
            _index.add(embeddings)
            _metadata = metas
            
            # Persist index
            os.makedirs(os.path.dirname(settings.INDEX_PATH), exist_ok=True)
            faiss.write_index(_index, settings.INDEX_PATH)
            with open(metadata_path, "wb") as f:
                pickle.dump(_metadata, f)
            logger.info("Index saved to disk.")
        else:
            logger.warning("No documents found to index.")

def similarity_search(query_embedding: np.ndarray, top_k: int = 5):
    if _index is None or _index.ntotal == 0:
        return []
    
    distances, indices = _index.search(query_embedding, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1 and idx < len(_metadata):
            results.append({
                "chunk": _metadata[idx]["chunk"],
                "source": _metadata[idx]["source"],
                "distance": float(distances[0][i])
            })
    return results
