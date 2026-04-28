"""Story API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.job import RenderJob
from app.models.scene import Scene
from app.models.story import Story
from app.schemas.job import RenderJobResponse
from app.schemas.scene import SceneResponse
from app.schemas.story import StoryCreate, StoryResponse, StoryUpdate, StoryWithProgress
from app.tasks.story_tasks import process_story

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("", response_model=StoryWithProgress, status_code=status.HTTP_201_CREATED)
def create_story(data: StoryCreate, db: Session = Depends(get_db)) -> Story:
    story = Story(**data.model_dump())
    story.status = "draft"
    db.add(story)
    db.commit()
    db.refresh(story)

    # Kick off Celery task
    job = RenderJob(story_id=story.id, status="queued")
    db.add(job)
    db.commit()

    process_story.delay(story.id)

    # Return enriched response
    return _enrich_story(story, job)


@router.get("", response_model=list[StoryWithProgress])
def list_stories(db: Session = Depends(get_db)) -> list[Story]:
    stories = db.query(Story).order_by(Story.created_at.desc()).all()
    result = []
    for story in stories:
        job = (
            db.query(RenderJob)
            .filter(RenderJob.story_id == story.id)
            .order_by(RenderJob.created_at.desc())
            .first()
        )
        result.append(_enrich_story(story, job))
    return result


@router.get("/{story_id}", response_model=StoryWithProgress)
def get_story(story_id: str, db: Session = Depends(get_db)) -> Story:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    job = (
        db.query(RenderJob)
        .filter(RenderJob.story_id == story_id)
        .order_by(RenderJob.created_at.desc())
        .first()
    )
    return _enrich_story(story, job)


@router.patch("/{story_id}", response_model=StoryResponse)
def update_story(story_id: str, data: StoryUpdate, db: Session = Depends(get_db)) -> Story:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(story, field, value)

    db.commit()
    db.refresh(story)
    return story


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_story(story_id: str, db: Session = Depends(get_db)) -> None:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    db.delete(story)
    db.commit()


@router.get("/{story_id}/scenes", response_model=list[SceneResponse])
def get_story_scenes(story_id: str, db: Session = Depends(get_db)) -> list[Scene]:
    scenes = (
        db.query(Scene)
        .filter(Scene.story_id == story_id)
        .order_by(Scene.sequence_number)
        .all()
    )
    return scenes


@router.post("/{story_id}/render", response_model=RenderJobResponse)
def trigger_render(story_id: str, db: Session = Depends(get_db)) -> RenderJob:
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    job = RenderJob(story_id=story_id, status="queued")
    db.add(job)
    db.commit()
    db.refresh(job)

    process_story.delay(story_id)
    return job


def _enrich_story(story: Story, job: RenderJob | None) -> Story:
    """Attach progress info to story response."""
    story.progress_percent = job.progress_percent if job else 0
    story.current_stage = job.current_stage if job else None
    story.latest_job_id = job.id if job else None
    return story
