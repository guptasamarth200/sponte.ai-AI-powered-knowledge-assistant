# AI Knowledge Assistant

Simple RAG app using FastAPI, FAISS, and Next.js. Loads documents from a folder, embeds them, and streams answers using a local LLM.

## Setup

1. **Download the Model**
Grab a Mistral GGUF model and drop it in `backend/models/mistral.gguf`.
```bash
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf -O backend/models/mistral.gguf
```

2. **Add Docs**
Drop any `.txt` or `.pdf` files into `backend/data/docs`. The app parses them on startup.

3. **Run**
```bash
docker-compose up --build
```
Backend runs on `:8000`, frontend on `localhost:3000`.

## Notes
- **Local Inferencing**: Everything runs locally via `llama-cpp-python`. It's a bit slow on CPU but gets the job done without dealing with external APIs.
- **Strict Prompts**: If the vector DB doesn't return anything relevant, the model is hardcoded to just say it doesn't know, rather than hallucinating an answer.
- **Index Caching**: The FAISS index is written to disk so it doesn't rebuild every time you restart. If you add new docs, delete `backend/data/index.faiss` to force a re-index.
