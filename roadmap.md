# Automated Story-to-Reels App for Kids
## Kalila & Dimna / Children's Stories → Short Video Reels

---

## 1. Executive Overview

An end-to-end pipeline that accepts a text story (e.g., *Kalila wa Dimna* fables) and automatically generates:
- **Narration** (TTS, child-friendly voice)
- **Visuals** (AI-generated images/animations per scene)
- **Subtitles/Captions** (large, readable, kid-safe fonts)
- **Background music & SFX** (gentle, engaging)
- **Final output**: 15-60 second vertical reels (9:16), ready for Instagram/TikTok/YouTube Shorts

---

## 1.5 Implementation Status

> **Last Updated:** 2026-04-28

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI backend scaffold | ✅ Done | `app/main.py`, routes, CORS, static files |
| Database models (SQLAlchemy 2.0) | ✅ Done | Story, Scene, RenderJob with relationships |
| Pydantic schemas | ✅ Done | Request/response validation |
| GPT-4 story parser | ✅ Done | Structured JSON output, prompt enhancement |
| ElevenLabs TTS | ✅ Done | `eleven_multilingual_v2`, local caching |
| DALL-E 3 image generation | ✅ Done | `1024x1792`, kid-safe prompt wrapping |
| MoviePy video compiler | ✅ Done | Ken Burns, subtitles, title/outro cards |
| Celery task pipeline | ✅ Done | End-to-end `process_story` task |
| React frontend | ✅ Done | Dashboard, New Story, Story Detail pages |
| Docker Compose | ✅ Done | API, worker, Redis, frontend |
| Background music & SFX | ✅ Done | MoviePy CompositeAudioClip, music library, SFX triggers |
| WebSocket progress | ✅ Done | Redis pub/sub bridge, WS endpoint, React hook |
| Scene editor UI | ✅ Done | Inline editing, regenerate image/audio per scene |
| User accounts / auth | ❌ Skipped | Personal tool — single user, no auth needed |
| PostgreSQL | ✅ Done | Docker Compose service added, `psycopg2-binary` installed, config supports both SQLite + PG |
| Arabic support | ✅ Done | `arabic_utils.py`: normalization, heuristic tashkeel, RTL reshape for PIL subtitles |
| Karaoke subtitles | ✅ Done | PIL-based frame generation: active word highlighted in yellow at 115% size |
| Multilingual voice cloning | ⏳ Pending | Only single-language ElevenLabs |
| Local GPU stack | ⏳ Pending | No ComfyUI, XTTS v2, or AnimateDiff |
| Auto-upload to socials | ⏳ Pending | Phase 4 |
| Mobile app | ⏳ Pending | Phase 4 |

---

## 2. High-Level Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   INPUT LAYER   │────▶│  PROCESSING CORE  │────▶│   OUTPUT LAYER  │
│                 │     │                  │     │                 │
│ • Text Story    │     │ • Story Parser   │     │ • Video Reel    │
│ • Voice Style   │     │ • Scene Engine   │     │ • Audio Track   │
│ • Visual Theme  │     │ • Asset Gen      │     │ • Metadata      │
│ • Music Mood    │     │ • Video Compiler │     │ • Thumbnail     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 3. Detailed Pipeline Flow

### Phase 1: Story Ingestion & Parsing

```
Raw Story Text
      │
      ▼
┌─────────────────────────────────────┐
│ 1. TEXT PREPROCESSING               │
│    • Language detection (AR/EN)      │
│    • UTF-8 normalization             │
│    • Remove special chars            │
│    • Fix diacritics (Arabic)         │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 2. CHUNKING ENGINE                  │
│    • Split into scenes (3-5 per    │
│      story for 30-45s reels)         │
│    • Identify:                       │
│      - Characters                    │
│      - Setting/Location              │
│      - Action/Dialogue               │
│      - Moral/Lesson                  │
│    • Assign timestamps per scene     │
│      (5-10s each)                  │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 3. SCENE SCRIPT GENERATION          │
│    • For each chunk, generate:       │
│      - Visual description (prompt)  │
│      - Narration text (simplified)   │
│      - Animation type (static/pan/   │
│        zoom/parallax)                │
│      - SFX trigger points            │
└─────────────────────────────────────┘
```

**Implementation Options:**
- **LLM-based**: GPT-4/Claude/Gemini with structured JSON output
- **Rule-based**: Regex + NLP (spaCy/NLTK) for simpler stories
- **Hybrid**: LLM for creative generation, rules for structure validation

---

### Phase 2: Asset Generation

#### 2A: Narration (Text-to-Speech)

```
Scene Script
      │
      ▼
┌─────────────────────────────────────┐
│ TTS ENGINE SELECTION                │
│                                     │
│ Option A: Cloud APIs                │
│ • ElevenLabs (best quality, voices) │
│ • Azure Neural TTS (multilingual)    │
│ • Google Cloud TTS (WaveNet)         │
│ • Amazon Polly (cost-effective)      │
│                                     │
│ Option B: Local/Open Source         │
│ • Coqui TTS (XTTS v2)               │
│ • Piper TTS (fast, lightweight)      │
│ • MeloTTS (multilingual)             │
│ • MMS-TTS (Meta, 1000+ languages)   │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ VOICE CONFIGURATION                 │
│ • Select "warm storyteller" persona │
│ • Adjust:                            │
│   - Speed: 0.9x (slower for kids)    │
│   - Pitch: +2 semitones (friendly)   │
│   - Emotion: "gentle/calm"          │
│ • Add natural pauses at punctuation  │
│ • Output: WAV/FLAC (lossless)      │
└─────────────────────────────────────┘
```

**Key Requirement**: Arabic diacritization (tashkeel) before TTS if using Arabic stories. Use `camel-tools` or `farasa` for automatic diacritization.

#### 2B: Visual Generation (Scene Images)

```
Visual Prompt
      │
      ▼
┌─────────────────────────────────────┐
│ IMAGE GENERATION PIPELINE           │
│                                     │
│ Option A: AI Image Gen APIs          │
│ • Midjourney (best artistic quality)│
│ • DALL-E 3 (prompt adherence)        │
│ • Stable Diffusion XL (cost/local)  │
│ • Ideogram (text in images)          │
│ • Leonardo.ai (consistent style)     │
│                                     │
│ Option B: Local SD Setup            │
│ • ComfyUI workflow                   │
│ • Automatic1111 WebUI               │
│ • Fooocus (simplified)               │
│ • SDXL Lightning (fast inference)    │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ STYLE CONSISTENCY SYSTEM            │
│ • Character consistency:             │
│   - Use IP-Adapter or Reference      │
│     Only technique                   │
│   - Seed locking for character faces │
│   - LoRA training for main chars     │
│ • Art style lock:                    │
│   - "Watercolor children's book      │
│     illustration, soft colors,       │
│     rounded shapes, no sharp edges"  │
│ • Aspect ratio: 9:16 (576x1024)      │
│ • Safe content filter (no scary/     │
│   violent imagery for kids)          │
└─────────────────────────────────────┘
```

**Prompt Template Example:**
```
Style: [Watercolor children's book illustration, soft pastel colors, 
        rounded friendly shapes, Studio Ghibli inspired]
Subject: [Two cute cartoon lions, Kalila and Dimna, sitting under 
          an oak tree in a sunny meadow]
Mood: [Warm, friendly, educational]
Technical: [9:16 aspect ratio, high detail, no text, no watermarks]
```

#### 2C: Animation (Static Image → Motion)

