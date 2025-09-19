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
import { AISettingsPageUnified } from './pages/ai-settings/AISettingsPageUnified';
import { ControlCenterPage } from './pages/control-center/ControlCenterPage';

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
// UnifiedAIAssistant now wrapped in SafeAIAssistant
import UserCommandCenter from './components/UserCommandCenter';

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
// Removed ChatWidget - now using SafeAIAssistant
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
import { SafeAIAssistant } from './components/SafeAIAssistant';

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
            <Route path="command-center" element={<UserCommandCenter defaultTab="profile" />} />
            <Route path="decision/:domain/:decisionId" element={<DecisionDetailPage />} />

            {/* New Enhanced UI/UX Components */}
            <Route path="decision-command" element={<DecisionCommand />} />
            <Route path="neural-orchestra" element={<NeuralOrchestra />} />
            <Route path="control-center" element={<ControlCenterPage />} />
            <Route path="studio" element={<StudioPage />} />
            <Route path="gallery" element={<GalleryPage />} />
            <Route path="ebooks" element={<EbooksPage />} />
            <Route path="voice" element={<VoicePage />} />
            <Route path="character" element={<CharacterPage />} />
            <Route path="profile" element={<Navigate to="/command-center" state={{ tab: 'profile' }} />} />
            <Route path="ai-settings" element={<AISettingsPageUnified />} />
            
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

            {/* Unified Command Center Redirects */}
            <Route path="opportunities" element={<Navigate to="/command-center" state={{ tab: 'opportunities' }} />} />
            <Route path="income-builder" element={<Navigate to="/command-center" state={{ tab: 'opportunities' }} />} />
            <Route path="ai-job-tracker" element={<Navigate to="/command-center" state={{ tab: 'opportunities' }} />} />
            <Route path="decision-command" element={<Navigate to="/command-center" state={{ tab: 'opportunities' }} />} />

            <Route path="monetization" element={<Navigate to="/command-center" state={{ tab: 'revenue' }} />} />
            <Route path="revenue-opportunities" element={<Navigate to="/command-center" state={{ tab: 'revenue' }} />} />
            <Route path="revenue-dashboard" element={<Navigate to="/command-center" state={{ tab: 'revenue' }} />} />
            <Route path="revenue" element={<Navigate to="/command-center" state={{ tab: 'revenue' }} />} />
            <Route path="debug" element={<DebugPage />} />
          </Route>
        </Routes>
        <CommandPalette />
        <SafeAIAssistant />
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
