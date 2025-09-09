interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'small' | 'medium' | 'large';
  className?: string;
}

export function LoadingSpinner({ size = 'medium', className = '' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    small: 'h-4 w-4',
    md: 'h-8 w-8',
    medium: 'h-8 w-8',
    lg: 'h-12 w-12',
    large: 'h-12 w-12'
  };

  return (
    <div className={`animate-spin rounded-full border-2 border-primary border-t-primary/30 ${sizeClasses[size]} ${className}`} />
  );
}