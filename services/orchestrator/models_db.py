from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import uuid
from db import Base

def uuid4():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    locale: Mapped[str | None] = mapped_column(String, nullable=True)

    totals = relationship("Totals", back_populates="user", uselist=False)

class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))
    problem_text: Mapped[str] = mapped_column(String)
    emotion_tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    last_stage: Mapped[str | None] = mapped_column(String, nullable=True)

class Story(Base):
    __tablename__ = "stories"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sessions.id"))
    story_json: Mapped[dict] = mapped_column(JSON)
    citations_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"))
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("sessions.id"))
    persona: Mapped[str] = mapped_column(String)
    turns: Mapped[list[dict]] = mapped_column(JSON)  # [{role, text, ts}]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("now()"))

class Totals(Base):
    __tablename__ = "totals"
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id"), primary_key=True)
    karmic_points: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_active: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="totals")
