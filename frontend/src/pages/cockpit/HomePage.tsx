import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Package, FileText, Send, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import TodayRunsCard from '@/components/cockpit/today/TodayRunsCard'
import TodayErrorsCard from '@/components/cockpit/today/TodayErrorsCard'
import NorthStarCard from '@/components/cockpit/today/NorthStarCard'
import NoiseLeaderboardCard from '@/components/cockpit/today/NoiseLeaderboardCard'
import FocusModeCard from '@/components/cockpit/today/FocusModeCard'
import { useRuns, useErrorSummary } from '@/hooks/cockpitQueries'
import { getVipContext, type VipContext } from '@/lib/cockpitApi'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { api } from '@/lib/api'
import type { RunSummary, NextActionType } from '@/types/cockpit'

// Action types that indicate a blocking issue
const BLOCKING_ACTIONS: NextActionType[] = [
  'investigate_failure',
  'retry_timeout',
  'fix_config',
  'rate_limited',
]

// Action types that indicate reviewable output
const REVIEW_ACTIONS: NextActionType[] = [
  'review_deliverable',
  'approve_content',
  'preview_media',
  'view_artifacts',
]

function classifyRun(r: RunSummary): 'attention' | 'review' | 'routine' {
  if (r.status === 'failed' && !(r as any).superseded) return 'attention'

  const actionType = r.enrichment?.next_action?.type
  const importance = r.enrichment?.importance?.level

  if (importance === 'action_required') return 'attention'
  if (actionType && BLOCKING_ACTIONS.includes(actionType)) return 'attention'

  if (actionType && REVIEW_ACTIONS.includes(actionType)) {
    // Only "review" if there are actual artifacts
    const arts = r.enrichment?.artifacts
    if (arts) {
      const count =
        (arts.deliverables?.length || 0) +
        (arts.blogs?.length || 0) +
        (arts.media?.length || 0) +
        (arts.wagers?.length || 0) +
        (arts.initiatives?.length || 0)
      if (count > 0) return 'review'
    }
  }

  return 'routine'
}

// ── VIP Deliverables List (expandable cards with inline content) ────────────

