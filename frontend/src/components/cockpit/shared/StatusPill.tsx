import { cn } from '@/lib/cn'

export type Tone = 'gray' | 'blue' | 'green' | 'red' | 'amber'

const toneClasses: Record<Tone, string> = {
  gray: 'bg-gray-500/20 text-gray-400',
  blue: 'bg-blue-500/20 text-blue-400',
  green: 'bg-emerald-500/20 text-emerald-400',
  red: 'bg-red-500/20 text-red-400',
  amber: 'bg-amber-500/20 text-amber-400',
}

interface StatusPillProps {
  label: string
  tone: Tone
  title?: string
}

export default function StatusPill({ label, tone, title }: StatusPillProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-medium whitespace-nowrap',
        toneClasses[tone],
      )}
      title={title}
    >
      {label}
    </span>
  )
}
