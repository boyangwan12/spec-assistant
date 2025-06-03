from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pinecone_utils import embed_and_upsert_chunks

router = APIRouter(prefix="/embed", tags=["embed"])

class EmbedRequest(BaseModel):
    chunks: list
    filename: str

@router.post("")
def embed_chunks(req: EmbedRequest):
    result = embed_and_upsert_chunks(req.chunks, req.filename)
    return JSONResponse({"result": result})
