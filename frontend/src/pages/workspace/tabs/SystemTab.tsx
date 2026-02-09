/**
 * Session 971b: System Tab — merged view of Infrastructure + Orchestration + Triggers.
 *
 * B1: Adapter delegating to original tab components (double nav).
 * B3: Now passes controlledSubTab to suppress inner nav — single unified nav.
 */

import { useState } from 'react'
import {
  Heart,
  Link2,
  Server,
  Cpu,
  Activity,
  Workflow,
  Brain,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { InfrastructureTab } from './InfrastructureTab'
import { OrchestrationTab } from './OrchestrationTab'
import { TriggersTab } from './TriggersTab'
import type { SystemSubTab } from '../types'

interface SystemTabProps {
  initialSubTab?: string
  showSuccess?: (msg: string) => void
  showError?: (msg: string) => void
}

// Which merged sub-tab should render which original component
type DelegateView = 'infra' | 'orch' | 'triggers'

const subTabs: Array<{
  id: SystemSubTab
  label: string
  icon: typeof Heart
  delegate: DelegateView
}> = [
  // From Infrastructure
  { id: 'health', label: 'Health', icon: Heart, delegate: 'infra' },
  { id: 'services', label: 'Services', icon: Server, delegate: 'infra' },
  { id: 'llm', label: 'LLM', icon: Cpu, delegate: 'infra' },
  { id: 'integration', label: 'Integration', icon: Link2, delegate: 'infra' },
  // From Orchestration
  { id: 'monitor', label: 'Monitor', icon: Activity, delegate: 'orch' },
  { id: 'workflows', label: 'Workflows', icon: Workflow, delegate: 'orch' },
  { id: 'hivemind', label: 'HiveMind', icon: Brain, delegate: 'orch' },
  // From Triggers
  { id: 'triggers', label: 'Triggers', icon: Zap, delegate: 'triggers' },
]

export function SystemTab({ initialSubTab, showSuccess, showError }: SystemTabProps) {
  const initial = (initialSubTab && subTabs.some(t => t.id === initialSubTab)
    ? initialSubTab
    : 'health') as SystemSubTab

  const [activeSubTab, setActiveSubTab] = useState<SystemSubTab>(initial)

  const current = subTabs.find(t => t.id === activeSubTab)
  const delegate = current?.delegate ?? 'infra'

  return (
    <div className="space-y-4">
      {/* Unified sub-tab nav */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Session 971b B3: controlledSubTab suppresses inner nav — single nav level */}
      {delegate === 'infra' && <InfrastructureTab controlledSubTab={activeSubTab} />}
      {delegate === 'orch' && <OrchestrationTab controlledSubTab={activeSubTab} />}
      {delegate === 'triggers' && (
        <TriggersTab showSuccess={showSuccess} showError={showError} />
      )}
    </div>
  )
}
