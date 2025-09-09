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
        'relative w-full rounded-lg border p-4',
        {
          'border-dark-700 bg-dark-800 text-gray-300': variant === 'default',
          'border-red-500/50 bg-red-500/10 text-red-400': variant === 'destructive',
          'border-yellow-500/50 bg-yellow-500/10 text-yellow-400': variant === 'warning',
          'border-green-500/50 bg-green-500/10 text-green-400': variant === 'success',
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
      className={clsx('mb-1 font-medium leading-none tracking-tight', className)}
      {...props}
    />
  )
);
AlertTitle.displayName = 'AlertTitle';

const AlertDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('text-sm [&_p]:leading-relaxed', className)}
      {...props}
    />
  )
);
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertTitle, AlertDescription };