"""Social media upload service."""

from pathlib import Path
from typing import Optional

import httpx

from app.core.config import settings


class SocialUploader:
    """Upload reels to social platforms."""

    PLATFORMS = ["instagram", "tiktok", "youtube", "twitter"]

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)

    async def upload(
        self,
        platform: str,
        video_path: Path,
        title: str,
        description: str,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """Upload video to a social platform."""
        if platform not in self.PLATFORMS:
            raise ValueError(f"Platform {platform} not supported. Use: {self.PLATFORMS}")

        # Each platform requires its own OAuth flow and API
        handlers = {
            "youtube": self._upload_youtube,
            "instagram": self._upload_instagram,
            "tiktok": self._upload_tiktok,
            "twitter": self._upload_twitter,
        }

        handler = handlers[platform]
        return await handler(video_path, title, description, tags or [])

    async def _upload_youtube(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
    ) -> dict:
        """Upload to YouTube via Data API (requires OAuth2)."""
        # Placeholder: requires google-api-python-client + OAuth credentials
        return {
            "platform": "youtube",
            "status": "requires_oauth",
            "message": "YouTube upload requires OAuth2 setup. Configure YOUTUBE_CLIENT_* env vars.",
        }

    async def _upload_instagram(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
    ) -> dict:
        """Upload to Instagram via Graph API (requires Business/Creator account)."""
        return {
            "platform": "instagram",
            "status": "requires_oauth",
            "message": "Instagram upload requires Facebook Graph API token. Configure INSTAGRAM_ACCESS_TOKEN env var.",
        }

    async def _upload_tiktok(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
    ) -> dict:
        """Upload to TikTok via Research API or unofficial endpoints."""
        return {
            "platform": "tiktok",
            "status": "requires_api_key",
            "message": "TikTok upload requires official API access. Configure TIKTOK_ACCESS_TOKEN env var.",
        }

    async def _upload_twitter(
        self,
        video_path: Path,
        title: str,
        description: str,
        tags: list[str],
    ) -> dict:
        """Upload to Twitter/X via v2 API."""
        return {
            "platform": "twitter",
            "status": "requires_oauth",
            "message": "Twitter upload requires OAuth 1.0a or 2.0. Configure TWITTER_API_* env vars.",
        }
