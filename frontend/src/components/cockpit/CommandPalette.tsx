import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Home, Inbox, PlusCircle, Play, FolderOpen, AlertTriangle, Wrench, Settings, Zap, ShieldCheck, Bell, ScrollText, Bot,
  Layers, DollarSign,
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface Action {
  id: string
  label: string
  icon: React.ElementType
  action: () => void
}

interface CommandPaletteProps {
  open: boolean
  onClose: () => void
  onToggleFocusMode: () => void
}

export default function CommandPalette({ open, onClose, onToggleFocusMode }: CommandPaletteProps) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const actions: Action[] = [
    { id: 'today', label: 'Go to Today', icon: Home, action: () => navigate('/cockpit') },
    { id: 'inbox', label: 'Go to Inbox', icon: Inbox, action: () => navigate('/cockpit/inbox') },
    { id: 'create', label: 'Go to Create', icon: PlusCircle, action: () => navigate('/cockpit/create') },
    { id: 'runs', label: 'Go to Runs', icon: Play, action: () => navigate('/cockpit/runs') },
    { id: 'library', label: 'Go to Library', icon: FolderOpen, action: () => navigate('/cockpit/library') },
    { id: 'errors', label: 'Go to Errors', icon: AlertTriangle, action: () => navigate('/cockpit/errors') },
    { id: 'ops', label: 'Go to Ops', icon: Wrench, action: () => navigate('/cockpit/ops') },
    { id: 'approvals', label: 'Go to Approvals', icon: ShieldCheck, action: () => navigate('/cockpit/approvals') },
    { id: 'alerts', label: 'Go to Alerts', icon: Bell, action: () => navigate('/cockpit/alerts') },
    { id: 'audit', label: 'Go to Audit Log', icon: ScrollText, action: () => navigate('/cockpit/audit') },
    { id: 'agents', label: 'Go to Agent Fleet', icon: Bot, action: () => navigate('/cockpit/agents') },
    { id: 'queues', label: 'Go to Queues', icon: Layers, action: () => navigate('/cockpit/queues') },
    { id: 'cost', label: 'Go to Cost', icon: DollarSign, action: () => navigate('/cockpit/cost') },
    { id: 'settings', label: 'Go to Settings', icon: Settings, action: () => navigate('/settings') },
    { id: 'focus', label: 'Toggle Focus Mode', icon: Zap, action: onToggleFocusMode },
  ]

  const filtered = query
    ? actions.filter((a) => a.label.toLowerCase().includes(query.toLowerCase()))
    : actions

  const [selected, setSelected] = useState(0)

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelected(0)
      setTimeout(() => inputRef.current?.focus(), 0)
    }
  }, [open])

  useEffect(() => {
    setSelected(0)
  }, [query])

  const runAction = useCallback(
    (action: Action) => {
      action.action()
      onClose()
    },
    [onClose],
  )

  useEffect(() => {
    if (!open) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose()
      } else if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelected((s) => Math.min(s + 1, filtered.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelected((s) => Math.max(s - 1, 0))
      } else if (e.key === 'Enter' && filtered[selected]) {
        e.preventDefault()
        runAction(filtered[selected])
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [open, filtered, selected, onClose, runAction])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60" />
      <div
        className="relative w-full max-w-md rounded-xl border border-dark-border bg-dark-card shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type a command..."
          className="w-full rounded-t-xl border-b border-dark-border bg-transparent px-4 py-3 text-sm text-gray-200 placeholder-gray-500 outline-none"
        />
        <ul className="max-h-64 overflow-y-auto py-2">
          {filtered.length === 0 && (
            <li className="px-4 py-3 text-sm text-gray-500">No results</li>
          )}
          {filtered.map((action, i) => {
            const Icon = action.icon
            return (
              <li key={action.id}>
                <button
                  className={cn(
                    'flex w-full items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-dark-border/50',
                    i === selected && 'bg-dark-border/50 text-white',
                  )}
                  onClick={() => runAction(action)}
                  onMouseEnter={() => setSelected(i)}
                >
                  <Icon size={16} className="text-gray-500" />
                  {action.label}
                </button>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}
