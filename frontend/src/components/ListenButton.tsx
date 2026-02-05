/**
 * Session 926: Universal Agent Voice System - Listen Button
 *
 * A reusable button that converts any text content to speech via ElevenLabs TTS.
 * Features:
 * - Automatic agent voice lookup
 * - Audio caching for cost savings
 * - Cost warning for long content (>2000 chars)
 * - Loading state with spinner
 * - Play/pause toggle
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import { Volume2, Square, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/cn'
import { ttsApi } from '@/lib/api'

interface ListenButtonProps {
  /** The text content to convert to speech */
  text: string
  /** Optional agent name for automatic voice selection */
  agentName?: string
  /** Optional explicit voice ID override */
  voiceId?: string
  /** Additional CSS classes */
  className?: string
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Show tooltip */
  showTooltip?: boolean
  /** Callback when audio starts playing */
  onPlay?: () => void
  /** Callback when audio stops */
  onStop?: () => void
  /** Callback on error */
  onError?: (error: string) => void
}

interface TTSResponse {
  success: boolean
  audio_url?: string
  audio_base64?: string
  cached?: boolean
  estimated_cost?: number
  duration_estimate?: number
  voice_name?: string
  error?: string
}

interface EstimateResponse {
  success: boolean
  text_length: number
  word_count: number
  estimated_cost: number
  estimated_duration: number
  needs_confirmation: boolean
}

type ButtonState = 'idle' | 'loading' | 'playing' | 'paused' | 'error'

const COST_WARNING_THRESHOLD = 2000 // chars

