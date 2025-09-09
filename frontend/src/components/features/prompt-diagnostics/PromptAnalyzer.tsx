/**
 * Prompt Analyzer Component
 * Interactive tool for analyzing and optimizing prompts
 */

import { useState, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  BeakerIcon, 
  ClipboardDocumentIcon, 
  ArrowPathIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  LightBulbIcon,
  ChartBarIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { LoadingSpinner } from '../../common/LoadingSpinner';
import { promptDiagnosticsService } from '../../../services/promptDiagnostics.service';
import toast from 'react-hot-toast';
import type { 
  PromptAnalysisRequest, 
  PromptAnalysisResult, 
  QuickAnalysisResult 
} from '../../../types/promptDiagnostics.types';

interface Props {
  onAnalysisComplete?: () => void;
}

export function PromptAnalyzer({ onAnalysisComplete }: Props) {
  const [prompt, setPrompt] = useState('');
  const [title, setTitle] = useState('');
  const [promptType, setPromptType] = useState<'user' | 'system' | 'assistant' | 'function'>('user');
  const [targetModel, setTargetModel] = useState('gpt-4');
  const [optimizationGoals, setOptimizationGoals] = useState<string[]>(['reduce_tokens', 'improve_clarity']);
  const [analysisResult, setAnalysisResult] = useState<PromptAnalysisResult | null>(null);
  const [quickAnalysis, setQuickAnalysis] = useState<QuickAnalysisResult | null>(null);
  
  const queryClient = useQueryClient();

  // Quick analysis mutation (real-time feedback)
  const quickAnalyzeMutation = useMutation({
    mutationFn: (prompt: string) => promptDiagnosticsService.quickAnalyze(prompt),
    onSuccess: (data) => {
      setQuickAnalysis(data);
    },
    onError: (error: any) => {
      console.error('Quick analysis failed:', error);
    },
  });

  // Full analysis mutation
  const analyzeMutation = useMutation({
    mutationFn: (request: PromptAnalysisRequest) => promptDiagnosticsService.analyzePrompt(request),
    onSuccess: (data) => {
      setAnalysisResult(data);
      toast.success('Prompt analysis completed successfully!');
      queryClient.invalidateQueries({ queryKey: ['prompt-diagnostics-dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['prompt-analyses'] });
      onAnalysisComplete?.();
    },
    onError: (error: any) => {
      toast.error(error.userMessage || 'Analysis failed. Please try again.');
    },
  });

  // Template creation mutation
  const createTemplateMutation = useMutation({
    mutationFn: (data: { analysis_id: string; name: string; description: string; category: string }) => 
      promptDiagnosticsService.createTemplate(data),
    onSuccess: () => {
      toast.success('Template created successfully!');
      queryClient.invalidateQueries({ queryKey: ['prompt-templates'] });
    },
    onError: (error: any) => {
      toast.error(error.userMessage || 'Failed to create template.');
    },
  });

  // Handle prompt input changes (trigger quick analysis)
  const handlePromptChange = useCallback((value: string) => {
    setPrompt(value);
    
    // Clear previous results when prompt changes
    if (value !== prompt) {
      setAnalysisResult(null);
      setQuickAnalysis(null);
    }
    
    // Trigger quick analysis for non-empty prompts
    if (value.trim().length > 10) {
      quickAnalyzeMutation.mutate(value.trim());
    }
  }, [prompt]);

  // Handle full analysis
  const handleAnalyze = () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt to analyze');
      return;
    }

    const request: PromptAnalysisRequest = {
      prompt: prompt.trim(),
      title: title.trim() || `Analysis ${new Date().toLocaleDateString()}`,
      prompt_type: promptType,
      target_model: targetModel,
      optimization_goals: optimizationGoals,
    };

    analyzeMutation.mutate(request);
  };

  // Handle template creation
  const handleCreateTemplate = () => {
    if (!analysisResult) return;

    const templateName = prompt('Enter template name:', `Optimized ${analysisResult.analysis_id}`);
    if (!templateName) return;

    const templateDescription = prompt('Enter template description:', 'Optimized prompt template');
    if (!templateDescription) return;

    createTemplateMutation.mutate({
      analysis_id: analysisResult.analysis_id,
      name: templateName,
      description: templateDescription,
      category: 'general',
    });
  };

  // Copy to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
              <BeakerIcon className="h-6 w-6 mr-2 text-blue-500" />
              Prompt Analyzer
            </h2>
            {quickAnalysis && (
              <div className="flex items-center space-x-4 text-sm">
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  promptDiagnosticsService.getComplexityColor(quickAnalysis.complexity_rating)
                }`}>
                  {quickAnalysis.complexity_rating} Complexity
                </div>
                <div className="text-gray-500 dark:text-gray-400">
                  {promptDiagnosticsService.formatTokenCount(quickAnalysis.token_count)}
                </div>
              </div>
            )}
          </div>

          {/* Configuration Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Title (optional)
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Analysis title..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Prompt Type
              </label>
              <select
                value={promptType}
                onChange={(e) => setPromptType(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="user">User Prompt</option>
                <option value="system">System Prompt</option>
                <option value="assistant">Assistant Prompt</option>
                <option value="function">Function Prompt</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Target Model
              </label>
              <select
                value={targetModel}
                onChange={(e) => setTargetModel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                <option value="claude-3">Claude 3</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Goals
              </label>
              <div className="flex flex-wrap gap-1">
                {['reduce_tokens', 'improve_clarity', 'enhance_structure', 'maintain_context'].map((goal) => (
                  <button
                    key={goal}
                    onClick={() => {
                      if (optimizationGoals.includes(goal)) {
                        setOptimizationGoals(prev => prev.filter(g => g !== goal));
                      } else {
                        setOptimizationGoals(prev => [...prev, goal]);
                      }
                    }}
                    className={`px-2 py-1 text-xs rounded-md transition-colors ${
                      optimizationGoals.includes(goal)
                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 hover:bg-gray-200'
                    }`}
                  >
                    {goal.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Prompt Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Prompt to Analyze
            </label>
            <textarea
              value={prompt}
              onChange={(e) => handlePromptChange(e.target.value)}
              placeholder="Enter your prompt here for analysis..."
              rows={8}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white resize-y"
            />
            
            {/* Quick Analysis Feedback */}
            {quickAnalysis && (
              <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-md">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Tokens:</span>
                    <span className="ml-1 font-medium">{quickAnalysis.token_count}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Readability:</span>
                    <span className="ml-1 font-medium">{quickAnalysis.readability_score.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Grade Level:</span>
                    <span className="ml-1 font-medium">{quickAnalysis.grade_level.toFixed(1)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Issues:</span>
                    <span className="ml-1 font-medium">{quickAnalysis.issues_count}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Critical:</span>
                    <span className="ml-1 font-medium text-red-600">{quickAnalysis.critical_issues}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center">
            <div className="flex space-x-3">
              <Button
                onClick={handleAnalyze}
                disabled={!prompt.trim() || analyzeMutation.isPending}
                className="flex items-center"
              >
                {analyzeMutation.isPending ? (
                  <LoadingSpinner size="sm" className="mr-2" />
                ) : (
                  <ChartBarIcon className="h-4 w-4 mr-2" />
                )}
                Analyze & Optimize
              </Button>
              
              {prompt && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setPrompt('');
                    setAnalysisResult(null);
                    setQuickAnalysis(null);
                  }}
                >
                  <ArrowPathIcon className="h-4 w-4 mr-2" />
                  Clear
                </Button>
              )}
            </div>

            {quickAnalysis?.recommendations.length > 0 && (
              <div className="text-sm text-amber-600 dark:text-amber-400 flex items-center">
                <LightBulbIcon className="h-4 w-4 mr-1" />
                {quickAnalysis.recommendations.length} recommendations available
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Results Summary */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
                <CheckCircleIcon className="h-6 w-6 mr-2 text-green-500" />
                Analysis Results
              </h3>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(analysisResult.optimized_prompt)}
                >
                  <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                  Copy Optimized
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCreateTemplate}
                  disabled={createTemplateMutation.isPending}
                >
                  <DocumentTextIcon className="h-4 w-4 mr-1" />
                  Save as Template
                </Button>
              </div>
            </div>

            {/* Metrics Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  -{analysisResult.metrics.token_reduction_percentage.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Token Reduction</div>
                <div className="text-xs text-gray-400">
                  {analysisResult.metrics.original_tokens} → {analysisResult.metrics.optimized_tokens}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {analysisResult.metrics.clarity_score.toFixed(1)}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Clarity Score</div>
                <div className="text-xs text-gray-400">/100</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {analysisResult.issues.length}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Issues Found</div>
                <div className="text-xs text-gray-400">
                  {analysisResult.issues.filter(i => i.severity === 'critical').length} critical
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {analysisResult.quick_wins.length}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">Quick Wins</div>
                <div className="text-xs text-gray-400">Available</div>
              </div>
            </div>

            {/* Prompt Comparison */}
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Original Prompt</h4>
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg text-sm">
                  <pre className="whitespace-pre-wrap font-mono">{analysisResult.original_prompt}</pre>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Optimized Prompt</h4>
                <div className="bg-green-50 dark:bg-green-900 p-4 rounded-lg text-sm">
                  <pre className="whitespace-pre-wrap font-mono">{analysisResult.optimized_prompt}</pre>
                </div>
              </div>
            </div>
          </Card>

          {/* Issues and Quick Wins */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Issues */}
            <Card className="p-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-orange-500" />
                Issues Detected ({analysisResult.issues.length})
              </h4>
              <div className="space-y-3">
                {analysisResult.issues.slice(0, 5).map((issue, index) => (
                  <div key={index} className="border-l-4 border-orange-300 pl-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        promptDiagnosticsService.getSeverityColor(issue.severity)
                      }`}>
                        {issue.severity}
                      </span>
                      <span className="text-xs text-gray-500">{issue.confidence.toFixed(1)}% confidence</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">{issue.description}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{issue.suggestion}</p>
                  </div>
                ))}
                {analysisResult.issues.length > 5 && (
                  <p className="text-sm text-gray-500 text-center">
                    +{analysisResult.issues.length - 5} more issues
                  </p>
                )}
              </div>
            </Card>

            {/* Quick Wins */}
            <Card className="p-6">
              <h4 className="font-medium text-gray-900 dark:text-white mb-4 flex items-center">
                <LightBulbIcon className="h-5 w-5 mr-2 text-green-500" />
                Quick Wins ({analysisResult.quick_wins.length})
              </h4>
              <div className="space-y-3">
                {analysisResult.quick_wins.slice(0, 5).map((win, index) => (
                  <div key={index} className="border-l-4 border-green-300 pl-4">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        promptDiagnosticsService.getPriorityColor(win.priority)
                      }`}>
                        {win.priority}
                      </span>
                      <span className="text-xs text-green-600">-{win.token_savings} tokens</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">{win.description}</p>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      <span className="font-mono bg-red-50 dark:bg-red-900 px-1">{win.before}</span>
                      {' → '}
                      <span className="font-mono bg-green-50 dark:bg-green-900 px-1">{win.after}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Implementation Notes */}
          <Card className="p-6">
            <h4 className="font-medium text-gray-900 dark:text-white mb-4 flex items-center">
              <InformationCircleIcon className="h-5 w-5 mr-2 text-blue-500" />
              Implementation Guidance
            </h4>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Summary</h5>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {analysisResult.improvements_summary}
                </p>
              </div>
              
              <div>
                <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Implementation Notes</h5>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {analysisResult.implementation_notes}
                </p>
              </div>
              
              <div>
                <h5 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Rollback Strategy</h5>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {analysisResult.rollback_strategy}
                </p>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}