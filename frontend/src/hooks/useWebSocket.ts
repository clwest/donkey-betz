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

// Session 702: Specialized hook for HEART service updates
export function useHeartUpdates(onUpdate?: (data: HeartBeatUpdate) => void) {
  return useWebSocket('/heart', {
    onMessage: (data) => {
      onUpdate?.(data as HeartBeatUpdate)
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

// Session 702: HEART service WebSocket update
export interface HeartBeatUpdate {
  type: 'heartbeat' | 'component_status' | 'health_alert'
  health_score: number
  overall_status: 'healthy' | 'degraded' | 'critical'
  is_alive: boolean
  timestamp: string
  components?: Record<string, {
    status: string
    is_healthy: boolean
    response_time_ms?: number
    details?: Record<string, unknown>
  }>
}

// ============================================================================
// Session 714: System Events - Real-time event broadcasting across all pages
// ============================================================================

export type SystemEventType =
  | 'connection_established'
  | 'agent_execution_complete'
  | 'agent_execution_failed'
  | 'gate_became_critical'
  | 'body_status_changed'
  | 'file_modified'
  | 'pilot_started'
  | 'pilot_completed'
  | 'dream_generated'
  | 'level_up'
  | 'hive_mind_started'
  | 'system_status'
  | 'pong'
  | 'error'

export interface SystemEvent {
  type: SystemEventType
  data?: Record<string, unknown>
  timestamp?: string
  message?: string
}

export interface AgentExecutionEvent extends SystemEvent {
  type: 'agent_execution_complete' | 'agent_execution_failed'
  data: {
    execution_id: string
    agent_name: string
    status: string
    execution_time_ms?: number
    artifact_id?: string
  }
}

export interface PilotEvent extends SystemEvent {
  type: 'pilot_started' | 'pilot_completed'
  data: {
    pilot_id: string
    name: string
    status?: string
    outcome?: string
    gate_id?: string
    hours_running?: number
  }
}

export interface DreamEvent extends SystemEvent {
  type: 'dream_generated'
  data: {
    dream_id: string
    agent_id: string
    agent_name: string
    title: string
    dream_type: string
    vividness_score: number
  }
}

export interface HiveMindEvent extends SystemEvent {
  type: 'hive_mind_started'
  data: {
    session_id: string
    question: string
    mode: string
    participant_count: number
    participants: string[]
  }
}

export interface SystemEventHandlers {
  onAgentExecutionComplete?: (event: AgentExecutionEvent) => void
  onAgentExecutionFailed?: (event: AgentExecutionEvent) => void
  onGateBecameCritical?: (event: SystemEvent) => void
  onBodyStatusChanged?: (event: SystemEvent) => void
  onFileModified?: (event: SystemEvent) => void
  onPilotStarted?: (event: PilotEvent) => void
  onPilotCompleted?: (event: PilotEvent) => void
  onDreamGenerated?: (event: DreamEvent) => void
  onLevelUp?: (event: SystemEvent) => void
  onHiveMindStarted?: (event: HiveMindEvent) => void
  onAnyEvent?: (event: SystemEvent) => void
}

/**
 * Session 714: Hook for subscribing to system-wide events.
 *
 * All connected clients receive real-time notifications about:
 * - Agent executions (complete/failed)
 * - Pilot lifecycle (started/completed)
 * - Dream generation
 * - Hive mind sessions
 * - Body status changes
 * - File modifications
 * - Gate criticality
 *
 * @param handlers - Object with callbacks for specific event types
 * @returns WebSocket status and control functions
 */
export function useSystemEvents(handlers: SystemEventHandlers = {}) {
  const handleMessage = useCallback((data: unknown) => {
    const event = data as SystemEvent

    // Always call onAnyEvent if provided
    handlers.onAnyEvent?.(event)

    // Route to specific handlers based on event type
    switch (event.type) {
      case 'agent_execution_complete':
        handlers.onAgentExecutionComplete?.(event as AgentExecutionEvent)
        break
      case 'agent_execution_failed':
        handlers.onAgentExecutionFailed?.(event as AgentExecutionEvent)
        break
      case 'gate_became_critical':
        handlers.onGateBecameCritical?.(event)
        break
      case 'body_status_changed':
        handlers.onBodyStatusChanged?.(event)
        break
      case 'file_modified':
        handlers.onFileModified?.(event)
        break
      case 'pilot_started':
        handlers.onPilotStarted?.(event as PilotEvent)
        break
      case 'pilot_completed':
        handlers.onPilotCompleted?.(event as PilotEvent)
        break
      case 'dream_generated':
        handlers.onDreamGenerated?.(event as DreamEvent)
        break
      case 'level_up':
        handlers.onLevelUp?.(event)
        break
      case 'hive_mind_started':
        handlers.onHiveMindStarted?.(event as HiveMindEvent)
        break
    }
  }, [handlers])

  return useWebSocket('/system-events', {
    onMessage: handleMessage,
  })
}
