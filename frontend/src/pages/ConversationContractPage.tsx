/**
 * Conversation Contract Page
 *
 * Session 717: Visualizes conversation quality metrics and contract compliance.
 *
 * The Conversation Contract ensures agent conversations have:
 * 1. TENSION - Constructive disagreement (no empty agreement)
 * 2. GROUNDING - References to platform metrics/systems
 * 3. DECISION SUMMARY - Structured output with insights, features, next steps
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  FileCheck,
  AlertTriangle,
  CheckCircle2,
  Zap,
  Target,
  FileText,
  ChevronDown,
  ChevronUp,
  Info,
  TrendingUp,
  Users,
  Clock,
  Lightbulb,
  Wrench,
  ArrowRight,
} from 'lucide-react'
import { conversationContractApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

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
          {complianceRate.toFixed(0)}% compliant
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
function ConversationRow({
  conversation,
  onSelect,
  isSelected,
}: {
  conversation: Conversation
  onSelect: () => void
  isSelected: boolean
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

      {/* Expanded details */}
      {isSelected && conversation.decision_summary && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          <DecisionSummaryView summary={conversation.decision_summary} />
        </div>
      )}

      {isSelected && !conversation.decision_summary && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          <div className="flex items-center gap-2 text-yellow-400">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-sm">
              No decision summary found in this conversation
            </span>
          </div>
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

// Main Page Component
export default function ConversationContractPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [days, setDays] = useState(30)

  const { data, isLoading, error } = useQuery({
    queryKey: ['conversation-contract', days],
    queryFn: async () => {
      const response = await conversationContractApi.overview(days)
      return response.data
    },
    staleTime: 30000,
  })

  const overview: ContractOverview | undefined = data?.overview
  const requirements: ContractRequirements | undefined = data?.contract_requirements
  const conversations: Conversation[] = data?.conversations || []

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
      <Breadcrumb currentPage="Conversation Contract" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Conversation Contract</h1>
          <p className="text-gray-400 mt-1">
            Quality analytics ensuring productive agent conversations
          </p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-lg border border-dark-border bg-dark-card px-3 py-2 text-white"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

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
                {overview.avg_quality_score.toFixed(0)}%
              </span>
            </div>
            <div className="text-sm text-gray-400">Average Quality</div>
          </div>
          <div className="rounded-lg border border-dark-border bg-dark-card p-4">
            <div className="text-2xl font-bold text-white">
              {overview.valid_summary_rate.toFixed(0)}%
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
          <Users className="h-5 w-5 text-primary-400" />
          Recent Conversations ({conversations.length})
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
