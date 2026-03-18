/**
 * Session 1077: Ops Console Tab (#7)
 * Surfaces SLO breaches, failure signatures, blocked agents, queue depth.
 * Replaces the generic System tab with actionable ops data.
 */

import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle, CheckCircle, XCircle, Loader2, Shield,
  Clock, Zap, Activity, Ban, TrendingDown,
} from 'lucide-react'
import { cn } from '@/lib/cn'

export function OpsConsoleTab() {
  // Fetch SLO status
  const sloQuery = useQuery({
    queryKey: ['ops-slo'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/ops/slo-status/', { credentials: 'include' })
        if (!r.ok) return null
        return r.json()
      } catch { return null }
    },
    staleTime: 60000,
  })

  // Fetch failure signatures
  const sigQuery = useQuery({
    queryKey: ['ops-signatures'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/ops/failure-signatures/?window=24h&limit=10', { credentials: 'include' })
        if (!r.ok) return null
        return r.json()
      } catch { return null }
    },
    staleTime: 60000,
  })

  // Fetch blocked agents
  const blockedQuery = useQuery({
    queryKey: ['ops-blocked'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/ops/blocked-agents/', { credentials: 'include' })
        if (!r.ok) return null
        return r.json()
      } catch { return null }
    },
    staleTime: 60000,
  })

  const slos = sloQuery.data?.slos || []
  const breaches = slos.filter((s: Record<string, boolean>) => s.breach)
  const signatures = sigQuery.data?.signatures || []
  const blocked = blockedQuery.data?.blocked || []
  const isLoading = sloQuery.isLoading

  return (
    <div className="space-y-6">
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
    </div>
  )
}
