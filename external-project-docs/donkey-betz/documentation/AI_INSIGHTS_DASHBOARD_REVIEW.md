# AI Insights Dashboard Error Review and Solutions

**Review Date**: August 10, 2025  
**Session**: AI Insights Dashboard Error Analysis  
**Status**: Multiple Critical Issues Identified  
**Impact**: Dashboard functionality severely degraded

## Executive Summary

The AI Insights Dashboard is experiencing multiple critical issues:
1. **5 Missing API Endpoints** (404 errors) - Core dashboard data unavailable
2. **WebSocket Routing Failure** - Memory timeline real-time updates broken
3. **Performance Metrics Error** (500) - Metrics visualization failing
4. **Frontend attempting to connect to non-existent endpoints**
5. **Universal Styling Not Applied** - Frontend components not using the centralized styling system

## Issue Categories

### 1. Missing API Endpoints (404 Errors)

**Affected Endpoints**:
```
1. GET /api/ai-partner/performance/summary/?timeframe=7d - 404
2. GET /api/ai-partner/agents/active/ - 404
3. GET /api/ai-partner/knowledge/summary/ - 404
4. GET /api/ai-partner/insights/recent/?limit=5 - 404
5. GET /api/ai-partner/insights/summary/?timeframe=7d - 404
```

**Impact**: 
- Dashboard widgets showing loading states or errors
- No performance data displayed
- No active agents information
- No knowledge graph summary
- No recent insights displayed

**Analysis**:
These endpoints are being called from the AI Insights page components but don't exist in the backend. The frontend was likely developed expecting these endpoints based on the Phase 6 design, but they were never implemented or were implemented with different paths.

### 2. WebSocket Routing Issue

**Error Details**:
```
Exception inside application: No route found for path 'ws/memory/2/'.
ValueError: No route found for path 'ws/memory/2/'.
```

**Location**: WebSocket connection attempt at `/ws/memory/2/`

**Impact**:
- Real-time memory updates not working
- MemoryTimeline component cannot receive live updates
- User experience degraded to polling-only mode

**Analysis**:
The frontend MemoryTimeline component is trying to establish a WebSocket connection for real-time updates, but the route doesn't exist in the Django Channels routing configuration.

### 3. Performance Metrics Internal Error

**Error Details**:
```
Internal Server Error: /api/ai-partner/performance/metrics/
GET /api/ai-partner/performance/metrics/?timeframe=7d - 500
```

**Impact**:
- Performance charts not rendering
- Critical metrics unavailable
- Dashboard incomplete

**Analysis**:
This endpoint exists but is throwing an internal server error. Likely causes:
- Missing database fields
- Calculation errors
- Dependency on other services that aren't running

### 4. Working Endpoint

**Success**:
```
GET /api/ai-partner/knowledge/graph/?depth=2&node_limit=100 - 200
```

This shows that some Phase 6 endpoints are working, indicating partial implementation.

### 5. Universal Styling Not Applied

**Issue Details**:
The AI Insights Dashboard components (MemoryTimeline, LearningInsightsDashboard, PerformanceMetrics, KnowledgeGraphExplorer, FeedbackWidget) are not utilizing the universal styling system implemented in the codebase.

**Impact**:
- Inconsistent visual appearance across the application
- Accessibility features from universal styling not applied
- Theme switching (dark/light mode) may not work correctly
- Reduced maintainability due to duplicated styles
- User experience inconsistency

**Analysis**:
The Phase 6 components were likely developed in isolation without integrating with the existing universal styling system. Components are using inline styles or local style definitions instead of the centralized `universalStyling` context that provides:
- Consistent color schemes
- Typography standards
- Spacing and layout rules
- Accessibility features (high contrast, font scaling)
- Theme management

## Detailed Solutions

### Solution 1: Implement Missing API Endpoints

**Priority**: CRITICAL  
**Estimated Time**: 2-3 hours

#### Step 1: Create Performance Summary Endpoint

