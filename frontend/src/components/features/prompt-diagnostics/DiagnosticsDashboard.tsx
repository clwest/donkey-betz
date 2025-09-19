/**
 * Diagnostics Dashboard Component
 * Displays analytics and insights for prompt optimization activities
 */

import { useState } from 'react';
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CurrencyDollarIcon,
  ClockIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';
import { Card } from '../../common/Card';
import { Button } from '../../common/Button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import type { DiagnosticsDashboardData } from '../../../types/promptDiagnostics.types';

interface Props {
  data: DiagnosticsDashboardData;
}

export function DiagnosticsDashboard({ data }: Props) {
  const [selectedPeriod, setSelectedPeriod] = useState<'7' | '30' | '90'>('30');

  // Process issues breakdown for chart
  const issuesChartData = data?.issues_breakdown 
    ? Object.entries(data.issues_breakdown).map(([type, count]) => ({
        name: type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: count,
        percentage: ((count / Object.values(data.issues_breakdown!).reduce((sum, val) => sum + val, 0)) * 100).toFixed(1)
      }))
    : [];

  // Colors for charts
  const chartColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16'];

  // Prompt types chart data
  const promptTypesData = data?.prompt_types?.map(item => ({
    name: item.prompt_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value: item.count
  })) || [];

  return (
    <div className="space-y-6">
      {/* Header with Period Selector */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-foreground">Analytics Dashboard</h2>
          <p className="text-gray-600 dark:text-muted-foreground">
            Performance insights for your prompt optimization activities
          </p>
        </div>
        
        <div className="flex space-x-2">
          {['7', '30', '90'].map((period) => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedPeriod(period as any)}
            >
              {period} days
            </Button>
          ))}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4 flex-1">
              <h3 className="text-sm font-medium text-muted-foreground dark:text-muted-foreground">Total Analyses</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-foreground">
                {(data?.overview?.total_analyses || 0).toLocaleString()}
              </p>
              <div className="flex items-center mt-1">
                <span className="text-green-600 dark:text-green-500 flex items-center text-sm">
                  <ArrowTrendingUpIcon className="h-4 w-4 mr-1" />
                  {(data?.overview?.success_rate || 0).toFixed(1)}% success
                </span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4 flex-1">
              <h3 className="text-sm font-medium text-muted-foreground dark:text-muted-foreground">Token Savings</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-foreground">
                {(data?.overview?.total_token_savings || 0).toLocaleString()}
              </p>
              <div className="flex items-center mt-1">
                <span className="text-green-600 dark:text-green-500 flex items-center text-sm">
                  <ArrowTrendingDownIcon className="h-4 w-4 mr-1" />
                  {data?.performance_metrics?.cost_savings_estimate || '$0'}
                </span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ArrowTrendingUpIcon className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-4 flex-1">
              <h3 className="text-sm font-medium text-muted-foreground dark:text-muted-foreground">Avg Efficiency</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-foreground">
                {(data?.overview?.avg_token_reduction || 0).toFixed(1)}%
              </p>
              <div className="flex items-center mt-1">
                <span className="text-purple-600 dark:text-purple-400 text-sm">
                  {data?.performance_metrics?.efficiency_gain || '0%'} improvement
                </span>
              </div>
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-4 flex-1">
              <h3 className="text-sm font-medium text-muted-foreground dark:text-muted-foreground">Templates Created</h3>
              <p className="text-2xl font-bold text-gray-900 dark:text-foreground">
                {data?.overview?.templates_created || 0}
              </p>
              <div className="flex items-center mt-1">
                <span className={`text-sm ${
                  data?.performance_metrics?.quality_improvement === 'High' ? 'text-green-600 dark:text-green-500' :
                  data?.performance_metrics?.quality_improvement === 'Medium' ? 'text-yellow-600 dark:text-yellow-500' :
                  'text-red-600 dark:text-red-500'
                }`}>
                  {data?.performance_metrics?.quality_improvement || 'Unknown'} quality
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Issues Breakdown */}
        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2 text-orange-500" />
            Issues Detected
          </h3>
          {issuesChartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={issuesChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {issuesChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-muted-foreground dark:text-muted-foreground">
              <div className="text-center">
                <CheckCircleIcon className="h-12 w-12 mx-auto mb-2 text-green-500" />
                <p>No issues detected</p>
              </div>
            </div>
          )}
        </Card>

        {/* Prompt Types Distribution */}
        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <ChartBarIcon className="h-5 w-5 mr-2 text-blue-500" />
            Prompt Types
          </h3>
          {promptTypesData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={promptTypesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-muted-foreground dark:text-muted-foreground">
              <div className="text-center">
                <InformationCircleIcon className="h-12 w-12 mx-auto mb-2" />
                <p>No data available</p>
              </div>
            </div>
          )}
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-foreground mb-4 flex items-center">
          <ClockIcon className="h-5 w-5 mr-2 text-muted-foreground" />
          Recent Analyses
        </h3>
        
        {data?.recent_analyses?.length > 0 ? (
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-background/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Analysis
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Token Reduction
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="bg-card/20 divide-y divide-white/10">
                {data?.recent_analyses?.map((analysis) => (
                  <tr key={analysis.id} className="hover:bg-dark-700/30">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-foreground">
                        {analysis.title}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        analysis.status === 'completed' 
                          ? 'bg-green-500/20 text-green-300'
                          : analysis.status === 'analyzing'
                          ? 'bg-yellow-500/20 text-yellow-300'
                          : 'bg-red-500/20 text-red-300'
                      }`}>
                        {analysis.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900 dark:text-foreground">
                        {analysis.token_reduction_percentage ? (
                          <span className="text-green-600 dark:text-green-500 font-medium">
                            -{analysis.token_reduction_percentage.toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {new Date(analysis.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8">
            <ClockIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground dark:text-muted-foreground">No recent analyses</p>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground mt-1">
              Start analyzing prompts to see your activity here
            </p>
          </div>
        )}
      </Card>

      {/* Performance Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="text-center">
            <CurrencyDollarIcon className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 dark:text-foreground mb-2">
              Cost Savings
            </h4>
            <p className="text-3xl font-bold text-green-600 dark:text-green-500 mb-2">
              {data?.performance_metrics?.cost_savings_estimate || '$0'}
            </p>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground">
              Estimated savings from token optimization
            </p>
          </div>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="text-center">
            <ArrowTrendingUpIcon className="h-12 w-12 text-blue-500 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 dark:text-foreground mb-2">
              Efficiency Gain
            </h4>
            <p className="text-3xl font-bold text-blue-600 dark:text-blue-500 mb-2">
              {data?.performance_metrics?.efficiency_gain || '0%'}
            </p>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground">
              Average token reduction across all prompts
            </p>
          </div>
        </Card>

        <Card className="p-6 bg-card/50 backdrop-blur-sm border border-white/10">
          <div className="text-center">
            <CheckCircleIcon className="h-12 w-12 text-purple-500 mx-auto mb-4" />
            <h4 className="text-lg font-semibold text-gray-900 dark:text-foreground mb-2">
              Quality Score
            </h4>
            <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
              {(data?.overview?.avg_clarity_score || 0).toFixed(1)}/100
            </p>
            <p className="text-sm text-muted-foreground dark:text-muted-foreground">
              Average clarity score improvement
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}