"""RenderJob SQLAlchemy model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.story import Story


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class RenderJob(Base):
    __tablename__ = "render_jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    story_id: Mapped[str] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="queued")
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    current_stage: Mapped[str | None] = mapped_column(String(100))
    scenes_total: Mapped[int] = mapped_column(Integer, default=0)
    scenes_completed: Mapped[int] = mapped_column(Integer, default=0)
    output_url: Mapped[str | None] = mapped_column(Text)
    output_format: Mapped[str] = mapped_column(String(20), default="mp4")
    resolution: Mapped[str] = mapped_column(String(20), default="1080x1920")
    file_size_mb: Mapped[float | None] = mapped_column(Float)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=now_utc)
    completed_at: Mapped[datetime | None] = mapped_column()
    worker_id: Mapped[str | None] = mapped_column(String(100))

    story: Mapped["Story"] = relationship("Story", back_populates="jobs")

    def update_status(
        self,
        status: str,
        current_stage: str | None = None,
        progress_percent: int | None = None,
        output_url: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.status = status
        if current_stage is not None:
            self.current_stage = current_stage
        if progress_percent is not None:
            self.progress_percent = progress_percent
        if output_url is not None:
            self.output_url = output_url
        if error_message is not None:
            self.error_message = error_message
        if status in ("completed", "failed"):
            self.completed_at = datetime.now(timezone.utc)

    def increment_completed(self) -> None:
        self.scenes_completed += 1
        if self.scenes_total > 0:
            self.progress_percent = int((self.scenes_completed / self.scenes_total) * 100)
