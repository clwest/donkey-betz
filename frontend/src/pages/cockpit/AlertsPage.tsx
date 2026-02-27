import { useState } from 'react'
import { useAlerts, useCreateIncidentNote } from '@/hooks/cockpitQueries'
import { getRunbook } from '@/lib/cockpitApi'
import StatusPill from '@/components/cockpit/shared/StatusPill'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import type { Tone } from '@/components/cockpit/shared/StatusPill'
import type { AlertItem } from '@/types/cockpit'
import { Bell, AlertTriangle, Bot, HeartPulse, ShieldCheck, ChevronDown, ChevronUp, FileText } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

const SEVERITY_TONE: Record<string, Tone> = {
  critical: 'red',
  high: 'red',
  medium: 'amber',
  low: 'gray',
}

const KIND_CONFIG: Record<string, { icon: typeof AlertTriangle; label: string; route?: string }> = {
  error_spike: { icon: AlertTriangle, label: 'Error Spike', route: '/cockpit/errors' },
  agent_failure: { icon: Bot, label: 'Agent Failure', route: '/cockpit/ops' },
  health: { icon: HeartPulse, label: 'Health', route: '/cockpit/ops' },
  approvals: { icon: ShieldCheck, label: 'Approvals', route: '/cockpit/approvals' },
}

function AlertCard({ alert }: { alert: AlertItem }) {
  const navigate = useNavigate()
  const config = KIND_CONFIG[alert.kind] ?? { icon: Bell, label: alert.kind }
  const Icon = config.icon
  const [showRunbook, setShowRunbook] = useState(false)
  const [runbookSteps, setRunbookSteps] = useState<string[] | null>(null)
  const [loadingRunbook, setLoadingRunbook] = useState(false)
  const incidentMutation = useCreateIncidentNote()

  async function toggleRunbook() {
    if (showRunbook) {
      setShowRunbook(false)
      return
    }
    if (!runbookSteps) {
      setLoadingRunbook(true)
      try {
        const rb = await getRunbook(alert.kind)
        setRunbookSteps(rb.steps)
      } catch {
        setRunbookSteps(['Failed to load runbook.'])
      }
      setLoadingRunbook(false)
    }
    setShowRunbook(true)
  }

  return (
    <div
      className={`card p-4 border-l-4 ${
        alert.severity === 'critical' || alert.severity === 'high'
          ? 'border-l-red-500'
          : alert.severity === 'medium'
          ? 'border-l-amber-500'
          : 'border-l-gray-600'
      }`}
    >
      <div
        className={`flex items-start gap-3 ${config.route ? 'cursor-pointer' : ''}`}
        onClick={() => config.route && navigate(config.route)}
      >
        <Icon size={18} className={
          alert.severity === 'high' || alert.severity === 'critical'
            ? 'text-red-400 mt-0.5'
            : alert.severity === 'medium'
            ? 'text-amber-400 mt-0.5'
            : 'text-gray-500 mt-0.5'
        } />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <StatusPill label={alert.severity} tone={SEVERITY_TONE[alert.severity] ?? 'gray'} />
            <span className="text-xs text-gray-500">{config.label}</span>
          </div>
          <h3 className="text-sm font-medium text-gray-200">{alert.title}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{alert.detail}</p>
        </div>
      </div>

      {/* Action bar */}
      <div className="flex items-center gap-2 mt-3 pt-2 border-t border-dark-border/50">
        <button
          onClick={(e) => { e.stopPropagation(); toggleRunbook() }}
          className="text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1 transition-colors"
        >
          {showRunbook ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
          {loadingRunbook ? 'Loading…' : 'Runbook'}
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            incidentMutation.mutate({
              title: alert.title,
              detail: alert.detail,
              source_type: alert.kind,
              source_id: alert.id,
            })
          }}
          disabled={incidentMutation.isPending}
          className="text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1 transition-colors"
        >
          <FileText size={12} />
          {incidentMutation.isPending ? 'Creating…' : incidentMutation.isSuccess ? 'Created' : 'Incident Note'}
        </button>
      </div>

      {/* Runbook steps */}
      {showRunbook && runbookSteps && (
        <ol className="mt-2 ml-6 space-y-1 list-decimal text-xs text-gray-400">
          {runbookSteps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      )}
    </div>
  )
}

export default function CockpitAlertsPage() {
  const { data, isLoading } = useAlerts()

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Alerts</h1>
        <div className="card p-6"><SkeletonRows count={5} /></div>
      </div>
    )
  }

  const highCount = data?.items.filter(a => a.severity === 'critical' || a.severity === 'high').length ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Bell size={20} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Alerts</h1>
        {data && data.total > 0 && (
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
            highCount > 0 ? 'bg-red-600/20 text-red-400' : 'bg-primary-600/20 text-primary-400'
          }`}>
            {data.total}
          </span>
        )}
      </div>

      {!data || data.items.length === 0 ? (
        <div className="card p-8 text-center text-gray-500">
          No active alerts. All systems quiet.
        </div>
      ) : (
        <div className="space-y-3">
          {data.items.map((alert) => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      )}
    </div>
  )
}
