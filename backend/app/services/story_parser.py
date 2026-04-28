"""LLM-based story parser with multi-provider support (OpenAI, Ollama, LiteLLM, Hybrid)."""

import json
import logging
import re
from typing import List

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.arabic_utils import prepare_for_tts, estimate_duration

logger = logging.getLogger(__name__)

# Optional litellm import — graceful fallback if not installed
try:
    import litellm
    litellm.suppress_debug_info = True
    _LITELLM_AVAILABLE = True
except Exception:
    _LITELLM_AVAILABLE = False


class SceneData(BaseModel):
    sequence: int
    narration: str = Field(..., description="Simplified narration for kids, max 2 sentences")
    visual_prompt: str = Field(..., description="Detailed image generation prompt")
    duration: float = Field(..., ge=3.0, le=15.0, description="Scene duration in seconds")
    sfx: List[str] = Field(default_factory=list, description="Sound effect keywords")


class StoryParser:
    def __init__(self, provider: str | None = None):
        self.provider = (provider or settings.LLM_PROVIDER).lower().strip()
        self.client = httpx.AsyncClient(timeout=60.0)

    # ------------------------------------------------------------------
    # Prompt construction (provider-agnostic)
    # ------------------------------------------------------------------
    def _build_prompts(self, story_text: str, target_scenes: int, language: str) -> tuple[str, str]:
        system = (
            f"You are a children's story editor. Break the following story into {target_scenes} "
            f"short scenes suitable for a 30-60 second video reel for kids aged 3-7.\n\n"
            f"Language: {language}\n\n"
            "For each scene, provide ONLY these fields in valid JSON array format:\n"
            "- sequence: integer starting at 1\n"
            "- narration: Simplified text for kids (max 2 short sentences, easy words, friendly tone)\n"
            "- visual_prompt: Detailed description for AI image generation. Start with art style:\n"
            '  "Watercolor children\'s book illustration, soft pastel colors, rounded friendly shapes, '
            'gentle lighting, no scary elements, Studio Ghibli inspired." Then describe the scene.\n'
            "- duration: Estimated seconds (4-12s per scene)\n"
            "- sfx: List of 1-3 simple sound effect keywords (e.g. ['bird_chirp', 'wind'])\n\n"
            "Rules:\n"
            "- Keep narration VERY simple for young children\n"
            "- Each scene should show ONE clear visual moment\n"
            "- Visual prompts must be kid-safe: no weapons, no blood, no frightening creatures\n"
            "- Characters should be cute, friendly, and expressive\n"
            "- Output ONLY the JSON array, no markdown, no explanation"
        )
        return system, story_text[:4000]

    # ------------------------------------------------------------------
    # Provider dispatch
    # ------------------------------------------------------------------
    async def _generate_completion(self, system: str, user: str) -> str:
        if self.provider == "ollama":
            return await self._generate_ollama(system, user)
        if self.provider == "litellm":
            return await self._generate_litellm(system, user)
        return await self._generate_openai(system, user)

    async def _generate_openai(self, system: str, user: str) -> str:
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _generate_ollama(self, system: str, user: str) -> str:
        response = await self.client.post(
            f"{settings.OLLAMA_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "model": settings.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"temperature": 0.7},
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]

    async def _generate_litellm(self, system: str, user: str) -> str:
        if not _LITELLM_AVAILABLE:
            raise RuntimeError("LiteLLM is not installed. Run: pip install litellm")

        kwargs = {
            "model": settings.LITELLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        if settings.LITELLM_API_KEY:
            kwargs["api_key"] = settings.LITELLM_API_KEY
        if settings.LITELLM_BASE_URL:
            kwargs["api_base"] = settings.LITELLM_BASE_URL

        response = litellm.completion(**kwargs)
        return response.choices[0].message.content

    # ------------------------------------------------------------------
    # Hybrid fallback
    # ------------------------------------------------------------------
    async def _generate_hybrid(self, system: str, user: str) -> str:
        priority = [p.strip() for p in settings.HYBRID_LLM_PRIORITY.split(",") if p.strip()]
        last_exc = None
        for prov in priority:
            try:
                if prov == "ollama":
                    return await self._generate_ollama(system, user)
                if prov == "litellm":
                    return await self._generate_litellm(system, user)
                if prov == "openai":
                    return await self._generate_openai(system, user)
            except Exception as exc:
                logger.warning("Hybrid LLM fallback: %s failed (%s)", prov, exc)
                last_exc = exc
                continue
        raise RuntimeError(f"All hybrid LLM providers failed. Last error: {last_exc}")

    # ------------------------------------------------------------------
    # Main parse entrypoint
    # ------------------------------------------------------------------
    async def parse(self, story_text: str, target_scenes: int = 5, language: str = "en") -> List[SceneData]:
        system_prompt, user_prompt = self._build_prompts(story_text, target_scenes, language)

        for attempt in range(3):
            try:
                if self.provider == "hybrid":
                    content = await self._generate_hybrid(system_prompt, user_prompt)
                else:
                    content = await self._generate_completion(system_prompt, user_prompt)
                return self._parse_json(content, language=language)
            except Exception as exc:
                logger.warning("Story parse attempt %d failed: %s", attempt + 1, exc)
                if attempt == 2:
                    raise RuntimeError(f"Failed to parse story after 3 attempts: {exc}")
                # Small delay before retry
                await self.client.get("https://api.openai.com/v1/models", timeout=5.0)

        return []

    # ------------------------------------------------------------------
    # JSON extraction & validation
    # ------------------------------------------------------------------
    def _parse_json(self, content: str, language: str = "en") -> List[SceneData]:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            content = match.group(0)

        raw = json.loads(content)
        scenes = []
        for idx, item in enumerate(raw):
            narration = item["narration"]
            if language == "ar":
                narration = prepare_for_tts(narration)

            duration = float(item.get("duration", 5.0))
            if language == "ar":
                duration = max(duration, estimate_duration(narration, "ar"))

            scene = SceneData(
                sequence=item.get("sequence", idx + 1),
                narration=narration,
                visual_prompt=item["visual_prompt"],
                duration=duration,
                sfx=item.get("sfx", []),
            )
            scenes.append(scene)
        return scenes

    # ------------------------------------------------------------------
    # Prompt enhancer
    # ------------------------------------------------------------------
    def enhance_prompt(self, base_prompt: str, style: str | None) -> str:
        modifiers = {
            "watercolor_illustration": (
                "watercolor children's book illustration, soft pastel colors, "
                "rounded friendly shapes, gentle lighting, no scary elements"
            ),
            "3d_cartoon": (
                "3D Pixar-style animation render, cute rounded characters, "
                "bright cheerful colors, soft shadows, kid-friendly"
            ),
            "flat_vector": (
                "flat vector illustration, bold colors, simple shapes, "
                "Material Design style, kid-friendly, clean lines"
            ),
        }
        style_text = modifiers.get(style, modifiers["watercolor_illustration"])
        return f"{base_prompt}, {style_text}, 9:16 vertical composition, high detail, no text, no watermarks"
