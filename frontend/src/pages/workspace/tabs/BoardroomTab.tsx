// Session 927: Boardroom Tab - Decision Hub
// Displays HumanAttentionItems and AgentDecisionSummary for review/action
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Gavel,
  CheckCircle,
  XCircle,
  Eye,
  Loader2,
  RefreshCw,
  Filter,
  ThumbsUp,
  ThumbsDown,
  Clock,
  AlertTriangle,
  Bot,
  FileText,
  Lightbulb,
  TrendingUp,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { humanApi, decisionsApi } from '@/lib/api'

interface AttentionItem {
  id: string
  title: string
  summary?: string
  item_type: string
  source_type: string
  source_agent?: string
  urgency: 'critical' | 'high' | 'medium' | 'low'
  status: string
  created_at: string
  ml_recommendation?: string
}

interface Decision {
  id: string
  topic: string
  decision_type: string
  decision_type_display: string
  impact_area: string
  impact_area_display: string
  key_insights: string[]
  recommended_stance: string
  suggested_feature?: string
  status: string
  created_at: string
  participants?: string[]
}

type TabView = 'attention' | 'decisions'
type AttentionFilter = 'all' | 'review' | 'insight' | 'alert' | 'opportunity'
type DecisionFilter = 'all' | 'product' | 'experiment' | 'pipeline' | 'research'

