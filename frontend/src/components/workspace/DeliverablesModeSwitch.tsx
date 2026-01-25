/**
 * Session 819: Deliverables Marketplace - Mode Switcher
 *
 * Allows switching between Timeline (operations), Deliverables, and Jobs views.
 */

import React from 'react'
import { History, Package, Briefcase } from 'lucide-react'
import { cn } from '@/lib/cn'

export type DeliverableViewMode = 'timeline' | 'deliverables' | 'jobs'

interface DeliverablesModeSwitch {
  mode: DeliverableViewMode
  onModeChange: (mode: DeliverableViewMode) => void
  counts?: {
    timeline?: number
    deliverables?: number
    jobs?: number
  }
}

export function DeliverablesModeSwitch({
  mode,
  onModeChange,
  counts = {}
}: DeliverablesModeSwitch) {
  const modes: Array<{
    value: DeliverableViewMode
    label: string
    icon: React.ElementType
    description: string
  }> = [
    {
      value: 'timeline',
      label: 'Timeline',
      icon: History,
      description: 'Developer event log'
    },
    {
      value: 'deliverables',
      label: 'Deliverables',
      icon: Package,
      description: 'AI output catalog'
    },
    {
      value: 'jobs',
      label: 'Jobs',
      icon: Briefcase,
      description: 'Execution tracking'
    }
  ]

  return (
    <div className="flex items-center gap-1 bg-zinc-800/50 rounded-lg p-1">
      {modes.map(({ value, label, icon: Icon }) => {
        const count = counts[value]
        const isActive = mode === value

        return (
          <button
            key={value}
            onClick={() => onModeChange(value)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
              isActive
                ? 'bg-zinc-700 text-zinc-100'
                : 'text-zinc-400 hover:text-zinc-300 hover:bg-zinc-700/50'
            )}
          >
            <Icon className="w-4 h-4" />
            <span>{label}</span>
            {count !== undefined && (
              <span
                className={cn(
                  'px-1.5 py-0.5 text-xs rounded-full',
                  isActive
                    ? 'bg-zinc-600 text-zinc-200'
                    : 'bg-zinc-700 text-zinc-400'
                )}
              >
                {count.toLocaleString()}
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

export default DeliverablesModeSwitch
