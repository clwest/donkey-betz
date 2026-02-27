import type { RunStatus } from '@/types/cockpit'
import type { Tone } from '@/components/cockpit/shared/StatusPill'

export const RUN_STATUS_LABEL: Record<RunStatus, string> = {
  pending: 'Pending',
  in_progress: 'Running',
  completed: 'Completed',
  failed: 'Failed',
}

export const RUN_STATUS_TONE: Record<RunStatus, Tone> = {
  pending: 'gray',
  in_progress: 'blue',
  completed: 'green',
  failed: 'red',
}
