from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid
from backend.config import settings
from backend.db.mongo import mongo_db
from backend.rag.ingest import ingest_policy
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("sub") != settings.admin_username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if req.username != settings.admin_username or req.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    expire = datetime.utcnow() + timedelta(hours=24)
    token = jwt.encode({"sub": req.username, "exp": expire}, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"token": token}

@router.post("/policies/upload", dependencies=[Depends(verify_token)])
async def upload_policy(
    policy_name: str = Form(...),
    insurer: str = Form(...),
    file: UploadFile = File(...)
):
    valid_exts = ["pdf", "txt", "json"]
    ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in valid_exts:
        ext = "pdf" # fallback logic or validation

    policy_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    chunk_count = await ingest_policy(file_bytes, file.filename, policy_name, insurer, policy_id)
    
    policy_doc = {
        "_id": policy_id,
        "policy_name": policy_name,
        "insurer": insurer,
        "filename": file.filename,
        "upload_date": datetime.utcnow(),
        "chunk_count": chunk_count
    }
    
    await mongo_db.policies_collection.insert_one(policy_doc)
    return {"policy_id": policy_id}

@router.get("/policies", dependencies=[Depends(verify_token)])
async def list_policies():
    cursor = mongo_db.policies_collection.find({})
    policies = await cursor.to_list(length=100)
    return policies

class PolicyUpdate(BaseModel):
    policy_name: str | None = None
    insurer: str | None = None

@router.patch("/policies/{policy_id}", dependencies=[Depends(verify_token)])
async def update_policy(policy_id: str, req: PolicyUpdate):
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        return {"status": "no update provided"}
        
    await mongo_db.policies_collection.update_one(
        {"_id": policy_id},
        {"$set": update_data}
    )
    # Update chunks to keep in sync
    await mongo_db.chunks_collection.update_many(
        {"policy_id": policy_id},
        {"$set": update_data}
    )
    return {"status": "updated"}

@router.delete("/policies/{policy_id}", dependencies=[Depends(verify_token)])
async def delete_policy(policy_id: str):
    async with await mongo_db.client.start_session() as session:
        async with session.start_transaction():
            res1 = await mongo_db.policies_collection.delete_one({"_id": policy_id}, session=session)
            await mongo_db.chunks_collection.delete_many({"policy_id": policy_id}, session=session)
            
    if res1.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
        
    return {"status": "deleted"}