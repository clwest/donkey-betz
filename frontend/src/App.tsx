import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { usePAStore } from '@/stores/paStore'
import Layout from '@/components/layout/Layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import InboxPage from '@/pages/InboxPage'
import WorkspaceCreatePage from '@/pages/WorkspaceCreatePage'
import WorkspaceDashboardPage from '@/pages/WorkspaceDashboardPage'
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
import ProjectsPage from '@/pages/ProjectsPage'  // Project Hub: card grid
import ProjectHubPage from '@/pages/ProjectHubPage'  // Project Hub: detail view
import HowItWorksPage from '@/pages/HowItWorksPage'
import BoardroomPage from '@/pages/BoardroomPage'  // Session 1067: Full-page boardroom
import GovernancePage from '@/pages/GovernancePage'  // Session 1067: Full-page governance
import ExecutorPage from '@/pages/ExecutorPage'  // Session 1076: Executor runs UI
import MediaPage from '@/pages/MediaPage'
import VipAcceptPage from '@/pages/VipAcceptPage'

// Focus Cockpit — imports preserved for potential admin-bypass restore (Phase 1 consolidation)
// All cockpit routes now redirect to Workspace tabs. See cockpit/ directory for original pages.

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  const syncUser = usePAStore((s) => s.syncUser)

  // Sync PA store with current user — clears conversations if user changed
  syncUser(user?.id ?? null)

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
        <Route path="platform" element={<Navigate to="/workspace" replace />} />

        {/* Session 1067: Boardroom + governance now in Workspace tabs */}
        <Route path="boardroom" element={<Navigate to="/workspace?tab=boardroom" replace />} />
        <Route path="governance" element={<Navigate to="/workspace?tab=system" replace />} />

        {/* In-app messaging */}
        <Route path="inbox" element={<InboxPage />} />

        {/* Workspace creation wizard + dashboard */}
        <Route path="workspace/new" element={<WorkspaceCreatePage />} />
        <Route path="workspace/:workspaceId" element={<WorkspaceDashboardPage />} />

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
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="projects/:projectId" element={<ProjectHubPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="image-studio" element={<ImageStudioPage />} />
        <Route path="video-studio" element={<VideoStudioPage />} />
        <Route path="media" element={<MediaPage />} />
        <Route path="how-it-works" element={<HowItWorksPage />} />
        <Route path="executor" element={<ExecutorPage />} />
      </Route>

      {/* Focus Cockpit — hidden (Phase 1 of UI consolidation).
          Targeted redirects for high-priority pages, blanket catch-all for the rest.
          Cockpit code preserved in pages/cockpit/ — routes can be restored. */}
      <Route path="/cockpit/incidents/*" element={<Navigate to="/workspace?tab=system&sub=incidents" replace />} />
      <Route path="/cockpit/alerts" element={<Navigate to="/workspace?tab=system&sub=alerts" replace />} />
      <Route path="/cockpit/autopilot" element={<Navigate to="/workspace?tab=system&sub=autopilot" replace />} />
      <Route path="/cockpit/cost" element={<Navigate to="/workspace?tab=system&sub=cost" replace />} />
      <Route path="/cockpit/queues" element={<Navigate to="/workspace?tab=system&sub=queues" replace />} />
      <Route path="/cockpit/ops*" element={<Navigate to="/workspace?tab=system&sub=ops" replace />} />
      <Route path="/cockpit/errors/*" element={<Navigate to="/workspace?tab=system&sub=ops" replace />} />
      <Route path="/cockpit/runs/*" element={<Navigate to="/workspace?tab=system&sub=ops" replace />} />
      <Route path="/cockpit/library" element={<Navigate to="/workspace?tab=work&sub=deliverables" replace />} />
      <Route path="/cockpit/agents" element={<Navigate to="/workspace?tab=system&sub=ops" replace />} />
      <Route path="/cockpit/learning" element={<Navigate to="/workspace?tab=intelligence&sub=knowledge" replace />} />
      <Route path="/cockpit/config" element={<Navigate to="/workspace?tab=system&sub=config" replace />} />
      <Route path="/cockpit/audit" element={<Navigate to="/workspace?tab=system&sub=audit" replace />} />
      <Route path="/cockpit/approvals" element={<Navigate to="/workspace?tab=system&sub=boardroom" replace />} />
      <Route path="/cockpit/inbox" element={<Navigate to="/workspace?tab=home" replace />} />
      <Route path="/cockpit/*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  )
}

export default App
