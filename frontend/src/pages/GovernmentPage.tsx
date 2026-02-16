import { useState, useRef, useCallback } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Landmark,
  FileText,
  MessageSquare,
  Loader2,
  Search,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Send,
  Users,
  Building2,
  Tag,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { governmentApi, assistantApi, type GovernmentBill } from '@/lib/api'
import { ChatMarkdown } from '@/components/ChatMarkdown'

// Sub-tab config
type SubTab = 'hub' | 'bills' | 'ask'
const subTabs: Array<{ id: SubTab; label: string; icon: typeof Landmark }> = [
  { id: 'hub', label: 'Hub', icon: Landmark },
  { id: 'bills', label: 'Bills', icon: FileText },
  { id: 'ask', label: 'Ask A Bill', icon: MessageSquare },
]

export default function GovernmentPage() {
  const [activeTab, setActiveTab] = useState<SubTab>('hub')

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center gap-3 mb-4">
        <Landmark size={24} className="text-primary-400" />
        <h1 className="text-2xl font-bold text-white">Government & Legislation</h1>
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'hub' && <HubTab />}
      {activeTab === 'bills' && <BillsTab />}
      {activeTab === 'ask' && <AskTab />}
    </div>
  )
}

// =============================================================================
// Hub Tab
// =============================================================================

