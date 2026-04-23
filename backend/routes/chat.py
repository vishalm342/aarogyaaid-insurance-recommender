from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.agent.session import get_session, append_chat_message
from backend.agent.prompts import SYSTEM_PROMPT
from backend.config import settings
from langchain_openai import ChatOpenAI
import json

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
async def chat(req: ChatRequest):
    session = await get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Guardrail check
    lower_msg = req.message.lower()
    medical_keywords = ["surgery", "dosage", "serious condition", "should i take", "prescription", "diagnose"]
    if any(k in lower_msg for k in medical_keywords):
        fallback = "I can only help with understanding insurance coverage. For medical decisions, please consult your doctor."
        await append_chat_message(req.session_id, "user", req.message)
        await append_chat_message(req.session_id, "assistant", fallback)
        return {"response": fallback, "session_id": req.session_id}

    await append_chat_message(req.session_id, "user", req.message)
    
    llm = ChatOpenAI(
        model=settings.sambanova_model,
        api_key=settings.sambanova_api_key,
        base_url=settings.sambanova_base_url,
        max_retries=2
    )
    
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in session.get("messages", [])])
    prompt = f"{SYSTEM_PROMPT}\n\nUSER PROFILE:\n{json.dumps(session.get('profile', {}))}\n\nRECOMMENDED POLICY:\n{json.dumps(session.get('recommendation', {}))}\n\nCHAT HISTORY:\n{history_str}\n\nUSER: {req.message}\nASSISTANT:"
    
    response = await llm.ainvoke(prompt)
    bot_msg = response.content
    
    await append_chat_message(req.session_id, "assistant", bot_msg)
    
    return {"response": bot_msg, "session_id": req.session_id}