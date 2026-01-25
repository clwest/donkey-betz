// Session 825: Governance Tab
// Extracted from WorkspacePage.tsx for modular architecture
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CheckSquare, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/cn'
import { platformApi } from '@/lib/api'
import { EmergencyControls } from '@/components/platform'

export function GovernanceTab() {
  const queryClient = useQueryClient()

  const { data: governanceData, isLoading: loadingGovernance } = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
  })

  const emergencyHaltMutation = useMutation({
    mutationFn: () => platformApi.emergencyHalt(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
    },
  })

  const skinLockMutation = useMutation({
    mutationFn: (action: 'lock' | 'unlock' | 'toggle') => platformApi.skinLock(action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['platform-governance'] })
    },
  })

  return (
    <div className="space-y-6">
      <EmergencyControls
        emergency={governanceData?.emergency_controls}
        owner={governanceData?.owner}
        isLoading={loadingGovernance}
        onEmergencyHalt={async () => {
          await emergencyHaltMutation.mutateAsync()
        }}
        onSkinLockToggle={async (action: 'lock' | 'unlock' | 'toggle') => {
          await skinLockMutation.mutateAsync(action)
        }}
      />

      {/* Pending Decisions Full List */}
      {governanceData?.pending_decisions && (
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <CheckSquare className="text-primary-400" size={18} />
            <h3 className="text-md font-semibold uppercase">
              Pending Decisions ({governanceData.pending_decisions_count})
            </h3>
          </div>
          {governanceData.pending_decisions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="mx-auto mb-2" size={24} />
              <p>No pending decisions</p>
            </div>
          ) : (
            <div className="space-y-3">
              {governanceData.pending_decisions.map((decision: any) => (
                <div
                  key={decision.id}
                  className="p-4 bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{decision.title}</h4>
                      <p className="text-xs text-gray-400 mt-1">
                        {decision.source_agent || decision.source_type}
                      </p>
                    </div>
                    <span
                      className={cn(
                        'text-xs px-2 py-0.5 rounded',
                        decision.urgency === 'critical'
                          ? 'bg-accent-red/20 text-accent-red'
                          : decision.urgency === 'high'
                          ? 'bg-accent-amber/20 text-accent-amber'
                          : 'bg-gray-700 text-gray-400'
                      )}
                    >
                      {decision.urgency}
                    </span>
                  </div>
                  {decision.description && (
                    <p className="text-sm text-gray-400">{decision.description}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
