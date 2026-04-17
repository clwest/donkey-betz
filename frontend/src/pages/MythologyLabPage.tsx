/**
 * Mythology Lab Page
 *
 * Session 733: Hallucination detection and review interface.
 * Session 734: Updated to display all rich data from backend API.
 *
 * The Mythology Lab monitors AI outputs for potential hallucinations,
 * providing tools for reviewing flagged content and managing quarantine.
 *
 * Features:
 * 1. Dashboard stats - comprehensive real-time metrics
 * 2. Recent events - mutation types, risk levels, prevention status
 * 3. Quarantine review - teacher/student agents, violation details, spider sources
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2,
  XCircle,
  Shield,
  Activity,
  Clock,
  Flag,
  AlertCircle,
  Info,
  ChevronDown,
  ChevronUp,
  Beaker,
  Skull,
  User,
  FileQuestion,
  Zap,
  TrendingUp,
  Timer,
  Target,
  ShieldCheck,
  ArrowRight,
  ExternalLink,
  AlertTriangle,
  Ban,
} from 'lucide-react'
import { mythologyApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// =============================================================================
// Types - Matching actual backend API responses
// =============================================================================

// Stats from /api/mythology/stats/
interface MythologyStats {
  // Main dashboard stats
  total_flagged: number
  pending_review: number
  high_priority: number
  resolved_today: number
  false_positive_rate: number
  avg_review_time: number
  recent_events_24h: number
  unacknowledged_alerts: number
  // Neural Processing Stats
  total_processed: number
  events_last_hour: number
  prevention_success_rate: number
  avg_risk_score: number
  processing_rate_per_hour: number
  system_efficiency: number
  // Pattern tracking
  active_patterns?: number
}

// Events from /api/mythology/recent-events/
interface MythologyEvent {
  id: string
  event_type: string
  mutation_type?: string
  patterns_detected: string[]
  risk_level: number
  confidence_score: number
  was_prevented: boolean
  prevention_method?: string | null
  created_at: string
  content_preview: string
  original_content?: string  // Full content for expanded view
  mutated_content?: string | null  // If mutation occurred
  source_type?: string | null
  source_id?: string | null  // Session 898: The source identifier
  agent_name?: string | null  // Session 898: Direct agent name from backend
  metadata?: Record<string, unknown>
}

// Quarantine from /api/mythology/quarantine/
interface QuarantineItem {
  id: string
  teacher: string
  student: string
  blocked_title: string
  blocked_content: string
  violation_type: string
  violation_count: number
  violation_patterns: string[]
  mythology_warning: string
  spider_sources: string[]
  status: 'pending' | 'approved' | 'rejected' | 'edited'
  created_at: string
  reviewed_at?: string
  reviewed_by?: string
}

// =============================================================================
// Pattern Definitions - Human readable labels and descriptions
// =============================================================================

const PATTERN_INFO: Record<string, { label: string; description: string; icon: string }> = {
  // Myth categories detected in events
  time_myth: {
    label: 'Time Claim',
    description: 'Unrealistic timeframes or instant success claims',
    icon: '⏰',
  },
  dangerous_myth: {
    label: 'Dangerous Content',
    description: 'Potentially harmful or misleading information',
    icon: '⚠️',
  },
  financial_myth: {
    label: 'Financial Claim',
    description: 'Unverified financial projections or guarantees',
    icon: '💰',
  },
  technical_myth: {
    label: 'Technical Claim',
    description: 'Exaggerated or false technical capabilities',
    icon: '🔧',
  },
  spider_data_myth: {
    label: 'Spider Data Issue',
    description: 'Suspicious claims from spider-collected data sources',
    icon: '🕷️',
  },
  // Standard pattern types from MythPattern model
  capability_exaggeration: {
    label: 'Capability Exaggeration',
    description: 'Exaggerated claims about AI, systems, or products',
    icon: '📈',
  },
  confidence_decay: {
    label: 'Confidence Issue',
    description: 'Inappropriate confidence in uncertain claims',
    icon: '🎯',
  },
  context_loss: {
    label: 'Missing Context',
    description: 'Important context or caveats omitted',
    icon: '📝',
  },
  false_action_claims: {
    label: 'False Action',
    description: 'Claims of actions not actually performed',
    icon: '🚫',
  },
  false_authority: {
    label: 'False Authority',
    description: 'Claims of false credentials or endorsements',
    icon: '🏅',
  },
  false_technology: {
    label: 'False Tech Claim',
    description: 'False claims about technological capabilities',
    icon: '💻',
  },
  numeric_inflation: {
    label: 'Number Inflation',
    description: 'Exaggerated numeric claims or statistics',
    icon: '🔢',
  },
  semantic_drift: {
    label: 'Semantic Drift',
    description: 'Terms shifting meaning inappropriately',
    icon: '🔄',
  },
  temporal_confusion: {
    label: 'Time Confusion',
    description: 'Unrealistic time claims or instant success promises',
    icon: '📅',
  },
  unverified_stats: {
    label: 'Unverified Stats',
    description: 'Statistics without sources or verification',
    icon: '📊',
  },
}

function getPatternInfo(pattern: string): { label: string; description: string; icon: string } {
  return PATTERN_INFO[pattern] || {
    label: pattern.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
    description: 'Pattern detected in content',
    icon: '🔍',
  }
}

// =============================================================================
// Content Formatting - Clean up messy content for better readability
// =============================================================================

interface FormattedContent {
  source: string | null // e.g. "TechCrunch", "Gumroad", "Venturebeat"
  sourceType: string | null // e.g. "Spider Fetch Intelligence", "Article Intelligence"
  agents: string[] // List of agents mentioned
  cleanContent: string // The actual content, cleaned up
}

function formatMythologyContent(content: string): FormattedContent {
  const result: FormattedContent = {
    source: null,
    sourceType: null,
    agents: [],
    cleanContent: content,
  }

  if (!content) return result

  let cleanContent = content

  // Extract source header pattern: "SourceName - Intelligence Type"
  // Examples: "Gumroad - Spider Fetch Intelligence", "Techcrunch - Article Intelligence"
  const sourceMatch = cleanContent.match(/^(\[Learned\]\s*)?([A-Za-z0-9_]+)\s*-\s*([A-Za-z\s]+Intelligence)/i)
  if (sourceMatch) {
    result.source = sourceMatch[2].charAt(0).toUpperCase() + sourceMatch[2].slice(1).toLowerCase()
    result.sourceType = sourceMatch[3]
    // Remove the header from content
    cleanContent = cleanContent.replace(/^(\[Learned\]\s*)?[A-Za-z0-9_]+\s*-\s*[A-Za-z\s]+Intelligence\s*/i, '')
  }

  // Remove [Learned] prefix if still present
  cleanContent = cleanContent.replace(/^\[Learned\]\s*/i, '')

  // Clean up "Learned from X:" chains - remove nested ones, keep just the info
  // Pattern: "Learned from AgentName: Learned from AnotherAgent: Learned from..."
  const learnedFromPattern = /(?:Learned\s+from\s+[A-Za-z]+(?:Agent)?:\s*)+/gi
  const learnedMatches = cleanContent.match(/Learned\s+from\s+([A-Za-z]+(?:Agent)?)/gi)
  if (learnedMatches) {
    learnedMatches.forEach(match => {
      const agentMatch = match.match(/Learned\s+from\s+([A-Za-z]+(?:Agent)?)/i)
      if (agentMatch && !result.agents.includes(agentMatch[1])) {
        result.agents.push(agentMatch[1])
      }
    })
    // Remove the "Learned from X:" chains from content
    cleanContent = cleanContent.replace(learnedFromPattern, '')
  }

  // Clean up "Aggregated X data points from source" noise
  cleanContent = cleanContent.replace(/Aggregated\s+\d+\s+[a-z]+\s+data\s+points\s+from\s+[a-z0-9_]+\s*/gi, '')

  // Clean up multiple spaces and trim
  cleanContent = cleanContent.replace(/\s+/g, ' ').trim()

  // If content starts with agent commentary like "Building on X's point," or "I strongly disagree with X"
  // Extract the mentioned agent
  const agentRefMatch = cleanContent.match(/(?:Building on|I(?:'d| would)?\s+(?:strongly\s+)?(?:dis)?agree with|from)\s+([A-Za-z]+(?:Agent)?)'?s?\s+/i)
  if (agentRefMatch && !result.agents.includes(agentRefMatch[1])) {
    result.agents.push(agentRefMatch[1])
  }

  result.cleanContent = cleanContent

  return result
}

// =============================================================================
// Utility Components
// =============================================================================

type TabKey = 'events' | 'quarantine'

// Risk Level Badge - converts 0-1 float to visual indicator
function RiskBadge({ level }: { level: number }) {
  const getRiskInfo = (risk: number) => {
    if (risk >= 0.8) return { label: 'Critical', color: 'bg-red-500/20 text-red-300' }
    if (risk >= 0.6) return { label: 'High', color: 'bg-orange-500/20 text-orange-300' }
    if (risk >= 0.4) return { label: 'Medium', color: 'bg-yellow-500/20 text-yellow-300' }
    return { label: 'Low', color: 'bg-blue-500/20 text-blue-300' }
  }

  const { label, color } = getRiskInfo(level)

  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${color}`}>
      {label} ({((level ?? 0) * 100).toFixed(0)}%)
    </span>
  )
}

// Status Badge for quarantine items
function StatusBadge({ status }: { status: string }) {
  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-500/20 text-yellow-300',
    approved: 'bg-green-500/20 text-green-300',
    rejected: 'bg-red-500/20 text-red-300',
    edited: 'bg-blue-500/20 text-blue-300',
  }

  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${statusColors[status] || statusColors.pending}`}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

// Prevention Badge
function PreventionBadge({ prevented, method }: { prevented: boolean; method?: string | null }) {
  if (prevented) {
    return (
      <span className="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium bg-green-500/20 text-green-300">
        <ShieldCheck className="h-3 w-3" />
        {method ? `Prevented (${method})` : 'Auto-blocked'}
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium bg-red-500/20 text-red-300">
      <AlertTriangle className="h-3 w-3" />
      Detected
    </span>
  )
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon: Icon,
  color = 'text-primary-400',
  subtitle,
  trend,
}: {
  title: string
  value: number | string
  icon: React.ElementType
  color?: string
  subtitle?: string
  trend?: 'up' | 'down' | 'neutral'
}) {
  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-4">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg bg-dark-bg p-2 ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <div className="text-2xl font-bold text-white">{value}</div>
            {trend && (
              <TrendingUp
                className={`h-4 w-4 ${
                  trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400 rotate-180' : 'text-gray-400'
                }`}
              />
            )}
          </div>
          <div className="text-sm text-gray-400">{title}</div>
          {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        </div>
      </div>
    </div>
  )
}

// =============================================================================
// Event Row Component - Shows rich event data
// =============================================================================

function EventRow({
  event,
  isExpanded,
  onToggle,
}: {
  event: MythologyEvent
  isExpanded: boolean
  onToggle: () => void
}) {
  // Format the content for cleaner display
  const formatted = formatMythologyContent(event.original_content || event.content_preview)

  // Session 898: Use agent_name from API if available, fallback to regex extraction
  const displayAgents = event.agent_name
    ? [event.agent_name]
    : formatted.agents

  return (
    <div
      className={`border-b border-dark-border p-4 cursor-pointer transition-colors ${
        isExpanded ? 'bg-dark-bg' : 'hover:bg-dark-bg/50'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          {/* Header Row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <RiskBadge level={event.risk_level} />
            <span className="font-medium text-white">{event.event_type}</span>
            {event.mutation_type && (
              <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
                {event.mutation_type}
              </span>
            )}
            <PreventionBadge prevented={event.was_prevented} method={event.prevention_method} />
          </div>

          {/* Source Header (if spider data) */}
          {formatted.source && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-medium">
                {formatted.source}
              </span>
              {formatted.sourceType && (
                <span className="text-xs text-gray-500">{formatted.sourceType}</span>
              )}
            </div>
          )}

          {/* Agent - Session 898: Use API field instead of regex */}
          {displayAgents.length > 0 && (
            <div className="flex items-center gap-1 mb-2 text-xs">
              <User className="h-3 w-3 text-blue-400" />
              <span className="text-gray-500">Agent:</span>
              {displayAgents.slice(0, 3).map((agent, idx) => (
                <span key={idx} className="text-blue-300 font-medium">
                  {agent}{idx < Math.min(displayAgents.length - 1, 2) ? ',' : ''}
                </span>
              ))}
              {displayAgents.length > 3 && (
                <span className="text-gray-500">+{displayAgents.length - 3} more</span>
              )}
            </div>
          )}

          {/* Content Preview (cleaned) */}
          <p className="text-sm text-gray-300 line-clamp-2 mb-2">
            {formatted.cleanContent.slice(0, 200)}{formatted.cleanContent.length > 200 ? '...' : ''}
          </p>

          {/* Patterns Detected */}
          {event.patterns_detected && event.patterns_detected.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-2">
              {event.patterns_detected.map((pattern, idx) => {
                const info = getPatternInfo(pattern)
                return (
                  <span
                    key={idx}
                    className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400 border border-dark-border"
                    title={info.description}
                  >
                    {info.icon} {info.label}
                  </span>
                )
              })}
            </div>
          )}

          {/* Meta Info */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Target className="h-3 w-3" />
              Confidence: {((event.confidence_score ?? 0) * 100).toFixed(0)}%
            </span>
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(event.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
        )}
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-dark-border space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">Risk Level</div>
              <div className="text-white font-medium">{((event.risk_level ?? 0) * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Confidence</div>
              <div className="text-white font-medium">{((event.confidence_score ?? 0) * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Prevention</div>
              <div className="text-white font-medium">{event.was_prevented ? 'Yes' : 'No'}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Method</div>
              <div className="text-white font-medium">
                {event.prevention_method || (event.was_prevented ? 'Auto-blocked' : 'Not prevented')}
              </div>
            </div>
          </div>

          {event.source_type && (
            <div>
              <div className="text-xs text-gray-500 mb-1">Source Type</div>
              <div className="text-white font-medium">{event.source_type}</div>
            </div>
          )}

          {event.patterns_detected && event.patterns_detected.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-2">Patterns Detected</div>
              <div className="space-y-2">
                {event.patterns_detected.map((pattern, idx) => {
                  const info = getPatternInfo(pattern)
                  return (
                    <div
                      key={idx}
                      className="flex items-start gap-3 p-2 rounded bg-dark-bg border border-dark-border"
                    >
                      <span className="text-lg">{info.icon}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-300">{info.label}</div>
                        <div className="text-xs text-gray-500">{info.description}</div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Formatted Content (cleaned up) */}
          <div>
            <div className="text-xs text-gray-500 mb-2">Content Analysis</div>
            <div className="bg-dark-bg rounded p-3 space-y-3">
              {/* Source Info */}
              {formatted.source && (
                <div className="flex items-center gap-2 pb-2 border-b border-dark-border">
                  <span className="text-xs px-2 py-1 rounded bg-cyan-500/20 text-cyan-300 font-medium">
                    {formatted.source}
                  </span>
                  {formatted.sourceType && (
                    <span className="text-xs text-gray-500">{formatted.sourceType}</span>
                  )}
                </div>
              )}

              {/* Agent - Session 898: Use API field instead of regex */}
              {displayAgents.length > 0 && (
                <div className="flex flex-wrap items-center gap-2 pb-2 border-b border-dark-border">
                  <span className="text-xs text-gray-500">Agent:</span>
                  {displayAgents.map((agent, idx) => (
                    <span key={idx} className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-medium">
                      {agent}
                    </span>
                  ))}
                </div>
              )}

              {/* Clean Content */}
              <div className="text-sm text-gray-300 max-h-40 overflow-y-auto whitespace-pre-wrap">
                {formatted.cleanContent}
              </div>
            </div>
          </div>

          {/* Raw Original Content (collapsible) */}
          {/* Session 757: Stop propagation to prevent card from collapsing when clicking details */}
          <details className="group" onClick={(e) => e.stopPropagation()}>
            <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-400">
              View Raw Original Content
            </summary>
            <div className="mt-2 text-sm text-gray-500 bg-dark-bg/50 rounded p-3 max-h-40 overflow-y-auto whitespace-pre-wrap border border-dark-border">
              {event.original_content || event.content_preview}
            </div>
          </details>

          {event.mutated_content && (
            <div>
              <div className="text-xs text-gray-500 mb-2">Mutated Content</div>
              <div className="text-sm text-red-400 bg-red-500/10 rounded p-3 max-h-40 overflow-y-auto whitespace-pre-wrap border border-red-500/30">
                {event.mutated_content}
              </div>
            </div>
          )}

          {event.metadata && Object.keys(event.metadata).length > 0 && (() => {
            // Filter out technical fields (regex patterns, internal keys)
            const technicalKeys = ['time_myth', 'dangerous_myth', 'financial_myth', 'technical_myth',
              'spider_data_myth', 'regex', 'pattern', 'patterns', 'matcher', 'rule', '_myth']
            const displayableEntries = Object.entries(event.metadata).filter(([key, value]) => {
              // Skip if key is a known technical field
              if (technicalKeys.some(tk => key.toLowerCase().includes(tk))) return false
              // Skip if value looks like a regex pattern
              if (typeof value === 'string' && (value.includes('(?:') || value.includes('\\b'))) return false
              // Skip if value is an array of regex patterns
              if (Array.isArray(value) && value.some(v => typeof v === 'string' && (v.includes('(?:') || v.includes('\\b')))) return false
              return true
            })

            if (displayableEntries.length === 0) return null

            return (
              <div>
                <div className="text-xs text-gray-500 mb-2">Additional Metadata</div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 bg-dark-bg rounded p-3">
                  {displayableEntries.map(([key, value]) => (
                    <div key={key} className="text-sm">
                      <div className="text-gray-500 text-xs capitalize">{key.replace(/_/g, ' ')}</div>
                      <div className="text-gray-300 font-medium">
                        {typeof value === 'boolean'
                          ? (value ? 'Yes' : 'No')
                          : typeof value === 'object'
                            ? JSON.stringify(value)
                            : String(value)}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })()}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Quarantine Row Component - Shows teacher/student, violations, spider sources
// =============================================================================

function QuarantineRow({
  item,
  isExpanded,
  onToggle,
  onApprove,
  onReject,
  isProcessing,
}: {
  item: QuarantineItem
  isExpanded: boolean
  onToggle: () => void
  onApprove: () => void
  onReject: () => void
  isProcessing: boolean
}) {
  return (
    <div className={`border-b border-dark-border p-4 ${isExpanded ? 'bg-dark-bg' : ''}`}>
      <div className="flex items-start justify-between cursor-pointer" onClick={onToggle}>
        <div className="flex-1 min-w-0">
          {/* Header Row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <StatusBadge status={item.status} />
            <span className="text-xs px-2 py-0.5 rounded bg-orange-500/20 text-orange-300">
              {item.violation_type}
            </span>
            <span className="text-xs text-gray-500">
              {item.violation_count} violation{item.violation_count !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Title */}
          <h4 className="font-medium text-white mb-1">{item.blocked_title}</h4>

          {/* Agent Flow */}
          <div className="flex items-center gap-2 text-sm text-gray-400 mb-2">
            <User className="h-4 w-4 text-blue-400" />
            <span className="text-blue-300">{item.teacher}</span>
            <ArrowRight className="h-4 w-4" />
            <User className="h-4 w-4 text-green-400" />
            <span className="text-green-300">{item.student}</span>
          </div>

          {/* Mythology Warning */}
          {item.mythology_warning && (
            <div className="flex items-start gap-2 text-sm text-yellow-400 mb-2">
              <AlertTriangle className="h-4 w-4 flex-shrink-0 mt-0.5" />
              <span className="line-clamp-2">{item.mythology_warning}</span>
            </div>
          )}

          {/* Meta Info */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(item.created_at).toLocaleString()}
            </span>
            {item.reviewed_by && (
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                Reviewed by {item.reviewed_by}
              </span>
            )}
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
        )}
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-dark-border space-y-4">
          {/* Violation Patterns */}
          {item.violation_patterns && item.violation_patterns.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-2">Violation Patterns</div>
              <div className="flex flex-wrap gap-2">
                {item.violation_patterns.map((pattern, idx) => (
                  <span
                    key={idx}
                    className="text-sm px-3 py-1 rounded bg-red-500/10 text-red-300 border border-red-500/30"
                  >
                    <Ban className="h-3 w-3 inline mr-1" />
                    {pattern}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Spider Sources */}
          {item.spider_sources && item.spider_sources.length > 0 && (
            <div>
              <div className="text-xs text-gray-500 mb-2">Spider Sources</div>
              <div className="flex flex-wrap gap-2">
                {item.spider_sources.map((source, idx) => (
                  <span
                    key={idx}
                    className="text-sm px-3 py-1 rounded bg-blue-500/10 text-blue-300 border border-blue-500/30"
                  >
                    <ExternalLink className="h-3 w-3 inline mr-1" />
                    {source}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Blocked Content */}
          <div>
            <div className="text-xs text-gray-500 mb-2">Blocked Content</div>
            <div className="text-sm text-gray-400 bg-dark-bg rounded p-3 max-h-60 overflow-y-auto whitespace-pre-wrap">
              {item.blocked_content}
            </div>
          </div>

          {/* Actions */}
          {item.status === 'pending' && (
            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onApprove()
                }}
                disabled={isProcessing}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg text-sm transition-colors"
              >
                <CheckCircle2 className="h-4 w-4" />
                Approve (False Positive)
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onReject()
                }}
                disabled={isProcessing}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg text-sm transition-colors"
              >
                <XCircle className="h-4 w-4" />
                Reject (Confirm Myth)
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Main Page Component
// =============================================================================

export default function MythologyLabPage() {
  const [activeTab, setActiveTab] = useState<TabKey>('events')
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null)
  const [expandedQuarantineId, setExpandedQuarantineId] = useState<string | null>(null)
  const [processingId, setProcessingId] = useState<string | null>(null)

  const queryClient = useQueryClient()

  // Fetch stats
  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['mythology-stats'],
    queryFn: async () => {
      const response = await mythologyApi.stats()
      return response.data as MythologyStats
    },
    staleTime: 30000,
  })

  // Fetch recent events
  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['mythology-events'],
    queryFn: async () => {
      const response = await mythologyApi.recentEvents({ limit: 50 })
      return response.data
    },
    staleTime: 30000,
  })

  // Fetch quarantine items
  const { data: quarantineData, isLoading: quarantineLoading } = useQuery({
    queryKey: ['mythology-quarantine'],
    queryFn: async () => {
      const response = await mythologyApi.quarantine({ status: 'pending' })
      return response.data
    },
    staleTime: 30000,
  })

  // Approve mutation
  const approveMutation = useMutation({
    mutationFn: async (quarantineId: string) => {
      setProcessingId(quarantineId)
      const response = await mythologyApi.quarantineApprove(quarantineId)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mythology-quarantine'] })
      queryClient.invalidateQueries({ queryKey: ['mythology-stats'] })
      setProcessingId(null)
    },
    onError: () => {
      setProcessingId(null)
    },
  })

  // Reject mutation
  const rejectMutation = useMutation({
    mutationFn: async (quarantineId: string) => {
      setProcessingId(quarantineId)
      const response = await mythologyApi.quarantineReject(quarantineId)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mythology-quarantine'] })
      queryClient.invalidateQueries({ queryKey: ['mythology-stats'] })
      setProcessingId(null)
    },
    onError: () => {
      setProcessingId(null)
    },
  })

  // Session 1095 Tier 1b: bulk-review by pattern_type mutation.
  // Unblocks the FP backlog when an over-broad regex is flooding the
  // queue. Response reports how many rows got reviewed + pattern tuning.
  const bulkReviewMutation = useMutation({
    mutationFn: async (args: { pattern_type: string; action: 'flag_false_positive' | 'remove'; priority?: string; notes?: string }) => {
      const response = await mythologyApi.bulkReview({
        pattern_type: args.pattern_type,
        action: args.action,
        priority: (args.priority as 'critical' | 'high' | 'medium' | 'low' | undefined),
        notes: args.notes,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mythology-stats'] })
      queryClient.invalidateQueries({ queryKey: ['mythology-events'] })
      queryClient.invalidateQueries({ queryKey: ['mythology-quarantine'] })
    },
  })

  const stats = statsData
  const events: MythologyEvent[] = eventsData?.events || []
  const quarantineItems: QuarantineItem[] = quarantineData?.items || []

  // Session 1095 Tier 1b: compute pattern-frequency histogram from
  // recent events so we can surface "this one pattern is dominating"
  // as a one-click bulk-clear target.
  const patternFrequency = (() => {
    const counts = new Map<string, number>()
    for (const ev of events) {
      for (const p of (ev.patterns_detected || [])) {
        counts.set(p, (counts.get(p) || 0) + 1)
      }
    }
    return Array.from(counts.entries())
      .map(([pattern, count]) => ({ pattern, count }))
      .sort((a, b) => b.count - a.count)
  })()
  const topPattern = patternFrequency[0]
  const dominantPattern =
    topPattern && topPattern.count >= 20 &&
    (patternFrequency.length === 1 || topPattern.count >= (patternFrequency[1]?.count || 0) * 1.5)
      ? topPattern
      : null

  const isLoading = statsLoading || eventsLoading || quarantineLoading

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse text-gray-400">Loading Mythology Lab...</div>
      </div>
    )
  }

  const tabs = [
    {
      key: 'events' as const,
      label: 'Recent Events',
      icon: Activity,
      count: events.length,
    },
    {
      key: 'quarantine' as const,
      label: 'Quarantine Review',
      icon: Shield,
      count: quarantineItems.length,
    },
  ]

  return (
    <div className="space-y-6 p-6">
      <Breadcrumb currentPage="Mythology Lab" />

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-3 text-2xl font-bold text-white">
            <Beaker className="h-8 w-8 text-purple-400" />
            Mythology Lab
          </h1>
          <p className="text-gray-400 mt-1">Hallucination detection, prevention, and content review system</p>
        </div>
      </div>

      {/* Primary Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Flagged"
            value={stats.total_flagged || 0}
            icon={Flag}
            color="text-red-400"
          />
          <StatCard
            title="Pending Review"
            value={stats.pending_review || 0}
            icon={FileQuestion}
            color="text-yellow-400"
          />
          <StatCard
            title="High Priority"
            value={stats.high_priority || 0}
            icon={AlertCircle}
            color="text-orange-400"
          />
          <StatCard
            title="Resolved Today"
            value={stats.resolved_today || 0}
            icon={CheckCircle2}
            color="text-green-400"
          />
        </div>
      )}

      {/* Session 1095 Tier 1b: Bulk review panel — surfaces only when
         a single pattern dominates recent events (likely FP flood from
         an over-broad regex). One-click batch clear with pattern tuning. */}
      {dominantPattern && (
        <div className="rounded-lg border-2 border-amber-500/40 bg-amber-500/10 p-4">
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-amber-100 flex items-center gap-2">
                  Pattern dominates recent events
                </h3>
                <p className="text-xs text-amber-200/80 mt-1">
                  <code className="bg-amber-900/40 px-1.5 py-0.5 rounded">{dominantPattern.pattern}</code>
                  {' '}fired <strong>{dominantPattern.count}</strong> times in recent events
                  {patternFrequency[1] ? ` (vs ${patternFrequency[1].count} for next-most pattern)` : ''}.
                  {' '}Likely over-broad regex producing false positives — review one sample, then bulk-clear the rest.
                </p>
              </div>
            </div>
            <div className="flex gap-2 flex-shrink-0">
              <button
                onClick={() => {
                  if (!confirm(`Mark all pending "${dominantPattern.pattern}" flags as FALSE POSITIVES?\n\nThis will clear the backlog and nudge the pattern's severity down. Undoable via admin.`)) return
                  bulkReviewMutation.mutate({
                    pattern_type: dominantPattern.pattern,
                    action: 'flag_false_positive',
                    notes: `Bulk clear — over-broad pattern dominating ${dominantPattern.count} of ${events.length} recent events`,
                  })
                }}
                disabled={bulkReviewMutation.isPending}
                className="px-3 py-1.5 text-xs font-medium bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {bulkReviewMutation.isPending ? 'Processing...' : 'Bulk clear as FPs'}
              </button>
              <button
                onClick={() => {
                  if (!confirm(`Mark all pending "${dominantPattern.pattern}" flags as VERIFIED HALLUCINATIONS?\n\nOnly do this if you've confirmed this pattern catches real bad content.`)) return
                  bulkReviewMutation.mutate({
                    pattern_type: dominantPattern.pattern,
                    action: 'remove',
                    notes: `Bulk confirm — pattern catches real hallucinations`,
                  })
                }}
                disabled={bulkReviewMutation.isPending}
                className="px-3 py-1.5 text-xs font-medium bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-100 rounded disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Confirm as hallucinations
              </button>
            </div>
          </div>
          {bulkReviewMutation.isSuccess && bulkReviewMutation.data && (
            <div className="mt-3 pt-3 border-t border-amber-500/30 text-xs text-amber-100">
              <CheckCircle2 className="h-4 w-4 inline mr-1 text-green-400" />
              Bulk-reviewed <strong>{(bulkReviewMutation.data as {reviewed_count?: number}).reviewed_count || 0}</strong> flags.
              {(bulkReviewMutation.data as {pattern_tuning?: {auto_disabled?: string[]}}).pattern_tuning?.auto_disabled?.length ? (
                <span className="ml-2 text-green-300">
                  Auto-disabled pattern(s): {(bulkReviewMutation.data as {pattern_tuning?: {auto_disabled?: string[]}}).pattern_tuning?.auto_disabled?.join(', ')}
                </span>
              ) : null}
            </div>
          )}
          {bulkReviewMutation.isError && (
            <div className="mt-3 pt-3 border-t border-red-500/30 text-xs text-red-200">
              <XCircle className="h-4 w-4 inline mr-1" />
              Bulk review failed — check the API and retry.
            </div>
          )}
        </div>
      )}

      {/* Neural Processing Stats */}
      {stats && (
        <div className="rounded-lg border border-dark-border bg-dark-card p-4">
          <h3 className="flex items-center gap-2 text-sm font-medium text-white mb-4">
            <Zap className="h-4 w-4 text-purple-400" />
            Neural Processing Stats
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{stats.total_processed || 0}</div>
              <div className="text-xs text-gray-500">Total Processed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{stats.events_last_hour || 0}</div>
              <div className="text-xs text-gray-500">Events/Hour</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">{stats.prevention_success_rate?.toFixed(1) || 0}%</div>
              <div className="text-xs text-gray-500">Prevention Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">{stats.avg_risk_score?.toFixed(2) || 0}</div>
              <div className="text-xs text-gray-500">Avg Risk Score</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-400">{stats.false_positive_rate?.toFixed(1) || 0}%</div>
              <div className="text-xs text-gray-500">False Positive Rate</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">{stats.active_patterns || 0}</div>
              <div className="text-xs text-gray-500">Active Patterns</div>
            </div>
          </div>
        </div>
      )}

      {/* Secondary Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Recent Events (24h)"
            value={stats.recent_events_24h || 0}
            icon={Activity}
            color="text-blue-400"
          />
          <StatCard
            title="Unacknowledged Alerts"
            value={stats.unacknowledged_alerts || 0}
            icon={AlertCircle}
            color="text-red-400"
          />
          <StatCard
            title="Avg Review Time"
            value={`${stats.avg_review_time?.toFixed(1) || 0}s`}
            icon={Timer}
            color="text-cyan-400"
          />
          <StatCard
            title="System Efficiency"
            value={`${stats.system_efficiency?.toFixed(1) || 0}%`}
            icon={Target}
            color="text-green-400"
          />
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex items-center gap-2 border-b border-dark-border">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'border-primary-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {tab.count > 0 && (
              <span className="ml-1 px-2 py-0.5 rounded-full bg-dark-bg text-xs">{tab.count}</span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content - Events */}
      {activeTab === 'events' && (
        <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
          {events.length === 0 ? (
            <div className="p-8 text-center">
              <Skull className="h-12 w-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400">No mythology events detected</p>
              <p className="text-sm text-gray-500 mt-1">
                Events will appear here when hallucinations are detected
              </p>
            </div>
          ) : (
            events.map((event) => (
              <EventRow
                key={event.id}
                event={event}
                isExpanded={expandedEventId === event.id}
                onToggle={() => setExpandedEventId(expandedEventId === event.id ? null : event.id)}
              />
            ))
          )}
        </div>
      )}

      {/* Tab Content - Quarantine */}
      {activeTab === 'quarantine' && (
        <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
          {quarantineItems.length === 0 ? (
            <div className="p-8 text-center">
              <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-400">No items pending review</p>
              <p className="text-sm text-gray-500 mt-1">
                Quarantined knowledge transfers will appear here for approval
              </p>
            </div>
          ) : (
            quarantineItems.map((item) => (
              <QuarantineRow
                key={item.id}
                item={item}
                isExpanded={expandedQuarantineId === item.id}
                onToggle={() =>
                  setExpandedQuarantineId(expandedQuarantineId === item.id ? null : item.id)
                }
                onApprove={() => approveMutation.mutate(item.id)}
                onReject={() => rejectMutation.mutate(item.id)}
                isProcessing={processingId === item.id}
              />
            ))
          )}
        </div>
      )}

      {/* Info Box */}
      <div className="rounded-lg border border-dark-border bg-dark-card p-4">
        <h3 className="flex items-center gap-2 text-white font-medium mb-3">
          <Info className="h-5 w-5 text-primary-400" />
          About Mythology Lab
        </h3>
        <div className="text-sm text-gray-400 space-y-2">
          <p>
            The Mythology Lab is the AI hallucination detection and review system. It monitors all
            AI-generated content for potential fabrications, inconsistencies, and unsupported claims.
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>
              <strong className="text-gray-300">Detection Patterns</strong> - Rules that identify
              suspicious content patterns (numeric inflation, false claims, context loss)
            </li>
            <li>
              <strong className="text-gray-300">Events</strong> - Logged instances with risk levels,
              confidence scores, and prevention status
            </li>
            <li>
              <strong className="text-gray-300">Quarantine</strong> - Blocked knowledge transfers
              between agents awaiting human review
            </li>
            <li>
              <strong className="text-gray-300">Spider Sources</strong> - External data sources that
              may have contributed to flagged content
            </li>
          </ul>
          <p>
            Review quarantined items to approve false positives or reject confirmed myths before they
            propagate through the agent network.
          </p>
        </div>
      </div>
    </div>
  )
}
