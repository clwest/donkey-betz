// Session 834: Dream Detail Modal
// View full dream details without leaving Workspace
// Session 926: Added ListenButton for TTS

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  X,
  Sparkles,
  Clock,
  Star,
  ThumbsUp,
  ThumbsDown,
  Lightbulb,
  AlertCircle,
  Loader2,
  Hash,
  User,
  Brain,
  Zap,
  Heart,
  Flame,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { dreamsApi } from '@/lib/api'
import { ListenButton } from '@/components/ListenButton'

interface DreamDetailModalProps {
  dreamId: string
  onClose: () => void
}

interface Dream {
  id: string
  agent_name: string
  agent_emoji?: string
  dream_type: string
  content: string
  interpretation?: string
  creativity_score?: number
  novelty_score?: number
  coherence_score?: number
  emotional_valence?: number
  key_symbols?: string[]
  potential_insights?: string[]
  reactions?: Record<string, number>
  rating?: number
  created_at: string
  shown_to_user?: boolean
}

const REACTIONS = [
  { emoji: '💡', label: 'Insightful', key: 'insightful' },
  { emoji: '🔥', label: 'Inspiring', key: 'inspiring' },
  { emoji: '🤔', label: 'Thought-provoking', key: 'thought_provoking' },
  { emoji: '❤️', label: 'Love it', key: 'love' },
  { emoji: '😮', label: 'Surprising', key: 'surprising' },
]

