import { useState, useEffect, useCallback } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import CockpitSidebar from './CockpitSidebar'
import CockpitTopBar from './CockpitTopBar'
import CommandPalette from './CommandPalette'
import GlobalPADock from '@/components/GlobalPADock'
import { useFocusMode } from '@/hooks/useFocusMode'

const PAGE_TITLES: Record<string, string> = {
  '/cockpit': 'Today',
  '/cockpit/inbox': 'Inbox',
  '/cockpit/create': 'Create',
  '/cockpit/runs': 'Runs',
  '/cockpit/library': 'Library',
  '/cockpit/errors': 'Errors',
  '/cockpit/ops': 'Ops',
  '/cockpit/obs': 'OBS Studio',
}

export default function CockpitLayout() {
  const { focusMode, toggleFocusMode } = useFocusMode()
  const [paletteOpen, setPaletteOpen] = useState(false)
  const location = useLocation()

  // Derive page title from path
  const title = PAGE_TITLES[location.pathname] ?? 'Cockpit'

  // Global Cmd+K / Ctrl+K listener
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setPaletteOpen((prev) => !prev)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const closePalette = useCallback(() => setPaletteOpen(false), [])
  const openPalette = useCallback(() => setPaletteOpen(true), [])

  return (
    <div className="flex h-screen overflow-hidden">
      <CockpitSidebar focusMode={focusMode} onToggleFocusMode={toggleFocusMode} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <CockpitTopBar
          title={title}
          focusMode={focusMode}
          onCommandPalette={openPalette}
        />
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>

      {!focusMode && <GlobalPADock />}

      <CommandPalette
        open={paletteOpen}
        onClose={closePalette}
        onToggleFocusMode={toggleFocusMode}
      />
    </div>
  )
}
