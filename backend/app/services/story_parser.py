"""LLM-based story parser."""

import json
import re
from typing import List

import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.arabic_utils import prepare_for_tts, estimate_duration


class SceneData(BaseModel):
    sequence: int
    narration: str = Field(..., description="Simplified narration for kids, max 2 sentences")
    visual_prompt: str = Field(..., description="Detailed image generation prompt")
    duration: float = Field(..., ge=3.0, le=15.0, description="Scene duration in seconds")
    sfx: List[str] = Field(default_factory=list, description="Sound effect keywords")


class StoryParser:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)

    async def parse(self, story_text: str, target_scenes: int = 5, language: str = "en") -> List[SceneData]:
        """Parse story into scenes using structured LLM output."""
        system_prompt = (
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

        for attempt in range(3):
            try:
                response = await self.client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": story_text[:4000]},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return self._parse_json(content)
            except Exception as exc:
                if attempt == 2:
                    raise RuntimeError(f"Failed to parse story after 3 attempts: {exc}")
                await self.client.get("https://api.openai.com/v1/models", timeout=5.0)

        return []

    def _parse_json(self, content: str) -> List[SceneData]:
        """Extract and validate JSON array from LLM output."""
        # Strip markdown fences
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Try to find JSON array
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if match:
            content = match.group(0)

        raw = json.loads(content)
        scenes = []
        for idx, item in enumerate(raw):
            narration = item["narration"]
            # Arabic preprocessing
            if language == "ar":
                narration = prepare_for_tts(narration)

            duration = float(item.get("duration", 5.0))
            # Refine duration estimate for Arabic
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

    def enhance_prompt(self, base_prompt: str, style: str | None) -> str:
        """Add consistent style modifiers."""
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
