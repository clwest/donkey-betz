# 🔗 SYSTEM PROMPT: Phase 3 Result Integration - Real Data Connection

**Session**: 108+ (After migration fix and cleanup complete)  
**Priority**: High - Complete Phase 3 implementation  
**Estimated Time**: 3-4 hours  
**Prerequisites**: Migration fixes complete, Phase 2 functional with real data

## YOUR MISSION

You are a frontend-backend integration specialist. Phase 3 frontend components were created in Session 105 but are disconnected from real data due to migration issues. Now that migrations are fixed and Phase 2 is functional with real database data, complete the Phase 3 Result Integration by connecting the frontend components to live agent results.

## 📊 CURRENT STATE

### ✅ Frontend Components Ready (Session 105)
- **ResultCard.tsx**: Individual result display with markdown, syntax highlighting (355 lines)
- **ResultSummary.tsx**: Aggregated visualization with metrics (336 lines)  
- **InlineResults.tsx**: Chat integration with expandable views (436 lines)

### ✅ Backend Services Ready
- **ResultFormatter service**: Exists and functional (backend/ai_partner/services/result_formatter.py)
- **Phase 2 APIs**: Working with real data (recommendation engine, workflow orchestrator)
- **Agent Orchestra**: Fully functional agent deployment and execution
- **Database**: All Phase 2 tables exist and accessible

### 🔄 Integration Needed
- Connect frontend components to real agent result data
- Implement real-time result updates via WebSocket or polling
- Add proper error handling for live data scenarios  
- Integrate with existing chat interface
- Add result caching and performance optimization

## 🎯 SUCCESS CRITERIA

1. ✅ Phase 3 components display real agent execution results
2. ✅ Real-time updates show agent progress and completion
3. ✅ Results persist and reload correctly after page refresh  
4. ✅ Error handling works for failed/cancelled agents
5. ✅ Performance optimized for multiple concurrent agents
6. ✅ Seamless integration with existing chat interface
7. ✅ All result types supported (text, data, visualizations, files)

## 📋 INTEGRATION IMPLEMENTATION

### Step 1: Analyze Existing Backend Result System

First, understand the current result architecture:

```bash
cd /Users/donkeyking/development/donkey_betz/backend

# Examine result formatter service
cat ai_partner/services/result_formatter.py | head -50

# Check agent result models
python manage.py shell -c "
from agent_orchestra.models import AgentInstance, AgentResult
from agent_orchestra.models import TaskOrchestration

# Show recent agent results
recent_results = AgentResult.objects.order_by('-created_at')[:5]
for result in recent_results:
    print(f'AgentResult {result.id}: {result.result_type} - {result.agent.template.name if result.agent else \"No agent\"}')
    print(f'  Content: {str(result.content_json)[:100]}...')
    print(f'  Status: {result.status}, Created: {result.created_at}')
    print()

# Show recent orchestrations
recent_orches = TaskOrchestration.objects.order_by('-started_at')[:3]
for orch in recent_orches:
    print(f'Orchestration {orch.id}: {orch.overall_status}')
    print(f'  Task: {orch.master_task[:80]}...')
    agents = orch.agents.count()
    print(f'  Agents: {agents}')
    print()
"
```

### Step 2: Create Real-Time Result API Endpoints

Add new endpoints for Phase 3 result streaming:

