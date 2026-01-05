import { useEffect, useRef, useCallback, useState } from 'react'
import { useAuthStore } from '@/stores/authStore'

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

interface UseWebSocketOptions {
  onMessage?: (data: unknown) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
  reconnectAttempts?: number
  reconnectInterval?: number
  autoConnect?: boolean
}

interface UseWebSocketReturn {
  status: WebSocketStatus
  send: (data: unknown) => void
  connect: () => void
  disconnect: () => void
  lastMessage: unknown
}

export function useWebSocket(
  endpoint: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
    autoConnect = true,
  } = options

  const { token } = useAuthStore()
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>()
  const mountedRef = useRef(true)

  // Store callbacks in refs to avoid dependency issues
  const callbacksRef = useRef({ onMessage, onConnect, onDisconnect, onError })
  callbacksRef.current = { onMessage, onConnect, onDisconnect, onError }

  const [status, setStatus] = useState<WebSocketStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<unknown>(null)

  const getWebSocketUrl = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    // For WebSocket, connect directly to Django backend in dev mode
    const isDev = import.meta.env.DEV
    const host = import.meta.env.VITE_WS_URL || (isDev ? 'localhost:8000' : window.location.host)
    const tokenParam = token ? `?token=${token}` : ''
    return `${protocol}//${host}/ws${endpoint}/${tokenParam}`
  }, [endpoint, token])

  const connect = useCallback(() => {
    // Don't connect if not mounted or already connected/connecting
    if (!mountedRef.current) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    const url = getWebSocketUrl()

    if (import.meta.env.DEV) {
      console.log('[WebSocket] Connecting to:', url)
    }

    setStatus('connecting')

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close()
          return
        }
        console.log('[WebSocket] Connected:', endpoint)
        setStatus('connected')
        reconnectCountRef.current = 0
        callbacksRef.current.onConnect?.()
      }

      ws.onmessage = (event) => {
        if (!mountedRef.current) return
        try {
          const data = JSON.parse(event.data)
          setLastMessage(data)
          callbacksRef.current.onMessage?.(data)
        } catch {
          setLastMessage(event.data)
          callbacksRef.current.onMessage?.(event.data)
        }
      }

      ws.onclose = (event) => {
        if (!mountedRef.current) return
        console.log('[WebSocket] Disconnected:', endpoint, 'code:', event.code)
        setStatus('disconnected')
        callbacksRef.current.onDisconnect?.()

        // Only reconnect if still mounted and under limit
        if (mountedRef.current && reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1
          console.log(`[WebSocket] Reconnecting (${reconnectCountRef.current}/${reconnectAttempts})...`)
          reconnectTimeoutRef.current = setTimeout(() => {
            if (mountedRef.current) {
              connect()
            }
          }, reconnectInterval)
        }
      }

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', endpoint, error)
        setStatus('error')
        callbacksRef.current.onError?.(error)
      }
    } catch (error) {
      console.error('[WebSocket] Failed to create connection:', error)
      setStatus('error')
    }
  }, [getWebSocketUrl, endpoint, reconnectAttempts, reconnectInterval])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = undefined
    }
    reconnectCountRef.current = reconnectAttempts // Prevent reconnection
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setStatus('disconnected')
  }, [reconnectAttempts])

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Cannot send - not connected')
    }
  }, [])

  // Connect/disconnect effect - only depends on token and autoConnect
  useEffect(() => {
    mountedRef.current = true

    if (autoConnect && token) {
      // Small delay to avoid rapid reconnects during render
      const timer = setTimeout(() => {
        if (mountedRef.current) {
          connect()
        }
      }, 100)
      return () => {
        clearTimeout(timer)
        mountedRef.current = false
        disconnect()
      }
    }

    return () => {
      mountedRef.current = false
      disconnect()
    }
  }, [token, autoConnect]) // Intentionally exclude connect/disconnect to avoid loops

  return {
    status,
    send,
    connect,
    disconnect,
    lastMessage,
  }
}

// Specialized hook for agent updates
export function useAgentUpdates(onUpdate?: (data: AgentUpdate) => void) {
  return useWebSocket('/agent-updates', {
    onMessage: (data) => {
      onUpdate?.(data as AgentUpdate)
    },
  })
}

// Specialized hook for learning feed
export function useLearningFeed(onUpdate?: (data: LearningEvent) => void) {
  return useWebSocket('/learning-feed', {
    onMessage: (data) => {
      onUpdate?.(data as LearningEvent)
    },
  })
}

// Specialized hook for agent conversations
export function useAgentConversations(onMessage?: (data: ConversationMessage) => void) {
  return useWebSocket('/agent-conversations', {
    onMessage: (data) => {
      onMessage?.(data as ConversationMessage)
    },
  })
}

// Types for WebSocket messages
export interface AgentUpdate {
  type: 'agent_status' | 'agent_execution' | 'agent_completed' | 'agent_error'
  agent_name: string
  status: string
  message?: string
  timestamp: string
  data?: Record<string, unknown>
}

export interface LearningEvent {
  type: 'learning_event' | 'knowledge_shared' | 'preference_learned'
  agent_name: string
  event_type: string
  description: string
  timestamp: string
  data?: Record<string, unknown>
}

export interface ConversationMessage {
  type: 'conversation' | 'message' | 'agent_response'
  from_agent: string
  to_agent?: string
  message: string
  timestamp: string
  conversation_id?: string
}
