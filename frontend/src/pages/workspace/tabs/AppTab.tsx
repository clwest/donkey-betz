// Embedded App Tab — renders standalone apps inside workspace as an iframe
// Phase 1 integration: each app workspace gets a "Launch App" tab

import { useState } from 'react'
import { ExternalLink, Maximize2, Minimize2, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useWorkspaceStore } from '@/stores/workspaceStore'

// Map workspace names to their app URLs (dev = localhost, prod = deployed)
const APP_URLS: Record<string, { dev: string; prod?: string; port: number; description: string }> = {
  'SellerPilot': {
    dev: 'http://localhost:5177',
    port: 5177,
    description: 'E-commerce listing optimizer — AI-powered product descriptions, pricing, and SEO',
  },
  'MentorForge': {
    dev: 'http://localhost:5174',
    port: 5174,
    description: 'AI mentoring platform with 8 expert personas and tiered learning paths',
  },
  'SignalStudio': {
    dev: 'http://localhost:5173',
    port: 5173,
    description: 'Real-time signal intelligence — market trends, opportunities, and alerts',
  },
  'Contract Concierge': {
    dev: 'http://localhost:5175',
    port: 5175,
    description: 'AI-assisted contract drafting, review, and negotiation support',
  },
  'PitchDeckForge': {
    dev: 'http://localhost:5176',
    port: 5176,
    description: 'Generate investor-ready pitch decks with AI-crafted narratives',
  },
  'DealFlowTracker': {
    dev: 'http://localhost:5178',
    port: 5178,
    description: 'Deal pipeline CRM — track prospects, deals, and revenue',
  },
  'ScoutPlays': {
    dev: 'http://localhost:5179',
    port: 5179,
    description: 'Player scouting reports and analysis powered by sports data',
  },
  'ComplianceSentinel': {
    dev: 'http://localhost:5180',
    port: 5180,
    description: 'Regulatory compliance monitoring — track policy changes and alerts',
  },
}

export function getAppUrl(workspaceName: string): string | null {
  const config = APP_URLS[workspaceName]
  if (!config) return null
  return config.prod || config.dev
}

export function hasApp(workspaceName: string): boolean {
  return workspaceName in APP_URLS
}

export default function AppTab() {
  const activeWorkspace = useWorkspaceStore(s => s.activeWorkspace)
  const [expanded, setExpanded] = useState(false)
  const [iframeKey, setIframeKey] = useState(0)

  if (!activeWorkspace) return null

  const config = APP_URLS[activeWorkspace.name]
  if (!config) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No app configured for this workspace
      </div>
    )
  }

  const appUrl = config.prod || config.dev

  return (
    <div className={cn(
      'flex flex-col',
      expanded ? 'fixed inset-0 z-50 bg-dark-bg' : 'h-[calc(100vh-12rem)]'
    )}>
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-dark-card border-b border-dark-border">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-white">{activeWorkspace.name}</span>
          <span className="text-xs text-gray-500">{config.description}</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIframeKey(k => k + 1)}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white transition"
            title="Refresh app"
          >
            <RefreshCw size={14} />
          </button>
          <a
            href={appUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white transition"
            title="Open in new tab"
          >
            <ExternalLink size={14} />
          </a>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white transition"
            title={expanded ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {expanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
        </div>
      </div>

      {/* App iframe */}
      <iframe
        key={iframeKey}
        src={appUrl}
        className="flex-1 w-full border-0"
        title={activeWorkspace.name}
        allow="clipboard-write"
      />
    </div>
  )
}
