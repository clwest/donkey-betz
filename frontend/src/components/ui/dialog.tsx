import { createContext, forwardRef, useContext, useEffect, useState } from 'react';
import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface DialogContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DialogContext = createContext<DialogContextValue>({
  open: false,
  onOpenChange: () => {},
});

interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: ReactNode;
}

export const Dialog = ({ open = false, onOpenChange, children }: DialogProps) => {
  return (
    <DialogContext.Provider value={{ open, onOpenChange: onOpenChange || (() => {}) }}>
      {children}
    </DialogContext.Provider>
  );
};

interface DialogTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

export const DialogTrigger = forwardRef<HTMLButtonElement, DialogTriggerProps>(
  ({ className, onClick, asChild, children, ...props }, ref) => {
    const { onOpenChange } = useContext(DialogContext);
    
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      onClick?.(e);
      onOpenChange(true);
    };

    if (asChild) {
      // In a full implementation, this would clone the child element and add event handlers
      // For simplicity, we'll just render the children
      return <>{children}</>;
    }
    
    return (
      <button
        ref={ref}
        className={className}
        onClick={handleClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);
DialogTrigger.displayName = 'DialogTrigger';

interface DialogContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

export const DialogContent = forwardRef<HTMLDivElement, DialogContentProps>(
  ({ className, children, ...props }, ref) => {
    const { open, onOpenChange } = useContext(DialogContext);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
      setMounted(true);
      return () => setMounted(false);
    }, []);

    if (!mounted || !open) return null;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        {/* Enhanced Gaming Backdrop */}
        <div
          className="fixed inset-0 bg-background/95 backdrop-blur-md"
          onClick={() => onOpenChange(false)}
        />

        {/* Enhanced Gaming Modal Content */}
        <div
          ref={ref}
          className={clsx(
            // Default small modal - can be overridden
            'fixed z-50 grid w-full gap-4',
            // Only apply default sizing if not overridden
            !className?.includes('max-w-') && 'max-w-lg',
            !className?.includes('!p-') && !className?.includes('p-') && 'p-6',
            // Enhanced gaming modal background
            'bg-card/95 backdrop-blur-md border border-primary/30 rounded-xl shadow-dark-xl',
            // Enhanced glow effects
            'shadow-glow-primary',
            // Gaming entrance animation
            'duration-300 animate-slide-up',
            // Background gradient overlay
            'before:absolute before:inset-0 before:bg-gradient-to-br before:from-primary/5 before:to-transparent before:pointer-events-none before:rounded-xl',
            'relative overflow-hidden',
            className
          )}
          {...props}
        >
          {/* Subtle accent line */}
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />

          {children}
        </div>
      </div>
    );
  }
);
DialogContent.displayName = 'DialogContent';

export const DialogHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        'flex flex-col space-y-1.5 text-center sm:text-left',
        // Enhanced gaming header
        'border-b border-border/30 pb-4 mb-2',
        // Subtle glow effect
        'relative before:absolute before:bottom-0 before:left-0 before:right-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-primary/50 before:to-transparent',
        className
      )}
      {...props}
    />
  )
);
DialogHeader.displayName = 'DialogHeader';

export const DialogTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h2
      ref={ref}
      className={clsx(
        'text-lg font-bold leading-none tracking-tight text-foreground',
        // Enhanced title styling
        'font-semibold',
        className
      )}
      {...props}
    />
  )
);
DialogTitle.displayName = 'DialogTitle';

export const DialogDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={clsx(
        'text-sm text-muted-foreground leading-relaxed',
        className
      )}
      {...props}
    />
  )
);
DialogDescription.displayName = 'DialogDescription';

export const DialogFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        'flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2',
        // Enhanced footer styling
        'border-t border-border/30 pt-4 mt-4',
        // Subtle top accent line
        'relative before:absolute before:top-0 before:left-0 before:right-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-primary/30 before:to-transparent',
        className
      )}
      {...props}
    />
  )
);
DialogFooter.displayName = 'DialogFooter';