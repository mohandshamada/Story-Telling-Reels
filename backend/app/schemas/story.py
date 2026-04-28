"""Pydantic schemas for Story."""

from datetime import datetime
from pydantic import BaseModel, Field


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    source: str | None = None
    language: str = "en"
    content: str = Field(..., min_length=10)
    target_duration: int = 45
    target_audience: str | None = "3-7 years"
    visual_theme: str = "watercolor_illustration"
    voice_style: str = "warm_female_storyteller"
    music_mood: str = "gentle_playful"
    moral_lesson: str | None = None


class StoryCreate(StoryBase):
    pass


class StoryUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    target_duration: int | None = None
    visual_theme: str | None = None
    voice_style: str | None = None
    music_mood: str | None = None
    moral_lesson: str | None = None


class StoryResponse(StoryBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryWithProgress(StoryResponse):
    progress_percent: int = 0
    current_stage: str | None = None
    latest_job_id: str | None = None
