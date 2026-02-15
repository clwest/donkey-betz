import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '@/lib/api'
import {
  Film, Type, Image, Loader2, Heart, Download, ChevronDown, ChevronUp,
  Maximize2, Clock, Trash2, X, Check, AlertCircle, Play, Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// ── Types ───────────────────────────────────────────────────────────────────

interface GalleryVideo {
  id: string
  url: string
  thumbnail_url?: string
  prompt?: string
  model?: string
  duration?: number
  aspect_ratio?: string
  style?: string
  is_favorite?: boolean
  generation_type?: string
  view_count?: number
  download_count?: number
  created_at: string
}

interface ActiveGeneration {
  taskId: string
  prompt: string
  startedAt: number
  estimatedTime: number
}

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

// ── Constants ───────────────────────────────────────────────────────────────

const DURATION_OPTIONS = [2, 4, 6, 8, 10]

const QUALITY_OPTIONS = [
  { value: 'veo3.1_fast', label: 'Veo 3.1 Fast', desc: '~15s' },
  { value: 'veo3.1', label: 'Veo 3.1', desc: '~30s' },
  { value: 'gen4_turbo', label: 'Gen4 Turbo', desc: '~45s' },
]

const RATIO_OPTIONS = [
  { value: '1920:1080', label: '16:9', desc: 'Landscape' },
  { value: '1080:1920', label: '9:16', desc: 'Portrait' },
  { value: '1080:1080', label: '1:1', desc: 'Square' },
]

const STYLE_OPTIONS = [
  'cinematic', 'realistic', 'dramatic', 'animated',
  'documentary', 'slow_motion', 'timelapse', 'abstract',
]

function formatStyleLabel(style: string): string {
  return style.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function formatElapsed(startedAt: number): string {
  const seconds = Math.floor((Date.now() - startedAt) / 1000)
  return `${seconds}s`
}

// ── Main Page ───────────────────────────────────────────────────────────────

export default function VideoStudioPage() {
  const queryClient = useQueryClient()

  // Mode
  const [mode, setMode] = useState<'text' | 'image'>('text')

  // Text-to-video
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState<string | null>(null)
  const [quality, setQuality] = useState('veo3.1_fast')
  const [duration, setDuration] = useState(4)
  const [ratio, setRatio] = useState('1920:1080')
  const [enhancePrompt, setEnhancePrompt] = useState(true)

  // Image-to-video
  const [imageUrl, setImageUrl] = useState('')
  const [motionPrompt, setMotionPrompt] = useState('')

  // Gallery
  const [galleryFilter, setGalleryFilter] = useState('all')
  const [galleryOffset, setGalleryOffset] = useState(0)
  const [selectedVideo, setSelectedVideo] = useState<GalleryVideo | null>(null)

  // Polling
  const [activeGenerations, setActiveGenerations] = useState<ActiveGeneration[]>([])
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Feedback + mobile
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [generatePanelOpen, setGeneratePanelOpen] = useState(true)

  // Auto-switch quality default when mode changes
  useEffect(() => {
    setQuality(mode === 'text' ? 'veo3.1_fast' : 'gen4_turbo')
  }, [mode])

  // ── Queries ─────────────────────────────────────────────────────────────

  const { data: galleryData, isLoading: galleryLoading } = useQuery({
    queryKey: ['video-history', galleryFilter, galleryOffset],
    queryFn: () =>
      contentApi.videoHistory({
        ...(galleryFilter === 'favorites' ? { is_favorite: 'true' } : {}),
        ...(galleryFilter === 'text' ? { generation_type: 'text_to_video' } : {}),
        ...(galleryFilter === 'image' ? { generation_type: 'image_to_video' } : {}),
        limit: 20,
        offset: galleryOffset,
      }),
  })

  const videos: GalleryVideo[] = galleryData?.data?.videos || galleryData?.data?.results || []
  const totalCount: number = galleryData?.data?.total || galleryData?.data?.count || videos.length

  // ── Helpers ───────────────────────────────────────────────────────────

  const showFeedback = useCallback((type: 'success' | 'error', message: string) => {
    setActionResult({ type, message })
    setTimeout(() => setActionResult(null), type === 'success' ? 3000 : 4000)
  }, [])

  const refetchGallery = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['video-history'] })
  }, [queryClient])

  const addGeneration = useCallback((taskId: string, promptText: string, estimatedTime: number) => {
    setActiveGenerations(prev => [...prev, {
      taskId,
      prompt: promptText,
      startedAt: Date.now(),
      estimatedTime,
    }])
  }, [])

  const removeGeneration = useCallback((taskId: string) => {
    setActiveGenerations(prev => prev.filter(g => g.taskId !== taskId))
  }, [])

  // ── Polling ───────────────────────────────────────────────────────────

  useEffect(() => {
    if (activeGenerations.length === 0) {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
      return
    }

    if (pollingRef.current) return // already polling

    pollingRef.current = setInterval(async () => {
      const currentGens = activeGenerations
      for (const gen of currentGens) {
        try {
          const res = await contentApi.videoStatus(gen.taskId)
          const status = res.data?.status
          if (status === 'completed' || status === 'COMPLETED') {
            showFeedback('success', 'Video generation complete!')
            refetchGallery()
            removeGeneration(gen.taskId)
          } else if (status === 'failed' || status === 'FAILED') {
            showFeedback('error', res.data?.error || 'Video generation failed')
            removeGeneration(gen.taskId)
          }
        } catch {
          // Network error — keep polling
        }
      }
    }, 5000)

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [activeGenerations, showFeedback, refetchGallery, removeGeneration])

  // ── Mutations ─────────────────────────────────────────────────────────

  const getEstimatedTime = () => {
    const opt = QUALITY_OPTIONS.find(q => q.value === quality)
    return parseInt(opt?.desc?.replace(/[^0-9]/g, '') || '30')
  }

  const textToVideoMutation = useMutation({
    mutationFn: () =>
      contentApi.textToVideo(prompt, {
        model: quality,
        duration,
        ratio,
        style: style || undefined,
        enhance_prompt: enhancePrompt,
      }),
    onSuccess: (res) => {
      const taskId = res.data?.task_id || res.data?.id
      if (taskId) {
        addGeneration(taskId, prompt.slice(0, 60), getEstimatedTime())
        showFeedback('success', 'Video generation started!')
      } else {
        // Synchronous response — direct completion
        refetchGallery()
        showFeedback('success', 'Video generated!')
      }
    },
    onError: () => showFeedback('error', 'Failed to start video generation'),
  })

  const imageToVideoMutation = useMutation({
    mutationFn: () =>
      contentApi.imageToVideo(imageUrl, {
        prompt: motionPrompt || undefined,
        model: quality,
        duration,
        ratio,
      }),
    onSuccess: (res) => {
      const taskId = res.data?.task_id || res.data?.id
      if (taskId) {
        addGeneration(taskId, motionPrompt.slice(0, 60) || 'Image to video', getEstimatedTime())
        showFeedback('success', 'Video generation started!')
      } else {
        refetchGallery()
        showFeedback('success', 'Video generated!')
      }
    },
    onError: () => showFeedback('error', 'Failed to start video generation'),
  })

  const favoriteMutation = useMutation({
    mutationFn: (videoId: string) => contentApi.toggleVideoFavorite(videoId),
    onSuccess: () => refetchGallery(),
  })

  const deleteMutation = useMutation({
    mutationFn: (videoId: string) => contentApi.deleteVideo(videoId),
    onSuccess: () => {
      refetchGallery()
      setSelectedVideo(null)
      showFeedback('success', 'Video deleted')
    },
  })

  // ── Handlers ──────────────────────────────────────────────────────────

  const handleGenerate = () => {
    if (mode === 'text') {
      if (!prompt.trim()) return
      textToVideoMutation.mutate()
    } else {
      if (!imageUrl.trim()) return
      imageToVideoMutation.mutate()
    }
  }

  const handleExtend = (video: GalleryVideo) => {
    if (!video.url) return
    contentApi.extendVideo(video.url, { prompt: video.prompt })
      .then(res => {
        const taskId = res.data?.task_id || res.data?.id
        if (taskId) {
          addGeneration(taskId, `Extend: ${(video.prompt || '').slice(0, 40)}`, 30)
          showFeedback('success', 'Video extend started!')
        }
      })
      .catch(() => showFeedback('error', 'Failed to extend video'))
  }

  const handleUpscale = (video: GalleryVideo) => {
    if (!video.url) return
    contentApi.upscaleVideo(video.url, video.prompt || '')
      .then(res => {
        const taskId = res.data?.task_id || res.data?.id
        if (taskId) {
          addGeneration(taskId, `Upscale: ${(video.prompt || '').slice(0, 40)}`, 30)
          showFeedback('success', 'Video upscale started!')
        }
      })
      .catch(() => showFeedback('error', 'Failed to upscale video'))
  }

  const handleDownload = (video: GalleryVideo) => {
    contentApi.incrementVideoDownload(video.id).catch(() => {})
    window.open(video.url, '_blank')
  }

  const handleVideoClick = (video: GalleryVideo) => {
    setSelectedVideo(video)
    contentApi.incrementVideoView(video.id).catch(() => {})
  }

  const isGenerating = textToVideoMutation.isPending || imageToVideoMutation.isPending

  // ── Render ────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-dark-border px-6 py-4">
        <div className="flex items-center gap-3">
          <Film className="text-primary-400" size={24} />
          <h1 className="text-xl font-bold text-white">Video Studio</h1>
        </div>
        {actionResult && (
          <div
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm',
              actionResult.type === 'success'
                ? 'bg-green-500/10 text-green-400'
                : 'bg-red-500/10 text-red-400'
            )}
          >
            {actionResult.type === 'success' ? <Check size={14} /> : <AlertCircle size={14} />}
            {actionResult.message}
          </div>
        )}
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* ── Generate Panel (left) ──────────────────────────────────── */}
        <div
          className={cn(
            'border-b lg:border-b-0 lg:border-r border-dark-border overflow-y-auto',
            'lg:w-1/3 xl:w-[360px] flex-shrink-0'
          )}
        >
          {/* Mobile toggle */}
          <button
            className="lg:hidden w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-gray-300 hover:text-white"
            onClick={() => setGeneratePanelOpen(!generatePanelOpen)}
          >
            Generate
            {generatePanelOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          <div className={cn('p-4 space-y-4', !generatePanelOpen && 'hidden lg:block')}>
            {/* Mode tabs */}
            <div className="flex border-b border-dark-border">
              <button
                onClick={() => setMode('text')}
                className={cn(
                  'flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                  mode === 'text'
                    ? 'border-primary-500 text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                )}
              >
                <Type size={14} />
                Text to Video
              </button>
              <button
                onClick={() => setMode('image')}
                className={cn(
                  'flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                  mode === 'image'
                    ? 'border-primary-500 text-primary-400'
                    : 'border-transparent text-gray-500 hover:text-gray-300'
                )}
              >
                <Image size={14} />
                Image to Video
              </button>
            </div>

            {/* Text-to-video inputs */}
            {mode === 'text' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Prompt</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe your video..."
                  rows={4}
                  className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none"
                />
              </div>
            )}

            {/* Image-to-video inputs */}
            {mode === 'image' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Image URL</label>
                  <input
                    type="text"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                    placeholder="https://example.com/image.jpg"
                    className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Motion Prompt</label>
                  <textarea
                    value={motionPrompt}
                    onChange={(e) => setMotionPrompt(e.target.value)}
                    placeholder="Describe the motion or camera movement..."
                    rows={3}
                    className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none"
                  />
                </div>
              </>
            )}

            {/* Duration */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Duration</label>
              <div className="flex gap-1.5">
                {DURATION_OPTIONS.map((d) => (
                  <button
                    key={d}
                    onClick={() => setDuration(d)}
                    className={cn(
                      'flex-1 rounded-lg border px-2 py-1.5 text-center text-xs transition-colors',
                      duration === d
                        ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                        : 'border-dark-border text-gray-400 hover:border-gray-600 hover:text-gray-200'
                    )}
                  >
                    {d}s
                  </button>
                ))}
              </div>
            </div>

            {/* Quality / Model */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Quality</label>
              <div className="space-y-1.5">
                {QUALITY_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setQuality(opt.value)}
                    className={cn(
                      'w-full rounded-lg border px-3 py-2 text-left transition-colors',
                      quality === opt.value
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-dark-border hover:border-gray-600'
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span className={cn('text-sm font-medium', quality === opt.value ? 'text-primary-300' : 'text-gray-300')}>
                        {opt.label}
                      </span>
                      <span className="text-[10px] text-gray-500">{opt.desc}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Aspect Ratio */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Aspect Ratio</label>
              <div className="flex gap-2">
                {RATIO_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setRatio(opt.value)}
                    className={cn(
                      'flex-1 rounded-lg border px-2 py-1.5 text-center transition-colors',
                      ratio === opt.value
                        ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                        : 'border-dark-border text-gray-400 hover:border-gray-600 hover:text-gray-200'
                    )}
                  >
                    <div className="text-xs font-medium">{opt.label}</div>
                    <div className="text-[10px] text-gray-500">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Style */}
            {mode === 'text' && (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Style</label>
                <div className="flex flex-wrap gap-1.5">
                  {STYLE_OPTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => setStyle(style === s ? null : s)}
                      className={cn(
                        'px-2 py-0.5 rounded-full text-xs border transition-colors',
                        style === s
                          ? 'border-primary-500 bg-primary-500/20 text-primary-300'
                          : 'border-dark-border text-gray-400 hover:text-gray-200 hover:border-gray-600'
                      )}
                    >
                      {formatStyleLabel(s)}
                    </button>
                  ))}
                </div>
                {style && (
                  <button
                    onClick={() => setStyle(null)}
                    className="mt-1.5 text-xs text-gray-500 hover:text-gray-300"
                  >
                    Clear style
                  </button>
                )}
              </div>
            )}

            {/* Enhance prompt */}
            {mode === 'text' && (
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={enhancePrompt}
                  onChange={(e) => setEnhancePrompt(e.target.checked)}
                  className="rounded border-dark-border bg-dark-bg text-primary-500 focus:ring-primary-500 focus:ring-offset-0"
                />
                <span className="text-sm text-gray-300">Enhance prompt</span>
              </label>
            )}

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || (mode === 'text' ? !prompt.trim() : !imageUrl.trim())}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-medium text-white transition-colors"
            >
              {isGenerating ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Generate Video
                </>
              )}
            </button>

            {/* Active Generations */}
            {activeGenerations.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs text-gray-500">In Progress</span>
                {activeGenerations.map((gen) => (
                  <div
                    key={gen.taskId}
                    className="flex items-center gap-2 rounded-lg border border-dark-border bg-dark-bg px-3 py-2"
                  >
                    <Loader2 size={14} className="animate-spin text-primary-400 flex-shrink-0" />
                    <span className="text-xs text-gray-300 truncate flex-1">
                      {gen.prompt || 'Generating...'}
                    </span>
                    <span className="text-[10px] text-gray-500 flex-shrink-0">
                      {formatElapsed(gen.startedAt)} / ~{gen.estimatedTime}s
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Gallery Panel (right) ──────────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Filter bar */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-dark-border">
            {[
              { key: 'all', label: 'All' },
              { key: 'favorites', label: 'Favorites' },
              { key: 'text', label: 'Text to Video' },
              { key: 'image', label: 'Image to Video' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => {
                  setGalleryFilter(key)
                  setGalleryOffset(0)
                }}
                className={cn(
                  'px-3 py-1 rounded-full text-xs font-medium transition-colors',
                  galleryFilter === key
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:text-white'
                )}
              >
                {label}
              </button>
            ))}
            <span className="ml-auto text-xs text-gray-500">
              {totalCount} video{totalCount !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Grid */}
          <div className="flex-1 overflow-y-auto p-4">
            {galleryLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="animate-spin text-gray-500" size={24} />
              </div>
            ) : videos.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                <Film size={40} className="mb-3 opacity-40" />
                <p className="text-sm">
                  {galleryFilter === 'all'
                    ? 'Generate your first video'
                    : `No ${galleryFilter} videos`}
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
                  {videos.map((video) => (
                    <button
                      key={video.id}
                      onClick={() => handleVideoClick(video)}
                      className="group relative aspect-video rounded-lg overflow-hidden border border-dark-border hover:border-primary-500/50 transition-colors text-left"
                    >
                      {video.thumbnail_url ? (
                        <img
                          src={video.thumbnail_url}
                          alt={video.prompt || 'Generated video'}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                      ) : (
                        <div className="w-full h-full bg-dark-bg flex items-center justify-center">
                          <Film size={32} className="text-gray-700" />
                        </div>
                      )}
                      {/* Play overlay */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="w-12 h-12 rounded-full bg-black/60 flex items-center justify-center">
                          <Play size={20} className="text-white ml-0.5" />
                        </div>
                      </div>
                      {/* Bottom gradient bar */}
                      <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-2 flex items-end justify-between">
                        <div className="flex items-center gap-2 min-w-0">
                          {video.duration && (
                            <span className="text-[10px] text-gray-300 flex-shrink-0">
                              {video.duration}s
                            </span>
                          )}
                          {video.prompt && (
                            <span className="text-[10px] text-gray-400 truncate">
                              {video.prompt}
                            </span>
                          )}
                        </div>
                        {video.is_favorite && (
                          <Heart size={12} className="text-red-400 fill-red-400 flex-shrink-0" />
                        )}
                      </div>
                      {/* Model badge */}
                      {video.model && (
                        <span className="absolute top-1.5 right-1.5 text-[9px] bg-black/70 text-gray-400 px-1.5 py-0.5 rounded">
                          {video.model}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                {/* Load more */}
                {videos.length < totalCount && (
                  <div className="flex justify-center mt-4">
                    <button
                      onClick={() => setGalleryOffset((prev) => prev + 20)}
                      className="px-4 py-2 rounded-lg border border-dark-border text-sm text-gray-400 hover:text-white hover:border-gray-600 transition-colors"
                    >
                      Load more
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* ── Video Detail Modal ────────────────────────────────────────── */}
      {selectedVideo && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) setSelectedVideo(null)
          }}
        >
          <div className="bg-dark-card rounded-xl border border-dark-border max-w-5xl w-full max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-dark-border">
              <h3 className="text-sm font-medium text-white truncate">Video Detail</h3>
              <button
                onClick={() => setSelectedVideo(null)}
                className="text-gray-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal body */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col lg:flex-row gap-4">
              {/* Video player */}
              <div className="lg:flex-1 flex items-center justify-center bg-black rounded-lg overflow-hidden">
                <video
                  src={selectedVideo.url}
                  controls
                  autoPlay
                  loop
                  poster={selectedVideo.thumbnail_url}
                  className="max-h-[60vh] w-full object-contain"
                />
              </div>

              {/* Info + actions */}
              <div className="lg:w-64 space-y-4 flex-shrink-0">
                {/* Metadata */}
                {selectedVideo.prompt && (
                  <div>
                    <span className="text-xs text-gray-500">Prompt</span>
                    <p className="text-sm text-gray-300 mt-0.5">{selectedVideo.prompt}</p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {selectedVideo.model && (
                    <div>
                      <span className="text-gray-500">Model</span>
                      <p className="text-gray-300">{selectedVideo.model}</p>
                    </div>
                  )}
                  {selectedVideo.duration && (
                    <div>
                      <span className="text-gray-500">Duration</span>
                      <p className="text-gray-300">{selectedVideo.duration}s</p>
                    </div>
                  )}
                  {selectedVideo.aspect_ratio && (
                    <div>
                      <span className="text-gray-500">Ratio</span>
                      <p className="text-gray-300">{selectedVideo.aspect_ratio}</p>
                    </div>
                  )}
                  {selectedVideo.created_at && (
                    <div>
                      <span className="text-gray-500">Created</span>
                      <p className="text-gray-300">{new Date(selectedVideo.created_at).toLocaleDateString()}</p>
                    </div>
                  )}
                  {(selectedVideo.view_count ?? 0) > 0 && (
                    <div>
                      <span className="text-gray-500">Views</span>
                      <p className="text-gray-300">{selectedVideo.view_count}</p>
                    </div>
                  )}
                  {(selectedVideo.download_count ?? 0) > 0 && (
                    <div>
                      <span className="text-gray-500">Downloads</span>
                      <p className="text-gray-300">{selectedVideo.download_count}</p>
                    </div>
                  )}
                </div>

                {/* Action buttons */}
                <div className="space-y-1.5">
                  <span className="text-xs text-gray-500">Actions</span>

                  <button
                    onClick={() => handleExtend(selectedVideo)}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 transition-colors"
                  >
                    <Clock size={14} />
                    Extend
                  </button>

                  <button
                    onClick={() => handleUpscale(selectedVideo)}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 transition-colors"
                  >
                    <Maximize2 size={14} />
                    Upscale
                  </button>

                  <button
                    onClick={() => handleDownload(selectedVideo)}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 transition-colors"
                  >
                    <Download size={14} />
                    Download
                  </button>

                  <button
                    onClick={() => favoriteMutation.mutate(selectedVideo.id)}
                    disabled={favoriteMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    <Heart size={14} className={selectedVideo.is_favorite ? 'text-red-400 fill-red-400' : ''} />
                    {selectedVideo.is_favorite ? 'Unfavorite' : 'Favorite'}
                  </button>

                  <button
                    onClick={() => {
                      if (confirm('Delete this video?')) {
                        deleteMutation.mutate(selectedVideo.id)
                      }
                    }}
                    disabled={deleteMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-red-800/50 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:border-red-700 disabled:opacity-40 transition-colors"
                  >
                    {deleteMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
