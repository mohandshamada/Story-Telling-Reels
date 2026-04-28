"""Scene API endpoints (editor + regeneration)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.scene import Scene
from app.schemas.scene import SceneResponse, SceneUpdate
from app.services.asset_generator import AssetGenerator
from app.services.story_parser import StoryParser

router = APIRouter(prefix="/scenes", tags=["scenes"])


@router.patch("/{scene_id}", response_model=SceneResponse)
def update_scene(
    scene_id: str,
    data: SceneUpdate,
    db: Session = Depends(get_db),
) -> Scene:
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(scene, field, value)

    db.commit()
    db.refresh(scene)
    return scene


@router.post("/{scene_id}/regenerate-image")
def regenerate_image(scene_id: str, db: Session = Depends(get_db)) -> dict:
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    import asyncio

    generator = AssetGenerator()
    parser = StoryParser()
    prompt = parser.enhance_prompt(
        scene.visual_prompt or "cute cartoon characters in a friendly scene",
        None,
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        path = loop.run_until_complete(
            generator.generate_image(
                prompt,
                output_filename=f"{scene.story_id}_scene_{scene.sequence_number}_regen",
            )
        )
    finally:
        loop.close()

    scene.image_url = generator.get_local_url(path)
    db.commit()
    db.refresh(scene)
    return {"image_url": scene.image_url}


@router.post("/{scene_id}/regenerate-audio")
def regenerate_audio(scene_id: str, db: Session = Depends(get_db)) -> dict:
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    import asyncio

    generator = AssetGenerator()
    text = scene.narration_text or ""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        path = loop.run_until_complete(
            generator.generate_narration(
                text,
                output_filename=f"{scene.story_id}_scene_{scene.sequence_number}_regen",
            )
        )
    finally:
        loop.close()

    scene.narration_audio_url = generator.get_local_url(path)
    db.commit()
    db.refresh(scene)
    return {"audio_url": scene.narration_audio_url}
