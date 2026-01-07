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
import WorkspacePage from '@/pages/WorkspacePage'
import LLMRoutingPage from '@/pages/LLMRoutingPage'
import BodyHealthPage from '@/pages/BodyHealthPage'
import HiveMindPage from '@/pages/HiveMindPage'
import MemoryPalacePage from '@/pages/MemoryPalacePage'
import EvolutionPage from '@/pages/EvolutionPage'
import AgentMoodPage from '@/pages/AgentMoodPage'
import TimeCapsulePage from '@/pages/TimeCapsulePage'
import TimeTravelPage from '@/pages/TimeTravelPage'

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
        <Route index element={<Navigate to="/dashboard" replace />} />
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
      </Route>
    </Routes>
  )
}

export default App
