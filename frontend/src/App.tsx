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
        {/* Session 931: Unified Command Center replaces Home, Assistant, Human */}
        <Route index element={<CommandCenterPage />} />
        <Route path="assistant" element={<Navigate to="/" replace />} />
        <Route path="human" element={<Navigate to="/" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agents" element={<AgentsPage />} />
        <Route path="intelligence" element={<IntelligencePage />} />
        <Route path="content" element={<ContentPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="betting" element={<BettingPage />} />
        <Route path="legal" element={<LegalPage />} />
        <Route path="portfolio" element={<PortfolioPage />} />
        <Route path="stocks" element={<StockIntelligencePage />} />
        <Route path="admin" element={<AdminPage />} />
        <Route path="workspace" element={<WorkspacePage />} />

        {/* Standalone pages kept — distinct UI not duplicated in workspace */}
        <Route path="advisors" element={<AdvisorsPage />} />
        <Route path="neural-orchestra" element={<NeuralOrchestraPage />} />
        <Route path="conversation-contract" element={<ConversationContractPage />} />
        <Route path="mythology-lab" element={<MythologyLabPage />} />
        <Route path="billing" element={<BillingPage />} />
        <Route path="analytics" element={<AnalyticsDashboardPage />} />
        <Route path="docs-index" element={<DocsIndexPage />} />
        <Route path="blog/:blogId" element={<BlogViewerPage />} />

        {/* Session 971b C: Legacy routes → workspace tab redirects.
            Old bookmarks keep working for 2-4 weeks, then these can be removed. */}

        {/* → System tab */}
        <Route path="body-health" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="llm-routing" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="integration-health" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="orchestration" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="agent-monitor" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="autonomous" element={<Navigate to="/workspace?tab=system" replace />} />
        <Route path="hive-mind" element={<Navigate to="/workspace?tab=system" replace />} />

        {/* → DataIntel tab */}
        <Route path="spiders" element={<Navigate to="/workspace?tab=dataintel" replace />} />
        <Route path="spider-feed" element={<Navigate to="/workspace?tab=dataintel" replace />} />
        <Route path="reasoning" element={<Navigate to="/workspace?tab=dataintel" replace />} />
        <Route path="collective" element={<Navigate to="/workspace?tab=dataintel" replace />} />

        {/* → Content tab */}
        <Route path="podcast" element={<Navigate to="/workspace?tab=content" replace />} />
        <Route path="content-channels" element={<Navigate to="/workspace?tab=content" replace />} />
        <Route path="distribution" element={<Navigate to="/workspace?tab=content" replace />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="voice-marketplace" element={<Navigate to="/workspace?tab=content" replace />} />
        <Route path="blogs" element={<Navigate to="/workspace?tab=content" replace />} />

        {/* → Knowledge tab */}
        <Route path="memory-palace" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="evolution" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="agent-mood" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="time-capsules" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="time-travel" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="agent-social" element={<Navigate to="/workspace?tab=knowledge" replace />} />
        <Route path="relationships" element={<Navigate to="/workspace?tab=knowledge" replace />} />

        {/* → Learning tab */}
        <Route path="learning-journey" element={<Navigate to="/workspace?tab=learning" replace />} />
      </Route>
    </Routes>
  )
}

export default App
