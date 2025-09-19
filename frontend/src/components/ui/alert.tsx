import { forwardRef } from 'react';
import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive' | 'warning' | 'success';
}

const Alert = forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant = 'default', ...props }, ref) => (
    <div
      ref={ref}
      role="alert"
      className={clsx(
        'relative w-full rounded-lg border-2 p-4',
        {
          'border-cyan-500/50 bg-black text-muted-foreground shadow-[0_0_10px_rgba(0,255,255,0.2)]': variant === 'default',
          'border-red-500/50 bg-red-500/10 text-red-500 shadow-[0_0_10px_rgba(255,0,0,0.2)]': variant === 'destructive',
          'border-yellow-500/50 bg-yellow-500/10 text-yellow-500 shadow-[0_0_10px_rgba(255,255,0,0.2)]': variant === 'warning',
          'border-green-500/50 bg-green-500/10 text-green-500 shadow-[0_0_10px_rgba(0,255,0,0.2)]': variant === 'success',
        },
        'before:absolute before:inset-0 before:border-2 before:border-opacity-30 before:rounded-lg before:animate-pulse',
        {
          'before:border-cyan-500': variant === 'default',
          'before:border-red-500': variant === 'destructive',
          'before:border-yellow-500': variant === 'warning',
          'before:border-green-500': variant === 'success',
        },
        className
      )}
      {...props}
    />
  )
);
Alert.displayName = 'Alert';

const AlertTitle = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h5
      ref={ref}
      className={clsx('mb-1 font-bold leading-none tracking-wider uppercase font-mono', className)}
      {...props}
    />
  )
);
AlertTitle.displayName = 'AlertTitle';

const AlertDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('text-sm [&_p]:leading-relaxed font-mono', className)}
      {...props}
    />
  )
);
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertTitle, AlertDescription };