from backend.db.mongo import mongo_db
from backend.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

async def retrieve_chunks(query: str, policy_ids: list[str] = None, top_k: int = 5) -> list[dict]:
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.embedding_model, google_api_key=settings.gemini_api_key)
    query_vector = embeddings.embed_query(query)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "policy_chunks_vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": top_k * 10,
                "limit": top_k
            }
        },
        {
            "$project": {
                "text": 1,
                "clause_type": 1,
                "policy_name": 1,
                "insurer": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    if policy_ids:
        pipeline[0]["$vectorSearch"]["filter"] = {"policy_id": {"$in": policy_ids}}
        
    cursor = mongo_db.chunks_collection.aggregate(pipeline)
    results = await cursor.to_list(length=top_k)
    return results