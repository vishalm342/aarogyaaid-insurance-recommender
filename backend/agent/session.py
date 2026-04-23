import uuid
from backend.db.mongo import mongo_db
from datetime import datetime

async def create_session(session_id: str, profile: dict) -> None:
    session_data = {
        "_id": session_id,
        "profile": profile,
        "messages": [],
        "recommendation": None,
        "created_at": datetime.utcnow()
    }
    await mongo_db.sessions_collection.insert_one(session_data)

async def get_session(session_id: str) -> dict | None:
    return await mongo_db.sessions_collection.find_one({"_id": session_id})

async def update_session_recommendation(session_id: str, recommended_policy_id: str, recommended_policy_name: str, recommendation: dict) -> None:
    await mongo_db.sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {
            "recommended_policy_id": recommended_policy_id,
            "recommended_policy_name": recommended_policy_name,
            "recommendation": recommendation
        }}
    )

async def append_chat_message(session_id: str, role: str, content: str) -> None:
    message = {"role": role, "content": content, "timestamp": datetime.utcnow()}
    await mongo_db.sessions_collection.update_one(
        {"_id": session_id},
        {"$push": {"messages": message}}
    )