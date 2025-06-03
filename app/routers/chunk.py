from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pdf_utils import chunk_elements

router = APIRouter(prefix="/chunk", tags=["chunk"])

class ChunkRequest(BaseModel):
    elements: list

@router.post("")
def chunk_elements_endpoint(req: ChunkRequest):
    chunks = chunk_elements(req.elements)
    return JSONResponse({"chunks": chunks})
