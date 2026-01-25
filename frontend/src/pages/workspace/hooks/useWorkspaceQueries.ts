// Session 825: Centralized workspace queries
// Extracted from WorkspacePage.tsx for modular architecture

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useCallback } from 'react'
import {
  workspaceApi,
  workspaceOperationsApi,
  bodyApi,
  docsIndexApi,
  platformApi,
} from '@/lib/api'
import { useAuthStore } from '@/stores/authStore'
import { useSystemEvents } from '@/hooks/useWebSocket'
import type { Workspace, WorkspaceTab } from '../types'

interface UseWorkspaceQueriesOptions {
  activeTab: WorkspaceTab
  activeWorkspaceId?: string
  selectedFilePath?: string
  showFileHistory?: boolean
  selectedOperationId?: string | null
  showFileContent?: boolean
  docsSearch?: string
  docsStatusFilter?: string
  docsTypeFilter?: string
  selectedDocPath?: string | null
  workspaceSearchTerms?: string
}

export function useWorkspaceQueries(options: UseWorkspaceQueriesOptions) {
  const {
    activeTab,
    activeWorkspaceId,
    selectedFilePath,
    showFileHistory = false,
    selectedOperationId,
    showFileContent = false,
    docsSearch = '',
    docsStatusFilter = '',
    docsTypeFilter = '',
    selectedDocPath,
    workspaceSearchTerms = '',
  } = options

  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuthStore()

  // Real-time event handlers
  const handleFileModified = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['workspace-files'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-git-status'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
  }, [queryClient])

  const handleAgentExecution = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
    queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
  }, [queryClient])

  // Subscribe to system events
  const { status: wsStatus } = useSystemEvents({
    onFileModified: handleFileModified,
    onAgentExecutionComplete: handleAgentExecution,
  })

  // ============ Core Workspace Queries ============

  const workspacesQuery = useQuery({
    queryKey: ['workspaces'],
    queryFn: () => workspaceApi.list(),
    retry: false,
    enabled: isAuthenticated,
  })

  const activeWorkspaceQuery = useQuery({
    queryKey: ['workspace-active'],
    queryFn: () => workspaceApi.getActive(),
    retry: false,
    enabled: isAuthenticated,
  })

  const dashboardQuery = useQuery({
    queryKey: ['workspace-dashboard'],
    queryFn: () => workspaceApi.dashboard(),
    retry: false,
    enabled: isAuthenticated,
  })

  const statsQuery = useQuery({
    queryKey: ['workspace-stats', activeWorkspaceId],
    queryFn: () => activeWorkspaceId ? workspaceApi.stats(activeWorkspaceId) : null,
    enabled: !!activeWorkspaceId,
  })

  // ============ Git Queries ============

  const gitStatusQuery = useQuery({
    queryKey: ['workspace-git-status', activeWorkspaceId],
    queryFn: () => activeWorkspaceId ? workspaceApi.gitStatus(activeWorkspaceId) : null,
    enabled: !!activeWorkspaceId && activeTab === 'files',
  })

  // ============ Files Queries ============

  const filesQuery = useQuery({
    queryKey: ['workspace-files', activeWorkspaceId],
    queryFn: () => activeWorkspaceId ? workspaceApi.files(activeWorkspaceId, '**/*') : null,
    enabled: !!activeWorkspaceId && activeTab === 'files',
  })

  const fileContentQuery = useQuery({
    queryKey: ['workspace-file', activeWorkspaceId, selectedFilePath],
    queryFn: () => activeWorkspaceId && selectedFilePath
      ? workspaceApi.readFile(activeWorkspaceId, selectedFilePath)
      : null,
    enabled: !!activeWorkspaceId && !!selectedFilePath,
  })

  const fileHistoryQuery = useQuery({
    queryKey: ['workspace-file-history', activeWorkspaceId, selectedFilePath],
    queryFn: () => activeWorkspaceId && selectedFilePath
      ? workspaceApi.fileHistory(activeWorkspaceId, selectedFilePath)
      : null,
    enabled: !!activeWorkspaceId && !!selectedFilePath && showFileHistory,
  })

  // ============ Operations Queries ============

  const operationsQuery = useQuery({
    queryKey: ['workspace-operations', activeWorkspaceId],
    queryFn: () => activeWorkspaceId ? workspaceApi.operations(activeWorkspaceId) : null,
    enabled: !!activeWorkspaceId,
  })

  const pendingReviewsQuery = useQuery({
    queryKey: ['workspace-pending-reviews'],
    queryFn: () => workspaceOperationsApi.pendingReviews(),
    enabled: activeTab === 'operations',
    retry: false,
  })

  const operationDetailQuery = useQuery({
    queryKey: ['workspace-operation-detail', selectedOperationId],
    queryFn: () => selectedOperationId
      ? workspaceOperationsApi.detail(selectedOperationId)
      : null,
    enabled: !!selectedOperationId && showFileContent,
  })

  // ============ Body Health Query ============

  const bodyVitalsQuery = useQuery({
    queryKey: ['body-vitals'],
    queryFn: () => bodyApi.vitals(),
    refetchInterval: 60000,
  })

  // ============ Docs Queries ============

  const docsQuery = useQuery({
    queryKey: ['workspace-docs', docsSearch || workspaceSearchTerms, docsStatusFilter, docsTypeFilter],
    queryFn: async () => {
      const params: Record<string, string> = {}
      const searchTerm = docsSearch || workspaceSearchTerms
      if (searchTerm) params.search = searchTerm
      if (docsStatusFilter) params.status = docsStatusFilter
      if (docsTypeFilter) params.type = docsTypeFilter
      params.limit = '50'
      const res = await docsIndexApi.index(params)
      return res.data
    },
    enabled: activeTab === 'knowledge',
  })

  const docsStatsQuery = useQuery({
    queryKey: ['docs-stats'],
    queryFn: async () => {
      const res = await docsIndexApi.stats()
      return res.data
    },
    enabled: activeTab === 'knowledge',
  })

  const selectedDocQuery = useQuery({
    queryKey: ['docs-detail', selectedDocPath],
    queryFn: async () => {
      const res = await docsIndexApi.detail(selectedDocPath!)
      return res.data
    },
    enabled: !!selectedDocPath && activeTab === 'knowledge',
  })

  // ============ Platform Command Center Queries ============

  const missionQuery = useQuery({
    queryKey: ['platform-mission'],
    queryFn: async () => {
      const res = await platformApi.mission()
      return res.data
    },
    enabled: activeTab === 'command',
  })

  const metricsQuery = useQuery({
    queryKey: ['platform-metrics'],
    queryFn: async () => {
      const res = await platformApi.metrics()
      return res.data
    },
    enabled: activeTab === 'command',
  })

  const governanceQuery = useQuery({
    queryKey: ['platform-governance'],
    queryFn: async () => {
      const res = await platformApi.governance()
      return res.data
    },
    enabled: activeTab === 'governance' || activeTab === 'command',
  })

  const canonQuery = useQuery({
    queryKey: ['platform-canon'],
    queryFn: async () => {
      const res = await platformApi.canon()
      return res.data
    },
    enabled: activeTab === 'knowledge',
  })

  const playbooksQuery = useQuery({
    queryKey: ['platform-playbooks'],
    queryFn: async () => {
      const res = await platformApi.playbooks()
      return res.data
    },
    enabled: activeTab === 'knowledge',
  })

  const auditsQuery = useQuery({
    queryKey: ['platform-audits'],
    queryFn: async () => {
      const res = await platformApi.audits()
      return res.data
    },
    enabled: activeTab === 'knowledge',
  })

  // Extract data
  const activeWorkspace = activeWorkspaceQuery.data?.data as Workspace | undefined
  const workspaces = (workspacesQuery.data?.data?.results || workspacesQuery.data?.data || []) as Workspace[]

  return {
    // WebSocket status
    wsStatus,

    // Core workspace
    workspaces,
    activeWorkspace,
    loadingWorkspaces: workspacesQuery.isLoading,
    workspacesError: workspacesQuery.error,
    dashboardData: dashboardQuery.data,
    loadingDashboard: dashboardQuery.isLoading,
    statsData: statsQuery.data,

    // Git
    gitStatusData: gitStatusQuery.data,
    refetchGitStatus: gitStatusQuery.refetch,

    // Files
    filesData: filesQuery.data,
    fileContentData: fileContentQuery.data,
    loadingFileContent: fileContentQuery.isLoading,
    fileHistoryData: fileHistoryQuery.data,
    loadingFileHistory: fileHistoryQuery.isLoading,

    // Operations
    operationsData: operationsQuery.data,
    loadingOperations: operationsQuery.isLoading,
    pendingReviewsData: pendingReviewsQuery.data,
    operationDetailData: operationDetailQuery.data,
    loadingOperationDetail: operationDetailQuery.isLoading,

    // Body health
    bodyVitalsResponse: bodyVitalsQuery.data,

    // Docs
    docsData: docsQuery.data,
    loadingDocs: docsQuery.isLoading,
    docsStatsData: docsStatsQuery.data,
    selectedDocData: selectedDocQuery.data,
    loadingDocDetail: selectedDocQuery.isLoading,

    // Platform
    missionData: missionQuery.data,
    loadingMission: missionQuery.isLoading,
    metricsData: metricsQuery.data,
    loadingMetrics: metricsQuery.isLoading,
    governanceData: governanceQuery.data,
    loadingGovernance: governanceQuery.isLoading,
    canonData: canonQuery.data,
    loadingCanon: canonQuery.isLoading,
    playbooksData: playbooksQuery.data,
    loadingPlaybooks: playbooksQuery.isLoading,
    auditsData: auditsQuery.data,
    loadingAudits: auditsQuery.isLoading,

    // Query client for invalidation
    queryClient,
  }
}

