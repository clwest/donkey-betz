import { forwardRef } from 'react';
import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';
import { Slot } from '@radix-ui/react-slot';

/**
 * Enhanced Button Component
 * 
 * Features:
 * - Multiple variants (primary, secondary, ghost, outline, danger)
 * - Multiple sizes (sm, md, lg, xl)
 * - Loading states with spinner
 * - Icon support
 * - Polymorphic with asChild prop
 * - Full accessibility support
 */

const buttonVariants = cva(
  [
    // Base styles
    'inline-flex items-center justify-center font-medium transition-all duration-200',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
    'disabled:pointer-events-none disabled:opacity-50',
    'relative overflow-hidden',
  ],
  {
    variants: {
      variant: {
        primary: [
          'bg-gradient-to-r from-primary-500 to-primary-600',
          'text-white shadow-dark-sm',
          'hover:shadow-dark-md hover:shadow-primary-500/25 hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-dark-sm',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-bg-primary',
        ],
        secondary: [
          'bg-bg-tertiary border border-border-secondary',
          'text-text-primary shadow-dark-sm',
          'hover:bg-bg-elevated hover:border-border-tertiary hover:-translate-y-0.5',
          'active:translate-y-0',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-bg-primary',
        ],
        ghost: [
          'text-text-secondary',
          'hover:bg-bg-secondary hover:text-text-primary',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-bg-primary',
        ],
        outline: [
          'border border-border-primary bg-transparent',
          'text-text-primary',
          'hover:bg-bg-secondary hover:border-border-secondary',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-bg-primary',
        ],
        danger: [
          'bg-status-error border border-accent-rose-600',
          'text-white shadow-dark-sm',
          'hover:bg-accent-rose-600 hover:shadow-dark-md hover:shadow-status-error/25 hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-dark-sm',
          'focus-visible:ring-status-error focus-visible:ring-offset-bg-primary',
        ],
        success: [
          'bg-status-success border border-accent-emerald-600',
          'text-white shadow-dark-sm',
          'hover:bg-accent-emerald-600 hover:shadow-dark-md hover:shadow-status-success/25 hover:-translate-y-0.5',
          'active:translate-y-0 active:shadow-dark-sm',
          'focus-visible:ring-status-success focus-visible:ring-offset-bg-primary',
        ],
        tech: [
          'bg-gradient-to-br from-bg-tertiary to-bg-secondary',
          'border border-border-secondary text-text-primary',
          'hover:border-primary-500 hover:shadow-glow-primary hover:-translate-y-1',
          'active:translate-y-0',
          'focus-visible:ring-primary-500 focus-visible:ring-offset-bg-primary',
          // Tech button shine effect
          'before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-white/10 before:to-transparent',
          'before:translate-x-[-100%] before:transition-transform before:duration-700',
          'hover:before:translate-x-[100%]',
        ],
      },
      size: {
        sm: ['h-8 px-3 text-xs gap-1.5 rounded-md'],
        md: ['h-10 px-4 text-sm gap-2 rounded-lg'],
        lg: ['h-12 px-6 text-base gap-2.5 rounded-lg'],
        xl: ['h-14 px-8 text-lg gap-3 rounded-xl'],
      },
      loading: {
        true: 'cursor-wait',
        false: '',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
      loading: false,
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * If true, the button will show a loading spinner and be disabled
   */
  loading?: boolean;
  /**
   * Icon to display before the button text
   */
  icon?: ReactNode;
  /**
   * Icon to display after the button text
   */
  iconEnd?: ReactNode;
  /**
   * If true, the component will render as a child element instead of a button
   */
  asChild?: boolean;
  /**
   * Custom className to apply to the button
   */
  className?: string;
}

/**
 * Loading spinner component
 */
const LoadingSpinner = ({ size = 'sm' }: { size?: 'xs' | 'sm' | 'md' }) => {
  const sizeClasses = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
  };

  return (
    <svg
      className={cn('animate-spin', sizeClasses[size])}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-label="Loading"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
};

export const EnhancedButton = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      loading = false,
      icon,
      iconEnd,
      asChild = false,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const Comp = asChild ? Slot : 'button';

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, loading, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <LoadingSpinner size={size === 'sm' ? 'xs' : size === 'xl' ? 'md' : 'sm'} />
        )}
        {!loading && icon && <span className="flex-shrink-0">{icon}</span>}
        {children && <span className={loading ? 'opacity-0' : ''}>{children}</span>}
        {!loading && iconEnd && <span className="flex-shrink-0">{iconEnd}</span>}
      </Comp>
    );
  }
);

EnhancedButton.displayName = 'EnhancedButton';

// Export the original Button for backward compatibility
export { buttonVariants };
export type { VariantProps } from 'class-variance-authority';