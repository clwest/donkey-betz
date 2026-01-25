/**
 * Session 820: Smart Output Renderer
 *
 * A unified component that renders agent output_data in human-readable format.
 * Handles all common output types: blogs, research, podcasts, recommendations,
 * analysis, signals, code, images, tool results, and documents.
 *
 * Usage:
 *   <SmartOutputRenderer data={output_data} agentName="ContentWriterAgent" />
 */

import React, { useState } from 'react'
import {
  FileText, BookOpen, Mic, Lightbulb, BarChart3, Signal, Code2,
  Image as ImageIcon, Wrench, ChevronDown, ChevronRight, ExternalLink,
  Play, Clock, Users, TrendingUp, AlertCircle, CheckCircle, XCircle,
  Brain, Sparkles, ListChecks, Quote, Newspaper, Radio
} from 'lucide-react'
import { cn } from '@/lib/cn'

// =============================================================================
// Types
// =============================================================================

interface OutputData {
  // Core fields
  message?: string
  task?: string
  summary?: string
  type?: string

  // Blog/Article content
  content?: BlogContent | string
  content_type?: string

  // Research
  results?: ResearchResult[]
  sources?: string[]

  // Podcast
  episodes?: PodcastEpisode[]
  transcript?: string
  speakers?: string[]
  topics?: string[]

  // Recommendations
  recommendations?: (string | Recommendation)[]

  // Analysis
  analysis?: AnalysisResult
  insights?: string[]
  key_insights?: string[]

  // Signals
  signals?: Signal[]

  // Tool results
  tool_results?: ToolResult[]

  // Images
  images?: ImageResult[]

  // Code
  code?: string
  language?: string

  // Documents
  sections?: DocumentSection[]
  document_type?: string

  // Metrics
  metrics?: Record<string, number | string>

  // Status
  success?: boolean
  error?: string

  // Thinking/Reasoning
  thinking_result?: ThinkingResult
  reasoning?: string
  conclusion?: string

  // Workflow
  suggested_workflow?: (string | WorkflowStep)[]
  workflow_type?: string

  // Debate
  debate_result?: DebateResult

  // System metrics
  items_count?: number
  info_count?: number
  warning_count?: number
  critical_count?: number
  execution_time?: number

  // Any other fields
  [key: string]: unknown
}

interface BlogContent {
  title?: string
  headline?: string
  sections?: { heading: string; content: string }[]
  body?: string
  full_text?: string
  word_count?: number
  reading_time?: number
}

interface ResearchResult {
  source?: string
  title?: string
  summary?: string
  url?: string
  data?: unknown
  relevance?: number
}

interface PodcastEpisode {
  title?: string
  description?: string
  duration?: string
  speakers?: string[]
  topics?: string[]
}

interface Recommendation {
  title?: string
  description?: string
  priority?: 'high' | 'medium' | 'low'
  action?: string
}

interface AnalysisResult {
  summary?: string
  key_insights?: string[]
  findings?: string[]
  charts?: ChartData[]
  [key: string]: unknown
}

interface ChartData {
  type?: string
  data?: unknown
  labels?: string[]
}

interface Signal {
  type?: string
  market?: string
  strength?: 'strong' | 'moderate' | 'weak' | string
  confidence?: number
  description?: string
}

interface ToolResult {
  tool?: string
  name?: string
  arguments?: Record<string, unknown>
  result?: unknown
  success?: boolean
}

interface ImageResult {
  image_url?: string
  url?: string
  image_id?: string
  prompt?: string
  thumbnail?: string
}

interface DocumentSection {
  heading?: string
  title?: string
  content?: string
  body?: string
}

interface ThinkingResult {
  conclusion?: string
  reasoning?: string
  confidence?: number
  alternatives?: string[]
}

interface WorkflowStep {
  step?: string
  agent?: string
  description?: string
}

interface DebateResult {
  topic?: string
  winner?: string
  summary?: string
  arguments?: { side: string; points: string[] }[]
}

