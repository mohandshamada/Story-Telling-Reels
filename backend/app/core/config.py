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

    # Database
    DATABASE_URL: str = "sqlite:///./story_reels.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Provider Selection
    IMAGE_PROVIDER: str = "dalle"  # dalle | comfyui
    TTS_PROVIDER: str = "elevenlabs"  # elevenlabs | xtts

    # OpenAI (cloud)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # DALL-E (cloud image gen)
    DALLE_MODEL: str = "dall-e-3"
    DALLE_SIZE: str = "1024x1792"

    # ElevenLabs (cloud TTS)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "XB0fDUnXU5powFXDhCwa"

    # ComfyUI (local GPU image gen)
    COMFYUI_URL: str = "http://localhost:8188"
    COMFYUI_WORKFLOW: str = "sdxl_base"  # sdxl_base | sdxl_ipadapter
    COMFYUI_WIDTH: int = 576
    COMFYUI_HEIGHT: int = 1024
    COMFYUI_STEPS: int = 25
    COMFYUI_CFG: float = 7.0

    # XTTS v2 (local GPU TTS)
    XTTS_MODEL_PATH: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    XTTS_DEFAULT_SPEAKER_WAV: str = ""  # path to default reference voice
    XTTS_SPEED: float = 0.9

    # Storage
    STORAGE_PROVIDER: str = "local"
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
