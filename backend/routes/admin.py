from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
import datetime
import tempfile
import os
from config import settings
from db.mongo import chunks_collection
from rag.ingest import ingest_policy

router = APIRouter()
security = HTTPBearer()


def create_token() -> str:
    payload = {
        "sub": "admin",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/admin/login")
async def login(req: LoginRequest):
    if req.username != settings.admin_username or req.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(), "token_type": "bearer"}


@router.get("/admin/policies", dependencies=[Depends(verify_token)])
async def list_policies():
    pipeline = [
        {"$group": {
            "_id": "$policy_id",
            "policy_name": {"$first": "$policy_name"},
            "insurer": {"$first": "$insurer"},
            "file_type": {"$first": "$file_type"},
            "uploaded_at": {"$first": "$uploaded_at"},
            "chunk_count": {"$sum": 1}
        }},
        {"$sort": {"uploaded_at": -1}}
    ]
    cursor = chunks_collection.aggregate(pipeline)
    docs = await cursor.to_list(length=100)
    return [
        {
            "policy_id": d["_id"],
            "policy_name": d["policy_name"],
            "insurer": d["insurer"],
            "file_type": d.get("file_type", "unknown"),
            "uploaded_at": str(d.get("uploaded_at", "")),
            "chunk_count": d["chunk_count"]
        }
        for d in docs
    ]


@router.post("/admin/upload", dependencies=[Depends(verify_token)])
async def upload_policy(
    file: UploadFile = File(...),
    policy_name: str = Form(...),
    insurer: str = Form(...)
):
    allowed = {".pdf", ".txt", ".json"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Use PDF, TXT, or JSON.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        chunk_count = await ingest_policy(tmp_path, policy_name=policy_name, insurer=insurer, file_type=ext)
        return {"message": f"Ingested {chunk_count} chunks", "policy_name": policy_name}
    finally:
        os.unlink(tmp_path)


class EditPolicyRequest(BaseModel):
    policy_name: str
    insurer: str


@router.put("/admin/policies/{policy_id}", dependencies=[Depends(verify_token)])
async def edit_policy(policy_id: str, req: EditPolicyRequest):
    result = await chunks_collection.update_many(
        {"policy_id": policy_id},
        {"$set": {"policy_name": req.policy_name, "insurer": req.insurer}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": f"Updated {result.modified_count} chunks"}


@router.delete("/admin/policies/{policy_id}", dependencies=[Depends(verify_token)])
async def delete_policy(policy_id: str):
    result = await chunks_collection.delete_many({"policy_id": policy_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Policy not found")
    return {"message": f"Deleted {result.deleted_count} chunks from vector store"}