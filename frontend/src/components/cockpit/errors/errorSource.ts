import type { FailureSourceType } from '@/types/cockpit'
import type { Tone } from '@/components/cockpit/shared/StatusPill'

export const ERROR_SOURCE_LABEL: Record<FailureSourceType, string> = {
  agent: 'Agent',
  celery: 'Celery',
}

export const ERROR_SOURCE_TONE: Record<FailureSourceType, Tone> = {
  agent: 'blue',
  celery: 'amber',
}
