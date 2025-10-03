# Section 7: Frontend Systems
**Agent Name: Frontend Architecture Reviewer**

## Scope Overview
This section covers the frontend implementations including the React web application and Flutter mobile app, analyzing architecture, state management, and UI patterns.

### Primary Directories:
- `donkey-betz-frontend/` - React/Vite web application
- `frontend/` - Flutter mobile application
- Frontend configuration and build files

## Analysis Instructions for Claude Code Agent

### 1. React Application Architecture
**Investigate:**
- `donkey-betz-frontend/src/` - Main source directory
- `donkey-betz-frontend/src/features/` - Feature-based organization
- `donkey-betz-frontend/src/components/` - Shared components
- `donkey-betz-frontend/vite.config.ts` - Build configuration

**Key Questions:**
- What is the folder structure?
- How are features organized?
- What routing strategy is used?
- How is code splitting implemented?

### 2. State Management (Zustand)
**Investigate:**
- `donkey-betz-frontend/src/store/` - Zustand stores
- Store usage patterns across features
- State persistence strategies
- Store composition patterns

**Key Questions:**
- What stores exist?
- How is state organized?
- What persistence is used?
- How are stores composed?

### 3. API Client Implementation
**Investigate:**
- `donkey-betz-frontend/src/services/apiClient.ts` - API client
- `donkey-betz-frontend/src/services/` - Service layer
- Request/response interceptors
- Error handling patterns

**Key Questions:**
- How are API calls made?
- How is auth handled?
- What error handling exists?
- How are types managed?

### 4. UI Component Library
**Investigate:**
- `donkey-betz-frontend/src/components/ui/` - UI components
- Component composition patterns
- Styling approach (Tailwind CSS)
- Animation libraries

**Key Questions:**
- What UI components exist?
- How is styling managed?
- What animation is used?
- How accessible are components?

### 5. Feature Implementation
**Investigate key features:**
- `donkey-betz-frontend/src/features/ai-assistant/` - AI chat
- `donkey-betz-frontend/src/features/memory-palace/` - Memory system
- `donkey-betz-frontend/src/features/business-hub/` - Business tools
- `donkey-betz-frontend/src/features/scout-hub/` - Discovery platform
- `donkey-betz-frontend/src/features/command-center/` - Agent control

**Key Questions:**
- How are features structured?
- What components are shared?
- How do features communicate?
- What are the data flows?

### 6. WebSocket Integration
**Investigate:**
- `donkey-betz-frontend/src/services/websocket/` - WebSocket client
- WebSocket usage in features
- Reconnection strategies
- Message handling patterns

**Key Questions:**
- How are WebSockets managed?
- What reconnection logic exists?
- How are messages typed?
- What events are handled?

### 7. Flutter Mobile App
**Investigate:**
- `frontend/lib/` - Flutter source
- `frontend/lib/screens/` - Screen components
- `frontend/lib/providers/` - State management
- `frontend/lib/services/` - Service layer

**Key Questions:**
- What screens exist?
- How is navigation handled?
- What state management is used?
- How does it sync with web?

### 8. Performance Optimization
**Investigate:**
- Bundle size optimization
- Lazy loading implementation
- Image optimization
- Cache strategies

**Key Questions:**
- What is the bundle size?
- How is code split?
- What caching exists?
- How are images optimized?

### 9. TypeScript & Type Safety
**Investigate:**
- `donkey-betz-frontend/src/types/` - Type definitions
- API type generation
- Type safety patterns
- Runtime validation

**Key Questions:**
- How are types defined?
- Are types generated?
- What validation exists?
- How strict is typing?

### 10. Build & Deployment
**Investigate:**
- `donkey-betz-frontend/package.json` - Dependencies
- Build scripts and configuration
- Environment configuration
- Deployment process

**Key Questions:**
- What is the build process?
- How are envs managed?
- What is deployed?
- How is it optimized?

## Critical Files to Review
1. `donkey-betz-frontend/src/App.tsx` - Main app component
2. `donkey-betz-frontend/src/router.tsx` - Routing configuration
3. `donkey-betz-frontend/src/services/apiClient.ts` - API integration
4. `donkey-betz-frontend/src/store/index.ts` - Store configuration
5. `frontend/lib/main.dart` - Flutter entry point

## UI/UX Patterns
1. **Dark Theme** - Primary visual design
2. **Card-based Layout** - Content organization
3. **Real-time Updates** - WebSocket indicators
4. **Loading States** - Skeleton screens
5. **Error Boundaries** - Graceful failures
6. **Animations** - Smooth transitions
7. **Responsive Design** - Mobile-first
8. **Accessibility** - ARIA labels

## Expected Outputs from Analysis
1. Component hierarchy diagram
2. State management flow
3. API integration patterns
4. WebSocket architecture
5. Performance metrics
6. Bundle size analysis
7. Type coverage report
8. Feature dependency graph

## Special Considerations
- Vite vs Create React App migration
- TypeScript strict mode compliance
- WebSocket reconnection reliability
- State synchronization across tabs
- Mobile app feature parity
- PWA capabilities
- Offline functionality
- Cross-browser compatibility
- Performance on low-end devices
- Accessibility compliance