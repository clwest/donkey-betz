import TodayRunsCard from '@/components/cockpit/today/TodayRunsCard'
import TodayErrorsCard from '@/components/cockpit/today/TodayErrorsCard'
import { useRuns, useErrorSummary } from '@/hooks/cockpitQueries'

export default function CockpitHomePage() {
  const { data: runs = [], isLoading: runsLoading } = useRuns({ hours: 24, limit: 5 })
  const { data: errors, isLoading: errorsLoading } = useErrorSummary(24)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Today</h1>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TodayRunsCard runs={runs} isLoading={runsLoading} />
        <TodayErrorsCard data={errors} isLoading={errorsLoading} />
      </div>
    </div>
  )
}
