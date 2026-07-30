import { Outlet, Link, useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

export default function CustomerLayout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-gray-50 dark:bg-gray-900">
      <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3 dark:border-gray-800 dark:bg-gray-950">
        <Link
          to="/my"
          className="text-lg font-semibold text-gray-900 dark:text-white"
        >
          Donkey Betz
        </Link>
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {user.email || user.username}
            </span>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </header>
      <main className="min-h-0 flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
