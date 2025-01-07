from datetime import datetime
from enum import Enum
from uuid import uuid4

import numpy as np
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Enum as DbEnum, LargeBinary, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import Config

# Create engine and Base for standalone use
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
Base = declarative_base()


# Session factory for standalone scripts (outside of Flask)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Helper function for UUID primary keys
def string_uuid() -> str:
    return str(uuid4())

# Enums for Event Types and User Roles
class EventType(str, Enum):
    STUDENT_ENTRANCE = "STUDENT_ENTRANCE"
    STUDENT_EXIT = "STUDENT_EXIT"
    FIGHTING = "FIGHTING"
    SMOKING = "SMOKING"
    WEAPON = "WEAPON"
    LYING_MAN = "LYING_MAN"

class UserRole(str, Enum):
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    STAFF = "STAFF"
    ADMIN = "ADMIN"

# Base model class for timestamps
class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

# Organization Table
class Organization(Base):
    __tablename__ = "organization"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    org_name = Column(String, unique=True, nullable=False)


# User Account Table
class UserAccount(Base):
    __tablename__ = "account"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    organization_id = Column(String, ForeignKey("organization.id"))
    user_name = Column(String, nullable=False)
    user_role = Column(DbEnum(UserRole), nullable=False)
    user_login = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)


# Face Encoding Table
class FaceEncoding(Base):
    __tablename__ = "face_encoding"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    face_encoding = Column(LargeBinary, nullable=False)
    user_id = Column(String, ForeignKey("account.id"))

    @property
    def embedding(self) -> np.ndarray:
        return np.frombuffer(self.face_encoding, dtype=np.float64)


# Subscription Table
class Subscription(Base):
    __tablename__ = "subscription"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    organization_id = Column(String, ForeignKey("organization.id"))
    telegram_chat_id = Column(Integer, nullable=False)
    event_type = Column(DbEnum(EventType), nullable=False)
    student_id = Column(String, ForeignKey("account.id"), nullable=True, default=None)


# Event Table
class Event(Base):
    __tablename__ = "event"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    event_type = Column(DbEnum(EventType), nullable=False)
    organization_id = Column(String, ForeignKey("organization.id"), nullable=True, default=None)
    timestamp = Column(DateTime, nullable=True, default=None)
    student_id = Column(String, ForeignKey("account.id"), nullable=True, default=None)
    camera_id = Column(String, nullable=True, default=None)


# Schedule Table
class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(String, primary_key=True, default=lambda: string_uuid())
    organization_id = Column(String, ForeignKey("organization.id"))
    start_time = Column(DateTime, nullable=True, default=None)
    end_time = Column(DateTime, nullable=True, default=None)


# Create all tables in the database
Base.metadata.create_all(engine)
