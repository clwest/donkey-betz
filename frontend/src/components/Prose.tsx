/**
 * Session 943: Unified Prose Component for Long-Form Content
 *
 * Use this for blogs, documents, reports, and any long-form content.
 * Uses Tailwind Typography plugin with custom dark theme.
 *
 * For chat messages, use ChatMarkdown instead.
 */

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/cn'

interface ProseProps {
  children: string
  className?: string
  size?: 'sm' | 'base' | 'lg'
}

/**
 * Prose wrapper for markdown content with consistent dark theme styling.
 *
 * @example
 * <Prose>{markdownContent}</Prose>
 * <Prose size="sm">{shortContent}</Prose>
 */
export function Prose({ children, className, size = 'base' }: ProseProps) {
  const sizeClass = {
    sm: 'prose-sm',
    base: 'prose-base',
    lg: 'prose-lg',
  }[size]

  return (
    <div
      className={cn(
        'prose prose-invert prose-dark max-w-none',
        sizeClass,
        className
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {children}
      </ReactMarkdown>
    </div>
  )
}

/**
 * ProseHTML wrapper for pre-rendered HTML content.
 * Use when content is already HTML (not markdown).
 */
export function ProseHTML({
  children,
  className,
  size = 'base',
}: {
  children: string
  className?: string
  size?: 'sm' | 'base' | 'lg'
}) {
  const sizeClass = {
    sm: 'prose-sm',
    base: 'prose-base',
    lg: 'prose-lg',
  }[size]

  return (
    <div
      className={cn(
        'prose prose-invert prose-dark max-w-none',
        sizeClass,
        className
      )}
      dangerouslySetInnerHTML={{ __html: children }}
    />
  )
}

export default Prose