```
Static Image
      │
      ▼
┌─────────────────────────────────────┐
│ ANIMATION TECHNIQUES                │
│                                     │
│ 1. Ken Burns Effect (Simple)       │
│    • Slow zoom in/out                │
│    • Gentle pan across image         │
│    • Tools: MoviePy, FFmpeg           │
│                                     │
│ 2. Parallax Depth (Medium)          │
│    • Separate foreground/background  │
│    • Use Depth Anything v2 / MiDaS   │
│    • Animate layers at diff speeds   │
│    • Tools: LeiaPix, InstaMAT        │
│                                     │
│ 3. AI Video Generation (Advanced)    │
│    • AnimateDiff (local)             │
│    • Runway Gen-2 / Pika Labs        │
│    • Stable Video Diffusion          │
│    • Luma Dream Machine              │
│    • Kling AI / Haiper               │
│    • CogVideo / Open-Sora (OSS)      │
│                                     │
│ 4. Character Animation (Premium)    │
│    • Live2D / Spine 2D rigging       │
│    • Adobe Character Animator        │
│    • HeyGen / D-ID (talking heads)   │
└─────────────────────────────────────┘
```

**Recommended for MVP**: Ken Burns + subtle parallax. Upgrade to AI video for v2.

#### 2D: Audio Layer (Music & SFX)

```
┌─────────────────────────────────────┐
│ BACKGROUND MUSIC                    │
│ • Source options:                    │
│   - Uppbeat.io (free, kid-safe)     │
│   - Epidemic Sound (licensed)        │
│   - Artlist.io                       │
│   - AI-generated: MusicGen, Suno    │
│ • Style: "Gentle acoustic, playful,  │
│   no lyrics, 60-80 BPM"             │
│ • Ducking: -12dB when narration      │
│   plays, fade up in gaps            │
│ • Loop seamlessly for story length   │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ SOUND EFFECTS                       │
│ • Triggered by scene content:      │
│   - Animal sounds (lions, etc.)    │
│   - Nature (wind, water, birds)     │
│   - Magical/sparkle for lessons     │
│ • Source: Freesound.org, BBC SFX    │
│ • Volume: -20dB relative to voice   │
│ • Sparse usage (not overwhelming)    │
└─────────────────────────────────────┘
```

---

### Phase 3: Video Assembly

```
All Assets Ready
      │
      ▼
┌─────────────────────────────────────┐
│ VIDEO COMPOSITION ENGINE            │
│                                     │
│ 1. Timeline Construction             │
│    • Layer 0: Background image/video │
│    • Layer 1: Animated elements      │
│    • Layer 2: Character overlays    │
│    • Layer 3: Text/subtitles         │
│    • Layer 4: SFX markers           │
│    • Layer 5: Music track            │
│    • Layer 6: Narration track        │
│                                     │
│ 2. Subtitle Generation              │
│    • Large, rounded font (Comic Sans │
│      / Nunito / Varela Round)       │
│    • Text stroke/shadow for contrast │
│    • Word-by-word highlight (karaoke  │
│      style for reading along)        │
│    • Position: lower 1/3, safe area  │
│    • Colors: white text, black       │
│      outline, soft drop shadow      │
│                                     │
│ 3. Transitions                       │
│    • Soft crossfade between scenes   │
│    • 0.5s duration                   │
│    • Optional: page-turn effect      │
│                                     │
│ 4. Intro/Outro Cards                 │
│    • 2s animated title card          │
│    • Story name + episode number    │
│    • Outro: "Moral of the story"     │
│      text + subscribe CTA          │
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ RENDER & EXPORT                     │
│ • Resolution: 1080x1920 (9:16)       │
│ • FPS: 30fps                         │
│ • Codec: H.264 (libx264)             │
│ • Bitrate: 8-12 Mbps                │
│ • Audio: AAC, 192kbps               │
│ • Format: MP4                       │
│ • Max file size: 50MB for platforms  │
└─────────────────────────────────────┘
```

---

### Phase 4: Post-Processing & Distribution

```
┌─────────────────────────────────────┐
│ METADATA GENERATION                 │
│ • Auto-generate from story:          │
│   - Title: "[Animal] Learns [Lesson]"│
│   - Description with moral summary   │
│   - Tags: #kids #storytime #fables   │
│   - Hashtags by platform             │
│ • Thumbnail: Best frame + title text│
└─────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ PLATFORM OPTIMIZATION               │
│ • Instagram Reels: 90s max, trending │
│   audio integration                 │
│ • TikTok: Hook in first 3s, text    │
│   overlays, trending sounds         │
│ • YouTube Shorts: 60s max, end     │
│   screen with subscribe button    │
│ • WhatsApp Status: 30s segments      │
└─────────────────────────────────────┘
```

---

## 4. Technical Stack Options

> **Status:** Option A (Full Cloud/SaaS) is active for Phase 1 MVP. Local AI stack (Option C) is ⏳ planned for Phase 3.

### Option A: Full Cloud/SaaS (Fastest to Market)

| Component | Tool | Cost |
|-----------|------|------|
| Backend | Python + FastAPI / Node.js + Express | Free |
| Database | PostgreSQL + Redis | Free tier |
| Queue | Celery + RabbitMQ / AWS SQS | Low |
| Storage | AWS S3 / Cloudflare R2 | Pay per use |
| LLM | OpenAI GPT-4 / Anthropic Claude | Per token |
| TTS | ElevenLabs API | Per character |
| Image Gen | DALL-E 3 / Midjourney API | Per image |
| Video Gen | Runway / Pika API | Per second |
| Video Edit | FFmpeg (cloud) | Compute cost |
| Hosting | Vercel / Railway / Render | Free tier |

### Option B: Hybrid (Cost-Effective, Some Local)

| Component | Tool |
|-----------|------|
| Backend | Python + FastAPI |
| LLM | Local: Ollama (Llama 3) + Cloud fallback |
| TTS | Local: Coqui XTTS v2 (multilingual) |
| Image Gen | Local: ComfyUI + SDXL + LoRAs |
| Video Gen | Local: AnimateDiff + SVD |
| Video Edit | FFmpeg + MoviePy |
| Queue | Celery + Redis |
| GPU | Local RTX 4090 / Cloud GPU (RunPod/Vast.ai) |

### Option C: Fully Local (Privacy-First, No Subscriptions)

| Component | Tool | VRAM Required |
|-----------|------|---------------|
| LLM | Llama 3 70B (4-bit) / Mistral 7B | 8-40GB |
| TTS | Piper TTS + MeloTTS | 2GB |
| Image Gen | SDXL + ControlNet + IP-Adapter | 8-12GB |
| Video Gen | AnimateDiff v3 + SVD | 12-24GB |
| Video Edit | FFmpeg + MoviePy | CPU |
| Upscaling | Real-ESRGAN / SUPIR | 4-8GB |

---

## 5. Data Models & Schemas

> **Status:** ✅ Implemented in `backend/app/models/` and `backend/app/schemas/`

### Story Input Schema
```json
{
  "story_id": "uuid",
  "title": "The Lion and the Mouse",
  "source": "kalila_dimna",
  "language": "ar",
  "content": "full text...",
  "target_duration_seconds": 45,
  "target_audience": "3-7 years",
  "visual_theme": "watercolor_illustration",
  "voice_style": "warm_female_storyteller",
  "music_mood": "gentle_playful",
  "moral_lesson": "Kindness is never wasted"
}
```

### Scene Schema
```json
{
  "scene_id": "uuid",
  "story_id": "uuid",
  "sequence_number": 1,
  "narration_text": "Once upon a time...",
  "narration_audio_url": "s3://...",
  "visual_prompt": "A cute cartoon lion sleeping under a tree...",
  "image_url": "s3://...",
  "animation_type": "ken_burns_slow_zoom",
  "animation_video_url": "s3://...",
  "duration_seconds": 8.5,
  "sfx_triggers": [
    {"time_offset": 2.0, "sfx": "bird_chirp", "volume_db": -20}
  ],
  "subtitle_text": "Once upon a time...",
  "subtitle_style": {
    "font": "Nunito-Bold",
    "size": 64,
    "color": "#FFFFFF",
    "stroke_color": "#000000",
    "stroke_width": 3
  }
}
```

### Render Job Schema
```json
{
  "job_id": "uuid",
  "story_id": "uuid",
  "status": "queued|processing|rendering|completed|failed",
  "progress_percent": 75,
  "current_stage": "video_compilation",
  "scenes_total": 5,
  "scenes_completed": 4,
  "output_url": "s3://...",
  "output_format": "mp4",
  "resolution": "1080x1920",
  "file_size_mb": 12.4,
  "created_at": "2026-04-28T14:16:00Z",
  "completed_at": null,
  "error_message": null
}
```

