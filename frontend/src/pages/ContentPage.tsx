import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '@/lib/api'
import {
  Image, Video, Music, Box, Plus, Calendar, Wand2, Heart,
  Loader2, CheckCircle, XCircle, Sparkles, FileText, Send,
  Play, X, Grid, FolderKanban, Layout, Clock
} from 'lucide-react'
import { cn } from '@/lib/cn'

type ContentType = 'images' | 'video' | 'audio' | '3d'
type TabType = 'gallery' | 'calendar' | 'projects' | 'templates'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface GalleryItem {
  id: string
  type: 'image' | 'video' | 'audio' | '3d'
  url: string
  thumbnail_url?: string
  prompt?: string
  created_at: string
  is_favorite?: boolean
}

interface CalendarEvent {
  id: string
  title: string
  scheduled_for: string
  channel: string
  status: 'scheduled' | 'published' | 'draft'
  type: string
}

interface Project {
  id: string
  name: string
  description: string
  status: 'active' | 'completed' | 'archived'
  items_count: number
  created_at: string
  updated_at: string
}

interface Template {
  id: string
  name: string
  category: string
  description: string
  uses: number
}

interface GenerateModalProps {
  type: ContentType
  onClose: () => void
  onGenerate: (prompt: string) => void
  isLoading: boolean
}

