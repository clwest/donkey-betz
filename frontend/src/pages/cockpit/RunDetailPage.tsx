import { useParams } from 'react-router-dom'

export default function CockpitRunDetailPage() {
  const { runId } = useParams<{ runId: string }>()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Run: {runId?.slice(0, 8)}</h1>
      <div className="card p-6 text-center text-gray-400">
        Execution details, input, output, and metrics.
        <br />
        <span className="text-sm text-gray-500">Coming soon</span>
      </div>
    </div>
  )
}