---

## 6. API Endpoints (Backend Design)

> **Status:** ✅ Implemented in `backend/app/api/v1/`. WebSocket events are ⏳ planned.

### Core Endpoints

```
POST /api/v1/stories
  -> Submit new story for processing
  Body: StoryInputSchema
  Response: { story_id, job_id, status, estimated_seconds }

GET /api/v1/stories/{story_id}
  -> Get story status and metadata
  Response: Story + progress info

GET /api/v1/stories/{story_id}/scenes
  -> Get all scenes with asset URLs
  Response: Scene[]

POST /api/v1/stories/{story_id}/regenerate-scene/{scene_id}
  -> Regenerate a specific scene (different prompt/voice)
  Body: { visual_prompt?, voice_style? }

GET /api/v1/jobs/{job_id}
  -> Get render job status
  Response: RenderJobSchema

GET /api/v1/jobs/{job_id}/download
  -> Download final video (presigned URL)
  Response: 302 redirect to S3/Storage

POST /api/v1/templates
  -> Save reusable style template
  Body: { name, visual_theme, voice_style, music_mood, subtitle_style }

GET /api/v1/templates
  -> List saved templates
```

### WebSocket Events (Real-time Progress)

```
ws://api/v1/ws/jobs/{job_id}

Events:
  - job.started
  - scene.generation_started { scene_id, type: "image|audio|video" }
  - scene.generation_completed { scene_id, type, url }
  - scene.generation_failed { scene_id, type, error }
  - video.compilation_started
  - video.compilation_progress { percent }
  - video.completed { download_url }
  - job.failed { error_message }
```

---

## 7. Database Schema (PostgreSQL)

```sql
-- Stories table
CREATE TABLE stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    source VARCHAR(100),
    language VARCHAR(10) DEFAULT 'ar',
    content TEXT NOT NULL,
    target_duration INT DEFAULT 45,
    target_audience VARCHAR(50),
    visual_theme VARCHAR(100),
    voice_style VARCHAR(100),
    music_mood VARCHAR(100),
    moral_lesson TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Scenes table
CREATE TABLE scenes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    sequence_number INT NOT NULL,
    narration_text TEXT,
    narration_audio_url TEXT,
    visual_prompt TEXT,
    image_url TEXT,
    animation_type VARCHAR(100),
    animation_video_url TEXT,
    duration_seconds DECIMAL(5,2),
    subtitle_text TEXT,
    subtitle_style JSONB,
    sfx_triggers JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Render jobs table
CREATE TABLE render_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'queued',
    progress_percent INT DEFAULT 0,
    current_stage VARCHAR(100),
    scenes_total INT DEFAULT 0,
    scenes_completed INT DEFAULT 0,
    output_url TEXT,
    output_format VARCHAR(20) DEFAULT 'mp4',
    resolution VARCHAR(20) DEFAULT '1080x1920',
    file_size_mb DECIMAL(8,2),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    worker_id VARCHAR(100)
);

-- Templates table
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    visual_theme VARCHAR(100),
    voice_style VARCHAR(100),
    music_mood VARCHAR(100),
    subtitle_style JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets table (reusable generated assets)
CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_type VARCHAR(50) NOT NULL, -- image, audio, video, sfx, music
    storage_url TEXT NOT NULL,
    storage_provider VARCHAR(50), -- s3, local, r2
    prompt_hash VARCHAR(64), -- for caching/deduplication
    metadata JSONB,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_scenes_story_id ON scenes(story_id);
CREATE INDEX idx_jobs_status ON render_jobs(status);
CREATE INDEX idx_jobs_story_id ON render_jobs(story_id);
CREATE INDEX idx_assets_type ON assets(asset_type);
CREATE INDEX idx_assets_prompt_hash ON assets(prompt_hash);
```

---

## 8. Core Processing Modules (Python)

> **Status:** ✅ Implemented in `backend/app/services/`. See `story_parser.py`, `asset_generator.py`, `video_compiler.py`.

### 8.1 Story Parser Module
```python
# story_parser.py
from typing import List, Dict
from dataclasses import dataclass
import json

@dataclass
class Scene:
    sequence: int
    narration: str
    visual_prompt: str
    duration: float
    sfx: List[Dict]

class StoryParser:
    def __init__(self, llm_client):
        self.llm = llm_client

    def parse(self, story_text: str, target_scenes: int = 5) -> List[Scene]:
        # Split story into scenes using LLM with structured output
        # Returns list of Scene objects
        system_prompt = (
            "You are a children's story editor. "
            "Break the following story into {n} short scenes suitable for a 30-45 second video reel."
            "For each scene, provide:"
            "1. narration: Simplified text for kids (max 2 sentences, easy words)"
            "2. visual_prompt: Detailed description for AI image generation"
            "3. duration: Estimated seconds (5-10s per scene)"
            "4. sfx: List of sound effects needed"
            "Output valid JSON array."
        )
        # Implementation with retry logic, validation
        pass

    def enhance_prompt(self, base_prompt: str, style: str) -> str:
        # Add consistent style modifiers to image prompts
        style_modifiers = {
            "watercolor": "watercolor children's book illustration, soft pastel colors, rounded friendly shapes, gentle lighting, no scary elements",
            "3d_cartoon": "3D Pixar-style animation, cute rounded characters, bright cheerful colors, soft shadows",
            "flat_vector": "flat vector illustration, bold colors, simple shapes, Material Design style, kid-friendly"
        }
        return f"{base_prompt}, {style_modifiers.get(style, '')}, 9:16 aspect ratio"
```

### 8.2 Asset Generator Module
```python
# asset_generator.py
import asyncio
from pathlib import Path

class AssetGenerator:
    def __init__(self, config):
        self.tts_provider = config.tts_provider  # elevenlabs, coqui, azure
        self.image_provider = config.image_provider  # dalle, sdxl, midjourney
        self.video_provider = config.video_provider  # runway, animatediff

    async def generate_narration(self, text: str, voice_id: str) -> Path:
        # Generate TTS audio for a scene
        # ElevenLabs example
        # Coqui XTTS v2 example for local
        pass

    async def generate_image(self, prompt: str, seed: int = None) -> Path:
        # Generate scene image with consistency controls
        # IP-Adapter for character consistency
        # Seed control for reproducibility
        pass

    async def generate_animation(self, image_path: Path, animation_type: str) -> Path:
        # Convert static image to animated video segment
        # Ken Burns: MoviePy zoom/pan
        # Parallax: Depth-based layer separation
        # AI Video: AnimateDiff or API
        pass

    async def generate_all_scene_assets(self, scene: Scene) -> Dict:
        # Parallel generation of all assets for a scene
        results = await asyncio.gather(
            self.generate_narration(scene.narration, scene.voice_id),
            self.generate_image(scene.visual_prompt, scene.seed),
            return_exceptions=True
        )
        return {
            "audio": results[0],
            "image": results[1]
        }
```

