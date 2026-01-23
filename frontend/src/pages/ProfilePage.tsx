import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { settingsApi } from '@/lib/api'
import {
  User, MapPin, Briefcase, Calendar, Edit2, Save, X,
  Image, Video, FileText, BookOpen, Zap,
  Loader2, Sparkles, CheckCircle, XCircle,
  TrendingUp, Clock, Star
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface ProfileData {
  user: {
    id: number
    username: string
    email: string
    first_name: string
    last_name: string
    date_joined: string
  }
  profile: {
    avatar: string | null
    bio: string
    display_name: string
    occupation: string
    location: string
    account_type: string
    credits_remaining: number
    storage_used_mb: number
    last_active: string
    preferred_ai_model: string
    default_content_tone: string
  }
  statistics: {
    total_contents: number
    total_images: number
    total_videos: number
    total_blogs: number
    total_social_posts: number
    total_ebooks: number
    total_research_docs: number
    total_agents: number
    total_ai_requests: number
    total_tokens_used: number
    total_exports: number
    favorite_style: string
  }
}

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

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: number | string; color: string }) {
  return (
    <div className="card p-4">
      <div className="flex items-center gap-3">
        <div className={cn('h-10 w-10 rounded-lg flex items-center justify-center', color)}>
          <Icon size={20} className="text-white" />
        </div>
        <div>
          <p className="text-2xl font-bold">{value}</p>
          <p className="text-sm text-gray-400">{label}</p>
        </div>
      </div>
    </div>
  )
}

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const queryClient = useQueryClient()

  // Editable fields
  const [editForm, setEditForm] = useState({
    display_name: '',
    bio: '',
    occupation: '',
    location: '',
  })

  // Fetch profile data
  const { data: profileResponse, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: () => settingsApi.getProfile(),
  })

  const profileData: ProfileData | null = profileResponse?.data || null

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: (data: Record<string, string>) => settingsApi.updateProfile(data),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Profile updated successfully!' })
      setIsEditing(false)
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to update profile' })
    },
  })

  // Generate avatar mutation
  const generateAvatarMutation = useMutation({
    mutationFn: () => settingsApi.generateAvatar(),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'New avatar generated!' })
      queryClient.invalidateQueries({ queryKey: ['profile'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate avatar' })
    },
  })

  // Start editing
  const handleStartEdit = () => {
    if (profileData) {
      setEditForm({
        display_name: profileData.profile.display_name || '',
        bio: profileData.profile.bio || '',
        occupation: profileData.profile.occupation || '',
        location: profileData.profile.location || '',
      })
      setIsEditing(true)
    }
  }

  // Save edits
  const handleSave = () => {
    updateProfileMutation.mutate(editForm)
  }

  // Format date
  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    } catch {
      return 'Unknown'
    }
  }

  // Format relative time
  const formatRelativeTime = (dateString: string) => {
    try {
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now.getTime() - date.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return formatDate(dateString)
    } catch {
      return 'Unknown'
    }
  }

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 size={32} className="animate-spin text-primary-400" />
      </div>
    )
  }

  if (!profileData) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-gray-400">Failed to load profile</p>
      </div>
    )
  }

  const { user, profile, statistics } = profileData

  return (
    <div className="max-w-5xl space-y-6">
      {/* Profile Header */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-6">
          {/* Avatar Section */}
          <div className="flex flex-col items-center gap-3">
            <div className="relative">
              <div className="h-32 w-32 rounded-full bg-primary-600 flex items-center justify-center text-4xl font-bold overflow-hidden ring-4 ring-primary-500/30">
                {profile.avatar ? (
                  <img src={profile.avatar} alt="Avatar" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-white">
                    {(profile.display_name || user.username)?.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <button
                className="absolute bottom-0 right-0 h-10 w-10 rounded-full bg-primary-500 flex items-center justify-center hover:bg-primary-600 transition-colors shadow-lg"
                onClick={() => generateAvatarMutation.mutate()}
                disabled={generateAvatarMutation.isPending}
                title="Generate new avatar"
              >
                {generateAvatarMutation.isPending ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Sparkles size={18} />
                )}
              </button>
            </div>
            <div className={cn(
              'px-3 py-1 rounded-full text-xs font-medium',
              profile.account_type === 'premium' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-600/20 text-gray-400'
            )}>
              {profile.account_type === 'premium' ? (
                <span className="flex items-center gap-1"><Star size={12} /> Premium</span>
              ) : (
                'Free Plan'
              )}
            </div>
          </div>

          {/* Info Section */}
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.display_name}
                    onChange={(e) => setEditForm({ ...editForm, display_name: e.target.value })}
                    className="text-2xl font-bold bg-dark-bg border border-dark-border rounded-lg px-3 py-1 w-full max-w-xs focus:outline-none focus:border-primary-500"
                    placeholder="Display Name"
                  />
                ) : (
                  <h1 className="text-2xl font-bold">{profile.display_name || user.username}</h1>
                )}
                <p className="text-gray-400">@{user.username}</p>
              </div>
              <div className="flex gap-2">
                {isEditing ? (
                  <>
                    <button
                      className="btn btn-secondary text-sm"
                      onClick={() => setIsEditing(false)}
                    >
                      <X size={16} />
                      Cancel
                    </button>
                    <button
                      className="btn btn-primary text-sm"
                      onClick={handleSave}
                      disabled={updateProfileMutation.isPending}
                    >
                      {updateProfileMutation.isPending ? (
                        <Loader2 size={16} className="animate-spin" />
                      ) : (
                        <Save size={16} />
                      )}
                      Save
                    </button>
                  </>
                ) : (
                  <button
                    className="btn btn-secondary text-sm"
                    onClick={handleStartEdit}
                  >
                    <Edit2 size={16} />
                    Edit Profile
                  </button>
                )}
              </div>
            </div>

            {/* Bio */}
            <div className="mb-4">
              {isEditing ? (
                <textarea
                  value={editForm.bio}
                  onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-gray-300 focus:outline-none focus:border-primary-500 resize-none"
                  rows={3}
                  placeholder="Write a short bio..."
                />
              ) : (
                <p className="text-gray-300">
                  {profile.bio || 'No bio yet. Click Edit Profile to add one!'}
                </p>
              )}
            </div>

            {/* Meta Info */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-1">
                <Briefcase size={14} />
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.occupation}
                    onChange={(e) => setEditForm({ ...editForm, occupation: e.target.value })}
                    className="bg-dark-bg border border-dark-border rounded px-2 py-0.5 text-gray-300 focus:outline-none focus:border-primary-500 w-32"
                    placeholder="Occupation"
                  />
                ) : (
                  <span>{profile.occupation || 'Not specified'}</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <MapPin size={14} />
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.location}
                    onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                    className="bg-dark-bg border border-dark-border rounded px-2 py-0.5 text-gray-300 focus:outline-none focus:border-primary-500 w-32"
                    placeholder="Location"
                  />
                ) : (
                  <span>{profile.location || 'Not specified'}</span>
                )}
              </div>
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                <span>Joined {formatDate(user.date_joined)}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock size={14} />
                <span>Active {formatRelativeTime(profile.last_active)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Creation Stats</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={FileText}
            label="Total Content"
            value={statistics.total_contents}
            color="bg-primary-600"
          />
          <StatCard
            icon={Image}
            label="Images"
            value={statistics.total_images}
            color="bg-accent-purple"
          />
          <StatCard
            icon={Video}
            label="Videos"
            value={statistics.total_videos}
            color="bg-accent-pink"
          />
          <StatCard
            icon={BookOpen}
            label="Blog Posts"
            value={statistics.total_blogs}
            color="bg-accent-cyan"
          />
        </div>
      </div>

      {/* More Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Content Breakdown */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Content Breakdown</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Social Posts</span>
              <span className="font-medium">{statistics.total_social_posts}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">E-Books</span>
              <span className="font-medium">{statistics.total_ebooks}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Research Docs</span>
              <span className="font-medium">{statistics.total_research_docs}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Custom Agents</span>
              <span className="font-medium">{statistics.total_agents}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Exports</span>
              <span className="font-medium">{statistics.total_exports}</span>
            </div>
          </div>
        </div>

        {/* AI Usage */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">AI Usage</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400">AI Requests</span>
                <span className="font-medium">{statistics.total_ai_requests.toLocaleString()}</span>
              </div>
              <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-primary-600 to-accent-purple rounded-full"
                  style={{ width: `${Math.min((statistics.total_ai_requests / 10000) * 100, 100)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-400">Tokens Used</span>
                <span className="font-medium">{((statistics.total_tokens_used ?? 0) / 1000).toFixed(1)}K</span>
              </div>
              <div className="h-2 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-accent-cyan to-accent-green rounded-full"
                  style={{ width: `${Math.min((statistics.total_tokens_used / 1000000) * 100, 100)}%` }}
                />
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-dark-border">
              <span className="text-gray-400">Favorite Style</span>
              <span className="font-medium capitalize">{statistics.favorite_style}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Account Info */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Account Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-accent-green/20 flex items-center justify-center">
              <Zap size={20} className="text-accent-green" />
            </div>
            <div>
              <p className="text-2xl font-bold">{profile.credits_remaining.toLocaleString()}</p>
              <p className="text-sm text-gray-400">Credits Remaining</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-accent-amber/20 flex items-center justify-center">
              <TrendingUp size={20} className="text-accent-amber" />
            </div>
            <div>
              <p className="text-2xl font-bold">{(profile.storage_used_mb ?? 0).toFixed(1)} MB</p>
              <p className="text-sm text-gray-400">Storage Used</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center">
              <User size={20} className="text-primary-400" />
            </div>
            <div>
              <p className="text-lg font-bold">{user.email}</p>
              <p className="text-sm text-gray-400">Email Address</p>
            </div>
          </div>
        </div>
      </div>

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
