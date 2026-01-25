import { useState, useMemo, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { humanApi, agentsApi, bodyApi, platformApi } from '@/lib/api'
// Session 714: Real-time system events
import { useSystemEvents } from '@/hooks/useWebSocket'
import {
  User,
  Bell,
  Sliders,
  AlertTriangle,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Pause,
  Play,
  Moon,
  Eye,
  Bot,
  Settings,
  ChevronRight,
  ThumbsUp,
  ThumbsDown,
  Timer,
  Activity,
  Loader2,
  RefreshCw,
  Heart,
  ExternalLink,
  DollarSign,
  FileText,
  Zap,
  Target,
  BarChart3,
  Lightbulb,
  Sparkles,
  PieChart,
  History,
  Scale,
  Database,
  GitBranch,
  Brain,
  AlertOctagon,
  BookMarked,
} from 'lucide-react'
import { cn } from '@/lib/cn'

// Types
// Session 763: Available action type for Mission Control
interface AvailableAction {
  id: string
  label: string
  style?: 'primary' | 'danger' | 'warning' | 'success' | 'secondary'
  description?: string
}

interface AttentionItem {
  id: string
  source_type: string
  source_id: string
  source_agent: string
  item_type: string
  title: string
  summary: string
  payload: Record<string, unknown> & { available_actions?: AvailableAction[] }
  urgency: 'critical' | 'high' | 'medium' | 'low'
  priority_score: number
  impact_estimate: string | null
  ml_confidence: number | null
  ml_recommendation: string | null
  // Session 746: Added watching and verified statuses
  status: 'pending' | 'viewed' | 'acted' | 'deferred' | 'ignored' | 'expired' | 'watching' | 'verified'
  created_at: string
  expires_at: string | null
  deferred_until: string | null
  viewed_at: string | null
  // Session 746: Decision fields
  decision: string | null
  decision_feedback: string | null
  decision_confidence: number | null
  decided_at: string | null
  time_to_decision_ms: number | null
  // Session 746: ML override fields
  human_overrode_ml: boolean
  override_reason: string | null
  // Session 746: Verification fields for Watch & Verify feature
  verification_outcome?: 'pending' | 'won' | 'lost' | 'push' | 'cancelled' | null
  verified_at?: string | null
  verification_profit?: number | null
  verification_notes?: string
  event_completed_at?: string | null
}

interface AttentionStats {
  pending_count: number
  by_urgency: Record<string, number>
  avg_decision_time_ms: number | null
  ml_agreement_rate: number | null
  total_with_ml_context: number
  // Session 746: New comprehensive stats
  by_type: Record<string, number>
  by_source: Record<string, number>
  by_status: Record<string, number>
  by_decision: Record<string, number>
  watching_count: number
  verified_count: number
  verification_outcomes: Record<string, number>
  paper_profit: number
  override_count: number
  feedback_count: number
  fed_to_ml_count: number
  recent_actions: Array<{
    action_type: string
    target_type: string
    target_id: string
    reason: string
    created_at: string
  }>
  total_items: number
}

interface SystemState {
  system_paused: boolean
  review_mode: boolean
  quiet_mode: boolean
  quiet_mode_until: string | null
  paused_agents: string[]
  ml_confidence_threshold: number
  auto_approve_threshold: number
}

interface Preferences {
  quiet_hours_start: string | null
  quiet_hours_end: string | null
  min_urgency_to_notify: string
  preferred_channel: string
  review_depth: string
  auto_approve_low_risk: boolean
  require_review_above_confidence: number
  trusted_agents: string[]
  blocked_sources: string[]
  // Learned stats
  topic_weights: Record<string, number>
  avg_decision_time_ms: number | null
  approval_rate: number | null
  total_decisions: number
}

// Urgency config
const URGENCY_CONFIG = {
  critical: { color: 'bg-accent-red', textColor: 'text-accent-red', icon: AlertTriangle },
  high: { color: 'bg-accent-amber', textColor: 'text-accent-amber', icon: AlertCircle },
  medium: { color: 'bg-accent-cyan', textColor: 'text-accent-cyan', icon: Clock },
  low: { color: 'bg-gray-500', textColor: 'text-gray-400', icon: CheckCircle },
}

// Session 742: Item type config for visual differentiation
const ITEM_TYPE_CONFIG: Record<string, { color: string; textColor: string; icon: typeof DollarSign; label: string }> = {
  arbitrage: { color: 'bg-accent-green', textColor: 'text-accent-green', icon: DollarSign, label: 'Arbitrage' },
  alert: { color: 'bg-accent-red', textColor: 'text-accent-red', icon: AlertTriangle, label: 'Alert' },
  approval: { color: 'bg-accent-amber', textColor: 'text-accent-amber', icon: CheckCircle, label: 'Approval' },
  review: { color: 'bg-accent-purple', textColor: 'text-accent-purple', icon: FileText, label: 'Review' },
  insight: { color: 'bg-accent-cyan', textColor: 'text-accent-cyan', icon: Lightbulb, label: 'Insight' },
  milestone: { color: 'bg-primary-500', textColor: 'text-primary-400', icon: Target, label: 'Milestone' },
  decision: { color: 'bg-accent-orange', textColor: 'text-accent-orange', icon: Zap, label: 'Decision' },
  opportunity: { color: 'bg-accent-green', textColor: 'text-accent-green', icon: Sparkles, label: 'Opportunity' },
}

// Session 742: Payload renderer for different item types
function PayloadDisplay({ item }: { item: AttentionItem }) {
  const { payload, item_type, source_type } = item
  if (!payload || Object.keys(payload).length === 0) return null

  // Arbitrage-specific display
  if (item_type === 'arbitrage' && (source_type === 'arbitrage_detection' || source_type === 'betting_monitor')) {
    return (
      <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
        {payload.profit_pct !== undefined && (
          <div className="flex items-center gap-2">
            <DollarSign className="text-accent-green" size={16} />
            <div>
              <p className="text-xs text-gray-500">Profit</p>
              <p className="font-bold text-accent-green">{(Number(payload.profit_pct) || 0).toFixed(2)}%</p>
            </div>
          </div>
        )}
        {payload.profit_percentage !== undefined && (
          <div className="flex items-center gap-2">
            <DollarSign className="text-accent-green" size={16} />
            <div>
              <p className="text-xs text-gray-500">Profit</p>
              <p className="font-bold text-accent-green">{(Number(payload.profit_percentage) || 0).toFixed(2)}%</p>
            </div>
          </div>
        )}
        {!!payload.rating && (
          <div className="flex items-center gap-2">
            <Zap className={payload.rating === 'HOT' ? 'text-accent-red' : 'text-accent-amber'} size={16} />
            <div>
              <p className="text-xs text-gray-500">Rating</p>
              <p className={cn('font-bold', payload.rating === 'HOT' ? 'text-accent-red' : 'text-accent-amber')}>
                {String(payload.rating)}
              </p>
            </div>
          </div>
        )}
        {!!payload.markets && Array.isArray(payload.markets) && (
          <div className="col-span-2">
            <p className="text-xs text-gray-500 mb-1">Markets</p>
            <div className="flex gap-2 flex-wrap">
              {payload.markets.map((market: string, i: number) => (
                <span key={i} className="px-2 py-0.5 rounded bg-primary-500/20 text-primary-400 text-sm">
                  {market}
                </span>
              ))}
            </div>
          </div>
        )}
        {!!(payload.home_team || payload.away_team) && (
          <div className="col-span-2">
            <p className="text-xs text-gray-500 mb-1">Matchup</p>
            <p className="text-sm">
              <span className="font-medium">{String(payload.away_team || 'Away')}</span>
              <span className="text-gray-500 mx-2">@</span>
              <span className="font-medium">{String(payload.home_team || 'Home')}</span>
            </p>
          </div>
        )}
        {!!payload.game_time && (
          <div className="flex items-center gap-2">
            <Clock className="text-gray-400" size={16} />
            <div>
              <p className="text-xs text-gray-500">Game Time</p>
              <p className="text-sm">{String(payload.game_time)}</p>
            </div>
          </div>
        )}
        {payload.stake_away !== undefined && payload.stake_home !== undefined && (
          <div className="col-span-2 grid grid-cols-2 gap-2 mt-2 pt-2 border-t border-dark-border">
            <div>
              <p className="text-xs text-gray-500">Stake Away</p>
              <p className="font-medium">${(Number(payload.stake_away) || 0).toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Stake Home</p>
              <p className="font-medium">${(Number(payload.stake_home) || 0).toFixed(2)}</p>
            </div>
          </div>
        )}
        {!!payload.suggested_actions && Array.isArray(payload.suggested_actions) && (
          <div className="col-span-2 mt-2 pt-2 border-t border-dark-border">
            <p className="text-xs text-gray-500 mb-1">Suggested Actions</p>
            <ul className="text-sm space-y-1">
              {payload.suggested_actions.map((action: string, i: number) => (
                <li key={i} className="flex items-center gap-2">
                  <ChevronRight size={12} className="text-primary-400" />
                  {action}
                </li>
              ))}
            </ul>
          </div>
        )}
        {/* Session 742: Quick action - link to Betting page */}
        <div className="col-span-2 mt-2 pt-2 border-t border-dark-border">
          <a
            href="/betting"
            className="text-sm text-accent-green hover:text-accent-green/80 flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <DollarSign size={14} />
            View Betting Dashboard
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    )
  }

  // Pilot/experiment display - Session 742: Added link to Intelligence page
  if (item_type === 'approval' || item_type === 'milestone') {
    return (
      <div className="grid grid-cols-2 gap-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
        {!!payload.pilot_id && (
          <div className="col-span-2">
            <p className="text-xs text-gray-500">Pilot ID</p>
            <a
              href="/intelligence"
              className="font-medium text-primary-400 hover:text-primary-300 hover:underline inline-flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              {String(payload.pilot_id)}
              <ExternalLink size={12} />
            </a>
          </div>
        )}
        {payload.accuracy !== undefined && (
          <div>
            <p className="text-xs text-gray-500">Accuracy</p>
            <p className="font-bold text-accent-green">{(Number(payload.accuracy) || 0).toFixed(1)}%</p>
          </div>
        )}
        {payload.improvement !== undefined && (
          <div>
            <p className="text-xs text-gray-500">Improvement</p>
            <p className="font-bold text-accent-green">+{Number(payload.improvement)}%</p>
          </div>
        )}
        {payload.target !== undefined && (
          <div>
            <p className="text-xs text-gray-500">Target</p>
            <p className="font-medium">{Number(payload.target)}%</p>
          </div>
        )}
        {/* Quick action: View in Intelligence */}
        <div className="col-span-2 pt-2 border-t border-dark-border">
          <a
            href="/intelligence"
            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <Target size={14} />
            View in Intelligence Dashboard
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    )
  }

  // Alert/monitoring display - Session 742: Enhanced with links to Body Health
  if (item_type === 'alert') {
    return (
      <div className="space-y-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
        <div className="grid grid-cols-2 gap-3">
          {payload.spike_percentage !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Spike</p>
              <p className="font-bold text-accent-red">+{Number(payload.spike_percentage)}%</p>
            </div>
          )}
          {payload.concurrent_executions !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Concurrent Executions</p>
              <p className="font-medium">{Number(payload.concurrent_executions)}</p>
            </div>
          )}
          {/* System health check fields */}
          {payload.agents !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Agents</p>
              <p className="font-medium">{Number(payload.agents)}</p>
            </div>
          )}
          {payload.spiders !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Spiders</p>
              <p className="font-medium">{Number(payload.spiders)}</p>
            </div>
          )}
          {payload.capacity !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Capacity</p>
              <p className="font-medium">{String(payload.capacity)}</p>
            </div>
          )}
        </div>
        {/* Quick action: View Body Health */}
        <div className="pt-2 border-t border-dark-border">
          <a
            href="/body-health"
            className="text-sm text-accent-red hover:text-accent-red/80 flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <Heart size={14} />
            View Body Health Dashboard
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    )
  }

  // Content review display - Session 742: Show linked blog titles
  if (item_type === 'review') {
    // Check if we have blog_ids array or just a single content_id
    const hasBlogList = !!payload.blog_titles && Array.isArray(payload.blog_titles)
    const singleContentId = !!payload.content_id && !hasBlogList

    return (
      <div className="space-y-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
        <div className="flex gap-4">
          {payload.post_count !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Posts</p>
              <p className="font-medium">{Number(payload.post_count)}</p>
            </div>
          )}
          {payload.quality_score !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Quality Score</p>
              <p className="font-bold text-accent-green">{Number(payload.quality_score)}%</p>
            </div>
          )}
        </div>
        {/* Session 742: Show linked blog titles */}
        {hasBlogList && (
          <div className="border-t border-dark-border pt-3">
            <p className="text-xs text-gray-500 mb-2">Blog Posts to Review</p>
            <ul className="space-y-2">
              {(payload.blog_titles as string[]).map((title: string, i: number) => {
                const blogId = payload.blog_ids && Array.isArray(payload.blog_ids) ? (payload.blog_ids as string[])[i] : null
                return (
                  <li key={i} className="flex items-start gap-2">
                    <FileText size={14} className="text-primary-400 mt-0.5 flex-shrink-0" />
                    {blogId ? (
                      <a
                        href={`/blog/${blogId}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-primary-400 hover:text-primary-300 hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {title}
                      </a>
                    ) : (
                      <span className="text-sm">{title}</span>
                    )}
                  </li>
                )
              })}
            </ul>
          </div>
        )}
        {/* Session 742: Handle single content_id case */}
        {singleContentId && (
          <div className="border-t border-dark-border pt-3">
            <a
              href={`/blog/${payload.content_id}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-2"
              onClick={(e) => e.stopPropagation()}
            >
              <FileText size={14} />
              View Content
              <ExternalLink size={12} />
            </a>
          </div>
        )}
        {/* Quick action: View Content Channels */}
        <div className="pt-2 border-t border-dark-border">
          <a
            href="/content-channels"
            className="text-sm text-accent-purple hover:text-accent-purple/80 flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <FileText size={14} />
            View Content Channels
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    )
  }

  // Spider/insight display - Session 742: Added links to Spiders page
  if (item_type === 'insight') {
    const spiderName = payload.spider_name || payload.spider
    return (
      <div className="space-y-3 p-3 rounded-lg bg-dark-bg border border-dark-border">
        <div className="grid grid-cols-2 gap-3">
          {!!spiderName && (
            <div className="col-span-2">
              <p className="text-xs text-gray-500">Spider</p>
              <a
                href="/spiders"
                className="font-medium text-primary-400 hover:text-primary-300 hover:underline inline-flex items-center gap-1"
                onClick={(e) => e.stopPropagation()}
              >
                {String(spiderName)}
                <ExternalLink size={12} />
              </a>
            </div>
          )}
          {payload.duplicate_rate !== undefined && (
            <div>
              <p className="text-xs text-gray-500">Duplicate Rate</p>
              <p className="font-medium text-accent-amber">{Number(payload.duplicate_rate)}%</p>
            </div>
          )}
          {!!payload.alert_type && (
            <div>
              <p className="text-xs text-gray-500">Alert Type</p>
              <p className="font-medium capitalize">{String(payload.alert_type).replace(/_/g, ' ')}</p>
            </div>
          )}
        </div>
        {/* Spider data preview if available */}
        {!!payload.data && typeof payload.data === 'object' && (
          <div className="border-t border-dark-border pt-2">
            <p className="text-xs text-gray-500 mb-1">Data Preview</p>
            <pre className="text-xs bg-dark-card p-2 rounded overflow-x-auto max-h-24">
              {JSON.stringify(payload.data, null, 2).slice(0, 200)}
              {JSON.stringify(payload.data).length > 200 && '...'}
            </pre>
          </div>
        )}
        {/* Quick action: View Spider Integration */}
        <div className="pt-2 border-t border-dark-border">
          <a
            href="/spiders"
            className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <Activity size={14} />
            View Spider Integration
            <ExternalLink size={12} />
          </a>
        </div>
      </div>
    )
  }

  // Generic payload display for unknown types
  return (
    <div className="p-3 rounded-lg bg-dark-bg border border-dark-border">
      <p className="text-xs text-gray-500 mb-2">Additional Data</p>
      <div className="grid grid-cols-2 gap-2 text-sm">
        {Object.entries(payload).slice(0, 6).map(([key, value]) => (
          <div key={key}>
            <p className="text-xs text-gray-500 capitalize">{key.replace(/_/g, ' ')}</p>
            <p className="font-medium truncate">
              {typeof value === 'object' ? JSON.stringify(value) : String(value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

// Session 763: Style mapping for Mission Control action buttons
const ACTION_STYLE_MAP: Record<string, string> = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700',
  success: 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30',
  danger: 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30',
  warning: 'bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30',
  secondary: 'bg-dark-card text-gray-300 hover:bg-dark-hover',
}

// Decision Modal - Session 742: Enhanced with payload display and item type badges
// Session 763: Added Mission Control execute action support
// Session 819: Added Canon promotion support
function DecisionModal({
  item,
  onClose,
  onDecide,
  onExecuteAction,
  onPromoteToCanon,
  isLoading,
  isExecuting,
  isPromoting,
}: {
  item: AttentionItem
  onClose: () => void
  onDecide: (decision: string, feedback: string, confidence: number) => void
  onExecuteAction?: (action: string, feedback: string) => void
  onPromoteToCanon?: (category: 'creative' | 'technical' | 'operational') => void
  isLoading: boolean
  isExecuting?: boolean
  isPromoting?: boolean
}) {
  const [feedback, setFeedback] = useState('')
  const [confidence, setConfidence] = useState(80)

  const urgencyConfig = URGENCY_CONFIG[item.urgency]
  const UrgencyIcon = urgencyConfig.icon
  const itemTypeConfig = ITEM_TYPE_CONFIG[item.item_type] || { color: 'bg-gray-500', textColor: 'text-gray-400', icon: Activity, label: item.item_type }
  const ItemTypeIcon = itemTypeConfig.icon

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-xl max-w-2xl w-full max-h-[90vh] overflow-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', `${urgencyConfig.color}/20`)}>
              <UrgencyIcon className={urgencyConfig.textColor} size={20} />
            </div>
            <div>
              <h3 className="font-semibold">{item.title}</h3>
              <div className="flex items-center gap-2 mt-1">
                {/* Item Type Badge */}
                <span className={cn('inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium', `${itemTypeConfig.color}/20`, itemTypeConfig.textColor)}>
                  <ItemTypeIcon size={12} />
                  {itemTypeConfig.label}
                </span>
                <span className="text-sm text-gray-400">{item.source_agent || item.source_type}</span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">&times;</button>
        </div>

        {/* Meta bar - Session 742: Show priority score and expiration */}
        <div className="flex items-center gap-4 px-4 py-2 bg-dark-bg/50 border-b border-dark-border text-xs">
          <div className="flex items-center gap-1">
            <BarChart3 size={12} className="text-gray-500" />
            <span className="text-gray-400">Priority:</span>
            <span className="font-medium">{(item.priority_score ?? 0).toFixed(1)}</span>
          </div>
          {item.expires_at && (
            <div className="flex items-center gap-1">
              <Timer size={12} className="text-accent-amber" />
              <span className="text-gray-400">Expires:</span>
              <span className="font-medium text-accent-amber">
                {new Date(item.expires_at).toLocaleString()}
              </span>
            </div>
          )}
          {item.impact_estimate && (
            <div className="flex items-center gap-1">
              <Target size={12} className="text-gray-500" />
              <span className="text-gray-400">Impact:</span>
              <span className="font-medium">{item.impact_estimate}</span>
            </div>
          )}
          <div className="flex items-center gap-1 ml-auto">
            <Clock size={12} className="text-gray-500" />
            <span className="text-gray-400">{new Date(item.created_at).toLocaleString()}</span>
          </div>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          <div className="prose prose-invert max-w-none">
            <p className="text-gray-300">{item.summary}</p>
          </div>

          {/* Session 742: Rich Payload Display */}
          <PayloadDisplay item={item} />

          {/* ML Recommendation */}
          {item.ml_recommendation && (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-primary-500/10 border border-primary-500/30">
              <Bot className="text-primary-400" size={20} />
              <div>
                <p className="text-sm font-medium text-primary-400">ML Recommendation</p>
                <p className="text-sm text-gray-300">
                  {item.ml_recommendation}
                  {item.ml_confidence && (
                    <span className="ml-2 text-gray-500">
                      ({Math.round(item.ml_confidence * 100)}% confidence)
                    </span>
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Feedback */}
          <div>
            <label className="block text-sm font-medium mb-2">Your Notes (Optional)</label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full px-4 py-3 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
              rows={3}
              placeholder="Add any notes about your decision..."
            />
          </div>

          {/* Confidence Slider */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Your Confidence: {confidence}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={confidence}
              onChange={(e) => setConfidence(parseInt(e.target.value))}
              className="w-full accent-primary-500"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-2 p-4 border-t border-dark-border">
          {/* Session 763: Render dynamic Mission Control actions if available */}
          {item.payload?.available_actions && item.payload.available_actions.length > 0 && onExecuteAction ? (
            <>
              {/* Mission Control Actions */}
              <div className="w-full mb-2">
                <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                  <Zap size={12} className="text-primary-400" />
                  Mission Control Actions
                </p>
                <div className="flex flex-wrap gap-2">
                  {item.payload.available_actions.map((action: AvailableAction) => (
                    <button
                      key={action.id}
                      onClick={() => onExecuteAction(action.id, feedback)}
                      disabled={isLoading || isExecuting}
                      className={cn(
                        'btn flex items-center gap-2',
                        ACTION_STYLE_MAP[action.style || 'secondary']
                      )}
                      title={action.description}
                    >
                      {(isLoading || isExecuting) ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : null}
                      {action.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="w-full border-t border-dark-border my-2 pt-2">
                <p className="text-xs text-gray-500 mb-2">Standard Actions</p>
              </div>
            </>
          ) : null}

          {/* Standard decision actions */}
          <button
            onClick={() => onDecide('approve', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className="btn btn-primary flex items-center gap-2"
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : <ThumbsUp size={16} />}
            Approve
          </button>
          <button
            onClick={() => onDecide('reject', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className="btn flex items-center gap-2 bg-accent-red/20 text-accent-red hover:bg-accent-red/30"
          >
            <ThumbsDown size={16} />
            Reject
          </button>
          <button
            onClick={() => onDecide('modify', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className="btn btn-secondary"
          >
            Modify
          </button>
          <button
            onClick={() => onDecide('defer', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className="btn btn-secondary"
          >
            Defer
          </button>
          <button
            onClick={() => onDecide('escalate', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className="btn flex items-center gap-2 bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30"
          >
            <AlertTriangle size={16} />
            Escalate
          </button>

          {/* Session 746: Watch & Verify button - especially useful for arbitrage opportunities */}
          <button
            onClick={() => onDecide('watch', feedback, confidence / 100)}
            disabled={isLoading || isExecuting}
            className={cn(
              "btn flex items-center gap-2",
              item.item_type === 'arbitrage'
                ? "bg-cyan-500/30 text-cyan-300 hover:bg-cyan-500/40 ring-1 ring-cyan-500/50"
                : "bg-cyan-500/20 text-cyan-400 hover:bg-cyan-500/30"
            )}
          >
            <Eye size={16} />
            Watch & Verify
          </button>

          {/* Session 819: Promote to Canon button for high-quality content */}
          {onPromoteToCanon && ['review', 'insight', 'approval'].includes(item.item_type) && (
            <div className="relative group">
              <button
                disabled={isLoading || isExecuting || isPromoting}
                className="btn flex items-center gap-2 bg-purple-500/20 text-purple-400 hover:bg-purple-500/30"
                onClick={() => onPromoteToCanon('operational')}
              >
                {isPromoting ? <Loader2 size={16} className="animate-spin" /> : <BookMarked size={16} />}
                Promote to Canon
              </button>
              <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block">
                <div className="bg-dark-card border border-dark-border rounded-lg shadow-lg p-2 text-xs">
                  <div className="text-gray-400 mb-2">Select category:</div>
                  <div className="flex flex-col gap-1">
                    <button
                      onClick={() => onPromoteToCanon('creative')}
                      disabled={isPromoting}
                      className="px-3 py-1 rounded hover:bg-purple-500/20 text-left text-purple-300"
                    >
                      Creative
                    </button>
                    <button
                      onClick={() => onPromoteToCanon('technical')}
                      disabled={isPromoting}
                      className="px-3 py-1 rounded hover:bg-purple-500/20 text-left text-purple-300"
                    >
                      Technical
                    </button>
                    <button
                      onClick={() => onPromoteToCanon('operational')}
                      disabled={isPromoting}
                      className="px-3 py-1 rounded hover:bg-purple-500/20 text-left text-purple-300"
                    >
                      Operational
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function HumanPage() {
  const [activeTab, setActiveTab] = useState<'attention' | 'control' | 'preferences'>('attention')
  const [selectedItem, setSelectedItem] = useState<AttentionItem | null>(null)
  const [urgencyFilter, setUrgencyFilter] = useState<string[]>([])
  // Session 746: Add status filter to view acted/pending/all items
  const [statusFilter, setStatusFilter] = useState<string[]>(['pending', 'viewed'])
  // Session 746: Toggle for decision history view
  const [showDecisionHistory, setShowDecisionHistory] = useState(false)
  const [localPrefs, setLocalPrefs] = useState<Partial<Preferences>>({})
  const queryClient = useQueryClient()

  // Session 714: Real-time event handlers - refresh data when events occur
  const handleGateBecameCritical = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
    queryClient.invalidateQueries({ queryKey: ['human-control'] })
  }, [queryClient])

  const handleBodyStatusChanged = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['body-vitals'] })
  }, [queryClient])

  const handlePilotEvent = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['human-attention'] })
    queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
  }, [queryClient])

  // Session 714: Subscribe to system events
  useSystemEvents({
    onGateBecameCritical: handleGateBecameCritical,
    onBodyStatusChanged: handleBodyStatusChanged,
    onPilotStarted: handlePilotEvent,
    onPilotCompleted: handlePilotEvent,
  })

  // REST API queries
  // Session 746: Include status filter in API call
  const { data: attentionResponse, isLoading: loadingAttention, refetch: refetchAttention, error: attentionError } = useQuery({
    queryKey: ['human-attention', urgencyFilter, statusFilter],
    queryFn: () => humanApi.attention({
      limit: 100,
      urgency: urgencyFilter.length > 0 ? urgencyFilter : undefined,
      status: statusFilter.length > 0 ? statusFilter : undefined,
    }),
  })

  // Debug: Log API response
  if (attentionError) {
    console.error('Human Attention API Error:', attentionError)
  }
  if (attentionResponse) {
    console.log('Human Attention API Response:', attentionResponse.data)
  }

  const { data: statsResponse, isLoading: loadingStats } = useQuery({
    queryKey: ['human-attention-stats'],
    queryFn: () => humanApi.attentionStats(),
  })

  const { data: controlResponse, isLoading: loadingControl, refetch: refetchControl } = useQuery({
    queryKey: ['human-control'],
    queryFn: () => humanApi.control(),
  })

  const { data: preferencesResponse, isLoading: loadingPreferences } = useQuery({
    queryKey: ['human-preferences'],
    queryFn: () => humanApi.preferences(),
  })

  const { data: agentsResponse } = useQuery({
    queryKey: ['agents-list'],
    queryFn: () => agentsApi.list(),
  })

  // Session 712: Body Health integration - connect consciousness to body
  const { data: bodyVitalsResponse } = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000, // Refresh every 60 seconds
  })

  // Mutations
  const decideMutation = useMutation({
    mutationFn: ({ itemId, decision, feedback, confidence }: { itemId: string; decision: string; feedback: string; confidence: number }) =>
      humanApi.decide(itemId, decision, feedback, confidence),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
      setSelectedItem(null)
    },
  })

  // Session 763: Mission Control execute action mutation
  const executeActionMutation = useMutation({
    mutationFn: ({ itemId, action, feedback, extraData }: { itemId: string; action: string; feedback?: string; extraData?: Record<string, unknown> }) =>
      humanApi.executeAction(itemId, action, feedback, extraData),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
      queryClient.invalidateQueries({ queryKey: ['human-attention-stats'] })
      // Show success message from response
      const data = response.data
      if (data.message) {
        console.log('Action executed:', data.message)
      }
      setSelectedItem(null)
    },
  })

  // Session 819: Canon promotion mutation
  const canonPromoteMutation = useMutation({
    mutationFn: (params: {
      title: string
      content: string
      category: 'creative' | 'technical' | 'operational'
      source_type?: string
      source_id?: string
    }) => platformApi.promoteToCanon(params),
    onSuccess: (response) => {
      const data = response.data
      if (data.success) {
        console.log('Promoted to Canon:', data.path)
        // Invalidate canon data in platform queries
        queryClient.invalidateQueries({ queryKey: ['platform-canon'] })
        setSelectedItem(null)
      }
    },
  })

  const pauseAgentMutation = useMutation({
    mutationFn: ({ agent, reason }: { agent: string; reason?: string }) => humanApi.pauseAgent(agent, reason),
    onSuccess: () => refetchControl(),
  })

  const resumeAgentMutation = useMutation({
    mutationFn: ({ agent, reason }: { agent: string; reason?: string }) => humanApi.resumeAgent(agent, reason),
    onSuccess: () => refetchControl(),
  })

  const quietModeMutation = useMutation({
    mutationFn: ({ enabled, duration }: { enabled: boolean; duration?: number }) =>
      humanApi.setQuietMode(enabled, duration),
    onSuccess: () => refetchControl(),
  })

  const reviewModeMutation = useMutation({
    mutationFn: (enabled: boolean) => humanApi.setReviewMode(enabled),
    onSuccess: () => refetchControl(),
  })

  const thresholdMutation = useMutation({
    mutationFn: (threshold: number) => humanApi.adjustThreshold(threshold),
    onSuccess: () => refetchControl(),
  })

  const updatePrefsMutation = useMutation({
    mutationFn: (data: Partial<Preferences>) => humanApi.updatePreferences(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['human-preferences'] })
      setLocalPrefs({})
    },
  })

  // Helper to update a preference
  const updatePref = (key: keyof Preferences, value: unknown) => {
    const newPrefs = { ...localPrefs, [key]: value }
    setLocalPrefs(newPrefs)
    updatePrefsMutation.mutate({ [key]: value })
  }

  // Data extraction
  const attentionItems: AttentionItem[] = attentionResponse?.data?.items || []
  const stats: AttentionStats = statsResponse?.data?.stats || {}
  const systemState: SystemState = controlResponse?.data?.state || {}
  const preferences: Preferences = preferencesResponse?.data?.preferences || {}
  const agentsList = agentsResponse?.data?.agents || []

  // Session 712: Body health data
  const bodyVitals = bodyVitalsResponse?.data || null
  const bodyHealthScore = bodyVitals?.health_score || 0
  const bodyOverallStatus = bodyVitals?.overall_health || 'unknown'
  const bodySystems = bodyVitals?.systems || {}

  // Group items by urgency
  const groupedItems = useMemo(() => {
    const groups: Record<string, AttentionItem[]> = {
      critical: [],
      high: [],
      medium: [],
      low: [],
    }
    attentionItems.forEach((item) => {
      groups[item.urgency]?.push(item)
    })
    return groups
  }, [attentionItems])

  const isLoading = loadingAttention || loadingStats || loadingControl || loadingPreferences

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin h-8 w-8 border-2 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  // Show error if API call failed
  if (attentionError) {
    return (
      <div className="card text-center py-12">
        <XCircle className="mx-auto mb-4 text-accent-red" size={48} />
        <h3 className="text-lg font-semibold mb-2">Failed to Load Attention Items</h3>
        <p className="text-gray-400 mb-4">
          {(attentionError as Error)?.message || 'Authentication may be required. Please log in again.'}
        </p>
        <button
          onClick={() => refetchAttention()}
          className="btn btn-primary"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary-500/20 flex items-center justify-center">
            <User size={24} className="text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Human Interface</h1>
            <p className="text-sm text-gray-400">Your control center for the AI ecosystem</p>
          </div>
        </div>

        {/* System Status Indicators */}
        <div className="flex items-center gap-3">
          {systemState.quiet_mode && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-purple/20 text-accent-purple text-sm">
              <Moon size={14} />
              Quiet Mode
            </span>
          )}
          {systemState.review_mode && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-amber/20 text-accent-amber text-sm">
              <Eye size={14} />
              Review Mode
            </span>
          )}
          {systemState.system_paused && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-accent-red/20 text-accent-red text-sm">
              <Pause size={14} />
              System Paused
            </span>
          )}
        </div>
      </div>

      {/* Session 712: Body Health Card - Consciousness connected to Body */}
      {bodyVitals && (
        <a
          href="/body-health"
          className="card hover:border-primary-500/50 transition-colors group cursor-pointer block"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={cn(
                'h-12 w-12 rounded-full flex items-center justify-center',
                bodyHealthScore >= 80 ? 'bg-accent-green/20' :
                bodyHealthScore >= 60 ? 'bg-accent-amber/20' :
                bodyHealthScore >= 40 ? 'bg-accent-orange/20' : 'bg-accent-red/20'
              )}>
                <Heart className={cn(
                  'animate-pulse',
                  bodyHealthScore >= 80 ? 'text-accent-green' :
                  bodyHealthScore >= 60 ? 'text-accent-amber' :
                  bodyHealthScore >= 40 ? 'text-accent-orange' : 'text-accent-red'
                )} size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-400">Body Health</p>
                <p className="text-2xl font-bold">{Math.round(bodyHealthScore)}%</p>
                <p className={cn(
                  'text-sm capitalize',
                  bodyOverallStatus === 'healthy' ? 'text-accent-green' :
                  bodyOverallStatus === 'degraded' ? 'text-accent-amber' : 'text-accent-red'
                )}>
                  {bodyOverallStatus}
                </p>
              </div>
            </div>
            <div className="flex flex-col items-end gap-2">
              {/* System emoji strip */}
              <div className="flex gap-1 text-lg">
                {Object.entries(bodySystems).map(([name, system]: [string, any]) => (
                  <span key={name} title={`${name}: ${system.status}`}>
                    {system.emoji || '❓'}
                  </span>
                ))}
              </div>
              <div className="flex items-center gap-1 text-sm text-gray-400 group-hover:text-primary-400">
                <span>View Details</span>
                <ExternalLink size={14} />
              </div>
            </div>
          </div>
        </a>
      )}

      {/* Stats Cards - Primary Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <Bell className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Pending</p>
              <p className="text-2xl font-bold">{stats.pending_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-accent-red" size={24} />
            <div>
              <p className="text-sm text-gray-400">Urgent</p>
              <p className="text-2xl font-bold">
                {(stats.by_urgency?.critical || 0) + (stats.by_urgency?.high || 0)}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Eye className="text-cyan-400" size={24} />
            <div>
              <p className="text-sm text-gray-400">Watching</p>
              <p className="text-2xl font-bold">{stats.watching_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <DollarSign className={cn("size-6", (stats.paper_profit || 0) >= 0 ? "text-accent-green" : "text-accent-red")} />
            <div>
              <p className="text-sm text-gray-400">Paper P/L</p>
              <p className={cn("text-2xl font-bold", (stats.paper_profit || 0) >= 0 ? "text-accent-green" : "text-accent-red")}>
                {(stats.paper_profit || 0) >= 0 ? '+' : ''}${(stats.paper_profit || 0).toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Cards - Secondary Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <Timer className="text-accent-cyan" size={20} />
            <div>
              <p className="text-xs text-gray-400">Avg Decision</p>
              <p className="text-lg font-bold">
                {stats.avg_decision_time_ms ? `${Math.round(stats.avg_decision_time_ms / 1000)}s` : '--'}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Bot className="text-primary-400" size={20} />
            <div>
              <p className="text-xs text-gray-400">ML Agreement</p>
              <p className="text-lg font-bold">
                {stats.ml_agreement_rate ? `${Math.round(stats.ml_agreement_rate)}%` : '--'}
              </p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Scale className="text-accent-amber" size={20} />
            <div>
              <p className="text-xs text-gray-400">ML Overrides</p>
              <p className="text-lg font-bold">{stats.override_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Database className="text-accent-purple" size={20} />
            <div>
              <p className="text-xs text-gray-400">Feedback Records</p>
              <p className="text-lg font-bold">{stats.feedback_count || 0}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Brain className="text-primary-400" size={20} />
            <div>
              <p className="text-xs text-gray-400">Fed to ML</p>
              <p className="text-lg font-bold">{stats.fed_to_ml_count || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Expandable Stats Breakdown */}
      <details className="card">
        <summary className="flex items-center gap-2 cursor-pointer font-medium">
          <PieChart size={18} className="text-primary-400" />
          Detailed Breakdown
          <span className="text-sm text-gray-400 ml-2">({stats.total_items || 0} total items)</span>
        </summary>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* By Item Type */}
          <div className="p-3 rounded-lg bg-dark-bg">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <Activity size={14} className="text-primary-400" />
              By Type
            </h4>
            <div className="space-y-1">
              {Object.entries(stats.by_type || {}).map(([type, count]) => (
                <div key={type} className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{type}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
              {Object.keys(stats.by_type || {}).length === 0 && (
                <p className="text-xs text-gray-500">No data</p>
              )}
            </div>
          </div>

          {/* By Source Agent */}
          <div className="p-3 rounded-lg bg-dark-bg">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <Bot size={14} className="text-accent-cyan" />
              By Agent
            </h4>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {Object.entries(stats.by_source || {}).map(([agent, count]) => (
                <div key={agent} className="flex justify-between text-sm">
                  <span className="text-gray-400 truncate max-w-[150px]">{agent}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
              {Object.keys(stats.by_source || {}).length === 0 && (
                <p className="text-xs text-gray-500">No data</p>
              )}
            </div>
          </div>

          {/* By Decision */}
          <div className="p-3 rounded-lg bg-dark-bg">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <GitBranch size={14} className="text-accent-green" />
              By Decision
            </h4>
            <div className="space-y-1">
              {Object.entries(stats.by_decision || {}).map(([decision, count]) => (
                <div key={decision} className="flex justify-between text-sm">
                  <span className="text-gray-400 capitalize">{decision}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
              {Object.keys(stats.by_decision || {}).length === 0 && (
                <p className="text-xs text-gray-500">No decisions yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Verification Stats */}
        {(stats.watching_count > 0 || stats.verified_count > 0) && (
          <div className="mt-4 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2 text-cyan-400">
              <Eye size={14} />
              Watch & Verify Stats
            </h4>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-cyan-400">{stats.watching_count || 0}</p>
                <p className="text-xs text-gray-400">Watching</p>
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.verified_count || 0}</p>
                <p className="text-xs text-gray-400">Verified</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-accent-green">{stats.verification_outcomes?.won || 0}</p>
                <p className="text-xs text-gray-400">Would Win</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-accent-red">{stats.verification_outcomes?.lost || 0}</p>
                <p className="text-xs text-gray-400">Would Lose</p>
              </div>
              <div>
                <p className={cn("text-2xl font-bold", (stats.paper_profit || 0) >= 0 ? "text-accent-green" : "text-accent-red")}>
                  {(stats.paper_profit || 0) >= 0 ? '+' : ''}${(stats.paper_profit || 0).toFixed(2)}
                </p>
                <p className="text-xs text-gray-400">Paper P/L</p>
              </div>
            </div>
          </div>
        )}
      </details>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-dark-border pb-4">
        {[
          { id: 'attention', label: 'Attention Stream', icon: Bell },
          { id: 'control', label: 'Control Panel', icon: Sliders },
          { id: 'preferences', label: 'Preferences', icon: Settings },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id as typeof activeTab)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-card'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'attention' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-col gap-3">
            {/* Urgency Filter */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">Urgency:</span>
                <div className="flex gap-2">
                  {(['critical', 'high', 'medium', 'low'] as const).map((urgency) => {
                    const config = URGENCY_CONFIG[urgency]
                    const isSelected = urgencyFilter.includes(urgency)
                    return (
                      <button
                        key={urgency}
                        onClick={() => {
                          setUrgencyFilter((prev) =>
                            isSelected ? prev.filter((u) => u !== urgency) : [...prev, urgency]
                          )
                        }}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-sm capitalize transition-colors',
                          isSelected
                            ? `${config.color} text-white`
                            : `${config.color}/20 ${config.textColor} hover:${config.color}/30`
                        )}
                      >
                        {urgency}
                      </button>
                    )
                  })}
                </div>
              </div>
              <button
                onClick={() => refetchAttention()}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-white"
              >
                <RefreshCw size={14} />
                Refresh
              </button>
            </div>

            {/* Session 746: Status Filter */}
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-400">Status:</span>
              <div className="flex gap-2">
                {[
                  { value: 'pending', label: 'Pending', color: 'bg-yellow-500' },
                  { value: 'viewed', label: 'Viewed', color: 'bg-blue-500' },
                  { value: 'acted', label: 'Acted', color: 'bg-green-500' },
                  { value: 'deferred', label: 'Deferred', color: 'bg-purple-500' },
                  // Session 746: Add watching and verified statuses for arbitrage verification
                  { value: 'watching', label: 'Watching', color: 'bg-cyan-500' },
                  { value: 'verified', label: 'Verified', color: 'bg-emerald-500' },
                ].map((status) => {
                  const isSelected = statusFilter.includes(status.value)
                  return (
                    <button
                      key={status.value}
                      onClick={() => {
                        setStatusFilter((prev) =>
                          isSelected ? prev.filter((s) => s !== status.value) : [...prev, status.value]
                        )
                      }}
                      className={cn(
                        'px-3 py-1.5 rounded-lg text-sm transition-colors',
                        isSelected
                          ? `${status.color} text-white`
                          : `${status.color}/20 text-gray-300 hover:${status.color}/30`
                      )}
                    >
                      {status.label}
                    </button>
                  )
                })}
              </div>
              <button
                onClick={() => setStatusFilter(['pending', 'viewed'])}
                className="ml-2 px-2 py-1 text-xs text-gray-500 hover:text-gray-300"
              >
                Reset
              </button>
            </div>

            {/* Session 746: Decision History Toggle */}
            <div className="flex items-center gap-2 ml-auto">
              <button
                onClick={() => setShowDecisionHistory(!showDecisionHistory)}
                className={cn(
                  'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors',
                  showDecisionHistory
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-card text-gray-400 hover:text-white'
                )}
              >
                <History size={14} />
                Decision History
              </button>
            </div>
          </div>

          {/* Session 746: Decision History View */}
          {showDecisionHistory && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <History size={20} className="text-primary-400" />
                Decision History
              </h3>
              {attentionItems.filter(i => i.decision).length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <History size={32} className="mx-auto mb-2 opacity-50" />
                  <p>No decisions recorded yet</p>
                  <p className="text-xs mt-1">Make decisions on pending items to see them here</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="border-b border-dark-border">
                      <tr className="text-left text-gray-400">
                        <th className="pb-2 font-medium">Item</th>
                        <th className="pb-2 font-medium">Type</th>
                        <th className="pb-2 font-medium">Decision</th>
                        <th className="pb-2 font-medium">Confidence</th>
                        <th className="pb-2 font-medium">ML Override</th>
                        <th className="pb-2 font-medium">Time to Decide</th>
                        <th className="pb-2 font-medium">Decided At</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-dark-border">
                      {attentionItems
                        .filter(i => i.decision)
                        .sort((a, b) => new Date(b.decided_at || 0).getTime() - new Date(a.decided_at || 0).getTime())
                        .slice(0, 20)
                        .map((item) => (
                          <tr key={item.id} className="hover:bg-dark-hover">
                            <td className="py-2">
                              <span className="font-medium truncate max-w-[200px] block" title={item.title}>
                                {item.title.slice(0, 40)}{item.title.length > 40 ? '...' : ''}
                              </span>
                            </td>
                            <td className="py-2">
                              <span className="capitalize text-gray-400">{item.item_type}</span>
                            </td>
                            <td className="py-2">
                              <span className={cn(
                                'px-2 py-0.5 rounded text-xs font-medium capitalize',
                                item.decision === 'approve' ? 'bg-accent-green/20 text-accent-green' :
                                item.decision === 'reject' ? 'bg-accent-red/20 text-accent-red' :
                                item.decision === 'watch' ? 'bg-cyan-500/20 text-cyan-400' :
                                item.decision === 'modify' ? 'bg-accent-amber/20 text-accent-amber' :
                                item.decision === 'defer' ? 'bg-accent-purple/20 text-accent-purple' :
                                'bg-gray-500/20 text-gray-400'
                              )}>
                                {item.decision}
                              </span>
                            </td>
                            <td className="py-2">
                              {item.decision_confidence ? (
                                <span className={cn(
                                  'text-xs',
                                  item.decision_confidence >= 0.8 ? 'text-accent-green' :
                                  item.decision_confidence >= 0.5 ? 'text-accent-amber' : 'text-accent-red'
                                )}>
                                  {Math.round(item.decision_confidence * 100)}%
                                </span>
                              ) : (
                                <span className="text-gray-500">--</span>
                              )}
                            </td>
                            <td className="py-2">
                              {item.human_overrode_ml ? (
                                <span className="flex items-center gap-1 text-accent-amber">
                                  <AlertOctagon size={12} />
                                  Yes
                                </span>
                              ) : item.ml_confidence ? (
                                <span className="text-gray-500">No</span>
                              ) : (
                                <span className="text-gray-600">N/A</span>
                              )}
                            </td>
                            <td className="py-2">
                              {item.time_to_decision_ms ? (
                                <span className="text-gray-300">
                                  {item.time_to_decision_ms < 60000
                                    ? `${Math.round(item.time_to_decision_ms / 1000)}s`
                                    : `${Math.round(item.time_to_decision_ms / 60000)}m`}
                                </span>
                              ) : (
                                <span className="text-gray-500">--</span>
                              )}
                            </td>
                            <td className="py-2 text-gray-400 text-xs">
                              {item.decided_at ? new Date(item.decided_at).toLocaleString() : '--'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
              {/* Feedback notes */}
              {attentionItems.filter(i => i.decision && i.decision_feedback).length > 0 && (
                <details className="mt-4">
                  <summary className="text-sm text-gray-400 cursor-pointer hover:text-white">
                    View decision notes ({attentionItems.filter(i => i.decision_feedback).length})
                  </summary>
                  <div className="mt-2 space-y-2 max-h-40 overflow-y-auto">
                    {attentionItems
                      .filter(i => i.decision_feedback)
                      .map(item => (
                        <div key={item.id} className="p-2 rounded bg-dark-bg text-sm">
                          <span className="font-medium">{item.title.slice(0, 30)}:</span>
                          <span className="text-gray-400 ml-2 italic">"{item.decision_feedback}"</span>
                        </div>
                      ))}
                  </div>
                </details>
              )}
            </div>
          )}

          {/* Attention Items by Urgency */}
          {!showDecisionHistory && attentionItems.length === 0 ? (
            <div className="card text-center py-12">
              <CheckCircle className="mx-auto mb-4 text-accent-green" size={48} />
              <h3 className="text-lg font-semibold mb-2">All Clear!</h3>
              <p className="text-gray-400">No items requiring your attention right now.</p>
            </div>
          ) : !showDecisionHistory && (
            <div className="space-y-4">
              {Object.entries(groupedItems)
                .filter(([, items]) => items.length > 0)
                .map(([urgency, items]) => {
                  const config = URGENCY_CONFIG[urgency as keyof typeof URGENCY_CONFIG]
                  const UrgencyIcon = config.icon
                  return (
                    <div key={urgency} className="card p-0 overflow-hidden">
                      <div className={cn('flex items-center gap-2 px-4 py-3', `${config.color}/20`)}>
                        <UrgencyIcon className={config.textColor} size={18} />
                        <span className={cn('font-medium capitalize', config.textColor)}>
                          {urgency}
                        </span>
                        <span className="text-sm text-gray-400">({items.length})</span>
                      </div>
                      {/* Session 746: Add scroll area for each urgency section */}
                      <div className="divide-y divide-dark-border max-h-80 overflow-y-auto">
                        {items.map((item) => {
                          // Session 742: Add item type config for list view
                          const listItemTypeConfig = ITEM_TYPE_CONFIG[item.item_type] || { color: 'bg-gray-500', textColor: 'text-gray-400', icon: Activity, label: item.item_type }
                          const ListItemIcon = listItemTypeConfig.icon
                          return (
                            <div
                              key={item.id}
                              onClick={() => setSelectedItem(item)}
                              className="flex items-start gap-4 p-4 hover:bg-dark-hover cursor-pointer transition-colors"
                            >
                              <div className={cn('p-2 rounded-lg', `${listItemTypeConfig.color}/20`)}>
                                <ListItemIcon className={listItemTypeConfig.textColor} size={16} />
                              </div>
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium">{item.title}</h4>
                                  {/* Session 742: Show profit % for arbitrage items */}
                                  {item.item_type === 'arbitrage' && !!item.payload?.profit_pct && (
                                    <span className="px-2 py-0.5 rounded bg-accent-green/20 text-accent-green text-xs font-bold">
                                      +{(Number(item.payload.profit_pct) || 0).toFixed(2)}%
                                    </span>
                                  )}
                                  {item.item_type === 'arbitrage' && item.payload?.rating === 'HOT' && (
                                    <span className="px-2 py-0.5 rounded bg-accent-red/20 text-accent-red text-xs font-bold animate-pulse">
                                      HOT
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-gray-400 mt-1 line-clamp-2">
                                  {item.summary}
                                </p>
                                <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                                  {/* Session 742: Item type badge */}
                                  <span className={cn('px-2 py-0.5 rounded', `${listItemTypeConfig.color}/20`, listItemTypeConfig.textColor)}>
                                    {listItemTypeConfig.label}
                                  </span>
                                  <span>{item.source_agent || item.source_type}</span>
                                  <span>{new Date(item.created_at).toLocaleString()}</span>
                                  {item.ml_confidence && (
                                    <span className="px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                                      ML: {Math.round(item.ml_confidence * 100)}%
                                    </span>
                                  )}
                                  {/* Session 746: ML Override indicator */}
                                  {item.human_overrode_ml && (
                                    <span className="px-2 py-0.5 rounded bg-accent-amber/20 text-accent-amber flex items-center gap-1">
                                      <AlertOctagon size={10} />
                                      Overrode ML
                                    </span>
                                  )}
                                  {/* Session 746: Decision badge for acted items */}
                                  {item.decision && (
                                    <span className={cn(
                                      'px-2 py-0.5 rounded capitalize',
                                      item.decision === 'approve' ? 'bg-accent-green/20 text-accent-green' :
                                      item.decision === 'reject' ? 'bg-accent-red/20 text-accent-red' :
                                      item.decision === 'watch' ? 'bg-cyan-500/20 text-cyan-400' :
                                      'bg-gray-500/20 text-gray-400'
                                    )}>
                                      {item.decision}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <ChevronRight className="text-gray-500" size={18} />
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'control' && (
        <div className="space-y-4">
          {/* Global Controls */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">System Controls</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Quiet Mode */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Moon className="text-accent-purple" size={18} />
                    <span className="font-medium">Quiet Mode</span>
                  </div>
                  <button
                    onClick={() => quietModeMutation.mutate({ enabled: !systemState.quiet_mode })}
                    disabled={quietModeMutation.isPending}
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                      systemState.quiet_mode
                        ? 'bg-accent-purple text-white'
                        : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                    )}
                  >
                    {systemState.quiet_mode ? 'ON' : 'OFF'}
                  </button>
                </div>
                <p className="text-xs text-gray-500">Suppress non-critical notifications</p>
              </div>

              {/* Review Mode */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Eye className="text-accent-amber" size={18} />
                    <span className="font-medium">Review Mode</span>
                  </div>
                  <button
                    onClick={() => reviewModeMutation.mutate(!systemState.review_mode)}
                    disabled={reviewModeMutation.isPending}
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                      systemState.review_mode
                        ? 'bg-accent-amber text-white'
                        : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                    )}
                  >
                    {systemState.review_mode ? 'ON' : 'OFF'}
                  </button>
                </div>
                <p className="text-xs text-gray-500">Require approval for all decisions</p>
              </div>

              {/* ML Threshold */}
              <div className="p-4 rounded-lg bg-dark-bg border border-dark-border">
                <div className="flex items-center gap-2 mb-3">
                  <Bot className="text-primary-400" size={18} />
                  <span className="font-medium">ML Threshold</span>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}
                    onChange={(e) => thresholdMutation.mutate(parseInt(e.target.value) / 100)}
                    className="flex-1 accent-primary-500"
                  />
                  <span className="text-sm font-medium w-12">
                    {Math.round((systemState.ml_confidence_threshold || 0.6) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Paused Agents */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Agent Control</h3>
            <div className="space-y-2 max-h-[400px] overflow-auto">
              {agentsList.slice(0, 20).map((agent: { name: string; description?: string }) => {
                const isPaused = systemState.paused_agents?.includes(agent.name)
                return (
                  <div
                    key={agent.name}
                    className="flex items-center justify-between p-3 rounded-lg bg-dark-bg"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'h-2 w-2 rounded-full',
                        isPaused ? 'bg-accent-red' : 'bg-accent-green'
                      )} />
                      <span>{agent.name}</span>
                    </div>
                    <button
                      onClick={() =>
                        isPaused
                          ? resumeAgentMutation.mutate({ agent: agent.name })
                          : pauseAgentMutation.mutate({ agent: agent.name })
                      }
                      disabled={pauseAgentMutation.isPending || resumeAgentMutation.isPending}
                      className={cn(
                        'flex items-center gap-1 px-3 py-1 rounded text-sm transition-colors',
                        isPaused
                          ? 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30'
                          : 'bg-accent-red/20 text-accent-red hover:bg-accent-red/30'
                      )}
                    >
                      {isPaused ? (
                        <>
                          <Play size={12} /> Resume
                        </>
                      ) : (
                        <>
                          <Pause size={12} /> Pause
                        </>
                      )}
                    </button>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Session 746: Control Action History / Audit Log */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <History size={20} className="text-primary-400" />
              Control Action History
            </h3>
            {stats.recent_actions && stats.recent_actions.length > 0 ? (
              <div className="space-y-2 max-h-[300px] overflow-auto">
                {stats.recent_actions.map((action, index) => (
                  <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-dark-bg">
                    <div className={cn(
                      'p-2 rounded-lg',
                      action.action_type.includes('pause') ? 'bg-accent-red/20' :
                      action.action_type.includes('resume') ? 'bg-accent-green/20' :
                      action.action_type.includes('quiet') ? 'bg-accent-purple/20' :
                      'bg-primary-500/20'
                    )}>
                      {action.action_type.includes('pause') ? <Pause size={14} className="text-accent-red" /> :
                       action.action_type.includes('resume') ? <Play size={14} className="text-accent-green" /> :
                       action.action_type.includes('quiet') ? <Moon size={14} className="text-accent-purple" /> :
                       action.action_type.includes('review') ? <Eye size={14} className="text-accent-amber" /> :
                       <Settings size={14} className="text-primary-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm capitalize">
                        {action.action_type.replace(/_/g, ' ')}
                      </p>
                      <p className="text-xs text-gray-400">
                        {action.target_type}: {action.target_id}
                      </p>
                      {action.reason && (
                        <p className="text-xs text-gray-500 mt-1 italic">"{action.reason}"</p>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 whitespace-nowrap">
                      {new Date(action.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <History size={32} className="mx-auto mb-2 opacity-50" />
                <p>No control actions recorded yet</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'preferences' && (
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Minimum Urgency to Notify</label>
                <select
                  value={localPrefs.min_urgency_to_notify ?? preferences.min_urgency_to_notify ?? 'medium'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('min_urgency_to_notify', e.target.value)}
                >
                  <option value="critical">Critical Only</option>
                  <option value="high">High and Above</option>
                  <option value="medium">Medium and Above</option>
                  <option value="low">All</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Preferred Channel</label>
                <select
                  value={localPrefs.preferred_channel ?? preferences.preferred_channel ?? 'discord'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('preferred_channel', e.target.value)}
                >
                  <option value="discord">Discord</option>
                  <option value="web">Web Dashboard</option>
                  <option value="email">Email</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Review Depth</label>
                <select
                  value={localPrefs.review_depth ?? preferences.review_depth ?? 'standard'}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                  onChange={(e) => updatePref('review_depth', e.target.value)}
                >
                  <option value="quick">Quick (&lt; 30s)</option>
                  <option value="standard">Standard (30s-2min)</option>
                  <option value="thorough">Thorough (&gt; 2min)</option>
                </select>
              </div>
              <div className="flex items-center justify-between p-4 rounded-lg bg-dark-bg">
                <span>Auto-approve Low Risk Items</span>
                <button
                  onClick={() => updatePref('auto_approve_low_risk', !preferences.auto_approve_low_risk)}
                  className={cn(
                    'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                    preferences.auto_approve_low_risk
                      ? 'bg-accent-green text-white'
                      : 'bg-dark-card text-gray-400 hover:bg-dark-hover'
                  )}
                >
                  {preferences.auto_approve_low_risk ? 'ON' : 'OFF'}
                </button>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Quiet Hours</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Start Time</label>
                <input
                  type="time"
                  value={localPrefs.quiet_hours_start ?? preferences.quiet_hours_start ?? '22:00'}
                  onChange={(e) => updatePref('quiet_hours_start', e.target.value)}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">End Time</label>
                <input
                  type="time"
                  value={localPrefs.quiet_hours_end ?? preferences.quiet_hours_end ?? '08:00'}
                  onChange={(e) => updatePref('quiet_hours_end', e.target.value)}
                  className="w-full px-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white"
                />
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Your Stats</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">{preferences.total_decisions || 0}</p>
                <p className="text-sm text-gray-400">Total Decisions</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">
                  {preferences.avg_decision_time_ms ? `${Math.round(preferences.avg_decision_time_ms / 1000)}s` : '--'}
                </p>
                <p className="text-sm text-gray-400">Avg Decision Time</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <p className="text-2xl font-bold">
                  {preferences.approval_rate ? `${Math.round(preferences.approval_rate * 100)}%` : '--'}
                </p>
                <p className="text-sm text-gray-400">Approval Rate</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Decision Modal */}
      {selectedItem && (
        <DecisionModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
          onDecide={(decision, feedback, confidence) =>
            decideMutation.mutate({
              itemId: selectedItem.id,
              decision,
              feedback,
              confidence,
            })
          }
          // Session 763: Mission Control execute action
          onExecuteAction={(action, feedback) =>
            executeActionMutation.mutate({
              itemId: selectedItem.id,
              action,
              feedback,
            })
          }
          // Session 819: Canon promotion
          onPromoteToCanon={(category) =>
            canonPromoteMutation.mutate({
              title: selectedItem.title,
              content: selectedItem.summary + (selectedItem.payload ? '\n\n---\n\n' + JSON.stringify(selectedItem.payload, null, 2) : ''),
              category,
              source_type: selectedItem.source_type,
              source_id: selectedItem.source_id,
            })
          }
          isLoading={decideMutation.isPending}
          isExecuting={executeActionMutation.isPending}
          isPromoting={canonPromoteMutation.isPending}
        />
      )}
    </div>
  )
}
