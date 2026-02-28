// Session 1067: Full-page Boardroom — elevated from workspace tab
// Summary cards, filter bar, search, two tabs, slide-over drawer, bulk actions
import { useState, useEffect, useRef, useCallback } from 'react'
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
  Search,
  X,
  Clock,
  ArrowUpDown,
  Timer,
  Target,
  BarChart3,
  ShieldAlert,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { humanApi, decisionsApi, classificationApi } from '@/lib/api'

// --- Types (mirrored from BoardroomTab) ---

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
  decision_feedback?: string
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

// Session 1070: Added 'classify' tab for decision gates
interface UnclassifiedArtifact {
  id: string
  type: string
  type_display: string
  title: string
  description: string
  source_agent?: string
  composite_score: number
  classified: boolean
  classification: Record<string, string>
  extracted_at?: string
}

const WHAT_IS_THIS_OPTIONS = [
  { value: 'research_finding', label: 'Research Finding' },
  { value: 'actionable_recommendation', label: 'Actionable Recommendation' },
  { value: 'scope_change', label: 'Scope Change' },
  { value: 'risk_flag', label: 'Risk Flag' },
  { value: 'informational', label: 'Informational' },
]
const WHO_IS_IT_FOR_OPTIONS = [
  { value: 'platform', label: 'Platform' },
  { value: 'end_users', label: 'End Users' },
  { value: 'founder', label: 'Founder' },
  { value: 'agents', label: 'Agents' },
  { value: 'public', label: 'Public' },
]
const DATA_ALLOWED_OPTIONS = [
  { value: 'public_only', label: 'Public Only' },
  { value: 'internal_ops', label: 'Internal Ops' },
  { value: 'api_data', label: 'API Data' },
  { value: 'user_data', label: 'User Data' },
  { value: 'all', label: 'All' },
]
const PHASE_APPROVED_OPTIONS = [
  { value: 'research', label: 'Research' },
  { value: 'prototype', label: 'Prototype' },
  { value: 'pilot', label: 'Pilot' },
  { value: 'production', label: 'Production' },
  { value: 'none', label: 'None' },
]

type TabView = 'inbox' | 'history' | 'classify'
type UrgencyFilter = 'all' | 'critical' | 'high' | 'medium' | 'low'
type SortOption = 'newest' | 'oldest' | 'urgency'

// --- Helpers ---

const getUrgencyStyle = (urgency: string) => {
  switch (urgency) {
    case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30'
    case 'high': return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    case 'medium': return 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'review': return <FileText size={14} />
    case 'insight': return <Lightbulb size={14} />
    case 'alert': return <AlertTriangle size={14} />
    case 'opportunity': return <TrendingUp size={14} />
    default: return <Bot size={14} />
  }
}

const getMLRecommendationStyle = (recommendation: string) => {
  switch (recommendation) {
    case 'approve': return 'bg-green-500/20 text-green-400 border-green-500/30'
    case 'ignore': return 'bg-red-500/20 text-red-400 border-red-500/30'
    default: return 'bg-amber-500/20 text-amber-400 border-amber-500/30'
  }
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.7) return 'bg-green-500'
  if (confidence >= 0.4) return 'bg-amber-500'
  return 'bg-gray-500'
}

const urgencyOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }

