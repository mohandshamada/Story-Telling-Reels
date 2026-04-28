# AGENTS.md — Automated Story-to-Reels App for Kids

> **Current State: Planning / Roadmap Only**  
> This repository currently contains no source code, build configuration, or runtime artifacts. The entire project specification lives in `roadmap.md`. Treat that document as the single source of truth for architecture, data models, API design, and implementation phases.

---

## 1. Project Overview

An end-to-end pipeline that accepts a text story (e.g. *Kalila wa Dimna* fables or other children's stories) and automatically produces short vertical video reels (9:16, 15–60 seconds) ready for Instagram Reels, TikTok, and YouTube Shorts.

Planned outputs per story:
- **Narration** — TTS in a child-friendly voice
- **Visuals** — AI-generated images/animations per scene
- **Subtitles/Captions** — large, readable, kid-safe fonts
- **Background music & SFX** — gentle, instrumental, volume-ducked
- **Final video** — 1080×1920 MP4, H.264, 30 fps

A key differentiator is **multilingual voice cloning**: the same narrator voice profile can speak multiple languages (including Arabic) while preserving timbre and style.

---

## 2. Project Structure (Today)

```
storyelling-AI/
└── roadmap.md          # Complete architecture & implementation spec
```

There are **no other files**. No `pyproject.toml`, `package.json`, `Cargo.toml`, `Dockerfile`, source directories, or tests exist yet.

---

## 3. Technology Stack (Planned)

### Backend
- **Framework**: Python + FastAPI
- **ORM / Migrations**: SQLAlchemy + Alembic
- **Task Queue**: Celery + Redis
- **Video Editing**: MoviePy + FFmpeg (`ffmpeg-python` bindings)
- **Image Processing**: Pillow
- **HTTP Client**: httpx (async)
- **Validation**: Pydantic v2
- **Auth**: python-jose + passlib

### Cloud APIs (MVP / fallback)
- **LLM**: OpenAI GPT-4 (structured JSON output)
- **TTS**: ElevenLabs API
- **Image Gen**: DALL-E 3
- **Storage**: AWS S3 or Cloudflare R2

### Local AI Stack (cost-reduction / privacy mode)
- **LLM**: Ollama (Llama 3) or Mistral 7B
- **TTS**: Coqui XTTS v2 (cross-lingual, supports Arabic)
- **Image Gen**: ComfyUI + SDXL + IP-Adapter (character consistency)
- **Video Gen**: AnimateDiff / Stable Video Diffusion
- **Depth**: Depth Anything v2 (parallax)
- **Upscale**: Real-ESRGAN

### Frontend
- **Framework**: Next.js 14 (App Router) or React + Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **Data Fetching**: TanStack Query + Axios
- **Real-time**: Socket.io-client
- **Upload**: react-dropzone
- **Video Player**: ReactPlayer or native HTML5

### Database
- **Primary**: PostgreSQL 15+
- **Cache / Broker**: Redis 7+
- **Local dev**: SQLite acceptable for Phase 1 MVP only

### Infrastructure
- **Local Dev**: Docker Compose (api, worker, db, redis, frontend)
- **Production Backend**: Railway / Render / Fly.io / AWS ECS
- **GPU Workers**: RunPod / Vast.ai / Lambda Labs (on-demand)
- **CDN**: Cloudflare
- **Monitoring**: Sentry + Logtail

---

## 4. Code Organization (Target)

The roadmap proposes the following module layout (not yet implemented):

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── api/
│   │   ├── v1/
│   │   │   ├── stories.py   # CRUD + processing endpoints
│   │   │   ├── jobs.py      # Render job status & download
│   │   │   ├── templates.py # Reusable style templates
│   │   │   └── voice_profiles.py  # Multilingual voice management
│   │   └── deps.py          # Dependency injection (DB, config)
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (env vars)
│   │   ├── security.py      # JWT, password hashing
│   │   └── exceptions.py    # Custom HTTP exceptions
│   ├── models/
│   │   ├── story.py         # SQLAlchemy Story, Scene, RenderJob
│   │   ├── template.py
│   │   ├── asset.py
│   │   └── voice_profile.py
│   ├── schemas/
│   │   ├── story.py         # Pydantic request/response models
│   │   ├── scene.py
│   │   └── job.py
│   ├── services/
│   │   ├── story_parser.py      # LLM-based chunking & prompt gen
│   │   ├── asset_generator.py   # TTS + image + animation generation
│   │   ├── video_compiler.py    # MoviePy composition & render
│   │   ├── multilingual_voice_manager.py  # XTTS/ElevenLabs voice profiles
│   │   └── arabic_utils.py      # Normalization, tashkeel, RTL helpers
│   ├── tasks/
│   │   └── story_tasks.py   # Celery tasks for end-to-end pipeline
│   ├── db/
│   │   ├── session.py       # SQLAlchemy session & engine
│   │   └── base.py          # Declarative base
│   └── utils/
│       └── storage.py       # S3/R2 upload helpers
├── celeryconfig.py
├── alembic/
├── tests/
├── Dockerfile
└── requirements.txt / pyproject.toml

frontend/
├── app/                     # Next.js App Router
├── components/
│   └── ui/                  # shadcn/ui components
├── lib/
│   ├── api.ts               # Axios + TanStack Query hooks
│   └── utils.ts             # cn() helper, etc.
├── pages or route groups:
│   ├── (dashboard)/
│   ├── stories/
│   ├── templates/
│   └── settings/
├── public/
├── Dockerfile
└── package.json
```

---

## 5. Build & Development Commands (Planned)

Until a build system is introduced, these are the intended commands based on the roadmap:

### Local Development (Docker Compose)
```bash
# Start full stack
docker-compose up --build

# API available at http://localhost:8000
# Frontend available at http://localhost:3000
# Docs (auto-generated) at http://localhost:8000/docs
```

### Backend (manual)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt   # or pip install -e .

# Run API
uvicorn app.main:app --reload --port 8000

# Run Celery worker
celery -A tasks worker -l info -c 2

# Run database migrations
alembic upgrade head
```

### Frontend (manual)
```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm run lint
```

---

## 6. Testing Strategy (Planned)

No tests exist yet. The roadmap does not prescribe a specific framework, so standard Python/JS tooling is recommended:

- **Backend**: pytest + pytest-asyncio + httpx (for FastAPI TestClient)
- **Frontend**: Vitest + React Testing Library (if Next.js) or Jest
- **E2E**: Playwright for critical user flows (upload story → render → download)

Priority test areas:
1. Story parser JSON schema validation and retry logic
2. VideoCompiler scene composition (without hitting real APIs)
3. Arabic text normalization and diacritization
4. MultilingualVoiceManager language support matrix
5. Celery task idempotency and failure recovery

---

## 7. Data Models & Key Schemas

Refer to `roadmap.md` §5 and §7 for full schemas. Critical entities:

- **Story** — input text, language, target duration, visual theme, voice style, music mood
- **Scene** — sequence number, narration text, visual prompt, image/audio URLs, animation type, SFX triggers, subtitle style
- **RenderJob** — status tracker with progress percent, current stage, output URL
- **Template** — reusable style presets (visual theme + voice + music + subtitle style)
- **Asset** — deduplicated generated media (prompt hash for cache lookup)
- **VoiceProfile** — speaker embedding, TTS engine, supported languages, fine-tuning status
- **StoryTranslation / SceneTranslation** — per-language text and audio

All tables use UUID primary keys. JSONB columns store flexible metadata (subtitle styles, SFX triggers).

---

## 8. API Endpoints (Planned)

Refer to `roadmap.md` §6 and §13 for the full list. Key routes:

```
POST   /api/v1/stories
GET    /api/v1/stories/{story_id}
GET    /api/v1/stories/{story_id}/scenes
POST   /api/v1/stories/{story_id}/regenerate-scene/{scene_id}
GET    /api/v1/jobs/{job_id}
GET    /api/v1/jobs/{job_id}/download
POST   /api/v1/templates
GET    /api/v1/templates
POST   /api/v1/voice-profiles
POST   /api/v1/voice-profiles/{id}/fine-tune
POST   /api/v1/stories/{story_id}/translate
POST   /api/v1/stories/{story_id}/render-multilingual
GET    /api/v1/stories/{story_id}/versions
WS     /api/v1/ws/jobs/{job_id}       # real-time progress
```

---

## 9. Security & Safety Considerations

### Content Safety (Multi-layer)
1. **Text Filter** — LLM + rule-based blocklist for violence, adult themes, inappropriate language
2. **Image Filter** — AWS Rekognition / Azure Content Safety for NSFW / scary imagery
3. **Audio Filter** — manual review queue for TTS glitches and mispronunciations

### Kid-Safe Defaults
- All images must pass a "child-friendly" style check
- No realistic weapons, blood, or frightening creatures
- Moral lessons must be positive and age-appropriate
- Background music: instrumental only, no lyrics, 60–80 BPM
- Max volume levels: narration -6 dB, music -18 dB, SFX -24 dB

### Secrets Management
- API keys (OpenAI, ElevenLabs, AWS) must be injected via environment variables
- Never commit `.env` files
- Use Pydantic `Settings` with `secrets_dir` support for containerized deployments

---

## 10. Implementation Roadmap (From `roadmap.md`)

| Phase | Duration | Focus |
|-------|----------|-------|
| **Phase 1: MVP** | Weeks 1–4 | FastAPI backend, GPT-4 parsing, ElevenLabs TTS, DALL-E 3 images, MoviePy compilation (Ken Burns), simple React frontend, SQLite |
| **Phase 2: Polish** | Weeks 5–8 | Scene editor UI, subtitles, background music, visual themes, PostgreSQL + Redis + Celery, WebSocket progress, user accounts |
| **Phase 3: Scale** | Weeks 9–12 | Local GPU worker (ComfyUI), IP-Adapter character consistency, AI video generation, Arabic full support, batch processing, platform exports |
| **Phase 4: Advanced** | Months 4–6 | Voice cloning, interactive elements, auto-upload to social platforms, A/B testing, community templates, mobile app |

**Current status**: Pre-Phase 1. No code has been written.

---

## 11. Arabic / Multilingual Specifics

- **Language detection**: auto-detect AR/EN input; allow manual override
- **Arabic normalization**: remove tatweel (kashida), normalize alef variants
- **Diacritization (tashkeel)**: required before TTS for Arabic. Use `camel-tools` or Farasa API. Cache diacritized results.
- **RTL subtitles**: MoviePy RTL support requires `arabic-reshaper` + `python-bidi` + PIL/Pillow
- **Cross-lingual voice**: XTTS v2 recommended for local GPU (16 languages, native Arabic support). ElevenLabs v3 is the cloud alternative.
- **Text expansion**: Arabic is ~30 % shorter than English; adjust subtitle font size and scene duration per language

---

## 12. Cost & Performance Targets

| Metric | Cloud Target | Hybrid Target |
|--------|-------------|---------------|
| Generation time | < 5 min / story | < 30 min / story |
| Cost per reel | < $5 | < $0.50 |
| Quality score | > 4.0 / 5.0 (parent testers) | > 4.0 / 5.0 |
| Watch-through rate | > 60 % | > 60 % |
| Safety incidents | 0 | 0 |
| Uptime | > 99 % | > 99 % |

---

## 13. How to Start Contributing

1. Read `roadmap.md` in full — it is the authoritative specification.
2. Pick a Phase 1 component (backend scaffold, parser service, or frontend upload page).
3. Introduce `pyproject.toml` (or `requirements.txt`) and `package.json` before writing application code.
4. Add Docker Compose early so the full stack can be spun up locally.
5. Write tests for any new service module before moving to the next.
6. Update this `AGENTS.md` as soon as real files, conventions, or commands are established.

---

*Document Version: 1.0*  
*Based on roadmap.md v1.0 (2026-04-28)*