```python
# Create backend/ai_partner/api/views_phase3.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta

from agent_orchestra.models import TaskOrchestration, AgentInstance, AgentResult
from ai_partner.services.result_formatter import ResultFormatter
from ai_partner.api.serializers_phase3 import (
    AgentResultSerializer, 
    OrchestrationStatusSerializer,
    ResultSummarySerializer
)

class ResultStreamViewSet(viewsets.ViewSet):
    """
    Phase 3: Real-time result streaming API
    
    Endpoints:
    - GET /results/orchestration/{id}/stream/ - Get real-time orchestration results
    - GET /results/orchestration/{id}/summary/ - Get result summary
    - GET /results/agent/{id}/latest/ - Get latest agent result
    - GET /results/user/recent/ - Get user's recent results
    """
    
    @action(detail=True, methods=['get'], url_path='stream')
    def orchestration_stream(self, request, pk=None):
        """Get real-time results for an orchestration"""
        orchestration = get_object_or_404(TaskOrchestration, id=pk, user=request.user)
        
        # Get all results for this orchestration
        results = AgentResult.objects.filter(
            agent__orchestration=orchestration
        ).select_related('agent', 'agent__template').order_by('-created_at')
        
        # Format results using ResultFormatter
        formatter = ResultFormatter()
        formatted_results = []
        
        for result in results:
            formatted_result = formatter.format_agent_result(
                result=result,
                include_metadata=True,
                format_type='json'
            )
            formatted_results.append(formatted_result)
        
        return Response({
            'orchestration_id': orchestration.id,
            'status': orchestration.overall_status,
            'progress': orchestration.overall_progress,
            'results': formatted_results,
            'last_updated': timezone.now(),
            'total_agents': orchestration.agents.count(),
            'completed_agents': orchestration.agents.filter(current_status='completed').count()
        })
    
    @action(detail=True, methods=['get'], url_path='summary')  
    def orchestration_summary(self, request, pk=None):
        """Get aggregated summary of orchestration results"""
        orchestration = get_object_or_404(TaskOrchestration, id=pk, user=request.user)
        
        # Calculate summary metrics
        agents = orchestration.agents.all()
        results = AgentResult.objects.filter(agent__orchestration=orchestration)
        
        summary_data = {
            'orchestration_id': orchestration.id,
            'total_agents': agents.count(),
            'status_distribution': {
                'completed': agents.filter(current_status='completed').count(),
                'working': agents.filter(current_status='working').count(),
                'failed': agents.filter(current_status='failed').count(),
                'pending': agents.filter(current_status='pending').count(),
            },
            'result_types': {},
            'performance_metrics': {
                'avg_execution_time': 0,
                'total_results': results.count(),
                'success_rate': 0
            },
            'key_insights': [],
            'generated_content': []
        }
        
        # Calculate result type distribution
        for result in results:
            result_type = result.result_type or 'unknown'
            summary_data['result_types'][result_type] = summary_data['result_types'].get(result_type, 0) + 1
        
        # Extract key insights and content
        formatter = ResultFormatter()
        summary_data['key_insights'] = formatter.extract_key_insights(results)
        summary_data['generated_content'] = formatter.get_content_summary(results)
        
        return Response(summary_data)
    
    @action(detail=True, methods=['get'], url_path='latest')
    def agent_latest(self, request, pk=None):
        """Get latest result for a specific agent"""
        agent = get_object_or_404(AgentInstance, id=pk, user=request.user)
        
        latest_result = AgentResult.objects.filter(agent=agent).order_by('-created_at').first()
        
        if not latest_result:
            return Response({'message': 'No results found for this agent'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        formatter = ResultFormatter()
        formatted_result = formatter.format_agent_result(
            result=latest_result,
            include_metadata=True,
            format_type='detailed'
        )
        
        return Response({
            'agent_id': agent.id,
            'agent_name': agent.template.name if agent.template else 'Unknown',
            'status': agent.current_status,
            'progress': agent.progress_percentage,
            'result': formatted_result,
            'last_updated': latest_result.created_at
        })
    
    @action(detail=False, methods=['get'], url_path='recent')
    def user_recent_results(self, request):
        """Get user's recent orchestration results"""
        # Get orchestrations from last 24 hours
        recent_cutoff = timezone.now() - timedelta(hours=24)
        recent_orchestrations = TaskOrchestration.objects.filter(
            user=request.user,
            started_at__gte=recent_cutoff
        ).order_by('-started_at')[:10]
        
        results_data = []
        for orchestration in recent_orchestrations:
            results_count = AgentResult.objects.filter(
                agent__orchestration=orchestration
            ).count()
            
            results_data.append({
                'orchestration_id': orchestration.id,
                'task': orchestration.master_task,
                'status': orchestration.overall_status,
                'progress': orchestration.overall_progress,
                'started_at': orchestration.started_at,
                'results_count': results_count,
                'agents_count': orchestration.agents.count()
            })
        
        return Response({
            'recent_results': results_data,
            'total_count': len(results_data),
            'last_updated': timezone.now()
        })


# Create backend/ai_partner/api/serializers_phase3.py

from rest_framework import serializers
from agent_orchestra.models import AgentResult, TaskOrchestration, AgentInstance

class AgentResultSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.template.name', read_only=True)
    formatted_content = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentResult
        fields = [
            'id', 'agent_name', 'result_type', 'status', 
            'formatted_content', 'metadata', 'created_at'
        ]
    
    def get_formatted_content(self, obj):
        from ai_partner.services.result_formatter import ResultFormatter
        formatter = ResultFormatter()
        return formatter.format_agent_result(obj, format_type='json')

class OrchestrationStatusSerializer(serializers.ModelSerializer):
    agents_count = serializers.SerializerMethodField()
    results_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskOrchestration
        fields = [
            'id', 'master_task', 'overall_status', 'overall_progress',
            'started_at', 'agents_count', 'results_count'
        ]
    
    def get_agents_count(self, obj):
        return obj.agents.count()
    
    def get_results_count(self, obj):
        return AgentResult.objects.filter(agent__orchestration=obj).count()

class ResultSummarySerializer(serializers.Serializer):
    orchestration_id = serializers.UUIDField()
    total_agents = serializers.IntegerField()
    status_distribution = serializers.DictField()
    result_types = serializers.DictField()
    performance_metrics = serializers.DictField()
    key_insights = serializers.ListField()
    generated_content = serializers.ListField()
```

