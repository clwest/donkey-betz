import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StyleInsightsDashboard } from '../features/style-memory/StyleInsightsDashboard';
import { StyleLineageVisualization } from '../features/style-memory/StyleLineageVisualization';
import { useState } from 'react';

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden" style={{ backgroundColor: 'var(--gaming-bg-primary)' }}>
      {/* Gaming Background gradient mesh */}
      <div className="fixed inset-0 opacity-30 pointer-events-none" style={{ background: 'var(--gradient-mesh)' }} />
      
      {/* Gaming ambient glow overlay */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-20 left-20 w-96 h-96 rounded-full opacity-5" 
             style={{ background: 'radial-gradient(circle, var(--gaming-neon-cyan) 0%, transparent 70%)' }}></div>
        <div className="absolute bottom-20 right-20 w-80 h-80 rounded-full opacity-5" 
             style={{ background: 'radial-gradient(circle, var(--gaming-neon-purple) 0%, transparent 70%)' }}></div>
        <div className="absolute top-1/2 left-1/2 w-72 h-72 rounded-full opacity-3 transform -translate-x-1/2 -translate-y-1/2" 
             style={{ background: 'radial-gradient(circle, var(--gaming-neon-green) 0%, transparent 70%)' }}></div>
      </div>
      
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Page content with gaming styling */}
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