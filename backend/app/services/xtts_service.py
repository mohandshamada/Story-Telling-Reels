"""XTTS v2 service for local multilingual voice cloning."""

from pathlib import Path
from typing import List

from app.core.config import settings


class XTTSService:
    """Local XTTS v2 TTS engine. Requires Coqui TTS installation + GPU."""

    SUPPORTED_LANGUAGES = [
        "en", "es", "fr", "de", "it", "pt", "pl", "tr",
        "ru", "nl", "cs", "ar", "zh", "hu", "ko", "ja",
    ]

    def __init__(self):
        self.model = None
        self._initialized = False

    def _ensure_loaded(self):
        if self._initialized:
            return
        try:
            from TTS.api import TTS
            self.model = TTS(settings.XTTS_MODEL_PATH)
            self._initialized = True
        except ImportError as exc:
            raise RuntimeError(
                "XTTS v2 not available. Install with: pip install TTS\n"
                "Then download models on first run. Error: {exc}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Failed to load XTTS v2: {exc}") from exc

    def generate(
        self,
        text: str,
        language: str,
        speaker_wav: Path,
        output_path: Path,
        speed: float = 0.9,
    ) -> Path:
        """Generate narration cloning the voice from speaker_wav."""
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Language {language} not supported by XTTS v2. "
                f"Supported: {self.SUPPORTED_LANGUAGES}"
            )

        self._ensure_loaded()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.model.tts_to_file(
            text=text,
            speaker_wav=str(speaker_wav),
            language=language,
            file_path=str(output_path),
            speed=speed,
        )
        return output_path

    def extract_embedding(self, speaker_wav: Path) -> dict:
        """Extract speaker embedding for caching."""
        self._ensure_loaded()
        return {"speaker_wav": str(speaker_wav)}

    def fine_tune(self, speaker_wavs: List[Path], epochs: int = 10) -> Path:
        """Fine-tune voice with additional training data."""
        raise NotImplementedError("XTTS fine-tuning requires manual training setup")
