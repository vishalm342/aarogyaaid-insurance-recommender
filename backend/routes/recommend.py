from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from enum import Enum
import uuid
from backend.agent.session import create_session, update_session_recommendation
from backend.agent.graph import get_recommendation_graph

router = APIRouter()

class LifestyleEnum(str, Enum):
    Sedentary = "Sedentary"
    Moderate = "Moderate"
    Active = "Active"
    Athlete = "Athlete"

class IncomeEnum(str, Enum):
    under_3L = "under_3L"
    from_3_8L = "3_8L"
    from_8_15L = "8_15L"
    above_15L = "15L_plus"

class CityEnum(str, Enum):
    Metro = "Metro"
    Tier2 = "Tier2"
    Tier3 = "Tier3"

class ProfileRequest(BaseModel):
    full_name: str
    age: int
    lifestyle: LifestyleEnum
    pre_existing_conditions: List[str]
    annual_income_band: IncomeEnum
    city_tier: CityEnum

@router.post("/profile/recommend")
async def recommend_policy(req: ProfileRequest):
    session_id = str(uuid.uuid4())
    profile_dict = req.model_dump()
    await create_session(session_id, profile_dict)
    
    app_graph = get_recommendation_graph()
    state = {
        "profile": profile_dict,
        "messages": [],
        "retrieved_chunks": [],
        "recommendation": {},
        "session_id": session_id
    }
    
    result = await app_graph.ainvoke(state)
    rec = result.get("recommendation", {})
    
    # Simple fallback parsing if needed
    best_policy_name = "Unknown"
    if rec.get("peer_comparison"):
        best_policy_name = rec["peer_comparison"][0].get("policy_name", "Unknown")
        
    await update_session_recommendation(session_id, "unknown_id", best_policy_name, rec)
    
    return {
        "session_id": session_id,
        "peer_comparison": rec.get("peer_comparison", []),
        "coverage_detail": rec.get("coverage_detail", {}),
        "why_this_policy": rec.get("why_this_policy", "")
    }