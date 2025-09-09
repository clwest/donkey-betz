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
      name: 'Dashboard',
      icon: ChartBarIcon,
      count: dashboardData?.overview?.total_analyses || 0,
    },
    {
      id: 'analyzer' as const,
      name: 'Analyzer',
      icon: BeakerIcon,
      count: null,
    },
    {
      id: 'history' as const,
      name: 'History',
      icon: ClockIcon,
      count: analysesData?.analyses?.length || 0,
    },
    {
      id: 'templates' as const,
      name: 'Templates',
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
    <div className="min-h-screen bg-dark-900">
      {/* Header */}
      <div className="glass border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Prompt Diagnostics
              </h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Analyze, optimize, and manage your AI prompts for better performance
              </p>
            </div>
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={() => setActiveTab('templates')}
                className="flex items-center"
              >
                <DocumentTextIcon className="h-4 w-4 mr-2" />
                Templates
              </Button>
              <Button
                onClick={() => setActiveTab('analyzer')}
                className="flex items-center"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                New Analysis
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="glass border-b border-white/10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    flex items-center py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600'
                    }
                  `}
                >
                  <Icon className="h-5 w-5 mr-2" />
                  {tab.name}
                  {tab.count !== null && (
                    <span className={`
                      ml-2 py-0.5 px-2 rounded-full text-xs font-medium
                      ${activeTab === tab.id
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-200'
                        : 'bg-dark-700 text-gray-400'
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
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Failed to load dashboard
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
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

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            {/* Search Bar */}
            <Card className="p-4">
              <div className="flex items-center space-x-4">
                <div className="flex-1 relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search analyses..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 bg-dark-800 border border-dark-600 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-white placeholder-gray-400"
                  />
                </div>
                <Button variant="outline">Filter</Button>
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
                  <Card key={analysis.id} className="p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {getStatusIcon(analysis.status)}
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            {analysis.title}
                          </h3>
                          <span className="px-2 py-1 text-xs font-medium bg-dark-700 text-gray-400 rounded">
                            {analysis.prompt_type}
                          </span>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Token Reduction</p>
                            <p className="text-lg font-medium text-green-600 dark:text-green-400">
                              {analysis.token_reduction_percentage?.toFixed(1)}%
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Clarity Score</p>
                            <p className="text-lg font-medium text-blue-600 dark:text-blue-400">
                              {analysis.clarity_score?.toFixed(1)}/100
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Issues Found</p>
                            <p className="text-lg font-medium text-orange-600 dark:text-orange-400">
                              {analysis.issues_count}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Quick Wins</p>
                            <p className="text-lg font-medium text-purple-600 dark:text-purple-400">
                              {analysis.quick_wins_count}
                            </p>
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
                          Created {new Date(analysis.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      
                      <div className="flex flex-col space-y-2 ml-4">
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                        <Button variant="outline" size="sm">
                          Create Template
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