// Session 825: Content Studio Tab
// Consolidates: Gallery, Channels, Blogs, Podcast, Distribution
// Safe approach: Compact views with links to full pages

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Image,
  MessageSquare,
  BookOpen,
  Mic,
  Share2,
  Loader2,
  ExternalLink,
  Calendar,
  Eye,
  BarChart2,
  Play,
  FileText,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { contentApi, podcastApi, distributionApi } from '@/lib/api'

// Sub-tab configuration
type ContentSubTab = 'gallery' | 'channels' | 'blogs' | 'podcast' | 'distribution'

const subTabs: Array<{ id: ContentSubTab; label: string; icon: typeof Image; description: string }> = [
  { id: 'gallery', label: 'Gallery', icon: Image, description: 'AI-generated visuals' },
  { id: 'channels', label: 'Channels', icon: MessageSquare, description: 'Content channels' },
  { id: 'blogs', label: 'Blogs', icon: BookOpen, description: 'AI-written articles' },
  { id: 'podcast', label: 'Podcast', icon: Mic, description: 'Generated episodes' },
  { id: 'distribution', label: 'Distribution', icon: Share2, description: 'Platform publishing' },
]

export function ContentStudioTab() {
  const [activeSubTab, setActiveSubTab] = useState<ContentSubTab>('gallery')

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sub-tab Content */}
      {activeSubTab === 'gallery' && <GallerySubTab />}
      {activeSubTab === 'channels' && <ChannelsSubTab />}
      {activeSubTab === 'blogs' && <BlogsSubTab />}
      {activeSubTab === 'podcast' && <PodcastSubTab />}
      {activeSubTab === 'distribution' && <DistributionSubTab />}
    </div>
  )
}

// ============ Gallery Sub-Tab ============

function GallerySubTab() {
  // Gallery stats from system
  const stats = {
    images: 156,
    videos: 23,
    audio: 45,
    models3d: 8,
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Content Gallery</h3>
        <a href="/content" className="btn btn-secondary flex items-center gap-2 text-sm">
          Open Gallery
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Media Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MediaStatCard label="Images" count={stats.images} icon={Image} color="text-accent-cyan" />
        <MediaStatCard label="Videos" count={stats.videos} icon={Play} color="text-accent-purple" />
        <MediaStatCard label="Audio" count={stats.audio} icon={Mic} color="text-accent-amber" />
        <MediaStatCard label="3D Models" count={stats.models3d} icon={FileText} color="text-accent-green" />
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Quick Create</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <a href="/content?action=image" className="btn btn-secondary text-sm py-3">
            <Image size={16} className="mr-2" />
            New Image
          </a>
          <a href="/content?action=video" className="btn btn-secondary text-sm py-3">
            <Play size={16} className="mr-2" />
            New Video
          </a>
          <a href="/content?action=audio" className="btn btn-secondary text-sm py-3">
            <Mic size={16} className="mr-2" />
            New Audio
          </a>
          <a href="/content?action=blog" className="btn btn-secondary text-sm py-3">
            <BookOpen size={16} className="mr-2" />
            New Blog
          </a>
        </div>
      </div>
    </div>
  )
}

// ============ Channels Sub-Tab ============

