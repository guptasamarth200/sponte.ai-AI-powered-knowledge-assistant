from app.config import settings

def chunk_text(text: str, chunk_size=None, overlap=None) -> list[str]:
    c_size = chunk_size or settings.CHUNK_SIZE
    c_overlap = overlap or settings.CHUNK_OVERLAP
    chunks = []
    length = len(text)
    start = 0
    while start < length:
        end = min(start + c_size, length)
        chunks.append(text[start:end])
        start += (c_size - c_overlap)
    return chunks
