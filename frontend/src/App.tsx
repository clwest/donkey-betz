import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { useEffect } from 'react';
import { Logger } from './utils/logger';

// Layout
import { AppLayout } from './components/layout/AppLayout';

// Pages
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { WorkflowsPage } from './pages/workflows/WorkflowsPage';
import { WorkflowBuilderPage } from './pages/workflows/WorkflowBuilderPage';
import { AgentsPage } from './pages/agents/AgentsPage';
// import { GameBettingPage } from './pages/betting/GameBettingPage'; // DISABLED - NO SPORTS
import { StudioPage } from './pages/studio/StudioPage';
import { GalleryPage } from './pages/gallery/GalleryPage';
import { EbooksPage } from './pages/ebooks/EbooksPage';
import { VoicePage } from './pages/voice/VoicePage';
import { CharacterPage } from './pages/character/CharacterPage';
import { ProfilePage } from './pages/profile/ProfilePage';
import { AISettingsPage } from './pages/ai-settings/AISettingsPage';

// Public Pages
import { PublicBlogListPage } from './pages/public/PublicBlogListPage';
import { PublicBlogPage } from './pages/public/PublicBlogPage';
import LandingPage from './pages/public/LandingPage';
import BlogsPage from './pages/public/BlogsPage';

// User Pages
// import UserDashboard from './pages/user/UserDashboard'; // Removed to avoid dashboard conflict

// Sports Pages - DISABLED
// import SportsAnalysisPage from './pages/sports/SportsAnalysisPage';

// Assistant Pages
import AssistantChatPage from './pages/assistant/AssistantChatPage';

// Unified Agent Orchestra Hub
import AgentOrchestraHub from './pages/AgentOrchestraHub';

// Universal Decision Command Center
import { DecisionDetailPage } from './pages/DecisionDetailPage';

// New UI/UX Components
import DecisionCommand from './components/DecisionCommand';
import NeuralOrchestra from './components/NeuralOrchestra';
import ControlCenter from './components/ControlCenter';
import { UnifiedAIAssistant } from './components/UnifiedAIAssistant';
import UnifiedCommandCenter from './components/UnifiedCommandCenter';

// Debug Page
import DebugPage from './pages/DebugPage';

// Connectivity
import { ConnectivityPage } from './pages/connectivity/ConnectivityPage';

// Sports - DISABLED
// import { SportsBoardPage } from './features/sports/pages/SportsBoardPage';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import { AuthGuard } from './components/auth/AuthGuard';

// Features
// Removed ChatWidget - now using UnifiedAIAssistant
import { LifeConvictionsPage } from './pages/life-convictions/LifeConvictionsPage';
import OpportunitiesHub from './components/OpportunitiesHub'; // Unified hub replacing Income Builder, Job Tracker, Decision Command
import MonetizationDashboard from './pages/MonetizationDashboard';
import RevenueOpportunities from './components/RevenueOpportunities';
import RevenueDashboard from './components/RevenueDashboard';
import RevenueCommandCenter from './components/RevenueCommandCenter';
import AIJobTrackerPage from './pages/AIJobTrackerPage';

