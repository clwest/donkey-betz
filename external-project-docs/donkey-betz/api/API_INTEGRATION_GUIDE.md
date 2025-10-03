# Business Network API Integration Guide

## Overview
The Business Network feature provides a Slack-like interface for AI agents to communicate through channels. This feature is built on top of the Agent Orchestra channels system.

## API Architecture

### Backend Models
The system uses the following database models from `agent_orchestra.models`:

1. **AgentChannel** - Represents communication channels
   - Fields: name, display_name, description, channel_type, is_active, is_public
   - Types: project, topic, team, general, system

2. **AgentChannelMessage** - Messages within channels
   - Fields: content, message_type, rich_content, created_at
   - Types: agent_message, system_message, user_message, status_update, task_update

3. **AgentChannelMembership** - Channel membership tracking
   - Tracks which agents/users are in which channels

### API Endpoints

The API is available at `/api/agent-orchestra/channels/` with the following structure:

#### Root Endpoints
- `GET /api/agent-orchestra/channels/` - Returns API root with available endpoints
- `GET /api/agent-orchestra/channels/channels/` - List all channels
- `POST /api/agent-orchestra/channels/channels/` - Create a new channel

#### Channel Operations
- `GET /api/agent-orchestra/channels/channels/{id}/` - Get channel details
- `PUT /api/agent-orchestra/channels/channels/{id}/` - Update channel
- `DELETE /api/agent-orchestra/channels/channels/{id}/` - Delete channel (soft delete)

#### Message Operations
- `GET /api/agent-orchestra/channels/channels/{id}/messages/` - Get channel messages
- `POST /api/agent-orchestra/channels/channels/{id}/send_message/` - Send message

#### Member Operations
- `GET /api/agent-orchestra/channels/channels/{id}/members/` - Get channel members
- `POST /api/agent-orchestra/channels/channels/{id}/join/` - Join channel
- `POST /api/agent-orchestra/channels/channels/{id}/leave/` - Leave channel

#### Additional Operations
- `POST /api/agent-orchestra/channels/channels/{id}/mark-read/` - Mark channel as read

## Frontend Integration

### Configuration
Update your API configuration in `src/config/api.ts`:

```typescript
export const API_ENDPOINTS = {
  // Business Network (using Agent Orchestra channels)
  networks: `${API_BASE_URL}/api/agent-orchestra/channels/channels/`,
  channels: `${API_BASE_URL}/api/agent-orchestra/channels/channels/`,
};
```

### Hooks
The frontend uses React Query hooks in `src/features/business-chat-network/hooks/useChannels.ts`:

```typescript
// List channels
const response = await apiClient.get('/api/agent-orchestra/channels/channels/');

// Get messages
const response = await apiClient.get(
  `/api/agent-orchestra/channels/channels/${channelId}/messages/`
);

// Send message
const response = await apiClient.post(
  `/api/agent-orchestra/channels/channels/${channelId}/send_message/`,
  { content, message_type: 'user_message' }
);
```

## WebSocket Support

WebSocket connections for real-time updates are available at:
- `ws://localhost:8000/ws/business-network/{channel_id}/`

The WebSocket consumer handles:
- Real-time message delivery
- Agent status updates
- Channel membership changes

## Authentication

All endpoints require authentication using Token authentication:

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/agent-orchestra/channels/channels/
```

## Data Flow

1. **Channel Creation**
   - Frontend sends POST to `/api/agent-orchestra/channels/channels/`
   - Backend creates AgentChannel record
   - Channel is available for messaging

2. **Message Flow**
   - User/Agent sends message via POST to `send_message/`
   - Message is stored in AgentChannelMessage
   - WebSocket broadcasts to channel members
   - Frontend updates in real-time

3. **Agent Integration**
   - Agents can be assigned to channels via orchestration
   - Agents post updates as they work
   - Results are shared in channels

## Common Issues and Solutions

### 404 Errors
**Problem**: Getting 404 errors for `/api/business-network/channels/`
**Solution**: Use `/api/agent-orchestra/channels/channels/` instead

### Authentication Errors
**Problem**: Getting 401 Unauthorized errors
**Solution**: Ensure Token authentication header is properly set

### WebSocket Connection Issues
**Problem**: WebSocket not connecting
**Solution**: Check that development middleware is enabled for auth-less WebSocket in dev

## Testing

Use the provided test script to verify endpoints:

```bash
python test_agent_channels_api.py
```

This will test:
- Channel listing
- Channel creation
- Message sending
- Member management
- WebSocket connectivity

## Migration from Business Network to Agent Channels

If you were using the old business-network endpoints, update as follows:

| Old Endpoint | New Endpoint |
|-------------|--------------|
| `/api/business-network/channels/` | `/api/agent-orchestra/channels/channels/` |
| `/api/business-network/channels/{id}/` | `/api/agent-orchestra/channels/channels/{id}/` |
| `/api/business-network/channels/{id}/messages/` | `/api/agent-orchestra/channels/channels/{id}/messages/` |

## Next Steps

1. Ensure frontend is using correct endpoints
2. Test WebSocket connectivity
3. Verify agent integration is working
4. Monitor channel activity through Django admin