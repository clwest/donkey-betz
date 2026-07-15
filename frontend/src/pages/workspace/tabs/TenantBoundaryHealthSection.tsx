/**
 * S2794 — Tenant Boundary Health section for the System primary tab.
 *
 * Operator-facing readiness surface for the RUR-C1 (Real User Readiness
 * Campaign 1 — Tenant Boundary Lockdown) cross-tenant regression suite.
 * Reads the latest TenantBoundaryHealthReport from
 * /api/governance/tenant-boundary-health/ and renders:
 *
 *   - Advisory banner + Launch approval policy (F1 mitigation — this
 *     surface is not a launch gate; Chris ratification remains explicit).
 *   - Provenance strip: env / git SHA / runner / timestamp / elapsed
 *     (F3 mitigation — every green result traceable to a specific run).
 *   - Overall status pill: green / red / unknown (advisory colouring).
 *   - Coverage matrix: per-surface covered / partial / not_yet_covered
 *     with trailing notes (F2 mitigation — green suite ≠ platform safe).
 *   - Known gaps list (F2 mitigation, extension).
 *   - Failing test IDs when any (fold-back friendly).
 *
 * Explicit non-features (F1 mitigation, encoded in code shape):
 *   - No toggles. No "Enable Alpha" button. No status→flag auto-wire.
 *   - No secret exfiltration in stored artifact (backend responsibility;
 *     this component never displays secrets even if fields appear).
 */
import { useQuery } from '@tanstack/react-query'
import {
  Info,
  Loader2,
  ShieldCheck,
  Circle,
  AlertCircle,
  HelpCircle,
  Clock,
  GitCommit,
  Server,
  User,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// S2794 F2 mitigation: coverage status values recognized by the UI.
// Values may carry trailing parenthesized notes; head token is the enum.
type CoverageStatus = 'covered' | 'partial' | 'not_yet_covered'

interface LatestReport {
  id: string
  created_at: string
  env: string
  git_sha: string
  runner_identity: string
  elapsed_secs: number
  total_tests: number
  passed: number
  failed: number
  errored: number
  skipped: number
  failing_test_ids: string[]
  coverage_metadata: Record<string, string>
  overall_status: 'green' | 'red' | 'unknown'
}

interface TenantBoundaryHealthResponse {
  advisory: string
  is_gate: boolean
  policy: {
    launch_approval: string
    reason: string
  }
  latest_report: LatestReport | null
  coverage_metadata: Record<string, string>
  known_gaps: string[]
}

function coverageHead(status: string): CoverageStatus {
  const head = status.split(' ')[0]
  if (head === 'covered' || head === 'partial' || head === 'not_yet_covered') {
    return head
  }
  return 'not_yet_covered'
}

const COVERAGE_BADGE_CLASS: Record<CoverageStatus, string> = {
  // Non-severity palette — same discipline as ZoomOutLedgerSection
  // (S2780 V5 fold): no red/orange for advisory signals.
  covered: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
  partial: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
  not_yet_covered: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
}

const COVERAGE_LABEL: Record<CoverageStatus, string> = {
  covered: 'covered',
  partial: 'partial',
  not_yet_covered: 'not yet covered',
}

const STATUS_BADGE_CLASS: Record<'green' | 'red' | 'unknown', string> = {
  green: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40',
  red: 'bg-rose-500/15 text-rose-300 border-rose-500/40',
  unknown: 'bg-slate-500/15 text-slate-400 border-slate-500/40',
}

const STATUS_ICON: Record<'green' | 'red' | 'unknown', React.ComponentType<{ size?: number; className?: string }>> = {
  green: ShieldCheck,
  red: AlertCircle,
  unknown: HelpCircle,
}

function friendlySurface(key: string): string {
  return key.replace(/_/g, ' ')
}

function formatTimestamp(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso)
    return d.toISOString().replace('T', ' ').split('.')[0] + 'Z'
  } catch {
    return iso
  }
}

