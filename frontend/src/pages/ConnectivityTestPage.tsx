import React from 'react';
import { ConnectivityTest } from '@/components/ConnectivityTest';

export const ConnectivityTestPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">System Connectivity Test</h1>
        <p className="text-muted-foreground mb-6">
          Test connections to all backend services and verify API endpoints
        </p>
        <ConnectivityTest />
      </div>
    </div>
  );
};

export default ConnectivityTestPage;