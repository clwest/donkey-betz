/**
 * Project Hub — unified view of everything under one project.
 * Shows deliverables, initiatives, conversations, and stats in one place.
 */

import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  ArrowLeft, FileText, Lightbulb, MessageSquare, BarChart3,
  Clock, Loader2, ChevronDown, ChevronUp, Package, Bot,
  CheckCircle, AlertCircle, Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// ── Types ──────────────────────────────────────────────────────────────────

interface Deliverable {
  id: string
  title: string
  type: string
  category: string
  status: string
  agent_name: string
  quality_score: number
  word_count: number
  created_at: string | null
  preview: string
}

interface Initiative {
  id: string
  name: string
  status: string
  current_stage: number
  priority_score: number | null
  purpose: string
  program: string
  updated_at: string | null
}

interface Conversation {
  conversation_id: string
  title: string
  message_count: number
  last_at: string | null
}

interface HubData {
  project: { id: string; name: string; description: string }
  deliverables: Deliverable[]
  initiatives: Initiative[]
  conversations: Conversation[]
  stats: {
    total_deliverables: number
    total_initiatives: number
    total_conversations: number
    deliverables_by_type: Record<string, number>
    deliverables_by_status: Record<string, number>
  }
}

type Tab = 'overview' | 'deliverables' | 'initiatives' | 'conversations'

// ── Helpers ────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  completed: 'bg-green-500/20 text-green-400',
  ready: 'bg-blue-500/20 text-blue-400',
  published: 'bg-emerald-500/20 text-emerald-400',
  draft: 'bg-yellow-500/20 text-yellow-400',
  COMPLETED: 'bg-green-500/20 text-green-400',
  ACTIVE: 'bg-blue-500/20 text-blue-400',
  TRIAGE: 'bg-yellow-500/20 text-yellow-400',
}

function StatusBadge({ status }: { status: string }) {
  return (
    <span className={cn('text-[10px] px-1.5 py-0.5 rounded font-medium', STATUS_COLORS[status] || 'bg-gray-500/20 text-gray-400')}>
      {status}
    </span>
  )
}

function formatDate(iso: string | null): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// ── Main Component ─────────────────────────────────────────────────────────

