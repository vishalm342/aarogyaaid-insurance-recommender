from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from agent.graph import run_recommendation

router = APIRouter()

class UserProfile(BaseModel):
    full_name: str
    age: int
    lifestyle: str
    pre_existing_conditions: List[str]
    annual_income: str
    city_tier: str

@router.post("/profile/recommend")
async def recommend(profile: UserProfile):
    try:
        session_id = str(uuid.uuid4())
        result = await run_recommendation(profile.model_dump(), session_id)
        return {"session_id": session_id, "recommendation": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))