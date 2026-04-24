from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.mongo import connect, close
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await close()

app = FastAPI(title="AarogyaAid Recommender API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes import recommend, chat, admin
app.include_router(recommend.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
async def health():
    return {"status": "ok", "service": "AarogyaAid Recommender API"}