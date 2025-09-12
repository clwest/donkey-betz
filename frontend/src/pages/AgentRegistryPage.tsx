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
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { toast } from 'react-hot-toast';

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
  system_prompt?: string;
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
      console.log('Number of agents received:', response.agents?.length || 0);
      
      if (response.agents && Array.isArray(response.agents)) {
        setAgents(response.agents);
        setError(null);
      } else if (response.success && response.agents) {
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
      if (response.discovery_stats) {
        setDiscoveryStats(response.discovery_stats);
      } else if (response.success && response.discovery_stats) {
        setDiscoveryStats(response.discovery_stats);
      } else if (response) {
        setDiscoveryStats(response);
      }
    } catch (err) {
      console.error('Failed to load discovery stats:', err);
    }
  };

  const refreshDiscovery = async () => {
    try {
      setRefreshing(true);
      await agentDiscoveryService.refreshDiscovery();
      await loadAgents();
      await loadStats();
      setError(null);
      toast.success('Discovery refreshed successfully');
    } catch (err) {
      console.error('Failed to refresh discovery:', err);
      setError(err instanceof Error ? err.message : 'Failed to refresh discovery');
      toast.error('Failed to refresh discovery');
    } finally {
      setRefreshing(false);
    }
  };

  const filterAgents = () => {
    let filtered = agents;
    console.log('Filtering agents. Starting with:', agents.length);

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(agent =>
        agent.name?.toLowerCase().includes(query) ||
        agent.description?.toLowerCase().includes(query) ||
        agent.specialization?.toLowerCase().includes(query) ||
        agent.trigger_keywords?.some(keyword => keyword?.toLowerCase().includes(query))
      );
      console.log('After search filter:', filtered.length);
    }

    if (selectedSpecialization !== 'all') {
      filtered = filtered.filter(agent => agent.specialization === selectedSpecialization);
      console.log('After specialization filter:', filtered.length);
    }

    console.log('Final filtered agents:', filtered.length);
    setFilteredAgents(filtered);
  };

  const viewAgentDetails = async (agent: Agent) => {
    try {
      const response = await agentDiscoveryService.getAgentDetails(agent.id);
      if (response && (response.agent || response.success)) {
        setSelectedAgent(response.agent || response);
        setShowAgentDetails(true);
      }
    } catch (err) {
      console.error('Failed to load agent details:', err);
      toast.error('Failed to load agent details');
    }
  };

  const getSpecializationIcon = (specialization: string) => {
    const icons: Record<string, React.ReactNode> = {
      orchestration: <CommandLineIcon className="h-5 w-5" />,
      content_creation: <DocumentTextIcon className="h-5 w-5" />,
      prompt_optimization: <SparklesIcon className="h-5 w-5" />,
      general: <CpuChipIcon className="h-5 w-5" />,
      finance: <ChartBarIcon className="h-5 w-5" />,
      research: <MagnifyingGlassIcon className="h-5 w-5" />,
    };
    return icons[specialization] || <CpuChipIcon className="h-5 w-5" />;
  };

  const getProviderColor = (provider: string) => {
    if (!provider) return 'text-gray-400 bg-gray-400/10';
    const colors: Record<string, string> = {
      openai: 'text-green-400 bg-green-400/10',
      anthropic: 'text-purple-400 bg-purple-400/10',
      google: 'text-blue-400 bg-blue-400/10',
    };
    return colors[provider.toLowerCase()] || 'text-gray-400 bg-gray-400/10';
  };

  const getPriorityColor = (priority: number) => {
    if (priority >= 8) return 'text-red-400 bg-red-400/10';
    if (priority >= 5) return 'text-yellow-400 bg-yellow-400/10';
    return 'text-green-400 bg-green-400/10';
  };


  const specializations = discoveryStats?.by_specialization ? Object.keys(discoveryStats.by_specialization) : [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <Card>
          <div className="text-center py-12">
            <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">
              Failed to Load Agents
            </h3>
            <p className="text-gray-400 mb-4">{error}</p>
            <Button onClick={() => loadAgents()} variant="secondary">
              <ArrowPathIcon className="h-4 w-4" />
              Try Again
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black space-y-6 p-4">
      {/* Gaming Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-cyan-400 font-mono uppercase tracking-wider glow-text-sm animate-pulse-glow">
            AGENT NEURAL REGISTRY
          </h1>
          <p className="text-purple-400 mt-1 text-lg font-mono">
            {'>>>'} NEURAL NETWORK AGENTS • STATUS MONITORING ACTIVE
          </p>
        </div>
        <Button
          onClick={refreshDiscovery}
          disabled={refreshing}
          className="bg-gray-900/80 border-2 border-cyan-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 text-cyan-400 font-mono uppercase tracking-wider transition-all duration-300"
        >
          <ArrowPathIcon className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''} text-cyan-400`} />
          {refreshing ? 'SCANNING...' : 'NEURAL SCAN'}
        </Button>
      </div>

      {/* Gaming Stats Cards */}
      {discoveryStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gray-900/80 border-2 border-cyan-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">TOTAL AGENTS</p>
                <p className="text-3xl font-bold text-cyan-400 font-mono glow-text-sm">{discoveryStats?.total_agents || 0}</p>
              </div>
              <CpuChipIcon className="h-8 w-8 text-cyan-400 animate-pulse" />
            </div>
          </Card>
          
          <Card className="bg-gray-900/80 border-2 border-purple-800/50 hover:border-purple-400/80 hover:shadow-lg hover:shadow-purple-500/30 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">CORE AGENTS</p>
                <p className="text-3xl font-bold text-purple-400 font-mono glow-text-sm">
                  {discoveryStats?.by_source?.builtin || 0}
                </p>
              </div>
              <SparklesIcon className="h-8 w-8 text-purple-400 animate-pulse" />
            </div>
          </Card>
          
          <Card className="bg-gray-900/80 border-2 border-blue-800/50 hover:border-blue-400/80 hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">NEURAL FILES</p>
                <p className="text-3xl font-bold text-blue-400 font-mono glow-text-sm">
                  {discoveryStats?.by_source?.claude_files || 0}
                </p>
              </div>
              <DocumentTextIcon className="h-8 w-8 text-blue-400 animate-pulse" />
            </div>
          </Card>
          
          <Card className="bg-gray-900/80 border-2 border-orange-800/50 hover:border-orange-400/80 hover:shadow-lg hover:shadow-orange-500/30 transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-400 font-mono uppercase tracking-wider">CAPABILITIES</p>
                <p className="text-3xl font-bold text-orange-400 font-mono glow-text-sm">
                  {discoveryStats?.total_capabilities || 0}
                </p>
              </div>
              <CircleStackIcon className="h-8 w-8 text-orange-400 animate-pulse" />
            </div>
          </Card>
        </div>
      )}

      {/* Gaming Search & Filters */}
      <Card className="bg-gray-900/80 border-2 border-purple-800/50 hover:border-purple-400/80 hover:shadow-lg hover:shadow-purple-500/30 transition-all duration-300">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-cyan-400 animate-pulse" />
              <input
                type="text"
                placeholder=">>> Neural search: agent name, description, capabilities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-black/50 border-2 border-gray-800/50 rounded-lg text-cyan-400 font-mono placeholder-purple-400/70 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 transition-all duration-300"
              />
            </div>
          </div>
          <div className="md:w-48">
            <select
              value={selectedSpecialization}
              onChange={(e) => setSelectedSpecialization(e.target.value)}
              className="w-full px-4 py-3 bg-black/50 border-2 border-gray-800/50 rounded-lg text-cyan-400 font-mono focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-400 transition-all duration-300"
            >
              <option value="all" className="bg-black text-cyan-400">ALL SPECIALIZATIONS</option>
              {specializations.map(spec => (
                <option key={spec} value={spec} className="bg-black text-cyan-400">
                  {spec.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>
        </div>
      </Card>

      {/* Gaming Agents Grid */}
      {filteredAgents.length === 0 ? (
        <Card className="bg-gray-900/80 border-2 border-red-800/50 hover:border-red-400/80 hover:shadow-lg hover:shadow-red-500/30 transition-all duration-300">
          <div className="text-center py-12">
            <MagnifyingGlassIcon className="h-12 w-12 text-red-400 mx-auto mb-3 animate-pulse" />
            <p className="text-red-400 mb-4 font-mono uppercase tracking-wider">NO NEURAL AGENTS DETECTED</p>
            <p className="text-sm text-purple-400 mb-4 font-mono">
              {'>>>'} Adjust neural scan parameters or reinitialize discovery protocols
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <Card key={agent.id} className="bg-gray-900/80 border-2 border-purple-800/50 hover:border-cyan-400/80 hover:shadow-lg hover:shadow-cyan-500/30 transition-all duration-300 flex flex-col">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-cyan-400 animate-pulse">
                    {getSpecializationIcon(agent.specialization)}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-mono font-bold text-cyan-400 uppercase tracking-wider">{agent.name}</h3>
                    <p className="text-sm text-purple-300 line-clamp-2 font-mono">
                      {agent.description}
                    </p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-mono font-bold border ${getPriorityColor(agent.priority)}`}>
                  P{agent.priority}
                </span>
              </div>

              {/* Gaming Info Section */}
              <div className="flex-1 space-y-3">
                <div className="flex items-center justify-between">
                  <Badge className="bg-purple-900/50 text-purple-400 border border-purple-400/50 font-mono uppercase tracking-wider">
                    {agent.specialization?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'GENERAL'}
                  </Badge>
                  <span className={`px-2 py-1 rounded text-xs font-mono font-bold border ${getProviderColor(agent.llm_provider)}`}>
                    {agent.llm_provider?.toUpperCase() || 'UNKNOWN'}
                  </span>
                </div>

                {/* Neural Capabilities */}
                <div>
                  <p className="text-xs text-cyan-400 mb-2 font-mono uppercase tracking-wider">
                    {agent.capabilities?.length || 0} NEURAL PROTOCOLS
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {agent.capabilities?.slice(0, 3).map((cap, index) => (
                      <span
                        key={cap.name || `cap-${index}`}
                        className="inline-block px-2 py-1 text-xs bg-black/50 text-green-400 border border-green-400/30 rounded font-mono"
                      >
                        {cap.name?.replace('_', ' ') || cap.name}
                      </span>
                    ))}
                    {(agent.capabilities?.length || 0) > 3 && (
                      <span className="inline-block px-2 py-1 text-xs bg-black/50 text-green-400 border border-green-400/30 rounded font-mono">
                        +{agent.capabilities.length - 3} MORE
                      </span>
                    )}
                  </div>
                </div>

                {/* Activation Keywords */}
                {agent.trigger_keywords?.length > 0 && (
                  <div>
                    <p className="text-xs text-cyan-400 mb-2 font-mono uppercase tracking-wider">ACTIVATION KEYS</p>
                    <div className="flex flex-wrap gap-1">
                      {agent.trigger_keywords?.slice(0, 3).map((keyword) => (
                        <span
                          key={keyword}
                          className="inline-block px-2 py-1 text-xs bg-black/50 text-yellow-400 border border-yellow-400/30 rounded font-mono"
                        >
                          {keyword}
                        </span>
                      ))}
                      {agent.trigger_keywords?.length > 3 && (
                        <span className="inline-block px-2 py-1 text-xs bg-black/50 text-yellow-400 border border-yellow-400/30 rounded font-mono">
                          +{agent.trigger_keywords.length - 3}
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Gaming Actions */}
              <div className="flex justify-between items-center pt-3 mt-3 border-t border-purple-800/50">
                <div className="text-xs text-purple-400 font-mono">
                  {agent.source_file ? (
                    <span>📄 FILE-BASED</span>
                  ) : agent.id.startsWith('db_') ? (
                    <span>💾 DATABASE</span>
                  ) : (
                    <span>⚡ CORE</span>
                  )}
                </div>
                <Button
                  size="sm"
                  onClick={() => viewAgentDetails(agent)}
                  className="bg-cyan-900/50 border border-cyan-400/50 text-cyan-400 hover:bg-cyan-900/80 hover:shadow-lg hover:shadow-cyan-500/30 font-mono uppercase tracking-wider transition-all duration-300"
                >
                  <EyeIcon className="h-4 w-4" />
                  ANALYZE
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Agent Details Modal */}
      <Dialog open={showAgentDetails} onOpenChange={setShowAgentDetails}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-dark-800 border-dark-700">
          {selectedAgent && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center space-x-2 text-white">
                  <span className="text-primary-400">
                    {getSpecializationIcon(selectedAgent.specialization)}
                  </span>
                  <span>{selectedAgent.name}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(selectedAgent.priority)}`}>
                    Priority {selectedAgent.priority}
                  </span>
                </DialogTitle>
                <DialogDescription className="text-gray-400">
                  {selectedAgent.description}
                </DialogDescription>
              </DialogHeader>

              <Tabs defaultValue="overview" className="mt-4">
                <TabsList className="bg-dark-700">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="capabilities">Capabilities</TabsTrigger>
                  <TabsTrigger value="configuration">Configuration</TabsTrigger>
                  <TabsTrigger value="usage">Usage Stats</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4 text-white">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Basic Info</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">ID:</span>
                          <span className="font-mono text-sm">{selectedAgent.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Specialization:</span>
                          <Badge variant="outline" className="text-gray-300 border-gray-600">
                            {selectedAgent.specialization.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Provider:</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getProviderColor(selectedAgent.llm_provider)}`}>
                            {selectedAgent.llm_provider.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-400">Model:</span>
                          <span>{selectedAgent.llm_model}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Source Info</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-gray-400">Source:</span>
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
                            <span className="text-gray-400">File:</span>
                            <span className="font-mono text-sm truncate max-w-48">
                              {selectedAgent.source_file.split('/').pop()}
                            </span>
                          </div>
                        )}
                        <div className="flex justify-between">
                          <span className="text-gray-400">Confidence:</span>
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
                          <Badge key={keyword} variant="secondary" className="bg-dark-700 text-gray-300">
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
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h5 className="font-semibold text-white">
                              {capability.name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h5>
                            <p className="text-gray-400 text-sm mt-1">
                              {capability.description}
                            </p>
                            {capability.required_tools && capability.required_tools.length > 0 && (
                              <div className="mt-2">
                                <p className="text-xs text-gray-500 mb-1">Required Tools:</p>
                                <div className="flex flex-wrap gap-1">
                                  {capability.required_tools.map((tool) => (
                                    <Badge key={tool} variant="outline" className="text-xs text-gray-400 border-gray-600">
                                      {tool}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          <Badge variant="outline" className="ml-2 text-gray-300 border-gray-600">
                            {capability.category}
                          </Badge>
                        </div>
                      </Card>
                    ))}
                  </div>
                </TabsContent>

                <TabsContent value="configuration" className="space-y-4">
                  {selectedAgent.system_prompt && (
                    <div>
                      <h4 className="font-semibold mb-2 text-white">System Prompt</h4>
                      <div className="bg-dark-700 p-4 rounded-lg">
                        <pre className="whitespace-pre-wrap text-sm text-gray-300">
                          {selectedAgent.system_prompt}
                        </pre>
                      </div>
                    </div>
                  )}

                  {selectedAgent.personality_traits && Object.keys(selectedAgent.personality_traits).length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 text-white">Personality Traits</h4>
                      <div className="space-y-2">
                        {Object.entries(selectedAgent.personality_traits).map(([trait, value]) => (
                          <div key={trait} className="flex items-center justify-between">
                            <span className="text-gray-300">{trait.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                            <div className="flex items-center space-x-2">
                              <div className="w-24 bg-dark-700 rounded-full h-2">
                                <div 
                                  className="bg-primary-500 h-2 rounded-full" 
                                  style={{ width: `${value * 100}%` }}
                                />
                              </div>
                              <span className="text-sm text-gray-400">
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
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-400">
                            {selectedAgent.usage_stats.usage_count}
                          </p>
                          <p className="text-sm text-gray-400">Total Uses</p>
                        </div>
                      </Card>
                      <Card>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-400">
                            {selectedAgent.usage_stats.success_count}
                          </p>
                          <p className="text-sm text-gray-400">Successful</p>
                        </div>
                      </Card>
                      <Card>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-400">
                            {(selectedAgent.usage_stats.success_rate * 100).toFixed(1)}%
                          </p>
                          <p className="text-sm text-gray-400">Success Rate</p>
                        </div>
                      </Card>
                      {selectedAgent.usage_stats.last_used && (
                        <Card className="md:col-span-3">
                          <div>
                            <p className="text-sm text-gray-400">Last Used</p>
                            <p className="font-semibold text-white">
                              {new Date(selectedAgent.usage_stats.last_used).toLocaleString()}
                            </p>
                          </div>
                        </Card>
                      )}
                    </div>
                  ) : (
                    <Card>
                      <div className="text-center py-8">
                        <ChartBarIcon className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-white mb-2">
                          No Usage Data
                        </h3>
                        <p className="text-gray-400">
                          This agent hasn't been used yet or usage tracking is not available.
                        </p>
                      </div>
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