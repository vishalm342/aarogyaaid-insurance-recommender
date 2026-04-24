from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI
from config import settings
from agent.tools import tool_retrieve_policy_chunks

router = APIRouter()

client = AsyncOpenAI(
    api_key=settings.sambanova_api_key,
    base_url=settings.sambanova_base_url
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str
    profile: dict
    recommended_policy: str = ""
    history: List[ChatMessage] = []

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        chunks = await tool_retrieve_policy_chunks(req.message, top_k=4)
        context = "\n\n".join([c["text"] for c in chunks]) if chunks else "No specific policy data found."

        system_prompt = f"""You are an empathetic health insurance advisor for AarogyaAid.

User Profile:
- Name: {req.profile.get('full_name')}
- Age: {req.profile.get('age')}
- Lifestyle: {req.profile.get('lifestyle')}
- Conditions: {', '.join(req.profile.get('pre_existing_conditions', ['None']))}
- Income: {req.profile.get('annual_income')}
- City Tier: {req.profile.get('city_tier')}

Recommended Policy: {req.recommended_policy}

Relevant Policy Document Excerpts:
{context}

Rules:
- Answer ONLY using the policy documents above. Do NOT use training knowledge for policy facts.
- If information is not in the documents, say: "I cannot find that in the uploaded policy documents."
- Define any insurance term the first time you use it.
- Decline medical advice questions. Say: "I can only help with policy coverage questions."
- Always connect answers to the user's specific profile and conditions.
- Remember the user's profile across all turns — never ask for it again."""

        messages = [{"role": "system", "content": system_prompt}]
        for h in req.history[-6:]:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": req.message})

        response = await client.chat.completions.create(
            model=settings.sambanova_model,
            messages=messages,
            temperature=0.3,
            max_tokens=800
        )

        return {"reply": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))