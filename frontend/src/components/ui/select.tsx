import { forwardRef } from 'react';
import type { SelectHTMLAttributes } from 'react';
import clsx from 'clsx';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  value?: string;
  onValueChange?: (value: string) => void;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, className, children, value, onValueChange, onChange, ...props }, ref) => {
    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
      onChange?.(e);
      onValueChange?.(e.target.value);
    };

    return (
      <div className="space-y-2">
        {label && (
          <label className="block text-sm font-medium text-gray-300">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={clsx(
            'w-full bg-dark-800 border border-dark-700 rounded-lg px-3 py-2',
            'text-gray-100 placeholder-gray-400',
            'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'transition-colors duration-200',
            error && 'border-red-500 focus:ring-red-500 focus:border-red-500',
            className
          )}
          value={value}
          onChange={handleChange}
          {...props}
        >
          {children}
        </select>
        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

// Additional components that might be used
export const SelectContent = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={clsx('absolute z-50 min-w-32 bg-dark-800 border border-dark-700 rounded-md shadow-lg', className)}>
    {children}
  </div>
);

export const SelectItem = ({ children, value, className }: { children: React.ReactNode; value: string; className?: string }) => (
  <option value={value} className={clsx('px-2 py-1 text-gray-100', className)}>
    {children}
  </option>
);

export const SelectTrigger = forwardRef<HTMLButtonElement, { children: React.ReactNode; className?: string }>(
  ({ children, className, ...props }, ref) => (
    <button
      ref={ref}
      className={clsx(
        'flex w-full items-center justify-between rounded-md border border-dark-700 bg-dark-800 px-3 py-2 text-sm text-gray-100',
        'focus:outline-none focus:ring-2 focus:ring-primary-500',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
);

SelectTrigger.displayName = 'SelectTrigger';

export const SelectValue = ({ placeholder, className }: { placeholder?: string; className?: string }) => (
  <span className={clsx('text-gray-400', className)}>
    {placeholder}
  </span>
);