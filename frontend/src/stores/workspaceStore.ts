/**
 * Workspace Store — shared state for the active workspace.
 *
 * Used by:
 * - WorkspacePageNew: sets the active workspace when user selects one
 * - GlobalPADock: reads the active workspace to include in chat context
 * - Any component that needs to know which workspace is active
 */

import { create } from 'zustand'

interface WorkspaceInfo {
  id: string
  name: string
  workspace_type?: string
  git_remote_url?: string
}

interface WorkspaceStore {
  activeWorkspace: WorkspaceInfo | null
  setActiveWorkspace: (workspace: WorkspaceInfo | null) => void
}

export const useWorkspaceStore = create<WorkspaceStore>((set) => ({
  activeWorkspace: null,
  setActiveWorkspace: (workspace) => set({ activeWorkspace: workspace }),
}))