```python
# In backend/ai_partner/views_phase6_ux.py or views_performance.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum, Q
from datetime import datetime, timedelta
from django.utils import timezone

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_summary(request):
    """Get performance summary for specified timeframe"""
    timeframe = request.GET.get('timeframe', '7d')
    
    # Parse timeframe
    days = {
        '24h': 1,
        '7d': 7,
        '30d': 30,
        '90d': 90
    }.get(timeframe, 7)
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Get performance data from AgentInstance and TaskOrchestration
    from agent_orchestra.models import AgentInstance, TaskOrchestration
    
    summary = {
        'timeframe': timeframe,
        'total_tasks': TaskOrchestration.objects.filter(
            user=request.user,
            created_at__gte=start_date
        ).count(),
        'success_rate': TaskOrchestration.objects.filter(
            user=request.user,
            created_at__gte=start_date,
            overall_status='completed'
        ).count() / max(1, TaskOrchestration.objects.filter(
            user=request.user,
            created_at__gte=start_date
        ).count()) * 100,
        'avg_completion_time': AgentInstance.objects.filter(
            user=request.user,
            created_at__gte=start_date
        ).aggregate(
            avg_time=Avg('completion_time')
        )['avg_time'] or 0,
        'agent_performance': [],
        'trends': {
            'tasks': [],
            'success_rate': [],
            'response_time': []
        }
    }
    
    # Get per-agent performance
    agents = AgentInstance.objects.filter(
        user=request.user,
        created_at__gte=start_date
    ).values('template__name').annotate(
        total=Count('id'),
        success=Count('id', filter=Q(current_status='completed')),
        avg_time=Avg('completion_time')
    )
    
    for agent in agents:
        summary['agent_performance'].append({
            'name': agent['template__name'],
            'total_executions': agent['total'],
            'success_count': agent['success'],
            'success_rate': (agent['success'] / max(1, agent['total'])) * 100,
            'avg_completion_time': agent['avg_time'] or 0
        })
    
    # Generate trend data (simplified - in production, group by day)
    for i in range(days):
        date = timezone.now() - timedelta(days=i)
        day_tasks = TaskOrchestration.objects.filter(
            user=request.user,
            created_at__date=date.date()
        ).count()
        
        summary['trends']['tasks'].append({
            'date': date.strftime('%Y-%m-%d'),
            'value': day_tasks
        })
    
    return Response(summary)
```

#### Step 2: Create Active Agents Endpoint

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_agents(request):
    """Get currently active agent instances"""
    from agent_orchestra.models import AgentInstance
    
    active = AgentInstance.objects.filter(
        user=request.user,
        current_status__in=['working', 'pending', 'initializing']
    ).select_related('template', 'orchestration')
    
    agents = []
    for agent in active:
        agents.append({
            'id': agent.id,
            'name': agent.template.name if agent.template else 'Unknown',
            'status': agent.current_status,
            'progress': agent.progress_percentage,
            'task': agent.assigned_task,
            'started_at': agent.created_at,
            'orchestration_id': agent.orchestration_id,
            'estimated_completion': agent.estimated_completion if hasattr(agent, 'estimated_completion') else None
        })
    
    return Response({
        'active_count': len(agents),
        'agents': agents
    })
```

#### Step 3: Create Knowledge Summary Endpoint

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def knowledge_summary(request):
    """Get knowledge base summary statistics"""
    from shared_memory.models import UnifiedMemoryEntry
    
    total_memories = UnifiedMemoryEntry.objects.filter(user=request.user).count()
    
    summary = {
        'total_memories': total_memories,
        'memories_with_embeddings': UnifiedMemoryEntry.objects.filter(
            user=request.user
        ).exclude(embedding__isnull=True).count(),
        'memory_types': {},
        'topics': [],
        'recent_additions': 0,
        'quality_metrics': {}
    }
    
    # Get memory type distribution
    type_dist = UnifiedMemoryEntry.objects.filter(
        user=request.user
    ).values('content_type').annotate(count=Count('id'))
    
    for item in type_dist:
        summary['memory_types'][item['content_type']] = item['count']
    
    # Get top topics
    topics = UnifiedMemoryEntry.objects.filter(
        user=request.user,
        topics__isnull=False
    ).values_list('topics', flat=True)[:100]
    
    topic_count = {}
    for topic_list in topics:
        if topic_list:
            for topic in topic_list:
                topic_count[topic] = topic_count.get(topic, 0) + 1
    
    summary['topics'] = sorted([
        {'name': k, 'count': v} 
        for k, v in topic_count.items()
    ], key=lambda x: x['count'], reverse=True)[:10]
    
    # Recent additions (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    summary['recent_additions'] = UnifiedMemoryEntry.objects.filter(
        user=request.user,
        created_at__gte=week_ago
    ).count()
    
    # Quality metrics
    quality = UnifiedMemoryEntry.objects.filter(
        user=request.user
    ).aggregate(
        avg_quality=Avg('quality_score'),
        avg_importance=Avg('importance_score'),
        avg_confidence=Avg('confidence_score')
    )
    
    summary['quality_metrics'] = {
        'avg_quality': quality['avg_quality'] or 0,
        'avg_importance': quality['avg_importance'] or 0,
        'avg_confidence': quality['avg_confidence'] or 0
    }
    
    return Response(summary)
```

