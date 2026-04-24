from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    session_id: str
    profile: Dict[str, Any]
    messages: List[Dict[str, str]]
    retrieved_chunks: List[Dict[str, Any]]
    recommendation: Dict[str, Any]
