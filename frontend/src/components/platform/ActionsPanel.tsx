/**
 * Session 824: Actions Panel
 *
 * Manual action buttons for triggering system operations from the UI.
 * Replaces CLI commands with clickable buttons.
 */

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bug,
  Wrench,
  Bot,
  FileSearch,
  Loader2,
  CheckCircle,
  XCircle,
  Play,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

interface ActionResult {
  success: boolean
  message: string
  error?: string
}

// Session 830: Use api instance to include auth token
async function runAction(endpoint: string, body?: object): Promise<ActionResult> {
  // Strip /api prefix if present since api instance adds it
  const path = endpoint.replace(/^\/api/, '')
  const response = await api.post(path, body)
  return response.data
}

interface ActionButtonProps {
  icon: React.ElementType
  label: string
  description: string
  endpoint: string
  body?: object
  color: string
  onResult?: (result: ActionResult) => void
}

function ActionButton({
  icon: Icon,
  label,
  description,
  endpoint,
  body,
  color,
  onResult,
}: ActionButtonProps) {
  const queryClient = useQueryClient()
  const [lastResult, setLastResult] = useState<ActionResult | null>(null)

  const mutation = useMutation({
    mutationFn: () => runAction(endpoint, body),
    onSuccess: (result) => {
      setLastResult(result)
      onResult?.(result)
      // Refresh live metrics after any action
      queryClient.invalidateQueries({ queryKey: ['live-metrics'] })
    },
    onError: () => {
      setLastResult({ success: false, message: 'Request failed' })
    },
  })

  return (
    <div className="card hover:bg-gray-800/80 transition-colors">
      <div className="flex items-start gap-4">
        <div
          className="h-12 w-12 rounded-lg flex items-center justify-center shrink-0"
          style={{ backgroundColor: `${color}20` }}
        >
          <Icon size={24} style={{ color }} />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-white mb-1">{label}</h4>
          <p className="text-xs text-gray-400 mb-3">{description}</p>

          {lastResult && (
            <div
              className={cn(
                'flex items-center gap-2 text-xs mb-3 p-2 rounded',
                lastResult.success
                  ? 'bg-accent-green/10 text-accent-green'
                  : 'bg-accent-red/10 text-accent-red'
              )}
            >
              {lastResult.success ? <CheckCircle size={14} /> : <XCircle size={14} />}
              <span className="truncate">{lastResult.message}</span>
            </div>
          )}

          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
              'bg-gray-700 hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {mutation.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Play size={14} />
            )}
            {mutation.isPending ? 'Running...' : 'Run'}
          </button>
        </div>
      </div>
    </div>
  )
}

export function ActionsPanel() {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Wrench className="text-accent-cyan" size={18} />
        <h3 className="text-md font-semibold uppercase">Manual Actions</h3>
      </div>

      <p className="text-sm text-gray-400">
        Trigger system operations manually. These are the same operations that run automatically
        via the self-execution engine when conditions are met.
      </p>

      {/* Action Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ActionButton
          icon={Bug}
          label="Run Spider Network"
          description="Collect fresh data from all configured spiders (news, financial, tech, etc.)"
          endpoint="/api/platform/actions/run-spiders/"
          color="#f59e0b"
        />

        <ActionButton
          icon={Wrench}
          label="Run Remediation Cycle"
          description="Execute autonomous remediation on open findings (default: 5 findings)"
          endpoint="/api/platform/actions/run-remediation/"
          body={{ limit: 5 }}
          color="#8b5cf6"
        />

        <ActionButton
          icon={Bot}
          label="Agent Health Check"
          description="Verify all agent categories are healthy and loadable"
          endpoint="/api/platform/actions/agent-health-check/"
          color="#22c55e"
        />

        <ActionButton
          icon={FileSearch}
          label="Run Self-Audit"
          description="Generate a comprehensive system audit with live data (saved to docs/audits/)"
          endpoint="/api/platform/actions/run-self-audit/"
          color="#06b6d4"
        />
      </div>

      {/* Note */}
      <div className="text-xs text-gray-500 bg-gray-800/50 p-3 rounded-lg">
        <strong>Note:</strong> Actions run asynchronously via Celery. Results appear in the Recent
        Activity feed and system logs. The self-execution engine also runs these actions
        automatically when trigger conditions are met.
      </div>
    </div>
  )
}