export default function ProjectHubPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<Tab>('overview')
  const [expandedDeliverable, setExpandedDeliverable] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery<HubData>({
    queryKey: ['project-hub', projectId],
    queryFn: () => api.get(`/projects/${projectId}/hub/`).then(r => r.data),
    enabled: !!projectId,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-400" />
      </div>
    )
  }

  if (error) return <ErrorState error={error} />
  if (!data) return null

  const { project, deliverables, initiatives, conversations, stats } = data

  // Group deliverables by category
  const byCategory: Record<string, Deliverable[]> = {}
  for (const d of deliverables) {
    const cat = d.category || 'Uncategorized'
    if (!byCategory[cat]) byCategory[cat] = []
    byCategory[cat].push(d)
  }

  const tabs: { id: Tab; label: string; icon: React.ElementType; count: number }[] = [
    { id: 'overview', label: 'Overview', icon: BarChart3, count: 0 },
    { id: 'deliverables', label: 'Deliverables', icon: FileText, count: stats.total_deliverables },
    { id: 'initiatives', label: 'Initiatives', icon: Lightbulb, count: stats.total_initiatives },
    { id: 'conversations', label: 'Conversations', icon: MessageSquare, count: stats.total_conversations },
  ]

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={() => navigate('/projects')}
          className="p-2 rounded-lg hover:bg-dark-border transition-colors"
        >
          <ArrowLeft size={18} />
        </button>
        <div>
          <h1 className="text-2xl font-bold">{project.name}</h1>
          {project.description && <p className="text-sm text-gray-400 mt-0.5">{project.description}</p>}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 p-1 bg-dark-bg rounded-lg w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
              activeTab === tab.id ? 'bg-primary-600 text-white' : 'text-gray-400 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
            {tab.count > 0 && (
              <span className={cn(
                'text-[10px] px-1.5 py-0.5 rounded-full',
                activeTab === tab.id ? 'bg-white/20' : 'bg-dark-border'
              )}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-dark-card border border-dark-border">
              <div className="flex items-center gap-2 mb-2">
                <FileText size={16} className="text-primary-400" />
                <span className="text-sm text-gray-400">Deliverables</span>
              </div>
              <p className="text-2xl font-bold">{stats.total_deliverables}</p>
              <div className="flex gap-2 mt-2 flex-wrap">
                {Object.entries(stats.deliverables_by_status).map(([status, count]) => (
                  <span key={status} className="text-[10px] text-gray-500">{count} {status}</span>
                ))}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-dark-card border border-dark-border">
              <div className="flex items-center gap-2 mb-2">
                <Lightbulb size={16} className="text-yellow-400" />
                <span className="text-sm text-gray-400">Initiatives</span>
              </div>
              <p className="text-2xl font-bold">{stats.total_initiatives}</p>
            </div>
            <div className="p-4 rounded-xl bg-dark-card border border-dark-border">
              <div className="flex items-center gap-2 mb-2">
                <MessageSquare size={16} className="text-emerald-400" />
                <span className="text-sm text-gray-400">Conversations</span>
              </div>
              <p className="text-2xl font-bold">{stats.total_conversations}</p>
            </div>
          </div>

          {/* Recent deliverables */}
          <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">Recent Deliverables</h3>
            <div className="space-y-2">
              {deliverables.slice(0, 5).map((d) => (
                <div
                  key={d.id}
                  className="p-3 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors cursor-pointer"
                  onClick={() => { setActiveTab('deliverables'); setExpandedDeliverable(d.id) }}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <Package size={14} className="text-primary-400 flex-shrink-0" />
                      <span className="text-sm font-medium truncate">{d.title}</span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <StatusBadge status={d.status} />
                      <span className="text-[10px] text-gray-500">{formatDate(d.created_at)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent initiatives */}
          {initiatives.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-400 mb-3">Initiatives</h3>
              <div className="space-y-2">
                {initiatives.map((i) => (
                  <div key={i.id} className="p-3 rounded-lg bg-dark-card border border-dark-border">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Lightbulb size={14} className="text-yellow-400" />
                        <span className="text-sm font-medium">{i.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <StatusBadge status={i.status} />
                        <span className="text-[10px] text-gray-500">Stage {i.current_stage}/5</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Deliverables Tab */}
      {activeTab === 'deliverables' && (
        <div className="space-y-6">
          {Object.entries(byCategory).map(([category, items]) => (
            <div key={category}>
              <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
                <span>{category}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-dark-border">{items.length}</span>
              </h3>
              <div className="space-y-2">
                {items.map((d) => (
                  <div key={d.id} className="rounded-lg bg-dark-card border border-dark-border overflow-hidden">
                    <button
                      onClick={() => setExpandedDeliverable(expandedDeliverable === d.id ? null : d.id)}
                      className="w-full p-3 flex items-center justify-between hover:bg-dark-border/30 transition-colors"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <Package size={14} className="text-primary-400 flex-shrink-0" />
                        <div className="text-left min-w-0">
                          <p className="text-sm font-medium truncate">{d.title}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-[10px] text-gray-500">{d.type}</span>
                            {d.agent_name && <span className="text-[10px] text-gray-500">by {d.agent_name}</span>}
                            {d.word_count > 0 && <span className="text-[10px] text-gray-500">{d.word_count} words</span>}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <StatusBadge status={d.status} />
                        <span className="text-[10px] text-gray-500">{formatDate(d.created_at)}</span>
                        {expandedDeliverable === d.id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </div>
                    </button>
                    {expandedDeliverable === d.id && d.preview && (
                      <div className="px-4 pb-4 border-t border-dark-border/50">
                        <div className="mt-3 text-sm text-gray-300 prose prose-invert prose-sm max-w-none">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>{d.preview}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Initiatives Tab */}
      {activeTab === 'initiatives' && (
        <div className="space-y-3">
          {initiatives.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Lightbulb size={32} className="mx-auto mb-3 opacity-40" />
              <p>No initiatives for this project</p>
            </div>
          ) : (
            initiatives.map((i) => (
              <div key={i.id} className="p-4 rounded-xl bg-dark-card border border-dark-border">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">{i.name}</h3>
                  <StatusBadge status={i.status} />
                </div>
                <div className="flex items-center gap-4 text-xs text-gray-400">
                  <span>Stage {i.current_stage}/5</span>
                  {i.purpose && <span>{i.purpose}</span>}
                  {i.program && <span>{i.program}</span>}
                  {i.updated_at && <span>{formatDate(i.updated_at)}</span>}
                </div>
                {/* Stage progress bar */}
                <div className="flex gap-1 mt-3">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <div
                      key={s}
                      className={cn(
                        'h-1.5 flex-1 rounded-full',
                        s <= i.current_stage ? 'bg-primary-500' : 'bg-dark-border'
                      )}
                    />
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Conversations Tab */}
      {activeTab === 'conversations' && (
        <div className="space-y-3">
          {conversations.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <MessageSquare size={32} className="mx-auto mb-3 opacity-40" />
              <p>No conversations for this project</p>
            </div>
          ) : (
            conversations.map((c) => (
              <div
                key={c.conversation_id}
                className="p-4 rounded-xl bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors cursor-pointer"
                onClick={() => navigate(`/?conversation=${c.conversation_id}`)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Bot size={14} className="text-primary-400" />
                    <span className="font-medium text-sm">{c.title}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>{c.message_count} messages</span>
                    {c.last_at && <span>{formatDate(c.last_at)}</span>}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}
