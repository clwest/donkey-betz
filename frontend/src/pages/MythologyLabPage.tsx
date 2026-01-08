/**
 * Mythology Lab Page
 *
 * Session 733: Hallucination detection and review interface.
 *
 * The Mythology Lab monitors AI outputs for potential hallucinations,
 * providing tools for reviewing flagged content and managing quarantine.
 *
 * Features:
 * 1. Dashboard stats - total events, patterns, alerts, flagged content
 * 2. Recent events - severity badges, event type, agent source
 * 3. Pattern library - detection patterns and statistics
 * 4. Quarantine review - approve/reject flagged content
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  CheckCircle2,
  XCircle,
  Shield,
  Activity,
  BookOpen,
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
} from 'lucide-react'
import { mythologyApi } from '@/lib/api'
import Breadcrumb from '@/components/Breadcrumb'

// Types
interface MythologyStats {
  total_events: number
  patterns_count: number
  active_alerts: number
  flagged_content_count: number
  quarantine_pending: number
  events_by_severity?: Record<string, number>
}

interface MythologyEvent {
  id: string
  event_type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  agent_name?: string
  description: string
  created_at: string
  details?: Record<string, unknown>
}

interface QuarantineItem {
  id: string
  content_type: string
  content_preview: string
  reason: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  agent_name?: string
  created_at: string
  status: 'pending' | 'approved' | 'rejected'
}

// Tabs
type TabKey = 'events' | 'quarantine'

// Severity Badge Component
function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    low: 'bg-blue-500/20 text-blue-300',
    medium: 'bg-yellow-500/20 text-yellow-300',
    high: 'bg-orange-500/20 text-orange-300',
    critical: 'bg-red-500/20 text-red-300',
  }

  return (
    <span
      className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${
        colors[severity] || colors.low
      }`}
    >
      {severity.charAt(0).toUpperCase() + severity.slice(1)}
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
}: {
  title: string
  value: number | string
  icon: React.ElementType
  color?: string
  subtitle?: string
}) {
  return (
    <div className="rounded-lg border border-dark-border bg-dark-card p-4">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg bg-dark-bg p-2 ${color}`}>
          <Icon className="h-5 w-5" />
        </div>
        <div>
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-sm text-gray-400">{title}</div>
          {subtitle && <div className="text-xs text-gray-500">{subtitle}</div>}
        </div>
      </div>
    </div>
  )
}

// Event Row Component
function EventRow({
  event,
  isExpanded,
  onToggle,
}: {
  event: MythologyEvent
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <div
      className={`border-b border-dark-border p-4 cursor-pointer transition-colors ${
        isExpanded ? 'bg-dark-bg' : 'hover:bg-dark-bg/50'
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <SeverityBadge severity={event.severity} />
            <span className="font-medium text-white">{event.event_type}</span>
          </div>
          <p className="text-sm text-gray-400 truncate">{event.description}</p>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            {event.agent_name && (
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {event.agent_name}
              </span>
            )}
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

      {isExpanded && event.details && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          <h4 className="text-sm font-medium text-white mb-2">Event Details</h4>
          <pre className="text-xs text-gray-400 bg-dark-bg rounded p-3 overflow-x-auto">
            {JSON.stringify(event.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}

// Quarantine Row Component
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
    <div
      className={`border-b border-dark-border p-4 ${
        isExpanded ? 'bg-dark-bg' : ''
      }`}
    >
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={onToggle}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <SeverityBadge severity={item.severity} />
            <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-300">
              {item.content_type}
            </span>
            {item.status === 'pending' && (
              <span className="text-xs px-2 py-0.5 rounded bg-yellow-500/20 text-yellow-300">
                Pending Review
              </span>
            )}
          </div>
          <p className="text-sm text-gray-300 line-clamp-2">
            {item.content_preview}
          </p>
          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Flag className="h-3 w-3" />
              {item.reason}
            </span>
            {item.agent_name && (
              <span className="flex items-center gap-1">
                <User className="h-3 w-3" />
                {item.agent_name}
              </span>
            )}
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(item.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0" />
        )}
      </div>

      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          <div className="mb-4">
            <h4 className="text-sm font-medium text-white mb-2">
              Full Content Preview
            </h4>
            <div className="text-sm text-gray-400 bg-dark-bg rounded p-3 max-h-40 overflow-y-auto">
              {item.content_preview}
            </div>
          </div>

          {item.status === 'pending' && (
            <div className="flex items-center gap-3">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onApprove()
                }}
                disabled={isProcessing}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white rounded-lg text-sm transition-colors"
              >
                <CheckCircle2 className="h-4 w-4" />
                Approve
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
                Reject
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Main Page Component
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
      return response.data
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

  const stats: MythologyStats | undefined = statsData
  const events: MythologyEvent[] = eventsData?.events || eventsData || []
  const quarantineItems: QuarantineItem[] =
    quarantineData?.items || quarantineData || []

  const isLoading = statsLoading || eventsLoading || quarantineLoading

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-pulse text-gray-400">
          Loading Mythology Lab...
        </div>
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
          <p className="text-gray-400 mt-1">
            Hallucination detection and content review system
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Total Events"
            value={stats.total_events || 0}
            icon={Activity}
            color="text-blue-400"
          />
          <StatCard
            title="Detection Patterns"
            value={stats.patterns_count || 0}
            icon={BookOpen}
            color="text-green-400"
          />
          <StatCard
            title="Active Alerts"
            value={stats.active_alerts || 0}
            icon={AlertCircle}
            color="text-yellow-400"
          />
          <StatCard
            title="Pending Review"
            value={stats.quarantine_pending || quarantineItems.length || 0}
            icon={FileQuestion}
            color="text-orange-400"
          />
        </div>
      )}

      {/* Severity Breakdown */}
      {stats?.events_by_severity && (
        <div className="rounded-lg border border-dark-border bg-dark-card p-4">
          <h3 className="text-sm font-medium text-white mb-3">
            Events by Severity
          </h3>
          <div className="flex items-center gap-6">
            {Object.entries(stats.events_by_severity).map(([severity, count]) => (
              <div key={severity} className="flex items-center gap-2">
                <SeverityBadge severity={severity} />
                <span className="text-white font-medium">{count as number}</span>
              </div>
            ))}
          </div>
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
              <span className="ml-1 px-2 py-0.5 rounded-full bg-dark-bg text-xs">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
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
                onToggle={() =>
                  setExpandedEventId(
                    expandedEventId === event.id ? null : event.id
                  )
                }
              />
            ))
          )}
        </div>
      )}

      {activeTab === 'quarantine' && (
        <div className="rounded-lg border border-dark-border bg-dark-card overflow-hidden">
          {quarantineItems.length === 0 ? (
            <div className="p-8 text-center">
              <CheckCircle2 className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <p className="text-gray-400">No items pending review</p>
              <p className="text-sm text-gray-500 mt-1">
                Quarantined content will appear here for approval
              </p>
            </div>
          ) : (
            quarantineItems.map((item) => (
              <QuarantineRow
                key={item.id}
                item={item}
                isExpanded={expandedQuarantineId === item.id}
                onToggle={() =>
                  setExpandedQuarantineId(
                    expandedQuarantineId === item.id ? null : item.id
                  )
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
            The Mythology Lab is the AI hallucination detection and review system.
            It monitors all AI-generated content for potential fabrications,
            inconsistencies, and unsupported claims.
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>
              <strong className="text-gray-300">Detection Patterns</strong> -
              Rules that identify suspicious content patterns
            </li>
            <li>
              <strong className="text-gray-300">Events</strong> - Logged
              instances where potential hallucinations were detected
            </li>
            <li>
              <strong className="text-gray-300">Quarantine</strong> - Content
              held for human review before release
            </li>
          </ul>
          <p>
            Review quarantined items to approve safe content or reject
            hallucinated outputs before they reach users.
          </p>
        </div>
      </div>
    </div>
  )
}
