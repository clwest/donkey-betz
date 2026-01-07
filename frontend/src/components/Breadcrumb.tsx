/**
 * Session 713: Breadcrumb Component - Navigation Context Display
 *
 * Shows "Back to X" when user navigated from another page with context.
 * Provides contextual navigation breadcrumbs.
 */

import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, ChevronRight, Home, Clock } from 'lucide-react'
import { cn } from '@/lib/cn'
import {
  useNavigationContext,
  useRecentEntities,
  getPageLabel,
  buildBreadcrumb,
} from '@/stores/navigationStore'

interface BreadcrumbProps {
  currentPage: string
  className?: string
  showRecent?: boolean
}

/**
 * Breadcrumb - Shows navigation context and back link
 */
export default function Breadcrumb({
  currentPage,
  className,
  showRecent = false,
}: BreadcrumbProps) {
  const context = useNavigationContext()
  const navigate = useNavigate()
  const breadcrumb = buildBreadcrumb(context)

  // If no context, show just current page
  if (!breadcrumb) {
    return (
      <div className={cn('flex items-center gap-2 text-sm', className)}>
        <Link to="/" className="text-gray-400 hover:text-white transition-colors">
          <Home size={14} />
        </Link>
        <ChevronRight size={14} className="text-gray-600" />
        <span className="text-white font-medium">{currentPage}</span>
      </div>
    )
  }

  const handleBack = () => {
    // Navigate back to previous page
    navigate(breadcrumb.path)
  }

  return (
    <div className={cn('flex items-center gap-3', className)}>
      {/* Back button */}
      <button
        onClick={handleBack}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-dark-border/50 hover:bg-dark-border transition-colors text-sm"
      >
        <ArrowLeft size={14} />
        <span>Back to {breadcrumb.label}</span>
      </button>

      {/* Breadcrumb trail */}
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Link to="/" className="hover:text-white transition-colors">
          <Home size={14} />
        </Link>
        <ChevronRight size={14} className="text-gray-600" />
        <Link to={breadcrumb.path} className="hover:text-white transition-colors">
          {breadcrumb.label}
        </Link>
        <ChevronRight size={14} className="text-gray-600" />
        <span className="text-white font-medium">{currentPage}</span>
      </div>

      {/* Entity context */}
      {context?.entityLabel && (
        <span className="text-xs px-2 py-1 rounded bg-primary-500/20 text-primary-400">
          {context.entityType}: {context.entityLabel}
        </span>
      )}

      {/* Recent entities dropdown */}
      {showRecent && <RecentEntitiesDropdown />}
    </div>
  )
}

/**
 * CompactBreadcrumb - Minimal version for tight spaces
 */
export function CompactBreadcrumb({ currentPage: _currentPage, className }: BreadcrumbProps) {
  const context = useNavigationContext()
  const navigate = useNavigate()
  const breadcrumb = buildBreadcrumb(context)

  if (!breadcrumb) return null

  return (
    <button
      onClick={() => navigate(breadcrumb.path)}
      className={cn(
        'flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors',
        className
      )}
    >
      <ArrowLeft size={14} />
      <span>Back</span>
    </button>
  )
}

/**
 * RecentEntitiesDropdown - Quick access to recently viewed entities
 */
function RecentEntitiesDropdown() {
  const recentEntities = useRecentEntities()

  if (recentEntities.length === 0) return null

  return (
    <div className="relative group">
      <button className="flex items-center gap-1.5 px-2 py-1 rounded text-xs text-gray-400 hover:text-white hover:bg-dark-border/50 transition-colors">
        <Clock size={12} />
        <span>Recent</span>
      </button>

      {/* Dropdown */}
      <div className="absolute top-full left-0 mt-1 w-64 py-2 bg-dark-card border border-dark-border rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
        <div className="px-3 py-1 text-xs text-gray-500 border-b border-dark-border mb-1">
          Recently Viewed
        </div>
        {recentEntities.slice(0, 5).map((entity, idx) => (
          <Link
            key={`${entity.type}-${entity.id}-${idx}`}
            to={entity.page}
            className="flex items-center gap-2 px-3 py-2 hover:bg-dark-border/50 transition-colors"
          >
            <span className="text-xs px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400 uppercase">
              {entity.type.slice(0, 3)}
            </span>
            <span className="text-sm truncate flex-1">{entity.label}</span>
            <span className="text-xs text-gray-500">{getPageLabel(entity.page)}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}

/**
 * PageHeader - Standard page header with breadcrumb
 */
export function PageHeader({
  title,
  subtitle,
  breadcrumb = true,
  actions,
  className,
}: {
  title: string
  subtitle?: string
  breadcrumb?: boolean
  actions?: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn('space-y-2', className)}>
      {breadcrumb && <Breadcrumb currentPage={title} />}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{title}</h1>
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
    </div>
  )
}

/**
 * NavigationContextBanner - Full-width banner showing navigation context
 */
export function NavigationContextBanner({ className }: { className?: string }) {
  const context = useNavigationContext()
  const navigate = useNavigate()

  if (!context) return null

  const breadcrumb = buildBreadcrumb(context)
  if (!breadcrumb) return null

  return (
    <div
      className={cn(
        'flex items-center justify-between px-4 py-2 bg-primary-500/10 border-b border-primary-500/20',
        className
      )}
    >
      <div className="flex items-center gap-3 text-sm">
        <span className="text-gray-400">Navigated from</span>
        <span className="font-medium text-primary-400">{breadcrumb.label}</span>
        {context.entityLabel && (
          <>
            <ChevronRight size={14} className="text-gray-600" />
            <span className="text-gray-300">
              {context.entityType}: <span className="text-white">{context.entityLabel}</span>
            </span>
          </>
        )}
      </div>
      <button
        onClick={() => navigate(breadcrumb.path)}
        className="flex items-center gap-1.5 px-3 py-1 rounded bg-primary-500/20 hover:bg-primary-500/30 text-primary-400 text-sm transition-colors"
      >
        <ArrowLeft size={14} />
        Go Back
      </button>
    </div>
  )
}