### 8.3 Video Compiler Module
```python
# video_compiler.py
from moviepy.editor import *
from moviepy.video.fx.all import *
import ffmpeg

class VideoCompiler:
    def __init__(self, config):
        self.resolution = config.resolution  # (1080, 1920)
        self.fps = config.fps  # 30
        self.font = config.subtitle_font  # Nunito-Bold

    def compile_scene(self, scene_assets: Dict, duration: float) -> VideoFileClip:
        # Compile single scene with all layers
        # Load background image/video
        bg = ImageClip(str(scene_assets["image"])).set_duration(duration)
        bg = bg.resize(self.resolution)

        # Apply animation (Ken Burns)
        if scene_assets.get("animation"):
            bg = self.apply_ken_burns(bg, duration)

        # Add narration audio
        narration = AudioFileClip(str(scene_assets["audio"]))

        # Add subtitles
        subtitles = self.create_subtitle_clip(
            scene_assets["narration_text"], 
            duration,
            self.font
        )

        # Compose layers
        scene = CompositeVideoClip([bg, subtitles])
        scene = scene.set_audio(narration)

        return scene

    def apply_ken_burns(self, clip: ImageClip, duration: float) -> VideoClip:
        # Apply slow zoom and pan effect
        # Zoom from 1.0 to 1.1 over duration
        # Gentle pan from center to slightly offset
        def resize_func(t):
            return 1 + 0.1 * (t / duration)

        def position_func(t):
            x = 0 + 20 * (t / duration)
            y = 0 + 10 * (t / duration)
            return (x, y)

        return clip.resize(resize_func).set_position(position_func)

    def create_subtitle_clip(self, text: str, duration: float, font: str) -> TextClip:
        # Create styled subtitle text with stroke
        return (TextClip(
            text,
            fontsize=64,
            font=font,
            color='white',
            stroke_color='black',
            stroke_width=3,
            method='caption',
            size=(900, None),  # Width constraint
            align='center'
        )
        .set_position(('center', 1500))  # Lower third
        .set_duration(duration)
        .fadein(0.5)
        .fadeout(0.5))

    def add_music_and_sfx(self, video: VideoClip, music_path: Path, 
                          sfx_list: List[Dict]) -> VideoClip:
        # Mix background music with ducking and SFX
        music = AudioFileClip(str(music_path)).volumex(0.3)  # -12dB

        # Duck music during narration
        # This requires analyzing narration audio for speech segments
        # Simple approach: lower music volume when narration exists

        # Add SFX at specific timestamps
        composite_audio = [video.audio, music]
        for sfx in sfx_list:
            sfx_clip = AudioFileClip(sfx["path"]).volumex(0.1)
            sfx_clip = sfx_clip.set_start(sfx["time_offset"])
            composite_audio.append(sfx_clip)

        final_audio = CompositeAudioClip(composite_audio)
        return video.set_audio(final_audio)

    def render_final(self, scenes: List[VideoClip], output_path: Path):
        # Concatenate all scenes and render final video
        final = concatenate_videoclips(scenes, method="compose")

        # Add intro/outro
        intro = self.create_title_card(scenes[0].story_title)
        outro = self.create_outro_card(scenes[0].moral_lesson)

        final = concatenate_videoclips([intro, final, outro])

        final.write_videofile(
            str(output_path),
            fps=self.fps,
            codec='libx264',
            audio_codec='aac',
            bitrate='8000k',
            threads=4,
            preset='medium'
        )

        return output_path
```

### 8.4 Queue Worker (Celery)
```python
# tasks.py
from celery import Celery
from celery.signals import task_prerun, task_postrun

app = Celery('story_reels')
app.config_from_object('celeryconfig')

@app.task(bind=True, max_retries=3)
def process_story(self, story_id: str):
    # Main Celery task for end-to-end story processing
    try:
        # 1. Update job status
        job = RenderJob.get_by_story(story_id)
        job.update_status('parsing')

        # 2. Parse story into scenes
        story = Story.get(story_id)
        parser = StoryParser(get_llm_client())
        scenes = parser.parse(story.content, target_scenes=5)

        job.update_status('generating_assets', scenes_total=len(scenes))

        # 3. Generate assets for each scene (parallel batches)
        generator = AssetGenerator(get_config())
        for i, scene in enumerate(scenes):
            self.update_state(
                state='PROGRESS',
                meta={'current': i+1, 'total': len(scenes), 'stage': 'assets'}
            )
            assets = generator.generate_all_scene_assets(scene)
            scene.save_assets(assets)
            job.increment_completed()

        # 4. Compile video
        job.update_status('compiling')
        compiler = VideoCompiler(get_config())
        scene_clips = [compiler.compile_scene(s.assets, s.duration) for s in scenes]

        # Add music
        music_path = get_music_for_mood(story.music_mood)
        final_video = compiler.add_music_and_sfx(
            concatenate_videoclips(scene_clips),
            music_path,
            [s.sfx for s in scenes]
        )

        # 5. Render and upload
        output_path = Path(f"/tmp/{story_id}.mp4")
        compiler.render_final(scene_clips, output_path)

        upload_url = upload_to_storage(output_path, story_id)

        job.update_status('completed', output_url=upload_url)

        return {
            'story_id': story_id,
            'download_url': upload_url,
            'duration': final_video.duration
        }

    except Exception as exc:
        job.update_status('failed', error=str(exc))
        raise self.retry(exc=exc, countdown=60)
```

---

## 9. Frontend App Architecture

> **Status:** ✅ Implemented in `frontend/src/`. Scene editor is read-only; full editing UI is ⏳ planned.

### Tech Stack
- **Framework**: Next.js 14 (App Router) or React + Vite
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: Zustand or Redux Toolkit
- **API Client**: TanStack Query (React Query) + Axios
- **WebSocket**: Socket.io-client for real-time progress
- **Video Player**: ReactPlayer or native HTML5 video
- **Upload**: react-dropzone + tus resumable upload

### Key Pages

```
/                    -> Dashboard (all stories, stats)
/stories/new         -> Upload/Input new story
/stories/{id}        -> Story detail + scene editor
/stories/{id}/edit   -> Manual scene adjustments
/stories/{id}/render -> Render progress + preview
/templates           -> Manage style templates
/settings            -> API keys, voice selection, defaults
```

### Scene Editor UI
```
┌─────────────────────────────────────────────┐
│  Story: The Lion and the Mouse              │
├─────────────────────────────────────────────┤
│  Scene 1 / 5                                │
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │              │  │ Narration:          │  │
│  │   [IMAGE]    │  │ "Once upon a time,  │  │
│  │   Preview    │  │  a big lion..."     │  │
│  │              │  │                     │  │
│  │  [▶ Preview] │  │ [🎙️ Regenerate]    │  │
│  │              │  │ [📝 Edit Text]      │  │
│  └──────────────┘  └─────────────────────┘  │
│                                             │
│  Visual Prompt:                             │
│  [A cute cartoon lion sleeping under a      │
│   big oak tree, watercolor style...    ]    │
│  [🎨 Regenerate Image]                    │
│                                             │
│  [⬅ Previous]  [Next ➡]                   │
│                                             │
│  [🎬 Render Final Video]                   │
└─────────────────────────────────────────────┘
```

---

## 10. Arabic Language Specific Considerations

### Text Processing
```python
# arabic_utils.py
import re

class ArabicProcessor:
    def normalize(self, text: str) -> str:
        # Normalize Arabic text for processing
        # Remove tatweel (kashida)
        text = re.sub(r'ـ', '', text)
        # Normalize alef variants
        text = re.sub(r'[آأإ]', 'ا', text)
        return text

    def add_diacritics(self, text: str) -> str:
        # Add tashkeel for TTS pronunciation
        # Use camel-tools or farasa
        from camel_tools.dialectal import DialectalIdentifier
        # Or call Farasa API
        pass

    def split_sentences(self, text: str) -> List[str]:
        # Split Arabic text into sentences
        # Arabic sentence delimiters
        delimiters = r'[.!?۔]+'
        return [s.strip() for s in re.split(delimiters, text) if s.strip()]

    def estimate_duration(self, text: str) -> float:
        # Estimate narration duration for Arabic text
        # Arabic is denser, ~3-4 chars per second spoken
        char_count = len(text.replace(' ', ''))
        return max(char_count / 3.5, 3.0)  # Minimum 3 seconds
```

### RTL Layout
```css
/* For Arabic interface */
[dir="rtl"] .scene-editor {
    direction: rtl;
    text-align: right;
}

[dir="rtl"] .subtitle-preview {
    font-family: 'Noto Sans Arabic', 'Vazirmatn', sans-serif;
    /* Ensure subtitles render correctly in video */
}
```

