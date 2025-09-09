import { createContext, forwardRef, useContext } from 'react';
import type { HTMLAttributes } from 'react';
import clsx from 'clsx';

interface TabsContextValue {
  value?: string;
  onValueChange?: (value: string) => void;
}

const TabsContext = createContext<TabsContextValue>({});

interface TabsProps extends HTMLAttributes<HTMLDivElement> {
  value?: string;
  onValueChange?: (value: string) => void;
}

const Tabs = forwardRef<HTMLDivElement, TabsProps>(
  ({ className, value, onValueChange, ...props }, ref) => (
    <TabsContext.Provider value={{ value, onValueChange }}>
      <div
        ref={ref}
        className={clsx('w-full', className)}
        {...props}
      />
    </TabsContext.Provider>
  )
);
Tabs.displayName = 'Tabs';

const TabsList = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        'inline-flex h-10 items-center justify-center rounded-md bg-dark-800 p-1 text-gray-400',
        className
      )}
      {...props}
    />
  )
);
TabsList.displayName = 'TabsList';

interface TabsTriggerProps extends HTMLAttributes<HTMLButtonElement> {
  value: string;
}

const TabsTrigger = forwardRef<HTMLButtonElement, TabsTriggerProps>(
  ({ className, value: triggerValue, ...props }, ref) => {
    const { value, onValueChange } = useContext(TabsContext);
    const isActive = value === triggerValue;

    return (
      <button
        ref={ref}
        className={clsx(
          'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium',
          'transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
          'disabled:pointer-events-none disabled:opacity-50',
          isActive
            ? 'bg-dark-700 text-white shadow-sm'
            : 'hover:bg-dark-700/50 hover:text-gray-200',
          className
        )}
        onClick={() => onValueChange?.(triggerValue)}
        {...props}
      />
    );
  }
);
TabsTrigger.displayName = 'TabsTrigger';

interface TabsContentProps extends HTMLAttributes<HTMLDivElement> {
  value: string;
}

const TabsContent = forwardRef<HTMLDivElement, TabsContentProps>(
  ({ className, value: contentValue, ...props }, ref) => {
    const { value } = useContext(TabsContext);
    
    if (value !== contentValue) return null;

    return (
      <div
        ref={ref}
        className={clsx(
          'mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2',
          className
        )}
        {...props}
      />
    );
  }
);
TabsContent.displayName = 'TabsContent';

export { Tabs, TabsList, TabsTrigger, TabsContent };