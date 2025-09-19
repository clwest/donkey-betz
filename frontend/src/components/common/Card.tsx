import type { ReactNode } from 'react';
import clsx from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export function Card({ children, className, hover = false, onClick }: CardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border bg-card/95 backdrop-blur-sm text-card-foreground shadow-dark-lg transition-all duration-300 relative overflow-hidden',
        'before:absolute before:inset-0 before:bg-gradient-to-br before:from-primary/5 before:to-transparent before:pointer-events-none',
        hover && 'hover:shadow-dark-xl hover:border-primary/40 hover:-translate-y-1 hover:shadow-glow-subtle cursor-pointer',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}