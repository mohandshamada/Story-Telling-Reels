# Story Reels — Automated Story-to-Video for Kids

Turn children's stories into short vertical video reels (9:16) ready for Instagram Reels, TikTok, and YouTube Shorts.

## Features

- **Story Parser** — GPT-4 breaks stories into kid-friendly scenes with narration and image prompts
- **TTS** — ElevenLabs cloud or XTTS v2 local (multilingual, voice cloning)
- **Image Generation** — DALL-E 3 cloud or ComfyUI + SDXL local (IP-Adapter for character consistency)
- **Video Compiler** — MoviePy 2.x with Ken Burns, karaoke word-by-word subtitles, RTL Arabic, music & SFX
- **Scene Editor** — Edit narration, visual prompts, regenerate individual scenes
- **Real-time Progress** — WebSocket live updates during generation
- **Auth** — JWT-based user accounts
- **Social Upload** — Scaffold for YouTube, Instagram, TikTok, Twitter

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (for GPT-4 parsing)
- ElevenLabs API key (for cloud TTS, optional if using XTTS)
- GPU optional — RTX 4090 recommended for local stack

### 1. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your keys
```

### 2. Run everything

```bash
docker-compose up --build
```

- **Frontend** → http://localhost:3000
- **API docs** → http://localhost:8000/docs
- **API** → http://localhost:8000

### 3. Create your first reel

1. Open http://localhost:3000
2. Register an account
3. Click **New Story**
4. Paste a children's story and hit **Generate Reel**
5. Watch scenes, images, and audio generate in real time
6. Download the final MP4 when ready

## Project Structure

```
storyelling-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/v1/              # REST + WebSocket endpoints
│   │   │   ├── auth.py          # JWT login/register
│   │   │   ├── stories.py       # Story CRUD + render trigger
│   │   │   ├── scenes.py        # Scene editor + regeneration
│   │   │   ├── jobs.py          # Job status + download
│   │   │   ├── voices.py        # Voice profile management
│   │   │   ├── upload.py        # Social platform upload
│   │   │   └── ws.py            # WebSocket progress
│   │   ├── core/config.py       # Settings (provider switching)
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic models
│   │   ├── services/            # Business logic
│   │   │   ├── story_parser.py      # GPT-4 scene parser
│   │   │   ├── asset_generator.py   # TTS + image (cloud/local switch)
│   │   │   ├── video_compiler.py    # MoviePy assembler (karaoke, RTL)
│   │   │   ├── arabic_utils.py      # Normalization, tashkeel, RTL
│   │   │   ├── auth_service.py      # JWT + password hashing
│   │   │   ├── comfyui_client.py    # Local SDXL/IP-Adapter
│   │   │   ├── xtts_service.py      # Local multilingual TTS
│   │   │   ├── social_upload.py     # YouTube/IG/TikTok/Twitter
│   │   │   └── redis_pubsub.py      # WS progress bridge
│   │   └── tasks/               # Celery background jobs
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, NewStory, StoryDetail, Auth
│   │   ├── hooks/               # useJobProgress (WebSocket)
│   │   └── lib/                 # API client, Auth context
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Provider Switching (Cloud vs Local)

Control which AI engines to use via environment variables:

```bash
# Image generation
IMAGE_PROVIDER=dalle        # or "comfyui" for local GPU

# TTS / Voice
TTS_PROVIDER=elevenlabs     # or "xtts" for local GPU voice cloning
```

### Cloud Mode (default)
- **Images:** DALL-E 3 (~$0.04/image)
- **TTS:** ElevenLabs v2 (~$0.30/1K chars)
- **Cost:** ~$4/story

### Local GPU Mode
Requires RTX 4090 (or similar) with ~16GB VRAM.

**1. Install XTTS v2**

```bash
cd backend
source .venv/bin/activate
pip install TTS

# Place a reference voice sample
mkdir -p storage/voices
cp your_voice.wav storage/voices/

# Set env
export TTS_PROVIDER=xtts
export XTTS_DEFAULT_SPEAKER_WAV=storage/voices/your_voice.wav
```

**2. Install ComfyUI**

```bash
# Option A: Native
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
python main.py

# Option B: Docker (see docker-compose.yml, uncomment comfyui service)
docker-compose up comfyui
```

Download models:
- SDXL Base: `sd_xl_base_1.0.safetensors` → `ComfyUI/models/checkpoints/`
- IP-Adapter: `ip-adapter_sd15.safetensors` → `ComfyUI/models/ipadapter/`

**3. Switch providers**

```bash
export IMAGE_PROVIDER=comfyui
export COMFYUI_URL=http://localhost:8188
export TTS_PROVIDER=xtts
```

**Cost in local mode:** ~$0.10-0.50/story (mostly electricity)

## Manual Development (no Docker)

### Backend

```bash
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e "."

# Run API
uvicorn app.main:app --reload --port 8000

# Run Celery worker
celery -A app.tasks.story_tasks worker -l info -c 1
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Celery, Redis |
| Cloud AI | OpenAI GPT-4, DALL-E 3, ElevenLabs |
| Local AI | ComfyUI + SDXL + IP-Adapter, Coqui XTTS v2 |
| Video | MoviePy 2.x, FFmpeg, Pillow |
| Frontend | React 18, Vite, Tailwind CSS, TanStack Query |
| DevOps | Docker Compose, PostgreSQL, Redis |

## License

MIT
