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
import { BettingPage } from './pages/betting/BettingPage';
import { StudioPage } from './pages/studio/StudioPage';
import { GalleryPage } from './pages/gallery/GalleryPage';
import { CampaignsPage } from './pages/campaigns/CampaignsPage';
import { CampaignDetailPage } from './pages/campaigns/CampaignDetailPage';
import { EbooksPage } from './pages/ebooks/EbooksPage';
import { VoicePage } from './pages/voice/VoicePage';
import { ResearchPage } from './pages/research/ResearchPage';
import { CharacterPage } from './pages/character/CharacterPage';
import { ProfilePage } from './pages/profile/ProfilePage';
import { FeedbackDashboard } from './pages/feedback/FeedbackDashboard';
import { AISettingsPage } from './pages/ai-settings/AISettingsPage';

// Public Pages
import { PublicBlogListPage } from './pages/public/PublicBlogListPage';
import { PublicBlogPage } from './pages/public/PublicBlogPage';
import LandingPage from './pages/public/LandingPage';
import BlogsPage from './pages/public/BlogsPage';

// User Pages
// import UserDashboard from './pages/user/UserDashboard'; // Removed to avoid dashboard conflict

// Sports Pages
import SportsAnalysisPage from './pages/sports/SportsAnalysisPage';

// Assistant Pages
import AssistantChatPage from './pages/assistant/AssistantChatPage';

// Prompt Diagnostics
import PromptDiagnosticsPage from './pages/prompt-diagnostics/PromptDiagnosticsPage';

// Agent Registry
import AgentRegistryPage from './pages/AgentRegistryPage';

// Multi-Agent Workflows
import MultiAgentWorkflowsPage from './pages/WorkflowsPage';

// Debug Page
import DebugPage from './pages/DebugPage';

// Connectivity
import { ConnectivityPage } from './pages/connectivity/ConnectivityPage';


// Sports
import { SportsBoardPage } from './features/sports/pages/SportsBoardPage';

// Agent Orchestra
import AgentOrchestrationPage from './pages/AgentOrchestrationPage';
import { OrchestraPage } from './features/agent-orchestra/pages/OrchestraPage';

// Mythology
import { MythologyDashboard } from './features/mythology/pages/MythologyDashboard';

// Auth Pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';
import ResetPasswordPage from './pages/auth/ResetPasswordPage';
import { AuthGuard } from './components/auth/AuthGuard';

// Features
import PersonalKnowledge from './components/features/personal-knowledge/PersonalKnowledge';
import { ChatWidget } from './components/Assistant';


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
          
          {/* Sports Analysis */}
          <Route path="/sports/analyze" element={<SportsAnalysisPage />} />
          
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
            <Route path="betting" element={<BettingPage />} />
            <Route path="studio" element={<StudioPage />} />
            <Route path="gallery" element={<GalleryPage />} />
            <Route path="campaigns">
              <Route index element={<CampaignsPage />} />
              <Route path=":id" element={<CampaignDetailPage />} />
              <Route path="new" element={<CampaignsPage />} />
            </Route>
            <Route path="ebooks" element={<EbooksPage />} />
            <Route path="voice" element={<VoicePage />} />
            <Route path="research" element={<ResearchPage />} />
            <Route path="character" element={<CharacterPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="feedback" element={<FeedbackDashboard />} />
            <Route path="ai-settings" element={<AISettingsPage />} />
            <Route path="knowledge" element={<PersonalKnowledge />} />
            <Route path="prompt-diagnostics" element={<PromptDiagnosticsPage />} />
            <Route path="agent-registry" element={<AgentRegistryPage />} />
            <Route path="workflows-multi" element={<MultiAgentWorkflowsPage />} />
            <Route path="connectivity" element={<ConnectivityPage />} />
            <Route path="sports/board" element={<SportsBoardPage />} />
            <Route path="agent-orchestra" element={<AgentOrchestrationPage />} />
            <Route path="orchestra" element={<OrchestraPage />} />
            <Route path="mythology" element={<MythologyDashboard />} />
            <Route path="debug" element={<DebugPage />} />
          </Route>
        </Routes>
        <CommandPalette />
        <ChatWidget />
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
