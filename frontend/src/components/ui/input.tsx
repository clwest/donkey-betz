import { forwardRef } from 'react';
import type { InputHTMLAttributes } from 'react';
import clsx from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-foreground">
            {label}
          </label>
        )}
        <input
          type={type}
          className={clsx(
            'flex h-10 w-full rounded-lg border border-border/60 bg-background/60 backdrop-blur-sm px-3 py-2 text-sm text-foreground transition-all duration-200',
            'file:border-0 file:bg-transparent file:text-sm file:font-medium',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:border-primary/60 focus:shadow-glow-subtle',
            'disabled:cursor-not-allowed disabled:opacity-50',
            'hover:border-border hover:bg-background/80',
            error && 'border-destructive/60 focus-visible:ring-destructive/20 focus-visible:border-destructive/80',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-sm text-destructive font-medium">{error}</p>
        )}
      </div>
    );
  }
);
Input.displayName = 'Input';