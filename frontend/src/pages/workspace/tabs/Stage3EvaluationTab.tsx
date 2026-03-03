// Stage 3 Evaluation Dashboard — Capitalize Opportunity Initiative
// Tracks ATR-24h (Action-Taken Rate within 24 hours) for synthesis outputs
// during the 14-day pilot (Mar 4–18, 2026).

import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  Target,
  Clock,
  Eye,
  TrendingUp,
  Users,
  AlertTriangle,
  ArrowDown,
  Loader2,
  RefreshCw,
  ShieldCheck,
  XCircle,
  Minus,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// ── Types ──────────────────────────────────────────────────────────

interface HeadlineKPIs {
  total_syntheses: number
  atr_24h: number
  median_hours_to_action: number | null
  viewed_rate: number
}

interface FunnelStep {
  step: string
  count: number
  pct: number
}

interface RoleRow {
  role: string
  syntheses: number
  viewed: number
  saved_exported_shared: number
  acted_24h: number
  atr_24h: number
  median_hours: number | null
}

interface AgentRow {
  agent: string
  syntheses: number
  acted_24h: number
  atr_24h: number
}

interface GateInfo {
  status: 'APPROVED' | 'CONDITIONAL' | 'FAILED' | 'IN_PROGRESS' | 'NO_DATA'
  details: {
    atr_overall?: number
    atr_target?: number
    roles_below_15?: string[]
    total_syntheses?: number
  }
}

interface DashboardData {
  headline: HeadlineKPIs
  funnel: FunnelStep[]
  by_role: RoleRow[]
  top_agents: AgentRow[]
  gate: GateInfo
}

// ── Component ──────────────────────────────────────────────────────

