import { forwardRef } from 'react';
import type { ButtonHTMLAttributes } from 'react';
import clsx from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline' | 'default' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  asChild?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    children, 
    variant = 'primary', 
    size = 'md', 
    loading = false, 
    icon,
    className,
    disabled,
    asChild,
    ...props 
  }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus-visible-ring';
    
    const variants = {
      primary: 'bg-gradient-primary text-white hover:shadow-lg hover:shadow-primary-500/25 hover:-translate-y-0.5 active:translate-y-0',
      secondary: 'bg-dark-800 text-gray-100 border border-dark-700 hover:bg-dark-700 hover:-translate-y-0.5 active:translate-y-0',
      ghost: 'text-gray-300 hover:bg-white/5 hover:text-white',
      danger: 'bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30',
      outline: 'text-gray-300 border border-gray-600 hover:bg-gray-600/10 hover:text-white',
      default: 'bg-dark-800 text-gray-100 border border-dark-700 hover:bg-dark-700',
      destructive: 'bg-red-500 text-white hover:bg-red-600',
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-sm gap-2',
      lg: 'px-6 py-3 text-base gap-2.5',
    };

    // For simplicity, we ignore asChild for now
    // In a full implementation, asChild would render children as the button element
    
    return (
      <button
        ref={ref}
        className={clsx(
          baseStyles,
          variants[variant],
          sizes[size],
          (disabled || loading) && 'opacity-50 cursor-not-allowed',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </>
        ) : (
          <>
            {icon && <span>{icon}</span>}
            {children}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';