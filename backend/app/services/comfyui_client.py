"""ComfyUI API client for local GPU image/video generation."""

import json
import uuid
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings


class ComfyUIClient:
    """Client for ComfyUI HTTP API."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.COMFYUI_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=300.0)

    async def generate_image(
        self,
        prompt: str,
        width: int = 576,
        height: int = 1024,
        seed: int | None = None,
        model: str = "sdxl_base",
    ) -> Path:
        """Generate image via ComfyUI workflow submission."""
        # Build a basic SDXL text-to-image workflow
        workflow = self._build_txt2img_workflow(prompt, width, height, seed, model)
        return await self._run_workflow(workflow, output_prefix="image")

    async def generate_image_ipadapter(
        self,
        prompt: str,
        reference_image: Path,
        width: int = 576,
        height: int = 1024,
        seed: int | None = None,
    ) -> Path:
        """Generate image with IP-Adapter for character consistency."""
        workflow = self._build_ipadapter_workflow(prompt, reference_image, width, height, seed)
        return await self._run_workflow(workflow, output_prefix="image_ipa")

    async def _run_workflow(self, workflow: dict, output_prefix: str) -> Path:
        """Submit workflow to ComfyUI and wait for result."""
        prompt_id = str(uuid.uuid4())
        res = await self.client.post("/prompt", json={"prompt": workflow})
        res.raise_for_status()
        data = res.json()
        prompt_id = data.get("prompt_id", prompt_id)

        # Poll for completion (simplified)
        # In production, use WebSocket or history endpoint
        import asyncio

        for _ in range(300):  # 5 min max
            await asyncio.sleep(1)
            history_res = await self.client.get(f"/history/{prompt_id}")
            if history_res.status_code == 200:
                history = history_res.json()
                if history.get(prompt_id, {}).get("outputs"):
                    break

        # Download output
        # This is simplified; real implementation parses workflow outputs
        output_dir = Path(settings.STORAGE_LOCAL_PATH) / "images"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{output_prefix}_{prompt_id}.png"
        return output_path

    def _build_txt2img_workflow(
        self,
        prompt: str,
        width: int,
        height: int,
        seed: int | None,
        model: str,
    ) -> dict:
        """Build a minimal ComfyUI text-to-image workflow dict."""
        seed = seed or 42
        return {
            "1": {
                "inputs": {"ckpt_name": f"{model}.safetensors"},
                "class_type": "CheckpointLoaderSimple",
            },
            "2": {
                "inputs": {"text": prompt, "clip": ["1", 0]},
                "class_type": "CLIPTextEncode",
            },
            "3": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1,
                },
                "class_type": "EmptyLatentImage",
            },
            "4": {
                "inputs": {
                    "seed": seed,
                    "steps": 25,
                    "cfg": 7.0,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["2", 0],
                    "latent_image": ["3", 0],
                },
                "class_type": "KSampler",
            },
            "5": {
                "inputs": {"samples": ["4", 0], "vae": ["1", 2]},
                "class_type": "VAEDecode",
            },
            "6": {
                "inputs": {"filename_prefix": "ComfyUI", "images": ["5", 0]},
                "class_type": "SaveImage",
            },
        }

    def _build_ipadapter_workflow(
        self,
        prompt: str,
        reference_image: Path,
        width: int,
        height: int,
        seed: int | None,
    ) -> dict:
        """Build ComfyUI workflow with IP-Adapter for character consistency."""
        # Simplified: real workflow would include IPAdapterApply + LoadImage nodes
        return self._build_txt2img_workflow(prompt, width, height, seed, "sdxl_base")