export function ListenButton({
  text,
  agentName,
  voiceId,
  className,
  size = 'sm',
  showTooltip = true,
  onPlay,
  onStop,
  onError,
}: ListenButtonProps) {
  const [state, setState] = useState<ButtonState>('idle')
  const [showCostWarning, setShowCostWarning] = useState(false)
  const [estimate, setEstimate] = useState<EstimateResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const audioUrlRef = useRef<string | null>(null)

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
      if (audioUrlRef.current?.startsWith('blob:')) {
        URL.revokeObjectURL(audioUrlRef.current)
      }
    }
  }, [])

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
    }
    setState('idle')
    onStop?.()
  }, [onStop])

  const generateAndPlay = useCallback(async () => {
    setState('loading')
    setErrorMessage(null)

    try {
      const response = await ttsApi.generate(text, agentName, voiceId)
      const data: TTSResponse = response.data

      if (!data.success) {
        throw new Error(data.error || 'TTS generation failed')
      }

      // Get audio URL
      let audioUrl: string
      if (data.audio_url) {
        audioUrl = data.audio_url
      } else if (data.audio_base64) {
        // Convert base64 to blob URL
        const binaryString = atob(data.audio_base64)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }
        const blob = new Blob([bytes], { type: 'audio/mpeg' })
        audioUrl = URL.createObjectURL(blob)
        audioUrlRef.current = audioUrl
      } else {
        throw new Error('No audio data in response')
      }

      // Create and play audio
      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.onplay = () => {
        setState('playing')
        onPlay?.()
      }

      audio.onpause = () => {
        if (audio.currentTime < audio.duration) {
          setState('paused')
        }
      }

      audio.onended = () => {
        setState('idle')
        onStop?.()
      }

      audio.onerror = () => {
        const err = 'Audio playback failed'
        setErrorMessage(err)
        setState('error')
        onError?.(err)
      }

      await audio.play()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to generate audio'
      setErrorMessage(message)
      setState('error')
      onError?.(message)
    }
  }, [text, agentName, voiceId, onPlay, onStop, onError])

  const handleClick = useCallback(async () => {
    // If currently playing, stop
    if (state === 'playing') {
      stopAudio()
      return
    }

    // If paused, resume
    if (state === 'paused' && audioRef.current) {
      audioRef.current.play()
      return
    }

    // Check if we need cost confirmation for long content
    if (text.length > COST_WARNING_THRESHOLD && !estimate) {
      try {
        const response = await ttsApi.estimate(text)
        const data: EstimateResponse = response.data
        if (data.needs_confirmation) {
          setEstimate(data)
          setShowCostWarning(true)
          return
        }
      } catch {
        // If estimate fails, proceed anyway
      }
    }

    // Generate and play
    await generateAndPlay()
  }, [state, text, estimate, stopAudio, generateAndPlay])

  const handleConfirmCost = useCallback(async () => {
    setShowCostWarning(false)
    await generateAndPlay()
  }, [generateAndPlay])

  const handleCancelCost = useCallback(() => {
    setShowCostWarning(false)
    setEstimate(null)
  }, [])

  // Size variants
  const sizeClasses = {
    sm: 'w-6 h-6 p-1',
    md: 'w-8 h-8 p-1.5',
    lg: 'w-10 h-10 p-2',
  }

  const iconSize = {
    sm: 14,
    md: 18,
    lg: 22,
  }

  // Render the appropriate icon
  const renderIcon = () => {
    switch (state) {
      case 'loading':
        return <Loader2 size={iconSize[size]} className="animate-spin" />
      case 'playing':
        return <Square size={iconSize[size]} className="fill-current" />
      case 'error':
        return <AlertCircle size={iconSize[size]} className="text-red-500" />
      default:
        return <Volume2 size={iconSize[size]} />
    }
  }

  // Tooltip text
  const tooltipText = {
    idle: 'Listen',
    loading: 'Generating audio...',
    playing: 'Stop',
    paused: 'Resume',
    error: errorMessage || 'Error',
  }

  return (
    <>
      <button
        onClick={handleClick}
        disabled={state === 'loading' || !text}
        title={showTooltip ? tooltipText[state] : undefined}
        className={cn(
          'inline-flex items-center justify-center rounded-md transition-colors',
          'hover:bg-muted focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          state === 'playing' && 'text-primary bg-primary/10',
          state === 'error' && 'text-red-500',
          sizeClasses[size],
          className
        )}
      >
        {renderIcon()}
      </button>

      {/* Cost Warning Modal */}
      {showCostWarning && estimate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-background border rounded-lg p-6 max-w-md mx-4 shadow-xl">
            <h3 className="text-lg font-semibold mb-2">Long Content Warning</h3>
            <p className="text-muted-foreground mb-4">
              This content is {estimate.text_length.toLocaleString()} characters
              ({estimate.word_count.toLocaleString()} words).
            </p>
            <div className="bg-muted rounded-md p-3 mb-4 text-sm">
              <div className="flex justify-between mb-1">
                <span>Estimated duration:</span>
                <span className="font-medium">
                  {Math.floor(estimate.estimated_duration / 60)}:
                  {String(Math.floor(estimate.estimated_duration % 60)).padStart(2, '0')}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Estimated cost:</span>
                <span className="font-medium">${estimate.estimated_cost.toFixed(3)}</span>
              </div>
            </div>
            <div className="flex gap-3 justify-end">
              <button
                onClick={handleCancelCost}
                className="px-4 py-2 rounded-md border hover:bg-muted transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmCost}
                className="px-4 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
              >
                Generate Audio
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

/**
 * ListenAllButton - For playing multiple messages in sequence (podcast-style)
 */
interface ListenAllButtonProps {
  messages: Array<{
    text: string
    agentName?: string
  }>
  className?: string
  onProgress?: (current: number, total: number) => void
}

export function ListenAllButton({ messages, className, onProgress }: ListenAllButtonProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const abortRef = useRef(false)

  const stopAll = useCallback(() => {
    abortRef.current = true
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setIsPlaying(false)
    setCurrentIndex(0)
    setIsLoading(false)
  }, [])

  const playAll = useCallback(async () => {
    if (messages.length === 0) return

    setIsPlaying(true)
    abortRef.current = false

    for (let i = 0; i < messages.length; i++) {
      if (abortRef.current) break

      setCurrentIndex(i)
      setIsLoading(true)
      onProgress?.(i + 1, messages.length)

      try {
        const { text, agentName } = messages[i]
        const response = await ttsApi.generate(text, agentName)
        const data: TTSResponse = response.data

        if (!data.success || abortRef.current) break

        setIsLoading(false)

        // Get audio URL
        let audioUrl: string
        if (data.audio_url) {
          audioUrl = data.audio_url
        } else if (data.audio_base64) {
          const binaryString = atob(data.audio_base64)
          const bytes = new Uint8Array(binaryString.length)
          for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i)
          }
          const blob = new Blob([bytes], { type: 'audio/mpeg' })
          audioUrl = URL.createObjectURL(blob)
        } else {
          continue
        }

        // Play and wait for completion
        await new Promise<void>((resolve) => {
          const audio = new Audio(audioUrl)
          audioRef.current = audio
          audio.onended = () => resolve()
          audio.onerror = () => resolve()
          audio.play().catch(() => resolve())
        })
      } catch {
        // Continue to next message on error
      }
    }

    setIsPlaying(false)
    setCurrentIndex(0)
    setIsLoading(false)
  }, [messages, onProgress])

  const handleClick = useCallback(() => {
    if (isPlaying) {
      stopAll()
    } else {
      playAll()
    }
  }, [isPlaying, stopAll, playAll])

  return (
    <button
      onClick={handleClick}
      disabled={messages.length === 0}
      title={isPlaying ? `Playing ${currentIndex + 1}/${messages.length}` : 'Listen to All'}
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm',
        'hover:bg-muted transition-colors',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        isPlaying && 'bg-primary/10 text-primary',
        className
      )}
    >
      {isLoading ? (
        <Loader2 size={16} className="animate-spin" />
      ) : isPlaying ? (
        <Square size={16} className="fill-current" />
      ) : (
        <Volume2 size={16} />
      )}
      <span>
        {isPlaying ? `${currentIndex + 1}/${messages.length}` : 'Listen to All'}
      </span>
    </button>
  )
}

export default ListenButton
