"""TTS and image generation services."""

import hashlib
import os
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings


class AssetGenerator:
    def __init__(self):
        self.storage_path = Path(settings.STORAGE_LOCAL_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=120.0)

    def _asset_path(self, prefix: str, key: str, ext: str) -> Path:
        """Generate a deterministic local path for an asset."""
        subdir = self.storage_path / prefix
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f"{key}{ext}"

    # ------------------------------------------------------------------
    # TTS via ElevenLabs
    # ------------------------------------------------------------------
    async def generate_narration(
        self,
        text: str,
        voice_id: str | None = None,
        output_filename: str | None = None,
    ) -> Path:
        """Generate TTS audio using ElevenLabs API."""
        voice_id = voice_id or settings.ELEVENLABS_VOICE_ID
        key = output_filename or hashlib.sha256(f"{voice_id}:{text}".encode()).hexdigest()[:16]
        out_path = self._asset_path("audio", key, ".mp3")

        if out_path.exists():
            return out_path

        if not settings.ELEVENLABS_API_KEY:
            # Fallback: create a dummy file for dev without API key
            out_path.touch()
            return out_path

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True,
            },
        }

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        out_path.write_bytes(response.content)
        return out_path

    # ------------------------------------------------------------------
    # Image via DALL-E 3
    # ------------------------------------------------------------------
    async def generate_image(
        self,
        prompt: str,
        output_filename: str | None = None,
    ) -> Path:
        """Generate image using DALL-E 3."""
        key = output_filename or hashlib.sha256(prompt.encode()).hexdigest()[:16]
        out_path = self._asset_path("images", key, ".png")

        if out_path.exists():
            return out_path

        if not settings.OPENAI_API_KEY:
            out_path.touch()
            return out_path

        response = await self.client.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.DALLE_MODEL,
                "prompt": prompt,
                "n": 1,
                "size": settings.DALLE_SIZE,
                "response_format": "url",
            },
        )
        response.raise_for_status()
        data = response.json()
        image_url = data["data"][0]["url"]

        img_response = await self.client.get(image_url)
        img_response.raise_for_status()
        out_path.write_bytes(img_response.content)
        return out_path

    # ------------------------------------------------------------------
    # Music & SFX
    # ------------------------------------------------------------------
    def get_music_path(self, mood: str, duration: float) -> Path:
        """Return path to background music file for a given mood."""
        music_dir = self.storage_path / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        # Try exact mood match
        for ext in (".mp3", ".wav"):
            path = music_dir / f"{mood}{ext}"
            if path.exists():
                return path
        # Fallback to gentle_playful
        for ext in (".mp3", ".wav"):
            path = music_dir / f"gentle_playful{ext}"
            if path.exists():
                return path
        return music_dir / "gentle_playful.mp3"

    def get_sfx_path(self, sfx_name: str) -> Path:
        """Return path to a sound effect file."""
        sfx_dir = self.storage_path / "sfx"
        sfx_dir.mkdir(parents=True, exist_ok=True)
        for ext in (".mp3", ".wav"):
            path = sfx_dir / f"{sfx_name}{ext}"
            if path.exists():
                return path
        return sfx_dir / f"{sfx_name}.mp3"

    # ------------------------------------------------------------------
    # Local file helpers
    # ------------------------------------------------------------------
    def get_local_url(self, path: Path) -> str:
        """Convert local path to a relative URL path."""
        rel = path.relative_to(self.storage_path)
        return f"/storage/{rel.as_posix()}"

    def cleanup(self, path: Path) -> None:
        if path.exists():
            path.unlink()
