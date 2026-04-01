import logging
import os
from typing import Generator, List
from pydantic import BaseModel
from llama_cpp import Llama
from app.config import settings

logger = logging.getLogger(__name__)

_llm = None

def load_llm():
    global _llm
    if _llm is None:
        if not os.path.exists(settings.MODEL_PATH):
            logger.warning(f"Model path {settings.MODEL_PATH} does not exist. Skipping LLM load.")
            return
        
        logger.info(f"Loading LLM model... ({settings.MODEL_PATH})")
        _llm = Llama(
            model_path=settings.MODEL_PATH,
            n_ctx=2048,
            verbose=False,
            n_threads=4 
        )
        logger.info("Model loaded successfully")

def build_prompt(context: str, question: str) -> str:
    """Strict prompt template formatted for Mistral Instruct."""
    return f"""[INST] You are an AI knowledge assistant. Synthesize your answer ONLY using the context below.
If the context does not contain enough information to answer the question, output exactly "I don't know." and nothing else.

Context:
{context}

Question:
{question} [/INST]"""

def generate_answer(prompt: str) -> str:
    if _llm is None:
        return "LLM model not loaded. Please ensure the model file exists."
    
    response = _llm(
        prompt,
        max_tokens=512,
        stop=["Question:", "Context:"],
        echo=False
    )
    return response["choices"][0]["text"].strip()

def stream_answer(prompt: str) -> Generator[str, None, None]:
    if _llm is None:
        yield "LLM model not loaded."
        return
        
    for output in _llm(
        prompt,
        max_tokens=512,
        stop=["Question:", "Context:"],
        echo=False,
        stream=True
    ):
        yield output["choices"][0]["text"]