### Arabic TTS Voices
- **ElevenLabs**: Custom voice cloning or "Adam" (can be configured)
- **Azure**: "ar-SA-HamedNeural" (male), "ar-SA-ZariyahNeural" (female)
- **Google Cloud**: "ar-XA-Wavenet-A" through "D"
- **Local**: Coqui XTTS v2 supports Arabic with fine-tuning

---

## 10.5 Multilingual Voice System (Same Voice, Multiple Languages)

### Overview

The app supports generating the **same story reel in multiple languages** while preserving a **consistent narrator voice identity** across all languages. This means a child can watch "The Lion and the Rabbit" in Arabic, then switch to English, and hear the **same warm storyteller voice** — not a different actor per language.

This is achieved through **cross-lingual voice cloning / voice transfer** technology.

---

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│           MULTILINGUAL VOICE PIPELINE                        │
│                                                              │
│  Step 1: Voice Profile Creation                              │
│  ┌─────────────────┐                                         │
│  │ Record/Upload   │  10-60s of clean speech                │
│  │ Voice Sample    │  (any language — the voice identity     │
│  │                 │   is language-agnostic)                │
│  └────────┬────────┘                                         │
│           │                                                  │
│           ▼                                                  │
│  Step 2: Voice Embedding Extraction                          │
│  ┌─────────────────┐                                         │
│  │ XTTS v2 /       │  Extract speaker embedding (timbre,   │
│  │ ElevenLabs v3   │  pitch, tone, speaking style)          │
│  │ / OpenVoice2    │  -> 512-dim speaker vector              │
│  └────────┬────────┘                                         │
│           │                                                  │
│           ▼                                                  │
│  Step 3: Language-Specific TTS Generation                     │
│  ┌─────────────────────────────────────────┐                │
│  │                                         │                │
│  │  Speaker Embedding ──┐                  │                │
│  │                      │                  │                │
│  │  Arabic Text    ─────┼──▶ [TTS Model] ──┼──▶ Arabic Audio│
│  │  (with tashkeel)     │    (XTTS/Eleven)│    (same voice) │
│  │                      │                  │                │
│  │  English Text   ─────┼──▶ [TTS Model] ──┼──▶ English Audio│
│  │                      │    (same model)  │    (same voice) │
│  │                      │                  │                │
│  │  French Text    ─────┼──▶ [TTS Model] ──┼──▶ French Audio │
│  │                      │    (same model)  │    (same voice) │
│  │                      │                  │                │
│  │  [16+ languages]  ───┘                  │                │
│  │                                         │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  Step 4: Per-Language Video Assembly                         │
│  • Same scenes, same images, same music                      │
│  • Only narration audio changes per language                 │
│  • Subtitles rendered in target language script               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Supported TTS Engines for Multilingual Voice

| Engine | Cross-Lingual | Languages | Local/Cloud | Cost | Quality |
|--------|--------------|-----------|-------------|------|---------|
| **XTTS v2** | Yes Native | 16+ (incl. Arabic) | Local | Free | 5 stars |
| **ElevenLabs v3** | Yes Native | 32+ (incl. Arabic) | Cloud | $5/mo+ | 5 stars |
| **OpenVoice2** | Yes | 10+ | Local | Free | 4 stars |
| **Coqui TTS** | Yes | 1100+ | Local | Free | 4 stars |
| **MeloTTS** | No | 8 (no Arabic) | Local | Free | 3 stars |
| **Azure Neural** | Limited | 140+ | Cloud | Pay-per-use | 4 stars |
| **Google Cloud** | Limited | 75+ | Cloud | Pay-per-use | 4 stars |

**Recommended for your setup (CachyOS + RTX 4090): XTTS v2** — runs locally, supports Arabic natively, and preserves voice identity across languages.

---

### XTTS v2: Technical Details

From the Coqui XTTS research paper:

- **16 languages supported**: English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, **Arabic**, Chinese, Hungarian, Korean, Japanese
- **Cross-lingual voice cloning**: Clone a voice from a 3-10 second sample in ANY language, then speak in ANY other supported language while preserving the original speaker's timbre, prosody, and style
- **Speaker similarity score (SECS)**: 0.5852 baseline -> 0.7166 after fine-tuning on 10 min of target speaker audio
- **Fine-tuning capable**: 10 minutes of clean speech from your target narrator improves quality significantly
- **Romanization for complex scripts**: Korean, Japanese, Chinese are romanized before tokenization; Arabic uses native script with diacritics

**Arabic-specific notes**:
- Quality rating: 4/5 stars — good but not perfect
- **Requires tashkeel (diacritics)** for best pronunciation
- Use `camel-tools` or `farasa` for automatic diacritization before TTS
- Fine-tuning with 10+ minutes of Arabic speech improves accent naturalness

---

### Implementation: Multilingual Voice Manager

```python
# multilingual_voice_manager.py
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class MultilingualVoiceManager:
    """Manages a single voice profile across multiple languages."""

    def __init__(self, tts_engine: str = 'xtts_v2', config: Dict = None):
        self.engine = tts_engine
        self.config = config or {}
        self.voice_profiles = {}

    class VoiceProfile:
        def __init__(self, profile_id: str, name: str, sample_path: Path):
            self.profile_id = profile_id
            self.name = name
            self.sample_path = sample_path
            self.speaker_embedding = None
            self.supported_languages = []
            self.fine_tuned = False

    def create_voice_profile(self, name: str, sample_audio: Path,
                             languages: List[str] = None) -> VoiceProfile:
        """Create a new voice profile from a sample recording."""
        if languages is None:
            languages = ["en", "ar"]
        profile_id = hashlib.sha256(name.encode()).hexdigest()[:12]
        profile = self.VoiceProfile(profile_id, name, sample_audio)

        if self.engine == 'xtts_v2':
            profile.speaker_embedding = self._extract_xtts_embedding(sample_audio)
            profile.supported_languages = [
                "en", "es", "fr", "de", "it", "pt", "pl", "tr",
                "ru", "nl", "cs", "ar", "zh", "hu", "ko", "ja"
            ]
        elif self.engine == 'elevenlabs_v3':
            profile.speaker_embedding = self._upload_elevenlabs_voice(sample_audio)
            profile.supported_languages = self._get_elevenlabs_languages()

        self.voice_profiles[profile_id] = profile
        return profile

    def generate_narration(self, profile_id: str, text: str, language: str,
                           output_path: Path, speed: float = 0.9,
                           emotion: str = "gentle") -> Path:
        """Generate narration in target language using the voice profile."""
        profile = self.voice_profiles[profile_id]

        if language not in profile.supported_languages:
            raise ValueError(
                f"Language {language} not supported by profile {profile.name}. "
                f"Supported: {profile.supported_languages}"
            )

        processed_text = self._preprocess_text(text, language)

        if self.engine == 'xtts_v2':
            return self._generate_xtts(profile.speaker_embedding, processed_text,
                                         language, output_path, speed)
        elif self.engine == 'elevenlabs_v3':
            return self._generate_elevenlabs(profile.speaker_embedding, processed_text,
                                             language, output_path, speed)

    def _preprocess_text(self, text: str, language: str) -> str:
        """Language-specific text preprocessing before TTS."""
        if language == 'ar':
            text = self._normalize_arabic(text)
            if not self._has_diacritics(text):
                text = self._add_tashkeel(text)
            return text
        elif language == 'en':
            return self._simplify_english(text)
        return text

    def _normalize_arabic(self, text: str) -> str:
        """Normalize Arabic Unicode characters."""
        import re
        text = re.sub(r'\u0640', '', text)
        text = re.sub(r'[\u0622\u0623\u0625]', '\u0627', text)
        return text

    def _has_diacritics(self, text: str) -> bool:
        """Check if Arabic text already has tashkeel."""
        diacritic_range = range(0x064B, 0x065F)
        return any(ord(c) in diacritic_range for c in text)

    def _add_tashkeel(self, text: str) -> str:
        """Add diacritics using camel-tools or farasa."""
        # Option A: camel-tools
        # from camel_tools.dialectal import DialectalIdentifier
        # Option B: Farasa API
        # Option C: Local model (Shakkelha)
        pass

    def _generate_xtts(self, speaker_embedding, text: str, language: str,
                       output_path: Path, speed: float) -> Path:
        """Generate audio using local XTTS v2."""
        from TTS.api import TTS
        tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')

        profile = self.voice_profiles.get(profile_id)
        tts.tts_to_file(
            text=text,
            speaker_wav=str(profile.sample_path),
            language=language,
            file_path=str(output_path),
            speed=speed
        )
        return output_path

    def generate_multilingual_reel_set(self, story, profile_id: str,
                                       languages: List[str],
                                       base_output_dir: Path) -> Dict[str, Path]:
        """Generate the SAME reel in multiple languages."""
        results = {}

        for lang in languages:
            lang_dir = base_output_dir / lang
            lang_dir.mkdir(parents=True, exist_ok=True)

            scene_audios = []
            for i, scene in enumerate(story.scenes):
                narration_text = scene.translations.get(lang, scene.narration)
                audio_path = lang_dir / f"scene_{i}_narration.wav"
                self.generate_narration(
                    profile_id=profile_id,
                    text=narration_text,
                    language=lang,
                    output_path=audio_path
                )
                scene_audios.append(audio_path)

            video_path = self._assemble_reel(
                story=story,
                scene_audios=scene_audios,
                language=lang,
                output_path=lang_dir / f"reel_{lang}.mp4"
            )
            results[lang] = video_path

        return results
```

