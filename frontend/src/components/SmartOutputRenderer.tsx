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

import { useState } from 'react'
import {
  BookOpen, Mic, Lightbulb, BarChart3, Signal,
  Image as ImageIcon, Wrench, ChevronDown, ChevronRight, ExternalLink,
  Clock, Users, TrendingUp, AlertCircle, CheckCircle, XCircle,
  Brain, Sparkles, ListChecks, Newspaper, Radio
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

// Session 820: Trend and Discussion interfaces for TopicMiner/TrendAnalysis output
interface TrendItem {
  topic?: string
  title?: string
  source?: string
  relevance?: number
  score?: number
  mentions?: number
  articles?: unknown[]
}

interface DiscussionItem {
  title?: string
  description?: string
  url?: string
  source?: string
  category?: string
  similarity?: number
}

// Session 820: Specialist delegation result (agent delegation patterns)
interface SpecialistResult {
  success?: boolean
  specialist?: string
  delegating_agent?: string
  specialist_response?: string
  specialist_data?: {
    task?: string
    tool_results?: ToolResult[]
    [key: string]: unknown
  }
}

// Session 820: Helper to unwrap nested specialist delegation patterns
function unwrapSpecialistData(data: OutputData): {
  trends: TrendItem[]
  discussions: DiscussionItem[]
  delegations: { specialist: string; task: string }[]
  unwrappedTask?: string
} {
  const trends: TrendItem[] = []
  const discussions: DiscussionItem[] = []
  const delegations: { specialist: string; task: string }[] = []
  let unwrappedTask: string | undefined

  // Check for direct trends/discussions
  if (data.trends && Array.isArray(data.trends)) {
    trends.push(...data.trends)
  }
  if (data.discussions && Array.isArray(data.discussions)) {
    discussions.push(...data.discussions)
  }

  // Check tool_results for specialist delegations
  if (data.tool_results && Array.isArray(data.tool_results)) {
    for (const tr of data.tool_results) {
      const toolResult = tr as SpecialistResult

      // Track delegation
      if (toolResult.specialist) {
        delegations.push({
          specialist: toolResult.specialist,
          task: toolResult.specialist_data?.task || 'Delegated task'
        })
      }

      // Look for trends/discussions in specialist_data.tool_results
      if (toolResult.specialist_data?.tool_results) {
        for (const innerTr of toolResult.specialist_data.tool_results) {
          const result = innerTr.result as Record<string, unknown> | undefined
          if (result) {
            if (result.trends && Array.isArray(result.trends)) {
              trends.push(...result.trends)
            }
            if (result.discussions && Array.isArray(result.discussions)) {
              discussions.push(...result.discussions)
            }
          }
        }
        // Get the task from specialist_data
        if (toolResult.specialist_data.task) {
          unwrappedTask = toolResult.specialist_data.task
        }
      }

      // Also check direct result object
      const directResult = tr.result as Record<string, unknown> | undefined
      if (directResult) {
        if (directResult.trends && Array.isArray(directResult.trends)) {
          trends.push(...directResult.trends)
        }
        if (directResult.discussions && Array.isArray(directResult.discussions)) {
          discussions.push(...directResult.discussions)
        }
      }
    }
  }

  return { trends, discussions, delegations, unwrappedTask }
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

// Session 822: Smart Tool Results Renderer
// Renders executive tools (roadmap, sprint, risk) with nice cards instead of raw JSON
function ToolResultsRenderer({ results }: { results: ToolResult[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-amber flex items-center gap-2">
        <Wrench className="w-4 h-4" />
        Tool Results ({results.length})
      </h4>
      <div className="space-y-3">
        {results.map((tr, i) => {
          const result = tr.result as Record<string, unknown> | undefined
          const toolName = tr.tool || tr.name || `Tool ${i + 1}`

          // Detect and render specific tool types
          if (result?.analysis && typeof result.analysis === 'object') {
            return <RoadmapAnalysisCard key={i} toolName={toolName} data={result.analysis as RoadmapAnalysis} />
          }
          if (result?.plan && typeof result.plan === 'object') {
            return <SprintPlanCard key={i} toolName={toolName} data={result.plan as SprintPlan} />
          }
          if (result?.assessment && typeof result.assessment === 'object') {
            return <RiskAssessmentCard key={i} toolName={toolName} data={result.assessment as RiskAssessment} />
          }

          // Fallback: Collapsible JSON view for unknown tools
          return <GenericToolCard key={i} toolName={toolName} result={tr} />
        })}
      </div>
    </div>
  )
}

// Types for executive tools
interface RoadmapAnalysis {
  scope?: string
  timeframe?: string
  priorities?: Array<{ priority: number; item: string; status: string }>
  recommendations?: string[]
}

interface SprintPlan {
  sprint_name?: string
  duration_days?: number
  focus_area?: string
  suggested_tasks?: Array<{ task: string; estimate: string }>
  capacity_notes?: string
  notes?: string
}

interface RiskAssessment {
  area?: string
  identified_risks?: Array<{ risk: string; severity: string; mitigation: string }>
  overall_risk_level?: string
  recommendations?: string[]
}

// Roadmap Analysis Card
function RoadmapAnalysisCard({ toolName, data }: { toolName: string; data: RoadmapAnalysis }) {
  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4 space-y-3">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-accent-blue" />
        <span className="text-sm font-medium text-white">{toolName}</span>
        {data.scope && <span className="text-xs px-2 py-0.5 bg-accent-blue/20 text-accent-blue rounded">{data.scope}</span>}
        {data.timeframe && <span className="text-xs text-gray-400">{data.timeframe}</span>}
      </div>

      {data.priorities && data.priorities.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Priorities</span>
          <div className="space-y-1">
            {data.priorities.map((p, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="w-5 h-5 rounded-full bg-accent-amber/20 text-accent-amber text-xs flex items-center justify-center font-medium">
                  {p.priority}
                </span>
                <span className="text-gray-200 flex-1">{p.item}</span>
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded",
                  p.status === 'in_progress' ? 'bg-accent-blue/20 text-accent-blue' :
                  p.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                  'bg-gray-700 text-gray-400'
                )}>{p.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.recommendations && data.recommendations.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Recommendations</span>
          <ul className="space-y-1">
            {data.recommendations.map((rec, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <Lightbulb className="w-3 h-3 text-accent-amber mt-1 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// Sprint Plan Card
function SprintPlanCard({ toolName, data }: { toolName: string; data: SprintPlan }) {
  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4 space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <ListChecks className="w-4 h-4 text-accent-green" />
        <span className="text-sm font-medium text-white">{data.sprint_name || toolName}</span>
        {data.duration_days && (
          <span className="text-xs px-2 py-0.5 bg-accent-green/20 text-accent-green rounded flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {data.duration_days} days
          </span>
        )}
      </div>

      {data.focus_area && (
        <p className="text-sm text-gray-400">
          <span className="text-gray-500">Focus:</span> {data.focus_area}
        </p>
      )}

      {data.suggested_tasks && data.suggested_tasks.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Tasks</span>
          <div className="space-y-1">
            {data.suggested_tasks.map((t, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-3 h-3 text-gray-500" />
                <span className="text-gray-200 flex-1">{t.task}</span>
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded",
                  t.estimate === 'small' ? 'bg-accent-green/20 text-accent-green' :
                  t.estimate === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                  'bg-accent-red/20 text-accent-red'
                )}>{t.estimate}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.notes && (
        <p className="text-xs text-gray-500 italic">{data.notes}</p>
      )}
    </div>
  )
}

// Risk Assessment Card
function RiskAssessmentCard({ toolName, data }: { toolName: string; data: RiskAssessment }) {
  const riskLevelColor = {
    low: 'bg-accent-green/20 text-accent-green',
    medium: 'bg-accent-amber/20 text-accent-amber',
    high: 'bg-accent-red/20 text-accent-red',
    critical: 'bg-red-600/30 text-red-400'
  }[data.overall_risk_level || 'low'] || 'bg-gray-700 text-gray-400'

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4 space-y-3">
      <div className="flex items-center gap-2">
        <AlertCircle className="w-4 h-4 text-accent-amber" />
        <span className="text-sm font-medium text-white">{toolName}</span>
        {data.area && <span className="text-xs text-gray-400">({data.area})</span>}
        {data.overall_risk_level && (
          <span className={cn("text-xs px-2 py-0.5 rounded uppercase", riskLevelColor)}>
            {data.overall_risk_level} risk
          </span>
        )}
      </div>

      {data.identified_risks && data.identified_risks.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Identified Risks</span>
          <div className="space-y-2">
            {data.identified_risks.map((r, i) => (
              <div key={i} className="bg-dark-bg rounded p-2 space-y-1">
                <div className="flex items-center gap-2">
                  <span className={cn(
                    "text-xs px-1.5 py-0.5 rounded uppercase",
                    r.severity === 'low' ? 'bg-accent-green/20 text-accent-green' :
                    r.severity === 'medium' ? 'bg-accent-amber/20 text-accent-amber' :
                    'bg-accent-red/20 text-accent-red'
                  )}>{r.severity}</span>
                  <span className="text-sm text-white">{r.risk}</span>
                </div>
                <p className="text-xs text-gray-400 pl-2">
                  <span className="text-gray-500">Mitigation:</span> {r.mitigation}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.recommendations && data.recommendations.length > 0 && (
        <div className="space-y-2">
          <span className="text-xs text-gray-400 uppercase tracking-wide">Recommendations</span>
          <ul className="space-y-1">
            {data.recommendations.map((rec, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <CheckCircle className="w-3 h-3 text-accent-green mt-1 flex-shrink-0" />
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// Generic Tool Card (fallback for unknown tools)
function GenericToolCard({ toolName, result }: { toolName: string; result: ToolResult }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 flex items-center justify-between hover:bg-dark-lighter transition-colors"
      >
        <div className="flex items-center gap-2">
          <Wrench className="w-4 h-4 text-accent-amber" />
          <span className="text-sm text-white font-medium">{toolName}</span>
          {result.success !== undefined && (
            result.success ?
              <CheckCircle className="w-4 h-4 text-accent-green" /> :
              <XCircle className="w-4 h-4 text-accent-red" />
          )}
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
      </button>
      {expanded && result.result != null && (
        <div className="p-3 border-t border-dark-border bg-dark-bg">
          <pre className="text-xs text-gray-300 overflow-auto max-h-40 font-mono">
            {typeof result.result === 'string' ? result.result : JSON.stringify(result.result, null, 2) as string}
          </pre>
        </div>
      )}
    </div>
  )
}

// Session 820: Trending Topics
function TrendsRenderer({ trends }: { trends: TrendItem[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-amber flex items-center gap-2">
        <TrendingUp className="w-4 h-4" />
        Trending Topics ({trends.length})
      </h4>
      <div className="space-y-2">
        {trends.slice(0, 15).map((trend, i) => (
          <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium line-clamp-2">
                  {trend.topic || trend.title || `Topic ${i + 1}`}
                </p>
                {trend.source && (
                  <span className="inline-block mt-1 px-2 py-0.5 text-xs bg-accent-cyan/20 text-accent-cyan rounded">
                    {trend.source}
                  </span>
                )}
              </div>
              {(trend.relevance !== undefined || trend.score !== undefined) && (
                <div className="flex-shrink-0 text-right">
                  <div className="text-lg font-bold text-accent-amber">
                    {((trend.relevance ?? trend.score ?? 0) * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">relevance</div>
                </div>
              )}
              {trend.mentions !== undefined && (
                <div className="flex-shrink-0 text-right">
                  <div className="text-lg font-bold text-accent-purple">
                    {trend.mentions}
                  </div>
                  <div className="text-xs text-gray-500">mentions</div>
                </div>
              )}
            </div>
          </div>
        ))}
        {trends.length > 15 && (
          <p className="text-xs text-gray-500 text-center">+ {trends.length - 15} more topics</p>
        )}
      </div>
    </div>
  )
}

// Session 820: Discussions/Articles
function DiscussionsRenderer({ discussions }: { discussions: DiscussionItem[] }) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-accent-green flex items-center gap-2">
        <Newspaper className="w-4 h-4" />
        Related Discussions ({discussions.length})
      </h4>
      <div className="space-y-2">
        {discussions.slice(0, 10).map((disc, i) => (
          <div key={i} className="p-3 bg-dark-card rounded-lg border border-dark-border">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                {disc.url ? (
                  <a
                    href={disc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-white font-medium hover:text-accent-cyan transition-colors line-clamp-2 flex items-start gap-1"
                  >
                    {disc.title || 'Discussion'}
                    <ExternalLink className="w-3 h-3 flex-shrink-0 mt-0.5 text-gray-500" />
                  </a>
                ) : (
                  <p className="text-sm text-white font-medium line-clamp-2">
                    {disc.title || 'Discussion'}
                  </p>
                )}
                {disc.description && (
                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">{disc.description}</p>
                )}
                <div className="flex items-center gap-2 mt-2">
                  {disc.source && (
                    <span className="px-2 py-0.5 text-xs bg-accent-green/20 text-accent-green rounded">
                      {disc.source}
                    </span>
                  )}
                  {disc.category && (
                    <span className="px-2 py-0.5 text-xs bg-gray-700 text-gray-300 rounded">
                      {disc.category}
                    </span>
                  )}
                </div>
              </div>
              {disc.similarity !== undefined && (
                <div className="flex-shrink-0 text-right">
                  <div className="text-sm font-bold text-accent-green">
                    {(disc.similarity * 100).toFixed(0)}%
                  </div>
                  <div className="text-xs text-gray-500">match</div>
                </div>
              )}
            </div>
          </div>
        ))}
        {discussions.length > 10 && (
          <p className="text-xs text-gray-500 text-center">+ {discussions.length - 10} more discussions</p>
        )}
      </div>
    </div>
  )
}

// Session 820: Specialist Delegations
function DelegationsRenderer({ delegations }: { delegations: { specialist: string; task: string }[] }) {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-accent-purple flex items-center gap-2">
        <Users className="w-4 h-4" />
        Agent Delegations ({delegations.length})
      </h4>
      <div className="space-y-1">
        {delegations.map((del, i) => (
          <div key={i} className="p-2 bg-accent-purple/10 border border-accent-purple/30 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-xs text-accent-purple font-medium">{del.specialist}</span>
            </div>
            <p className="text-xs text-gray-400 mt-1 line-clamp-2">{del.task}</p>
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
  agentName: _agentName,
  maxHeight = '600px',
  showRawToggle = true,
  className
}: SmartOutputRendererProps) {
  const [showRaw, setShowRaw] = useState(false)

  // Handle null/undefined/string data
  if (!data) {
    return <p className="text-sm text-gray-500 italic">No output data</p>
  }

  let parsedData: OutputData
  if (typeof data === 'string') {
    // Try to parse as JSON
    try {
      parsedData = JSON.parse(data) as OutputData
    } catch {
      // If not JSON, render as text
      return (
        <div className={cn("p-3 bg-dark-card rounded-lg", className)}>
          <p className="text-sm text-gray-300 whitespace-pre-wrap">{data}</p>
        </div>
      )
    }
  } else {
    parsedData = data
  }

  const outputData = parsedData

  // Session 820: Unwrap specialist delegation patterns to extract trends/discussions
  const { trends, discussions, delegations, unwrappedTask } = unwrapSpecialistData(outputData)
  const hasTrends = trends.length > 0
  const hasDiscussions = discussions.length > 0
  const hasDelegations = delegations.length > 0

  // Determine what type of content we have
  const hasBlog = outputData.content && typeof outputData.content === 'object' &&
    ('title' in outputData.content || 'sections' in outputData.content || 'body' in outputData.content)
  const hasResearch = outputData.results && Array.isArray(outputData.results) && outputData.results.length > 0
  const hasPodcast = outputData.episodes || outputData.transcript || (outputData.topics && outputData.speakers)
  const hasRecommendations = outputData.recommendations && Array.isArray(outputData.recommendations) && outputData.recommendations.length > 0
  const hasAnalysis = outputData.analysis && typeof outputData.analysis === 'object'
  const hasSignals = outputData.signals && Array.isArray(outputData.signals) && outputData.signals.length > 0
  // Don't show raw tool_results if we've already extracted trends/discussions from them
  const hasToolResults = !hasTrends && !hasDiscussions &&
    outputData.tool_results && Array.isArray(outputData.tool_results) && outputData.tool_results.length > 0
  const hasImages = outputData.images && Array.isArray(outputData.images) && outputData.images.length > 0
  const hasThinking = outputData.thinking_result && typeof outputData.thinking_result === 'object'
  const hasMetrics = outputData.items_count !== undefined || outputData.info_count !== undefined ||
    outputData.warning_count !== undefined || outputData.critical_count !== undefined
  const hasInsights = (outputData.insights && Array.isArray(outputData.insights) && outputData.insights.length > 0) ||
    (outputData.key_insights && Array.isArray(outputData.key_insights) && outputData.key_insights.length > 0)

  // Check if we have any structured content
  const hasStructuredContent = hasBlog || hasResearch || hasPodcast || hasRecommendations ||
    hasAnalysis || hasSignals || hasToolResults || hasImages || hasThinking || hasMetrics || hasInsights ||
    hasTrends || hasDiscussions

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

          {/* Task (use unwrapped task if available from specialist delegation) */}
          {(unwrappedTask || outputData.task) && (
            <div className="p-3 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg">
              <div className="text-xs text-accent-cyan mb-1">Task</div>
              <p className="text-sm text-white">{unwrappedTask || outputData.task}</p>
            </div>
          )}

          {/* Session 820: Agent Delegations */}
          {hasDelegations && <DelegationsRenderer delegations={delegations} />}

          {/* Session 820: Trending Topics (unwrapped from specialist data) */}
          {hasTrends && <TrendsRenderer trends={trends} />}

          {/* Session 820: Related Discussions (unwrapped from specialist data) */}
          {hasDiscussions && <DiscussionsRenderer discussions={discussions} />}

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
