# Claude Code Action Items - Multi-LLM Agent Teams

## 🎯 Project Goal
Enable the Mythology Lab to run experiments with agent teams using different LLMs (GPT-4, Claude, Llama2, etc.) to study cross-model communication and mythology propagation.

## 📋 Implementation Checklist

### Day 1: Database Updates ✓
- [ ] Add LLM fields to `AgentTemplate` model:
  - `llm_provider` (CharField with choices)
  - `llm_model` (CharField)
  - `llm_config` (JSONField)
- [ ] Add runtime LLM fields to `AgentInstance`:
  - `runtime_llm_provider`
  - `runtime_llm_model`
  - `team` (ForeignKey to new AgentTeam model)
- [ ] Create `AgentTeam` model in `agent_orchestra/models.py`
- [ ] Create `CrossModelInteraction` model for tracking
- [ ] Run migrations: `python manage.py makemigrations && python manage.py migrate`

### Day 2: Multi-LLM Service ✓
- [ ] Create `backend/agent_orchestra/services/multi_llm_service.py`
- [ ] Implement providers:
  - OpenAI (already have API key)
  - Anthropic (already have API key)  
  - Ollama (for local models)
  - Google/Gemini (already have API key)
  - Groq (already have API key)
- [ ] Add Ollama configuration to `.env`:
  ```
  OLLAMA_BASE_URL=http://localhost:11434
  ```
- [ ] Test each provider independently

### Day 3: Agent Execution Updates ✓
- [ ] Modify `enhanced_agent_service.py`:
  - Replace direct OpenAI calls with MultiLLMService
  - Add cross-model interaction tracking
  - Add mythology detection for each LLM response
- [ ] Update agent execution to use configured LLM
- [ ] Test agent execution with different providers

### Day 4: Experiment Integration ✓
- [ ] Create `backend/mythology_lab/experiments/multi_llm_experiment.py`
- [ ] Implement `MultiLLMExperimentRunner` class
- [ ] Add team creation and parallel execution logic
- [ ] Integrate with existing mythology tracking
- [ ] Create API endpoints in `mythology_lab/views.py`

### Day 5: Frontend & Testing ✓
- [ ] Add React component for experiment configuration
- [ ] Create visualization for results
- [ ] Run test experiments:
  - Homogeneous team (all GPT-4)
  - Heterogeneous team (GPT-4 + Claude + Llama)
- [ ] Analyze mythology propagation differences

## 🔑 Key Files to Modify

1. **Models**: `backend/agent_orchestra/models.py`
2. **Services**: Create `backend/agent_orchestra/services/multi_llm_service.py`
3. **Agent Execution**: `backend/agent_orchestra/services/enhanced_agent_service.py`
4. **Experiments**: Create `backend/mythology_lab/experiments/multi_llm_experiment.py`
5. **Views**: `backend/mythology_lab/views.py`
6. **Frontend**: `donkey-betz-frontend/src/features/mythology-lab/components/MultiLLMExperiment.tsx`

## 🧪 Test Scenarios

### Scenario 1: Basic Multi-LLM Test
```python
# Create two teams
team_a = ["GPT-4", "GPT-4", "GPT-4"]  # Control
team_b = ["GPT-4", "Claude-3", "Llama2"]  # Experimental

# Same task
task = "Create a business plan for AI-powered senior fitness"

# Compare results
```

### Scenario 2: Mythology Propagation
```python
# Inject known myth
myth = "Our platform has 350 active deployments"

# Track mutations across models
# Expected: Different models will interpret/modify differently
```

### Scenario 3: Cross-Model Communication
```python
# Complex technical task requiring precise communication
# Measure semantic similarity between model interpretations
# Track where communication breaks down
```

## 📊 Expected Outcomes

1. **Cross-model friction**: 15-25% information loss between different LLMs
2. **Mythology patterns**: 
   - GPT-4: Maintains structure, moderate inflation
   - Claude: More cautious, less mythology creation
   - Llama2: More creative, higher mythology rate
3. **Team efficiency**: Homogeneous teams 20-30% faster
4. **Innovation**: Heterogeneous teams produce more diverse solutions

## 🚀 Quick Start Commands

```bash
# Install Ollama (for local models)
curl -fsSL https://ollama.com/install.sh | sh

# Pull some models
ollama pull llama2
ollama pull mistral
ollama pull codellama

# Start Ollama server
ollama serve

# Run migrations after model changes
python manage.py makemigrations agent_orchestra mythology_lab
python manage.py migrate

# Test multi-LLM service
python manage.py shell
>>> from agent_orchestra.services.multi_llm_service import MultiLLMService
>>> service = MultiLLMService()
>>> result = await service.generate_completion('openai', 'gpt-4', 'Hello')
>>> result = await service.generate_completion('anthropic', 'claude-3-opus', 'Hello')
>>> result = await service.generate_completion('ollama', 'llama2', 'Hello')
```

## 📈 Success Metrics

- [ ] Successfully execute agents with 3+ different LLM providers
- [ ] Track cross-model interactions with semantic similarity scores
- [ ] Identify mythology propagation patterns unique to each LLM
- [ ] Generate comparison reports showing team performance differences
- [ ] Document optimal team compositions for different task types

## 🔧 Troubleshooting

1. **Ollama not connecting**: Ensure `ollama serve` is running on port 11434
2. **API key errors**: Check `.env` file has all required keys
3. **Migration issues**: Drop and recreate test database if needed
4. **Async errors**: Use `sync_to_async` wrapper for Django ORM calls

## 📝 Notes

- Start with OpenAI + Anthropic (easiest to test)
- Add Ollama for local model testing (no API limits)
- Google/Gemini and Groq can be added later
- Focus on mythology tracking differences between models
- Document any unexpected behaviors or patterns

This implementation leverages the existing agent and mythology infrastructure while adding minimal complexity. The key insight is that different LLMs may create and propagate myths differently, which could lead to fascinating "For Science" discoveries!