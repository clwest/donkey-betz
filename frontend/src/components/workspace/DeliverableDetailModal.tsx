/**
 * Session 819: Deliverables Marketplace - Detail Modal
 *
 * Full-screen modal showing complete deliverable content with:
 * - Markdown rendering
 * - All metadata displayed
 * - Action buttons (Save, Clone, Export, Templateize)
 * - Code syntax highlighting
 */

import React, { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  X, FileText, Image, Video, Music, Code, BarChart3, FileSpreadsheet,
  Layout, Microscope, Target, FileCheck, Scroll,
  Bookmark, BookmarkCheck, Copy, Download,
  Clock, Coins, Bot, Calendar, Tag, Bug, Volume2
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { Deliverable } from './DeliverableCard'
import { ListenButton } from '@/components/ListenButton'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface DeliverableDetailModalProps {
  deliverable: Deliverable
  onClose: () => void
  onTraceClick?: () => void
}

const TYPE_ICONS: Record<string, React.ElementType> = {
  document: FileText,
  image: Image,
  video: Video,
  audio: Music,
  code: Code,
  analysis: BarChart3,
  report: FileSpreadsheet,
  template: Layout,
  research: Microscope,
  strategy: Target,
  plan: FileCheck,
  script: Scroll,
}

const TYPE_COLORS: Record<string, string> = {
  document: 'text-blue-400 bg-blue-400/10',
  image: 'text-purple-400 bg-purple-400/10',
  video: 'text-pink-400 bg-pink-400/10',
  audio: 'text-green-400 bg-green-400/10',
  code: 'text-amber-400 bg-amber-400/10',
  analysis: 'text-cyan-400 bg-cyan-400/10',
  report: 'text-orange-400 bg-orange-400/10',
  template: 'text-indigo-400 bg-indigo-400/10',
  research: 'text-emerald-400 bg-emerald-400/10',
  strategy: 'text-rose-400 bg-rose-400/10',
  plan: 'text-teal-400 bg-teal-400/10',
  script: 'text-yellow-400 bg-yellow-400/10',
}

// API functions
async function saveDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/save/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to save')
}

async function unsaveDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/unsave/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to unsave')
}

async function cloneDeliverable(id: string): Promise<Deliverable> {
  const response = await fetch(`/api/deliverables/${id}/clone/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to clone')
  return data.deliverable
}

async function templateizeDeliverable(id: string): Promise<void> {
  const response = await fetch(`/api/deliverables/${id}/templateize/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
  })
  const data = await response.json()
  if (!data.success) throw new Error(data.error || 'Failed to templateize')
}

async function exportDeliverable(id: string, format: string): Promise<Blob> {
  const response = await fetch(`/api/deliverables/${id}/export/`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format })
  })
  if (!response.ok) {
    const data = await response.json()
    throw new Error(data.error || 'Export failed')
  }
  return response.blob()
}

