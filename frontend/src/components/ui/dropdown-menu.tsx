import { createContext, forwardRef, useContext, useState, useRef, useEffect } from 'react';
import type { HTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface DropdownMenuContextValue {
  open: boolean;
  setOpen: (open: boolean) => void;
}

const DropdownMenuContext = createContext<DropdownMenuContextValue>({
  open: false,
  setOpen: () => {},
});

interface DropdownMenuProps {
  children: ReactNode;
}

export const DropdownMenu = ({ children }: DropdownMenuProps) => {
  const [open, setOpen] = useState(false);

  return (
    <DropdownMenuContext.Provider value={{ open, setOpen }}>
      <div className="relative inline-block text-left">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  );
};

interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

export const DropdownMenuTrigger = forwardRef<HTMLButtonElement, DropdownMenuTriggerProps>(
  ({ className, onClick, asChild, children, ...props }, ref) => {
    const { open, setOpen } = useContext(DropdownMenuContext);
    
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      onClick?.(e);
      setOpen(!open);
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
DropdownMenuTrigger.displayName = 'DropdownMenuTrigger';

interface DropdownMenuContentProps extends HTMLAttributes<HTMLDivElement> {
  align?: 'start' | 'center' | 'end';
  side?: 'top' | 'right' | 'bottom' | 'left';
}

export const DropdownMenuContent = forwardRef<HTMLDivElement, DropdownMenuContentProps>(
  ({ className, align = 'center', side = 'bottom', children, ...props }, ref) => {
    const { open, setOpen } = useContext(DropdownMenuContext);
    const contentRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
      const handleClickOutside = (event: MouseEvent) => {
        if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
          setOpen(false);
        }
      };

      if (open) {
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
      }
    }, [open, setOpen]);

    if (!open) return null;

    return (
      <div
        ref={contentRef}
        className={clsx(
          'absolute z-50 min-w-32 overflow-hidden rounded-md border border-dark-700 bg-dark-800 p-1 shadow-md',
          'animate-in fade-in-0 zoom-in-95',
          {
            'left-0': align === 'start',
            'left-1/2 -translate-x-1/2': align === 'center',
            'right-0': align === 'end',
            'bottom-full mb-1': side === 'top',
            'top-full mt-1': side === 'bottom',
            'right-full mr-1 top-0': side === 'left',
            'left-full ml-1 top-0': side === 'right',
          },
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
DropdownMenuContent.displayName = 'DropdownMenuContent';

interface DropdownMenuItemProps extends HTMLAttributes<HTMLDivElement> {
  disabled?: boolean;
}

export const DropdownMenuItem = forwardRef<HTMLDivElement, DropdownMenuItemProps>(
  ({ className, disabled, onClick, ...props }, ref) => {
    const { setOpen } = useContext(DropdownMenuContext);
    
    const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
      if (disabled) return;
      onClick?.(e);
      setOpen(false);
    };
    
    return (
      <div
        ref={ref}
        className={clsx(
          'relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm text-gray-300',
          'outline-none transition-colors hover:bg-dark-700 hover:text-white',
          'focus:bg-dark-700 focus:text-white',
          disabled && 'pointer-events-none opacity-50',
          className
        )}
        onClick={handleClick}
        {...props}
      />
    );
  }
);
DropdownMenuItem.displayName = 'DropdownMenuItem';

export const DropdownMenuSeparator = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('-mx-1 my-1 h-px bg-dark-700', className)}
      {...props}
    />
  )
);
DropdownMenuSeparator.displayName = 'DropdownMenuSeparator';

export const DropdownMenuLabel = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('px-2 py-1.5 text-sm font-semibold text-gray-400', className)}
      {...props}
    />
  )
);
DropdownMenuLabel.displayName = 'DropdownMenuLabel';