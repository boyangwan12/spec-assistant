"""
PDF utilities: file validation, parsing, chunking logic.
"""
import os
from typing import List, Dict, Any
from app.utils.pdf_chunker import chunk_pdf_with_bbox

def partition_file_with_metadata(filename: str) -> List[Dict[str, Any]]:
    """
    Parse a PDF, Word DOCX, or Excel XLSX and return list of elements with metadata.
    For PDFs, use PyMuPDF to extract text blocks and bounding boxes.
    For DOCX/XLSX, fallback to unstructured.
    """
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    data_dir = os.path.join(project_root, 'data')
    # If absolute path, use as-is
    if os.path.isabs(filename):
        file_path = filename
    # If contains a directory, resolve relative to project root
    elif os.sep in filename or '/' in filename:
        file_path = os.path.join(project_root, filename)
    # Otherwise, look in /data
    else:
        file_path = os.path.join(data_dir, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        # Use PyMuPDF-based chunking
        chunks = chunk_pdf_with_bbox(file_path)
        # Add element_id and type for downstream compatibility
        import uuid
        for ch in chunks:
            ch["element_id"] = str(uuid.uuid4())
            ch["type"] = "paragraph"
            ch["page_number"] = ch["page"]
            ch["metadata"] = {"bbox": ch["bbox"]}
        return chunks
    else:
        from unstructured.partition.docx import partition_docx
        from unstructured.partition.xlsx import partition_xlsx
        import traceback
        try:
            if ext == ".docx":
                elements = partition_docx(filename=file_path)
            elif ext == ".xlsx":
                elements = partition_xlsx(filename=file_path)
            else:
                raise ValueError("Unsupported file type: only .pdf, .docx, and .xlsx are supported")
            parsed = []
            import uuid
            for el in elements:
                parsed.append({
                    "element_id": str(uuid.uuid4()),
                    "type": getattr(el, 'category', None),
                    "page_number": getattr(el.metadata, 'page_number', None),
                    "text": str(el),
                    "metadata": el.metadata.to_dict() if hasattr(el, 'metadata') and hasattr(el.metadata, 'to_dict') else {},
                })
            return parsed
        except Exception as e:
            print("Exception in partition_file_with_metadata:", e)
            traceback.print_exc()
            return [{"error": str(e)}]


def chunk_elements(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chunk parsed elements using heading+paragraph merge and sliding window overlap.
    Returns a list of semantic chunks with bbox and page for embedding.
    """
    from app.utils.pdf_chunker import chunk_from_parsed_elements
    # Use heading+paragraph merge and sliding window of 2 for overlap
    return chunk_from_parsed_elements(elements, merge_headings=True, sliding_window=8)
