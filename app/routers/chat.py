from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.llm import answer_query

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    filename: str
    top_k: int = 5

@router.post("")
def chat_endpoint(req: ChatRequest):
    answer = answer_query(req.query, req.filename, req.top_k)
    return JSONResponse(answer)