export function Stage3EvaluationTab() {
  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['stage3-dashboard'],
    queryFn: async () => {
      const res = await api.get('/deliverables/stage3-dashboard/')
      return res.data.dashboard as DashboardData
    },
    refetchInterval: 30_000,
    staleTime: 15_000,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-primary-400 mr-3" size={24} />
        <span className="text-gray-400">Loading Stage 3 dashboard...</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-20 gap-3">
        <XCircle className="text-accent-red" size={32} />
        <p className="text-gray-400">Failed to load dashboard</p>
        <p className="text-xs text-gray-500">{String(error)}</p>
        <button onClick={() => refetch()} className="text-xs text-primary-400 hover:underline">
          Retry
        </button>
      </div>
    )
  }

  if (!data) return null

  const { headline, funnel, by_role, top_agents, gate } = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <BarChart3 size={20} className="text-primary-400" />
            Stage 3 Evaluation Dashboard
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Capitalize Opportunity — 14-day pilot (Mar 4–18)
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-white px-3 py-1.5 rounded-md hover:bg-dark-border/50 transition-colors"
        >
          <RefreshCw size={13} />
          Refresh
        </button>
      </div>

      {/* Gate Status Banner */}
      <GateBanner gate={gate} />

      {/* Panel A — Headline KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <KPICard
          label="Syntheses Generated"
          value={headline.total_syntheses}
          icon={BarChart3}
          color="#6366f1"
        />
        <KPICard
          label="ATR-24h"
          value={`${headline.atr_24h}%`}
          icon={Target}
          color={headline.atr_24h >= 25 ? '#22c55e' : headline.atr_24h >= 15 ? '#eab308' : '#ef4444'}
          subtitle={`Target: 25%`}
        />
        <KPICard
          label="Median Hrs to Action"
          value={headline.median_hours_to_action !== null ? `${headline.median_hours_to_action}h` : '--'}
          icon={Clock}
          color="#f59e0b"
        />
        <KPICard
          label="Viewed Rate"
          value={`${headline.viewed_rate}%`}
          icon={Eye}
          color="#8b5cf6"
        />
      </div>

      {/* ATR by Role mini-cards */}
      {by_role.length > 0 && (
        <div className="grid grid-cols-3 gap-3">
          {by_role
            .filter(r => r.role !== 'unknown')
            .map(r => (
              <RoleMiniCard key={r.role} role={r} />
            ))}
        </div>
      )}

      {/* Panels B, C, D in a responsive grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Panel B — Funnel */}
        <div className="bg-[#1a1a1a] rounded-lg border border-[#333] p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <ArrowDown size={14} className="text-primary-400" />
            Engagement Funnel
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-[#333]">
                <th className="text-left py-2 font-medium">Step</th>
                <th className="text-right py-2 font-medium">Count</th>
                <th className="text-right py-2 font-medium">% of Total</th>
              </tr>
            </thead>
            <tbody>
              {funnel.map((step) => (
                <tr key={step.step} className="border-b border-[#222]">
                  <td className="py-2.5 text-gray-300">{step.step}</td>
                  <td className="py-2.5 text-right font-mono text-gray-200">{step.count}</td>
                  <td className="py-2.5 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-16 h-1.5 bg-[#333] rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full bg-primary-400"
                          style={{ width: `${step.pct}%` }}
                        />
                      </div>
                      <span className="text-gray-400 font-mono w-12 text-right">{step.pct}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Panel C — Role Breakdown */}
        <div className="bg-[#1a1a1a] rounded-lg border border-[#333] p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <Users size={14} className="text-primary-400" />
            Role Breakdown
          </h3>
          {by_role.length === 0 ? (
            <p className="text-xs text-gray-500 py-4 text-center">No role data yet</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 border-b border-[#333]">
                  <th className="text-left py-2 font-medium">Role</th>
                  <th className="text-right py-2 font-medium">Synth</th>
                  <th className="text-right py-2 font-medium">Viewed</th>
                  <th className="text-right py-2 font-medium">Saved</th>
                  <th className="text-right py-2 font-medium">Acted</th>
                  <th className="text-right py-2 font-medium">ATR</th>
                </tr>
              </thead>
              <tbody>
                {by_role.map(r => (
                  <tr key={r.role} className="border-b border-[#222]">
                    <td className="py-2.5 capitalize text-gray-300">{r.role}</td>
                    <td className="py-2.5 text-right font-mono text-gray-200">{r.syntheses}</td>
                    <td className="py-2.5 text-right font-mono text-gray-400">{r.viewed}</td>
                    <td className="py-2.5 text-right font-mono text-gray-400">{r.saved_exported_shared}</td>
                    <td className="py-2.5 text-right font-mono text-gray-200">{r.acted_24h}</td>
                    <td className="py-2.5 text-right">
                      <ATRBadge value={r.atr_24h} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Panel D — Top Agents */}
      {top_agents.length > 0 && (
        <div className="bg-[#1a1a1a] rounded-lg border border-[#333] p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
            <TrendingUp size={14} className="text-primary-400" />
            Top Agents by ATR-24h
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-[#333]">
                <th className="text-left py-2 font-medium">Agent</th>
                <th className="text-right py-2 font-medium">Syntheses</th>
                <th className="text-right py-2 font-medium">Acted (24h)</th>
                <th className="text-right py-2 font-medium">ATR-24h</th>
              </tr>
            </thead>
            <tbody>
              {top_agents.map((a, i) => (
                <tr key={a.agent} className="border-b border-[#222]">
                  <td className="py-2.5 text-gray-300">
                    <span className="text-xs text-gray-500 mr-2">{i + 1}.</span>
                    {a.agent}
                  </td>
                  <td className="py-2.5 text-right font-mono text-gray-200">{a.syntheses}</td>
                  <td className="py-2.5 text-right font-mono text-gray-200">{a.acted_24h}</td>
                  <td className="py-2.5 text-right">
                    <ATRBadge value={a.atr_24h} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

// ── Sub-components ─────────────────────────────────────────────────

function KPICard({
  label,
  value,
  icon: Icon,
  color,
  subtitle,
}: {
  label: string
  value: string | number
  icon: React.ElementType
  color: string
  subtitle?: string
}) {
  return (
    <div className="bg-[#1a1a1a] rounded-lg border border-[#333] p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-gray-500">{label}</p>
          <p className="text-2xl font-bold mt-1" style={{ color }}>
            {value}
          </p>
          {subtitle && <p className="text-[10px] text-gray-600 mt-0.5">{subtitle}</p>}
        </div>
        <div
          className="h-10 w-10 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}18` }}
        >
          <Icon size={20} style={{ color }} />
        </div>
      </div>
    </div>
  )
}

function RoleMiniCard({ role }: { role: RoleRow }) {
  const color = role.atr_24h >= 25 ? '#22c55e' : role.atr_24h >= 15 ? '#eab308' : '#ef4444'
  return (
    <div className="bg-[#1a1a1a] rounded-lg border border-[#333] px-4 py-3 flex items-center justify-between">
      <div>
        <p className="text-xs text-gray-500 capitalize">{role.role} ATR-24h</p>
        <p className="text-lg font-bold mt-0.5" style={{ color }}>
          {role.atr_24h}%
        </p>
      </div>
      <div className="text-right">
        <p className="text-xs text-gray-500">{role.syntheses} synth</p>
        <p className="text-xs text-gray-500">{role.acted_24h} acted</p>
      </div>
    </div>
  )
}

function ATRBadge({ value }: { value: number }) {
  const color = value >= 25 ? 'text-accent-green' : value >= 15 ? 'text-yellow-400' : 'text-accent-red'
  const bgColor = value >= 25 ? 'bg-accent-green/10' : value >= 15 ? 'bg-yellow-400/10' : 'bg-accent-red/10'
  return (
    <span className={cn('px-2 py-0.5 rounded text-xs font-mono font-medium', color, bgColor)}>
      {value}%
    </span>
  )
}

function GateBanner({ gate }: { gate: GateInfo }) {
  const configs = {
    APPROVED: {
      icon: ShieldCheck,
      bg: 'bg-accent-green/10 border-accent-green/30',
      text: 'text-accent-green',
      label: 'Stage 3 APPROVED — Ready to advance to Stage 4',
    },
    CONDITIONAL: {
      icon: AlertTriangle,
      bg: 'bg-yellow-400/10 border-yellow-400/30',
      text: 'text-yellow-400',
      label: 'Stage 3 CONDITIONAL — One role needs remediation',
    },
    FAILED: {
      icon: XCircle,
      bg: 'bg-accent-red/10 border-accent-red/30',
      text: 'text-accent-red',
      label: 'Stage 3 NOT MET — Iterate on templates/playbooks',
    },
    IN_PROGRESS: {
      icon: Clock,
      bg: 'bg-primary-500/10 border-primary-500/30',
      text: 'text-primary-400',
      label: 'Stage 3 IN PROGRESS — Pilot running',
    },
    NO_DATA: {
      icon: Minus,
      bg: 'bg-[#333]/30 border-[#333]',
      text: 'text-gray-500',
      label: 'No synthesis data yet — Pilot starts Mar 4',
    },
  }

  const c = configs[gate.status]
  const Icon = c.icon

  return (
    <div className={cn('flex items-center gap-3 px-4 py-3 rounded-lg border', c.bg)}>
      <Icon size={18} className={c.text} />
      <div>
        <p className={cn('text-sm font-medium', c.text)}>{c.label}</p>
        {gate.details.roles_below_15 && gate.details.roles_below_15.length > 0 && (
          <p className="text-xs text-gray-500 mt-0.5">
            Roles below 15%: {gate.details.roles_below_15.join(', ')}
          </p>
        )}
      </div>
    </div>
  )
}
