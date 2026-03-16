import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import Layout from '@/components/layout/Layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import CommandCenterPage from '@/pages/CommandCenterPage'  // Session 931: Unified Command Center
import AgentsPage from '@/pages/AgentsPage'
import IntelligencePage from '@/pages/IntelligencePage'
import ContentPage from '@/pages/ContentPage'
import SettingsPage from '@/pages/SettingsPage'
import ProfilePage from '@/pages/ProfilePage'
import BettingPage from '@/pages/BettingPage'
import LegalPage from '@/pages/LegalPage'
import PortfolioPage from '@/pages/PortfolioPage'
import AdminPage from '@/pages/AdminPage'
import WorkspacePage from '@/pages/WorkspacePageNew'  // Session 825: New modular workspace
import PlatformPage from '@/pages/PlatformPage'  // Session 1035: System-wide dashboard
import AdvisorsPage from '@/pages/AdvisorsPage'
import NeuralOrchestraPage from '@/pages/NeuralOrchestraPage'
import ConversationContractPage from '@/pages/ConversationContractPage'
import MythologyLabPage from '@/pages/MythologyLabPage'
import BlogViewerPage from '@/pages/BlogViewerPage'  // Session 742: Blog viewer for content review
import BillingPage from '@/pages/BillingPage'  // Session 745: Billing & subscriptions
import AnalyticsDashboardPage from '@/pages/AnalyticsDashboardPage'  // Session 745: Analytics dashboard
import DocsIndexPage from '@/pages/DocsIndexPage'  // Session 784: Documentation Index Browser
import StockIntelligencePage from '@/pages/StockIntelligencePage'
import DocumentsPage from '@/pages/DocumentsPage'
import ImageStudioPage from '@/pages/ImageStudioPage'
import VideoStudioPage from '@/pages/VideoStudioPage'
import GovernmentPage from '@/pages/GovernmentPage'
import ReviewPortalPage from '@/pages/ReviewPortalPage'  // Preview System: Public review portal
import DemoHomePage from '@/pages/DemoHomePage'  // BPaaS: Platform overview + demo dashboard
import DeliverablesPage from '@/pages/DeliverablesPage'  // Deliverables library
import HowItWorksPage from '@/pages/HowItWorksPage'
import BoardroomPage from '@/pages/BoardroomPage'  // Session 1067: Full-page boardroom
import GovernancePage from '@/pages/GovernancePage'  // Session 1067: Full-page governance
import ExecutorPage from '@/pages/ExecutorPage'  // Session 1076: Executor runs UI
import MediaPage from '@/pages/MediaPage'
import VipAcceptPage from '@/pages/VipAcceptPage'