function HubTab() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['government-hub'],
    queryFn: async () => {
      const res = await governmentApi.hub()
      return res.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-primary-400" size={32} />
      </div>
    )
  }

  if (error || !data?.success) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
        Failed to load government data. The legislation spider may not have run yet.
      </div>
    )
  }

  const { stats, top_topics, bills } = data

  return (
    <div className="space-y-6">
      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Bills"
          value={stats.total_bills}
          icon={<FileText size={18} />}
        />
        <StatCard
          label="House Bills"
          value={stats.house_count}
          icon={<Building2 size={18} />}
          color="text-green-400"
        />
        <StatCard
          label="Senate Bills"
          value={stats.senate_count}
          icon={<Users size={18} />}
          color="text-blue-400"
        />
        <StatCard
          label="Topics"
          value={top_topics.length}
          icon={<Tag size={18} />}
          color="text-purple-400"
        />
      </div>

      {/* Two-panel: Bills + Ask A Bill */}
      <div className="grid lg:grid-cols-5 gap-6">
        {/* Bills list — wider */}
        <div className="lg:col-span-3 space-y-3">
          <h2 className="text-lg font-semibold text-white">Recent Bills</h2>
          {bills.length === 0 ? (
            <div className="bg-gray-800/50 rounded-lg p-6 text-gray-400 text-center">
              No legislation data yet. The spider may not have run.
            </div>
          ) : (
            bills.slice(0, 8).map((bill) => (
              <BillCard key={bill.id} bill={bill} />
            ))
          )}
        </div>

        {/* Ask A Bill chat — narrower */}
        <div className="lg:col-span-2">
          <h2 className="text-lg font-semibold text-white mb-3">Ask A Bill</h2>
          <AskABillChat />
        </div>
      </div>

      {/* Top Topics */}
      {top_topics.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">Top Topics</h2>
          <div className="flex flex-wrap gap-2">
            {top_topics.map((t) => (
              <span
                key={t.topic}
                className="px-3 py-1.5 rounded-full bg-gray-800 text-gray-300 text-sm border border-gray-700"
              >
                {t.topic} <span className="text-gray-500">({t.count})</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Bills Tab — Full-width filterable list
// =============================================================================

function BillsTab() {
  const [search, setSearch] = useState('')
  const [chamberFilter, setChamberFilter] = useState<'all' | 'house' | 'senate'>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data, isLoading } = useQuery({
    queryKey: ['government-hub'],
    queryFn: async () => {
      const res = await governmentApi.hub()
      return res.data
    },
  })

  const bills = data?.bills || []
  const statusOptions = Object.keys(data?.stats?.status_breakdown || {})

  const filtered = bills.filter((b) => {
    // Search
    if (search) {
      const q = search.toLowerCase()
      const matchesSearch =
        b.bill_number.toLowerCase().includes(q) ||
        b.title.toLowerCase().includes(q) ||
        b.description.toLowerCase().includes(q) ||
        b.topics.some((t) => t.toLowerCase().includes(q))
      if (!matchesSearch) return false
    }

    // Chamber
    if (chamberFilter !== 'all') {
      const bn = b.bill_number.toUpperCase()
      if (chamberFilter === 'house' && !bn.match(/^(HR|H\.R|HB|HJR|HRES)/)) return false
      if (chamberFilter === 'senate' && !bn.match(/^(S|SB|SJR|SRES)/)) return false
    }

    // Status
    if (statusFilter !== 'all' && b.status !== statusFilter) return false

    return true
  })

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
          <input
            type="text"
            placeholder="Search bills by number, title, or topic..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        <select
          value={chamberFilter}
          onChange={(e) => setChamberFilter(e.target.value as 'all' | 'house' | 'senate')}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
        >
          <option value="all">All Chambers</option>
          <option value="house">House</option>
          <option value="senate">Senate</option>
        </select>

        {statusOptions.length > 0 && (
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="all">All Statuses</option>
            {statusOptions.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        )}
      </div>

      {/* Results count */}
      <p className="text-sm text-gray-400">
        {filtered.length} bill{filtered.length !== 1 ? 's' : ''} found
      </p>

      {/* Bill Cards */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="animate-spin text-primary-400" size={32} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-gray-800/50 rounded-lg p-6 text-gray-400 text-center">
          No bills match your filters.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((bill) => (
            <BillCard key={bill.id} bill={bill} expandable />
          ))}
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Ask Tab — Full-width dedicated chat
// =============================================================================

function AskTab() {
  return (
    <div className="max-w-3xl mx-auto">
      <p className="text-gray-400 text-sm mb-4">
        Ask questions about legislation in plain English. Answers are grounded in actual bill text
        — Reps can lie but the Bills won't.
      </p>
      <AskABillChat fullWidth />
    </div>
  )
}

// =============================================================================
// Shared Components
// =============================================================================

function StatCard({
  label,
  value,
  icon,
  color = 'text-primary-400',
}: {
  label: string
  value: number
  icon: React.ReactNode
  color?: string
}) {
  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-1">
        <span className={color}>{icon}</span>
        <span className="text-xs text-gray-400 uppercase tracking-wide">{label}</span>
      </div>
      <p className="text-2xl font-bold text-white">{value.toLocaleString()}</p>
    </div>
  )
}

function BillCard({ bill, expandable = false }: { bill: GovernmentBill; expandable?: boolean }) {
  const [expanded, setExpanded] = useState(false)

  const bn = bill.bill_number.toUpperCase()
  const isSenate = bn.match(/^(S|SB|SJR|SRES)/)
  const chamberColor = isSenate
    ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    : 'bg-green-500/20 text-green-400 border-green-500/30'
  const chamberLabel = isSenate ? 'Senate' : 'House'

  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg overflow-hidden">
      <div
        className={cn('p-4', expandable && 'cursor-pointer hover:bg-gray-800/80')}
        onClick={expandable ? () => setExpanded(!expanded) : undefined}
      >
        <div className="flex items-start gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono font-semibold text-white text-sm">{bill.bill_number}</span>
              <span className={cn('px-2 py-0.5 rounded text-xs border', chamberColor)}>
                {chamberLabel}
              </span>
              {bill.status && (
                <span className="px-2 py-0.5 rounded text-xs bg-gray-700/50 text-gray-300 border border-gray-600/50">
                  {bill.status}
                </span>
              )}
            </div>
            <p className="text-gray-200 text-sm line-clamp-2">{bill.title}</p>
          </div>
          {expandable && (
            <button className="text-gray-500 flex-shrink-0 mt-1">
              {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-gray-700/50 p-4 space-y-3 bg-gray-900/30">
          {bill.description && (
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wide mb-1">Description</h4>
              <p className="text-gray-300 text-sm">{bill.description}</p>
            </div>
          )}
          {bill.plain_summary && (
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wide mb-1">Plain Summary</h4>
              <p className="text-gray-300 text-sm">{bill.plain_summary}</p>
            </div>
          )}
          {bill.sponsors.length > 0 && (
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wide mb-1">Sponsors</h4>
              <div className="flex flex-wrap gap-2">
                {bill.sponsors.map((s, i) => (
                  <span key={i} className="px-2 py-1 rounded bg-gray-800 text-gray-300 text-xs">
                    {s.name}
                    {s.party && <span className="text-gray-500 ml-1">({s.party})</span>}
                  </span>
                ))}
                {bill.sponsor_count > bill.sponsors.length && (
                  <span className="px-2 py-1 text-gray-500 text-xs">
                    +{bill.sponsor_count - bill.sponsors.length} more
                  </span>
                )}
              </div>
            </div>
          )}
          {bill.committee && (
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wide mb-1">Committee</h4>
              <p className="text-gray-300 text-sm">{bill.committee}</p>
            </div>
          )}
          {bill.topics.length > 0 && (
            <div>
              <h4 className="text-xs text-gray-400 uppercase tracking-wide mb-1">Topics</h4>
              <div className="flex flex-wrap gap-1.5">
                {bill.topics.map((t) => (
                  <span key={t} className="px-2 py-0.5 rounded-full bg-gray-700/50 text-gray-400 text-xs">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}
          {bill.last_action && (
            <p className="text-xs text-gray-500">
              Last action: {bill.last_action}
              {bill.last_action_date && ` (${bill.last_action_date})`}
            </p>
          )}
          <div className="flex gap-3">
            {bill.url && (
              <a
                href={bill.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
              >
                <ExternalLink size={12} /> Full text
              </a>
            )}
            {bill.congress_gov_url && (
              <a
                href={bill.congress_gov_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300"
              >
                <ExternalLink size={12} /> Congress.gov
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Ask A Bill Chat
// =============================================================================

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const SUGGESTED_QUESTIONS = [
  'How does the healthcare bill affect regular people?',
  'What bills about AI are in Congress?',
  'Explain the immigration bill in simple terms',
]

function AskABillChat({ fullWidth = false }: { fullWidth?: boolean }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isPolling, setIsPolling] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg])
    setTimeout(scrollToBottom, 100)
  }, [scrollToBottom])

  const sendMessage = useMutation({
    mutationFn: (message: string) =>
      assistantApi.paChat(`legislation ${message}`, {
        context: { source: 'government_page' },
      }),
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      pollRef.current = setInterval(async () => {
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (status.data.status === 'completed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({
              role: 'assistant',
              content: status.data.content || 'No response',
            })
          } else if (status.data.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({
              role: 'assistant',
              content: status.data.error || 'Sorry, there was an error. Please try again.',
            })
          }
        } catch {
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          addMessage({
            role: 'assistant',
            content: 'Sorry, there was an error. Please try again.',
          })
        }
      }, 1500)
    },
    onError: () => {
      addMessage({
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.',
      })
    },
  })

  const isBusy = sendMessage.isPending || isPolling

  const handleSend = (text?: string) => {
    const msg = text || input.trim()
    if (!msg || isBusy) return
    addMessage({ role: 'user', content: msg })
    setInput('')
    sendMessage.mutate(msg)
  }

  return (
    <div
      className={cn(
        'flex flex-col bg-gray-900/50 border border-gray-700/50 rounded-lg',
        fullWidth ? 'h-[700px]' : 'h-[600px] lg:sticky lg:top-6'
      )}
    >
      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <MessageSquare size={32} className="text-gray-600" />
            <div>
              <p className="text-gray-400 text-sm mb-1">Ask questions about legislation</p>
              <p className="text-gray-500 text-xs">Answers grounded in actual bill text</p>
            </div>
            <div className="space-y-2 w-full max-w-sm">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  disabled={isBusy}
                  className="w-full px-3 py-2 text-left text-sm text-gray-300 bg-gray-800/50 border border-gray-700/50 rounded-lg hover:bg-gray-800 hover:text-white transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={cn(
                'flex',
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-[85%] rounded-lg px-4 py-3',
                  msg.role === 'user'
                    ? 'bg-primary-600/20 border border-primary-500/30 text-gray-200'
                    : 'bg-gray-800/50 border border-gray-700/50'
                )}
              >
                {msg.role === 'assistant' ? (
                  <ChatMarkdown content={msg.content} />
                ) : (
                  <p className="text-sm">{msg.content}</p>
                )}
              </div>
            </div>
          ))
        )}

        {isBusy && (
          <div className="flex justify-start">
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-3 flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-primary-400" />
              <span className="text-sm text-gray-400">Analyzing legislation...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700/50 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask about any bill..."
            disabled={isBusy}
            className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-primary-500 disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isBusy}
            className="px-3 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50 disabled:hover:bg-primary-600"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
