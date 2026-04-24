import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(os.environ.get("MONGODB_URI"))
db = client[settings.mongodb_db_name]
policies_collection = db["policies"]
chunks_collection = db["policy_chunks"]
sessions_collection = db["sessions"]

async def connect():
    try:
        await client.admin.command("ping")
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

async def close():
    client.close()
    print("MongoDB connection closed")
