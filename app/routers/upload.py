from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

import shutil
from docx2pdf import convert as docx2pdf_convert
import pdfkit
import xlsx2html
import pypandoc

@router.post("")
def upload_pdf(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        temp_input = os.path.join(DATA_DIR, f"temp_{uuid.uuid4().hex}{ext}")
        with open(temp_input, "wb") as f:
            shutil.copyfileobj(file.file, f)

        pdf_name = f"{uuid.uuid4().hex}.pdf"
        pdf_path = os.path.join(DATA_DIR, pdf_name)

        if ext == ".pdf":
            shutil.move(temp_input, pdf_path)
        elif ext == ".docx":
            # Convert DOCX to PDF
            try:
                docx2pdf_convert(temp_input, pdf_path)
            except Exception:
                # fallback to pypandoc
                pypandoc.convert_file(temp_input, 'pdf', outputfile=pdf_path)
            os.remove(temp_input)
        elif ext in [".xlsx", ".xls"]:
            # Convert XLSX to HTML, then HTML to PDF
            html_path = temp_input + ".html"
            with open(html_path, "w", encoding="utf-8") as html_file:
                xlsx2html.xlsx2html(temp_input, html_file)
            pdfkit.from_file(html_path, pdf_path)
            os.remove(temp_input)
            os.remove(html_path)
        else:
            os.remove(temp_input)
            return JSONResponse({"error": "Unsupported file type"}, status_code=400)

        return JSONResponse({"filename": pdf_name})
    except Exception as e:
        import traceback
        print("Exception in /upload:", e)
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
