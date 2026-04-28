"""Pydantic schemas for VoiceProfile."""

from pydantic import BaseModel


class VoiceProfileCreate(BaseModel):
    name: str
    description: str | None = None
    tts_engine: str = "elevenlabs"
    supported_languages: list[str] | None = None


class VoiceProfileResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    tts_engine: str
    supported_languages: list | None = None
    fine_tuned: bool
    created_at: str

    model_config = {"from_attributes": True}


class GenerateNarrationRequest(BaseModel):
    text: str
    language: str
    voice_profile_id: str
