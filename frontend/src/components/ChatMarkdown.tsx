/**
 * Session 943: Modern Chat Markdown Renderer
 * Session 1100+: Memoized to prevent re-render on every keystroke
 *
 * Renders markdown in chat messages with modern, readable styling
 * optimized for dark backgrounds. Supports:
 * - Headers with proper hierarchy
 * - Code blocks with syntax highlighting colors
 * - Lists (ordered and unordered)
 * - Bold, italic, links
 * - Tables (via GFM)
 * - Blockquotes
 * - Status icons/emojis
 */

import React from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import { cn } from '@/lib/cn'

interface ChatMarkdownProps {
  content: string
  className?: string
}

const remarkPlugins = [remarkGfm]
const rehypePlugins = [rehypeSanitize]

// Stable component overrides — defined once, never recreated
const markdownComponents: Components = {
  // Headers - clean, readable with subtle color accents
  h1: ({ children }) => (
    <h1 className="text-lg font-semibold text-white mt-4 mb-2 first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-semibold text-white mt-3 mb-2 first:mt-0">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-semibold text-gray-100 mt-3 mb-1.5 first:mt-0">
      {children}
    </h3>
  ),

  // Paragraphs - comfortable line height
  p: ({ children }) => (
    <p className="text-gray-200 leading-relaxed mb-2 last:mb-0">
      {children}
    </p>
  ),

  // Strong/Bold - white for emphasis
  strong: ({ children }) => (
    <strong className="font-semibold text-white">
      {children}
    </strong>
  ),

  // Italic
  em: ({ children }) => (
    <em className="text-gray-300 italic">
      {children}
    </em>
  ),

  // Links - accent color with hover effect
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary-400 hover:text-primary-300 underline underline-offset-2 transition-colors"
    >
      {children}
    </a>
  ),

  // Code inline - pill style with accent
  code: ({ className, children, ...props }) => {
    // Check if this is a code block (has language class)
    const isCodeBlock = className?.includes('language-')

    if (isCodeBlock) {
      return (
        <code className={cn('text-gray-200 font-mono text-sm', className)} {...props}>
          {children}
        </code>
      )
    }

    // Inline code
    return (
      <code className="px-1.5 py-0.5 rounded-md bg-gray-800/80 text-primary-300 font-mono text-sm">
        {children}
      </code>
    )
  },

  // Code blocks - modern dark with border
  pre: ({ children }) => (
    <pre className="my-3 p-3 rounded-lg bg-gray-900/80 border border-gray-700/50 overflow-x-auto">
      {children}
    </pre>
  ),

  // Unordered lists
  ul: ({ children }) => (
    <ul className="my-2 ml-1 space-y-1">
      {children}
    </ul>
  ),

  // Ordered lists
  ol: ({ children }) => (
    <ol className="my-2 ml-1 space-y-1 list-decimal list-inside">
      {children}
    </ol>
  ),

  // List items - modern bullet style
  li: ({ children }) => (
    <li className="text-gray-200 ml-4">
      {children}
    </li>
  ),

  // Blockquotes - accent border
  blockquote: ({ children }) => (
    <blockquote className="my-3 pl-4 border-l-2 border-primary-500/50 text-gray-300 italic">
      {children}
    </blockquote>
  ),

  // Tables - clean modern style
  table: ({ children }) => (
    <div className="my-3 overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="border-b border-gray-700">
      {children}
    </thead>
  ),
  th: ({ children }) => (
    <th className="text-left py-2 px-3 text-gray-300 font-medium">
      {children}
    </th>
  ),
  tbody: ({ children }) => (
    <tbody className="divide-y divide-gray-800">
      {children}
    </tbody>
  ),
  tr: ({ children }) => (
    <tr className="hover:bg-gray-800/30 transition-colors">
      {children}
    </tr>
  ),
  td: ({ children }) => (
    <td className="py-2 px-3 text-gray-200">
      {children}
    </td>
  ),

  // Horizontal rule
  hr: () => (
    <hr className="my-4 border-gray-700/50" />
  ),
}

export const ChatMarkdown = React.memo(function ChatMarkdown({ content, className }: ChatMarkdownProps) {
  return (
    <div className={cn('chat-markdown', className)}>
      <ReactMarkdown
        remarkPlugins={remarkPlugins}
        rehypePlugins={rehypePlugins}
        components={markdownComponents}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
})

export default ChatMarkdown
