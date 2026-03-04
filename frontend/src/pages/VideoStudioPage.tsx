import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '@/lib/api'
import {
  Film, Type, Image, Loader2, Heart, Download, ChevronDown, ChevronUp,
  Maximize2, Clock, Trash2, X, Check, AlertCircle, Play, Sparkles,
  Scissors, Palette, Music, ArrowUp, ArrowDown, Link2, Upload,
  Mic, Volume2, Grid, FileText, Package, ExternalLink,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// ── Types ───────────────────────────────────────────────────────────────────

interface GalleryVideo {
  id: string
  url?: string
  video_url?: string
  thumbnail_url?: string
  prompt?: string
  model?: string
  model_used?: string
  duration?: number
  aspect_ratio?: string
  ratio?: string
  style?: string
  is_favorite?: boolean
  generation_type?: string
  video_type?: string
  view_count?: number
  download_count?: number
  created_at: string
}

interface TranscriptSummary {
  id: string
  video_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  provider?: string
  language?: string
  text_length: number
  segment_count: number
  duration_seconds?: number
  error?: string | null
  created_at?: string
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

type StudioMode = 'generate' | 'edit' | 'chain'

/** Get playable URL — API returns video_url, some paths use url */
const getVideoUrl = (v: GalleryVideo) => v.video_url || v.url || ''

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

const COLOR_GRADE_OPTIONS = [
  { value: 'cinematic_warm', label: 'Cinematic Warm', desc: 'Warm orange tones' },
  { value: 'cinematic_cool', label: 'Cinematic Cool', desc: 'Cool blue tones' },
  { value: 'vintage', label: 'Vintage', desc: 'Retro film look' },
  { value: 'modern', label: 'Modern', desc: 'Clean and balanced' },
  { value: 'high_contrast', label: 'High Contrast', desc: 'Bold dramatic' },
  { value: 'soft', label: 'Soft', desc: 'Gentle diffused' },
  { value: 'vibrant', label: 'Vibrant', desc: 'Punchy saturated' },
]

const VOICE_PRESETS = [
  'Rachel', 'Antoni', 'Bella', 'Callum', 'Charlotte', 'Daniel',
  'Domi', 'Elli', 'Emily', 'George', 'Matilda', 'Sam',
]

interface ImageHistoryItem {
  id: string
  image_url?: string
  url?: string
  prompt?: string
  created_at?: string
}

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

  // Studio mode
  const [studioMode, setStudioMode] = useState<StudioMode>('generate')

  // Generate > Mode
  const [mode, setMode] = useState<'text' | 'image' | 'upload'>('text')

  // Upload
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const uploadInputRef = useRef<HTMLInputElement>(null)

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

  // Edit mode
  const [editVideoId, setEditVideoId] = useState<string | null>(null)
  const [editTool, setEditTool] = useState<'text' | 'color' | 'audio' | 'voice' | 'sfx'>('text')
  const [overlayText, setOverlayText] = useState('')
  const [overlayPosition, setOverlayPosition] = useState('center')
  const [overlayFontSize, setOverlayFontSize] = useState(72)
  const [overlayStart, setOverlayStart] = useState(0)
  const [overlayDuration, setOverlayDuration] = useState(3)
  const [colorStyle, setColorStyle] = useState('cinematic_warm')
  const [audioFile, setAudioFile] = useState<File | null>(null)
  const [audioVolume, setAudioVolume] = useState(0.3)

  // Voice tool
  const [voiceText, setVoiceText] = useState('')
  const [voicePreset, setVoicePreset] = useState('Rachel')
  const [voiceVolume, setVoiceVolume] = useState(0.8)

  // SFX tool
  const [sfxDescription, setSfxDescription] = useState('')
  const [sfxDuration, setSfxDuration] = useState(5)
  const [sfxVolume, setSfxVolume] = useState(0.5)

  // Image gallery picker
  const [showImageGallery, setShowImageGallery] = useState(false)

  // Chain mode
  const [chainVideos, setChainVideos] = useState<GalleryVideo[]>([])
  const [chainTransitions, setChainTransitions] = useState(true)

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
  const totalCount: number = galleryData?.data?.total_count || galleryData?.data?.total || galleryData?.data?.count || videos.length

  // Image history for gallery picker
  const { data: imageHistoryData } = useQuery({
    queryKey: ['image-history-picker'],
    queryFn: () => contentApi.imageHistory({ limit: 40 }),
    enabled: showImageGallery,
  })
  const imageHistoryItems: ImageHistoryItem[] = imageHistoryData?.data?.images || imageHistoryData?.data?.results || []

  // Transcripts for selected video (polls while queued/running)
  const { data: transcriptsData } = useQuery({
    queryKey: ['video-transcripts', selectedVideo?.id],
    queryFn: () => contentApi.videoTranscripts(selectedVideo!.id),
    enabled: !!selectedVideo,
    refetchInterval: (query) => {
      const transcripts: TranscriptSummary[] = query.state.data?.data?.transcripts || []
      const hasPending = transcripts.some(t => t.status === 'queued' || t.status === 'running')
      return hasPending ? 3000 : false
    },
  })
  const transcripts: TranscriptSummary[] = transcriptsData?.data?.transcripts || []
  const latestTranscript = transcripts[0] || null

  // Resolve editVideo from gallery
  const editVideo = editVideoId ? videos.find(v => v.id === editVideoId) || null : null

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

  const uploadVideoMutation = useMutation({
    mutationFn: () => contentApi.uploadVideo(uploadFile!, uploadTitle || undefined),
    onSuccess: () => {
      refetchGallery()
      setUploadFile(null)
      setUploadTitle('')
      if (uploadInputRef.current) uploadInputRef.current.value = ''
      showFeedback('success', 'Video uploaded!')
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.error || 'Upload failed'
      showFeedback('error', msg)
    },
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

  const transcribeMutation = useMutation({
    mutationFn: (videoId: string) => contentApi.videoTranscribe(videoId),
    onSuccess: (resp) => {
      const msg = resp.data?.status === 'queued'
        ? `Transcription queued (ID: ${resp.data?.transcript_id?.slice(0, 8)}...)`
        : resp.data?.message || 'Transcription started'
      showFeedback('success', msg)
      queryClient.invalidateQueries({ queryKey: ['video-transcripts', selectedVideo?.id] })
    },
    onError: () => showFeedback('error', 'Failed to start transcription'),
  })

  const contentPackMutation = useMutation({
    mutationFn: (videoId: string) => contentApi.videoContentPack(videoId),
    onSuccess: () => {
      showFeedback('success', 'Content pack generation started')
      queryClient.invalidateQueries({ queryKey: ['video-transcripts', selectedVideo?.id] })
    },
    onError: (err: { response?: { data?: { error?: string } } }) => {
      const msg = err?.response?.data?.error || 'Failed to generate content pack'
      showFeedback('error', msg)
    },
  })

  const textOverlayMutation = useMutation({
    mutationFn: () => {
      if (!editVideoId) throw new Error('No video selected')
      return contentApi.addTextOverlay(editVideoId, overlayText, {
        position: overlayPosition,
        font_size: overlayFontSize,
        start_second: overlayStart,
        duration: overlayDuration,
      })
    },
    onSuccess: () => {
      refetchGallery()
      showFeedback('success', 'Text overlay applied!')
      setEditVideoId(null)
      setOverlayText('')
    },
    onError: () => showFeedback('error', 'Failed to apply text overlay'),
  })

  const colorGradingMutation = useMutation({
    mutationFn: () => {
      if (!editVideoId) throw new Error('No video selected')
      return contentApi.applyColorGrading(editVideoId, colorStyle)
    },
    onSuccess: () => {
      refetchGallery()
      showFeedback('success', 'Color grade applied!')
      setEditVideoId(null)
    },
    onError: () => showFeedback('error', 'Failed to apply color grade'),
  })

  const audioMutation = useMutation({
    mutationFn: () => {
      if (!editVideoId || !audioFile) throw new Error('No video or audio selected')
      return contentApi.addAudioToVideo(editVideoId, audioFile, audioVolume)
    },
    onSuccess: () => {
      refetchGallery()
      showFeedback('success', 'Audio added!')
      setEditVideoId(null)
      setAudioFile(null)
    },
    onError: () => showFeedback('error', 'Failed to add audio'),
  })

  const voiceoverMutation = useMutation({
    mutationFn: () => {
      if (!editVideoId || !voiceText.trim()) throw new Error('No video or text')
      return contentApi.addVoiceoverToVideo(editVideoId, voiceText, voicePreset, voiceVolume)
    },
    onSuccess: (res) => {
      refetchGallery()
      showFeedback('success', 'Voiceover added!')
      if (res.data?.video_url && selectedVideo) {
        setSelectedVideo({ ...selectedVideo, video_url: res.data.video_url })
      }
      setEditVideoId(null)
      setVoiceText('')
    },
    onError: () => showFeedback('error', 'Failed to add voiceover'),
  })

  const sfxMutation = useMutation({
    mutationFn: () => {
      if (!editVideoId || !sfxDescription.trim()) throw new Error('No video or description')
      return contentApi.addSfxToVideo(editVideoId, sfxDescription, sfxDuration, sfxVolume)
    },
    onSuccess: (res) => {
      refetchGallery()
      showFeedback('success', 'Sound effect added!')
      if (res.data?.video_url && selectedVideo) {
        setSelectedVideo({ ...selectedVideo, video_url: res.data.video_url })
      }
      setEditVideoId(null)
      setSfxDescription('')
    },
    onError: () => showFeedback('error', 'Failed to add sound effect'),
  })

  const chainMutation = useMutation({
    mutationFn: () => {
      const urls = chainVideos.map(v => getVideoUrl(v))
      return contentApi.chainVideos(urls, { add_transitions: chainTransitions })
    },
    onSuccess: () => {
      refetchGallery()
      showFeedback('success', 'Videos chained!')
      setChainVideos([])
    },
    onError: () => showFeedback('error', 'Failed to chain videos'),
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
    if (!getVideoUrl(video)) return
    contentApi.extendVideo(getVideoUrl(video), { prompt: video.prompt })
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
    if (!getVideoUrl(video)) return
    contentApi.upscaleVideo(getVideoUrl(video), video.prompt || '')
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
    window.open(getVideoUrl(video), '_blank')
  }

  const handleVideoClick = (video: GalleryVideo) => {
    if (studioMode === 'edit') {
      setEditVideoId(editVideoId === video.id ? null : video.id)
    } else if (studioMode === 'chain') {
      setChainVideos(prev => {
        const exists = prev.find(v => v.id === video.id)
        if (exists) return prev.filter(v => v.id !== video.id)
        return [...prev, video]
      })
    } else {
      setSelectedVideo(video)
      contentApi.incrementVideoView(video.id).catch(() => {})
    }
  }

  const moveChainVideo = (index: number, direction: 'up' | 'down') => {
    setChainVideos(prev => {
      const next = [...prev]
      const swapIdx = direction === 'up' ? index - 1 : index + 1
      if (swapIdx < 0 || swapIdx >= next.length) return prev
      ;[next[index], next[swapIdx]] = [next[swapIdx], next[index]]
      return next
    })
  }

  const isGenerating = textToVideoMutation.isPending || imageToVideoMutation.isPending
  const isChaining = chainMutation.isPending

  // ── Render ────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-dark-border px-6 py-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <Film className="text-primary-400" size={24} />
            <h1 className="text-xl font-bold text-white">Video Studio</h1>
          </div>
          {/* Mode tabs */}
          <div className="flex gap-1 bg-dark-bg rounded-lg p-0.5">
            {[
              { key: 'generate' as StudioMode, label: 'Generate', icon: Sparkles },
              { key: 'edit' as StudioMode, label: 'Edit', icon: Scissors },
              { key: 'chain' as StudioMode, label: 'Chain', icon: Link2 },
            ].map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setStudioMode(key)}
                className={cn(
                  'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-colors',
                  studioMode === key
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-400 hover:text-white'
                )}
              >
                <Icon size={13} />
                {label}
              </button>
            ))}
          </div>
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
        {/* ── Left Panel ──────────────────────────────────────────────── */}
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
            {studioMode === 'generate' ? 'Generate' : studioMode === 'edit' ? 'Edit' : 'Chain'}
            {generatePanelOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          <div className={cn('p-4 space-y-4', !generatePanelOpen && 'hidden lg:block')}>

            {/* ════════════════ GENERATE MODE ════════════════ */}
            {studioMode === 'generate' && (
              <>
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
                  <button
                    onClick={() => setMode('upload')}
                    className={cn(
                      'flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                      mode === 'upload'
                        ? 'border-primary-500 text-primary-400'
                        : 'border-transparent text-gray-500 hover:text-gray-300'
                    )}
                  >
                    <Upload size={14} />
                    Upload
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
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={imageUrl}
                          onChange={(e) => setImageUrl(e.target.value)}
                          placeholder="https://example.com/image.jpg"
                          className="flex-1 rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                        />
                        <button
                          onClick={() => setShowImageGallery(true)}
                          className="flex items-center gap-1.5 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-500 transition-colors flex-shrink-0"
                          title="Browse generated images"
                        >
                          <Grid size={14} />
                          Browse
                        </button>
                      </div>
                      {imageUrl && (
                        <div className="mt-2 rounded-lg overflow-hidden border border-dark-border bg-dark-bg">
                          <img
                            src={imageUrl}
                            alt="Selected"
                            className="w-full h-32 object-contain"
                            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                          />
                        </div>
                      )}
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

                {/* Upload inputs */}
                {mode === 'upload' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1.5">Video File</label>
                      <input
                        ref={uploadInputRef}
                        type="file"
                        accept="video/mp4,video/quicktime,video/webm,video/x-msvideo,video/x-matroska,.mp4,.mov,.webm,.avi,.mkv"
                        onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                        className="hidden"
                      />
                      <button
                        onClick={() => uploadInputRef.current?.click()}
                        className={cn(
                          'w-full rounded-lg border-2 border-dashed px-4 py-8 text-center transition-colors',
                          uploadFile
                            ? 'border-primary-500 bg-primary-500/5'
                            : 'border-dark-border hover:border-gray-500'
                        )}
                      >
                        {uploadFile ? (
                          <div className="space-y-1">
                            <Film size={24} className="mx-auto text-primary-400" />
                            <p className="text-sm text-white font-medium truncate">{uploadFile.name}</p>
                            <p className="text-xs text-gray-400">{(uploadFile.size / 1024 / 1024).toFixed(1)} MB</p>
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <Upload size={24} className="mx-auto text-gray-500" />
                            <p className="text-sm text-gray-400">Click to select a video file</p>
                            <p className="text-xs text-gray-500">MP4, MOV, WebM, AVI, MKV — max 50 MB</p>
                          </div>
                        )}
                      </button>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1.5">Title (optional)</label>
                      <input
                        type="text"
                        value={uploadTitle}
                        onChange={(e) => setUploadTitle(e.target.value)}
                        placeholder="Give your video a name..."
                        className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                      />
                    </div>
                    <button
                      onClick={() => uploadVideoMutation.mutate()}
                      disabled={!uploadFile || uploadVideoMutation.isPending}
                      className={cn(
                        'w-full rounded-lg py-2.5 text-sm font-medium transition-colors flex items-center justify-center gap-2',
                        uploadFile && !uploadVideoMutation.isPending
                          ? 'bg-primary-600 text-white hover:bg-primary-500'
                          : 'bg-dark-border text-gray-500 cursor-not-allowed'
                      )}
                    >
                      {uploadVideoMutation.isPending ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload size={16} />
                          Upload Video
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Generation options — hidden in upload mode */}
                {mode !== 'upload' && (<>
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
                </>)}

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
              </>
            )}

            {/* ════════════════ EDIT MODE ════════════════ */}
            {studioMode === 'edit' && (
              <>
                {/* Selected video */}
                <div>
                  <span className="text-xs text-gray-500">Selected Video</span>
                  {editVideo ? (
                    <div className="mt-1.5 flex items-center gap-3 rounded-lg border border-primary-500/50 bg-primary-500/5 p-2">
                      <div className="w-16 h-10 rounded overflow-hidden bg-dark-bg flex-shrink-0">
                        {editVideo.thumbnail_url ? (
                          <img src={editVideo.thumbnail_url} alt="" className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Film size={14} className="text-gray-700" />
                          </div>
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-gray-300 truncate">{editVideo.prompt || 'Video'}</p>
                        <p className="text-[10px] text-gray-500">
                          {editVideo.duration ? `${editVideo.duration}s` : ''}{editVideo.duration && editVideo.model ? ' \u00B7 ' : ''}{editVideo.model || ''}
                        </p>
                      </div>
                      <button onClick={() => setEditVideoId(null)} className="text-gray-500 hover:text-white flex-shrink-0">
                        <X size={14} />
                      </button>
                    </div>
                  ) : (
                    <p className="mt-1.5 text-sm text-gray-500 italic">Click a gallery video to select it</p>
                  )}
                </div>

                {/* Tool tabs */}
                <div className="flex flex-wrap border-b border-dark-border">
                  {[
                    { key: 'text' as const, label: 'Text', icon: Type },
                    { key: 'color' as const, label: 'Color', icon: Palette },
                    { key: 'audio' as const, label: 'Audio', icon: Music },
                    { key: 'voice' as const, label: 'Voice', icon: Mic },
                    { key: 'sfx' as const, label: 'SFX', icon: Volume2 },
                  ].map(({ key, label, icon: Icon }) => (
                    <button
                      key={key}
                      onClick={() => setEditTool(key)}
                      className={cn(
                        'flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
                        editTool === key
                          ? 'border-primary-500 text-primary-400'
                          : 'border-transparent text-gray-500 hover:text-gray-300'
                      )}
                    >
                      <Icon size={13} />
                      {label}
                    </button>
                  ))}
                </div>

                {/* ── Text Overlay Tool ── */}
                {editTool === 'text' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Text</label>
                      <textarea
                        value={overlayText}
                        onChange={(e) => setOverlayText(e.target.value)}
                        placeholder="Enter overlay text..."
                        rows={2}
                        disabled={!editVideoId}
                        className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none disabled:opacity-40"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Position</label>
                      <div className="flex gap-1.5">
                        {[
                          { value: 'upper_third', label: 'Top' },
                          { value: 'center', label: 'Center' },
                          { value: 'lower_third', label: 'Bottom' },
                        ].map((pos) => (
                          <button
                            key={pos.value}
                            onClick={() => setOverlayPosition(pos.value)}
                            disabled={!editVideoId}
                            className={cn(
                              'flex-1 rounded-lg border px-2 py-1.5 text-center text-xs transition-colors disabled:opacity-40',
                              overlayPosition === pos.value
                                ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                                : 'border-dark-border text-gray-400 hover:border-gray-600'
                            )}
                          >
                            {pos.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">
                        Font Size: {overlayFontSize}
                      </label>
                      <input
                        type="range"
                        min={36}
                        max={144}
                        value={overlayFontSize}
                        onChange={(e) => setOverlayFontSize(Number(e.target.value))}
                        disabled={!editVideoId}
                        className="w-full accent-primary-500 disabled:opacity-40"
                      />
                    </div>
                    <div className="flex gap-3">
                      <div className="flex-1">
                        <label className="block text-xs font-medium text-gray-400 mb-1">Start (s)</label>
                        <input
                          type="number"
                          min={0}
                          step={0.5}
                          value={overlayStart}
                          onChange={(e) => setOverlayStart(Number(e.target.value))}
                          disabled={!editVideoId}
                          className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-40"
                        />
                      </div>
                      <div className="flex-1">
                        <label className="block text-xs font-medium text-gray-400 mb-1">Duration (s)</label>
                        <input
                          type="number"
                          min={0.5}
                          step={0.5}
                          value={overlayDuration}
                          onChange={(e) => setOverlayDuration(Number(e.target.value))}
                          disabled={!editVideoId}
                          className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-40"
                        />
                      </div>
                    </div>
                    <button
                      onClick={() => textOverlayMutation.mutate()}
                      disabled={!editVideoId || !overlayText.trim() || textOverlayMutation.isPending}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                      {textOverlayMutation.isPending ? (
                        <><Loader2 size={14} className="animate-spin" /> Applying...</>
                      ) : (
                        <><Type size={14} /> Apply Text</>
                      )}
                    </button>
                  </div>
                )}

                {/* ── Color Grading Tool ── */}
                {editTool === 'color' && (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-1.5">
                      {COLOR_GRADE_OPTIONS.map((opt) => (
                        <button
                          key={opt.value}
                          onClick={() => setColorStyle(opt.value)}
                          disabled={!editVideoId}
                          className={cn(
                            'rounded-lg border px-2.5 py-2 text-left transition-colors disabled:opacity-40',
                            colorStyle === opt.value
                              ? 'border-primary-500 bg-primary-500/10'
                              : 'border-dark-border hover:border-gray-600'
                          )}
                        >
                          <div className={cn('text-xs font-medium', colorStyle === opt.value ? 'text-primary-300' : 'text-gray-300')}>
                            {opt.label}
                          </div>
                          <div className="text-[10px] text-gray-500">{opt.desc}</div>
                        </button>
                      ))}
                    </div>
                    <button
                      onClick={() => colorGradingMutation.mutate()}
                      disabled={!editVideoId || colorGradingMutation.isPending}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                      {colorGradingMutation.isPending ? (
                        <><Loader2 size={14} className="animate-spin" /> Applying...</>
                      ) : (
                        <><Palette size={14} /> Apply Grade</>
                      )}
                    </button>
                  </div>
                )}

                {/* ── Audio Tool ── */}
                {editTool === 'audio' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Audio File</label>
                      <label
                        className={cn(
                          'flex items-center gap-2 rounded-lg border border-dashed px-3 py-3 cursor-pointer transition-colors',
                          !editVideoId ? 'opacity-40 cursor-not-allowed' : 'border-dark-border hover:border-gray-500'
                        )}
                      >
                        <Upload size={16} className="text-gray-400" />
                        <span className="text-xs text-gray-400 truncate">
                          {audioFile ? audioFile.name : 'Choose audio file...'}
                        </span>
                        <input
                          type="file"
                          accept="audio/*"
                          onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                          disabled={!editVideoId}
                          className="hidden"
                        />
                      </label>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">
                        Volume: {Math.round(audioVolume * 100)}%
                      </label>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={audioVolume}
                        onChange={(e) => setAudioVolume(Number(e.target.value))}
                        disabled={!editVideoId}
                        className="w-full accent-primary-500 disabled:opacity-40"
                      />
                    </div>
                    <button
                      onClick={() => audioMutation.mutate()}
                      disabled={!editVideoId || !audioFile || audioMutation.isPending}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                      {audioMutation.isPending ? (
                        <><Loader2 size={14} className="animate-spin" /> Adding...</>
                      ) : (
                        <><Music size={14} /> Add Audio</>
                      )}
                    </button>
                  </div>
                )}

                {/* ── Voice Tool ── */}
                {editTool === 'voice' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Voiceover Script</label>
                      <textarea
                        value={voiceText}
                        onChange={(e) => setVoiceText(e.target.value)}
                        placeholder="Type the voiceover narration..."
                        rows={3}
                        disabled={!editVideoId}
                        className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none disabled:opacity-40"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Voice</label>
                      <div className="grid grid-cols-3 gap-1">
                        {VOICE_PRESETS.map((v) => (
                          <button
                            key={v}
                            onClick={() => setVoicePreset(v)}
                            disabled={!editVideoId}
                            className={cn(
                              'rounded-lg border px-2 py-1.5 text-xs transition-colors disabled:opacity-40',
                              voicePreset === v
                                ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                                : 'border-dark-border text-gray-400 hover:border-gray-600'
                            )}
                          >
                            {v}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">
                        Volume: {Math.round(voiceVolume * 100)}%
                      </label>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={voiceVolume}
                        onChange={(e) => setVoiceVolume(Number(e.target.value))}
                        disabled={!editVideoId}
                        className="w-full accent-primary-500 disabled:opacity-40"
                      />
                    </div>
                    <button
                      onClick={() => voiceoverMutation.mutate()}
                      disabled={!editVideoId || !voiceText.trim() || voiceoverMutation.isPending}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                      {voiceoverMutation.isPending ? (
                        <><Loader2 size={14} className="animate-spin" /> Generating...</>
                      ) : (
                        <><Mic size={14} /> Add Voiceover</>
                      )}
                    </button>
                  </div>
                )}

                {/* ── SFX Tool ── */}
                {editTool === 'sfx' && (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">Sound Description</label>
                      <input
                        type="text"
                        value={sfxDescription}
                        onChange={(e) => setSfxDescription(e.target.value)}
                        placeholder="e.g. thunderstorm, crowd cheering, ocean waves..."
                        disabled={!editVideoId}
                        className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-40"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">
                        Duration: {sfxDuration}s
                      </label>
                      <input
                        type="range"
                        min={0.5}
                        max={22}
                        step={0.5}
                        value={sfxDuration}
                        onChange={(e) => setSfxDuration(Number(e.target.value))}
                        disabled={!editVideoId}
                        className="w-full accent-primary-500 disabled:opacity-40"
                      />
                      <div className="flex justify-between text-[10px] text-gray-600">
                        <span>0.5s</span>
                        <span>22s</span>
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-400 mb-1">
                        Volume: {Math.round(sfxVolume * 100)}%
                      </label>
                      <input
                        type="range"
                        min={0}
                        max={1}
                        step={0.05}
                        value={sfxVolume}
                        onChange={(e) => setSfxVolume(Number(e.target.value))}
                        disabled={!editVideoId}
                        className="w-full accent-primary-500 disabled:opacity-40"
                      />
                    </div>
                    <button
                      onClick={() => sfxMutation.mutate()}
                      disabled={!editVideoId || !sfxDescription.trim() || sfxMutation.isPending}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2 text-sm font-medium text-white transition-colors"
                    >
                      {sfxMutation.isPending ? (
                        <><Loader2 size={14} className="animate-spin" /> Generating...</>
                      ) : (
                        <><Volume2 size={14} /> Add Sound Effect</>
                      )}
                    </button>
                  </div>
                )}
              </>
            )}

            {/* ════════════════ CHAIN MODE ════════════════ */}
            {studioMode === 'chain' && (
              <>
                <div>
                  <span className="text-xs text-gray-500">
                    Selected Videos ({chainVideos.length})
                  </span>
                  {chainVideos.length === 0 ? (
                    <p className="mt-1.5 text-sm text-gray-500 italic">Click gallery videos to add them to the chain</p>
                  ) : (
                    <div className="mt-1.5 space-y-1">
                      {chainVideos.map((video, idx) => (
                        <div
                          key={video.id}
                          className="flex items-center gap-2 rounded-lg border border-dark-border bg-dark-bg p-1.5"
                        >
                          <span className="w-5 h-5 rounded-full bg-primary-600 text-white text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                            {idx + 1}
                          </span>
                          <div className="w-12 h-7 rounded overflow-hidden bg-dark-card flex-shrink-0">
                            {video.thumbnail_url ? (
                              <img src={video.thumbnail_url} alt="" className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                <Film size={10} className="text-gray-700" />
                              </div>
                            )}
                          </div>
                          <span className="text-[10px] text-gray-400 truncate flex-1">
                            {video.prompt || 'Video'}
                          </span>
                          <div className="flex items-center gap-0.5 flex-shrink-0">
                            <button
                              onClick={() => moveChainVideo(idx, 'up')}
                              disabled={idx === 0}
                              className="p-0.5 text-gray-500 hover:text-white disabled:opacity-20"
                            >
                              <ArrowUp size={12} />
                            </button>
                            <button
                              onClick={() => moveChainVideo(idx, 'down')}
                              disabled={idx === chainVideos.length - 1}
                              className="p-0.5 text-gray-500 hover:text-white disabled:opacity-20"
                            >
                              <ArrowDown size={12} />
                            </button>
                            <button
                              onClick={() => setChainVideos(prev => prev.filter(v => v.id !== video.id))}
                              className="p-0.5 text-gray-500 hover:text-red-400"
                            >
                              <X size={12} />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={chainTransitions}
                    onChange={(e) => setChainTransitions(e.target.checked)}
                    className="rounded border-dark-border bg-dark-bg text-primary-500 focus:ring-primary-500 focus:ring-offset-0"
                  />
                  <span className="text-sm text-gray-300">Add transitions between clips</span>
                </label>

                <button
                  onClick={() => chainMutation.mutate()}
                  disabled={chainVideos.length < 2 || isChaining}
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-medium text-white transition-colors"
                >
                  {isChaining ? (
                    <><Loader2 size={16} className="animate-spin" /> Stitching...</>
                  ) : (
                    <><Link2 size={16} /> Stitch {chainVideos.length} Video{chainVideos.length !== 1 ? 's' : ''}</>
                  )}
                </button>
              </>
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

          {/* Hint for edit/chain mode */}
          {studioMode !== 'generate' && (
            <div className="px-4 py-2 bg-primary-500/5 border-b border-dark-border">
              <p className="text-xs text-primary-400">
                {studioMode === 'edit'
                  ? 'Click a video to select it for editing'
                  : 'Click videos to add them to the chain'}
              </p>
            </div>
          )}

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
                  {videos.map((video) => {
                    const isEditSelected = studioMode === 'edit' && editVideoId === video.id
                    const chainIndex = studioMode === 'chain'
                      ? chainVideos.findIndex(v => v.id === video.id)
                      : -1
                    const isChainSelected = chainIndex >= 0

                    return (
                      <button
                        key={video.id}
                        onClick={() => handleVideoClick(video)}
                        className={cn(
                          'group relative aspect-video rounded-lg overflow-hidden border transition-colors text-left',
                          isEditSelected
                            ? 'border-primary-400 ring-2 ring-primary-500/50'
                            : isChainSelected
                              ? 'border-primary-400 ring-2 ring-primary-500/50'
                              : 'border-dark-border hover:border-primary-500/50'
                        )}
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
                        {/* Play overlay (generate mode only) */}
                        {studioMode === 'generate' && (
                          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="w-12 h-12 rounded-full bg-black/60 flex items-center justify-center">
                              <Play size={20} className="text-white ml-0.5" />
                            </div>
                          </div>
                        )}
                        {/* Chain number badge */}
                        {isChainSelected && (
                          <div className="absolute top-1.5 left-1.5 w-6 h-6 rounded-full bg-primary-600 text-white text-xs font-bold flex items-center justify-center">
                            {chainIndex + 1}
                          </div>
                        )}
                        {/* Edit selected indicator */}
                        {isEditSelected && (
                          <div className="absolute top-1.5 left-1.5">
                            <div className="w-6 h-6 rounded-full bg-primary-600 text-white flex items-center justify-center">
                              <Check size={14} />
                            </div>
                          </div>
                        )}
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
                        {(video.model_used || video.model) && (
                          <span className="absolute top-1.5 right-1.5 text-[9px] bg-black/70 text-gray-400 px-1.5 py-0.5 rounded">
                            {video.model_used || video.model}
                          </span>
                        )}
                      </button>
                    )
                  })}
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

      {/* ── Image Gallery Picker Modal ───────────────────────────────── */}
      {showImageGallery && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowImageGallery(false)
          }}
        >
          <div className="bg-dark-card rounded-xl border border-dark-border max-w-3xl w-full max-h-[80vh] flex flex-col overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-dark-border">
              <h3 className="text-sm font-medium text-white">Select Image</h3>
              <button
                onClick={() => setShowImageGallery(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              {imageHistoryItems.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                  <Image size={40} className="mb-3 opacity-40" />
                  <p className="text-sm">No generated images yet</p>
                  <p className="text-xs text-gray-600 mt-1">Generate images in Image Studio first</p>
                </div>
              ) : (
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                  {imageHistoryItems.map((img) => {
                    const imgSrc = img.image_url || img.url
                    if (!imgSrc) return null
                    return (
                      <button
                        key={img.id}
                        onClick={() => {
                          setImageUrl(imgSrc)
                          setShowImageGallery(false)
                        }}
                        className="group relative aspect-square rounded-lg overflow-hidden border border-dark-border hover:border-primary-500 transition-colors"
                      >
                        <img
                          src={imgSrc}
                          alt={img.prompt || 'Generated image'}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors flex items-center justify-center">
                          <Check size={24} className="text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                        </div>
                        {img.prompt && (
                          <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/80 to-transparent p-1.5">
                            <span className="text-[9px] text-gray-300 line-clamp-2">{img.prompt}</span>
                          </div>
                        )}
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Video Detail Modal ────────────────────────────────────────── */}
      {selectedVideo && studioMode === 'generate' && (
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
                  src={getVideoUrl(selectedVideo)}
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

                {/* Transcript status */}
                {latestTranscript && (
                  <div className="rounded-lg border border-dark-border bg-dark-bg/50 p-3 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-400 flex items-center gap-1.5">
                        <FileText size={12} /> Transcript
                      </span>
                      <span className={cn(
                        'rounded-full px-2 py-0.5 text-[10px] font-medium',
                        latestTranscript.status === 'completed' && 'bg-green-500/10 text-green-400',
                        latestTranscript.status === 'running' && 'bg-blue-500/10 text-blue-400',
                        latestTranscript.status === 'queued' && 'bg-yellow-500/10 text-yellow-400',
                        latestTranscript.status === 'failed' && 'bg-red-500/10 text-red-400',
                      )}>
                        {latestTranscript.status === 'running' && <Loader2 size={10} className="inline animate-spin mr-1" />}
                        {latestTranscript.status}
                      </span>
                    </div>
                    {latestTranscript.status === 'completed' && (
                      <div className="space-y-1.5">
                        <div className="flex gap-3 text-[10px] text-gray-500">
                          <span>{latestTranscript.text_length.toLocaleString()} chars</span>
                          <span>{latestTranscript.segment_count} segments</span>
                          {latestTranscript.duration_seconds && (
                            <span>{Math.floor(latestTranscript.duration_seconds / 60)}:{String(Math.floor(latestTranscript.duration_seconds % 60)).padStart(2, '0')}</span>
                          )}
                        </div>
                        <button
                          onClick={() => window.open(`/api/v1/video/transcripts/${latestTranscript.id}/`, '_blank')}
                          className="flex items-center gap-1 text-[11px] text-primary-400 hover:text-primary-300 transition-colors"
                        >
                          <ExternalLink size={10} /> View full transcript
                        </button>
                      </div>
                    )}
                    {latestTranscript.status === 'failed' && latestTranscript.error && (
                      <p className="text-[11px] text-red-400">{latestTranscript.error}</p>
                    )}
                  </div>
                )}

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
                    onClick={() => transcribeMutation.mutate(selectedVideo.id)}
                    disabled={transcribeMutation.isPending || latestTranscript?.status === 'queued' || latestTranscript?.status === 'running'}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    {transcribeMutation.isPending || latestTranscript?.status === 'running' ? <Loader2 size={14} className="animate-spin" /> : <FileText size={14} />}
                    {latestTranscript?.status === 'completed' ? 'Re-transcribe' : latestTranscript?.status === 'running' ? 'Transcribing...' : latestTranscript?.status === 'queued' ? 'Queued...' : 'Transcribe'}
                  </button>

                  <button
                    onClick={() => contentPackMutation.mutate(selectedVideo.id)}
                    disabled={contentPackMutation.isPending || latestTranscript?.status !== 'completed'}
                    title={latestTranscript?.status !== 'completed' ? 'Transcribe first to generate a content pack' : undefined}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    {contentPackMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Package size={14} />}
                    Content Pack
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
