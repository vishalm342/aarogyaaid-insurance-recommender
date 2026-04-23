from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from backend.agent.prompts import SYSTEM_PROMPT
from backend.agent.tools import retrieve_policy_chunks_tool
from backend.config import settings
from langchain_openai import ChatOpenAI
import json

class UserState(TypedDict):
    profile: dict
    messages: list
    retrieved_chunks: list
    recommendation: dict
    session_id: str

def get_recommendation_graph():
    llm = ChatOpenAI(
        model=settings.sambanova_model,
        api_key=settings.sambanova_api_key,
        base_url=settings.sambanova_base_url,
        max_retries=2,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    async def guardrail_node(state: UserState):
        # We check messages or profile for medical queries
        # For simplicity in recommendation flow, if it's purely profile data, we pass.
        # This will be more relevant in the chat route.
        return state

    async def retrieve_node(state: UserState):
        p = state["profile"]
        query = f"Health insurance for {p['age']} year old, {p['lifestyle']} lifestyle, pre-existing conditions: {', '.join(p['pre_existing_conditions'])}, income {p['annual_income_band']}, living in {p['city_tier']}."
        chunks_str = await retrieve_policy_chunks_tool(query)
        state["retrieved_chunks"] = [chunks_str]
        return state

    async def recommend_node(state: UserState):
        chunks_context = state["retrieved_chunks"][0]
        prompt = f"{SYSTEM_PROMPT}\n\nRETRIEVED KNOWLEDGE:\n{chunks_context}\n\nUSER PROFILE:\n{json.dumps(state['profile'])}\n\nRespond with ONLY the JSON object."
        
        response = await llm.ainvoke(prompt)
        try:
            state["recommendation"] = json.loads(response.content)
        except Exception:
            state["recommendation"] = {} # Fallback
        return state

    builder = StateGraph(UserState)
    builder.add_node("guardrail_node", guardrail_node)
    builder.add_node("retrieve_node", retrieve_node)
    builder.add_node("recommend_node", recommend_node)

    builder.add_edge(START, "guardrail_node")
    builder.add_edge("guardrail_node", "retrieve_node")
    builder.add_edge("retrieve_node", "recommend_node")
    builder.add_edge("recommend_node", END)

    return builder.compile()