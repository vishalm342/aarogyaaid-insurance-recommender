import re

def chunk_policy_document(text: str, policy_id: str, policy_name: str, insurer: str) -> list[dict]:
    # Semantic chunking by headers
    headers = ["Inclusions", "Exclusions", "Sub-limits", "Co-pay", "Waiting Period", "Coverage", "Benefits", "Conditions"]
    pattern = re.compile(r'(?=(?:' + '|'.join(headers) + r')\b)', re.IGNORECASE)
    
    raw_chunks = pattern.split(text)
    chunks = []
    
    for idx, chunk_text in enumerate(raw_chunks):
        chunk_text = chunk_text.strip()
        if not chunk_text:
            continue
            
        # Determine clause type based on starting text
        clause_type = "General"
        for h in headers:
            if chunk_text.lower().startswith(h.lower()):
                clause_type = h
                break
                
        chunks.append({
            "policy_id": policy_id,
            "policy_name": policy_name,
            "insurer": insurer,
            "clause_type": clause_type,
            "text": chunk_text,
            "chunk_index": idx
        })
    return chunks