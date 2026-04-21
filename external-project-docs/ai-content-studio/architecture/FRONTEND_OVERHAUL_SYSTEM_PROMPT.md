# 🚀 FRONTEND OVERHAUL SYSTEM PROMPT

## Mission
You are tasked with performing a complete frontend overhaul of the AI Content Studio application. The current frontend consists of multiple disconnected HTML files with inline JavaScript and is "hideous" according to the client. There's already a React Native Web setup in `/ai-studio-premium/` that needs to be the foundation for the new unified frontend.

## Current State Analysis

### Existing Frontend Files (To Be Replaced/Migrated):
- **studio.html** (596KB!) - Main monolithic interface with everything crammed in
- **index.html** (241KB) - Another huge file with duplicate functionality  
- **voice-ui.html** - Voice recording interface
- **edit-interface.html** - Content editing interface
- **blog-studio.html** - Blog generation interface
- **auth.html** - Authentication pages
- **landing.html** - Marketing landing page
- **test-batch.html** - Testing interface

### Existing React Native Web App (`/ai-studio-premium/`):
- Already has TypeScript, React Navigation, Zustand state management
- Has premium UI components with glass morphism and gradients
- Configured with Expo for cross-platform (Web, iOS, Android)
- Has basic screens but needs to integrate ALL functionality

### Backend API (157+ endpoints!):
The backend is comprehensive with these major feature groups:
1. **Content Generation**: Text, images, batch processing
2. **Stability AI**: 15+ image editing features (upscale, inpaint, remove background, etc.)
3. **Video Generation**: Runway ML integration
4. **Voice Studio**: Transcription, speaker diarization
5. **Campaign Management**: Multi-channel campaigns
6. **eBooks**: Full book generation with chapters
7. **Pitch Decks**: Presentation generation
8. **Podcasts**: Script generation
9. **Infographics**: Data visualization
10. **Research-to-Book**: Document ingestion and book creation with citations
11. **Gallery System**: Save and manage generated content
12. **Memory System**: Context-aware generation
13. **Export System**: Multiple format exports

## Your Task

### Phase 1: Architecture & Setup
1. **Use the existing React Native Web app** in `/ai-studio-premium/` as the foundation
2. **Convert to a proper React Web App** with React Router for web-first experience
3. **Setup a modern build system** (Vite recommended for speed)
4. **Configure TypeScript** properly with strict mode
5. **Setup Tailwind CSS** with a cohesive design system

