import { forwardRef } from 'react';
import type { SelectHTMLAttributes } from 'react';
import clsx from 'clsx';

// Simple native HTML select wrapper
// For shadcn/ui Select components, use select-proper.tsx instead

interface NativeSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
}

export const NativeSelect = forwardRef<HTMLSelectElement, NativeSelectProps>(
  ({ label, error, className, children, ...props }, ref) => {
    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-muted-foreground">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={clsx(
            'w-full bg-card border border-border rounded-lg px-3 py-2',
            'text-foreground placeholder-gray-400',
            'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'transition-colors duration-200',
            error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
            className
          )}
          {...props}
        >
          {children}
        </select>
        {error && (
          <p className="text-sm text-red-500">{error}</p>
        )}
      </div>
    );
  }
);

NativeSelect.displayName = 'NativeSelect';

// Simple option wrapper for native select
export const NativeOption = ({
  children,
  value,
  className
}: {
  children: React.ReactNode;
  value: string | number;
  className?: string
}) => (
  <option value={value} className={className}>
    {children}
  </option>
);

// Export the proper shadcn Select components from select-proper.tsx
// This prevents accidental mixing of native and shadcn components
export {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  SelectGroup,
  SelectLabel,
  SelectSeparator
} from './select-proper';