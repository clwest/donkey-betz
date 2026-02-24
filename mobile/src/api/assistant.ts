import http from './http';

// ── Types ────────────────────────────────────────────────────────────────────

export interface ToolRun {
  tool: string;
  ok: boolean;
  latency_ms: number;
  error_code?: string;
  error_message?: string;
}

export interface PAChatResponse {
  success: boolean;
  task_id: string;
  status: 'processing';
}

export interface PAChatStatus {
  success: boolean;
  status: 'processing' | 'completed' | 'failed';
  content?: string;
  trace_id?: string;
  tool_runs?: ToolRun[];
  audio_url?: string | null;
  intent?: string | null;
  routed_to?: string | null;
  latency_ms?: number;
  conversation_id?: string;
  error?: string;
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  message_count: number;
  last_message_at: string | null;
  preview: string;
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tools_used?: string[];
}

export interface ConversationDetail {
  success: boolean;
  conversation_id: string;
  title: string;
  messages: ConversationMessage[];
}

// ── Endpoints ────────────────────────────────────────────────────────────────

export async function paChat(
  message: string,
  options?: { conversation_id?: string; context?: Record<string, unknown> },
): Promise<PAChatResponse> {
  const { data } = await http.post<PAChatResponse>('/pa/chat/', {
    message,
    ...options,
  });
  return data;
}

export async function paChatStatus(taskId: string): Promise<PAChatStatus> {
  const { data } = await http.get<PAChatStatus>(`/pa/chat/status/${taskId}/`);
  return data;
}

export async function listConversations(): Promise<{
  conversations: ConversationSummary[];
  total: number;
}> {
  const { data } = await http.get<{
    success: boolean;
    conversations: ConversationSummary[];
    total: number;
  }>('/pa/conversations/');
  return data;
}

export async function getConversation(
  conversationId: string,
): Promise<ConversationDetail> {
  const { data } = await http.get<ConversationDetail>(
    `/pa/conversations/${conversationId}/`,
  );
  return data;
}

export async function createConversation(): Promise<string> {
  const { data } = await http.post<{ success: boolean; conversation_id: string }>(
    '/pa/conversations/new/',
  );
  return data.conversation_id;
}
