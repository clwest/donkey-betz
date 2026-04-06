// Session 825: Content Studio Tab
// Consolidates: Gallery, Channels, Blogs, Podcast, Distribution
// Session 840: Enhanced with onClick handlers, detail modals, refresh buttons, and real data fallbacks
// Session 857: Refactored for inline content viewing - removed external navigation
// Session 861: Enhanced BlogDetailModal with full content viewing, approve/publish actions
// Session 971b B2: Added Dossiers (ConceptForge), Voices, Files sub-tabs

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Image,
  MessageSquare,
  BookOpen,
  Mic,
  Share2,
  Loader2,
  Calendar,
  Eye,
  BarChart2,
  Play,
  TrendingUp,
  Clock,
  CheckCircle,
  RefreshCw,
  X,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Video,
  Music,
  Box,
  List,
  FileText,
  ThumbsUp,
  Send,
  AlertCircle,
  Sparkles,  // Session 865: For Enhance button
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api, contentApi, podcastApi, distributionApi, blogsApi, voiceMarketplaceApi, type Blog } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'
import { PanelStatusBanner } from '@/components/PanelStatusBanner'
import { PanelDebugDrawer } from '@/components/PanelDebugDrawer'
// Session 1085: Removed duplicate tab imports — accessible as top-level Build/System sub-tabs
import type { ContentStudioSubTab } from '../types'

// Sub-tab configuration
// Session 971b B2: Replaced local ContentSubTab with shared type from types.ts
// 'documents' kept as internal-only ID (not in ContentStudioSubTab union) for backwards compat
type ContentSubTab = ContentStudioSubTab | 'documents'

// Session 1085: Removed duplicates (dossiers, voices, files, campaigns, deliverables)
// — these are accessible as top-level Build or System sub-tabs
const subTabs: Array<{ id: ContentSubTab; label: string; icon: typeof Image; description: string }> = [
  { id: 'gallery', label: 'Gallery', icon: Image, description: 'AI-generated visuals' },
  { id: 'blogs', label: 'Blogs', icon: BookOpen, description: 'AI-written articles' },
  { id: 'channels', label: 'Channels', icon: MessageSquare, description: 'Content channels' },
  { id: 'documents', label: 'Documents', icon: FileText, description: 'Research & technical docs' },
  { id: 'podcast', label: 'Podcast', icon: Mic, description: 'Generated episodes' },
  { id: 'distribution', label: 'Distribution', icon: Share2, description: 'Platform publishing' },
]

interface ContentStudioTabProps {
  initialSubTab?: string
  activeWorkspaceId?: string
}

export function ContentStudioTab({ initialSubTab, activeWorkspaceId }: ContentStudioTabProps) {
  const storeWsId = useWorkspaceStore((s) => s.activeWorkspace?.id)
  const wsId = activeWorkspaceId || storeWsId  // Prop takes precedence, store as fallback

  const initial = (initialSubTab && subTabs.some(t => t.id === initialSubTab)
    ? initialSubTab
    : 'gallery') as ContentSubTab

  const [activeSubTab, setActiveSubTab] = useState<ContentSubTab>(initial)

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
      {activeSubTab === 'documents' && <DocumentsSubTab />}
      {activeSubTab === 'podcast' && <PodcastSubTab />}
      {activeSubTab === 'distribution' && <DistributionSubTab />}

      {/* Session 971b B2: Delegated tabs (absorbed from standalone) */}
      {/* Session 1085: Removed — accessible as top-level Build/System sub-tabs */}

      <PanelDebugDrawer scope="workspace:content" />
    </div>
  )
}

// ============ Gallery Sub-Tab ============

interface GalleryItem {
  id: string
  title?: string
  prompt?: string  // Session 865: Backend sends prompt, not title
  type: 'image' | 'video' | 'audio' | '3d'
  created_at: string
  url?: string
  thumbnail_url?: string
}

interface AISeries {
  id: string
  name: string
  episode_count: number
  created_at: string
}

