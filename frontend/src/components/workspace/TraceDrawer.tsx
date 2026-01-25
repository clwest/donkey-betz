/**
 * Session 819: Deliverables Marketplace - Trace Drawer
 *
 * Slide-out panel showing developer details:
 * - Raw JSON output
 * - Tool call sequence with timing
 * - LLM prompts/responses
 * - Performance metrics
 */

import React, { useState } from 'react'
import {
  X, ChevronRight, ChevronDown, Clock, Cpu, Zap, Hash,
  FileJson, Terminal, MessageSquare, AlertCircle, CheckCircle,
  Copy, Check
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { Deliverable } from './DeliverableCard'

interface TraceDrawerProps {
  deliverable: Deliverable
  isOpen: boolean
  onClose: () => void
}

interface ToolCall {
  name: string
  arguments?: Record<string, any>
  result?: any
  duration_ms?: number
  success?: boolean
  error?: string
}

export function TraceDrawer({ deliverable, isOpen, onClose }: TraceDrawerProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'tools' | 'raw'>('overview')
  const [expandedTools, setExpandedTools] = useState<Set<number>>(new Set())
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  const toolCalls: ToolCall[] = deliverable.tool_calls || []
  const rawOutput = deliverable.raw_output || {}
  const metadata = deliverable.metadata || {}

  const toggleTool = (index: number) => {
    const newExpanded = new Set(expandedTools)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedTools(newExpanded)
  }

  const copyToClipboard = async (text: string, section: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedSection(section)
    setTimeout(() => setCopiedSection(null), 2000)
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className={cn(
        'fixed right-0 top-0 bottom-0 z-50 w-full max-w-xl bg-zinc-900 shadow-2xl',
        'transform transition-transform duration-300',
        isOpen ? 'translate-x-0' : 'translate-x-full'
      )}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-zinc-700/50">
          <div>
            <h3 className="text-lg font-medium text-zinc-100">Execution Trace</h3>
            <p className="text-sm text-zinc-400 mt-0.5">{deliverable.title}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-zinc-700/50">
          {(['overview', 'tools', 'raw'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'flex-1 px-4 py-3 text-sm font-medium transition-colors',
                activeTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400 bg-zinc-800/50'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/30'
              )}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4" style={{ height: 'calc(100vh - 130px)' }}>
          {activeTab === 'overview' && (
            <OverviewTab
              deliverable={deliverable}
              metadata={metadata}
              toolCalls={toolCalls}
            />
          )}

          {activeTab === 'tools' && (
            <ToolsTab
              toolCalls={toolCalls}
              expandedTools={expandedTools}
              toggleTool={toggleTool}
              copyToClipboard={copyToClipboard}
              copiedSection={copiedSection}
            />
          )}

          {activeTab === 'raw' && (
            <RawTab
              rawOutput={rawOutput}
              metadata={metadata}
              copyToClipboard={copyToClipboard}
              copiedSection={copiedSection}
            />
          )}
        </div>
      </div>
    </>
  )
}

function OverviewTab({
  deliverable,
  metadata,
  toolCalls
}: {
  deliverable: Deliverable
  metadata: Record<string, any>
  toolCalls: ToolCall[]
}) {
  const totalToolTime = toolCalls.reduce((acc, tc) => acc + (tc.duration_ms || 0), 0)
  const successfulTools = toolCalls.filter(tc => tc.success !== false).length

  return (
    <div className="space-y-6">
      {/* Performance Metrics */}
      <section>
        <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400" />
          Performance Metrics
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <MetricBox
            icon={<Clock className="w-4 h-4" />}
            label="Total Execution"
            value={`${(deliverable.execution_time_ms / 1000).toFixed(2)}s`}
          />
          <MetricBox
            icon={<Cpu className="w-4 h-4" />}
            label="Tool Time"
            value={`${(totalToolTime / 1000).toFixed(2)}s`}
          />
          <MetricBox
            icon={<Hash className="w-4 h-4" />}
            label="Tool Calls"
            value={`${successfulTools}/${toolCalls.length}`}
          />
          <MetricBox
            icon={<FileJson className="w-4 h-4" />}
            label="Output Size"
            value={`${deliverable.word_count} words`}
          />
        </div>
      </section>

      {/* Agent Info */}
      <section>
        <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-green-400" />
          Agent Information
        </h4>
        <div className="bg-zinc-800/50 rounded-lg p-4 space-y-2">
          <InfoRow label="Agent" value={deliverable.agent_name} />
          <InfoRow label="Task" value={deliverable.agent_task || 'N/A'} />
          <InfoRow label="Status" value={deliverable.status} />
          <InfoRow label="Quality Score" value={`${Math.round(deliverable.quality_score * 100)}%`} />
          <InfoRow label="Confidence" value={`${Math.round(deliverable.confidence_score * 100)}%`} />
        </div>
      </section>

      {/* Metadata */}
      {Object.keys(metadata).length > 0 && (
        <section>
          <h4 className="text-sm font-medium text-zinc-300 mb-3 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-blue-400" />
            Metadata
          </h4>
          <div className="bg-zinc-800/50 rounded-lg p-4 space-y-2">
            {Object.entries(metadata).map(([key, value]) => (
              <InfoRow
                key={key}
                label={key}
                value={typeof value === 'object' ? JSON.stringify(value) : String(value)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Source Operation */}
      {deliverable.metadata?.source_operation && (
        <section>
          <h4 className="text-sm font-medium text-zinc-300 mb-3">Source Operation</h4>
          <div className="bg-zinc-800/50 rounded-lg p-4 space-y-2">
            <InfoRow label="Operation ID" value={deliverable.metadata.source_operation.id} />
            <InfoRow label="Type" value={deliverable.metadata.source_operation.operation_type} />
            {deliverable.metadata.source_operation.file_path && (
              <InfoRow label="File" value={deliverable.metadata.source_operation.file_path} />
            )}
          </div>
        </section>
      )}
    </div>
  )
}

function ToolsTab({
  toolCalls,
  expandedTools,
  toggleTool,
  copyToClipboard,
  copiedSection
}: {
  toolCalls: ToolCall[]
  expandedTools: Set<number>
  toggleTool: (index: number) => void
  copyToClipboard: (text: string, section: string) => void
  copiedSection: string | null
}) {
  if (toolCalls.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-zinc-500">
        <Terminal className="w-12 h-12 mb-3 opacity-50" />
        <p>No tool calls recorded</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {toolCalls.map((tool, index) => (
        <div
          key={index}
          className="bg-zinc-800/50 rounded-lg overflow-hidden"
        >
          {/* Tool Header */}
          <button
            onClick={() => toggleTool(index)}
            className="w-full flex items-center justify-between p-3 hover:bg-zinc-700/30 transition-colors"
          >
            <div className="flex items-center gap-3">
              {expandedTools.has(index) ? (
                <ChevronDown className="w-4 h-4 text-zinc-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-zinc-400" />
              )}
              <span className="font-mono text-sm text-zinc-200">{tool.name}</span>
              {tool.success === false ? (
                <AlertCircle className="w-4 h-4 text-red-400" />
              ) : (
                <CheckCircle className="w-4 h-4 text-green-400" />
              )}
            </div>
            {tool.duration_ms !== undefined && (
              <span className="text-xs text-zinc-500">
                {tool.duration_ms}ms
              </span>
            )}
          </button>

          {/* Tool Details */}
          {expandedTools.has(index) && (
            <div className="border-t border-zinc-700/50 p-3 space-y-3">
              {/* Arguments */}
              {tool.arguments && Object.keys(tool.arguments).length > 0 && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-zinc-500 uppercase">Arguments</span>
                    <button
                      onClick={() => copyToClipboard(
                        JSON.stringify(tool.arguments, null, 2),
                        `args-${index}`
                      )}
                      className="p-1 text-zinc-500 hover:text-zinc-300"
                    >
                      {copiedSection === `args-${index}` ? (
                        <Check className="w-3 h-3" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  </div>
                  <pre className="bg-zinc-900 rounded p-2 text-xs text-zinc-400 overflow-x-auto">
                    {JSON.stringify(tool.arguments, null, 2)}
                  </pre>
                </div>
              )}

              {/* Result */}
              {tool.result !== undefined && (
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-zinc-500 uppercase">Result</span>
                    <button
                      onClick={() => copyToClipboard(
                        JSON.stringify(tool.result, null, 2),
                        `result-${index}`
                      )}
                      className="p-1 text-zinc-500 hover:text-zinc-300"
                    >
                      {copiedSection === `result-${index}` ? (
                        <Check className="w-3 h-3" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  </div>
                  <pre className="bg-zinc-900 rounded p-2 text-xs text-zinc-400 overflow-x-auto max-h-48">
                    {typeof tool.result === 'string'
                      ? tool.result
                      : JSON.stringify(tool.result, null, 2)}
                  </pre>
                </div>
              )}

              {/* Error */}
              {tool.error && (
                <div>
                  <span className="text-xs text-red-400 uppercase">Error</span>
                  <pre className="bg-red-900/20 rounded p-2 text-xs text-red-300 mt-1">
                    {tool.error}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

function RawTab({
  rawOutput,
  metadata,
  copyToClipboard,
  copiedSection
}: {
  rawOutput: Record<string, any>
  metadata: Record<string, any>
  copyToClipboard: (text: string, section: string) => void
  copiedSection: string | null
}) {
  const combinedData = {
    raw_output: rawOutput,
    metadata: metadata
  }

  const jsonString = JSON.stringify(combinedData, null, 2)

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-zinc-300">Raw Output Data</h4>
        <button
          onClick={() => copyToClipboard(jsonString, 'raw')}
          className="flex items-center gap-1 px-2 py-1 text-xs text-zinc-400 hover:text-zinc-200 bg-zinc-800 rounded"
        >
          {copiedSection === 'raw' ? (
            <>
              <Check className="w-3 h-3" />
              Copied
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              Copy
            </>
          )}
        </button>
      </div>
      <pre className="bg-zinc-800/50 rounded-lg p-4 text-xs text-zinc-400 overflow-x-auto">
        {jsonString}
      </pre>
    </div>
  )
}

function MetricBox({
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
      <div className="flex items-center gap-2 text-zinc-400 mb-1">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <span className="text-lg font-medium text-zinc-200">{value}</span>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between">
      <span className="text-sm text-zinc-500">{label}</span>
      <span className="text-sm text-zinc-300 text-right max-w-[60%] break-words">
        {value}
      </span>
    </div>
  )
}

export default TraceDrawer
