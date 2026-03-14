// Demo Home — Platform overview + BPaaS/Preview entrypoints
// Single-page dashboard showing platform health, revenue, and primary CTAs

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Rocket, Activity, DollarSign, Server, Clock, GitBranch,
  ArrowRight, Zap, Target, BarChart3, Globe, Layers,
  CheckCircle2, AlertTriangle, Loader2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { statusApi, revenueApi, previewApi } from '@/lib/api'

export default function DemoHomePage() {
  const navigate = useNavigate()

  const { data: status, isLoading: statusLoading } = useQuery({
    queryKey: ['status-overview'],
    queryFn: () => statusApi.overview().then(r => r.data),
    refetchInterval: 30000,
  })

  const { data: revenue } = useQuery({
    queryKey: ['revenue-summary'],
    queryFn: () => revenueApi.summary(30).then(r => r.data),
  })

  const { data: projects } = useQuery({
    queryKey: ['preview-projects-home'],
    queryFn: () => previewApi.projects().then(r => r.data),
  })

  const projectList = projects?.results || projects || []

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="animate-spin text-primary" size={32} />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Layers size={24} /> Platform Overview
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Real-time platform health, revenue, and project management
        </p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatusCard
          icon={GitBranch}
          label="Deploy"
          value={status?.deploy?.sha || 'dev'}
          sub={status?.deploy?.uptime || ''}
          color="text-blue-400"
        />
        <StatusCard
          icon={Activity}
          label="Tasks (24h)"
          value={
            status?.celery?.tasks_24h
              ? String(Object.values(status.celery.tasks_24h as Record<string, number>).reduce((a: number, b: number) => a + b, 0))
              : '0'
          }
          sub={`${status?.celery?.beat_schedules || 0} beat schedules`}
          color="text-green-400"
        />
        <StatusCard
          icon={DollarSign}
          label="Revenue"
          value={`$${(revenue?.total_revenue || status?.revenue?.total_confirmed || 0).toLocaleString()}`}
          sub={`${revenue?.total_count || 0} entries`}
          color="text-yellow-400"
        />
        <StatusCard
          icon={Rocket}
          label="Projects"
          value={String(projectList.length || status?.preview_system?.projects || 0)}
          sub={`${status?.preview_system?.active_environments || 0} active envs`}
          color="text-purple-400"
        />
      </div>

      {/* Primary Actions */}
      <div className="grid md:grid-cols-3 gap-4">
        <ActionCard
          icon={Rocket}
          title="Create BPaaS Project"
          description="Launch the Build Packet wizard to create a new client project with repos, preview env, and magic link."
          buttonLabel="Build Packet"
          onClick={() => navigate('/workspace?tab=launchpad')}
          color="bg-green-600 hover:bg-green-700"
        />
        <ActionCard
          icon={Globe}
          title="View Projects & Previews"
          description={`${projectList.length} project${projectList.length !== 1 ? 's' : ''} in Launchpad. Manage preview environments and magic links.`}
          buttonLabel="Open Launchpad"
          onClick={() => navigate('/workspace?tab=launchpad')}
          color="bg-purple-600 hover:bg-purple-700"
        />
        <ActionCard
          icon={Target}
          title="Initiatives"
          description="Track strategic initiatives: Content Distribution, Revenue Fix, and more."
          buttonLabel="View Initiatives"
          onClick={() => navigate('/platform?tab=initiatives')}
          color="bg-blue-600 hover:bg-blue-700"
        />
      </div>

      {/* Revenue Breakdown */}
      {revenue?.by_source && (
        <div className="border border-dark-border rounded-xl p-5">
          <h2 className="font-semibold flex items-center gap-2 mb-4">
            <BarChart3 size={18} /> Revenue by Source (30 days)
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {(revenue.by_source as Array<{ source_type: string; total: number }>).map((src) => (
              <div key={src.source_type} className="bg-dark-bg rounded-lg p-3">
                <p className="text-xs text-muted-foreground capitalize">{src.source_type}</p>
                <p className="text-lg font-bold">${Number(src.total || 0).toLocaleString()}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Projects */}
      {projectList.length > 0 && (
        <div className="border border-dark-border rounded-xl p-5">
          <h2 className="font-semibold flex items-center gap-2 mb-4">
            <Rocket size={18} /> BPaaS Projects
          </h2>
          <div className="space-y-2">
            {projectList.slice(0, 5).map((project: Record<string, unknown>) => (
              <div
                key={project.id as string}
                className="flex items-center justify-between bg-dark-bg rounded-lg p-3 cursor-pointer hover:bg-dark-bg/80"
                onClick={() => navigate('/workspace?tab=launchpad')}
              >
                <div>
                  <p className="font-medium text-sm">{project.name as string}</p>
                  <p className="text-xs text-muted-foreground">
                    {(project.repos as unknown[])?.length || 0} repos &middot; {project.preview_env_count as number || 0} envs
                  </p>
                </div>
                <ArrowRight size={16} className="text-muted-foreground" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Health */}
      <div className="border border-dark-border rounded-xl p-5">
        <h2 className="font-semibold flex items-center gap-2 mb-4">
          <Server size={18} /> System Health
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <HealthItem label="API" status="healthy" />
          <HealthItem label="Database" status="healthy" />
          <HealthItem label="Redis" status="healthy" />
          <HealthItem label="Celery Workers" status="healthy" detail={`${status?.celery?.beat_schedules || 0} schedules`} />
          <HealthItem label="Preview System" status={status?.preview_system?.projects > 0 ? 'healthy' : 'idle'} />
          <HealthItem label="Revenue Tracking" status={status?.revenue?.total_confirmed > 0 ? 'healthy' : 'idle'} />
        </div>
      </div>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────

function StatusCard({ icon: Icon, label, value, sub, color }: {
  icon: typeof Activity; label: string; value: string; sub: string; color: string
}) {
  return (
    <div className="border border-dark-border rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        <Icon size={16} className={color} />
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <p className="text-xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground mt-1">{sub}</p>
    </div>
  )
}

function ActionCard({ icon: Icon, title, description, buttonLabel, onClick, color }: {
  icon: typeof Rocket; title: string; description: string; buttonLabel: string;
  onClick: () => void; color: string
}) {
  return (
    <div className="border border-dark-border rounded-xl p-5 flex flex-col justify-between">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Icon size={18} className="text-primary" />
          <h3 className="font-semibold">{title}</h3>
        </div>
        <p className="text-sm text-muted-foreground mb-4">{description}</p>
      </div>
      <button
        onClick={onClick}
        className={cn('flex items-center justify-center gap-2 text-white font-medium py-2.5 rounded-lg text-sm', color)}
      >
        {buttonLabel} <ArrowRight size={14} />
      </button>
    </div>
  )
}

function HealthItem({ label, status, detail }: { label: string; status: string; detail?: string }) {
  return (
    <div className="flex items-center gap-2 bg-dark-bg rounded-lg p-3">
      {status === 'healthy' ? (
        <CheckCircle2 size={16} className="text-green-400" />
      ) : status === 'idle' ? (
        <Clock size={16} className="text-yellow-400" />
      ) : (
        <AlertTriangle size={16} className="text-red-400" />
      )}
      <div>
        <p className="text-sm">{label}</p>
        {detail && <p className="text-xs text-muted-foreground">{detail}</p>}
      </div>
    </div>
  )
}
