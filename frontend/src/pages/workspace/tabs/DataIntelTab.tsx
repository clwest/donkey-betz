/**
 * Session 971b: Data & Intel Tab — merged view of DataSources + Intelligence.
 *
 * Adapter that delegates to existing tab components via a unified sub-tab nav.
 * No content was moved — the original components render as-is.
 */

import { useState } from 'react'
import {
  Globe,
  Rss,
  BookOpen,
  Brain,
  Shield,
  Users,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { DataSourcesTab } from './DataSourcesTab'
import { IntelligenceTab } from './IntelligenceTab'
import type { DataIntelSubTab } from '../types'

interface DataIntelTabProps {
  initialSubTab?: string
}

type DelegateView = 'data' | 'intel'

const subTabs: Array<{
  id: DataIntelSubTab
  label: string
  icon: typeof Globe
  delegate: DelegateView
}> = [
  // From DataSources
  { id: 'spiders', label: 'Spiders', icon: Globe, delegate: 'data' },
  { id: 'feed', label: 'Feed', icon: Rss, delegate: 'data' },
  { id: 'learning', label: 'Learning', icon: BookOpen, delegate: 'data' },
  // From Intelligence
  { id: 'reasoning', label: 'Reasoning', icon: Brain, delegate: 'intel' },
  { id: 'safety', label: 'Safety', icon: Shield, delegate: 'intel' },
  { id: 'collective', label: 'Collective', icon: Users, delegate: 'intel' },
]

export function DataIntelTab({ initialSubTab }: DataIntelTabProps) {
  const initial = (initialSubTab && subTabs.some(t => t.id === initialSubTab)
    ? initialSubTab
    : 'spiders') as DataIntelSubTab

  const [activeSubTab, setActiveSubTab] = useState<DataIntelSubTab>(initial)

  const current = subTabs.find(t => t.id === activeSubTab)
  const delegate = current?.delegate ?? 'data'

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

      {/* Delegate to original components */}
      {delegate === 'data' && <DataSourcesTab />}
      {delegate === 'intel' && <IntelligenceTab />}
    </div>
  )
}
