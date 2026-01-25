// Session 825: Reusable tab container with sub-navigation
// Provides consistent styling and layout for all workspace tabs

import React from 'react'
import { cn } from '@/lib/cn'
import { Loader2 } from 'lucide-react'

interface SubTab {
  id: string
  label: string
  icon?: React.ComponentType<{ size?: number; className?: string }>
}

interface TabContainerProps {
  title?: string
  description?: string
  subTabs?: SubTab[]
  activeSubTab?: string
  onSubTabChange?: (id: string) => void
  children: React.ReactNode
  isLoading?: boolean
  actions?: React.ReactNode
  className?: string
}

export function TabContainer({
  title,
  description,
  subTabs,
  activeSubTab,
  onSubTabChange,
  children,
  isLoading = false,
  actions,
  className,
}: TabContainerProps) {
  return (
    <div className={cn('space-y-4', className)}>
      {/* Header with title, description, and actions */}
      {(title || actions) && (
        <div className="flex items-start justify-between">
          <div>
            {title && <h2 className="text-xl font-semibold">{title}</h2>}
            {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
          </div>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
      )}

      {/* Sub-tab navigation */}
      {subTabs && subTabs.length > 0 && (
        <SubTabNav
          tabs={subTabs}
          activeTab={activeSubTab || subTabs[0].id}
          onTabChange={onSubTabChange}
        />
      )}

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 size={24} className="animate-spin text-primary-400" />
        </div>
      ) : (
        children
      )}
    </div>
  )
}

interface SubTabNavProps {
  tabs: SubTab[]
  activeTab: string
  onTabChange?: (id: string) => void
}

export function SubTabNav({ tabs, activeTab, onTabChange }: SubTabNavProps) {
  return (
    <div className="flex items-center gap-1 p-1 bg-dark-bg rounded-lg border border-dark-border">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id
        const Icon = tab.icon

        return (
          <button
            key={tab.id}
            onClick={() => onTabChange?.(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all',
              isActive
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
            )}
          >
            {Icon && <Icon size={14} />}
            {tab.label}
          </button>
        )
      })}
    </div>
  )
}

// Card component for consistent styling
interface CardProps {
  title?: string
  icon?: React.ComponentType<{ size?: number; className?: string }>
  iconColor?: string
  children: React.ReactNode
  actions?: React.ReactNode
  className?: string
  collapsible?: boolean
  defaultExpanded?: boolean
}

export function Card({
  title,
  icon: Icon,
  iconColor = 'text-primary-400',
  children,
  actions,
  className,
  collapsible = false,
  defaultExpanded = true,
}: CardProps) {
  const [expanded, setExpanded] = React.useState(defaultExpanded)

  return (
    <div className={cn('card', className)}>
      {(title || actions) && (
        <div
          className={cn(
            'flex items-center justify-between mb-4',
            collapsible && 'cursor-pointer'
          )}
          onClick={collapsible ? () => setExpanded(!expanded) : undefined}
        >
          <div className="flex items-center gap-2">
            {Icon && <Icon size={18} className={iconColor} />}
            {title && <h3 className="font-semibold">{title}</h3>}
          </div>
          <div className="flex items-center gap-2">
            {actions}
            {collapsible && (
              <span className="text-xs text-gray-400">
                {expanded ? '▼' : '▶'}
              </span>
            )}
          </div>
        </div>
      )}
      {(!collapsible || expanded) && children}
    </div>
  )
}

// Stat card for metrics display
interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<{ size?: number | string; className?: string }>
  color: string
  trend?: {
    value: number
    label: string
  }
  onClick?: () => void
}

export function StatCard({ title, value, icon: Icon, color, trend, onClick }: StatCardProps) {
  return (
    <div
      className={cn(
        'card',
        onClick && 'cursor-pointer hover:border-primary-500/50 transition-colors'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{title}</p>
          <p className="text-2xl font-bold mt-1">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {trend && (
            <p className={cn(
              'text-xs mt-1',
              trend.value >= 0 ? 'text-accent-green' : 'text-accent-red'
            )}>
              {trend.value >= 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
            </p>
          )}
        </div>
        <div
          className="h-12 w-12 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}20` }}
        >
          <Icon size={24} className={`text-[${color}]`} />
        </div>
      </div>
    </div>
  )
}

// Empty state component
interface EmptyStateProps {
  icon: React.ComponentType<{ size?: number | string; className?: string }>
  title: string
  description?: string
  action?: React.ReactNode
}

export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="h-16 w-16 rounded-full bg-dark-border flex items-center justify-center mb-4">
        <Icon size={32} className="text-gray-400" />
      </div>
      <h3 className="font-semibold text-lg">{title}</h3>
      {description && <p className="text-sm text-gray-400 mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
