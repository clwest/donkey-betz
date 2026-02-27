import { cn } from '@/lib/cn'

interface SkeletonRowsProps {
  count?: number
  className?: string
}

export default function SkeletonRows({ count = 5, className }: SkeletonRowsProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 animate-pulse">
          <div className="h-4 flex-1 rounded bg-dark-border" />
          <div className="h-4 w-16 rounded bg-dark-border" />
          <div className="h-4 w-12 rounded bg-dark-border" />
        </div>
      ))}
    </div>
  )
}
