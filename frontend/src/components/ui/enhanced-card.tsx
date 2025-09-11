import { forwardRef } from 'react';
import type { HTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';

/**
 * Enhanced Card Component System
 * 
 * Features:
 * - Multiple variants (default, elevated, interactive, glass)
 * - Multiple sizes (sm, md, lg, xl)
 * - Hover effects and animations
 * - Consistent spacing and shadows
 * - Full composability with subcomponents
 */

const cardVariants = cva(
  [
    'rounded-xl transition-all duration-300',
    'border border-border-primary',
  ],
  {
    variants: {
      variant: {
        default: [
          'bg-bg-secondary shadow-dark-sm',
        ],
        elevated: [
          'bg-bg-secondary shadow-dark-md',
        ],
        interactive: [
          'bg-bg-secondary shadow-dark-sm cursor-pointer',
          'hover:bg-bg-elevated hover:shadow-dark-lg hover:-translate-y-1',
          'hover:border-border-secondary',
          'active:translate-y-0 active:shadow-dark-sm',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
        ],
        glass: [
          'bg-bg-secondary/60 backdrop-blur-xl border-border-primary/50',
          'shadow-dark-sm',
        ],
        tech: [
          'bg-gradient-to-br from-bg-secondary to-bg-tertiary',
          'border-border-secondary shadow-dark-sm',
          'hover:border-primary-500 hover:shadow-glow-primary',
          'transition-all duration-300',
          // Tech card glow effect
          'relative overflow-hidden',
          'before:absolute before:inset-0 before:bg-gradient-to-r before:from-transparent before:via-primary-500/5 before:to-transparent',
          'before:translate-x-[-100%] before:transition-transform before:duration-1000',
          'hover:before:translate-x-[100%]',
        ],
        status: [
          'bg-bg-secondary border-border-secondary',
          'relative',
          // Status indicator
          'before:absolute before:top-0 before:left-0 before:right-0 before:h-1 before:bg-gradient-primary before:rounded-t-xl',
        ],
      },
      size: {
        sm: ['p-4'],
        md: ['p-6'],
        lg: ['p-8'],
        xl: ['p-10'],
      },
      padding: {
        none: 'p-0',
        sm: 'p-4',
        md: 'p-6',
        lg: 'p-8',
        xl: 'p-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
);

export interface CardProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  /**
   * Card content
   */
  children: ReactNode;
  /**
   * Custom className to apply to the card
   */
  className?: string;
  /**
   * If true, the card will have hover effects
   */
  hover?: boolean;
  /**
   * Status color for status variant
   */
  status?: 'success' | 'warning' | 'error' | 'info' | 'primary';
}

export const EnhancedCard = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, padding, hover, status, children, ...props }, ref) => {
    const statusColors = {
      success: 'before:bg-status-success',
      warning: 'before:bg-status-warning',
      error: 'before:bg-status-error',
      info: 'before:bg-status-info',
      primary: 'before:bg-gradient-primary',
    };

    return (
      <div
        ref={ref}
        className={cn(
          cardVariants({ 
            variant: hover ? 'interactive' : variant, 
            size: padding ? undefined : size,
            padding: padding || undefined,
          }),
          variant === 'status' && status && statusColors[status],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

EnhancedCard.displayName = 'EnhancedCard';

/**
 * Card Header Component
 */
export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 pb-4', className)}
      {...props}
    />
  )
);
CardHeader.displayName = 'CardHeader';

/**
 * Card Title Component
 */
export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement> & {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
}>(
  ({ className, as: Component = 'h3', ...props }, ref) => (
    <Component
      ref={ref}
      className={cn(
        'text-xl font-semibold leading-tight tracking-tight text-text-primary',
        className
      )}
      {...props}
    />
  )
);
CardTitle.displayName = 'CardTitle';

/**
 * Card Description Component
 */
export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn('text-sm text-text-secondary leading-relaxed', className)}
      {...props}
    />
  )
);
CardDescription.displayName = 'CardDescription';

/**
 * Card Content Component
 */
export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('', className)} {...props} />
  )
);
CardContent.displayName = 'CardContent';

/**
 * Card Footer Component
 */
export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex items-center justify-between pt-4', className)}
      {...props}
    />
  )
);
CardFooter.displayName = 'CardFooter';

/**
 * Card Action Area - For clickable cards
 */
export const CardActionArea = forwardRef<HTMLButtonElement, HTMLAttributes<HTMLButtonElement> & {
  onClick?: () => void;
}>(
  ({ className, children, onClick, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        'w-full text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary rounded-xl',
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
);
CardActionArea.displayName = 'CardActionArea';

/**
 * Stats Card - Specialized card for displaying metrics
 */
export interface StatsCardProps extends Omit<CardProps, 'children'> {
  title: string;
  value: string | number;
  description?: string;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  icon?: ReactNode;
  onClick?: () => void;
}

export const StatsCard = forwardRef<HTMLDivElement, StatsCardProps>(
  ({ title, value, description, trend, icon, onClick, className, ...props }, ref) => (
    <EnhancedCard
      ref={ref}
      variant={onClick ? 'interactive' : 'default'}
      className={cn('group', className)}
      onClick={onClick}
      {...props}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-text-secondary">{title}</p>
          <p className="text-2xl font-bold text-text-primary mt-1">{value}</p>
          {description && (
            <p className="text-xs text-text-muted mt-1">{description}</p>
          )}
          {trend && (
            <div className={cn(
              'flex items-center gap-1 text-xs mt-2',
              trend.isPositive ? 'text-status-success' : 'text-status-error'
            )}>
              <span>{trend.isPositive ? '↗' : '↘'}</span>
              <span>{trend.value}</span>
            </div>
          )}
        </div>
        {icon && (
          <div className="p-2 bg-primary-500/10 rounded-lg text-primary-400 group-hover:bg-primary-500/20 transition-colors">
            {icon}
          </div>
        )}
      </div>
    </EnhancedCard>
  )
);
StatsCard.displayName = 'StatsCard';

// Export variants for external use
export { cardVariants };