import axios from 'axios';

// Create a dedicated API client for AI Content Studio on port 8000
const aiStudioClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to include fresh auth token
aiStudioClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken') || import.meta.env.VITE_AUTH_TOKEN || 'fc58364ffbca4e77b732d03711d44965cf40acb6';
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface AssistantSession {
  id: string;
  title: string;
  message_count: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssistantMemory {
  id: string;
  title: string;
  summary: string;
  content: string;
  importance: number;
  topics: string[];
  created_at: string;
  search_count: number;
}

export interface AssistantProfile {
  assistant_style: string;
  preferred_name: string;
  enable_memory: boolean;
  memory_retention_days: number;
  save_conversations: boolean;
}

export interface AssistantStats {
  total_messages: number;
  total_sessions: number;
  total_memories: number;
  active_sessions: number;
  member_since: string;
}

class AssistantService {
  private baseURL = '/assistant';

  async sendMessage(message: string, sessionId?: string) {
    console.log('AssistantService.sendMessage - sessionId:', sessionId, 'type:', typeof sessionId);
    
    // Build payload conditionally - only include session_id if it's a valid value
    const payload: any = {
      message,
      use_personal_assistant: true  // Force use of enhanced Personal Assistant
    };
    
    // Only add session_id if it's a truthy value and not the string "undefined"
    if (sessionId && sessionId !== 'undefined') {
      payload.session_id = sessionId;
    }
    
    console.log('Sending payload:', payload);
    
    const response = await aiStudioClient.post(`${this.baseURL}/chat/`, payload);
    
    console.log('Assistant response:', response.data);
    
    return response.data;
  }

  async getSessions() {
    const response = await aiStudioClient.get(`${this.baseURL}/sessions/`);
    return response.data;
  }

  async getConversation(sessionId: string) {
    const response = await aiStudioClient.get(`${this.baseURL}/sessions/${sessionId}/`);
    return response.data;
  }

  async createNewSession(title?: string) {
    const response = await aiStudioClient.post(`${this.baseURL}/sessions/new/`, {
      title
    });
    return response.data;
  }

  async deleteSession(sessionId: string) {
    const response = await aiStudioClient.delete(`${this.baseURL}/sessions/${sessionId}/delete/`);
    return response.data;
  }

  async getMemories(search?: string, limit: number = 20) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    params.append('limit', limit.toString());
    
    const response = await aiStudioClient.get(`${this.baseURL}/memories/?${params}`);
    return response.data;
  }

  async updateProfile(profile: Partial<AssistantProfile>) {
    const response = await aiStudioClient.post(`${this.baseURL}/profile/`, profile);
    return response.data;
  }

  async getStats(): Promise<AssistantStats> {
    const response = await aiStudioClient.get(`${this.baseURL}/stats/`);
    return response.data;
  }

  async getContext() {
    const response = await aiStudioClient.get(`${this.baseURL}/context/`);
    return response.data;
  }
}

export const assistantService = new AssistantService();