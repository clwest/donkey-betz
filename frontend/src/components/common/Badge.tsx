import { ReactNode } from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'success' | 'warning';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  const variants = {
    default: 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 shadow-[0_0_8px_rgba(0,255,255,0.3)]',
    secondary: 'bg-background text-muted-foreground border border-gray-700',
    destructive: 'bg-red-500/20 text-red-500 border border-red-500/50 shadow-[0_0_8px_rgba(255,0,0,0.3)]',
    outline: 'bg-transparent text-muted-foreground border border-cyan-500/30',
    success: 'bg-green-500/20 text-green-500 border border-green-500/50 shadow-[0_0_8px_rgba(0,255,0,0.3)]',
    warning: 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/50 shadow-[0_0_8px_rgba(255,255,0,0.3)]',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-lg text-xs font-bold uppercase font-mono tracking-wider transition-all duration-200',
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}