// Session 1008: Campaign Orchestrator Tab
// List / Create / Detail views for marketing campaigns

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Megaphone,
  Loader2,
  RefreshCw,
  Trash2,
  Play,
  CheckCircle,
  Plus,
  ArrowLeft,
  ChevronRight,
  Clock,
  DollarSign,
  Target,
  FileText,
  Image,
  Mail,
  Video,
  Share2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { campaignApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// ============ Types ============

interface Campaign {
  id: string
  name: string
  client_name?: string
  product_name: string
  product_description?: string
  target_market?: string
  target_location?: string
  budget_tier: string
  status: string
  progress_percentage: number
  platforms: string[]
  deliverable_counts?: Record<string, number>
  created_at: string
  updated_at?: string
}

interface CampaignDetail extends Campaign {
  competitors?: string
  brand_colors?: string
  brand_style?: string
  research_items?: Array<{
    id: string
    research_type: string
    title: string
    summary?: string
    created_at: string
  }>
  deliverables?: Deliverable[]
  execution_log?: Array<{
    phase: string
    message: string
    timestamp: string
  }>
}

interface Deliverable {
  id: string
  deliverable_type: string
  title: string
  status: string
  platform?: string
  content_preview?: string
  created_at: string
}

interface BudgetTier {
  id: string
  name: string
  budget_range: string
  description: string
}

type ViewMode = 'list' | 'create' | 'detail'

const PHASES = ['intake', 'research', 'strategy', 'creation', 'review', 'complete'] as const

const STATUS_COLORS: Record<string, string> = {
  intake: 'bg-gray-500/20 text-gray-400',
  research: 'bg-blue-500/20 text-blue-400',
  strategy: 'bg-purple-500/20 text-purple-400',
  creation: 'bg-amber-500/20 text-amber-400',
  review: 'bg-orange-500/20 text-orange-400',
  complete: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
}

const DELIVERABLE_ICONS: Record<string, typeof FileText> = {
  ad_copy: FileText,
  image: Image,
  email: Mail,
  video: Video,
  social_post: Share2,
}

// ============ Main Component ============

export function CampaignTab() {
  const [view, setView] = useState<ViewMode>('list')
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string | null>(null)

  const openDetail = (id: string) => {
    setSelectedId(id)
    setView('detail')
  }

  const goBack = () => {
    setView('list')
    setSelectedId(null)
  }

  return (
    <div className="space-y-4">
      {view === 'list' && (
        <CampaignListView
          statusFilter={statusFilter}
          setStatusFilter={setStatusFilter}
          onSelect={openDetail}
          onCreate={() => setView('create')}
        />
      )}
      {view === 'create' && (
        <CampaignCreateForm
          onBack={goBack}
          onCreated={(id) => openDetail(id)}
        />
      )}
      {view === 'detail' && selectedId && (
        <CampaignDetailView
          campaignId={selectedId}
          onBack={goBack}
        />
      )}
    </div>
  )
}

// ============ Campaign List View ============

function CampaignListView({
  statusFilter,
  setStatusFilter,
  onSelect,
  onCreate,
}: {
  statusFilter: string | null
  setStatusFilter: (s: string | null) => void
  onSelect: (id: string) => void
  onCreate: () => void
}) {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['campaigns', statusFilter],
    queryFn: () => campaignApi.list(statusFilter ? { status: statusFilter } : undefined),
    select: (res) => res.data?.results ?? res.data ?? [],
  })

  const campaigns = (data ?? []) as Campaign[]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Megaphone size={20} className="text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Campaigns</h3>
          <span className="text-sm text-gray-500">({campaigns.length})</span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg bg-gray-800/50 text-gray-400 hover:text-white transition-colors"
          >
            <RefreshCw size={14} />
          </button>
          <button
            onClick={onCreate}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors text-sm"
          >
            <Plus size={14} />
            New Campaign
          </button>
        </div>
      </div>

      {/* Status filters */}
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => setStatusFilter(null)}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs transition-colors',
            !statusFilter
              ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
              : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800'
          )}
        >
          All
        </button>
        {PHASES.map((phase) => (
          <button
            key={phase}
            onClick={() => setStatusFilter(phase)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs capitalize transition-colors',
              statusFilter === phase
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800'
            )}
          >
            {phase}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-primary-400" size={24} />
        </div>
      )}

      {error && <ErrorState error={error as Error} message="Failed to load campaigns" onRetry={() => refetch()} />}

      {!isLoading && !error && campaigns.length === 0 && (
        <div className="text-center py-16 max-w-md mx-auto">
          <Megaphone size={40} className="mx-auto text-indigo-400 mb-4" />
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Turn content into campaigns</h3>
          <p className="text-gray-400 text-sm mb-6">
            Package published assets, schedule distribution, and measure impact across platforms.
          </p>
          <button
            onClick={onCreate}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition-colors mb-6"
          >
            <Plus size={16} className="inline mr-1.5 -mt-0.5" />
            Create your first campaign
          </button>
          <div className="text-left bg-dark-card border border-dark-border rounded-lg p-4 space-y-2">
            <p className="text-xs text-gray-500 uppercase tracking-wide font-medium mb-2">What you can do</p>
            <p className="text-sm text-gray-400 flex items-start gap-2"><Target size={14} className="mt-0.5 text-gray-500 shrink-0" /> Choose assets and target channels</p>
            <p className="text-sm text-gray-400 flex items-start gap-2"><Clock size={14} className="mt-0.5 text-gray-500 shrink-0" /> Schedule and automate delivery</p>
            <p className="text-sm text-gray-400 flex items-start gap-2"><Play size={14} className="mt-0.5 text-gray-500 shrink-0" /> Track performance across platforms</p>
          </div>
        </div>
      )}

      {!isLoading && !error && campaigns.length > 0 && (
        <div className="grid gap-3">
          {campaigns.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.id)}
              className="w-full text-left p-4 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/30 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-white">{c.name}</span>
                  <span className={cn('px-2 py-0.5 rounded text-xs capitalize', STATUS_COLORS[c.status] ?? STATUS_COLORS.intake)}>
                    {c.status}
                  </span>
                </div>
                <ChevronRight size={14} className="text-gray-500" />
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-400">
                {c.client_name && <span>{c.client_name}</span>}
                <span>{c.product_name}</span>
                <span className="flex items-center gap-1">
                  <DollarSign size={10} />
                  {c.budget_tier}
                </span>
              </div>
              {/* Progress bar */}
              <div className="mt-3 h-1.5 rounded-full bg-gray-800 overflow-hidden">
                <div
                  className="h-full rounded-full bg-primary-500 transition-all"
                  style={{ width: `${c.progress_percentage ?? 0}%` }}
                />
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-xs text-gray-500">{c.progress_percentage ?? 0}%</span>
                {c.deliverable_counts && (
                  <span className="text-xs text-gray-500">
                    {Object.values(c.deliverable_counts).reduce((a, b) => a + b, 0)} deliverables
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

// ============ Campaign Create Form ============

const PLATFORM_OPTIONS = ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok', 'youtube', 'email', 'google_ads']

function CampaignCreateForm({
  onBack,
  onCreated,
}: {
  onBack: () => void
  onCreated: (id: string) => void
}) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    name: '',
    product_name: '',
    product_description: '',
    target_market: '',
    target_location: '',
    budget_tier: 'starter',
    platforms: [] as string[],
    client_name: '',
    competitors: '',
    brand_colors: '',
    brand_style: '',
  })

  const { data: tiersData } = useQuery({
    queryKey: ['campaign-budget-tiers'],
    queryFn: () => campaignApi.budgetTiers(),
    select: (res) => (res.data?.tiers ?? res.data ?? []) as BudgetTier[],
  })

  const tiers = tiersData ?? []

  const createMutation = useMutation({
    mutationFn: (data: Record<string, unknown>) => campaignApi.create(data),
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      const id = res.data?.id ?? res.data?.campaign?.id
      if (id) onCreated(id)
      else onBack()
    },
  })

  const togglePlatform = (p: string) => {
    setForm((f) => ({
      ...f,
      platforms: f.platforms.includes(p) ? f.platforms.filter((x) => x !== p) : [...f.platforms, p],
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Record<string, unknown> = {
      name: form.name,
      product_name: form.product_name,
      product_description: form.product_description,
      target_market: form.target_market,
      budget_tier: form.budget_tier,
    }
    if (form.target_location) payload.target_location = form.target_location
    if (form.platforms.length) payload.platforms = form.platforms
    if (form.client_name) payload.client_name = form.client_name
    if (form.competitors) payload.competitors = form.competitors
    if (form.brand_colors) payload.brand_colors = form.brand_colors
    if (form.brand_style) payload.brand_style = form.brand_style
    createMutation.mutate(payload)
  }

  const canSubmit = form.name && form.product_name && form.product_description && form.target_market

  return (
    <div className="space-y-4">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft size={14} />
        Back to campaigns
      </button>

      <h3 className="text-lg font-semibold text-white">Create Campaign</h3>

      <form onSubmit={handleSubmit} className="space-y-4 max-w-2xl">
        {/* Required fields */}
        <Field label="Campaign Name *" value={form.name} onChange={(v) => setForm((f) => ({ ...f, name: v }))} placeholder="Q1 Product Launch" />
        <Field label="Product Name *" value={form.product_name} onChange={(v) => setForm((f) => ({ ...f, product_name: v }))} placeholder="Widget Pro" />
        <TextArea label="Product Description *" value={form.product_description} onChange={(v) => setForm((f) => ({ ...f, product_description: v }))} placeholder="Describe the product or service..." />
        <TextArea label="Target Market *" value={form.target_market} onChange={(v) => setForm((f) => ({ ...f, target_market: v }))} placeholder="Tech-savvy professionals, ages 25-45..." />

        {/* Optional fields */}
        <Field label="Target Location" value={form.target_location} onChange={(v) => setForm((f) => ({ ...f, target_location: v }))} placeholder="United States, Bay Area" />
        <Field label="Client Name" value={form.client_name} onChange={(v) => setForm((f) => ({ ...f, client_name: v }))} placeholder="Acme Corp" />
        <Field label="Competitors (comma-separated)" value={form.competitors} onChange={(v) => setForm((f) => ({ ...f, competitors: v }))} placeholder="Competitor A, Competitor B" />
        <Field label="Brand Colors" value={form.brand_colors} onChange={(v) => setForm((f) => ({ ...f, brand_colors: v }))} placeholder="#FF5733, #333333" />
        <Field label="Brand Style" value={form.brand_style} onChange={(v) => setForm((f) => ({ ...f, brand_style: v }))} placeholder="Modern, minimalist, professional" />

        {/* Budget Tier */}
        <div>
          <label className="block text-sm text-gray-300 mb-1">Budget Tier</label>
          <select
            value={form.budget_tier}
            onChange={(e) => setForm((f) => ({ ...f, budget_tier: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg bg-gray-800/50 border border-dark-border text-white text-sm focus:outline-none focus:border-primary-500/50"
          >
            {tiers.length > 0
              ? tiers.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.name} — {t.budget_range}
                  </option>
                ))
              : ['starter', 'growth', 'professional', 'enterprise'].map((t) => (
                  <option key={t} value={t}>
                    {t.charAt(0).toUpperCase() + t.slice(1)}
                  </option>
                ))}
          </select>
        </div>

        {/* Platforms */}
        <div>
          <label className="block text-sm text-gray-300 mb-2">Platforms</label>
          <div className="flex flex-wrap gap-2">
            {PLATFORM_OPTIONS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => togglePlatform(p)}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-xs capitalize transition-colors',
                  form.platforms.includes(p)
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800'
                )}
              >
                {p.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Error */}
        {createMutation.isError && (
          <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
            {(createMutation.error as Error)?.message ?? 'Failed to create campaign'}
          </div>
        )}

        {/* Submit */}
        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            disabled={!canSubmit || createMutation.isPending}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              canSubmit && !createMutation.isPending
                ? 'bg-primary-500 text-white hover:bg-primary-600'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            )}
          >
            {createMutation.isPending && <Loader2 size={14} className="animate-spin" />}
            Create Campaign
          </button>
          <button
            type="button"
            onClick={onBack}
            className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

// ============ Campaign Detail View ============

function CampaignDetailView({
  campaignId,
  onBack,
}: {
  campaignId: string
  onBack: () => void
}) {
  const queryClient = useQueryClient()

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['campaign', campaignId],
    queryFn: () => campaignApi.detail(campaignId),
    select: (res) => (res.data?.campaign ?? res.data) as CampaignDetail,
  })

  const startMutation = useMutation({
    mutationFn: () => campaignApi.start(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaign', campaignId] })
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => campaignApi.delete(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      onBack()
    },
  })

  const [confirmDelete, setConfirmDelete] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (error || !data) {
    return <ErrorState error={error as Error} message="Failed to load campaign" onRetry={() => refetch()} />
  }

  const campaign = data
  const currentPhaseIdx = PHASES.indexOf(campaign.status as typeof PHASES[number])

  return (
    <div className="space-y-6">
      {/* Back */}
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft size={14} />
        Back to campaigns
      </button>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-white">{campaign.name}</h3>
            <span className={cn('px-2 py-0.5 rounded text-xs capitalize', STATUS_COLORS[campaign.status] ?? STATUS_COLORS.intake)}>
              {campaign.status}
            </span>
          </div>
          <div className="flex items-center gap-4 mt-1 text-xs text-gray-400">
            {campaign.client_name && <span>{campaign.client_name}</span>}
            <span>{campaign.product_name}</span>
            <span className="flex items-center gap-1">
              <DollarSign size={10} />
              {campaign.budget_tier}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => refetch()}
            className="p-2 rounded-lg bg-gray-800/50 text-gray-400 hover:text-white transition-colors"
          >
            <RefreshCw size={14} />
          </button>
          {campaign.status === 'intake' && (
            <button
              onClick={() => startMutation.mutate()}
              disabled={startMutation.isPending}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors text-sm"
            >
              {startMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} />}
              Start Campaign
            </button>
          )}
          {!confirmDelete ? (
            <button
              onClick={() => setConfirmDelete(true)}
              className="p-2 rounded-lg bg-gray-800/50 text-gray-400 hover:text-red-400 transition-colors"
            >
              <Trash2 size={14} />
            </button>
          ) : (
            <div className="flex items-center gap-2">
              <button
                onClick={() => deleteMutation.mutate()}
                disabled={deleteMutation.isPending}
                className="flex items-center gap-1 px-3 py-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 text-sm"
              >
                {deleteMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                Confirm Delete
              </button>
              <button
                onClick={() => setConfirmDelete(false)}
                className="px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white"
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Phase Stepper */}
      <div className="flex items-center gap-1 p-3 rounded-lg bg-dark-card border border-dark-border">
        {PHASES.map((phase, idx) => {
          const isActive = phase === campaign.status
          const isDone = idx < currentPhaseIdx
          return (
            <div key={phase} className="flex items-center gap-1 flex-1">
              <div className={cn(
                'flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium',
                isDone ? 'bg-green-500/20 text-green-400' :
                isActive ? 'bg-primary-500/20 text-primary-400 ring-1 ring-primary-500/50' :
                'bg-gray-800 text-gray-500'
              )}>
                {isDone ? <CheckCircle size={12} /> : idx + 1}
              </div>
              <span className={cn(
                'text-xs capitalize hidden sm:inline',
                isActive ? 'text-primary-400' : isDone ? 'text-green-400' : 'text-gray-500'
              )}>
                {phase}
              </span>
              {idx < PHASES.length - 1 && (
                <div className={cn(
                  'flex-1 h-px mx-1',
                  isDone ? 'bg-green-500/30' : 'bg-gray-700'
                )} />
              )}
            </div>
          )
        })}
      </div>

      {/* Progress bar */}
      <div>
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{campaign.progress_percentage ?? 0}%</span>
        </div>
        <div className="h-2 rounded-full bg-gray-800 overflow-hidden">
          <div
            className="h-full rounded-full bg-primary-500 transition-all"
            style={{ width: `${campaign.progress_percentage ?? 0}%` }}
          />
        </div>
      </div>

      {/* Info grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {campaign.product_description && (
          <InfoCard icon={Target} label="Product" value={campaign.product_description} />
        )}
        {campaign.target_market && (
          <InfoCard icon={Target} label="Target Market" value={campaign.target_market} />
        )}
        {campaign.platforms && campaign.platforms.length > 0 && (
          <InfoCard icon={Share2} label="Platforms" value={campaign.platforms.map(p => p.replace('_', ' ')).join(', ')} />
        )}
        {campaign.competitors && (
          <InfoCard icon={Target} label="Competitors" value={campaign.competitors} />
        )}
      </div>

      {/* Deliverables */}
      {campaign.deliverables && campaign.deliverables.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Deliverables ({campaign.deliverables.length})</h4>
          <div className="grid gap-2">
            {campaign.deliverables.map((d) => {
              const Icon = DELIVERABLE_ICONS[d.deliverable_type] ?? FileText
              return (
                <div key={d.id} className="flex items-center gap-3 p-3 rounded-lg bg-gray-800/50 border border-dark-border">
                  <Icon size={14} className="text-gray-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <span className="text-sm text-white">{d.title}</span>
                    {d.content_preview && (
                      <p className="text-xs text-gray-500 truncate mt-0.5">{d.content_preview}</p>
                    )}
                  </div>
                  <span className={cn('px-2 py-0.5 rounded text-xs capitalize', STATUS_COLORS[d.status] ?? 'bg-gray-500/20 text-gray-400')}>
                    {d.status}
                  </span>
                  {d.platform && (
                    <span className="text-xs text-gray-500 capitalize">{d.platform.replace('_', ' ')}</span>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Research Items */}
      {campaign.research_items && campaign.research_items.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Research ({campaign.research_items.length})</h4>
          <div className="grid gap-2">
            {campaign.research_items.map((r) => (
              <div key={r.id} className="p-3 rounded-lg bg-gray-800/50 border border-dark-border">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-primary-400 capitalize">{r.research_type}</span>
                  <span className="text-sm text-white">{r.title}</span>
                </div>
                {r.summary && <p className="text-xs text-gray-400">{r.summary}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Execution Log */}
      {campaign.execution_log && campaign.execution_log.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Execution Log</h4>
          <div className="space-y-1 max-h-60 overflow-y-auto">
            {campaign.execution_log.slice(-20).map((entry, i) => (
              <div key={i} className="flex items-center gap-3 text-xs py-1">
                <Clock size={10} className="text-gray-500 shrink-0" />
                <span className="text-gray-500 w-16 shrink-0 capitalize">{entry.phase}</span>
                <span className="text-gray-300">{entry.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {startMutation.isError && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {(startMutation.error as Error)?.message ?? 'Failed to start campaign'}
        </div>
      )}
    </div>
  )
}

// ============ Shared UI Helpers ============

function InfoCard({ icon: Icon, label, value }: { icon: typeof Target; label: string; value: string }) {
  return (
    <div className="p-3 rounded-lg bg-gray-800/50 border border-dark-border">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={12} className="text-gray-400" />
        <span className="text-xs text-gray-400">{label}</span>
      </div>
      <p className="text-sm text-gray-200">{value}</p>
    </div>
  )
}

function Field({ label, value, onChange, placeholder }: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <div>
      <label className="block text-sm text-gray-300 mb-1">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full px-3 py-2 rounded-lg bg-gray-800/50 border border-dark-border text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
      />
    </div>
  )
}

function TextArea({ label, value, onChange, placeholder }: {
  label: string
  value: string
  onChange: (v: string) => void
  placeholder?: string
}) {
  return (
    <div>
      <label className="block text-sm text-gray-300 mb-1">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={3}
        className="w-full px-3 py-2 rounded-lg bg-gray-800/50 border border-dark-border text-white text-sm placeholder-gray-500 focus:outline-none focus:border-primary-500/50 resize-y"
      />
    </div>
  )
}
