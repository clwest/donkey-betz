import { ReactNode, useState, useRef, useEffect } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';
import clsx from 'clsx';

interface SelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  children: ReactNode;
  className?: string;
}

interface SelectTriggerProps {
  children: ReactNode;
  className?: string;
}

interface SelectContentProps {
  children: ReactNode;
  className?: string;
}

interface SelectItemProps {
  value: string;
  children: ReactNode;
  className?: string;
}

interface SelectValueProps {
  placeholder?: string;
  className?: string;
}

// Simple select implementation that matches platform design
export function Select({ value, onValueChange, children }: SelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState(value || '');
  const [displayValue, setDisplayValue] = useState('');
  const selectRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (newValue: string, displayText: string) => {
    setSelectedValue(newValue);
    setDisplayValue(displayText);
    setIsOpen(false);
    onValueChange?.(newValue);
  };

  return (
    <div ref={selectRef} className="relative w-full">
      <button
        type="button"
        className="input flex items-center justify-between w-full"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={clsx(displayValue ? 'text-gray-100' : 'text-gray-500')}>
          {displayValue || 'Select option...'}
        </span>
        <ChevronDownIcon className={clsx('h-4 w-4 transition-transform', isOpen && 'rotate-180')} />
      </button>
      
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 glass rounded-lg border border-dark-700 shadow-lg">
          <div className="py-1">
            {React.Children.map(children, (child) => {
              if (React.isValidElement(child) && child.type === SelectItem) {
                return React.cloneElement(child as React.ReactElement<SelectItemProps>, {
                  onSelect: handleSelect,
                });
              }
              return child;
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export function SelectTrigger({ children, className }: SelectTriggerProps) {
  return (
    <div className={clsx('input flex items-center justify-between', className)}>
      {children}
    </div>
  );
}

export function SelectContent({ children }: SelectContentProps) {
  return (
    <div className="glass rounded-lg border border-dark-700 shadow-lg py-1">
      {children}
    </div>
  );
}

export function SelectItem({ value, children, onSelect }: SelectItemProps & { onSelect?: (value: string, display: string) => void }) {
  const handleClick = () => {
    const displayText = typeof children === 'string' ? children : value;
    onSelect?.(value, displayText);
  };

  return (
    <button
      type="button"
      className="w-full px-3 py-2 text-left text-gray-300 hover:bg-primary-500/20 hover:text-white transition-colors focus:outline-none focus:bg-primary-500/20"
      onClick={handleClick}
    >
      {children}
    </button>
  );
}

export function SelectValue({ placeholder }: SelectValueProps) {
  return <span className="text-gray-500">{placeholder}</span>;
}

// React import for Children API
import React from 'react';