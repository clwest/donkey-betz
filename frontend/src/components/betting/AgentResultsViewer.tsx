/**
 * Agent Results Viewer - Display comprehensive agent analysis reports
 * 
 * Shows the actual output from agent executions including:
 * - Full agent analysis text
 * - Tool calculations and results
 * - Recommendations and insights
 * - Execution metadata
 */

import React, { useState, useEffect } from 'react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../common/Tabs';
import { 
  FileText, 
  Calculator, 
  TrendingUp, 
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Download,
  Eye,
  EyeOff,
  Copy,
  Bot,
  Zap,
  DollarSign,
  Target
} from 'lucide-react';
import { toast } from 'sonner';
import { agentOrchestraService } from '../../services/agent-orchestra.service';

interface AgentExecution {
  id: string;
  execution_id: string;
  template_name: string;
  task_description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: {
    output?: string;
    success?: boolean;
    tools_used?: string[];
    tool_results?: Record<string, any>;
    execution_time?: number;
    token_usage?: any;
  };
  output_data?: {
    response?: string;
    tools_context?: any;
    tool_calculations?: any;
  };
  llm_response?: string;
  started_at?: string;
  completed_at?: string;
  execution_time_seconds?: number;
  error_message?: string;
  progress_percentage?: number;
  current_step?: string;
}

interface AgentResultsViewerProps {
  gameId?: string;
  limit?: number;
  autoRefresh?: boolean;
  className?: string;
}

