# Modèle User SQLAlchemy pour v1

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.db_base import Base
import datetime
from datetime import timezone

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(timezone.utc))
    role = Column(String, default="user", nullable=False)  # "user" ou "admin"
