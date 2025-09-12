import { forwardRef } from 'react';
import type { HTMLAttributes } from 'react';
import clsx from 'clsx';

interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
}

export const Progress = forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, ...props }, ref) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    
    return (
      <div
        ref={ref}
        className={clsx(
          'relative h-4 w-full overflow-hidden rounded-lg bg-gray-900 border border-cyan-500/30',
          className
        )}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-gradient-to-r from-cyan-500 to-purple-500 transition-all duration-300 relative"
          style={{ transform: `translateX(-${100 - percentage}%)` }}
        >
          {/* Gaming progress glow effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-400/50 to-purple-400/50 animate-pulse" />
        </div>
      </div>
    );
  }
);
Progress.displayName = 'Progress';