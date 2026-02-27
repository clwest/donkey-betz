import { useQuery } from '@tanstack/react-query'
import {
  getRuns,
  getRunDetail,
  getErrorSummary,
  getMedia,
  getDeliverables,
  getHealthOverview,
  type RunsParams,
  type MediaParams,
  type DeliverableParams,
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

export function useMedia(params?: MediaParams) {
  return useQuery({
    queryKey: ['cockpit-media', params],
    queryFn: () => getMedia(params),
  })
}

export function useDeliverables(params?: DeliverableParams) {
  return useQuery({
    queryKey: ['cockpit-deliverables', params],
    queryFn: () => getDeliverables(params),
  })
}

export function useHealthOverview() {
  return useQuery({
    queryKey: ['cockpit-health'],
    queryFn: getHealthOverview,
    refetchInterval: 30_000,
  })
}
