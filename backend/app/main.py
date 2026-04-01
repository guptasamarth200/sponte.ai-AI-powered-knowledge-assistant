from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.embeddings.generator import load_embedding_model
from app.llm.generator import load_llm
from app.vector_store.faiss_store import initialize_index
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load models and initialize index
    logger.info("Starting up: Preloading models to avoid first-request delay.")
    load_embedding_model()
    load_llm()
    
    # Initialize index, load if persists, else build
    initialize_index()
    logger.info("System initialized successfully.")
    yield
    # Shutdown
    logger.info("Shutting down.")

app = FastAPI(title="AI Knowledge Assistant API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