### Step 3: Update Frontend Components for Real Data

#### 3A: Update ResultCard Component

```typescript
// Edit donkey-betz-frontend/src/features/ai-agent/ResultCard.tsx

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp, Copy, Download, ExternalLink } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import ReactMarkdown from 'react-markdown';
import { api } from '@/lib/api';

interface AgentResult {
  id: string;
  agent_name: string;
  result_type: string;
  status: 'completed' | 'working' | 'failed' | 'pending';
  formatted_content: {
    content: string;
    metadata: Record<string, any>;
    visualizations?: any[];
    files?: any[];
  };
  created_at: string;
}

interface ResultCardProps {
  orchestrationId: string;
  agentId?: string;
  refreshInterval?: number;
  onResultUpdate?: (result: AgentResult) => void;
}

export const ResultCard: React.FC<ResultCardProps> = ({
  orchestrationId,
  agentId,
  refreshInterval = 5000,
  onResultUpdate
}) => {
  const [results, setResults] = useState<AgentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());

  // Fetch latest results
  const fetchResults = async () => {
    try {
      const endpoint = agentId 
        ? `/ai-partner/results/agent/${agentId}/latest/`
        : `/ai-partner/results/orchestration/${orchestrationId}/stream/`;
        
      const response = await api.get(endpoint);
      
      if (agentId) {
        // Single agent result
        const newResults = [response.data.result];
        setResults(newResults);
        onResultUpdate?.(newResults[0]);
      } else {
        // Orchestration results
        setResults(response.data.results || []);
        response.data.results?.forEach(onResultUpdate);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching results:', err);
      setError('Failed to load results');
    } finally {
      setLoading(false);
    }
  };

  // Set up polling for real-time updates
  useEffect(() => {
    fetchResults();
    
    const interval = setInterval(fetchResults, refreshInterval);
    return () => clearInterval(interval);
  }, [orchestrationId, agentId, refreshInterval]);

  const toggleExpanded = (resultId: string) => {
    const newExpanded = new Set(expandedResults);
    if (newExpanded.has(resultId)) {
      newExpanded.delete(resultId);
    } else {
      newExpanded.add(resultId);
    }
    setExpandedResults(newExpanded);
  };

  const copyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content);
    // Add toast notification here
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'working': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderContent = (result: AgentResult) => {
    const { content, metadata, visualizations, files } = result.formatted_content;
    const isExpanded = expandedResults.has(result.id);

    return (
      <div className="space-y-4">
        {/* Main content */}
        <div className={`${!isExpanded ? 'line-clamp-3' : ''}`}>
          {result.result_type === 'code' ? (
            <SyntaxHighlighter
              language={metadata?.language || 'text'}
              style={oneDark}
              className="rounded-md"
            >
              {content}
            </SyntaxHighlighter>
          ) : result.result_type === 'markdown' ? (
            <ReactMarkdown className="prose prose-sm max-w-none">
              {content}
            </ReactMarkdown>
          ) : (
            <p className="text-gray-700 whitespace-pre-wrap">{content}</p>
          )}
        </div>

        {/* Visualizations */}
        {visualizations && visualizations.length > 0 && isExpanded && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900">Visualizations</h4>
            {visualizations.map((viz, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-md">
                {/* Render visualization based on type */}
                {viz.type === 'chart' && <div>Chart: {viz.title}</div>}
                {viz.type === 'image' && <img src={viz.url} alt={viz.title} className="max-w-full h-auto" />}
              </div>
            ))}
          </div>
        )}

        {/* Files */}
        {files && files.length > 0 && isExpanded && (
          <div className="space-y-2">
            <h4 className="font-medium text-gray-900">Generated Files</h4>
            {files.map((file, idx) => (
              <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded-md">
                <span className="text-sm text-gray-700">{file.name}</span>
                <div className="flex space-x-2">
                  <Button variant="ghost" size="sm" onClick={() => window.open(file.url)}>
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Metadata */}
        {metadata && Object.keys(metadata).length > 0 && isExpanded && (
          <div className="text-xs text-gray-500 space-y-1">
            {Object.entries(metadata).map(([key, value]) => (
              <div key={key}>
                <span className="font-medium">{key}:</span> {String(value)}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardContent className="p-6">
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-20 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="text-red-600">
            <p>{error}</p>
            <Button variant="outline" size="sm" onClick={fetchResults} className="mt-2">
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {results.map((result) => (
        <Card key={result.id} className="border border-gray-200">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg font-medium">
                {result.agent_name}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Badge className={getStatusColor(result.status)}>
                  {result.status}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(result.formatted_content.content)}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              {new Date(result.created_at).toLocaleString()}
            </p>
          </CardHeader>

          <CardContent>
            <Collapsible>
              <div>{renderContent(result)}</div>
              
              {result.formatted_content.content.length > 200 && (
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="mt-3 w-full"
                    onClick={() => toggleExpanded(result.id)}
                  >
                    {expandedResults.has(result.id) ? (
                      <>
                        <ChevronUp className="h-4 w-4 mr-2" />
                        Show Less
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4 mr-2" />
                        Show More
                      </>
                    )}
                  </Button>
                </CollapsibleTrigger>
              )}
            </Collapsible>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
```

