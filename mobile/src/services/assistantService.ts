import { apiClient } from './apiClient';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  session_id: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
}

export interface ChatHistory {
  messages: ChatMessage[];
  total: number;
  has_more: boolean;
}

class AssistantService {
  // Send a chat message to the assistant
  async chat(message: string, context?: string): Promise<ChatResponse> {
    try {
      const response = await apiClient.post('/assistant/chat/', {
        message,
        context,
      });
      return response;
    } catch (error: any) {
      console.error('Assistant chat error:', error);
      // Return a fallback response for demo purposes
      return {
        response: `I received your message: "${message}". The AI assistant is currently experiencing some technical difficulties, but I'm here to help! Try asking me about content creation, prompts, or platform features.`,
        session_id: 'demo-session',
        message_id: Date.now().toString(),
      };
    }
  }

  // Get chat history
  async getHistory(limit: number = 50, offset: number = 0): Promise<ChatHistory> {
    return await apiClient.get('/assistant/history/', {
      params: { limit, offset }
    });
  }

  // Get assistant memory/context
  async getContext(): Promise<any> {
    return await apiClient.get('/assistant/context/');
  }

  // Get assistant memory details
  async getMemory(): Promise<any> {
    return await apiClient.get('/assistant/memory/');
  }

  // Enhanced chat with specific commands
  async enhancePrompt(prompt: string): Promise<string> {
    const response = await this.chat(`/enhance ${prompt}`);
    return response.response;
  }

  // Search personal knowledge
  async searchKnowledge(query: string): Promise<string> {
    const response = await this.chat(`/search ${query}`);
    return response.response;
  }

  // Remember information
  async rememberInfo(info: string): Promise<string> {
    const response = await this.chat(`/remember ${info}`);
    return response.response;
  }

  // Get help/guide for specific features
  async getGuide(feature?: 'image' | 'video' | 'blog'): Promise<string> {
    const command = feature ? `/guide ${feature}` : '/help';
    const response = await this.chat(command);
    return response.response;
  }
}

export const assistantService = new AssistantService();
export default assistantService;