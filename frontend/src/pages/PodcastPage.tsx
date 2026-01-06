import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { podcastApi } from '@/lib/api'
import {
  Mic, Radio, Play, Users, MessageSquare,
  Loader2, CheckCircle, XCircle, Plus, Clock,
  Headphones, Wand2, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'shows' | 'episodes' | 'debates' | 'generate'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface PodcastShow {
  id: string
  name: string
  description: string
  episodes_count: number
  total_plays: number
  status: 'active' | 'paused' | 'archived'
  created_at: string
}

interface PodcastEpisode {
  id: string
  title: string
  description: string
  show_name: string
  duration: number
  plays: number
  status: 'draft' | 'published' | 'scheduled'
  published_at?: string
}

interface Debate {
  id: string
  topic: string
  status: 'pending' | 'in_progress' | 'completed'
  participants: string[]
  created_at: string
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: Radio },
  { id: 'shows' as TabType, label: 'Shows', icon: Headphones },
  { id: 'episodes' as TabType, label: 'Episodes', icon: Mic },
  { id: 'debates' as TabType, label: 'Debates', icon: Users },
  { id: 'generate' as TabType, label: 'Generate', icon: Wand2 },
]

function Toast({ result, onClose }: { result: ActionResult; onClose: () => void }) {
  return (
    <div className={cn(
      'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
      result.type === 'success' ? 'bg-accent-green/20 text-accent-green border border-accent-green/30' : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
    )}>
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">&times;</button>
    </div>
  )
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export default function PodcastPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [generateTopic, setGenerateTopic] = useState('')
  const queryClient = useQueryClient()

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['podcast-stats'],
    queryFn: () => podcastApi.stats(),
  })

  // Fetch shows
  const { data: showsData, isLoading: loadingShows } = useQuery({
    queryKey: ['podcast-shows'],
    queryFn: () => podcastApi.shows(),
    enabled: activeTab === 'shows' || activeTab === 'overview',
  })

  // Fetch episodes
  const { data: episodesData, isLoading: loadingEpisodes } = useQuery({
    queryKey: ['podcast-episodes'],
    queryFn: () => podcastApi.episodes(),
    enabled: activeTab === 'episodes' || activeTab === 'overview',
  })

  // Fetch debates
  const { data: debatesData, isLoading: loadingDebates } = useQuery({
    queryKey: ['podcast-debates'],
    queryFn: () => podcastApi.debates(),
    enabled: activeTab === 'debates',
  })

  // Generate script mutation
  const generateScriptMutation = useMutation({
    mutationFn: (topic: string) => podcastApi.generateScript(topic),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Script generated! Check your episodes.' })
      setGenerateTopic('')
      queryClient.invalidateQueries({ queryKey: ['podcast-episodes'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate script.' })
    },
  })

  // Create debate mutation
  const createDebateMutation = useMutation({
    mutationFn: (topic: string) => podcastApi.createDebate(topic),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Debate created! Agents are preparing arguments.' })
      queryClient.invalidateQueries({ queryKey: ['podcast-debates'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to create debate.' })
    },
  })

  const stats = statsData?.data || {}
  const shows: PodcastShow[] = showsData?.data?.shows || showsData?.data || []
  const episodes: PodcastEpisode[] = episodesData?.data?.episodes || episodesData?.data || []
  const debates: Debate[] = debatesData?.data?.debates || debatesData?.data || []

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    if (generateTopic.trim()) {
      generateScriptMutation.mutate(generateTopic)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-accent-purple/20 flex items-center justify-center">
            <Radio size={28} className="text-accent-purple" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Podcast Studio</h1>
            <p className="text-gray-400">AI-powered podcast creation and management</p>
          </div>
        </div>
        <button
          className="btn btn-primary flex items-center gap-2"
          onClick={() => setActiveTab('generate')}
        >
          <Wand2 size={16} />
          Generate Episode
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2 overflow-x-auto">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap',
              activeTab === id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-bg'
            )}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="card">
              <div className="flex items-center gap-3">
                <Headphones className="text-accent-purple" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Shows</p>
                  <p className="text-2xl font-bold">{stats.total_shows || shows.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Mic className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Episodes</p>
                  <p className="text-2xl font-bold">{stats.total_episodes || episodes.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Play className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Total Plays</p>
                  <p className="text-2xl font-bold">{(stats.total_plays || 0).toLocaleString()}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Users className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Debates</p>
                  <p className="text-2xl font-bold">{stats.total_debates || debates.length}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Episodes & Shows */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Recent Episodes */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Recent Episodes</h3>
              {loadingEpisodes ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : episodes.length > 0 ? (
                <div className="space-y-3">
                  {episodes.slice(0, 5).map((episode) => (
                    <div
                      key={episode.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <button className="h-8 w-8 rounded-full bg-accent-purple/20 flex items-center justify-center hover:bg-accent-purple/30">
                          <Play size={14} className="text-accent-purple" />
                        </button>
                        <div>
                          <p className="font-medium text-sm">{episode.title}</p>
                          <p className="text-xs text-gray-500">{episode.show_name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm">{formatDuration(episode.duration)}</p>
                        <p className="text-xs text-gray-500">{episode.plays} plays</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Mic className="mx-auto mb-2" size={32} />
                  <p>No episodes yet</p>
                </div>
              )}
            </div>

            {/* Shows */}
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Your Shows</h3>
              {loadingShows ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="animate-spin" size={24} />
                </div>
              ) : shows.length > 0 ? (
                <div className="space-y-3">
                  {shows.slice(0, 5).map((show) => (
                    <div
                      key={show.id}
                      className="flex items-center justify-between p-3 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                          <Headphones size={18} className="text-accent-purple" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{show.name}</p>
                          <p className="text-xs text-gray-500">{show.episodes_count} episodes</p>
                        </div>
                      </div>
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        show.status === 'active' ? 'bg-accent-green/20 text-accent-green' :
                        show.status === 'paused' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {show.status}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-400">
                  <Headphones className="mx-auto mb-2" size={32} />
                  <p>No shows yet</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Shows Tab */}
      {activeTab === 'shows' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Podcast Shows</h3>
            <button
              className="btn btn-primary text-sm flex items-center gap-2"
              onClick={() => setActionResult({ type: 'success', message: 'Create show coming soon!' })}
            >
              <Plus size={14} />
              New Show
            </button>
          </div>
          {loadingShows ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : shows.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {shows.map((show) => (
                <div
                  key={show.id}
                  className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="h-12 w-12 rounded-lg bg-accent-purple/20 flex items-center justify-center">
                      <Headphones size={24} className="text-accent-purple" />
                    </div>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      show.status === 'active' ? 'bg-accent-green/20 text-accent-green' :
                      show.status === 'paused' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      {show.status}
                    </span>
                  </div>
                  <h4 className="font-medium mb-1">{show.name}</h4>
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{show.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{show.episodes_count} episodes</span>
                    <span>{show.total_plays.toLocaleString()} plays</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Headphones className="mx-auto mb-2" size={48} />
              <p>No shows created</p>
              <p className="text-sm text-gray-500 mt-1">Create your first podcast show to get started</p>
            </div>
          )}
        </div>
      )}

      {/* Episodes Tab */}
      {activeTab === 'episodes' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">All Episodes</h3>
          {loadingEpisodes ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : episodes.length > 0 ? (
            <div className="space-y-3">
              {episodes.map((episode) => (
                <div
                  key={episode.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <button className="h-12 w-12 rounded-full bg-accent-purple/20 flex items-center justify-center hover:bg-accent-purple/30 transition-colors">
                      <Play size={20} className="text-accent-purple" />
                    </button>
                    <div>
                      <p className="font-medium">{episode.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{episode.show_name}</span>
                        <span className="text-xs text-gray-500 flex items-center gap-1">
                          <Clock size={10} /> {formatDuration(episode.duration)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">{episode.plays.toLocaleString()} plays</p>
                      <p className="text-xs text-gray-500">
                        {episode.published_at ? new Date(episode.published_at).toLocaleDateString() : 'Not published'}
                      </p>
                    </div>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      episode.status === 'published' ? 'bg-accent-green/20 text-accent-green' :
                      episode.status === 'scheduled' ? 'bg-accent-cyan/20 text-accent-cyan' : 'bg-accent-amber/20 text-accent-amber'
                    )}>
                      {episode.status}
                    </span>
                    <ChevronRight size={16} className="text-gray-500" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Mic className="mx-auto mb-2" size={48} />
              <p>No episodes yet</p>
              <p className="text-sm text-gray-500 mt-1">Generate your first episode to get started</p>
            </div>
          )}
        </div>
      )}

      {/* Debates Tab */}
      {activeTab === 'debates' && (
        <div className="space-y-6">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">AI Debates</h3>
              <button
                className="btn btn-primary text-sm flex items-center gap-2"
                onClick={() => {
                  const topic = prompt('Enter debate topic:')
                  if (topic) createDebateMutation.mutate(topic)
                }}
                disabled={createDebateMutation.isPending}
              >
                {createDebateMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
                New Debate
              </button>
            </div>
            {loadingDebates ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="animate-spin" size={32} />
              </div>
            ) : debates.length > 0 ? (
              <div className="space-y-3">
                {debates.map((debate) => (
                  <div
                    key={debate.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-dark-border hover:border-gray-600 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        'h-10 w-10 rounded-lg flex items-center justify-center',
                        debate.status === 'completed' ? 'bg-accent-green/20' :
                        debate.status === 'in_progress' ? 'bg-accent-amber/20' : 'bg-gray-500/20'
                      )}>
                        <MessageSquare size={20} className={
                          debate.status === 'completed' ? 'text-accent-green' :
                          debate.status === 'in_progress' ? 'text-accent-amber' : 'text-gray-400'
                        } />
                      </div>
                      <div>
                        <p className="font-medium">{debate.topic}</p>
                        <p className="text-xs text-gray-500">{debate.participants.join(' vs ')}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        debate.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                        debate.status === 'in_progress' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {debate.status}
                      </span>
                      <ChevronRight size={16} className="text-gray-500" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Users className="mx-auto mb-2" size={48} />
                <p>No debates yet</p>
                <p className="text-sm text-gray-500 mt-1">Create a debate topic to watch AI agents argue different perspectives</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Generate Podcast Content</h3>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Topic</label>
                <textarea
                  value={generateTopic}
                  onChange={(e) => setGenerateTopic(e.target.value)}
                  placeholder="Enter the topic for your podcast episode..."
                  className="w-full h-32 bg-dark-bg border border-dark-border rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
                />
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="btn btn-primary flex items-center gap-2"
                  disabled={generateScriptMutation.isPending || !generateTopic.trim()}
                >
                  {generateScriptMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Wand2 size={16} />}
                  Generate Script
                </button>
              </div>
            </form>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Generation Options</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div
                className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                onClick={() => setActionResult({ type: 'success', message: 'Solo episode mode selected' })}
              >
                <Mic size={24} className="text-accent-purple mb-3" />
                <h4 className="font-medium mb-1">Solo Episode</h4>
                <p className="text-sm text-gray-400">Single narrator exploring a topic in depth</p>
              </div>
              <div
                className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                onClick={() => setActionResult({ type: 'success', message: 'Interview mode selected' })}
              >
                <Users size={24} className="text-accent-green mb-3" />
                <h4 className="font-medium mb-1">Interview</h4>
                <p className="text-sm text-gray-400">Simulated interview with an AI expert</p>
              </div>
              <div
                className="p-4 rounded-lg border border-dark-border hover:border-primary-500 transition-colors cursor-pointer"
                onClick={() => setActionResult({ type: 'success', message: 'Debate mode selected' })}
              >
                <MessageSquare size={24} className="text-accent-amber mb-3" />
                <h4 className="font-medium mb-1">Debate</h4>
                <p className="text-sm text-gray-400">Two AI agents debating opposing viewpoints</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast notification */}
      {actionResult && (
        <Toast result={actionResult} onClose={() => setActionResult(null)} />
      )}
    </div>
  )
}