const contentTypes = [
  {
    id: 'images' as ContentType,
    title: 'Image Generation',
    description: 'Create AI-generated images with various models',
    icon: Image,
    color: '#8b5cf6',
    actions: ['Generate', 'Edit', 'Upscale'],
  },
  {
    id: 'video' as ContentType,
    title: 'Video Generation',
    description: 'Generate videos with AI-powered tools',
    icon: Video,
    color: '#22c55e',
    actions: ['Text to Video', 'Image to Video'],
  },
  {
    id: 'audio' as ContentType,
    title: 'Audio Generation',
    description: 'Create music, voiceovers, and sound effects',
    icon: Music,
    color: '#f59e0b',
    actions: ['Voice Clone', 'Music Generate'],
  },
  {
    id: '3d' as ContentType,
    title: '3D Generation',
    description: 'Generate 3D models and assets',
    icon: Box,
    color: '#06b6d4',
    actions: ['Text to 3D', 'Image to 3D'],
  },
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

function GenerateModal({ type, onClose, onGenerate, isLoading }: GenerateModalProps) {
  const [prompt, setPrompt] = useState('')
  const typeConfig = contentTypes.find(t => t.id === type)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (prompt.trim()) {
      onGenerate(prompt)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4 p-6" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {typeConfig && <typeConfig.icon size={24} style={{ color: typeConfig.color }} />}
            <h3 className="text-lg font-semibold">New {typeConfig?.title.replace(' Generation', '')}</h3>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">Describe what you want to create</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full h-32 bg-dark-bg border border-dark-border rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
              placeholder={type === 'images' ? 'A futuristic cityscape at sunset with flying cars...' :
                          type === 'video' ? 'A timelapse of clouds moving over mountains...' :
                          type === 'audio' ? 'An upbeat electronic track with synth melodies...' :
                          'A low-poly character model for a mobile game...'}
              autoFocus
            />
          </div>

          <div className="flex justify-end gap-3">
            <button type="button" onClick={onClose} className="btn btn-secondary">
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary flex items-center gap-2"
              disabled={isLoading || !prompt.trim()}
            >
              {isLoading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : (
                <Sparkles size={16} />
              )}
              Generate
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const tabs = [
  { id: 'gallery' as TabType, label: 'Gallery', icon: Grid },
  { id: 'calendar' as TabType, label: 'Calendar', icon: Calendar },
  { id: 'projects' as TabType, label: 'Projects', icon: FolderKanban },
  { id: 'templates' as TabType, label: 'Templates', icon: Layout },
]

export default function ContentPage() {
  const [activeTab, setActiveTab] = useState<TabType>('gallery')
  const [activeType, setActiveType] = useState<ContentType | null>(null)
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [generateType, setGenerateType] = useState<ContentType>('images')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const queryClient = useQueryClient()

  // Fetch gallery items
  const { data: galleryData, isLoading: loadingGallery } = useQuery({
    queryKey: ['gallery'],
    queryFn: () => contentApi.unifiedGallery(),
  })

  // Fetch content calendar
  const { data: calendarData, isLoading: loadingCalendar } = useQuery({
    queryKey: ['content-calendar'],
    queryFn: () => contentApi.calendar(),
    enabled: activeTab === 'calendar',
  })

  // Fetch projects
  const { data: projectsData, isLoading: loadingProjects } = useQuery({
    queryKey: ['creative-projects'],
    queryFn: () => contentApi.projects(),
    enabled: activeTab === 'projects',
  })

  // Fetch templates
  const { data: templatesData, isLoading: loadingTemplates } = useQuery({
    queryKey: ['content-templates'],
    queryFn: () => contentApi.templates(),
    enabled: activeTab === 'templates',
  })

  // Generate image mutation
  const generateImageMutation = useMutation({
    mutationFn: (prompt: string) => contentApi.generateImage(prompt),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Image generation started! Check gallery in a moment.' })
      setShowGenerateModal(false)
      queryClient.invalidateQueries({ queryKey: ['gallery'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate image' })
    },
  })

  // Generate video mutation
  const generateVideoMutation = useMutation({
    mutationFn: (prompt: string) => contentApi.textToVideo(prompt),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Video generation started! This may take a few minutes.' })
      setShowGenerateModal(false)
      queryClient.invalidateQueries({ queryKey: ['gallery'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate video' })
    },
  })

  // Toggle favorite mutation
  const toggleFavoriteMutation = useMutation({
    mutationFn: (itemId: string) => contentApi.toggleFavorite(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gallery'] })
    },
  })

  // Generate blog mutation
  const generateBlogMutation = useMutation({
    mutationFn: () => contentApi.generateBlog('AI and Creative Technology'),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Blog post generated!' })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate blog post' })
    },
  })

  const galleryItems: GalleryItem[] = galleryData?.data?.items || galleryData?.data || []
  const calendarEvents: CalendarEvent[] = calendarData?.data?.events || calendarData?.data?.upcoming || []
  const projects: Project[] = projectsData?.data?.projects || projectsData?.data || []
  const templates: Template[] = templatesData?.data?.templates || templatesData?.data || []

  // Filter gallery by active type
  const filteredGallery = activeType
    ? galleryItems.filter(item => {
        if (activeType === 'images') return item.type === 'image'
        if (activeType === 'video') return item.type === 'video'
        return item.type === activeType
      })
    : galleryItems

  const handleGenerate = (prompt: string) => {
    if (generateType === 'images') {
      generateImageMutation.mutate(prompt)
    } else if (generateType === 'video') {
      generateVideoMutation.mutate(prompt)
    } else {
      setActionResult({ type: 'success', message: `${generateType} generation coming soon!` })
      setShowGenerateModal(false)
    }
  }

  const openGenerateModal = (type: ContentType) => {
    setGenerateType(type)
    setShowGenerateModal(true)
  }

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const isGenerating = generateImageMutation.isPending || generateVideoMutation.isPending

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Content Studio</h1>
          <p className="text-gray-400">Create and manage all your content</p>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => openGenerateModal('images')}
        >
          <Plus size={16} />
          New Content
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Gallery Tab */}
      {activeTab === 'gallery' && (
        <>
          {/* Content Type Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {contentTypes.map(({ id, title, description, icon: Icon, color, actions }) => (
          <div
            key={id}
            className={cn(
              'card cursor-pointer transition-all',
              activeType === id ? 'border-primary-500 ring-1 ring-primary-500' : 'hover:border-gray-600'
            )}
            onClick={() => setActiveType(activeType === id ? null : id)}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className="h-12 w-12 rounded-lg flex items-center justify-center"
                style={{ backgroundColor: `${color}20` }}
              >
                <Icon size={24} style={{ color }} />
              </div>
              <button
                className="h-8 w-8 rounded-lg bg-primary-500/20 flex items-center justify-center hover:bg-primary-500/30 transition-colors"
                onClick={(e) => {
                  e.stopPropagation()
                  openGenerateModal(id)
                }}
              >
                <Plus size={16} className="text-primary-400" />
              </button>
            </div>
            <h3 className="font-semibold mb-1">{title}</h3>
            <p className="text-sm text-gray-400 mb-3">{description}</p>
            <div className="flex flex-wrap gap-2">
              {actions.map((action) => {
                const isImplemented = ['Generate', 'Text to Video', 'Text to 3D'].includes(action)
                return (
                  <button
                    key={action}
                    className={`text-xs px-2 py-1 rounded transition-colors ${
                      isImplemented
                        ? 'bg-dark-bg text-gray-400 hover:text-white hover:bg-dark-border'
                        : 'bg-dark-bg text-gray-600 cursor-not-allowed opacity-50'
                    }`}
                    disabled={!isImplemented}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (isImplemented) {
                        openGenerateModal(id)
                      }
                    }}
                  >
                    {action}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Recent Creations */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">
            {activeType ? `${contentTypes.find(t => t.id === activeType)?.title}` : 'Recent Creations'}
          </h3>
          {activeType && (
            <button
              className="text-sm text-gray-400 hover:text-white"
              onClick={() => setActiveType(null)}
            >
              Show All
            </button>
          )}
        </div>
        {loadingGallery ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="animate-spin" size={32} />
          </div>
        ) : filteredGallery.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {filteredGallery.slice(0, 12).map((item) => (
              <div
                key={item.id}
                className="group relative aspect-square rounded-lg bg-dark-border overflow-hidden cursor-pointer"
                onClick={() => setActionResult({ type: 'success', message: `Viewing: ${item.prompt?.slice(0, 50) || 'Content item'}...` })}
              >
                {item.thumbnail_url || item.url ? (
                  <img
                    src={item.thumbnail_url || item.url}
                    alt={item.prompt || 'Generated content'}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    {item.type === 'video' ? <Video className="text-gray-600" size={32} /> :
                     item.type === 'audio' ? <Music className="text-gray-600" size={32} /> :
                     item.type === '3d' ? <Box className="text-gray-600" size={32} /> :
                     <Image className="text-gray-600" size={32} />}
                  </div>
                )}
                {/* Overlay on hover */}
                <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button
                    className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30"
                    onClick={(e) => {
                      e.stopPropagation()
                      toggleFavoriteMutation.mutate(item.id)
                    }}
                  >
                    <Heart size={16} className={item.is_favorite ? 'text-accent-red fill-accent-red' : 'text-white'} />
                  </button>
                  {item.type === 'video' && (
                    <button className="h-8 w-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30">
                      <Play size={16} className="text-white" />
                    </button>
                  )}
                </div>
                {/* Type badge */}
                <div className="absolute top-2 left-2">
                  <span className={cn(
                    'text-xs px-1.5 py-0.5 rounded',
                    item.type === 'image' ? 'bg-purple-500/80' :
                    item.type === 'video' ? 'bg-green-500/80' :
                    item.type === 'audio' ? 'bg-amber-500/80' : 'bg-cyan-500/80'
                  )}>
                    {item.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-400">
            <Image className="mx-auto mb-2" size={48} />
            <p>No content yet</p>
            <p className="text-sm text-gray-500 mt-1">Create your first piece of content above</p>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <button
            className="btn btn-primary flex items-center gap-2"
            onClick={() => openGenerateModal('images')}
            disabled={isGenerating}
          >
            {generateImageMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
            New Image
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => openGenerateModal('video')}
            disabled={isGenerating}
          >
            {generateVideoMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Video size={16} />}
            New Video
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => setActionResult({ type: 'success', message: 'Voice cloning coming soon!' })}
          >
            <Music size={16} />
            Voice Clone
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => setActionResult({ type: 'success', message: 'Opening content calendar...' })}
          >
            <Calendar size={16} />
            Content Calendar
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => generateBlogMutation.mutate()}
            disabled={generateBlogMutation.isPending}
          >
            {generateBlogMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <FileText size={16} />}
            Generate Blog
          </button>
          <button
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => setActionResult({ type: 'success', message: 'Social post generator coming soon!' })}
          >
            <Send size={16} />
            Social Post
          </button>
        </div>
      </div>

        </>
      )}

      {/* Calendar Tab */}
      {activeTab === 'calendar' && (
        <div className="space-y-6">
          {/* Calendar Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <Calendar className="text-primary-400" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Scheduled</p>
                  <p className="text-2xl font-bold">{calendarEvents.filter(e => e.status === 'scheduled').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <CheckCircle className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Published</p>
                  <p className="text-2xl font-bold">{calendarEvents.filter(e => e.status === 'published').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <FileText className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Drafts</p>
                  <p className="text-2xl font-bold">{calendarEvents.filter(e => e.status === 'draft').length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Clock className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">This Week</p>
                  <p className="text-2xl font-bold">{calendarEvents.length}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Calendar Events List */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Content Calendar</h3>
            {loadingCalendar ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin" size={32} />
              </div>
            ) : calendarEvents.length > 0 ? (
              <div className="space-y-3">
                {calendarEvents.map((event) => (
                  <div
                    key={event.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                    onClick={() => setActionResult({ type: 'success', message: `Viewing: ${event.title}` })}
                  >
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        'h-10 w-10 rounded-lg flex items-center justify-center',
                        event.status === 'published' ? 'bg-accent-green/20' :
                        event.status === 'scheduled' ? 'bg-primary-500/20' : 'bg-accent-amber/20'
                      )}>
                        {event.status === 'published' ? <CheckCircle size={20} className="text-accent-green" /> :
                         event.status === 'scheduled' ? <Calendar size={20} className="text-primary-400" /> :
                         <FileText size={20} className="text-accent-amber" />}
                      </div>
                      <div>
                        <p className="font-medium">{event.title}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{event.channel}</span>
                          <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{event.type}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-sm font-medium">{new Date(event.scheduled_for).toLocaleDateString()}</p>
                        <p className="text-xs text-gray-500">{new Date(event.scheduled_for).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        event.status === 'published' ? 'bg-accent-green/20 text-accent-green' :
                        event.status === 'scheduled' ? 'bg-primary-500/20 text-primary-400' : 'bg-accent-amber/20 text-accent-amber'
                      )}>
                        {event.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Calendar className="mx-auto mb-2" size={48} />
                <p>No scheduled content</p>
                <p className="text-sm text-gray-500 mt-1">Schedule content to see it here</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Projects Tab */}
      {activeTab === 'projects' && (
        <div className="space-y-6">
          {/* Projects Grid */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Creative Projects</h3>
              <button
                className="btn btn-primary text-sm flex items-center gap-2"
                onClick={() => setActionResult({ type: 'success', message: 'Create project coming soon!' })}
              >
                <Plus size={14} />
                New Project
              </button>
            </div>
            {loadingProjects ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin" size={32} />
              </div>
            ) : projects.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                    onClick={() => setActionResult({ type: 'success', message: `Opening: ${project.name}` })}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className={cn(
                        'h-10 w-10 rounded-lg flex items-center justify-center',
                        project.status === 'active' ? 'bg-accent-green/20' :
                        project.status === 'completed' ? 'bg-accent-cyan/20' : 'bg-gray-500/20'
                      )}>
                        <FolderKanban size={20} className={
                          project.status === 'active' ? 'text-accent-green' :
                          project.status === 'completed' ? 'text-accent-cyan' : 'text-gray-400'
                        } />
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        project.status === 'active' ? 'bg-accent-green/20 text-accent-green' :
                        project.status === 'completed' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {project.status}
                      </span>
                    </div>
                    <h4 className="font-medium mb-1">{project.name}</h4>
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">{project.description}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{project.items_count} items</span>
                      <span>Updated {new Date(project.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <FolderKanban className="mx-auto mb-2" size={48} />
                <p>No projects yet</p>
                <p className="text-sm text-gray-500 mt-1">Create a project to organize your content</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Content Templates</h3>
          {loadingTemplates ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : templates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map((template) => (
                <div
                  key={template.id}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                  onClick={() => setActionResult({ type: 'success', message: `Using template: ${template.name}` })}
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs px-2 py-0.5 rounded bg-primary-600/20 text-primary-400">
                      {template.category}
                    </span>
                    <span className="text-xs text-gray-500">{template.uses} uses</span>
                  </div>
                  <h4 className="font-medium mb-1">{template.name}</h4>
                  <p className="text-sm text-gray-400">{template.description}</p>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Layout className="mx-auto mb-2" size={48} />
              <p>No templates available</p>
              <p className="text-sm text-gray-500 mt-1">Templates will appear here</p>
            </div>
          )}
        </div>
      )}

      {/* Generate Modal */}
      {showGenerateModal && (
        <GenerateModal
          type={generateType}
          onClose={() => setShowGenerateModal(false)}
          onGenerate={handleGenerate}
          isLoading={isGenerating}
        />
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
