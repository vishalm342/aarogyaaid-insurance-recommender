import os
import requests, asyncio
from config import settings
from db.mongo import chunks_collection
from rag.chunker import chunk_pdf, chunk_text
from typing import List

def _embed_batch(texts: List[str]) -> List[List[float]]:
    r = requests.post('https://api.cohere.com/v2/embed',
        headers={'Authorization': f"Bearer {os.environ.get('COHERE_API_KEY')}"},
        json={'texts': texts, 'model': 'embed-english-light-v3.0',
              'input_type': 'search_document', 'embedding_types': ['float']},
        timeout=60)
    r.raise_for_status()
    return r.json()['embeddings']['float']

async def embed_texts(texts: List[str]) -> List[List[float]]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _embed_batch, texts)

async def ingest_policy(file_bytes: bytes, filename: str, policy_id: str, policy_name: str, insurer: str):
    if filename.endswith(".pdf"):
        chunks = chunk_pdf(file_bytes, policy_id, policy_name, insurer)
    else:
        chunks = chunk_text(file_bytes.decode("utf-8"), policy_id, policy_name, insurer)
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    embeddings = await embed_texts(texts)
    docs = [{**chunk, "embedding": emb} for chunk, emb in zip(chunks, embeddings)]
    await chunks_collection.insert_many(docs)
    return len(docs)

async def delete_policy_chunks(policy_id: str):
    result = await chunks_collection.delete_many({"policy_id": policy_id})
    return result.deleted_count
