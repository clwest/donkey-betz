/**
 * Unified Conversations Page
 *
 * Session 717: Original conversation contract with quality metrics.
 * Session 782: Consolidated into unified view with all conversation types.
 * Session 826: Added goal-driven conversation creation form.
 *
 * Features:
 * - Merged view of HiveMind sessions + Legacy AgentConversations
 * - Type filter tabs (All / HiveMind / Legacy)
 * - Quality contract metrics and compliance rates
 * - Message-level analysis on expansion
 * - Goal-driven conversation creation with objectives and success criteria
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  AlertTriangle,
  CheckCircle2,
  Zap,
  Target,
  FileText,
  FileCheck,
  ChevronDown,
  ChevronUp,
  Info,
  TrendingUp,
  Users,
  Clock,
  Lightbulb,
  Wrench,
  ArrowRight,
  Loader2,
  MessageSquare,
  User,
  Plus,
  Brain,
  History,
  Play,
  Sparkles,
  X,
} from 'lucide-react'
import { conversationContractApi, conversationsApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// Session 782: Type filter for conversations
type ConversationTypeFilter = 'all' | 'hivemind' | 'legacy'

// Session 826: Conversation type options for goal-driven conversations
type ConversationType = 'analytical' | 'creative' | 'debate' | 'planning' | 'critique' | 'general'

const CONVERSATION_TYPES: { value: ConversationType; label: string; description: string }[] = [
  { value: 'analytical', label: 'Analytical', description: 'Rigorous analysis: Propose → Challenge → Synthesize → Decide' },
  { value: 'creative', label: 'Creative', description: 'Ideation: Brainstorm → Expand → Refine → Select' },
  { value: 'debate', label: 'Debate', description: 'Opposing viewpoints: Position → Counter → Rebut → Conclude' },
  { value: 'planning', label: 'Planning', description: 'Implementation: Goals → Steps → Dependencies → Schedule' },
  { value: 'critique', label: 'Critique', description: 'Stress-test: Present → Challenge → Defend → Improve' },
  { value: 'general', label: 'General', description: 'Open discussion: Explore → Discuss → Clarify → Summarize' },
]

// Types
interface ContractOverview {
  total_conversations: number
  avg_quality_score: number
  tension_compliance_rate: number
  grounding_compliance_rate: number
  summary_rate: number
  valid_summary_rate: number
  empty_agreement_count: number
}

interface ConversationContract {
  has_tension: boolean
  has_grounding: boolean
  has_empty_agreement: boolean
  has_summary: boolean
  summary_valid: boolean
  insights_count: number
  quality_score: number
}

interface DecisionSummary {
  insights: string[]
  proposed_feature: {
    name?: string
    inputs?: string
    outputs?: string
    integration?: string
  }
  next_steps: string[]
  raw_text?: string
}

interface Conversation {
  id: string
  topic: string
  type: 'hivemind' | 'legacy'
  status: string
  created_at: string
  participant_count: number
  contract: ConversationContract
  decision_summary: DecisionSummary | null
}

// Session 782: Types for detail endpoint
interface MessageAnalysis {
  has_tension: boolean
  has_grounding: boolean
  has_empty_agreement: boolean
  grounding_refs: string[]
}

interface ConversationMessage {
  sequence: number
  agent_name: string
  content: string
  analysis: MessageAnalysis
}

interface ContractAnalysis {
  tension_count: number
  tension_required: number
  tension_met: boolean
  grounding_count: number
  grounding_required: number
  grounding_met: boolean
  empty_agreement_count: number
  has_decision_summary: boolean
  summary_validation: {
    has_enough_insights: boolean
    has_feature_name: boolean
    has_enough_next_steps: boolean
    is_valid: boolean
  }
  is_contract_valid: boolean
}

interface ConversationDetail {
  conversation: {
    id: string
    topic: string
    type: 'hivemind' | 'legacy'
    status: string
    created_at: string
    participants: Array<{ id: string; name: string }>
  }
  contract_analysis: ContractAnalysis
  decision_summary: DecisionSummary | null
  messages: ConversationMessage[]
  message_count: number
}

interface ContractRequirements {
  tension: {
    description: string
    indicators: string[]
  }
  grounding: {
    description: string
    metrics: string[]
    systems: string[]
  }
  decision_summary: {
    description: string
    required_sections: string[]
  }
}

// Session 826: Goal-Driven Conversation Creation Form
function GoalDrivenConversationForm({
  onSuccess,
  onClose,
}: {
  onSuccess: () => void
  onClose: () => void
}) {
  const [topic, setTopic] = useState('')
  const [conversationType, setConversationType] = useState<ConversationType>('analytical')
  const [objective, setObjective] = useState('')
  const [criteriaInput, setCriteriaInput] = useState('')
  const [successCriteria, setSuccessCriteria] = useState<string[]>([])
  const [autoSelectAgents, setAutoSelectAgents] = useState(true)

  const createMutation = useMutation({
    mutationFn: () =>
      conversationsApi.create({
        topic,
        conversation_type: conversationType,
        objective: objective || undefined,
        success_criteria: successCriteria.length > 0 ? successCriteria : undefined,
        auto_select_agents: autoSelectAgents,
      }),
    onSuccess: () => {
      onSuccess()
      onClose()
    },
  })

  const addCriteria = () => {
    if (criteriaInput.trim()) {
      setSuccessCriteria([...successCriteria, criteriaInput.trim()])
      setCriteriaInput('')
    }
  }

  const removeCriteria = (index: number) => {
    setSuccessCriteria(successCriteria.filter((_, i) => i !== index))
  }

  return (
    <div className="rounded-lg border border-primary-500/30 bg-gradient-to-br from-primary-900/20 to-purple-900/20 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary-400" />
          Create Goal-Driven Conversation
        </h3>
        <button
          onClick={onClose}
          className="p-1 text-gray-400 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Topic */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Topic <span className="text-red-400">*</span>
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="What should the agents discuss?"
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Conversation Type */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Conversation Type
          </label>
          <select
            value={conversationType}
            onChange={(e) => setConversationType(e.target.value as ConversationType)}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {CONVERSATION_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label} - {type.description}
              </option>
            ))}
          </select>
        </div>

        {/* Objective */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Objective
            <span className="text-gray-500 font-normal ml-1">(What should be achieved?)</span>
          </label>
          <textarea
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            placeholder="e.g., Determine the best approach for implementing user authentication"
            rows={2}
            className="w-full px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
          />
        </div>

        {/* Success Criteria */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">
            Success Criteria
            <span className="text-gray-500 font-normal ml-1">(Measurable outcomes)</span>
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={criteriaInput}
              onChange={(e) => setCriteriaInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addCriteria())}
              placeholder="Add a success criterion..."
              className="flex-1 px-3 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={addCriteria}
              disabled={!criteriaInput.trim()}
              className="px-3 py-2 bg-primary-500/20 text-primary-300 rounded-lg hover:bg-primary-500/30 transition-colors disabled:opacity-50"
            >
              <Plus className="h-4 w-4" />
            </button>
          </div>
          {successCriteria.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {successCriteria.map((criteria, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-dark-bg border border-dark-border rounded text-sm text-gray-300"
                >
                  {criteria}
                  <button
                    onClick={() => removeCriteria(i)}
                    className="text-gray-500 hover:text-red-400"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Auto-select agents */}
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="autoSelectAgents"
            checked={autoSelectAgents}
            onChange={(e) => setAutoSelectAgents(e.target.checked)}
            className="rounded border-dark-border bg-dark-bg text-primary-500 focus:ring-primary-500"
          />
          <label htmlFor="autoSelectAgents" className="text-sm text-gray-300">
            Auto-select agents based on topic
            <span className="text-gray-500 ml-1">(recommended)</span>
          </label>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => createMutation.mutate()}
            disabled={!topic.trim() || createMutation.isPending}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50"
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Start Conversation
              </>
            )}
          </button>
        </div>

        {createMutation.isError && (
          <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 text-sm">
            Failed to create conversation: {(createMutation.error as Error)?.message || 'Unknown error'}
          </div>
        )}
      </div>
    </div>
  )
}

