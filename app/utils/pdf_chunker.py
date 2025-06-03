import fitz  # PyMuPDF
from typing import List, Dict, Any


def chunk_pdf_with_bbox(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text blocks and bounding boxes from each page of the PDF.
    Returns a list of dicts: {text, page, bbox: (x0, y0, x1, y1)}
    """
    doc = fitz.open(pdf_path)
    chunks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("blocks")  # returns (x0, y0, x1, y1, text, block_no, block_type)
        for block in blocks:
            x0, y0, x1, y1, text, *_ = block
            if text.strip():
                chunks.append({
                    "text": text.strip(),
                    "page": page_num + 1,  # 1-based page numbering
                    "bbox": [x0, y0, x1, y1],
                })
    doc.close()
    return chunks

def normalize_text(text):
    import re
    return re.sub(r'\s+', ' ', text).strip().lower()

def semantic_chunk_pdf_with_bbox(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Semantic chunking: splits each page's text into paragraphs, normalizes text before searching for bounding boxes.
    Returns a list of dicts: {text, page, bbox: (x0, y0, x1, y1)}
    """
    import re
    doc = fitz.open(pdf_path)
    chunks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        full_text = page.get_text()
        paragraphs = re.split(r'\n\s*\n', full_text)
        norm_page_text = normalize_text(full_text)
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            norm_para = normalize_text(para)
            if norm_para and norm_para in norm_page_text:
                # Use original para for search_for to get bbox
                bboxes = page.search_for(para)
                if not bboxes:
                    # Try searching for normalized version if exact match fails
                    bboxes = page.search_for(norm_para)
                if not bboxes:
                    continue
                for bbox in bboxes:
                    chunks.append({
                        "text": para,
                        "page": page_num + 1,
                        "bbox": list(bbox)
                    })
    doc.close()
    return chunks


def debug_print_sample_chunks_from_elements(elements, max_chunks=5, merge_headings=True, sliding_window=8):
    """
    Print a sample of chunks produced by chunk_from_parsed_elements for inspection.
    """
    chunks = chunk_from_parsed_elements(elements, merge_headings=True, sliding_window=8)
    print(f"\n--- Sample {max_chunks} chunks (merge_headings={merge_headings}, sliding_window={sliding_window}) ---")
    for i, chunk in enumerate(chunks[:max_chunks]):
        print(f"Chunk {i+1} (Page {chunk.get('page')}):\nText: {chunk.get('text')[:200]}\nBBox: {chunk.get('bbox')}\n---")
    if len(chunks) > max_chunks:
        print(f"... ({len(chunks) - max_chunks} more chunks not shown)")


def chunk_from_parsed_elements(elements: List[Dict[str, Any]], merge_headings: bool = True, sliding_window: int = 1) -> List[Dict[str, Any]]:
    """
    Chunk directly from parsed PDF elements.
    - merge_headings: if True, merge heading elements with their following paragraph.
    - sliding_window: if >1, create overlapping chunks of N elements.
    Returns list of chunks with merged text, combined bbox, page, section, and page_numbers.
    """
    import re
    chunks = []
    used = set()
    section = None
    section_pattern = re.compile(r"^(\d+(?:\.\d+)*)([ .])|^[A-Z][A-Z ]+$")
    # Pass 1: assign section to each element
    for i, el in enumerate(elements):
        text = el.get('text', '').strip()
        # Detect heading as section
        if text.isupper() or section_pattern.match(text):
            section = text
        elements[i]['section'] = section
        elements[i]['page_numbers'] = [el.get('page', el.get('page_number', None))] if el.get('page', el.get('page_number', None)) is not None else []
    # Merge headings with next paragraph if requested
    i = 0
    while i < len(elements):
        if merge_headings:
            is_heading = (
                elements[i]['text'].isupper() or
                re.match(r"^\d+(\.\d+)*[ .]", elements[i]['text'])
            )
            if is_heading and i + 1 < len(elements):
                merged_text = elements[i]['text'].strip() + '\n' + elements[i + 1]['text'].strip()
                bboxes = [elements[i]['bbox'], elements[i + 1]['bbox']]
                merged_bbox = [
                    min([b[0] for b in bboxes]),
                    min([b[1] for b in bboxes]),
                    max([b[2] for b in bboxes]),
                    max([b[3] for b in bboxes])
                ]
                chunks.append({
                    "text": merged_text,
                    "page": elements[i]['page'],
                    "bbox": merged_bbox,
                    "section": elements[i]['section'],
                    "page_numbers": elements[i]['page_numbers']
                })
                used.add(i)
                used.add(i+1)
                i += 2
                continue
        if i not in used:
            chunk = dict(elements[i])
            chunk['section'] = elements[i]['section']
            chunk['page_numbers'] = elements[i]['page_numbers']
            chunks.append(chunk)
        i += 1
    # Sliding window overlap
    if sliding_window > 1:
        window_chunks = []
        for i in range(len(chunks) - sliding_window + 1):
            window_text = '\n'.join([chunks[j]['text'] for j in range(i, i+sliding_window)])
            bboxes = [chunks[j]['bbox'] for j in range(i, i+sliding_window) if chunks[j]['bbox']]
            if bboxes:
                window_bbox = [
                    min([b[0] for b in bboxes]),
                    min([b[1] for b in bboxes]),
                    max([b[2] for b in bboxes]),
                    max([b[3] for b in bboxes])
                ]
            else:
                window_bbox = None
            # Use section of first chunk in window, combine all unique page_numbers
            window_section = chunks[i]['section']
            window_page_numbers = sorted(list({pn for j in range(i, i+sliding_window) for pn in chunks[j].get('page_numbers', [])}))
            window_chunks.append({
                "text": window_text,
                "page": chunks[i]['page'],
                "bbox": window_bbox,
                "section": window_section,
                "page_numbers": window_page_numbers
            })
        return window_chunks
    return chunks

    """
    Chunk directly from parsed PDF elements.
    - merge_headings: if True, merge heading elements with their following paragraph.
    - sliding_window: if >1, create overlapping chunks of N elements.
    Returns list of chunks with merged text, combined bbox, and page.
    """
    import re
    chunks = []
    used = set()
    # Merge headings with next paragraph if requested
    i = 0
    while i < len(elements):
        if merge_headings:
            # Heading detection: all-caps or section pattern
            is_heading = (
                elements[i]['text'].isupper() or
                re.match(r"^\d+(\.\d+)*[ .]", elements[i]['text'])
            )
            if is_heading and i + 1 < len(elements):
                merged_text = elements[i]['text'].strip() + '\n' + elements[i + 1]['text'].strip()
                bboxes = [elements[i]['bbox'], elements[i + 1]['bbox']]
                merged_bbox = [
                    min([b[0] for b in bboxes]),
                    min([b[1] for b in bboxes]),
                    max([b[2] for b in bboxes]),
                    max([b[3] for b in bboxes])
                ]
                chunks.append({
                    "text": merged_text,
                    "page": elements[i]['page'],
                    "bbox": merged_bbox
                })
                used.add(i)
                used.add(i+1)
                i += 2
                continue
        if i not in used:
            chunks.append(elements[i])
        i += 1
    # Sliding window overlap
    if sliding_window > 1:
        window_chunks = []
        for i in range(len(chunks) - sliding_window + 1):
            window_text = '\n'.join([chunks[j]['text'] for j in range(i, i+sliding_window)])
            bboxes = [chunks[j]['bbox'] for j in range(i, i+sliding_window) if chunks[j]['bbox']]
            if bboxes:
                window_bbox = [
                    min([b[0] for b in bboxes]),
                    min([b[1] for b in bboxes]),
                    max([b[2] for b in bboxes]),
                    max([b[3] for b in bboxes])
                ]
            else:
                window_bbox = None
            window_chunks.append({
                "text": window_text,
                "page": chunks[i]['page'],
                "bbox": window_bbox
            })
        return window_chunks
    return chunks


def sliding_window_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create overlapping chunks, each chunk = current + next paragraph.
    """
    window_chunks = []
    for i in range(len(chunks) - 1):
        window_chunks.append({
            "text": chunks[i]['text'] + ' ' + chunks[i + 1]['text'],
            "page": chunks[i]['page'],
            "bbox": chunks[i]['bbox']
        })
    return window_chunks


def get_neighbors(chunks: List[Dict[str, Any]], index: int) -> List[Dict[str, Any]]:
    """
    Given a chunk index, fetch neighbors (previous and next chunks).
    """
    if index < 0 or index >= len(chunks):
        return []
    neighbors = []
    if index > 0:
        neighbors.append(chunks[index - 1])
    if index < len(chunks) - 1:
        neighbors.append(chunks[index + 1])
    return neighbors