### Phase 2: Design System
Create a beautiful, modern design system with:
1. **Color Palette**: 
   - Primary: Modern purple-blue gradient (#667eea to #764ba2)
   - Dark mode by default with light mode option
   - Semantic colors for success, error, warning, info

2. **Typography**:
   - Use Inter or similar modern font
   - Clear hierarchy (h1-h6, body, caption)
   - Responsive sizing

3. **Components Library**:
   - Cards with glass morphism effect
   - Modern form inputs with floating labels
   - Beautiful buttons with hover states
   - Loading states with skeletons
   - Toast notifications
   - Modal system
   - Dropdown menus
   - Tab navigation

### Phase 3: Application Structure

```
/src
  /components
    /common         # Shared components
      Button.tsx
      Card.tsx
      Input.tsx
      Modal.tsx
      Toast.tsx
    /layout         # Layout components
      Header.tsx
      Sidebar.tsx
      Footer.tsx
    /features       # Feature-specific components
      /content-generation
      /gallery
      /voice-studio
      /campaigns
      
  /pages           # Route pages
    /dashboard
    /studio
    /gallery
    /campaigns
    /ebooks
    /voice
    /research
    
  /services        # API services
    api.ts
    auth.ts
    content.ts
    
  /store           # Zustand stores
    authStore.ts
    contentStore.ts
    uiStore.ts
    
  /hooks           # Custom hooks
    useApi.ts
    useAuth.ts
    useToast.ts
    
  /utils           # Utilities
    constants.ts
    helpers.ts
    
  /styles          # Global styles
    globals.css
    tailwind.css
```

### Phase 4: Core Features to Implement

#### 1. Dashboard (Homepage)
- **Statistics cards**: Total content created, credits used, recent activity
- **Quick actions**: Generate content, upload image, start voice recording
- **Recent generations gallery**
- **Activity feed**

#### 2. Content Studio (Main Creation Hub)
Tabbed interface with:
- **Text Generation**: Blog posts, social media, emails
- **Image Generation**: Single, batch, variations
- **Image Editing**: All Stability AI features in a Photoshop-like interface
- **Video Generation**: Runway ML integration
- **Voice Studio**: Recording, transcription, processing

#### 3. Research & Books
- **Document Upload**: Drag-and-drop for PDFs, URLs, YouTube
- **Research Dashboard**: View ingested documents
- **Book Creator**: Configure and generate books from research
- **Citation Manager**: Track and edit citations

#### 4. Campaign Manager
- **Campaign List**: Card view with status indicators
- **Campaign Builder**: Multi-step wizard
- **Analytics Dashboard**: Charts and metrics
- **A/B Testing**: Visual comparison tools

#### 5. Gallery & Library
- **Masonry layout** for images
- **Filtering**: By type, date, tags
- **Collections**: User-created folders
- **Quick actions**: Download, edit, share, delete

#### 6. Professional Tools
- **eBook Editor**: Chapter management, preview
- **Pitch Deck Builder**: Slide editor with templates
- **Podcast Script Editor**: Segment management
- **Infographic Designer**: Template-based creation

### Phase 5: UI/UX Requirements

1. **Navigation**:
   - Collapsible sidebar with icons and labels
   - Breadcrumb navigation
   - Search bar in header
   - User profile dropdown

2. **Responsive Design**:
   - Mobile-first approach
   - Breakpoints: 640px, 768px, 1024px, 1280px
   - Touch-friendly on mobile
   - Desktop-optimized layouts

3. **Interactions**:
   - Smooth animations (Framer Motion)
   - Hover states on all interactive elements
   - Loading skeletons instead of spinners
   - Optimistic UI updates
   - Keyboard shortcuts for power users

4. **Data Visualization**:
   - Use Recharts or similar for analytics
   - Progress bars for generation status
   - Real-time updates via WebSocket if available

### Phase 6: Technical Requirements

1. **State Management**:
   - Use Zustand (already in project)
   - Persist user preferences
   - Optimistic updates
   - Cache API responses

2. **API Integration**:
   - Axios with interceptors
   - Automatic retry logic
   - Error boundaries
   - Request cancellation

3. **Performance**:
   - Code splitting by route
   - Lazy loading for images
   - Virtual scrolling for long lists
   - Service worker for offline support
   - Image optimization

4. **Authentication**:
   - JWT token management
   - Auto-refresh tokens
   - Protected routes
   - Role-based access

### Phase 7: Migration Strategy

1. **Start with core functionality** in React
2. **Import existing services** from HTML files:
   - `research-book-service.js`
   - `voice-capture.js`
   - `styles_data.js`
3. **Preserve API compatibility** - use same endpoints
4. **Gradual feature migration** - don't break existing backend

### Phase 8: Content Pipeline Workflow System (CRITICAL FEATURE)

This is the **MOST IMPORTANT** feature to implement - a complete workflow system that allows users to create content pipelines from research to publication.

#### Workflow Builder Interface
Create a visual workflow builder (like Zapier/n8n) where users can:

1. **Drag and drop workflow nodes** to create custom pipelines
2. **Connect nodes** to define data flow
3. **Save workflows** as templates for reuse
4. **Run workflows** with one click or on schedule
5. **Monitor progress** with real-time status updates

#### Core Workflow Nodes

**Input Nodes:**
- 📚 **Research Input**: URLs, PDFs, YouTube videos, documents
- 🎤 **Voice Input**: Record or upload audio
- 📝 **Text Input**: Manual text entry or paste
- 🖼️ **Image Input**: Upload existing images
- 📊 **Data Input**: CSV, JSON, API webhooks

**Processing Nodes:**
- 🧠 **Content Generation**: Generate text from research/prompts
- 🎨 **Image Generation**: Create images from text/style
- 🎬 **Video Generation**: Create videos from images/text
- ✏️ **Content Enhancement**: Improve/edit existing content
- 🔄 **Format Conversion**: Convert between formats
- 🎯 **Content Optimization**: SEO, readability, tone adjustment
- 📝 **Summarization**: Create summaries from long content
- 🏷️ **Tagging/Categorization**: Auto-tag and categorize

**Output Nodes:**
- 📱 **Social Media**: Post to Twitter, LinkedIn, Instagram, Facebook
- 📰 **Blog Publishing**: WordPress, Medium, Ghost, Webflow
- 📚 **eBook Creation**: Generate EPUB/MOBI with chapters
- 📧 **Email Campaigns**: Send to investors, customers, lists
- 📊 **Presentations**: Create pitch decks, slides
- 🎙️ **Podcast Scripts**: Generate episode scripts
- 📈 **Reports**: Generate PDF reports with charts
- 💾 **Storage**: Save to gallery, cloud storage, database
- 🔗 **Webhooks**: Send to external services

#### Example Workflows

**1. Research to Multi-Channel Campaign:**
```
[Research URLs] → [Extract Key Points] → [Generate Blog Post] → 
                                      ↓
                            [Generate Social Posts] → [Create Images] →
                                      ↓
                            [Schedule Publishing] → [Twitter/LinkedIn/Blog]
```

**2. Voice Memo to Investor Update:**
```
[Voice Recording] → [Transcribe] → [Extract Action Items] →
                                ↓
                    [Generate Executive Summary] → [Create Charts] →
                                ↓
                    [Format Email] → [Send to Investor List]
```

**3. Document to Educational Content:**
```
[Upload PDFs] → [Extract Information] → [Generate eBook Chapters] →
                                    ↓
                        [Create Tutorial Videos] → [Generate Quiz] →
                                    ↓
                        [Package as Course] → [Publish to LMS]
```

**4. Complete Content Suite from Single Idea:**
```
[Text Prompt] → [Generate Long-form Article] → [Extract Key Points] →
            ↓                               ↓                    ↓
    [Generate Images]              [Social Media Posts]    [Email Newsletter]
            ↓                               ↓                    ↓
    [Create Infographic]           [Schedule Posts]        [Send Campaign]
```

#### Workflow UI Components

```tsx
// Example Workflow Builder Component Structure
interface WorkflowNode {
  id: string;
  type: 'input' | 'process' | 'output';
  category: string;
  name: string;
  config: Record<string, any>;
  position: { x: number; y: number };
  inputs: string[];
  outputs: string[];
}

interface WorkflowConnection {
  id: string;
  source: string;
  target: string;
  sourceHandle: string;
  targetHandle: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  connections: WorkflowConnection[];
  schedule?: CronSchedule;
  triggers?: WorkflowTrigger[];
}
```

#### Visual Workflow Editor Features

1. **Node Library Panel**: Categorized list of available nodes
2. **Canvas Area**: Drag-drop workspace with grid snap
3. **Properties Panel**: Configure selected node
4. **Execution Panel**: Run, test, debug workflows
5. **History Panel**: View past executions and logs

#### Workflow Execution Engine

```tsx
// Workflow execution should support:
- Sequential execution
- Parallel processing where possible
- Error handling with retry logic
- Conditional branching (if/then)
- Loops and iterations
- Variable passing between nodes
- Progress tracking
- Result caching
```

#### Pre-built Workflow Templates

Provide ready-to-use workflows:
1. **Content Repurposing**: Blog → Social → Newsletter
2. **Research Paper**: Documents → Analysis → Academic Paper
3. **Marketing Campaign**: Idea → Content → Images → Multi-channel
4. **Weekly Newsletter**: Gather content → Curate → Format → Send
5. **Podcast Production**: Script → Audio → Transcript → Show Notes
6. **Course Creation**: Outline → Chapters → Videos → Quizzes
7. **Investor Updates**: Metrics → Summary → Visuals → Email
8. **Product Launch**: Announcement → Press Release → Social → Email

### Phase 9: Modern Features to Add

1. **AI Assistant Chat**: Floating chat widget for help
2. **Command Palette**: Cmd+K for quick actions
3. **Collaborative Features**: Share and collaborate on content
4. **Templates Marketplace**: Browse and use templates
5. **Real-time Notifications**: WebSocket for live updates
6. **Dark/Light Mode**: System preference detection
7. **Internationalization**: Multi-language support ready
8. **Analytics Dashboard**: Track workflow performance
9. **Version Control**: Track changes in workflows
10. **API Integration**: Connect external services

## Success Criteria

1. ✅ Single cohesive React application (no more separate HTML files)
2. ✅ Beautiful, modern UI that looks professional
3. ✅ All 157+ API endpoints integrated
4. ✅ Mobile responsive
5. ✅ Fast performance (Lighthouse score 90+)
6. ✅ TypeScript with no any types
7. ✅ Comprehensive error handling
8. ✅ Loading states for all async operations
9. ✅ Keyboard accessible
10. ✅ Documentation for components

## Getting Started Commands

```bash
# Navigate to the React app
cd /Users/donkeyking/development/ai-content-studio/ai-studio-premium

# Install additional dependencies you'll need
npm install react-router-dom@6 \
  @tanstack/react-query \
  framer-motion \
  recharts \
  react-dropzone \
  react-markdown \
  @headlessui/react \
  @heroicons/react \
  clsx \
  date-fns

# Start development
npm run web

# The app should run on http://localhost:8081
# Backend API is on http://localhost:8001
```

## File Structure Example

Here's an example of what a clean component should look like:

```tsx
// src/components/features/ContentGeneration/TextGenerator.tsx
import React, { useState } from 'react';
import { useContentStore } from '@/store/contentStore';
import { Button, Card, Input, Select } from '@/components/common';
import { useToast } from '@/hooks/useToast';
import { contentAPI } from '@/services/api';

interface TextGeneratorProps {
  onGenerate?: (content: string) => void;
}

export const TextGenerator: React.FC<TextGeneratorProps> = ({ onGenerate }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const { addContent } = useContentStore();
  const { showToast } = useToast();

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      showToast('Please enter a prompt', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await contentAPI.generateText({ prompt });
      addContent(response.data);
      onGenerate?.(response.data.content);
      showToast('Content generated successfully!', 'success');
    } catch (error) {
      showToast('Failed to generate content', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-4">Generate Text Content</h3>
      <div className="space-y-4">
        <Input
          label="Enter your prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Write a blog post about..."
          multiline
          rows={4}
        />
        <Button
          onClick={handleGenerate}
          loading={loading}
          className="w-full"
        >
          Generate Content
        </Button>
      </div>
    </Card>
  );
};
```

## Backend Infrastructure: Redis/Celery Integration

**IMPORTANT**: The donkey_betz app at `/Users/donkeyking/development/donkey_betz/backend/` already has a robust Redis/Celery setup that we can adapt. Here's what to leverage:

### Existing Infrastructure to Copy:
1. **Redis Configuration**:
   - Multiple Redis databases for different caches (default, memory_search, embeddings, api, orchestration)
   - WebSocket support via Redis channels
   - Connection pooling with 150+ max connections

2. **Celery Setup**:
   - Beat scheduler for periodic tasks
   - Multiple queues (default, agents, high_priority, low_priority, maintenance, cache, security)
   - Worker auto-scaling based on load
   - Task routing and priority management
   - Retry logic with exponential backoff

3. **Content Pipeline System** (`/donkey_betz/backend/content_pipeline/`):
   - Pipeline models and stage execution
   - Async task chaining with Celery
   - Stage-by-stage execution with auto-advance
   - Error handling and retries

### Setup Instructions for Backend:

```bash
# Install Redis and Celery dependencies
pip install redis celery django-celery-beat django-celery-results django-redis

# Copy Celery configuration from donkey_betz
cp /Users/donkeyking/development/donkey_betz/backend/server/celery.py \
   /Users/donkeyking/development/ai-content-studio/backend/core/celery.py

# Start Redis (if not running)
redis-server

# Start Celery worker
celery -A core worker -l info --pool=prefork --concurrency=4

# Start Celery beat (for scheduled tasks)
celery -A core beat -l info

# Optional: Start Flower for monitoring
pip install flower
celery -A core flower
```

### Workflow Execution Architecture:

```python
# Example async workflow execution with Celery
from celery import chain, group, chord

# Sequential workflow
workflow = chain(
    research_task.s(urls),
    extract_key_points.s(),
    generate_content.s(),
    generate_images.s(),
    publish_multi_channel.s()
)

# Parallel processing
parallel_tasks = group(
    generate_blog.s(content),
    generate_social.s(content),
    generate_email.s(content)
)

# Complex workflow with parallel and sequential
complex_workflow = chain(
    research_task.s(urls),
    chord(
        group(
            extract_text.s(),
            extract_images.s(),
            extract_metadata.s()
        ),
        combine_results.s()
    ),
    generate_final_content.s()
)
```

## Backend API Requirements for Workflow System

The workflow system will need these new API endpoints (to be implemented):

```typescript
// Workflow Management APIs
POST   /api/workflows/                    // Create new workflow
GET    /api/workflows/                    // List user workflows
GET    /api/workflows/:id/                // Get workflow details
PUT    /api/workflows/:id/                // Update workflow
DELETE /api/workflows/:id/                // Delete workflow
POST   /api/workflows/:id/duplicate/      // Duplicate workflow
POST   /api/workflows/:id/execute/        // Execute workflow
GET    /api/workflows/:id/executions/     // Get execution history
GET    /api/workflows/executions/:id/     // Get execution details
POST   /api/workflows/:id/schedule/       // Schedule workflow
DELETE /api/workflows/:id/schedule/       // Remove schedule
GET    /api/workflows/templates/          // Get workflow templates
POST   /api/workflows/from-template/      // Create from template

// Workflow Node Registry
GET    /api/workflow-nodes/               // Get available nodes
GET    /api/workflow-nodes/:type/config/  // Get node configuration schema

// Workflow execution will use existing APIs:
// - /api/research-to-book/
// - /api/content/create/
// - /api/content/batch/
// - /api/stability/*/
// - /api/campaigns/
// - /api/ebooks/
// - /api/voice/transcribe/
// etc.
```

### WebSocket Integration for Real-time Updates:

The frontend should connect to WebSocket for real-time workflow updates:

```typescript
// WebSocket connection for workflow updates
interface WorkflowWebSocket {
  connect(): void;
  subscribe(workflowId: string): void;
  onProgress(callback: (data: ProgressData) => void): void;
  onComplete(callback: (data: CompleteData) => void): void;
  onError(callback: (error: ErrorData) => void): void;
  disconnect(): void;
}

// Example usage in React component
useEffect(() => {
  const ws = new WorkflowWebSocket();
  ws.connect();
  
  ws.subscribe(workflowId);
  
  ws.onProgress((data) => {
    setProgress(data.percentage);
    setCurrentNode(data.nodeId);
    setLogs([...logs, data.message]);
  });
  
  ws.onComplete((data) => {
    setStatus('completed');
    setResults(data.outputs);
  });
  
  return () => ws.disconnect();
}, [workflowId]);
```

## Important Notes

1. **Preserve the backend** - It's working well, just needs a better frontend
2. **Use the auth token**: `<redacted-993f8273-2026-04-20>` for testing
3. **API Base URL**: `http://localhost:8001/api/`
4. **Focus on UX**: Make it intuitive and delightful to use
5. **Performance matters**: Users are generating lots of content
6. **Error handling**: Every API call should have proper error handling
7. **Loading states**: Never leave users wondering what's happening
8. **Workflow System is PRIORITY #1**: This is the killer feature that ties everything together

## Visual Mockup: Workflow Builder Interface

```
┌──────────────────────────────────────────────────────────────────────┐
│  AI Content Studio  [Search...]  [⌘K]  [🔔]  [User ▼]              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐  ┌────────────────────────────────┐  ┌──────────┐ │
│  │   INPUTS    │  │     WORKFLOW CANVAS            │  │PROPERTIES│ │
│  ├─────────────┤  │                                │  ├──────────┤ │
│  │ 📚 Research │  │  ┌──────────┐                  │  │Node: Blog│ │
│  │ 🎤 Voice    │  │  │Research  │                  │  │          │ │
│  │ 📝 Text     │  │  │URLs      │                  │  │Title:    │ │
│  │ 🖼️ Image    │  │  └────┬─────┘                  │  │[_______] │ │
│  │             │  │       │                        │  │          │ │
│  ├─────────────┤  │       ▼                        │  │Tone:     │ │
│  │  PROCESS    │  │  ┌──────────┐   ┌──────────┐  │  │[Casual▼] │ │
│  ├─────────────┤  │  │Extract   │──▶│Generate  │  │  │          │ │
│  │ 🧠 Generate │  │  │Key Points│   │Blog Post │  │  │Length:   │ │
│  │ 🎨 Images   │  │  └──────────┘   └────┬─────┘  │  │[1500]    │ │
│  │ ✏️ Edit     │  │                       │        │  │          │ │
│  │ 🔄 Convert  │  │                       ▼        │  │Keywords: │ │
│  │             │  │                ┌──────────┐    │  │[_______] │ │
│  ├─────────────┤  │                │Generate  │    │  │          │ │
│  │   OUTPUTS   │  │                │Social    │    │  │[Save]    │ │
│  ├─────────────┤  │                │Posts     │    │  │          │ │
│  │ 📱 Social   │  │                └────┬─────┘    │  └──────────┘ │
│  │ 📰 Blog     │  │                     │          │                │
│  │ 📚 eBook    │  │                     ▼          │  ┌──────────┐ │
│  │ 📧 Email    │  │              ┌──────────┐      │  │EXECUTION │ │
│  │ 💾 Save     │  │              │Publish   │      │  ├──────────┤ │
│  └─────────────┘  │              │Multi-    │      │  │▶ Run Now │ │
│                   │              │Channel   │      │  │          │ │
│                   │              └──────────┘      │  │Schedule: │ │
│                   └────────────────────────────────┘  │[Daily ▼] │ │
│                                                        │          │ │
│  ┌───────────────────────────────────────────────────────────────┐ │ │
│  │ Execution Log:  [Running... 45%]  ████████░░░░░░░░           │ │ │
│  │ ✓ Research URLs loaded (3 documents)                         │ │ │
│  │ ✓ Key points extracted (15 points)                          │ │ │
│  │ ⟳ Generating blog post...                                   │ │ │
│  └───────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Inspiration & References

Look at these for UI inspiration:
- **Vercel Dashboard**: Clean, modern, great use of space
- **Linear**: Beautiful interactions and keyboard shortcuts
- **Notion**: Powerful but approachable interface
- **Runway ML**: Great for creative tools UI
- **Figma**: Excellent tool panels and workspace
- **Zapier/n8n**: Workflow builder interfaces
- **Retool**: Visual programming paradigm

## Final Deliverable

A single, beautiful, cohesive React application that:
1. Replaces all existing HTML files
2. Integrates all backend features
3. Looks modern and professional
4. Works on all devices
5. Is a joy to use

The client should be able to delete the entire `/frontend` folder of HTML files and have everything working better in the new React app.

---

Good luck! Make it beautiful! 🎨✨