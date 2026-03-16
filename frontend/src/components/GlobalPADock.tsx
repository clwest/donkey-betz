/**
 * Session 948: Global PA Dock
 * Session 974: Switched to paChat API with conversation_id, added history overlay
 * Session 1036: Added file upload — paperclip, drag-and-drop, clipboard paste, Media Library link
 *
 * A persistent, dockable chat panel that appears on every page.
 * - Slides in from the right side
 * - Can be minimized to a floating button
 * - Preserves chat history across page navigations
 * - Aware of current page context
 * - Shares state with CommandCenterPage via paStore
 * - Supports file attachments (images, videos, documents)
 */

import { useState, useRef, useEffect, useCallback } from 'react'
import { useLocation } from 'react-router-dom'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Bot, User, Send, X, Minus, Maximize2, MessageSquare,
  Loader2, Copy, ThumbsUp, ThumbsDown, Trash2, Clock, Plus, Terminal,
  Paperclip, Image as ImageIcon, FileText, Film, Music, File, FolderOpen,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { assistantApi, contentApi, workspaceApi } from '@/lib/api'
import { usePAStore } from '@/stores/paStore'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { ChatMarkdown } from './ChatMarkdown'
import PAConversationSidebar from './PAConversationSidebar'

// ── Attachment types ────────────────────────────────────────────────────────

interface Attachment {
  id: string
  file: File
  name: string
  size: number
  type: string // mime type
  status: 'pending' | 'uploading' | 'done' | 'error'
  progress: number
  url?: string       // CDN URL after upload
  mediaId?: string   // backend record ID
  error?: string
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function getFileIcon(mimeType: string) {
  if (mimeType.startsWith('image/')) return ImageIcon
  if (mimeType.startsWith('video/')) return Film
  if (mimeType.startsWith('audio/')) return Music
  if (mimeType.includes('pdf') || mimeType.includes('document') || mimeType.includes('text'))
    return FileText
  return File
}

export default function GlobalPADock() {
  const location = useLocation()
  const inputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)
  const [showWsPicker, setShowWsPicker] = useState(false)

  // PA Store
  const {
    isDockOpen,
    isDockMinimized,
    messages,
    currentInput,
    activeConversationId,
    isSidebarOpen,
    toggleDock,
    closeDock,
    minimizeDock,
    maximizeDock,
    addMessage,
    updateMessageFeedback,
    clearMessages,
    setCurrentInput,
    setCurrentPage,
    setActiveConversationId,
    toggleSidebar,
    startNewConversation,
    fetchConversations,
    setActiveConversation,
  } = usePAStore()

