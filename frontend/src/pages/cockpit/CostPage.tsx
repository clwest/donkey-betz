import { useState } from 'react'
import { useCostOverview } from '@/hooks/cockpitQueries'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/lib/cn'

const RANGE_OPTIONS = [
  { value: 6, label: '6h' },
  { value: 24, label: '24h' },
  { value: 168, label: '7d' },
  { value: 720, label: '30d' },
]

function fmt(cost: number) {
  if (cost >= 1) return `$${cost.toFixed(2)}`
  if (cost >= 0.01) return `$${cost.toFixed(3)}`
  return `$${cost.toFixed(4)}`
}

function fmtTokens(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

function KpiCard({ label, value, sub, tone }: { label: string; value: string | number; sub?: string; tone?: Tone }) {
  return (
    <div className="card p-4">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className={cn(
        'text-2xl font-bold',
        tone === 'red' ? 'text-red-400' : tone === 'amber' ? 'text-amber-400' : tone === 'green' ? 'text-green-400' : 'text-white',
      )}>
        {value}
      </div>
      {sub && <div className="text-xs text-gray-500 mt-0.5">{sub}</div>}
    </div>
  )
}

export default function CostPage() {
  const [hours, setHours] = useState(24)
  const { data, isLoading } = useCostOverview({ hours })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Cost & Tokens</h1>
        <div className="card p-6"><SkeletonRows count={8} /></div>
      </div>
    )
  }

  const o = data?.overall

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <DollarSign size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Cost & Tokens</h1>
        <div className="flex rounded-lg border border-dark-border overflow-hidden ml-auto">
          {RANGE_OPTIONS.map((r) => (
            <button
              key={r.value}
              onClick={() => setHours(r.value)}
              className={cn(
                'px-3 py-1.5 text-xs transition-colors',
                hours === r.value
                  ? 'bg-primary-600/20 text-primary-400'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border/50',
              )}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {/* KPI row */}
      {o && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <KpiCard
            label="Total Spend"
            value={fmt(o.total_cost)}
            sub={o.cost_delta_pct !== 0 ? `${o.cost_delta_pct > 0 ? '+' : ''}${o.cost_delta_pct}% vs prev` : undefined}
            tone={o.cost_delta_pct > 50 ? 'red' : o.cost_delta_pct > 20 ? 'amber' : undefined}
          />
          <KpiCard label="API Calls" value={o.total_calls.toLocaleString()} />
          <KpiCard label="Tokens" value={fmtTokens(o.total_tokens)} />
          <KpiCard
            label="Avg Latency"
            value={o.avg_latency_ms > 1000 ? `${(o.avg_latency_ms / 1000).toFixed(1)}s` : `${o.avg_latency_ms}ms`}
          />
        </div>
      )}

      {/* Delta indicator */}
      {o && o.cost_delta_pct !== 0 && (
        <div className={cn(
          'card p-3 flex items-center gap-2 text-sm',
          o.cost_delta_pct > 0 ? 'border-l-2 border-l-amber-500' : 'border-l-2 border-l-green-500',
        )}>
          {o.cost_delta_pct > 0
            ? <TrendingUp size={16} className="text-amber-400" />
            : <TrendingDown size={16} className="text-green-400" />
          }
          <span className="text-gray-300">
            Spending {o.cost_delta_pct > 0 ? 'up' : 'down'} {Math.abs(o.cost_delta_pct)}% vs previous {hours}h window
          </span>
          <span className="text-gray-500 ml-auto">prev: {fmt(o.prev_cost)}</span>
        </div>
      )}

      {/* By Provider */}
      {data && data.by_provider.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2">By Provider</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Provider</th>
                  <th className="p-3 text-right">Cost</th>
                  <th className="p-3 text-right">Calls</th>
                  <th className="p-3 text-right">Tokens</th>
                  <th className="p-3 text-right">Latency</th>
                  <th className="p-3 text-right">Success</th>
                </tr>
              </thead>
              <tbody>
                {data.by_provider.map((p) => (
                  <tr key={p.provider} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-300 capitalize">{p.provider}</td>
                    <td className="p-3 text-right text-gray-200 font-medium">{fmt(p.cost)}</td>
                    <td className="p-3 text-right text-gray-400">{p.calls}</td>
                    <td className="p-3 text-right text-gray-400">{fmtTokens(p.tokens)}</td>
                    <td className="p-3 text-right text-gray-400">{p.avg_latency}ms</td>
                    <td className="p-3 text-right">
                      <StatusPill
                        label={`${p.success_rate}%`}
                        tone={p.success_rate < 80 ? 'red' : p.success_rate < 95 ? 'amber' : 'green'}
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* By Model */}
      {data && data.by_model.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2">By Model</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Model</th>
                  <th className="p-3">Provider</th>
                  <th className="p-3 text-right">Cost</th>
                  <th className="p-3 text-right">Calls</th>
                  <th className="p-3 text-right">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {data.by_model.map((m) => (
                  <tr key={`${m.provider}-${m.model_id}`} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-300">{m.model_id}</td>
                    <td className="p-3 text-gray-500 capitalize">{m.provider}</td>
                    <td className="p-3 text-right text-gray-200 font-medium">{fmt(m.cost)}</td>
                    <td className="p-3 text-right text-gray-400">{m.calls}</td>
                    <td className="p-3 text-right text-gray-400">{fmtTokens(m.tokens)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Top Agents by Cost */}
      {data && data.by_agent.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-gray-300 mb-2">Top Agents by Cost</h2>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-xs text-gray-500 border-b border-dark-border">
                  <th className="p-3">Agent</th>
                  <th className="p-3 text-right">Cost</th>
                  <th className="p-3 text-right">Calls</th>
                  <th className="p-3 text-right">Tokens</th>
                </tr>
              </thead>
              <tbody>
                {data.by_agent.map((a) => (
                  <tr key={a.agent_name} className="border-b border-dark-border/50 hover:bg-dark-border/20">
                    <td className="p-3 text-gray-300">{a.agent_name}</td>
                    <td className="p-3 text-right text-gray-200 font-medium">{fmt(a.cost)}</td>
                    <td className="p-3 text-right text-gray-400">{a.calls}</td>
                    <td className="p-3 text-right text-gray-400">{fmtTokens(a.tokens)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty state */}
      {data && data.by_provider.length === 0 && (
        <div className="card p-8 text-center text-gray-500">
          No LLM calls recorded in this period.
        </div>
      )}
    </div>
  )
}
