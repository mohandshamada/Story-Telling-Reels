# Story Reels — Automated Story-to-Video for Kids

Turn children's stories into short vertical video reels (9:16) ready for Instagram Reels, TikTok, and YouTube Shorts.

## Features

- **Story Parser** — Multi-provider LLM support: OpenAI GPT-4, Ollama (local), LiteLLM (100+ providers), and Hybrid auto-fallback
- **TTS** — ElevenLabs cloud or XTTS v2 local (multilingual, voice cloning)
- **Image Generation** — DALL-E 3 cloud or ComfyUI + SDXL local (IP-Adapter for character consistency)
- **Video Compiler** — MoviePy 2.x with Ken Burns, karaoke word-by-word subtitles, RTL Arabic, music & SFX
- **Scene Editor** — Edit narration, visual prompts, regenerate individual scenes
- **Real-time Progress** — WebSocket live updates during generation
- **Auth** — JWT-based user accounts with proper error handling
- **Social Upload** — Scaffold for YouTube, Instagram, TikTok, Twitter
- **Provider Switching** — Choose cloud, local, or hybrid AI for every pipeline (LLM, TTS, Images)

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Manual Installation](#manual-installation)
3. [Provider Configuration](#provider-configuration)
   - [LLM Providers](#llm-providers)
   - [TTS / Voice Providers](#tts--voice-providers)
   - [Image Generation Providers](#image-generation-providers)
4. [How to Use](#how-to-use)
5. [Project Structure](#project-structure)
6. [Tech Stack](#tech-stack)
7. [Troubleshooting](#troubleshooting)
8. [License](#license)

---

## Quick Start (Docker)

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (for GPT-4 parsing) **OR** Ollama for local LLM
- ElevenLabs API key (for cloud TTS, optional if using XTTS)
- GPU optional — RTX 4090 recommended for local stack

### 1. Clone and configure

```bash
git clone https://github.com/mohandshamada/Story-Telling-Reels.git
cd Story-Telling-Reels
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (see Provider Configuration below)
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
4. Paste a children's story
5. Select your preferred **AI Story Parser** (OpenAI, LiteLLM, Ollama, or Hybrid)
6. Hit **Generate Reel**
7. Watch scenes, images, and audio generate in real time
8. Download the final MP4 when ready

---

## Manual Installation

### Backend

**Requirements:** Python 3.11+, `uv` (recommended) or `pip`

```bash
cd backend

# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e "."

# Run database migrations (SQLite auto-creates on first run)
# For PostgreSQL, use Alembic: alembic upgrade head

# Run API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Run Celery worker** (requires Redis):
```bash
# Terminal 2
cd backend
source .venv/bin/activate
celery -A app.tasks.story_tasks worker -l info -c 1
```

### Frontend

**Requirements:** Node.js 20+, npm

```bash
cd frontend
npm install
npm run dev
```

The dev server starts on http://localhost:3000 and proxies `/api` to the backend.

---

## Provider Configuration

All providers are controlled via `backend/.env`. Copy from `.env.example` and fill in your keys.

### LLM Providers (Story Parser)

The story parser breaks your text into scenes. You can switch between 4 modes:

| Provider | Type | Setup |
|----------|------|-------|
| `openai` | Cloud | Set `OPENAI_API_KEY` |
| `litellm` | Cloud/Proxy | Set `LITELLM_API_KEY` + `LITELLM_MODEL` |
| `ollama` | Local (free) | Install Ollama, run `ollama pull llama3` |
| `hybrid` | Auto-fallback | Tries cloud first, falls back to local |

#### OpenAI (default)
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

#### LiteLLM — connect 100+ providers
LiteLLM is a unified API for OpenAI, Anthropic, Google, Azure, Groq, Cohere, and more.

```bash
LLM_PROVIDER=litellm
LITELLM_MODEL=openai/gpt-4o-mini
LITELLM_API_KEY=sk-...
```

**Popular model strings:**
```bash
# Anthropic Claude
LITELLM_MODEL=anthropic/claude-3-sonnet-20240229
LITELLM_API_KEY=sk-ant-...

# Google Gemini
LITELLM_MODEL=gemini/gemini-1.5-flash
LITELLM_API_KEY=AIza...

# Groq (fast & cheap)
LITELLM_MODEL=groq/llama3-70b-8192
LITELLM_API_KEY=gsk-...

# Azure OpenAI
LITELLM_MODEL=azure/gpt-4o
LITELLM_API_KEY=your-azure-key
LITELLM_BASE_URL=https://your-resource.openai.azure.com/

# Local via LiteLLM
LITELLM_MODEL=ollama/llama3
LITELLM_BASE_URL=http://localhost:11434
```

#### Ollama (local, no API costs)
```bash
# 1. Install Ollama: https://ollama.com
# 2. Pull a model
ollama pull llama3
# 3. Start Ollama (usually auto-runs on port 11434)
ollama serve

# 4. Configure app
LLM_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

#### Hybrid (recommended for reliability)
Tries providers in order until one succeeds:
```bash
LLM_PROVIDER=hybrid
HYBRID_LLM_PRIORITY=openai,litellm,ollama
```

**How it works:**
1. First tries OpenAI (fast, high quality)
2. If OpenAI fails, tries LiteLLM (your configured backup)
3. If LiteLLM fails, tries Ollama (local, free, always available)

You can also override the LLM provider **per-story** in the frontend UI.

---

### TTS / Voice Providers (Narration)

| Provider | Type | Setup |
|----------|------|-------|
| `elevenlabs` | Cloud | Set `ELEVENLABS_API_KEY` |
| `xtts` | Local GPU | Install Coqui TTS, provide speaker WAV |

#### ElevenLabs (default, high quality)
```bash
TTS_PROVIDER=elevenlabs
ELEVENLABS_API_KEY=your-key
ELEVENLABS_VOICE_ID=XB0fDUnXU5powFXDhCwa
```
- Get API key: https://elevenlabs.io/app/settings/api-keys
- Get voice IDs: https://elevenlabs.io/app/voice-library
- Supports 29 languages with `eleven_multilingual_v2`

#### XTTS v2 (local, voice cloning)
Requires GPU with ~8GB VRAM.

```bash
# 1. Install TTS engine
cd backend
source .venv/bin/activate
pip install TTS

# 2. Place a reference voice sample
mkdir -p storage/voices
cp your_voice.wav storage/voices/

# 3. Configure
TTS_PROVIDER=xtts
XTTS_DEFAULT_SPEAKER_WAV=storage/voices/your_voice.wav
XTTS_MODEL_PATH=tts_models/multilingual/multi-dataset/xtts_v2
```

XTTS supports 16 languages including Arabic, and clones the speaker's voice from the reference WAV.

---

### Image Generation Providers

| Provider | Type | Setup |
|----------|------|-------|
| `dalle` | Cloud | Set `OPENAI_API_KEY` |
| `comfyui` | Local GPU | Run ComfyUI with SDXL models |

#### DALL-E 3 (default)
```bash
IMAGE_PROVIDER=dalle
OPENAI_API_KEY=sk-...
DALLE_MODEL=dall-e-3
DALLE_SIZE=1024x1792
```

#### ComfyUI (local GPU)
Requires GPU with ~12GB VRAM.

```bash
# Option A: Native
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
pip install -r requirements.txt
python main.py

# Option B: Docker (uncomment in docker-compose.yml)
docker-compose up comfyui
```

Download models:
- SDXL Base → `ComfyUI/models/checkpoints/sd_xl_base_1.0.safetensors`
- IP-Adapter → `ComfyUI/models/ipadapter/ip-adapter_sd15.safetensors`

```bash
IMAGE_PROVIDER=comfyui
COMFYUI_URL=http://localhost:8188
```

---

## How to Use

### 1. Register / Login

Open http://localhost:3000 and create an account. The app uses JWT tokens stored in `localStorage`.

### 2. Create a New Story

Click **New Story** and fill in:
- **Title** — e.g., "The Brave Little Mouse"
- **Story Text** — paste your full story
- **Language** — `en`, `ar`, `fr`, `es`
- **Target Duration** — 15-90 seconds
- **Visual Theme** — Watercolor, 3D Cartoon, or Flat Vector
- **Voice Style** — Warm Female or Gentle Male storyteller
- **Music Mood** — Gentle & Playful, Calm & Dreamy, Upbeat & Happy
- **AI Story Parser** — OpenAI, LiteLLM, Ollama, or Hybrid
- **Moral Lesson** — optional (appears at the end of the video)

### 3. Monitor Progress

After submitting, you'll see:
- Real-time progress bar
- Live scene generation (images + audio)
- WebSocket status indicator ("Live" when connected)

### 4. Edit Scenes

Once parsing completes, click into any scene to:
- Edit narration text
- Edit visual prompts
- Regenerate the image
- Regenerate the audio
- Adjust scene duration

### 5. Download

When the status shows **completed**, click **Download MP4** to get your 1080×1920 vertical video.

---

## Project Structure

```
Story-Telling-Reels/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app factory
│   │   ├── api/v1/              # REST + WebSocket endpoints
│   │   │   ├── auth.py          # JWT login/register
│   │   │   ├── stories.py       # Story CRUD + render trigger
│   │   │   ├── scenes.py        # Scene editor + regeneration
│   │   │   ├── jobs.py          # Job status + download
│   │   │   ├── voices.py        # Voice profile management
│   │   │   ├── upload.py        # Social platform upload
│   │   │   └── ws.py            # WebSocket progress (Redis)
│   │   ├── core/config.py       # Settings (provider switching)
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── services/            # Business logic
│   │   │   ├── story_parser.py      # Multi-provider LLM parser
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
│   ├── celeryconfig.py
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, NewStory, StoryDetail, Auth
│   │   ├── hooks/               # useJobProgress (WebSocket)
│   │   └── lib/                 # API client, Auth context
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0, Celery, Redis |
| LLM | OpenAI GPT-4, LiteLLM (100+ providers), Ollama (local) |
| Cloud AI | DALL-E 3, ElevenLabs |
| Local AI | ComfyUI + SDXL + IP-Adapter, Coqui XTTS v2 |
| Video | MoviePy 2.x, FFmpeg, Pillow |
| Frontend | React 18, Vite, Tailwind CSS, TanStack Query |
| DevOps | Docker Compose, PostgreSQL, Redis |

---

## Troubleshooting

### "Username or email already taken" on first registration
This was a frontend bug that showed a hardcoded message for **any** error. It's now fixed — the real backend error (network issue, validation error, etc.) is displayed.

### Backend crashes with "Connection refused" to Redis
Redis is required for Celery background jobs. Without it:
- Stories still save to the database
- The job status shows "failed" with: "Background worker unavailable. Please start Redis or run docker-compose up."

**Fix:** Start Redis:
```bash
# With Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or native
redis-server
```

### Registration returns 500 / "password cannot be longer than 72 bytes"
This was a `passlib` + `bcrypt` compatibility bug. Fixed by pinning `bcrypt<4.0`.

**Fix:** Reinstall dependencies:
```bash
cd backend
source .venv/bin/activate
uv pip install -e "."
```

### Frontend shows blank page / build errors
The original repo was missing `frontend/src/lib/api.ts` and `auth.tsx`. These are now included.

**Fix:**
```bash
cd frontend
npm install
npm run build
```

### Ollama connection refused
Make sure Ollama is running:
```bash
ollama serve
# or
ollama run llama3
```

### CORS errors in browser
The backend allows all origins (`*`) with credentials. If you see CORS errors, check that the backend is running on port 8000 and the frontend proxy is configured correctly in `frontend/vite.config.ts`.

---

## License

MIT
