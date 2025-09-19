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
    const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 backdrop-blur-sm relative overflow-hidden';

    const variants = {
      primary: 'bg-gradient-primary text-white hover:shadow-glow-primary border border-primary/30 hover:border-primary/60',
      secondary: 'bg-secondary/20 text-secondary hover:bg-secondary/30 border border-secondary/30 hover:border-secondary/60 hover:shadow-glow-secondary',
      ghost: 'hover:bg-accent/60 hover:text-accent-foreground backdrop-blur-sm',
      danger: 'bg-destructive/90 text-destructive-foreground hover:bg-destructive hover:shadow-glow-error border border-destructive/30',
      outline: 'border border-input bg-background/60 hover:bg-accent/60 hover:text-accent-foreground backdrop-blur-sm hover:border-primary/30',
      default: 'bg-secondary/20 text-secondary-foreground hover:bg-secondary/30 border border-secondary/30',
      destructive: 'bg-destructive/90 text-destructive-foreground hover:bg-destructive hover:shadow-glow-error border border-destructive/30',
    };

    const sizes = {
      sm: 'h-9 px-3 text-sm',
      md: 'h-10 px-4 py-2',
      lg: 'h-11 px-8',
    };

    return (
      <button
        ref={ref}
        className={clsx(
          baseStyles,
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-4 w-4" viewBox="0 0 24 24">
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
            Loading...
          </>
        ) : (
          <>
            {icon && <span className="mr-2">{icon}</span>}
            {children}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';