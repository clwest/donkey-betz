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
    style,
    ...props 
  }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus-visible-ring relative overflow-hidden';
    
    const variants = {
      primary: 'gaming-btn-primary text-white hover:-translate-y-0.5 active:translate-y-0',
      secondary: 'gaming-btn-secondary hover:-translate-y-0.5 active:translate-y-0',
      ghost: 'gaming-btn-ghost',
      danger: 'gaming-btn-danger border hover:-translate-y-0.5',
      outline: 'gaming-btn-outline border hover:-translate-y-0.5',
      default: 'gaming-btn-secondary',
      destructive: 'gaming-btn-danger text-white hover:-translate-y-0.5',
    };

    const getVariantStyles = (variant: string) => {
      switch (variant) {
        case 'primary':
          return {
            background: 'var(--gaming-gradient-primary)',
            border: '1px solid var(--gaming-neon-cyan)',
            boxShadow: 'var(--gaming-glow-primary)',
            color: 'white'
          };
        case 'secondary':
          return {
            background: 'var(--gaming-bg-elevated)',
            border: '1px solid var(--gaming-border)',
            color: 'var(--gaming-text-primary)'
          };
        case 'ghost':
          return {
            background: 'transparent',
            color: 'var(--gaming-text-secondary)'
          };
        case 'danger':
        case 'destructive':
          return {
            background: 'rgba(255, 20, 147, 0.2)',
            border: '1px solid var(--gaming-neon-pink)',
            color: 'var(--gaming-neon-pink)'
          };
        case 'outline':
          return {
            background: 'transparent',
            border: '1px solid var(--gaming-border)',
            color: 'var(--gaming-text-primary)'
          };
        default:
          return {
            background: 'var(--gaming-bg-elevated)',
            border: '1px solid var(--gaming-border)',
            color: 'var(--gaming-text-primary)'
          };
      }
    };
    
    const sizes = {
      sm: 'px-3 py-1.5 text-sm gap-1.5',
      md: 'px-4 py-2 text-sm gap-2',
      lg: 'px-6 py-3 text-base gap-2.5',
    };

    // For simplicity, we ignore asChild for now
    // In a full implementation, asChild would render children as the button element
    
    const buttonStyle = {
      ...getVariantStyles(variant),
      ...style
    };

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
        style={buttonStyle}
        disabled={disabled || loading}
        onMouseEnter={(e) => {
          if (variant === 'primary') {
            e.currentTarget.style.boxShadow = 'var(--gaming-glow-primary), 0 0 30px rgba(0, 255, 255, 0.3)';
          } else if (variant === 'secondary') {
            e.currentTarget.style.background = 'var(--gaming-bg-tertiary)';
            e.currentTarget.style.borderColor = 'var(--gaming-neon-cyan)';
            e.currentTarget.style.boxShadow = 'var(--gaming-glow-subtle)';
          } else if (variant === 'ghost') {
            e.currentTarget.style.background = 'rgba(0, 255, 255, 0.05)';
            e.currentTarget.style.color = 'var(--gaming-text-primary)';
          }
        }}
        onMouseLeave={(e) => {
          if (variant === 'primary') {
            e.currentTarget.style.boxShadow = 'var(--gaming-glow-primary)';
          } else if (variant === 'secondary') {
            e.currentTarget.style.background = 'var(--gaming-bg-elevated)';
            e.currentTarget.style.borderColor = 'var(--gaming-border)';
            e.currentTarget.style.boxShadow = 'none';
          } else if (variant === 'ghost') {
            e.currentTarget.style.background = 'transparent';
            e.currentTarget.style.color = 'var(--gaming-text-secondary)';
          }
        }}
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