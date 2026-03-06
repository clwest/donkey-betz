import { useState } from 'react'
import TodayRunsCard from '@/components/cockpit/today/TodayRunsCard'
import TodayErrorsCard from '@/components/cockpit/today/TodayErrorsCard'
import { useRuns, useErrorSummary } from '@/hooks/cockpitQueries'
import type { ImportanceLevel } from '@/types/cockpit'

const IMPORTANCE_ORDER: ImportanceLevel[] = ['action_required', 'high_impact', 'fyi', 'routine']

export default function CockpitHomePage() {
  const { data: runs = [], isLoading: runsLoading } = useRuns({ hours: 24, limit: 30, enrich: 1 })
  const { data: errors, isLoading: errorsLoading } = useErrorSummary(24)
  const [showRoutine, setShowRoutine] = useState(false)

  // Split runs by importance
  const importantRuns = runs.filter(
    (r) => r.enrichment && r.enrichment.importance.level !== 'routine'
  )
  const routineRuns = runs.filter(
    (r) => !r.enrichment || r.enrichment.importance.level === 'routine'
  )

  // Sort important runs by importance level
  const sortedImportant = [...importantRuns].sort((a, b) => {
    const aLevel = IMPORTANCE_ORDER.indexOf(a.enrichment?.importance.level ?? 'routine')
    const bLevel = IMPORTANCE_ORDER.indexOf(b.enrichment?.importance.level ?? 'routine')
    return aLevel - bLevel
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Today</h1>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <TodayRunsCard
            runs={sortedImportant}
            isLoading={runsLoading}
            title="Runs needing attention"
            emptyMessage="Nothing needs attention"
            maxRows={10}
          />
          {routineRuns.length > 0 && (
            <div className="card">
              <button
                onClick={() => setShowRoutine(!showRoutine)}
                className="w-full flex items-center justify-between px-4 py-3 text-sm text-gray-400 hover:text-gray-200 transition-colors"
              >
                <span>Routine runs ({routineRuns.length})</span>
                <span className="text-xs">{showRoutine ? 'Hide' : 'Show'}</span>
              </button>
              {showRoutine && (
                <TodayRunsCard
                  runs={routineRuns}
                  isLoading={false}
                  compact
                  maxRows={20}
                />
              )}
            </div>
          )}
        </div>
        <TodayErrorsCard data={errors} isLoading={errorsLoading} />
      </div>
    </div>
  )
}
