# Installation & Bug Fixes Log

**Date:** 2026-04-28

## Summary

Installed the Story Reels application (backend + frontend), identified and fixed multiple missing dependencies, missing source files, and code bugs that prevented the app from building or running. Also added multi-provider LLM support (OpenAI, Ollama, LiteLLM, Hybrid) with frontend integration.

---

## 1. Backend Fixes

### 1.1 Missing `email-validator` dependency
**File:** `backend/pyproject.toml`
**Issue:** Pydantic v2 `EmailStr` type (used in `app/schemas/auth.py`) requires `email-validator` to be installed. Without it, importing the FastAPI app fails with:
```
ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
```
**Fix:** Added `email-validator>=2.0.0` to the `dependencies` list in `pyproject.toml`.

### 1.2 `story_parser.py` — undefined `language` variable
**File:** `backend/app/services/story_parser.py`
**Issue:** The `_parse_json` method referenced a `language` variable that was not in its scope. The variable was only available as a parameter to the `parse` method, but `_parse_json` did not receive it, which would cause a `NameError` at runtime when parsing Arabic stories.
**Fix:**
- Added `language: str = "en"` parameter to `_parse_json` method signature.
- Updated the call site in `parse` to pass `language=language`: `return self._parse_json(content, language=language)`.

### 1.3 `video_compiler.py` — misplaced import
**File:** `backend/app/services/video_compiler.py`
**Issue:** The import `from moviepy import concatenate_audioclips` was located at the very bottom of the file (line 369) instead of the top-level imports section.
**Fix:** Moved `concatenate_audioclips` into the top-level `from moviepy import (...)` block and removed the duplicate import at the bottom of the file.

### 1.4 Backend crashed on story creation when Redis is unavailable
**File:** `backend/app/api/v1/stories.py`
**Issue:** Calling `process_story.delay(story.id)` triggered a Celery connection to Redis. When Redis is not running (local dev without Docker), this raised a `RuntimeError` and crashed the API with HTTP 500, making the frontend appear completely broken.
```
RuntimeError: Retry limit exceeded while trying to reconnect to the Celery result store backend.
```
**Fix:** Created a `_dispatch_task()` helper that wraps `process_story.delay()` in a try/except. If Celery/Redis is unreachable, the job is updated to status `failed` with a helpful error message, but the API returns HTTP 201 with the story data so the frontend doesn't crash.

### 1.5 WebSocket endpoint crashed when Redis is unavailable
**File:** `backend/app/api/v1/ws.py`
**Issue:** The WebSocket endpoint immediately tried to subscribe to Redis pub/sub on connection. Without Redis, this raised an unhandled exception and crashed the WebSocket.
**Fix:** Wrapped `redis_pubsub.subscribe()` in a try/except. If Redis is unreachable, the server sends a graceful error message to the client and closes the WebSocket cleanly.

### 1.6 `redis_pubsub.py` publish crashed on connection failure
**File:** `backend/app/services/redis_pubsub.py`
**Issue:** `publish()` let Redis connection exceptions bubble up, which could crash the background task pipeline.
**Fix:** Wrapped the publish operation in a try/except that logs the failure at debug level instead of crashing.

