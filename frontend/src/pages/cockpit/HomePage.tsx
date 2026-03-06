import { useState } from 'react'
import TodayRunsCard from '@/components/cockpit/today/TodayRunsCard'
import TodayErrorsCard from '@/components/cockpit/today/TodayErrorsCard'
import NorthStarCard from '@/components/cockpit/today/NorthStarCard'
import NoiseLeaderboardCard from '@/components/cockpit/today/NoiseLeaderboardCard'
import FocusModeCard from '@/components/cockpit/today/FocusModeCard'
import { useRuns, useErrorSummary } from '@/hooks/cockpitQueries'
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
  if (r.status === 'failed') return 'attention'

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

export default function CockpitHomePage() {
  const { data: runs = [], isLoading: runsLoading } = useRuns({ hours: 24, limit: 50, enrich: 1 })
  const { data: errors, isLoading: errorsLoading } = useErrorSummary(24)
  const [showRoutine, setShowRoutine] = useState(false)

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
