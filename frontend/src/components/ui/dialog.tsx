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
        {/* Gaming Backdrop */}
        <div 
          className="fixed inset-0 bg-black/90 backdrop-blur-sm" 
          onClick={() => onOpenChange(false)}
        />
        
        {/* Gaming Modal Content */}
        <div
          ref={ref}
          className={clsx(
            // Default small modal - can be overridden
            'fixed z-50 grid w-full gap-4',
            // Only apply default sizing if not overridden
            !className?.includes('max-w-') && 'max-w-lg',
            !className?.includes('!p-') && !className?.includes('p-') && 'p-6',
            // Gaming modal background with neon border
            'bg-black border-2 border-cyan-500/50 rounded-lg',
            // Cyberpunk glow effects
            'shadow-[0_0_20px_rgba(0,255,255,0.3)] shadow-cyan-500/30',
            // Gaming entrance animation
            'duration-300 animate-in fade-in-0 zoom-in-95 slide-in-from-bottom-4',
            // Pulsing border animation
            'before:absolute before:inset-0 before:border-2 before:border-cyan-500/30 before:rounded-lg before:animate-pulse',
            'relative',
            className
          )}
          {...props}
        >
          {/* Gaming corner decorations */}
          <div className="absolute top-2 left-2 w-3 h-3 border-l-2 border-t-2 border-cyan-500" />
          <div className="absolute top-2 right-2 w-3 h-3 border-r-2 border-t-2 border-cyan-500" />
          <div className="absolute bottom-2 left-2 w-3 h-3 border-l-2 border-b-2 border-cyan-500" />
          <div className="absolute bottom-2 right-2 w-3 h-3 border-r-2 border-b-2 border-cyan-500" />
          
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
        // Gaming header with neon accent
        'border-b border-cyan-500/30 pb-4 mb-2',
        // Subtle glow effect
        'relative before:absolute before:bottom-0 before:left-0 before:right-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-cyan-500 before:to-transparent',
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
        'text-lg font-bold leading-none tracking-wider text-cyan-400',
        // Gaming title styling
        'uppercase font-mono',
        // Subtle text glow
        'text-shadow-sm drop-shadow-[0_0_8px_rgba(0,255,255,0.5)]',
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
        'text-sm text-gray-300',
        // Gaming description styling
        'font-mono leading-relaxed',
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
        // Gaming footer styling
        'border-t border-cyan-500/20 pt-4 mt-4',
        // Subtle top accent line
        'relative before:absolute before:top-0 before:left-0 before:right-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-cyan-500/50 before:to-transparent',
        className
      )}
      {...props}
    />
  )
);
DialogFooter.displayName = 'DialogFooter';