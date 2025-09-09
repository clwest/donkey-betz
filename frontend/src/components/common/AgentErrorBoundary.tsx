import React, { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import {
  ExclamationTriangleIcon,
  ArrowPathIcon,
  BugAntIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline';
import { Logger } from '../../utils/logger';
import { toast } from 'sonner';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
  contextName?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string | null;
}

export class AgentErrorBoundary extends Component<Props, State> {
  private retryCount = 0;
  private maxRetries = 3;

  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
    errorId: null
  };

  public static getDerivedStateFromError(error: Error): State {
    const errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    return {
      hasError: true,
      error,
      errorInfo: null,
      errorId
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    const contextName = this.props.contextName || 'Agent Component';
    
    Logger.error(contextName, {
      message: 'Component error boundary caught error',
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      errorId: this.state.errorId
    });

    this.setState({
      errorInfo
    });

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);

    // Show user-friendly error toast
    toast.error(`An error occurred in ${contextName}. Please try refreshing.`);
  }

  private handleRetry = () => {
    if (this.retryCount < this.maxRetries) {
      this.retryCount++;
      Logger.debug('Error Boundary', `Retry attempt ${this.retryCount}/${this.maxRetries}`);
      
      this.setState({
        hasError: false,
        error: null,
        errorInfo: null,
        errorId: null
      });
    } else {
      toast.error('Maximum retry attempts reached. Please refresh the page.');
    }
  };

  private handleCopyError = () => {
    const { error, errorInfo, errorId } = this.state;
    const errorDetails = {
      errorId,
      timestamp: new Date().toISOString(),
      message: error?.message,
      stack: error?.stack,
      componentStack: errorInfo?.componentStack,
      context: this.props.contextName || 'Unknown',
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => toast.success('Error details copied to clipboard'))
      .catch(() => toast.error('Failed to copy error details'));
  };

  private handleReportError = () => {
    const { error, errorId } = this.state;
    
    // In a real application, you would send this to your error reporting service
    Logger.error('Error Reporting', {
      message: 'User reported error',
      errorId,
      error: error?.message,
      context: this.props.contextName
    });
    
    toast.success('Error reported. Thank you for helping improve the application!');
  };

  public render() {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-[400px] flex items-center justify-center p-8">
          <div className="max-w-md w-full bg-white border border-red-200 rounded-lg p-6 text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-red-100 rounded-full p-3">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              </div>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Something went wrong
            </h3>

            <p className="text-gray-600 mb-6">
              {this.props.contextName || 'This component'} encountered an unexpected error. 
              You can try again or refresh the page.
            </p>

            <div className="space-y-3">
              {/* Retry Button */}
              {this.retryCount < this.maxRetries && (
                <button
                  onClick={this.handleRetry}
                  className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
                >
                  <ArrowPathIcon className="h-4 w-4 mr-2" />
                  Try Again ({this.maxRetries - this.retryCount} attempts left)
                </button>
              )}

              {/* Refresh Page Button */}
              <button
                onClick={() => window.location.reload()}
                className="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Refresh Page
              </button>

              {/* Error Details (if enabled) */}
              {this.props.showDetails && this.state.error && (
                <details className="text-left">
                  <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 mb-2">
                    <BugAntIcon className="h-4 w-4 inline mr-1" />
                    Show Error Details
                  </summary>
                  <div className="bg-gray-50 border rounded p-3 text-xs text-left">
                    <div className="mb-2">
                      <strong>Error ID:</strong> {this.state.errorId}
                    </div>
                    <div className="mb-2">
                      <strong>Message:</strong> {this.state.error.message}
                    </div>
                    {this.state.error.stack && (
                      <div className="mb-2">
                        <strong>Stack:</strong>
                        <pre className="mt-1 overflow-x-auto text-xs bg-gray-100 p-2 rounded">
                          {this.state.error.stack}
                        </pre>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex space-x-2 mt-3">
                    <button
                      onClick={this.handleCopyError}
                      className="flex-1 px-3 py-2 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center justify-center"
                    >
                      <ClipboardDocumentIcon className="h-3 w-3 mr-1" />
                      Copy Details
                    </button>
                    <button
                      onClick={this.handleReportError}
                      className="flex-1 px-3 py-2 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                    >
                      Report Error
                    </button>
                  </div>
                </details>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Hook version for functional components
export const withAgentErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  contextName?: string,
  showDetails?: boolean
) => {
  return React.forwardRef<any, P>((props, ref) => (
    <AgentErrorBoundary contextName={contextName} showDetails={showDetails}>
      <Component {...props} ref={ref} />
    </AgentErrorBoundary>
  ));
};

// Loading Error Component for network/API errors
interface LoadingErrorProps {
  error: string | Error;
  onRetry?: () => void;
  loading?: boolean;
  contextName?: string;
  className?: string;
}

export const LoadingError: React.FC<LoadingErrorProps> = ({
  error,
  onRetry,
  loading = false,
  contextName = 'Data',
  className = ''
}) => {
  const errorMessage = typeof error === 'string' ? error : error.message;

  return (
    <div className={`flex flex-col items-center justify-center p-8 ${className}`}>
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-sm w-full text-center">
        <div className="flex justify-center mb-4">
          <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
        </div>
        
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Failed to load {contextName}
        </h3>
        
        <p className="text-sm text-gray-600 mb-4">
          {errorMessage}
        </p>
        
        {onRetry && (
          <button
            onClick={onRetry}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            {loading ? (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                Retrying...
              </>
            ) : (
              <>
                <ArrowPathIcon className="h-4 w-4 mr-2" />
                Try Again
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

// Suspense fallback loading component
export const AgentLoadingFallback: React.FC<{ 
  message?: string; 
  className?: string 
}> = ({ 
  message = 'Loading agent components...', 
  className = '' 
}) => (
  <div className={`flex items-center justify-center p-8 ${className}`}>
    <div className="text-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-gray-600">{message}</p>
    </div>
  </div>
);