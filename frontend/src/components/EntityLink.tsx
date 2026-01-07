/**
 * Session 713: EntityLink - Cross-Page Navigation Component
 *
 * Renders clickable links for entities that navigate to the appropriate page.
 * Stores navigation context so pages know where the user came from.
 */

import { Link, useNavigate } from 'react-router-dom'
import {
  Bot, FileCode, Lightbulb, Target, CheckSquare,
  CloudLightning, Brain, Heart, Workflow, ExternalLink
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useNavigationStore } from '@/stores/navigationStore'

export type EntityType =
  | 'agent'
  | 'opportunity'
  | 'file'
  | 'dream'
  | 'memory'
  | 'gate'
  | 'pilot'
  | 'prediction'
  | 'body_system'
  | 'workflow'

interface EntityLinkProps {
  type: EntityType
  id: string
  label: string
  className?: string
  showIcon?: boolean
  iconSize?: number
  showExternal?: boolean
  context?: Record<string, unknown>
  // Optional: Override default navigation
  href?: string
  tab?: string
}

// Entity type to route mapping
const ENTITY_ROUTES: Record<EntityType, string> = {
  agent: '/agents',
  opportunity: '/intelligence',
  file: '/workspace',
  dream: '/agents',
  memory: '/agents',
  gate: '/intelligence',
  pilot: '/intelligence',
  prediction: '/intelligence',
  body_system: '/body-health',
  workflow: '/intelligence',
}

// Entity type to default tab mapping
const ENTITY_TABS: Record<EntityType, string | undefined> = {
  agent: 'agents',
  opportunity: 'opportunities',
  file: 'files',
  dream: 'dreams',
  memory: 'learning',
  gate: 'gates',
  pilot: 'pilots',
  prediction: 'predictions',
  body_system: undefined,
  workflow: 'opportunities',
}

// Entity type to icon mapping
const ENTITY_ICONS: Record<EntityType, typeof Bot> = {
  agent: Bot,
  opportunity: Lightbulb,
  file: FileCode,
  dream: CloudLightning,
  memory: Brain,
  gate: CheckSquare,
  pilot: Target,
  prediction: Target,
  body_system: Heart,
  workflow: Workflow,
}

// Entity type to color mapping
const ENTITY_COLORS: Record<EntityType, string> = {
  agent: 'text-primary-400 hover:text-primary-300',
  opportunity: 'text-accent-amber hover:text-accent-amber/80',
  file: 'text-accent-cyan hover:text-accent-cyan/80',
  dream: 'text-purple-400 hover:text-purple-300',
  memory: 'text-pink-400 hover:text-pink-300',
  gate: 'text-accent-green hover:text-accent-green/80',
  pilot: 'text-blue-400 hover:text-blue-300',
  prediction: 'text-orange-400 hover:text-orange-300',
  body_system: 'text-red-400 hover:text-red-300',
  workflow: 'text-indigo-400 hover:text-indigo-300',
}

/**
 * EntityLink Component
 *
 * Renders a clickable link to navigate to an entity's page with context.
 *
 * Usage:
 * <EntityLink type="agent" id="agent-123" label="ResearchAgent" />
 * <EntityLink type="opportunity" id="opp-456" label="New Feature" showIcon />
 */
export default function EntityLink({
  type,
  id,
  label,
  className,
  showIcon = true,
  iconSize = 14,
  showExternal = false,
  context,
  href,
  tab,
}: EntityLinkProps) {
  const setNavigationContext = useNavigationStore((state) => state.setContext)
  const Icon = ENTITY_ICONS[type]
  const colorClass = ENTITY_COLORS[type]

  // Build the target URL
  const targetRoute = href || ENTITY_ROUTES[type]
  const targetTab = tab || ENTITY_TABS[type]

  // Build URL with query params
  const buildUrl = () => {
    const params = new URLSearchParams()
    if (id) params.set('id', id)
    if (targetTab) params.set('tab', targetTab)
    const queryString = params.toString()
    return queryString ? `${targetRoute}?${queryString}` : targetRoute
  }

  // Handle click to store context
  const handleClick = () => {
    setNavigationContext({
      fromPage: window.location.pathname,
      entityType: type,
      entityId: id,
      entityLabel: label,
      timestamp: new Date().toISOString(),
      ...context,
    })
  }

  return (
    <Link
      to={buildUrl()}
      onClick={handleClick}
      className={cn(
        'inline-flex items-center gap-1.5 transition-colors',
        colorClass,
        className
      )}
      title={`View ${type}: ${label}`}
    >
      {showIcon && <Icon size={iconSize} />}
      <span className="truncate">{label}</span>
      {showExternal && <ExternalLink size={12} className="opacity-60" />}
    </Link>
  )
}

/**
 * EntityBadge - Compact badge version of EntityLink
 */
