// Session 927: Boardroom Tab - Decision Hub
// Session 942: Added bulk selection and bulk actions
// Session 956: Enhanced ML prediction display with confidence, reasoning, similar items
// Displays HumanAttentionItems and AgentDecisionSummary for review/action
import { useState, useEffect, useRef } from 'react'
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
  AlertTriangle,
  Bot,
  FileText,
  Lightbulb,
  TrendingUp,
  ChevronDown,
  ChevronRight,
  CheckSquare,
  Square,
  Brain,
  Sparkles,
  History,
  Code,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { humanApi, decisionsApi } from '@/lib/api'

// S3035: Recent canonical-lifecycle event (mirrors backend emit payload)
// S3036: schema_version 2 events add `actor` (source-of-transition — one of
// the values in `CANONICAL_LIFECYCLE_ACTORS` in
// `core/services/canonical_decision_broadcast.py`). Old v1 events already in
// the ring at deploy time have no `actor` — treated as 'unknown' via
// `resolveActorStyle` below.
interface LifecycleEvent {
  schema_version: number
  type: 'canonical_decision_promoted' | 'canonical_decision_rejected'
  actor?: string
  timestamp: string
  decision_id: string
  topic: string
  decision_type: string
  summary?: string
  participants?: string[]
}

// S3036: authoritative actor → pill styling map. Adding a new actor requires
// updating both this map AND `CANONICAL_LIFECYCLE_ACTORS` in the backend
// module. Any actor string not in this map (typo at a call site, or future
// backend actor that has not yet shipped its frontend palette entry) falls
// through to the neutral "unknown" pill — per Rigby S3036 T1 Fold #1
// (same_pr_mitigatable) — so mystery-string regressions never show up as
// broken UI.
const ACTOR_PILL_STYLES: Record<string, { label: string; className: string }> = {
  'human': { label: 'human', className: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  'human-bulk': { label: 'human-bulk', className: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' },
  'human-gate': { label: 'human-gate', className: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
  'pa-tool': { label: 'pa-tool', className: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  'ai-promoter': { label: 'ai-promoter', className: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  'ops-task': { label: 'ops-task', className: 'bg-teal-500/20 text-teal-300 border-teal-500/30' },
  'rules-service': { label: 'rules-service', className: 'bg-green-500/20 text-green-300 border-green-500/30' },
}

const UNKNOWN_ACTOR_STYLE = {
  label: 'unknown',
  className: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
}

function resolveActorStyle(actor: string | undefined): { label: string; className: string } {
  if (!actor) return UNKNOWN_ACTOR_STYLE
  return ACTOR_PILL_STYLES[actor] ?? UNKNOWN_ACTOR_STYLE
}

interface LifecycleActivityResponse {
  success: boolean
  // S3035 A2 fold: true iff Redis read failed → UI shows "feed temporarily
  // unavailable" instead of the merits-empty state.
  degraded?: boolean
  counters: { promoted_total: number; rejected_total: number }
  events: LifecycleEvent[]
}

// Session 956: Extended interface for ML prediction data
interface SimilarItem {
  id: string
  title: string
  decision: string
  similarity: number
}

interface MLPrediction {
  prediction: 'approve' | 'ignore' | 'uncertain'
  confidence?: number
  approval_probability?: number
  reasoning?: string
  similar_items?: SimilarItem[]
  predicted_at?: string
}

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
  ml_confidence?: number
  ml_prediction?: MLPrediction
  payload?: Record<string, unknown>
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

  // Session 942: Bulk selection state
  const [selectedAttention, setSelectedAttention] = useState<Set<string>>(new Set())
  const [selectedDecisions, setSelectedDecisions] = useState<Set<string>>(new Set())

  // S3035: Lifecycle Activity panel expand toggle
  const [lifecycleExpanded, setLifecycleExpanded] = useState(false)

  // Session 988: Track last visit for "NEW" badges
  const visitMarked = useRef(false)

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

  // S3035: Recent canonical-lifecycle activity (promoted + rejected across
  // all production emit-helper callers, not just boardroom clicks).
  const { data: lifecycleData } = useQuery<LifecycleActivityResponse>({
    queryKey: ['boardroom-lifecycle-activity'],
    queryFn: async () => {
      const res = await decisionsApi.lifecycleActivity()
      return res.data
    },
    refetchInterval: 10000,
  })

  const lifecycleCounters = lifecycleData?.counters ?? { promoted_total: 0, rejected_total: 0 }
  const lifecycleEvents = lifecycleData?.events ?? []
  const lifecycleDegraded = lifecycleData?.degraded ?? false

  // Attention item actions
  const decideMutation = useMutation({
    mutationFn: ({ itemId, decision }: { itemId: string; decision: string }) =>
      humanApi.decide(itemId, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
    },
  })

  // Session 942: Bulk attention actions
  const bulkDecideMutation = useMutation({
    mutationFn: ({ decision, itemIds }: { decision: string; itemIds: string[] }) =>
      humanApi.bulkDecide(decision, itemIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
      setSelectedAttention(new Set())
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

  // Session 942: Bulk decision actions
  const bulkPromoteMutation = useMutation({
    mutationFn: (decisionIds: string[]) => decisionsApi.bulkPromote(decisionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-decisions-list'] })
      setSelectedDecisions(new Set())
    },
  })

  const bulkRejectMutation = useMutation({
    mutationFn: (decisionIds: string[]) => decisionsApi.bulkReject(decisionIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-decisions-list'] })
      setSelectedDecisions(new Set())
    },
  })

  const attentionItems: AttentionItem[] = attentionData?.items || []
  const decisions: Decision[] = (decisionsData?.decisions || []).filter(
    (d: Decision) => d.status === 'draft'
  )

  // Session 988: "NEW" badge support
  const lastVisitedAt = attentionData?.last_visited_at as string | null | undefined
  const isNewItem = (createdAt: string) => {
    if (!lastVisitedAt) return false
    return new Date(createdAt) > new Date(lastVisitedAt)
  }
  const newAttentionCount = attentionItems.filter(i => isNewItem(i.created_at)).length
  const newDecisionCount = decisions.filter(d => isNewItem(d.created_at)).length
  const totalNewCount = newAttentionCount + newDecisionCount

  // Session 988: Mark visit after 3s delay so badges show briefly
  useEffect(() => {
    if (visitMarked.current) return
    const timer = setTimeout(() => {
      visitMarked.current = true
      humanApi.markBoardroomVisited().catch(() => {})
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

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

  // Session 942: Selection helpers
  const toggleAttentionSelection = (id: string) => {
    const newSelected = new Set(selectedAttention)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedAttention(newSelected)
  }

  const toggleDecisionSelection = (id: string) => {
    const newSelected = new Set(selectedDecisions)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedDecisions(newSelected)
  }

  const selectAllAttention = () => {
    if (selectedAttention.size === filteredAttention.length) {
      setSelectedAttention(new Set())
    } else {
      setSelectedAttention(new Set(filteredAttention.map(i => i.id)))
    }
  }

  const selectAllDecisions = () => {
    if (selectedDecisions.size === filteredDecisions.length) {
      setSelectedDecisions(new Set())
    } else {
      setSelectedDecisions(new Set(filteredDecisions.map(d => d.id)))
    }
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

  // Session 956: ML Prediction styling helpers
  const getMLRecommendationStyle = (recommendation: string) => {
    switch (recommendation) {
      case 'approve':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'ignore':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return 'bg-green-500'
    if (confidence >= 0.4) return 'bg-amber-500'
    return 'bg-gray-500'
  }

  // Session 956: ML Prediction Panel Component
  const MLPredictionPanel = ({ item }: { item: AttentionItem }) => {
    const [showSimilar, setShowSimilar] = useState(false)

    if (!item.ml_recommendation && !item.ml_prediction) return null

    const prediction = item.ml_prediction
    const confidence = item.ml_confidence ?? prediction?.confidence ?? 0
    if (confidence < 0.3) return null
    const confidencePercent = Math.round(confidence * 100)
    const approvalProb = prediction?.approval_probability ?? 0.5
    const approvalPercent = Math.round(approvalProb * 100)
    const reasoning = prediction?.reasoning || ''
    const reasoningParts = reasoning.split(' | ').filter(Boolean)
    const similarItems = prediction?.similar_items || []

    return (
      <div className="mt-3 space-y-3">
        {/* ML Header with recommendation and confidence */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <Brain size={16} className="text-primary-400" />
            <span className="text-sm font-medium text-gray-300">AI Prediction:</span>
          </div>

          {/* Recommendation badge */}
          <span className={cn(
            "px-2 py-0.5 text-xs font-medium rounded-full border capitalize",
            getMLRecommendationStyle(item.ml_recommendation || prediction?.prediction || 'uncertain')
          )}>
            {item.ml_recommendation || prediction?.prediction || 'uncertain'}
          </span>

          {/* Confidence bar */}
          {confidence > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Confidence:</span>
              <div className="w-20 h-2 bg-dark-border rounded-full overflow-hidden">
                <div
                  className={cn("h-full rounded-full transition-all", getConfidenceColor(confidence))}
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
              <span className="text-xs font-medium text-gray-400">{confidencePercent}%</span>
            </div>
          )}
        </div>

        {/* Approval probability gauge */}
        {prediction?.approval_probability !== undefined && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-24">Approval likelihood:</span>
            <div className="flex-1 h-3 bg-dark-border rounded-full overflow-hidden relative">
              {/* Red to green gradient background */}
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/30 via-amber-500/30 to-green-500/30" />
              {/* Approval probability marker */}
              <div
                className="absolute top-0 h-full w-1 bg-white rounded-full shadow-lg transition-all"
                style={{ left: `${approvalPercent}%`, transform: 'translateX(-50%)' }}
              />
            </div>
            <span className={cn(
              "text-xs font-medium min-w-[3rem] text-right",
              approvalPercent >= 60 ? "text-green-400" : approvalPercent >= 40 ? "text-amber-400" : "text-red-400"
            )}>
              {approvalPercent}%
            </span>
          </div>
        )}

        {/* Reasoning breakdown */}
        {reasoningParts.length > 0 && (
          <div className="space-y-1.5">
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Sparkles size={12} /> Signals:
            </span>
            <div className="flex flex-wrap gap-2">
              {reasoningParts.map((reason, idx) => (
                <span
                  key={idx}
                  className="px-2 py-1 text-xs bg-dark-border rounded-lg text-gray-400"
                >
                  {reason}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Similar items (collapsible) */}
        {similarItems.length > 0 && (
          <div>
            <button
              onClick={() => setShowSimilar(!showSimilar)}
              className="flex items-center gap-2 text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              <History size={12} />
              <span>Similar past decisions ({similarItems.length})</span>
              {showSimilar ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>

            {showSimilar && (
              <div className="mt-2 space-y-1.5 pl-4 border-l border-dark-border">
                {similarItems.slice(0, 5).map((similar, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between text-xs p-2 bg-dark-bg/50 rounded"
                  >
                    <span className="text-gray-400 truncate flex-1 mr-2">
                      {similar.title}
                    </span>
                    <div className="flex items-center gap-2 shrink-0">
                      <span className={cn(
                        "px-1.5 py-0.5 rounded text-[10px] font-medium",
                        similar.decision === 'approve' || similar.decision === 'approved'
                          ? "bg-green-500/20 text-green-400"
                          : "bg-red-500/20 text-red-400"
                      )}>
                        {similar.decision}
                      </span>
                      <span className="text-gray-600">
                        {Math.round(similar.similarity * 100)}% match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // Session 1067: Detect and clean raw Python dict/JSON summaries from spider data
  const cleanRawSummary = (text: string): string => {
    if (/^\s*\{.*'[a-z_]+':/i.test(text) || /^\s*\[?\s*\{.*"[a-z_]+":/i.test(text)) {
      try {
        const jsonStr = text.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false')
        const parsed = JSON.parse(jsonStr)
        if (parsed.items && Array.isArray(parsed.items)) {
          const titles = parsed.items.slice(0, 5).map((it: any) => it.title).filter(Boolean)
          if (titles.length) return titles.join(' | ')
        }
        for (const key of ['title', 'summary', 'description', 'content']) {
          if (parsed[key]) return String(parsed[key])
        }
      } catch {
        const titleMatches = text.match(/'title':\s*'([^']+)'/g)
        if (titleMatches) {
          return titleMatches.slice(0, 5).map(m => m.replace(/'title':\s*'/, '').replace(/'$/, '')).join(' | ')
        }
      }
      return 'Spider data (structured)'
    }
    return text
  }

  // Session 972: Strip provenance markdown header from agent messages
  const stripProvenance = (text: string): string => {
    return text.replace(/^---\n## Report Provenance[\s\S]*?---\n?/, '').trim()
  }

  // Strip markdown formatting for plain-text display
  const stripMarkdown = (text: string): string => {
    return text
      .replace(/^---\n[\s\S]*?---\n?/gm, '')    // provenance/hr blocks
      .replace(/^#{1,6}\s+/gm, '')                // heading markers
      .replace(/\*\*([^*]+)\*\*/g, '$1')          // **bold** → bold
      .replace(/\*([^*]+)\*/g, '$1')              // *italic* → italic
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')    // [text](url) → text
      .replace(/\n{3,}/g, '\n\n')                 // collapse multiple newlines
      .trim()
  }

  // Session 972: Extract the richest content from payload.result_data
  // Deep-searches sub-agent results (*_results.message, *_results.data.analysis)
  const extractResultContent = (resultData: unknown): string | null => {
    if (!resultData) return null
    if (typeof resultData === 'string') return resultData
    if (typeof resultData === 'object' && resultData !== null) {
      const data = resultData as Record<string, unknown>

      // 1. Try known content keys at top level (must be substantial)
      for (const key of ['report', 'analysis', 'content', 'output', 'message', 'result']) {
        if (typeof data[key] === 'string' && (data[key] as string).length > 100) {
          const cleaned = stripProvenance(data[key] as string)
          if (cleaned.length > 50) return cleaned
        }
      }

      // 2. Deep search: look for *_results objects with .message or .data.analysis
      const subResults: string[] = []
      for (const value of Object.values(data)) {
        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
          const sub = value as Record<string, unknown>
          // Check .data.analysis (rich analysis text)
          if (typeof sub.data === 'object' && sub.data !== null) {
            const subData = sub.data as Record<string, unknown>
            if (typeof subData.analysis === 'string' && subData.analysis.length > 50) {
              subResults.push(subData.analysis)
            }
          }
          // Check .message (agent output) — strip provenance header
          if (typeof sub.message === 'string' && sub.message.length > 100) {
            const cleaned = stripProvenance(sub.message)
            if (cleaned.length > 50) {
              subResults.push(cleaned)
            }
          }
        }
      }
      if (subResults.length > 0) {
        // Return the longest (richest) sub-result
        return subResults.sort((a, b) => b.length - a.length)[0]
      }

      // 3. Fall back to key-value pairs, skipping metadata fields
      const skipKeys = new Set(['discord_sent', 'validation_status', 'publishable', 'provenance'])
      const pairs = Object.entries(data)
        .filter(([k, v]) => !skipKeys.has(k) && (typeof v === 'string' || typeof v === 'number'))
        .map(([k, v]) => `${k}: ${v}`)
      if (pairs.length > 0) return pairs.join('\n')
    }
    return null
  }

  // Type-specific expanded content components
  const SpiderItemDetail = ({ data }: { data: Record<string, unknown> }) => (
    <div className="mt-2 space-y-1 text-sm">
      {!!data.source && <div className="text-gray-500">Source: <span className="text-gray-300">{String(data.source)}</span></div>}
      {!!data.url && (
        <a href={String(data.url)} target="_blank" rel="noopener noreferrer"
          className="text-primary-400 hover:underline text-xs truncate block">{String(data.url)}</a>
      )}
      {!!data.published && <div className="text-xs text-gray-500">Published: {new Date(String(data.published)).toLocaleString()}</div>}
    </div>
  )

  const ArbitrageDetail = ({ payload }: { payload: Record<string, unknown> }) => (
    <div className="mt-2 p-3 bg-dark-bg rounded-lg border border-dark-border space-y-2">
      <div className="flex items-center gap-4 text-sm">
        <span className="text-green-400 font-bold text-lg">{Number(payload.profit_pct || 0).toFixed(1)}% profit</span>
        <span className="text-gray-400">{String(payload.sport || '')}</span>
      </div>
      <div className="text-sm text-gray-300">{String(payload.away_team || '')} @ {String(payload.home_team || '')}</div>
      {payload.stake_home != null && (
        <div className="text-xs text-gray-500">
          Stakes: Home ${Number(payload.stake_home).toFixed(2)} / Away ${Number(payload.stake_away).toFixed(2)}
        </div>
      )}
    </div>
  )

  const ReviewDetail = ({ payload }: { payload: Record<string, unknown> }) => {
    const score = Number(payload.quality_score || 0)
    return (
      <div className="mt-2 flex items-center gap-3">
        <span className="text-xs text-gray-500">Quality:</span>
        <div className="w-32 h-2 bg-dark-border rounded-full overflow-hidden">
          <div className={cn("h-full rounded-full",
            score >= 70 ? "bg-green-500" : score >= 50 ? "bg-amber-500" : "bg-red-500"
          )} style={{ width: `${score}%` }} />
        </div>
        <span className="text-sm font-medium text-gray-300">{score}/100</span>
      </div>
    )
  }

  // Session 972: Attention Item Detail component for expanded view
  const AttentionItemDetail = ({ item }: { item: AttentionItem }) => {
    const [showRaw, setShowRaw] = useState(false)
    const [showFull, setShowFull] = useState(false)
    const TEXT_LIMIT = 5000

    const resultData = item.payload?.result_data
    const richContent = extractResultContent(resultData)
    const taskText = typeof item.payload?.task === 'string' ? item.payload.task : null
    const agentName = typeof item.payload?.agent_name === 'string' ? item.payload.agent_name : null

    // Clean summary: strip provenance header, skip if only metadata remains
    const cleanSummary = item.summary ? cleanRawSummary(stripProvenance(item.summary)) : null
    const showSummary = cleanSummary && cleanSummary.length > 10

    return (
      <div className="space-y-3 mt-2">
        {/* Summary (with provenance header stripped) */}
        {showSummary && cleanSummary && (
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{stripMarkdown(cleanSummary)}</p>
        )}

        {/* Type-specific expanded content */}
        {item.item_type === 'spider_action' && !!item.payload?.spider_item && (
          <SpiderItemDetail data={item.payload.spider_item as Record<string, unknown>} />
        )}
        {item.item_type === 'arbitrage' && item.payload?.profit_pct !== undefined && (
          <ArbitrageDetail payload={item.payload} />
        )}
        {item.item_type === 'review' && item.payload?.quality_score !== undefined && (
          <ReviewDetail payload={item.payload} />
        )}

        {/* Rich content from result_data */}
        {richContent && richContent !== item.summary && (
          <div className="mt-2">
            <span className="text-xs text-gray-500 uppercase font-medium">Agent Output</span>
            <div className="mt-1 p-3 bg-dark-bg rounded-lg border border-dark-border">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                {showFull ? richContent : (richContent.length > TEXT_LIMIT ? richContent.slice(0, TEXT_LIMIT) + '...' : richContent)}
              </pre>
              {richContent.length > TEXT_LIMIT && (
                <button
                  onClick={(e) => { e.stopPropagation(); setShowFull(!showFull) }}
                  className="mt-2 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                >
                  {showFull ? 'Show less' : `Show full (${Math.round(richContent.length / 1000)}k chars)`}
                </button>
              )}
            </div>
          </div>
        )}

        {/* Task and agent context */}
        {(taskText || agentName) && (
          <div className="flex items-center gap-4 text-xs text-gray-500">
            {agentName && <span>Agent: <span className="text-gray-400">{agentName}</span></span>}
            {taskText && <span className="truncate max-w-md">Task: <span className="text-gray-400">{taskText}</span></span>}
          </div>
        )}

        {/* ML Prediction */}
        <MLPredictionPanel item={item} />

        {/* Raw data toggle */}
        {item.payload && Object.keys(item.payload).length > 0 && (
          <div>
            <button
              onClick={(e) => { e.stopPropagation(); setShowRaw(!showRaw) }}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              <Code size={12} />
              <span>Raw Data</span>
              {showRaw ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            </button>
            {showRaw && (
              <pre className="mt-2 p-3 bg-dark-bg rounded-lg border border-dark-border text-xs text-gray-400 overflow-x-auto max-h-64 overflow-y-auto">
                {JSON.stringify(item.payload, null, 2)}
              </pre>
            )}
          </div>
        )}
      </div>
    )
  }

  const isBulkPending = bulkDecideMutation.isPending || bulkPromoteMutation.isPending || bulkRejectMutation.isPending

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

      {/* Session 988: New items banner */}
      {totalNewCount > 0 && (
        <div className="flex items-center gap-2 px-3 py-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-400">
          <span className="px-1.5 py-0.5 text-xs font-bold bg-blue-500 text-white rounded">NEW</span>
          {totalNewCount} new item{totalNewCount !== 1 ? 's' : ''} since your last visit
        </div>
      )}

      {/* S3035: Recent Lifecycle Activity — bounded ring of last 20 canonical
          promote/reject events across all production paths (boardroom clicks +
          AI-service auto-promotions + ops-task auto-approvals + PA tool). */}
      <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
        <button
          onClick={() => setLifecycleExpanded(!lifecycleExpanded)}
          className="w-full flex items-center gap-3 px-3 py-2 hover:bg-dark-border/30 transition-colors"
        >
          <Activity size={16} className="text-primary-400" />
          <span className="text-sm font-medium">Recent Lifecycle Activity</span>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-green-400">
              <CheckCircle size={12} />
              {lifecycleCounters.promoted_total} promoted
            </span>
            <span className="flex items-center gap-1 text-red-400">
              <XCircle size={12} />
              {lifecycleCounters.rejected_total} rejected
            </span>
          </div>
          <div className="flex-1" />
          <span className="text-xs text-gray-500">last {lifecycleEvents.length}</span>
          {lifecycleExpanded ? (
            <ChevronDown size={14} className="text-gray-400" />
          ) : (
            <ChevronRight size={14} className="text-gray-400" />
          )}
        </button>
        {lifecycleExpanded && (
          <div className="border-t border-dark-border max-h-64 overflow-y-auto">
            {lifecycleEvents.length === 0 ? (
              <p className="text-xs text-gray-500 text-center py-4">
                {lifecycleDegraded
                  ? 'Activity feed temporarily unavailable (Redis read failed). Counters and events will refresh once the backend recovers.'
                  : 'No recent lifecycle events. Promote or reject a draft decision to populate the feed.'}
              </p>
            ) : (
              <ul className="divide-y divide-dark-border">
                {lifecycleEvents.map((event, idx) => {
                  const isPromoted = event.type === 'canonical_decision_promoted'
                  const actorStyle = resolveActorStyle(event.actor)
                  return (
                    <li
                      key={`${event.decision_id}-${idx}`}
                      className="flex items-center gap-3 px-3 py-2 text-xs"
                    >
                      <span
                        className={cn(
                          'flex items-center gap-1 px-1.5 py-0.5 rounded border',
                          isPromoted
                            ? 'bg-green-500/20 text-green-400 border-green-500/30'
                            : 'bg-red-500/20 text-red-400 border-red-500/30'
                        )}
                      >
                        {isPromoted ? <CheckCircle size={10} /> : <XCircle size={10} />}
                        {isPromoted ? 'promoted' : 'rejected'}
                      </span>
                      <span
                        className={cn(
                          'px-1.5 py-0.5 rounded border shrink-0',
                          actorStyle.className
                        )}
                        title={`Actor: ${actorStyle.label}`}
                      >
                        {actorStyle.label}
                      </span>
                      <span className="text-gray-300 truncate flex-1" title={event.topic}>
                        {event.topic}
                      </span>
                      <span className="px-1.5 py-0.5 rounded bg-dark-border text-gray-400 shrink-0">
                        {event.decision_type}
                      </span>
                      <span className="text-gray-500 shrink-0">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        )}
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
          {/* Filters + Select All */}
          <div className="flex items-center justify-between flex-wrap gap-2">
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
            {/* Select All checkbox */}
            {filteredAttention.length > 0 && (
              <button
                onClick={selectAllAttention}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-dark-border rounded-lg hover:bg-dark-border/80 transition-colors"
              >
                {selectedAttention.size === filteredAttention.length ? (
                  <CheckSquare size={16} className="text-primary-400" />
                ) : (
                  <Square size={16} className="text-gray-400" />
                )}
                Select All ({filteredAttention.length})
              </button>
            )}
          </div>

          {/* Session 942: Bulk Action Bar */}
          {selectedAttention.size > 0 && (
            <div className="flex items-center gap-3 p-3 bg-primary-500/10 border border-primary-500/30 rounded-lg">
              <span className="text-sm font-medium text-primary-400">
                {selectedAttention.size} selected
              </span>
              <div className="flex-1" />
              <button
                onClick={() => bulkDecideMutation.mutate({ decision: 'approved', itemIds: Array.from(selectedAttention) })}
                disabled={isBulkPending}
                className="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors disabled:opacity-50"
              >
                {isBulkPending ? <Loader2 size={14} className="animate-spin" /> : <ThumbsUp size={14} />}
                Approve All
              </button>
              <button
                onClick={() => bulkDecideMutation.mutate({ decision: 'ignored', itemIds: Array.from(selectedAttention) })}
                disabled={isBulkPending}
                className="flex items-center gap-2 px-3 py-1.5 bg-gray-500/20 text-gray-400 rounded-lg hover:bg-gray-500/30 transition-colors disabled:opacity-50"
              >
                {isBulkPending ? <Loader2 size={14} className="animate-spin" /> : <ThumbsDown size={14} />}
                Ignore All
              </button>
              <button
                onClick={() => setSelectedAttention(new Set())}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Clear
              </button>
            </div>
          )}

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
                  className={cn(
                    "bg-dark-card border rounded-lg overflow-hidden",
                    selectedAttention.has(item.id) ? "border-primary-500/50" : "border-dark-border"
                  )}
                >
                  <div
                    className="flex items-start gap-3 p-3 cursor-pointer hover:bg-dark-border/30 transition-colors"
                    onClick={() => toggleExpanded(item.id)}
                  >
                    {/* Checkbox */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleAttentionSelection(item.id)
                      }}
                      className="mt-1 flex-shrink-0"
                    >
                      {selectedAttention.has(item.id) ? (
                        <CheckSquare size={18} className="text-primary-400" />
                      ) : (
                        <Square size={18} className="text-gray-500 hover:text-gray-300" />
                      )}
                    </button>
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
                        {/* Session 988: NEW badge */}
                        {isNewItem(item.created_at) && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-500 text-white rounded">
                            NEW
                          </span>
                        )}
                        {/* Session 956: ML prediction indicator badge (hidden below 30% confidence) */}
                        {(item.ml_recommendation || item.ml_prediction) && (item.ml_confidence ?? 0) >= 0.3 && (
                          <span className={cn(
                            "flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded border",
                            getMLRecommendationStyle(item.ml_recommendation || item.ml_prediction?.prediction || 'uncertain')
                          )}>
                            <Brain size={10} />
                            {item.ml_confidence ? `${Math.round(item.ml_confidence * 100)}%` : 'AI'}
                          </span>
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
                      {/* Session 972: Full attention item detail with payload rendering */}
                      <AttentionItemDetail item={item} />
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
          {/* Filters + Select All */}
          <div className="flex items-center justify-between flex-wrap gap-2">
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
            {/* Select All checkbox */}
            {filteredDecisions.length > 0 && (
              <button
                onClick={selectAllDecisions}
                className="flex items-center gap-2 px-3 py-1 text-sm bg-dark-border rounded-lg hover:bg-dark-border/80 transition-colors"
              >
                {selectedDecisions.size === filteredDecisions.length ? (
                  <CheckSquare size={16} className="text-primary-400" />
                ) : (
                  <Square size={16} className="text-gray-400" />
                )}
                Select All ({filteredDecisions.length})
              </button>
            )}
          </div>

          {/* Session 942: Bulk Action Bar */}
          {selectedDecisions.size > 0 && (
            <div className="flex items-center gap-3 p-3 bg-primary-500/10 border border-primary-500/30 rounded-lg">
              <span className="text-sm font-medium text-primary-400">
                {selectedDecisions.size} selected
              </span>
              <div className="flex-1" />
              <button
                onClick={() => bulkPromoteMutation.mutate(Array.from(selectedDecisions))}
                disabled={isBulkPending}
                className="flex items-center gap-2 px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors disabled:opacity-50"
              >
                {isBulkPending ? <Loader2 size={14} className="animate-spin" /> : <CheckCircle size={14} />}
                Promote All
              </button>
              <button
                onClick={() => bulkRejectMutation.mutate(Array.from(selectedDecisions))}
                disabled={isBulkPending}
                className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors disabled:opacity-50"
              >
                {isBulkPending ? <Loader2 size={14} className="animate-spin" /> : <XCircle size={14} />}
                Reject All
              </button>
              <button
                onClick={() => setSelectedDecisions(new Set())}
                className="px-3 py-1.5 text-sm text-gray-400 hover:text-white transition-colors"
              >
                Clear
              </button>
            </div>
          )}

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
                  className={cn(
                    "bg-dark-card border rounded-lg overflow-hidden",
                    selectedDecisions.has(decision.id) ? "border-primary-500/50" : "border-dark-border"
                  )}
                >
                  <div
                    className="flex items-start gap-3 p-3 cursor-pointer hover:bg-dark-border/30 transition-colors"
                    onClick={() => toggleExpanded(decision.id)}
                  >
                    {/* Checkbox */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleDecisionSelection(decision.id)
                      }}
                      className="mt-1 flex-shrink-0"
                    >
                      {selectedDecisions.has(decision.id) ? (
                        <CheckSquare size={18} className="text-primary-400" />
                      ) : (
                        <Square size={18} className="text-gray-500 hover:text-gray-300" />
                      )}
                    </button>
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
                        {/* Session 988: NEW badge */}
                        {isNewItem(decision.created_at) && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-500 text-white rounded">
                            NEW
                          </span>
                        )}
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
