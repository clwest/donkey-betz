import { useNavigate } from 'react-router-dom'
import { RECIPES } from '@/components/cockpit/create/recipes'
import { PlusCircle, Clock, Tag } from 'lucide-react'

export default function CockpitCreateHubPage() {
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <PlusCircle size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Create</h1>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {RECIPES.map((recipe) => (
          <div
            key={recipe.id}
            className="card flex flex-col gap-3 p-5 hover:border-primary-500/40 cursor-pointer transition-colors"
            onClick={() => navigate(`/cockpit/create/${recipe.id}`)}
          >
            <h2 className="text-lg font-semibold text-gray-200">{recipe.title}</h2>
            <p className="text-sm text-gray-400 flex-1">{recipe.description}</p>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Clock size={12} />
                {recipe.eta}
              </div>
              <div className="flex gap-1.5">
                {recipe.tags.map((tag) => (
                  <span key={tag} className="rounded-full bg-dark-border px-2 py-0.5 text-[10px] text-gray-500">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
