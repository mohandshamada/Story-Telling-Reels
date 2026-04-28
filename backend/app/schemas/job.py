"""Pydantic schemas for RenderJob."""

from datetime import datetime
from pydantic import BaseModel


class RenderJobBase(BaseModel):
    status: str = "queued"
    progress_percent: int = 0
    current_stage: str | None = None
    scenes_total: int = 0
    scenes_completed: int = 0
    output_url: str | None = None
    output_format: str = "mp4"
    resolution: str = "1080x1920"
    file_size_mb: float | None = None
    error_message: str | None = None


class RenderJobResponse(RenderJobBase):
    id: str
    story_id: str
    created_at: datetime
    completed_at: datetime | None = None
    worker_id: str | None = None

    model_config = {"from_attributes": True}


class RenderJobCreate(BaseModel):
    story_id: str
