from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATA_PATH: str = os.getenv("DOCS_PATH", "data/docs")
    INDEX_PATH: str = os.getenv("INDEX_PATH", "data/index.faiss")
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/app/models/mistral.gguf")
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 5

settings = Settings()
