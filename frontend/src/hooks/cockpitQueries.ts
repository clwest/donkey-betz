import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getRuns,
  getRunDetail,
  getErrorSummary,
  getInbox,
  getJobStatus,
  getMedia,
  getDeliverables,
  getOpsOverview,
  getAlerts,
  retryRun,
  createIncidentNote,
  getApprovals,
  decideApproval,
  getAuditLog,
  type RunsParams,
  type InboxParams,
  type MediaParams,
  type DeliverableParams,
  type OpsParams,
  type AlertsParams,
  type ApprovalsParams,
  type AuditLogParams,
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

export function useAlerts(params?: AlertsParams) {
  return useQuery({
    queryKey: ['cockpit-alerts', params],
    queryFn: () => getAlerts(params),
    refetchInterval: 30_000,
  })
}

export function useRetryRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (runId: string) => retryRun(runId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cockpit-runs'] })
      qc.invalidateQueries({ queryKey: ['cockpit-alerts'] })
    },
  })
}

export function useCreateIncidentNote() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: { title: string; detail?: string; source_type?: string; source_id?: string }) =>
      createIncidentNote(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cockpit-deliverables'] })
    },
  })
}

export function useApprovals(params?: ApprovalsParams) {
  return useQuery({
    queryKey: ['cockpit-approvals', params],
    queryFn: () => getApprovals(params),
    refetchInterval: 20_000,
  })
}

export function useAuditLog(params?: AuditLogParams) {
  return useQuery({
    queryKey: ['cockpit-audit', params],
    queryFn: () => getAuditLog(params),
    refetchInterval: 30_000,
  })
}

export function useDecideApproval() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (vars: { kind: 'decision' | 'gate'; id: string; payload: Record<string, string> }) =>
      decideApproval(vars.kind, vars.id, vars.payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['cockpit-approvals'] })
      qc.invalidateQueries({ queryKey: ['cockpit-inbox'] })
    },
  })
}
