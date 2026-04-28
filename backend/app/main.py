"""FastAPI application factory."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import stories, jobs, scenes, ws, auth, voices, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(stories.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(scenes.router, prefix="/api/v1")
app.include_router(voices.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")
app.include_router(ws.router, prefix="/api/v1")

# Static file serving for generated assets
storage_path = Path(settings.STORAGE_LOCAL_PATH)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(storage_path)), name="storage")


@app.get("/health")
def health():
    return {"status": "ok"}
