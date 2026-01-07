import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { llmRoutingApi } from '@/lib/api'
import {
  Brain, Server, DollarSign, Activity, Bot, CheckCircle, XCircle,
  Loader2, RefreshCw, Search, Filter, Clock, Zap, TrendingUp,
  AlertTriangle, ChevronDown, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'providers' | 'models' | 'agents' | 'logs' | 'analytics'

interface Provider {
  name: string
  display_name: string
  has_api_key: boolean
  model_count: number
  calls_24h: number
  cost_24h: number
  success_rate_24h: number
}

interface Model {
  model_id: string
  display_name: string
  provider: string | { name: string; display_name: string }
  cost_per_1m_input: number
  cost_per_1m_output: number
  max_context: number
  capabilities: string[]
  is_active: boolean
}

interface AgentConfig {
  id: string
  agent_name: string
  agent_category: string
  is_active: boolean
  primary_model: {
    model_id: string
    display_name: string
    provider: string
  }
  fallback_model?: {
    model_id: string
    display_name: string
    provider: string
  }
  temperature: number
  max_tokens: number
  total_calls: number
  total_cost: number
  notes?: string
}

interface CallLog {
  id: string
  agent_name: string
  provider: string
  model_id: string
  success: boolean
  input_tokens: number
  output_tokens: number
  cost: number
  latency_ms: number
  error_message?: string
  created_at: string
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: Activity },
  { id: 'providers' as TabType, label: 'Providers', icon: Server },
  { id: 'models' as TabType, label: 'Models', icon: Brain },
  { id: 'agents' as TabType, label: 'Agent Configs', icon: Bot },
  { id: 'logs' as TabType, label: 'Call Logs', icon: Clock },
  { id: 'analytics' as TabType, label: 'Analytics', icon: TrendingUp },
]

function StatCard({ title, value, subtitle, icon: Icon, color }: {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ElementType
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="h-12 w-12 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon size={24} style={{ color }} />
        </div>
      </div>
    </div>
  )
}

