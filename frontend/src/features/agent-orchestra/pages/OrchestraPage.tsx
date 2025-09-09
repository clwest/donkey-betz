/**
 * Orchestra Page
 * 
 * Main page for the Agent Orchestra feature, providing a unified interface for:
 * - Agent orchestration and management
 * - Real-time monitoring and status
 * - WebSocket connectivity testing
 * - Integration with the shared WebSocket client
 */

import React, { Suspense } from 'react';
import { motion } from 'framer-motion';
import { 
  CpuChipIcon, 
  InformationCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

import { Card } from '../../../components/common/Card';
import { LoadingSpinner } from '../../../components/common/LoadingSpinner';
import { PokerVloggerPanel } from '../../../components/agents/PokerVloggerPanel';
import { OrchestraPanel } from '../components/OrchestraPanel';

import { Logger } from '../../../utils/logger';
import { toast } from 'sonner';

// Error boundary for the Orchestra feature
class OrchestraErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    Logger.error('Orchestra Page', { 
      message: 'Component error boundary triggered', 
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <Card className="p-8 border-red-500/20 bg-red-500/5">
          <div className="text-center">
            <ExclamationTriangleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-400 mb-2">
              Agent Orchestra Error
            </h2>
            <p className="text-red-300 mb-4">
              An unexpected error occurred while loading the Agent Orchestra interface.
            </p>
            <p className="text-sm text-red-400 font-mono bg-red-950/50 p-3 rounded">
              {this.state.error?.message || 'Unknown error'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: undefined });
                window.location.reload();
              }}
              className="mt-4 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
            >
              Reload Page
            </button>
          </div>
        </Card>
      );
    }

    return this.props.children;
  }
}

// Loading fallback component
const OrchestraLoadingFallback: React.FC = () => (
  <Card className="p-8">
    <div className="text-center">
      <LoadingSpinner size="lg" />
      <p className="mt-4 text-muted-foreground">
        Loading Agent Orchestra interface...
      </p>
    </div>
  </Card>
);

export const OrchestraPage: React.FC = () => {
  const handleInstanceCreate = (instance: any) => {
    Logger.debug('Orchestra Page', `New instance created: ${instance?.id || 'unknown'}`);
    const displayName = instance?.template?.name || (instance?.id ? instance.id.slice(0, 8) : 'Task');
    toast.success(`Agent task started: ${displayName}`);
  };

  const handleInstanceUpdate = (instance: any) => {
    Logger.debug('Orchestra Page', `Instance updated: ${instance?.id || 'unknown'} - ${instance?.status}`);
    
    const displayName = instance?.template?.name || (instance?.id ? instance.id.slice(0, 8) : 'Task');
    
    if (instance?.status === 'completed') {
      toast.success(`Task completed: ${displayName}`);
    } else if (instance?.status === 'failed') {
      toast.error(`Task failed: ${displayName}`);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Page Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground flex items-center">
              <CpuChipIcon className="h-8 w-8 mr-3 text-primary" />
              Agent Orchestra
            </h1>
            <p className="mt-2 text-muted-foreground">
              Unified AI agent orchestration with real-time monitoring and WebSocket connectivity
            </p>
          </div>
        </div>
      </motion.div>

      {/* Main Orchestra Interface */}
      <OrchestraErrorBoundary>
        <Suspense fallback={<OrchestraLoadingFallback />}>
          <OrchestraPanel
            onInstanceCreate={handleInstanceCreate}
            onInstanceUpdate={handleInstanceUpdate}
          />
        </Suspense>
      </OrchestraErrorBoundary>

      {/* Poker Vlogger Agent Demo */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-8"
      >
        <PokerVloggerPanel />
      </motion.div>

      {/* Connection Information */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mt-8"
      >
        <Card className="p-4">
          <h3 className="text-sm font-medium text-foreground mb-2 flex items-center">
            <InformationCircleIcon className="h-4 w-4 mr-2 text-primary" />
            Connection Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-muted-foreground">
            <div>
              <span className="font-medium">REST API:</span>
              <span className="ml-2 font-mono">
                {import.meta.env.VITE_API_URL || 'http://localhost:8001/api'}
              </span>
            </div>
            <div>
              <span className="font-medium">WebSocket:</span>
              <span className="ml-2 font-mono">
                {import.meta.env.VITE_WS_URL || 'ws://localhost:8001'}/ws/assistant/
              </span>
            </div>
            <div>
              <span className="font-medium">Environment:</span>
              <span className="ml-2 font-mono">{import.meta.env.MODE}</span>
            </div>
            <div>
              <span className="font-medium">DBAO API:</span>
              <span className="ml-2 font-mono">
                {import.meta.env.VITE_DBAO_API_URL || 'http://localhost:8001/api'}
              </span>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
};