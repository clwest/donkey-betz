// Session 1008: ToolCall Analytics Dashboard
// Aggregated tool-call metrics, decision records, and signal clusters

import { useState } from 'react'
import { useQuery, keepPreviousData } from '@tanstack/react-query'
import {
  BarChart3,
  Loader2,
  RefreshCw,
  CheckCircle,
  XCircle,
  ChevronDown,
  ChevronRight,
  Activity,
  Cpu,
  Search,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { auditApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// ============ Types ============

interface ToolCallAggregate {
  id: number
  agent_name: string
  tool_name: string
  date: string
  total_calls: number
  successful_calls: number
  failed_calls: number
  avg_latency_ms: number | null
}

interface DecisionRecord {
  id: number
  agent_name: string
  decision_type: string
  was_successful: boolean
  reasoning: string
  outcome: string
  created_at: string
}

interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ============ Main Component ============

export function ToolCallAnalyticsTab() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2 mb-2">
        <BarChart3 size={20} className="text-primary-400" />
        <h3 className="text-lg font-semibold text-white">Tool Call Analytics</h3>
      </div>

      <SummaryCards />
      <AggregatesTable />
      <DecisionRecordsTable />
    </div>
  )
}

// ============ Summary Cards ============

function SummaryCards() {
  const today = new Date().toISOString().slice(0, 10)

  const { data: todayData, isLoading } = useQuery({
    queryKey: ['tool-call-aggregates', 'today', today],
    queryFn: () => auditApi.toolCallAggregates({ date: today }),
    select: (res) => {
      const results = (res.data as PaginatedResponse<ToolCallAggregate>)?.results ?? res.data ?? []
      return results as ToolCallAggregate[]
    },
  })

  const { data: allData } = useQuery({
    queryKey: ['tool-call-aggregates', 'all'],
    queryFn: () => auditApi.toolCallAggregates(),
    select: (res) => {
      const results = (res.data as PaginatedResponse<ToolCallAggregate>)?.results ?? res.data ?? []
      return results as ToolCallAggregate[]
    },
  })

  const todayAggs = todayData ?? []
  const allAggs = allData ?? []

  const todayCalls = todayAggs.reduce((sum, a) => sum + a.total_calls, 0)
  const allCalls = allAggs.reduce((sum, a) => sum + a.total_calls, 0)
  const allSuccesses = allAggs.reduce((sum, a) => sum + a.successful_calls, 0)
  const successRate = allCalls > 0 ? ((allSuccesses / allCalls) * 100).toFixed(1) : '—'
  const uniqueAgents = new Set(allAggs.map((a) => a.agent_name)).size
  const uniqueTools = new Set(allAggs.map((a) => a.tool_name)).size

  const cards = [
    { label: 'Calls Today', value: isLoading ? '...' : todayCalls.toLocaleString(), icon: Activity },
    { label: 'Total Calls', value: allCalls.toLocaleString(), icon: BarChart3 },
    { label: 'Success Rate', value: `${successRate}%`, icon: CheckCircle },
    { label: 'Agents / Tools', value: `${uniqueAgents} / ${uniqueTools}`, icon: Cpu },
  ]

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {cards.map((card) => (
        <div key={card.label} className="p-4 rounded-lg bg-dark-card border border-dark-border">
          <div className="flex items-center gap-2 mb-2">
            <card.icon size={14} className="text-gray-400" />
            <span className="text-xs text-gray-400">{card.label}</span>
          </div>
          <span className="text-xl font-semibold text-white">{card.value}</span>
        </div>
      ))}
    </div>
  )
}

// ============ Aggregates Table ============

