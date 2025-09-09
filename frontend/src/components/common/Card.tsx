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
        'glass rounded-xl p-6 transition-all duration-300',
        hover && 'hover:bg-white/10 hover:shadow-2xl hover:shadow-primary-500/10 hover:-translate-y-1 cursor-pointer',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  );
}