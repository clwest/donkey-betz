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
    <div className={`animate-spin rounded-full border-2 border-cyan-500 border-t-transparent shadow-[0_0_10px_rgba(0,255,255,0.5)] ${sizeClasses[size]} ${className}`} />
  );
}