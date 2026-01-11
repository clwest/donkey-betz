/**
 * Content Channels Page - Session 741
 *
 * Displays autonomous content channels created by the AutonomousContentStudioCoordinator.
 * Shows channels, episodes, scripts, and debate information.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { contentApi } from '@/lib/api'
import {
  Radio,
  FileText,
  Play,
  Loader2,
  ChevronRight,
  ChevronDown,
  Youtube,
  MessageSquare,
  Eye,
  ThumbsUp,
  Clock,
  Calendar,
  Sparkles,
  Users,
  X,
} from 'lucide-react'
import { cn } from '@/lib/cn'

interface Episode {
  id: string
  title: string
  topic: string
  description?: string
  script?: string
  script_preview?: string
  script_length?: number
  has_full_script?: boolean
  created_at: string
  publish_date?: string
  metrics: {
    views: number
    likes: number
    comments: number
    shares: number
    engagement: number
    retention_rate: number
    performance_score: number
  }
  platform_url?: string
}

interface Channel {
  id: string
  name: string
  topic_domain: string
  target_audience: string
  content_frequency: string
  status: string
  visual_style: string
  voice_name: string
  platform: string
  publish_automatically: boolean
  total_episodes: number
  total_views: number
  total_engagement: number
  avg_retention: number
  next_content_due?: string
  last_content_created?: string
  created_at: string
  episodes: Episode[]
  episode_count: number
}

interface Stats {
  total_channels: number
  active_channels: number
  total_episodes: number
}

// Note: Debate interface available for future debates tab integration

const platformIcons: Record<string, typeof Youtube> = {
  youtube: Youtube,
  discord: MessageSquare,
  default: Radio,
}

const statusColors: Record<string, string> = {
  active: 'bg-accent-green/20 text-accent-green',
  paused: 'bg-accent-amber/20 text-accent-amber',
  archived: 'bg-gray-500/20 text-gray-400',
}

// Episode Detail Modal
function EpisodeModal({
  episode,
  channelName,
  onClose,
}: {
  episode: Episode
  channelName: string
  onClose: () => void
}) {
  const { data: detailData, isLoading } = useQuery({
    queryKey: ['episode-detail', episode.id],
    queryFn: () => contentApi.episodeDetail(episode.id),
  })

  const fullEpisode = detailData?.data?.episode || episode
  const debate = detailData?.data?.debate

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-dark-card border border-dark-border rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div>
            <h3 className="font-semibold text-lg">{fullEpisode.title}</h3>
            <p className="text-sm text-gray-400">{channelName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-dark-bg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="animate-spin" size={32} />
            </div>
          ) : (
            <>
              {/* Topic & Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-dark-bg">
                  <p className="text-xs text-gray-500">Views</p>
                  <p className="text-xl font-bold">{fullEpisode.metrics?.views || 0}</p>
                </div>
                <div className="p-3 rounded-lg bg-dark-bg">
                  <p className="text-xs text-gray-500">Engagement</p>
                  <p className="text-xl font-bold">{fullEpisode.metrics?.engagement || 0}</p>
                </div>
                <div className="p-3 rounded-lg bg-dark-bg">
                  <p className="text-xs text-gray-500">Retention</p>
                  <p className="text-xl font-bold">{(fullEpisode.metrics?.retention_rate || 0).toFixed(0)}%</p>
                </div>
                <div className="p-3 rounded-lg bg-dark-bg">
                  <p className="text-xs text-gray-500">Performance</p>
                  <p className="text-xl font-bold">{(fullEpisode.metrics?.performance_score || 0).toFixed(1)}</p>
                </div>
              </div>

              {/* Description */}
              {fullEpisode.description && (
                <div>
                  <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
                  <p className="text-gray-300">{fullEpisode.description}</p>
                </div>
              )}

              {/* Debate Info */}
              {debate && (
                <div className="border border-primary-500/30 rounded-lg p-4 bg-primary-500/5">
                  <h4 className="text-sm font-medium text-primary-400 mb-3 flex items-center gap-2">
                    <Sparkles size={16} />
                    Agent Debate
                  </h4>
                  <div className="space-y-3 text-sm">
                    {debate.topic_miner_position && (
                      <div className="p-3 rounded bg-dark-bg">
                        <p className="text-xs text-accent-cyan mb-1 font-medium">TopicMiner</p>
                        <p className="text-gray-300">{debate.topic_miner_position}</p>
                      </div>
                    )}
                    {debate.contrarian_position && (
                      <div className="p-3 rounded bg-dark-bg">
                        <p className="text-xs text-accent-amber mb-1 font-medium">Contrarian</p>
                        <p className="text-gray-300">{debate.contrarian_position}</p>
                      </div>
                    )}
                    {debate.analyst_position && (
                      <div className="p-3 rounded bg-dark-bg">
                        <p className="text-xs text-accent-green mb-1 font-medium">Analyst</p>
                        <p className="text-gray-300">{debate.analyst_position}</p>
                      </div>
                    )}
                    {debate.final_decision && (
                      <div className="p-3 rounded bg-primary-500/10 border border-primary-500/20">
                        <p className="text-xs text-primary-400 mb-1 font-medium">Final Decision</p>
                        <p className="text-gray-200">{debate.final_decision}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Script */}
              <div>
                <h4 className="text-sm font-medium text-gray-400 mb-2 flex items-center gap-2">
                  <FileText size={16} />
                  Script
                  {fullEpisode.script && (
                    <span className="text-xs text-gray-500">
                      ({fullEpisode.script.length.toLocaleString()} chars)
                    </span>
                  )}
                </h4>
                <div className="bg-dark-bg rounded-lg p-4 max-h-[400px] overflow-auto">
                  <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono">
                    {fullEpisode.script || 'No script available'}
                  </pre>
                </div>
              </div>

              {/* Metadata */}
              <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-2 border-t border-dark-border">
                <span className="flex items-center gap-1">
                  <Calendar size={12} />
                  Created: {new Date(fullEpisode.created_at).toLocaleDateString()}
                </span>
                {fullEpisode.publish_date && (
                  <span className="flex items-center gap-1">
                    <Play size={12} />
                    Published: {new Date(fullEpisode.publish_date).toLocaleDateString()}
                  </span>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

// Channel Card Component
function ChannelCard({ channel }: { channel: Channel }) {
  const [expanded, setExpanded] = useState(false)
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null)

  const PlatformIcon = platformIcons[channel.platform?.toLowerCase()] || platformIcons.default

  return (
    <div className="card">
      {/* Channel Header */}
      <div
        className="flex items-start justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start gap-4">
          <div className="h-12 w-12 rounded-lg bg-primary-500/20 flex items-center justify-center">
            <PlatformIcon className="text-primary-400" size={24} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-lg">{channel.name}</h3>
              <span className={cn('text-xs px-2 py-0.5 rounded capitalize', statusColors[channel.status] || statusColors.archived)}>
                {channel.status}
              </span>
            </div>
            <p className="text-sm text-gray-400 mt-1">{channel.topic_domain}</p>
            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <FileText size={12} />
                {channel.episode_count} episodes
              </span>
              <span className="flex items-center gap-1">
                <Eye size={12} />
                {channel.total_views.toLocaleString()} views
              </span>
              <span className="flex items-center gap-1">
                <Clock size={12} />
                {channel.content_frequency}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500 capitalize">{channel.platform}</span>
          {expanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
        </div>
      </div>

      {/* Expanded Episodes */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-dark-border">
          {/* Channel Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
            <div className="p-3 rounded-lg bg-dark-bg text-center">
              <p className="text-xs text-gray-500">Total Views</p>
              <p className="text-lg font-bold">{channel.total_views.toLocaleString()}</p>
            </div>
            <div className="p-3 rounded-lg bg-dark-bg text-center">
              <p className="text-xs text-gray-500">Engagement</p>
              <p className="text-lg font-bold">{channel.total_engagement.toLocaleString()}</p>
            </div>
            <div className="p-3 rounded-lg bg-dark-bg text-center">
              <p className="text-xs text-gray-500">Avg Retention</p>
              <p className="text-lg font-bold">{channel.avg_retention.toFixed(0)}%</p>
            </div>
            <div className="p-3 rounded-lg bg-dark-bg text-center">
              <p className="text-xs text-gray-500">Audience</p>
              <p className="text-sm font-medium truncate">{channel.target_audience}</p>
            </div>
          </div>

          {/* Episodes List */}
          <h4 className="text-sm font-medium text-gray-400 mb-3">Recent Episodes</h4>
          {channel.episodes.length > 0 ? (
            <div className="space-y-2">
              {channel.episodes.map((episode) => (
                <div
                  key={episode.id}
                  onClick={() => setSelectedEpisode(episode)}
                  className="flex items-center justify-between p-3 rounded-lg bg-dark-bg hover:bg-dark-hover cursor-pointer transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{episode.title}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      <span>{episode.topic}</span>
                      <span>{new Date(episode.created_at).toLocaleDateString()}</span>
                      {episode.script_length && (
                        <span className="text-primary-400">{episode.script_length.toLocaleString()} chars</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <Eye size={12} />
                      {episode.metrics.views}
                    </span>
                    <span className="flex items-center gap-1">
                      <ThumbsUp size={12} />
                      {episode.metrics.engagement}
                    </span>
                    <ChevronRight size={16} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500 text-center py-4">No episodes yet</p>
          )}

          {/* Next Due */}
          {channel.next_content_due && (
            <div className="mt-4 p-3 rounded-lg bg-accent-amber/10 border border-accent-amber/20">
              <p className="text-sm text-accent-amber flex items-center gap-2">
                <Clock size={14} />
                Next content due: {new Date(channel.next_content_due).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Episode Modal */}
      {selectedEpisode && (
        <EpisodeModal
          episode={selectedEpisode}
          channelName={channel.name}
          onClose={() => setSelectedEpisode(null)}
        />
      )}
    </div>
  )
}

export default function ContentChannelsPage() {
  const { data: channelsData, isLoading, error } = useQuery({
    queryKey: ['content-channels'],
    queryFn: () => contentApi.channels(10),
  })

  const channels: Channel[] = channelsData?.data?.channels || []
  const stats: Stats = channelsData?.data?.stats || {
    total_channels: 0,
    active_channels: 0,
    total_episodes: 0,
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="animate-spin mx-auto mb-4" size={32} />
          <p className="text-gray-400">Loading content channels...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <Radio className="mx-auto mb-4 text-accent-red" size={48} />
        <h3 className="text-lg font-semibold mb-2">Failed to Load Channels</h3>
        <p className="text-gray-400">Please try again later.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-primary-500/20 flex items-center justify-center">
            <Radio size={24} className="text-primary-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Content Channels</h1>
            <p className="text-sm text-gray-400">Autonomous content creation by AI agents</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <Radio className="text-primary-400" size={24} />
            <div>
              <p className="text-sm text-gray-400">Total Channels</p>
              <p className="text-2xl font-bold">{stats.total_channels}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Sparkles className="text-accent-green" size={24} />
            <div>
              <p className="text-sm text-gray-400">Active</p>
              <p className="text-2xl font-bold">{stats.active_channels}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <FileText className="text-accent-cyan" size={24} />
            <div>
              <p className="text-sm text-gray-400">Total Episodes</p>
              <p className="text-2xl font-bold">{stats.total_episodes}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center gap-3">
            <Users className="text-accent-amber" size={24} />
            <div>
              <p className="text-sm text-gray-400">Agents</p>
              <p className="text-2xl font-bold">3</p>
              <p className="text-xs text-gray-500">TopicMiner, Contrarian, Analyst</p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="p-4 rounded-lg bg-primary-500/10 border border-primary-500/20">
        <div className="flex items-start gap-3">
          <Sparkles className="text-primary-400 mt-0.5" size={20} />
          <div>
            <h3 className="font-medium text-primary-400">Autonomous Content Studio</h3>
            <p className="text-sm text-gray-300 mt-1">
              These channels are powered by the <strong>AutonomousContentStudioCoordinator</strong>.
              Three AI agents - TopicMiner, Contrarian, and Analyst - debate topics before content is created,
              ensuring diverse perspectives and high-quality output.
            </p>
          </div>
        </div>
      </div>

      {/* Channels List */}
      {channels.length > 0 ? (
        <div className="space-y-4">
          {channels.map((channel) => (
            <ChannelCard key={channel.id} channel={channel} />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <Radio className="mx-auto mb-4 text-gray-500" size={48} />
          <h3 className="text-lg font-semibold mb-2">No Channels Yet</h3>
          <p className="text-gray-400">
            Content channels will appear here when the autonomous content studio creates them.
          </p>
        </div>
      )}
    </div>
  )
}
