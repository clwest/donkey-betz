/**
 * Session 1077: Ops Console Tab (#7)
 * Surfaces SLO breaches, failure signatures, blocked agents, queue depth.
 * Replaces the generic System tab with actionable ops data.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle, CheckCircle, XCircle, Loader2, Shield,
  Clock, Zap, Activity, Ban, TrendingDown, Layers, Copy, Check,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface OpsHealthSummary {
  window: string
  verdict: 'FRESH' | 'STALE_DAPHNE' | 'STALE_CELERY' | 'STALE_BOTH' | 'UNKNOWN'
  head_commit_sha_short: string
  tenant_boundary_violations: {
    total: number
    by_task_name: Record<string, number>
    by_failure_kind: Record<string, number>
  }
  staleness_warnings: {
    total: number
    by_verdict: Record<string, number>
  }
  slo_status: {
    total: number
    breach_count: number
    healthy_count: number
    worst_breach: {
      key: string | null
      name: string | null
      current: number
      target: number
    } | null
  }
}

interface CloseCeremonyItem {
  session_number: number
  title: string
  date: string | null
  handoff_path: string
  envelope_path: string | null
  envelope_exists: boolean
}

interface CloseCeremonyLedger {
  items: CloseCeremonyItem[]
  count: number
  limit: number
}

export function OpsConsoleTab() {
  // S2761: unified health summary — freshness verdict + I-0303 tenant
  // boundary violation counts + S2759 staleness warning counts. Wraps the
  // three S2755→S2760 diagnostic surfaces into one always-visible tile.
  // S2762: sibling SLO/failure/blocked queries below now share this
  // `api.get` pattern (raw fetch omitted the Authorization token → 401).
  const healthQuery = useQuery<OpsHealthSummary | null>({
    queryKey: ['ops-health-summary'],
    queryFn: async () => {
      try {
        const r = await api.get<OpsHealthSummary>('/ops/health-summary/')
        return r.data
      } catch { return null }
    },
    refetchInterval: 30000,
  })

  const sloQuery = useQuery({
    queryKey: ['ops-slo'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/slo-status/')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  const sigQuery = useQuery({
    queryKey: ['ops-signatures'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/failure-signatures/?window=24h&limit=10')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  const blockedQuery = useQuery({
    queryKey: ['ops-blocked'],
    queryFn: async () => {
      try {
        const r = await api.get('/ops/blocked-agents/')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })

  // S2763: close-ceremony ledger — last 10 handoffs paired with envelopes.
  // Filesystem-backed (docs/handoffs/ + docs/research/implementation/), no
  // data model. Read-only operator surface for fast context re-load.
  const ledgerQuery = useQuery<CloseCeremonyLedger | null>({
    queryKey: ['ops-close-ceremony-ledger'],
    queryFn: async () => {
      try {
        const r = await api.get<CloseCeremonyLedger>('/ops/close-ceremony-ledger/?limit=10')
        return r.data
      } catch { return null }
    },
    staleTime: 60000,
  })
  const [copiedPath, setCopiedPath] = useState<string | null>(null)
  const copyPath = async (path: string) => {
    try {
      await navigator.clipboard.writeText(path)
      setCopiedPath(path)
      setTimeout(() => setCopiedPath(null), 1500)
    } catch { /* clipboard unavailable — no-op */ }
  }

  const slos = sloQuery.data?.slos || []
  const breaches = slos.filter((s: Record<string, boolean>) => s.breach)
  const signatures = sigQuery.data?.signatures || []
  const blocked = blockedQuery.data?.blocked || []
  const isLoading = sloQuery.isLoading

  const opsHealth = healthQuery.data

  return (
    <div className="space-y-6">
      {/* S2761: Ops Health tile — verdict + I-0303 + S2759 counts */}
      {opsHealth && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Activity size={14} />
            Ops Health (24h)
            <span
              className={cn(
                'ml-2 h-1.5 w-1.5 rounded-full',
                opsHealth.verdict === 'FRESH' && 'bg-green-400',
                opsHealth.verdict === 'UNKNOWN' && 'bg-gray-500',
                opsHealth.verdict !== 'FRESH' && opsHealth.verdict !== 'UNKNOWN' && 'bg-red-400',
              )}
            />
            <span className={cn(
              'text-xs font-medium',
              opsHealth.verdict === 'FRESH' ? 'text-green-400' :
              opsHealth.verdict === 'UNKNOWN' ? 'text-gray-400' : 'text-red-400'
            )}>{opsHealth.verdict}</span>
            {opsHealth.head_commit_sha_short && (
              <code className="text-xs text-gray-500 ml-1">{opsHealth.head_commit_sha_short.slice(0, 7)}</code>
            )}
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.tenant_boundary_violations.total > 0
                ? 'border-amber-500/30 bg-amber-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Shield size={14} className={opsHealth.tenant_boundary_violations.total > 0 ? 'text-amber-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">Tenant Boundary Violations</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.tenant_boundary_violations.total > 0 ? 'text-amber-400' : 'text-green-400'
              )}>
                {opsHealth.tenant_boundary_violations.total}
              </p>
              {opsHealth.tenant_boundary_violations.total > 0 && (
                <div className="mt-2 space-y-0.5">
                  {Object.entries(opsHealth.tenant_boundary_violations.by_failure_kind).slice(0, 4).map(([kind, count]) => (
                    <div key={kind} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500 truncate">{kind}</span>
                      <span className="text-gray-400 ml-2">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.staleness_warnings.total > 0
                ? 'border-red-500/30 bg-red-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Clock size={14} className={opsHealth.staleness_warnings.total > 0 ? 'text-red-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">Staleness Warnings</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.staleness_warnings.total > 0 ? 'text-red-400' : 'text-green-400'
              )}>
                {opsHealth.staleness_warnings.total}
              </p>
              {opsHealth.staleness_warnings.total > 0 && (
                <div className="mt-2 space-y-0.5">
                  {Object.entries(opsHealth.staleness_warnings.by_verdict).slice(0, 4).map(([v, count]) => (
                    <div key={v} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500 truncate">{v}</span>
                      <span className="text-gray-400 ml-2">{count}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {/* S2764: SLO Status tile card — 3rd tile per N1 */}
            <div className={cn(
              'p-3 rounded-lg border',
              opsHealth.slo_status.breach_count > 0
                ? 'border-red-500/30 bg-red-500/5'
                : 'border-dark-border bg-dark-card'
            )}>
              <div className="flex items-center gap-2 mb-1">
                <Zap size={14} className={opsHealth.slo_status.breach_count > 0 ? 'text-red-400' : 'text-green-400'} />
                <span className="text-xs text-gray-400">SLO Breaches</span>
              </div>
              <p className={cn(
                'text-lg font-bold',
                opsHealth.slo_status.breach_count > 0 ? 'text-red-400' : 'text-green-400'
              )}>
                {opsHealth.slo_status.breach_count}
                <span className="text-sm font-normal text-gray-500 ml-1">/ {opsHealth.slo_status.total}</span>
              </p>
              {opsHealth.slo_status.worst_breach && (
                <div className="mt-2 space-y-0.5">
                  <div className="text-xs text-gray-400 truncate" title={opsHealth.slo_status.worst_breach.name ?? ''}>
                    {opsHealth.slo_status.worst_breach.name}
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">current</span>
                    <span className="text-red-400 font-mono">
                      {opsHealth.slo_status.worst_breach.current < 1
                        ? `${(opsHealth.slo_status.worst_breach.current * 100).toFixed(2)}%`
                        : opsHealth.slo_status.worst_breach.current.toFixed(0)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">target</span>
                    <span className="text-gray-400 font-mono">
                      {opsHealth.slo_status.worst_breach.target < 1
                        ? `${(opsHealth.slo_status.worst_breach.target * 100).toFixed(2)}%`
                        : opsHealth.slo_status.worst_breach.target.toFixed(0)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SLO Overview */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
          <Activity size={14} />
          SLO Status (24h)
        </h3>
        {isLoading ? (
          <div className="flex justify-center py-8"><Loader2 size={20} className="animate-spin text-primary-400" /></div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {slos.map((slo: Record<string, string | number | boolean>) => (
              <div
                key={slo.key as string}
                className={cn(
                  'p-3 rounded-lg border',
                  slo.breach ? 'border-red-500/30 bg-red-500/5' : 'border-dark-border bg-dark-card'
                )}
              >
                <div className="flex items-center gap-2 mb-1">
                  {slo.breach ? <XCircle size={14} className="text-red-400" /> : <CheckCircle size={14} className="text-green-400" />}
                  <span className="text-xs text-gray-400 truncate">{slo.name as string}</span>
                </div>
                <p className={cn('text-lg font-bold', slo.breach ? 'text-red-400' : 'text-green-400')}>
                  {typeof slo.current === 'number' ? (slo.current as number > 1 ? (slo.current as number).toFixed(0) : `${((slo.current as number) * 100).toFixed(1)}%`) : slo.current}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Breaches */}
      {breaches.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
            <AlertTriangle size={14} />
            SLO Breaches ({breaches.length})
          </h3>
          <div className="space-y-2">
            {breaches.map((b: Record<string, string | number>) => (
              <div key={b.key as string} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                <p className="text-sm text-white">{b.name as string}</p>
                <p className="text-xs text-red-300 mt-1">
                  Current: {typeof b.current === 'number' && (b.current as number) < 1 ? `${((b.current as number) * 100).toFixed(2)}%` : b.current}
                  {b.target !== undefined && ` (target: ${typeof b.target === 'number' && (b.target as number) < 1 ? `${((b.target as number) * 100).toFixed(1)}%` : b.target})`}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Failure Signatures */}
      {signatures.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <TrendingDown size={14} />
            Failure Signatures (24h)
          </h3>
          <div className="space-y-2">
            {signatures.map((sig: Record<string, string | number>, i: number) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-dark-card border border-dark-border">
                <AlertTriangle size={14} className="text-orange-400 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{sig.signature as string}</p>
                  <p className="text-xs text-gray-500">{sig.description as string}</p>
                </div>
                <span className="text-xs text-gray-400">x{sig.total_count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Blocked Agents */}
      {blocked.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Ban size={14} />
            Blocked Agents ({blocked.length})
          </h3>
          <div className="space-y-2">
            {blocked.map((agent: Record<string, string>, i: number) => (
              <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-dark-card border border-dark-border">
                <Shield size={14} className="text-red-400" />
                <div className="flex-1">
                  <p className="text-sm text-white">{agent.agent_name}</p>
                  <p className="text-xs text-gray-500">{agent.reason}</p>
                </div>
                {agent.ttl_hours && (
                  <span className="text-xs text-gray-400">{agent.ttl_hours}h TTL</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {!isLoading && breaches.length === 0 && signatures.length === 0 && blocked.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <CheckCircle size={32} className="mx-auto mb-2 opacity-50" />
          <p className="text-sm">All systems healthy. No breaches, failures, or blocked agents.</p>
        </div>
      )}

      {/* S2763: Close-Ceremony Ledger */}
      {ledgerQuery.data && ledgerQuery.data.items.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Layers size={14} />
            Recent Close-Ceremonies (last {ledgerQuery.data.count})
          </h3>
          <div className="space-y-2">
            {ledgerQuery.data.items.map((item) => (
              <div key={item.session_number} className="p-3 rounded-lg bg-dark-card border border-dark-border">
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-medium text-primary-400 shrink-0">
                    S{item.session_number}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate">{item.title}</p>
                    <div className="flex items-center gap-2 mt-0.5 text-xs">
                      {item.date && <span className="text-gray-500">{item.date}</span>}
                      <span
                        className={cn(
                          'px-1.5 py-0.5 rounded font-medium',
                          item.envelope_exists
                            ? 'bg-green-500/10 text-green-400'
                            : 'bg-gray-500/10 text-gray-400',
                        )}
                      >
                        {item.envelope_exists ? 'envelope' : 'handoff-only'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="mt-2 space-y-1">
                  <button
                    onClick={() => copyPath(item.handoff_path)}
                    className="w-full flex items-center gap-2 text-xs text-left px-2 py-1 rounded bg-dark-bg hover:bg-dark-border transition-colors group"
                    title="Copy handoff path"
                  >
                    {copiedPath === item.handoff_path ? (
                      <Check size={11} className="text-green-400 shrink-0" />
                    ) : (
                      <Copy size={11} className="text-gray-500 shrink-0 group-hover:text-gray-300" />
                    )}
                    <code className="text-gray-400 truncate flex-1">{item.handoff_path}</code>
                  </button>
                  {item.envelope_path && (
                    <button
                      onClick={() => copyPath(item.envelope_path!)}
                      className="w-full flex items-center gap-2 text-xs text-left px-2 py-1 rounded bg-dark-bg hover:bg-dark-border transition-colors group"
                      title="Copy envelope path"
                    >
                      {copiedPath === item.envelope_path ? (
                        <Check size={11} className="text-green-400 shrink-0" />
                      ) : (
                        <Copy size={11} className="text-gray-500 shrink-0 group-hover:text-gray-300" />
                      )}
                      <code className="text-gray-400 truncate flex-1">{item.envelope_path}</code>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