// Quality Score Badge
function QualityBadge({ score }: { score: number }) {
  let color = 'bg-red-500'
  let label = 'Poor'

  if (score >= 80) {
    color = 'bg-green-500'
    label = 'Excellent'
  } else if (score >= 60) {
    color = 'bg-blue-500'
    label = 'Good'
  } else if (score >= 40) {
    color = 'bg-yellow-500'
    label = 'Fair'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`h-2 w-16 rounded-full bg-dark-border`}>
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm text-gray-400">
        {score}% ({label})
      </span>
    </div>
  )
}

// Contract Requirement Card
function RequirementCard({
  title,
  description,
  icon: Icon,
  items,
  complianceRate,
}: {
  title: string
  description: string
  icon: React.ElementType
  items: string[]
  complianceRate: number
}) {
  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className="h-5 w-5 text-primary-400" />
          <h3 className="font-medium text-white">{title}</h3>
        </div>
        <span
          className={`text-sm font-medium ${
            complianceRate >= 70
              ? 'text-green-400'
              : complianceRate >= 40
                ? 'text-yellow-400'
                : 'text-red-400'
          }`}
        >
          {(complianceRate ?? 0).toFixed(0)}% compliant
        </span>
      </div>
      <p className="text-sm text-gray-400 mb-3">{description}</p>
      <div className="flex flex-wrap gap-1">
        {items.map((item, i) => (
          <span
            key={i}
            className="inline-block rounded bg-dark-bg px-2 py-0.5 text-xs text-gray-300"
          >
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}

// Conversation Row Component
// Session 782: Updated to show message-level analysis from detail endpoint
function ConversationRow({
  conversation,
  onSelect,
  isSelected,
  detail,
  isLoadingDetail,
}: {
  conversation: Conversation
  onSelect: () => void
  isSelected: boolean
  detail: ConversationDetail | null
  isLoadingDetail: boolean
}) {
  const { contract } = conversation

  return (
    <div
      className={`border-b border-dark-border p-4 cursor-pointer transition-colors ${
        isSelected ? 'bg-dark-bg' : 'hover:bg-dark-bg/50'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-white truncate">
              {conversation.topic}
            </span>
            <span
              className={`text-xs px-2 py-0.5 rounded ${
                conversation.type === 'hivemind'
                  ? 'bg-purple-500/20 text-purple-300'
                  : 'bg-gray-500/20 text-gray-300'
              }`}
            >
              {conversation.type}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-400">
            <span className="flex items-center gap-1">
              <Users className="h-3 w-3" />
              {conversation.participant_count} agents
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(conversation.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Contract indicators */}
          <div className="flex items-center gap-2">
            <div
              className={`p-1 rounded ${contract.has_tension ? 'bg-green-500/20' : 'bg-red-500/20'}`}
              title={`Tension: ${contract.has_tension ? 'Yes' : 'No'}`}
            >
              <Zap
                className={`h-4 w-4 ${contract.has_tension ? 'text-green-400' : 'text-red-400'}`}
              />
            </div>
            <div
              className={`p-1 rounded ${contract.has_grounding ? 'bg-green-500/20' : 'bg-red-500/20'}`}
              title={`Grounding: ${contract.has_grounding ? 'Yes' : 'No'}`}
            >
              <Target
                className={`h-4 w-4 ${contract.has_grounding ? 'text-green-400' : 'text-red-400'}`}
              />
            </div>
            <div
              className={`p-1 rounded ${contract.summary_valid ? 'bg-green-500/20' : contract.has_summary ? 'bg-yellow-500/20' : 'bg-red-500/20'}`}
              title={`Summary: ${contract.summary_valid ? 'Valid' : contract.has_summary ? 'Partial' : 'None'}`}
            >
              <FileText
                className={`h-4 w-4 ${contract.summary_valid ? 'text-green-400' : contract.has_summary ? 'text-yellow-400' : 'text-red-400'}`}
              />
            </div>
          </div>

          <QualityBadge score={contract.quality_score} />

          {isSelected ? (
            <ChevronUp className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          )}
        </div>
      </div>

      {/* Session 782: Expanded details with message-level analysis */}
      {isSelected && (
        <div className="mt-4 pt-4 border-t border-dark-border" onClick={(e) => e.stopPropagation()}>
          <MessageAnalysisView detail={detail} isLoading={isLoadingDetail} />
        </div>
      )}
    </div>
  )
}

// Decision Summary View
function DecisionSummaryView({ summary }: { summary: DecisionSummary }) {
  return (
    <div className="space-y-4">
      {/* Insights */}
      {summary.insights && summary.insights.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-sm font-medium text-white mb-2">
            <Lightbulb className="h-4 w-4 text-yellow-400" />
            Insights ({summary.insights.length})
          </h4>
          <ul className="space-y-1">
            {summary.insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-primary-400">{i + 1}.</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Proposed Feature */}
      {summary.proposed_feature && summary.proposed_feature.name && (
        <div>
          <h4 className="flex items-center gap-2 text-sm font-medium text-white mb-2">
            <Wrench className="h-4 w-4 text-blue-400" />
            Proposed Feature
          </h4>
          <div className="rounded bg-dark-bg p-3 space-y-2">
            <div className="text-white font-medium">{summary.proposed_feature.name}</div>
            {summary.proposed_feature.inputs && (
              <div className="text-sm">
                <span className="text-gray-400">Inputs:</span>{' '}
                <span className="text-gray-300">{summary.proposed_feature.inputs}</span>
              </div>
            )}
            {summary.proposed_feature.outputs && (
              <div className="text-sm">
                <span className="text-gray-400">Outputs:</span>{' '}
                <span className="text-gray-300">{summary.proposed_feature.outputs}</span>
              </div>
            )}
            {summary.proposed_feature.integration && (
              <div className="text-sm">
                <span className="text-gray-400">Integration:</span>{' '}
                <span className="text-gray-300">{summary.proposed_feature.integration}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Next Steps */}
      {summary.next_steps && summary.next_steps.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-sm font-medium text-white mb-2">
            <ArrowRight className="h-4 w-4 text-green-400" />
            Next Steps ({summary.next_steps.length})
          </h4>
          <ul className="space-y-1">
            {summary.next_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                <span className="text-green-400">{i + 1}.</span>
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// Session 782: Message Analysis View - shows message-by-message breakdown
function MessageAnalysisView({
  detail,
  isLoading
}: {
  detail: ConversationDetail | null
  isLoading: boolean
}) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin text-primary-400" />
        <span className="ml-2 text-gray-400">Loading message analysis...</span>
      </div>
    )
  }

  if (!detail) {
    return (
      <div className="text-center py-4 text-gray-400">
        Failed to load conversation details
      </div>
    )
  }

  const { contract_analysis, messages, decision_summary } = detail

  return (
    <div className="space-y-4">
      {/* Contract Analysis Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className={`rounded-lg p-3 ${contract_analysis.tension_met ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Zap className={`h-4 w-4 ${contract_analysis.tension_met ? 'text-green-400' : 'text-red-400'}`} />
            <span className="text-sm font-medium text-white">Tension</span>
          </div>
          <div className="text-xs text-gray-400">
            {contract_analysis.tension_count}/{contract_analysis.tension_required} required
          </div>
        </div>
        <div className={`rounded-lg p-3 ${contract_analysis.grounding_met ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
          <div className="flex items-center gap-2 mb-1">
            <Target className={`h-4 w-4 ${contract_analysis.grounding_met ? 'text-green-400' : 'text-red-400'}`} />
            <span className="text-sm font-medium text-white">Grounding</span>
          </div>
          <div className="text-xs text-gray-400">
            {contract_analysis.grounding_count}/{contract_analysis.grounding_required} required
          </div>
        </div>
        <div className={`rounded-lg p-3 ${contract_analysis.empty_agreement_count === 0 ? 'bg-green-500/10 border border-green-500/30' : 'bg-yellow-500/10 border border-yellow-500/30'}`}>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className={`h-4 w-4 ${contract_analysis.empty_agreement_count === 0 ? 'text-green-400' : 'text-yellow-400'}`} />
            <span className="text-sm font-medium text-white">Empty Agreement</span>
          </div>
          <div className="text-xs text-gray-400">
            {contract_analysis.empty_agreement_count} instances
          </div>
        </div>
        <div className={`rounded-lg p-3 ${contract_analysis.summary_validation?.is_valid ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
          <div className="flex items-center gap-2 mb-1">
            <FileText className={`h-4 w-4 ${contract_analysis.summary_validation?.is_valid ? 'text-green-400' : 'text-red-400'}`} />
            <span className="text-sm font-medium text-white">Summary</span>
          </div>
          <div className="text-xs text-gray-400">
            {contract_analysis.has_decision_summary ? (contract_analysis.summary_validation?.is_valid ? 'Valid' : 'Incomplete') : 'Missing'}
          </div>
        </div>
      </div>

      {/* Participants */}
      {detail.conversation.participants && detail.conversation.participants.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-sm font-medium text-white mb-2">
            <Users className="h-4 w-4 text-primary-400" />
            Participants ({detail.conversation.participants.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {detail.conversation.participants.map((p, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded bg-dark-bg px-2 py-1 text-xs text-gray-300"
              >
                <User className="h-3 w-3" />
                {p.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Message-by-Message Analysis */}
      {messages && messages.length > 0 && (
        <div>
          <h4 className="flex items-center gap-2 text-sm font-medium text-white mb-3">
            <MessageSquare className="h-4 w-4 text-primary-400" />
            Message Analysis ({messages.length} messages)
          </h4>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
            {messages.map((msg, i) => (
              <div
                key={i}
                className="rounded-lg bg-dark-bg p-3 border border-dark-border"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">#{msg.sequence}</span>
                    <span className="font-medium text-primary-300">{msg.agent_name}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    {msg.analysis.has_tension && (
                      <span className="px-1.5 py-0.5 rounded text-xs bg-purple-500/20 text-purple-300" title="Has tension">
                        <Zap className="h-3 w-3 inline" /> Tension
                      </span>
                    )}
                    {msg.analysis.has_grounding && (
                      <span className="px-1.5 py-0.5 rounded text-xs bg-blue-500/20 text-blue-300" title="Has grounding">
                        <Target className="h-3 w-3 inline" /> Grounded
                      </span>
                    )}
                    {msg.analysis.has_empty_agreement && (
                      <span className="px-1.5 py-0.5 rounded text-xs bg-yellow-500/20 text-yellow-300" title="Empty agreement">
                        <AlertTriangle className="h-3 w-3 inline" /> Empty
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-gray-300 line-clamp-3">{msg.content}</p>
                {msg.analysis.grounding_refs && msg.analysis.grounding_refs.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {msg.analysis.grounding_refs.map((ref, j) => (
                      <span
                        key={j}
                        className="inline-block rounded bg-blue-500/10 px-1.5 py-0.5 text-xs text-blue-300"
                      >
                        {ref}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decision Summary */}
      {decision_summary && (
        <div className="border-t border-dark-border pt-4">
          <DecisionSummaryView summary={decision_summary} />
        </div>
      )}
    </div>
  )
}

// Session 782: Type Filter Tabs Component
function TypeFilterTabs({
  filter,
  onChange,
  counts,
}: {
  filter: ConversationTypeFilter
  onChange: (filter: ConversationTypeFilter) => void
  counts: { all: number; hivemind: number; legacy: number }
}) {
  const tabs: { key: ConversationTypeFilter; label: string; icon: React.ElementType }[] = [
    { key: 'all', label: 'All', icon: MessageSquare },
    { key: 'hivemind', label: 'Hive Mind', icon: Brain },
    { key: 'legacy', label: 'Legacy', icon: History },
  ]

  return (
    <div className="flex gap-1 p-1 bg-dark-bg rounded-lg">
      {tabs.map(({ key, label, icon: Icon }) => (
        <button
          key={key}
          onClick={() => onChange(key)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            filter === key
              ? 'bg-primary-500/20 text-primary-300'
              : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
          }`}
        >
          <Icon className="h-4 w-4" />
          {label}
          <span className={`text-xs px-1.5 py-0.5 rounded ${
            filter === key ? 'bg-primary-500/30' : 'bg-dark-border'
          }`}>
            {counts[key]}
          </span>
        </button>
      ))}
    </div>
  )
}

// Main Page Component
export default function ConversationContractPage() {
  const queryClient = useQueryClient()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [days, setDays] = useState(30)
  const [typeFilter, setTypeFilter] = useState<ConversationTypeFilter>('all')
  const [showCreateForm, setShowCreateForm] = useState(false)

  // Overview query
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['conversation-contract', days],
    queryFn: async () => {
      const response = await conversationContractApi.overview(days)
      return response.data
    },
    staleTime: 30000,
  })

  // Session 782: Detail query - fetches message-level analysis when conversation is selected
  const { data: detailData, isLoading: isLoadingDetail } = useQuery({
    queryKey: ['conversation-contract-detail', selectedId],
    queryFn: async () => {
      if (!selectedId) return null
      const response = await conversationContractApi.detail(selectedId)
      return response.data as ConversationDetail
    },
    enabled: !!selectedId, // Only fetch when a conversation is selected
    staleTime: 60000, // Cache for 1 minute
  })

  const overview: ContractOverview | undefined = data?.overview
  const requirements: ContractRequirements | undefined = data?.contract_requirements
  const allConversations: Conversation[] = data?.conversations || []

  // Session 782: Filter conversations by type and compute counts
  const typeCounts = {
    all: allConversations.length,
    hivemind: allConversations.filter(c => c.type === 'hivemind').length,
    legacy: allConversations.filter(c => c.type === 'legacy').length,
  }

  const conversations = typeFilter === 'all'
    ? allConversations
    : allConversations.filter(c => c.type === typeFilter)

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading contract analytics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-red-400">Error loading contract analytics</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <Breadcrumb currentPage="Conversations" />

      {/* Header - Session 782: Updated for unified view */}
      {/* Session 826: Added goal-driven conversation creation */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Agent Conversations</h1>
          <p className="text-gray-400 mt-1">
            Goal-driven agent conversations with quality analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="rounded-lg border border-dark-border bg-dark-card px-3 py-2 text-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="flex items-center gap-2 rounded-lg bg-primary-500 px-4 py-2 text-white hover:bg-primary-600 transition-colors"
          >
            {showCreateForm ? (
              <>
                <X className="h-4 w-4" />
                Cancel
              </>
            ) : (
              <>
                <Plus className="h-4 w-4" />
                New Conversation
              </>
            )}
          </button>
        </div>
      </div>

      {/* Session 826: Goal-Driven Conversation Creation Form */}
      {showCreateForm && (
        <GoalDrivenConversationForm
          onSuccess={() => {
            refetch()
            queryClient.invalidateQueries({ queryKey: ['conversation-contract'] })
          }}
          onClose={() => setShowCreateForm(false)}
        />
      )}

      {/* Session 782: Type Filter Tabs */}
      <TypeFilterTabs
        filter={typeFilter}
        onChange={setTypeFilter}
        counts={typeCounts}
      />

      {/* Overview Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="text-2xl font-bold text-white">
              {overview.total_conversations}
            </div>
            <div className="text-sm text-gray-400">Total Conversations</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2">
              <TrendingUp
                className={`h-5 w-5 ${
                  overview.avg_quality_score >= 70
                    ? 'text-green-400'
                    : overview.avg_quality_score >= 40
                      ? 'text-yellow-400'
                      : 'text-red-400'
                }`}
              />
              <span className="text-2xl font-bold text-white">
                {(overview.avg_quality_score ?? 0).toFixed(0)}%
              </span>
            </div>
            <div className="text-sm text-gray-400">Average Quality</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="text-2xl font-bold text-white">
              {(overview.valid_summary_rate ?? 0).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-400">Valid Summaries</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="flex items-center gap-2">
              {overview.empty_agreement_count > 0 ? (
                <AlertTriangle className="h-5 w-5 text-yellow-400" />
              ) : (
                <CheckCircle2 className="h-5 w-5 text-green-400" />
              )}
              <span className="text-2xl font-bold text-white">
                {overview.empty_agreement_count}
              </span>
            </div>
            <div className="text-sm text-gray-400">Empty Agreements</div>
          </div>
        </div>
      )}

      {/* Contract Requirements */}
      {requirements && overview && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <FileCheck className="h-5 w-5 text-primary-400" />
            Contract Requirements
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            <RequirementCard
              title="Tension"
              description={requirements.tension.description}
              icon={Zap}
              items={requirements.tension.indicators}
              complianceRate={overview.tension_compliance_rate}
            />
            <RequirementCard
              title="Grounding"
              description={requirements.grounding.description}
              icon={Target}
              items={[...requirements.grounding.metrics, ...requirements.grounding.systems]}
              complianceRate={overview.grounding_compliance_rate}
            />
            <RequirementCard
              title="Decision Summary"
              description={requirements.decision_summary.description}
              icon={FileText}
              items={requirements.decision_summary.required_sections}
              complianceRate={overview.summary_rate}
            />
          </div>
        </div>
      )}

      {/* Conversations List */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5 text-primary-400" />
          {typeFilter === 'all' ? 'All Conversations' : typeFilter === 'hivemind' ? 'Hive Mind Sessions' : 'Legacy Conversations'}
          <span className="text-gray-400 font-normal">({conversations.length})</span>
        </h2>

        {conversations.length === 0 ? (
          <div className="rounded-lg border border-dark-border bg-dark-card p-8 text-center">
            <Info className="h-12 w-12 text-gray-500 mx-auto mb-4" />
            <p className="text-gray-400">No conversations found in this period</p>
          </div>
        ) : (
          <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
            {conversations.map((conv) => (
              <ConversationRow
                key={conv.id}
                conversation={conv}
                onSelect={() =>
                  setSelectedId(selectedId === conv.id ? null : conv.id)
                }
                isSelected={selectedId === conv.id}
                detail={selectedId === conv.id ? detailData ?? null : null}
                isLoadingDetail={selectedId === conv.id && isLoadingDetail}
              />
            ))}
          </div>
        )}
      </div>

      {/* Contract Info */}
      <div className="rounded-lg border border-dark-border bg-dark-card p-4">
        <h3 className="flex items-center gap-2 text-white font-medium mb-3">
          <Info className="h-5 w-5 text-primary-400" />
          About the Conversation Contract
        </h3>
        <div className="text-sm text-gray-400 space-y-2">
          <p>
            The Conversation Contract ensures agent-to-agent conversations are productive
            and generate actionable insights. Every conversation is evaluated on three criteria:
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>
              <strong className="text-gray-300">Tension</strong> - At least 2 instances of
              constructive disagreement to avoid echo chambers
            </li>
            <li>
              <strong className="text-gray-300">Grounding</strong> - At least 2 references to
              real platform metrics or systems
            </li>
            <li>
              <strong className="text-gray-300">Decision Summary</strong> - Structured output
              with 3+ insights, a proposed feature, and 2+ next steps
            </li>
          </ul>
          <p>
            Quality scores range from 0-100%, with points awarded for each requirement met
            and penalties for empty agreement ("Absolutely!", "Great point!", etc.).
          </p>
        </div>
      </div>
    </div>
  )
}
