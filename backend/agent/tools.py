from backend.rag.retriever import retrieve_chunks
from backend.db.mongo import mongo_db

async def retrieve_policy_chunks_tool(query: str) -> str:
    chunks = await retrieve_chunks(query, top_k=5)
    formatted = ["---"]
    for c in chunks:
        formatted.append(f"Source: {c.get('policy_name', 'Unknown Policy')} ({c.get('insurer', 'Unknown Insurer')}) - Clause: {c.get('clause_type', 'General')}")
        formatted.append(c.get("text", ""))
        formatted.append("---")
    return "\n".join(formatted)

async def get_all_policies_tool() -> str:
    cursor = mongo_db.policies_collection.find({}, {"policy_name": 1, "insurer": 1})
    policies = await cursor.to_list(length=100)
    
    if not policies:
        return "No policies available in the database."
        
    res = []
    for p in policies:
        res.append(f"- {p.get('policy_name')} by {p.get('insurer')}")
    return "\n".join(res)