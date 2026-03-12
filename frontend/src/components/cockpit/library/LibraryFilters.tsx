import { Search } from 'lucide-react'
import { useEffect, useRef } from 'react'

interface LibraryFiltersProps {
  search: string
  onSearchChange: (v: string) => void
  typeFilter: string
  onTypeChange: (v: string) => void
  typeOptions: { value: string; label: string }[]
  daysFilter: number
  onDaysChange: (v: number) => void
}

const DAYS_OPTIONS = [
  { value: 7, label: '7d' },
  { value: 30, label: '30d' },
  { value: 90, label: '90d' },
  { value: 365, label: '1y' },
  { value: 0, label: 'All' },
]

export default function LibraryFilters({
  search,
  onSearchChange,
  typeFilter,
  onTypeChange,
  typeOptions,
  daysFilter,
  onDaysChange,
}: LibraryFiltersProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [])

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px]">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
        <input
          ref={inputRef}
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search… (press /)"
          className="input pl-9 w-full"
        />
      </div>
      <select
        value={typeFilter}
        onChange={(e) => onTypeChange(e.target.value)}
        className="input w-auto"
      >
        {typeOptions.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
      <div className="flex rounded-lg overflow-hidden border border-dark-border">
        {DAYS_OPTIONS.map((o) => (
          <button
            key={o.value}
            onClick={() => onDaysChange(o.value)}
            className={`px-3 py-1.5 text-xs font-medium transition-colors ${
              daysFilter === o.value
                ? 'bg-primary-600 text-white'
                : 'bg-dark-card text-gray-400 hover:text-gray-200'
            }`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}
