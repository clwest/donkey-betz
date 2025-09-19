import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@radix-ui/react-tabs';
import { AgentExecutionPanel } from '../../components/agents/AgentExecutionPanel';
import { WorkflowBuilder } from '../../components/orchestration/WorkflowBuilder';
import { FinanceAgentPanel } from '../../components/agents/FinanceAgentPanel';
import { useAgentOrchestraStore, useAgentOrchestraSelectors } from '../../store/agentOrchestraStore';
import { 
  BoltIcon, 
  UserGroupIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChartBarIcon,
  CurrencyDollarIcon
} from '@heroicons/react/24/outline';

export const AgentsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('execution');
  
  const {
    instances,
    orchestrations,
    fetchInstances,
    fetchOrchestrations,
    connectWebSocket,
    wsConnected
  } = useAgentOrchestraStore();

  const {
    runningInstances,
    completedInstances,
    failedInstances,
    activeOrchestrations,
    completedOrchestrations
  } = useAgentOrchestraSelectors();

  useEffect(() => {
    fetchInstances();
    fetchOrchestrations();
    
    if (!wsConnected) {
      connectWebSocket();
    }
  }, []);

  const stats = [
    {
      name: 'Running Tasks',
      value: runningInstances.length,
      icon: ClockIcon,
      color: 'text-yellow-600 bg-yellow-100',
    },
    {
      name: 'Completed Tasks',
      value: completedInstances.length,
      icon: CheckCircleIcon,
      color: 'text-green-600 bg-green-100',
    },
    {
      name: 'Failed Tasks',
      value: failedInstances.length,
      icon: XCircleIcon,
      color: 'text-red-600 bg-red-100',
    },
    {
      name: 'Active Workflows',
      value: activeOrchestrations.length,
      icon: UserGroupIcon,
      color: 'text-blue-600 bg-blue-100',
    },
  ];

  return (
    <div className="min-h-screen bg-muted/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                AI Agent Orchestra
              </h1>
              <p className="mt-2 text-gray-600">
                Execute individual agents or create multi-agent workflows
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              {wsConnected ? (
                <div className="flex items-center text-green-600">
                  <div className="h-2 w-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                  <span className="text-sm">Connected</span>
                </div>
              ) : (
                <div className="flex items-center text-red-600">
                  <div className="h-2 w-2 bg-red-500 rounded-full mr-2" />
                  <span className="text-sm">Disconnected</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white overflow-hidden shadow rounded-lg"
            >
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`p-3 rounded-full ${stat.color}`}>
                      <stat.icon className="h-6 w-6" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-muted-foreground truncate">
                        {stat.name}
                      </dt>
                      <dd className="text-2xl font-semibold text-gray-900">
                        {stat.value}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg border border-border overflow-hidden">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <div className="border-b border-border">
              <TabsList className="flex space-x-8 px-6 py-4">
                <TabsTrigger 
                  value="execution" 
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'execution' 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'text-muted-foreground hover:text-gray-700'
                  }`}
                >
                  <BoltIcon className="h-5 w-5" />
                  <span>Agent Execution</span>
                </TabsTrigger>
                
                <TabsTrigger 
                  value="workflows" 
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'workflows' 
                      ? 'bg-purple-100 text-purple-700' 
                      : 'text-muted-foreground hover:text-gray-700'
                  }`}
                >
                  <UserGroupIcon className="h-5 w-5" />
                  <span>Workflow Builder</span>
                </TabsTrigger>
                
                <TabsTrigger 
                  value="finance" 
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'finance' 
                      ? 'bg-emerald-100 text-emerald-700' 
                      : 'text-muted-foreground hover:text-gray-700'
                  }`}
                >
                  <CurrencyDollarIcon className="h-5 w-5" />
                  <span>Finance Agent</span>
                </TabsTrigger>
                
                <TabsTrigger 
                  value="analytics" 
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    activeTab === 'analytics' 
                      ? 'bg-green-100 text-green-700' 
                      : 'text-muted-foreground hover:text-gray-700'
                  }`}
                >
                  <ChartBarIcon className="h-5 w-5" />
                  <span>Analytics</span>
                </TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="execution" className="p-6">
              <AgentExecutionPanel />
            </TabsContent>

            <TabsContent value="workflows" className="p-0">
              <div className="h-[800px]">
                <WorkflowBuilder />
              </div>
            </TabsContent>

            <TabsContent value="finance" className="p-6">
              <FinanceAgentPanel />
            </TabsContent>

            <TabsContent value="analytics" className="p-6">
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  Agent Performance Analytics
                </h3>
                
                {/* Performance Overview */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                    <h4 className="text-lg font-medium text-blue-900 mb-4">
                      Total Executions
                    </h4>
                    <div className="text-3xl font-bold text-blue-700">
                      {instances.length}
                    </div>
                    <p className="text-sm text-blue-600 mt-2">
                      All time agent executions
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                    <h4 className="text-lg font-medium text-green-900 mb-4">
                      Success Rate
                    </h4>
                    <div className="text-3xl font-bold text-green-700">
                      {instances.length > 0 
                        ? Math.round((completedInstances.length / instances.length) * 100)
                        : 0
                      }%
                    </div>
                    <p className="text-sm text-green-600 mt-2">
                      Task completion rate
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                    <h4 className="text-lg font-medium text-purple-900 mb-4">
                      Workflows Created
                    </h4>
                    <div className="text-3xl font-bold text-purple-700">
                      {orchestrations.length}
                    </div>
                    <p className="text-sm text-purple-600 mt-2">
                      Multi-agent orchestrations
                    </p>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-muted/5 rounded-lg p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">
                    Recent Activity
                  </h4>
                  
                  {instances.length > 0 ? (
                    <div className="space-y-3">
                      {instances.slice(0, 5).map((instance) => (
                        <div
                          key={instance.id}
                          className="flex items-center justify-between bg-white rounded-lg p-4 border border-border"
                        >
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-full ${
                              instance.status === 'completed' ? 'bg-green-100' :
                              instance.status === 'processing' ? 'bg-yellow-100' :
                              instance.status === 'failed' ? 'bg-red-100' : 'bg-muted/10'
                            }`}>
                              {instance.status === 'completed' && <CheckCircleIcon className="h-4 w-4 text-green-600" />}
                              {instance.status === 'processing' && <ClockIcon className="h-4 w-4 text-yellow-600 animate-spin" />}
                              {instance.status === 'failed' && <XCircleIcon className="h-4 w-4 text-red-600" />}
                              {instance.status === 'pending' && <ClockIcon className="h-4 w-4 text-gray-600" />}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">
                                {instance.template.name}
                              </p>
                              <p className="text-sm text-gray-600 truncate max-w-md">
                                {instance.task_description}
                              </p>
                            </div>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {new Date(instance.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <ChartBarIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">No activity data available</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Execute some agents to see analytics here
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};