#### 3B: Update ResultSummary Component

```typescript
// Edit donkey-betz-frontend/src/features/ai-agent/ResultSummary.tsx

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { CheckCircle, Clock, AlertCircle, XCircle, TrendingUp, FileText, Image, Code } from 'lucide-react';
import { api } from '@/lib/api';

interface ResultSummaryData {
  orchestration_id: string;
  total_agents: number;
  status_distribution: {
    completed: number;
    working: number;
    failed: number;
    pending: number;
  };
  result_types: Record<string, number>;
  performance_metrics: {
    avg_execution_time: number;
    total_results: number;
    success_rate: number;
  };
  key_insights: string[];
  generated_content: Array<{
    type: string;
    title: string;
    preview: string;
  }>;
}

interface ResultSummaryProps {
  orchestrationId: string;
  refreshInterval?: number;
}

export const ResultSummary: React.FC<ResultSummaryProps> = ({
  orchestrationId,
  refreshInterval = 10000
}) => {
  const [summaryData, setSummaryData] = useState<ResultSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      const response = await api.get(`/ai-partner/results/orchestration/${orchestrationId}/summary/`);
      setSummaryData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching summary:', err);
      setError('Failed to load summary');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
    const interval = setInterval(fetchSummary, refreshInterval);
    return () => clearInterval(interval);
  }, [orchestrationId, refreshInterval]);

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-3">
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !summaryData) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-6">
          <div className="text-red-600 text-center">
            <AlertCircle className="mx-auto h-12 w-12 mb-4" />
            <p>{error || 'No summary data available'}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { status_distribution, result_types, performance_metrics, key_insights, generated_content } = summaryData;

  // Prepare chart data
  const statusChartData = Object.entries(status_distribution).map(([status, count]) => ({
    name: status.charAt(0).toUpperCase() + status.slice(1),
    value: count,
    color: {
      completed: '#22c55e',
      working: '#f59e0b', 
      failed: '#ef4444',
      pending: '#6b7280'
    }[status]
  }));

  const resultTypesChartData = Object.entries(result_types).map(([type, count]) => ({
    type: type.charAt(0).toUpperCase() + type.slice(1),
    count
  }));

  const overallProgress = status_distribution.completed / summaryData.total_agents * 100;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'working': return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'failed': return <XCircle className="h-5 w-5 text-red-500" />;
      default: return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getContentIcon = (type: string) => {
    switch (type) {
      case 'text': return <FileText className="h-4 w-4" />;
      case 'image': return <Image className="h-4 w-4" />;
      case 'code': return <Code className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Overall Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="h-5 w-5 mr-2" />
            Overall Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">
                {status_distribution.completed} of {summaryData.total_agents} agents completed
              </span>
              <span className="text-sm text-gray-500">
                {Math.round(overallProgress)}%
              </span>
            </div>
            <Progress value={overallProgress} className="h-2" />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Agent Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={statusChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {statusChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(status_distribution).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(status)}
                      <span className="text-sm capitalize">{status}</span>
                    </div>
                    <Badge variant="outline">{count}</Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Result Types */}
        <Card>
          <CardHeader>
            <CardTitle>Result Types</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={resultTypesChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Performance Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {Math.round(performance_metrics.avg_execution_time)}s
              </div>
              <div className="text-sm text-blue-800">Avg Execution Time</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {performance_metrics.total_results}
              </div>
              <div className="text-sm text-green-800">Total Results</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(performance_metrics.success_rate * 100)}%
              </div>
              <div className="text-sm text-purple-800">Success Rate</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Insights */}
      {key_insights && key_insights.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {key_insights.map((insight, index) => (
                <div key={index} className="p-3 bg-yellow-50 border-l-4 border-yellow-400 rounded-r">
                  <p className="text-sm text-yellow-800">{insight}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Generated Content */}
      {generated_content && generated_content.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Generated Content</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {generated_content.map((content, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getContentIcon(content.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {content.title}
                      </h4>
                      <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                        {content.preview}
                      </p>
                      <Badge variant="outline" className="mt-2">
                        {content.type}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
```

