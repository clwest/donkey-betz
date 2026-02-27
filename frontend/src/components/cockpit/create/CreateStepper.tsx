import { cn } from '@/lib/cn'

const STEPS = ['Inputs', 'Review', 'Run']

interface CreateStepperProps {
  current: number // 0, 1, 2
}

export default function CreateStepper({ current }: CreateStepperProps) {
  return (
    <div className="flex items-center gap-2">
      {STEPS.map((label, i) => (
        <div key={label} className="flex items-center gap-2">
          {i > 0 && <div className={cn('h-px w-6', i <= current ? 'bg-primary-500' : 'bg-dark-border')} />}
          <div className="flex items-center gap-1.5">
            <div
              className={cn(
                'flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium',
                i < current && 'bg-primary-600 text-white',
                i === current && 'bg-primary-600/20 text-primary-400 ring-1 ring-primary-500',
                i > current && 'bg-dark-border text-gray-500',
              )}
            >
              {i + 1}
            </div>
            <span className={cn('text-xs', i <= current ? 'text-gray-200' : 'text-gray-500')}>
              {label}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
