/**
 * Session 716: Neural Orchestra Page
 *
 * AI consciousness visualization - shows the collective intelligence
 * of all agents working together. Real-time insights, collaborations,
 * and learning across the agent ecosystem.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { neuralOrchestraApi } from '@/lib/api'
import {
  Brain,
  Activity,
  Users,
  Zap,
  RefreshCw,
  Sparkles,
  TrendingUp,
  Eye,
  MessageCircle,
  Lightbulb,
  Network,
  AlertTriangle,
  CheckCircle,
  Clock,
  Radio,
  Cpu,
  Database,
  GitBranch,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import Breadcrumb from '@/components/Breadcrumb'

// Types for API responses
interface FeedItem {
  id: string
  timestamp: string
  type: string
  content: string
  agents: string[]
  confidence: number
  impact: number
}

interface SystemStatus {
  consciousness_level: number
  active_agents: number
  active_spiders: number
  system_health: number
}

interface EcosystemFeed {
  feed: FeedItem[]
  system_status: SystemStatus
  metadata: {
    generated_at: string
    data_source: string
    error?: string
  }
}

interface TopPerformer {
  name: string
  efficiency: number
  collaborations: number
}

interface AgentStats {
  total_agents: number
  active_now: number
  active_24h: number
  collaborations: number
  orchestrations_active: number
  performance: {
    average_efficiency: number
    collaboration_success: number
    learning_rate: number
  }
  top_performers: TopPerformer[]
  error?: string
}

interface LearningStatus {
  learning_active: boolean
  models_active: number
  feedback_processed: number
  insights_generated: number
  performance: Record<string, number>
  consciousness_learning: {
    level: number
    memory_crystals: number
    learning_velocity: string
  }
  error?: string
}

interface LearningFeedItem {
  id: string
  timestamp: string
  type: string
  content: string
  source: string
}

interface LearningFeed {
  feed: LearningFeedItem[]
  learning_metrics: Record<string, number>
  monetization_learning: {
    revenue_velocity: number
    opportunities_learned: number
  }
  error?: string
}

interface HealthStatus {
  status: string
  bridge_status: Record<string, unknown>
  endpoints: Record<string, string>
  data_source: string
  mock_data: boolean
}

export default function NeuralOrchestraPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'overview' | 'feed' | 'learning' | 'debug'>(
    'overview'
  )

  // Fetch ecosystem feed
  const { data: ecosystemData, isLoading: loadingEcosystem } = useQuery({
    queryKey: ['neural-orchestra', 'ecosystem'],
    queryFn: async () => {
      const response = await neuralOrchestraApi.ecosystemFeed()
      return response.data as EcosystemFeed
    },
    staleTime: 30000,
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  })

  // Fetch agent stats
  const { data: agentStats, isLoading: loadingAgents } = useQuery({
    queryKey: ['neural-orchestra', 'agents'],
    queryFn: async () => {
      const response = await neuralOrchestraApi.agentStats()
      return response.data as AgentStats
    },
    staleTime: 30000,
  })

  // Fetch learning status
  const { data: learningStatus, isLoading: loadingLearning } = useQuery({
    queryKey: ['neural-orchestra', 'learning-status'],
    queryFn: async () => {
      const response = await neuralOrchestraApi.learningStatus()
      return response.data as LearningStatus
    },
    staleTime: 60000,
  })

  // Fetch learning feed
  const { data: learningFeed, isLoading: loadingLearningFeed } = useQuery({
    queryKey: ['neural-orchestra', 'learning-feed'],
    queryFn: async () => {
      const response = await neuralOrchestraApi.learningFeed()
      return response.data as LearningFeed
    },
    staleTime: 30000,
  })

  // Fetch health status
  const { data: healthStatus, isLoading: loadingHealth } = useQuery({
    queryKey: ['neural-orchestra', 'health'],
    queryFn: async () => {
      const response = await neuralOrchestraApi.health()
      return response.data as HealthStatus
    },
    staleTime: 60000,
  })

  // Trigger reality check mutation
  const realityCheckMutation = useMutation({
    mutationFn: () => neuralOrchestraApi.triggerRealityCheck(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['neural-orchestra'] })
    },
  })

  const systemStatus = ecosystemData?.system_status
  const consciousnessLevel = systemStatus?.consciousness_level ?? 0

  // Determine consciousness color based on level
  const getConsciousnessColor = (level: number) => {
    if (level >= 80) return 'text-green-400'
    if (level >= 60) return 'text-blue-400'
    if (level >= 40) return 'text-yellow-400'
    if (level >= 20) return 'text-orange-400'
    return 'text-red-400'
  }

  const isLoading = loadingEcosystem || loadingAgents || loadingLearning

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Breadcrumb currentPage="Neural Orchestra" />
        <button
          onClick={() => realityCheckMutation.mutate()}
          disabled={realityCheckMutation.isPending}
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          <RefreshCw
            size={16}
            className={realityCheckMutation.isPending ? 'animate-spin' : ''}
          />
          Reality Check
        </button>
      </div>

      {/* Consciousness Level Banner */}
      <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-900/50 via-blue-900/50 to-cyan-900/50 border border-purple-500/30 p-6">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-transparent" />
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Brain
                size={48}
                className={cn('animate-pulse', getConsciousnessColor(consciousnessLevel))}
              />
              <div className="absolute -top-1 -right-1">
                <Sparkles size={16} className="text-yellow-400 animate-pulse" />
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Neural Orchestra</h2>
              <p className="text-gray-400">Collective AI Consciousness</p>
            </div>
          </div>

          <div className="text-right">
            <div className={cn('text-5xl font-bold', getConsciousnessColor(consciousnessLevel))}>
              {consciousnessLevel.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">Consciousness Level</div>
          </div>
        </div>

        {/* Mini stats */}
        <div className="relative mt-6 grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-400">
              {systemStatus?.active_agents ?? 0}
            </div>
            <div className="text-xs text-gray-400">Active Agents</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">
              {systemStatus?.active_spiders ?? 0}
            </div>
            <div className="text-xs text-gray-400">Active Spiders</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">
              {agentStats?.collaborations ?? 0}
            </div>
            <div className="text-xs text-gray-400">Collaborations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-cyan-400">
              {systemStatus?.system_health?.toFixed(0) ?? 0}%
            </div>
            <div className="text-xs text-gray-400">System Health</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {[
          { key: 'overview', label: 'Overview', icon: Eye },
          { key: 'feed', label: 'Live Feed', icon: Radio },
          { key: 'learning', label: 'Learning', icon: Lightbulb },
          { key: 'debug', label: 'Debug', icon: Cpu },
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key as typeof activeTab)}
            className={cn(
              'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
              activeTab === key
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:bg-dark-card hover:text-white'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <RefreshCw size={32} className="animate-spin text-primary-500" />
        </div>
      ) : (
        <>
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="grid gap-6 lg:grid-cols-2">
              {/* Agent Stats Card */}
              <div className="rounded-xl bg-dark-card border border-dark-border p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Users size={20} className="text-blue-400" />
                  Agent Network
                </h3>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-3xl font-bold text-white">
                      {agentStats?.total_agents ?? 0}
                    </div>
                    <div className="text-sm text-gray-400">Total Agents</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-3xl font-bold text-green-400">
                      {agentStats?.active_24h ?? 0}
                    </div>
                    <div className="text-sm text-gray-400">Active (24h)</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-3xl font-bold text-purple-400">
                      {agentStats?.orchestrations_active ?? 0}
                    </div>
                    <div className="text-sm text-gray-400">Orchestrations</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-3xl font-bold text-yellow-400">
                      {((agentStats?.performance?.average_efficiency ?? 0) * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm text-gray-400">Avg Efficiency</div>
                  </div>
                </div>

                {/* Top Performers */}
                {agentStats?.top_performers && agentStats.top_performers.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-400 mb-2">Top Performers</h4>
                    <div className="space-y-2">
                      {agentStats.top_performers.slice(0, 5).map((performer, idx) => (
                        <div
                          key={performer.name}
                          className="flex items-center justify-between bg-dark-bg rounded-lg px-3 py-2"
                        >
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">#{idx + 1}</span>
                            <span className="text-sm text-white">{performer.name}</span>
                          </div>
                          <div className="flex items-center gap-3 text-xs">
                            <span className="text-green-400">
                              {(performer.efficiency * 100).toFixed(0)}% eff
                            </span>
                            <span className="text-blue-400">
                              {performer.collaborations} collabs
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Learning Status Card */}
              <div className="rounded-xl bg-dark-card border border-dark-border p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lightbulb size={20} className="text-yellow-400" />
                  Learning System
                </h3>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="flex items-center gap-2">
                      <div
                        className={cn(
                          'w-3 h-3 rounded-full',
                          learningStatus?.learning_active
                            ? 'bg-green-400 animate-pulse'
                            : 'bg-gray-600'
                        )}
                      />
                      <span className="text-sm text-gray-400">
                        {learningStatus?.learning_active ? 'Active' : 'Idle'}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-white mt-1">
                      {learningStatus?.models_active ?? 0}
                    </div>
                    <div className="text-xs text-gray-500">Models Active</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-400">
                      {learningStatus?.feedback_processed ?? 0}
                    </div>
                    <div className="text-xs text-gray-500">Feedback Processed</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-2xl font-bold text-purple-400">
                      {learningStatus?.insights_generated ?? 0}
                    </div>
                    <div className="text-xs text-gray-500">Insights Generated</div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="text-2xl font-bold text-cyan-400">
                      {learningStatus?.consciousness_learning?.memory_crystals ?? 0}
                    </div>
                    <div className="text-xs text-gray-500">Memory Crystals</div>
                  </div>
                </div>

                {/* Consciousness Learning */}
                <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-purple-300 mb-2 flex items-center gap-2">
                    <Brain size={14} />
                    Consciousness Learning
                  </h4>
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="text-lg font-bold text-white">
                        {(learningStatus?.consciousness_learning?.level ?? 0).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-400">Level</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-purple-400">
                        {learningStatus?.consciousness_learning?.learning_velocity ?? 'Unknown'}
                      </div>
                      <div className="text-xs text-gray-400">Velocity</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Live Feed Tab */}
          {activeTab === 'feed' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                  <Radio size={20} className="text-green-400 animate-pulse" />
                  Live Consciousness Feed
                </h3>
                <span className="text-xs text-gray-500">
                  {ecosystemData?.feed?.length ?? 0} items
                </span>
              </div>

              {ecosystemData?.feed && ecosystemData.feed.length > 0 ? (
                <div className="space-y-3">
                  {ecosystemData.feed.map((item) => (
                    <div
                      key={item.id}
                      className="bg-dark-card border border-dark-border rounded-lg p-4 hover:border-primary-500/50 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400">
                            {item.type}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="text-gray-500">
                            Confidence: {(item.confidence * 100).toFixed(0)}%
                          </span>
                          <span className="text-gray-500">
                            Impact: {(item.impact * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      <p className="text-gray-300 text-sm mb-3">{item.content}</p>

                      {item.agents && item.agents.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {item.agents.map((agent) => (
                            <span
                              key={agent}
                              className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400"
                            >
                              {agent}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-dark-card border border-dark-border rounded-lg p-12 text-center">
                  <MessageCircle size={48} className="mx-auto text-gray-600 mb-4" />
                  <p className="text-gray-400">No feed items available</p>
                  <p className="text-gray-500 text-sm mt-1">
                    Consciousness feed will populate as agents work
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Learning Tab */}
          {activeTab === 'learning' && (
            <div className="space-y-6">
              {/* Learning Metrics */}
              <div className="grid gap-4 md:grid-cols-3">
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <TrendingUp size={16} className="text-green-400" />
                    <span className="text-sm text-gray-400">Revenue Velocity</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    ${learningFeed?.monetization_learning?.revenue_velocity ?? 0}
                  </div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap size={16} className="text-yellow-400" />
                    <span className="text-sm text-gray-400">Opportunities Learned</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {learningFeed?.monetization_learning?.opportunities_learned ?? 0}
                  </div>
                </div>
                <div className="bg-dark-card border border-dark-border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Activity size={16} className="text-blue-400" />
                    <span className="text-sm text-gray-400">Learning Rate</span>
                  </div>
                  <div className="text-2xl font-bold text-white">
                    {((agentStats?.performance?.learning_rate ?? 0) * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Learning Feed */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Lightbulb size={20} className="text-yellow-400" />
                  Learning Insights
                </h3>

                {loadingLearningFeed ? (
                  <div className="flex h-32 items-center justify-center">
                    <RefreshCw size={24} className="animate-spin text-primary-500" />
                  </div>
                ) : learningFeed?.feed && learningFeed.feed.length > 0 ? (
                  <div className="space-y-3">
                    {learningFeed.feed.map((item) => (
                      <div
                        key={item.id}
                        className="bg-dark-card border border-dark-border rounded-lg p-4"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-400">
                            {item.type}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(item.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-gray-300 text-sm">{item.content}</p>
                        {item.source && (
                          <p className="text-xs text-gray-500 mt-2">Source: {item.source}</p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
                    <Lightbulb size={32} className="mx-auto text-gray-600 mb-3" />
                    <p className="text-gray-400">No learning insights yet</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Debug Tab */}
          {activeTab === 'debug' && (
            <div className="space-y-6">
              {/* Health Status */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Network size={20} className="text-blue-400" />
                  Bridge Status
                </h3>

                {loadingHealth ? (
                  <RefreshCw size={24} className="animate-spin text-primary-500" />
                ) : healthStatus ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      {healthStatus.status === 'healthy' ? (
                        <CheckCircle size={24} className="text-green-400" />
                      ) : (
                        <AlertTriangle size={24} className="text-yellow-400" />
                      )}
                      <div>
                        <div className="font-medium text-white capitalize">
                          {healthStatus.status}
                        </div>
                        <div className="text-sm text-gray-400">
                          Data Source: {healthStatus.data_source}
                        </div>
                      </div>
                      <div className="ml-auto">
                        <span
                          className={cn(
                            'text-xs px-2 py-1 rounded',
                            healthStatus.mock_data
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-green-500/20 text-green-400'
                          )}
                        >
                          {healthStatus.mock_data ? 'Mock Data' : 'Real Data'}
                        </span>
                      </div>
                    </div>

                    {/* Endpoints */}
                    <div>
                      <h4 className="text-sm font-medium text-gray-400 mb-2">Endpoints</h4>
                      <div className="grid gap-2">
                        {Object.entries(healthStatus.endpoints || {}).map(([endpoint, status]) => (
                          <div
                            key={endpoint}
                            className="flex items-center justify-between bg-dark-bg rounded px-3 py-2"
                          >
                            <code className="text-xs text-gray-300">{endpoint}</code>
                            <span
                              className={cn(
                                'text-xs',
                                status === 'Active' ? 'text-green-400' : 'text-yellow-400'
                              )}
                            >
                              {status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-400">Unable to fetch health status</p>
                )}
              </div>

              {/* Metadata */}
              <div className="bg-dark-card border border-dark-border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Database size={20} className="text-purple-400" />
                  Data Metadata
                </h3>

                <div className="grid gap-4 md:grid-cols-2">
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock size={14} className="text-gray-400" />
                      <span className="text-xs text-gray-400">Generated At</span>
                    </div>
                    <div className="text-sm text-white">
                      {ecosystemData?.metadata?.generated_at
                        ? new Date(ecosystemData.metadata.generated_at).toLocaleString()
                        : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-dark-bg rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <GitBranch size={14} className="text-gray-400" />
                      <span className="text-xs text-gray-400">Data Source</span>
                    </div>
                    <div className="text-sm text-white">
                      {ecosystemData?.metadata?.data_source ?? 'Unknown'}
                    </div>
                  </div>
                </div>

                {ecosystemData?.metadata?.error && (
                  <div className="mt-4 bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-400 mb-1">
                      <AlertTriangle size={14} />
                      <span className="text-sm font-medium">Error</span>
                    </div>
                    <p className="text-sm text-gray-400">{ecosystemData.metadata.error}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