  const [localInput, setLocalInput] = useState(currentInput)
  const [isPolling, setIsPolling] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Attachment state
  const [attachments, setAttachments] = useState<Attachment[]>([])
  const [isDragging, setIsDragging] = useState(false)

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
    }
  }, [])

  // Update current page context
  useEffect(() => {
    setCurrentPage(location.pathname)
  }, [location.pathname, setCurrentPage])

  // Sync local input with store
  useEffect(() => {
    setCurrentInput(localInput)
  }, [localInput, setCurrentInput])

  // Auto-scroll to bottom
  useEffect(() => {
    if (isDockOpen && !isDockMinimized && !isSidebarOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isDockOpen, isDockMinimized, isSidebarOpen])

  // Focus input when dock opens
  useEffect(() => {
    if (isDockOpen && !isDockMinimized && !isSidebarOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isDockOpen, isDockMinimized, isSidebarOpen])

  // ── File upload logic ───────────────────────────────────────────────────

  const uploadFile = useCallback(async (attachment: Attachment) => {
    setAttachments(prev =>
      prev.map(a => a.id === attachment.id ? { ...a, status: 'uploading' as const, progress: 10 } : a)
    )

    try {
      const mime = attachment.type

      if (mime.startsWith('image/')) {
        // Use image upload endpoint
        const resp = await contentApi.uploadImage(attachment.file, attachment.name)
        setAttachments(prev =>
          prev.map(a => a.id === attachment.id ? {
            ...a,
            status: 'done' as const,
            progress: 100,
            url: resp.data.image?.url,
            mediaId: resp.data.image?.id,
          } : a)
        )
      } else if (mime.startsWith('video/')) {
        // Use video upload endpoint
        const resp = await contentApi.uploadVideo(attachment.file, attachment.name)
        setAttachments(prev =>
          prev.map(a => a.id === attachment.id ? {
            ...a,
            status: 'done' as const,
            progress: 100,
            url: resp.data.video?.url || resp.data.video?.file_path,
            mediaId: resp.data.video?.id,
          } : a)
        )
      } else {
        // For other files (audio, documents, etc.) — use image endpoint as generic
        // or RAG upload for documents. For now, use image endpoint which saves to Cloudinary.
        const formData = new FormData()
        formData.append('file', attachment.file)
        formData.append('title', attachment.name)
        // Try image upload — it will reject non-image types, so catch and note
        try {
          const resp = await contentApi.uploadImage(attachment.file, attachment.name)
          setAttachments(prev =>
            prev.map(a => a.id === attachment.id ? {
              ...a,
              status: 'done' as const,
              progress: 100,
              url: resp.data.image?.url,
              mediaId: resp.data.image?.id,
            } : a)
          )
        } catch {
          // Non-image file — mark as pending with note
          setAttachments(prev =>
            prev.map(a => a.id === attachment.id ? {
              ...a,
              status: 'error' as const,
              error: 'Use Media Library for this file type',
            } : a)
          )
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setAttachments(prev =>
        prev.map(a => a.id === attachment.id ? {
          ...a,
          status: 'error' as const,
          error: errorMessage,
        } : a)
      )
    }
  }, [])

  const addFiles = useCallback((files: FileList | File[]) => {
    const newAttachments: Attachment[] = Array.from(files).map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      file,
      name: file.name,
      size: file.size,
      type: file.type || 'application/octet-stream',
      status: 'pending' as const,
      progress: 0,
    }))

    setAttachments(prev => [...prev, ...newAttachments])

    // Start uploading each file
    newAttachments.forEach(a => uploadFile(a))
  }, [uploadFile])

  const removeAttachment = useCallback((id: string) => {
    setAttachments(prev => prev.filter(a => a.id !== id))
  }, [])

  // ── Drag and drop ─────────────────────────────────────────────────────

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    // Only set false if leaving the drop zone entirely
    if (dropZoneRef.current && !dropZoneRef.current.contains(e.relatedTarget as Node)) {
      setIsDragging(false)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    if (e.dataTransfer.files.length > 0) {
      addFiles(e.dataTransfer.files)
    }
  }, [addFiles])

  // ── Clipboard paste ───────────────────────────────────────────────────

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (!items) return

    const imageFiles: File[] = []
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) {
          // Pasted images get a timestamp name via Object.defineProperty
          const ext = item.type.split('/')[1] || 'png'
          Object.defineProperty(file, 'name', {
            writable: true,
            value: `pasted-image-${Date.now()}.${ext}`,
          })
          imageFiles.push(file)
        }
      }
    }

    if (imageFiles.length > 0) {
      e.preventDefault() // Don't paste the image data as text
      addFiles(imageFiles)
    }
  }, [addFiles])

  // Live sync: poll server for new messages from Claude Code or other clients
  useQuery({
    queryKey: ['pa-dock-sync', activeConversationId],
    queryFn: async () => {
      if (!activeConversationId) return null
      const response = await assistantApi.getConversation(activeConversationId)
      const data = response.data
      const currentCount = usePAStore.getState().messages.length
      if (data.success && data.messages.length > currentCount) {
        setActiveConversation(activeConversationId)
      }
      return data
    },
    enabled: !!activeConversationId && isDockOpen && !isPolling && !location.pathname.startsWith('/command-center'),
    refetchInterval: 5000,
    refetchIntervalInBackground: false,
  })

  // Session 974b: Chat mutation — dispatches Celery task, then polls for result
  const chatMutation = useMutation({
    mutationFn: ({ message, attachmentMeta }: { message: string; attachmentMeta?: { url: string; name: string; type: string; mediaId?: string }[] }) =>
      assistantApi.paChat(message, {
        context: {
          current_page: location.pathname,
          ...(useWorkspaceStore.getState().activeWorkspace ? {
            workspace_id: useWorkspaceStore.getState().activeWorkspace!.id,
            workspace_name: useWorkspaceStore.getState().activeWorkspace!.name,
          } : {}),
          ...(attachmentMeta && attachmentMeta.length > 0 ? { attachments: attachmentMeta } : {}),
        },
        conversation_id: activeConversationId || undefined,
        source: 'web-dock',
        workspace_id: useWorkspaceStore.getState().activeWorkspace?.id || undefined,
      }),
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      // Guard against overlapping async callbacks (same fix as CommandCenterPage)
      let resolved = false

      pollRef.current = setInterval(async () => {
        if (resolved) return
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (resolved) return
          if (status.data.status === 'completed') {
            resolved = true
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)

            const content = status.data.content || 'No response'
            const toolNames = (status.data.tool_runs || []).map((r) => r.tool)
            const sourceLabel = status.data.source
            addMessage({ role: 'assistant', content, tools_used: toolNames, source: sourceLabel })

            if (status.data.conversation_id && !activeConversationId) {
              setActiveConversationId(status.data.conversation_id)
            }
            fetchConversations()
          } else if (status.data.status === 'failed') {
            resolved = true
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({
              role: 'assistant',
              content: status.data.error || 'Sorry, there was an error. Please try again.',
            })
          }
        } catch {
          resolved = true
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          addMessage({
            role: 'assistant',
            content: 'Sorry, there was an error. Please try again.',
          })
        }
      }, 2000)
    },
    onError: () => {
      addMessage({
        role: 'assistant',
        content: 'Sorry, there was an error. Please try again.',
      })
    },
  })

  const isBusy = chatMutation.isPending || isPolling
  const hasUploading = attachments.some(a => a.status === 'uploading')
  const completedAttachments = attachments.filter(a => a.status === 'done')

  const sendMessage = useCallback(() => {
    const hasText = localInput.trim().length > 0
    const hasAttached = completedAttachments.length > 0
    if ((!hasText && !hasAttached) || isBusy || hasUploading) return

    // Build message text with attachment references
    let messageText = localInput.trim()
    if (completedAttachments.length > 0 && !messageText) {
      messageText = `Shared ${completedAttachments.length} file${completedAttachments.length > 1 ? 's' : ''}`
    }

    // Build attachment metadata for context
    const attachmentMeta = completedAttachments.map(a => ({
      url: a.url || '',
      name: a.name,
      type: a.type,
      mediaId: a.mediaId,
    }))

    // Show attachments in user message
    const displayParts = [messageText]
    if (completedAttachments.length > 0) {
      displayParts.push(
        completedAttachments.map(a => `[${a.name}](${a.url})`).join('\n')
      )
    }

    addMessage({
      role: 'user',
      content: displayParts.join('\n\n'),
    })
    chatMutation.mutate({ message: messageText, attachmentMeta: attachmentMeta.length > 0 ? attachmentMeta : undefined })
    setLocalInput('')
    setAttachments([])
  }, [localInput, isBusy, hasUploading, completedAttachments, chatMutation, addMessage])

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
  }

  // Minimized floating button
  if (!isDockOpen) {
    return (
      <button
        onClick={toggleDock}
        className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-primary-600 shadow-lg hover:bg-primary-500 transition-all hover:scale-105 flex items-center justify-center group"
        title="Open AI Assistant"
      >
        <MessageSquare size={24} className="text-white" />
        {messages.length > 0 && (
          <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-accent-amber text-[10px] font-medium flex items-center justify-center text-white">
            {messages.length > 9 ? '9+' : messages.length}
          </span>
        )}
      </button>
    )
  }

  // Minimized dock (just header bar)
  if (isDockMinimized) {
    return (
      <div className="fixed bottom-6 right-6 z-50 w-72 bg-dark-card border border-dark-border rounded-lg shadow-xl">
        <div className="flex items-center justify-between p-3">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center">
              <Bot size={16} className="text-primary-400" />
            </div>
            <span className="text-sm font-medium">AI Assistant</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={maximizeDock}
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
              title="Maximize"
            >
              <Maximize2 size={14} />
            </button>
            <button
              onClick={closeDock}
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
              title="Close"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Full dock
  return (
    <div
      ref={dropZoneRef}
      className={cn(
        'fixed bottom-6 right-6 z-50 w-96 h-[500px] bg-dark-card border rounded-xl shadow-2xl flex flex-col overflow-hidden transition-colors',
        isDragging ? 'border-primary-400 bg-primary-900/10' : 'border-dark-border'
      )}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-dark-card/90 border-2 border-dashed border-primary-400 rounded-xl">
          <div className="text-center">
            <Paperclip size={32} className="text-primary-400 mx-auto mb-2" />
            <p className="text-sm font-medium text-primary-400">Drop files here</p>
            <p className="text-xs text-gray-500 mt-1">Images, videos, documents</p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-dark-border flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-primary-600/20 flex items-center justify-center">
            <Bot size={16} className="text-primary-400" />
          </div>
          <div>
            <span className="text-sm font-medium">AI Assistant</span>
            <button
              onClick={() => setShowWsPicker(!showWsPicker)}
              className="block text-[10px] text-gray-500 hover:text-primary-400 transition-colors text-left"
              title="Click to change workspace"
            >
              {useWorkspaceStore.getState().activeWorkspace
                ? `📂 ${useWorkspaceStore.getState().activeWorkspace!.name} ▾`
                : `📂 No workspace ▾`}
            </button>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* Session 974: History toggle */}
          <button
            onClick={toggleSidebar}
            className={cn(
              'p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white',
              isSidebarOpen && 'bg-primary-600/20 text-primary-400'
            )}
            title="Conversation history"
          >
            <Clock size={14} />
          </button>
          {/* New chat */}
          <button
            onClick={() => startNewConversation()}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="New chat"
          >
            <Plus size={14} />
          </button>
          <button
            onClick={clearMessages}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-accent-red"
            title="Clear chat"
            disabled={messages.length === 0}
          >
            <Trash2 size={14} />
          </button>
          <button
            onClick={minimizeDock}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="Minimize"
          >
            <Minus size={14} />
          </button>
          <button
            onClick={closeDock}
            className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-white"
            title="Close"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Workspace Picker Dropdown */}
      {showWsPicker && <WorkspacePicker onSelect={(ws) => {
        useWorkspaceStore.getState().setActiveWorkspace(ws)
        // Also activate on the backend
        workspaceApi.activate(ws.id).catch(() => {})
        setShowWsPicker(false)
      }} onClose={() => setShowWsPicker(false)} />}

      {/* Messages or Sidebar Overlay */}
      <div className="flex-1 overflow-auto p-3 space-y-3 relative">
        {/* Session 974: Conversation history overlay */}
        {isSidebarOpen && (
          <PAConversationSidebar variant="overlay" />
        )}

        {!isSidebarOpen && (
          <>
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <Bot size={32} className="mb-2 opacity-50" />
                <p className="text-sm mb-1">How can I help?</p>
                <p className="text-xs text-gray-500">I'm available on any page</p>
                <p className="text-xs text-gray-600 mt-2">Drag & drop files or paste images</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-2',
                    message.source === 'claude-code' ? 'justify-start' : message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && message.source !== 'claude-code' && (
                    <div className="h-6 w-6 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                      <Bot size={12} className="text-primary-400" />
                    </div>
                  )}
                  {message.source === 'claude-code' && (
                    <div className="h-6 w-6 rounded-full bg-emerald-600/20 flex items-center justify-center flex-shrink-0">
                      <Terminal size={12} className="text-emerald-400" />
                    </div>
                  )}

                  <div className={cn('max-w-[80%] group', message.role === 'user' && message.source !== 'claude-code' && 'order-first')}>
                    <div
                      className={cn(
                        'rounded-lg px-3 py-2 text-sm',
                        message.source === 'claude-code'
                          ? 'bg-emerald-900/30 border border-emerald-500/20'
                          : message.role === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-dark-bg border border-dark-border'
                      )}
                    >
                      {message.role === 'assistant' ? (
                        <ChatMarkdown content={message.content} />
                      ) : (
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      )}
                      {message.tools_used && message.tools_used.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-dark-border/50">
                          {message.tools_used.map((tool) => (
                            <span
                              key={tool}
                              className="text-[10px] px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-400"
                            >
                              {tool}
                            </span>
                          ))}
                        </div>
                      )}
                      {message.source === 'claude-code' && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono mt-1 inline-block">
                          Claude Code
                        </span>
                      )}
                    </div>

                    {/* Message actions */}
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-1 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => copyMessage(message.content)}
                          className="p-1 rounded hover:bg-dark-border"
                        >
                          <Copy size={10} className="text-gray-400" />
                        </button>
                        <button
                          onClick={() => updateMessageFeedback(message.id, 'positive')}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'positive' && 'bg-accent-green/20'
                          )}
                        >
                          <ThumbsUp
                            size={10}
                            className={message.feedback === 'positive' ? 'text-accent-green' : 'text-gray-400'}
                          />
                        </button>
                        <button
                          onClick={() => updateMessageFeedback(message.id, 'negative')}
                          className={cn(
                            'p-1 rounded hover:bg-dark-border',
                            message.feedback === 'negative' && 'bg-accent-red/20'
                          )}
                        >
                          <ThumbsDown
                            size={10}
                            className={message.feedback === 'negative' ? 'text-accent-red' : 'text-gray-400'}
                          />
                        </button>
                      </div>
                    )}
                  </div>

                  {message.role === 'user' && (
                    <div className="h-6 w-6 rounded-full bg-primary-600 flex items-center justify-center flex-shrink-0">
                      <User size={12} className="text-white" />
                    </div>
                  )}
                </div>
              ))
            )}

            {isBusy && (
              <div className="flex gap-2 justify-start">
                <div className="h-6 w-6 rounded-full bg-primary-600/20 flex items-center justify-center flex-shrink-0">
                  <Bot size={12} className="text-primary-400" />
                </div>
                <div className="bg-dark-bg border border-dark-border rounded-lg px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Loader2 className="h-3 w-3 animate-spin text-primary-400" />
                    <span className="text-xs text-gray-400">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input area */}
      {!isSidebarOpen && (
        <div className="border-t border-dark-border flex-shrink-0">
          {/* Attachment chips */}
          {attachments.length > 0 && (
            <div className="px-3 pt-2 flex flex-wrap gap-1.5">
              {attachments.map(a => {
                const Icon = getFileIcon(a.type)
                return (
                  <div
                    key={a.id}
                    className={cn(
                      'flex items-center gap-1.5 pl-2 pr-1 py-1 rounded-md text-[11px] max-w-[180px]',
                      a.status === 'done' && 'bg-accent-green/10 border border-accent-green/20 text-accent-green',
                      a.status === 'uploading' && 'bg-primary-600/10 border border-primary-500/20 text-primary-400',
                      a.status === 'error' && 'bg-accent-red/10 border border-accent-red/20 text-accent-red',
                      a.status === 'pending' && 'bg-dark-bg border border-dark-border text-gray-400',
                    )}
                  >
                    {a.status === 'uploading' ? (
                      <Loader2 size={10} className="animate-spin flex-shrink-0" />
                    ) : (
                      <Icon size={10} className="flex-shrink-0" />
                    )}
                    <span className="truncate">{a.name}</span>
                    <span className="text-[9px] opacity-60 flex-shrink-0">{formatFileSize(a.size)}</span>
                    <button
                      onClick={() => removeAttachment(a.id)}
                      className="p-0.5 rounded hover:bg-white/10 flex-shrink-0"
                    >
                      <X size={8} />
                    </button>
                  </div>
                )
              })}
            </div>
          )}

          {/* Composer row */}
          <div className="p-3 flex items-center gap-2">
            {/* Paperclip — file picker */}
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isBusy}
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-primary-400 transition-colors disabled:opacity-40"
              title="Attach files"
            >
              <Paperclip size={16} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  addFiles(e.target.files)
                  e.target.value = '' // reset so same file can be re-selected
                }
              }}
            />

            {/* Media Library link */}
            <a
              href="/media"
              target="_blank"
              rel="noopener noreferrer"
              className="p-1.5 rounded hover:bg-dark-border text-gray-400 hover:text-primary-400 transition-colors"
              title="Open Media Library"
            >
              <FolderOpen size={16} />
            </a>

            {/* Text input */}
            <input
              ref={inputRef}
              type="text"
              value={localInput}
              onChange={(e) => setLocalInput(e.target.value)}
              onKeyDown={handleKeyPress}
              onPaste={handlePaste}
              placeholder={attachments.length > 0 ? 'Add a message...' : 'Ask anything...'}
              className="input flex-1 text-sm py-2"
              disabled={isBusy}
            />

            {/* Send button */}
            <button
              onClick={sendMessage}
              disabled={isBusy || hasUploading || (!localInput.trim() && completedAttachments.length === 0)}
              className="btn btn-sm btn-primary px-3"
            >
              {isBusy ? (
                <Loader2 size={14} className="animate-spin" />
              ) : (
                <Send size={14} />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}


// ── Workspace Picker (inline dropdown) ───────────────────────────────────

function WorkspacePicker({ onSelect, onClose }: {
  onSelect: (ws: { id: string; name: string; workspace_type?: string; git_remote_url?: string }) => void
  onClose: () => void
}) {
  const { data, isLoading } = useQuery({
    queryKey: ['workspaces-picker'],
    queryFn: () => workspaceApi.list().then(r => r.data),
  })

  const workspaces = (data?.results || data || []) as Array<Record<string, unknown>>
  const currentId = useWorkspaceStore.getState().activeWorkspace?.id

  return (
    <div className="border-b border-dark-border bg-dark-bg/95 max-h-[200px] overflow-y-auto">
      <div className="px-3 py-2 text-[10px] text-gray-500 uppercase tracking-wide flex items-center justify-between">
        <span>Switch Workspace</span>
        <button onClick={onClose} className="text-gray-500 hover:text-white">
          <X size={12} />
        </button>
      </div>
      {isLoading ? (
        <div className="px-3 py-4 text-center text-xs text-gray-500">Loading...</div>
      ) : (
        workspaces.map((ws) => (
          <button
            key={ws.id as string}
            onClick={() => onSelect({
              id: ws.id as string,
              name: ws.name as string,
              workspace_type: ws.workspace_type as string,
              git_remote_url: ws.git_remote_url as string,
            })}
            className={cn(
              'w-full text-left px-3 py-2 text-xs hover:bg-dark-border/50 flex items-center justify-between transition-colors',
              currentId === ws.id && 'bg-primary-600/10 text-primary-400'
            )}
          >
            <div className="flex items-center gap-2 min-w-0">
              <FolderOpen size={12} className="flex-shrink-0" />
              <span className="truncate">{ws.name as string}</span>
            </div>
            {currentId === ws.id && (
              <span className="text-[9px] text-primary-400 flex-shrink-0 ml-2">active</span>
            )}
          </button>
        ))
      )}
    </div>
  )
}
