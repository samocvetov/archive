from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./archive_new.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    UPLOAD_DIR: str = "./static/uploads"
    FRAGMENTS_DIR: str = "./static/uploads/fragments"
    MAX_UPLOAD_SIZE: int = 500 * 1024 * 1024
    
    FFmpeg_PATH: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
