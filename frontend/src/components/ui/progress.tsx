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
          'relative h-4 w-full overflow-hidden rounded-full bg-dark-800',
          className
        )}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-300"
          style={{ transform: `translateX(-${100 - percentage}%)` }}
        />
      </div>
    );
  }
);
Progress.displayName = 'Progress';