// Focus Cockpit
import CockpitLayout from '@/components/cockpit/CockpitLayout'
import CockpitHomePage from '@/pages/cockpit/HomePage'
import CockpitInboxPage from '@/pages/cockpit/InboxPage'
import CockpitCreateHubPage from '@/pages/cockpit/CreateHubPage'
import CockpitCreateFlowPage from '@/pages/cockpit/CreateFlowPage'
import CockpitRunsPage from '@/pages/cockpit/RunsPage'
import CockpitRunDetailPage from '@/pages/cockpit/RunDetailPage'
import CockpitLibraryPage from '@/pages/cockpit/LibraryPage'
import CockpitErrorsPage from '@/pages/cockpit/ErrorsPage'
import CockpitErrorDetailPage from '@/pages/cockpit/ErrorDetailPage'
import CockpitOpsPage from '@/pages/cockpit/OpsPage'
import CockpitApprovalsPage from '@/pages/cockpit/ApprovalsPage'
import CockpitAlertsPage from '@/pages/cockpit/AlertsPage'
import CockpitAuditLogPage from '@/pages/cockpit/AuditLogPage'
import CockpitAgentsPage from '@/pages/cockpit/AgentsPage'
import CockpitQueuesPage from '@/pages/cockpit/QueuesPage'
import CockpitCostPage from '@/pages/cockpit/CostPage'
import CockpitAutopilotPage from '@/pages/cockpit/AutopilotPage'
import CockpitRunTracePage from '@/pages/cockpit/RunTracePage'
import CockpitConfigPage from '@/pages/cockpit/ConfigPage'
import CockpitIncidentsPage from '@/pages/cockpit/IncidentsPage'
import CockpitIncidentDetailPage from '@/pages/cockpit/IncidentDetailPage'
import CockpitOpsRunsPage from '@/pages/cockpit/OpsRunsPage'
import CockpitOpsRunDetailPage from '@/pages/cockpit/OpsRunDetailPage'
import CockpitObsPage from '@/pages/cockpit/ObsPage'

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
      <Route path="/vip/accept" element={<VipAcceptPage />} />
      <Route path="/r/:token" element={<ReviewPortalPage />} />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        {/* Session 931: Unified Command Center replaces Home, Assistant, Human */}
        <Route index element={<CommandCenterPage />} />
        <Route path="assistant" element={<Navigate to="/" replace />} />
        <Route path="human" element={<Navigate to="/" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="demo" element={<DemoHomePage />} />
        <Route path="agents" element={<AgentsPage />} />
        <Route path="intelligence" element={<IntelligencePage />} />
        <Route path="content" element={<ContentPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="betting" element={<BettingPage />} />
        <Route path="legal" element={<LegalPage />} />
        <Route path="portfolio" element={<PortfolioPage />} />
        <Route path="stocks" element={<StockIntelligencePage />} />
        <Route path="government" element={<GovernmentPage />} />
        <Route path="admin" element={<AdminPage />} />
        <Route path="workspace" element={<WorkspacePage />} />
        <Route path="platform" element={<PlatformPage />} />

        {/* Session 1067: Full-page boardroom + governance */}
        <Route path="boardroom" element={<BoardroomPage />} />
        <Route path="governance" element={<GovernancePage />} />

        {/* Standalone pages kept — distinct UI not duplicated in workspace */}
        <Route path="advisors" element={<AdvisorsPage />} />
        <Route path="neural-orchestra" element={<NeuralOrchestraPage />} />
        <Route path="conversation-contract" element={<ConversationContractPage />} />
        <Route path="mythology-lab" element={<MythologyLabPage />} />
        <Route path="billing" element={<BillingPage />} />
        <Route path="analytics" element={<AnalyticsDashboardPage />} />
        <Route path="docs-index" element={<DocsIndexPage />} />
        <Route path="blog/:blogId" element={<BlogViewerPage />} />

        {/* Standalone content pages */}
        <Route path="deliverables" element={<DeliverablesPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="image-studio" element={<ImageStudioPage />} />
        <Route path="video-studio" element={<VideoStudioPage />} />
        <Route path="media" element={<MediaPage />} />
        <Route path="how-it-works" element={<HowItWorksPage />} />
        <Route path="executor" element={<ExecutorPage />} />
      </Route>

      {/* Focus Cockpit — solo-operator flow */}
      <Route path="/cockpit" element={<ProtectedRoute><CockpitLayout /></ProtectedRoute>}>
        <Route index element={<CockpitHomePage />} />
        <Route path="inbox" element={<CockpitInboxPage />} />
        <Route path="create" element={<CockpitCreateHubPage />} />
        <Route path="create/:recipeId" element={<CockpitCreateFlowPage />} />
        <Route path="runs" element={<CockpitRunsPage />} />
        <Route path="runs/:runId" element={<CockpitRunDetailPage />} />
        <Route path="runs/:runId/trace" element={<CockpitRunTracePage />} />
        <Route path="library" element={<CockpitLibraryPage />} />
        <Route path="errors" element={<CockpitErrorsPage />} />
        <Route path="errors/:signatureId" element={<CockpitErrorDetailPage />} />
        <Route path="ops" element={<CockpitOpsPage />} />
        <Route path="approvals" element={<CockpitApprovalsPage />} />
        <Route path="alerts" element={<CockpitAlertsPage />} />
        <Route path="audit" element={<CockpitAuditLogPage />} />
        <Route path="agents" element={<CockpitAgentsPage />} />
        <Route path="queues" element={<CockpitQueuesPage />} />
        <Route path="cost" element={<CockpitCostPage />} />
        <Route path="autopilot" element={<CockpitAutopilotPage />} />
        <Route path="config" element={<CockpitConfigPage />} />
        <Route path="incidents" element={<CockpitIncidentsPage />} />
        <Route path="incidents/:incidentId" element={<CockpitIncidentDetailPage />} />
        <Route path="obs" element={<CockpitObsPage />} />
        <Route path="ops-runs" element={<CockpitOpsRunsPage />} />
        <Route path="ops-runs/:runId" element={<CockpitOpsRunDetailPage />} />
      </Route>
    </Routes>
  )
}

export default App