export function useWorkspaceMutations() {
  const queryClient = useQueryClient()

  const activateMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.activate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-active'] })
    },
  })

  const registerMutation = useMutation({
    mutationFn: (data: {
      path?: string
      github_url?: string
      github_token?: string
      name?: string
      description?: string
    }) => workspaceApi.create({ path: data.path || '', name: data.name, description: data.description }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
    },
  })

  const scanMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.scan(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-stats'] })
    },
  })

  const rollbackMutation = useMutation({
    mutationFn: (operationId: string) => workspaceOperationsApi.rollback(operationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-files'] })
    },
  })

  const reviewMutation = useMutation({
    mutationFn: ({ operationId, approved, notes }: { operationId: string; approved: boolean; notes?: string }) =>
      workspaceOperationsApi.review(operationId, { approved, notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-pending-reviews'] })
    },
  })

  const commitMutation = useMutation({
    mutationFn: ({ workspaceId, message, files }: { workspaceId: string; message: string; files?: string[] }) =>
      workspaceApi.gitCommit(workspaceId, { message, files }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspace-git-status'] })
      queryClient.invalidateQueries({ queryKey: ['workspace-operations'] })
    },
  })

  return {
    activateMutation,
    registerMutation,
    scanMutation,
    rollbackMutation,
    reviewMutation,
    commitMutation,
  }
}