### 1.7 `passlib` incompatible with `bcrypt>=4.0`
**File:** `backend/pyproject.toml`
**Issue:** `passlib==1.7.4` has a known compatibility bug with `bcrypt>=4.0` (and 5.0). The internal `detect_wrap_bug` check triggers:
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
```
This caused user registration to return HTTP 500.
**Fix:** Pinned `bcrypt>=3.1.0,<4.0` in `pyproject.toml` to ensure a passlib-compatible bcrypt version is installed.

---

## 2. Frontend Fixes

### 2.1 Missing `frontend/src/lib/api.ts`
**File:** `frontend/src/lib/api.ts` (did not exist)
**Issue:** Multiple components import API functions and types from `./lib/api` or `../lib/api`. The file was completely missing, causing TypeScript build errors such as:
```
error TS2307: Cannot find module '../lib/api' or its corresponding type declarations.
```
**Fix:** Created `frontend/src/lib/api.ts` with:
- `request<T>` helper with Bearer token auth header injection
- TypeScript interfaces: `Story`, `StoryInput`, `Scene`, `User`, `AuthResponse`
- API functions: `fetchStories`, `createStory`, `fetchStory`, `fetchScenes`, `updateScene`, `regenerateSceneImage`, `regenerateSceneAudio`, `downloadUrl`, `login`, `register`

### 2.2 Missing `frontend/src/lib/auth.tsx`
**File:** `frontend/src/lib/auth.tsx` (did not exist)
**Issue:** `App.tsx`, `main.tsx`, and `Auth.tsx` import `useAuth` and `AuthProvider` from `./lib/auth`. The file was completely missing, causing TypeScript build errors.
**Fix:** Created `frontend/src/lib/auth.tsx` with:
- `AuthContext` using React Context API
- `AuthProvider` component that persists token/user to `localStorage`
- `useAuth()` hook that returns `{ user, login, logout }`

### 2.3 `StoryDetail.tsx` — `setTimeout` side effect during render
**File:** `frontend/src/pages/StoryDetail.tsx`
**Issue:** A `setTimeout` call was placed directly in the component body (lines 221–226), which is a React anti-pattern. It scheduled `invalidateQueries` on every render when `wsData.type` was `"complete"` or `"scene"`, causing potential infinite re-render loops and stale timer leaks.
**Fix:** Wrapped the logic in a `useEffect` hook with proper cleanup (`clearTimeout` in the return function) and added `wsData`, `id`, and `queryClient` to the dependency array.

### 2.4 Missing `vite.svg` caused 404 on page load
**File:** `frontend/index.html`
**Issue:** The HTML referenced `/vite.svg` as a favicon, but the file did not exist (no `public/` directory), causing an unnecessary 404 on every page load.
**Fix:** Removed the `<link rel="icon" ... href="/vite.svg" />` line from `index.html`.

### 2.5 Auth error messages were hardcoded and misleading
**Files:** `frontend/src/pages/Auth.tsx`, `frontend/src/lib/api.ts`
**Issue:** Both login and register pages showed static error messages ("Invalid username or password" / "Username or email already taken") for **any** mutation failure, masking the real backend error. Additionally, `api.ts` threw `new Error(errText)` where `errText` was raw JSON, so the user saw `[object Object]` or unreadable JSON in the UI.
**Fix:**
- Updated `api.ts` `request()` to parse FastAPI's JSON error body and throw `Error(errJson.detail)` when available.
- Updated `Auth.tsx` `LoginPage` and `RegisterPage` to render `mutation.error.message` dynamically instead of hardcoded strings.

---

## 3. New Feature: Multi-Provider LLM Support

### 3.1 Backend config for LLM providers
**File:** `backend/app/core/config.py`
**Changes:** Added new settings following the existing `IMAGE_PROVIDER` / `TTS_PROVIDER` pattern:
- `LLM_PROVIDER: str = "openai"` — default provider
- `OLLAMA_URL: str = "http://localhost:11434"` — local Ollama endpoint
- `OLLAMA_MODEL: str = "llama3"` — local model name
- `LITELLM_API_KEY: str = ""`, `LITELLM_BASE_URL: str = ""`, `LITELLM_MODEL: str = "openai/gpt-4o-mini"` — LiteLLM proxy settings
- `HYBRID_LLM_PRIORITY: str = "openai,litellm,ollama"` — fallback order for hybrid mode

### 3.2 Refactored story parser for provider dispatch
**File:** `backend/app/services/story_parser.py`
**Changes:** Completely refactored `StoryParser` to match the existing `AssetGenerator` provider-switch pattern:
- `__init__(provider: str | None = None)` — accepts per-story provider override
- `_generate_openai(system, user)` — direct OpenAI API via `httpx`
- `_generate_ollama(system, user)` — local Ollama `/api/chat` endpoint
- `_generate_litellm(system, user)` — LiteLLM `completion()` SDK call
- `_generate_hybrid(system, user)` — loops through `HYBRID_LLM_PRIORITY` providers until one succeeds
- `_generate_completion(system, user)` — dispatcher based on `self.provider`
- Prompt construction and JSON extraction remain **provider-agnostic**

### 3.3 Per-story LLM provider selection
**Files:** `backend/app/models/story.py`, `backend/app/schemas/story.py`, `backend/app/tasks/story_tasks.py`
**Changes:**
- Added `llm_provider: Mapped[str | None]` column to the `Story` SQLAlchemy model
- Added `llm_provider: str | None = None` to `StoryBase` and `StoryUpdate` Pydantic schemas
- Updated `story_tasks.py` to pass `story.llm_provider` into `StoryParser(provider=...)`

### 3.4 LiteLLM dependency
**File:** `backend/pyproject.toml`
**Fix:** Added `litellm>=1.40.0` to dependencies.

### 3.5 Environment variable documentation
**File:** `backend/.env.example`
**Fix:** Added all new LLM-related environment variables with comments.

### 3.6 Frontend LLM provider selector
**File:** `frontend/src/pages/NewStory.tsx`
**Changes:**
- Added `LLM_PROVIDERS` constant array with human-readable labels:
  - `openai` → "OpenAI GPT-4 (Cloud)"
  - `litellm` → "LiteLLM Proxy (Cloud)"
  - `ollama` → "Ollama / Llama (Local)"
  - `hybrid` → "Hybrid (Cloud → Local)"
- Added `<select>` dropdown in the creation form (4-column grid: Visual Theme, Voice Style, Music Mood, AI Story Parser)
- Default selection is `"openai"`

### 3.7 Frontend API types updated
**File:** `frontend/src/lib/api.ts`
**Changes:** Added `llm_provider?: string` to both `Story` and `StoryInput` interfaces.

---

## 4. Installation Steps Performed

### Backend
```bash
cd backend
uv venv .venv
source .venv/bin/activate
uv pip install -e "."
```
- Used `uv` (available on the system) to create a Python 3.13 virtual environment.
- Installed all backend dependencies successfully (including `litellm`, `email-validator`, `bcrypt` 3.2.2).
- Verified FastAPI app imports and starts: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- Verified Celery task module loads: `python -c "from app.tasks.story_tasks import app"`

### Frontend
```bash
cd frontend
npm install
npm run build
npm run dev
```
- `npm install` completed successfully (164 packages).
- `npm run build` completed with zero TypeScript errors.
- `npm run dev` starts the Vite dev server on `http://localhost:3000`.

