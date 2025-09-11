/**
 * Mythology Feature Exports
 * Central export point for mythology review system components and API
 */

// Pages
export { MythologyDashboard } from './pages/MythologyDashboard';

// Components
export { FlaggedContentTable } from './components/FlaggedContentTable';
export { ReviewModal } from './components/ReviewModal';
export { AlertNotifications } from './components/AlertNotifications';
export { UserReportButton, useReportContentModal } from './components/UserReportButton';

// API & Types
export {
  // API functions
  default as mythologyAPI,
  
  // Query hooks
  useMythologyStats,
  useFlaggedContent,
  useFlaggedContentDetail,
  useNotifications,
  useSubmitReview,
  useReportContent,
  useMarkNotificationRead,
  useMarkAllNotificationsRead,
  useMythologyWebSocket,
  
  // Query keys
  mythologyKeys,
  
  // Types
  type FlaggedContent,
  type ReviewAction,
  type ReportContent,
  type MythologyStats,
  type AlertNotification,
} from './api/mythology';