export function DeliverableDetailModal({
  deliverable,
  onClose,
  onTraceClick
}: DeliverableDetailModalProps) {
  const queryClient = useQueryClient()
  const [exportFormat, setExportFormat] = useState('html')

  const TypeIcon = TYPE_ICONS[deliverable.deliverable_type] || FileText
  const typeColor = TYPE_COLORS[deliverable.deliverable_type] || 'text-zinc-400 bg-zinc-400/10'

  // Mutations
  const saveMutation = useMutation({
    mutationFn: () => deliverable.is_saved
      ? unsaveDeliverable(deliverable.id)
      : saveDeliverable(deliverable.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  const cloneMutation = useMutation({
    mutationFn: () => cloneDeliverable(deliverable.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
      queryClient.invalidateQueries({ queryKey: ['deliverables-stats'] })
    }
  })

  const templateMutation = useMutation({
    mutationFn: () => templateizeDeliverable(deliverable.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliverables'] })
    }
  })

  const handleExport = async () => {
    try {
      const blob = await exportDeliverable(deliverable.id, exportFormat)
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${deliverable.slug}.${exportFormat === 'markdown' ? 'md' : exportFormat}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  // Format dates
  const createdDate = new Date(deliverable.created_at)
  const updatedDate = new Date(deliverable.updated_at)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-zinc-900 rounded-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-zinc-700/50">
          <div className="flex items-start gap-4">
            <div className={cn('p-3 rounded-xl', typeColor)}>
              <TypeIcon className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-zinc-100">
                {deliverable.title}
              </h2>
              <div className="flex items-center gap-3 mt-2 text-sm text-zinc-400">
                <span className="flex items-center gap-1">
                  <Bot className="w-4 h-4" />
                  {deliverable.agent_name}
                </span>
                {deliverable.category && (
                  <>
                    <span className="text-zinc-600">|</span>
                    <span>{deliverable.category}</span>
                  </>
                )}
                <span className="text-zinc-600">|</span>
                <span className="capitalize">{deliverable.deliverable_type}</span>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            {/* Metadata Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <MetricCard
                icon={<div className={cn(
                  'w-2 h-2 rounded-full',
                  deliverable.quality_score >= 0.7 ? 'bg-green-400' :
                  deliverable.quality_score >= 0.4 ? 'bg-yellow-400' : 'bg-red-400'
                )} />}
                label="Quality"
                value={`${Math.round(deliverable.quality_score * 100)}%`}
              />
              <MetricCard
                icon={<Clock className="w-4 h-4 text-zinc-400" />}
                label="Execution"
                value={deliverable.execution_time_ms > 0
                  ? `${(deliverable.execution_time_ms / 1000).toFixed(1)}s`
                  : 'N/A'}
              />
              <MetricCard
                icon={<Coins className="w-4 h-4 text-zinc-400" />}
                label="Cost"
                value={parseFloat(deliverable.llm_cost) > 0
                  ? `$${deliverable.llm_cost}`
                  : 'N/A'}
              />
              <MetricCard
                icon={<Copy className="w-4 h-4 text-zinc-400" />}
                label="Clones"
                value={deliverable.clone_count.toString()}
              />
            </div>

            {/* Tags */}
            {deliverable.tags && deliverable.tags.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-zinc-400 mb-2 flex items-center gap-2">
                  <Tag className="w-4 h-4" />
                  Tags
                </h4>
                <div className="flex flex-wrap gap-2">
                  {deliverable.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 text-sm bg-zinc-800 text-zinc-300 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Main Content */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-zinc-400">Content</h4>
                {(deliverable.content || deliverable.preview_content) && (
                  <ListenButton
                    text={deliverable.content || deliverable.preview_content}
                    agentName={deliverable.agent_name}
                    size="sm"
                  />
                )}
              </div>
              <div className="bg-zinc-800/50 rounded-lg p-4 prose prose-invert prose-sm max-w-none">
                {deliverable.content_format === 'markdown' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {deliverable.content || deliverable.preview_content}
                  </ReactMarkdown>
                ) : deliverable.content_format === 'code' ? (
                  <pre className="bg-zinc-900 p-4 rounded-lg overflow-x-auto">
                    <code>{deliverable.content || deliverable.preview_content}</code>
                  </pre>
                ) : (
                  <div className="whitespace-pre-wrap">
                    {deliverable.content || deliverable.preview_content}
                  </div>
                )}
              </div>
            </div>

            {/* Timestamps */}
            <div className="flex items-center gap-6 text-sm text-zinc-500">
              <span className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Created: {createdDate.toLocaleString()}
              </span>
              <span className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Updated: {updatedDate.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-between p-4 border-t border-zinc-700/50 bg-zinc-800/30">
          <div className="flex items-center gap-2">
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                deliverable.is_saved
                  ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
                  : 'bg-zinc-700 text-zinc-300 hover:bg-zinc-600'
              )}
            >
              {deliverable.is_saved ? (
                <BookmarkCheck className="w-4 h-4" />
              ) : (
                <Bookmark className="w-4 h-4" />
              )}
              {deliverable.is_saved ? 'Saved' : 'Save'}
            </button>

            <button
              onClick={() => cloneMutation.mutate()}
              disabled={cloneMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-700 text-zinc-300 rounded-lg text-sm font-medium hover:bg-zinc-600 transition-colors"
            >
              <Copy className="w-4 h-4" />
              Clone
            </button>

            <button
              onClick={() => templateMutation.mutate()}
              disabled={templateMutation.isPending || deliverable.is_template}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
                deliverable.is_template
                  ? 'bg-indigo-500/20 text-indigo-400'
                  : 'bg-zinc-700 text-zinc-300 hover:bg-zinc-600'
              )}
            >
              <Layout className="w-4 h-4" />
              {deliverable.is_template ? 'Template' : 'Make Template'}
            </button>

            {onTraceClick && (
              <button
                onClick={onTraceClick}
                className="flex items-center gap-2 px-4 py-2 bg-zinc-700 text-zinc-300 rounded-lg text-sm font-medium hover:bg-zinc-600 transition-colors"
              >
                <Bug className="w-4 h-4" />
                Trace
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            <select
              value={exportFormat}
              onChange={(e) => setExportFormat(e.target.value)}
              className="px-3 py-2 bg-zinc-700 border border-zinc-600 rounded-lg text-sm text-zinc-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="html">HTML</option>
              <option value="markdown">Markdown</option>
              <option value="json">JSON</option>
            </select>
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-500 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricCard({
  icon,
  label,
  value
}: {
  icon: React.ReactNode
  label: string
  value: string
}) {
  return (
    <div className="bg-zinc-800/50 rounded-lg p-3">
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-xs text-zinc-500">{label}</span>
      </div>
      <span className="text-lg font-medium text-zinc-200">{value}</span>
    </div>
  )
}

export default DeliverableDetailModal
