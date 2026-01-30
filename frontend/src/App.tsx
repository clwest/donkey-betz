import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import Layout from '@/components/layout/Layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import AssistantPage from '@/pages/AssistantPage'
import AgentsPage from '@/pages/AgentsPage'
import IntelligencePage from '@/pages/IntelligencePage'
import ContentPage from '@/pages/ContentPage'
import SettingsPage from '@/pages/SettingsPage'
import ProfilePage from '@/pages/ProfilePage'
import BettingPage from '@/pages/BettingPage'
import LegalPage from '@/pages/LegalPage'
import PodcastPage from '@/pages/PodcastPage'
import PortfolioPage from '@/pages/PortfolioPage'
import AdminPage from '@/pages/AdminPage'
import HumanPage from '@/pages/HumanPage'
import WorkspacePage from '@/pages/WorkspacePageNew'  // Session 825: New modular workspace
import LLMRoutingPage from '@/pages/LLMRoutingPage'
import BodyHealthPage from '@/pages/BodyHealthPage'
import HiveMindPage from '@/pages/HiveMindPage'
import MemoryPalacePage from '@/pages/MemoryPalacePage'
import EvolutionPage from '@/pages/EvolutionPage'
import AgentMoodPage from '@/pages/AgentMoodPage'
import TimeCapsulePage from '@/pages/TimeCapsulePage'
import TimeTravelPage from '@/pages/TimeTravelPage'
import AgentSocialPage from '@/pages/AgentSocialPage'
import AdvisorsPage from '@/pages/AdvisorsPage'
import RelationshipsPage from '@/pages/RelationshipsPage'
import NeuralOrchestraPage from '@/pages/NeuralOrchestraPage'
import ConversationContractPage from '@/pages/ConversationContractPage'
import SpiderIntegrationPage from '@/pages/SpiderIntegrationPage'
import DocumentsPage from '@/pages/DocumentsPage'
import MythologyLabPage from '@/pages/MythologyLabPage'
import ContentChannelsPage from '@/pages/ContentChannelsPage'
import BlogViewerPage from '@/pages/BlogViewerPage'  // Session 742: Blog viewer for content review
import BlogsPage from '@/pages/BlogsPage'  // Session 814: Dedicated blogs list page
import DistributionPage from '@/pages/DistributionPage'  // Session 745: Distribution dashboard
import AutonomousSystemsPage from '@/pages/AutonomousSystemsPage'  // Session 745: Autonomous systems
import ReasoningEnginePage from '@/pages/ReasoningEnginePage'  // Session 745: Reasoning engine
import VoiceMarketplacePage from '@/pages/VoiceMarketplacePage'  // Session 745: Voice marketplace
import BillingPage from '@/pages/BillingPage'  // Session 745: Billing & subscriptions
import LearningJourneyPage from '@/pages/LearningJourneyPage'  // Session 745: Learning journeys
import CollectiveIntelligencePage from '@/pages/CollectiveIntelligencePage'  // Session 745: Collective intelligence
import AnalyticsDashboardPage from '@/pages/AnalyticsDashboardPage'  // Session 745: Analytics dashboard
import IntegrationHealthPage from '@/pages/IntegrationHealthPage'  // Session 758: Integration observability
import OrchestrationPage from '@/pages/OrchestrationPage'  // Session 768: Orchestration layer UI
import SpiderFeedPage from '@/pages/SpiderFeedPage'  // Session 783: Spider News Feed
import DocsIndexPage from '@/pages/DocsIndexPage'  // Session 784: Documentation Index Browser
import AgentMonitorPage from '@/pages/AgentMonitorPage'  // Session 794: Live Agent Monitor
import HomePage from '@/pages/HomePage'  // Session 884: AI OS Boot Experience

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Session 884: Home page is the AI OS boot experience */}
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="assistant" element={<AssistantPage />} />
        <Route path="agents" element={<AgentsPage />} />
        <Route path="intelligence" element={<IntelligencePage />} />
        <Route path="content" element={<ContentPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="betting" element={<BettingPage />} />
        <Route path="legal" element={<LegalPage />} />
        <Route path="podcast" element={<PodcastPage />} />
        <Route path="content-channels" element={<ContentChannelsPage />} />
        <Route path="portfolio" element={<PortfolioPage />} />
        <Route path="admin" element={<AdminPage />} />
        <Route path="llm-routing" element={<LLMRoutingPage />} />
        <Route path="human" element={<HumanPage />} />
        <Route path="workspace" element={<WorkspacePage />} />
        <Route path="body-health" element={<BodyHealthPage />} />
        <Route path="hive-mind" element={<HiveMindPage />} />
        <Route path="memory-palace" element={<MemoryPalacePage />} />
        <Route path="evolution" element={<EvolutionPage />} />
        <Route path="agent-mood" element={<AgentMoodPage />} />
        <Route path="time-capsules" element={<TimeCapsulePage />} />
        <Route path="time-travel" element={<TimeTravelPage />} />
        <Route path="agent-social" element={<AgentSocialPage />} />
        <Route path="advisors" element={<AdvisorsPage />} />
        <Route path="relationships" element={<RelationshipsPage />} />
        <Route path="neural-orchestra" element={<NeuralOrchestraPage />} />
        <Route path="conversation-contract" element={<ConversationContractPage />} />
        <Route path="spiders" element={<SpiderIntegrationPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="mythology-lab" element={<MythologyLabPage />} />
        <Route path="distribution" element={<DistributionPage />} />  {/* Session 745: Distribution dashboard */}
        <Route path="autonomous" element={<AutonomousSystemsPage />} />  {/* Session 745: Autonomous systems */}
        <Route path="reasoning" element={<ReasoningEnginePage />} />  {/* Session 745: Reasoning engine */}
        <Route path="voice-marketplace" element={<VoiceMarketplacePage />} />  {/* Session 745: Voice marketplace */}
        <Route path="billing" element={<BillingPage />} />  {/* Session 745: Billing & subscriptions */}
        <Route path="learning-journey" element={<LearningJourneyPage />} />  {/* Session 745: Learning journeys */}
        <Route path="collective" element={<CollectiveIntelligencePage />} />  {/* Session 745: Collective intelligence */}
        <Route path="analytics" element={<AnalyticsDashboardPage />} />  {/* Session 745: Analytics dashboard */}
        <Route path="integration-health" element={<IntegrationHealthPage />} />  {/* Session 758: Integration observability */}
        <Route path="orchestration" element={<OrchestrationPage />} />  {/* Session 768: Orchestration layer */}
        <Route path="spider-feed" element={<SpiderFeedPage />} />  {/* Session 783: Spider News Feed */}
        <Route path="docs-index" element={<DocsIndexPage />} />  {/* Session 784: Documentation Index Browser */}
        <Route path="agent-monitor" element={<AgentMonitorPage />} />  {/* Session 794: Live Agent Monitor */}
        <Route path="blogs" element={<BlogsPage />} />  {/* Session 814: Blogs list page */}
        <Route path="blog/:blogId" element={<BlogViewerPage />} />  {/* Session 742: Blog viewer for content review */}
      </Route>
    </Routes>
  )
}

export default App
