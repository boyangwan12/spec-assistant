"""
Pinecone utilities: embedding, upsert, retrieval.
"""
from typing import List, Dict, Any
import os
import openai
from dotenv import load_dotenv
from pinecone import Pinecone

def reset_pinecone_index(index_name: str, pinecone_api_key: str, dimension: int = 1536, metric: str = "cosine"):
    """
    Deletes and recreates the Pinecone index with the given name.
    NOTE: dimension=1536 is required for OpenAI 'text-embedding-3-small' embeddings.
    """
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=pinecone_api_key)
    if index_name in pc.list_indexes().names():
        print(f"Deleting Pinecone index: {index_name}")
        pc.delete_index(index_name)
    print(f"Creating Pinecone index: {index_name}")
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )


def embed_and_upsert_chunks(chunks: List[Dict[str, Any]], filename: str) -> dict:
    # Batch embed all chunktexts with OpenAI
    client = openai.OpenAI()  # Uses OPENAI_API_KEY from env
    texts = [chunk['text'] for chunk in chunks]
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    embeddings = [d.embedding for d in response.data]

    print("\n--- DEBUG: First 15 chunks before embedding ---")
    for i, chunk in enumerate(chunks[:15]):
        print(f"Chunk {i+1}:", chunk)
    print("--- END DEBUG ---\n")
    """
    Embed each chunk using OpenAI and upsert into Pinecone with metadata.
    Metadata includes: filename, section, page_numbers, chunk index.
    """
    load_dotenv()
    print("DEBUG Pinecone API Key:", os.getenv("PINECONE_API_KEY"))
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    INDEX_NAME = os.getenv("PINECONE_INDEX", "spec-assistant-index")

    if not PINECONE_API_KEY:
        return {"error": "Missing Pinecone API key in .env"}
    # Always reset Pinecone index before upserting
    # Use dimension=1536 for OpenAI embeddings
    reset_pinecone_index(INDEX_NAME, PINECONE_API_KEY, dimension=1536, metric="cosine")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    # Prepare batch upsert
    vectors = []
    for i, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        if not text.strip():
            continue
        embedding = embeddings[i]
        # Ensure Pinecone metadata values are valid types (no None/null)
        section = chunk.get("section")
        if section is None:
            section = ""
        page_numbers = chunk.get("page_numbers")
        if page_numbers is None:
            page_numbers = []
        # Pinecone requires list of strings for metadata lists
        if isinstance(page_numbers, list):
            page_numbers = [str(p) for p in page_numbers]
        meta = {
            "filename": filename,
            "section": section,
            "page_numbers": page_numbers,
            "chunk_index": i,
        }
        # Add bbox and page for citation/highlighting if present
        if "bbox" in chunk:
            # Store bbox as a string for Pinecone compatibility
            meta["bbox"] = str(chunk["bbox"])
        if "page_numbers" in chunk and chunk["page_numbers"]:
            meta["page"] = chunk["page_numbers"][0]
        # Pinecone expects id, values, metadata
        vectors.append((f"{filename}-{i}", embedding, meta))
    try:
        print("\n--- DEBUG: Vectors to upsert ---")
        for i, v in enumerate(vectors[:5]):
            print(f"Vector {i+1}: id={v[0]}, text={chunks[i]['text'] if i < len(chunks) else ''}, meta={v[2]}")
        print("--- END DEBUG ---\n")
        if vectors:
            index.upsert(vectors)
        return {"upserted": len(vectors)}
    except Exception as e:
        return {"error": str(e)}

