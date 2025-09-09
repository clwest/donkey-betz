import type { ReactNode } from 'react';
import clsx from 'clsx';

interface BadgeProps {
  children: ReactNode;
  variant?: 'success' | 'error' | 'warning' | 'info' | 'secondary' | 'default' | 'outline' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Badge({ 
  children, 
  variant = 'default', 
  size = 'md', 
  className 
}: BadgeProps) {
  const baseStyles = 'inline-flex items-center font-medium rounded-full transition-all duration-200';
  
  const variants = {
    success: 'bg-green-500/20 text-green-400 border border-green-500/50',
    error: 'bg-red-500/20 text-red-400 border border-red-500/50',
    warning: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50',
    info: 'bg-blue-500/20 text-blue-400 border border-blue-500/50',
    secondary: 'bg-gray-700 text-gray-300 border border-gray-600',
    default: 'bg-gray-500/20 text-gray-400 border border-gray-500/50',
    outline: 'text-gray-300 border border-gray-600 hover:bg-gray-600/10',
    destructive: 'bg-red-500/20 text-red-400 border border-red-500/50',
  };
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };
  
  return (
    <span
      className={clsx(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}