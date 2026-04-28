# Story Reels — Automated Story-to-Video for Kids

Turn children's stories into short vertical video reels (9:16) ready for Instagram Reels, TikTok, and YouTube Shorts.

## Features (Phase 1 MVP)

- **Story Parser** — GPT-4 breaks stories into kid-friendly scenes with narration and image prompts
- **TTS** — ElevenLabs multilingual voices
- **Image Generation** — DALL-E 3 with consistent watercolor/3D/flat styles
- **Video Compiler** — MoviePy with Ken Burns effect, subtitles, and title/outro cards
- **Web UI** — React + Tailwind for uploading stories and monitoring progress

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- ElevenLabs API key (optional — falls back to placeholder in dev)

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
2. Click **New Story**
3. Paste a children's story and hit **Generate Reel**
4. Watch scenes, images, and audio generate in real time
5. Download the final MP4 when ready

## Project Structure

```
storyelling-AI/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── api/v1/              # REST endpoints
│   │   ├── core/config.py       # Settings
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── story_parser.py      # GPT-4 scene parser
│   │   │   ├── asset_generator.py   # TTS + image gen
│   │   │   └── video_compiler.py    # MoviePy assembler
│   │   └── tasks/               # Celery background jobs
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/               # Dashboard, NewStory, StoryDetail
│   │   └── lib/api.ts           # API client
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```

## Manual Development (no Docker)

### Backend

```bash
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e "."
uvicorn app.main:app --reload --port 8000

# In another terminal:
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
| Backend | Python 3.12, FastAPI, SQLAlchemy, Celery, Redis |
| AI APIs | OpenAI GPT-4, DALL-E 3, ElevenLabs |
| Video | MoviePy 2.x, FFmpeg, Pillow |
| Frontend | React 18, Vite, Tailwind CSS, TanStack Query |
| DevOps | Docker Compose |

## Roadmap

See [`roadmap.md`](roadmap.md) for the full architecture spec, data models, and planned phases.

| Phase | Focus |
|-------|-------|
| **1** | MVP: FastAPI, GPT-4, ElevenLabs, DALL-E 3, MoviePy, React UI |
| **2** | Scene editor, subtitles, background music, PostgreSQL + Celery |
| **3** | Local GPU stack (ComfyUI, XTTS v2), Arabic full support |
| **4** | Voice cloning, interactive elements, auto-upload, mobile app |

## License

MIT
