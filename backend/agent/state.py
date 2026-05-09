from typing import Any, List, Dict
from typing_extensions import TypedDict

class AgentState(TypedDict):
    session_id: str
    profile: Dict[str, Any]
    messages: List[Dict]
    retrieved_chunks: List[Dict]
    policy_scores: List[Dict] 
    recommendation: Dict[str, Any]