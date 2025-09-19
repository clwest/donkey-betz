import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useState } from 'react';

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background relative">
      {/* Gaming mesh background overlay */}
      <div className="fixed inset-0 bg-gradient-mesh opacity-30 pointer-events-none" />

      {/* Sidebar with enhanced styling */}
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main content area with glass morphism */}
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        {/* Header with enhanced styling */}
        <Header />

        {/* Page content with premium gaming styling */}
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-6 py-8 animate-fade-in">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}