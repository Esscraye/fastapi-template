from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Template"
    DEBUG: bool = False
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache
def get_settings() -> Settings:
    return Settings()
