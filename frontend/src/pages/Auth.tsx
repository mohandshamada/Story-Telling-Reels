import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Loader2, LogIn, UserPlus } from 'lucide-react'
import { useAuth } from '../lib/auth'
import { login, register } from '../lib/api'

export function LoginPage() {
  const navigate = useNavigate()
  const { login: authLogin } = useAuth()
  const [form, setForm] = useState({ username: '', password: '' })

  const mutation = useMutation({
    mutationFn: login,
    onSuccess: (data) => {
      authLogin(data.access_token, data.user)
      navigate('/')
    },
  })

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm bg-white rounded-xl border border-slate-200 p-6">
        <h1 className="text-xl font-bold text-slate-900 mb-1">Welcome back</h1>
        <p className="text-sm text-slate-500 mb-5">Sign in to your Story Reels account</p>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate(form)
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <input
              type="text"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-brand-500 text-white font-semibold py-2 rounded-lg hover:bg-brand-600 transition disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <LogIn className="w-4 h-4" />}
            Sign In
          </button>
          {mutation.isError && (
            <p className="text-sm text-red-600">
              {mutation.error instanceof Error ? mutation.error.message : 'An error occurred'}
            </p>
          )}
        </form>

        <p className="text-sm text-slate-500 mt-4 text-center">
          Don't have an account?{' '}
          <Link to="/register" className="text-brand-600 font-medium hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}

export function RegisterPage() {
  const navigate = useNavigate()
  const { login: authLogin } = useAuth()
  const [form, setForm] = useState({ email: '', username: '', password: '' })

  const mutation = useMutation({
    mutationFn: register,
    onSuccess: (data) => {
      authLogin(data.access_token, data.user)
      navigate('/')
    },
  })

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm bg-white rounded-xl border border-slate-200 p-6">
        <h1 className="text-xl font-bold text-slate-900 mb-1">Create account</h1>
        <p className="text-sm text-slate-500 mb-5">Join Story Reels and start creating</p>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate(form)
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
            <input
              type="text"
              required
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input
              type="password"
              required
              minLength={6}
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full bg-brand-500 text-white font-semibold py-2 rounded-lg hover:bg-brand-600 transition disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {mutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <UserPlus className="w-4 h-4" />}
            Create Account
          </button>
          {mutation.isError && (
            <p className="text-sm text-red-600">
              {mutation.error instanceof Error ? mutation.error.message : 'An error occurred'}
            </p>
          )}
        </form>

        <p className="text-sm text-slate-500 mt-4 text-center">
          Already have an account?{' '}
          <Link to="/login" className="text-brand-600 font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
