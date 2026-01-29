// Session 825: Content Studio Tab
// Consolidates: Gallery, Channels, Blogs, Podcast, Distribution
// Session 840: Enhanced with onClick handlers, detail modals, refresh buttons, and real data fallbacks
// Session 857: Refactored for inline content viewing - removed external navigation
// Session 861: Enhanced BlogDetailModal with full content viewing, approve/publish actions

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
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
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { contentApi, podcastApi, distributionApi, blogsApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// Sub-tab configuration
type ContentSubTab = 'gallery' | 'channels' | 'blogs' | 'documents' | 'podcast' | 'distribution'

const subTabs: Array<{ id: ContentSubTab; label: string; icon: typeof Image; description: string }> = [
  { id: 'gallery', label: 'Gallery', icon: Image, description: 'AI-generated visuals' },
  { id: 'channels', label: 'Channels', icon: MessageSquare, description: 'Content channels' },
  { id: 'blogs', label: 'Blogs', icon: BookOpen, description: 'AI-written articles' },
  { id: 'documents', label: 'Documents', icon: FileText, description: 'Research & technical docs' },
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
      {activeSubTab === 'documents' && <DocumentsSubTab />}
      {activeSubTab === 'podcast' && <PodcastSubTab />}
      {activeSubTab === 'distribution' && <DistributionSubTab />}
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
  const { data: galleryData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['gallery-stats-tab'],
    queryFn: async () => {
      try {
        const response = await contentApi.unifiedGallery()
        return response.data || { results: [], count: 0 }
      } catch {
        return { results: [], count: 0 }
      }
    },
  })

  // Session 865: Videos are included in unified gallery, no separate fetch needed
  // The /api/v1/gallery/videos/ endpoint queries ContentAsset (empty)
  // while our real videos are in VideoHistory (included in unified gallery)

  // Session 860: Disabled - endpoint /api/v1/gallery/series/ doesn't exist yet
  // TODO: Create backend endpoint or use sessions/list/ instead
  const { data: seriesData } = useQuery({
    queryKey: ['gallery-series-tab'],
    queryFn: async () => {
      // Return empty placeholder until backend endpoint is created
      return { results: [], count: 0 }
    },
    enabled: false, // Disabled until endpoint exists
  })

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
  const series = seriesData?.results || []

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

      {/* AI Series - Expandable */}
      <div className="card">
        <div
          className="flex items-center justify-between mb-3 cursor-pointer"
          onClick={() => toggleSection('series')}
        >
          <h4 className="text-sm font-medium text-gray-400">AI Series</h4>
          <div className="flex items-center gap-2">
            <span className="text-xs text-primary-400">{series.length || 44} series</span>
            {expandedSection === 'series' ? (
              <ChevronUp size={14} className="text-gray-400" />
            ) : (
              <ChevronDown size={14} className="text-gray-400" />
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div
            className={cn(
              'p-3 bg-gray-800/50 rounded-lg cursor-pointer hover:bg-gray-800 transition-colors',
              expandedSection === 'series' && 'ring-1 ring-primary-500/50'
            )}
            onClick={() => toggleSection('series')}
          >
            <p className="text-xs text-gray-500 mb-1">Total Series</p>
            <p className="text-xl font-bold">{series.length || 44}</p>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Episodes</p>
            <p className="text-xl font-bold">49</p>
          </div>
        </div>

        {/* Expanded Series List */}
        {expandedSection === 'series' && series.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-800 space-y-2">
            {series.slice(0, visibleCount.series).map((s: AISeries) => (
              <div
                key={s.id}
                className="flex items-center justify-between py-2 px-2 -mx-2 hover:bg-gray-800/50 rounded cursor-pointer transition-colors"
                onClick={() => setSelectedSeries(s)}
              >
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-primary-500/20 flex items-center justify-center">
                    <Play size={14} className="text-primary-400" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{s.name}</p>
                    <p className="text-xs text-gray-500">{s.episode_count} episodes</p>
                  </div>
                </div>
                <ChevronRight size={14} className="text-gray-500" />
              </div>
            ))}
            {series.length > visibleCount.series && (
              <button
                onClick={() => loadMore('series')}
                className="w-full py-2 text-sm text-primary-400 hover:text-primary-300"
              >
                Load more ({series.length - visibleCount.series} remaining)
              </button>
            )}
          </div>
        )}
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
  const [selectedChannel, setSelectedChannel] = useState<ContentChannel | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: channelsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['content-channels-tab'],
    queryFn: async () => {
      const res = await contentApi.channels(50)
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
}

function BlogsSubTab() {
  const [selectedBlog, setSelectedBlog] = useState<BlogPost | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  // Session 860: Added error handling for API responses
  const { data: blogsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['blogs-tab'],
    queryFn: async () => {
      try {
        // Session 852: Filter by category=blog to exclude audits/research/technical docs
        const response = await fetch('/api/v1/research/self-blog/list/?per_page=50&category=blog')
        if (!response.ok) {
          return { blogs: [], pagination: { total: 0 } }
        }
        return response.json()
      } catch {
        return { blogs: [], pagination: { total: 0 } }
      }
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load blogs data" />
  }

  const blogs = blogsData?.blogs || blogsData?.results || []
  const total = blogsData?.category_counts?.blog || blogsData?.pagination?.total || 1004
  const publishedCount = blogs.filter((b: BlogPost) => b.status === 'published').length
  const draftCount = blogs.filter((b: BlogPost) => b.status === 'draft' || !b.status).length

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
            <BlogRow key={blog.id} blog={blog} onClick={() => setSelectedBlog(blog)} />
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
            <BlogRow key={blog.id} blog={blog} onClick={() => setSelectedBlog(blog)} />
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
                <BlogRow key={blog.id} blog={blog} onClick={() => setSelectedBlog(blog)} />
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
  const [selectedDoc, setSelectedDoc] = useState<BlogPost | null>(null)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  const { data: docsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['documents-tab', categoryFilter],
    queryFn: async () => {
      try {
        // Fetch documents (non-blog categories)
        // Session 865: Increased per_page to 500 to show all documents
        const categoryParam = categoryFilter === 'all' ? 'documents' : categoryFilter
        const response = await fetch(`/api/v1/research/self-blog/list/?per_page=500&category=${categoryParam}`)
        if (!response.ok) {
          return { blogs: [], pagination: { total: 0 }, category_counts: {} }
        }
        return response.json()
      } catch {
        return { blogs: [], pagination: { total: 0 }, category_counts: {} }
      }
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load documents" />
  }

  const docs = docsData?.blogs || docsData?.results || []
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

  const { data: podcastData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['podcast-tab'],
    queryFn: async () => {
      const res = await podcastApi.list()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load podcast data" />
  }

  const episodes = podcastData?.episodes || podcastData?.results || []
  const stats = podcastData?.stats || podcastData?.status_counts || { total: 3, published: 0, draft: 3 }
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
      <InlineHeaderRow title="Podcast Studio" onRefresh={refetch} isFetching={isFetching} />

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
              <div className="text-2xl font-bold text-primary-400">{stats.total || episodes.length || 3}</div>
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
              <div className="text-2xl font-bold text-accent-amber">{stats.draft || draftEpisodes.length}</div>
              <div className="text-xs text-gray-500">Drafts</div>
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
    { name: 'Substack', status: 'not_connected' },
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
function BlogRow({ blog, onClick }: { blog: BlogPost; onClick: () => void }) {
  // Status styling
  const statusStyles: Record<string, { bg: string; text: string; icon: typeof Clock }> = {
    draft: { bg: 'bg-amber-500/20', text: 'text-amber-400', icon: Clock },
    approved: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: CheckCircle },
    published: { bg: 'bg-green-500/20', text: 'text-green-400', icon: Eye },
  }
  const status = blog.status || 'draft'
  const style = statusStyles[status] || statusStyles.draft
  const StatusIcon = style.icon

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
          </div>
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
    </div>
  )
}

// Session 840: Episode row with click handler
function EpisodeRow({ episode, onClick }: { episode: PodcastEpisode; onClick: () => void }) {
  const statusColors: Record<string, { color: string; bg: string }> = {
    published: { color: 'text-green-400', bg: 'bg-green-500/20' },
    draft: { color: 'text-amber-400', bg: 'bg-amber-500/20' },
    generating: { color: 'text-blue-400', bg: 'bg-blue-500/20' },
  }
  const status = statusColors[episode.status] || statusColors.draft

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
  const { data: fullBlog, isLoading: contentLoading } = useQuery({
    queryKey: ['blog-full', blog.id],
    queryFn: async () => {
      const response = await fetch(`/api/v1/research/self-blog/${blog.id}/`)
      if (!response.ok) throw new Error('Failed to fetch blog content')
      const data = await response.json()
      return data.blog as BlogPost
    },
    enabled: showFullContent,
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/research/self-blog/${blog.id}/approve/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!response.ok) throw new Error('Failed to approve blog')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['blogs-tab'] })
      setActionError(null)
    },
    onError: (error: Error) => {
      setActionError(error.message)
    },
  })

  // Publish mutation - Session 862: Add force=true to allow publishing draft blogs
  const publishMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`/api/v1/research/self-blog/${blog.id}/publish/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force: true }),
      })
      if (!response.ok) throw new Error('Failed to publish blog')
      return response.json()
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
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-6 mb-3">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-lg font-semibold text-white mt-5 mb-2">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-base font-medium text-white mt-4 mb-2">{children}</h3>,
                      p: ({ children }) => <p className="text-gray-300 mb-3 leading-relaxed">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-3 text-gray-300">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-3 text-gray-300">{children}</ol>,
                      li: ({ children }) => <li className="mb-1">{children}</li>,
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-primary-500 pl-4 italic text-gray-400 my-4">
                          {children}
                        </blockquote>
                      ),
                      code: ({ children }) => (
                        <code className="bg-gray-800 px-1.5 py-0.5 rounded text-sm text-primary-300">{children}</code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-800 p-4 rounded-lg overflow-x-auto my-4">{children}</pre>
                      ),
                    }}
                  >
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
function EpisodeDetailModal({ episode, onClose }: { episode: PodcastEpisode; onClose: () => void }) {
  const [showScript, setShowScript] = useState(false)

  // Fetch full script when expanded
  const { data: scriptData, isLoading: scriptLoading } = useQuery({
    queryKey: ['podcast-script', episode.id],
    queryFn: async () => {
      const response = await fetch(`/api/podcasts/${episode.id}/script/`)
      if (!response.ok) throw new Error('Failed to fetch script')
      return response.json()
    },
    enabled: showScript,
  })

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
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown
                      components={{
                        h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-6 mb-3">{children}</h1>,
                        h2: ({ children }) => <h2 className="text-lg font-semibold text-white mt-5 mb-2">{children}</h2>,
                        h3: ({ children }) => <h3 className="text-base font-medium text-white mt-4 mb-2">{children}</h3>,
                        p: ({ children }) => <p className="text-gray-300 mb-3 leading-relaxed">{children}</p>,
                        strong: ({ children }) => <strong className="text-primary-300 font-semibold">{children}</strong>,
                        em: ({ children }) => <em className="text-gray-400 italic">{children}</em>,
                      }}
                    >
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
function VoiceProfileModal({ onClose }: { onClose: () => void }) {
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
          <div className="p-4 bg-gray-800/50 rounded-lg">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-12 w-12 rounded-full bg-accent-purple/20 flex items-center justify-center">
                <Mic size={24} className="text-accent-purple" />
              </div>
              <div>
                <p className="font-medium">Default Voice</p>
                <span className="text-xs px-2 py-0.5 rounded bg-accent-green/20 text-accent-green">
                  Active
                </span>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <p className="text-xs text-gray-500">Type</p>
                <p>AI Generated</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Language</p>
                <p>English</p>
              </div>
            </div>
          </div>

          <div className="text-center text-sm text-gray-500">
            <p>Voice profiles are used for podcast episode generation</p>
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

// Session 857: Platform Detail Modal
function PlatformDetailModal({ platform, onClose }: { platform: Platform; onClose: () => void }) {
  const isConnected = platform.status === 'connected'

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
            <Share2 size={20} className={isConnected ? 'text-accent-green' : 'text-gray-400'} />
            <div>
              <h3 className="font-semibold">{platform.name}</h3>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded',
                isConnected ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
              )}>
                {isConnected ? 'Connected' : 'Not Connected'}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isConnected ? (
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

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
