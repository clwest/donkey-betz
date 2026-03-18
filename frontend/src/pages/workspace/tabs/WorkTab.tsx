/**
 * Session 1077: Unified Work Tab
 *
 * Combines Deliverables + Initiatives + Governance into a single
 * "what needs my attention?" dashboard with ranked priority queue,
 * KPI tiles, and deep links to detail views.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Package, Target, ClipboardList, Loader2, AlertCircle,
  CheckCircle, Clock, ArrowRight, ExternalLink,
  FileText, Zap, AlertTriangle, Eye, ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { deliverablesApi, assistantApi } from '@/lib/api'
import { useWorkspaceStore } from '@/stores/workspaceStore'

interface WorkTabProps {
  workspaceId?: string
  onNavigateTab?: (tab: string) => void
}

interface WorkItem {
  id: string
  title: string
  type: 'deliverable' | 'initiative' | 'attention'
  status: string
  urgency?: string
  category?: string
  agent?: string
  age?: string
  created_at?: string
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

const urgencyColors: Record<string, string> = {
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  low: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

const typeIcons: Record<string, React.ElementType> = {
  deliverable: Package,
  initiative: Target,
  attention: ClipboardList,
}

const typeBadgeColors: Record<string, string> = {
  deliverable: 'bg-blue-500/20 text-blue-400',
  initiative: 'bg-purple-500/20 text-purple-400',
  attention: 'bg-amber-500/20 text-amber-400',
}

export function WorkTab({ workspaceId, onNavigateTab }: WorkTabProps) {
  const activeWsId = workspaceId || useWorkspaceStore(s => s.activeWorkspace?.id)
  const [selectedType, setSelectedType] = useState<string | null>(null)

  // Fetch deliverables (ready for review)
  const deliverableQuery = useQuery({
    queryKey: ['work-deliverables', activeWsId],
    queryFn: () => deliverablesApi.list({
      status: 'completed',
      per_page: 10,
      ...(activeWsId ? { workspace: activeWsId } : {}),
    }).then(r => r.data),
    staleTime: 30000,
  })

  // Fetch deliverable stats
  const statsQuery = useQuery({
    queryKey: ['work-stats', activeWsId],
    queryFn: () => deliverablesApi.stats(activeWsId ? { workspace: activeWsId } : undefined).then(r => r.data),
    staleTime: 30000,
  })

  // Fetch initiatives via PA
  const initiativeQuery = useQuery({
    queryKey: ['work-initiatives'],
    queryFn: async () => {
      try {
        const r = await assistantApi.paChat('List active initiatives with status ACTIVE or TRIAGE, limit 10', {
          source: 'work-tab',
          context: { silent: true },
        })
        // This returns a task_id for async polling — for MVP just use the deliverables
        return null
      } catch {
        return null
      }
    },
    enabled: false, // Disabled for MVP — initiatives come from direct API later
  })

  // Fetch governance attention items
  const attentionQuery = useQuery({
    queryKey: ['work-attention'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/human/attention/?limit=10&urgency=critical,high', {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        })
        if (!r.ok) return { items: [], total: 0 }
        const data = await r.json()
        return {
          items: (data.results || data.items || []).slice(0, 10),
          total: data.count || data.total || 0,
        }
      } catch {
        return { items: [], total: 0 }
      }
    },
    staleTime: 30000,
  })

  const stats = statsQuery.data?.stats
  const deliverables = deliverableQuery.data?.results || deliverableQuery.data?.deliverables || []
  const attention = attentionQuery.data || { items: [], total: 0 }

  // Build unified work queue
  const workItems: WorkItem[] = []

  // Add attention items (highest priority)
  for (const item of attention.items) {
    workItems.push({
      id: item.id,
      title: item.title,
      type: 'attention',
      status: item.status || 'pending',
      urgency: item.urgency || 'medium',
      category: item.item_type || item.category,
      agent: item.source_agent,
      age: getAge(item.created_at),
      created_at: item.created_at,
    })
  }

  // Add deliverables (ready for review)
  for (const d of deliverables) {
    workItems.push({
      id: d.id,
      title: d.title,
      type: 'deliverable',
      status: d.status || 'completed',
      category: d.category,
      agent: d.agent_name,
      age: getAge(d.created_at),
      created_at: d.created_at,
    })
  }

  // Sort: critical attention first, then high, then deliverables by age
  const urgencyOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }
  workItems.sort((a, b) => {
    if (a.type === 'attention' && b.type !== 'attention') return -1
    if (b.type === 'attention' && a.type !== 'attention') return 1
    const ua = urgencyOrder[a.urgency || 'low'] ?? 3
    const ub = urgencyOrder[b.urgency || 'low'] ?? 3
    if (ua !== ub) return ua - ub
    return (b.created_at || '').localeCompare(a.created_at || '')
  })

  const filtered = selectedType
    ? workItems.filter(w => w.type === selectedType)
    : workItems

  const isLoading = deliverableQuery.isLoading || statsQuery.isLoading || attentionQuery.isLoading

  return (
    <div className="space-y-6">
      {/* KPI Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <button
          onClick={() => setSelectedType(selectedType === 'deliverable' ? null : 'deliverable')}
          className={cn(
            'p-4 rounded-xl border transition-all text-left',
            selectedType === 'deliverable'
              ? 'border-blue-500/50 bg-blue-500/10'
              : 'border-dark-border bg-dark-card hover:border-gray-600'
          )}
        >
          <div className="flex items-center justify-between mb-2">
            <Package size={20} className="text-blue-400" />
            <span className="text-2xl font-bold text-white">
              {stats?.total ?? '—'}
            </span>
          </div>
          <p className="text-sm text-gray-400">Deliverables</p>
          <p className="text-xs text-gray-500 mt-1">
            {stats?.saved ?? 0} saved &middot; {stats?.recent_7d ?? 0} this week
          </p>
        </button>

        <button
          onClick={() => setSelectedType(selectedType === 'attention' ? null : 'attention')}
          className={cn(
            'p-4 rounded-xl border transition-all text-left',
            selectedType === 'attention'
              ? 'border-amber-500/50 bg-amber-500/10'
              : 'border-dark-border bg-dark-card hover:border-gray-600'
          )}
        >
          <div className="flex items-center justify-between mb-2">
            <ClipboardList size={20} className="text-amber-400" />
            <span className="text-2xl font-bold text-white">
              {attention.total || '—'}
            </span>
          </div>
          <p className="text-sm text-gray-400">Needs Attention</p>
          <p className="text-xs text-gray-500 mt-1">
            {attention.items.filter((i: Record<string, string>) => i.urgency === 'critical' || i.urgency === 'high').length} critical/high
          </p>
        </button>

        <button
          onClick={() => onNavigateTab?.('initiatives')}
          className="p-4 rounded-xl border border-dark-border bg-dark-card hover:border-gray-600 transition-all text-left"
        >
          <div className="flex items-center justify-between mb-2">
            <Target size={20} className="text-purple-400" />
            <ArrowRight size={16} className="text-gray-500" />
          </div>
          <p className="text-sm text-gray-400">Initiatives</p>
          <p className="text-xs text-gray-500 mt-1">View pipeline &rarr;</p>
        </button>
      </div>

      {/* Type filter pills */}
      <div className="flex gap-2">
        <button
          onClick={() => setSelectedType(null)}
          className={cn(
            'px-3 py-1.5 rounded-full text-xs font-medium transition-colors',
            !selectedType ? 'bg-primary-500/20 text-primary-400' : 'bg-gray-800 text-gray-400 hover:text-white'
          )}
        >
          All ({workItems.length})
        </button>
        {(['attention', 'deliverable'] as const).map(type => {
          const count = workItems.filter(w => w.type === type).length
          if (count === 0) return null
          const TypeIcon = typeIcons[type]
          return (
            <button
              key={type}
              onClick={() => setSelectedType(selectedType === type ? null : type)}
              className={cn(
                'px-3 py-1.5 rounded-full text-xs font-medium transition-colors flex items-center gap-1',
                selectedType === type ? typeBadgeColors[type] : 'bg-gray-800 text-gray-400 hover:text-white'
              )}
            >
              <TypeIcon size={12} />
              {type === 'attention' ? 'Attention' : 'Deliverables'} ({count})
            </button>
          )
        })}
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-primary-400" />
        </div>
      )}

      {/* Work Queue */}
      {!isLoading && (
        <div className="space-y-2">
          {filtered.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <CheckCircle size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">All caught up! Nothing needs your attention right now.</p>
            </div>
          ) : (
            filtered.map(item => {
              const TypeIcon = typeIcons[item.type]
              return (
                <div
                  key={`${item.type}-${item.id}`}
                  className="flex items-center gap-3 p-3 rounded-lg bg-dark-card border border-dark-border hover:border-gray-600 transition-colors cursor-pointer group"
                  onClick={() => {
                    if (item.type === 'deliverable') onNavigateTab?.('deliverables')
                    if (item.type === 'attention') onNavigateTab?.('boardroom')
                    if (item.type === 'initiative') onNavigateTab?.('initiatives')
                  }}
                >
                  {/* Type icon */}
                  <div className={cn('p-2 rounded-lg', typeBadgeColors[item.type])}>
                    <TypeIcon size={16} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white truncate group-hover:text-primary-400 transition-colors">
                      {item.title}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      {item.category && (
                        <span className="text-xs text-gray-500 truncate max-w-[150px]">{item.category}</span>
                      )}
                      {item.agent && (
                        <span className="text-xs text-gray-600">&middot; {item.agent}</span>
                      )}
                    </div>
                  </div>

                  {/* Urgency badge */}
                  {item.urgency && item.type === 'attention' && (
                    <span className={cn(
                      'px-2 py-0.5 rounded-full text-xs font-medium border',
                      urgencyColors[item.urgency] || urgencyColors.low
                    )}>
                      {item.urgency}
                    </span>
                  )}

                  {/* Age */}
                  <span className="text-xs text-gray-500 whitespace-nowrap">{item.age}</span>

                  <ChevronRight size={14} className="text-gray-600 group-hover:text-gray-400" />
                </div>
              )
            })
          )}
        </div>
      )}

      {/* Deep links */}
      <div className="grid grid-cols-3 gap-3 pt-4 border-t border-dark-border">
        {[
          { tab: 'deliverables', label: 'All Deliverables', icon: Package, color: 'text-blue-400' },
          { tab: 'initiatives', label: 'All Initiatives', icon: Target, color: 'text-purple-400' },
          { tab: 'boardroom', label: 'Boardroom', icon: ClipboardList, color: 'text-amber-400' },
        ].map(link => (
          <button
            key={link.tab}
            onClick={() => onNavigateTab?.(link.tab)}
            className="flex items-center gap-2 p-3 rounded-lg bg-gray-800/30 hover:bg-gray-800/60 transition-colors text-sm text-gray-400 hover:text-white"
          >
            <link.icon size={16} className={link.color} />
            {link.label}
            <ArrowRight size={12} className="ml-auto" />
          </button>
        ))}
      </div>
    </div>
  )
}
