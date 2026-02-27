import type { InboxItemType, InboxSeverity } from '@/types/cockpit'
import type { Tone } from '@/components/cockpit/shared/StatusPill'

export const INBOX_TYPE_LABEL: Record<InboxItemType, string> = {
  decision: 'Decision',
  gate: 'Gate',
  error_signature: 'Error',
  failed_run: 'Failed Run',
}

export const INBOX_TYPE_TONE: Record<InboxItemType, Tone> = {
  decision: 'blue',
  gate: 'amber',
  error_signature: 'red',
  failed_run: 'red',
}

export const INBOX_SEVERITY_LABEL: Record<InboxSeverity, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

export const INBOX_SEVERITY_TONE: Record<InboxSeverity, Tone> = {
  critical: 'red',
  high: 'amber',
  medium: 'gray',
  low: 'gray',
}