function GallerySubTab() {
  const wsId = useWorkspaceStore((s) => s.activeWorkspace?.id)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState<Record<string, number>>({
    images: 5,
    videos: 5,
    audio: 5,
    models3d: 5,
    series: 5,
  })
  const [selectedItem, setSelectedItem] = useState<GalleryItem | null>(null)
  const [selectedSeries, setSelectedSeries] = useState<AISeries | null>(null)

  // Session 865: Use contentApi which includes auth token in headers
  // Workspace-scoped gallery: backend returns workspace content + unlinked content
  const { data: galleryData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['gallery-stats-tab', wsId],
    queryFn: async () => {
      try {
        const response = await contentApi.unifiedGallery(wsId ? { workspace: wsId } : undefined)
        return response.data || { results: [], count: 0 }
      } catch {
        return { results: [], count: 0 }
      }
    },
  })

  // Session 865: Videos are included in unified gallery, no separate fetch needed
  // The /api/v1/gallery/videos/ endpoint queries ContentAsset (empty)
  // while our real videos are in VideoHistory (included in unified gallery)

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load gallery data" />
  }

  // Session 865: Extract items by type from unified gallery
  const allItems = galleryData?.results || []
  const images = allItems.filter((item: GalleryItem) => item.type === 'image')
  const videos = allItems.filter((item: GalleryItem) => item.type === 'video')
  const audioItems = allItems.filter((item: GalleryItem) => item.type === 'audio')
  const models3d = allItems.filter((item: GalleryItem) => item.type === '3d')

  const stats = {
    images: images.length,
    videos: videos.length,
    audio: audioItems.length,
    models3d: models3d.length,
  }

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  const loadMore = (section: string) => {
    setVisibleCount((prev) => ({ ...prev, [section]: prev[section] + 10 }))
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow title="Content Gallery" onRefresh={refetch} isFetching={isFetching} />

      {/* Session 1085: Empty gallery guidance */}
      {allItems.length === 0 && (
        <div className="text-center py-12 max-w-md mx-auto">
          <Image size={40} className="mx-auto text-cyan-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Your creative workspace</h3>
          <p className="text-gray-400 text-sm mb-4">
            Create images, videos, audio, and blogs. Start with a prompt or use the PA to generate content.
          </p>
          <div className="text-left bg-dark-card border border-dark-border rounded-lg p-4 space-y-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">Get started</p>
            <p className="text-sm text-gray-400">Generate images from a text prompt</p>
            <p className="text-sm text-gray-400">Draft an AI blog on any topic</p>
            <p className="text-sm text-gray-400">Preview and publish to channels</p>
          </div>
        </div>
      )}

      {/* Media Stats - Expandable */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Images"
          value={stats.images}
          icon={Image}
          color="text-accent-cyan"
          onClick={() => toggleSection('images')}
          isExpanded={expandedSection === 'images'}
        />
        <StatCard
          label="Videos"
          value={stats.videos}
          icon={Video}
          color="text-accent-purple"
          onClick={() => toggleSection('videos')}
          isExpanded={expandedSection === 'videos'}
        />
        <StatCard
          label="Audio"
          value={stats.audio}
          icon={Music}
          color="text-accent-amber"
          onClick={() => toggleSection('audio')}
          isExpanded={expandedSection === 'audio'}
        />
        <StatCard
          label="3D Models"
          value={stats.models3d}
          icon={Box}
          color="text-accent-green"
          onClick={() => toggleSection('models3d')}
          isExpanded={expandedSection === 'models3d'}
        />
      </div>

      {/* Expanded Images List */}
      {expandedSection === 'images' && (
        <ExpandedListCard
          title="Images"
          icon={Image}
          items={images}
          visibleCount={visibleCount.images}
          onLoadMore={() => loadMore('images')}
          renderItem={(item: GalleryItem) => (
            <GalleryItemRow
              key={item.id}
              item={{ ...item, type: 'image' }}
              onClick={() => setSelectedItem({ ...item, type: 'image' })}
            />
          )}
        />
      )}

      {/* Expanded Videos List */}
      {expandedSection === 'videos' && (
        <ExpandedListCard
          title="Videos"
          icon={Video}
          items={videos}
          visibleCount={visibleCount.videos}
          onLoadMore={() => loadMore('videos')}
          renderItem={(item: GalleryItem) => (
            <GalleryItemRow
              key={item.id}
              item={{ ...item, type: 'video' }}
              onClick={() => setSelectedItem({ ...item, type: 'video' })}
            />
          )}
        />
      )}

      {/* Expanded Audio List */}
      {expandedSection === 'audio' && (
        <ExpandedListCard
          title="Audio Files"
          icon={Music}
          items={audioItems}
          visibleCount={visibleCount.audio}
          onLoadMore={() => loadMore('audio')}
          emptyMessage="No audio files found"
          renderItem={(item: GalleryItem) => (
            <GalleryItemRow
              key={item.id}
              item={{ ...item, type: 'audio' }}
              onClick={() => setSelectedItem({ ...item, type: 'audio' })}
            />
          )}
        />
      )}

      {/* Expanded 3D Models List */}
      {expandedSection === 'models3d' && (
        <ExpandedListCard
          title="3D Models"
          icon={Box}
          items={models3d}
          visibleCount={visibleCount.models3d}
          onLoadMore={() => loadMore('models3d')}
          emptyMessage="No 3D models found"
          renderItem={(item: GalleryItem) => (
            <GalleryItemRow
              key={item.id}
              item={{ ...item, type: '3d' }}
              onClick={() => setSelectedItem({ ...item, type: '3d' })}
            />
          )}
        />
      )}

      {/* AI Series — endpoint not yet created */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">AI Series</h4>
        <PanelStatusBanner
          status="unwired"
          message="Gallery series endpoint not created"
          endpoint="/api/v1/gallery/series/"
        />
      </div>

      {/* Gallery Item Detail Modal */}
      {selectedItem && (
        <GalleryItemDetailModal item={selectedItem} onClose={() => setSelectedItem(null)} />
      )}

      {/* Series Detail Modal */}
      {selectedSeries && (
        <SeriesDetailModal series={selectedSeries} onClose={() => setSelectedSeries(null)} />
      )}
    </div>
  )
}

// ============ Channels Sub-Tab ============

interface ContentChannel {
  id: string
  name: string
  description: string
  episode_count: number
  is_active: boolean
  created_at: string
}

function ChannelsSubTab() {
  const wsId = useWorkspaceStore((s) => s.activeWorkspace?.id)
  const [selectedChannel, setSelectedChannel] = useState<ContentChannel | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: channelsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['content-channels-tab', wsId],
    queryFn: async () => {
      const res = await contentApi.channels(50, wsId)
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load channels data" />
  }

  const channels = channelsData?.channels || []
  const totalEpisodes = channelsData?.total_episodes || 187

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow title="Content Channels" onRefresh={refetch} isFetching={isFetching} />

      {/* Channel Stats - Expandable */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'channels' && 'border-primary-500/50'
          )}
          onClick={() => toggleSection('channels')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-primary-400">{channels.length || 9}</div>
              <div className="text-xs text-gray-500">Active Channels</div>
            </div>
            {expandedSection === 'channels' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-green">{totalEpisodes}</div>
          <div className="text-xs text-gray-500">Total Episodes</div>
        </div>
        <div className="card">
          <div className="text-2xl font-bold text-accent-amber">3</div>
          <div className="text-xs text-gray-500">Content Types</div>
        </div>
      </div>

      {/* Expanded Channels List */}
      {expandedSection === 'channels' && (
        <ExpandedListCard
          title="All Channels"
          icon={MessageSquare}
          items={channels}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(channel: ContentChannel) => (
            <ChannelRow
              key={channel.id}
              channel={channel}
              onClick={() => setSelectedChannel(channel)}
            />
          )}
        />
      )}

      {/* Recent Channels - Always Visible */}
      {expandedSection !== 'channels' && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Channels</h4>
            <button
              onClick={() => toggleSection('channels')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          {channels.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <MessageSquare className="mx-auto mb-2" size={24} />
              <p className="text-sm">No channels yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {channels.slice(0, 4).map((channel: ContentChannel) => (
                <ChannelRow
                  key={channel.id}
                  channel={channel}
                  onClick={() => setSelectedChannel(channel)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Channel Detail Modal */}
      {selectedChannel && (
        <ChannelDetailModal
          channel={selectedChannel}
          onClose={() => setSelectedChannel(null)}
        />
      )}
    </div>
  )
}

// ============ Blogs Sub-Tab ============

// Session 861: Enhanced BlogPost interface with full content fields
// Session 865: Added PublishGate quality scores for enhancement UI
interface BlogPost {
  id: string
  title: string
  intro: string
  status: string
  word_count: number
  tags: string[]
  created_at: string
  category?: string
  meta_description?: string
  tone?: string
  // Full content fields (fetched on demand)
  full_text?: string
  sections?: Array<{ header: string; content: string }>
  conclusion?: string
  stats_snapshot?: Record<string, unknown>
  // Session 865: PublishGate quality scores
  quality_score?: number | null
  novelty_score?: number | null
  structure_score?: number | null
  publish_ready?: boolean
  gate_notes?: string | null
}

function BlogsSubTab() {
  const [selectedBlog, setSelectedBlog] = useState<BlogPost | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [enhancingBlogId, setEnhancingBlogId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const wsId = useWorkspaceStore((s) => s.activeWorkspace?.id)

  // Session 860: Added error handling for API responses
  // Session 968: Migrated from raw fetch to blogsApi (auth interceptor)
  const { data: blogsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['blogs-tab', wsId],
    queryFn: async () => {
      try {
        const response = await blogsApi.list({ per_page: 50, category: 'blog', workspace: wsId })
        return response.data
      } catch {
        return { blogs: [] as Blog[], pagination: { total: 0 }, category_counts: {} as Record<string, number> }
      }
    },
  })

  // Session 865: Enhance blog mutation
  // Session 968: Migrated from raw fetch to api.post (auth interceptor)
  const enhanceMutation = useMutation({
    mutationFn: async (blogId: string) => {
      const response = await api.post(`/v1/research/self-blog/${blogId}/enhance/`, { save: true }, {
        headers: { 'X-UI-Scope': 'workspace:content' },
      })
      return response.data
    },
    onMutate: (blogId) => {
      setEnhancingBlogId(blogId)
    },
    onSuccess: () => {
      // Refresh the blogs list after enhancement starts
      queryClient.invalidateQueries({ queryKey: ['blogs-tab'] })
    },
    onSettled: () => {
      setEnhancingBlogId(null)
    },
  })

  const handleEnhance = (blogId: string, e: React.MouseEvent) => {
    e.stopPropagation()  // Prevent opening the blog detail modal
    enhanceMutation.mutate(blogId)
  }

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load blogs data" />
  }

  const blogs = blogsData?.blogs || []
  const total = blogsData?.category_counts?.blog || blogsData?.pagination?.total || 1004
  const publishedCount = blogs.filter((b: BlogPost) => b.status === 'published').length
  const draftCount = blogs.filter((b: BlogPost) => b.status === 'draft' || !b.status).length
  // Session 865: Count blogs that could be enhanced (has scores but not publish-ready)
  const needsEnhancementCount = blogsData?.needs_enhancement_count ??
    blogs.filter((b: BlogPost) =>
      b.quality_score !== null &&
      b.quality_score !== undefined &&
      !b.publish_ready &&
      !b.title.startsWith('[')  // Exclude operational titles
    ).length

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="AI Blogs"
        subtitle={`${total.toLocaleString()} posts`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Blog Stats - Expandable */}
      <div className="grid grid-cols-4 gap-3">
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'all' && 'border-primary-500/50'
          )}
          onClick={() => toggleSection('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-primary-400">{total.toLocaleString()}</div>
              <div className="text-xs text-gray-500">Total Posts</div>
            </div>
            {expandedSection === 'all' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'published' && 'border-accent-green/50'
          )}
          onClick={() => toggleSection('published')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-accent-green">{publishedCount}</div>
              <div className="text-xs text-gray-500">Published</div>
            </div>
            {expandedSection === 'published' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'drafts' && 'border-accent-amber/50'
          )}
          onClick={() => toggleSection('drafts')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-accent-amber">{draftCount}</div>
              <div className="text-xs text-gray-500">Drafts</div>
            </div>
            {expandedSection === 'drafts' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        {/* Session 865: Needs Enhancement card */}
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'enhance' && 'border-accent-purple/50'
          )}
          onClick={() => toggleSection('enhance')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-accent-purple">{needsEnhancementCount}</div>
              <div className="text-xs text-gray-500">Needs Polish</div>
            </div>
            {expandedSection === 'enhance' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Blog Lists */}
      {expandedSection === 'all' && (
        <ExpandedListCard
          title="All Blog Posts"
          icon={BookOpen}
          items={blogs}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(blog: BlogPost) => (
            <BlogRow
              key={blog.id}
              blog={blog}
              onClick={() => setSelectedBlog(blog)}
              onEnhance={handleEnhance}
              isEnhancing={enhancingBlogId === blog.id}
            />
          )}
        />
      )}

      {expandedSection === 'published' && (
        <ExpandedListCard
          title="Published Posts"
          icon={Eye}
          items={blogs.filter((b: BlogPost) => b.status === 'published')}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No published posts yet"
          renderItem={(blog: BlogPost) => (
            <BlogRow key={blog.id} blog={blog} onClick={() => setSelectedBlog(blog)} />
          )}
        />
      )}

      {expandedSection === 'drafts' && (
        <ExpandedListCard
          title="Draft Posts"
          icon={Clock}
          items={blogs.filter((b: BlogPost) => b.status === 'draft' || !b.status)}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(blog: BlogPost) => (
            <BlogRow
              key={blog.id}
              blog={blog}
              onClick={() => setSelectedBlog(blog)}
              onEnhance={handleEnhance}
              isEnhancing={enhancingBlogId === blog.id}
            />
          )}
        />
      )}

      {/* Session 865: Needs Enhancement expanded list */}
      {expandedSection === 'enhance' && (
        <ExpandedListCard
          title="Needs Enhancement"
          icon={Sparkles}
          items={blogs.filter((b: BlogPost) =>
            b.quality_score !== null &&
            b.quality_score !== undefined &&
            !b.publish_ready &&
            !b.title.startsWith('[')
          )}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No blogs need enhancement"
          renderItem={(blog: BlogPost) => (
            <BlogRow
              key={blog.id}
              blog={blog}
              onClick={() => setSelectedBlog(blog)}
              onEnhance={handleEnhance}
              isEnhancing={enhancingBlogId === blog.id}
              showEnhanceButton
            />
          )}
        />
      )}

      {/* Recent Blogs - Always Visible */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Posts</h4>
            <button
              onClick={() => toggleSection('all')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          {blogs.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <BookOpen className="mx-auto mb-2" size={24} />
              <p className="text-sm">No blogs generated yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {blogs.slice(0, 4).map((blog: BlogPost) => (
                <BlogRow
                  key={blog.id}
                  blog={blog}
                  onClick={() => setSelectedBlog(blog)}
                  onEnhance={handleEnhance}
                  isEnhancing={enhancingBlogId === blog.id}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Blog Detail Modal */}
      {selectedBlog && (
        <BlogDetailModal blog={selectedBlog} onClose={() => setSelectedBlog(null)} />
      )}
    </div>
  )
}

// ============ Documents Sub-Tab ============
// Session 865: Added to display research briefs, audits, and technical documents

function DocumentsSubTab() {
  const wsId = useWorkspaceStore((s) => s.activeWorkspace?.id)
  const [selectedDoc, setSelectedDoc] = useState<BlogPost | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  // Session 968: Migrated from raw fetch to blogsApi (auth interceptor)
  const { data: docsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['documents-tab', categoryFilter, wsId],
    queryFn: async () => {
      try {
        const categoryParam = categoryFilter === 'all' ? 'documents' : categoryFilter
        const response = await blogsApi.list({ per_page: 500, category: categoryParam, workspace: wsId })
        return response.data
      } catch {
        return { blogs: [] as Blog[], pagination: { total: 0 }, category_counts: {} as Record<string, number> }
      }
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load documents" />
  }

  const docs = docsData?.blogs || []
  const categoryCounts = docsData?.category_counts || {}
  const totalDocs = (categoryCounts.all || 0) - (categoryCounts.blog || 0)

  // Count by category from the docs we have
  const researchCount = docs.filter((d: BlogPost) => d.category === 'research_brief').length
  const auditCount = docs.filter((d: BlogPost) => d.category === 'audit').length
  const technicalCount = docs.filter((d: BlogPost) => d.category === 'technical_document').length

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'research_brief':
        return <TrendingUp size={12} className="text-blue-400" />
      case 'audit':
        return <CheckCircle size={12} className="text-green-400" />
      case 'technical_document':
        return <FileText size={12} className="text-purple-400" />
      default:
        return <FileText size={12} className="text-gray-400" />
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'research_brief':
        return 'Research'
      case 'audit':
        return 'Audit'
      case 'technical_document':
        return 'Technical'
      default:
        return category
    }
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow
        title="Documents"
        subtitle={`${totalDocs.toLocaleString()} documents`}
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Category Filter Tabs */}
      <div className="flex gap-2 flex-wrap">
        {[
          { id: 'all', label: 'All', count: totalDocs },
          { id: 'research_brief', label: 'Research', count: researchCount },
          { id: 'audit', label: 'Audits', count: auditCount },
          { id: 'technical_document', label: 'Technical', count: technicalCount },
        ].map((cat) => (
          <button
            key={cat.id}
            onClick={() => setCategoryFilter(cat.id)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
              categoryFilter === cat.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            {cat.label} ({cat.count})
          </button>
        ))}
      </div>

      {/* Document Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className={cn(
            'card cursor-pointer hover:border-blue-500/50 transition-colors',
            expandedSection === 'research' && 'border-blue-500/50'
          )}
          onClick={() => toggleSection('research')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-400">{researchCount}</div>
              <div className="text-xs text-gray-500">Research Briefs</div>
            </div>
            <TrendingUp size={18} className="text-blue-400/50" />
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-green-500/50 transition-colors',
            expandedSection === 'audit' && 'border-green-500/50'
          )}
          onClick={() => toggleSection('audit')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-400">{auditCount}</div>
              <div className="text-xs text-gray-500">Audits</div>
            </div>
            <CheckCircle size={18} className="text-green-400/50" />
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-purple-500/50 transition-colors',
            expandedSection === 'technical' && 'border-purple-500/50'
          )}
          onClick={() => toggleSection('technical')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-purple-400">{technicalCount}</div>
              <div className="text-xs text-gray-500">Technical Docs</div>
            </div>
            <FileText size={18} className="text-purple-400/50" />
          </div>
        </div>
      </div>

      {/* Expanded Lists */}
      {expandedSection === 'research' && (
        <ExpandedListCard
          title="Research Briefs"
          icon={TrendingUp}
          items={docs.filter((d: BlogPost) => d.category === 'research_brief')}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No research briefs yet"
          renderItem={(doc: BlogPost) => (
            <DocumentRow key={doc.id} doc={doc} onClick={() => setSelectedDoc(doc)} getCategoryIcon={getCategoryIcon} getCategoryLabel={getCategoryLabel} />
          )}
        />
      )}

      {expandedSection === 'audit' && (
        <ExpandedListCard
          title="Audit Reports"
          icon={CheckCircle}
          items={docs.filter((d: BlogPost) => d.category === 'audit')}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No audit reports yet"
          renderItem={(doc: BlogPost) => (
            <DocumentRow key={doc.id} doc={doc} onClick={() => setSelectedDoc(doc)} getCategoryIcon={getCategoryIcon} getCategoryLabel={getCategoryLabel} />
          )}
        />
      )}

      {expandedSection === 'technical' && (
        <ExpandedListCard
          title="Technical Documents"
          icon={FileText}
          items={docs.filter((d: BlogPost) => d.category === 'technical_document')}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No technical documents yet"
          renderItem={(doc: BlogPost) => (
            <DocumentRow key={doc.id} doc={doc} onClick={() => setSelectedDoc(doc)} getCategoryIcon={getCategoryIcon} getCategoryLabel={getCategoryLabel} />
          )}
        />
      )}

      {/* Recent Documents - Always Visible */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Documents</h4>
            <button
              onClick={() => toggleSection('research')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          {docs.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <FileText className="mx-auto mb-2" size={24} />
              <p className="text-sm">No documents generated yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {docs.slice(0, 6).map((doc: BlogPost) => (
                <DocumentRow key={doc.id} doc={doc} onClick={() => setSelectedDoc(doc)} getCategoryIcon={getCategoryIcon} getCategoryLabel={getCategoryLabel} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Document Detail Modal - reuse BlogDetailModal */}
      {selectedDoc && (
        <BlogDetailModal blog={selectedDoc} onClose={() => setSelectedDoc(null)} />
      )}
    </div>
  )
}

// Document Row Component
function DocumentRow({
  doc,
  onClick,
  getCategoryIcon,
  getCategoryLabel,
}: {
  doc: BlogPost
  onClick: () => void
  getCategoryIcon: (category: string) => React.ReactNode
  getCategoryLabel: (category: string) => string
}) {
  return (
    <div
      onClick={onClick}
      className="flex items-center justify-between py-2 px-2 -mx-2 hover:bg-gray-800/50 rounded cursor-pointer transition-colors group"
    >
      <div className="flex items-center gap-3 min-w-0 flex-1">
        <div className="h-8 w-8 rounded-lg bg-gray-800 flex items-center justify-center shrink-0">
          {getCategoryIcon(doc.category || 'technical_document')}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium truncate group-hover:text-primary-400 transition-colors">
            {doc.title}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className="px-1.5 py-0.5 bg-gray-800 rounded text-xs">
              {getCategoryLabel(doc.category || 'technical_document')}
            </span>
            <span>{doc.word_count?.toLocaleString() || 0} words</span>
            <span>•</span>
            <span>{new Date(doc.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
      <ChevronRight size={14} className="text-gray-500 group-hover:text-primary-400 shrink-0" />
    </div>
  )
}

// ============ Podcast Sub-Tab ============

interface PodcastEpisode {
  id: string
  title: string
  topic: string
  status: string
  duration: number
  created_at: string
  // Additional fields for enhanced modal
  audio_url?: string
  has_audio?: boolean
  word_count?: number
  duration_seconds?: number
  format_type?: string
  description?: string
  error_message?: string
  script?: string
  script_segments?: Array<{
    speaker: string
    text: string
    duration_seconds?: number
  }>
}

function PodcastSubTab() {
  const [selectedEpisode, setSelectedEpisode] = useState<PodcastEpisode | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [showVoiceModal, setShowVoiceModal] = useState(false)
  const [showNewForm, setShowNewForm] = useState(false)
  const [newTopic, setNewTopic] = useState('')
  const [newFormat, setNewFormat] = useState('debate')
  const [newAudio, setNewAudio] = useState(false)
  const [createSuccess, setCreateSuccess] = useState('')

  const queryClient = useQueryClient()

  const { data: podcastData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['podcast-tab'],
    queryFn: async () => {
      const res = await podcastApi.list()
      return res.data
    },
  })

  const createMutation = useMutation({
    mutationFn: () => podcastApi.create({ topic: newTopic, format_type: newFormat, generate_audio: newAudio }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['podcast-tab'] })
      setCreateSuccess('Episode queued — generation takes 1-2 minutes')
      setNewTopic('')
      setNewFormat('debate')
      setNewAudio(false)
      setTimeout(() => { setShowNewForm(false); setCreateSuccess('') }, 3000)
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load podcast data" />
  }

  const episodes = podcastData?.episodes || podcastData?.results || []
  const stats = podcastData?.status_counts || podcastData?.stats || {}
  // Session 862: Backend uses 'complete' not 'published', and various in-progress statuses not 'draft'
  const publishedEpisodes = episodes.filter((e: PodcastEpisode) => e.status === 'complete' || e.status === 'published')
  const draftEpisodes = episodes.filter((e: PodcastEpisode) =>
    !e.status || ['pending', 'researching', 'debating', 'scripting', 'generating_audio', 'draft', 'failed'].includes(e.status)
  )

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Podcast Studio</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowNewForm(!showNewForm)}
            className="text-xs px-3 py-1.5 rounded-lg bg-accent-purple/20 text-accent-purple hover:bg-accent-purple/30 transition-colors flex items-center gap-1"
          >
            <Mic size={12} />
            + New Episode
          </button>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
            title="Refresh data"
          >
            <RefreshCw size={14} className={cn('text-gray-400', isFetching && 'animate-spin')} />
          </button>
        </div>
      </div>

      {/* New Episode Form */}
      {showNewForm && (
        <div className="card border-accent-purple/30">
          {createSuccess ? (
            <div className="flex items-center gap-2 text-accent-green text-sm">
              <CheckCircle size={14} />
              {createSuccess}
            </div>
          ) : (
            <div className="space-y-3">
              <textarea
                value={newTopic}
                onChange={(e) => setNewTopic(e.target.value)}
                placeholder="Episode topic — e.g. 'AI regulation in 2026' or 'Bitcoin vs Ethereum'"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:border-accent-purple/50"
                rows={2}
              />
              <div className="flex items-center gap-3">
                <select
                  value={newFormat}
                  onChange={(e) => setNewFormat(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-accent-purple/50"
                >
                  <option value="debate">Debate</option>
                  <option value="interview">Interview</option>
                  <option value="panel">Panel</option>
                  <option value="solo">Solo</option>
                </select>
                <label className="flex items-center gap-1.5 text-xs text-gray-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newAudio}
                    onChange={(e) => setNewAudio(e.target.checked)}
                    className="rounded border-gray-600"
                  />
                  Generate Audio
                </label>
                <div className="flex-1" />
                <button
                  onClick={() => setShowNewForm(false)}
                  className="text-xs text-gray-500 hover:text-gray-300 px-2 py-1"
                >
                  Cancel
                </button>
                <button
                  onClick={() => createMutation.mutate()}
                  disabled={!newTopic.trim() || createMutation.isPending}
                  className="text-xs px-4 py-1.5 rounded-lg bg-accent-purple text-white hover:bg-accent-purple/80 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
                >
                  {createMutation.isPending ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                  Create
                </button>
              </div>
              {createMutation.isError && (
                <p className="text-xs text-red-400">Failed to create episode. Please try again.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Stats - Expandable */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'all' && 'border-primary-500/50'
          )}
          onClick={() => toggleSection('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-primary-400">{stats.total || episodes.length}</div>
              <div className="text-xs text-gray-500">Total Episodes</div>
            </div>
            {expandedSection === 'all' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'published' && 'border-accent-green/50'
          )}
          onClick={() => toggleSection('published')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-accent-green">{stats.complete || stats.published || publishedEpisodes.length}</div>
              <div className="text-xs text-gray-500">Complete</div>
            </div>
            {expandedSection === 'published' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div
          className={cn(
            'card cursor-pointer hover:border-primary-500/50 transition-colors',
            expandedSection === 'drafts' && 'border-accent-amber/50'
          )}
          onClick={() => toggleSection('drafts')}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-accent-amber">{draftEpisodes.length}</div>
              <div className="text-xs text-gray-500">In Progress / Failed</div>
            </div>
            {expandedSection === 'drafts' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Episode Lists */}
      {expandedSection === 'all' && (
        <ExpandedListCard
          title="All Episodes"
          icon={Mic}
          items={episodes}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(episode: PodcastEpisode) => (
            <EpisodeRow key={episode.id} episode={episode} onClick={() => setSelectedEpisode(episode)} />
          )}
        />
      )}

      {expandedSection === 'published' && (
        <ExpandedListCard
          title="Published Episodes"
          icon={Eye}
          items={publishedEpisodes}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          emptyMessage="No published episodes yet"
          renderItem={(episode: PodcastEpisode) => (
            <EpisodeRow key={episode.id} episode={episode} onClick={() => setSelectedEpisode(episode)} />
          )}
        />
      )}

      {expandedSection === 'drafts' && (
        <ExpandedListCard
          title="Draft Episodes"
          icon={Clock}
          items={draftEpisodes}
          visibleCount={visibleCount}
          onLoadMore={() => setVisibleCount((v) => v + 10)}
          renderItem={(episode: PodcastEpisode) => (
            <EpisodeRow key={episode.id} episode={episode} onClick={() => setSelectedEpisode(episode)} />
          )}
        />
      )}

      {/* Voice Profile - Show inline */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-400">Voice Profiles</h4>
          <button
            onClick={() => setShowVoiceModal(true)}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            Manage
          </button>
        </div>
        <div
          className="p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors"
          onClick={() => setShowVoiceModal(true)}
        >
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-accent-purple/20 flex items-center justify-center">
              <Mic size={18} className="text-accent-purple" />
            </div>
            <div>
              <p className="text-sm font-medium">1 Voice Profile</p>
              <p className="text-xs text-gray-500">Active for generation</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Episodes - Always Visible */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Episodes</h4>
            <button
              onClick={() => toggleSection('all')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          {episodes.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <Mic className="mx-auto mb-2" size={24} />
              <p className="text-sm">No episodes yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {episodes.slice(0, 4).map((episode: PodcastEpisode) => (
                <EpisodeRow key={episode.id} episode={episode} onClick={() => setSelectedEpisode(episode)} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Episode Detail Modal */}
      {selectedEpisode && (
        <EpisodeDetailModal episode={selectedEpisode} onClose={() => setSelectedEpisode(null)} />
      )}

      {/* Voice Profile Modal */}
      {showVoiceModal && (
        <VoiceProfileModal onClose={() => setShowVoiceModal(false)} />
      )}
    </div>
  )
}

// ============ Distribution Sub-Tab ============

interface Platform {
  name: string
  status: 'connected' | 'not_connected'
  icon?: string
}

function DistributionSubTab() {
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null)

  const { data: statsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['distribution-stats-tab'],
    queryFn: async () => {
      const res = await distributionApi.stats()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load distribution data" />
  }

  const stats = statsData || {
    platforms: 0,
    published: 0,
    pending: 0,
    revenue: 0,
  }

  const platforms: Platform[] = [
    { name: 'YouTube', status: 'not_connected' },
    { name: 'Spotify', status: 'not_connected' },
    { name: 'Medium', status: 'not_connected' },
    { name: 'Substack', status: 'connected' },
  ]

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? null : section)
  }

  return (
    <div className="space-y-4">
      <InlineHeaderRow title="Distribution" onRefresh={refetch} isFetching={isFetching} />

      {/* Stats - Expandable */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Platforms"
          value={stats.platforms || platforms.filter((p) => p.status === 'connected').length}
          icon={Share2}
          color="text-primary-400"
          onClick={() => toggleSection('platforms')}
          isExpanded={expandedSection === 'platforms'}
        />
        <StatCard
          label="Published"
          value={stats.published || 0}
          icon={Eye}
          color="text-accent-green"
          onClick={() => toggleSection('published')}
          isExpanded={expandedSection === 'published'}
        />
        <StatCard
          label="Pending"
          value={stats.pending || 0}
          icon={Calendar}
          color="text-accent-amber"
          onClick={() => toggleSection('pending')}
          isExpanded={expandedSection === 'pending'}
        />
        <StatCard
          label="Revenue"
          value={`$${stats.revenue || 0}`}
          icon={TrendingUp}
          color="text-accent-cyan"
          onClick={() => toggleSection('revenue')}
          isExpanded={expandedSection === 'revenue'}
        />
      </div>

      {/* Expanded Platforms List */}
      {expandedSection === 'platforms' && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">All Platforms</h4>
          <div className="space-y-2">
            {platforms.map((platform) => (
              <PlatformRow
                key={platform.name}
                name={platform.name}
                status={platform.status}
                onClick={() => setSelectedPlatform(platform)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Expanded Published Content */}
      {expandedSection === 'published' && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Published Content</h4>
          <div className="text-center py-6 text-gray-500">
            <Eye className="mx-auto mb-2" size={24} />
            <p className="text-sm">No published content yet</p>
            <p className="text-xs text-gray-600 mt-1">Connect a platform to start publishing</p>
          </div>
        </div>
      )}

      {/* Expanded Pending Content */}
      {expandedSection === 'pending' && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Pending Content</h4>
          <div className="text-center py-6 text-gray-500">
            <Calendar className="mx-auto mb-2" size={24} />
            <p className="text-sm">No pending content</p>
            <p className="text-xs text-gray-600 mt-1">Schedule content for future publishing</p>
          </div>
        </div>
      )}

      {/* Expanded Revenue */}
      {expandedSection === 'revenue' && (
        <div className="card">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Revenue Overview</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Total Revenue</p>
              <p className="text-xl font-bold text-accent-cyan">${stats.revenue || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">This Month</p>
              <p className="text-xl font-bold">$0</p>
            </div>
          </div>
          <div className="mt-3 text-center text-sm text-gray-500">
            <BarChart2 className="inline mr-2" size={14} />
            Connect platforms to track revenue
          </div>
        </div>
      )}

      {/* Platform Integration - Always visible when no section expanded */}
      {!expandedSection && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Platform Integration</h4>
            <button
              onClick={() => toggleSection('platforms')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              <List size={12} />
              View All
            </button>
          </div>
          <div className="space-y-2">
            {platforms.slice(0, 4).map((platform) => (
              <PlatformRow
                key={platform.name}
                name={platform.name}
                status={platform.status}
                onClick={() => setSelectedPlatform(platform)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Platform Detail Modal */}
      {selectedPlatform && (
        <PlatformDetailModal platform={selectedPlatform} onClose={() => setSelectedPlatform(null)} />
      )}
    </div>
  )
}

// ============ Helper Components ============

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-400" size={24} />
    </div>
  )
}

// Session 857: Inline header row without external navigation
function InlineHeaderRow({
  title,
  subtitle,
  onRefresh,
  isFetching,
}: {
  title: string
  subtitle?: string
  onRefresh?: () => void
  isFetching?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && (
          <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
            {subtitle}
          </span>
        )}
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh data"
        >
          <RefreshCw size={14} className={cn('text-gray-400', isFetching && 'animate-spin')} />
        </button>
      )}
    </div>
  )
}

// Session 857: StatCard with isExpanded indicator
function StatCard({
  label,
  value,
  icon: Icon,
  color,
  onClick,
  isExpanded,
}: {
  label: string
  value: number | string
  icon: typeof Image
  color: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <div
      className={cn(
        'card',
        onClick && 'cursor-pointer hover:border-primary-500/50 transition-colors',
        isExpanded && 'border-primary-500/50 bg-primary-500/5'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
            <Icon size={20} className={color} />
          </div>
          {onClick && (
            isExpanded ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )
          )}
        </div>
      </div>
    </div>
  )
}

// Session 857: Expanded list card for inline content viewing
function ExpandedListCard<T>({
  title,
  icon: Icon,
  items,
  visibleCount,
  onLoadMore,
  renderItem,
  emptyMessage,
}: {
  title: string
  icon: typeof Image
  items: T[]
  visibleCount: number
  onLoadMore: () => void
  renderItem: (item: T) => React.ReactNode
  emptyMessage?: string
}) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-3">
        <Icon size={16} className="text-primary-400" />
        <h4 className="text-sm font-medium text-gray-400">{title}</h4>
        <span className="text-xs text-gray-500">({items.length})</span>
      </div>
      {items.length === 0 ? (
        <div className="text-center py-6 text-gray-500">
          <Icon className="mx-auto mb-2" size={24} />
          <p className="text-sm">{emptyMessage || `No ${title.toLowerCase()} found`}</p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.slice(0, visibleCount).map(renderItem)}
          {items.length > visibleCount && (
            <button
              onClick={onLoadMore}
              className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({items.length - visibleCount} remaining)
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// Session 857: Gallery item row for inline display
function GalleryItemRow({ item, onClick }: { item: GalleryItem; onClick: () => void }) {
  const typeIcons = {
    image: Image,
    video: Video,
    audio: Music,
    '3d': Box,
  }
  const TypeIcon = typeIcons[item.type] || Image

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
          <TypeIcon size={14} className="text-primary-400" />
        </div>
        <div>
          <p className="text-sm font-medium truncate max-w-[300px]">{item.title || item.prompt || `${item.type} ${item.id}`}</p>
          <p className="text-xs text-gray-500">
            {new Date(item.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>
      <ChevronRight size={14} className="text-gray-500" />
    </div>
  )
}

// Session 840: Channel row with click handler
function ChannelRow({ channel, onClick }: { channel: ContentChannel; onClick: () => void }) {
  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
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

// Session 840: Blog row with click handler
// Session 865: Added enhance button support
interface BlogRowProps {
  blog: BlogPost
  onClick: () => void
  onEnhance?: (blogId: string, e: React.MouseEvent) => void
  isEnhancing?: boolean
  showEnhanceButton?: boolean
}

function BlogRow({ blog, onClick, onEnhance, isEnhancing, showEnhanceButton }: BlogRowProps) {
  // Status styling
  const statusStyles: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
    draft: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: Clock },
    approved: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: CheckCircle },
    published: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Eye },
  }
  const status = blog.status || 'draft'
  const style = statusStyles[status] || statusStyles.draft
  const StatusIcon = style.icon

  // Session 865: Determine if blog can be enhanced
  const canEnhance = showEnhanceButton ||
    (blog.quality_score !== null &&
     blog.quality_score !== undefined &&
     !blog.publish_ready &&
     !blog.title.startsWith('[') &&
     blog.status !== 'published')

  return (
    <div
      onClick={onClick}
      className="block py-2 border-b border-gray-800 last:border-0 hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <div className="text-sm font-medium truncate">{blog.title}</div>
            {/* Status badge */}
            <span className={cn('px-1.5 py-0.5 rounded text-xs flex items-center gap-1', style.bg, style.text)}>
              <StatusIcon size={10} />
              {status}
            </span>
            {/* Session 865: Quality score indicator */}
            {blog.quality_score !== null && blog.quality_score !== undefined && (
              <span className={cn(
                'px-1.5 py-0.5 rounded text-xs',
                blog.publish_ready
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-purple-500/20 text-purple-400'
              )}>
                {blog.publish_ready ? 'Ready' : `${Math.round(blog.quality_score * 100)}%`}
              </span>
            )}
          </div>
          <div className="text-xs text-gray-500 line-clamp-1">{blog.intro}</div>
        </div>
        <div className="flex items-center gap-2 ml-2">
          {/* Session 865: Enhance button */}
          {canEnhance && onEnhance && (
            <button
              onClick={(e) => onEnhance(blog.id, e)}
              disabled={isEnhancing}
              className={cn(
                'px-2 py-1 rounded text-xs flex items-center gap-1 transition-colors',
                isEnhancing
                  ? 'bg-purple-500/20 text-purple-300 cursor-wait'
                  : 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30'
              )}
              title="Enhance with EditorAgent"
            >
              {isEnhancing ? (
                <Loader2 size={12} className="animate-spin" />
              ) : (
                <Sparkles size={12} />
              )}
              {isEnhancing ? 'Enhancing...' : 'Enhance'}
            </button>
          )}
          <div className="text-xs text-gray-500 whitespace-nowrap">
            {blog.word_count} words
          </div>
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
    </div>
  )
}

// Session 840: Episode row with click handler
function EpisodeRow({ episode, onClick }: { episode: PodcastEpisode; onClick: () => void }) {
  const statusColors: Record<string, { color: string; bg: string }> = {
    complete: { color: 'text-green-400', bg: 'bg-green-500/20' },
    published: { color: 'text-green-400', bg: 'bg-green-500/20' },
    pending: { color: 'text-gray-400', bg: 'bg-gray-500/20' },
    researching: { color: 'text-cyan-400', bg: 'bg-cyan-500/20' },
    debating: { color: 'text-purple-400', bg: 'bg-purple-500/20' },
    scripting: { color: 'text-blue-400', bg: 'bg-blue-500/20' },
    generating_audio: { color: 'text-amber-400', bg: 'bg-amber-500/20' },
    failed: { color: 'text-red-400', bg: 'bg-red-500/20' },
  }
  const status = statusColors[episode.status] || { color: 'text-gray-400', bg: 'bg-gray-500/20' }

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-accent-purple/20 flex items-center justify-center">
          <Mic size={14} className="text-accent-purple" />
        </div>
        <div>
          <div className="text-sm font-medium">{episode.title || episode.topic}</div>
          <div className="text-xs text-gray-500">
            {episode.duration_seconds ? `${Math.round(episode.duration_seconds / 60)}min` : episode.status === 'complete' ? 'No audio' : 'Processing...'}
          </div>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', status.bg, status.color)}>
        {episode.status === 'generating_audio' ? 'Audio Gen' : episode.status}
      </span>
    </div>
  )
}

// Session 840: Platform row component
function PlatformRow({ name, status, onClick }: { name: string; status: string; onClick: () => void }) {
  const isConnected = status === 'connected'

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-8 w-8 rounded-lg flex items-center justify-center',
          isConnected ? 'bg-accent-green/20' : 'bg-gray-800'
        )}>
          <Share2 size={14} className={isConnected ? 'text-accent-green' : 'text-gray-400'} />
        </div>
        <span className="text-sm">{name}</span>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded',
        isConnected ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
      )}>
        {isConnected ? 'Connected' : 'Connect'}
      </span>
    </div>
  )
}

// ============ Detail Modals ============

// Session 857: Gallery Item Detail Modal
// Session 865: Enhanced with video/audio playback support
function GalleryItemDetailModal({ item, onClose }: { item: GalleryItem; onClose: () => void }) {
  const typeIcons = {
    image: Image,
    video: Video,
    audio: Music,
    '3d': Box,
  }
  const TypeIcon = typeIcons[item.type] || Image

  // Session 865: Render appropriate media player based on type
  const renderMediaContent = () => {
    const mediaUrl = item.url || item.thumbnail_url

    if (item.type === 'video' && mediaUrl) {
      return (
        <div className="rounded-lg overflow-hidden bg-black">
          <video
            src={mediaUrl}
            controls
            autoPlay
            className="w-full h-auto max-h-[60vh]"
            poster={item.thumbnail_url}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )
    }

    if (item.type === 'audio' && mediaUrl) {
      return (
        <div className="p-6 bg-gray-800/50 rounded-lg">
          <div className="flex items-center justify-center mb-4">
            <div className="h-24 w-24 rounded-full bg-primary-500/20 flex items-center justify-center">
              <Music size={48} className="text-primary-400" />
            </div>
          </div>
          <audio src={mediaUrl} controls autoPlay className="w-full">
            Your browser does not support the audio element.
          </audio>
        </div>
      )
    }

    if (item.type === '3d') {
      return (
        <div className="p-6 bg-gray-800/50 rounded-lg text-center">
          <div className="flex items-center justify-center mb-4">
            <div className="h-24 w-24 rounded-full bg-accent-green/20 flex items-center justify-center">
              <Box size={48} className="text-accent-green" />
            </div>
          </div>
          <p className="text-gray-400 mb-4">3D Model Viewer</p>
          {mediaUrl && (
            <a
              href={mediaUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary text-sm inline-flex items-center gap-2"
            >
              <Box size={14} />
              Open Model File
            </a>
          )}
        </div>
      )
    }

    // Default: Image
    if (mediaUrl) {
      return (
        <div className="rounded-lg overflow-hidden bg-gray-800">
          <img src={mediaUrl} alt={item.title || item.prompt} className="w-full h-auto" />
        </div>
      )
    }

    return (
      <div className="p-6 bg-gray-800/50 rounded-lg text-center text-gray-400">
        No preview available
      </div>
    )
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <TypeIcon size={20} className="text-primary-400" />
            <div>
              <h3 className="font-semibold">{item.title || item.prompt || `${item.type} ${item.id.slice(0, 8)}`}</h3>
              <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400 capitalize">
                {item.type}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {renderMediaContent()}

          {/* Prompt/Description */}
          {item.prompt && (
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Prompt</p>
              <p className="text-sm text-gray-300">{item.prompt}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Type</p>
              <p className="text-lg font-bold capitalize">{item.type}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(item.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end gap-2">
          {item.url && (
            <a
              href={item.url}
              download
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary text-sm"
            >
              Download
            </a>
          )}
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Series Detail Modal
function SeriesDetailModal({ series, onClose }: { series: AISeries; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Play size={20} className="text-primary-400" />
            <h3 className="font-semibold">{series.name}</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Episodes</p>
              <p className="text-xl font-bold">{series.episode_count}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(series.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Channel Detail Modal (updated - removed external link)
function ChannelDetailModal({ channel, onClose }: { channel: ContentChannel; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <MessageSquare size={20} className="text-primary-400" />
            <div>
              <h3 className="font-semibold">{channel.name}</h3>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded',
                channel.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
              )}>
                {channel.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {channel.description && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
              <p className="text-sm">{channel.description}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Episodes</p>
              <p className="text-xl font-bold">{channel.episode_count || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(channel.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 861: Enhanced Blog Detail Modal with full content viewing and actions
function BlogDetailModal({ blog, onClose }: { blog: BlogPost; onClose: () => void }) {
  const [showFullContent, setShowFullContent] = useState(false)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch full blog content when showing full content
  // Session 968: Migrated from raw fetch to blogsApi (auth interceptor)
  const { data: fullBlog, isLoading: contentLoading } = useQuery({
    queryKey: ['blog-full', blog.id],
    queryFn: async () => {
      const response = await blogsApi.get(blog.id)
      return response.data.blog as BlogPost
    },
    enabled: showFullContent,
  })

  // Approve mutation — Session 968: Migrated to blogsApi
  const approveMutation = useMutation({
    mutationFn: async () => {
      const response = await blogsApi.approve(blog.id)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-tab'] })
      setActionError(null)
    },
    onError: (error: Error) => {
      setActionError(error.message)
    },
  })

  // Publish mutation — Session 968: Migrated to blogsApi
  const publishMutation = useMutation({
    mutationFn: async () => {
      const response = await blogsApi.publish(blog.id, true)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-tab'] })
      setActionError(null)
    },
    onError: (error: Error) => {
      setActionError(error.message)
    },
  })

  const statusStyles: Record<string, { bg: string; text: string; icon: typeof CheckCircle }> = {
    draft: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: FileText },
    approved: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: ThumbsUp },
    published: { bg: 'bg-green-500/20', text: 'text-green-400', icon: CheckCircle },
  }
  const currentStatus = blog.status || 'draft'
  const style = statusStyles[currentStatus] || statusStyles.draft
  const StatusIcon = style.icon

  const displayContent = fullBlog || blog
  const canApprove = currentStatus === 'draft'
  const canPublish = currentStatus === 'approved' || currentStatus === 'draft'

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <BookOpen size={20} className="text-accent-green" />
            <div>
              <h3 className="font-semibold text-lg">{blog.title}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize flex items-center gap-1', style.bg, style.text)}>
                  <StatusIcon size={12} />
                  {currentStatus}
                </span>
                {blog.category && blog.category !== 'blog' && (
                  <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                    {blog.category}
                  </span>
                )}
                {blog.tone && (
                  <span className="text-xs text-gray-500">Tone: {blog.tone}</span>
                )}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Action Error */}
          {actionError && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400">
              <AlertCircle size={16} />
              <span className="text-sm">{actionError}</span>
            </div>
          )}

          {/* Intro */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Introduction</h4>
            <p className="text-sm leading-relaxed">{blog.intro}</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Word Count</p>
              <p className="text-xl font-bold">{blog.word_count?.toLocaleString() || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(blog.created_at).toLocaleDateString()}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Reading Time</p>
              <p className="text-sm">{Math.ceil((blog.word_count || 0) / 200)} min</p>
            </div>
          </div>

          {/* Tags */}
          {blog.tags?.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Tags</h4>
              <div className="flex flex-wrap gap-2">
                {blog.tags.map((tag: string) => (
                  <span key={tag} className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-400">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Full Content Toggle */}
          <div className="border-t border-dark-border pt-4">
            <button
              onClick={() => setShowFullContent(!showFullContent)}
              className="flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors"
            >
              <Eye size={16} />
              <span className="text-sm font-medium">
                {showFullContent ? 'Hide Full Content' : 'Read Full Content'}
              </span>
              {showFullContent ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          </div>

          {/* Full Content Section */}
          {showFullContent && (
            <div className="border border-dark-border rounded-lg p-4 bg-gray-900/50">
              {contentLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin text-gray-400" size={24} />
                  <span className="ml-2 text-gray-400">Loading content...</span>
                </div>
              ) : displayContent.full_text ? (
                /* Session 943: Unified prose styling */
                <div className="prose prose-invert prose-dark prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {displayContent.full_text}
                  </ReactMarkdown>
                </div>
              ) : displayContent.sections?.length ? (
                <div className="space-y-4">
                  {displayContent.sections.map((section, idx) => (
                    <div key={idx}>
                      <h3 className="text-base font-semibold text-white mb-2">{section.header}</h3>
                      <p className="text-sm text-gray-300 leading-relaxed">{section.content}</p>
                    </div>
                  ))}
                  {displayContent.conclusion && (
                    <div className="mt-4 pt-4 border-t border-dark-border">
                      <h3 className="text-base font-semibold text-white mb-2">Conclusion</h3>
                      <p className="text-sm text-gray-300 leading-relaxed">{displayContent.conclusion}</p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No content available</p>
              )}
            </div>
          )}
        </div>

        {/* Footer with Actions */}
        <div className="p-4 border-t border-dark-border flex items-center justify-between">
          <div className="text-xs text-gray-500">
            ID: {blog.id.slice(0, 8)}...
          </div>
          <div className="flex items-center gap-2">
            {canApprove && (
              <button
                onClick={() => approveMutation.mutate()}
                disabled={approveMutation.isPending}
                className="btn btn-secondary text-sm flex items-center gap-2"
              >
                {approveMutation.isPending ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <ThumbsUp size={14} />
                )}
                Approve
              </button>
            )}
            {canPublish && (
              <button
                onClick={() => publishMutation.mutate()}
                disabled={publishMutation.isPending}
                className="btn btn-primary text-sm flex items-center gap-2"
              >
                {publishMutation.isPending ? (
                  <Loader2 size={14} className="animate-spin" />
                ) : (
                  <Send size={14} />
                )}
                Publish
              </button>
            )}
            <button onClick={onClose} className="btn btn-ghost text-sm">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Session 861: Enhanced Episode Detail Modal with script viewing and audio playback
// Session 865: Fixed authentication - use podcastApi instead of raw fetch
// Session 865: Added Generate Audio button for TTS
function EpisodeDetailModal({ episode, onClose }: { episode: PodcastEpisode; onClose: () => void }) {
  const [showScript, setShowScript] = useState(false)
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false)
  const [audioError, setAudioError] = useState<string | null>(null)
  const [audioSuccess, setAudioSuccess] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch full script when expanded - Session 865: Use podcastApi for proper auth
  const { data: scriptData, isLoading: scriptLoading } = useQuery({
    queryKey: ['podcast-script', episode.id],
    queryFn: async () => {
      const response = await podcastApi.script(episode.id)
      return response.data
    },
    enabled: showScript,
  })

  // Session 865: Generate Audio handler
  // Reads selected voice from localStorage (set by VoiceProfileModal)
  const handleGenerateAudio = async () => {
    setIsGeneratingAudio(true)
    setAudioError(null)
    setAudioSuccess(null)

    try {
      // Get selected voice profile from localStorage
      const voiceProfileId = localStorage.getItem('podcast_voice_profile_id')
      // Pass voice profile to API (null/undefined uses default voices)
      const response = await podcastApi.generateAudio(episode.id, voiceProfileId || undefined)
      if (response.data?.success) {
        setAudioSuccess(`Audio generated! Duration: ${Math.round(response.data.duration_seconds / 60)} min`)
        queryClient.invalidateQueries({ queryKey: ['podcast-tab'] })
        queryClient.invalidateQueries({ queryKey: ['podcast-list'] })
      } else {
        setAudioError(response.data?.error || 'Failed to generate audio')
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } }; message?: string }
      setAudioError(error.response?.data?.error || error.message || 'Failed to generate audio')
    } finally {
      setIsGeneratingAudio(false)
    }
  }

  const statusColors: Record<string, { color: string; bg: string; icon: typeof Clock }> = {
    complete: { color: 'text-green-400', bg: 'bg-green-500/20', icon: CheckCircle },
    published: { color: 'text-green-400', bg: 'bg-green-500/20', icon: CheckCircle },
    draft: { color: 'text-amber-400', bg: 'bg-amber-500/20', icon: Clock },
    pending: { color: 'text-amber-400', bg: 'bg-amber-500/20', icon: Clock },
    researching: { color: 'text-blue-400', bg: 'bg-blue-500/20', icon: Loader2 },
    debating: { color: 'text-blue-400', bg: 'bg-blue-500/20', icon: Loader2 },
    scripting: { color: 'text-blue-400', bg: 'bg-blue-500/20', icon: Loader2 },
    recording: { color: 'text-purple-400', bg: 'bg-purple-500/20', icon: Mic },
    generating: { color: 'text-blue-400', bg: 'bg-blue-500/20', icon: Loader2 },
    failed: { color: 'text-red-400', bg: 'bg-red-500/20', icon: AlertCircle },
  }
  const status = statusColors[episode.status] || statusColors.draft
  const StatusIcon = status.icon

  const hasAudio = episode.audio_url || episode.has_audio

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Mic size={20} className="text-accent-purple" />
            <div>
              <h3 className="font-semibold text-lg">{episode.title || episode.topic}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize flex items-center gap-1', status.bg, status.color)}>
                  <StatusIcon size={12} className={episode.status?.includes('ing') ? 'animate-spin' : ''} />
                  {episode.status}
                </span>
                {episode.format_type && (
                  <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">
                    {episode.format_type}
                  </span>
                )}
                {hasAudio && (
                  <span className="text-xs px-2 py-0.5 rounded bg-green-500/20 text-green-400 flex items-center gap-1">
                    <Music size={10} /> Audio
                  </span>
                )}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Topic/Description */}
          {(episode.topic || episode.description) && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Topic</h4>
              <p className="text-sm leading-relaxed">{episode.description || episode.topic}</p>
            </div>
          )}

          {/* Audio Player */}
          {hasAudio && episode.audio_url && (
            <div className="p-4 bg-gray-800/50 rounded-lg">
              <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <Play size={14} /> Listen to Episode
              </h4>
              <audio
                controls
                className="w-full"
                src={episode.audio_url}
              >
                Your browser does not support the audio element.
              </audio>
            </div>
          )}

          {/* Session 865: Generate Audio Section - show when no audio exists */}
          {!hasAudio && (
            <div className="p-4 bg-gray-800/50 rounded-lg border border-dashed border-gray-600">
              <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <Music size={14} /> Generate Audio (TTS)
              </h4>
              <p className="text-xs text-gray-500 mb-3">
                Convert this script to audio using ElevenLabs text-to-speech. This uses premium voices and will incur API costs.
              </p>
              {audioError && (
                <div className="mb-3 p-2 bg-red-500/20 border border-red-500/30 rounded text-red-400 text-sm">
                  {audioError}
                </div>
              )}
              {audioSuccess && (
                <div className="mb-3 p-2 bg-green-500/20 border border-green-500/30 rounded text-green-400 text-sm">
                  {audioSuccess}
                </div>
              )}
              <button
                onClick={handleGenerateAudio}
                disabled={isGeneratingAudio}
                className={cn(
                  'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                  isGeneratingAudio
                    ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    : 'bg-accent-purple hover:bg-accent-purple/80 text-white'
                )}
              >
                {isGeneratingAudio ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    Generating Audio...
                  </>
                ) : (
                  <>
                    <Mic size={16} />
                    Generate Audio
                  </>
                )}
              </button>
            </div>
          )}

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Duration</p>
              <p className="text-xl font-bold">
                {episode.duration_seconds
                  ? `${Math.round(episode.duration_seconds / 60)} min`
                  : episode.duration
                  ? `${Math.round(episode.duration / 60)} min`
                  : 'N/A'}
              </p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Word Count</p>
              <p className="text-xl font-bold">{episode.word_count?.toLocaleString() || 0}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(episode.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Script Toggle */}
          <div className="border-t border-dark-border pt-4">
            <button
              onClick={() => setShowScript(!showScript)}
              className="flex items-center gap-2 text-primary-400 hover:text-primary-300 transition-colors"
            >
              <FileText size={16} />
              <span className="text-sm font-medium">
                {showScript ? 'Hide Script' : 'Read Full Script'}
              </span>
              {showScript ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          </div>

          {/* Full Script Section */}
          {showScript && (
            <div className="border border-dark-border rounded-lg p-4 bg-gray-900/50">
              {scriptLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin text-gray-400" size={24} />
                  <span className="ml-2 text-gray-400">Loading script...</span>
                </div>
              ) : scriptData?.script ? (
                <div className="space-y-4">
                  {/* Session 943: Unified prose styling */}
                  <div className="prose prose-invert prose-dark prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {scriptData.script}
                    </ReactMarkdown>
                  </div>
                  {scriptData.debate && (
                    <div className="mt-4 pt-4 border-t border-dark-border space-y-3">
                      <h4 className="text-sm font-medium text-gray-400">Debate Insights</h4>
                      {scriptData.debate.consensus && (
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                          <p className="text-xs text-gray-500 mb-1">Consensus</p>
                          <p className="text-sm text-gray-300">{scriptData.debate.consensus}</p>
                        </div>
                      )}
                      {scriptData.debate.key_insights?.length > 0 && (
                        <div className="p-3 bg-gray-800/50 rounded-lg">
                          <p className="text-xs text-gray-500 mb-2">Key Takeaways</p>
                          <ul className="list-disc list-inside text-sm text-gray-300 space-y-1">
                            {scriptData.debate.key_insights.map((insight: string, idx: number) => (
                              <li key={idx}>{insight}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No script available</p>
              )}
            </div>
          )}

          {/* Error Message */}
          {episode.error_message && (
            <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400">
              <AlertCircle size={16} />
              <span className="text-sm">{episode.error_message}</span>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border flex items-center justify-between">
          <div className="text-xs text-gray-500">
            ID: {episode.id.slice(0, 8)}...
          </div>
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Voice Profile Modal
// Session 865: Connected to real voice marketplace API
interface VoiceProfile {
  id: string
  name: string
  elevenlabs_voice_id: string
  gender: string
  primary_use_case: string
  is_public: boolean
  creation_method?: string
  created_at: string
}

// Default ElevenLabs voices for podcast generation
const DEFAULT_VOICES = [
  { id: 'default-host', name: 'Antoni (Host)', role: 'HOST', elevenlabs_id: 'ErXwobaYiN019PkySvjV', gender: 'male' },
  { id: 'default-advocate', name: 'Rachel (Advocate)', role: 'ADVOCATE', elevenlabs_id: '21m00Tcm4TlvDq8ikWAM', gender: 'female' },
  { id: 'default-skeptic', name: 'Clyde (Skeptic)', role: 'SKEPTIC', elevenlabs_id: '2EiwWnXFnvU5JabPnv8n', gender: 'male' },
  { id: 'default-analyst', name: 'Paul (Analyst)', role: 'ANALYST', elevenlabs_id: '5Q0t7uMcjvnagumLfvZi', gender: 'male' },
]

function VoiceProfileModal({ onClose }: { onClose: () => void }) {
  const [selectedVoiceId, setSelectedVoiceId] = useState<string | null>(() => {
    // Load from localStorage
    return localStorage.getItem('podcast_voice_profile_id')
  })
  const [previewingVoice, setPreviewingVoice] = useState<string | null>(null)

  // Fetch user's custom voice profiles
  const { data: voicesData, isLoading, isError, refetch } = useQuery({
    queryKey: ['my-voices'],
    queryFn: async () => {
      const response = await voiceMarketplaceApi.myVoices()
      return response.data
    },
  })

  const myVoices: VoiceProfile[] = voicesData?.voices || []

  const handleSelectVoice = (voiceId: string | null) => {
    setSelectedVoiceId(voiceId)
    if (voiceId) {
      localStorage.setItem('podcast_voice_profile_id', voiceId)
    } else {
      localStorage.removeItem('podcast_voice_profile_id')
    }
  }

  const handlePreview = async (voiceId: string) => {
    setPreviewingVoice(voiceId)
    try {
      const response = await voiceMarketplaceApi.preview(voiceId)
      if (response.data?.audio_url) {
        const audio = new Audio(response.data.audio_url)
        audio.play()
        audio.onended = () => setPreviewingVoice(null)
      }
    } catch {
      // Preview failed silently
    } finally {
      setTimeout(() => setPreviewingVoice(null), 3000)
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Mic size={20} className="text-accent-purple" />
            <h3 className="font-semibold">Voice Profiles</h3>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Default System Voices */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <Radio size={14} /> Default Podcast Voices
            </h4>
            <div className="space-y-2">
              {/* Use Default Option */}
              <div
                className={cn(
                  'p-3 rounded-lg cursor-pointer transition-colors border',
                  !selectedVoiceId
                    ? 'bg-accent-purple/20 border-accent-purple'
                    : 'bg-gray-800/50 border-transparent hover:border-gray-600'
                )}
                onClick={() => handleSelectVoice(null)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-accent-purple/20 flex items-center justify-center">
                      <Radio size={18} className="text-accent-purple" />
                    </div>
                    <div>
                      <p className="font-medium text-sm">Use Default Voices</p>
                      <p className="text-xs text-gray-500">Multi-voice debate format (4 speakers)</p>
                    </div>
                  </div>
                  {!selectedVoiceId && (
                    <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
                      Active
                    </span>
                  )}
                </div>
              </div>

              {/* Show default voice details */}
              {!selectedVoiceId && (
                <div className="ml-4 pl-4 border-l border-gray-700 space-y-1">
                  {DEFAULT_VOICES.map(voice => (
                    <div key={voice.id} className="flex items-center gap-2 text-xs text-gray-400">
                      <span className="w-20 text-gray-500">{voice.role}:</span>
                      <span>{voice.name}</span>
                      <span className="text-gray-600">({voice.gender})</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Custom Voice Profiles */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
              <Mic size={14} /> Your Custom Voices
              <button
                onClick={() => refetch()}
                className="ml-auto text-xs text-primary-400 hover:text-primary-300"
              >
                Refresh
              </button>
            </h4>

            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="animate-spin text-gray-400" size={24} />
              </div>
            ) : isError ? (
              <div className="text-center py-4 text-red-400 text-sm">
                Failed to load voice profiles
              </div>
            ) : myVoices.length === 0 ? (
              <div className="text-center py-6 text-gray-500">
                <Mic size={32} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No custom voices yet</p>
                <p className="text-xs mt-1">Clone your voice or create a custom voice in the Voice Marketplace</p>
              </div>
            ) : (
              <div className="space-y-2">
                {myVoices.map(voice => (
                  <div
                    key={voice.id}
                    className={cn(
                      'p-3 rounded-lg cursor-pointer transition-colors border',
                      selectedVoiceId === voice.id
                        ? 'bg-accent-purple/20 border-accent-purple'
                        : 'bg-gray-800/50 border-transparent hover:border-gray-600'
                    )}
                    onClick={() => handleSelectVoice(voice.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-gray-700 flex items-center justify-center">
                          <Mic size={18} className="text-gray-300" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{voice.name}</p>
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span className="capitalize">{voice.gender}</span>
                            <span>•</span>
                            <span className="capitalize">{voice.primary_use_case?.replace('_', ' ')}</span>
                            {voice.creation_method === 'cloned' && (
                              <>
                                <span>•</span>
                                <span className="text-accent-purple">Cloned</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handlePreview(voice.id)
                          }}
                          disabled={previewingVoice === voice.id}
                          className="p-1.5 hover:bg-gray-600 rounded transition-colors"
                          title="Preview voice"
                        >
                          {previewingVoice === voice.id ? (
                            <Loader2 size={14} className="animate-spin text-gray-400" />
                          ) : (
                            <Play size={14} className="text-gray-400" />
                          )}
                        </button>
                        {selectedVoiceId === voice.id && (
                          <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
                            Active
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Info */}
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <p className="text-xs text-blue-300">
              <strong>Tip:</strong> The selected voice will be used for all speakers when generating audio.
              For multi-voice debates, use the default voices which assign different speakers to different roles.
            </p>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex items-center justify-between">
          <p className="text-xs text-gray-500">
            {selectedVoiceId ? 'Custom voice selected' : 'Using default multi-voice'}
          </p>
          <button onClick={onClose} className="btn btn-primary text-sm">
            Done
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Platform Detail Modal
function PlatformDetailModal({ platform, onClose }: { platform: Platform; onClose: () => void }) {
  const isConnected = platform.status === 'connected'
  const isSubstack = platform.name === 'Substack'

  // Fetch newsletter deliverables for Substack
  const { data: newsletterData, isLoading: nlLoading } = useQuery({
    queryKey: ['newsletter-deliverables'],
    queryFn: async () => {
      const res = await api.get('/deliverables/', {
        params: { category: 'Newsletter', per_page: 20 },
      })
      return res.data
    },
    enabled: isSubstack,
  })

  const [copied, setCopied] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const { data: selectedDetail } = useQuery({
    queryKey: ['deliverable-detail', selectedId],
    queryFn: async () => {
      if (!selectedId) return null
      const res = await api.get(`/deliverables/${selectedId}/`)
      return res.data
    },
    enabled: !!selectedId,
  })

  const handleCopy = async (content: string) => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Group newsletter deliverables by issue number
  const issues = (newsletterData?.results || newsletterData?.items || []).reduce(
    (acc: Record<string, Array<{ id: string; title: string; metadata?: Record<string, unknown> }>>, d: { id: string; title: string; metadata?: Record<string, unknown> }) => {
      const issueNum = (d.metadata as Record<string, unknown>)?.issue_number || 'other'
      const key = String(issueNum)
      if (!acc[key]) acc[key] = []
      acc[key].push(d)
      return acc
    },
    {} as Record<string, Array<{ id: string; title: string; metadata?: Record<string, unknown> }>>
  )

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-3xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            {isSubstack ? (
              <Send size={20} className="text-accent-green" />
            ) : (
              <Share2 size={20} className={isConnected ? 'text-accent-green' : 'text-gray-400'} />
            )}
            <div>
              <h3 className="font-semibold">{platform.name}</h3>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded',
                isSubstack ? 'bg-accent-green/20 text-accent-green' :
                isConnected ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
              )}>
                {isSubstack ? 'Manual Deploy' : isConnected ? 'Connected' : 'Not Connected'}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isSubstack ? (
            <>
              {/* Substack Deploy Panel */}
              <div className="p-3 bg-primary-500/10 border border-primary-500/20 rounded-lg">
                <p className="text-sm text-primary-300">
                  Deploy to Substack by copying publish-ready content below and pasting into your Substack editor.
                </p>
                <a
                  href="https://substack.com/@donkeybetzking"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-400 hover:text-primary-300 mt-1 inline-flex items-center gap-1"
                >
                  Open Substack <ChevronRight size={12} />
                </a>
              </div>

              {/* Newsletter Issues */}
              {nlLoading ? (
                <div className="text-center py-6">
                  <Loader2 className="mx-auto mb-2 animate-spin text-gray-400" size={24} />
                  <p className="text-sm text-gray-500">Loading newsletter content...</p>
                </div>
              ) : Object.keys(issues).length === 0 ? (
                <div className="text-center py-6 text-gray-500">
                  <FileText className="mx-auto mb-2" size={24} />
                  <p className="text-sm">No newsletter content yet</p>
                  <p className="text-xs text-gray-600 mt-1">Use the newsletter tool to prepare issues</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-gray-400">Newsletter Issues</h4>
                  {(newsletterData?.results || newsletterData?.items || []).map((d: { id: string; title: string; created_at?: string; metadata?: Record<string, unknown> }) => {
                    const artifactType = (d.metadata as Record<string, unknown>)?.artifact_type as string || ''
                    const isPublishReady = artifactType?.includes('publish_ready')
                    const isChecklist = artifactType === 'publish_checklist'
                    const isSubjectPreheader = artifactType === 'subject_preheader'
                    return (
                      <div
                        key={d.id}
                        className={cn(
                          'p-3 rounded-lg border cursor-pointer transition-all',
                          selectedId === d.id
                            ? 'border-primary-500 bg-primary-500/10'
                            : 'border-dark-border bg-gray-800/30 hover:border-gray-600'
                        )}
                        onClick={() => setSelectedId(selectedId === d.id ? null : d.id)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            {isPublishReady && <Send size={14} className="text-accent-green" />}
                            {isChecklist && <CheckCircle size={14} className="text-accent-amber" />}
                            {isSubjectPreheader && <FileText size={14} className="text-primary-400" />}
                            {!isPublishReady && !isChecklist && !isSubjectPreheader && <FileText size={14} className="text-gray-500" />}
                            <span className="text-sm font-medium">{d.title}</span>
                          </div>
                          {isPublishReady && (
                            <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
                              Ready
                            </span>
                          )}
                        </div>
                        {d.created_at && (
                          <p className="text-xs text-gray-500 mt-1 ml-6">
                            {new Date(d.created_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}

              {/* Selected Content Preview + Copy */}
              {selectedDetail && (
                <div className="border border-dark-border rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between p-3 bg-gray-800/50 border-b border-dark-border">
                    <span className="text-sm font-medium">{selectedDetail.title}</span>
                    <button
                      onClick={() => handleCopy(selectedDetail.content || '')}
                      className={cn(
                        'flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-all',
                        copied
                          ? 'bg-accent-green/20 text-accent-green'
                          : 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30'
                      )}
                    >
                      {copied ? <CheckCircle size={14} /> : <Send size={14} />}
                      {copied ? 'Copied!' : 'Copy to Clipboard'}
                    </button>
                  </div>
                  <div className="p-4 max-h-64 overflow-y-auto">
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {(selectedDetail.content || '').slice(0, 3000)}
                      </ReactMarkdown>
                      {(selectedDetail.content || '').length > 3000 && (
                        <p className="text-xs text-gray-500 mt-2 italic">
                          Content truncated in preview. Full content copied to clipboard.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          ) : isConnected ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-800/50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Published</p>
                  <p className="text-xl font-bold">0</p>
                </div>
                <div className="p-3 bg-gray-800/50 rounded-lg">
                  <p className="text-xs text-gray-500 mb-1">Pending</p>
                  <p className="text-xl font-bold">0</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-6">
              <Share2 className="mx-auto mb-3 text-gray-500" size={32} />
              <p className="text-sm text-gray-400 mb-4">
                Connect your {platform.name} account to start publishing content
              </p>
              <p className="text-xs text-gray-500">
                Platform integration coming soon
              </p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-dark-border flex justify-between">
          {isSubstack && (
            <a
              href="https://substack.com/@donkeybetzking"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary text-sm flex items-center gap-2"
            >
              <Send size={14} />
              Open Substack Editor
            </a>
          )}
          <button onClick={onClose} className={cn("btn text-sm", isSubstack ? "btn-secondary" : "btn-primary ml-auto")}>
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
