/**
 * Session 1078: Home Tab — "What needs my attention right now?"
 *
 * Replaces the old Overview tab (developer stats). Shows:
 * - Attention Queue: ranked next actions across the workspace
 * - Active Work: pinned/recent items
 * - Workspace Pulse: compact health cards
 */

import { useQuery } from '@tanstack/react-query'
import {
  AlertTriangle, CheckCircle, Clock, Package, Target,
  MessageSquare, ArrowRight, Loader2, Activity, Zap,
  FileText, RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api, deliverablesApi } from '@/lib/api'
import { usePAStore } from '@/stores/paStore'
import { useAssistantContextStore } from '@/stores/assistantContextStore'

interface HomeTabProps {
  activeWorkspace: { id: string; name: string } | null
  onNavigateTab: (tab: string) => void
}

const urgencyColors: Record<string, string> = {
  critical: 'text-red-400',
  high: 'text-orange-400',
  medium: 'text-yellow-400',
  low: 'text-gray-400',
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
  // Attention items
  const attentionQuery = useQuery({
    queryKey: ['home-attention'],
    queryFn: () => api.get('/human/attention/', { params: { limit: 8 } }).then(r => r.data),
    refetchInterval: 30000,
  })

  // Recent deliverables
  const delivQuery = useQuery({
    queryKey: ['home-deliverables'],
    queryFn: () => deliverablesApi.list({ page_size: 5, ordering: '-created_at' }).then(r => r.data),
    refetchInterval: 60000,
  })

  // Active initiatives
  const initQuery = useQuery({
    queryKey: ['home-initiatives'],
    queryFn: () => api.get('/initiatives/', { params: { status: 'ACTIVE', page_size: 5 } }).then(r => r.data),
    refetchInterval: 60000,
  })

  // System pulse
  const pulseQuery = useQuery({
    queryKey: ['home-pulse'],
    queryFn: () => api.get('/body/vitals/', { params: { include_details: false } }).then(r => r.data),
    refetchInterval: 30000,
  })

  // Stats
  const statsQuery = useQuery({
    queryKey: ['home-stats'],
    queryFn: () => api.get('/assistant/attention/stats/').then(r => r.data),
    refetchInterval: 30000,
  })

  const attentionItems = (attentionQuery.data?.results || attentionQuery.data || []) as Array<Record<string, unknown>>
  const deliverables = (delivQuery.data?.results || []) as Array<Record<string, unknown>>
  const initiatives = (initQuery.data?.results || []) as Array<Record<string, unknown>>
  const pulse = pulseQuery.data as Record<string, unknown> | undefined
  const stats = statsQuery.data as Record<string, unknown> | undefined

  const pendingCount = (stats as Record<string, number>)?.pending_count ?? attentionItems.length
  const healthScore = (pulse as Record<string, number>)?.health_score ?? null

  return (
    <div className="space-y-6">
      {/* Pulse Strip */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <PulseCard
          label="Needs Attention"
          value={pendingCount}
          icon={AlertTriangle}
          color={pendingCount > 0 ? 'text-orange-400' : 'text-green-400'}
          onClick={() => onNavigateTab('work')}
        />
        <PulseCard
          label="Active Initiatives"
          value={initiatives.length}
          icon={Target}
          color="text-primary-400"
          onClick={() => onNavigateTab('work')}
        />
        <PulseCard
          label="Deliverables (7d)"
          value={deliverables.length}
          icon={Package}
          color="text-emerald-400"
          onClick={() => onNavigateTab('work')}
        />
        <PulseCard
          label="System Health"
          value={healthScore !== null ? `${healthScore}%` : '--'}
          icon={Activity}
          color={healthScore !== null && healthScore >= 80 ? 'text-green-400' : 'text-yellow-400'}
          onClick={() => onNavigateTab('system')}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Attention Queue — takes 2 cols */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between">
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

          {attentionQuery.isLoading ? (
            <div className="flex items-center gap-2 text-gray-500 text-sm py-8 justify-center">
              <Loader2 size={14} className="animate-spin" /> Loading...
            </div>
          ) : attentionItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              <CheckCircle size={24} className="mx-auto mb-2 text-green-500/50" />
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
                  <div className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', urgencyColors[(item.urgency as string) || 'low'] || 'bg-gray-500')} />
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

        {/* Active Work — right column */}
        <div className="space-y-4">
          {/* Active Initiatives */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Target size={12} /> Active Initiatives
            </h3>
            {initiatives.length === 0 ? (
              <p className="text-xs text-gray-600">No active initiatives</p>
            ) : (
              <div className="space-y-1.5">
                {initiatives.slice(0, 4).map((init) => (
                  <button
                    key={init.id as string}
                    onClick={() => onNavigateTab('work')}
                    className="w-full text-left px-3 py-2 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors"
                  >
                    <p className="text-xs text-gray-300 truncate">{(init.name || init.title || 'Untitled') as string}</p>
                    <p className="text-[10px] text-gray-500 mt-0.5">
                      {init.current_stage && `Stage ${init.current_stage}`}
                      {init.status && ` \u00B7 ${init.status}`}
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Recent Deliverables */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2 flex items-center gap-1.5">
              <Package size={12} /> Recent Deliverables
            </h3>
            {deliverables.length === 0 ? (
              <p className="text-xs text-gray-600">No recent deliverables</p>
            ) : (
              <div className="space-y-1.5">
                {deliverables.slice(0, 4).map((d) => (
                  <button
                    key={d.id as string}
                    onClick={() => onNavigateTab('work')}
                    className="w-full text-left px-3 py-2 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors"
                  >
                    <p className="text-xs text-gray-300 truncate">{(d.title || 'Untitled') as string}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {d.quality_score !== undefined && (
                        <span className={cn('text-[10px]', (d.quality_score as number) >= 0.75 ? 'text-green-400' : 'text-yellow-400')}>
                          {Math.round((d.quality_score as number) * 100)}%
                        </span>
                      )}
                      {d.created_at && <span className="text-[10px] text-gray-600">{getAge(d.created_at as string)}</span>}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Ask Rigby CTA */}
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
      className="flex items-center gap-3 px-4 py-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors text-left"
    >
      <Icon size={18} className={color} />
      <div>
        <p className={cn('text-lg font-semibold', color)}>{value}</p>
        <p className="text-[11px] text-gray-500">{label}</p>
      </div>
    </button>
  )
}
