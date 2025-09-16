import { createContext, forwardRef, useContext, useState, useRef, useEffect, cloneElement, isValidElement } from 'react';
import type { HTMLAttributes, ReactNode, ReactElement } from 'react';
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
      <div className="relative inline-block text-left z-50">
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

    if (asChild && isValidElement(children)) {
      // Clone the child element and add the click handler
      return cloneElement(children as ReactElement<any>, {
        onClick: handleClick,
        ref
      });
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
          'absolute z-[100] min-w-32 overflow-hidden rounded-lg border-2 border-cyan-500/50 bg-black p-1 shadow-[0_0_20px_rgba(0,255,255,0.3)]',
          'animate-in fade-in-0 zoom-in-95',
          'before:absolute before:inset-0 before:border-2 before:border-cyan-500/30 before:rounded-lg before:animate-pulse',
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
          'relative flex cursor-default select-none items-center rounded-lg px-2 py-1.5 text-sm text-gray-300 font-mono',
          'outline-none transition-all duration-200 hover:bg-cyan-500/20 hover:text-cyan-400 hover:border-cyan-500/50',
          'focus:bg-cyan-500/20 focus:text-cyan-400 hover:shadow-[0_0_8px_rgba(0,255,255,0.3)]',
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
      className={clsx('-mx-1 my-1 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent', className)}
      {...props}
    />
  )
);
DropdownMenuSeparator.displayName = 'DropdownMenuSeparator';

export const DropdownMenuLabel = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx('px-2 py-1.5 text-sm font-bold text-cyan-400 uppercase font-mono tracking-wider', className)}
      {...props}
    />
  )
);
DropdownMenuLabel.displayName = 'DropdownMenuLabel';