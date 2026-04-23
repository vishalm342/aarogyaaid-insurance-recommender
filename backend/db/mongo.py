from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None
    policies_collection = None
    chunks_collection = None
    sessions_collection = None

mongo_db = MongoDB()

async def connect():
    mongo_db.client = AsyncIOMotorClient(settings.mongodb_uri)
    mongo_db.db = mongo_db.client[settings.mongodb_db_name]
    mongo_db.policies_collection = mongo_db.db["policies"]
    mongo_db.chunks_collection = mongo_db.db["chunks"]
    mongo_db.sessions_collection = mongo_db.db["sessions"]

async def close():
    if mongo_db.client:
        mongo_db.client.close()