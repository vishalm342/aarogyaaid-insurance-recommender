from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db.mongo import connect, close
from backend.config import settings
from backend.routes import recommend, chat, admin
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await close()

app = FastAPI(title="AarogyaAid Recommender", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(admin.router, prefix="/api/admin")

@app.get("/")
async def health_check():
    return {"status": "ok"}