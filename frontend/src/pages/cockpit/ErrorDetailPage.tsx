import { useParams } from 'react-router-dom'

export default function CockpitErrorDetailPage() {
  const { signatureId } = useParams<{ signatureId: string }>()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Error: {signatureId?.slice(0, 12)}</h1>
      <div className="card p-6 text-center text-gray-400">
        Error occurrences, stack traces, and affected agents.
        <br />
        <span className="text-sm text-gray-500">Coming soon</span>
      </div>
    </div>
  )
}