#### Step 4: Create Insights Endpoints

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def insights_recent(request):
    """Get recent insights"""
    limit = int(request.GET.get('limit', 5))
    
    # Get recent high-value memories and patterns
    from shared_memory.models import UnifiedMemoryEntry
    from ai_partner.models import LearningPattern
    
    insights = []
    
    # Recent high-importance memories
    recent_memories = UnifiedMemoryEntry.objects.filter(
        user=request.user,
        importance_score__gte=0.7
    ).order_by('-created_at')[:limit]
    
    for memory in recent_memories:
        insights.append({
            'id': str(memory.id),
            'type': 'memory',
            'title': memory.title or 'Untitled Memory',
            'summary': memory.summary or memory.content_text[:100],
            'importance': memory.importance_score,
            'created_at': memory.created_at,
            'category': memory.content_type
        })
    
    # Recent patterns (if the model exists)
    try:
        patterns = LearningPattern.objects.filter(
            user=request.user
        ).order_by('-discovered_at')[:limit]
        
        for pattern in patterns:
            insights.append({
                'id': str(pattern.id),
                'type': 'pattern',
                'title': pattern.pattern_name,
                'summary': pattern.description,
                'confidence': pattern.confidence_score,
                'created_at': pattern.discovered_at,
                'category': pattern.pattern_type
            })
    except:
        # LearningPattern model might not exist
        pass
    
    # Sort by creation date and limit
    insights.sort(key=lambda x: x['created_at'], reverse=True)
    insights = insights[:limit]
    
    return Response({
        'count': len(insights),
        'insights': insights
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def insights_summary(request):
    """Get insights summary for timeframe"""
    timeframe = request.GET.get('timeframe', '7d')
    
    days = {
        '24h': 1,
        '7d': 7,
        '30d': 30,
        '90d': 90
    }.get(timeframe, 7)
    
    start_date = timezone.now() - timedelta(days=days)
    
    from shared_memory.models import UnifiedMemoryEntry
    
    # Calculate insights metrics
    memories_in_period = UnifiedMemoryEntry.objects.filter(
        user=request.user,
        created_at__gte=start_date
    )
    
    summary = {
        'timeframe': timeframe,
        'total_insights': memories_in_period.count(),
        'high_value_insights': memories_in_period.filter(
            importance_score__gte=0.7
        ).count(),
        'categories': {},
        'growth_rate': 0,
        'quality_trend': [],
        'top_topics': []
    }
    
    # Category distribution
    cat_dist = memories_in_period.values('content_type').annotate(
        count=Count('id')
    )
    for item in cat_dist:
        summary['categories'][item['content_type']] = item['count']
    
    # Calculate growth rate
    previous_period = UnifiedMemoryEntry.objects.filter(
        user=request.user,
        created_at__gte=start_date - timedelta(days=days),
        created_at__lt=start_date
    ).count()
    
    if previous_period > 0:
        summary['growth_rate'] = ((memories_in_period.count() - previous_period) / previous_period) * 100
    
    # Quality trend (simplified)
    for i in range(min(7, days)):
        date = timezone.now() - timedelta(days=i)
        day_quality = memories_in_period.filter(
            created_at__date=date.date()
        ).aggregate(avg=Avg('quality_score'))
        
        summary['quality_trend'].append({
            'date': date.strftime('%Y-%m-%d'),
            'quality': day_quality['avg'] or 0
        })
    
    return Response(summary)
```

#### Step 5: Update URL Configuration

```python
# In backend/ai_partner/urls.py

from django.urls import path
from . import views_phase6_ux  # or wherever you put the views

urlpatterns = [
    # ... existing patterns ...
    
    # Performance endpoints
    path('performance/summary/', views_phase6_ux.performance_summary, name='performance-summary'),
    path('performance/metrics/', views_phase6_ux.performance_metrics, name='performance-metrics'),
    
    # Agent endpoints
    path('agents/active/', views_phase6_ux.active_agents, name='active-agents'),
    
    # Knowledge endpoints
    path('knowledge/summary/', views_phase6_ux.knowledge_summary, name='knowledge-summary'),
    path('knowledge/graph/', views_phase6_ux.knowledge_graph, name='knowledge-graph'),  # Already exists
    
    # Insights endpoints
    path('insights/recent/', views_phase6_ux.insights_recent, name='insights-recent'),
    path('insights/summary/', views_phase6_ux.insights_summary, name='insights-summary'),
]
```

### Solution 2: Fix WebSocket Routing

**Priority**: HIGH  
**Estimated Time**: 1 hour

#### Step 1: Create Memory WebSocket Consumer

```python
# In backend/ai_partner/consumers_memory.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class MemoryConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time memory updates"""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'memory_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to memory updates'
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            # Handle subscription to specific memory types
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'filters': data.get('filters', [])
            }))
        elif message_type == 'ping':
            # Respond to ping
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))
    
    async def memory_update(self, event):
        """Send memory update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'memory_update',
            'memory': event['memory']
        }))
    
    async def memory_created(self, event):
        """Send new memory notification"""
        await self.send(text_data=json.dumps({
            'type': 'memory_created',
            'memory': event['memory']
        }))
    
    async def memory_deleted(self, event):
        """Send memory deletion notification"""
        await self.send(text_data=json.dumps({
            'type': 'memory_deleted',
            'memory_id': event['memory_id']
        }))
```

#### Step 2: Update WebSocket Routing

```python
# In backend/ai_partner/routing.py (create if doesn't exist)

from django.urls import re_path
from . import consumers_memory

websocket_urlpatterns = [
    re_path(r'ws/memory/(?P<user_id>\d+)/$', consumers_memory.MemoryConsumer.as_asgi()),
]
```

#### Step 3: Update Main Routing Configuration

```python
# In backend/server/routing.py or backend/server/asgi.py

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
import ai_partner.routing
import agent_orchestra.routing

websocket_urlpatterns = [
    # Existing patterns
    *agent_orchestra.routing.websocket_urlpatterns,
    
    # Add AI Partner patterns
    *ai_partner.routing.websocket_urlpatterns,
]

# Or if using path-based routing:
websocket_urlpatterns = [
    re_path(r'ws/memory/(?P<user_id>\d+)/$', ai_partner.consumers_memory.MemoryConsumer.as_asgi()),
    # ... other patterns
]
```

### Solution 3: Fix Performance Metrics 500 Error

**Priority**: HIGH  
**Estimated Time**: 30 minutes

#### Step 1: Debug the Existing Endpoint

```python
# In backend/ai_partner/views_phase6_ux.py or similar

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_metrics(request):
    """Get detailed performance metrics"""
    try:
        timeframe = request.GET.get('timeframe', '7d')
        
        # Add error handling and logging
        import logging
        logger = logging.getLogger(__name__)
        
        days = {
            '24h': 1,
            '7d': 7,
            '30d': 30,
            '90d': 90
        }.get(timeframe, 7)
        
        start_date = timezone.now() - timedelta(days=days)
        
        from agent_orchestra.models import AgentInstance
        from shared_memory.models import UnifiedMemoryEntry
        
        # Safely get metrics with defaults
        metrics = {
            'response_times': [],
            'success_rates': [],
            'throughput': [],
            'memory_usage': [],
            'error_rates': []
        }
        
        # Generate daily metrics
        for i in range(days):
            date = timezone.now() - timedelta(days=i)
            
            # Get agent metrics for the day
            day_agents = AgentInstance.objects.filter(
                user=request.user,
                created_at__date=date.date()
            )
            
            total = day_agents.count()
            completed = day_agents.filter(current_status='completed').count()
            failed = day_agents.filter(current_status='failed').count()
            
            # Calculate safely with defaults
            success_rate = (completed / max(1, total)) * 100 if total > 0 else 0
            error_rate = (failed / max(1, total)) * 100 if total > 0 else 0
            
            # Get average response time (use a default field or calculate)
            avg_time = day_agents.aggregate(
                avg_time=Avg('progress_percentage')  # Temporary field
            )['avg_time'] or 0
            
            metrics['response_times'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': avg_time
            })
            
            metrics['success_rates'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': success_rate
            })
            
            metrics['throughput'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': total
            })
            
            metrics['error_rates'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': error_rate
            })
            
            # Memory usage (simplified)
            day_memories = UnifiedMemoryEntry.objects.filter(
                user=request.user,
                created_at__date=date.date()
            ).count()
            
            metrics['memory_usage'].append({
                'date': date.strftime('%Y-%m-%d'),
                'value': day_memories
            })
        
        return Response({
            'timeframe': timeframe,
            'metrics': metrics
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Performance metrics error: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Return a safe default response
        return Response({
            'timeframe': timeframe,
            'metrics': {
                'response_times': [],
                'success_rates': [],
                'throughput': [],
                'memory_usage': [],
                'error_rates': []
            },
            'error': 'Unable to calculate metrics'
        }, status=200)  # Return 200 with error flag instead of 500
```

### Solution 4: Frontend Fixes

**Priority**: MEDIUM  
**Estimated Time**: 1 hour

#### Update API Hooks to Handle Errors Gracefully

```typescript
// In donkey-betz-frontend/src/features/ai-agent/hooks/usePerformanceMetrics.ts

export const usePerformanceMetrics = (userId: number, timeframe: string) => {
  return useQuery({
    queryKey: ['performance-metrics', userId, timeframe],
    queryFn: async () => {
      try {
        const response = await api.get(`/api/ai-partner/performance/metrics/`, {
          params: { timeframe }
        });
        return response.data;
      } catch (error) {
        console.error('Performance metrics error:', error);
        // Return default data structure
        return {
          timeframe,
          metrics: {
            response_times: [],
            success_rates: [],
            throughput: [],
            memory_usage: [],
            error_rates: []
          },
          error: true
        };
      }
    },
    retry: 1,
    retryDelay: 1000,
    staleTime: 60000, // 1 minute
  });
};
```

### Solution 5: Apply Universal Styling to AI Insights Components

**Priority**: MEDIUM-HIGH  
**Estimated Time**: 2 hours

#### Step 1: Import and Use Universal Styling Context

```typescript
// In each component (MemoryTimeline.tsx, LearningInsightsDashboard.tsx, etc.)

import React from 'react';
import { useUniversalStyling } from '../../contexts/UniversalStylingContext';

const MemoryTimeline: React.FC<MemoryTimelineProps> = ({ userId, limit, filterType }) => {
  const { styles, theme, accessibility } = useUniversalStyling();
  
  // Replace inline styles with universal styles
  return (
    <div style={styles.containers.primary}>
      <div style={styles.headers.section}>
        <h2 style={styles.text.h2}>Memory Timeline</h2>
      </div>
      {/* ... rest of component */}
    </div>
  );
};
```

#### Step 2: Replace Custom Styling Patterns

```typescript
// Before (custom styles)
const cardStyle = {
  backgroundColor: '#ffffff',
  borderRadius: '8px',
  padding: '16px',
  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
};

// After (universal styles)
const cardStyle = {
  ...styles.cards.default,
  ...(theme === 'dark' && styles.cards.dark)
};
```

#### Step 3: Update Chart Components for Theme Support

```typescript
// In LearningInsightsDashboard.tsx and PerformanceMetrics.tsx

const chartColors = {
  primary: theme === 'dark' ? '#60a5fa' : '#3b82f6',
  secondary: theme === 'dark' ? '#34d399' : '#10b981',
  accent: theme === 'dark' ? '#f59e0b' : '#f97316',
  text: theme === 'dark' ? '#e5e7eb' : '#374151',
  grid: theme === 'dark' ? '#374151' : '#e5e7eb'
};

// Apply to Recharts components
<LineChart>
  <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
  <XAxis stroke={chartColors.text} />
  <YAxis stroke={chartColors.text} />
  <Line type="monotone" dataKey="value" stroke={chartColors.primary} />
</LineChart>
```

#### Step 4: Implement Accessibility Features

```typescript
// Add accessibility support in components

const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({ resultId, onClose }) => {
  const { styles, accessibility } = useUniversalStyling();
  
  return (
    <div 
      style={{
        ...styles.modals.default,
        fontSize: accessibility.fontSize,
        ...(accessibility.highContrast && styles.accessibility.highContrast)
      }}
      role="dialog"
      aria-label="Feedback Widget"
    >
      <button
        style={{
          ...styles.buttons.primary,
          ...(accessibility.reducedMotion && { transition: 'none' })
        }}
        aria-label="Submit feedback"
      >
        Submit
      </button>
    </div>
  );
};
```

#### Step 5: Update Knowledge Graph Explorer with Theme Support

```typescript
// In KnowledgeGraphExplorer.tsx

useEffect(() => {
  if (!svgRef.current) return;
  
  const svg = d3.select(svgRef.current);
  
  // Apply theme-aware colors
  const nodeColor = theme === 'dark' ? '#60a5fa' : '#3b82f6';
  const linkColor = theme === 'dark' ? '#4b5563' : '#d1d5db';
  const textColor = theme === 'dark' ? '#e5e7eb' : '#374151';
  const backgroundColor = theme === 'dark' ? '#1f2937' : '#ffffff';
  
  svg.style('background-color', backgroundColor);
  
  // Update D3 visualizations with theme colors
  svg.selectAll('.node')
    .style('fill', nodeColor);
    
  svg.selectAll('.link')
    .style('stroke', linkColor);
    
  svg.selectAll('text')
    .style('fill', textColor);
}, [theme, data]);
```

#### Step 6: Create Styled Component Wrappers

```typescript
// Create a styled wrapper for consistent styling
// In src/features/ai-agent/components/StyledDashboardCard.tsx

import React from 'react';
import { useUniversalStyling } from '../../../contexts/UniversalStylingContext';

interface StyledDashboardCardProps {
  title: string;
  children: React.ReactNode;
  actions?: React.ReactNode;
  loading?: boolean;
  error?: string;
}

export const StyledDashboardCard: React.FC<StyledDashboardCardProps> = ({
  title,
  children,
  actions,
  loading,
  error
}) => {
  const { styles, theme } = useUniversalStyling();
  
  return (
    <div style={styles.cards.elevated}>
      <div style={styles.cards.header}>
        <h3 style={styles.text.h3}>{title}</h3>
        {actions && <div style={styles.flexbox.row}>{actions}</div>}
      </div>
      <div style={styles.cards.body}>
        {loading && (
          <div style={styles.loading.container}>
            <div style={styles.loading.spinner} />
          </div>
        )}
        {error && (
          <div style={styles.alerts.error}>
            {error}
          </div>
        )}
        {!loading && !error && children}
      </div>
    </div>
  );
};
```

#### Step 7: Update All Components to Use Styled Wrappers

```typescript
// Example update for PerformanceMetrics.tsx

import { StyledDashboardCard } from './components/StyledDashboardCard';

const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ userId, timeframe }) => {
  const { data, isLoading, error } = usePerformanceMetrics(userId, timeframe);
  const { styles, theme } = useUniversalStyling();
  
  return (
    <StyledDashboardCard
      title="Performance Metrics"
      loading={isLoading}
      error={error?.message}
      actions={
        <select style={styles.forms.select} value={timeframe} onChange={handleTimeframeChange}>
          <option value="24h">Last 24 Hours</option>
          <option value="7d">Last 7 Days</option>
          <option value="30d">Last 30 Days</option>
        </select>
      }
    >
      {/* Chart content here */}
    </StyledDashboardCard>
  );
};
```

#### Step 8: Update AIInsights Page Container

```typescript
// In src/pages/AIInsights.tsx

import { useUniversalStyling } from '../contexts/UniversalStylingContext';

const AIInsights: React.FC = () => {
  const { styles, theme } = useUniversalStyling();
  
  return (
    <div style={styles.pages.default}>
      <header style={styles.headers.page}>
        <h1 style={styles.text.h1}>AI Insights Dashboard</h1>
      </header>
      
      <Tab.Group>
        <Tab.List style={styles.tabs.container}>
          {tabs.map((tab) => (
            <Tab
              key={tab.name}
              style={({ selected }) => ({
                ...styles.tabs.tab,
                ...(selected ? styles.tabs.active : styles.tabs.inactive)
              })}
            >
              {tab.name}
            </Tab>
          ))}
        </Tab.List>
        
        <Tab.Panels style={styles.containers.content}>
          {/* Tab content here */}
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};
```

## Testing Checklist

### API Endpoint Testing
- [ ] Test `/api/ai-partner/performance/summary/` with different timeframes
- [ ] Test `/api/ai-partner/agents/active/` with active and inactive agents
- [ ] Test `/api/ai-partner/knowledge/summary/` with and without memories
- [ ] Test `/api/ai-partner/insights/recent/` with different limits
- [ ] Test `/api/ai-partner/insights/summary/` with different timeframes
- [ ] Test `/api/ai-partner/performance/metrics/` error handling

### WebSocket Testing
- [ ] Test WebSocket connection at `/ws/memory/{user_id}/`
- [ ] Test real-time memory updates
- [ ] Test reconnection logic
- [ ] Test with multiple concurrent connections

### Integration Testing
- [ ] Load AI Insights page and verify no 404 errors
- [ ] Verify all widgets display data
- [ ] Test real-time updates in MemoryTimeline
- [ ] Test performance charts rendering
- [ ] Test error states and loading states

### Universal Styling Testing
- [ ] Verify all components use universal styling context
- [ ] Test theme switching (light/dark mode) across all components
- [ ] Verify accessibility features (high contrast, font scaling)
- [ ] Check for consistent visual appearance
- [ ] Test responsive behavior on different screen sizes
- [ ] Verify chart colors update with theme changes
- [ ] Test D3 graph visualization theme compatibility

## Implementation Priority

1. **IMMEDIATE (Fix Breaking Issues)**
   - Implement all 5 missing API endpoints
   - Fix performance metrics 500 error
   
2. **HIGH (Restore Functionality)**
   - Add WebSocket routing for memory updates
   - Update frontend error handling
   - Apply universal styling to all AI Insights components
   
3. **MEDIUM (Improve Experience)**
   - Complete universal styling integration with accessibility features
   - Add caching to expensive endpoints
   - Implement pagination where needed
   - Add comprehensive error messages
   - Ensure theme consistency across charts and visualizations
   
4. **LOW (Polish)**
   - Add unit tests for new endpoints
   - Add API documentation
   - Add performance monitoring

## Monitoring Setup

### Add Logging
```python
import logging
logger = logging.getLogger('ai_insights')

# In each endpoint
logger.info(f"Performance summary requested: user={request.user.id}, timeframe={timeframe}")
```

### Add Metrics Collection
```python
# Track endpoint usage
from django.core.cache import cache

def track_endpoint_usage(endpoint_name, user_id):
    key = f"endpoint_usage:{endpoint_name}:{user_id}"
    cache.incr(key, 1)
    
# In each view
track_endpoint_usage('performance_summary', request.user.id)
```

## Prevention Measures

1. **API Contract Testing**: Create tests that verify frontend expectations match backend implementations
2. **API Documentation**: Use Django REST Swagger or similar to document all endpoints
3. **Frontend Mocking**: Add mock data fallbacks when endpoints fail
4. **Health Checks**: Add endpoint health monitoring to catch issues early
5. **Development Process**: Ensure frontend and backend are developed in sync

## Conclusion

The AI Insights Dashboard has significant integration issues stemming from:
1. **Incomplete Phase 6 Implementation**: Frontend expects endpoints that were never created
2. **Missing WebSocket Routes**: Real-time features were designed but not connected
3. **Error Handling**: Existing endpoints lack proper error handling
4. **Styling Inconsistency**: Components not using the universal styling system

The solutions provided will:
- Create all missing endpoints with proper data structures
- Enable real-time updates via WebSocket
- Add comprehensive error handling
- Apply universal styling for consistency and accessibility
- Improve the overall reliability and user experience of the dashboard

Estimated total implementation time: 6-7 hours for all critical fixes (including 2 hours for universal styling integration).