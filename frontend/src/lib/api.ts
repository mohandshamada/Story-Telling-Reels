const API_BASE = import.meta.env.VITE_API_URL || ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`
  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    ...options,
  })
  if (!res.ok) {
    const errText = await res.text().catch(() => 'Unknown error')
    try {
      const errJson = JSON.parse(errText)
      throw new Error(errJson.detail || errText)
    } catch {
      throw new Error(errText)
    }
  }
  return res.json() as Promise<T>
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// ------------------------------------------------------------------
// Types
// ------------------------------------------------------------------

export interface Story {
  id: string
  title: string
  source?: string
  language: string
  content: string
  target_duration: number
  target_audience?: string
  visual_theme?: string
  voice_style?: string
  music_mood?: string
  llm_provider?: string
  moral_lesson?: string
  status: string
  created_at: string
  updated_at: string
  progress_percent: number
  current_stage?: string
  latest_job_id?: string
}

export interface StoryInput {
  title: string
  content: string
  language: string
  target_duration: number
  visual_theme?: string
  voice_style?: string
  music_mood?: string
  llm_provider?: string
  moral_lesson?: string
}

export interface Scene {
  id: string
  story_id: string
  sequence_number: number
  narration_text?: string
  narration_audio_url?: string
  visual_prompt?: string
  image_url?: string
  animation_type?: string
  animation_video_url?: string
  duration_seconds?: number
  subtitle_text?: string
  subtitle_style?: Record<string, unknown>
  sfx_triggers?: unknown[]
  created_at: string
}

export interface User {
  id: string
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

// ------------------------------------------------------------------
// Stories
// ------------------------------------------------------------------

export function fetchStories(): Promise<Story[]> {
  return request<Story[]>('/api/v1/stories')
}

export function createStory(data: StoryInput): Promise<Story> {
  return request<Story>('/api/v1/stories', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export function fetchStory(id: string): Promise<Story> {
  return request<Story>(`/api/v1/stories/${id}`)
}

export function fetchScenes(storyId: string): Promise<Scene[]> {
  return request<Scene[]>(`/api/v1/stories/${storyId}/scenes`)
}

// ------------------------------------------------------------------
// Scenes
// ------------------------------------------------------------------

export function updateScene(
  sceneId: string,
  data: Partial<Scene>
): Promise<Scene> {
  return request<Scene>(`/api/v1/scenes/${sceneId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export function regenerateSceneImage(sceneId: string): Promise<{ image_url: string }> {
  return request<{ image_url: string }>(`/api/v1/scenes/${sceneId}/regenerate-image`, {
    method: 'POST',
  })
}

export function regenerateSceneAudio(sceneId: string): Promise<{ audio_url: string }> {
  return request<{ audio_url: string }>(`/api/v1/scenes/${sceneId}/regenerate-audio`, {
    method: 'POST',
  })
}

// ------------------------------------------------------------------
// Jobs
// ------------------------------------------------------------------

export function downloadUrl(jobId: string): string {
  return `${API_BASE}/api/v1/jobs/${jobId}/download`
}

// ------------------------------------------------------------------
// Auth
// ------------------------------------------------------------------

export function login(credentials: { username: string; password: string }): Promise<AuthResponse> {
  return request<AuthResponse>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

export function register(data: { email: string; username: string; password: string }): Promise<AuthResponse> {
  return request<AuthResponse>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