export const AgentResultsViewer: React.FC<AgentResultsViewerProps> = ({
  gameId,
  limit = 10,
  autoRefresh = true,
  className = ''
}) => {
  const [executions, setExecutions] = useState<AgentExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedExecution, setSelectedExecution] = useState<AgentExecution | null>(null);
  const [expandedResults, setExpandedResults] = useState<Set<string>>(new Set());
  const [refreshInterval, setRefreshInterval] = useState<NodeJS.Timeout | null>(null);
  const [filter, setFilter] = useState<'all' | 'completed' | 'running' | 'failed'>('all');

  // Fetch executions
  const fetchExecutions = async () => {
    try {
      const params: any = {
        limit,
        ordering: '-created_at'
      };
      
      if (gameId) {
        params.input_data__game_id = gameId;
      }
      
      if (filter !== 'all') {
        params.status = filter;
      }
      
      const response = await agentOrchestraService.getExecutions(params);
      
      if (response.success && response.data) {
        setExecutions(response.data.results || response.data);
      }
    } catch (error) {
      console.error('Failed to fetch agent executions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
    
    if (autoRefresh) {
      const interval = setInterval(fetchExecutions, 5000); // Refresh every 5 seconds
      setRefreshInterval(interval);
      
      return () => {
        if (interval) clearInterval(interval);
      };
    }
  }, [gameId, filter]);

  const toggleResultExpansion = (executionId: string) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(executionId)) {
        newSet.delete(executionId);
      } else {
        newSet.add(executionId);
      }
      return newSet;
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const downloadReport = (execution: AgentExecution) => {
    const report = formatExecutionReport(execution);
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agent-report-${execution.execution_id}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatExecutionReport = (execution: AgentExecution): string => {
    let report = `AGENT ANALYSIS REPORT
========================
Agent: ${execution.template_name}
Task: ${execution.task_description}
Status: ${execution.status}
Execution ID: ${execution.execution_id}
Time: ${execution.execution_time_seconds?.toFixed(2) || 'N/A'} seconds

`;

    if (execution.result?.output) {
      report += `ANALYSIS RESULTS:
------------------------
${execution.result.output}

`;
    }

    if (execution.result?.tool_results) {
      report += `TOOL CALCULATIONS:
------------------------
`;
      for (const [tool, data] of Object.entries(execution.result.tool_results)) {
        report += `\n${tool.toUpperCase()}:\n${JSON.stringify(data, null, 2)}\n`;
      }
    }

    if (execution.result?.tools_used?.length) {
      report += `\nTOOLS USED: ${execution.result.tools_used.join(', ')}\n`;
    }

    return report;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'running':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500/30 bg-green-900/10';
      case 'running':
        return 'border-blue-500/30 bg-blue-900/10';
      case 'failed':
        return 'border-red-500/30 bg-red-900/10';
      default:
        return 'border-gray-500/30 bg-background/10';
    }
  };

  const renderToolResults = (toolResults: Record<string, any>) => {
    return (
      <div className="space-y-3">
        {Object.entries(toolResults).map(([tool, data]) => (
          <div key={tool} className="border border-bg-card/50 rounded-lg p-3">
            <h5 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
              <Calculator className="w-4 h-4 text-cyan-400" />
              {tool.replace(/_/g, ' ').toUpperCase()}
            </h5>
            
            {tool === 'kelly_calculation' && data && (
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-muted-foreground">Recommended Bet:</span>
                  <span className="ml-2 text-green-500 font-bold">
                    ${data.recommended_bet?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Kelly %:</span>
                  <span className="ml-2 text-yellow-500">
                    {data.adjusted_kelly?.toFixed(2) || '0.00'}%
                  </span>
                </div>
                {data.edge && (
                  <div>
                    <span className="text-muted-foreground">Edge:</span>
                    <span className="ml-2 text-cyan-400">
                      {(data.edge * 100).toFixed(2)}%
                    </span>
                  </div>
                )}
              </div>
            )}
            
            {tool === 'implied_probability' && data && (
              <div className="text-sm">
                <span className="text-muted-foreground">Probability:</span>
                <span className="ml-2 text-blue-500 font-bold">
                  {data.percentage || 'N/A'}
                </span>
              </div>
            )}
            
            {tool === 'expected_value' && data && (
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-muted-foreground">EV:</span>
                  <span className={`ml-2 font-bold ${data.expected_value > 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ${data.expected_value?.toFixed(2) || '0.00'}
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">ROI:</span>
                  <span className="ml-2 text-yellow-500">
                    {data.roi_percentage?.toFixed(2) || '0.00'}%
                  </span>
                </div>
              </div>
            )}
            
            {!['kelly_calculation', 'implied_probability', 'expected_value'].includes(tool) && (
              <pre className="text-xs text-muted-foreground overflow-x-auto">
                {JSON.stringify(data, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderExecutionResult = (execution: AgentExecution) => {
    const isExpanded = expandedResults.has(execution.execution_id);
    const resultText = execution.result?.output || 
                      execution.output_data?.response || 
                      execution.llm_response || 
                      'No result available';
    
    const displayText = isExpanded ? resultText : resultText.slice(0, 300);
    const needsExpansion = resultText.length > 300;
    
    return (
      <div key={execution.id || execution.execution_id} className={`border rounded-lg p-4 mb-4 transition-all ${getStatusColor(execution.status)}`}>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            {getStatusIcon(execution.status)}
            <h4 className="text-lg font-bold text-foreground">
              {execution.template_name}
            </h4>
            <Badge variant="outline" className="text-xs">
              {execution.status}
            </Badge>
            {execution.execution_time_seconds && (
              <span className="text-xs text-muted-foreground">
                {execution.execution_time_seconds.toFixed(2)}s
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => copyToClipboard(resultText)}
              className="p-2"
            >
              <Copy className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => downloadReport(execution)}
              className="p-2"
            >
              <Download className="w-4 h-4" />
            </Button>
            {needsExpansion && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => toggleResultExpansion(execution.execution_id)}
                className="p-2"
              >
                {isExpanded ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </Button>
            )}
          </div>
        </div>
        
        {/* Task Description */}
        <p className="text-sm text-muted-foreground mb-3">
          {execution.task_description}
        </p>
        
        {/* Main Result */}
        <div className="bg-black/30 rounded-lg p-3 mb-3">
          <pre className="text-sm text-muted-foreground whitespace-pre-wrap font-mono">
            {displayText}
            {!isExpanded && needsExpansion && '...'}
          </pre>
        </div>
        
        {/* Tool Results */}
        {execution.result?.tool_results && Object.keys(execution.result.tool_results).length > 0 && (
          <div className="mt-3">
            <h5 className="text-sm font-semibold text-muted-foreground mb-2 flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-500" />
              Tool Calculations
            </h5>
            {renderToolResults(execution.result.tool_results)}
          </div>
        )}
        
        {/* Tools Used */}
        {execution.result?.tools_used && execution.result.tools_used.length > 0 && (
          <div className="mt-3 flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Tools used:</span>
            {execution.result.tools_used.map(tool => (
              <Badge key={tool} variant="outline" className="text-xs">
                {tool}
              </Badge>
            ))}
          </div>
        )}
        
        {/* Error Message */}
        {execution.error_message && (
          <div className="mt-3 p-2 bg-red-900/20 border border-red-500/30 rounded">
            <p className="text-sm text-red-500">{execution.error_message}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className={`bg-card ${className}`}>
      <div className="bg-card"></div>
      
      {/* Header */}
      <div className="p-6 border-b border-bg-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-cyan-400" />
            <h2 className="text-2xl font-bold bg-card">Agent Analysis Reports</h2>
            <Badge variant="outline" className="text-sm">
              {executions.length} reports
            </Badge>
          </div>
          
          <div className="flex items-center gap-3">
            {/* Filter Tabs */}
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button
                variant={filter === 'completed' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('completed')}
              >
                Completed
              </Button>
              <Button
                variant={filter === 'running' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('running')}
              >
                Running
              </Button>
              <Button
                variant={filter === 'failed' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('failed')}
              >
                Failed
              </Button>
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={fetchExecutions}
              className="bg-card"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </Button>
          </div>
        </div>
      </div>
      
      {/* Results List */}
      <div className="p-6 max-h-[800px] overflow-y-auto bg-card">
        {loading ? (
          <div className="text-center py-12">
            <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto mb-4" />
            <p className="text-muted-foreground">Loading agent reports...</p>
          </div>
        ) : executions.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-muted-foreground">No agent reports available</p>
            <p className="text-sm text-muted-foreground mt-2">
              Deploy agents to see their analysis results here
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {executions.map(execution => renderExecutionResult(execution))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default AgentResultsViewer;