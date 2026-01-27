// Session 834: Advisors Panel for Workspace Command Tab
// Compact view of advisors with quick consultation

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Crown,
  MessageCircle,
  Star,
  TrendingUp,
  Briefcase,
  DollarSign,
  Zap,
  Target,
  Award,
  Rocket,
  Shield,
  Loader2,
  ExternalLink,
  Send,
  ChevronDown,
  ChevronRight,
  Users,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { advisorsApi } from '@/lib/api'

// Types
interface Advisor {
  id: string
  name: string
  title: string
  expertise: string
  category: string
  avatar_url?: string
  wisdom: string
  total_consultations: number
  influence_score: number
}

// Category configuration
const CATEGORY_CONFIG: Record<
  string,
  { icon: typeof Users; color: string; bgColor: string; label: string }
> = {
  finance: { icon: DollarSign, color: 'text-green-400', bgColor: 'bg-green-500/20', label: 'Finance' },
  investment: { icon: TrendingUp, color: 'text-blue-400', bgColor: 'bg-blue-500/20', label: 'Investment' },
  technology: { icon: Zap, color: 'text-purple-400', bgColor: 'bg-purple-500/20', label: 'Technology' },
  strategy: { icon: Target, color: 'text-orange-400', bgColor: 'bg-orange-500/20', label: 'Strategy' },
  leadership: { icon: Award, color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', label: 'Leadership' },
  innovation: { icon: Rocket, color: 'text-pink-400', bgColor: 'bg-pink-500/20', label: 'Innovation' },
  business: { icon: Briefcase, color: 'text-cyan-400', bgColor: 'bg-cyan-500/20', label: 'Business' },
  security: { icon: Shield, color: 'text-red-400', bgColor: 'bg-red-500/20', label: 'Security' },
}

const getCategoryConfig = (category: string) => {
  return CATEGORY_CONFIG[category?.toLowerCase()] || CATEGORY_CONFIG.business
}

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase()
}