---

### Database Schema Update (Multilingual Tables)

```sql
-- Voice Profiles table
CREATE TABLE voice_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    sample_audio_url TEXT NOT NULL,
    speaker_embedding JSONB,
    tts_engine VARCHAR(50) DEFAULT 'xtts_v2',
    fine_tuned BOOLEAN DEFAULT FALSE,
    fine_tune_data_url TEXT,
    supported_languages TEXT[] DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Story Translations table
CREATE TABLE story_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID REFERENCES stories(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    title VARCHAR(255),
    content TEXT NOT NULL,
    moral_lesson TEXT,
    translated_by VARCHAR(50) DEFAULT 'ai',
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(story_id, language)
);

-- Scene Translations table
CREATE TABLE scene_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scene_id UUID REFERENCES scenes(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    narration_text TEXT NOT NULL,
    subtitle_text TEXT,
    narration_audio_url TEXT,
    duration_seconds DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(scene_id, language)
);

-- Multilingual Render Jobs table
CREATE TABLE multilingual_render_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_job_id UUID REFERENCES render_jobs(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    voice_profile_id UUID REFERENCES voice_profiles(id),
    status VARCHAR(50) DEFAULT 'queued',
    output_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_voice_profiles_engine ON voice_profiles(tts_engine);
CREATE INDEX idx_story_translations_story ON story_translations(story_id);
CREATE INDEX idx_scene_translations_scene ON scene_translations(scene_id);
CREATE INDEX idx_multilingual_jobs_base ON multilingual_render_jobs(base_job_id);
```

---

### API Endpoints (Multilingual)

```
POST /api/v1/voice-profiles
  -> Create new voice profile from audio sample
  Body: { name, sample_audio_file, languages[] }
  Response: { profile_id, name, supported_languages }

GET /api/v1/voice-profiles
  -> List all voice profiles
  Response: VoiceProfile[]

POST /api/v1/voice-profiles/{id}/fine-tune
  -> Fine-tune voice with additional training data
  Body: { training_audio_files[], epochs: 10 }
  Response: { job_id, estimated_minutes }

POST /api/v1/stories/{story_id}/translate
  -> Auto-translate story to target languages
  Body: { target_languages: ["en", "ar", "fr"], translate_narration: true }
  Response: { translation_job_id, languages_requested }

POST /api/v1/stories/{story_id}/render-multilingual
  -> Generate reels in multiple languages with same voice
  Body: { voice_profile_id, languages: ["en", "ar"], visual_theme, music_mood }
  Response: { 
    base_job_id, 
    language_jobs: [
      { language: "en", job_id: "...", status: "queued" },
      { language: "ar", job_id: "...", status: "queued" }
    ]
  }

GET /api/v1/stories/{story_id}/versions
  -> Get all language versions of a story
  Response: {
    base_story: { ... },
    versions: [
      { language: "en", video_url: "...", duration: 45 },
      { language: "ar", video_url: "...", duration: 48 }
    ]
  }
```

---

### Frontend: Language Switcher UI

```
┌─────────────────────────────────────────────┐
│  The Lion and the Rabbit                    │
│  🌍 Language: [English ▼]                   │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │      [VIDEO PREVIEW]                │   │
│  │      0:23 / 0:45                    │   │
│  │                                     │   │
│  │  "A big lion ruled the jungle..."   │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Available Versions:                        │
│  [🇬🇧 English] [🇸🇦 Arabic] [🇫🇷 French]     │
│                                             │
│  Voice: "Warm Storyteller Amina"            │
│  [🎙️ Same voice in all languages]          │
│                                             │
│  [📥 Download] [📤 Share] [🔄 Regenerate]   │
└─────────────────────────────────────────────┘
```

---

### Workflow: Creating a Multilingual Reel Set

```
1. User uploads story in English
   │
   ▼
2. App parses into 5 scenes (English)
   │
   ▼
3. User selects voice profile "Amina"
   (previously created from 30s Arabic sample)
   │
   ▼
4. User requests versions in: English, Arabic, French
   │
   ▼
5. App auto-translates narration text for each scene
   • English: "A big lion ruled the jungle..."
   • Arabic: "كان هناك أسد كبير يحكم الغابة..." (with tashkeel)
   • French: "Un grand lion régnait sur la jungle..."
   │
   ▼
6. App generates narration audio for EACH language
   using the SAME voice profile (Amina's voice)
   • reel_en.mp4 — Amina speaks English
   • reel_ar.mp4 — Amina speaks Arabic  
   • reel_fr.mp4 — Amina speaks French
   │
   ▼
7. App assembles 3 final videos
   Same images, same music, same animations
   Only audio + subtitles differ
   │
   ▼
8. User gets 3 download links
   Can preview and switch languages in player
```

---

### Technical Considerations

| Challenge | Solution |
|-----------|----------|
| **Arabic text expansion** | Arabic is ~30% shorter than English; adjust subtitle font size and duration per language |
| **Tashkeel quality** | Use camel-tools + manual review for critical stories; cache diacritized versions |
| **Voice accent in cross-lingual** | Fine-tune with 10+ min of target language speech; or accept slight accent as character |
| **RTL subtitles** | MoviePy supports RTL via PIL/Pillow with Arabic reshaping (arabic-reshaper + python-bidi) |
| **Language detection** | Auto-detect input language; allow manual override |
| **Translation quality** | Use GPT-4 for first pass, human review for published content; preserve moral/lesson meaning |
| **Storage cost** | 3 language versions = 3x storage; use R2/S3 with lifecycle policies; keep only final versions |

---

### Cost Impact: Multilingual

| Scenario | Languages | Cost Multiplier |
|----------|-----------|----------------|
| Single language | 1 | 1x (baseline) |
| Bilingual (EN+AR) | 2 | ~1.8x (images reused, only audio regenerated) |
| Trilingual | 3 | ~2.5x |
| Full set (5 langs) | 5 | ~4x |

**Cost reduction strategies**:
- Reuse generated images across all languages (biggest savings)
- Reuse background music (no change needed)
- Cache translated text to avoid re-translation
- Batch TTS generation (parallel processing)

---

### Voice Profile Creation Guide

**For creators who want a custom storyteller voice:**

1. **Record a sample**: 30-60 seconds of clear speech in any language
   - Quiet room, no background noise
   - Consistent tone (the "storyteller" persona you want)
   - Save as WAV, 44.1kHz, mono or stereo

2. **Upload to app**: The app extracts the speaker embedding

3. **Test across languages**: Generate "Hello" in English, Arabic, French
   - Listen for consistency
   - Fine-tune if accent is too strong in any language