interface SmartOutputRendererProps {
  data: OutputData | string | null | undefined
  agentName?: string
  maxHeight?: string
  showRawToggle?: boolean
  className?: string
}

// =============================================================================
// Sub-Components
// =============================================================================

// Blog/Article Content
function BlogRenderer({ content }: { content: BlogContent }) {
  const [expanded, setExpanded] = useState(false)
  const title = content.title || content.headline
  const fullText = content.full_text || content.body
  const previewLength = 500

  return (
    <div className="space-y-3">
      {title && (
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Newspaper className="w-5 h-5 text-accent-cyan" />
          {title}
        </h3>
      )}

      {content.reading_time && (
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {content.reading_time} min read
          </span>
          {content.word_count && (
            <span>{content.word_count.toLocaleString()} words</span>
          )}
        </div>
      )}

      {content.sections && content.sections.length > 0 ? (
        <div className="space-y-4">
          {content.sections.map((section, i) => (
            <div key={i} className="border-l-2 border-accent-cyan/30 pl-4">
              <h4 className="text-sm font-medium text-accent-cyan mb-2">{section.heading}</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{section.content}</p>
            </div>
          ))}
        </div>
      ) : fullText ? (
        <div>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">
            {expanded ? fullText : fullText.slice(0, previewLength)}
            {!expanded && fullText.length > previewLength && '...'}
          </p>
          {fullText.length > previewLength && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2 text-xs text-accent-cyan hover:underline flex items-center gap-1"
            >
              {expanded ? (
                <>Show less <ChevronDown className="w-3 h-3" /></>
              ) : (
                <>Read more ({Math.ceil((fullText.length - previewLength) / 100) * 100}+ chars) <ChevronRight className="w-3 h-3" /></>
              )}
            </button>
          )}
        </div>
      ) : null}
    </div>
  )
}