const timeAgo = (dateStr: string) => {
  const diff = Date.now() - new Date(dateStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  return `${days}d ago`
}

// Session 1067: Detect and clean raw Python dict/JSON summaries from spider data
const cleanRawSummary = (text: string): string => {
  // Detect Python dict repr: starts with { and has single-quoted keys
  if (/^\s*\{.*'[a-z_]+':/i.test(text) || /^\s*\[?\s*\{.*"[a-z_]+":/i.test(text)) {
    try {
      // Try parsing as JSON (replace single quotes with double for Python dicts)
      const jsonStr = text.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false')
      const parsed = JSON.parse(jsonStr)
      // Extract readable content from parsed object
      if (parsed.items && Array.isArray(parsed.items)) {
        const titles = parsed.items.slice(0, 5).map((it: any) => it.title).filter(Boolean)
        if (titles.length) return titles.join(' | ')
      }
      if (parsed.title) return String(parsed.title)
      if (parsed.summary) return String(parsed.summary)
      if (parsed.description) return String(parsed.description)
      if (parsed.content) return String(parsed.content)
    } catch {
      // If JSON parse fails, try regex extraction of titles
      const titleMatches = text.match(/'title':\s*'([^']+)'/g)
      if (titleMatches) {
        const titles = titleMatches.slice(0, 5).map(m => m.replace(/'title':\s*'/, '').replace(/'$/, ''))
        return titles.join(' | ')
      }
    }
    return 'Spider data (structured)'
  }
  return text
}

const stripProvenance = (text: string): string =>
  text.replace(/^---\n## Report Provenance[\s\S]*?---\n?/, '').trim()

const stripMarkdown = (text: string): string =>
  text
    .replace(/^---\n[\s\S]*?---\n?/gm, '')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\*\*([^*]+)\*\*/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim()

// --- ML Prediction Panel ---

function MLPredictionPanel({ item }: { item: AttentionItem }) {
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
    <div className="space-y-3">
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center gap-2">
          <Brain size={16} className="text-primary-400" />
          <span className="text-sm font-medium text-gray-300">AI Prediction:</span>
        </div>
        <span className={cn(
          "px-2 py-0.5 text-xs font-medium rounded-full border capitalize",
          getMLRecommendationStyle(item.ml_recommendation || prediction?.prediction || 'uncertain')
        )}>
          {item.ml_recommendation || prediction?.prediction || 'uncertain'}
        </span>
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

      {prediction?.approval_probability !== undefined && (
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-500 w-24">Approval likelihood:</span>
          <div className="flex-1 h-3 bg-dark-border rounded-full overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-r from-red-500/30 via-amber-500/30 to-green-500/30" />
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

      {reasoningParts.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-xs text-gray-500 flex items-center gap-1">
            <Sparkles size={12} /> Signals:
          </span>
          <div className="flex flex-wrap gap-2">
            {reasoningParts.map((reason, idx) => (
              <span key={idx} className="px-2 py-1 text-xs bg-dark-border rounded-lg text-gray-400">
                {reason}
              </span>
            ))}
          </div>
        </div>
      )}

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
                <div key={idx} className="flex items-center justify-between text-xs p-2 bg-dark-bg/50 rounded">
                  <span className="text-gray-400 truncate flex-1 mr-2">{similar.title}</span>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={cn(
                      "px-1.5 py-0.5 rounded text-[10px] font-medium",
                      similar.decision === 'approve' || similar.decision === 'approved'
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    )}>
                      {similar.decision}
                    </span>
                    <span className="text-gray-600">{Math.round(similar.similarity * 100)}% match</span>
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

// --- Drawer Detail ---

function ItemDrawer({
  item,
  onClose,
  onDecide,
  isPending,
}: {
  item: AttentionItem
  onClose: () => void
  onDecide: (id: string, decision: string) => void
  isPending: boolean
}) {
  const [showRaw, setShowRaw] = useState(false)
  const [showFull, setShowFull] = useState(false)
  const TEXT_LIMIT = 5000

  const resultData = item.payload?.result_data
  const richContent = extractResultContent(resultData)
  const cleanSummary = item.summary ? cleanRawSummary(stripProvenance(item.summary)) : null
  const showSummary = cleanSummary && cleanSummary.length > 10

  return (
    <div className="fixed inset-y-0 right-0 w-[480px] max-w-full bg-dark-card border-l border-dark-border shadow-2xl z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-dark-border">
        <div className="flex items-center gap-2 min-w-0">
          <span className={cn("px-2 py-0.5 text-xs rounded border shrink-0", getUrgencyStyle(item.urgency))}>
            {item.urgency}
          </span>
          <span className="flex items-center gap-1 px-2 py-0.5 text-xs rounded bg-dark-border text-gray-400 shrink-0">
            {getTypeIcon(item.item_type)}
            {item.item_type}
          </span>
        </div>
        <button onClick={onClose} className="p-1.5 hover:bg-dark-border rounded-lg transition-colors shrink-0">
          <X size={18} />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <h2 className="text-lg font-semibold">{item.title}</h2>

        <div className="flex items-center gap-4 text-xs text-gray-500">
          {item.source_agent && <span>Source: <span className="text-gray-400">{item.source_agent}</span></span>}
          <span>{new Date(item.created_at).toLocaleString()}</span>
          <span>{timeAgo(item.created_at)}</span>
        </div>

        {item.status === 'deferred' && item.decision_feedback && (
          <div className="p-3 bg-orange-500/10 rounded-lg border border-orange-500/20">
            <div className="flex items-center gap-2 text-xs font-medium text-orange-400 mb-1">
              <ShieldAlert size={13} /> Deferred for Review
            </div>
            <p className="text-sm text-orange-300/80">{item.decision_feedback}</p>
          </div>
        )}

        {showSummary && cleanSummary && (
          <div className="p-3 bg-dark-bg rounded-lg border border-dark-border">
            <p className="text-sm text-gray-300 whitespace-pre-wrap">{stripMarkdown(cleanSummary)}</p>
          </div>
        )}

        <MLPredictionPanel item={item} />

        {richContent && richContent !== item.summary && (
          <div>
            <span className="text-xs text-gray-500 uppercase font-medium">Agent Output</span>
            <div className="mt-1 p-3 bg-dark-bg rounded-lg border border-dark-border">
              <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans leading-relaxed">
                {showFull ? richContent : (richContent.length > TEXT_LIMIT ? richContent.slice(0, TEXT_LIMIT) + '...' : richContent)}
              </pre>
              {richContent.length > TEXT_LIMIT && (
                <button
                  onClick={() => setShowFull(!showFull)}
                  className="mt-2 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                >
                  {showFull ? 'Show less' : `Show full (${Math.round(richContent.length / 1000)}k chars)`}
                </button>
              )}
            </div>
          </div>
        )}

        {item.payload && Object.keys(item.payload).length > 0 && (
          <div>
            <button
              onClick={() => setShowRaw(!showRaw)}
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

      {/* Actions footer */}
      <div className="p-4 border-t border-dark-border flex items-center gap-3">
        {item.status === 'deferred' ? (
          <>
            <div className="flex items-center gap-2 text-xs text-orange-400 mr-auto">
              <ShieldAlert size={14} />
              <span>Deferred — awaiting human confirmation</span>
            </div>
            <button
              onClick={() => onDecide(item.id, 'approved')}
              disabled={isPending}
              className="flex items-center justify-center gap-2 px-4 py-2.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors font-medium disabled:opacity-50"
            >
              <CheckCircle size={16} /> Confirm Close
            </button>
            <button
              onClick={() => onDecide(item.id, 'reopen')}
              disabled={isPending}
              className="flex items-center justify-center gap-2 px-4 py-2.5 bg-orange-500/20 text-orange-400 rounded-lg hover:bg-orange-500/30 transition-colors font-medium disabled:opacity-50"
            >
              <AlertTriangle size={16} /> Keep Open
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => onDecide(item.id, 'approved')}
              disabled={isPending}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors font-medium disabled:opacity-50"
            >
              <ThumbsUp size={16} /> Approve
            </button>
            <button
              onClick={() => onDecide(item.id, 'ignored')}
              disabled={isPending}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-500/20 text-gray-400 rounded-lg hover:bg-gray-500/30 transition-colors font-medium disabled:opacity-50"
            >
              <ThumbsDown size={16} /> Ignore
            </button>
            <button
              onClick={() => onDecide(item.id, 'deferred')}
              disabled={isPending}
              className="flex items-center justify-center gap-2 px-4 py-2.5 bg-dark-border text-gray-400 rounded-lg hover:bg-gray-700 transition-colors font-medium disabled:opacity-50"
            >
              <Clock size={16} /> Defer
            </button>
          </>
        )}
      </div>
    </div>
  )
}

// --- Content Extraction ---

function extractResultContent(resultData: unknown): string | null {
  if (!resultData) return null
  if (typeof resultData === 'string') return resultData
  if (typeof resultData === 'object' && resultData !== null) {
    const data = resultData as Record<string, unknown>
    for (const key of ['report', 'analysis', 'content', 'output', 'message', 'result']) {
      if (typeof data[key] === 'string' && (data[key] as string).length > 100) {
        const cleaned = stripProvenance(data[key] as string)
        if (cleaned.length > 50) return cleaned
      }
    }
    const subResults: string[] = []
    for (const value of Object.values(data)) {
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        const sub = value as Record<string, unknown>
        if (typeof sub.data === 'object' && sub.data !== null) {
          const subData = sub.data as Record<string, unknown>
          if (typeof subData.analysis === 'string' && subData.analysis.length > 50) {
            subResults.push(subData.analysis)
          }
        }
        if (typeof sub.message === 'string' && sub.message.length > 100) {
          const cleaned = stripProvenance(sub.message)
          if (cleaned.length > 50) subResults.push(cleaned)
        }
      }
    }
    if (subResults.length > 0) return subResults.sort((a, b) => b.length - a.length)[0]
    const skipKeys = new Set(['discord_sent', 'validation_status', 'publishable', 'provenance'])
    const pairs = Object.entries(data)
      .filter(([k, v]) => !skipKeys.has(k) && (typeof v === 'string' || typeof v === 'number'))
      .map(([k, v]) => `${k}: ${v}`)
    if (pairs.length > 0) return pairs.join('\n')
  }
  return null
}

// --- Main Page ---

export default function BoardroomPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<TabView>('inbox')
  const [urgencyFilter, setUrgencyFilter] = useState<UrgencyFilter>('all')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [sortBy, setSortBy] = useState<SortOption>('newest')
  const [selectedItem, setSelectedItem] = useState<AttentionItem | null>(null)
  const [selectedAttention, setSelectedAttention] = useState<Set<string>>(new Set())
  const [selectedDecisions, setSelectedDecisions] = useState<Set<string>>(new Set())
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

  // Fetch deferred items (critical items needing human sign-off)
  const {
    data: deferredData,
    isLoading: loadingDeferred,
    refetch: refetchDeferred,
  } = useQuery({
    queryKey: ['boardroom-deferred'],
    queryFn: async () => {
      const res = await humanApi.attention({ limit: 50, status: ['deferred'] })
      return res.data
    },
    refetchInterval: 30000,
  })

  // Fetch attention stats
  const { data: statsData } = useQuery({
    queryKey: ['boardroom-attention-stats'],
    queryFn: async () => {
      const res = await humanApi.attentionStats()
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

  // Session 1070: Fetch unclassified artifacts
  const {
    data: unclassifiedData,
    isLoading: loadingUnclassified,
    refetch: refetchUnclassified,
  } = useQuery({
    queryKey: ['boardroom-unclassified'],
    queryFn: async () => {
      const res = await classificationApi.listUnclassified(50)
      return res.data
    },
    refetchInterval: 30000,
  })

  // Session 1070: Classification form state per artifact
  const [classificationForms, setClassificationForms] = useState<Record<string, {
    what_is_this: string
    who_is_it_for: string
    data_allowed: string
    phase_approved: string
  }>>({})

  const updateClassificationForm = (artifactId: string, field: string, value: string) => {
    setClassificationForms(prev => ({
      ...prev,
      [artifactId]: { ...prev[artifactId], [field]: value },
    }))
  }

  const isClassificationComplete = (artifactId: string) => {
    const form = classificationForms[artifactId]
    return form?.what_is_this && form?.who_is_it_for && form?.data_allowed && form?.phase_approved
  }

  // Mutations
  const classifyMutation = useMutation({
    mutationFn: ({ artifactId, autoApprove }: { artifactId: string; autoApprove: boolean }) => {
      const form = classificationForms[artifactId]
      return classificationApi.classifyArtifact(artifactId, form, autoApprove)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-unclassified'] })
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
    },
  })

  const decideMutation = useMutation({
    mutationFn: ({ itemId, decision }: { itemId: string; decision: string }) =>
      humanApi.decide(itemId, decision),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
      queryClient.invalidateQueries({ queryKey: ['boardroom-deferred'] })
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention-stats'] })
      setSelectedItem(null)
    },
  })

  const bulkDecideMutation = useMutation({
    mutationFn: ({ decision, itemIds }: { decision: string; itemIds: string[] }) =>
      humanApi.bulkDecide(decision, itemIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention'] })
      queryClient.invalidateQueries({ queryKey: ['boardroom-deferred'] })
      queryClient.invalidateQueries({ queryKey: ['boardroom-attention-stats'] })
      setSelectedAttention(new Set())
    },
  })

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

  // Mark visit after 3s
  useEffect(() => {
    if (visitMarked.current) return
    const timer = setTimeout(() => {
      visitMarked.current = true
      humanApi.markBoardroomVisited().catch(() => {})
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  const attentionItems: AttentionItem[] = attentionData?.items || []
  const deferredItems: AttentionItem[] = deferredData?.items || []
  const decisions: Decision[] = (decisionsData?.decisions || []).filter(
    (d: Decision) => d.status === 'draft'
  )

  // NEW badge support
  const lastVisitedAt = attentionData?.last_visited_at as string | null | undefined
  const isNewItem = useCallback((createdAt: string) => {
    if (!lastVisitedAt) return false
    return new Date(createdAt) > new Date(lastVisitedAt)
  }, [lastVisitedAt])

  // Filter + sort attention items
  const filteredAttention = attentionItems
    .filter((item) => {
      if (urgencyFilter !== 'all' && item.urgency !== urgencyFilter) return false
      if (typeFilter !== 'all' && item.item_type !== typeFilter) return false
      if (searchQuery) {
        const q = searchQuery.toLowerCase()
        if (!item.title.toLowerCase().includes(q) &&
            !(item.summary?.toLowerCase().includes(q)) &&
            !(item.source_agent?.toLowerCase().includes(q))) return false
      }
      return true
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'oldest': return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        case 'urgency': return (urgencyOrder[a.urgency] ?? 4) - (urgencyOrder[b.urgency] ?? 4)
        default: return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      }
    })

  // Selection helpers
  const toggleAttentionSelection = (id: string) => {
    const next = new Set(selectedAttention)
    next.has(id) ? next.delete(id) : next.add(id)
    setSelectedAttention(next)
  }

  const toggleDecisionSelection = (id: string) => {
    const next = new Set(selectedDecisions)
    next.has(id) ? next.delete(id) : next.add(id)
    setSelectedDecisions(next)
  }

  const selectAllAttention = () => {
    setSelectedAttention(
      selectedAttention.size === filteredAttention.length
        ? new Set()
        : new Set(filteredAttention.map(i => i.id))
    )
  }

  const selectAllDecisions = () => {
    setSelectedDecisions(
      selectedDecisions.size === decisions.length
        ? new Set()
        : new Set(decisions.map(d => d.id))
    )
  }

  const isBulkPending = bulkDecideMutation.isPending || bulkPromoteMutation.isPending || bulkRejectMutation.isPending

  // Stats
  const pendingCount = statsData?.pending_count ?? attentionItems.length
  const deferredCount = deferredItems.length
  const decidedToday = statsData?.decided_today ?? 0
  const unclassifiedCount = unclassifiedData?.total_unclassified ?? unclassifiedData?.count ?? 0
  const avgResponseTime = statsData?.avg_response_time_hours ?? null
  const unclassifiedArtifacts: UnclassifiedArtifact[] = unclassifiedData?.artifacts ?? []

  return (
    <div className="flex-1 overflow-hidden flex flex-col">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Gavel className="text-primary-400" size={24} />
            <div>
              <h1 className="text-xl font-bold">Boardroom</h1>
              <p className="text-sm text-gray-500">Operator inbox for attention items and decisions</p>
            </div>
          </div>
          <button
            onClick={() => { refetchAttention(); refetchDeferred(); refetchDecisions(); refetchUnclassified() }}
            className="flex items-center gap-2 px-3 py-2 bg-dark-border rounded-lg hover:bg-gray-700 transition-colors text-sm"
          >
            <RefreshCw size={14} className={loadingAttention || loadingDecisions ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="px-6 py-4 border-b border-dark-border">
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Eye size={14} /> Pending
            </div>
            <div className="text-2xl font-bold text-white">{pendingCount}</div>
          </div>
          <div className={cn(
            "p-4 bg-dark-card border rounded-lg cursor-pointer transition-colors",
            deferredCount > 0 ? "border-orange-500/30 hover:border-orange-500/50" : "border-dark-border"
          )} onClick={() => setActiveTab('inbox')}>
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <ShieldAlert size={14} /> Needs Review
            </div>
            <div className={cn("text-2xl font-bold", deferredCount > 0 ? "text-orange-400" : "text-green-400")}>
              {deferredCount}
            </div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <CheckCircle size={14} /> Decided Today
            </div>
            <div className="text-2xl font-bold text-green-400">{decidedToday}</div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg cursor-pointer hover:border-amber-500/30 transition-colors"
            onClick={() => setActiveTab('classify')}>
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Target size={14} /> Needs Classification
            </div>
            <div className={cn("text-2xl font-bold", unclassifiedCount > 0 ? "text-amber-400" : "text-green-400")}>
              {unclassifiedCount}
            </div>
          </div>
          <div className="p-4 bg-dark-card border border-dark-border rounded-lg">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <Timer size={14} /> Avg Response
            </div>
            <div className="text-2xl font-bold text-amber-400">
              {avgResponseTime !== null ? `${avgResponseTime.toFixed(1)}h` : '--'}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="px-6 border-b border-dark-border flex items-center gap-1">
        <button
          onClick={() => setActiveTab('inbox')}
          className={cn(
            'flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2',
            activeTab === 'inbox'
              ? 'text-primary-400 border-primary-500'
              : 'text-gray-400 border-transparent hover:text-white'
          )}
        >
          <Eye size={16} />
          Inbox
          <span className="px-2 py-0.5 text-xs rounded-full bg-dark-border">{attentionItems.length}</span>
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={cn(
            'flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2',
            activeTab === 'history'
              ? 'text-primary-400 border-primary-500'
              : 'text-gray-400 border-transparent hover:text-white'
          )}
        >
          <Gavel size={16} />
          Draft Decisions
          <span className="px-2 py-0.5 text-xs rounded-full bg-dark-border">{decisions.length}</span>
        </button>
        <button
          onClick={() => setActiveTab('classify')}
          className={cn(
            'flex items-center gap-2 px-4 py-3 font-medium transition-colors border-b-2',
            activeTab === 'classify'
              ? 'text-amber-400 border-amber-500'
              : 'text-gray-400 border-transparent hover:text-white'
          )}
        >
          <Target size={16} />
          Needs Classification
          {unclassifiedCount > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-amber-500/20 text-amber-400">{unclassifiedCount}</span>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'inbox' ? (
          <div className="p-6 space-y-4">
            {/* Deferred Items — Needs Review Banner */}
            {deferredItems.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm font-medium text-orange-400">
                  <ShieldAlert size={16} />
                  Needs Review — {deferredItems.length} deferred item{deferredItems.length !== 1 ? 's' : ''} awaiting confirmation
                </div>
                {deferredItems.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 px-4 py-3 rounded-lg bg-orange-500/5 border border-orange-500/20 hover:border-orange-500/40 cursor-pointer transition-colors"
                    onClick={() => setSelectedItem(item)}
                  >
                    <span className={cn("px-2 py-0.5 text-xs rounded border shrink-0 capitalize", getUrgencyStyle(item.urgency))}>
                      {item.urgency}
                    </span>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-sm truncate">{item.title}</h4>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          {getTypeIcon(item.item_type)} {item.item_type}
                        </span>
                        {item.source_agent && <span>{item.source_agent}</span>}
                        <span>{timeAgo(item.created_at)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={() => decideMutation.mutate({ itemId: item.id, decision: 'approved' })}
                        disabled={decideMutation.isPending}
                        className="flex items-center gap-1 px-2 py-1.5 rounded text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                        title="Confirm close — issue resolved"
                      >
                        <CheckCircle size={13} /> Close
                      </button>
                      <button
                        onClick={() => {
                          // Re-open as pending for continued monitoring
                          decideMutation.mutate({ itemId: item.id, decision: 'reopen' })
                        }}
                        disabled={decideMutation.isPending}
                        className="flex items-center gap-1 px-2 py-1.5 rounded text-xs bg-orange-500/20 text-orange-400 hover:bg-orange-500/30 transition-colors"
                        title="Keep open — still needs attention"
                      >
                        <AlertTriangle size={13} /> Keep Open
                      </button>
                    </div>
                  </div>
                ))}
                <div className="border-b border-dark-border" />
              </div>
            )}

            {/* Filter Bar */}
            <div className="flex items-center gap-3 flex-wrap">
              {/* Urgency chips */}
              <div className="flex items-center gap-1">
                <Filter size={14} className="text-gray-500 mr-1" />
                {(['all', 'critical', 'high', 'medium', 'low'] as UrgencyFilter[]).map(u => (
                  <button
                    key={u}
                    onClick={() => setUrgencyFilter(u)}
                    className={cn(
                      'px-2.5 py-1 text-xs rounded-full transition-colors capitalize',
                      urgencyFilter === u
                        ? 'bg-primary-500 text-white'
                        : 'bg-dark-border text-gray-400 hover:text-white'
                    )}
                  >
                    {u}
                  </button>
                ))}
              </div>

              {/* Type dropdown */}
              <select
                value={typeFilter}
                onChange={e => setTypeFilter(e.target.value)}
                className="px-2.5 py-1.5 text-xs bg-dark-border border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-primary-500"
              >
                <option value="all">All Types</option>
                <option value="review">Review</option>
                <option value="insight">Insight</option>
                <option value="alert">Alert</option>
                <option value="opportunity">Opportunity</option>
              </select>

              {/* Search */}
              <div className="relative flex-1 min-w-[200px] max-w-xs">
                <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search items..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-sm bg-dark-bg border border-dark-border rounded-lg focus:outline-none focus:border-primary-500 text-gray-300 placeholder-gray-600"
                />
                {searchQuery && (
                  <button
                    onClick={() => setSearchQuery('')}
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                  >
                    <X size={12} />
                  </button>
                )}
              </div>

              {/* Sort */}
              <div className="flex items-center gap-1 ml-auto">
                <ArrowUpDown size={14} className="text-gray-500" />
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as SortOption)}
                  className="px-2.5 py-1.5 text-xs bg-dark-border border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-primary-500"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="urgency">By Urgency</option>
                </select>
              </div>
            </div>

            {/* Select All + Count */}
            {filteredAttention.length > 0 && (
              <div className="flex items-center justify-between">
                <button
                  onClick={selectAllAttention}
                  className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  {selectedAttention.size === filteredAttention.length
                    ? <CheckSquare size={16} className="text-primary-400" />
                    : <Square size={16} />}
                  {selectedAttention.size > 0
                    ? `${selectedAttention.size} of ${filteredAttention.length} selected`
                    : `Select all (${filteredAttention.length})`}
                </button>
                <span className="text-xs text-gray-500">{filteredAttention.length} items</span>
              </div>
            )}

            {/* Bulk Action Bar */}
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
              <div className="flex items-center justify-center py-16">
                <Loader2 className="animate-spin text-primary-400" size={28} />
              </div>
            ) : filteredAttention.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <CheckCircle className="mx-auto mb-3" size={36} />
                <p className="text-lg">No pending attention items</p>
                <p className="text-sm mt-1">All caught up!</p>
              </div>
            ) : (
              <div className="space-y-1">
                {filteredAttention.map((item) => (
                  <div
                    key={item.id}
                    className={cn(
                      "flex items-center gap-3 px-4 py-3 rounded-lg cursor-pointer transition-colors",
                      selectedItem?.id === item.id
                        ? "bg-primary-500/10 border border-primary-500/30"
                        : selectedAttention.has(item.id)
                        ? "bg-dark-card border border-primary-500/20"
                        : "bg-dark-card border border-dark-border hover:border-gray-600"
                    )}
                    onClick={() => setSelectedItem(item)}
                  >
                    {/* Checkbox */}
                    <button
                      onClick={(e) => { e.stopPropagation(); toggleAttentionSelection(item.id) }}
                      className="shrink-0"
                    >
                      {selectedAttention.has(item.id)
                        ? <CheckSquare size={18} className="text-primary-400" />
                        : <Square size={18} className="text-gray-500 hover:text-gray-300" />}
                    </button>

                    {/* Urgency badge */}
                    <span className={cn("px-2 py-0.5 text-xs rounded border shrink-0 capitalize", getUrgencyStyle(item.urgency))}>
                      {item.urgency}
                    </span>

                    {/* Title + metadata */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-sm truncate">{item.title}</h4>
                        {isNewItem(item.created_at) && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-500 text-white rounded shrink-0">NEW</span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 mt-0.5 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          {getTypeIcon(item.item_type)} {item.item_type}
                        </span>
                        {item.source_agent && <span>{item.source_agent}</span>}
                        <span>{timeAgo(item.created_at)}</span>
                      </div>
                    </div>

                    {/* ML badge */}
                    {(item.ml_recommendation || item.ml_prediction) && (item.ml_confidence ?? 0) >= 0.3 && (
                      <span className={cn(
                        "flex items-center gap-1 px-2 py-0.5 text-xs rounded border shrink-0",
                        getMLRecommendationStyle(item.ml_recommendation || item.ml_prediction?.prediction || 'uncertain')
                      )}>
                        <Brain size={12} />
                        {item.ml_confidence ? `${Math.round(item.ml_confidence * 100)}%` : 'AI'}
                      </span>
                    )}

                    {/* Quick actions */}
                    <div className="flex items-center gap-1 shrink-0" onClick={e => e.stopPropagation()}>
                      <button
                        onClick={() => decideMutation.mutate({ itemId: item.id, decision: 'approved' })}
                        disabled={decideMutation.isPending}
                        className="p-1.5 rounded bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                        title="Approve"
                      >
                        <ThumbsUp size={14} />
                      </button>
                      <button
                        onClick={() => decideMutation.mutate({ itemId: item.id, decision: 'ignored' })}
                        disabled={decideMutation.isPending}
                        className="p-1.5 rounded bg-gray-500/20 text-gray-400 hover:bg-gray-500/30 transition-colors"
                        title="Ignore"
                      >
                        <ThumbsDown size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : activeTab === 'history' ? (
          /* Draft Decisions Tab */
          <div className="p-6 space-y-4">
            {/* Select All */}
            {decisions.length > 0 && (
              <div className="flex items-center justify-between">
                <button
                  onClick={selectAllDecisions}
                  className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
                >
                  {selectedDecisions.size === decisions.length
                    ? <CheckSquare size={16} className="text-primary-400" />
                    : <Square size={16} />}
                  {selectedDecisions.size > 0
                    ? `${selectedDecisions.size} of ${decisions.length} selected`
                    : `Select all (${decisions.length})`}
                </button>
              </div>
            )}

            {/* Bulk Actions */}
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
              <div className="flex items-center justify-center py-16">
                <Loader2 className="animate-spin text-primary-400" size={28} />
              </div>
            ) : decisions.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <CheckCircle className="mx-auto mb-3" size={36} />
                <p className="text-lg">No draft decisions</p>
              </div>
            ) : (
              <div className="space-y-2">
                {decisions.map((decision) => (
                  <div
                    key={decision.id}
                    className={cn(
                      "bg-dark-card border rounded-lg p-4 transition-colors",
                      selectedDecisions.has(decision.id) ? "border-primary-500/50" : "border-dark-border hover:border-gray-600"
                    )}
                  >
                    <div className="flex items-start gap-3">
                      <button
                        onClick={() => toggleDecisionSelection(decision.id)}
                        className="mt-1 shrink-0"
                      >
                        {selectedDecisions.has(decision.id)
                          ? <CheckSquare size={18} className="text-primary-400" />
                          : <Square size={18} className="text-gray-500 hover:text-gray-300" />}
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap mb-1">
                          <span className="px-2 py-0.5 text-xs rounded bg-purple-500/20 text-purple-400">
                            {decision.decision_type_display || decision.decision_type}
                          </span>
                          <span className="px-2 py-0.5 text-xs rounded bg-dark-border text-gray-400">
                            {decision.impact_area_display || decision.impact_area}
                          </span>
                          {isNewItem(decision.created_at) && (
                            <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-500 text-white rounded">NEW</span>
                          )}
                        </div>
                        <h4 className="font-medium text-sm">{decision.topic}</h4>
                        {decision.recommended_stance && (
                          <p className="text-xs text-gray-400 mt-1 line-clamp-2">{decision.recommended_stance}</p>
                        )}
                        {decision.key_insights && decision.key_insights.length > 0 && (
                          <div className="mt-2">
                            <ul className="text-xs text-gray-400 list-disc list-inside space-y-0.5">
                              {decision.key_insights.slice(0, 3).map((insight, idx) => (
                                <li key={idx}>{insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {decision.suggested_feature && (
                          <div className="mt-2 px-2 py-1 bg-primary-500/10 rounded text-xs">
                            <span className="text-primary-400 font-medium">Feature:</span>{' '}
                            <span className="text-gray-300">{decision.suggested_feature}</span>
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-2">{new Date(decision.created_at).toLocaleString()}</p>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
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
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          /* Needs Classification Tab */
          <div className="p-6 space-y-4">
            <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-sm text-amber-300">
              Artifacts below need classification before they can be approved. Answer the 4 questions for each item.
            </div>
            {loadingUnclassified ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="animate-spin text-amber-400" size={28} />
              </div>
            ) : unclassifiedArtifacts.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <CheckCircle className="mx-auto mb-3" size={36} />
                <p className="text-lg">All artifacts classified</p>
                <p className="text-sm mt-1">No pending items need classification</p>
              </div>
            ) : (
              <div className="space-y-4">
                {unclassifiedArtifacts.map((artifact) => {
                  const form = classificationForms[artifact.id] || {}
                  const complete = isClassificationComplete(artifact.id)
                  return (
                    <div key={artifact.id} className="bg-dark-card border border-dark-border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="px-2 py-0.5 text-xs rounded bg-dark-border text-gray-400">{artifact.type_display || artifact.type}</span>
                            <span className="text-xs text-gray-500">{artifact.composite_score?.toFixed(2)}</span>
                          </div>
                          <h4 className="font-medium text-sm">{artifact.title}</h4>
                          <p className="text-xs text-gray-400 mt-1 line-clamp-2">{artifact.description}</p>
                          <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                            {artifact.source_agent && <span>Source: {artifact.source_agent}</span>}
                            {artifact.extracted_at && <span>{timeAgo(artifact.extracted_at)}</span>}
                          </div>
                        </div>
                      </div>

                      {/* Classification Form */}
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-500 block mb-1">What is this?</label>
                          <select
                            value={form.what_is_this || ''}
                            onChange={e => updateClassificationForm(artifact.id, 'what_is_this', e.target.value)}
                            className="w-full px-2 py-1.5 text-xs bg-dark-bg border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-amber-500"
                          >
                            <option value="">Select...</option>
                            {WHAT_IS_THIS_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 block mb-1">Who is it for?</label>
                          <select
                            value={form.who_is_it_for || ''}
                            onChange={e => updateClassificationForm(artifact.id, 'who_is_it_for', e.target.value)}
                            className="w-full px-2 py-1.5 text-xs bg-dark-bg border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-amber-500"
                          >
                            <option value="">Select...</option>
                            {WHO_IS_IT_FOR_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 block mb-1">Data allowed?</label>
                          <select
                            value={form.data_allowed || ''}
                            onChange={e => updateClassificationForm(artifact.id, 'data_allowed', e.target.value)}
                            className="w-full px-2 py-1.5 text-xs bg-dark-bg border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-amber-500"
                          >
                            <option value="">Select...</option>
                            {DATA_ALLOWED_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                          </select>
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 block mb-1">Phase approved?</label>
                          <select
                            value={form.phase_approved || ''}
                            onChange={e => updateClassificationForm(artifact.id, 'phase_approved', e.target.value)}
                            className="w-full px-2 py-1.5 text-xs bg-dark-bg border border-dark-border rounded-lg text-gray-300 focus:outline-none focus:border-amber-500"
                          >
                            <option value="">Select...</option>
                            {PHASE_APPROVED_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                          </select>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center gap-2 pt-1">
                        <button
                          onClick={() => classifyMutation.mutate({ artifactId: artifact.id, autoApprove: true })}
                          disabled={!complete || classifyMutation.isPending}
                          className={cn(
                            "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                            complete
                              ? "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                              : "bg-dark-border text-gray-600 cursor-not-allowed"
                          )}
                        >
                          {classifyMutation.isPending ? <Loader2 size={12} className="animate-spin" /> : <CheckCircle size={12} />}
                          Classify & Approve
                        </button>
                        <button
                          onClick={() => classifyMutation.mutate({ artifactId: artifact.id, autoApprove: false })}
                          disabled={!complete || classifyMutation.isPending}
                          className={cn(
                            "flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors",
                            complete
                              ? "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
                              : "bg-dark-border text-gray-600 cursor-not-allowed"
                          )}
                        >
                          Classify Only
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Slide-over Drawer */}
      {selectedItem && (
        <>
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => setSelectedItem(null)}
          />
          <ItemDrawer
            item={selectedItem}
            onClose={() => setSelectedItem(null)}
            onDecide={(id, decision) => decideMutation.mutate({ itemId: id, decision })}
            isPending={decideMutation.isPending}
          />
        </>
      )}
    </div>
  )
}
