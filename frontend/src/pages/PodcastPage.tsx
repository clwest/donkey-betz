import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { podcastApi } from '@/lib/api'
import {
  Mic, Radio, Play,
  Loader2, CheckCircle, XCircle, Plus, Clock,
  Wand2, ChevronRight, FileText
} from 'lucide-react'
import { cn } from '@/lib/cn'

type TabType = 'overview' | 'episodes' | 'generate'

interface ActionResult {
  type: 'success' | 'error'
  message: string
}

interface PodcastEpisode {
  id: string
  topic?: string
  title?: string
  style?: string
  status?: string
  script?: string
  audio_url?: string
  created_at?: string
}

const tabs = [
  { id: 'overview' as TabType, label: 'Overview', icon: Radio },
  { id: 'episodes' as TabType, label: 'Episodes', icon: Mic },
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

export default function PodcastPage() {
  const [activeTab, setActiveTab] = useState<TabType>('overview')
  const [actionResult, setActionResult] = useState<ActionResult | null>(null)
  const [generateTopic, setGenerateTopic] = useState('')
  const [generateStyle, setGenerateStyle] = useState('conversational')
  const queryClient = useQueryClient()

  // Fetch stats
  const { data: statsData } = useQuery({
    queryKey: ['podcast-stats'],
    queryFn: () => podcastApi.stats(),
  })

  // Fetch episodes list
  const { data: episodesData, isLoading: loadingEpisodes } = useQuery({
    queryKey: ['podcast-list'],
    queryFn: () => podcastApi.list(),
  })

  // Generate script mutation
  const generateScriptMutation = useMutation({
    mutationFn: ({ topic, style }: { topic: string; style?: string }) =>
      podcastApi.generateScript(topic, style),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Script generated! Check your episodes.' })
      setGenerateTopic('')
      queryClient.invalidateQueries({ queryKey: ['podcast-list'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to generate script.' })
    },
  })

  // Create episode mutation
  const createMutation = useMutation({
    mutationFn: (data: { topic: string; style?: string }) => podcastApi.create(data),
    onSuccess: () => {
      setActionResult({ type: 'success', message: 'Episode created!' })
      queryClient.invalidateQueries({ queryKey: ['podcast-list'] })
    },
    onError: () => {
      setActionResult({ type: 'error', message: 'Failed to create episode.' })
    },
  })

  const stats = statsData?.data || {}
  const episodes: PodcastEpisode[] = episodesData?.data?.episodes || episodesData?.data || []

  // Clear toast after 3 seconds
  if (actionResult) {
    setTimeout(() => setActionResult(null), 3000)
  }

  const handleGenerate = (e: React.FormEvent) => {
    e.preventDefault()
    if (generateTopic.trim()) {
      generateScriptMutation.mutate({ topic: generateTopic, style: generateStyle })
    }
  }

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    if (generateTopic.trim()) {
      createMutation.mutate({ topic: generateTopic, style: generateStyle })
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
                <Mic className="text-accent-purple" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Episodes</p>
                  <p className="text-2xl font-bold">{stats.total_episodes || episodes.length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <FileText className="text-accent-green" size={24} />
                <div>
                  <p className="text-sm text-gray-400">With Scripts</p>
                  <p className="text-2xl font-bold">{stats.with_scripts || episodes.filter(e => e.script).length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Play className="text-accent-cyan" size={24} />
                <div>
                  <p className="text-sm text-gray-400">With Audio</p>
                  <p className="text-2xl font-bold">{stats.with_audio || episodes.filter(e => e.audio_url).length}</p>
                </div>
              </div>
            </div>
            <div className="card">
              <div className="flex items-center gap-3">
                <Clock className="text-accent-amber" size={24} />
                <div>
                  <p className="text-sm text-gray-400">Processing</p>
                  <p className="text-2xl font-bold">{stats.processing || episodes.filter(e => e.status === 'processing').length}</p>
                </div>
              </div>
            </div>
          </div>

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
                        <p className="font-medium text-sm">{episode.topic || episode.title || 'Untitled'}</p>
                        <p className="text-xs text-gray-500">{episode.style || 'Standard'}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={cn(
                        'text-xs px-2 py-1 rounded',
                        episode.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                        episode.status === 'processing' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                      )}>
                        {episode.status || 'draft'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <Mic className="mx-auto mb-2" size={32} />
                <p>No episodes yet</p>
                <p className="text-sm text-gray-500 mt-1">Generate your first episode to get started</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Episodes Tab */}
      {activeTab === 'episodes' && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">All Episodes</h3>
            <button
              className="btn btn-primary text-sm flex items-center gap-2"
              onClick={() => setActiveTab('generate')}
            >
              <Plus size={14} />
              New Episode
            </button>
          </div>
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
                      <p className="font-medium">{episode.topic || episode.title || 'Untitled'}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs px-2 py-0.5 rounded bg-dark-bg text-gray-400">{episode.style || 'Standard'}</span>
                        <span className="text-xs text-gray-500">
                          {episode.created_at ? new Date(episode.created_at).toLocaleDateString() : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      {episode.script && (
                        <span className="text-xs px-2 py-1 rounded bg-accent-cyan/20 text-accent-cyan">Script</span>
                      )}
                      {episode.audio_url && (
                        <span className="text-xs px-2 py-1 rounded bg-accent-green/20 text-accent-green">Audio</span>
                      )}
                    </div>
                    <span className={cn(
                      'text-xs px-2 py-1 rounded',
                      episode.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                      episode.status === 'processing' ? 'bg-accent-amber/20 text-accent-amber' : 'bg-gray-500/20 text-gray-400'
                    )}>
                      {episode.status || 'draft'}
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
              <div>
                <label className="block text-sm text-gray-400 mb-2">Style</label>
                <select
                  value={generateStyle}
                  onChange={(e) => setGenerateStyle(e.target.value)}
                  className="w-full bg-dark-bg border border-dark-border rounded-lg p-3 text-white focus:outline-none focus:border-primary-500"
                >
                  <option value="conversational">Conversational</option>
                  <option value="educational">Educational</option>
                  <option value="storytelling">Storytelling</option>
                  <option value="interview">Interview Style</option>
                  <option value="debate">Debate Format</option>
                </select>
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={handleCreate}
                  className="btn btn-secondary flex items-center gap-2"
                  disabled={createMutation.isPending || !generateTopic.trim()}
                >
                  {createMutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
                  Create Episode
                </button>
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
            <h3 className="text-lg font-semibold mb-4">Style Guide</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Conversational</h4>
                <p className="text-sm text-gray-400">Natural, casual tone as if talking to a friend</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Educational</h4>
                <p className="text-sm text-gray-400">Structured learning with clear explanations</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Storytelling</h4>
                <p className="text-sm text-gray-400">Narrative-driven with engaging story arcs</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Interview</h4>
                <p className="text-sm text-gray-400">Q&A format with expert perspectives</p>
              </div>
              <div className="p-4 rounded-lg bg-dark-bg">
                <h4 className="font-medium mb-2">Debate</h4>
                <p className="text-sm text-gray-400">Multiple viewpoints discussing a topic</p>
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
