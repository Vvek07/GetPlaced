from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ats.db")
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:3001", 
        "http://127.0.0.1:3001",
        "https://*.vercel.app",
        "https://getplaced.vercel.app"
    ]
    
    # File Storage
    UPLOAD_DIRECTORY: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    
    # NLP
    SPACY_MODEL: str = "en_core_web_sm"
    
    class Config:
        env_file = ".env"


settings = Settings()