export function AdvisorsPanel() {
  const [isExpanded, setIsExpanded] = useState(true)
  const [selectedAdvisor, setSelectedAdvisor] = useState<Advisor | null>(null)
  const [question, setQuestion] = useState('')
  const [showConsultForm, setShowConsultForm] = useState(false)
  const [lastResponse, setLastResponse] = useState<string | null>(null)

  // Fetch advisors
  const { data: advisorsData, isLoading } = useQuery({
    queryKey: ['advisors-list'],
    queryFn: async () => {
      const response = await advisorsApi.list()
      return response.data
    },
    staleTime: 60000,
  })

  // Consult mutation
  const consultMutation = useMutation({
    mutationFn: (data: { advisor_id: string; question: string }) => advisorsApi.consult(data),
    onSuccess: (response) => {
      setLastResponse(response.data?.response || 'Consultation complete')
      setQuestion('')
      setShowConsultForm(false)
    },
  })

  const advisors: Advisor[] = Array.isArray(advisorsData?.advisors) ? advisorsData.advisors : []

  // Stats
  const totalConsultations = advisors.reduce((sum, a) => sum + (a.total_consultations || 0), 0)
  const topAdvisors = [...advisors].sort((a, b) => b.total_consultations - a.total_consultations).slice(0, 5)

  const handleQuickConsult = (advisor: Advisor) => {
    setSelectedAdvisor(advisor)
    setShowConsultForm(true)
    setLastResponse(null)
  }

  const handleSubmitConsult = () => {
    if (!selectedAdvisor || !question.trim()) return
    consultMutation.mutate({
      advisor_id: selectedAdvisor.id,
      question: question.trim(),
    })
  }

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-dark-border/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-yellow-500/20">
            <Crown size={18} className="text-yellow-400" />
          </div>
          <div className="text-left">
            <h3 className="font-semibold text-sm">Advisors</h3>
            <p className="text-xs text-gray-400">
              {advisors.length} advisors • {totalConsultations} consultations
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <a
            href="/advisors"
            onClick={(e) => e.stopPropagation()}
            className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
          >
            Full View <ExternalLink size={12} />
          </a>
          {isExpanded ? (
            <ChevronDown size={18} className="text-gray-400" />
          ) : (
            <ChevronRight size={18} className="text-gray-400" />
          )}
        </div>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="border-t border-dark-border p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 size={24} className="animate-spin text-primary-400" />
            </div>
          ) : advisors.length === 0 ? (
            <div className="text-center py-6 text-gray-400">
              <Crown size={32} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">No advisors available</p>
            </div>
          ) : (
            <>
              {/* Quick Consult Form */}
              {showConsultForm && selectedAdvisor && (
                <div className="bg-dark-bg rounded-lg p-3 space-y-3 border border-primary-500/30">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Sparkles size={14} className="text-primary-400" />
                      <span className="text-sm font-medium">Consulting {selectedAdvisor.name}</span>
                    </div>
                    <button
                      onClick={() => {
                        setShowConsultForm(false)
                        setLastResponse(null)
                      }}
                      className="text-gray-400 hover:text-white text-xs"
                    >
                      Cancel
                    </button>
                  </div>

                  {lastResponse ? (
                    <div className="bg-primary-500/10 border border-primary-500/20 rounded p-3">
                      <p className="text-sm text-gray-200 whitespace-pre-wrap">{lastResponse}</p>
                    </div>
                  ) : (
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        placeholder="Ask a question..."
                        className="flex-1 px-3 py-2 bg-dark-card border border-dark-border rounded text-sm focus:border-primary-500 focus:outline-none"
                        onKeyDown={(e) => e.key === 'Enter' && handleSubmitConsult()}
                      />
                      <button
                        onClick={handleSubmitConsult}
                        disabled={!question.trim() || consultMutation.isPending}
                        className="px-3 py-2 bg-primary-600 hover:bg-primary-500 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm font-medium flex items-center gap-1"
                      >
                        {consultMutation.isPending ? (
                          <Loader2 size={14} className="animate-spin" />
                        ) : (
                          <Send size={14} />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Top Advisors List */}
              <div className="space-y-2">
                <div className="text-xs text-gray-400 uppercase tracking-wide">Top Advisors</div>
                {topAdvisors.map((advisor) => {
                  const config = getCategoryConfig(advisor.category)
                  const Icon = config.icon
                  return (
                    <div
                      key={advisor.id}
                      className="flex items-center gap-3 p-2 rounded-lg hover:bg-dark-border/30 transition-colors group"
                    >
                      {/* Avatar */}
                      <div
                        className={cn(
                          'w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold',
                          config.bgColor,
                          config.color
                        )}
                      >
                        {getInitials(advisor.name)}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm truncate">{advisor.name}</span>
                          <span
                            className={cn(
                              'px-1.5 py-0.5 rounded text-[10px] font-medium',
                              config.bgColor,
                              config.color
                            )}
                          >
                            {config.label}
                          </span>
                        </div>
                        <p className="text-xs text-gray-400 truncate">{advisor.title}</p>
                      </div>

                      {/* Stats & Actions */}
                      <div className="flex items-center gap-2">
                        <div className="text-right hidden sm:block">
                          <div className="flex items-center gap-1 text-xs text-gray-400">
                            <MessageCircle size={10} />
                            {advisor.total_consultations}
                          </div>
                          <div className="flex items-center gap-1 text-xs text-yellow-400">
                            <Star size={10} />
                            {advisor.influence_score}
                          </div>
                        </div>
                        <button
                          onClick={() => handleQuickConsult(advisor)}
                          className="p-1.5 rounded bg-primary-600/20 text-primary-400 hover:bg-primary-600/30 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Quick consult"
                        >
                          <MessageCircle size={14} />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* View All Link */}
              {advisors.length > 5 && (
                <a
                  href="/advisors"
                  className="block text-center text-xs text-primary-400 hover:text-primary-300 py-2"
                >
                  View all {advisors.length} advisors
                </a>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
