import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Loader2, Sparkles } from 'lucide-react'
import { createStory, type StoryInput } from '../lib/api'

const THEMES = [
  { value: 'watercolor_illustration', label: 'Watercolor Illustration' },
  { value: '3d_cartoon', label: '3D Cartoon (Pixar-style)' },
  { value: 'flat_vector', label: 'Flat Vector' },
]

const VOICES = [
  { value: 'warm_female_storyteller', label: 'Warm Female Storyteller' },
  { value: 'gentle_male_storyteller', label: 'Gentle Male Storyteller' },
]

const MOODS = [
  { value: 'gentle_playful', label: 'Gentle & Playful' },
  { value: 'calm_dreamy', label: 'Calm & Dreamy' },
  { value: 'upbeat_happy', label: 'Upbeat & Happy' },
]

export default function NewStory() {
  const navigate = useNavigate()
  const [form, setForm] = useState<StoryInput>({
    title: '',
    content: '',
    language: 'en',
    target_duration: 45,
    visual_theme: 'watercolor_illustration',
    voice_style: 'warm_female_storyteller',
    music_mood: 'gentle_playful',
    moral_lesson: '',
  })

  const mutation = useMutation({
    mutationFn: createStory,
    onSuccess: (data) => {
      navigate(`/stories/${data.id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.title.trim() || !form.content.trim()) return
    mutation.mutate(form)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-6 h-6 text-brand-500" />
        <h1 className="text-2xl font-bold text-slate-900">Create New Story</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
          <input
            type="text"
            required
            className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            placeholder="e.g. The Lion and the Mouse"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Story Text</label>
          <textarea
            required
            rows={8}
            className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            placeholder="Paste your full story here..."
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Language</label>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2 bg-white"
              value={form.language}
              onChange={(e) => setForm({ ...form, language: e.target.value })}
            >
              <option value="en">English</option>
              <option value="ar">Arabic</option>
              <option value="fr">French</option>
              <option value="es">Spanish</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Target Duration (seconds)
            </label>
            <input
              type="number"
              min={15}
              max={90}
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.target_duration}
              onChange={(e) => setForm({ ...form, target_duration: Number(e.target.value) })}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Visual Theme</label>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2 bg-white"
              value={form.visual_theme}
              onChange={(e) => setForm({ ...form, visual_theme: e.target.value })}
            >
              {THEMES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Voice Style</label>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2 bg-white"
              value={form.voice_style}
              onChange={(e) => setForm({ ...form, voice_style: e.target.value })}
            >
              {VOICES.map((v) => (
                <option key={v.value} value={v.value}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Music Mood</label>
            <select
              className="w-full rounded-lg border border-slate-300 px-3 py-2 bg-white"
              value={form.music_mood}
              onChange={(e) => setForm({ ...form, music_mood: e.target.value })}
            >
              {MOODS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Moral Lesson</label>
          <input
            type="text"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500"
            placeholder="e.g. Kindness is never wasted"
            value={form.moral_lesson || ''}
            onChange={(e) => setForm({ ...form, moral_lesson: e.target.value })}
          />
        </div>

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-brand-500 text-white font-semibold py-2.5 rounded-lg hover:bg-brand-600 transition disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {mutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Creating...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Reel
            </>
          )}
        </button>

        {mutation.isError && (
          <p className="text-sm text-red-600">
            Something went wrong. Please try again.
          </p>
        )}
      </form>
    </div>
  )
}
