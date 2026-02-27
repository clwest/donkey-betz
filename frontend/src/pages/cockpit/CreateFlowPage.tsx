import { useParams } from 'react-router-dom'

export default function CockpitCreateFlowPage() {
  const { recipeId } = useParams<{ recipeId: string }>()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Create: {recipeId}</h1>
      <div className="card p-6 text-center text-gray-400">
        Fill in the details and generate.
        <br />
        <span className="text-sm text-gray-500">Coming soon</span>
      </div>
    </div>
  )
}
