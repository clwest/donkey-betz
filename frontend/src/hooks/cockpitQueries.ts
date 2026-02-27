import { useQuery } from '@tanstack/react-query'
import {
  getRuns,
  getRunDetail,
  getErrorSummary,
  getInbox,
  getJobStatus,
  getMedia,
  getDeliverables,
  getOpsOverview,
  type RunsParams,
  type InboxParams,
  type MediaParams,
  type DeliverableParams,
  type OpsParams,
} from '@/lib/cockpitApi'

export function useRuns(params?: RunsParams) {
  return useQuery({
    queryKey: ['cockpit-runs', params],
    queryFn: () => getRuns(params),
    refetchInterval: 15_000,
  })
}

export function useRunDetail(runId: string | undefined) {
  return useQuery({
    queryKey: ['cockpit-run', runId],
    queryFn: () => getRunDetail(runId!),
    enabled: !!runId,
  })
}

export function useErrorSummary(hours = 24) {
  return useQuery({
    queryKey: ['cockpit-errors', hours],
    queryFn: () => getErrorSummary(hours),
    refetchInterval: 30_000,
  })
}

export function useInbox(params?: InboxParams) {
  return useQuery({
    queryKey: ['cockpit-inbox', params],
    queryFn: () => getInbox(params),
    refetchInterval: 20_000,
  })
}

export function useJobStatus(jobId: string | undefined) {
  return useQuery({
    queryKey: ['cockpit-job-status', jobId],
    queryFn: () => getJobStatus(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (status === 'completed' || status === 'failed' || status === 'cancelled') return false
      return 3_000
    },
  })
}

export function useMedia(params?: MediaParams) {
  return useQuery({
    queryKey: ['cockpit-media', params],
    queryFn: () => getMedia(params),
    enabled: !!params,
  })
}

export function useDeliverables(params?: DeliverableParams) {
  return useQuery({
    queryKey: ['cockpit-deliverables', params],
    queryFn: () => getDeliverables(params),
    enabled: !!params,
  })
}

export function useOpsOverview(params?: OpsParams) {
  return useQuery({
    queryKey: ['cockpit-ops', params],
    queryFn: () => getOpsOverview(params),
    refetchInterval: 30_000,
  })
}
