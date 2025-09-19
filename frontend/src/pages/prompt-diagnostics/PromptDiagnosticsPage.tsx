/**
 * Main Prompt Diagnostics Page
 * Provides access to prompt analysis, optimization, and management tools
 */

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  BeakerIcon, 
  ChartBarIcon, 
  DocumentTextIcon, 
  LightBulbIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import EmptyState from '../../components/common/EmptyState';
import { PromptAnalyzer } from '../../components/features/prompt-diagnostics/PromptAnalyzer';
import { DiagnosticsDashboard } from '../../components/features/prompt-diagnostics/DiagnosticsDashboard';
import { TemplateLibrary } from '../../components/features/prompt-diagnostics/TemplateLibrary';
import { promptDiagnosticsService } from '../../services/promptDiagnostics.service';
import type { PromptAnalysisSummary, DiagnosticsDashboardData } from '../../types/promptDiagnostics.types';

type TabType = 'dashboard' | 'analyzer' | 'history' | 'templates';

export default function PromptDiagnosticsPage() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useQuery({
    queryKey: ['prompt-diagnostics-dashboard'],
    queryFn: () => promptDiagnosticsService.getDashboardData(30),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Fetch recent analyses
  const { data: analysesData, isLoading: analysesLoading, refetch: refetchAnalyses } = useQuery({
    queryKey: ['prompt-analyses', searchQuery],
    queryFn: () => promptDiagnosticsService.listAnalyses({
      limit: 20,
      offset: 0,
    }),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const tabs = [
    {
      id: 'dashboard' as const,
      name: 'NEURAL MATRIX',
      icon: ChartBarIcon,
      count: dashboardData?.overview?.total_analyses || 0,
    },
    {
      id: 'analyzer' as const,
      name: 'SCANNER',
      icon: BeakerIcon,
      count: null,
    },
    {
      id: 'history' as const,
      name: 'ARCHIVES',
      icon: ClockIcon,
      count: analysesData?.analyses?.length || 0,
    },
    {
      id: 'templates' as const,
      name: 'PROTOCOLS',
      icon: DocumentTextIcon,
      count: dashboardData?.overview?.templates_created || 0,
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
      case 'analyzing':
        return <LoadingSpinner size="sm" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  const handleAnalysisComplete = () => {
    refetchAnalyses();
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Gaming Header */}
      <div className="border-b-2 border-purple-800/50 bg-background/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-4xl font-bold text-cyan-400 font-mono uppercase tracking-wider glow-text-sm animate-pulse-glow">
                PROMPT NEURAL SCANNER
              </h1>
              <p className="mt-1 text-lg text-purple-400 font-mono">
                {'>>>'} NEURAL DIAGNOSTICS TERMINAL • PROMPT OPTIMIZATION PROTOCOLS ACTIVE
              </p>
            </div>
            <div className="flex space-x-3">
              <Button
                onClick={() => setActiveTab('templates')}
                className="bg-background/80 border-2 border-purple-800/50 hover:border-purple-400/80 hover:shadow-lg hover:shadow-purple-500/30 text-purple-400 font-mono uppercase tracking-wider transition-all duration-300 flex items-center"
              >
                <DocumentTextIcon className="h-4 w-4 mr-2 animate-pulse" />
                TEMPLATES
              </Button>
              <Button
                onClick={() => setActiveTab('analyzer')}
                className="bg-background/80 border-2 border-cyan-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 text-cyan-400 font-mono uppercase tracking-wider transition-all duration-300 flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2 animate-pulse" />
                NEURAL SCAN
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Gaming Navigation Tabs */}
      <div className="border-b-2 border-purple-800/50 bg-background/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center py-4 px-1 border-b-2 font-mono font-medium text-sm whitespace-nowrap uppercase tracking-wider transition-all duration-300
                    ${activeTab === tab.id
                      ? 'border-cyan-400 text-cyan-400 glow-text-sm'
                      : 'border-transparent text-purple-400 hover:text-cyan-300 hover:border-cyan-600/50'
                    }
                  `}
                >
                  <Icon className={`h-5 w-5 mr-2 ${activeTab === tab.id ? 'animate-pulse' : ''}`} />
                  {tab.name}
                  {tab.count !== null && (
                    <span className={`
                      ml-2 py-0.5 px-2 rounded text-xs font-mono font-bold border
                      ${activeTab === tab.id
                        ? 'bg-cyan-900/50 text-cyan-400 border-cyan-400/50 animate-pulse'
                        : 'bg-background/50 text-purple-400 border-purple-400/50'
                      }
                    `}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {dashboardLoading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner size="lg" />
              </div>
            ) : dashboardError ? (
              <div className="text-center py-12">
                <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-foreground mb-2">
                  Failed to load dashboard
                </h3>
                <p className="text-muted-foreground dark:text-muted-foreground">
                  Please try refreshing the page
                </p>
              </div>
            ) : dashboardData ? (
              <DiagnosticsDashboard data={dashboardData} />
            ) : (
              <EmptyState
                icon={ChartBarIcon}
                title="No data available"
                description="Start analyzing prompts to see your dashboard"
                action={{
                  label: 'Analyze Your First Prompt',
                  onClick: () => setActiveTab('analyzer')
                }}
              />
            )}
          </div>
        )}

        {/* Analyzer Tab */}
        {activeTab === 'analyzer' && (
          <div className="max-w-4xl mx-auto">
            <PromptAnalyzer onAnalysisComplete={handleAnalysisComplete} />
          </div>
        )}

        {/* Archives Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            {/* Gaming Search Bar */}
            <Card className="bg-background/80 border-2 border-purple-800/50 hover:border-purple-400/80 hover:shadow-lg hover:shadow-purple-500/30 transition-all duration-300 p-4">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-cyan-400 animate-pulse" />
                  <input
                    type="text"
                    placeholder=">>> Neural archive search: analyses, protocols, diagnostics..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-black/50 border-2 border-gray-800/50 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 text-cyan-400 font-mono placeholder-purple-400/70 transition-all duration-300"
                  />
                </div>
                <Button className="bg-background/80 border-2 border-purple-800/50 hover:border-purple-400/80 hover:shadow-lg hover:shadow-purple-500/30 text-purple-400 font-mono uppercase tracking-wider transition-all duration-300">
                  FILTER
                </Button>
              </div>
            </Card>

            {/* Analyses List */}
            {analysesLoading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner size="lg" />
              </div>
            ) : analysesData?.analyses?.length ? (
              <div className="grid gap-4">
                {analysesData.analyses?.map((analysis) => (
                  <Card key={analysis.id} className="bg-background/80 border-2 border-purple-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 transition-all duration-300 p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getStatusIcon(analysis.status)}
                          <h3 className="text-lg font-bold text-cyan-400 font-mono uppercase tracking-wider">
                            {analysis.title}
                          </h3>
                          <span className="px-2 py-1 text-xs font-mono font-bold bg-purple-900/50 text-purple-400 border border-purple-400/50 rounded">
                            {analysis.prompt_type?.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div>
                            <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">Token Efficiency</p>
                            <p className="text-lg font-bold text-green-500 font-mono glow-text-sm">
                              {analysis.token_reduction_percentage?.toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">Neural Clarity</p>
                            <p className="text-lg font-bold text-blue-500 font-mono glow-text-sm">
                              {analysis.clarity_score?.toFixed(1)}/100
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">Anomalies</p>
                            <p className="text-lg font-bold text-orange-400 font-mono glow-text-sm">
                              {analysis.issues_count}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">Quick Fixes</p>
                            <p className="text-lg font-bold text-purple-400 font-mono glow-text-sm">
                              {analysis.quick_wins_count}
                            </p>
                          </div>
                        </div>
                        
                        <p className="text-sm text-purple-300 mt-3 font-mono">
                          {'>>>'} Archived: {new Date(analysis.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-4">
                        <Button 
                          size="sm"
                          className="bg-cyan-900/50 border border-cyan-400/50 text-cyan-400 hover:bg-cyan-900/80 hover:shadow-lg hover:shadow-cyan-500/30 font-mono uppercase tracking-wider transition-all duration-300"
                        >
                          ANALYZE
                        </Button>
                        <Button 
                          size="sm"
                          className="bg-purple-900/50 border border-purple-400/50 text-purple-400 hover:bg-purple-900/80 hover:shadow-lg hover:shadow-purple-500/30 font-mono uppercase tracking-wider transition-all duration-300"
                        >
                          PROTOCOL
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={ClockIcon}
                title="No analyses yet"
                description="Your prompt analyses will appear here once you start using the analyzer"
                action={{
                  label: 'Analyze Your First Prompt',
                  onClick: () => setActiveTab('analyzer')
                }}
              />
            )}
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="max-w-6xl mx-auto">
            <TemplateLibrary />
          </div>
        )}
      </div>
    </div>
  );
}