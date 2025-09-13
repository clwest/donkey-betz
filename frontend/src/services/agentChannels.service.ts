/**
 * Agent Channels Service - API client for "Slack for AI Agents"
 * 
 * Provides REST API integration for agent channels, messages, and memberships.
 * Works in conjunction with WebSocket for real-time updates.
 */

import { apiRequest } from '../config/api.config';

// Types
export interface AgentChannel {
  id: string;
  name: string;
  display_name: string;
  description: string;
  channel_type: 'project' | 'topic' | 'team' | 'general' | 'system' | 'orchestration';
  is_active: boolean;
  is_archived: boolean;
  is_public: boolean;
  message_count: number;
  member_count: number;
  created_by: string;
  created_by_username: string;
  created_at: string;
  updated_at: string;
  metadata?: any;
  orchestration?: string;
  active_agents?: number;
  recent_messages?: ChannelMessage[];
}

export interface ChannelMessage {
  id: string;
  channel: string;
  channel_name?: string;
  message_type: 'agent_message' | 'system_message' | 'user_message' | 'status_update' | 
                'task_update' | 'tool_usage' | 'collaboration_request' | 'result_share' | 'error_report';
  agent_template?: string;
  agent_name?: string;
  user?: string;
  user_username?: string;
  content: string;
  rich_content?: any;
  timestamp: string;
  thread_id?: string;
  parent_message?: string;
  reactions?: Record<string, string[]>;
  reactions_count?: number;
  edited_at?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChannelMembership {
  id: string;
  channel: string;
  channel_name: string;
  agent_template?: string;
  agent_name?: string;
  user?: string;
  user_username?: string;
  role: 'member' | 'moderator' | 'admin' | 'observer';
  notification_level: 'all' | 'mentions' | 'none';
  is_watching: boolean;
  is_active: boolean;
  joined_at: string;
  last_read_at?: string;
  metadata?: any;
  member_display_name: string;
  created_at: string;
  updated_at: string;
}

export interface CreateChannelRequest {
  name: string;
  display_name: string;
  description?: string;
  channel_type?: 'project' | 'topic' | 'team' | 'general' | 'system' | 'orchestration';
  metadata?: any;
}

export interface PostMessageRequest {
  message_type?: 'agent_message' | 'system_message' | 'user_message' | 'status_update' | 
                  'task_update' | 'tool_usage' | 'collaboration_request' | 'result_share' | 'error_report';
  content: string;
  rich_content?: any;
  thread_id?: string;
  parent_message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// Channel operations
export const channelService = {
  /**
   * List all accessible channels
   */
  async listChannels(params?: {
    search?: string;
    channel_type?: string;
    is_active?: boolean;
    is_archived?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<AgentChannel>> {
    return apiRequest('/api/v1/agents/channels/', {
      method: 'GET',
      params
    });
  },

  /**
   * Get channel details
   */
  async getChannel(channelId: string): Promise<AgentChannel> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/`);
  },

  /**
   * Create a new channel
   */
  async createChannel(data: CreateChannelRequest): Promise<AgentChannel> {
    return apiRequest('/api/v1/agents/channels/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Update channel details
   */
  async updateChannel(channelId: string, data: Partial<AgentChannel>): Promise<AgentChannel> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete a channel
   */
  async deleteChannel(channelId: string): Promise<void> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/`, {
      method: 'DELETE'
    });
  },

  /**
   * Join a channel
   */
  async joinChannel(channelId: string): Promise<{ message: string; membership_id: string }> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/join/`, {
      method: 'POST'
    });
  },

  /**
   * Leave a channel
   */
  async leaveChannel(channelId: string): Promise<{ message: string }> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/leave/`, {
      method: 'POST'
    });
  },

  /**
   * Get channel messages
   */
  async getChannelMessages(
    channelId: string,
    params?: {
      thread_id?: string;
      page?: number;
      page_size?: number;
    }
  ): Promise<PaginatedResponse<ChannelMessage>> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/messages/`, {
      method: 'GET',
      params
    });
  },

  /**
   * Post a message to a channel
   */
  async postMessage(channelId: string, data: PostMessageRequest): Promise<ChannelMessage> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/post_message/`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  /**
   * Get channel members
   */
  async getChannelMembers(channelId: string): Promise<ChannelMembership[]> {
    return apiRequest(`/api/v1/agents/channels/${channelId}/members/`);
  }
};

// Message operations
export const messageService = {
  /**
   * List all accessible messages
   */
  async listMessages(params?: {
    channel?: string;
    message_type?: string;
    thread_id?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<ChannelMessage>> {
    return apiRequest('/api/v1/agents/messages/', {
      method: 'GET',
      params
    });
  },

  /**
   * Get message details
   */
  async getMessage(messageId: string): Promise<ChannelMessage> {
    return apiRequest(`/api/v1/agents/messages/${messageId}/`);
  },

  /**
   * Update a message
   */
  async updateMessage(messageId: string, data: Partial<ChannelMessage>): Promise<ChannelMessage> {
    return apiRequest(`/api/v1/agents/messages/${messageId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Delete a message (soft delete)
   */
  async deleteMessage(messageId: string): Promise<void> {
    return apiRequest(`/api/v1/agents/messages/${messageId}/`, {
      method: 'DELETE'
    });
  },

  /**
   * React to a message
   */
  async reactToMessage(messageId: string, emoji: string): Promise<{ reactions: Record<string, string[]> }> {
    return apiRequest(`/api/v1/agents/messages/${messageId}/react/`, {
      method: 'POST',
      body: JSON.stringify({ emoji })
    });
  }
};

// Membership operations
export const membershipService = {
  /**
   * List memberships
   */
  async listMemberships(params?: {
    channel?: string;
    role?: string;
    is_active?: boolean;
    is_watching?: boolean;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<ChannelMembership>> {
    return apiRequest('/api/v1/agents/memberships/', {
      method: 'GET',
      params
    });
  },

  /**
   * Get membership details
   */
  async getMembership(membershipId: string): Promise<ChannelMembership> {
    return apiRequest(`/api/v1/agents/memberships/${membershipId}/`);
  },

  /**
   * Update membership settings
   */
  async updateMembership(membershipId: string, data: Partial<ChannelMembership>): Promise<ChannelMembership> {
    return apiRequest(`/api/v1/agents/memberships/${membershipId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * Mute channel notifications
   */
  async muteChannel(membershipId: string): Promise<{ message: string }> {
    return apiRequest(`/api/v1/agents/memberships/${membershipId}/mute/`, {
      method: 'POST'
    });
  },

  /**
   * Unmute channel notifications
   */
  async unmuteChannel(membershipId: string, notificationLevel?: 'all' | 'mentions' | 'none'): Promise<{ message: string }> {
    return apiRequest(`/api/v1/agents/memberships/${membershipId}/unmute/`, {
      method: 'POST',
      body: JSON.stringify({ notification_level: notificationLevel })
    });
  }
};

// Combined service export
export const agentChannelsService = {
  channels: channelService,
  messages: messageService,
  memberships: membershipService
};

export default agentChannelsService;