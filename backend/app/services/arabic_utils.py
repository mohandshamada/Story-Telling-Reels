"""Arabic text processing: normalization, diacritization, RTL helpers."""

import re
from typing import List

import arabic_reshaper
from bidi.algorithm import get_display


# Arabic diacritics range (tashkeel)
DIACRITICS = re.compile(r"[\u064B-\u065F\u0670\u0640]")

# Tatweel (kashida) — elongation character
TATWEEL = re.compile(r"\u0640")

# Alef variants to normalize
ALEF_VARIANTS = re.compile(r"[\u0622\u0623\u0625]")

# Arabic letters range
ARABIC_CHARS = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]")


def is_arabic(text: str) -> bool:
    """Check if text contains Arabic characters."""
    return bool(ARABIC_CHARS.search(text))


def normalize(text: str) -> str:
    """Normalize Arabic text for processing and TTS."""
    # Remove tatweel (kashida)
    text = TATWEEL.sub("", text)
    # Normalize alef variants to bare alef
    text = ALEF_VARIANTS.sub("\u0627", text)
    # Normalize hamza on line
    text = text.replace("\u0624", "\u0648")  # hamza on waw -> waw
    text = text.replace("\u0626", "\u064A")  # hamza on ya -> ya
    # Standardize spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def has_diacritics(text: str) -> bool:
    """Check if Arabic text already has tashkeel."""
    return bool(DIACRITICS.search(text))


def add_diacritics(text: str) -> str:
    """Add tashkeel (diacritics) to Arabic text for better TTS pronunciation.

    For MVP we use a lightweight heuristic approach. In production,
    replace with camel-tools Tashkeela or Farasa API.
    """
    if not is_arabic(text):
        return text
    if has_diacritics(text):
        return text

    # Heuristic: add fatha (َ) to consonants that don't already have diacritics
    # This is far from perfect but improves TTS intelligibility vs no diacritics at all.
    result = []
    for char in text:
        result.append(char)
        if ARABIC_CHARS.match(char) and char not in "\u0640\u0627\u0648\u064A\u0629":
            if not result or not DIACRITICS.match(result[-2] if len(result) > 1 else ""):
                result.append("\u064E")  # fatha
    return "".join(result)


def prepare_for_tts(text: str) -> str:
    """Full Arabic pipeline before TTS: normalize + diacritize."""
    text = normalize(text)
    text = add_diacritics(text)
    return text


def reshape_for_display(text: str) -> str:
    """Reshape Arabic text for PIL/rendering (RTL handling)."""
    if not is_arabic(text):
        return text
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def split_words(text: str) -> List[str]:
    """Split text into words, preserving Arabic words."""
    return text.split()


def estimate_duration(text: str, language: str = "ar") -> float:
    """Estimate narration duration in seconds."""
    if language == "ar":
        # Arabic is denser, ~3.5 chars/sec spoken
        char_count = len(text.replace(" ", ""))
        return max(char_count / 3.5, 3.0)
    else:
        # English ~2.5 words/sec
        words = len(text.split())
        return max(words / 2.0, 3.0)
