"""
LLM inference logic for Mistral-7B (Ollama/vLLM).
"""
from typing import Any, Dict

def answer_query(query: str, filename: str, top_k: int = 10) -> Dict[str, Any]:
    """
    RAG pipeline: embed query, retrieve top-k chunks from Pinecone, build prompt, call Mistral-7B, return cited answer.
    """
    import os
    from pinecone import Pinecone
    
    from dotenv import load_dotenv
    import requests

    load_dotenv()
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    INDEX_NAME = os.getenv("PINECONE_INDEX", "spec-assistant-index")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    MODEL_NAME = os.getenv("MODEL_NAME", "mistral-7b-instruct")

    if not PINECONE_API_KEY:
        return {"error": "Missing Pinecone API key in .env"}
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)
    import openai
    client = openai.OpenAI()
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_emb = response.data[0].embedding

    # 2. Retrieve top-k relevant chunks for this file
    try:
        results = index.query(vector=query_emb, top_k=top_k, include_metadata=True, filter={"filename": {"$eq": filename}})
        print("\n--- DEBUG: Pinecone query results ---")
        import pprint
        pprint.pprint(results)
        print("--- END DEBUG ---\n")
    except Exception as e:
        return {"error": f"Pinecone query failed: {e}"}
    matches = results.get("matches", [])
    if not matches:
        return {"answer": "No relevant content found.", "sources": []}

    # 3. Build prompt for LLM
    context = ""
    for i, m in enumerate(matches):
        context += f"[{i+1}] Section: {m['metadata'].get('section')} (pages {m['metadata'].get('page_numbers')})\n{m['metadata'].get('text', '')}\n\n"
    prompt = (
        "You are a helpful technical assistant. "
        "You will be given some sections from a technical document and a user question. "
        "If you find the answer in the provided document sections, answer the question and clearly cite where you found it, including section and page metadata. "
        "If you do not find the answer in the document, say: 'I did not find this information in the provided document context. However, here is an answer from my general knowledge (not from the document):' and then provide a helpful answer from your own knowledge. "
        f"Context sections:\n{context}\n"
        f"User question: {query}\n"
        "Answer:"
    )

    # DEBUG LOGGING
    print("\n--- RAG DEBUG ---")
    print("Question:", query)
    print("Prompt:\n", prompt)
    print("Context Chunks (retrieved from Pinecone):")
    for i, m in enumerate(matches):
        print(f"[{i+1}] Section: {m['metadata'].get('section')} (pages {m['metadata'].get('page_numbers')}):", m['metadata'].get('text', '')[:200], '...')
    print("--- END DEBUG ---\n")

    # 4. Call OpenAI ChatCompletion API
    try:
        import openai
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        if not OPENAI_API_KEY:
            return {"error": "Missing OpenAI API key in .env"}
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful and factual assistant for technical specification documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.2,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"LLM call failed: {e}"}

    # 5. Prepare sources for citation (section/page info)
    sources = [
        {
            "section": m["metadata"].get("section"),
            "page_numbers": m["metadata"].get("page_numbers"),
            "chunk_index": m["metadata"].get("chunk_index"),
            "score": m.get("score"),
            "text": m["metadata"].get("text", ""),
            "bbox": m["metadata"].get("bbox"),
            "page": m["metadata"].get("page"),
        }
        for m in matches
    ]

    # Only return citations referenced in the answer ([1], [2], ...)
    import re
    citation_pattern = re.compile(r"\[(\d+)\]")
    cited_indices = set(int(m.group(1)) - 1 for m in citation_pattern.finditer(answer))
    filtered_sources = [src for idx, src in enumerate(sources) if idx in cited_indices]
    if filtered_sources:
        return {"answer": answer, "citations": filtered_sources}
    else:
        return {"answer": answer, "citations": sources}  # fallback if no citation markers