export function DreamDetailModal({ dreamId, onClose }: DreamDetailModalProps) {
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['dream-detail', dreamId],
    queryFn: async () => {
      const response = await dreamsApi.detail(dreamId)
      return response.data as { dream: Dream }
    },
  })

  const reactMutation = useMutation({
    mutationFn: (reaction: string) => dreamsApi.react(dreamId, reaction),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dream-detail', dreamId] })
      queryClient.invalidateQueries({ queryKey: ['dreams-panel'] })
    },
  })

  const rateMutation = useMutation({
    mutationFn: (rating: number) => dreamsApi.rate(dreamId, rating),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dream-detail', dreamId] })
      queryClient.invalidateQueries({ queryKey: ['dreams-panel'] })
    },
  })

  const dream = data?.dream

  const getDreamTypeIcon = (type: string) => {
    switch (type?.toLowerCase()) {
      case 'creative':
        return <Sparkles size={16} className="text-purple-400" />
      case 'analytical':
        return <Brain size={16} className="text-blue-400" />
      case 'predictive':
        return <Zap size={16} className="text-yellow-400" />
      case 'emotional':
        return <Heart size={16} className="text-pink-400" />
      default:
        return <Lightbulb size={16} className="text-primary-400" />
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400'
    if (score >= 0.6) return 'text-yellow-400'
    if (score >= 0.4) return 'text-orange-400'
    return 'text-red-400'
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border bg-gradient-to-r from-purple-500/10 to-pink-500/10">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-500/20">
              <Sparkles size={20} className="text-purple-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Dream Details</h2>
              <p className="text-xs text-gray-400">Agent dream exploration</p>
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
              <AlertCircle size={48} className="text-red-400 mb-4" />
              <p className="text-gray-400">Failed to load dream</p>
            </div>
          ) : dream ? (
            <>
              {/* Agent & Type */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{dream.agent_emoji || '🤖'}</span>
                    <div>
                      <h3 className="font-medium text-white">{dream.agent_name}</h3>
                      <div className="flex items-center gap-2 text-xs text-gray-400">
                        {getDreamTypeIcon(dream.dream_type)}
                        <span className="capitalize">{dream.dream_type} Dream</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock size={12} />
                    {new Date(dream.created_at).toLocaleString()}
                  </div>
                </div>
              </div>

              {/* Dream Content */}
              <div className="bg-dark-bg rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase flex items-center gap-2">
                    <Sparkles size={12} />
                    Dream Content
                  </h4>
                  {dream.content && (
                    <ListenButton
                      text={dream.content}
                      agentName={dream.agent_name}
                      size="sm"
                      className="opacity-60 hover:opacity-100"
                    />
                  )}
                </div>
                <p className="text-sm text-gray-200 whitespace-pre-wrap leading-relaxed">
                  {dream.content}
                </p>
              </div>

              {/* Interpretation */}
              {dream.interpretation && (
                <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-purple-400 uppercase mb-2 flex items-center gap-2">
                    <Lightbulb size={12} />
                    Interpretation
                  </h4>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">
                    {dream.interpretation}
                  </p>
                </div>
              )}

              {/* Scores */}
              {(dream.creativity_score || dream.novelty_score || dream.coherence_score) && (
                <div className="bg-dark-bg rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">Scores</h4>
                  <div className="grid grid-cols-3 gap-4">
                    {dream.creativity_score !== undefined && (
                      <div className="text-center">
                        <div className={cn('text-2xl font-bold', getScoreColor(dream.creativity_score))}>
                          {Math.round(dream.creativity_score * 100)}%
                        </div>
                        <div className="text-xs text-gray-400">Creativity</div>
                      </div>
                    )}
                    {dream.novelty_score !== undefined && (
                      <div className="text-center">
                        <div className={cn('text-2xl font-bold', getScoreColor(dream.novelty_score))}>
                          {Math.round(dream.novelty_score * 100)}%
                        </div>
                        <div className="text-xs text-gray-400">Novelty</div>
                      </div>
                    )}
                    {dream.coherence_score !== undefined && (
                      <div className="text-center">
                        <div className={cn('text-2xl font-bold', getScoreColor(dream.coherence_score))}>
                          {Math.round(dream.coherence_score * 100)}%
                        </div>
                        <div className="text-xs text-gray-400">Coherence</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Key Symbols */}
              {dream.key_symbols && dream.key_symbols.length > 0 && (
                <div className="bg-dark-bg rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2">Key Symbols</h4>
                  <div className="flex flex-wrap gap-2">
                    {dream.key_symbols.map((symbol, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-primary-600/20 text-primary-400 rounded text-xs"
                      >
                        {symbol}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Potential Insights */}
              {dream.potential_insights && dream.potential_insights.length > 0 && (
                <div className="bg-dark-bg rounded-lg p-4">
                  <h4 className="text-xs font-semibold text-gray-400 uppercase mb-2 flex items-center gap-2">
                    <Lightbulb size={12} />
                    Potential Insights
                  </h4>
                  <ul className="space-y-1">
                    {dream.potential_insights.map((insight, idx) => (
                      <li key={idx} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-yellow-400 mt-1">•</span>
                        {insight}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Rating */}
              <div className="bg-dark-bg rounded-lg p-4">
                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">Rate this Dream</h4>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => rateMutation.mutate(star)}
                      disabled={rateMutation.isPending}
                      className={cn(
                        'p-1 transition-colors',
                        dream.rating && star <= dream.rating
                          ? 'text-yellow-400'
                          : 'text-gray-600 hover:text-yellow-400'
                      )}
                    >
                      <Star size={24} fill={dream.rating && star <= dream.rating ? 'currentColor' : 'none'} />
                    </button>
                  ))}
                  {dream.rating && (
                    <span className="ml-2 text-sm text-gray-400">{dream.rating}/5</span>
                  )}
                </div>
              </div>

              {/* Reactions */}
              <div className="bg-dark-bg rounded-lg p-4">
                <h4 className="text-xs font-semibold text-gray-400 uppercase mb-3">React</h4>
                <div className="flex flex-wrap gap-2">
                  {REACTIONS.map((reaction) => {
                    const count = dream.reactions?.[reaction.key] || 0
                    return (
                      <button
                        key={reaction.key}
                        onClick={() => reactMutation.mutate(reaction.key)}
                        disabled={reactMutation.isPending}
                        className={cn(
                          'px-3 py-2 rounded-lg border transition-all flex items-center gap-2',
                          count > 0
                            ? 'bg-primary-600/20 border-primary-500/30 text-white'
                            : 'bg-dark-card border-dark-border text-gray-400 hover:border-primary-500/50 hover:text-white'
                        )}
                      >
                        <span>{reaction.emoji}</span>
                        <span className="text-xs">{reaction.label}</span>
                        {count > 0 && (
                          <span className="text-xs bg-primary-600/30 px-1.5 py-0.5 rounded">
                            {count}
                          </span>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Metadata */}
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-2">
                <span className="flex items-center gap-1">
                  <Hash size={12} />
                  {dream.id.slice(0, 8)}
                </span>
              </div>
            </>
          ) : (
            <p className="text-gray-400 text-center py-8">Dream not found</p>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border bg-dark-bg/50">
          <button
            onClick={onClose}
            className="w-full py-2 px-4 bg-dark-border hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
