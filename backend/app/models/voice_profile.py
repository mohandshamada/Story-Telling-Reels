"""VoiceProfile SQLAlchemy model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sample_audio_url: Mapped[str | None] = mapped_column(Text)
    speaker_embedding: Mapped[dict | None] = mapped_column(JSON)
    tts_engine: Mapped[str] = mapped_column(String(50), default="elevenlabs")
    fine_tuned: Mapped[bool] = mapped_column(Boolean, default=False)
    fine_tune_data_url: Mapped[str | None] = mapped_column(Text)
    supported_languages: Mapped[list | None] = mapped_column(JSON, default=list)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
