import React, { useState, useEffect } from 'react'

interface Deliverable {
  id: string
  title: string
  status: string
  created_at: string
  workspace?: string
}

interface DeliverableStats {
  total: number
  completed: number
  in_progress: number
}

const API_BASE = '/api'

async function fetchDeliverables(
  workspaceId: string | null
): Promise<Deliverable[]> {
  const params = new URLSearchParams()
  if (workspaceId) params.set('workspace', workspaceId)
  const res = await fetch(`${API_BASE}/deliverables/?${params}`)
  if (!res.ok) throw new Error('Failed to fetch deliverables')
  const data = await res.json()
  return Array.isArray(data) ? data : data.results ?? []
}

async function fetchDeliverableStats(
  workspaceId: string | null
): Promise<DeliverableStats> {
  const params = new URLSearchParams()
  if (workspaceId) params.set('workspace', workspaceId)
  const res = await fetch(`${API_BASE}/deliverables/stats/?${params}`)
  if (!res.ok) return { total: 0, completed: 0, in_progress: 0 }
  return res.json()
}

export function DeliverablesTab() {
  const [scope, setScope] = useState<'workspace' | 'all'>('workspace')
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null)
  const [deliverables, setDeliverables] = useState<Deliverable[]>([])
  const [stats, setStats] = useState<DeliverableStats>({
    total: 0,
    completed: 0,
    in_progress: 0,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('activeWorkspaceId')
    if (stored) setActiveWorkspaceId(stored)
  }, [])

  const effectiveWorkspaceId =
    scope === 'workspace' ? activeWorkspaceId : null

  useEffect(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      fetchDeliverables(effectiveWorkspaceId),
      fetchDeliverableStats(effectiveWorkspaceId),
    ])
      .then(([items, s]) => {
        setDeliverables(items)
        setStats(s)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [effectiveWorkspaceId])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          Deliverables
        </h2>
        <div
          className="inline-flex rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
          role="group"
          aria-label="Deliverable scope"
        >
          <button
            onClick={() => setScope('workspace')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              scope === 'workspace'
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            This workspace
          </button>
          <button
            onClick={() => setScope('all')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              scope === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            All deliverables
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">Completed</p>
          <p className="text-2xl font-bold text-green-600">{stats.completed}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-100 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">In Progress</p>
          <p className="text-2xl font-bold text-indigo-600">{stats.in_progress}</p>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-4 text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {!loading && !error && deliverables.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          No deliverables found
          {scope === 'workspace' && activeWorkspaceId ? ' in this workspace' : ''}.
        </div>
      )}

      {!loading && !error && deliverables.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {deliverables.map((d) => (
                <tr key={d.id}>
                  <td className="px-6 py-4 text-sm text-gray-900 dark:text-white">{d.title}</td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        d.status === 'completed'
                          ? 'bg-green-100 text-green-800'
                          : d.status === 'in_progress'
                          ? 'bg-indigo-100 text-indigo-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {d.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                    {new Date(d.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
