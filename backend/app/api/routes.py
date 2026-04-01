from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List
from sse_starlette.sse import EventSourceResponse
from app.retrieval.retriever import retrieve_context
from app.llm.generator import build_prompt, generate_answer, stream_answer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]

@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    question = request.question
    context, sources = retrieve_context(question)
    
    if not context:
        logger.info("The system avoids hallucination by restricting answers to retrieved context.")
        return AskResponse(
            answer="I could not find relevant information in the documents.",
            sources=[]
        )
        
    prompt = build_prompt(context, question)
    answer = generate_answer(prompt)
    
    return AskResponse(answer=answer, sources=sources)

@router.get("/ask/stream")
async def stream_question(q: str, request: Request):
    question = q
    context, sources = retrieve_context(question)
    
    if not context:
        logger.info("No context found for query")
        async def mock_stream():
            import json
            yield {"data": json.dumps({"type": "sources", "sources": []})}
            yield {"data": json.dumps({"type": "token", "text": "I could not find relevant information in the documents."})}
            yield {"data": json.dumps({"type": "done"})}
        return EventSourceResponse(mock_stream())

    prompt = build_prompt(context, question)
    
    async def sse_generator():
        import json
        yield {"data": json.dumps({"type": "sources", "sources": sources})}

        generator = stream_answer(prompt)
        for token in generator:
            if await request.is_disconnected():
                break
            yield {"data": json.dumps({"type": "token", "text": token})}
            
        yield {"data": json.dumps({"type": "done"})}

    return EventSourceResponse(sse_generator())
