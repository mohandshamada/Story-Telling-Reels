import { Routes, Route, Link, useNavigate } from 'react-router-dom'
import { BookOpen, LogOut, User } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import NewStory from './pages/NewStory'
import StoryDetail from './pages/StoryDetail'
import { LoginPage, RegisterPage } from './pages/Auth'
import { useAuth } from './lib/auth'

function App() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-brand-600 font-bold text-lg">
            <BookOpen className="w-6 h-6" />
            Story Reels
          </Link>
          <nav className="flex items-center gap-4">
            {user ? (
              <>
                <Link
                  to="/"
                  className="text-sm font-medium text-slate-600 hover:text-slate-900"
                >
                  Stories
                </Link>
                <Link
                  to="/new"
                  className="text-sm font-medium bg-brand-500 text-white px-3 py-1.5 rounded-md hover:bg-brand-600 transition"
                >
                  New Story
                </Link>
                <div className="flex items-center gap-2 text-sm text-slate-600">
                  <User className="w-4 h-4" />
                  <span className="hidden sm:inline">{user.username}</span>
                </div>
                <button
                  onClick={() => { logout(); navigate('/login') }}
                  className="text-slate-400 hover:text-slate-600"
                  title="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-sm font-medium text-slate-600 hover:text-slate-900"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="text-sm font-medium bg-brand-500 text-white px-3 py-1.5 rounded-md hover:bg-brand-600 transition"
                >
                  Get Started
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new" element={<NewStory />} />
          <Route path="/stories/:id" element={<StoryDetail />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
