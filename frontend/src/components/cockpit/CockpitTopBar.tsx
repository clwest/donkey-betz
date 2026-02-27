import { cn } from '@/lib/cn'

interface CockpitTopBarProps {
  title: string
  focusMode: boolean
  onCommandPalette: () => void
}

export default function CockpitTopBar({ title, focusMode, onCommandPalette }: CockpitTopBarProps) {
  return (
    <header className="flex h-12 items-center justify-between border-b border-dark-border bg-dark-card px-4">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-gray-200">{title}</h2>
        {focusMode && (
          <span className="rounded-full bg-primary-600/20 px-2 py-0.5 text-[11px] font-medium text-primary-400">
            Focus
          </span>
        )}
      </div>
      <button
        onClick={onCommandPalette}
        className="flex items-center gap-2 rounded-lg border border-dark-border px-3 py-1.5 text-xs text-gray-400 hover:border-gray-600 hover:text-gray-200 transition-colors"
      >
        <span>Search</span>
        <kbd className="rounded bg-dark-bg px-1.5 py-0.5 text-[10px] font-mono text-gray-500">
          {navigator.platform?.includes('Mac') ? '\u2318' : 'Ctrl'}K
        </kbd>
      </button>
    </header>
  )
}
