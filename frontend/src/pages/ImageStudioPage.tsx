import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { contentApi } from '@/lib/api'
import {
  Image, Sparkles, Loader2, Heart, Download, ChevronDown, ChevronUp,
  Maximize2, Scissors, Copy, Trash2, X, Wand2, Check, AlertCircle,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// ── Style categories (from 69 backend presets) ──────────────────────────────

interface StyleCategory {
  name: string
  defaults: string[]
  extra: string[]
}

const STYLE_CATEGORIES: StyleCategory[] = [
  {
    name: 'Photography',
    defaults: ['photorealistic', 'portrait', 'landscape', 'black_white'],
    extra: ['macro', 'street', 'fashion', 'architectural', 'vintage'],
  },
  {
    name: 'Digital Art',
    defaults: ['digital_art', 'concept_art', 'matte_painting', 'vector'],
    extra: ['low_poly', 'voxel', 'isometric'],
  },
  {
    name: 'Traditional',
    defaults: ['oil_painting', 'watercolor', 'ink', 'pencil'],
    extra: ['acrylic', 'gouache', 'charcoal', 'pastel'],
  },
  {
    name: 'Animation',
    defaults: ['pixar', 'anime', 'ghibli', 'disney'],
    extra: ['dreamworks', 'comic', 'cartoon', 'manga', 'chibi', 'claymation', 'stop_motion', 'rotoscope', 'flash', 'silhouette'],
  },
  {
    name: 'Art Movements',
    defaults: ['impressionist', 'surreal', 'pop_art', 'art_deco'],
    extra: ['expressionist', 'abstract', 'cubist', 'art_nouveau', 'minimalist', 'baroque', 'renaissance'],
  },
  {
    name: 'Genre',
    defaults: ['fantasy', 'cyberpunk', 'steampunk', 'scifi'],
    extra: ['gothic', 'horror', 'retro', 'vaporwave'],
  },
  {
    name: 'Special',
    defaults: ['pixel_art', 'neon', 'stained_glass', 'psychedelic'],
    extra: ['3d_render', 'clay_render', 'wireframe', 'holographic', 'glitch', 'graffiti', 'collage', 'mosaic', 'origami', 'ukiyo_e', 'mandala', 'tribal', 'celtic', 'byzantine'],
  },
]

const QUALITY_OPTIONS = [
  { value: 'fast', label: 'Fast', desc: '~3s' },
  { value: 'balanced', label: 'Balanced', desc: '~6s' },
  { value: 'high', label: 'High', desc: '~9s' },
  { value: 'premium', label: 'Premium', desc: '~10s' },
]

const SIZE_OPTIONS = [
  { label: '1:1', width: 1024, height: 1024 },
  { label: '16:9', width: 1280, height: 720 },
  { label: '9:16', width: 720, height: 1280 },
  { label: '4:3', width: 1024, height: 768 },
]

function formatStyleLabel(style: string): string {
  return style.replace(/_/g, ' ').replace(/\b3d\b/g, '3D').replace(/\b\w/g, c => c.toUpperCase())
}

// ── Gallery item type ───────────────────────────────────────────────────────

interface GalleryImage {
  id: string
  url: string
  thumbnail_url?: string
  prompt?: string
  style?: string
  model?: string
  quality?: string
  width?: number
  height?: number
  is_favorite?: boolean
  image_type?: string
  created_at: string
}

// ── Action feedback ─────────────────────────────────────────────────────────

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

// ── Main Page ───────────────────────────────────────────────────────────────

export default function ImageStudioPage() {
  const queryClient = useQueryClient()

  // Generation form
  const [prompt, setPrompt] = useState('')
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null)
  const [quality, setQuality] = useState('balanced')
  const [width, setWidth] = useState(1024)
  const [height, setHeight] = useState(1024)
  const [negativePrompt, setNegativePrompt] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Gallery
  const [galleryFilter, setGalleryFilter] = useState('all')
  const [galleryOffset, setGalleryOffset] = useState(0)
  const [selectedImage, setSelectedImage] = useState<GalleryImage | null>(null)

  // Style picker
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)

  // Feedback
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [generatePanelOpen, setGeneratePanelOpen] = useState(true)

  // ── Queries ─────────────────────────────────────────────────────────────

  const { data: galleryData, isLoading: galleryLoading } = useQuery({
    queryKey: ['image-history', galleryFilter, galleryOffset],
    queryFn: () =>
      contentApi.imageHistory({
        ...(galleryFilter === 'favorites' ? { is_favorite: 'true' } : {}),
        ...(galleryFilter === 'edited' ? { image_type: 'upscaled_creative' } : {}),
        limit: 24,
        offset: galleryOffset,
      }),
  })

  const images: GalleryImage[] = galleryData?.data?.images || galleryData?.data?.results || []
  const totalCount: number = galleryData?.data?.total || galleryData?.data?.count || images.length

  // ── Mutations ───────────────────────────────────────────────────────────

  const refetchGallery = () => {
    queryClient.invalidateQueries({ queryKey: ['image-history'] })
  }

  const generateMutation = useMutation({
    mutationFn: () =>
      contentApi.generateImage(prompt, {
        style: selectedStyle || undefined,
        quality,
        width,
        height,
        negative_prompt: negativePrompt || undefined,
      }),
    onSuccess: () => {
      refetchGallery()
      setActionResult({ type: 'success', message: 'Image generated successfully!' })
      setTimeout(() => setActionResult(null), 3000)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate image' })
      setTimeout(() => setActionResult(null), 4000)
    },
  })

  const optimizeMutation = useMutation({
    mutationFn: () => contentApi.optimizePrompt(prompt),
    onSuccess: (res) => {
      const enhanced = res.data?.enhanced_prompt || res.data?.optimized_prompt || prompt
      setPrompt(enhanced)
      setActionResult({ type: 'success', message: 'Prompt optimized!' })
      setTimeout(() => setActionResult(null), 3000)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to optimize prompt' })
      setTimeout(() => setActionResult(null), 4000)
    },
  })

  const upscaleMutation = useMutation({
    mutationFn: (imageId: string) => contentApi.upscaleImage(imageId),
    onSuccess: () => {
      refetchGallery()
      setActionResult({ type: 'success', message: 'Image upscaled!' })
      setTimeout(() => setActionResult(null), 3000)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Upscale failed' })
      setTimeout(() => setActionResult(null), 4000)
    },
  })

  const removeBgMutation = useMutation({
    mutationFn: (imageId: string) => contentApi.removeBackground(imageId),
    onSuccess: () => {
      refetchGallery()
      setActionResult({ type: 'success', message: 'Background removed!' })
      setTimeout(() => setActionResult(null), 3000)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Remove background failed' })
      setTimeout(() => setActionResult(null), 4000)
    },
  })

  const variationsMutation = useMutation({
    mutationFn: (imageId: string) => contentApi.createVariations(imageId),
    onSuccess: () => {
      refetchGallery()
      setActionResult({ type: 'success', message: 'Variations created!' })
      setTimeout(() => setActionResult(null), 3000)
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Create variations failed' })
      setTimeout(() => setActionResult(null), 4000)
    },
  })

  const favoriteMutation = useMutation({
    mutationFn: (itemId: string) => contentApi.toggleFavorite(itemId),
    onSuccess: () => refetchGallery(),
  })

  const deleteMutation = useMutation({
    mutationFn: (imageId: string) => contentApi.deleteImage(imageId),
    onSuccess: () => {
      refetchGallery()
      setSelectedImage(null)
      setActionResult({ type: 'success', message: 'Image deleted' })
      setTimeout(() => setActionResult(null), 3000)
    },
  })

  // ── Handlers ────────────────────────────────────────────────────────────

  const handleGenerate = () => {
    if (!prompt.trim()) return
    generateMutation.mutate()
  }

  const handleSizeSelect = (w: number, h: number) => {
    setWidth(w)
    setHeight(h)
  }

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-dark-border px-6 py-4">
        <div className="flex items-center gap-3">
          <Image className="text-primary-400" size={24} />
          <h1 className="text-xl font-bold text-white">Image Studio</h1>
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
            'lg:w-1/3 xl:w-[360px] flex-shrink-0',
            !generatePanelOpen && 'lg:w-1/3'
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
            {/* Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Prompt</label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your image..."
                rows={4}
                className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none"
              />
              <button
                onClick={() => optimizeMutation.mutate()}
                disabled={!prompt.trim() || optimizeMutation.isPending}
                className="mt-1.5 flex items-center gap-1.5 text-xs text-primary-400 hover:text-primary-300 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {optimizeMutation.isPending ? (
                  <Loader2 size={12} className="animate-spin" />
                ) : (
                  <Wand2 size={12} />
                )}
                Optimize prompt
              </button>
            </div>

            {/* Style Picker */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Style</label>
              <div className="space-y-2">
                {STYLE_CATEGORIES.map((cat) => {
                  const isExpanded = expandedCategory === cat.name
                  const visibleStyles = isExpanded ? [...cat.defaults, ...cat.extra] : cat.defaults
                  return (
                    <div key={cat.name}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-500 uppercase tracking-wider">{cat.name}</span>
                        {cat.extra.length > 0 && (
                          <button
                            onClick={() => setExpandedCategory(isExpanded ? null : cat.name)}
                            className="text-[10px] text-gray-500 hover:text-gray-300"
                          >
                            {isExpanded ? 'Show less' : `+${cat.extra.length} more`}
                          </button>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {visibleStyles.map((style) => (
                          <button
                            key={style}
                            onClick={() => setSelectedStyle(selectedStyle === style ? null : style)}
                            className={cn(
                              'px-2 py-0.5 rounded-full text-xs border transition-colors',
                              selectedStyle === style
                                ? 'border-primary-500 bg-primary-500/20 text-primary-300'
                                : 'border-dark-border text-gray-400 hover:text-gray-200 hover:border-gray-600'
                            )}
                          >
                            {formatStyleLabel(style)}
                          </button>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
              {selectedStyle && (
                <button
                  onClick={() => setSelectedStyle(null)}
                  className="mt-2 text-xs text-gray-500 hover:text-gray-300"
                >
                  Clear style
                </button>
              )}
            </div>

            {/* Quality */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Quality</label>
              <div className="grid grid-cols-2 gap-2">
                {QUALITY_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setQuality(opt.value)}
                    className={cn(
                      'rounded-lg border px-3 py-2 text-left transition-colors',
                      quality === opt.value
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-dark-border hover:border-gray-600'
                    )}
                  >
                    <div className={cn('text-sm font-medium', quality === opt.value ? 'text-primary-300' : 'text-gray-300')}>
                      {opt.label}
                    </div>
                    <div className="text-[10px] text-gray-500">{opt.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Size */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">Size</label>
              <div className="flex gap-2">
                {SIZE_OPTIONS.map((opt) => (
                  <button
                    key={opt.label}
                    onClick={() => handleSizeSelect(opt.width, opt.height)}
                    className={cn(
                      'flex-1 rounded-lg border px-2 py-1.5 text-center text-xs transition-colors',
                      width === opt.width && height === opt.height
                        ? 'border-primary-500 bg-primary-500/10 text-primary-300'
                        : 'border-dark-border text-gray-400 hover:border-gray-600 hover:text-gray-200'
                    )}
                  >
                    {opt.label}
                    <div className="text-[10px] text-gray-600">{opt.width}x{opt.height}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Advanced */}
            <div>
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300"
              >
                {showAdvanced ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                Advanced options
              </button>
              {showAdvanced && (
                <div className="mt-2">
                  <label className="block text-xs text-gray-500 mb-1">Negative prompt</label>
                  <textarea
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="What to exclude..."
                    rows={2}
                    className="w-full rounded-lg bg-dark-bg border border-dark-border px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-primary-500 resize-none"
                  />
                </div>
              )}
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!prompt.trim() || generateMutation.isPending}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-primary-600 hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed px-4 py-2.5 text-sm font-medium text-white transition-colors"
            >
              {generateMutation.isPending ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  Generate Image
                </>
              )}
            </button>
          </div>
        </div>

        {/* ── Gallery Panel (right) ──────────────────────────────────── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Filter bar */}
          <div className="flex items-center gap-2 px-4 py-3 border-b border-dark-border">
            {['all', 'favorites', 'edited'].map((filter) => (
              <button
                key={filter}
                onClick={() => {
                  setGalleryFilter(filter)
                  setGalleryOffset(0)
                }}
                className={cn(
                  'px-3 py-1 rounded-full text-xs font-medium capitalize transition-colors',
                  galleryFilter === filter
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-bg text-gray-400 hover:text-white'
                )}
              >
                {filter}
              </button>
            ))}
            <span className="ml-auto text-xs text-gray-500">
              {totalCount} image{totalCount !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Grid */}
          <div className="flex-1 overflow-y-auto p-4">
            {galleryLoading ? (
              <div className="flex items-center justify-center h-48">
                <Loader2 className="animate-spin text-gray-500" size={24} />
              </div>
            ) : images.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-48 text-gray-500">
                <Image size={40} className="mb-3 opacity-40" />
                <p className="text-sm">
                  {galleryFilter === 'all'
                    ? 'Generate your first image'
                    : `No ${galleryFilter} images`}
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
                  {images.map((img) => (
                    <button
                      key={img.id}
                      onClick={() => setSelectedImage(img)}
                      className="group relative aspect-square rounded-lg overflow-hidden border border-dark-border hover:border-primary-500/50 transition-colors"
                    >
                      <img
                        src={img.thumbnail_url || img.url}
                        alt={img.prompt || 'Generated image'}
                        className="w-full h-full object-cover"
                        loading="lazy"
                      />
                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-2">
                        <div className="flex justify-between items-start">
                          {img.style && (
                            <span className="text-[10px] bg-dark-bg/80 text-gray-300 px-1.5 py-0.5 rounded">
                              {formatStyleLabel(img.style)}
                            </span>
                          )}
                          {img.is_favorite && <Heart size={12} className="text-red-400 fill-red-400" />}
                        </div>
                        {img.prompt && (
                          <p className="text-[10px] text-gray-300 line-clamp-2">{img.prompt}</p>
                        )}
                      </div>
                      {/* Quality badge */}
                      {img.quality && (
                        <span className="absolute top-1 right-1 text-[9px] bg-black/70 text-gray-400 px-1 py-0.5 rounded">
                          {img.quality}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                {/* Load more */}
                {images.length < totalCount && (
                  <div className="flex justify-center mt-4">
                    <button
                      onClick={() => setGalleryOffset((prev) => prev + 24)}
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

      {/* ── Image Detail Modal ────────────────────────────────────────── */}
      {selectedImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) setSelectedImage(null)
          }}
        >
          <div className="bg-dark-card rounded-xl border border-dark-border max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">
            {/* Modal header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-dark-border">
              <h3 className="text-sm font-medium text-white truncate">Image Detail</h3>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-gray-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {/* Modal body */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col lg:flex-row gap-4">
              {/* Image */}
              <div className="lg:flex-1 flex items-center justify-center">
                <img
                  src={selectedImage.url}
                  alt={selectedImage.prompt || 'Generated image'}
                  className="max-h-[60vh] rounded-lg object-contain"
                />
              </div>

              {/* Info + actions */}
              <div className="lg:w-64 space-y-4 flex-shrink-0">
                {/* Metadata */}
                {selectedImage.prompt && (
                  <div>
                    <span className="text-xs text-gray-500">Prompt</span>
                    <p className="text-sm text-gray-300 mt-0.5">{selectedImage.prompt}</p>
                  </div>
                )}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {selectedImage.style && (
                    <div>
                      <span className="text-gray-500">Style</span>
                      <p className="text-gray-300">{formatStyleLabel(selectedImage.style)}</p>
                    </div>
                  )}
                  {selectedImage.quality && (
                    <div>
                      <span className="text-gray-500">Quality</span>
                      <p className="text-gray-300 capitalize">{selectedImage.quality}</p>
                    </div>
                  )}
                  {selectedImage.width && selectedImage.height && (
                    <div>
                      <span className="text-gray-500">Size</span>
                      <p className="text-gray-300">{selectedImage.width}x{selectedImage.height}</p>
                    </div>
                  )}
                  {selectedImage.created_at && (
                    <div>
                      <span className="text-gray-500">Created</span>
                      <p className="text-gray-300">{new Date(selectedImage.created_at).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>

                {/* Action buttons */}
                <div className="space-y-1.5">
                  <span className="text-xs text-gray-500">Actions</span>

                  <button
                    onClick={() => upscaleMutation.mutate(selectedImage.id)}
                    disabled={upscaleMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    {upscaleMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Maximize2 size={14} />}
                    Upscale
                  </button>

                  <button
                    onClick={() => removeBgMutation.mutate(selectedImage.id)}
                    disabled={removeBgMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    {removeBgMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Scissors size={14} />}
                    Remove Background
                  </button>

                  <button
                    onClick={() => variationsMutation.mutate(selectedImage.id)}
                    disabled={variationsMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    {variationsMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Copy size={14} />}
                    Create Variations
                  </button>

                  <button
                    onClick={() => window.open(selectedImage.url, '_blank')}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 transition-colors"
                  >
                    <Download size={14} />
                    Download
                  </button>

                  <button
                    onClick={() => favoriteMutation.mutate(selectedImage.id)}
                    disabled={favoriteMutation.isPending}
                    className="w-full flex items-center gap-2 rounded-lg border border-dark-border px-3 py-2 text-sm text-gray-300 hover:text-white hover:border-gray-600 disabled:opacity-40 transition-colors"
                  >
                    <Heart size={14} className={selectedImage.is_favorite ? 'text-red-400 fill-red-400' : ''} />
                    {selectedImage.is_favorite ? 'Unfavorite' : 'Favorite'}
                  </button>

                  <button
                    onClick={() => {
                      if (confirm('Delete this image?')) {
                        deleteMutation.mutate(selectedImage.id)
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