### Step 4: Update URL Configuration

```python
# Add to backend/ai_partner/urls.py

from ai_partner.api.views_phase3 import ResultStreamViewSet

# Add to router
router.register(r'results', ResultStreamViewSet, basename='result-stream')
```

### Step 5: Integration with Chat Interface

```typescript
// Create donkey-betz-frontend/src/features/ai-agent/ChatResultIntegration.tsx

import React from 'react';
import { ResultCard } from './ResultCard';
import { ResultSummary } from './ResultSummary';
import { InlineResults } from './InlineResults';

interface ChatResultIntegrationProps {
  orchestrationId?: string;
  messageId?: string;
  showSummary?: boolean;
  compact?: boolean;
}

export const ChatResultIntegration: React.FC<ChatResultIntegrationProps> = ({
  orchestrationId,
  messageId,
  showSummary = true,
  compact = false
}) => {
  if (!orchestrationId) return null;

  return (
    <div className={`space-y-4 ${compact ? 'text-sm' : ''}`}>
      {showSummary && (
        <ResultSummary 
          orchestrationId={orchestrationId}
          refreshInterval={5000}
        />
      )}
      
      <ResultCard
        orchestrationId={orchestrationId}
        refreshInterval={3000}
        onResultUpdate={(result) => {
          // Handle real-time result updates
          console.log('New result:', result);
        }}
      />
    </div>
  );
};
```

