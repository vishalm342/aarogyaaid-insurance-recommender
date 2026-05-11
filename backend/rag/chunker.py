import fitz
import re
from typing import List, Dict

def estimate_tokens(text: str) -> int:
    """Approximate token count using word count."""
    words = len(text.split())
    return int(words * 1.3)

def chunk_pdf(file_bytes: bytes, policy_id: str, policy_name: str, insurer: str) -> List[Dict]:
    """Chunk PDF with line-based and sentence-based splitting."""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text = ""
    
    for page_num, page in enumerate(doc):
        text = page.get_text().strip()
        if not text:
            continue
        all_text += "\n\n" + text
    
    doc.close()
    
    if not all_text.strip():
        return []
    
    return _chunk_text_internal(all_text, policy_id, policy_name, insurer)


def _chunk_text_internal(text: str, policy_id: str, policy_name: str, insurer: str) -> List[Dict]:
    """Internal function to chunk text - used by both PDF and TXT processing."""
    if not text.strip():
        return []
    
    # Step 1: Split by double newlines (sections)
    sections = [s.strip() for s in text.split('\n\n') if s.strip()]
    
    # Step 2: For each section, split by single newlines (lines)
    all_lines = []
    for section in sections:
        lines = [line.strip() for line in section.split('\n') if line.strip()]
        all_lines.extend(lines)
    
    # Step 3: Group lines into chunks by sentence + tokens
    chunks = []
    current_chunk = []
    current_tokens = 0
    chunk_index = 0
    
    for line in all_lines:
        if not line or len(line) < 5:
            continue
        
        # Split line into sentences if it has multiple periods
        sentences = re.split(r'(?<=[.!?])\s+', line)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 5:
                continue
            
            sentence_tokens = estimate_tokens(sentence)
            
            # If this single sentence exceeds 512 tokens, split it by words
            if sentence_tokens > 512:
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                for word in words:
                    word_tokens = estimate_tokens(word)
                    if temp_tokens + word_tokens > 512 and temp_chunk:
                        chunk_text = " ".join(temp_chunk).strip()
                        if len(chunk_text) > 50:
                            chunks.append({
                                "policy_id": policy_id,
                                "policy_name": policy_name,
                                "insurer": insurer,
                                "page": 1,
                                "chunk_index": chunk_index,
                                "text": chunk_text,
                                "source": policy_name
                            })
                            chunk_index += 1
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    chunk_text = " ".join(temp_chunk).strip()
                    if len(chunk_text) > 50:
                        chunks.append({
                            "policy_id": policy_id,
                            "policy_name": policy_name,
                            "insurer": insurer,
                            "page": 1,
                            "chunk_index": chunk_index,
                            "text": chunk_text,
                            "source": policy_name
                        })
                        chunk_index += 1
                current_chunk = []
                current_tokens = 0
                continue
            
            # Normal case: try to add to current chunk
            if current_tokens + sentence_tokens > 512 and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk).strip()
                if len(chunk_text) > 50:
                    chunks.append({
                        "policy_id": policy_id,
                        "policy_name": policy_name,
                        "insurer": insurer,
                        "page": 1,
                        "chunk_index": chunk_index,
                        "text": chunk_text,
                        "source": policy_name
                    })
                    chunk_index += 1
                
                # Start new chunk with overlap (last sentence)
                current_chunk = [current_chunk[-1]] if current_chunk else []
                current_tokens = estimate_tokens(current_chunk[0]) if current_chunk else 0
            
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
    
    # Save final chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk).strip()
        if len(chunk_text) > 50:
            chunks.append({
                "policy_id": policy_id,
                "policy_name": policy_name,
                "insurer": insurer,
                "page": 1,
                "chunk_index": chunk_index,
                "text": chunk_text,
                "source": policy_name
            })
    
    # Fallback: if no chunks created, return entire text as one chunk
    if not chunks and text.strip():
        chunks.append({
            "policy_id": policy_id,
            "policy_name": policy_name,
            "insurer": insurer,
            "page": 1,
            "chunk_index": 0,
            "text": text.strip(),
            "source": policy_name
        })
    
    return chunks


def chunk_text(text: str, policy_id: str, policy_name: str, insurer: str) -> List[Dict]:
    """Chunk plain text with line-based and sentence-based splitting."""
    return _chunk_text_internal(text, policy_id, policy_name, insurer)