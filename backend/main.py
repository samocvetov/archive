from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from config import settings
from database import init_db
from routers import videos, fragments, tags, auth, yandex

app = FastAPI(
    title="АРХИВ - Video Archive Service",
    description="Web service for video archiving, fragment management, and tagging with Yandex Disk support",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()
    
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.FRAGMENTS_DIR).mkdir(parents=True, exist_ok=True)
    Path(f"{settings.UPLOAD_DIR}/thumbnails").mkdir(parents=True, exist_ok=True)

app.include_router(auth.router, prefix="/api")
app.include_router(yandex.router, prefix="/api")
app.include_router(videos.router, prefix="/api")
app.include_router(fragments.router, prefix="/api")
app.include_router(fragments.global_router, prefix="/api")
app.include_router(tags.router, prefix="/api")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/fragments", StaticFiles(directory="static/uploads/fragments"), name="fragments")

@app.get("/")
async def root():
    return {
        "message": "АРХИВ - Video Archive Service",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
