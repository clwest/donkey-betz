/**
 * Projects Page — card grid showing all project workspaces.
 * Click a card → navigate to the Project Hub detail page.
 */

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Folder, FileText, Lightbulb, MessageSquare, Clock, Loader2 } from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

interface Project {
  id: string
  name: string
  description: string
  deliverable_count: number
  initiative_count: number
  latest_activity: string | null
  created_at: string | null
}

function formatRelativeTime(iso: string | null): string {
  if (!iso) return 'No activity'
  const diff = Date.now() - new Date(iso).getTime()
  const hours = Math.floor(diff / 3600000)
  if (hours < 1) return 'Just now'
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export default function ProjectsPage() {
  const navigate = useNavigate()

  const { data, isLoading, error } = useQuery({
    queryKey: ['projects-list'],
    queryFn: () => api.get('/projects/').then(r => r.data),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary-400" />
      </div>
    )
  }

  if (error) return <ErrorState error={error} />

  const projects: Project[] = data?.projects || []

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Projects</h1>
          <p className="text-sm text-gray-400 mt-1">All your workspaces with deliverables, initiatives, and conversations</p>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <Folder size={48} className="mx-auto mb-4 opacity-40" />
          <p className="text-lg">No projects yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <button
              key={project.id}
              onClick={() => navigate(`/projects/${project.id}`)}
              className={cn(
                'text-left p-5 rounded-xl border border-dark-border bg-dark-card',
                'hover:border-primary-500/40 hover:bg-dark-card/80 transition-all',
                'group cursor-pointer'
              )}
            >
              {/* Header */}
              <div className="flex items-start gap-3 mb-3">
                <div className="h-10 w-10 rounded-lg bg-primary-600/20 flex items-center justify-center flex-shrink-0 group-hover:bg-primary-600/30 transition-colors">
                  <Folder size={20} className="text-primary-400" />
                </div>
                <div className="min-w-0">
                  <h3 className="font-semibold text-white truncate group-hover:text-primary-300 transition-colors">
                    {project.name}
                  </h3>
                  {project.description && (
                    <p className="text-xs text-gray-500 truncate mt-0.5">{project.description}</p>
                  )}
                </div>
              </div>

              {/* Stats row */}
              <div className="flex items-center gap-4 text-xs text-gray-400">
                <span className="flex items-center gap-1">
                  <FileText size={12} />
                  {project.deliverable_count} deliverable{project.deliverable_count !== 1 ? 's' : ''}
                </span>
                <span className="flex items-center gap-1">
                  <Lightbulb size={12} />
                  {project.initiative_count} initiative{project.initiative_count !== 1 ? 's' : ''}
                </span>
              </div>

              {/* Activity */}
              <div className="flex items-center gap-1 mt-3 text-[11px] text-gray-500">
                <Clock size={10} />
                {formatRelativeTime(project.latest_activity)}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
