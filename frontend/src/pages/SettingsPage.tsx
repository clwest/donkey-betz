import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/stores/authStore'
import { settingsApi, portfolioApi } from '@/lib/api'
import {
  User, Bell, Shield, Palette, Database, Key, ChevronRight,
  CheckCircle, XCircle, Loader2, X, Save, Download, Trash2,
  Moon, Sun, Mail, MessageSquare, Zap, Eye, EyeOff, LogOut,
  RefreshCw, Sparkles, Copy, Check, Globe, Link2
} from 'lucide-react'
import { cn } from '@/lib/cn'

type SettingsSection = 'profile' | 'notifications' | 'security' | 'appearance' | 'api' | 'data'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface EditProfileModalProps {
  user: { username?: string; email?: string }
  onClose: () => void
  onSave: (data: { username: string; email: string }) => void
  isLoading: boolean
}

interface ChangePasswordModalProps {
  onClose: () => void
  onSave: (oldPassword: string, newPassword: string) => void
  isLoading: boolean
}

interface NotificationPreferences {
  email_enabled: boolean
  push_enabled: boolean
  alert_notifications: boolean
  suggestion_notifications: boolean
  insight_notifications: boolean
  celebration_notifications: boolean
  warning_notifications: boolean
}

const settingsSections = [
  { id: 'profile' as SettingsSection, title: 'Profile', icon: User, description: 'Manage your account settings' },
  { id: 'notifications' as SettingsSection, title: 'Notifications', icon: Bell, description: 'Configure notification preferences' },
  { id: 'security' as SettingsSection, title: 'Security', icon: Shield, description: 'Password and authentication' },
  { id: 'appearance' as SettingsSection, title: 'Appearance', icon: Palette, description: 'Theme and display options' },
  { id: 'api' as SettingsSection, title: 'API Keys', icon: Key, description: 'Manage API integrations' },
  { id: 'data' as SettingsSection, title: 'Data & Storage', icon: Database, description: 'Export and manage your data' },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

function Toggle({ enabled, onChange, disabled }: { enabled: boolean; onChange: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onChange}
      disabled={disabled}
      className={cn(
        'relative h-6 w-11 rounded-full transition-colors',
        enabled ? 'bg-primary-600' : 'bg-dark-border',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <span className={cn(
        'absolute top-1 h-4 w-4 rounded-full bg-white transition-transform',
        enabled ? 'right-1' : 'left-1'
      )} />
    </button>
  )
}

function EditProfileModal({ user, onClose, onSave, isLoading }: EditProfileModalProps) {
  const [username, setUsername] = useState(user.username || '')
  const [email, setEmail] = useState(user.email || '')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSave({ username, email })
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Edit Profile</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary flex items-center gap-2" disabled={isLoading}>
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ChangePasswordModal({ onClose, onSave, isLoading }: ChangePasswordModalProps) {
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPasswords, setShowPasswords] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    onSave(oldPassword, newPassword)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-md mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Change Password</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Current Password</label>
              <div className="relative">
                <input
                  type={showPasswords ? 'text' : 'password'}
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 pr-10 text-white focus:outline-none focus:border-primary-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  {showPasswords ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">New Password</label>
              <input
                type={showPasswords ? 'text' : 'password'}
                value={newPassword}
                onChange={(e) => { setNewPassword(e.target.value); setError('') }}
                className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Confirm New Password</label>
              <input
                type={showPasswords ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => { setConfirmPassword(e.target.value); setError('') }}
                className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-primary-500"
              />
            </div>
            {error && <p className="text-accent-red text-sm">{error}</p>}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary flex items-center gap-2" disabled={isLoading}>
              {isLoading ? <Loader2 size={16} className="animate-spin" /> : <Shield size={16} />}
              Update Password
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default function SettingsPage() {
  const { user, token, logout } = useAuthStore()
  const [activeSection, setActiveSection] = useState<SettingsSection | null>(null)
  const [showEditProfile, setShowEditProfile] = useState(false)
  const [showChangePassword, setShowChangePassword] = useState(false)
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [tokenCopied, setTokenCopied] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const queryClient = useQueryClient()

  // Fetch profile data
  const { data: profileData } = useQuery({
    queryKey: ['profile'],
    queryFn: () => settingsApi.getProfile(),
  })

  // Fetch profile stats
  const { data: statsData } = useQuery({
    queryKey: ['profile-stats'],
    queryFn: () => settingsApi.getProfileStats(),
  })

  // Fetch notifications
  const { data: notificationsData } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => settingsApi.getNotifications(),
  })

  // Fetch notification preferences
  const { data: notifPrefsData } = useQuery({
    queryKey: ['notification-preferences'],
    queryFn: () => settingsApi.getNotificationPreferences(),
  })

  // Session 745: Fetch connected platforms for API section
  const { data: accountsData, isLoading: loadingAccounts } = useQuery({
    queryKey: ['settings-connected-platforms'],
    queryFn: () => portfolioApi.accounts(),
    enabled: activeSection === 'api',
  })

  // Extract notification preferences from API response
  const notifPrefs: NotificationPreferences = notifPrefsData?.data?.preferences || {
    email_enabled: false,
    push_enabled: true,
    alert_notifications: true,
    suggestion_notifications: true,
    insight_notifications: true,
    celebration_notifications: true,
    warning_notifications: true,
  }

  // Extract dark_mode from profile
  const profile = profileData?.data || {}
  const darkMode = profile.dark_mode ?? true

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: { username?: string; email?: string; dark_mode?: boolean }) => settingsApi.updateProfile(data),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Profile updated successfully!' })
      setShowEditProfile(false)
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to update profile' })
    },
  })

  // Update notification preferences mutation
  const updateNotifPrefsMutation = useMutation({
    mutationFn: (prefs: Record<string, boolean>) => settingsApi.updateNotificationPreferences(prefs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-preferences'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to update notification preferences' })
    },
  })

  // Generate avatar mutation
  const generateAvatarMutation = useMutation({
    mutationFn: () => settingsApi.generateAvatar(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'AI avatar generated!' })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate avatar' })
    },
  })

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: ({ oldPassword, newPassword }: { oldPassword: string; newPassword: string }) =>
      settingsApi.changePassword(oldPassword, newPassword),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Password changed successfully!' })
      setShowChangePassword(false)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to change password. Check your current password.' })
    },
  })

  // Mark all notifications read mutation
  const markAllReadMutation = useMutation({
    mutationFn: () => settingsApi.markAllRead(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'All notifications marked as read' })
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to mark notifications as read' })
    },
  })

  // Clear preferences mutation
  const clearPreferencesMutation = useMutation({
    mutationFn: () => settingsApi.clearPreferences(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Preferences cleared' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to clear preferences' })
    },
  })

  const stats = statsData?.data || {}
  const notifications = notificationsData?.data?.notifications || []
  const unreadCount = notifications.filter((n: { is_read: boolean }) => !n.is_read).length

  // Handle notification preference toggle
  const handleNotifPrefToggle = (key: keyof NotificationPreferences) => {
    const newValue = !notifPrefs[key]
    updateNotifPrefsMutation.mutate({ [key]: newValue })
    setActionResult({ type: 'success', message: `${key.replace(/_/g, ' ')} ${newValue ? 'enabled' : 'disabled'}` })
  }

  // Handle dark mode toggle
  const handleDarkModeToggle = () => {
    updateProfileMutation.mutate({ dark_mode: !darkMode })
    setActionResult({ type: 'success', message: `${!darkMode ? 'Dark' : 'Light'} mode enabled` })
  }

  // Copy API token to clipboard
  const handleCopyToken = async () => {
    if (token) {
      await navigator.clipboard.writeText(token)
      setTokenCopied(true)
      setActionResult({ type: 'success', message: 'API token copied to clipboard!' })
      setTimeout(() => setTokenCopied(false), 2000)
    }
  }

  // Handle data export
  const handleExportData = async (format: 'json' | 'csv') => {
    setIsExporting(true)
    try {
      const response = await settingsApi.exportData(format)
      const data = response.data

      // Create a blob and download
      const blob = new Blob([format === 'json' ? JSON.stringify(data, null, 2) : data], {
        type: format === 'json' ? 'application/json' : 'text/csv'
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `donkey-betz-export-${new Date().toISOString().split('T')[0]}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      setActionResult({ type: 'success', message: `Data exported as ${format.toUpperCase()}!` })
    } catch {
      setActionResult({ type: 'error', message: `Failed to export data as ${format.toUpperCase()}` })
    } finally {
      setIsExporting(false)
    }
  }

  // Mask token for display
  const maskedToken = token ? `${token.slice(0, 8)}${'•'.repeat(24)}${token.slice(-8)}` : '••••••••••••••••••••••••••••••••'

  // Clear toast after 3 seconds
  useEffect(() => {
    if (actionResult) {
      const timer = setTimeout(() => setActionResult(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [actionResult])

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <div className="max-w-4xl space-y-6">
      {/* Profile Header */}
      <div className="card">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className="h-16 w-16 rounded-full bg-primary-600 flex items-center justify-center text-2xl font-bold overflow-hidden">
              {profile.avatar ? (
                <img src={profile.avatar} alt="Avatar" className="w-full h-full object-cover" />
              ) : (
                user?.username?.charAt(0).toUpperCase() || 'U'
              )}
            </div>
            <button
              className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-primary-500 flex items-center justify-center hover:bg-primary-600 transition-colors"
              onClick={() => generateAvatarMutation.mutate()}
              disabled={generateAvatarMutation.isPending}
            >
              {generateAvatarMutation.isPending ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <Sparkles size={12} />
              )}
            </button>
          </div>
          <div className="flex-1">
            <h2 className="text-xl font-bold">{profile.display_name || profile.username || user?.username}</h2>
            <p className="text-gray-400">{profile.email || user?.email}</p>
            {stats.total_creations && (
              <p className="text-sm text-primary-400 mt-1">{stats.total_creations} creations</p>
            )}
          </div>
          <div className="flex gap-2">
            <button
              className="btn btn-secondary"
              onClick={() => setShowEditProfile(true)}
            >
              Edit Profile
            </button>
            <button
              className="btn btn-secondary text-accent-red hover:bg-accent-red/10"
              onClick={handleLogout}
            >
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {settingsSections.map(({ id, title, icon: Icon, description }) => (
          <div
            key={id}
            className={cn(
              'card cursor-pointer transition-all',
              activeSection === id ? 'border-primary-500 ring-1 ring-primary-500' : 'hover:border-gray-600'
            )}
            onClick={() => setActiveSection(activeSection === id ? null : id)}
          >
            <div className="flex items-start gap-4">
              <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                <Icon size={20} className="text-primary-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">{title}</h3>
                  {id === 'notifications' && unreadCount > 0 && (
                    <span className="px-2 py-0.5 text-xs rounded-full bg-accent-red/20 text-accent-red">
                      {unreadCount}
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-400">{description}</p>
              </div>
              <ChevronRight size={16} className={cn(
                'text-gray-500 transition-transform',
                activeSection === id && 'rotate-90'
              )} />
            </div>
          </div>
        ))}
      </div>

      {/* Section Details */}
      {activeSection === 'notifications' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Notification Preferences</h3>
            <button
              className="btn btn-secondary text-sm"
              onClick={() => markAllReadMutation.mutate()}
              disabled={markAllReadMutation.isPending}
            >
              {markAllReadMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
              Mark All Read
            </button>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <Mail size={18} className="text-gray-400" />
                <div>
                  <p className="font-medium">Email Notifications</p>
                  <p className="text-sm text-gray-400">Receive updates via email</p>
                </div>
              </div>
              <Toggle
                enabled={notifPrefs.email_enabled}
                onChange={() => handleNotifPrefToggle('email_enabled')}
                disabled={updateNotifPrefsMutation.isPending}
              />
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <MessageSquare size={18} className="text-gray-400" />
                <div>
                  <p className="font-medium">Push Notifications</p>
                  <p className="text-sm text-gray-400">Browser push notifications</p>
                </div>
              </div>
              <Toggle
                enabled={notifPrefs.push_enabled}
                onChange={() => handleNotifPrefToggle('push_enabled')}
                disabled={updateNotifPrefsMutation.isPending}
              />
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                <Zap size={18} className="text-gray-400" />
                <div>
                  <p className="font-medium">Agent Alerts</p>
                  <p className="text-sm text-gray-400">Notifications from AI agents</p>
                </div>
              </div>
              <Toggle
                enabled={notifPrefs.alert_notifications}
                onChange={() => handleNotifPrefToggle('alert_notifications')}
                disabled={updateNotifPrefsMutation.isPending}
              />
            </div>
          </div>
        </div>
      )}

      {activeSection === 'security' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Security Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Password</p>
                <p className="text-sm text-gray-400">Last changed: Never</p>
              </div>
              <button
                className="btn btn-secondary text-sm"
                onClick={() => setShowChangePassword(true)}
              >
                Change Password
              </button>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-gray-400">Add an extra layer of security</p>
              </div>
              <button
                className="btn btn-secondary text-sm"
                onClick={() => setActionResult({ type: 'success', message: '2FA setup coming soon!' })}
              >
                Enable
              </button>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Active Sessions</p>
                <p className="text-sm text-gray-400">Manage your logged in devices</p>
              </div>
              <button
                className="btn btn-secondary text-sm"
                onClick={() => setActionResult({ type: 'success', message: 'Session management coming soon!' })}
              >
                View All
              </button>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'appearance' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Appearance Settings</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div className="flex items-center gap-3">
                {darkMode ? <Moon size={18} className="text-gray-400" /> : <Sun size={18} className="text-gray-400" />}
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className="text-sm text-gray-400">Use dark theme throughout the app</p>
                </div>
              </div>
              <Toggle
                enabled={darkMode}
                onChange={handleDarkModeToggle}
                disabled={updateProfileMutation.isPending}
              />
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Accent Color</p>
                <p className="text-sm text-gray-400">Customize your interface color</p>
              </div>
              <div className="flex gap-2">
                {['#8b5cf6', '#22c55e', '#f59e0b', '#06b6d4', '#ec4899'].map((color) => (
                  <button
                    key={color}
                    className="h-6 w-6 rounded-full border-2 border-transparent hover:border-white transition-colors"
                    style={{ backgroundColor: color }}
                    onClick={() => setActionResult({ type: 'success', message: 'Accent color updated!' })}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeSection === 'api' && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">API Keys</h3>
            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-dark-bg">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-medium">Personal API Token</p>
                  <p className="text-xs text-gray-500">Used for API authentication</p>
                </div>
                <div className="flex items-center gap-2">
                  <code className="flex-1 bg-dark-border rounded px-3 py-2 text-sm text-gray-400 font-mono overflow-hidden text-ellipsis">
                    {maskedToken}
                  </code>
                  <button
                    className="btn btn-secondary text-sm flex items-center gap-1"
                    onClick={handleCopyToken}
                    disabled={!token}
                  >
                    {tokenCopied ? <Check size={14} className="text-accent-green" /> : <Copy size={14} />}
                    {tokenCopied ? 'Copied' : 'Copy'}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  This is your authentication token. Keep it secure and never share it publicly.
                </p>
              </div>
            </div>
          </div>

          {/* Session 745: Connected Platforms */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Link2 className="text-primary-400" size={20} />
                Connected Platforms
              </h3>
              {loadingAccounts && <Loader2 className="animate-spin" size={16} />}
            </div>
            {(() => {
              const accounts = accountsData?.data?.accounts || accountsData?.data || []
              return accounts.length > 0 ? (
                <div className="space-y-3">
                  {accounts.map((account: { id: string; platform_name?: string; platform?: string; status?: string; connected_at?: string }) => (
                    <div
                      key={account.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
                          <Globe size={20} className="text-primary-400" />
                        </div>
                        <div>
                          <p className="font-medium">{account.platform_name || account.platform || 'Platform'}</p>
                          <p className="text-xs text-gray-500">
                            Connected {account.connected_at ? new Date(account.connected_at).toLocaleDateString() : 'recently'}
                          </p>
                        </div>
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        account.status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {account.status || 'Connected'}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-3 rounded-lg border border-dashed border-dark-border text-center">
                  <Globe className="mx-auto mb-2 text-gray-500" size={24} />
                  <p className="text-gray-400 mb-2">No platforms connected</p>
                  <button
                    className="btn btn-secondary text-sm"
                    onClick={() => setActionResult({ type: 'success', message: 'Visit Portfolio to connect platforms!' })}
                  >
                    Connect Platform
                  </button>
                </div>
              )
            })()}
          </div>
        </div>
      )}

      {activeSection === 'data' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Data & Storage</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Export Your Data</p>
                <p className="text-sm text-gray-400">Download all your content and settings</p>
              </div>
              <div className="flex gap-2">
                <button
                  className="btn btn-secondary text-sm flex items-center gap-1"
                  onClick={() => handleExportData('json')}
                  disabled={isExporting}
                >
                  {isExporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  JSON
                </button>
                <button
                  className="btn btn-secondary text-sm flex items-center gap-1"
                  onClick={() => handleExportData('csv')}
                  disabled={isExporting}
                >
                  {isExporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
                  CSV
                </button>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg">
              <div>
                <p className="font-medium">Clear Preferences</p>
                <p className="text-sm text-gray-400">Reset all learned preferences</p>
              </div>
              <button
                className="btn btn-secondary text-sm text-accent-amber flex items-center gap-1"
                onClick={() => clearPreferencesMutation.mutate()}
                disabled={clearPreferencesMutation.isPending}
              >
                {clearPreferencesMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <RefreshCw size={14} />}
                Clear
              </button>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-dark-bg border border-accent-red/30">
              <div>
                <p className="font-medium text-accent-red">Delete Account</p>
                <p className="text-sm text-gray-400">Permanently delete your account and data</p>
              </div>
              <button
                className="btn btn-secondary text-sm text-accent-red flex items-center gap-1"
                onClick={() => setActionResult({ type: 'error', message: 'Contact support to delete account' })}
              >
                <Trash2 size={14} />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Preferences (when no section selected) */}
      {!activeSection && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Quick Preferences</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Dark Mode</p>
                <p className="text-sm text-gray-400">Use dark theme</p>
              </div>
              <Toggle
                enabled={darkMode}
                onChange={handleDarkModeToggle}
                disabled={updateProfileMutation.isPending}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Email Notifications</p>
                <p className="text-sm text-gray-400">Receive email updates</p>
              </div>
              <Toggle
                enabled={notifPrefs.email_enabled}
                onChange={() => handleNotifPrefToggle('email_enabled')}
                disabled={updateNotifPrefsMutation.isPending}
              />
            </div>
          </div>
        </div>
      )}

      {/* Modals */}
      {showEditProfile && (
        <EditProfileModal
          user={user || {}}
          onClose={() => setShowEditProfile(false)}
          onSave={(data) => updateProfileMutation.mutate(data)}
          isLoading={updateProfileMutation.isPending}
        />
      )}

      {showChangePassword && (
        <ChangePasswordModal
          onClose={() => setShowChangePassword(false)}
          onSave={(oldPassword, newPassword) => changePasswordMutation.mutate({ oldPassword, newPassword })}
          isLoading={changePasswordMutation.isPending}
        />
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
