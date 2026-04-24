from rag.retriever import retrieve_policy_chunks
from db.mongo import chunks_collection
from typing import List, Dict

async def tool_retrieve_policy_chunks(query: str, policy_id: str = None, top_k: int = 5) -> List[Dict]:
    return await retrieve_policy_chunks(query, policy_id=policy_id, top_k=top_k)

async def tool_list_all_policies() -> List[Dict]:
    pipeline = [
        {"$group": {
            "_id": "$policy_id",
            "policy_name": {"$first": "$policy_name"},
            "insurer": {"$first": "$insurer"}
        }},
        {"$project": {"_id": 0, "policy_id": "$_id", "policy_name": 1, "insurer": 1}}
    ]
    cursor = chunks_collection.aggregate(pipeline)
    return await cursor.to_list(length=100)
