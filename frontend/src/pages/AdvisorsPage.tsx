import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { advisorsApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'
import {
  Users,
  MessageCircle,
  Star,
  Award,
  TrendingUp,
  Briefcase,
  Lightbulb,
  Send,
  RefreshCw,
  ChevronRight,
  Sparkles,
  Target,
  DollarSign,
  Rocket,
  Shield,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'

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

interface ConsultationResponse {
  success: boolean
  advisor_name: string
  question: string
  response: string
  consultation_id?: string
}

// Category configuration
const CATEGORY_CONFIG: Record<string, { icon: typeof Users; color: string; bgColor: string; label: string }> = {
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

// Get initials for avatar fallback
const getInitials = (name: string) => {
  return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
}

export default function AdvisorsPage() {
  const [selectedAdvisor, setSelectedAdvisor] = useState<Advisor | null>(null)
  const [question, setQuestion] = useState('')
  const [context, setContext] = useState('')
  const [lastResponse, setLastResponse] = useState<ConsultationResponse | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null)

  // Fetch advisors
  const { data: advisorsData, isLoading, refetch } = useQuery({
    queryKey: ['advisors-list'],
    queryFn: async () => {
      const response = await advisorsApi.list()
      return response.data
    },
    staleTime: 60000,
  })

  // Consult mutation
  const consultMutation = useMutation({
    mutationFn: (data: { advisor_id: string; question: string; context?: string }) =>
      advisorsApi.consult(data),
    onSuccess: (response) => {
      setLastResponse(response.data)
      setQuestion('')
      setContext('')
    },
  })

  // Parse data
  const advisors: Advisor[] = Array.isArray(advisorsData?.advisors) ? advisorsData.advisors : []

  // Get unique categories
  const categories = [...new Set(advisors.map(a => a.category))].filter(Boolean)

  // Filter advisors
  const filteredAdvisors = categoryFilter
    ? advisors.filter(a => a.category?.toLowerCase() === categoryFilter.toLowerCase())
    : advisors

  // Stats
  const totalAdvisors = advisors.length
  const totalConsultations = advisors.reduce((sum, a) => sum + (a.total_consultations || 0), 0)
  const avgInfluence = advisors.length > 0
    ? Math.round(advisors.reduce((sum, a) => sum + (a.influence_score || 0), 0) / advisors.length)
    : 0

  const handleConsult = () => {
    if (!selectedAdvisor || !question.trim()) return

    consultMutation.mutate({
      advisor_id: selectedAdvisor.id,
      question: question.trim(),
      context: context.trim() || undefined,
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Breadcrumb currentPage="Advisors Council" />
          <p className="text-sm text-gray-400 mt-1">
            Consult with legendary figures for wisdom and guidance
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border rounded-lg text-gray-300 hover:text-white hover:bg-dark-bg transition-colors"
        >
          <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Users className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalAdvisors}</p>
              <p className="text-xs text-gray-400">Total Advisors</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <MessageCircle className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{totalConsultations}</p>
              <p className="text-xs text-gray-400">Total Consultations</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Star className="w-5 h-5 text-yellow-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{avgInfluence}%</p>
              <p className="text-xs text-gray-400">Avg Influence</p>
            </div>
          </div>
        </div>

        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <Award className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{categories.length}</p>
              <p className="text-xs text-gray-400">Categories</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Panel - Advisors List */}
        <div className="col-span-2 space-y-4">
          {/* Category Filter */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => setCategoryFilter(null)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm transition-colors',
                !categoryFilter
                  ? 'bg-purple-600 text-white'
                  : 'bg-dark-card text-gray-400 hover:text-white'
              )}
            >
              All
            </button>
            {categories.map((cat) => {
              const config = getCategoryConfig(cat)
              return (
                <button
                  key={cat}
                  onClick={() => setCategoryFilter(cat)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-colors flex items-center gap-1',
                    categoryFilter === cat
                      ? `${config.bgColor} ${config.color}`
                      : 'bg-dark-card text-gray-400 hover:text-white'
                  )}
                >
                  <config.icon size={14} />
                  {config.label}
                </button>
              )
            })}
          </div>

          {/* Advisors Grid */}
          <div className="grid grid-cols-2 gap-4">
            {isLoading ? (
              <div className="col-span-2 bg-dark-card rounded-lg border border-dark-border p-8 text-center text-gray-400">
                Loading advisors...
              </div>
            ) : filteredAdvisors.length === 0 ? (
              <div className="col-span-2 bg-dark-card rounded-lg border border-dark-border p-8 text-center text-gray-400">
                <Users size={48} className="mx-auto mb-4 opacity-50" />
                <p>No advisors found</p>
              </div>
            ) : (
              filteredAdvisors.map((advisor) => {
                const config = getCategoryConfig(advisor.category)
                const Icon = config.icon

                return (
                  <button
                    key={advisor.id}
                    onClick={() => {
                      setSelectedAdvisor(advisor)
                      setLastResponse(null)
                    }}
                    className={cn(
                      'bg-dark-card rounded-lg border border-dark-border p-4 hover:bg-dark-bg transition-colors text-left',
                      selectedAdvisor?.id === advisor.id && 'ring-2 ring-purple-500'
                    )}
                  >
                    <div className="flex items-start gap-4">
                      {/* Avatar */}
                      <div className={cn(
                        'w-14 h-14 rounded-full flex items-center justify-center text-lg font-bold',
                        config.bgColor, config.color
                      )}>
                        {advisor.avatar_url ? (
                          <img
                            src={advisor.avatar_url}
                            alt={advisor.name}
                            className="w-full h-full rounded-full object-cover"
                          />
                        ) : (
                          getInitials(advisor.name)
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-white truncate">{advisor.name}</h3>
                        <p className="text-xs text-gray-400 truncate">{advisor.title}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={cn('text-xs px-2 py-0.5 rounded', config.bgColor, config.color)}>
                            <Icon size={10} className="inline mr-1" />
                            {config.label}
                          </span>
                          <span className="text-xs text-gray-500">
                            {advisor.total_consultations} consults
                          </span>
                        </div>
                      </div>

                      <ChevronRight size={16} className="text-gray-500" />
                    </div>

                    <p className="text-sm text-gray-400 mt-3 line-clamp-2">
                      {advisor.expertise}
                    </p>
                  </button>
                )
              })
            )}
          </div>
        </div>

        {/* Right Panel - Consultation */}
        <div className="space-y-4">
          {selectedAdvisor ? (
            <>
              {/* Selected Advisor */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-6">
                <div className="text-center">
                  {(() => {
                    const config = getCategoryConfig(selectedAdvisor.category)
                    return (
                      <div className={cn(
                        'inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 text-2xl font-bold',
                        config.bgColor, config.color
                      )}>
                        {selectedAdvisor.avatar_url ? (
                          <img
                            src={selectedAdvisor.avatar_url}
                            alt={selectedAdvisor.name}
                            className="w-full h-full rounded-full object-cover"
                          />
                        ) : (
                          getInitials(selectedAdvisor.name)
                        )}
                      </div>
                    )
                  })()}

                  <h3 className="text-lg font-medium text-white">{selectedAdvisor.name}</h3>
                  <p className="text-sm text-gray-400">{selectedAdvisor.title}</p>

                  <div className="flex items-center justify-center gap-3 mt-3">
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <MessageCircle size={12} />
                      {selectedAdvisor.total_consultations} consultations
                    </span>
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      <Star size={12} />
                      {selectedAdvisor.influence_score}% influence
                    </span>
                  </div>
                </div>

                {/* Expertise */}
                <div className="mt-4 p-3 bg-dark-bg rounded-lg">
                  <h4 className="text-xs text-gray-500 mb-1">Expertise</h4>
                  <p className="text-sm text-gray-300">{selectedAdvisor.expertise}</p>
                </div>

                {/* Wisdom */}
                {selectedAdvisor.wisdom && (
                  <div className="mt-3 p-3 bg-dark-bg rounded-lg">
                    <h4 className="text-xs text-gray-500 mb-1 flex items-center gap-1">
                      <Lightbulb size={12} className="text-yellow-400" />
                      Wisdom
                    </h4>
                    <p className="text-sm text-gray-300 italic">"{selectedAdvisor.wisdom}"</p>
                  </div>
                )}
              </div>

              {/* Consultation Form */}
              <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                  <Sparkles size={16} className="text-purple-400" />
                  Ask {selectedAdvisor.name.split(' ')[0]}
                </h4>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Your Question</label>
                    <textarea
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="What would you like to ask?"
                      className="w-full p-3 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="text-xs text-gray-400 mb-1 block">Context (optional)</label>
                    <input
                      type="text"
                      value={context}
                      onChange={(e) => setContext(e.target.value)}
                      placeholder="Any relevant context..."
                      className="w-full p-2 bg-dark-bg border border-dark-border rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500"
                    />
                  </div>

                  <button
                    onClick={handleConsult}
                    disabled={!question.trim() || consultMutation.isPending}
                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {consultMutation.isPending ? (
                      <>
                        <RefreshCw size={16} className="animate-spin" />
                        Consulting...
                      </>
                    ) : (
                      <>
                        <Send size={16} />
                        Consult
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Response */}
              {lastResponse && (
                <div className="bg-dark-card rounded-lg border border-dark-border p-4">
                  <h4 className="font-medium text-white mb-3 flex items-center gap-2">
                    <MessageCircle size={16} className="text-blue-400" />
                    Response from {lastResponse.advisor_name}
                  </h4>
                  <div className="p-3 bg-dark-bg rounded-lg">
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">{lastResponse.response}</p>
                  </div>
                </div>
              )}

              {/* Error */}
              {consultMutation.isError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                  <p className="text-sm text-red-400">Failed to get consultation. Please try again.</p>
                </div>
              )}
            </>
          ) : (
            <div className="bg-dark-card rounded-lg border border-dark-border p-8 text-center">
              <Users size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select an advisor to consult</p>
              <p className="text-xs text-gray-500 mt-2">
                Choose from legendary figures across finance, technology, and leadership
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
