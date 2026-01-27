// Session 843: Decision Detail Modal
// View full decision/attention item details without leaving Workspace

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  X,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Loader2,
  Hash,
  User,
  Brain,
  MessageSquare,
  Zap,
  Eye,
  Target,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { humanApi } from '@/lib/api'

interface DecisionDetailModalProps {
  decisionId: string
  onClose: () => void
}

interface Decision {
  id: string
  title: string
  summary: string
  urgency: string
  status: string
  item_type: string
  source_type: string
  source_agent: string
  source_id: string
  payload: Record<string, unknown>
  priority_score: number
  impact_estimate: number
  ml_prediction: string
  ml_confidence: number
  ml_recommendation: string
  decision: string
  decision_feedback: string
  decision_confidence: number
  decided_at: string | null
  human_overrode_ml: boolean
  override_reason: string
  deferred_until: string | null
  created_at: string
  viewed_at: string | null
  expires_at: string | null
  verification_outcome: string
  verified_at: string | null
  verification_profit: number
  verification_notes: string
}

export function DecisionDetailModal({ decisionId, onClose }: DecisionDetailModalProps) {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['decision-detail', decisionId],
    queryFn: async () => {
      const response = await humanApi.detail(decisionId)
      return response.data as { item: Decision }
    },
  })

  const decideMutation = useMutation({
    mutationFn: ({ decision, feedback }: { decision: string; feedback?: string }) =>
      humanApi.decide(decisionId, decision, feedback),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['decision-detail', decisionId] })
      queryClient.invalidateQueries({ queryKey: ['human-attention'] })
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
    },
  })

  const decision = data?.item

  const getUrgencyStyles = (urgency: string) => {
    switch (urgency?.toLowerCase()) {
      case 'critical':
        return {
          bg: 'bg-red-500/20',
          border: 'border-red-500/30',
          text: 'text-red-400',
          icon: <AlertTriangle size={16} className="text-red-400" />,
        }
      case 'high':
        return {
          bg: 'bg-amber-500/20',
          border: 'border-amber-500/30',
          text: 'text-amber-400',
          icon: <Zap size={16} className="text-amber-400" />,
        }
      case 'medium':
        return {
          bg: 'bg-blue-500/20',
          border: 'border-blue-500/30',
          text: 'text-blue-400',
          icon: <Target size={16} className="text-blue-400" />,
        }
      default:
        return {
          bg: 'bg-gray-500/20',
          border: 'border-gray-500/30',
          text: 'text-gray-400',
          icon: <MessageSquare size={16} className="text-gray-400" />,
        }
    }
  }

  const getStatusStyles = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'approved':
      case 'completed':
        return 'bg-green-500/20 text-green-400'
      case 'rejected':
      case 'dismissed':
        return 'bg-red-500/20 text-red-400'
      case 'deferred':
        return 'bg-amber-500/20 text-amber-400'
      case 'watching':
        return 'bg-purple-500/20 text-purple-400'
      default:
        return 'bg-gray-700 text-gray-400'
    }
  }

  const urgencyStyles = decision ? getUrgencyStyles(decision.urgency) : getUrgencyStyles('')

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className={cn(
          'flex items-center justify-between p-4 border-b border-dark-border',
          urgencyStyles.bg
        )}>
          <div className="flex items-center gap-3">
            <div className={cn('p-2 rounded-lg', urgencyStyles.bg)}>
              {urgencyStyles.icon}
            </div>
            <div>
              <h2 className="text-lg font-semibold">Decision Details</h2>
              <p className="text-xs text-gray-400">Human attention item</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-dark-border transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={32} className="animate-spin text-primary-400" />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle size={48} className="text-red-400 mb-4" />
              <p className="text-gray-400">Failed to load decision</p>
            </div>
          ) : decision ? (
            <>
              {/* Title & Status */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="font-medium text-white text-lg">{decision.title}</h3>
                    <div className="flex items-center gap-2 mt-2">
                      <span className={cn('text-xs px-2 py-0.5 rounded', urgencyStyles.bg, urgencyStyles.text)}>
                        {decision.urgency}
                      </span>
                      <span className={cn('text-xs px-2 py-0.5 rounded', getStatusStyles(decision.status))}>
                        {decision.status}
                      </span>
                      {decision.item_type && (
                        <span className="text-xs px-2 py-0.5 rounded bg-primary-500/20 text-primary-400">
                          {decision.item_type}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock size={12} />
                    {new Date(decision.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="bg-dark-bg rounded-lg p-4">
                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                  <MessageSquare size={12} />
                  Summary
                </h4>
                <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {decision.summary || 'No summary available'}
                </p>
              </div>

              {/* Source Info */}
              <div className="bg-dark-bg rounded-lg p-4">
                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">Source</h4>
                <div className="flex flex-wrap gap-4 text-sm">
                  {decision.source_agent && (
                    <div className="flex items-center gap-2">
                      <User size={14} className="text-gray-500" />
                      <span className="text-gray-400">Agent:</span>
                      <span className="text-white">{decision.source_agent}</span>
                    </div>
                  )}
                  {decision.source_type && (
                    <div className="flex items-center gap-2">
                      <Target size={14} className="text-gray-500" />
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white">{decision.source_type}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* ML Prediction */}
              {(decision.ml_prediction || decision.ml_recommendation) && (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-blue-400 uppercase mb-3 flex items-center gap-2">
                    <Brain size={12} />
                    AI Analysis
                  </h4>
                  <div className="space-y-2">
                    {decision.ml_recommendation && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-400">Recommendation:</span>
                        <span className="text-sm font-medium text-white px-2 py-0.5 bg-primary-500/20 rounded">
                          {decision.ml_recommendation}
                        </span>
                      </div>
                    )}
                    {decision.ml_confidence !== undefined && decision.ml_confidence !== null && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-400">Confidence:</span>
                        <span className={cn(
                          'text-sm font-medium',
                          decision.ml_confidence >= 0.8 ? 'text-green-400' :
                          decision.ml_confidence >= 0.6 ? 'text-yellow-400' : 'text-orange-400'
                        )}>
                          {Math.round(decision.ml_confidence * 100)}%
                        </span>
                      </div>
                    )}
                    {decision.ml_prediction && (
                      <div className="mt-2">
                        <span className="text-sm text-gray-400">Prediction:</span>
                        <p className="text-sm text-gray-200 mt-1">{decision.ml_prediction}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Scores */}
              {(decision.priority_score || decision.impact_estimate) && (
                <div className="bg-dark-bg rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">Scores</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {decision.priority_score !== undefined && decision.priority_score !== null && (
                      <div className="text-center">
                        <div className="text-2xl font-bold text-primary-400">
                          {typeof decision.priority_score === 'number'
                            ? decision.priority_score.toFixed(1)
                            : decision.priority_score}
                        </div>
                        <div className="text-xs text-gray-400">Priority Score</div>
                      </div>
                    )}
                    {decision.impact_estimate !== undefined && decision.impact_estimate !== null && (
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">
                          {typeof decision.impact_estimate === 'number'
                            ? `$${decision.impact_estimate.toFixed(2)}`
                            : decision.impact_estimate}
                        </div>
                        <div className="text-xs text-gray-400">Impact Estimate</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Decision Made */}
              {decision.decision && (
                <div className={cn(
                  'rounded-lg p-4 border',
                  decision.decision === 'approve' ? 'bg-green-500/10 border-green-500/20' :
                  decision.decision === 'reject' || decision.decision === 'dismiss' ? 'bg-red-500/10 border-red-500/20' :
                  'bg-gray-500/10 border-gray-500/20'
                )}>
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                    <CheckCircle size={12} />
                    Decision Made
                  </h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-white capitalize">{decision.decision}</span>
                      {decision.decided_at && (
                        <span className="text-xs text-gray-500">
                          on {new Date(decision.decided_at).toLocaleString()}
                        </span>
                      )}
                    </div>
                    {decision.decision_feedback && (
                      <p className="text-sm text-gray-300">{decision.decision_feedback}</p>
                    )}
                    {decision.human_overrode_ml && (
                      <div className="flex items-center gap-2 text-amber-400 text-xs">
                        <AlertTriangle size={12} />
                        Human overrode AI recommendation
                        {decision.override_reason && `: ${decision.override_reason}`}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Verification */}
              {decision.verification_outcome && (
                <div className={cn(
                  'rounded-lg p-4 border',
                  decision.verification_outcome === 'success' ? 'bg-green-500/10 border-green-500/20' :
                  decision.verification_outcome === 'failure' ? 'bg-red-500/10 border-red-500/20' :
                  'bg-purple-500/10 border-purple-500/20'
                )}>
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                    <Eye size={12} />
                    Verification Result
                  </h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-medium text-white capitalize">
                        {decision.verification_outcome}
                      </span>
                      {decision.verification_profit !== undefined && decision.verification_profit !== null && (
                        <span className={cn(
                          'text-sm font-medium',
                          decision.verification_profit >= 0 ? 'text-green-400' : 'text-red-400'
                        )}>
                          {decision.verification_profit >= 0 ? '+' : ''}${decision.verification_profit.toFixed(2)}
                        </span>
                      )}
                    </div>
                    {decision.verification_notes && (
                      <p className="text-sm text-gray-300">{decision.verification_notes}</p>
                    )}
                    {decision.verified_at && (
                      <span className="text-xs text-gray-500">
                        Verified on {new Date(decision.verified_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Payload */}
              {decision.payload && Object.keys(decision.payload).length > 0 && (
                <div className="bg-dark-bg rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                    <TrendingUp size={12} />
                    Additional Data
                  </h4>
                  <pre className="text-xs text-gray-300 bg-gray-900/50 p-3 rounded overflow-x-auto max-h-48">
                    {JSON.stringify(decision.payload, null, 2)}
                  </pre>
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-2">
                <span className="flex items-center gap-1">
                  <Hash size={12} />
                  {decision.id.slice(0, 8)}
                </span>
                {decision.viewed_at && (
                  <span className="flex items-center gap-1">
                    <Eye size={12} />
                    Viewed {new Date(decision.viewed_at).toLocaleString()}
                  </span>
                )}
                {decision.expires_at && (
                  <span className="flex items-center gap-1">
                    <Clock size={12} />
                    Expires {new Date(decision.expires_at).toLocaleString()}
                  </span>
                )}
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-center py-8">Decision not found</p>
          )}
        </div>

        {/* Footer with Actions */}
        <div className="p-4 border-t border-dark-border bg-dark-bg/50">
          {decision && decision.status === 'pending' ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => decideMutation.mutate({ decision: 'approve' })}
                disabled={decideMutation.isPending}
                className="flex-1 py-2 px-4 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <CheckCircle size={16} />
                Approve
              </button>
              <button
                onClick={() => decideMutation.mutate({ decision: 'dismiss' })}
                disabled={decideMutation.isPending}
                className="flex-1 py-2 px-4 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <XCircle size={16} />
                Dismiss
              </button>
              <button
                onClick={onClose}
                className="py-2 px-4 bg-dark-border hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
              >
                Close
              </button>
            </div>
          ) : (
            <button
              onClick={onClose}
              className="w-full py-2 px-4 bg-dark-border hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
