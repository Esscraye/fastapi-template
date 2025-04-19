# Connexion à la base de données et gestion de la session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import get_settings
from core.db_base import Base
from typing import Generator
import os

settings = get_settings()

# Always define the engine and SessionLocal, using test DB if in test mode
if os.environ.get("PYTEST_CURRENT_TEST"):
    # Use test database URL
    SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///file::memory:?cache=shared")
    print(f"[DEBUG] TEST DB URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"[DEBUG] ENV: {dict(os.environ)}")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Instanciation standard
    SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
    print(f"[DEBUG] PROD/DEV DB URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"[DEBUG] ENV: {dict(os.environ)}")
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False, "uri": True} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
