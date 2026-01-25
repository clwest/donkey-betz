// Session 825: Files Tab
// Extracted from WorkspacePage.tsx for modular architecture
// Placeholder - will be fully implemented when migrating file tree components

import { FolderTree } from 'lucide-react'

interface FilesTabProps {
  activeWorkspaceId?: string
}

export function FilesTab({ activeWorkspaceId: _activeWorkspaceId }: FilesTabProps) {
  // TODO: Migrate file tree, git status, and file content viewer from WorkspacePage

  return (
    <div className="space-y-4">
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="h-16 w-16 rounded-full bg-dark-border flex items-center justify-center mb-4">
          <FolderTree size={32} className="text-gray-400" />
        </div>
        <h3 className="font-semibold text-lg">Files Tab</h3>
        <p className="text-sm text-gray-400 mt-1 max-w-sm">
          File browser will be migrated here. Currently available in legacy WorkspacePage.
        </p>
      </div>
    </div>
  )
}
