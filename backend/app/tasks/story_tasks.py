"""Celery tasks for story processing pipeline."""

import asyncio
import json
from pathlib import Path

from celery import Celery
from sqlalchemy.orm import sessionmaker

from app.db.session import engine
from app.models.job import RenderJob
from app.models.scene import Scene
from app.models.story import Story
from app.services.asset_generator import AssetGenerator
from app.services.story_parser import StoryParser
from app.services.video_compiler import VideoCompiler
from app.core.config import settings

app = Celery("story_reels")
app.config_from_object("celeryconfig")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _notify(job_id: str, msg: dict):
    """Publish progress update to Redis pub/sub."""
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.publish(f"job:{job_id}", json.dumps(msg))
        r.close()
    except Exception:
        pass  # Don't let Redis failures break the pipeline


def _get_event_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


def _run(coro):
    loop = _get_event_loop()
    return loop.run_until_complete(coro)


@app.task(bind=True, max_retries=3)
def process_story(self, story_id: str) -> dict:
    """End-to-end story processing: parse -> generate assets -> compile video."""
    db = SessionLocal()
    job = None
    try:
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise ValueError(f"Story {story_id} not found")

        job = db.query(RenderJob).filter(RenderJob.story_id == story_id).first()
        if not job:
            job = RenderJob(story_id=story_id, status="queued")
            db.add(job)
            db.commit()

        def notify(status: str, stage: str, percent: int, extra: dict | None = None):
            job.update_status(status, current_stage=stage, progress_percent=percent)
            db.commit()
            msg = {"type": "status", "status": status, "stage": stage, "percent": percent}
            if extra:
                msg.update(extra)
            _notify(job.id, msg)

        # ------------------------------------------------------------------
        # Stage 1: Parse story into scenes
        # ------------------------------------------------------------------
        notify("processing", "parsing", 5)

        parser = StoryParser()
        target_scenes = max(3, min(7, story.target_duration // 8))
        scenes_data = _run(parser.parse(story.content, target_scenes=target_scenes, language=story.language))

        # Delete old scenes
        db.query(Scene).filter(Scene.story_id == story_id).delete()
        db.commit()

        scenes = []
        for idx, sd in enumerate(scenes_data):
            scene = Scene(
                story_id=story_id,
                sequence_number=sd.sequence,
                narration_text=sd.narration,
                visual_prompt=parser.enhance_prompt(sd.visual_prompt, story.visual_theme),
                animation_type="ken_burns_slow_zoom",
                duration_seconds=sd.duration,
                subtitle_text=sd.narration,
                sfx_triggers=[{"sfx": s} for s in sd.sfx],
            )
            scenes.append(scene)
            db.add(scene)

        job.scenes_total = len(scenes)
        db.commit()

        # ------------------------------------------------------------------
        # Stage 2: Generate assets
        # ------------------------------------------------------------------
        generator = AssetGenerator()

        for i, scene in enumerate(scenes):
            notify(
                "processing",
                f"generating scene {i + 1}/{len(scenes)}",
                int(10 + (i / len(scenes)) * 60),
            )

            # Generate narration audio
            audio_path = _run(
                generator.generate_narration(
                    scene.narration_text or "",
                    output_filename=f"{story_id}_scene_{scene.sequence_number}",
                    language=story.language,
                )
            )
            scene.narration_audio_url = generator.get_local_url(audio_path)
            _notify(job.id, {
                "type": "scene",
                "scene_id": scene.id,
                "kind": "audio",
                "sequence": scene.sequence_number,
                "url": scene.narration_audio_url,
            })

            # Generate image
            image_path = _run(
                generator.generate_image(
                    scene.visual_prompt or "cute cartoon characters in a friendly scene",
                    output_filename=f"{story_id}_scene_{scene.sequence_number}",
                )
            )

            # If using ComfyUI with IP-Adapter, use first scene's image as reference for consistency
            if settings.IMAGE_PROVIDER == "comfyui" and i > 0:
                ref_image = generator.storage_path / "images" / f"{story_id}_scene_1.png"
                if ref_image.exists():
                    image_path = _run(
                        generator.generate_image(
                            scene.visual_prompt or "cute cartoon characters in a friendly scene",
                            output_filename=f"{story_id}_scene_{scene.sequence_number}",
                            reference_image=ref_image,
                        )
                    )
            scene.image_url = generator.get_local_url(image_path)
            _notify(job.id, {
                "type": "scene",
                "scene_id": scene.id,
                "kind": "image",
                "sequence": scene.sequence_number,
                "url": scene.image_url,
            })

            job.increment_completed()
            db.commit()

        # ------------------------------------------------------------------
        # Stage 3: Compile video
        # ------------------------------------------------------------------
        notify("rendering", "video_compilation", 80)

        compiler = VideoCompiler()
        scene_clips = []
        for scene in scenes:
            audio_path = generator.storage_path / "audio" / f"{story_id}_scene_{scene.sequence_number}.mp3"
            image_path = generator.storage_path / "images" / f"{story_id}_scene_{scene.sequence_number}.png"

            # Collect SFX paths
            sfx_list = []
            if scene.sfx_triggers:
                for trigger in scene.sfx_triggers:
                    sfx_name = trigger.get("sfx") if isinstance(trigger, dict) else trigger
                    if sfx_name:
                        sfx_path = generator.get_sfx_path(sfx_name)
                        if sfx_path.exists():
                            sfx_list.append({"path": sfx_path, "time_offset": trigger.get("time_offset", 0.0)})

            # Get music for mood
            music_path = generator.get_music_path(story.music_mood or "gentle_playful", story.target_duration)

            clip = compiler.compile_scene(
                image_path=image_path,
                audio_path=audio_path,
                narration_text=scene.subtitle_text or "",
                duration=scene.duration_seconds,
                music_path=music_path if music_path.exists() else None,
                sfx_list=sfx_list,
            )
            scene_clips.append(clip)

        output_dir = generator.storage_path / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{story_id}.mp4"

        compiler.render_final(
            scenes=scene_clips,
            output_path=output_path,
            title=story.title,
            moral=story.moral_lesson or "",
        )

        job.update_status(
            "completed",
            current_stage="done",
            progress_percent=100,
            output_url=generator.get_local_url(output_path),
        )
        story.status = "completed"
        db.commit()

        _notify(job.id, {
            "type": "complete",
            "download_url": job.output_url,
        })

        return {
            "story_id": story_id,
            "job_id": job.id,
            "download_url": job.output_url,
        }

    except Exception as exc:
        if job:
            job.update_status("failed", error_message=str(exc))
            db.commit()
            _notify(job.id, {"type": "error", "message": str(exc)})
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()
