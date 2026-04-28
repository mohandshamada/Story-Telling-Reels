"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "Story Reels"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"

    # Database (SQLite for local dev, PostgreSQL for production)
    DATABASE_URL: str = "sqlite:///./story_reels.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ElevenLabs
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "XB0fDUnXU5powFXDhCwa"  # default friendly voice

    # DALL-E
    DALLE_MODEL: str = "dall-e-3"
    DALLE_SIZE: str = "1024x1792"  # closest to 9:16

    # Storage
    STORAGE_PROVIDER: str = "local"  # local, s3, r2
    STORAGE_LOCAL_PATH: str = "./storage"
    S3_BUCKET: str = ""
    S3_ENDPOINT: str = ""
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""

    # Video
    VIDEO_RESOLUTION: str = "1080x1920"
    VIDEO_FPS: int = 30
    VIDEO_BITRATE: str = "8000k"
    SUBTITLE_FONT: str = "Nunito-Bold"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Local AI / GPU
    COMFYUI_URL: str = "http://localhost:8188"
    XTTS_ENABLED: bool = False
    COMFYUI_ENABLED: bool = False

    # Social Upload
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    TIKTOK_ACCESS_TOKEN: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""

    @property
    def video_width(self) -> int:
        return int(self.VIDEO_RESOLUTION.split("x")[0])

    @property
    def video_height(self) -> int:
        return int(self.VIDEO_RESOLUTION.split("x")[1])


settings = Settings()