function VipDeliverablesList({ items }: { items: Array<{ id: string; title: string; category?: string; deliverable_type?: string; agent_name?: string; created_at?: string }> }) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  // Fetch full content for expanded deliverable
  const { data: expandedDetail } = useQuery({
    queryKey: ['deliverable-detail', expandedId],
    queryFn: async () => {
      if (!expandedId) return null
      const res = await api.get(`/deliverables/${expandedId}/`)
      // API returns {success, deliverable: {content, ...}} — unwrap
      return res.data?.deliverable || res.data
    },
    enabled: !!expandedId,
  })

  if (items.length === 0) {
    return (
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Workspace Deliverables</h2>
        <div className="card p-6 text-center text-gray-500">
          <FileText className="mx-auto mb-2" size={24} />
          <p className="text-sm">No deliverables yet</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-3">Workspace Deliverables</h2>
      <div className="space-y-2">
        {items.map((d) => {
          const isExpanded = expandedId === d.id
          return (
            <div key={d.id} className="card overflow-hidden">
              <button
                onClick={() => setExpandedId(isExpanded ? null : d.id)}
                className="w-full p-4 flex items-center justify-between hover:bg-gray-800/30 transition-colors text-left"
              >
                <div className="flex items-center gap-3">
                  <FileText size={16} className="text-primary-400 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-white">{d.title}</p>
                    <p className="text-xs text-gray-500">
                      {d.category || d.deliverable_type}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {d.created_at && (
                    <span className="text-xs text-gray-500">
                      {new Date(d.created_at).toLocaleDateString()}
                    </span>
                  )}
                  {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                </div>
              </button>

              {isExpanded && (
                <div className="border-t border-dark-border p-5">
                  {expandedDetail?.content ? (
                    <div className="prose prose-invert prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {expandedDetail.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <div className="text-center py-4 text-gray-500 text-sm">Loading...</div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ── VIP Welcome View ────────────────────────────────────────────────────────

function VipWelcome({ vip }: { vip: VipContext }) {
  const { data: deliverables } = useQuery({
    queryKey: ['vip-deliverables', vip.workspace_id],
    queryFn: async () => {
      if (!vip.workspace_id) return { items: [], total: 0 }
      const res = await api.get('/cockpit/library/deliverables/', {
        params: { days: 30, limit: 20 },
      })
      return res.data
    },
    enabled: !!vip.workspace_id,
  })

  const items = (
    Array.isArray(deliverables?.items) ? deliverables.items
    : Array.isArray(deliverables?.results) ? deliverables.results
    : Array.isArray(deliverables) ? deliverables
    : []
  )
  const firstName = (vip.recipient_name || 'there').split(' ')[0]

  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <div className="card bg-gradient-to-r from-primary-500/10 to-accent-cyan/10 border-primary-500/30">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white mb-2">
            Welcome{firstName !== 'there' ? `, ${firstName}` : ''}
          </h1>
          <p className="text-gray-300">
            {vip.workspace_name
              ? `You're viewing the ${vip.workspace_name} workspace — here's what we've built.`
              : `You have VIP access to the Donkey Betz platform.`}
          </p>
          {vip.workspace_deliverable_count != null && (
            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Package size={14} className="text-primary-400" />
                <span>{vip.workspace_deliverable_count} deliverables</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Deliverables — expandable cards with inline content */}
      <VipDeliverablesList items={items} />

      {/* Prospect Profile (rendered markdown) */}
      {vip.prospect_profile_preview && (
        <div className="card p-5">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Your Profile</h3>
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {vip.prospect_profile_preview}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Home Page ──────────────────────────────────────────────────────────

export default function CockpitHomePage() {
  const activeWorkspace = useWorkspaceStore((s) => s.activeWorkspace)
  const wsId = activeWorkspace?.id

  const { data: vipContext, isLoading: vipLoading } = useQuery({
    queryKey: ['vip-context'],
    queryFn: getVipContext,
    staleTime: 5 * 60 * 1000,
  })

  const { data: runs = [], isLoading: runsLoading } = useRuns({ hours: 24, limit: 50, enrich: 1, ...(wsId ? { workspace: wsId } : {}) })
  const { data: errors, isLoading: errorsLoading } = useErrorSummary(24)
  const [showRoutine, setShowRoutine] = useState(false)

  // If VIP user, show personalized view
  if (!vipLoading && vipContext?.is_vip) {
    return <VipWelcome vip={vipContext} />
  }

  // Split runs into 3 buckets
  const attention: RunSummary[] = []
  const review: RunSummary[] = []
  const routine: RunSummary[] = []

  for (const r of runs) {
    const bucket = classifyRun(r)
    if (bucket === 'attention') attention.push(r)
    else if (bucket === 'review') review.push(r)
    else routine.push(r)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Today</h1>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          {/* Section 1: Needs attention (blocking) */}
          <TodayRunsCard
            runs={attention}
            isLoading={runsLoading}
            title="Needs attention"
            emptyMessage="Nothing needs attention"
            maxRows={10}
            section="attention"
          />

          {/* Section 2: Ready for review (value created) */}
          <TodayRunsCard
            runs={review}
            isLoading={runsLoading}
            title="Ready for review"
            emptyMessage="No items to review"
            maxRows={10}
            section="review"
          />

          {/* Section 3: Routine (collapsed) */}
          {routine.length > 0 && (
            <div className="card">
              <button
                onClick={() => setShowRoutine(!showRoutine)}
                className="w-full flex items-center justify-between px-4 py-3 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                <span>Routine runs ({routine.length})</span>
                <span className="text-xs">{showRoutine ? 'Hide' : 'Show'}</span>
              </button>
              {showRoutine && (
                <TodayRunsCard
                  runs={routine}
                  isLoading={false}
                  compact
                  maxRows={20}
                  section="routine"
                />
              )}
            </div>
          )}
        </div>
        <div className="space-y-4">
          <TodayErrorsCard data={errors} isLoading={errorsLoading} />
          <NorthStarCard />
          <NoiseLeaderboardCard />
          <FocusModeCard />
        </div>
      </div>
    </div>
  )
}
