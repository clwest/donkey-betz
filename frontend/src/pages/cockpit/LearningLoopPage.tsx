import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Brain, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Clock, Zap, Target } from 'lucide-react'
import { cn } from '@/lib/cn'

interface LearningItem {
  id: string
  title?: string
  knowledge_type?: string
  memory_type?: string
  confidence_score?: number
  importance?: number
  valence?: string
  agent__name?: string
  last_updated_at?: string
  created_at?: string
  source?: string
  data_points_count?: number
}

interface AgentStat {
  agent__name: string
  total: number
  completed: number
  failed: number
  success_rate: number
  avg_time_ms: number
}

export default function LearningLoopPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['learning-loop'],
    queryFn: async () => {
      const res = await api.get('/cockpit/learning-loop/')
      return res.data
    },
    refetchInterval: 30_000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Brain size={24} className="text-primary-400" />
          Learning Loop
        </h1>
        <div className="card p-8 text-center text-gray-500">Loading learning data...</div>
      </div>
    )
  }

  const recent = data?.recent_learnings || { items: [], total_knowledge: 0, total_memories: 0 }
  const patterns = data?.reinforced_patterns || {}
  const rejected = data?.rejected || {}
  const improvement = data?.agent_improvement || {}

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white flex items-center gap-2">
        <Brain size={24} className="text-primary-400" />
        Learning Loop
      </h1>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Knowledge" value={recent.total_knowledge || 0} icon={Brain} color="text-primary-400" />
        <StatCard label="Total Memories" value={recent.total_memories || 0} icon={Zap} color="text-accent-cyan" />
        <StatCard label="Success Rate (30d)" value={`${improvement.overall_success_rate || 0}%`} icon={Target} color="text-accent-green" />
        <StatCard label="Executions (30d)" value={improvement.total_executions_30d || 0} icon={TrendingUp} color="text-accent-amber" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Panel 1: Recent Learnings */}
        <div className="card">
          <div className="p-4 border-b border-dark-border">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <Clock size={16} className="text-primary-400" />
              Recent Learnings ({recent.count || 0})
            </h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {(recent.items || []).length === 0 ? (
              <div className="p-6 text-center text-gray-500 text-sm">No recent learnings</div>
            ) : (
              (recent.items || []).map((item: LearningItem) => (
                <div key={item.id} className="px-4 py-3 border-b border-dark-border/30 hover:bg-gray-800/20">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-200 truncate">{item.title || 'Untitled'}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={cn(
                          'text-xs px-1.5 py-0.5 rounded',
                          item.source === 'knowledge' ? 'bg-primary-500/20 text-primary-400' : 'bg-accent-cyan/20 text-accent-cyan'
                        )}>
                          {item.knowledge_type || item.memory_type || item.source}
                        </span>
                        <span className="text-xs text-gray-500">{item.agent__name}</span>
                        {item.confidence_score != null && (
                          <span className="text-xs text-gray-500">{(item.confidence_score * 100).toFixed(0)}% conf</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Panel 2: Reinforced Patterns */}
        <div className="card">
          <div className="p-4 border-b border-dark-border">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <TrendingUp size={16} className="text-accent-green" />
              Reinforced Patterns
            </h2>
          </div>
          <div className="max-h-96 overflow-y-auto p-4 space-y-4">
            {/* Knowledge types */}
            <div>
              <h3 className="text-xs font-medium text-gray-400 mb-2">By Knowledge Type</h3>
              {(patterns.by_knowledge_type || []).map((p: { knowledge_type: string; count: number; avg_confidence: number }) => (
                <div key={p.knowledge_type} className="flex items-center justify-between py-1.5">
                  <span className="text-sm text-gray-300">{p.knowledge_type}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500">{(p.avg_confidence * 100).toFixed(0)}% avg</span>
                    <span className="text-sm font-medium text-white">{p.count}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Memory patterns */}
            <div>
              <h3 className="text-xs font-medium text-gray-400 mb-2">Memory Patterns (30d)</h3>
              {(patterns.memory_patterns || []).map((p: { memory_type: string; valence: string; count: number }, i: number) => (
                <div key={i} className="flex items-center justify-between py-1.5">
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      'w-2 h-2 rounded-full',
                      p.valence === 'positive' ? 'bg-accent-green' : p.valence === 'negative' ? 'bg-red-400' : 'bg-gray-400'
                    )} />
                    <span className="text-sm text-gray-300">{p.memory_type}</span>
                  </div>
                  <span className="text-sm font-medium text-white">{p.count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Panel 3: Rejected / Failed */}
        <div className="card">
          <div className="p-4 border-b border-dark-border">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <AlertTriangle size={16} className="text-red-400" />
              Rejected & Failed
            </h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {/* Failed executions */}
            {(rejected.failed_executions || []).length > 0 && (
              <div className="p-3">
                <h3 className="text-xs font-medium text-gray-400 mb-2">Failed Executions (7d): {rejected.failed_count_7d}</h3>
                {(rejected.failed_executions || []).map((item: { id: string; agent__name: string; task: string }) => (
                  <div key={item.id} className="py-1.5 flex items-center gap-2">
                    <TrendingDown size={12} className="text-red-400 flex-shrink-0" />
                    <span className="text-xs text-gray-400">{item.agent__name}:</span>
                    <span className="text-xs text-gray-500 truncate">{item.task}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Negative memories */}
            {(rejected.negative_memories || []).length > 0 && (
              <div className="p-3 border-t border-dark-border/30">
                <h3 className="text-xs font-medium text-gray-400 mb-2">Negative Feedback (30d): {rejected.negative_count_30d}</h3>
                {(rejected.negative_memories || []).map((item: LearningItem) => (
                  <div key={item.id} className="py-1.5">
                    <span className="text-xs text-gray-300">{item.title}</span>
                    <span className="text-xs text-gray-500 ml-2">({item.agent__name})</span>
                  </div>
                ))}
              </div>
            )}

            {(rejected.failed_executions || []).length === 0 && (rejected.negative_memories || []).length === 0 && (
              <div className="p-6 text-center text-gray-500 text-sm">No failures or rejections</div>
            )}
          </div>
        </div>

        {/* Panel 4: Agent Improvement */}
        <div className="card">
          <div className="p-4 border-b border-dark-border">
            <h2 className="text-sm font-semibold text-white flex items-center gap-2">
              <CheckCircle size={16} className="text-accent-green" />
              Agent Performance (30d)
            </h2>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {/* Top performers */}
            {(improvement.top_performers || []).length > 0 && (
              <div className="p-3">
                <h3 className="text-xs font-medium text-gray-400 mb-2">Top Performers</h3>
                {(improvement.top_performers || []).map((s: AgentStat) => (
                  <div key={s.agent__name} className="flex items-center justify-between py-1.5">
                    <span className="text-sm text-gray-300 truncate flex-1">{s.agent__name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500">{s.total} runs</span>
                      <span className={cn(
                        'text-sm font-medium',
                        s.success_rate >= 95 ? 'text-accent-green' : s.success_rate >= 80 ? 'text-accent-amber' : 'text-red-400'
                      )}>
                        {s.success_rate}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Struggling */}
            {(improvement.struggling || []).length > 0 && (
              <div className="p-3 border-t border-dark-border/30">
                <h3 className="text-xs font-medium text-gray-400 mb-2">Needs Attention</h3>
                {(improvement.struggling || []).map((s: AgentStat) => (
                  <div key={s.agent__name} className="flex items-center justify-between py-1.5">
                    <span className="text-sm text-gray-300 truncate flex-1">{s.agent__name}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-500">{s.failed} failed</span>
                      <span className="text-sm font-medium text-red-400">{s.success_rate}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {(improvement.agent_stats || []).length === 0 && (
              <div className="p-6 text-center text-gray-500 text-sm">No execution data yet</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, icon: Icon, color }: { label: string; value: string | number; icon: React.ElementType; color: string }) {
  return (
    <div className="card p-3">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={14} className={color} />
        <span className="text-xs text-gray-500">{label}</span>
      </div>
      <p className="text-xl font-bold text-white">{value}</p>
    </div>
  )
}
