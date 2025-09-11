import { ReactNode } from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-primary-500/20 text-primary-400 border border-primary-500/30',
    secondary: 'bg-dark-700 text-gray-300 border border-dark-600',
    destructive: 'bg-red-500/20 text-red-400 border border-red-500/30',
    outline: 'bg-transparent text-gray-400 border border-gray-600',
    success: 'bg-green-500/20 text-green-400 border border-green-500/30',
    warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium transition-colors',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}