4. **Fine-tune (optional)**: Upload 10+ minutes of speech in each target language
   - Improves native accent quality
   - Especially important for Arabic (complex phonemes)

5. **Save profile**: Name it (e.g., "Amina the Storyteller") and reuse for all future reels

---
## 11. Caching & Optimization Strategy

### Asset Deduplication
```python
# Cache generated assets by prompt hash
import hashlib

def get_prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]

def get_cached_image(prompt: str) -> Optional[Path]:
    hash = get_prompt_hash(prompt)
    asset = Asset.query.filter_by(prompt_hash=hash, asset_type='image').first()
    if asset:
        asset.usage_count += 1
        db.session.commit()
        return Path(asset.storage_url)
    return None
```

### Smart Batching
- Batch similar image generation prompts together
- Reuse character images across scenes (IP-Adapter reference)
- Pre-generate common backgrounds (forest, desert, village)

### Progressive Rendering
```
Draft Mode (Fast Preview):
  • Low-res images (512x512)
  • Fast TTS (Piper/MMS)
  • 15fps preview
  • Watermarked "PREVIEW"

Final Mode (Production):
  • Full-res images (1080x1920)
  • High-quality TTS (ElevenLabs)
  • 30fps + motion
  • Full music mix
```

---

## 12. Quality Assurance & Safety

### Content Safety Pipeline
```
Story Input
    │
    ▼
┌─────────────────┐
│ Text Filter     │ -> Block: violence, adult themes, 
│ (LLM + Rules)   │    inappropriate language
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Image Filter    │ -> Block: NSFW, scary imagery,
│ (AWS/Azure      │    photorealistic violence
│  Vision API)    │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Audio Filter    │ -> Check TTS output for glitches,
│ (Manual Review  │    mispronunciations
│  Queue)         │
└─────────────────┘
```

### Kid-Safe Defaults
- All images must pass "child-friendly" style check
- No realistic weapons, blood, or frightening creatures
- Moral lessons must be positive and age-appropriate
- Music: no lyrics (instrumental only), upbeat tempo
- Max volume levels: narration -6dB, music -18dB, SFX -24dB

---

## 13. Deployment & Infrastructure

### Docker Compose (Local Development)
```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/storyreels
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
    volumes:
      - ./assets:/app/assets
    depends_on:
      - db
      - redis

  worker:
    build: ./backend
    command: celery -A tasks worker -l info -c 2
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/storyreels
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./assets:/app/assets
      - /dev/shm:/dev/shm  # Shared memory for multiprocessing
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: storyreels
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

volumes:
  postgres_data:
  redis_data:
```

### Production Deployment
- **Backend**: Railway / Render / Fly.io / AWS ECS
- **GPU Workers**: RunPod / Vast.ai / Lambda Labs (on-demand)
- **Storage**: Cloudflare R2 (S3-compatible, no egress fees)
- **CDN**: Cloudflare for video delivery
- **Database**: Supabase / Neon (serverless PostgreSQL)
- **Queue**: Upstash Redis (serverless)
- **Monitoring**: Sentry (errors) + Logtail (logs)

---

## 14. Cost Estimates (Per Story)

### Cloud API Route (5 scenes, 45s reel)

| Component | Unit | Rate | Cost |
|-----------|------|------|------|
| LLM (GPT-4) | 10K tokens | $0.03/1K | $0.30 |
| TTS (ElevenLabs) | 500 chars | $0.30/1K | $0.15 |
| Images (DALL-E 3) | 5 images | $0.04/image | $0.20 |
| Video (Runway) | 45s | $0.05/s | $2.25 |
| Music (AI gen) | 45s | $0.02/s | $0.90 |
| Storage/Transfer | 15MB | $0.10/GB | ~$0.00 |
| Compute | 5 min | $0.05/min | $0.25 |
| **Total** | | | **~$4.05/story** |

### Hybrid Route (Local GPU + Cloud APIs)
| Component | Cost |
|-----------|------|
| LLM | Local (free) or $0.10 |
| TTS | Local Coqui (free) |
| Images | Local SDXL (free, GPU cost) |
| Video | Local AnimateDiff (free, GPU cost) |
| Music | Uppbeat free tier |
| **Total** | **~$0.10-0.50/story** + GPU electricity |

---

## 15. Implementation Roadmap (Personal-Use Focus)

### Phase 1: MVP (Weeks 1-4)
- [x] Basic FastAPI backend with story upload
- [x] GPT-4 story parsing with JSON output
- [x] ElevenLabs TTS integration
- [x] DALL-E 3 image generation
- [x] MoviePy video compilation (Ken Burns only)
- [x] Simple React frontend for upload + download
- [x] SQLite database (single file)
- [x] Background music & SFX mixing
- [x] WebSocket real-time progress
- [x] Scene editor (manual tweak UI)

### Phase 2: Polish (Weeks 5-8)
- [ ] Scene editor UI (manual adjustments)
- [x] Subtitle word-by-word highlighting (karaoke)
- [ ] Background music integration
- [ ] Multiple visual themes (templates)
- [ ] PostgreSQL + Redis + Celery queue
- [ ] WebSocket progress tracking
- [ ] ~~User accounts + story history~~ (skip for personal use)

### Phase 3: Scale (Weeks 9-12)
- [ ] Local GPU worker support (ComfyUI)
- [ ] Character consistency (IP-Adapter)
- [ ] AI video generation (AnimateDiff/Runway)
- [ ] Arabic language full support
- [ ] Batch processing (multiple stories)
- [ ] Platform-specific exports (Reels/Shorts/TikTok)
- [ ] Analytics (views, engagement)

### Phase 4: Advanced (Months 4-6)
- [ ] Voice cloning (custom storyteller)
- [ ] Interactive elements (polls, quizzes)
- [ ] Auto-upload to social platforms
- [ ] A/B testing for thumbnails/titles
- [ ] Community template marketplace
- [ ] Mobile app (React Native)

---

## 16. Detailed Implementation Specs (Pending Items)

> This section contains actionable specs for the next items to build. Once implemented, move status to ✅ in §1.5.

---

### 16.1 WebSocket Real-Time Progress

**Status:** ✅ Implemented  
**Files to touch:** `backend/app/api/v1/ws.py`, `backend/app/tasks/story_tasks.py`, `frontend/src/pages/StoryDetail.tsx`, `frontend/src/hooks/useJobProgress.ts`

**Why:** Frontend currently polls `GET /stories/{id}` every 3s. WebSockets give instant progress updates and reduce server load.

**Backend Design:**
```
WS /api/v1/ws/jobs/{job_id}

Messages (server → client):
  {"type": "status",   "status": "processing", "stage": "parsing", "percent": 5}
  {"type": "scene",    "scene_id": "...", "kind": "image|audio", "url": "..."}
  {"type": "error",    "message": "..."}
  {"type": "complete", "download_url": "..."}
```

**Implementation Steps:**
1. Add `backend/app/api/v1/ws.py` with FastAPI `WebSocket` endpoint.
2. Maintain an in-memory `job_connections: dict[str, list[WebSocket]]` (sufficient for single-instance MVP; upgrade to Redis pub/sub for multi-worker later).
3. In `story_tasks.py`, after each stage, call `notify_job_progress(job_id, {...})`.
4. If no listeners, the notification is a no-op (no crash).
5. Frontend: open WS on StoryDetail mount, close on unmount. Fall back to HTTP polling if WS fails (eager degradation).

**Acceptance Criteria:**
- [ ] Dashboard shows progress bar moving without page refresh
- [ ] Scene images appear in the UI as soon as they are generated
- [ ] Reel video player appears instantly when status flips to `completed`
- [ ] Works across browser refreshes

---

### 16.2 Scene Editor UI

**Status:** ✅ Implemented  
**Files to touch:** `backend/app/api/v1/scenes.py`, `frontend/src/pages/StoryDetail.tsx`, `frontend/src/components/SceneEditor.tsx`

**Why:** LLM output is good but not perfect. Users need to tweak narration, visual prompts, and regenerate individual scenes before final render.

