import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { workflowsService } from '@/services/workflows.service';
import { agentDiscoveryService } from '@/services/agentDiscovery.service';

export default function DebugPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const testAPI = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🚀 Starting API tests...');
      
      const [workflowsData, templatesData, agentsData] = await Promise.all([
        workflowsService.listWorkflows(),
        workflowsService.getWorkflowTemplates(),
        agentDiscoveryService.discoverAllAgents()
      ]);

      console.log('📥 API Responses:', { workflowsData, templatesData, agentsData });

      setWorkflows(workflowsData?.workflows || []);
      setTemplates(templatesData?.templates || []);
      setAgents(agentsData?.agents || []);
      
      console.log('✅ State updated:', {
        workflows: workflowsData?.workflows?.length || 0,
        templates: templatesData?.templates?.length || 0,
        agents: agentsData?.agents?.length || 0
      });
      
    } catch (err) {
      console.error('❌ API Test Error:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Debug Page</h1>
        <p className="text-muted-foreground">Testing API calls and component rendering</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Workflows</CardTitle>
            <CardDescription>{workflows.length} items</CardDescription>
          </CardHeader>
          <CardContent>
            {workflows.length === 0 ? (
              <p className="text-muted-foreground">No workflows found</p>
            ) : (
              <div className="space-y-2">
                {workflows.slice(0, 3).map((workflow, index) => (
                  <Badge key={index} variant="outline">
                    {workflow.name}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Templates</CardTitle>
            <CardDescription>{templates.length} items</CardDescription>
          </CardHeader>
          <CardContent>
            {templates.length === 0 ? (
              <p className="text-muted-foreground">No templates found</p>
            ) : (
              <div className="space-y-2">
                {templates.slice(0, 3).map((template, index) => (
                  <Badge key={index} variant="outline">
                    {template.name}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Agents</CardTitle>
            <CardDescription>{agents.length} items</CardDescription>
          </CardHeader>
          <CardContent>
            {agents.length === 0 ? (
              <p className="text-muted-foreground">No agents found</p>
            ) : (
              <div className="space-y-2">
                {agents.slice(0, 3).map((agent, index) => (
                  <Badge key={index} variant="outline">
                    {agent.name}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {error && (
        <Card className="border-red-500">
          <CardContent className="pt-6">
            <div className="text-red-500">
              <strong>Error:</strong> {error}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="flex gap-2">
        <Button onClick={testAPI} disabled={loading}>
          {loading ? 'Testing...' : 'Re-test APIs'}
        </Button>
        
        <Button 
          variant="outline" 
          onClick={() => {
            console.log('Current state:', { workflows, templates, agents });
          }}
        >
          Log State
        </Button>
      </div>

      {/* Raw Data Display */}
      <Card>
        <CardHeader>
          <CardTitle>Raw Data</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-background p-4 rounded overflow-auto max-h-96">
            {JSON.stringify({ workflows, templates, agents }, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}