function AggregatesTable() {
  const [page, setPage] = useState(1)
  const [agentFilter, setAgentFilter] = useState('')
  const [toolFilter, setToolFilter] = useState('')

  const params: Record<string, unknown> = { page }
  if (agentFilter) params.agent_name = agentFilter
  if (toolFilter) params.tool_name = toolFilter

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['tool-call-aggregates', 'table', page, agentFilter, toolFilter],
    queryFn: () => auditApi.toolCallAggregates(params as Parameters<typeof auditApi.toolCallAggregates>[0]),
    placeholderData: keepPreviousData,
  })

  const paginated = (data?.data ?? {}) as PaginatedResponse<ToolCallAggregate>
  const results = paginated.results ?? []
  const hasNext = !!paginated.next
  const hasPrev = !!paginated.previous
  const total = paginated.count ?? 0

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-300">Aggregates</h4>
        <button
          onClick={() => refetch()}
          className="p-1.5 rounded-lg bg-gray-800/50 text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <div className="relative flex-1 max-w-xs">
          <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Filter by agent..."
            value={agentFilter}
            onChange={(e) => { setAgentFilter(e.target.value); setPage(1) }}
            className="w-full pl-7 pr-3 py-1.5 rounded-lg bg-gray-800/50 border border-dark-border text-white text-xs placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
          />
        </div>
        <div className="relative flex-1 max-w-xs">
          <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            placeholder="Filter by tool..."
            value={toolFilter}
            onChange={(e) => { setToolFilter(e.target.value); setPage(1) }}
            className="w-full pl-7 pr-3 py-1.5 rounded-lg bg-gray-800/50 border border-dark-border text-white text-xs placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
          />
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-400" size={20} />
        </div>
      )}

      {error && <ErrorState error={error as Error} message="Failed to load aggregates" onRetry={() => refetch()} />}

      {!isLoading && !error && (
        <div className="overflow-x-auto rounded-lg border border-dark-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-800/50 text-gray-400 text-xs">
                <th className="text-left px-3 py-2">Date</th>
                <th className="text-left px-3 py-2">Agent</th>
                <th className="text-left px-3 py-2">Tool</th>
                <th className="text-right px-3 py-2">Calls</th>
                <th className="text-right px-3 py-2">Success</th>
                <th className="text-right px-3 py-2">Failed</th>
                <th className="text-right px-3 py-2">Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {results.length === 0 ? (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-gray-500 text-xs">No data found</td>
                </tr>
              ) : (
                results.map((row) => (
                  <tr key={row.id} className="border-t border-dark-border hover:bg-gray-800/30">
                    <td className="px-3 py-2 text-gray-400 text-xs">{row.date}</td>
                    <td className="px-3 py-2 text-white">{row.agent_name}</td>
                    <td className="px-3 py-2 text-gray-300">{row.tool_name}</td>
                    <td className="px-3 py-2 text-right text-white">{row.total_calls}</td>
                    <td className="px-3 py-2 text-right text-green-400">{row.successful_calls}</td>
                    <td className="px-3 py-2 text-right text-red-400">{row.failed_calls}</td>
                    <td className="px-3 py-2 text-right text-gray-300">
                      {row.avg_latency_ms != null ? `${Math.round(row.avg_latency_ms)}ms` : '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {total > 0 && (
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{total} total records</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!hasPrev}
              className={cn('px-2 py-1 rounded', hasPrev ? 'hover:text-white' : 'text-gray-600 cursor-not-allowed')}
            >
              Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasNext}
              className={cn('px-2 py-1 rounded', hasNext ? 'hover:text-white' : 'text-gray-600 cursor-not-allowed')}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ============ Decision Records Table ============

function DecisionRecordsTable() {
  const [page, setPage] = useState(1)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['decision-records', page],
    queryFn: () => auditApi.decisionRecords({ page }),
    placeholderData: keepPreviousData,
  })

  const paginated = (data?.data ?? {}) as PaginatedResponse<DecisionRecord>
  const results = paginated.results ?? []
  const hasNext = !!paginated.next
  const hasPrev = !!paginated.previous
  const total = paginated.count ?? 0

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-300">Decision Records</h4>
        <button
          onClick={() => refetch()}
          className="p-1.5 rounded-lg bg-gray-800/50 text-gray-400 hover:text-white transition-colors"
        >
          <RefreshCw size={12} />
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-400" size={20} />
        </div>
      )}

      {error && <ErrorState error={error as Error} message="Failed to load decision records" onRetry={() => refetch()} />}

      {!isLoading && !error && (
        <div className="space-y-2">
          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-xs">No decision records found</div>
          ) : (
            results.map((rec) => (
              <div key={rec.id} className="rounded-lg border border-dark-border overflow-hidden">
                <button
                  onClick={() => setExpandedId(expandedId === rec.id ? null : rec.id)}
                  className="w-full flex items-center gap-3 p-3 bg-gray-800/30 hover:bg-gray-800/50 transition-colors text-left"
                >
                  {expandedId === rec.id ? (
                    <ChevronDown size={12} className="text-gray-500 shrink-0" />
                  ) : (
                    <ChevronRight size={12} className="text-gray-500 shrink-0" />
                  )}
                  <span className="text-xs text-gray-400 w-24 shrink-0">
                    {new Date(rec.created_at).toLocaleDateString()}
                  </span>
                  <span className="text-sm text-white flex-1">{rec.agent_name}</span>
                  <span className="text-xs text-gray-400 w-28 shrink-0">{rec.decision_type}</span>
                  {rec.was_successful ? (
                    <CheckCircle size={12} className="text-green-400 shrink-0" />
                  ) : (
                    <XCircle size={12} className="text-red-400 shrink-0" />
                  )}
                  <span className="text-xs text-gray-400 truncate max-w-[200px]">{rec.outcome}</span>
                </button>
                {expandedId === rec.id && (
                  <div className="p-3 bg-gray-800/20 border-t border-dark-border space-y-2">
                    {rec.reasoning && (
                      <div>
                        <span className="text-xs text-gray-500">Reasoning:</span>
                        <p className="text-sm text-gray-300 mt-0.5">{rec.reasoning}</p>
                      </div>
                    )}
                    {rec.outcome && (
                      <div>
                        <span className="text-xs text-gray-500">Outcome:</span>
                        <p className="text-sm text-gray-300 mt-0.5">{rec.outcome}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* Pagination */}
      {total > 0 && (
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>{total} total records</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!hasPrev}
              className={cn('px-2 py-1 rounded', hasPrev ? 'hover:text-white' : 'text-gray-600 cursor-not-allowed')}
            >
              Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!hasNext}
              className={cn('px-2 py-1 rounded', hasNext ? 'hover:text-white' : 'text-gray-600 cursor-not-allowed')}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
