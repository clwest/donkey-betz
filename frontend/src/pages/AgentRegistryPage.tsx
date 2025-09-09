import React, { useState, useEffect } from 'react';
import { 
  CpuChipIcon, 
  MagnifyingGlassIcon, 
  ArrowPathIcon,
  EyeIcon,
  SparklesIcon,
  CircleStackIcon,
  CommandLineIcon,
  DocumentTextIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import clsx from 'clsx';

interface Agent {
  id: string;
  name: string;
  description: string;
  specialization: string;
  capabilities: Capability[];
  source_file?: string;
  llm_provider: string;
  llm_model: string;
  personality_traits: Record<string, number>;
  trigger_keywords: string[];
  confidence_threshold: number;
  priority: number;
  created_at: string;
  updated_at: string;
  usage_stats?: {
    usage_count: number;
    success_count: number;
    success_rate: number;
    last_used?: string;
  };
}

interface Capability {
  name: string;
  description: string;
  category: string;
  required_tools: string[];
}

interface DiscoveryStats {
  total_agents: number;
  by_source: {
    claude_files: number;
    builtin: number;
    database: number;
  };
  by_specialization: Record<string, number>;
  total_capabilities: number;
  last_scan?: string;
}

export default function AgentRegistryPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [discoveryStats, setDiscoveryStats] = useState<DiscoveryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('all');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [showAgentDetails, setShowAgentDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
    loadStats();
  }, []);

  useEffect(() => {
    filterAgents();
  }, [agents, searchQuery, selectedSpecialization]);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const response = await agentDiscoveryService.discoverAllAgents();
      console.log('AgentRegistryPage API response:', response);
      
      if (response.success) {
        setAgents(response.agents);
        setError(null);
      } else {
        throw new Error(response.error || 'Failed to load agents');
      }
    } catch (err) {
      console.error('Failed to load agents:', err);
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await agentDiscoveryService.getDiscoveryStats();
      if (response.success) {
        setDiscoveryStats(response.discovery_stats);
      }
    } catch (err) {
      console.error('Failed to load discovery stats:', err);
    }
  };

  const refreshDiscovery = async () => {
    try {
      setRefreshing(true);
      const response = await agentDiscoveryService.refreshDiscovery();
      if (response.success) {
        await loadAgents();
        await loadStats();
        setError(null);
      } else {
        throw new Error(response.error || 'Failed to refresh discovery');
      }
    } catch (err) {
      console.error('Failed to refresh discovery:', err);
      setError(err instanceof Error ? err.message : 'Failed to refresh discovery');
    } finally {
      setRefreshing(false);
    }
  };

  const filterAgents = () => {
    let filtered = agents;

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(agent =>
        agent.name.toLowerCase().includes(query) ||
        agent.description.toLowerCase().includes(query) ||
        agent.specialization.toLowerCase().includes(query) ||
        agent.trigger_keywords.some(keyword => keyword.toLowerCase().includes(query))
      );
    }

    // Filter by specialization
    if (selectedSpecialization !== 'all') {
      filtered = filtered.filter(agent => agent.specialization === selectedSpecialization);
    }

    setFilteredAgents(filtered);
  };

  const viewAgentDetails = async (agent: Agent) => {
    try {
      // Load detailed agent info including usage stats
      const response = await agentDiscoveryService.getAgentDetails(agent.id);
      if (response.success) {
        setSelectedAgent(response.agent);
        setShowAgentDetails(true);
      }
    } catch (err) {
      console.error('Failed to load agent details:', err);
    }
  };

  const getSpecializationIcon = (specialization: string) => {
    const icons: Record<string, React.ReactNode> = {
      orchestration: <CommandLineIcon className="h-4 w-4" />,
      content_creation: <DocumentTextIcon className="h-4 w-4" />,
      prompt_optimization: <SparklesIcon className="h-4 w-4" />,
      general: <CpuChipIcon className="h-4 w-4" />,
      finance: <ChartBarIcon className="h-4 w-4" />,
      research: <MagnifyingGlassIcon className="h-4 w-4" />,
    };
    return icons[specialization] || <CpuChipIcon className="h-4 w-4" />;
  };

  const getProviderColor = (provider: string) => {
    const colors: Record<string, string> = {
      openai: 'bg-emerald-100 text-emerald-800',
      anthropic: 'bg-purple-100 text-purple-800',
      google: 'bg-blue-100 text-blue-800',
    };
    return colors[provider.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'bg-red-100 text-red-800';
    if (priority >= 5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const specializations = discoveryStats ? Object.keys(discoveryStats.by_specialization) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Failed to Load Agents
            </h3>
            <p className="text-gray-500 mb-4">{error}</p>
            <Button onClick={() => loadAgents()} variant="outline">
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Agent Registry</h1>
          <p className="text-gray-500">
            Discover and manage all AI agents in your ecosystem
          </p>
        </div>
        <Button
          onClick={refreshDiscovery}
          disabled={refreshing}
          className="bg-emerald-600 hover:bg-emerald-700"
        >
          <ArrowPathIcon className={clsx("h-4 w-4 mr-2", refreshing && "animate-spin")} />
          {refreshing ? 'Refreshing...' : 'Refresh Discovery'}
        </Button>
      </div>

      {/* Stats Cards */}
      {discoveryStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Agents</p>
                  <p className="text-2xl font-bold">{discoveryStats.total_agents}</p>
                </div>
                <CpuChipIcon className="h-8 w-8 text-emerald-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Built-in Agents</p>
                  <p className="text-2xl font-bold">{discoveryStats.by_source.builtin}</p>
                </div>
                <SparklesIcon className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Claude Agents</p>
                  <p className="text-2xl font-bold">{discoveryStats.by_source.claude_files}</p>
                </div>
                <DocumentTextIcon className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">Total Capabilities</p>
                  <p className="text-2xl font-bold">{discoveryStats.total_capabilities}</p>
                </div>
                <CircleStackIcon className="h-8 w-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search agents by name, description, or capabilities..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="md:w-48">
              <select
                value={selectedSpecialization}
                onChange={(e) => setSelectedSpecialization(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
              >
                <option value="all">All Specializations</option>
                {specializations.map(spec => (
                  <option key={spec} value={spec}>
                    {spec.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => (
          <Card key={agent.id} className="hover:shadow-lg transition-shadow cursor-pointer">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-2">
                  {getSpecializationIcon(agent.specialization)}
                  <div>
                    <CardTitle className="text-lg">{agent.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {agent.description.substring(0, 80)}...
                    </CardDescription>
                  </div>
                </div>
                <Badge className={getPriorityColor(agent.priority)}>
                  P{agent.priority}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Specialization & Provider */}
              <div className="flex items-center justify-between">
                <Badge variant="outline">
                  {agent.specialization.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </Badge>
                <Badge className={getProviderColor(agent.llm_provider)}>
                  {agent.llm_provider.toUpperCase()}
                </Badge>
              </div>

              {/* Capabilities */}
              <div>
                <p className="text-sm text-gray-500 mb-2">
                  {agent.capabilities.length} Capabilities
                </p>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.slice(0, 3).map((cap) => (
                    <Badge key={cap.name} variant="secondary" className="text-xs">
                      {cap.name.replace('_', ' ')}
                    </Badge>
                  ))}
                  {agent.capabilities.length > 3 && (
                    <Badge variant="secondary" className="text-xs">
                      +{agent.capabilities.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>

              {/* Trigger Keywords */}
              {agent.trigger_keywords.length > 0 && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Trigger Keywords</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.trigger_keywords.slice(0, 4).map((keyword) => (
                      <span
                        key={keyword}
                        className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                    {agent.trigger_keywords.length > 4 && (
                      <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                        +{agent.trigger_keywords.length - 4}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-between items-center pt-2 border-t">
                <div className="text-xs text-gray-500">
                  {agent.source_file ? (
                    <span>📄 File-based</span>
                  ) : agent.id.startsWith('db_') ? (
                    <span>💾 Database</span>
                  ) : (
                    <span>⚡ Built-in</span>
                  )}
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => viewAgentDetails(agent)}
                >
                  <EyeIcon className="h-4 w-4 mr-1" />
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {filteredAgents.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center">
            <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No agents found
            </h3>
            <p className="text-gray-500">
              Try adjusting your search criteria or refresh the discovery.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Agent Details Modal */}
      <Dialog open={showAgentDetails} onOpenChange={setShowAgentDetails}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedAgent && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center space-x-2">
                  {getSpecializationIcon(selectedAgent.specialization)}
                  <span>{selectedAgent.name}</span>
                  <Badge className={getPriorityColor(selectedAgent.priority)}>
                    Priority {selectedAgent.priority}
                  </Badge>
                </DialogTitle>
                <DialogDescription>
                  {selectedAgent.description}
                </DialogDescription>
              </DialogHeader>

              <Tabs defaultValue="overview" className="mt-4">
                <TabsList>
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
                  <TabsTrigger value="configuration">Configuration</TabsTrigger>
                  <TabsTrigger value="usage">Usage Stats</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Basic Info</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-500">ID:</span>
                          <span className="font-mono text-sm">{selectedAgent.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Specialization:</span>
                          <Badge variant="outline">
                            {selectedAgent.specialization.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Provider:</span>
                          <Badge className={getProviderColor(selectedAgent.llm_provider)}>
                            {selectedAgent.llm_provider.toUpperCase()}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-500">Model:</span>
                          <span>{selectedAgent.llm_model}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Source Info</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-500">Source:</span>
                          <span>
                            {selectedAgent.source_file ? (
                              <span>📄 File-based</span>
                            ) : selectedAgent.id.startsWith('db_') ? (
                              <span>💾 Database</span>
                            ) : (
                              <span>⚡ Built-in</span>
                            )}
                          </span>
                        </div>
                        {selectedAgent.source_file && (
                          <div className="flex justify-between">
                            <span className="text-gray-500">File:</span>
                            <span className="font-mono text-sm truncate max-w-48">
                              {selectedAgent.source_file.split('/').pop()}
                            </span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-gray-500">Confidence:</span>
                          <span>{(selectedAgent.confidence_threshold * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {selectedAgent.trigger_keywords.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Trigger Keywords</h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedAgent.trigger_keywords.map((keyword) => (
                          <Badge key={keyword} variant="secondary">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="capabilities" className="space-y-4">
                  <div className="grid gap-4">
                    {selectedAgent.capabilities.map((capability) => (
                      <Card key={capability.name}>
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h5 className="font-semibold">
                                {capability.name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </h5>
                              <p className="text-gray-600 text-sm mt-1">
                                {capability.description}
                              </p>
                              {capability.required_tools.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-xs text-gray-500 mb-1">Required Tools:</p>
                                  <div className="flex flex-wrap gap-1">
                                    {capability.required_tools.map((tool) => (
                                      <Badge key={tool} variant="outline" className="text-xs">
                                        {tool}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                            <Badge variant="outline" className="ml-2">
                              {capability.category}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="configuration" className="space-y-4">
                  {selectedAgent.system_prompt && (
                    <div>
                      <h4 className="font-semibold mb-2">System Prompt</h4>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <pre className="whitespace-pre-wrap text-sm">
                          {selectedAgent.system_prompt}
                        </pre>
                      </div>
                    </div>
                  )}

                  {Object.keys(selectedAgent.personality_traits).length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Personality Traits</h4>
                      <div className="space-y-2">
                        {Object.entries(selectedAgent.personality_traits).map(([trait, value]) => (
                          <div key={trait} className="flex items-center justify-between">
                            <span>{trait.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-emerald-600 h-2 rounded-full" 
                                  style={{ width: `${value * 100}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-500">
                                {(value * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="usage" className="space-y-4">
                  {selectedAgent.usage_stats ? (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-emerald-600">
                            {selectedAgent.usage_stats.usage_count}
                          </p>
                          <p className="text-sm text-gray-500">Total Uses</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-blue-600">
                            {selectedAgent.usage_stats.success_count}
                          </p>
                          <p className="text-sm text-gray-500">Successful</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-purple-600">
                            {(selectedAgent.usage_stats.success_rate * 100).toFixed(1)}%
                          </p>
                          <p className="text-sm text-gray-500">Success Rate</p>
                        </CardContent>
                      </Card>
                      {selectedAgent.usage_stats.last_used && (
                        <Card className="md:col-span-3">
                          <CardContent className="p-4">
                            <p className="text-sm text-gray-500">Last Used</p>
                            <p className="font-semibold">
                              {new Date(selectedAgent.usage_stats.last_used).toLocaleString()}
                            </p>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  ) : (
                    <Card>
                      <CardContent className="p-8 text-center">
                        <ChartBarIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          No Usage Data
                        </h3>
                        <p className="text-gray-500">
                          This agent hasn't been used yet or usage tracking is not available.
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>
              </Tabs>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}