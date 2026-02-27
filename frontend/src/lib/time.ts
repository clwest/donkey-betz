const SECOND = 1000
const MINUTE = 60 * SECOND
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

/**
 * "5m ago", "2h ago", "3d ago"
 */
export function formatRelative(iso: string, now = new Date()): string {
  const diff = now.getTime() - new Date(iso).getTime()
  if (diff < MINUTE) return 'just now'
  if (diff < HOUR) return `${Math.floor(diff / MINUTE)}m ago`
  if (diff < DAY) return `${Math.floor(diff / HOUR)}h ago`
  return `${Math.floor(diff / DAY)}d ago`
}

/**
 * "Feb 26, 10:30"
 */
export function formatDateTime(iso: string): string {
  const d = new Date(iso)
  const month = d.toLocaleString('en-US', { month: 'short' })
  const day = d.getDate()
  const hours = d.getHours().toString().padStart(2, '0')
  const mins = d.getMinutes().toString().padStart(2, '0')
  return `${month} ${day}, ${hours}:${mins}`
}

/**
 * 45200 → "45.2s", 125000 → "2m 05s"
 */
export function formatDurationMs(ms?: number | null): string {
  if (ms == null) return '—'
  if (ms < MINUTE) return `${(ms / SECOND).toFixed(1)}s`
  const m = Math.floor(ms / MINUTE)
  const s = Math.floor((ms % MINUTE) / SECOND)
  return `${m}m ${s.toString().padStart(2, '0')}s`
}
