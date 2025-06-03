from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.pdf_utils import partition_file_with_metadata

router = APIRouter(prefix="/parse", tags=["parse"])

class ParseRequest(BaseModel):
    filename: str

@router.post("")
async def parse_pdf(req: ParseRequest):
    print(">>> /parse POST endpoint called with filename:", req.filename)
    import traceback
    try:
        elements = partition_file_with_metadata(req.filename)
        print(">>> partition_file_with_metadata returned:", elements)
        return JSONResponse({"elements": elements})
    except Exception as e:
        print("Exception in /parse POST:", e)
        traceback.print_exc()
        raise

@router.get("")
async def parse_get():
    print(">>> /parse GET endpoint called")
    return {"status": "parse GET ok"}

@router.get("/test")
async def test():
    print(">>> /parse/test endpoint called")
    return {"status": "ok"}
