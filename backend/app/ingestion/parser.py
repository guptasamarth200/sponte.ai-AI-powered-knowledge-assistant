import os
import pdfplumber
import logging
from app.ingestion.chunker import chunk_text

logger = logging.getLogger(__name__)

def parse_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading txt {file_path}: {e}")
        return ""

def parse_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading pdf {file_path}: {e}")
    return text

def ingest_documents(directory: str):
    logger.info(f"Scanning directory {directory} for documents...")
    chunks_all = []
    metadata_all = []
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return [], []
        
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            text = ""
            if file.endswith('.txt'):
                text = parse_txt(file_path)
            elif file.endswith('.pdf'):
                text = parse_pdf(file_path)
            
            if text.strip():
                chunks = chunk_text(text)
                chunks_all.extend(chunks)
                metadata_all.extend([{"chunk": chunk, "source": file} for chunk in chunks])
    
    logger.info(f"Extracted {len(chunks_all)} chunks from documents.")
    return chunks_all, metadata_all
