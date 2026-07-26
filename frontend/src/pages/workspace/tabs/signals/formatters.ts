/**
 * S2971: Shared formatters for the Signals sub-tab.
 *
 * Times display in America/Denver (MST/MDT) per spec §6 Step 6 —
 * Chris is Mountain time.
 */

const MST_FORMATTER = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/Denver',
  year: 'numeric',
  month: 'short',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

const MST_TIME_ONLY = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/Denver',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

export function formatMST(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return MST_FORMATTER.format(new Date(iso))
  } catch {
    return iso
  }
}

export function formatMSTTimeOnly(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return MST_TIME_ONLY.format(new Date(iso))
  } catch {
    return iso
  }
}

export function formatRelative(iso: string | null | undefined): string {
  if (!iso) return '—'
  const ts = new Date(iso).getTime()
  const now = Date.now()
  const diffMs = now - ts
  if (diffMs < 0) return 'just now'
  const seconds = Math.floor(diffMs / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function formatConfidence(value: number | null | undefined): string {
  if (value == null) return '—'
  return `${Math.round(value * 100)}%`
}

export function formatNumber(value: number | null | undefined): string {
  if (value == null) return '—'
  return value.toLocaleString('en-US')
}
