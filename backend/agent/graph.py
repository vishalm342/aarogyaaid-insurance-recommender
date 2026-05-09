import json
import re
from openai import AsyncOpenAI
from config import settings
from agent.state import AgentState
from agent.prompts import RECOMMENDATION_SYSTEM_PROMPT
from agent.tools import tool_retrieve_policy_chunks, tool_list_all_policies
from agent.scoring import InsuranceScoringEngine

client = AsyncOpenAI(
    api_key=settings.sambanova_api_key,
    base_url=settings.sambanova_base_url
)

scoring_engine = InsuranceScoringEngine()

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

    # Retrieve chunks for all policies
    all_chunks = []
    policy_chunks_map = {}  # policy_id -> chunks for scoring
    
    for policy in policies:
        chunks = await tool_retrieve_policy_chunks(query, policy_id=policy["policy_id"], top_k=5)
        all_chunks.extend(chunks)
        policy_chunks_map[policy["policy_id"]] = chunks

    if not all_chunks:
        all_chunks = await tool_retrieve_policy_chunks(query, top_k=8)
        # Reconstruct policy map if empty
        for chunk in all_chunks:
            policy_id = chunk.get('policy_id')
            if policy_id not in policy_chunks_map:
                policy_chunks_map[policy_id] = []
            policy_chunks_map[policy_id].append(chunk)

    # Calculate deterministic scores for each policy
    policy_scores = []
    for policy in policies:
        policy_id = policy["policy_id"]
        chunks = policy_chunks_map.get(policy_id, [])
        
        if chunks:
            score, breakdown = scoring_engine.calculate_suitability_score(chunks, profile)
            policy_scores.append({
                "policy_id": policy_id,
                "policy_name": chunks[0].get('policy_name', policy.get('policy_name')),
                "insurer": chunks[0].get('insurer', policy.get('insurer')),
                "score": score,
                "breakdown": breakdown,
                "chunks": chunks
            })
    
    # Sort by score
    policy_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Prepare context for LLM (top scored policies + all chunks)
    context = "\n\n---\n\n".join([
        f"Policy: {c['policy_name']} | Insurer: {c['insurer']} | Source: {c.get('source', 'Unknown')}\n{c['text']}"
        for c in all_chunks[:15]  # Limit to top 15 chunks
    ])

    # Prepare scored policies info for LLM
    scored_policies_info = "\n".join([
        f"- {p['policy_name']} (Insurer: {p['insurer']}): Deterministic Score = {p['score']}/100 "
        f"(Exclusion: {p['breakdown']['exclusion_match_score']}, "
        f"Affordability: {p['breakdown']['affordability_score']}, "
        f"Network: {p['breakdown']['network_availability_score']}, "
        f"Waiting Period: {p['breakdown']['waiting_period_score']})"
        for p in policy_scores[:5]
    ])

    user_message = f"""
User Profile:
- Name: {profile['full_name']}
- Age: {profile['age']}
- Lifestyle: {profile['lifestyle']}
- Pre-existing Conditions: {', '.join(profile.get('pre_existing_conditions', ['None']))}
- Annual Income Band: {profile['annual_income']}
- City Tier: {profile['city_tier']}

DETERMINISTIC POLICY SCORES (calculated from extracted data):
{scored_policies_info}

Retrieved Policy Documents (for reference):
{context}

Based on the profile, deterministic scores, and retrieved policy documents, generate the recommendation JSON.
Recommended policy should be the one with highest score. Use extracted data (premium, coverage, waiting period) from the breakdown.
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

    return {
        **state,
        "retrieved_chunks": all_chunks,
        "policy_scores": policy_scores,
        "recommendation": recommendation
    }


async def run_recommendation(profile: dict, session_id: str) -> dict:
    state: AgentState = {
        "session_id": session_id,
        "profile": profile,
        "messages": [],
        "retrieved_chunks": [],
        "policy_scores": [],
        "recommendation": {}
    }
    result = await recommendation_node(state)
    return result["recommendation"]