export function BoardroomTab() {
  const queryClient = useQueryClient()
  const [activeView, setActiveView] = useState<TabView>('attention')
  const [attentionFilter, setAttentionFilter] = useState<AttentionFilter>('all')
  const [decisionFilter, setDecisionFilter] = useState<DecisionFilter>('all')
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set())
  const [selectedItem, setSelectedItem] = useState<AttentionItem | null>(null)
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null)

  // Fetch attention items
  const {
    data: attentionData,
    isLoading: loadingAttention,
    refetch: refetchAttention,
  } = useQuery({
    queryKey: ['boardroom-attention'],
    queryFn: async () => {
      const res = await humanApi.attention({ limit: 100, status: ['pending'] })
      return res.data
    },
    refetchInterval: 30000,
  })

  // Fetch decisions
  const {
    data: decisionsData,
    isLoading: loadingDecisions,
    refetch: refetchDecisions,
  } = useQuery({
    queryKey: ['boardroom-decisions-list'],
    queryFn: async () => {
      const res = await decisionsApi.list(100)
      return res.data
    },
    refetchInterval: 30000,
  })

  // Attention item actions
  const decideMutation = useMutation({
    mutationFn: ({ itemId, decision }: { itemId: string; decision: string }) =>
      humanApi.decide(itemId, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
    },
  })

  // Decision actions
  const promoteMutation = useMutation({
    mutationFn: (decisionId: string) => decisionsApi.promote(decisionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-decisions-list'] })
    },
  })

  const rejectMutation = useMutation({
    mutationFn: (decisionId: string) => decisionsApi.reject(decisionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-decisions-list'] })
    },
  })

  const attentionItems: AttentionItem[] = attentionData?.items || []
  const decisions: Decision[] = (decisionsData?.decisions || []).filter(
    (d: Decision) => d.status === 'draft'
  )

  // Filter items
  const filteredAttention = attentionItems.filter((item) => {
    if (attentionFilter === 'all') return true
    return item.item_type === attentionFilter
  })

  const filteredDecisions = decisions.filter((d) => {
    if (decisionFilter === 'all') return true
    return d.decision_type === decisionFilter
  })

  // Count by type
  const attentionCounts = {
    all: attentionItems.length,
    review: attentionItems.filter((i) => i.item_type === 'review').length,
    insight: attentionItems.filter((i) => i.item_type === 'insight').length,
    alert: attentionItems.filter((i) => i.item_type === 'alert').length,
    opportunity: attentionItems.filter((i) => i.item_type === 'opportunity').length,
  }

  const decisionCounts = {
    all: decisions.length,
    product: decisions.filter((d) => d.decision_type === 'product').length,
    experiment: decisions.filter((d) => d.decision_type === 'experiment').length,
    pipeline: decisions.filter((d) => d.decision_type === 'pipeline').length,
    research: decisions.filter((d) => d.decision_type === 'research').length,
  }

  const toggleExpanded = (id: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedItems(newExpanded)
  }

  const getUrgencyStyle = (urgency: string) => {
    switch (urgency) {
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      case 'high':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
      case 'medium':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'review':
        return <FileText size={14} />
      case 'insight':
        return <Lightbulb size={14} />
      case 'alert':
        return <AlertTriangle size={14} />
      case 'opportunity':
        return <TrendingUp size={14} />
      default:
        return <Bot size={14} />
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Gavel className="text-primary-400" size={20} />
          <h2 className="text-lg font-semibold">Boardroom</h2>
          <span className="text-sm text-gray-400">
            {attentionItems.length + decisions.length} items awaiting decision
          </span>
        </div>
        <button
          onClick={() => {
            refetchAttention()
            refetchDecisions()
          }}
          className="p-2 hover:bg-dark-border rounded-lg transition-colors"
        >
          <RefreshCw
            size={16}
            className={loadingAttention || loadingDecisions ? 'animate-spin' : ''}
          />
        </button>
      </div>

      {/* View Toggle */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        <button
          onClick={() => setActiveView('attention')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors',
            activeView === 'attention'
              ? 'bg-primary-500/20 text-primary-400 border-b-2 border-primary-500'
              : 'text-gray-400 hover:text-white'
          )}
        >
          <Eye size={16} />
          Attention Items
          <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-dark-border">
            {attentionItems.length}
          </span>
        </button>
        <button
          onClick={() => setActiveView('decisions')}
          className={cn(
            'flex items-center gap-2 px-4 py-2 rounded-t-lg font-medium transition-colors',
            activeView === 'decisions'
              ? 'bg-primary-500/20 text-primary-400 border-b-2 border-primary-500'
              : 'text-gray-400 hover:text-white'
          )}
        >
          <Gavel size={16} />
          Draft Decisions
          <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-dark-border">
            {decisions.length}
          </span>
        </button>
      </div>

      {/* Attention Items View */}
      {activeView === 'attention' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-2 flex-wrap">
            <Filter size={14} className="text-gray-400" />
            {(['all', 'review', 'insight', 'alert', 'opportunity'] as AttentionFilter[]).map(
              (filter) => (
                <button
                  key={filter}
                  onClick={() => setAttentionFilter(filter)}
                  className={cn(
                    'px-3 py-1 text-sm rounded-full transition-colors',
                    attentionFilter === filter
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-border text-gray-400 hover:text-white'
                  )}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                  <span className="ml-1 opacity-70">({attentionCounts[filter]})</span>
                </button>
              )
            )}
          </div>

          {/* Items List */}
          {loadingAttention ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={24} />
            </div>
          ) : filteredAttention.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={32} />
              <p>No pending attention items</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredAttention.map((item) => (
                <div
                  key={item.id}
                  className="bg-dark-card border border-dark-border rounded-lg overflow-hidden"
                >
                  <div
                    className="flex items-start gap-3 p-3 cursor-pointer hover:bg-dark-border/30 transition-colors"
                    onClick={() => toggleExpanded(item.id)}
                  >
                    <div className="mt-1">
                      {expandedItems.has(item.id) ? (
                        <ChevronDown size={16} className="text-gray-400" />
                      ) : (
                        <ChevronRight size={16} className="text-gray-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span
                          className={cn(
                            'flex items-center gap-1 px-2 py-0.5 text-xs rounded border',
                            getUrgencyStyle(item.urgency)
                          )}
                        >
                          {item.urgency}
                        </span>
                        <span className="flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-dark-border text-gray-400">
                          {getTypeIcon(item.item_type)}
                          {item.item_type}
                        </span>
                        {item.source_agent && (
                          <span className="text-xs text-gray-500">{item.source_agent}</span>
                        )}
                      </div>
                      <h4 className="font-medium text-sm truncate">{item.title}</h4>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(item.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => decideMutation.mutate({ itemId: item.id, decision: 'approved' })}
                        disabled={decideMutation.isPending}
                        className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                        title="Approve"
                      >
                        <ThumbsUp size={14} />
                      </button>
                      <button
                        onClick={() => decideMutation.mutate({ itemId: item.id, decision: 'ignored' })}
                        disabled={decideMutation.isPending}
                        className="p-2 rounded-lg bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 transition-colors"
                        title="Ignore"
                      >
                        <ThumbsDown size={14} />
                      </button>
                    </div>
                  </div>
                  {expandedItems.has(item.id) && (
                    <div className="px-4 pb-3 pt-0 border-t border-dark-border bg-dark-bg/50">
                      {item.summary && (
                        <p className="text-sm text-gray-300 mt-2">{item.summary}</p>
                      )}
                      {item.ml_recommendation && (
                        <div className="mt-2 p-2 bg-primary-500/10 rounded text-sm">
                          <span className="text-primary-400 font-medium">AI Recommendation:</span>{' '}
                          {item.ml_recommendation}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Decisions View */}
      {activeView === 'decisions' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex items-center gap-2 flex-wrap">
            <Filter size={14} className="text-gray-400" />
            {(['all', 'product', 'experiment', 'pipeline', 'research'] as DecisionFilter[]).map(
              (filter) => (
                <button
                  key={filter}
                  onClick={() => setDecisionFilter(filter)}
                  className={cn(
                    'px-3 py-1 text-sm rounded-full transition-colors',
                    decisionFilter === filter
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-border text-gray-400 hover:text-white'
                  )}
                >
                  {filter.charAt(0).toUpperCase() + filter.slice(1)}
                  <span className="ml-1 opacity-70">({decisionCounts[filter]})</span>
                </button>
              )
            )}
          </div>

          {/* Decisions List */}
          {loadingDecisions ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin text-primary-400" size={24} />
            </div>
          ) : filteredDecisions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={32} />
              <p>No draft decisions</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredDecisions.map((decision) => (
                <div
                  key={decision.id}
                  className="bg-dark-card border border-dark-border rounded-lg overflow-hidden"
                >
                  <div
                    className="flex items-start gap-3 p-3 cursor-pointer hover:bg-dark-border/30 transition-colors"
                    onClick={() => toggleExpanded(decision.id)}
                  >
                    <div className="mt-1">
                      {expandedItems.has(decision.id) ? (
                        <ChevronDown size={16} className="text-gray-400" />
                      ) : (
                        <ChevronRight size={16} className="text-gray-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <span className="px-2 py-0.5 text-xs rounded bg-purple-500/20 text-purple-400">
                          {decision.decision_type_display || decision.decision_type}
                        </span>
                        <span className="px-2 py-0.5 text-xs rounded bg-dark-border text-gray-400">
                          {decision.impact_area_display || decision.impact_area}
                        </span>
                      </div>
                      <h4 className="font-medium text-sm line-clamp-2">{decision.topic}</h4>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(decision.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => promoteMutation.mutate(decision.id)}
                        disabled={promoteMutation.isPending}
                        className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                        title="Promote to Canonical"
                      >
                        <CheckCircle size={14} />
                      </button>
                      <button
                        onClick={() => rejectMutation.mutate(decision.id)}
                        disabled={rejectMutation.isPending}
                        className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                        title="Reject"
                      >
                        <XCircle size={14} />
                      </button>
                    </div>
                  </div>
                  {expandedItems.has(decision.id) && (
                    <div className="px-4 pb-3 pt-0 border-t border-dark-border bg-dark-bg/50">
                      {decision.recommended_stance && (
                        <div className="mt-2">
                          <span className="text-xs text-gray-400 uppercase">Recommended Stance:</span>
                          <p className="text-sm text-gray-300 mt-1">{decision.recommended_stance}</p>
                        </div>
                      )}
                      {decision.key_insights && decision.key_insights.length > 0 && (
                        <div className="mt-2">
                          <span className="text-xs text-gray-400 uppercase">Key Insights:</span>
                          <ul className="text-sm text-gray-300 mt-1 list-disc list-inside">
                            {decision.key_insights.slice(0, 3).map((insight, idx) => (
                              <li key={idx}>{insight}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {decision.suggested_feature && (
                        <div className="mt-2 p-2 bg-primary-500/10 rounded text-sm">
                          <span className="text-primary-400 font-medium">Suggested Feature:</span>{' '}
                          {decision.suggested_feature}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
