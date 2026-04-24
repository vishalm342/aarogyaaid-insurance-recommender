import json
import re
from openai import AsyncOpenAI
from config import settings
from agent.state import AgentState
from agent.prompts import RECOMMENDATION_SYSTEM_PROMPT
from agent.tools import tool_retrieve_policy_chunks, tool_list_all_policies

client = AsyncOpenAI(
    api_key=settings.sambanova_api_key,
    base_url=settings.sambanova_base_url
)

def _build_profile_query(profile: dict) -> str:
    conditions = ", ".join(profile.get("pre_existing_conditions", ["None"])) or "None"
    return (
        f"Health insurance for {profile['age']} year old "
        f"{profile['lifestyle']} lifestyle person "
        f"with {conditions} "
        f"income {profile['annual_income']} "
        f"city {profile['city_tier']}"
    )

async def recommendation_node(state: AgentState) -> AgentState:
    profile = state["profile"]
    policies = await tool_list_all_policies()
    query = _build_profile_query(profile)

    all_chunks = []
    for policy in policies:
        chunks = await tool_retrieve_policy_chunks(query, policy_id=policy["policy_id"], top_k=3)
        all_chunks.extend(chunks)

    if not all_chunks:
        all_chunks = await tool_retrieve_policy_chunks(query, top_k=8)

    context = "\n\n---\n\n".join([
        f"Policy: {c['policy_name']} | Insurer: {c['insurer']}\n{c['text']}"
        for c in all_chunks
    ])

    user_message = f"""
User Profile:
- Name: {profile['full_name']}
- Age: {profile['age']}
- Lifestyle: {profile['lifestyle']}
- Pre-existing Conditions: {', '.join(profile.get('pre_existing_conditions', ['None']))}
- Annual Income Band: {profile['annual_income']}
- City Tier: {profile['city_tier']}

Retrieved Policy Documents:
{context}

Based on the profile and ONLY the retrieved policy documents above, generate the recommendation JSON.
"""

    response = await client.chat.completions.create(
        model=settings.sambanova_model,
        messages=[
            {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        try:
            recommendation = json.loads(json_match.group())
        except json.JSONDecodeError:
            recommendation = {"raw_response": raw, "error": "JSON parse failed"}
    else:
        recommendation = {"raw_response": raw, "error": "No JSON found"}

    return {**state, "retrieved_chunks": all_chunks, "recommendation": recommendation}


async def run_recommendation(profile: dict, session_id: str) -> dict:
    state: AgentState = {
        "session_id": session_id,
        "profile": profile,
        "messages": [],
        "retrieved_chunks": [],
        "recommendation": {}
    }
    result = await recommendation_node(state)
    return result["recommendation"]
