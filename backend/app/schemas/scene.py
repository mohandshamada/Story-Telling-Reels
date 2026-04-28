"""Pydantic schemas for Scene."""

from datetime import datetime
from pydantic import BaseModel


class SceneBase(BaseModel):
    sequence_number: int
    narration_text: str | None = None
    visual_prompt: str | None = None
    animation_type: str = "ken_burns_slow_zoom"
    duration_seconds: float | None = None
    subtitle_text: str | None = None
    subtitle_style: dict | None = None
    sfx_triggers: list | None = None


class SceneCreate(SceneBase):
    pass


class SceneUpdate(BaseModel):
    narration_text: str | None = None
    visual_prompt: str | None = None
    animation_type: str | None = None
    duration_seconds: float | None = None
    subtitle_text: str | None = None
    subtitle_style: dict | None = None


class SceneResponse(SceneBase):
    id: str
    story_id: str
    narration_audio_url: str | None = None
    image_url: str | None = None
    animation_video_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
