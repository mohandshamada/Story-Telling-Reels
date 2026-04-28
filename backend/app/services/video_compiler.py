"""Video compilation using MoviePy 2.x with karaoke subtitles and RTL Arabic."""

import tempfile
from pathlib import Path
from typing import List

import numpy as np
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    VideoClip,
    VideoFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx import FadeIn, FadeOut, CrossFadeIn
from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.services.arabic_utils import is_arabic, reshape_for_display


class VideoCompiler:
    def __init__(self):
        self.width = settings.video_width
        self.height = settings.video_height
        self.fps = settings.VIDEO_FPS
        self.font = settings.SUBTITLE_FONT
        self.subtitle_font_size = 64

    # ------------------------------------------------------------------
    # Scene compilation
    # ------------------------------------------------------------------
    def compile_scene(
        self,
        image_path: Path,
        audio_path: Path,
        narration_text: str,
        duration: float | None = None,
        music_path: Path | None = None,
        sfx_list: List[dict] | None = None,
    ) -> VideoFileClip:
        """Compile a single scene: image + Ken Burns + narration + karaoke subtitles + music + SFX."""
        if audio_path.exists() and audio_path.stat().st_size > 0:
            narration_audio = AudioFileClip(str(audio_path))
            audio_duration = narration_audio.duration
        else:
            narration_audio = None
            audio_duration = duration or 5.0

        scene_duration = duration or audio_duration

        # Background image
        bg = self._load_background(image_path, scene_duration)

        # Ken Burns effect
        bg = self._apply_ken_burns(bg, scene_duration)

        # Karaoke subtitles
        subtitles = self._create_karaoke_subtitle_clip(narration_text, scene_duration)

        # Compose video layers
        scene = CompositeVideoClip([bg, subtitles], size=(self.width, self.height))
        scene = scene.with_duration(scene_duration)

        # Build audio layers
        audio_layers = []
        if narration_audio:
            audio_layers.append(narration_audio)

        if music_path and music_path.exists() and music_path.stat().st_size > 0:
            music = AudioFileClip(str(music_path))
            if music.duration < scene_duration:
                loops = int(scene_duration / music.duration) + 1
                music = concatenate_audioclips([music] * loops)
            music = music.subclipped(0, scene_duration)
            music = music.with_volume_scaled(0.12)
            audio_layers.append(music)

        if sfx_list:
            for sfx in sfx_list:
                sfx_path = sfx.get("path")
                offset = sfx.get("time_offset", 0.0)
                if sfx_path and Path(sfx_path).exists():
                    sfx_clip = AudioFileClip(str(sfx_path))
                    sfx_clip = sfx_clip.with_volume_scaled(0.25)
                    sfx_clip = sfx_clip.with_start(offset)
                    audio_layers.append(sfx_clip)

        if audio_layers:
            final_audio = CompositeAudioClip(audio_layers)
            scene = scene.with_audio(final_audio)

        return scene

    def _load_background(self, image_path: Path, duration: float) -> ImageClip:
        """Load and resize image to fill 9:16 canvas."""
        if not image_path.exists() or image_path.stat().st_size == 0:
            img = Image.new("RGB", (self.width, self.height), (255, 248, 230))
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            img.save(tmp.name)
            image_path = Path(tmp.name)

        clip = ImageClip(str(image_path)).with_duration(duration)
        img_w, img_h = clip.size
        target_ratio = self.width / self.height
        img_ratio = img_w / img_h

        if img_ratio > target_ratio:
            new_h = self.height
            new_w = int(new_h * img_ratio)
            clip = clip.resized(height=new_h)
            x_center = (new_w - self.width) // 2
            clip = clip.cropped(x1=x_center, y1=0, x2=x_center + self.width, y2=self.height)
        else:
            new_w = self.width
            new_h = int(new_w / img_ratio)
            clip = clip.resized(width=new_w)
            y_center = (new_h - self.height) // 2
            clip = clip.cropped(x1=0, y1=y_center, x2=self.width, y2=y_center + self.height)

        return clip

    def _apply_ken_burns(self, clip: ImageClip, duration: float) -> VideoFileClip:
        """Apply slow zoom from 1.0 to 1.08 over the duration."""

        def resize_func(t: float):
            return 1.0 + 0.08 * (t / max(duration, 0.1))

        return clip.resized(resize_func)

    # ------------------------------------------------------------------
    # Karaoke subtitles with PIL
    # ------------------------------------------------------------------
    def _create_karaoke_subtitle_clip(self, text: str, duration: float) -> VideoClip:
        """Create word-by-word karaoke subtitles using PIL frame generation."""
        if not text or not text.strip():
            # Return transparent clip
            return VideoClip(
                lambda t: np.zeros((self.height, self.width, 4), dtype=np.uint8)
            ).with_duration(duration)

        font_path = self._find_font()
        font = ImageFont.truetype(font_path, self.subtitle_font_size)
        highlight_font = ImageFont.truetype(font_path, int(self.subtitle_font_size * 1.15))

        words = text.split()
        rtl = is_arabic(text)

        # Calculate word timings
        total_chars = sum(len(w) for w in words) or 1
        word_timings = []
        cumulative = 0.0
        for word in words:
            word_duration = duration * (len(word) / total_chars)
            cumulative += word_duration
            word_timings.append(cumulative)

        # Subtitle area: bottom third of screen
        sub_y = self.height - 340
        max_width = self.width - 120

        def make_frame(t: float):
            # Determine active word
            active_idx = 0
            for i, end_time in enumerate(word_timings):
                if t <= end_time:
                    active_idx = i
                    break
            else:
                active_idx = len(words) - 1

            # Create transparent image
            img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Word wrap and layout
            lines = []
            current_line = []
            current_width = 0
            word_dims = []

            for word in words:
                display_word = reshape_for_display(word) if rtl else word
                w, h = draw.textbbox((0, 0), display_word, font=font)[2:4]
                word_dims.append((display_word, w, h))
                if current_width + w + (len(current_line) * 20) > max_width and current_line:
                    lines.append(current_line)
                    current_line = [display_word]
                    current_width = w
                else:
                    current_line.append(display_word)
                    current_width += w
            if current_line:
                lines.append(current_line)

            # Draw each line centered
            y = sub_y
            word_idx = 0
            for line in lines:
                # Measure full line width
                line_width = 0
                line_words = []
                for _ in line:
                    if word_idx < len(word_dims):
                        dw, w, h = word_dims[word_idx]
                        line_words.append((word_idx, dw, w, h))
                        line_width += w + 20
                        word_idx += 1
                line_width -= 20  # remove last spacing

                x = (self.width - line_width) // 2
                for wi, dw, w, h in line_words:
                    is_active = wi == active_idx
                    # Draw text shadow
                    shadow_offset = 3
                    draw.text(
                        (x + shadow_offset, y + shadow_offset),
                        dw,
                        font=highlight_font if is_active else font,
                        fill=(0, 0, 0, 200),
                    )
                    # Draw text
                    color = (255, 223, 100, 255) if is_active else (255, 255, 255, 255)
                    draw.text(
                        (x, y),
                        dw,
                        font=highlight_font if is_active else font,
                        fill=color,
                    )
                    x += w + 20

                # Line height estimate
                y += int(self.subtitle_font_size * 1.4)

            return np.array(img)

        return VideoClip(make_frame).with_duration(duration)

    def _find_font(self) -> str:
        """Find a usable font file path for Pillow."""
        candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansMono-Regular.ttf",
        ]
        for path in candidates:
            if Path(path).exists():
                return path
        # Fallback to default
        return "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

    # ------------------------------------------------------------------
    # Full video assembly
    # ------------------------------------------------------------------
    def render_final(
        self,
        scenes: List[VideoFileClip],
        output_path: Path,
        title: str = "",
        moral: str = "",
    ) -> Path:
        """Concatenate scenes and render final MP4."""
        clips: List[VideoFileClip] = []

        if title:
            intro = self._create_title_card(title, 2.0)
            clips.append(intro)

        for i, scene in enumerate(scenes):
            if i > 0:
                scene = scene.with_effects([CrossFadeIn(0.5)])
            clips.append(scene)

        if moral:
            outro = self._create_outro_card(moral, 3.0)
            clips.append(outro)

        final = concatenate_videoclips(clips, method="compose")

        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            bitrate=settings.VIDEO_BITRATE,
            threads=4,
            preset="medium",
            logger=None,
        )

        for c in clips:
            c.close()
        final.close()

        return output_path

    def _create_title_card(self, title: str, duration: float) -> VideoFileClip:
        """Create a simple animated title card."""
        font_path = self._find_font()
        font = ImageFont.truetype(font_path, 80)
        bg_path = self._solid_color_image((120, 180, 220))
        bg = ImageClip(str(bg_path)).with_duration(duration).resized((self.width, self.height))

        # Draw title with PIL for better RTL support
        def make_frame(t: float):
            img = Image.new("RGBA", (self.width, self.height), (120, 180, 220, 255))
            draw = ImageDraw.Draw(img)
            display_title = reshape_for_display(title) if is_arabic(title) else title
            bbox = draw.textbbox((0, 0), display_title, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            y = (self.height - th) // 2
            draw.text((x + 3, y + 3), display_title, font=font, fill=(0, 0, 0, 180))
            draw.text((x, y), display_title, font=font, fill=(255, 255, 255, 255))
            return np.array(img)

        txt_clip = VideoClip(make_frame).with_duration(duration)
        txt_clip = txt_clip.with_effects([FadeIn(0.5), FadeOut(0.5)])

        card = CompositeVideoClip([bg, txt_clip], size=(self.width, self.height))
        return card

    def _create_outro_card(self, moral: str, duration: float) -> VideoFileClip:
        """Create moral lesson outro card."""
        font_path = self._find_font()
        label_font = ImageFont.truetype(font_path, 56)
        moral_font = ImageFont.truetype(font_path, 64)
        bg_path = self._solid_color_image((100, 200, 150))
        bg = ImageClip(str(bg_path)).with_duration(duration).resized((self.width, self.height))

        def make_frame(t: float):
            img = Image.new("RGBA", (self.width, self.height), (100, 200, 150, 255))
            draw = ImageDraw.Draw(img)

            label_text = reshape_for_display("Moral of the Story") if is_arabic("Moral of the Story") else "Moral of the Story"
            bbox = draw.textbbox((0, 0), label_text, font=label_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (self.width - tw) // 2
            draw.text((x + 2, 402), label_text, font=label_font, fill=(0, 0, 0, 150))
            draw.text((x, 400), label_text, font=label_font, fill=(255, 255, 255, 220))

            display_moral = reshape_for_display(moral) if is_arabic(moral) else moral
            bbox2 = draw.textbbox((0, 0), display_moral, font=moral_font)
            tw2, th2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
            x2 = (self.width - tw2) // 2
            draw.text((x2 + 3, 603), display_moral, font=moral_font, fill=(0, 0, 0, 180))
            draw.text((x2, 600), display_moral, font=moral_font, fill=(255, 255, 255, 255))

            return np.array(img)

        txt_clip = VideoClip(make_frame).with_duration(duration)

        card = CompositeVideoClip([bg, txt_clip], size=(self.width, self.height))
        return card

    def _solid_color_image(self, color: tuple) -> Path:
        """Create a temporary solid color image."""
        img = Image.new("RGB", (self.width, self.height), color)
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        img.save(tmp.name)
        return Path(tmp.name)


from moviepy import concatenate_audioclips
