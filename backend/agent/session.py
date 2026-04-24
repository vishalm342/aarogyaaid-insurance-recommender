from db.mongo import db
from typing import Dict, Any
import datetime

sessions_col = db["sessions"]

async def create_session(session_id: str, profile: Dict[str, Any]):
    await sessions_col.insert_one({
        "_id": session_id,
        "profile": profile,
        "recommendation": {},
        "recommended_policy_id": None,
        "recommended_policy_name": None,
        "created_at": datetime.datetime.utcnow()
    })

async def get_session(session_id: str) -> Dict[str, Any]:
    return await sessions_col.find_one({"_id": session_id})

async def update_session_recommendation(session_id: str, policy_id: str, policy_name: str, recommendation: Dict):
    await sessions_col.update_one(
        {"_id": session_id},
        {"$set": {
            "recommendation": recommendation,
            "recommended_policy_id": policy_id,
            "recommended_policy_name": policy_name
        }}
    )
