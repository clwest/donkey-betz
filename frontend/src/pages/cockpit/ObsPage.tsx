import { useState, useEffect, useCallback } from 'react'
import {
  getObsHealth,
  getObsStatus,
  postObsStart,
  postObsStop,
  getObsLast,
  postObsUpload,
  type ObsResponse,
} from '@/lib/cockpitApi'
import { Video, Circle, Square, Upload, RefreshCw, Wifi, WifiOff, Clock, HardDrive, AlertTriangle, ExternalLink, Copy, Check } from 'lucide-react'
import { Link } from 'react-router-dom'

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`
}

export default function CockpitObsPage() {
  const [health, setHealth] = useState<ObsResponse | null>(null)
  const [status, setStatus] = useState<ObsResponse | null>(null)
  const [last, setLast] = useState<ObsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<string | null>(null)
  const [uploadTitle, setUploadTitle] = useState('')
  const [uploadTags, setUploadTags] = useState('')
  const [stopBeforeUpload, setStopBeforeUpload] = useState(true)
  const [uploadResult, setUploadResult] = useState<ObsResponse | null>(null)
  const [copied, setCopied] = useState<string | null>(null)

  const isRecording = status?.result?.isRecording === true
  const bridgeReachable = status?.bridgeReachable ?? health?.bridgeReachable ?? false

  const fetchStatus = useCallback(async () => {
    try {
      const data = await getObsStatus()
      setStatus(data)
      if (!data.ok && data.error) setError(`${data.error.code}: ${data.error.message}`)
      else setError(null)
    } catch {
      setError('Failed to reach platform')
    }
  }, [])

  const fetchHealth = useCallback(async () => {
    try {
      const data = await getObsHealth()
      setHealth(data)
    } catch { /* status will show errors */ }
  }, [])

  const fetchLast = useCallback(async () => {
    setLoading('last')
    try {
      const data = await getObsLast()
      setLast(data)
      if (!data.ok && data.error) setError(`${data.error.code}: ${data.error.message}`)
    } catch {
      setError('Failed to fetch last recording')
    } finally {
      setLoading(null)
    }
  }, [])

  // Poll status
  useEffect(() => {
    fetchHealth()
    fetchStatus()
    const interval = setInterval(fetchStatus, isRecording ? 2000 : 5000)
    return () => clearInterval(interval)
  }, [fetchHealth, fetchStatus, isRecording])

  const handleStart = async () => {
    setLoading('start')
    setError(null)
    try {
      const data = await postObsStart()
      if (!data.ok && data.error) setError(`${data.error.code}: ${data.error.message}`)
      await fetchStatus()
    } catch {
      setError('Failed to start recording')
    } finally {
      setLoading(null)
    }
  }

  const handleStop = async () => {
    setLoading('stop')
    setError(null)
    try {
      const data = await postObsStop()
      if (!data.ok && data.error) setError(`${data.error.code}: ${data.error.message}`)
      // Wait for file to settle, then refresh
      setTimeout(async () => {
        await fetchStatus()
        await fetchLast()
        setLoading(null)
      }, 2000)
    } catch {
      setError('Failed to stop recording')
      setLoading(null)
    }
  }

  const handleUpload = async () => {
    setLoading('upload')
    setError(null)
    setUploadResult(null)
    try {
      const body: { title?: string; tags?: string[]; stopIfRecording?: boolean } = {}
      if (uploadTitle.trim()) body.title = uploadTitle.trim()
      if (uploadTags.trim()) body.tags = uploadTags.split(',').map(t => t.trim()).filter(Boolean)
      if (stopBeforeUpload) body.stopIfRecording = true

      const data = await postObsUpload(body)
      setUploadResult(data)
      if (!data.ok && data.error) setError(`${data.error.code}: ${data.error.message}`)
      else {
        await fetchStatus()
        await fetchLast()
      }
    } catch {
      setError('Upload failed')
    } finally {
      setLoading(null)
    }
  }

  const result = status?.result as Record<string, unknown> | undefined
  const lastFile = last?.result as Record<string, unknown> | undefined
  const fileInfo = lastFile?.file as Record<string, unknown> | undefined

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Video size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">OBS Studio</h1>
        {bridgeReachable ? (
          <span className="flex items-center gap-1 rounded-full bg-green-500/10 px-2.5 py-0.5 text-xs font-medium text-green-400">
            <Wifi size={12} /> Connected
          </span>
        ) : (
          <span className="flex items-center gap-1 rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-medium text-red-400">
            <WifiOff size={12} /> Disconnected
          </span>
        )}
        {status?.latency_ms != null && (
          <span className="text-xs text-gray-500">{status.latency_ms}ms</span>
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-4 py-3 text-sm text-red-400">
          <AlertTriangle size={16} />
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recording Status */}
        <div className="card p-6 space-y-4">
          <h2 className="text-sm font-medium text-gray-400 flex items-center gap-1.5">
            <Clock size={14} /> Recording Status
          </h2>

          <div className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-600'}`} />
            <span className="text-lg font-semibold text-white">
              {isRecording ? 'Recording' : 'Stopped'}
            </span>
            {result?.recordingTimecode && (
              <span className="font-mono text-sm text-gray-400">{String(result.recordingTimecode)}</span>
            )}
          </div>

          {result?.obsVersion && (
            <p className="text-xs text-gray-500">
              OBS {String(result.obsVersion)} / WebSocket {String(result.websocketVersion)}
            </p>
          )}

          <div className="flex gap-2 pt-2">
            <button
              onClick={handleStart}
              disabled={isRecording || loading === 'start'}
              className="flex items-center gap-1.5 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-500 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Circle size={14} /> {loading === 'start' ? 'Starting...' : 'Start'}
            </button>
            <button
              onClick={handleStop}
              disabled={!isRecording || loading === 'stop'}
              className="flex items-center gap-1.5 rounded-lg bg-gray-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-gray-500 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Square size={14} /> {loading === 'stop' ? 'Stopping...' : 'Stop'}
            </button>
            <button
              onClick={fetchStatus}
              className="flex items-center gap-1.5 rounded-lg bg-dark-border px-3 py-2 text-sm text-gray-400 transition-colors hover:text-white"
            >
              <RefreshCw size={14} />
            </button>
          </div>
        </div>

        {/* Last Recording */}
        <div className="card p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-gray-400 flex items-center gap-1.5">
              <HardDrive size={14} /> Last Recording
            </h2>
            <button
              onClick={fetchLast}
              disabled={loading === 'last'}
              className="flex items-center gap-1.5 rounded-lg bg-dark-border px-3 py-1.5 text-xs text-gray-400 transition-colors hover:text-white disabled:opacity-40"
            >
              <RefreshCw size={12} /> {loading === 'last' ? 'Scanning...' : 'Scan'}
            </button>
          </div>

          {fileInfo ? (
            <div className="space-y-2">
              <p className="font-mono text-sm text-white truncate" title={String(fileInfo.path)}>
                {String(fileInfo.filename)}
              </p>
              <div className="flex gap-4 text-xs text-gray-500">
                <span>{formatBytes(Number(fileInfo.sizeBytes))}</span>
                <span>{String(fileInfo.ext)}</span>
                <span>{new Date(String(fileInfo.mtime)).toLocaleString()}</span>
              </div>
            </div>
          ) : last?.ok === true ? (
            <p className="text-sm text-gray-500">No recordings found</p>
          ) : !last ? (
            <p className="text-sm text-gray-500">Click Scan to check</p>
          ) : null}
        </div>
      </div>

      {/* Upload */}
      <div className="card p-6 space-y-4">
        <h2 className="text-sm font-medium text-gray-400 flex items-center gap-1.5">
          <Upload size={14} /> Upload to Platform
        </h2>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs text-gray-500">Title (optional)</label>
            <input
              type="text"
              value={uploadTitle}
              onChange={(e) => setUploadTitle(e.target.value)}
              placeholder="My recording"
              className="w-full rounded-lg border border-dark-border bg-dark-bg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-gray-500">Tags (comma-separated)</label>
            <input
              type="text"
              value={uploadTags}
              onChange={(e) => setUploadTags(e.target.value)}
              placeholder="obs, recording"
              className="w-full rounded-lg border border-dark-border bg-dark-bg px-3 py-2 text-sm text-white placeholder-gray-600 focus:border-primary-500 focus:outline-none"
            />
          </div>
          <div className="flex items-end">
            <label className="flex items-center gap-2 text-sm text-gray-300 cursor-pointer">
              <input
                type="checkbox"
                checked={stopBeforeUpload}
                onChange={(e) => setStopBeforeUpload(e.target.checked)}
                className="rounded border-dark-border bg-dark-bg"
              />
              Stop if recording
            </label>
          </div>
          <div className="flex items-end">
            <button
              onClick={handleUpload}
              disabled={loading === 'upload'}
              className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-500 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Upload size={14} /> {loading === 'upload' ? 'Uploading...' : 'Upload Last'}
            </button>
          </div>
        </div>

        {uploadResult?.ok && uploadResult.result && (() => {
          const r = uploadResult.result as Record<string, unknown>
          const video = (r?.video ?? r?.media) as Record<string, unknown> | undefined
          const videoId = video?.id ? String(video.id) : null
          const videoUrl = video?.url ? String(video.url) : null
          const seqNum = video?.sequential_number
          const resolution = video?.resolution ? String(video.resolution) : null
          const duration = video?.duration ? Number(video.duration) : null

          const copyToClipboard = (text: string, label: string) => {
            navigator.clipboard.writeText(text)
            setCopied(label)
            setTimeout(() => setCopied(null), 2000)
          }

          return (
            <div className="rounded-lg border border-green-500/20 bg-green-500/5 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-green-400">Upload successful!</span>
                <Link
                  to="/video-studio"
                  className="flex items-center gap-1.5 rounded-lg bg-primary-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-primary-500"
                >
                  <ExternalLink size={12} /> View in Video Studio
                </Link>
              </div>

              <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs text-gray-400">
                {seqNum != null && <span>Video <span className="text-white font-mono">#{String(seqNum)}</span></span>}
                {resolution && <span>{resolution}</span>}
                {duration != null && <span>{Math.floor(duration / 60)}:{String(duration % 60).padStart(2, '0')}</span>}
              </div>

              <div className="flex flex-wrap gap-2">
                {videoId && (
                  <button
                    onClick={() => copyToClipboard(videoId, 'id')}
                    className="flex items-center gap-1 rounded bg-dark-border px-2 py-1 text-xs text-gray-400 hover:text-white transition-colors"
                  >
                    {copied === 'id' ? <Check size={10} className="text-green-400" /> : <Copy size={10} />}
                    ID: <span className="font-mono">{videoId.slice(0, 8)}...</span>
                  </button>
                )}
                {videoUrl && (
                  <button
                    onClick={() => copyToClipboard(videoUrl, 'url')}
                    className="flex items-center gap-1 rounded bg-dark-border px-2 py-1 text-xs text-gray-400 hover:text-white transition-colors"
                  >
                    {copied === 'url' ? <Check size={10} className="text-green-400" /> : <Copy size={10} />}
                    Copy URL
                  </button>
                )}
              </div>
            </div>
          )
        })()}
      </div>
    </div>
  )
}