export function TenantBoundaryHealthSection() {
  const { data, isLoading, isError } = useQuery<TenantBoundaryHealthResponse | null>({
    queryKey: ['governance-tenant-boundary-health'],
    queryFn: async () => {
      try {
        const r = await api.get<TenantBoundaryHealthResponse>(
          '/governance/tenant-boundary-health/',
        )
        return r.data
      } catch {
        return null
      }
    },
    staleTime: 30_000,
  })

  const latest = data?.latest_report ?? null
  const overall = latest?.overall_status ?? 'unknown'
  const StatusIcon = STATUS_ICON[overall]

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-primary-400" size={18} />
          <h3 className="text-md font-semibold uppercase">
            Tenant Boundary Health
          </h3>
        </div>
        <div className="text-xs text-gray-500">
          RUR-C1 · Real User Readiness Campaign 1
        </div>
      </div>

      {/* F1 — Advisory banner. Repeat the "not a gate" language up top. */}
      <div className="mb-3 p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
        <div className="flex items-start gap-2">
          <Info size={14} className="text-amber-400 shrink-0 mt-0.5" aria-hidden />
          <div className="text-xs text-amber-200/90">
            <span className="font-semibold">
              {data?.advisory ?? 'Advisory signal — not a launch gate.'}
            </span>
          </div>
        </div>
      </div>

      {/* F1 — Explicit policy line — sits alongside overall status. */}
      {data?.policy && (
        <div className="mb-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
          <div className="text-xs text-gray-400">
            <span className="text-gray-500">Launch approval:</span>{' '}
            <span className="font-semibold text-gray-200">
              {data.policy.launch_approval}
            </span>
          </div>
          <div className="text-xs text-gray-500 mt-1">{data.policy.reason}</div>
        </div>
      )}

      {isLoading && (
        <div className="py-8 flex items-center justify-center text-gray-500">
          <Loader2 className="animate-spin" size={16} />
        </div>
      )}
      {isError && (
        <div className="py-4 text-sm text-red-400/80">
          Failed to load tenant boundary health. Retry on next refresh.
        </div>
      )}

      {data && !latest && (
        <div className="mb-3 p-3 rounded-lg bg-dark-bg border border-dark-border text-xs text-gray-400">
          No regression report on record yet. Run{' '}
          <code className="font-mono text-gray-200">
            python manage.py run_cross_tenant_regression --persist
          </code>{' '}
          to produce the first row.
        </div>
      )}

      {data && latest && (
        <>
          {/* Overall status + counts */}
          <div className="mb-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
            <div className="flex items-center gap-3 mb-2">
              <span
                className={cn(
                  'inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-xs font-semibold uppercase',
                  STATUS_BADGE_CLASS[overall],
                )}
              >
                <StatusIcon size={12} />
                {overall}
              </span>
              <span className="text-xs text-gray-500">
                {latest.total_tests} tests · {latest.passed} passed ·{' '}
                {latest.failed} failed · {latest.errored} errored ·{' '}
                {latest.skipped} skipped
              </span>
            </div>

            {/* F3 — Provenance strip: env / git SHA / runner / ts / elapsed */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-500">
              <div className="flex items-center gap-1.5">
                <Server size={11} className="text-gray-600" />
                <span className="text-gray-400 font-mono">{latest.env || '—'}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <GitCommit size={11} className="text-gray-600" />
                <span className="text-gray-400 font-mono">
                  {latest.git_sha ? latest.git_sha.slice(0, 8) : '—'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <User size={11} className="text-gray-600" />
                <span className="text-gray-400 font-mono">
                  {latest.runner_identity || '—'}
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <Clock size={11} className="text-gray-600" />
                <span className="text-gray-400 font-mono">
                  {formatTimestamp(latest.created_at)}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-600 mt-1">
              elapsed: {latest.elapsed_secs.toFixed(1)}s
            </div>
          </div>

          {/* Failing test IDs — only when there are any */}
          {latest.failing_test_ids.length > 0 && (
            <div className="mb-3 p-3 rounded-lg bg-rose-500/5 border border-rose-500/20">
              <div className="text-xs text-rose-300 font-semibold mb-2">
                Failing / errored tests ({latest.failing_test_ids.length})
              </div>
              <ul className="text-xs text-rose-200/80 space-y-1 max-h-40 overflow-y-auto font-mono">
                {latest.failing_test_ids.map((id) => (
                  <li key={id} className="break-all">{id}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {/* F2 — Coverage matrix (per-surface). Rendered whether or not
          there is a latest report — the coverage_metadata definition
          is source-of-truth from the service, not just from the report. */}
      {data && (
        <div className="mb-3">
          <div className="text-xs text-gray-500 mb-2">
            Coverage by surface (advisory — green suite ≠ platform safe)
          </div>
          <div className="space-y-1.5">
            {Object.entries(data.coverage_metadata).map(([surface, status]) => {
              const head = coverageHead(status)
              const badgeClass = COVERAGE_BADGE_CLASS[head]
              const note = status.includes(' ')
                ? status.slice(status.indexOf(' ') + 1)
                : null
              return (
                <div
                  key={surface}
                  className="flex items-center gap-2 text-xs"
                >
                  <span
                    className={cn(
                      'px-1.5 py-0.5 rounded border font-mono shrink-0',
                      badgeClass,
                    )}
                  >
                    {COVERAGE_LABEL[head]}
                  </span>
                  <span className="text-gray-300 font-mono">
                    {friendlySurface(surface)}
                  </span>
                  {note && (
                    <span className="text-gray-500 truncate">— {note}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* F2 — Known gaps: explicit list, "allowed to be ugly" per Rigby. */}
      {data && data.known_gaps.length > 0 && (
        <div className="mb-1 p-3 rounded-lg bg-slate-500/5 border border-slate-500/20">
          <div className="text-xs text-slate-300 font-semibold mb-2">
            Known gaps ({data.known_gaps.length})
          </div>
          <ul className="text-xs text-slate-300/80 space-y-1">
            {data.known_gaps.map((gap, i) => (
              <li key={i} className="flex items-start gap-2">
                <Circle size={8} className="text-slate-500 mt-1.5 shrink-0" />
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
