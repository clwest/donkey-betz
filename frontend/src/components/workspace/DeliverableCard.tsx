/**
 * Session 819: Deliverables Marketplace - Product Card
 *
 * Displays a deliverable as a product card with:
 * - Title, type, category
 * - Preview content
 * - Quality metrics
 * - Action buttons (Save, Clone, Export, Trace)
 */

import React from 'react'
import {
  FileText, Image, Video, Music, Code, BarChart3, FileSpreadsheet,
  Layout, Microscope, Target, FileCheck, Scroll,
  Bookmark, BookmarkCheck, Copy, Download, Bug, Star,
  Clock, Coins, Bot
} from 'lucide-react'
import { cn } from '@/lib/cn'

export interface Deliverable {
  id: string
  title: string
  slug: string
  deliverable_type: string
  category: string
  tags: string[]
  agent_name: string
  agent_task: string
  preview_content: string
  thumbnail_url?: string
  quality_score: number
  confidence_score: number
  is_saved: boolean
  is_template: boolean
  is_starred: boolean
  clone_count: number
  is_cloned: boolean
  execution_time_ms: number
  llm_cost: string
  word_count: number
  line_count: number
  status: string
  created_at: string
  updated_at: string
  // Full content (only when expanded)
  content?: string
  content_format?: string
  tool_calls?: any[]
  raw_output?: Record<string, any>
  metadata?: Record<string, any>
}

interface DeliverableCardProps {
  deliverable: Deliverable
  onSave?: () => void
  onClone?: () => void
  onExport?: () => void
  onTrace?: () => void
  onClick?: () => void
  compact?: boolean
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
  document: 'text-blue-400',
  image: 'text-purple-400',
  video: 'text-pink-400',
  audio: 'text-green-400',
  code: 'text-amber-400',
  analysis: 'text-cyan-400',
  report: 'text-orange-400',
  template: 'text-indigo-400',
  research: 'text-emerald-400',
  strategy: 'text-rose-400',
  plan: 'text-teal-400',
  script: 'text-yellow-400',
}

export function DeliverableCard({
  deliverable,
  onSave,
  onClone,
  onExport,
  onTrace,
  onClick,
  compact = false
}: DeliverableCardProps) {
  const TypeIcon = TYPE_ICONS[deliverable.deliverable_type] || FileText
  const typeColor = TYPE_COLORS[deliverable.deliverable_type] || 'text-zinc-400'

  // Format the date
  const createdDate = new Date(deliverable.created_at)
  const dateStr = createdDate.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: createdDate.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
  })

  // Clean agent name for display
  const agentDisplay = deliverable.agent_name.replace('Agent', '')

  return (
    <div
      onClick={onClick}
      className={cn(
        'bg-zinc-800/50 border border-zinc-700/50 rounded-lg overflow-hidden',
        'hover:border-zinc-600/50 hover:bg-zinc-800/70 transition-all cursor-pointer',
        'flex flex-col'
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-zinc-700/50">
        <div className="flex items-start gap-3">
          {/* Type Icon */}
          <div className={cn('p-2 rounded-lg bg-zinc-700/50', typeColor)}>
            <TypeIcon className="w-5 h-5" />
          </div>

          {/* Title & Meta */}
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-zinc-100 truncate">
              {deliverable.title}
            </h3>
            <div className="flex items-center gap-2 mt-1 text-xs text-zinc-400">
              <Bot className="w-3 h-3" />
              <span>{agentDisplay}</span>
              {deliverable.category && (
                <>
                  <span className="text-zinc-600">|</span>
                  <span>{deliverable.category}</span>
                </>
              )}
            </div>
          </div>

          {/* Saved/Starred indicators */}
          <div className="flex items-center gap-1">
            {deliverable.is_saved && (
              <BookmarkCheck className="w-4 h-4 text-blue-400" />
            )}
            {deliverable.is_starred && (
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            )}
          </div>
        </div>
      </div>

      {/* Preview Content */}
      {!compact && deliverable.preview_content && (
        <div className="p-4 flex-1">
          <p className="text-sm text-zinc-400 line-clamp-3">
            {deliverable.preview_content}
          </p>

          {/* Tags */}
          {deliverable.tags && deliverable.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {deliverable.tags.slice(0, 4).map((tag, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-xs bg-zinc-700/50 text-zinc-400 rounded"
                >
                  {tag}
                </span>
              ))}
              {deliverable.tags.length > 4 && (
                <span className="px-2 py-0.5 text-xs text-zinc-500">
                  +{deliverable.tags.length - 4}
                </span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Metrics */}
      <div className="px-4 py-2 bg-zinc-900/30 border-t border-zinc-700/30">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4 text-zinc-500">
            {/* Quality Score */}
            <div className="flex items-center gap-1" title="Quality Score">
              <div
                className={cn(
                  'w-1.5 h-1.5 rounded-full',
                  deliverable.quality_score >= 0.7
                    ? 'bg-green-400'
                    : deliverable.quality_score >= 0.4
                    ? 'bg-yellow-400'
                    : 'bg-red-400'
                )}
              />
              <span>{Math.round(deliverable.quality_score * 100)}%</span>
            </div>

            {/* Execution Time */}
            {deliverable.execution_time_ms > 0 && (
              <div className="flex items-center gap-1" title="Execution Time">
                <Clock className="w-3 h-3" />
                <span>{(deliverable.execution_time_ms / 1000).toFixed(1)}s</span>
              </div>
            )}

            {/* Cost */}
            {parseFloat(deliverable.llm_cost) > 0 && (
              <div className="flex items-center gap-1" title="LLM Cost">
                <Coins className="w-3 h-3" />
                <span>${deliverable.llm_cost}</span>
              </div>
            )}
          </div>

          <span className="text-zinc-600">{dateStr}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center border-t border-zinc-700/30">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onSave?.()
          }}
          className="flex-1 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 transition-colors flex items-center justify-center gap-1"
          title={deliverable.is_saved ? 'Remove from Library' : 'Save to Library'}
        >
          {deliverable.is_saved ? (
            <BookmarkCheck className="w-3.5 h-3.5" />
          ) : (
            <Bookmark className="w-3.5 h-3.5" />
          )}
          <span>{deliverable.is_saved ? 'Saved' : 'Save'}</span>
        </button>

        <div className="w-px h-6 bg-zinc-700/50" />

        <button
          onClick={(e) => {
            e.stopPropagation()
            onClone?.()
          }}
          className="flex-1 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 transition-colors flex items-center justify-center gap-1"
          title="Clone"
        >
          <Copy className="w-3.5 h-3.5" />
          <span>Clone</span>
        </button>

        <div className="w-px h-6 bg-zinc-700/50" />

        <button
          onClick={(e) => {
            e.stopPropagation()
            onExport?.()
          }}
          className="flex-1 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 transition-colors flex items-center justify-center gap-1"
          title="Export"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export</span>
        </button>

        <div className="w-px h-6 bg-zinc-700/50" />

        <button
          onClick={(e) => {
            e.stopPropagation()
            onTrace?.()
          }}
          className="flex-1 px-3 py-2 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 transition-colors flex items-center justify-center gap-1"
          title="View Trace"
        >
          <Bug className="w-3.5 h-3.5" />
          <span>Trace</span>
        </button>
      </div>
    </div>
  )
}

export default DeliverableCard
