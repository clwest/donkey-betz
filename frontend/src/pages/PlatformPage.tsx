// Session 1035: Platform Dashboard — system-wide tabs split from Workspace
// Contains the 7 non-workspace tabs: Command, Initiatives, Boardroom, Content, System, Data & Intel, Knowledge, Learn

import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Target,
  GitBranch,
  Gavel,
  Palette,
  Server,
  Database,
  BookOpen,
  GraduationCap,
  FlaskConical,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { CompactBreadcrumb } from '@/components/Breadcrumb'
import { useWorkspaceTabTracking } from '@/hooks/usePageTracking'

import {
  CommandTab,
  InitiativesTab,
  BoardroomTab,
  ContentStudioTab,
  SystemTab,
  DataIntelTab,
  KnowledgeTab,
  LearningJourneyTab,
  Stage3EvaluationTab,
} from './workspace/tabs'
import type { PlatformTab } from './workspace/types'
import { normalizePlatformTab, legacyTabToSubTab } from './workspace/types'

const tabGroups = [
  {
    label: 'Core',
    tabs: [
      { id: 'command' as PlatformTab, label: 'Command', icon: Target },
      { id: 'initiatives' as PlatformTab, label: 'Initiatives', icon: GitBranch },
      { id: 'evaluation' as PlatformTab, label: 'Evaluation', icon: FlaskConical },
      { id: 'boardroom' as PlatformTab, label: 'Boardroom', icon: Gavel },
    ],
  },
  {
    label: 'Content',
    tabs: [
      { id: 'content' as PlatformTab, label: 'Content', icon: Palette },
    ],
  },
  {
    label: 'System',
    tabs: [
      { id: 'system' as PlatformTab, label: 'System', icon: Server },
    ],
  },
  {
    label: 'Data',
    tabs: [
      { id: 'dataintel' as PlatformTab, label: 'Data & Intel', icon: Database },
      { id: 'knowledge' as PlatformTab, label: 'Knowledge', icon: BookOpen },
      { id: 'learning' as PlatformTab, label: 'Learn', icon: GraduationCap },
    ],
  },
]

const allTabs = tabGroups.flatMap(g => g.tabs)

export default function PlatformPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const rawUrlTab = searchParams.get('tab') || ''

  const validTabs = allTabs.map(t => t.id)
  const normalizedTab = rawUrlTab ? normalizePlatformTab(rawUrlTab) : 'command'
  const initialTab = validTabs.includes(normalizedTab) ? normalizedTab : 'command'

  const [legacySubTab, setLegacySubTab] = useState<string | undefined>(
    () => legacyTabToSubTab(rawUrlTab)
  )
  const [activeTab, setActiveTab] = useState<PlatformTab>(initialTab)

  useWorkspaceTabTracking(activeTab)

  const handleTabChange = (tab: PlatformTab) => {
    setActiveTab(tab)
    setLegacySubTab(undefined)
    setSearchParams({ tab }, { replace: true })
  }

  useEffect(() => {
    if (rawUrlTab) {
      const normalized = normalizePlatformTab(rawUrlTab)
      if (validTabs.includes(normalized) && normalized !== activeTab) {
        setActiveTab(normalized)
        setLegacySubTab(legacyTabToSubTab(rawUrlTab))
      }
      if (rawUrlTab !== normalized) {
        setSearchParams({ tab: normalized }, { replace: true })
      }
    }
  }, [rawUrlTab])

  // Toast state for child tabs that need it
  const [actionResult, setActionResult] = useState<{ type: 'success' | 'error'; message: string } | null>(null)
  const showSuccess = (message: string) => setActionResult({ type: 'success', message })
  const showError = (message: string) => setActionResult({ type: 'error', message })

  useEffect(() => {
    if (actionResult) {
      const timer = setTimeout(() => setActionResult(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [actionResult])

  // Track expanded activity IDs for CommandTab
  const [expandedActivityIds, setExpandedActivityIds] = useState<Set<string>>(new Set())
  const toggleActivityExpanded = (id: string) => {
    setExpandedActivityIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <CompactBreadcrumb currentPage="Platform" className="mb-2" />
        <h1 className="text-2xl font-bold">Platform</h1>
        <p className="text-sm text-gray-400 mt-1">System-wide dashboard — agents, content, data, infrastructure</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex items-center gap-1 border-b border-dark-border pb-2 flex-wrap">
        {tabGroups.map((group, gi) => (
          <div key={group.label} className="flex items-center">
            {gi > 0 && (
              <div className="w-px h-6 bg-dark-border mx-1.5 flex-shrink-0" />
            )}
            <div className="flex items-center gap-0.5">
              {group.tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={cn(
                    'flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors whitespace-nowrap',
                    activeTab === tab.id
                      ? 'bg-primary-500/20 text-primary-400'
                      : 'text-gray-500 hover:text-white hover:bg-dark-border/50'
                  )}
                >
                  <tab.icon size={14} />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'command' && (
        <CommandTab
          setActiveTab={(tab: string) => handleTabChange(tab as PlatformTab)}
          expandedActivityIds={expandedActivityIds}
          toggleActivityExpanded={toggleActivityExpanded}
        />
      )}

      {activeTab === 'initiatives' && <InitiativesTab />}

      {activeTab === 'evaluation' && <Stage3EvaluationTab />}

      {activeTab === 'boardroom' && <BoardroomTab />}

      {activeTab === 'content' && (
        <ContentStudioTab
          initialSubTab={legacySubTab}
        />
      )}

      {activeTab === 'system' && (
        <SystemTab
          initialSubTab={legacySubTab}
          showSuccess={showSuccess}
          showError={showError}
        />
      )}

      {activeTab === 'dataintel' && (
        <DataIntelTab initialSubTab={legacySubTab} />
      )}

      {activeTab === 'knowledge' && <KnowledgeTab />}

      {activeTab === 'learning' && <LearningJourneyTab />}

      {/* Toast */}
      {actionResult && (
        <div className={cn(
          'fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg text-sm font-medium',
          actionResult.type === 'success'
            ? 'bg-accent-green/20 text-accent-green border border-accent-green/30'
            : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
        )}>
          {actionResult.message}
        </div>
      )}
    </div>
  )
}
