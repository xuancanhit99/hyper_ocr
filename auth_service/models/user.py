# user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    russian_level = Column(String, nullable=True)
    gemini_api_key = Column(String, nullable=True)

    # Exam time fields
    time_start = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True, default=3600)  # Default: 60 minutes (in seconds)
    time_end = Column(DateTime(timezone=True), nullable=True)