---

## 5. Verification

| Component | Check | Result |
|-----------|-------|--------|
| Backend imports | All `app.*` modules import without error | ✅ Pass |
| Backend startup | Uvicorn starts on port 8000 | ✅ Pass |
| Celery app | `story_tasks.app` loads correctly | ✅ Pass |
| Frontend build | `tsc && vite build` succeeds | ✅ Pass |
| Frontend dev | Vite dev server starts on port 3000 | ✅ Pass |
| StoryParser | `_parse_json('...', language='en')` works | ✅ Pass |
| VideoCompiler | Instantiates without import errors | ✅ Pass |
| User registration | `POST /api/v1/auth/register` returns 201 + token | ✅ Pass |
| Story creation | `POST /api/v1/stories` returns 201 without Redis | ✅ Pass |
| Story listing | `GET /api/v1/stories` returns stories array | ✅ Pass |
| CORS preflight | `OPTIONS` request returns correct headers | ✅ Pass |
| LLM provider switch | `StoryParser('ollama')`, `('litellm')`, `('hybrid')` instantiate | ✅ Pass |
| Per-story LLM field | Create story with `llm_provider: 'hybrid'` persists correctly | ✅ Pass |
| Auth error messages | Register with duplicate shows real backend detail | ✅ Pass |

---

## 6. Known Limitations

- **Redis / Celery** — Background video processing requires Redis to be running. Without Redis, stories are saved as "draft" and the job status shows "failed" with a message explaining that the worker is unavailable. Start Redis with `redis-server` or use `docker-compose up` for full functionality.
- **Docker Compose** requires `OPENAI_API_KEY` and optionally `ELEVENLABS_API_KEY` to be set in `backend/.env` for cloud AI features.
- **Local GPU mode** (XTTS / ComfyUI) is optional and commented out in `docker-compose.yml`.
- **Frontend npm audit** reports 2 moderate severity vulnerabilities in dev dependencies (not application-breaking).
- **Ollama** must be installed and running separately for local LLM mode (`ollama run llama3`).
- **LiteLLM** proxy must be configured via `LITELLM_BASE_URL` and `LITELLM_API_KEY` if using the proxy mode.
