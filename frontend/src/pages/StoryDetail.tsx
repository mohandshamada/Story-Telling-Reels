import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Loader2,
  Download,
  ImageIcon,
  Pencil,
  Save,
  X,
  RotateCcw,
  Volume2,
} from 'lucide-react'
import {
  fetchStory,
  fetchScenes,
  downloadUrl,
  updateScene,
  regenerateSceneImage,
  regenerateSceneAudio,
  type Scene,
} from '../lib/api'
import { useJobProgress } from '../hooks/useJobProgress'

function EditableSceneCard({
  scene,
  storyStatus,
  onUpdate,
}: {
  scene: Scene
  storyStatus: string
  onUpdate: (updated: Scene) => void
}) {
  const [editing, setEditing] = useState(false)
  const [narration, setNarration] = useState(scene.narration_text || '')
  const [prompt, setPrompt] = useState(scene.visual_prompt || '')
  const [duration, setDuration] = useState(scene.duration_seconds || 5)

  const queryClient = useQueryClient()

  const saveMutation = useMutation({
    mutationFn: () =>
      updateScene(scene.id, {
        narration_text: narration,
        visual_prompt: prompt,
        duration_seconds: duration,
        subtitle_text: narration,
      }),
    onSuccess: (data) => {
      onUpdate(data)
      setEditing(false)
      queryClient.invalidateQueries({ queryKey: ['scenes', scene.story_id] })
    },
  })

  const imgMutation = useMutation({
    mutationFn: () => regenerateSceneImage(scene.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenes', scene.story_id] })
    },
  })

  const audioMutation = useMutation({
    mutationFn: () => regenerateSceneAudio(scene.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scenes', scene.story_id] })
    },
  })

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <div className="flex gap-4">
        <div className="shrink-0 w-28 h-40 bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center relative">
          {scene.image_url ? (
            <img
              src={scene.image_url}
              alt={`Scene ${scene.sequence_number}`}
              className="w-full h-full object-cover"
            />
          ) : (
            <ImageIcon className="w-8 h-8 text-slate-300" />
          )}
          {imgMutation.isPending && (
            <div className="absolute inset-0 bg-black/30 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            </div>
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium bg-brand-100 text-brand-700 px-2 py-0.5 rounded">
              Scene {scene.sequence_number}
            </span>
            {scene.narration_audio_url && (
              <Volume2 className="w-3.5 h-3.5 text-slate-400" />
            )}
            {storyStatus === 'completed' && (
              <button
                onClick={() => setEditing(!editing)}
                className="ml-auto text-xs flex items-center gap-1 text-slate-500 hover:text-brand-600"
              >
                {editing ? <X className="w-3 h-3" /> : <Pencil className="w-3 h-3" />}
                {editing ? 'Cancel' : 'Edit'}
              </button>
            )}
          </div>

          {editing ? (
            <div className="space-y-2">
              <textarea
                className="w-full text-sm border border-slate-300 rounded px-2 py-1"
                rows={2}
                value={narration}
                onChange={(e) => setNarration(e.target.value)}
                placeholder="Narration text..."
                dir="auto"
              />
              <textarea
                className="w-full text-xs border border-slate-300 rounded px-2 py-1"
                rows={2}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Visual prompt..."
              />
              <div className="flex items-center gap-3">
                <label className="text-xs text-slate-500">Duration:</label>
                <input
                  type="range"
                  min={3}
                  max={15}
                  step={0.5}
                  value={duration}
                  onChange={(e) => setDuration(Number(e.target.value))}
                  className="w-24"
                />
                <span className="text-xs text-slate-600">{duration}s</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => saveMutation.mutate()}
                  disabled={saveMutation.isPending}
                  className="text-xs bg-brand-500 text-white px-2 py-1 rounded flex items-center gap-1"
                >
                  <Save className="w-3 h-3" />
                  Save
                </button>
                <button
                  onClick={() => imgMutation.mutate()}
                  disabled={imgMutation.isPending}
                  className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded flex items-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  Regen Image
                </button>
                <button
                  onClick={() => audioMutation.mutate()}
                  disabled={audioMutation.isPending}
                  className="text-xs bg-slate-100 text-slate-700 px-2 py-1 rounded flex items-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  Regen Audio
                </button>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm font-medium text-slate-800" dir="auto">
                {scene.narration_text || 'No narration'}
              </p>
              {scene.visual_prompt && (
                <p className="text-xs text-slate-500 mt-2 line-clamp-2 italic" dir="auto">
                  {scene.visual_prompt}
                </p>
              )}
              {scene.duration_seconds && (
                <span className="text-xs text-slate-400 mt-1 block">
                  {scene.duration_seconds.toFixed(1)}s
                </span>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default function StoryDetail() {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()

  const { data: story, isLoading: storyLoading } = useQuery({
    queryKey: ['story', id],
    queryFn: () => fetchStory(id!),
    refetchInterval: (query) => {
      const s = query.state.data
      return s && s.status !== 'completed' && s.status !== 'failed' ? 5000 : false
    },
  })

  const { data: scenes, isLoading: scenesLoading } = useQuery({
    queryKey: ['scenes', id],
    queryFn: () => fetchScenes(id!),
    enabled: !!story,
    refetchInterval: (query) => {
      const s = query.state.data
      return !s || s.length === 0 ? 5000 : false
    },
  })

  // WebSocket for live progress
  const { wsData, connected } = useJobProgress(story?.latest_job_id)

  // Merge WS data into local state for instant UI updates
  const displayProgress = wsData?.percent ?? story?.progress_percent ?? 0
  const displayStage = wsData?.stage ?? story?.current_stage ?? ''
  const displayStatus = wsData?.status ?? story?.status ?? 'draft'

  // When WS says complete, invalidate queries to fetch final state
  useEffect(() => {
    if (wsData?.type === 'complete' || wsData?.type === 'scene') {
      const timer = setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['story', id] })
        queryClient.invalidateQueries({ queryKey: ['scenes', id] })
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [wsData, id, queryClient])

  const isProcessing =
    displayStatus !== 'completed' && displayStatus !== 'failed'

  if (storyLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 flex justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      </div>
    )
  }

  if (!story) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-slate-500">Story not found.</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">{story.title}</h1>
        <p className="text-slate-500 mt-1 line-clamp-2" dir="auto">{story.content}</p>

        <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-600">
          <span className="bg-slate-100 px-2 py-1 rounded capitalize">
            {story.language}
          </span>
          <span className="bg-slate-100 px-2 py-1 rounded capitalize">
            {story.visual_theme?.replace('_', ' ')}
          </span>
          <span className="bg-slate-100 px-2 py-1 rounded capitalize">
            {story.voice_style?.replace('_', ' ')}
          </span>
          <span className="bg-slate-100 px-2 py-1 rounded">
            {story.target_duration}s target
          </span>
          {connected && (
            <span className="bg-green-100 text-green-700 px-2 py-1 rounded flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              Live
            </span>
          )}
        </div>
      </div>

      {/* Progress / Video */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6">
        {isProcessing ? (
          <div className="py-8 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-brand-500 mx-auto mb-3" />
            <p className="font-medium text-slate-700">
              {displayStage || 'Processing...'}
            </p>
            <div className="max-w-xs mx-auto mt-3">
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-brand-500 rounded-full transition-all"
                  style={{ width: `${displayProgress}%` }}
                />
              </div>
              <p className="text-xs text-slate-500 mt-1">{displayProgress}%</p>
            </div>
          </div>
        ) : displayStatus === 'completed' ? (
          <div className="text-center">
            <div className="relative mx-auto max-w-sm rounded-lg overflow-hidden bg-slate-900 aspect-[9/16]">
              <video
                src={`/storage/videos/${story.id}.mp4`}
                controls
                className="w-full h-full"
                poster={scenes?.[0]?.image_url || undefined}
              />
            </div>
            <div className="mt-4 flex items-center justify-center gap-3">
              <a
                href={
                  story.latest_job_id
                    ? downloadUrl(story.latest_job_id)
                    : '#'
                }
                className="inline-flex items-center gap-2 bg-brand-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-600 transition"
              >
                <Download className="w-4 h-4" />
                Download MP4
              </a>
            </div>
          </div>
        ) : displayStatus === 'failed' ? (
          <div className="py-8 text-center text-red-600">
            <p className="font-medium">Rendering failed</p>
            <p className="text-sm mt-1">Please try regenerating the reel.</p>
          </div>
        ) : (
          <div className="py-8 text-center text-slate-500">
            <p>Waiting to start...</p>
          </div>
        )}
      </div>

      {/* Scenes */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-slate-900">Scenes</h2>
        {displayStatus === 'completed' && (
          <span className="text-xs text-slate-500">
            Click "Edit" on any scene to tweak narration, prompts, or regenerate assets.
          </span>
        )}
      </div>

      {scenesLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-brand-500" />
        </div>
      ) : !scenes?.length ? (
        <div className="text-center py-8 bg-white rounded-xl border border-dashed border-slate-300 text-slate-500">
          Scenes will appear here after parsing.
        </div>
      ) : (
        <div className="space-y-4">
          {scenes.map((scene) => (
            <EditableSceneCard
              key={scene.id}
              scene={scene}
              storyStatus={displayStatus}
              onUpdate={(updated) => {
                queryClient.setQueryData(
                  ['scenes', id],
                  (old: Scene[] | undefined) =>
                    old?.map((s) => (s.id === updated.id ? updated : s)) ?? []
                )
              }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
