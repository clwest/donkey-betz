/**
 * Session 1077: Unified Work Tab — Self-Contained
 *
 * Priority queue with inline expansion and actions.
 * Clicking an item expands it in-place (no navigation to other tabs).
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Package, Target, ClipboardList, Loader2,
  CheckCircle, Clock, ArrowRight,
  ChevronRight, ChevronDown, X,
  ThumbsUp, ThumbsDown, Eye, Archive,
  ExternalLink,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { deliverablesApi } from '@/lib/api'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { ChatMarkdown } from '@/components/ChatMarkdown'

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
  content?: string
  content_format?: string
  summary?: string
  tags?: string[]
  quality_score?: number
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
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch deliverables
  const deliverableQuery = useQuery({
    queryKey: ['work-deliverables', activeWsId],
    queryFn: () => deliverablesApi.list({
      status: 'completed',
      per_page: 15,
      ...(activeWsId ? { workspace: activeWsId } : {}),
    }).then(r => r.data),
    staleTime: 30000,
  })

  // Fetch stats
  const statsQuery = useQuery({
    queryKey: ['work-stats', activeWsId],
    queryFn: () => deliverablesApi.stats(activeWsId ? { workspace: activeWsId } : undefined).then(r => r.data),
    staleTime: 30000,
  })

  // Fetch attention items
  const attentionQuery = useQuery({
    queryKey: ['work-attention'],
    queryFn: async () => {
      try {
        const r = await fetch('/api/human/attention/?limit=15&urgency=critical,high,medium', {
          credentials: 'include',
        })
        if (!r.ok) return { items: [], total: 0 }
        const data = await r.json()
        return {
          items: (data.results || data.items || []).slice(0, 15),
          total: data.count || data.total || 0,
        }
      } catch {
        return { items: [], total: 0 }
      }
    },
    staleTime: 30000,
  })

  // Fetch expanded item detail
  const detailQuery = useQuery({
    queryKey: ['work-detail', expandedId],
    queryFn: () => expandedId ? deliverablesApi.detail(expandedId).then(r => r.data) : null,
    enabled: !!expandedId,
  })

  // Fetch activity
  const activityQuery = useQuery({
    queryKey: ['work-activity', activeWsId],
    queryFn: async () => {
      try {
        const r = await fetch(`/api/workspaces/${activeWsId}/operations/?limit=6&page_size=6`, {
          credentials: 'include',
        })
        if (!r.ok) return []
        const data = await r.json()
        return (data.results || data.operations || []).slice(0, 6)
      } catch {
        return []
      }
    },
    enabled: !!activeWsId,
    staleTime: 30000,
  })

  const stats = statsQuery.data?.stats
  const deliverables = deliverableQuery.data?.results || deliverableQuery.data?.deliverables || []
  const attention = attentionQuery.data || { items: [], total: 0 }
  const detail = detailQuery.data?.deliverable || detailQuery.data

  // Build unified work queue
  const workItems: WorkItem[] = []

  for (const item of attention.items) {
    workItems.push({
      id: item.id,
      title: item.title,
      type: 'attention',
      status: item.status || 'pending',
      urgency: item.urgency || 'medium',
      category: item.item_type || item.category,
      agent: item.source_agent,
      summary: item.summary,
      age: getAge(item.created_at),
      created_at: item.created_at,
    })
  }

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
      quality_score: d.quality_score,
      tags: d.tags,
    })
  }

  // Sort: critical attention first, then by age
  const urgencyOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }
  workItems.sort((a, b) => {
    if (a.type === 'attention' && b.type !== 'attention') return -1
    if (b.type === 'attention' && a.type !== 'attention') return 1
    const ua = urgencyOrder[a.urgency || 'low'] ?? 3
    const ub = urgencyOrder[b.urgency || 'low'] ?? 3
    if (ua !== ub) return ua - ub
    return (b.created_at || '').localeCompare(a.created_at || '')
  })

  const filtered = selectedType ? workItems.filter(w => w.type === selectedType) : workItems
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
            <span className="text-2xl font-bold text-white">{stats?.total ?? '—'}</span>
          </div>
          <p className="text-sm text-gray-400">Deliverables</p>
          <p className="text-xs text-gray-500 mt-1">{stats?.saved ?? 0} saved &middot; {stats?.recent_7d ?? 0} this week</p>
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
            <span className="text-2xl font-bold text-white">{attention.total || '—'}</span>
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
              const isExpanded = expandedId === item.id

              return (
                <div key={`${item.type}-${item.id}`} className="rounded-lg bg-dark-card border border-dark-border overflow-hidden">
                  {/* Item header (clickable to expand) */}
                  <div
                    className="flex items-center gap-3 p-3 hover:bg-gray-800/30 transition-colors cursor-pointer"
                    onClick={() => setExpandedId(isExpanded ? null : item.id)}
                  >
                    <div className={cn('p-2 rounded-lg', typeBadgeColors[item.type])}>
                      <TypeIcon size={16} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white truncate">{item.title}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {item.category && <span className="text-xs text-gray-500 truncate max-w-[150px]">{item.category}</span>}
                        {item.agent && <span className="text-xs text-gray-600">&middot; {item.agent}</span>}
                      </div>
                    </div>

                    {item.urgency && item.type === 'attention' && (
                      <span className={cn('px-2 py-0.5 rounded-full text-xs font-medium border', urgencyColors[item.urgency] || urgencyColors.low)}>
                        {item.urgency}
                      </span>
                    )}

                    {item.quality_score != null && (
                      <span className={cn(
                        'px-2 py-0.5 rounded text-xs',
                        item.quality_score >= 0.8 ? 'text-green-400' : item.quality_score >= 0.6 ? 'text-yellow-400' : 'text-gray-400'
                      )}>
                        {(item.quality_score * 100).toFixed(0)}%
                      </span>
                    )}

                    <span className="text-xs text-gray-500 whitespace-nowrap">{item.age}</span>

                    {isExpanded ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-600" />}
                  </div>

                  {/* Expanded detail panel */}
                  {isExpanded && (
                    <div className="border-t border-dark-border">
                      {/* Content preview */}
                      <div className="p-4 max-h-[400px] overflow-y-auto">
                        {item.type === 'deliverable' && detailQuery.isLoading && (
                          <div className="flex justify-center py-6"><Loader2 size={20} className="animate-spin text-primary-400" /></div>
                        )}

                        {item.type === 'deliverable' && detail?.content && (
                          <div className="prose prose-invert prose-sm max-w-none">
                            <ChatMarkdown content={detail.content.slice(0, 3000) + (detail.content.length > 3000 ? '\n\n*... (truncated — view full in Deliverables tab)*' : '')} />
                          </div>
                        )}

                        {item.type === 'attention' && item.summary && (
                          <div className="prose prose-invert prose-sm max-w-none">
                            <ChatMarkdown content={item.summary} />
                          </div>
                        )}

                        {!detail?.content && !item.summary && !detailQuery.isLoading && (
                          <p className="text-sm text-gray-500 italic">No content preview available</p>
                        )}
                      </div>

                      {/* Tags */}
                      {item.tags && item.tags.length > 0 && (
                        <div className="px-4 pb-2 flex flex-wrap gap-1">
                          {item.tags.slice(0, 8).map(tag => (
                            <span key={tag} className="px-2 py-0.5 bg-gray-700/50 rounded text-xs text-gray-400">{tag}</span>
                          ))}
                        </div>
                      )}

                      {/* Action bar */}
                      <div className="flex items-center gap-2 px-4 py-3 bg-gray-900/30 border-t border-dark-border">
                        {item.type === 'deliverable' && (
                          <>
                            <button
                              onClick={() => onNavigateTab?.('deliverables')}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 rounded text-xs font-medium transition-colors"
                            >
                              <Eye size={12} /> View Full
                            </button>
                            <button
                              onClick={() => {
                                deliverablesApi.save(item.id).then(() => {
                                  queryClient.invalidateQueries({ queryKey: ['work-deliverables'] })
                                  queryClient.invalidateQueries({ queryKey: ['work-stats'] })
                                })
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded text-xs font-medium transition-colors"
                            >
                              <ThumbsUp size={12} /> Save
                            </button>
                            <button
                              onClick={() => {
                                deliverablesApi.export(item.id, 'pdf').then(r => {
                                  const url = window.URL.createObjectURL(r.data)
                                  const a = document.createElement('a')
                                  a.href = url
                                  a.download = `${item.title.slice(0, 50)}.pdf`
                                  a.click()
                                })
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700/50 text-gray-300 hover:bg-gray-700 rounded text-xs font-medium transition-colors"
                            >
                              <ExternalLink size={12} /> Export PDF
                            </button>
                          </>
                        )}

                        {item.type === 'attention' && (
                          <>
                            <button
                              onClick={async () => {
                                await fetch(`/api/human/attention/${item.id}/decide/`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  credentials: 'include',
                                  body: JSON.stringify({ decision: 'approve' }),
                                })
                                queryClient.invalidateQueries({ queryKey: ['work-attention'] })
                                setExpandedId(null)
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-green-500/20 text-green-400 hover:bg-green-500/30 rounded text-xs font-medium transition-colors"
                            >
                              <ThumbsUp size={12} /> Approve
                            </button>
                            <button
                              onClick={async () => {
                                await fetch(`/api/human/attention/${item.id}/decide/`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  credentials: 'include',
                                  body: JSON.stringify({ decision: 'reject' }),
                                })
                                queryClient.invalidateQueries({ queryKey: ['work-attention'] })
                                setExpandedId(null)
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/20 text-red-400 hover:bg-red-500/30 rounded text-xs font-medium transition-colors"
                            >
                              <ThumbsDown size={12} /> Reject
                            </button>
                            <button
                              onClick={async () => {
                                await fetch(`/api/human/attention/${item.id}/defer/`, {
                                  method: 'POST',
                                  headers: { 'Content-Type': 'application/json' },
                                  credentials: 'include',
                                })
                                queryClient.invalidateQueries({ queryKey: ['work-attention'] })
                                setExpandedId(null)
                              }}
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-700/50 text-gray-300 hover:bg-gray-700 rounded text-xs font-medium transition-colors"
                            >
                              <Clock size={12} /> Defer
                            </button>
                          </>
                        )}

                        <button
                          onClick={() => setExpandedId(null)}
                          className="ml-auto flex items-center gap-1 px-2 py-1.5 text-gray-500 hover:text-white text-xs transition-colors"
                        >
                          <X size={12} /> Close
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      )}

      {/* Recent Activity Feed */}
      {(activityQuery.data || []).length > 0 && (
        <div className="pt-4 border-t border-dark-border">
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <Clock size={14} /> Recent Activity
          </h3>
          <div className="space-y-1.5">
            {(activityQuery.data || []).map((op: Record<string, string>) => (
              <div key={op.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800/30 text-xs">
                <span className={cn('w-1.5 h-1.5 rounded-full flex-shrink-0', op.success !== false ? 'bg-green-400' : 'bg-red-400')} />
                <span className="text-gray-300 truncate flex-1">
                  {op.agent_name && <span className="text-primary-400">{op.agent_name}</span>}
                  {op.agent_name && ' — '}
                  {op.agent_task || op.description || op.operation_type || 'Operation'}
                </span>
                <span className="text-gray-600 whitespace-nowrap">{getAge(op.created_at)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
