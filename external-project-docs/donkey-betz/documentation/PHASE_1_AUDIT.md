# Phase 1: Frontend Audit & Infrastructure Setup

## 1.1 Frontend Component Audit

### Directory Structure
The main frontend is located in `/donkey-betz-frontend/src/` with the following structure:

### Pages
Located in `/pages/`:
- AILearningCenter.tsx
- AIOpsDashboard.tsx
- AssetGallery.tsx
- ContentStudioTest.tsx
- Dashboard.tsx
- DataVerification.tsx
- Experiments.tsx
- Login.tsx
- MemoryTimeline.tsx
- MissionReport.tsx
- OptimizedMemoryTimelinePage.tsx
- Profile.tsx
- RealTimeDemo.tsx
- Settings.tsx
- StockDashboard.tsx
- TemplateLibrary.tsx
- TestPage.tsx
- UKFDemo.tsx
- UKFKnowledgeHub.tsx
- UKFKnowledgeHubTest.tsx
- UKFTest.tsx

### Features
Major features organized by domain:

#### AI & Agents
- **ai-assistant-hub/**: AI chat interface with agent selection, memory, and learning
- **ai-learning-center/**: AI learning dashboard and self-diagnosis
- **ai-os/**: AI assistant panel and agent launcher
- **ai-profile/**: User profile intelligence and fact management
- **agents/**: Component library and example adaptation for agents

#### Business & Finance
- **business-hub/**: Universal builder for generating businesses
- **business-chat-network/**: Multi-tenant chat network with agent channels
- **stock-intelligence/**: Stock market analysis and portfolio management
- **reddit-scout/**: Reddit idea scouting and stock discovery

#### Content & Media
- **content-studio/**: Asset library, image/video generation, YouTube integration
- **obs-studio/**: OBS Studio control dashboard
- **davinci-resolve/**: DaVinci Resolve integration dashboard
- **youtube/**: YouTube upload management

#### Knowledge & Memory
- **memory-palace/**: Document management, semantic search, knowledge graph
- **unified-knowledge-hub/**: Unified document and memory viewer
- **research-intelligence/**: Research assistant and search interface

#### System & Admin
- **admin/**: API health dashboard
- **command-center/**: Task management and agent deployment
- **dashboard/**: Main dashboard with stats
- **unified-dashboard/**: New unified dashboard with widgets
- **onboarding/**: User onboarding wizard
- **privacy-dashboard/**: Privacy controls and monitoring

### Components Requiring Real-time Updates

#### High Priority (Real-time Critical)
1. **business-chat-network/**
   - MessageList.tsx - Live message updates
   - ChannelList.tsx - Channel status and presence
   - AgentStatusPanel.tsx - Agent online/offline status
   - Uses: `useChannelWebSocket.ts`, `useNetworkWebSocket.ts`, `useAgentChannelWebSocket.ts`

2. **obs-studio/**
   - OBSConnectionStatus.tsx - Connection state
   - RecordingControls.tsx - Recording status/duration
   - StreamingControls.tsx - Stream status
   - LivePreview.tsx - Preview frames
   - Uses: `useOBSConnection.ts`, `useOBSRecording.ts`

3. **command-center/**
   - ActiveTasks.tsx - Task progress updates
   - AgentActivityVisualizer.tsx - Live agent activity
   - Uses: `useAgentProgress.ts`

4. **unified-dashboard/**
   - ActivityStream.tsx - Live activity feed
   - WidgetGrid.tsx - Widget data updates
   - Uses: `UnifiedWebSocketManager.ts`, `EventBus.ts`

5. **ai-assistant-hub/**
   - AIAssistantHub.tsx - Streaming chat responses
   - Uses: `useChatStream.ts`

#### Medium Priority (Periodic Updates)
1. **stock-intelligence/**
   - MarketScanner.tsx - Market data updates
   - StockScoutReport.tsx - Analysis updates
   - Uses: `useMarketData.ts`, `useStockPrices.ts`

2. **reddit-scout/**
   - RedditMonitor.tsx - New Reddit posts
   - Uses: `useRedditStream.ts`

3. **content-studio/**
   - BatchProcessor.tsx - Processing progress
   - Uses: `useBatchProcess.ts`

4. **memory-palace/**
   - EmbeddingProgress.tsx - Embedding job progress
   - ImportProgressTracker.tsx - Import status

### Frontend to Backend Service Mapping

#### API Services (`/services/api/`)
- `agent-orchestra.service.ts` → `/api/agent-orchestra/`
- `aiLearning.service.ts` → `/api/ai-learning/`
- `analytics.service.ts` → `/api/analytics/`
- `assets.service.ts` → `/api/assets/`
- `chat.service.ts` → `/api/chat/`
- `content.service.ts` → `/api/content/`
- `dashboard.service.ts` → `/api/dashboard/`
- `deployment.service.ts` → `/api/deployment/`
- `memory.service.ts` → `/api/memory/`
- `stocks.service.ts` → `/api/stocks/`
- `ukf.service.ts` → `/api/ukf/`
- `universalBuilder.service.ts` → `/api/universal-builder/`

#### WebSocket Services
- `websocket/WebSocketManager.ts` - Core WebSocket management
- `obsWebSocketService.ts` - OBS Studio WebSocket (port 4455)
- `websocket-legacy.ts` - Legacy WebSocket implementation
- Multiple feature-specific WebSocket hooks in various features

### Components NOT Using universalStyles

After reviewing the codebase, most components are already using `universalStyles.ts`. Components that need migration:

1. **Custom CSS Files:**
   - `features/ai-learning-center/components/diagnostics.css`
   - `features/stock-intelligence/styles/StockDashboard.css`
   - `features/universal-builder/styles/universal-builder.css`
   - `components/DocumentViewer/DocumentViewer.css`

2. **Components using inline styles or custom styling:**
   - Several older components in `business-chat-network/`
   - Some components in `memory-palace/`
   - Legacy components in various features

### WebSocket Events Needed

#### Core Events (System-wide)
- `connection:status` - Connection state changes
- `auth:verify` - Authentication verification
- `error:global` - Global error notifications
- `heartbeat` - Keep-alive ping/pong

#### Feature-specific Events

**Business Chat Network:**
- `message:new` - New message in channel
- `message:update` - Message edited
- `message:delete` - Message deleted
- `channel:join` - User joined channel
- `channel:leave` - User left channel
- `channel:update` - Channel metadata changed
- `presence:update` - User presence status
- `agent:status` - Agent online/offline

**Agent Orchestra:**
- `agent:start` - Agent task started
- `agent:progress` - Progress update
- `agent:complete` - Task completed
- `agent:error` - Agent error
- `orchestration:update` - Orchestration status

**OBS Studio:**
- `obs:connected` - OBS connected
- `obs:disconnected` - OBS disconnected
- `obs:recording:started` - Recording started
- `obs:recording:stopped` - Recording stopped
- `obs:streaming:started` - Stream started
- `obs:streaming:stopped` - Stream stopped
- `obs:scene:changed` - Scene switched

**Content Processing:**
- `generation:start` - Generation started
- `generation:progress` - Generation progress
- `generation:complete` - Generation complete
- `generation:error` - Generation failed

**Stock Intelligence:**
- `market:update` - Market data update
- `stock:alert` - Price alert triggered
- `portfolio:update` - Portfolio value changed

### Dependency Graph

```
WebSocketManager (Core)
├── UnifiedWebSocketManager (Dashboard)
├── Business Chat Network WebSockets
│   ├── useChannelWebSocket
│   ├── useNetworkWebSocket
│   └── useAgentChannelWebSocket
├── OBS WebSocket Service
├── Agent Progress WebSocket
└── Chat Stream WebSocket
```

## 1.2 Build Errors to Fix

### Known Issues
1. Case sensitivity in imports (Dialog.tsx vs dialog.tsx)
2. Circular dependencies between services
3. Type mismatches with backend responses
4. Unused imports in various files
5. Missing type definitions for some API responses

## 1.3 WebSocket Infrastructure Requirements

### Current State
- Multiple WebSocket implementations across features
- No unified connection management
- Limited error handling and reconnection logic
- No message queuing for offline scenarios

### Target Architecture
- Single WebSocketManager instance
- Automatic reconnection with exponential backoff
- Zustand store for connection state
- Debug tools for monitoring
- Message queue for offline resilience

## Next Steps
1. Fix all build errors first
2. Create unified WebSocket manager
3. Migrate features to use unified manager
4. Add real-time updates to priority components
5. Test and verify all connections

## Progress Update

### Completed Tasks
✅ Frontend audit complete - mapped all pages, features, and data requirements
✅ Documented components requiring real-time updates with priority levels
✅ Mapped frontend services to backend endpoints
✅ Identified components not using universalStyles
✅ Created comprehensive list of WebSocket events needed
✅ Fixed some TypeScript errors (colors.card, imports, etc.)
✅ Created UnifiedWebSocketManager with all required features
✅ Implemented Zustand store for WebSocket state management
✅ Created useUnifiedWebSocket hook for easy component integration
✅ Built WebSocket Debug Panel for monitoring and debugging

### Remaining Tasks
- Fix remaining TypeScript build errors
- Migrate existing WebSocket implementations to use UnifiedWebSocketManager
- Test the new WebSocket infrastructure
- Update components to use real-time data
- Complete documentation

### New Files Created
- `/WEBSOCKET_INFRASTRUCTURE.md` - Detailed plan for WebSocket consolidation
- `/donkey-betz-frontend/src/services/websocket/UnifiedWebSocketManager.ts` - Core WebSocket manager
- `/donkey-betz-frontend/src/store/websocketStore.ts` - Zustand store for state management
- `/donkey-betz-frontend/src/hooks/useUnifiedWebSocket.ts` - React hook for WebSocket usage
- `/donkey-betz-frontend/src/components/WebSocketDebugPanel.tsx` - Debug and monitoring UI