## 🧪 TESTING AND VALIDATION

### Step 6: End-to-End Testing

```bash
# Test the complete Phase 3 integration
cd /Users/donkeyking/development/donkey_betz/backend

# 1. Start backend server
python manage.py runserver &

# 2. Deploy a test agent and capture orchestration ID
python -c "
import asyncio, sys, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from ai_partner.personal_ai_services import PersonalAIService
from django.contrib.auth import get_user_model

async def test_deployment():
    User = get_user_model()
    user = User.objects.first()
    ai_service = PersonalAIService(user)
    
    result = await ai_service.deploy_agent_magic(
        user=user,
        agent_name='Research Agent',
        original_message='Research the latest trends in AI development and create a comprehensive report'
    )
    
    orch_id = result.get('orchestration_id')
    print(f'ORCHESTRATION_ID={orch_id}')
    return orch_id

orch_id = asyncio.run(test_deployment())
" > test_orchestration_id.txt

ORCH_ID=$(cat test_orchestration_id.txt | grep ORCHESTRATION_ID | cut -d'=' -f2)

# 3. Test Phase 3 API endpoints
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/ai-partner/results/orchestration/${ORCH_ID}/stream/" | jq '.'

curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/ai-partner/results/orchestration/${ORCH_ID}/summary/" | jq '.'

# 4. Monitor results in real-time
watch -n 2 "curl -s -H 'Authorization: Bearer YOUR_TOKEN' \
           'http://localhost:8000/api/ai-partner/results/orchestration/${ORCH_ID}/stream/' | \
           jq '.results | length, .[0].status // \"no results\"'"

# 5. Start frontend and test components
cd ../donkey-betz-frontend
npm run dev &

# Open browser to test Phase 3 components
echo "Test at: http://localhost:3000/chat?test_orchestration=${ORCH_ID}"
```

### Step 7: Performance Optimization

```typescript
// Add caching and optimization to components

// In ResultCard.tsx
const RESULT_CACHE = new Map<string, AgentResult[]>();

// Add memoization
const MemoizedResultCard = React.memo(ResultCard);

// In ResultSummary.tsx  
const useSummaryCache = (orchestrationId: string) => {
  return useMemo(() => {
    // Cache summary data for 30 seconds
    const cacheKey = `summary_${orchestrationId}`;
    const cached = sessionStorage.getItem(cacheKey);
    
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp < 30000) {
        return data;
      }
    }
    
    return null;
  }, [orchestrationId]);
};
```

## ✅ COMPLETION CHECKLIST

1. ✅ **Phase 3 API endpoints created** and functional
2. ✅ **ResultCard updated** to use real agent result data
3. ✅ **ResultSummary updated** with live orchestration metrics  
4. ✅ **InlineResults integrated** with chat interface
5. ✅ **Real-time updates** via polling (WebSocket optional enhancement)
6. ✅ **Error handling** for failed agents and network issues
7. ✅ **Performance optimized** with caching and memoization
8. ✅ **End-to-end testing** validates complete workflow
9. ✅ **Documentation updated** with Phase 3 integration status

## 📈 SUCCESS METRICS

**Functional Validation:**
- Phase 3 components show real agent results instead of mock data
- Real-time updates work during agent execution  
- All result types render correctly (text, code, markdown, visualizations)
- Error states handled gracefully
- Performance remains responsive with multiple agents

**Technical Achievement:**
- No mock data remaining in Phase 3 components
- Database-backed result persistence working
- Frontend-backend integration complete
- Ready for Phase 4 (Advanced Collaboration)

## 📤 HANDOFF TO NEXT SESSION

Phase 3 Result Integration is complete when:
1. All components connect to real backend APIs
2. End-to-end testing passes for full agent workflow
3. Real-time result updates function properly
4. Error handling covers edge cases
5. Performance is optimized and responsive

**Next Phase:** Advanced Collaboration (Phase 4) - Enable agents to work together on complex multi-step tasks

---

**Remember**: Phase 3 is the bridge between individual agent capabilities (Phase 2) and collaborative workflows (Phase 4). Get this integration solid and the advanced features will build naturally on top.