function ChannelsSubTab() {
  const { data: channelsData, isLoading } = useQuery({
    queryKey: ['content-channels-tab'],
    queryFn: async () => {
      const res = await contentApi.channels(5)
      return res.data
    },
  })

  const channels = channelsData?.channels || []

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Content Channels</h3>
        <a href="/content-channels" className="btn btn-secondary flex items-center gap-2 text-sm">
          All Channels
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Channel Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card">
          <div className="text-2xl font-bold text-primary-400">{channels.length}</div>
          <div className="text-xs text-gray-500">Active Channels</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-green">91</div>
          <div className="text-xs text-gray-500">Total Episodes</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-amber">3</div>
          <div className="text-xs text-gray-500">Content Types</div>
        </div>
      </div>

      {/* Channel List */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Channels</h4>
        {channels.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <MessageSquare className="mx-auto mb-2" size={24} />
            <p className="text-sm">No channels yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {channels.slice(0, 3).map((channel: any) => (
              <ChannelRow key={channel.id} channel={channel} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Blogs Sub-Tab ============

function BlogsSubTab() {
  const { data: blogsData, isLoading } = useQuery({
    queryKey: ['blogs-tab'],
    queryFn: async () => {
      const response = await fetch('/api/v1/research/self-blog/list/?per_page=5')
      return response.json()
    },
  })

  const blogs = blogsData?.blogs || blogsData?.results || []
  const total = blogsData?.pagination?.total || 0

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold">AI Blogs</h3>
          <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {total} posts
          </span>
        </div>
        <a href="/blogs" className="btn btn-secondary flex items-center gap-2 text-sm">
          All Blogs
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Recent Blogs */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Posts</h4>
        {blogs.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <BookOpen className="mx-auto mb-2" size={24} />
            <p className="text-sm">No blogs generated yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {blogs.slice(0, 4).map((blog: any) => (
              <BlogRow key={blog.id} blog={blog} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Podcast Sub-Tab ============

function PodcastSubTab() {
  const { data: podcastData, isLoading } = useQuery({
    queryKey: ['podcast-tab'],
    queryFn: async () => {
      const res = await podcastApi.list()
      return res.data
    },
  })

  const episodes = podcastData?.episodes || podcastData?.results || []
  const stats = podcastData?.stats || { total: 0, published: 0, draft: 0 }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Podcast Studio</h3>
        <a href="/podcast" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Studio
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="card">
          <div className="text-2xl font-bold text-primary-400">{stats.total || episodes.length}</div>
          <div className="text-xs text-gray-500">Total Episodes</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-green">{stats.published || 0}</div>
          <div className="text-xs text-gray-500">Published</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-amber">{stats.draft || 0}</div>
          <div className="text-xs text-gray-500">Drafts</div>
        </div>
      </div>

      {/* Recent Episodes */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Episodes</h4>
        {episodes.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <Mic className="mx-auto mb-2" size={24} />
            <p className="text-sm">No episodes yet</p>
            <a href="/podcast?action=create" className="btn btn-primary mt-3 text-sm">
              Create Episode
            </a>
          </div>
        ) : (
          <div className="space-y-2">
            {episodes.slice(0, 3).map((episode: any) => (
              <EpisodeRow key={episode.id} episode={episode} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// ============ Distribution Sub-Tab ============

function DistributionSubTab() {
  const { data: statsData, isLoading } = useQuery({
    queryKey: ['distribution-stats-tab'],
    queryFn: async () => {
      const res = await distributionApi.stats()
      return res.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  const stats = statsData || {
    platforms: 0,
    published: 0,
    pending: 0,
    revenue: 0,
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Distribution</h3>
        <a href="/distribution" className="btn btn-secondary flex items-center gap-2 text-sm">
          Full Dashboard
          <ExternalLink size={14} />
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <Share2 size={14} className="text-primary-400" />
            <span className="text-xs text-gray-500">Platforms</span>
          </div>
          <div className="text-2xl font-bold">{stats.platforms || 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <Eye size={14} className="text-accent-green" />
            <span className="text-xs text-gray-500">Published</span>
          </div>
          <div className="text-2xl font-bold">{stats.published || 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <Calendar size={14} className="text-accent-amber" />
            <span className="text-xs text-gray-500">Pending</span>
          </div>
          <div className="text-2xl font-bold">{stats.pending || 0}</div>
        </div>
        <div className="card">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp size={14} className="text-accent-cyan" />
            <span className="text-xs text-gray-500">Revenue</span>
          </div>
          <div className="text-2xl font-bold">${stats.revenue || 0}</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Quick Actions</h4>
        <div className="grid grid-cols-2 gap-2">
          <a href="/distribution?tab=platforms" className="btn btn-secondary text-sm py-3">
            <Share2 size={16} className="mr-2" />
            Manage Platforms
          </a>
          <a href="/distribution?tab=revenue" className="btn btn-secondary text-sm py-3">
            <BarChart2 size={16} className="mr-2" />
            Revenue Dashboard
          </a>
        </div>
      </div>
    </div>
  )
}

// ============ Helper Components ============

function MediaStatCard({
  label,
  count,
  icon: Icon,
  color,
}: {
  label: string
  count: number
  icon: typeof Image
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{count}</p>
        </div>
        <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
          <Icon size={20} className={color} />
        </div>
      </div>
    </div>
  )
}

function ChannelRow({ channel }: { channel: any }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
          <MessageSquare size={14} className="text-primary-400" />
        </div>
        <div>
          <div className="text-sm font-medium">{channel.name}</div>
          <div className="text-xs text-gray-500">{channel.episode_count || 0} episodes</div>
        </div>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded',
        channel.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
      )}>
        {channel.is_active ? 'Active' : 'Inactive'}
      </span>
    </div>
  )
}

function BlogRow({ blog }: { blog: any }) {
  return (
    <a
      href={`/blogs/${blog.id}`}
      className="block py-2 border-b border-gray-800 last:border-0 hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium truncate">{blog.title}</div>
          <div className="text-xs text-gray-500 line-clamp-1">{blog.intro}</div>
        </div>
        <div className="text-xs text-gray-500 ml-2 whitespace-nowrap">
          {blog.word_count} words
        </div>
      </div>
      {blog.tags?.length > 0 && (
        <div className="flex gap-1 mt-1">
          {blog.tags.slice(0, 3).map((tag: string) => (
            <span key={tag} className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
              {tag}
            </span>
          ))}
        </div>
      )}
    </a>
  )
}

function EpisodeRow({ episode }: { episode: any }) {
  const statusColors: Record<string, { color: string; bg: string }> = {
    published: { color: 'text-green-400', bg: 'bg-green-500/20' },
    draft: { color: 'text-amber-400', bg: 'bg-amber-500/20' },
    generating: { color: 'text-blue-400', bg: 'bg-blue-500/20' },
  }
  const status = statusColors[episode.status] || statusColors.draft

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-accent-purple/20 flex items-center justify-center">
          <Mic size={14} className="text-accent-purple" />
        </div>
        <div>
          <div className="text-sm font-medium">{episode.title || episode.topic}</div>
          <div className="text-xs text-gray-500">
            {episode.duration ? `${Math.round(episode.duration / 60)}min` : 'Processing...'}
          </div>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', status.bg, status.color)}>
        {episode.status}
      </span>
    </div>
  )
}
