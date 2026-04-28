"""Story SQLAlchemy model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.scene import Scene
    from app.models.job import RenderJob


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str | None] = mapped_column(String(100))
    language: Mapped[str] = mapped_column(String(10), default="en")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    target_duration: Mapped[int] = mapped_column(Integer, default=45)
    target_audience: Mapped[str | None] = mapped_column(String(50))
    visual_theme: Mapped[str | None] = mapped_column(String(100))
    voice_style: Mapped[str | None] = mapped_column(String(100))
    music_mood: Mapped[str | None] = mapped_column(String(100))
    llm_provider: Mapped[str | None] = mapped_column(String(50))
    moral_lesson: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(default=now_utc, onupdate=now_utc)

    scenes: Mapped[list["Scene"]] = relationship(
        "Scene", back_populates="story", cascade="all, delete-orphan", lazy="selectin"
    )
    jobs: Mapped[list["RenderJob"]] = relationship(
        "RenderJob", back_populates="story", cascade="all, delete-orphan", lazy="selectin"
    )