// Stores
import { useAuthStore } from './store/authStore';
import { CommandPalette } from './components/common/CommandPalette';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  const { initAuth, isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    Logger.component('App', 'Mounting', { timestamp: new Date().toISOString() });
    Logger.component('App', 'Authentication already initialized from store');
    
    return () => {
      Logger.component('App', 'Unmounting');
    };
  }, []);

  console.log('🔐 App: Current auth state', { 
    isAuthenticated, 
    hasUser: !!user,
    pathname: window.location.pathname 
  });
  
  Logger.component('App', 'Rendering main application');

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/blogs" element={<BlogsPage />} />
          <Route path="/blog/:slug" element={<PublicBlogPage />} />
          
          {/* Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          
          {/* User Dashboard - Removed to avoid conflict with main dashboard */}
          
          {/* Sports Analysis - DISABLED
          <Route path="/sports/analyze" element={<SportsAnalysisPage />} /> */}
          
          {/* AI Assistant */}
          <Route path="/assistant/chat" element={<AssistantChatPage />} />
          
          {/* Legacy Public Blog Routes */}
          <Route path="/blog" element={<PublicBlogListPage />} />
          <Route path="/blog/:id" element={<PublicBlogPage />} />
          
          {/* Private App Routes */}
          <Route path="/" element={<AuthGuard><AppLayout /></AuthGuard>}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="workflows">
              <Route index element={<WorkflowsPage />} />
              <Route path="new" element={<WorkflowBuilderPage />} />
              <Route path=":id" element={<WorkflowBuilderPage />} />
            </Route>
            <Route path="agents" element={<AgentsPage />} />
            <Route path="command-center" element={<UnifiedCommandCenter />} />
            <Route path="decision/:domain/:decisionId" element={<DecisionDetailPage />} />

            {/* New Enhanced UI/UX Components */}
            <Route path="decision-command" element={<DecisionCommand />} />
            <Route path="neural-orchestra" element={<NeuralOrchestra />} />
            <Route path="control-center" element={<UnifiedCommandCenter />} />
            <Route path="studio" element={<StudioPage />} />
            <Route path="gallery" element={<GalleryPage />} />
            <Route path="ebooks" element={<EbooksPage />} />
            <Route path="voice" element={<VoicePage />} />
            <Route path="character" element={<CharacterPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="ai-settings" element={<AISettingsPage />} />
            
            {/* Unified Agent Orchestra Hub - replaces all individual agent pages */}
            <Route path="agent-hub" element={<AgentOrchestraHub />} />

            {/* Redirects for backwards compatibility */}
            {/* Agent Hub redirects */}
            <Route path="agent-registry" element={<Navigate to="/agent-hub" replace />} />
            <Route path="workflows-multi" element={<Navigate to="/agent-hub" replace />} />
            <Route path="agent-orchestra" element={<Navigate to="/agent-hub" replace />} />
            <Route path="orchestra" element={<Navigate to="/agent-hub" replace />} />
            <Route path="agent-channels" element={<Navigate to="/agent-hub" replace />} />

            {/* Decision Command Center redirects - consolidated pages */}
            <Route path="betting" element={<Navigate to="/income-builder" replace />} /> {/* Redirect to Income Builder instead */}
            <Route path="research" element={<Navigate to="/command-center" replace />} />
            <Route path="feedback" element={<Navigate to="/command-center" replace />} />
            <Route path="knowledge" element={<Navigate to="/command-center" replace />} />
            <Route path="prompt-diagnostics" element={<Navigate to="/command-center" replace />} />
            <Route path="mythology" element={<Navigate to="/command-center" replace />} />

            <Route path="connectivity" element={<ConnectivityPage />} />
            {/* <Route path="sports/board" element={<SportsBoardPage />} /> DISABLED - NO SPORTS */}
            <Route path="life-convictions" element={<LifeConvictionsPage />} />

            {/* Unified Opportunities Hub - combines Income Builder, Job Tracker, and Decision Command */}
            <Route path="opportunities" element={<OpportunitiesHub />} />
            <Route path="income-builder" element={<Navigate to="/opportunities" replace />} />
            <Route path="ai-job-tracker" element={<Navigate to="/opportunities" replace />} />
            <Route path="decision-command" element={<Navigate to="/opportunities" replace />} />

            <Route path="monetization" element={<UnifiedCommandCenter />} />
            <Route path="revenue-opportunities" element={<RevenueCommandCenter />} />
            <Route path="revenue-dashboard" element={<RevenueCommandCenter />} />
            <Route path="revenue" element={<RevenueCommandCenter />} />
            <Route path="debug" element={<DebugPage />} />
          </Route>
        </Routes>
        <CommandPalette />
        <UnifiedAIAssistant />
        <Toaster
          position="bottom-right"
          theme="dark"
          richColors
          expand
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App
