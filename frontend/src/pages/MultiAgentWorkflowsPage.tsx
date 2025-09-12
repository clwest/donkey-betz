import React, { useState, useEffect } from 'react';
import { Card } from '@/components/common/Card';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  UserGroupIcon,
  PlusIcon, 
  PlayIcon,
  CpuChipIcon,
  ArrowPathIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import '../styles/gaming-theme.css';
import { workflowsService } from '@/services/workflows.service';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';
import { toast } from 'sonner';

interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  specialization: string;
  status?: 'active' | 'inactive';
}

interface TeamWorkflow {
  name: string;
  description: string;
  agents: string[];
  coordination_strategy: 'sequential' | 'parallel' | 'mixed' | 'adaptive';
  communication_mode: 'broadcast' | 'direct' | 'hierarchical';
  consensus_requirement?: boolean;
  max_iterations?: number;
}

export default function MultiAgentWorkflowsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  
  const [teamWorkflow, setTeamWorkflow] = useState<TeamWorkflow>({
    name: '',
    description: '',
    agents: [],
    coordination_strategy: 'parallel',
    communication_mode: 'broadcast',
    consensus_requirement: false,
    max_iterations: 5
  });

  const [taskPrompt, setTaskPrompt] = useState('');

  useEffect(() => {
    document.body.classList.add('gaming-theme');
    loadAgents();
    
    return () => {
      document.body.classList.remove('gaming-theme');
    };
  }, []);

  const loadAgents = async () => {
    try {
      const agentsData = await agentDiscoveryService.discoverAllAgents();
      const extractedAgents = agentsData?.agents || [];
      setAgents(extractedAgents);
    } catch (error) {
      console.error('Error loading agents:', error);
      toast.error('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const toggleAgentSelection = (agentName: string) => {
    const newSelection = new Set(selectedAgents);
    if (newSelection.has(agentName)) {
      newSelection.delete(agentName);
    } else {
      newSelection.add(agentName);
    }
    setSelectedAgents(newSelection);
  };

  const selectAllAgents = () => {
    if (selectedAgents.size === agents.length) {
      setSelectedAgents(new Set());
    } else {
      setSelectedAgents(new Set(agents.map(a => a.name)));
    }
  };

  const selectAgentsBySpecialization = (specialization: string) => {
    const specializationAgents = agents
      .filter(a => a.specialization === specialization)
      .map(a => a.name);
    setSelectedAgents(new Set(specializationAgents));
  };

  const handleCreateTeam = () => {
    if (selectedAgents.size < 2) {
      toast.error('Please select at least 2 agents to form a team');
      return;
    }
    
    setTeamWorkflow(prev => ({
      ...prev,
      agents: Array.from(selectedAgents)
    }));
    setDialogOpen(true);
  };

  const handleExecuteWorkflow = async () => {
    if (!teamWorkflow.name || !taskPrompt) {
      toast.error('Please provide a workflow name and task description');
      return;
    }

    setExecuting(true);
    try {
      // Create the multi-agent workflow
      const workflowData = {
        name: teamWorkflow.name,
        description: teamWorkflow.description,
        agents: teamWorkflow.agents.map((name, index) => ({
          name,
          order: index + 1,
          params: {
            coordination_strategy: teamWorkflow.coordination_strategy,
            communication_mode: teamWorkflow.communication_mode
          }
        })),
        flow_config: {
          type: teamWorkflow.coordination_strategy,
          consensus_requirement: teamWorkflow.consensus_requirement,
          max_iterations: teamWorkflow.max_iterations,
          save_intermediate: true,
          error_handling: 'continue'
        }
      };

      await workflowsService.createWorkflow(workflowData);
      
      // Execute the workflow
      await workflowsService.executeWorkflow({
        workflow_name: teamWorkflow.name,
        prompt: taskPrompt,
        params: {}
      });

      toast.success(`Team workflow "${teamWorkflow.name}" created and executed successfully`);
      setDialogOpen(false);
      setSelectedAgents(new Set());
      setTaskPrompt('');
      setTeamWorkflow({
        name: '',
        description: '',
        agents: [],
        coordination_strategy: 'parallel',
        communication_mode: 'broadcast',
        consensus_requirement: false,
        max_iterations: 5
      });
    } catch (error) {
      console.error('Error executing team workflow:', error);
      toast.error('Failed to execute team workflow');
    } finally {
      setExecuting(false);
    }
  };

  // Group agents by specialization
  const agentsBySpecialization = agents.reduce((acc, agent) => {
    const spec = agent.specialization || 'General';
    if (!acc[spec]) acc[spec] = [];
    acc[spec].push(agent);
    return acc;
  }, {} as Record<string, Agent[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Gaming Header */}
      <div className="gaming-card relative overflow-hidden mb-8">
        <div className="gaming-border-glow"></div>
        
        <div className="relative flex items-center justify-between p-8">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 gaming-card border-gaming-neon-purple flex items-center justify-center">
                <UserGroupIcon className="w-8 h-8 text-gaming-neon-purple" />
              </div>
              <h1 className="text-5xl font-black gaming-text-primary text-shadow-lg">
                AGENT <span className="gaming-text-neon">TEAM</span> BUILDER
              </h1>
            </div>
            
            <p className="gaming-text-secondary text-xl font-bold font-mono">
              [ASSEMBLING COLLABORATIVE NEURAL TEAMS] &gt;&gt; MULTI-AGENT COORDINATION
            </p>
            
            <div className="flex items-center gap-4">
              <div className="gaming-status gaming-status-live">
                <SparklesIcon className="w-4 h-4" />
                {agents.length} AGENTS AVAILABLE
              </div>
              
              <div className="gaming-status bg-gaming-neon-purple/20 border-gaming-neon-purple text-gaming-neon-purple">
                <UserGroupIcon className="w-4 h-4" />
                {selectedAgents.size} SELECTED
              </div>
            </div>
          </div>
          
          <div className="flex flex-col gap-3">
            <Button 
              onClick={handleCreateTeam}
              disabled={selectedAgents.size < 2}
              className="gaming-btn-active px-8 py-4 text-lg">
              <PlusIcon className="h-5 w-5 mr-3" />
              BUILD TEAM ({selectedAgents.size})
            </Button>
            
            <Button 
              onClick={selectAllAgents}
              variant="outline"
              className="px-8 py-2 text-sm">
              {selectedAgents.size === agents.length ? 'DESELECT ALL' : 'SELECT ALL'}
            </Button>
          </div>
        </div>
      </div>

      {/* Quick Selection Filters */}
      <div className="gaming-card p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="gaming-text-secondary font-mono text-sm">QUICK SELECT:</span>
          {Object.keys(agentsBySpecialization).map(spec => (
            <Button
              key={spec}
              size="sm"
              variant="outline"
              onClick={() => selectAgentsBySpecialization(spec)}
              className="text-xs"
            >
              {spec} ({agentsBySpecialization[spec].length})
            </Button>
          ))}
        </div>
      </div>

      {/* Agent Selection Grid */}
      {Object.entries(agentsBySpecialization).map(([specialization, specAgents]) => (
        <div key={specialization} className="gaming-card">
          <div className="gaming-border-glow"></div>
          
          <div className="mb-4">
            <h3 className="text-xl font-bold gaming-text-primary flex items-center gap-2">
              <CpuChipIcon className="w-5 h-5 gaming-text-neon" />
              {specialization.toUpperCase()} AGENTS
              <Badge className="ml-2" variant="outline">
                {specAgents.length}
              </Badge>
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {specAgents.map((agent) => (
              <div 
                key={agent.name}
                onClick={() => toggleAgentSelection(agent.name)}
                className={`gaming-card p-4 cursor-pointer transition-all gaming-hover-lift ${
                  selectedAgents.has(agent.name) 
                    ? 'border-gaming-neon-purple bg-gaming-neon-purple/10' 
                    : ''
                }`}>
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={selectedAgents.has(agent.name)}
                    onCheckedChange={() => toggleAgentSelection(agent.name)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <h4 className="font-bold gaming-text-primary text-sm">
                      {agent.name.toUpperCase()}
                    </h4>
                    <p className="text-xs gaming-text-secondary mt-1 line-clamp-2">
                      {agent.description}
                    </p>
                    {agent.capabilities && agent.capabilities.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {agent.capabilities.slice(0, 3).map((cap, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {cap}
                          </Badge>
                        ))}
                        {agent.capabilities.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{agent.capabilities.length - 3}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Team Configuration Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-3xl gaming-card border-gaming-neon-purple">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold gaming-text-primary">
              <UserGroupIcon className="w-6 h-6 mr-2 text-gaming-neon-purple inline" />
              CONFIGURE AGENT TEAM
            </DialogTitle>
            <DialogDescription className="gaming-text-secondary font-mono">
              &gt;&gt; SELECTED AGENTS: {Array.from(selectedAgents).join(', ')}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="team-name" className="text-gray-300">Team Name</Label>
                <input
                  id="team-name"
                  type="text"
                  value={teamWorkflow.name}
                  onChange={(e) => setTeamWorkflow(prev => ({...prev, name: e.target.value}))}
                  placeholder="Alpha Strike Team"
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
                />
              </div>
              
              <div>
                <Label htmlFor="coordination" className="text-gray-300">Coordination Strategy</Label>
                <select
                  id="coordination"
                  value={teamWorkflow.coordination_strategy}
                  onChange={(e) => setTeamWorkflow(prev => ({
                    ...prev, 
                    coordination_strategy: e.target.value as any
                  }))}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
                >
                  <option value="sequential">Sequential</option>
                  <option value="parallel">Parallel</option>
                  <option value="mixed">Mixed</option>
                  <option value="adaptive">Adaptive</option>
                </select>
              </div>
            </div>
            
            <div>
              <Label htmlFor="team-description" className="text-gray-300">Team Description</Label>
              <textarea
                id="team-description"
                value={teamWorkflow.description}
                onChange={(e) => setTeamWorkflow(prev => ({...prev, description: e.target.value}))}
                placeholder="Describe the team's mission..."
                rows={3}
                className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
              />
            </div>
            
            <div>
              <Label htmlFor="task-prompt" className="text-gray-300">Task Description</Label>
              <textarea
                id="task-prompt"
                value={taskPrompt}
                onChange={(e) => setTaskPrompt(e.target.value)}
                placeholder="What should this team accomplish?"
                rows={4}
                className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="communication" className="text-gray-300">Communication Mode</Label>
                <select
                  id="communication"
                  value={teamWorkflow.communication_mode}
                  onChange={(e) => setTeamWorkflow(prev => ({
                    ...prev, 
                    communication_mode: e.target.value as any
                  }))}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
                >
                  <option value="broadcast">Broadcast</option>
                  <option value="direct">Direct</option>
                  <option value="hierarchical">Hierarchical</option>
                </select>
              </div>
              
              <div>
                <Label htmlFor="iterations" className="text-gray-300">Max Iterations</Label>
                <input
                  id="iterations"
                  type="number"
                  min="1"
                  max="20"
                  value={teamWorkflow.max_iterations}
                  onChange={(e) => setTeamWorkflow(prev => ({
                    ...prev, 
                    max_iterations: parseInt(e.target.value) || 5
                  }))}
                  className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white"
                />
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Checkbox
                id="consensus"
                checked={teamWorkflow.consensus_requirement}
                onCheckedChange={(checked) => setTeamWorkflow(prev => ({
                  ...prev, 
                  consensus_requirement: !!checked
                }))}
              />
              <Label htmlFor="consensus" className="text-gray-300">
                Require consensus before proceeding
              </Label>
            </div>
            
            <div className="flex justify-end gap-3 mt-6">
              <Button 
                variant="outline"
                onClick={() => setDialogOpen(false)}
                disabled={executing}
              >
                Cancel
              </Button>
              <Button 
                onClick={handleExecuteWorkflow}
                disabled={executing || !teamWorkflow.name || !taskPrompt}
                className="gaming-btn-active"
              >
                {executing ? (
                  <>
                    <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
                    EXECUTING...
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-4 w-4 mr-2" />
                    DEPLOY TEAM
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}