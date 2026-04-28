"""Job API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.job import RenderJob
from app.schemas.job import RenderJobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=RenderJobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> RenderJob:
    job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/download")
def download_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(RenderJob).filter(RenderJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Job not yet completed")
    if not job.output_url:
        raise HTTPException(status_code=404, detail="Output not available")

    from fastapi.responses import FileResponse

    # Local file serving
    from app.core.config import settings
    from pathlib import Path

    rel = job.output_url.replace("/storage/", "")
    file_path = Path(settings.STORAGE_LOCAL_PATH) / rel

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=f"reel_{job.story_id}.mp4",
    )
