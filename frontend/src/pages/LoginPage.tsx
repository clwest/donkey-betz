import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { authApi } from '@/lib/api'
import { isCustomerRole } from '@/lib/roles'  // S3052 PR 4: post-auth redirect

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()
  const { login } = useAuthStore()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await authApi.login(username, password)
      const { token, user } = response.data
      login(token, user)
      // S3052 PR 4 — customer accounts land on /my; operators continue to /workspace hub.
      navigate(isCustomerRole(user) ? '/my' : '/workspace', { replace: true })
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      setError(error.response?.data?.detail || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-dark-bg">
      <div className="w-full max-w-md card">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-primary-400 mb-2">
            Donkey Betz
          </h1>
          <p className="text-gray-400">AI Intelligence Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-accent-red/10 border border-accent-red text-accent-red text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input w-full"
              placeholder="Enter your username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input w-full"
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* S2797: link out to public marketing surface for first-touch prospects
            who bounced to /login without knowing what Donkey Betz is. */}
        <div className="mt-6 text-center text-sm text-gray-500">
          New here?{' '}
          <Link to="/welcome" className="text-primary-400 hover:text-primary-300">
            Learn more →
          </Link>
        </div>
      </div>
    </div>
  )
}