// Research Results
function ResearchRenderer({ results }: { results: ResearchResult[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-purple flex items-center gap-2">
        <BookOpen className="w-4 h-4" />
        Research Results ({results.length})
      </h4>
      <div className="space-y-2">
        {results.slice(0, 8).map((result, i) => (
          <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                {result.source && (
                  <span className="text-xs text-accent-green font-medium">{result.source}</span>
                )}
                {result.title && (
                  <p className="text-sm text-white font-medium mt-1 truncate">{result.title}</p>
                )}
                {result.summary && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{result.summary}</p>
                )}
              </div>
              {result.url && (
                <a href={result.url} target="_blank" rel="noopener noreferrer" className="text-accent-cyan hover:text-accent-cyan/80">
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>
            {result.relevance !== undefined && (
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent-purple"
                    style={{ width: `${result.relevance * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{(result.relevance * 100).toFixed(0)}%</span>
              </div>
            )}
          </div>
        ))}
        {results.length > 8 && (
          <p className="text-xs text-gray-500 text-center">+ {results.length - 8} more results</p>
        )}
      </div>
    </div>
  )
}

// Podcast Content
function PodcastRenderer({ data }: { data: OutputData }) {
  const episodes = data.episodes || []
  const topics = data.topics || []
  const speakers = data.speakers || []

  return (
    <div className="space-y-4">
      <h4 className="text-sm font-medium text-accent-amber flex items-center gap-2">
        <Radio className="w-4 h-4" />
        Podcast Content
      </h4>

      {topics.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {topics.map((topic, i) => (
            <span key={i} className="px-2 py-1 text-xs bg-accent-amber/20 text-accent-amber rounded-full">
              {topic}
            </span>
          ))}
        </div>
      )}

      {speakers.length > 0 && (
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Users className="w-4 h-4" />
          {speakers.join(', ')}
        </div>
      )}

      {episodes.map((ep, i) => (
        <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-accent-amber/20 rounded-lg">
              <Mic className="w-5 h-5 text-accent-amber" />
            </div>
            <div className="flex-1">
              {ep.title && <p className="text-sm text-white font-medium">{ep.title}</p>}
              {ep.description && <p className="text-xs text-gray-400 mt-1">{ep.description}</p>}
              {ep.duration && (
                <span className="inline-flex items-center gap-1 mt-2 text-xs text-gray-500">
                  <Clock className="w-3 h-3" /> {ep.duration}
                </span>
              )}
            </div>
          </div>
        </div>
      ))}

      {data.transcript && (
        <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
          <h5 className="text-xs text-gray-400 mb-2">Transcript</h5>
          <p className="text-sm text-gray-300 whitespace-pre-wrap max-h-40 overflow-y-auto">
            {data.transcript}
          </p>
        </div>
      )}
    </div>
  )
}

// Recommendations
function RecommendationsRenderer({ recommendations }: { recommendations: (string | Recommendation)[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-purple flex items-center gap-2">
        <Lightbulb className="w-4 h-4" />
        Recommendations ({recommendations.length})
      </h4>
      <div className="space-y-2">
        {recommendations.map((rec, i) => (
          <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border flex items-start gap-3">
            <span className="text-accent-purple font-mono text-xs mt-0.5 flex-shrink-0">{i + 1}.</span>
            {typeof rec === 'string' ? (
              <p className="text-sm text-gray-300">{rec}</p>
            ) : (
              <div className="flex-1">
                {rec.title && <p className="text-sm text-white font-medium">{rec.title}</p>}
                {rec.description && <p className="text-xs text-gray-400 mt-1">{rec.description}</p>}
                {rec.priority && (
                  <span className={cn(
                    "inline-block mt-2 px-2 py-0.5 text-xs rounded",
                    rec.priority === 'high' ? 'bg-accent-red/20 text-accent-red' :
                    rec.priority === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                    'bg-gray-600/20 text-gray-400'
                  )}>
                    {rec.priority}
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Analysis
function AnalysisRenderer({ analysis }: { analysis: AnalysisResult }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-cyan flex items-center gap-2">
        <BarChart3 className="w-4 h-4" />
        Analysis
      </h4>

      {analysis.summary && (
        <p className="text-sm text-gray-300 p-3 bg-dark-card rounded-lg border border-dark-border">
          {analysis.summary}
        </p>
      )}

      {(analysis.key_insights || analysis.findings) && (
        <div className="space-y-2">
          <h5 className="text-xs text-gray-400">Key Insights</h5>
          {(analysis.key_insights || analysis.findings || []).map((insight, i) => (
            <div key={i} className="flex items-start gap-2 p-2 bg-dark-card/50 rounded">
              <Sparkles className="w-4 h-4 text-accent-amber flex-shrink-0 mt-0.5" />
              <p className="text-sm text-gray-300">{insight}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Signals
function SignalsRenderer({ signals }: { signals: Signal[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-green flex items-center gap-2">
        <Signal className="w-4 h-4" />
        Signals ({signals.length})
      </h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {signals.slice(0, 10).map((signal, i) => (
          <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border">
            <div className="flex items-center justify-between">
              <span className="text-sm text-white font-medium">
                {signal.type || signal.market || `Signal ${i + 1}`}
              </span>
              {signal.strength && (
                <span className={cn(
                  "px-2 py-0.5 text-xs rounded",
                  signal.strength === 'strong' ? 'bg-accent-green/20 text-accent-green' :
                  signal.strength === 'moderate' ? 'bg-accent-amber/20 text-accent-amber' :
                  'bg-gray-600/20 text-gray-400'
                )}>
                  {signal.strength}
                </span>
              )}
            </div>
            {signal.description && (
              <p className="text-xs text-gray-400 mt-1">{signal.description}</p>
            )}
            {signal.confidence !== undefined && (
              <div className="mt-2 flex items-center gap-2">
                <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-accent-green"
                    style={{ width: `${signal.confidence * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">{(signal.confidence * 100).toFixed(0)}%</span>
              </div>
            )}
          </div>
        ))}
      </div>
      {signals.length > 10 && (
        <p className="text-xs text-gray-500 text-center">+ {signals.length - 10} more signals</p>
      )}
    </div>
  )
}

// Tool Results
function ToolResultsRenderer({ results }: { results: ToolResult[] }) {
  const [expanded, setExpanded] = useState<number | null>(null)

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-amber flex items-center gap-2">
        <Wrench className="w-4 h-4" />
        Tool Results ({results.length})
      </h4>
      <div className="space-y-2">
        {results.map((tr, i) => (
          <div key={i} className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
            <button
              onClick={() => setExpanded(expanded === i ? null : i)}
              className="w-full p-3 flex items-center justify-between hover:bg-dark-lighter transition-colors"
            >
              <div className="flex items-center gap-2">
                <Wrench className="w-4 h-4 text-accent-amber" />
                <span className="text-sm text-white font-medium">{tr.tool || tr.name || `Tool ${i + 1}`}</span>
                {tr.success !== undefined && (
                  tr.success ?
                    <CheckCircle className="w-4 h-4 text-accent-green" /> :
                    <XCircle className="w-4 h-4 text-accent-red" />
                )}
              </div>
              {expanded === i ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
            </button>
            {expanded === i && tr.result && (
              <div className="p-3 border-t border-dark-border bg-dark-bg">
                <pre className="text-xs text-gray-300 overflow-auto max-h-40 font-mono">
                  {typeof tr.result === 'string' ? tr.result : JSON.stringify(tr.result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

// Images
function ImagesRenderer({ images }: { images: ImageResult[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-purple flex items-center gap-2">
        <ImageIcon className="w-4 h-4" />
        Generated Images ({images.length})
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {images.map((img, i) => {
          const url = img.image_url || img.url || img.thumbnail
          return (
            <div key={i} className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
              {url ? (
                <a href={url} target="_blank" rel="noopener noreferrer" className="block aspect-square bg-gray-800 relative group">
                  <img src={url} alt={img.prompt || `Image ${i + 1}`} className="w-full h-full object-cover" />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <ExternalLink className="w-6 h-6 text-white" />
                  </div>
                </a>
              ) : (
                <div className="aspect-square bg-gray-800 flex items-center justify-center">
                  <ImageIcon className="w-8 h-8 text-gray-600" />
                </div>
              )}
              {img.prompt && (
                <p className="p-2 text-xs text-gray-400 truncate">{img.prompt}</p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// Thinking/Reasoning
function ThinkingRenderer({ data }: { data: ThinkingResult }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-cyan flex items-center gap-2">
        <Brain className="w-4 h-4" />
        Thinking Result
      </h4>

      {data.conclusion && (
        <div className="p-3 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg">
          <p className="text-sm text-white font-medium">{data.conclusion}</p>
        </div>
      )}

      {data.reasoning && (
        <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
          <h5 className="text-xs text-gray-400 mb-2">Reasoning</h5>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{data.reasoning}</p>
        </div>
      )}

      {data.confidence !== undefined && (
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">Confidence</span>
          <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent-cyan"
              style={{ width: `${data.confidence * 100}%` }}
            />
          </div>
          <span className="text-sm text-white font-medium">{(data.confidence * 100).toFixed(0)}%</span>
        </div>
      )}

      {data.alternatives && data.alternatives.length > 0 && (
        <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
          <h5 className="text-xs text-gray-400 mb-2">Alternatives Considered</h5>
          <ul className="space-y-1">
            {data.alternatives.map((alt, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-gray-500">•</span> {alt}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// System Metrics
function MetricsRenderer({ data }: { data: OutputData }) {
  const metrics = [
    { label: 'Items', value: data.items_count, icon: ListChecks, color: 'text-accent-cyan' },
    { label: 'Info', value: data.info_count, icon: AlertCircle, color: 'text-accent-cyan' },
    { label: 'Warnings', value: data.warning_count, icon: AlertCircle, color: 'text-accent-amber' },
    { label: 'Critical', value: data.critical_count, icon: AlertCircle, color: 'text-accent-red' },
  ].filter(m => m.value !== undefined)

  if (metrics.length === 0) return null

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {metrics.map((m, i) => (
        <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border text-center">
          <m.icon className={cn("w-5 h-5 mx-auto mb-1", m.color)} />
          <p className="text-2xl font-bold text-white">{m.value}</p>
          <p className="text-xs text-gray-400">{m.label}</p>
        </div>
      ))}
      {data.execution_time !== undefined && (
        <div className="p-3 bg-dark-card rounded-lg border border-dark-border text-center">
          <Clock className="w-5 h-5 mx-auto mb-1 text-gray-400" />
          <p className="text-lg font-medium text-white">{data.execution_time.toFixed(2)}s</p>
          <p className="text-xs text-gray-400">Execution Time</p>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Main Component
// =============================================================================

export function SmartOutputRenderer({
  data,
  agentName,
  maxHeight = '600px',
  showRawToggle = true,
  className
}: SmartOutputRendererProps) {
  const [showRaw, setShowRaw] = useState(false)

  // Handle null/undefined/string data
  if (!data) {
    return <p className="text-sm text-gray-500 italic">No output data</p>
  }

  if (typeof data === 'string') {
    // Try to parse as JSON
    try {
      data = JSON.parse(data) as OutputData
    } catch {
      // If not JSON, render as text
      return (
        <div className={cn("p-3 bg-dark-card rounded-lg", className)}>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{data}</p>
        </div>
      )
    }
  }

  const outputData = data as OutputData

  // Determine what type of content we have
  const hasBlog = outputData.content && typeof outputData.content === 'object' &&
    ('title' in outputData.content || 'sections' in outputData.content || 'body' in outputData.content)
  const hasResearch = outputData.results && Array.isArray(outputData.results) && outputData.results.length > 0
  const hasPodcast = outputData.episodes || outputData.transcript || (outputData.topics && outputData.speakers)
  const hasRecommendations = outputData.recommendations && Array.isArray(outputData.recommendations) && outputData.recommendations.length > 0
  const hasAnalysis = outputData.analysis && typeof outputData.analysis === 'object'
  const hasSignals = outputData.signals && Array.isArray(outputData.signals) && outputData.signals.length > 0
  const hasToolResults = outputData.tool_results && Array.isArray(outputData.tool_results) && outputData.tool_results.length > 0
  const hasImages = outputData.images && Array.isArray(outputData.images) && outputData.images.length > 0
  const hasThinking = outputData.thinking_result && typeof outputData.thinking_result === 'object'
  const hasMetrics = outputData.items_count !== undefined || outputData.info_count !== undefined ||
    outputData.warning_count !== undefined || outputData.critical_count !== undefined
  const hasInsights = (outputData.insights && Array.isArray(outputData.insights) && outputData.insights.length > 0) ||
    (outputData.key_insights && Array.isArray(outputData.key_insights) && outputData.key_insights.length > 0)

  // Check if we have any structured content
  const hasStructuredContent = hasBlog || hasResearch || hasPodcast || hasRecommendations ||
    hasAnalysis || hasSignals || hasToolResults || hasImages || hasThinking || hasMetrics || hasInsights

  return (
    <div className={cn("space-y-4", className)} style={{ maxHeight, overflowY: 'auto' }}>
      {/* Toggle for raw view */}
      {showRawToggle && hasStructuredContent && (
        <div className="flex justify-end">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className="text-xs text-gray-400 hover:text-white px-2 py-1 rounded hover:bg-gray-700 transition-colors"
          >
            {showRaw ? 'Show Formatted' : 'Show Raw JSON'}
          </button>
        </div>
      )}

      {showRaw ? (
        <pre className="text-xs bg-dark-bg p-4 rounded-lg overflow-auto font-mono text-gray-300 border border-dark-border">
          {JSON.stringify(outputData, null, 2)}
        </pre>
      ) : (
        <>
          {/* Message */}
          {outputData.message && (
            <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{outputData.message}</p>
            </div>
          )}

          {/* Task */}
          {outputData.task && (
            <div className="p-3 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg">
              <div className="text-xs text-accent-cyan mb-1">Task</div>
              <p className="text-sm text-white">{outputData.task}</p>
            </div>
          )}

          {/* Summary */}
          {outputData.summary && !hasAnalysis && (
            <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
              <div className="text-xs text-gray-400 mb-1">Summary</div>
              <p className="text-sm text-gray-300">{outputData.summary}</p>
            </div>
          )}

          {/* Metrics (if present) */}
          {hasMetrics && <MetricsRenderer data={outputData} />}

          {/* Blog Content */}
          {hasBlog && <BlogRenderer content={outputData.content as BlogContent} />}

          {/* Research Results */}
          {hasResearch && <ResearchRenderer results={outputData.results!} />}

          {/* Podcast Content */}
          {hasPodcast && <PodcastRenderer data={outputData} />}

          {/* Recommendations */}
          {hasRecommendations && <RecommendationsRenderer recommendations={outputData.recommendations!} />}

          {/* Analysis */}
          {hasAnalysis && <AnalysisRenderer analysis={outputData.analysis!} />}

          {/* Key Insights (standalone) */}
          {hasInsights && !hasAnalysis && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-accent-amber flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Key Insights
              </h4>
              {(outputData.insights || outputData.key_insights || []).map((insight, i) => (
                <div key={i} className="flex items-start gap-2 p-2 bg-dark-card/50 rounded">
                  <span className="text-accent-amber">•</span>
                  <p className="text-sm text-gray-300">{insight}</p>
                </div>
              ))}
            </div>
          )}

          {/* Signals */}
          {hasSignals && <SignalsRenderer signals={outputData.signals!} />}

          {/* Tool Results */}
          {hasToolResults && <ToolResultsRenderer results={outputData.tool_results!} />}

          {/* Images */}
          {hasImages && <ImagesRenderer images={outputData.images!} />}

          {/* Thinking Result */}
          {hasThinking && <ThinkingRenderer data={outputData.thinking_result!} />}

          {/* Reasoning/Conclusion (standalone) */}
          {!hasThinking && (outputData.reasoning || outputData.conclusion) && (
            <div className="space-y-3">
              {outputData.conclusion && (
                <div className="p-3 bg-accent-green/10 border border-accent-green/30 rounded-lg">
                  <div className="text-xs text-accent-green mb-1">Conclusion</div>
                  <p className="text-sm text-white">{outputData.conclusion}</p>
                </div>
              )}
              {outputData.reasoning && (
                <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
                  <div className="text-xs text-gray-400 mb-1">Reasoning</div>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{outputData.reasoning}</p>
                </div>
              )}
            </div>
          )}

          {/* String content */}
          {typeof outputData.content === 'string' && (
            <div className="p-3 bg-dark-card rounded-lg border border-dark-border">
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{outputData.content}</p>
            </div>
          )}

          {/* Success/Error status */}
          {outputData.success !== undefined && (
            <div className={cn(
              "flex items-center gap-2 p-3 rounded-lg border",
              outputData.success
                ? "bg-accent-green/10 border-accent-green/30 text-accent-green"
                : "bg-accent-red/10 border-accent-red/30 text-accent-red"
            )}>
              {outputData.success ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
              <span className="text-sm font-medium">{outputData.success ? 'Success' : 'Failed'}</span>
              {outputData.error && <span className="text-sm ml-2">- {outputData.error}</span>}
            </div>
          )}

          {/* Fallback for unstructured data */}
          {!hasStructuredContent && !outputData.message && !outputData.task && !outputData.summary &&
           outputData.success === undefined && typeof outputData.content !== 'string' && (
            <pre className="text-xs bg-dark-bg p-4 rounded-lg overflow-auto font-mono text-gray-300 border border-dark-border">
              {JSON.stringify(outputData, null, 2)}
            </pre>
          )}
        </>
      )}
    </div>
  )
}

export default SmartOutputRenderer
