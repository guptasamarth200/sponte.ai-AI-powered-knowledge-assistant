import logging
from app.embeddings.generator import generate_embedding
from app.vector_store.faiss_store import similarity_search
from app.config import settings

logger = logging.getLogger(__name__)

def retrieve_context(question: str):
    logger.info(f"Retrieving context for question: {question}")
    q_emb = generate_embedding(question)
    
    results = similarity_search(q_emb, top_k=settings.TOP_K)
    logger.info(f"Got {len(results)} chunks")
    
    if not results:
        # Avoids hallucination when no docs match
        return None, []
        
    # Build text context and map sources per chunk!
    context_parts = []
    sources = set()
    
    for rank, res in enumerate(results, start=1):
        context_parts.append(f"[{rank}] {res['chunk']}")
        sources.add(res['source'])
        
    context_text = "\n\n".join(context_parts)
    return context_text, list(sources)
