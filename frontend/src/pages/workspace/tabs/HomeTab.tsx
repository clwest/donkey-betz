/**
 * Session 1078: Home Tab — Platform dashboard
 *
 * Uses /api/home/boot/ for greeting, while-away stats, active projects.
 * Uses /api/deliverables/stats/ for deliverable counts.
 * Uses /api/body/vitals/ for system health.
 * Uses /api/celery/breakdown/ for task throughput.
 */

import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle, CheckCircle, Clock, Package, Target,
  MessageSquare, ArrowRight, Loader2, Activity, Zap,
  Bot, Search, Cpu, Database, Radio, TrendingUp,
  Sparkles, Eye, BarChart3,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'
import { usePAStore } from '@/stores/paStore'
import DemoPipelineCard from '@/components/DemoPipelineCard'
import { useAssistantContextStore } from '@/stores/assistantContextStore'

interface HomeTabProps {
  activeWorkspace: { id: string; name: string } | null
  onNavigateTab: (tab: string) => void
}

function getAge(dateStr?: string): string {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export default function HomeTab({ activeWorkspace, onNavigateTab }: HomeTabProps) {
  // Primary data source — home boot endpoint
  const bootQuery = useQuery({
    queryKey: ['home-boot'],
    queryFn: () => api.get('/home/boot/').then(r => r.data),
    refetchInterval: 60000,
  })

  // Deliverable stats
  const delivStatsQuery = useQuery({
    queryKey: ['home-deliv-stats'],
    queryFn: () => api.get('/deliverables/stats/').then(r => r.data),
    refetchInterval: 60000,
  })

  // System vitals
  const vitalsQuery = useQuery({
    queryKey: ['home-vitals'],
    queryFn: () => api.get('/body/vitals/', { params: { include_details: true } }).then(r => r.data),
    refetchInterval: 30000,
  })

  // Celery throughput
  const celeryQuery = useQuery({
    queryKey: ['home-celery'],
    queryFn: () => api.get('/celery/breakdown/', { params: { window: '60m', limit: 10 } }).then(r => r.data),
    refetchInterval: 30000,
  })

  // Attention items
  const attentionQuery = useQuery({
    queryKey: ['home-attention'],
    queryFn: () => api.get('/human/attention/', { params: { limit: 6 } }).then(r => r.data),
    refetchInterval: 30000,
  })

  const boot = bootQuery.data as Record<string, unknown> | undefined
  const greeting = boot?.greeting as Record<string, string> | undefined
  const whileAway = boot?.while_away as Record<string, number> | undefined
  const activeProjects = (Array.isArray(boot?.active_projects) ? boot.active_projects : []) as Array<Record<string, unknown>>
  const quickStats = boot?.quick_stats as Record<string, unknown> | undefined

  const delivStats = delivStatsQuery.data as Record<string, number> | undefined
  const vitals = vitalsQuery.data as Record<string, unknown> | undefined
  const celery = celeryQuery.data as Record<string, unknown> | undefined

  const rawAttention = attentionQuery.data?.results ?? attentionQuery.data
  const attentionItems = (Array.isArray(rawAttention) ? rawAttention : []) as Array<Record<string, unknown>>

  const healthScore = (vitals as Record<string, number>)?.health_score ?? null
  const agentsActive = (quickStats?.agents_active as number) ?? 0
  const totalDeliverables = delivStats?.total ?? 0
  const savedDeliverables = delivStats?.saved ?? 0
  const last7d = delivStats?.last_7_days ?? 0

  // Celery stats
  const celeryTotal = (celery as Record<string, number>)?.total_tasks ?? 0
  const celerySuccess = (celery as Record<string, number>)?.success_rate ?? 0

  const isLoading = bootQuery.isLoading

  return (
    <div className="space-y-6">
      {/* Greeting */}
      {greeting && (
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Good {greeting.time_of_day}, {greeting.user_name}
            </h2>
            {whileAway && whileAway.hours_since_visit > 1 && (
              <p className="text-xs text-gray-500 mt-0.5">
                {whileAway.hours_since_visit > 24
                  ? `${Math.floor(whileAway.hours_since_visit / 24)}d since last visit`
                  : `${Math.round(whileAway.hours_since_visit)}h since last visit`
                }
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            <a
              href="/workspace/new"
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 transition-colors text-sm text-white font-medium"
            >
              <Zap size={14} />
              New Business
            </a>
            <button
              onClick={() => {
                usePAStore.getState().setCurrentInput("What should I focus on today?")
                usePAStore.getState().openDock()
              }}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary-500/10 border border-primary-500/20 hover:bg-primary-500/20 transition-colors text-sm text-primary-400"
            >
              <MessageSquare size={14} />
              Ask Rigby
            </button>
          </div>
        </div>
      )}

      {/* First Win — demo pipeline for new users */}
      <DemoPipelineCard />

      {/* My Business Workspaces */}
      <MyBusinessWorkspaces />

      {/* Pulse Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <PulseCard label="Agents Active" value={agentsActive} icon={Bot} color="text-primary-400" onClick={() => onNavigateTab('system')} />
        <PulseCard label="Deliverables" value={totalDeliverables} icon={Package} color="text-emerald-400" onClick={() => onNavigateTab('deliverables')} />
        <PulseCard label="Saved" value={savedDeliverables} icon={CheckCircle} color="text-green-400" onClick={() => onNavigateTab('deliverables')} />
        <PulseCard label="Last 7 Days" value={last7d} icon={TrendingUp} color="text-blue-400" onClick={() => onNavigateTab('deliverables')} />
        <PulseCard label="Tasks/hr" value={celeryTotal} icon={Cpu} color="text-yellow-400" onClick={() => onNavigateTab('system')} />
        <PulseCard
          label="System Health"
          value={healthScore !== null ? `${healthScore}%` : (quickStats?.system_health as string) || '--'}
          icon={Activity}
          color={healthScore !== null && healthScore >= 80 ? 'text-green-400' : 'text-yellow-400'}
          onClick={() => onNavigateTab('system')}
        />
      </div>

      {/* While Away Stats (only show if meaningful) */}
      {whileAway && (whileAway.spider_findings > 0 || whileAway.pending_decisions > 0 || whileAway.initiatives_progressed > 0 || whileAway.high_score_dreams > 0) && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 flex items-center gap-1.5">
            <Sparkles size={12} className="text-primary-400" /> While You Were Away
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {whileAway.spider_findings > 0 && (
              <div className="flex items-center gap-2">
                <Search size={14} className="text-blue-400" />
                <div>
                  <p className="text-sm font-medium text-white">{whileAway.spider_findings}</p>
                  <p className="text-[10px] text-gray-500">spider findings</p>
                </div>
              </div>
            )}
            {whileAway.pending_decisions > 0 && (
              <div className="flex items-center gap-2">
                <AlertTriangle size={14} className="text-orange-400" />
                <div>
                  <p className="text-sm font-medium text-white">{whileAway.pending_decisions}</p>
                  <p className="text-[10px] text-gray-500">pending decisions</p>
                </div>
              </div>
            )}
            {whileAway.initiatives_progressed > 0 && (
              <div className="flex items-center gap-2">
                <Target size={14} className="text-emerald-400" />
                <div>
                  <p className="text-sm font-medium text-white">{whileAway.initiatives_progressed}</p>
                  <p className="text-[10px] text-gray-500">initiatives progressed</p>
                </div>
              </div>
            )}
            {whileAway.high_score_dreams > 0 && (
              <div className="flex items-center gap-2">
                <Sparkles size={14} className="text-purple-400" />
                <div>
                  <p className="text-sm font-medium text-white">{whileAway.high_score_dreams}</p>
                  <p className="text-[10px] text-gray-500">high-score dreams</p>
                </div>
              </div>
            )}
            {whileAway.intelligence_desks_ready > 0 && (
              <div className="flex items-center gap-2">
                <Radio size={14} className="text-cyan-400" />
                <div>
                  <p className="text-sm font-medium text-white">{whileAway.intelligence_desks_ready}/4</p>
                  <p className="text-[10px] text-gray-500">intel desks ready</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Attention Queue + Active Projects (2 cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Attention Queue */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                <Zap size={14} className="text-orange-400" />
                Attention Queue
              </h2>
              <button
                onClick={() => onNavigateTab('work')}
                className="text-[11px] text-gray-500 hover:text-primary-400 flex items-center gap-1"
              >
                View all <ArrowRight size={10} />
              </button>
            </div>

            {isLoading ? (
              <div className="flex items-center gap-2 text-gray-500 text-sm py-6 justify-center">
                <Loader2 size={14} className="animate-spin" /> Loading...
              </div>
            ) : attentionItems.length === 0 ? (
              <div className="text-center py-6 text-gray-500 text-sm bg-dark-card border border-dark-border rounded-lg">
                <CheckCircle size={20} className="mx-auto mb-1.5 text-green-500/50" />
                All clear — nothing needs your attention
              </div>
            ) : (
              <div className="space-y-1.5">
                {attentionItems.slice(0, 6).map((item) => (
                  <button
                    key={item.id as string}
                    onClick={() => {
                      useAssistantContextStore.getState().setFocusedEntity({
                        type: 'attention',
                        id: item.id as string,
                        title: (item.title || item.summary || 'Item') as string,
                      })
                      onNavigateTab('work')
                    }}
                    className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors text-left group"
                  >
                    <div className={cn(
                      'w-1.5 h-1.5 rounded-full flex-shrink-0',
                      (item.urgency as string) === 'critical' ? 'bg-red-400' :
                      (item.urgency as string) === 'high' ? 'bg-orange-400' :
                      (item.urgency as string) === 'medium' ? 'bg-yellow-400' : 'bg-gray-500'
                    )} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-200 truncate group-hover:text-white">
                        {(item.title || item.summary || 'Untitled') as string}
                      </p>
                      <p className="text-[11px] text-gray-500">
                        {item.category && <span className="mr-2">{item.category as string}</span>}
                        {item.created_at && <span>{getAge(item.created_at as string)}</span>}
                      </p>
                    </div>
                    <ArrowRight size={12} className="text-gray-600 group-hover:text-primary-400 flex-shrink-0" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Active Projects / Initiatives */}
          {activeProjects.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                  <Target size={14} className="text-emerald-400" />
                  Active Initiatives
                </h2>
                <button
                  onClick={() => onNavigateTab('initiatives')}
                  className="text-[11px] text-gray-500 hover:text-primary-400 flex items-center gap-1"
                >
                  View all <ArrowRight size={10} />
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {activeProjects.slice(0, 4).map((proj) => (
                  <button
                    key={proj.id as string}
                    onClick={() => onNavigateTab('initiatives')}
                    className="text-left px-4 py-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors"
                  >
                    <p className="text-sm text-gray-200 truncate">{(proj.name || 'Untitled') as string}</p>
                    <div className="flex items-center gap-3 mt-1.5">
                      {proj.current_stage !== undefined && (
                        <span className="text-[10px] text-gray-500">Stage {proj.current_stage as number}/5</span>
                      )}
                      {proj.completion_percentage !== undefined && (
                        <div className="flex-1 flex items-center gap-2">
                          <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-emerald-500 rounded-full"
                              style={{ width: `${proj.completion_percentage as number}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-emerald-400">{proj.completion_percentage as number}%</span>
                        </div>
                      )}
                      {proj.status === 'decision_pending' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-orange-500/20 text-orange-400">Needs Review</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: System Status + Quick Actions */}
        <div className="space-y-4">
          {/* Body Systems Summary */}
          {vitals && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3 flex items-center gap-1.5">
                <Activity size={12} /> System Status
              </h3>
              <div className="space-y-2">
                {Array.isArray((vitals as Record<string, unknown>)?.systems) &&
                  ((vitals as Record<string, unknown>).systems as Array<Record<string, unknown>>).slice(0, 6).map((sys) => (
                    <div key={sys.name as string} className="flex items-center justify-between text-xs">
                      <span className="text-gray-400">{(sys.name as string || '').replace(/_/g, ' ')}</span>
                      <span className={cn(
                        'px-1.5 py-0.5 rounded text-[10px] font-medium',
                        (sys.status as string) === 'healthy' || (sys.status as string) === 'breathing'
                          ? 'bg-green-500/20 text-green-400'
                          : (sys.status as string) === 'stressed' || (sys.status as string) === 'labored'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-red-500/20 text-red-400'
                      )}>
                        {sys.status as string}
                      </span>
                    </div>
                  ))
                }
              </div>
              <button
                onClick={() => onNavigateTab('system')}
                className="mt-3 w-full text-center text-[11px] text-gray-500 hover:text-primary-400"
              >
                Full system details
              </button>
            </div>
          )}

          {/* Celery Throughput */}
          {celery && celeryTotal > 0 && (
            <div className="bg-dark-card border border-dark-border rounded-lg p-4">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Cpu size={12} /> Task Engine (1hr)
              </h3>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-500">Tasks processed</span>
                  <span className="text-white font-medium">{celeryTotal.toLocaleString()}</span>
                </div>
                {celerySuccess > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Success rate</span>
                    <span className={cn('font-medium', celerySuccess >= 95 ? 'text-green-400' : 'text-yellow-400')}>
                      {typeof celerySuccess === 'number' ? `${celerySuccess.toFixed(1)}%` : celerySuccess}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-dark-card border border-dark-border rounded-lg p-4">
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-3">Quick Actions</h3>
            <div className="space-y-1.5">
              <QuickAction label="View Work Queue" icon={Zap} onClick={() => onNavigateTab('work')} />
              <QuickAction label="Browse Deliverables" icon={Package} onClick={() => onNavigateTab('deliverables')} />
              <QuickAction label="Intelligence Feeds" icon={Radio} onClick={() => onNavigateTab('intelligence')} />
              <QuickAction label="Content Studio" icon={Sparkles} onClick={() => onNavigateTab('build')} />
            </div>
          </div>

          {/* Ask Rigby */}
          <button
            onClick={() => {
              usePAStore.getState().setCurrentInput("What should I focus on today?")
              usePAStore.getState().openDock()
            }}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg bg-primary-500/10 border border-primary-500/20 hover:bg-primary-500/20 transition-colors text-sm text-primary-400"
          >
            <MessageSquare size={14} />
            Ask Rigby what to focus on
          </button>
        </div>
      </div>
    </div>
  )
}


function PulseCard({
  label, value, icon: Icon, color, onClick,
}: {
  label: string
  value: string | number
  icon: React.ComponentType<{ size?: number; className?: string }>
  color: string
  onClick?: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-3 px-3 py-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors text-left"
    >
      <Icon size={16} className={color} />
      <div>
        <p className={cn('text-lg font-semibold', color)}>{value}</p>
        <p className="text-[10px] text-gray-500">{label}</p>
      </div>
    </button>
  )
}


function QuickAction({
  label, icon: Icon, onClick,
}: {
  label: string
  icon: React.ComponentType<{ size?: number; className?: string }>
  onClick: () => void
}) {
  return (
    <button
      onClick={onClick}
      className="w-full flex items-center gap-2 px-3 py-2 rounded text-xs text-gray-400 hover:text-white hover:bg-dark-border/50 transition-colors text-left"
    >
      <Icon size={12} />
      {label}
    </button>
  )
}


function MyBusinessWorkspaces() {
  const { data, isLoading } = useQuery({
    queryKey: ['my-workspaces'],
    queryFn: async () => {
      const res = await api.get('/workspaces/')
      return res.data
    },
    refetchInterval: 30000,
  })

  const workspaces = (data?.results || data || []) as Array<{
    id: string
    name: string
    workspace_type: string
    is_active: boolean
    updated_at: string
  }>

  // Show all workspaces (not just sandbox)
  const bizWorkspaces = workspaces.filter(w => w.is_active)

  if (isLoading || bizWorkspaces.length === 0) return null

  const TYPE_COLORS: Record<string, string> = {
    sandbox: 'bg-blue-900/30 text-blue-300',
    production: 'bg-green-900/30 text-green-300',
    default: 'bg-purple-900/30 text-purple-300',
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-400 uppercase tracking-wide">My Workspaces</h3>
        <a href="/workspace/new" className="text-xs text-blue-400 hover:text-blue-300">+ New</a>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {bizWorkspaces.map(ws => (
          <a
            key={ws.id}
            href={`/workspace/${ws.id}`}
            className="p-4 bg-dark-bg rounded-xl border border-dark-border hover:border-blue-800/50 hover:bg-dark-card transition-colors group"
          >
            <div className="flex items-center gap-2 mb-1">
              <Zap size={14} className="text-blue-400" />
              <span className="font-medium text-white group-hover:text-blue-300 transition-colors">{ws.name}</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_COLORS[ws.workspace_type] || TYPE_COLORS.default}`}>
                {ws.workspace_type}
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span>Updated {new Date(ws.updated_at).toLocaleDateString()}</span>
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}