**Backend Design:**
```
PATCH /api/v1/scenes/{scene_id}
  Body: { narration_text?, visual_prompt?, duration_seconds?, subtitle_text? }
  Response: SceneResponse

POST /api/v1/scenes/{scene_id}/regenerate-image
  Body: { visual_prompt? }  # uses existing prompt if omitted
  Response: { image_url }

POST /api/v1/scenes/{scene_id}/regenerate-audio
  Body: { narration_text? }  # uses existing text if omitted
  Response: { audio_url }
```

**Frontend Design:**
- StoryDetail gets a new "Edit Scenes" toggle.
- Each scene card expands into an editor:
  - Narration textarea (2-sentence limit hint)
  - Visual prompt textarea
  - Duration slider (3–15s)
  - "Regenerate Image" / "Regenerate Audio" buttons with loading spinners
  - Live preview of image + audio side-by-side
- "Save Changes" commits all edits. "Render Final Video" uses the updated scenes.

**Acceptance Criteria:**
- [ ] User can edit narration and regenerate just that scene's audio
- [ ] User can edit visual prompt and regenerate just that scene's image
- [ ] Changes persist in DB and are used by the video compiler on next render
- [ ] Regenerating a single scene does not affect other scenes

---

### 16.3 Background Music & SFX Mixing

**Status:** ✅ Implemented  
**Files to touch:** `backend/app/services/video_compiler.py`, `backend/app/services/asset_generator.py`, `backend/app/core/config.py`

**Why:** Silent videos feel unfinished. Gentle instrumental music + sparse sound effects dramatically improve watch-through rate.

**Backend Design:**
```
AssetGenerator.generate_music(mood: str, duration: float) -> Path
  Strategy:
  1. If MUSIC_LOCAL_PATH has a matching file (e.g. "gentle_playful_60s.mp3"), use it.
  2. Else generate a simple ambient loop with MusicGen (fallback) or use a stock track.

AssetGenerator.get_sfx(sfx_name: str) -> Path
  Looks in SFX_LOCAL_PATH for "{sfx_name}.mp3" / ".wav".
  Built-in library: bird_chirp, wind, water, lion_roar, magical_chime, applause.

VideoCompiler.add_music_and_sfx(...)
  music_clip = AudioFileClip(music_path).with_volume_scaled(0.15)  # -18 dB
  narration_clip = scene.audio
  # Duck music when narration is loud (simple gate: -30 dB during speech)
  final_audio = CompositeAudioClip([narration_clip, music_clip])
  # SFX clips are mixed in at their trigger timestamps
```

**Music Library (local files):**
Place royalty-free instrumental tracks in `storage/music/`:
- `gentle_playful_60s.mp3` — acoustic guitar, 60-80 BPM
- `calm_dreamy_60s.mp3` — soft piano, 50-70 BPM
- `upbeat_happy_60s.mp3` — ukulele + bells, 90-110 BPM

**SFX Library (local files):**
Place short CC0 sounds in `storage/sfx/`:
- `bird_chirp.mp3`, `wind.mp3`, `water.mp3`, `lion_roar.mp3`, `magical_chime.mp3`

**Acceptance Criteria:**
- [ ] Every rendered video has background music matching the story's `music_mood`
- [ ] Music volume ducks during narration (audible but not competing)
- [ ] SFX play at scene trigger points
- [ ] Final audio does not clip (peak < -1 dB)

---

## 17. Key Libraries & Tools Reference

### Python Backend (Installed)
```
fastapi==0.110+       # Web framework
uvicorn==0.46+        # ASGI server
sqlalchemy==2.0+      # ORM
alembic==1.13+        # Migrations
celery==5.3+          # Task queue
redis==5.0+           # Broker/Cache
moviepy==2.1+         # Video editing (NOTE: v2 API is very different from v1)
pillow==10.2+         # Image processing
httpx==0.27+          # Async HTTP client
openai==1.14+         # GPT-4 / DALL-E 3 API
python-multipart      # File uploads
pydantic==2.6+        # Data validation
pydantic-settings     # Environment config
python-jose           # JWT auth (planned)
passlib               # Password hashing (planned)
python-bidi           # RTL text support (planned)
arabic-reshaper       # Arabic subtitle shaping (planned)
```

### Local AI Stack
```
comfyui              # Node-based image/video gen
automatic1111        # Stable Diffusion WebUI
ollama               # Local LLM runner
coqui-tts            # Local TTS (XTTS v2)
piper-tts            # Fast lightweight TTS
animate-diff         # Image-to-video animation
stable-video-diffusion  # Video generation
depth-anything-v2    # Depth estimation
ip-adapter           # Image prompt adapter
controlnet           # Image structure control
real-esrgan          # Image upscaling
```

### Frontend (Installed)
```
react==18.2+         # UI library
vite==5.1+           # Build tool (used instead of Next.js for MVP)
tailwindcss==3.4+    # Utility CSS
@tanstack/react-query # Data fetching / caching
axios==1.6+          # HTTP client
react-router-dom     # Client-side routing
lucide-react==0.344+ # Icons
clsx + tailwind-merge # Conditional class names
# Planned for later:
# shadcn/ui, zustand, socket.io-client, react-player, framer-motion
```

---

## 17. Example: Kalila & Dimna Story Flow

### Input
```
Title: The Lion and the Rabbit
Source: Kalila wa Dimna

A cruel lion was terrorizing the jungle. Every day, 
the animals had to send one of them as his meal. 
A clever rabbit devised a plan. He arrived late and 
told the lion another lion had challenged him. 
The furious lion followed the rabbit to a well. 
Seeing his own reflection, he attacked it and drowned. 
The jungle was freed through wisdom, not strength.

Moral: Intelligence defeats brute force.
```

### Parsed Scenes (5 scenes, 40s total)

| Scene | Narration | Visual | Duration | SFX |
|-------|-----------|--------|----------|-----|
| 1 | "A big lion ruled the jungle with fear." | Lion on rock, animals hiding | 7s | Lion roar, jungle ambience |
| 2 | "Each day, one animal had to be his dinner." | Sad animals lining up | 8s | Owl hoot, rustling leaves |
| 3 | "A small rabbit had a clever idea!" | Rabbit thinking, lightbulb moment | 7s | Magical chime |
| 4 | "He tricked the lion into fighting his own shadow." | Rabbit leading lion to well | 9s | Water splashing |
| 5 | "The jungle was safe. Smart thinking won!" | Animals celebrating, rabbit hero | 9s | Cheerful music swell |

### Final Output
- **Video**: 40s vertical reel
- **Style**: Watercolor children's book
- **Voice**: Warm female storyteller, gentle pace
- **Music**: Soft acoustic guitar, playful
- **Subtitles**: Large white text with black outline, word highlighting
- **Intro**: "Kalila & Dimna - The Lion and the Rabbit" (2s)
- **Outro**: "Moral: Intelligence defeats brute force" + subscribe CTA (3s)

---

## 18. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| API costs spiral | Implement caching, local fallback options, usage quotas |
| AI generates inappropriate images | Multi-layer safety filters, manual review queue for new themes |
| TTS mispronounces Arabic | Force diacritization, test voice samples, fallback voices |
| Video rendering fails | Retry logic, scene-level regeneration, graceful degradation |
| Copyright on generated content | Use commercial-safe models, document provenance, terms of service |
| Platform bans (automated content) | Human-in-the-loop approval, original story transformation |
| GPU scarcity for local setup | Cloud GPU on-demand, queue management, priority tiers |

---

## 19. Success Metrics

- **Generation time**: < 5 minutes per story (cloud) / < 30 minutes (local)
- **Cost per reel**: <$5 (cloud) / <$0.50 (hybrid)
- **Quality score**: > 4.0/5.0 from parent testers
- **Engagement**: > 60% watch-through rate on published reels
- **Safety**: 0 incidents of inappropriate content
- **Uptime**: > 99% for generation service

---

*Document Version: 1.0*
*Created: 2026-04-28*
*For: Automated Children's Story Reels Application*
