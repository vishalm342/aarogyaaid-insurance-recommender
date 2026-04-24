import fitz
from typing import List, Dict

def chunk_pdf(file_bytes: bytes, policy_id: str, policy_name: str, insurer: str) -> List[Dict]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    chunks = []
    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            continue
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
        for i, para in enumerate(paragraphs):
            chunks.append({
                "policy_id": policy_id,
                "policy_name": policy_name,
                "insurer": insurer,
                "page": page_num + 1,
                "chunk_index": i,
                "text": para
            })
    doc.close()
    return chunks

def chunk_text(text: str, policy_id: str, policy_name: str, insurer: str) -> List[Dict]:
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
    return [
        {
            "policy_id": policy_id,
            "policy_name": policy_name,
            "insurer": insurer,
            "page": 1,
            "chunk_index": i,
            "text": para
        }
        for i, para in enumerate(paragraphs)
    ]
