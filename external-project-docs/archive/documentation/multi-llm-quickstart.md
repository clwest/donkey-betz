# Multi-LLM Teams Quick Implementation Guide

## Overview
Enable the Mythology Lab to run experiments with agent teams using different LLMs (GPT-4, Claude, Llama, etc.) to study cross-model communication and mythology propagation.

## Core Changes Needed

### 1. Database Migration (First Priority)
```bash
# Create new migration
python manage.py makemigrations agent_orchestra -n add_multi_llm_support
```

Add these fields to existing models:

```python
# agent_orchestra/models.py - Add to AgentTemplate
llm_provider = models.CharField(max_length=50, default='openai', choices=[
    ('openai', 'OpenAI'), ('anthropic', 'Anthropic'), ('ollama', 'Ollama'), 
    ('google', 'Google'), ('mistral', 'Mistral'), ('cohere', 'Cohere')
])
llm_model = models.CharField(max_length=100, default='gpt-4-turbo-preview')
llm_config = models.JSONField(default=dict)

# agent_orchestra/models.py - Add to AgentInstance  
runtime_llm_provider = models.CharField(max_length=50, blank=True)
runtime_llm_model = models.CharField(max_length=100, blank=True)
team = models.ForeignKey('AgentTeam', null=True, blank=True, on_delete=models.SET_NULL)
```

### 2. New Models for Teams
```python
# agent_orchestra/models.py - New model
class AgentTeam(models.Model):
    name = models.CharField(max_length=100)
    orchestration = models.ForeignKey(TaskOrchestration, on_delete=models.CASCADE)
    team_type = models.CharField(max_length=50, choices=[
        ('homogeneous', 'Same LLM'), ('heterogeneous', 'Mixed LLMs')
    ])
    mythology_experiment = models.ForeignKey(
        'mythology_lab.MythologyExperiment', null=True, blank=True, 
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. Multi-LLM Service (Core Logic)
```python
# agent_orchestra/services/multi_llm_service.py
import openai
import anthropic
import aiohttp

class MultiLLMService:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_completion(self, provider, model, prompt, system_prompt=None):
        if provider == 'openai':
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt or ""},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
            
        elif provider == 'anthropic':
            response = await self.anthropic_client.messages.create(
                model=model,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.content[0].text
            
        elif provider == 'ollama':
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{settings.OLLAMA_URL}/api/generate", json={
                    "model": model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False
                }) as resp:
                    result = await resp.json()
                    return result['response']
```

### 4. Update Agent Execution
```python
# agent_orchestra/services/enhanced_agent_service.py - Modify execute_agent method
async def execute_agent_with_llm(self, agent, task, context):
    # Get LLM config
    provider = agent.runtime_llm_provider or agent.template.llm_provider
    model = agent.runtime_llm_model or agent.template.llm_model
    
    # Use MultiLLMService instead of direct OpenAI
    llm_service = MultiLLMService()
    response = await llm_service.generate_completion(
        provider=provider,
        model=model,
        prompt=task,
        system_prompt=agent.template.system_prompt_template
    )
    
    # Track if this is cross-model communication
    if agent.team:
        await self._track_cross_model_interactions(agent, response)
    
    return response
```

### 5. Experiment API Endpoint
```python
# mythology_lab/urls.py - Add new route
path('experiments/multi-llm/', MultiLLMExperimentView.as_view()),

# mythology_lab/views.py - New view
class MultiLLMExperimentView(APIView):
    async def post(self, request):
        """Create multi-LLM team experiment"""
        data = request.data
        
        # Create teams with different LLM configs
        teams = []
        for team_config in data['teams']:
            team = AgentTeam.objects.create(
                name=team_config['name'],
                team_type=team_config['type']
            )
            
            # Create agents with specific LLMs
            for agent_config in team_config['agents']:
                template = AgentTemplate.objects.get(name=agent_config['template'])
                agent = AgentInstance.objects.create(
                    template=template,
                    team=team,
                    runtime_llm_provider=agent_config['provider'],
                    runtime_llm_model=agent_config['model'],
                    assigned_task=data['task']
                )
            
            teams.append(team)
        
        # Execute experiment
        results = await run_team_comparison(teams, data['task'])
        return Response(results)
```

### 6. Quick Frontend Component
```tsx
// Add to mythology lab dashboard
const MultiLLMConfig = () => {
  const [teams, setTeams] = useState([
    {
      name: "GPT-4 Team",
      agents: [
        {template: "Research Agent", provider: "openai", model: "gpt-4"},
        {template: "Business Agent", provider: "openai", model: "gpt-4"}
      ]
    },
    {
      name: "Mixed Team", 
      agents: [
        {template: "Research Agent", provider: "openai", model: "gpt-4"},
        {template: "Business Agent", provider: "anthropic", model: "claude-3-opus"}
      ]
    }
  ]);
  
  const runExperiment = async () => {
    const response = await fetch('/api/mythology/experiments/multi-llm/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        task: "Analyze AI fitness market",
        teams: teams
      })
    });
  };
  
  return (
    <div>
      {/* Team configuration UI */}
      <button onClick={runExperiment}>Run Experiment</button>
    </div>
  );
};
```

## Environment Setup
```bash
# Add to .env
ANTHROPIC_API_KEY=your_anthropic_key
OLLAMA_URL=http://localhost:11434
GOOGLE_AI_API_KEY=your_google_key  # Optional
MISTRAL_API_KEY=your_mistral_key   # Optional
```

## Testing Plan

### Phase 1: Basic Multi-LLM Support (Day 1-2)
1. Add database fields and migrate
2. Implement MultiLLMService with OpenAI + Anthropic
3. Test basic agent execution with different models

### Phase 2: Team Formation (Day 3)
1. Create AgentTeam model
2. Build team creation API
3. Test homogeneous vs heterogeneous teams

### Phase 3: Mythology Tracking (Day 4)
1. Track cross-model interactions
2. Detect mythology mutations between models
3. Generate comparison reports

### Phase 4: UI & Experiments (Day 5)
1. Add experiment configuration UI
2. Create results visualization
3. Run full comparison experiments

## Quick Test Scenarios

1. **Same Task, Different Models**
   - Team A: 3 GPT-4 agents
   - Team B: 1 GPT-4, 1 Claude, 1 Llama
   - Task: "Create a business plan for AI tutoring"

2. **Mythology Propagation Test**
   - Inject: "Our platform has 350 active deployments"
   - Track how each model interprets/modifies this

3. **Communication Breakdown Test**
   - Complex technical task requiring precise communication
   - Measure semantic similarity across model boundaries

## Expected Results

- **Cross-model friction**: 15-25% information loss between different LLMs
- **Mythology amplification**: Some models (especially open-source) may amplify myths more
- **Team efficiency**: Homogeneous teams 20-30% faster but less creative
- **Model personalities**: Claude more cautious, GPT more structured, Llama more creative

## Success Metrics

1. Successfully run experiments with 3+ different LLM providers
2. Track and visualize cross-model communication patterns
3. Identify mythology propagation differences between models
4. Generate actionable insights about optimal team composition

This implementation leverages existing infrastructure while adding minimal complexity. Start with Phase 1 and iterate based on findings!