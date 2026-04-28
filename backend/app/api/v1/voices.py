"""Voice profile API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.voice_profile import VoiceProfile
from app.schemas.voice import VoiceProfileCreate, VoiceProfileResponse

router = APIRouter(prefix="/voice-profiles", tags=["voice-profiles"])


@router.post("", response_model=VoiceProfileResponse, status_code=status.HTTP_201_CREATED)
def create_voice_profile(
    data: VoiceProfileCreate,
    db: Session = Depends(get_db),
) -> VoiceProfile:
    profile = VoiceProfile(**data.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=list[VoiceProfileResponse])
def list_voice_profiles(db: Session = Depends(get_db)) -> list[VoiceProfile]:
    return db.query(VoiceProfile).all()


@router.get("/{profile_id}", response_model=VoiceProfileResponse)
def get_voice_profile(profile_id: str, db: Session = Depends(get_db)) -> VoiceProfile:
    profile = db.query(VoiceProfile).filter(VoiceProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Voice profile not found")
    return profile
