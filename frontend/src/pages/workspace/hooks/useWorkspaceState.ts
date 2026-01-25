// Session 825: Centralized workspace state management
// Extracted from WorkspacePage.tsx for modular architecture

import { useState, useCallback } from 'react'
import type { WorkspaceTab, ActionResult } from '../types'
import type { DeliverableViewMode, Deliverable } from '@/components/workspace'

export interface WorkspaceState {
  // Tab navigation
  activeTab: WorkspaceTab
  setActiveTab: (tab: WorkspaceTab) => void

  // Modals
  showWorkspaceSelector: boolean
  setShowWorkspaceSelector: (show: boolean) => void
  showRegisterModal: boolean
  setShowRegisterModal: (show: boolean) => void
  showCommitModal: boolean
  setShowCommitModal: (show: boolean) => void
  showBranchModal: boolean
  setShowBranchModal: (show: boolean) => void
  showFileContent: boolean
  setShowFileContent: (show: boolean) => void

  // Files
  selectedFilePath: string | undefined
  setSelectedFilePath: (path: string | undefined) => void
  showFileHistory: boolean
  setShowFileHistory: (show: boolean) => void

  // Operations
  operationFilter: string
  setOperationFilter: (filter: string) => void
  selectedOperationId: string | null
  setSelectedOperationId: (id: string | null) => void
  reviewingOperationId: string | null
  setReviewingOperationId: (id: string | null) => void

  // Docs
  docsSearch: string
  setDocsSearch: (search: string) => void
  docsStatusFilter: string
  setDocsStatusFilter: (filter: string) => void
  docsTypeFilter: string
  setDocsTypeFilter: (filter: string) => void
  selectedDocPath: string | null
  setSelectedDocPath: (path: string | null) => void

  // Deliverables
  deliverablesMode: DeliverableViewMode
  setDeliverablesMode: (mode: DeliverableViewMode) => void
  selectedDeliverable: Deliverable | null
  setSelectedDeliverable: (deliverable: Deliverable | null) => void
  showTraceDrawer: boolean
  setShowTraceDrawer: (show: boolean) => void

  // UI State
  directoryMapExpanded: boolean
  setDirectoryMapExpanded: (expanded: boolean) => void
  expandedActivityIds: Set<string>
  toggleActivityExpanded: (id: string) => void

  // Document viewer
  viewerDocument: {
    path: string
    title: string
    category: string
    categoryColor: string
  } | null
  setViewerDocument: (doc: {
    path: string
    title: string
    category: string
    categoryColor: string
  } | null) => void

  // Action results (toasts)
  actionResult: ActionResult | null
  setActionResult: (result: ActionResult | null) => void
  showSuccess: (message: string) => void
  showError: (message: string) => void
}

export function useWorkspaceState(): WorkspaceState {
  // Tab navigation - default to Command for Platform Command Center
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('command')

  // Modal states
  const [showWorkspaceSelector, setShowWorkspaceSelector] = useState(false)
  const [showRegisterModal, setShowRegisterModal] = useState(false)
  const [showCommitModal, setShowCommitModal] = useState(false)
  const [showBranchModal, setShowBranchModal] = useState(false)
  const [showFileContent, setShowFileContent] = useState(false)

  // Files state
  const [selectedFilePath, setSelectedFilePath] = useState<string | undefined>()
  const [showFileHistory, setShowFileHistory] = useState(false)

  // Operations state
  const [operationFilter, setOperationFilter] = useState('')
  const [selectedOperationId, setSelectedOperationId] = useState<string | null>(null)
  const [reviewingOperationId, setReviewingOperationId] = useState<string | null>(null)

  // Docs state
  const [docsSearch, setDocsSearch] = useState('')
  const [docsStatusFilter, setDocsStatusFilter] = useState('')
  const [docsTypeFilter, setDocsTypeFilter] = useState('')
  const [selectedDocPath, setSelectedDocPath] = useState<string | null>(null)

  // Deliverables state
  const [deliverablesMode, setDeliverablesMode] = useState<DeliverableViewMode>('timeline')
  const [selectedDeliverable, setSelectedDeliverable] = useState<Deliverable | null>(null)
  const [showTraceDrawer, setShowTraceDrawer] = useState(false)

  // UI State
  const [directoryMapExpanded, setDirectoryMapExpanded] = useState(false)
  const [expandedActivityIds, setExpandedActivityIds] = useState<Set<string>>(new Set())

  // Document viewer
  const [viewerDocument, setViewerDocument] = useState<{
    path: string
    title: string
    category: string
    categoryColor: string
  } | null>(null)

  // Action results
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)

  // Toggle activity expansion
  const toggleActivityExpanded = useCallback((id: string) => {
    setExpandedActivityIds(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  // Helper functions for action results
  const showSuccess = useCallback((message: string) => {
    setActionResult({ type: 'success', message })
    setTimeout(() => setActionResult(null), 3000)
  }, [])

  const showError = useCallback((message: string) => {
    setActionResult({ type: 'error', message })
    setTimeout(() => setActionResult(null), 5000)
  }, [])

  return {
    // Tab navigation
    activeTab,
    setActiveTab,

    // Modals
    showWorkspaceSelector,
    setShowWorkspaceSelector,
    showRegisterModal,
    setShowRegisterModal,
    showCommitModal,
    setShowCommitModal,
    showBranchModal,
    setShowBranchModal,
    showFileContent,
    setShowFileContent,

    // Files
    selectedFilePath,
    setSelectedFilePath,
    showFileHistory,
    setShowFileHistory,

    // Operations
    operationFilter,
    setOperationFilter,
    selectedOperationId,
    setSelectedOperationId,
    reviewingOperationId,
    setReviewingOperationId,

    // Docs
    docsSearch,
    setDocsSearch,
    docsStatusFilter,
    setDocsStatusFilter,
    docsTypeFilter,
    setDocsTypeFilter,
    selectedDocPath,
    setSelectedDocPath,

    // Deliverables
    deliverablesMode,
    setDeliverablesMode,
    selectedDeliverable,
    setSelectedDeliverable,
    showTraceDrawer,
    setShowTraceDrawer,

    // UI State
    directoryMapExpanded,
    setDirectoryMapExpanded,
    expandedActivityIds,
    toggleActivityExpanded,

    // Document viewer
    viewerDocument,
    setViewerDocument,

    // Action results
    actionResult,
    setActionResult,
    showSuccess,
    showError,
  }
}