function ProviderCard({ provider }: { provider: Provider }) {
  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            'h-10 w-10 rounded-lg flex items-center justify-center',
            provider.has_api_key ? 'bg-accent-green/20' : 'bg-accent-amber/20'
          )}>
            <Server size={20} className={provider.has_api_key ? 'text-accent-green' : 'text-accent-amber'} />
          </div>
          <div>
            <h3 className="font-medium">{provider.display_name}</h3>
            <p className="text-xs text-gray-400">{provider.name}</p>
          </div>
        </div>
        <span className={cn(
          'text-xs px-2 py-1 rounded',
          provider.has_api_key ? 'bg-accent-green/20 text-accent-green' : 'bg-accent-amber/20 text-accent-amber'
        )}>
          {provider.has_api_key ? 'Active' : 'No Key'}
        </span>
      </div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <p className="text-gray-400">Models</p>
          <p className="font-medium">{provider.model_count ?? 0}</p>
        </div>
        <div>
          <p className="text-gray-400">Calls (24h)</p>
          <p className="font-medium">{provider.calls_24h ?? 0}</p>
        </div>
        <div>
          <p className="text-gray-400">Cost (24h)</p>
          <p className="font-medium">${(provider.cost_24h ?? 0).toFixed(4)}</p>
        </div>
      </div>
      {(provider.calls_24h ?? 0) > 0 && (
        <div className="mt-3 pt-3 border-t border-dark-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Success Rate</span>
            <span className={cn(
              'font-medium',
              (provider.success_rate_24h ?? 0) >= 90 ? 'text-accent-green' :
              (provider.success_rate_24h ?? 0) >= 70 ? 'text-accent-amber' : 'text-accent-red'
            )}>
              {(provider.success_rate_24h ?? 0).toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

function ModelRow({ model }: { model: Model }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="border border-dark-border rounded-lg">
      <div
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-dark-bg/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          {expanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          <div>
            <p className="font-medium">{model.display_name}</p>
            <p className="text-xs text-gray-400">{typeof model.provider === 'object' ? model.provider?.display_name || model.provider?.name : model.provider} • {model.model_id}</p>
          </div>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-gray-400">
            ${(model.cost_per_1m_input ?? 0).toFixed(2)}/1M in
          </span>
          <span className="text-gray-400">
            ${(model.cost_per_1m_output ?? 0).toFixed(2)}/1M out
          </span>
          <span className={cn(
            'px-2 py-1 rounded text-xs',
            model.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
          )}>
            {model.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
      </div>
      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-dark-border">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-400">Max Context</p>
              <p className="font-medium">{(model.max_context ?? 0).toLocaleString()} tokens</p>
            </div>
            <div>
              <p className="text-gray-400">Capabilities</p>
              <div className="flex flex-wrap gap-1 mt-1">
                {model.capabilities?.map((cap, index) => (
                  <span key={cap || `cap-${index}`} className="text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function AgentConfigRow({ config }: { config: AgentConfig }) {
  return (
    <tr className="border-b border-dark-border hover:bg-dark-bg/30">
      <td className="px-4 py-3">
        <div>
          <span className="font-medium">{config.agent_name}</span>
          <p className="text-xs text-gray-500">{config.agent_category}</p>
        </div>
      </td>
      <td className="px-4 py-3">
        <span className="text-primary-400">{config.primary_model?.display_name}</span>
        <p className="text-xs text-gray-500">{config.primary_model?.model_id}</p>
      </td>
      <td className="px-4 py-3">
        <span className="text-gray-400">{config.primary_model?.provider}</span>
      </td>
      <td className="px-4 py-3 text-sm">
        <span className={cn(
          'px-2 py-1 rounded text-xs',
          config.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
        )}>
          {config.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-400">
        {config.total_calls || 0} calls
      </td>
    </tr>
  )
}

function LogRow({ log }: { log: CallLog }) {
  return (
    <tr className="border-b border-dark-border hover:bg-dark-bg/30">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          {log.success ? (
            <CheckCircle size={14} className="text-accent-green" />
          ) : (
            <XCircle size={14} className="text-accent-red" />
          )}
          <span className="font-medium">{log.agent_name}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm">
        <span className="text-primary-400">{log.provider}</span>
        <p className="text-xs text-gray-500">{log.model_id}</p>
      </td>
      <td className="px-4 py-3 text-sm text-gray-400">
        {(log.input_tokens ?? 0) + (log.output_tokens ?? 0)} tokens
      </td>
      <td className="px-4 py-3 text-sm">
        <span className="text-accent-amber">${(log.cost ?? 0).toFixed(6)}</span>
      </td>
      <td className="px-4 py-3 text-sm text-gray-400">
        {log.latency_ms ?? 0}ms
      </td>
      <td className="px-4 py-3 text-xs text-gray-500">
        {new Date(log.created_at).toLocaleString()}
      </td>
    </tr>
  )
}

export default function LLMRoutingPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [agentSearch, setAgentSearch] = useState('')
  const [providerFilter, setProviderFilter] = useState('')
  const queryClient = useQueryClient()

  // Fetch status (overview)
  const { data: statusData, isLoading: loadingStatus, refetch: refetchStatus } = useQuery({
    queryKey: ['llm-routing-status'],
    queryFn: () => llmRoutingApi.status(),
    refetchInterval: 30000,
  })

  // Fetch providers
  const { data: providersData, isLoading: loadingProviders } = useQuery({
    queryKey: ['llm-routing-providers'],
    queryFn: () => llmRoutingApi.providers(),
    enabled: activeTab === 'overview' || activeTab === 'providers',
  })

  // Fetch models
  const { data: modelsData, isLoading: loadingModels } = useQuery({
    queryKey: ['llm-routing-models', providerFilter],
    queryFn: () => llmRoutingApi.models({ provider: providerFilter || undefined }),
    enabled: activeTab === 'models',
  })

  // Fetch agent configs
  const { data: agentConfigsData, isLoading: loadingAgentConfigs } = useQuery({
    queryKey: ['llm-routing-agent-configs', agentSearch],
    queryFn: () => llmRoutingApi.agentConfigs({ agent: agentSearch || undefined }),
    enabled: activeTab === 'agents',
  })

  // Fetch logs
  const { data: logsData, isLoading: loadingLogs } = useQuery({
    queryKey: ['llm-routing-logs'],
    queryFn: () => llmRoutingApi.logs({ hours: 24, limit: 50 }),
    enabled: activeTab === 'logs',
  })

  // Fetch analytics
  const { data: analyticsData, isLoading: loadingAnalytics } = useQuery({
    queryKey: ['llm-routing-analytics'],
    queryFn: () => llmRoutingApi.costAnalytics(168), // 7 days
    enabled: activeTab === 'analytics' || activeTab === 'overview',
  })

  const status = statusData?.data?.status || {}
  const providers: Provider[] = providersData?.data?.providers || status.providers?.details || []
  const models: Model[] = modelsData?.data?.models || []
  const agentConfigs: AgentConfig[] = agentConfigsData?.data?.configs || []
  const logs: CallLog[] = logsData?.data?.logs || []
  const analytics = analyticsData?.data?.analytics || {}

  const activity = status.activity_24h || {}
  const providerStats = status.providers || {}
  const modelStats = status.models || {}
  const configStats = status.agent_configs || {}

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-primary-600/20 flex items-center justify-center">
            <Brain size={28} className="text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">LLM Routing</h1>
            <p className="text-gray-400">Multi-provider model routing and cost analytics</p>
          </div>
        </div>
        <button
          className="btn btn-secondary flex items-center gap-2"
          onClick={() => {
            refetchStatus()
            queryClient.invalidateQueries({ queryKey: ['llm-routing'] })
          }}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {loadingStatus ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                  title="Providers"
                  value={`${providerStats.with_keys || 0}/${providerStats.total || 0}`}
                  subtitle="with API keys"
                  icon={Server}
                  color="#06b6d4"
                />
                <StatCard
                  title="Models"
                  value={modelStats.total || 0}
                  subtitle={`${modelStats.active || 0} active`}
                  icon={Brain}
                  color="#8b5cf6"
                />
                <StatCard
                  title="Agent Configs"
                  value={configStats.total || 0}
                  subtitle="agents configured"
                  icon={Bot}
                  color="#f59e0b"
                />
                <StatCard
                  title="Total Cost (24h)"
                  value={`$${(activity.total_cost || 0).toFixed(4)}`}
                  subtitle={`${activity.total_calls || 0} calls`}
                  icon={DollarSign}
                  color="#10b981"
                />
              </div>

              {/* Activity Summary */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* 24h Activity */}
                <div className="card">
                  <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                    <Activity size={18} className="text-primary-400" />
                    24-Hour Activity
                  </h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Total Calls</span>
                      <span className="font-medium">{activity.total_calls || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Successful</span>
                      <span className="font-medium text-accent-green">{activity.successful_calls || 0}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Success Rate</span>
                      <span className={cn(
                        'font-medium',
                        (activity.total_calls ? (activity.successful_calls / activity.total_calls * 100) : 0) >= 90
                          ? 'text-accent-green'
                          : 'text-accent-amber'
                      )}>
                        {activity.total_calls
                          ? ((activity.successful_calls / activity.total_calls) * 100).toFixed(1)
                          : 0}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between pt-2 border-t border-dark-border">
                      <span className="text-gray-400">Total Cost</span>
                      <span className="font-medium text-accent-amber">${(activity.total_cost || 0).toFixed(4)}</span>
                    </div>
                  </div>
                </div>

                {/* Provider Breakdown */}
                <div className="card">
                  <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                    <Server size={18} className="text-accent-cyan" />
                    Provider Status
                  </h3>
                  <div className="space-y-2">
                    {providers.slice(0, 6).map((provider: Provider, index: number) => (
                      <div key={provider.name || `provider-${index}`} className="flex items-center justify-between py-2 border-b border-dark-border last:border-0">
                        <div className="flex items-center gap-2">
                          {provider.has_api_key ? (
                            <CheckCircle size={14} className="text-accent-green" />
                          ) : (
                            <AlertTriangle size={14} className="text-accent-amber" />
                          )}
                          <span>{provider.display_name}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">{provider.model_count} models</span>
                          {provider.calls_24h > 0 && (
                            <span className="text-accent-green">{provider.calls_24h} calls</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 7-Day Analytics Preview */}
              {analytics.overall && (
                <div className="card">
                  <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                    <TrendingUp size={18} className="text-accent-green" />
                    7-Day Summary
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    <div>
                      <p className="text-sm text-gray-400">Total Calls</p>
                      <p className="text-xl font-bold">{analytics.overall.total_calls}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Success Rate</p>
                      <p className="text-xl font-bold text-accent-green">{analytics.overall.success_rate?.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Total Cost</p>
                      <p className="text-xl font-bold text-accent-amber">${analytics.overall.total_cost?.toFixed(4)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Total Tokens</p>
                      <p className="text-xl font-bold">{analytics.overall.total_tokens?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Avg Latency</p>
                      <p className="text-xl font-bold">{analytics.overall.avg_latency_ms?.toFixed(0)}ms</p>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Providers Tab */}
      {activeTab === 'providers' && (
        <div className="space-y-4">
          {loadingProviders ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {providers.map((provider: Provider, index: number) => (
                <ProviderCard key={provider.name || `provider-${index}`} provider={provider} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Models Tab */}
      {activeTab === 'models' && (
        <div className="space-y-4">
          {/* Filter */}
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-xs">
              <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <select
                value={providerFilter}
                onChange={(e) => setProviderFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-dark-card border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
              >
                <option value="">All Providers</option>
                {providers.map((p, index) => (
                  <option key={p.name || `provider-opt-${index}`} value={p.name}>{p.display_name}</option>
                ))}
              </select>
            </div>
          </div>

          {loadingModels ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <div className="space-y-2">
              {models.map((model: Model, index: number) => (
                <ModelRow key={model.model_id || `model-${index}`} model={model} />
              ))}
              {models.length === 0 && (
                <p className="text-center text-gray-400 py-8">No models found</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Agent Configs Tab */}
      {activeTab === 'agents' && (
        <div className="space-y-4">
          {/* Search */}
          <div className="relative max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search agents..."
              value={agentSearch}
              onChange={(e) => setAgentSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-card border border-dark-border rounded-lg text-sm focus:border-primary-500 focus:outline-none"
            />
          </div>

          {loadingAgentConfigs ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-border text-left text-sm text-gray-400">
                    <th className="px-4 py-3 font-medium">Agent</th>
                    <th className="px-4 py-3 font-medium">Primary Model</th>
                    <th className="px-4 py-3 font-medium">Provider</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Usage</th>
                  </tr>
                </thead>
                <tbody>
                  {agentConfigs.map((config: AgentConfig, index: number) => (
                    <AgentConfigRow key={config.agent_name || `config-${index}`} config={config} />
                  ))}
                </tbody>
              </table>
              {agentConfigs.length === 0 && (
                <p className="text-center text-gray-400 py-8">No agent configs found</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div className="space-y-4">
          {loadingLogs ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-border text-left text-sm text-gray-400">
                    <th className="px-4 py-3 font-medium">Agent</th>
                    <th className="px-4 py-3 font-medium">Model</th>
                    <th className="px-4 py-3 font-medium">Tokens</th>
                    <th className="px-4 py-3 font-medium">Cost</th>
                    <th className="px-4 py-3 font-medium">Latency</th>
                    <th className="px-4 py-3 font-medium">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log: CallLog, index: number) => (
                    <LogRow key={log.id || `log-${index}`} log={log} />
                  ))}
                </tbody>
              </table>
              {logs.length === 0 && (
                <p className="text-center text-gray-400 py-8">No call logs found</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {loadingAnalytics ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Overall Stats */}
              {analytics.overall && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <StatCard
                    title="Total Calls"
                    value={analytics.overall.total_calls || 0}
                    icon={Zap}
                    color="#8b5cf6"
                  />
                  <StatCard
                    title="Success Rate"
                    value={`${(analytics.overall.success_rate || 0).toFixed(1)}%`}
                    icon={CheckCircle}
                    color="#10b981"
                  />
                  <StatCard
                    title="Total Cost"
                    value={`$${(analytics.overall.total_cost || 0).toFixed(4)}`}
                    icon={DollarSign}
                    color="#f59e0b"
                  />
                  <StatCard
                    title="Total Tokens"
                    value={(analytics.overall.total_tokens || 0).toLocaleString()}
                    icon={Brain}
                    color="#06b6d4"
                  />
                  <StatCard
                    title="Avg Latency"
                    value={`${(analytics.overall.avg_latency_ms || 0).toFixed(0)}ms`}
                    icon={Clock}
                    color="#ec4899"
                  />
                </div>
              )}

              {/* By Provider */}
              {analytics.by_provider && (
                <div className="card">
                  <h3 className="text-lg font-medium mb-4">Cost by Provider (7 days)</h3>
                  <div className="space-y-3">
                    {analytics.by_provider.map((item: any, index: number) => (
                      <div key={item.provider || `by-provider-${index}`} className="flex items-center justify-between py-2 border-b border-dark-border last:border-0">
                        <div>
                          <span className="font-medium">{item.provider}</span>
                          <span className="text-sm text-gray-400 ml-2">({item.calls} calls)</span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className={cn(
                            'text-sm',
                            item.success_rate >= 90 ? 'text-accent-green' : 'text-accent-amber'
                          )}>
                            {item.success_rate?.toFixed(1)}%
                          </span>
                          <span className="font-medium text-accent-amber">${item.cost?.toFixed(4)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* By Agent */}
              {analytics.by_agent && analytics.by_agent.length > 0 && (
                <div className="card">
                  <h3 className="text-lg font-medium mb-4">Top Agents by Cost (7 days)</h3>
                  <div className="space-y-3">
                    {analytics.by_agent.slice(0, 10).map((item: any, index: number) => (
                      <div key={item.agent || `by-agent-${index}`} className="flex items-center justify-between py-2 border-b border-dark-border last:border-0">
                        <div>
                          <span className="font-medium">{item.agent}</span>
                          <span className="text-sm text-gray-400 ml-2">({item.calls} calls)</span>
                        </div>
                        <span className="font-medium text-accent-amber">${item.cost?.toFixed(4)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