export function EntityBadge({
  type,
  id,
  label,
  className,
  context,
}: Omit<EntityLinkProps, 'showIcon' | 'iconSize' | 'showExternal'>) {
  const setNavigationContext = useNavigationStore((state) => state.setContext)
  const Icon = ENTITY_ICONS[type]

  const targetRoute = ENTITY_ROUTES[type]
  const targetTab = ENTITY_TABS[type]

  const buildUrl = () => {
    const params = new URLSearchParams()
    if (id) params.set('id', id)
    if (targetTab) params.set('tab', targetTab)
    const queryString = params.toString()
    return queryString ? `${targetRoute}?${queryString}` : targetRoute
  }

  const handleClick = () => {
    setNavigationContext({
      fromPage: window.location.pathname,
      entityType: type,
      entityId: id,
      entityLabel: label,
      timestamp: new Date().toISOString(),
      ...context,
    })
  }

  // Badge background colors
  const badgeColors: Record<EntityType, string> = {
    agent: 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30',
    opportunity: 'bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30',
    file: 'bg-accent-cyan/20 text-accent-cyan hover:bg-accent-cyan/30',
    dream: 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30',
    memory: 'bg-pink-500/20 text-pink-400 hover:bg-pink-500/30',
    gate: 'bg-accent-green/20 text-accent-green hover:bg-accent-green/30',
    pilot: 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30',
    prediction: 'bg-orange-500/20 text-orange-400 hover:bg-orange-500/30',
    body_system: 'bg-red-500/20 text-red-400 hover:bg-red-500/30',
    workflow: 'bg-indigo-500/20 text-indigo-400 hover:bg-indigo-500/30',
  }

  return (
    <Link
      to={buildUrl()}
      onClick={handleClick}
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium transition-colors',
        badgeColors[type],
        className
      )}
      title={`View ${type}: ${label}`}
    >
      <Icon size={12} />
      <span className="truncate max-w-[120px]">{label}</span>
    </Link>
  )
}

/**
 * EntityCard - Card version for lists
 */
export function EntityCard({
  type,
  id,
  label,
  description,
  meta,
  className,
  context,
}: EntityLinkProps & { description?: string; meta?: string }) {
  const setNavigationContext = useNavigationStore((state) => state.setContext)
  const Icon = ENTITY_ICONS[type]

  const targetRoute = ENTITY_ROUTES[type]
  const targetTab = ENTITY_TABS[type]

  const buildUrl = () => {
    const params = new URLSearchParams()
    if (id) params.set('id', id)
    if (targetTab) params.set('tab', targetTab)
    const queryString = params.toString()
    return queryString ? `${targetRoute}?${queryString}` : targetRoute
  }

  const handleClick = () => {
    setNavigationContext({
      fromPage: window.location.pathname,
      entityType: type,
      entityId: id,
      entityLabel: label,
      timestamp: new Date().toISOString(),
      ...context,
    })
  }

  // Card border colors
  const cardColors: Record<EntityType, string> = {
    agent: 'border-primary-500/30 hover:border-primary-500/50',
    opportunity: 'border-accent-amber/30 hover:border-accent-amber/50',
    file: 'border-accent-cyan/30 hover:border-accent-cyan/50',
    dream: 'border-purple-500/30 hover:border-purple-500/50',
    memory: 'border-pink-500/30 hover:border-pink-500/50',
    gate: 'border-accent-green/30 hover:border-accent-green/50',
    pilot: 'border-blue-500/30 hover:border-blue-500/50',
    prediction: 'border-orange-500/30 hover:border-orange-500/50',
    body_system: 'border-red-500/30 hover:border-red-500/50',
    workflow: 'border-indigo-500/30 hover:border-indigo-500/50',
  }

  return (
    <Link
      to={buildUrl()}
      onClick={handleClick}
      className={cn(
        'block p-3 rounded-lg border bg-dark-card/50 transition-colors',
        cardColors[type],
        className
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn('p-2 rounded-lg', `bg-${type === 'agent' ? 'primary' : 'gray'}-500/20`)}>
          <Icon size={16} className={ENTITY_COLORS[type].split(' ')[0]} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{label}</p>
          {description && (
            <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">{description}</p>
          )}
          {meta && (
            <p className="text-xs text-gray-500 mt-1">{meta}</p>
          )}
        </div>
        <ExternalLink size={14} className="text-gray-500 flex-shrink-0" />
      </div>
    </Link>
  )
}

/**
 * useEntityNavigation - Hook for programmatic navigation with context
 */
export function useEntityNavigation() {
  const navigate = useNavigate()
  const setNavigationContext = useNavigationStore((state) => state.setContext)

  const navigateToEntity = (
    type: EntityType,
    id: string,
    label: string,
    context?: Record<string, unknown>
  ) => {
    // Store context
    setNavigationContext({
      fromPage: window.location.pathname,
      entityType: type,
      entityId: id,
      entityLabel: label,
      timestamp: new Date().toISOString(),
      ...context,
    })

    // Build URL
    const targetRoute = ENTITY_ROUTES[type]
    const targetTab = ENTITY_TABS[type]
    const params = new URLSearchParams()
    if (id) params.set('id', id)
    if (targetTab) params.set('tab', targetTab)
    const queryString = params.toString()
    const url = queryString ? `${targetRoute}?${queryString}` : targetRoute

    // Navigate
    navigate(url)
  }

  return { navigateToEntity }
}
