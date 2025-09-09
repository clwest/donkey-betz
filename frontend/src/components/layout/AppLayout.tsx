import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StyleInsightsDashboard } from '../features/style-memory/StyleInsightsDashboard';
import { StyleLineageVisualization } from '../features/style-memory/StyleLineageVisualization';
import { useState } from 'react';

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-dark-900 overflow-hidden">
      {/* Background gradient mesh */}
      <div className="fixed inset-0 bg-gradient-mesh opacity-30 pointer-events-none" />
      
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Page content */}
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-6 py-8">
            <Outlet />
          </div>
        </main>
      </div>

      {/* Style Memory Overlays */}
      <StyleInsightsDashboard />
      <StyleLineageVisualization />
    </div>
  );
}