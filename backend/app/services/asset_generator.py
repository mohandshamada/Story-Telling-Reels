"""TTS and image generation services with cloud/local provider switching."""

import hashlib
import os
from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings
from app.services.comfyui_client import ComfyUIClient
from app.services.xtts_service import XTTSService


class AssetGenerator:
    def __init__(self):
        self.storage_path = Path(settings.STORAGE_LOCAL_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.client = httpx.AsyncClient(timeout=120.0)

        # Lazy-load local providers
        self._comfyui: Optional[ComfyUIClient] = None
        self._xtts: Optional[XTTSService] = None

    def _comfyui_client(self) -> ComfyUIClient:
        if self._comfyui is None:
            self._comfyui = ComfyUIClient()
        return self._comfyui

    def _xtts_service(self) -> XTTSService:
        if self._xtts is None:
            self._xtts = XTTSService()
        return self._xtts

    def _asset_path(self, prefix: str, key: str, ext: str) -> Path:
        """Generate a deterministic local path for an asset."""
        subdir = self.storage_path / prefix
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f"{key}{ext}"

    # ------------------------------------------------------------------
    # Image Generation (provider switch)
    # ------------------------------------------------------------------
    async def generate_image(
        self,
        prompt: str,
        output_filename: str | None = None,
        reference_image: Path | None = None,
    ) -> Path:
        """Generate image using configured provider."""
        if settings.IMAGE_PROVIDER == "comfyui":
            return await self._generate_image_comfyui(prompt, output_filename, reference_image)
        return await self._generate_image_dalle(prompt, output_filename)

    async def _generate_image_dalle(
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

    async def _generate_image_comfyui(
        self,
        prompt: str,
        output_filename: str | None = None,
        reference_image: Path | None = None,
    ) -> Path:
        """Generate image using local ComfyUI."""
        key = output_filename or hashlib.sha256(prompt.encode()).hexdigest()[:16]
        out_path = self._asset_path("images", key, ".png")

        if out_path.exists():
            return out_path

        comfy = self._comfyui_client()

        if reference_image and reference_image.exists():
            result_path = await comfy.generate_image_ipadapter(
                prompt=prompt,
                reference_image=reference_image,
                width=settings.COMFYUI_WIDTH,
                height=settings.COMFYUI_HEIGHT,
            )
        else:
            result_path = await comfy.generate_image(
                prompt=prompt,
                width=settings.COMFYUI_WIDTH,
                height=settings.COMFYUI_HEIGHT,
            )

        # Copy result to our storage path if different
        if result_path != out_path:
            import shutil
            shutil.copy2(result_path, out_path)
        return out_path

    # ------------------------------------------------------------------
    # TTS (provider switch)
    # ------------------------------------------------------------------
    async def generate_narration(
        self,
        text: str,
        voice_id: str | None = None,
        output_filename: str | None = None,
        language: str = "en",
    ) -> Path:
        """Generate TTS using configured provider."""
        if settings.TTS_PROVIDER == "xtts":
            return await self._generate_narration_xtts(text, output_filename, language)
        return await self._generate_narration_elevenlabs(text, voice_id, output_filename)

    async def _generate_narration_elevenlabs(
        self,
        text: str,
        voice_id: str | None = None,
        output_filename: str | None = None,
    ) -> Path:
        """Generate TTS using ElevenLabs API."""
        vid = voice_id or settings.ELEVENLABS_VOICE_ID
        key = output_filename or hashlib.sha256(f"{vid}:{text}".encode()).hexdigest()[:16]
        out_path = self._asset_path("audio", key, ".mp3")

        if out_path.exists():
            return out_path

        if not settings.ELEVENLABS_API_KEY:
            out_path.touch()
            return out_path

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
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

    async def _generate_narration_xtts(
        self,
        text: str,
        output_filename: str | None = None,
        language: str = "en",
    ) -> Path:
        """Generate TTS using local XTTS v2."""
        key = output_filename or hashlib.sha256(f"xtts:{language}:{text}".encode()).hexdigest()[:16]
        out_path = self._asset_path("audio", key, ".wav")

        if out_path.exists():
            return out_path

        speaker_wav = Path(settings.XTTS_DEFAULT_SPEAKER_WAV) if settings.XTTS_DEFAULT_SPEAKER_WAV else None
        if not speaker_wav or not speaker_wav.exists():
            # Fallback to first available voice sample in storage
            voices_dir = self.storage_path / "voices"
            if voices_dir.exists():
                samples = list(voices_dir.glob("*.wav")) + list(voices_dir.glob("*.mp3"))
                if samples:
                    speaker_wav = samples[0]

        if not speaker_wav or not speaker_wav.exists():
            raise FileNotFoundError(
                "No speaker reference voice found for XTTS. "
                "Set XTTS_DEFAULT_SPEAKER_WAV or place a .wav in storage/voices/"
            )

        xtts = self._xtts_service()
        return xtts.generate(
            text=text,
            language=language,
            speaker_wav=speaker_wav,
            output_path=out_path,
            speed=settings.XTTS_SPEED,
        )

    # ------------------------------------------------------------------
    # Music & SFX
    # ------------------------------------------------------------------
    def get_music_path(self, mood: str, duration: float) -> Path:
        """Return path to background music file for a given mood."""
        music_dir = self.storage_path / "music"
        music_dir.mkdir(parents=True, exist_ok=True)
        for ext in (".mp3", ".wav"):
            path = music_dir / f"{mood}{ext}"
            if path.exists():
                return path
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
