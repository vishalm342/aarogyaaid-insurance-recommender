import os
import requests, asyncio
from config import settings
from db.mongo import chunks_collection
from typing import List, Dict

def _embed_single(text: str) -> List[float]:
    r = requests.post('https://api.cohere.com/v2/embed',
        headers={'Authorization': f"Bearer {os.environ.get('COHERE_API_KEY')}"},
        json={'texts': [text], 'model': 'embed-english-light-v3.0',
              'input_type': 'search_query', 'embedding_types': ['float']},
        timeout=60)
    r.raise_for_status()
    return r.json()['embeddings']['float'][0]

async def embed_query(text: str) -> List[float]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _embed_single, text)

async def retrieve_policy_chunks(query: str, policy_id: str = None, top_k: int = 5) -> List[Dict]:
    query_embedding = await embed_query(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "policy_chunks_vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 50,
                "limit": top_k,
                **({"filter": {"policy_id": {"$eq": policy_id}}} if policy_id else {})
            }
        },
        {"$project": {"_id": 0, "text": 1, "policy_name": 1,
                      "insurer": 1, "policy_id": 1,
                      "score": {"$meta": "vectorSearchScore"}}}
    ]
    cursor = chunks_collection.aggregate(pipeline)
    return await cursor.to_list(length=top_k)
