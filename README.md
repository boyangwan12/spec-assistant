# Spec Assistant Backend (FastAPI)

This backend powers an internal AI assistant for Q&A over technical specification PDFs (coils/transformers).

## Features
- Upload and parse PDFs
- Chunk and embed content
- Semantic retrieval (Pinecone)
- LLM answers with citations (Mistral-7B)

## Tech Stack
- Python 3.10+
- FastAPI
- Poetry
- Unstructured.io
- Pinecone
- LangChain
- Ollama/vLLM (Mistral-7B)

## Setup
1. Install Poetry: `pip install poetry`
2. Install dependencies: `poetry install`
3. Add secrets to `.env`
4. Run server: `uvicorn app.main:app --reload`

## API Endpoints
See `/app/routers/` for endpoint details.

## Folder Structure
```
app/
  main.py
  routers/
    upload.py
    parse.py
    chunk.py
    embed.py
    chat.py
  services/
    llm.py
    pinecone_utils.py
    pdf_utils.py
  utils/
    formatter.py
  data/
.env
pyproject.toml
```
