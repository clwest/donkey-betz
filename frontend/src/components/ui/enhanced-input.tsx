import { forwardRef, useState } from 'react';
import type { InputHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../utils/cn';
import { EyeIcon, EyeSlashIcon } from '@heroicons/react/24/outline';

/**
 * Enhanced Input Component
 * 
 * Features:
 * - Multiple variants (default, filled, outline)
 * - Multiple sizes (sm, md, lg)
 * - Error and success states
 * - Icon support (prefix and suffix)
 * - Password toggle functionality
 * - Helper text and error messages
 * - Loading states
 * - Full accessibility support
 */

const inputVariants = cva(
  [
    'flex w-full font-medium transition-all duration-200',
    'placeholder:text-text-muted',
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-bg-primary',
    'disabled:cursor-not-allowed disabled:opacity-50',
    'file:border-0 file:bg-transparent file:text-sm file:font-medium',
  ],
  {
    variants: {
      variant: {
        default: [
          'border border-border-primary bg-bg-tertiary text-text-primary',
          'focus:border-primary-500 focus:ring-primary-500',
          'hover:border-border-secondary',
        ],
        filled: [
          'border-0 bg-bg-tertiary text-text-primary',
          'focus:ring-primary-500',
          'hover:bg-bg-elevated',
        ],
        outline: [
          'border-2 border-border-primary bg-transparent text-text-primary',
          'focus:border-primary-500 focus:ring-primary-500',
          'hover:border-border-secondary',
        ],
        tech: [
          'border border-border-secondary bg-gradient-to-br from-bg-tertiary to-bg-secondary',
          'text-text-primary',
          'focus:border-primary-500 focus:ring-primary-500 focus:shadow-glow-primary',
          'hover:border-border-tertiary',
        ],
      },
      size: {
        sm: ['h-8 px-3 text-sm rounded-md'],
        md: ['h-10 px-4 text-sm rounded-lg'],
        lg: ['h-12 px-4 text-base rounded-lg'],
      },
      state: {
        default: '',
        error: [
          'border-status-error focus:border-status-error focus:ring-status-error',
          'text-text-primary',
        ],
        success: [
          'border-status-success focus:border-status-success focus:ring-status-success',
          'text-text-primary',
        ],
        warning: [
          'border-status-warning focus:border-status-warning focus:ring-status-warning',
          'text-text-primary',
        ],
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
      state: 'default',
    },
  }
);

export interface InputProps
  extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  /**
   * Label for the input
   */
  label?: string;
  /**
   * Helper text displayed below the input
   */
  helper?: string;
  /**
   * Error message - when provided, input will show error state
   */
  error?: string;
  /**
   * Success message - when provided, input will show success state
   */
  success?: string;
  /**
   * Warning message - when provided, input will show warning state
   */
  warning?: string;
  /**
   * Icon to display at the start of the input
   */
  prefixIcon?: ReactNode;
  /**
   * Icon to display at the end of the input
   */
  suffixIcon?: ReactNode;
  /**
   * Content to display at the start of the input (e.g., currency symbol)
   */
  prefix?: string;
  /**
   * Content to display at the end of the input (e.g., unit)
   */
  suffix?: string;
  /**
   * Loading state
   */
  loading?: boolean;
  /**
   * Custom container className
   */
  containerClassName?: string;
}

/**
 * Loading spinner for input
 */
const InputSpinner = () => (
  <svg
    className="w-4 h-4 animate-spin text-text-muted"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
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

export const EnhancedInput = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      containerClassName,
      variant,
      size,
      state,
      label,
      helper,
      error,
      success,
      warning,
      prefixIcon,
      suffixIcon,
      prefix,
      suffix,
      loading = false,
      type = 'text',
      disabled,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);

    // Determine the input state based on props
    const inputState = error ? 'error' : success ? 'success' : warning ? 'warning' : state;
    
    // Get the message to display
    const message = error || success || warning || helper;
    const messageType = error ? 'error' : success ? 'success' : warning ? 'warning' : 'helper';

    // Handle password toggle
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;

    // Determine if we need a suffix icon
    const needsSuffixIcon = loading || isPassword || suffixIcon;

    return (
      <div className={cn('space-y-2', containerClassName)}>
        {/* Label */}
        {label && (
          <label className="block text-sm font-medium text-text-primary">
            {label}
          </label>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Prefix Icon */}
          {prefixIcon && (
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <div className="w-5 h-5 text-text-muted">{prefixIcon}</div>
            </div>
          )}

          {/* Prefix Text */}
          {prefix && (
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <span className="text-text-secondary text-sm font-medium">{prefix}</span>
            </div>
          )}

          {/* Input */}
          <input
            type={inputType}
            className={cn(
              inputVariants({ variant, size, state: inputState }),
              prefixIcon && 'pl-10',
              prefix && 'pl-8',
              needsSuffixIcon && 'pr-10',
              suffix && 'pr-8',
              className
            )}
            ref={ref}
            disabled={disabled || loading}
            {...props}
          />

          {/* Suffix Content */}
          {(needsSuffixIcon || suffix) && (
            <div className="absolute inset-y-0 right-0 flex items-center pr-3">
              {loading && <InputSpinner />}
              {!loading && isPassword && (
                <button
                  type="button"
                  className="w-5 h-5 text-text-muted hover:text-text-secondary transition-colors focus:outline-none focus:text-text-primary"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeSlashIcon /> : <EyeIcon />}
                </button>
              )}
              {!loading && !isPassword && suffixIcon && (
                <div className="w-5 h-5 text-text-muted">{suffixIcon}</div>
              )}
              {suffix && (
                <span className="text-text-secondary text-sm font-medium ml-2">{suffix}</span>
              )}
            </div>
          )}
        </div>

        {/* Helper/Error/Success Message */}
        {message && (
          <p
            className={cn(
              'text-xs',
              messageType === 'error' && 'text-status-error',
              messageType === 'success' && 'text-status-success',
              messageType === 'warning' && 'text-status-warning',
              messageType === 'helper' && 'text-text-muted'
            )}
          >
            {message}
          </p>
        )}
      </div>
    );
  }
);

EnhancedInput.displayName = 'EnhancedInput';

/**
 * Search Input - Specialized input for search functionality
 */
export interface SearchInputProps extends Omit<InputProps, 'prefixIcon' | 'type'> {
  onSearch?: (value: string) => void;
  onClear?: () => void;
  showClearButton?: boolean;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ onSearch, onClear, showClearButton = true, ...props }, ref) => {
    const [value, setValue] = useState(props.value || '');

    const handleClear = () => {
      setValue('');
      onClear?.();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        onSearch?.(value as string);
      }
      props.onKeyDown?.(e);
    };

    return (
      <EnhancedInput
        ref={ref}
        type="search"
        prefixIcon={
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        }
        suffixIcon={
          showClearButton && value ? (
            <button
              type="button"
              onClick={handleClear}
              className="w-5 h-5 text-text-muted hover:text-text-secondary transition-colors"
              aria-label="Clear search"
            >
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          ) : undefined
        }
        value={value}
        onChange={(e) => {
          setValue(e.target.value);
          props.onChange?.(e);
        }}
        onKeyDown={handleKeyDown}
        placeholder="Search..."
        {...props}
      />
    );
  }
);

SearchInput.displayName = 'SearchInput';

// Export variants for external use
export { inputVariants };