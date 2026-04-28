import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Loader2, Film, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { fetchStories, type Story } from '../lib/api'

function statusIcon(status: string) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-4 h-4 text-green-500" />
    case 'failed':
      return <AlertCircle className="w-4 h-4 text-red-500" />
    case 'draft':
    default:
      return <Clock className="w-4 h-4 text-slate-400" />
  }
}

function StoryCard({ story }: { story: Story }) {
  return (
    <Link
      to={`/stories/${story.id}`}
      className="block bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 truncate">{story.title}</h3>
          <p className="text-sm text-slate-500 mt-1 line-clamp-2">{story.content}</p>
        </div>
        <div className="shrink-0">{statusIcon(story.status)}</div>
      </div>

      <div className="mt-4 flex items-center gap-3 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <Film className="w-3.5 h-3.5" />
          {story.target_duration}s
        </span>
        <span className="capitalize">{story.language}</span>
        <span className="capitalize">{story.visual_theme?.replace('_', ' ')}</span>
      </div>

      {story.status === 'draft' && story.progress_percent > 0 && (
        <div className="mt-3">
          <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-500 rounded-full transition-all"
              style={{ width: `${story.progress_percent}%` }}
            />
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {story.current_stage || 'Processing...'} ({story.progress_percent}%)
          </p>
        </div>
      )}
    </Link>
  )
}

export default function Dashboard() {
  const { data: stories, isLoading } = useQuery({
    queryKey: ['stories'],
    queryFn: fetchStories,
    refetchInterval: 5000,
  })

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Your Stories</h1>
        <Link
          to="/new"
          className="bg-brand-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-brand-600 transition"
        >
          Create New Story
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
        </div>
      ) : !stories?.length ? (
        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
          <Film className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-slate-700">No stories yet</h3>
          <p className="text-slate-500 mt-1">Upload a story to generate your first reel.</p>
          <Link
            to="/new"
            className="inline-block mt-4 text-brand-600 font-medium hover:underline"
          >
            Create your first story &rarr;
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {stories.map((story) => (
            <StoryCard key={story.id} story={story} />
          ))}
        </div>
      )}
    </div>
  )
}
