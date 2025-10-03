# Multi-LLM Agent Teams for Mythology Lab - Claude Code Handoff

## Project Overview

Create a "For Science" experiment system in the Mythology Lab that allows testing agent teams/crews with different LLM providers to study cross-model communication, mythology propagation, and emergent behaviors.

## Current State Analysis

### Existing Infrastructure

1. **Agent System** (`/backend/agent_orchestra/`)
   - `AgentTemplate` model: Base templates for 21 agent types
   - `AgentInstance` model: Active agent instances
   - `TaskOrchestration` model: Manages multi-agent workflows
   - Current limitation: All agents use OpenAI GPT models

2. **Mythology Lab** (`/backend/mythology_lab/`)
   - Complete tracking system for mythology events
   - `MythSeeder` for controlled experiments
   - Agent behavior profiling
   - Pattern analysis and propagation tracking

3. **Missing Components**
   - No LLM provider configuration per agent
   - No multi-model orchestration support
   - No CrewAI integration (but adaptable architecture)

## Proposed Architecture

### 1. Database Schema Updates

#### Add to `AgentTemplate` model:
```python
# In backend/agent_orchestra/models.py

class AgentTemplate(models.Model):
    # ... existing fields ...
    
    # New LLM Configuration
    llm_provider = models.CharField(
        max_length=50, 
        choices=[
            ('openai', 'OpenAI (GPT)'),
            ('anthropic', 'Anthropic (Claude)'),
            ('google', 'Google (Gemini)'),
            ('meta', 'Meta (Llama)'),
            ('mistral', 'Mistral AI'),
            ('cohere', 'Cohere'),
            ('groq', 'Groq'),
            ('ollama', 'Ollama (Local)'),
            ('custom', 'Custom Endpoint'),
        ],
        default='openai',
        help_text="LLM provider for this agent"
    )
    
    llm_model = models.CharField(
        max_length=100,
        default='gpt-4-turbo-preview',
        help_text="Specific model name (e.g., gpt-4, claude-3-opus, llama-2-70b)"
    )
    
    llm_config = models.JSONField(
        default=dict,
        help_text="Provider-specific configuration (API endpoints, parameters, etc.)"
    )
    
    # Team/Crew Configuration
    team_role = models.CharField(
        max_length=50,
        choices=[
            ('leader', 'Team Leader'),
            ('member', 'Team Member'),
            ('specialist', 'Specialist'),
            ('reviewer', 'Reviewer'),
            ('coordinator', 'Coordinator'),
        ],
        default='member',
        help_text="Role within agent team"
    )
```

#### Add to `AgentInstance` model:
```python
class AgentInstance(models.Model):
    # ... existing fields ...
    
    # Runtime LLM Configuration (can override template)
    runtime_llm_provider = models.CharField(max_length=50, blank=True)
    runtime_llm_model = models.CharField(max_length=100, blank=True)
    runtime_llm_config = models.JSONField(default=dict, blank=True)
    
    # Team Membership
    team = models.ForeignKey(
        'AgentTeam', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members'
    )
    
    # Cross-model communication tracking
    cross_model_interactions = models.JSONField(
        default=list,
        help_text="Track interactions with agents using different LLMs"
    )
```

### 2. New Models for Team Management

```python
# In backend/agent_orchestra/models.py

class AgentTeam(models.Model):
    """Represents a team/crew of agents working together"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    orchestration = models.ForeignKey(
        TaskOrchestration, 
        on_delete=models.CASCADE,
        related_name='teams'
    )
    
    # Team Configuration
    team_type = models.CharField(
        max_length=50,
        choices=[
            ('homogeneous', 'Same LLM Provider'),
            ('heterogeneous', 'Mixed LLM Providers'),
            ('control', 'Control Group'),
            ('experimental', 'Experimental Group'),
        ]
    )
    
    leader_agent = models.ForeignKey(
        AgentInstance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    
    # Mythology Experiment Integration
    mythology_experiment = models.ForeignKey(
        'mythology_lab.MythologyExperiment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_teams'
    )
    
    # Team Metrics
    coordination_score = models.FloatField(default=0.0)
    mythology_creation_rate = models.FloatField(default=0.0)
    cross_model_friction = models.FloatField(
        default=0.0,
        help_text="Measure of communication difficulties between different LLMs"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.team_type})"


class CrossModelInteraction(models.Model):
    """Track specific interactions between agents using different LLMs"""
    
    from_agent = models.ForeignKey(
        AgentInstance,
        on_delete=models.CASCADE,
        related_name='cross_model_sent'
    )
    to_agent = models.ForeignKey(
        AgentInstance,
        on_delete=models.CASCADE,
        related_name='cross_model_received'
    )
    
    # Interaction Details
    interaction_type = models.CharField(
        max_length=50,
        choices=[
            ('data_transfer', 'Data Transfer'),
            ('instruction', 'Instruction'),
            ('question', 'Question'),
            ('clarification', 'Clarification Request'),
            ('mythology_spread', 'Mythology Propagation'),
        ]
    )
    
    original_content = models.TextField()
    interpreted_content = models.TextField()
    
    # Metrics
    semantic_similarity = models.FloatField(
        default=1.0,
        help_text="How well the receiving agent understood the message"
    )
    mythology_mutations = models.JSONField(
        default=list,
        help_text="Track any mythological mutations in the interaction"
    )
    
    # LLM Details
    from_llm = models.CharField(max_length=100)
    to_llm = models.CharField(max_length=100)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['from_llm', 'to_llm']),
        ]
```

### 3. LLM Provider Service

Create a unified service to handle multiple LLM providers:

```python
# backend/agent_orchestra/services/multi_llm_service.py

from typing import Dict, Any, List, Optional
import asyncio
from abc import ABC, abstractmethod

# Provider imports
import openai
import anthropic
from google.generativeai import GenerativeModel
import cohere
import requests
from transformers import pipeline  # For local models

class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate_completion(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate completion from the LLM"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider name for tracking"""
        pass


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 1000)
        )
        return response.choices[0].message.content
    
    def get_provider_name(self) -> str:
        return f"openai:{self.model}"


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7),
            system=system_prompt if system_prompt else "",
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def get_provider_name(self) -> str:
        return f"anthropic:{self.model}"


class OllamaProvider(BaseLLMProvider):
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    async def generate_completion(self, prompt: str, system_prompt: Optional[str] = None, **kwargs):
        url = f"{self.base_url}/api/generate"
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "model": self.model,
                "prompt": full_prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 1000),
                "stream": False
            }) as response:
                result = await response.json()
                return result['response']
    
    def get_provider_name(self) -> str:
        return f"ollama:{self.model}"


class MultiLLMService:
    """Service to manage multiple LLM providers"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on settings"""
        from django.conf import settings
        
        # OpenAI
        if hasattr(settings, 'OPENAI_API_KEY'):
            self.providers['openai'] = OpenAIProvider(settings.OPENAI_API_KEY)
        
        # Anthropic
        if hasattr(settings, 'ANTHROPIC_API_KEY'):
            self.providers['anthropic'] = AnthropicProvider(settings.ANTHROPIC_API_KEY)
        
        # Ollama (local)
        if hasattr(settings, 'OLLAMA_BASE_URL'):
            self.providers['ollama'] = OllamaProvider(base_url=settings.OLLAMA_BASE_URL)
        
        # Add more providers as needed
    
    async def generate_completion(
        self,
        provider: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion using specified provider and model"""
        
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
        
        provider_instance = self.providers[provider]
        
        # Override model if specified
        if hasattr(provider_instance, 'model'):
            original_model = provider_instance.model
            provider_instance.model = model
        
        try:
            response = await provider_instance.generate_completion(
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs
            )
            
            return {
                'success': True,
                'response': response,
                'provider': provider,
                'model': model,
                'metadata': {
                    'provider_name': provider_instance.get_provider_name(),
                    'timestamp': timezone.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'provider': provider,
                'model': model
            }
        finally:
            # Restore original model
            if hasattr(provider_instance, 'model'):
                provider_instance.model = original_model
```

### 4. Enhanced Agent Execution

Update the agent execution to use multi-LLM support:

```python
# backend/agent_orchestra/services/multi_llm_agent_service.py

from typing import Dict, Any, Optional
from .multi_llm_service import MultiLLMService
from ..models import AgentInstance, CrossModelInteraction
from mythology_lab.models import MythologyEvent

class MultiLLMAgentService:
    """Enhanced agent service with multi-LLM support"""
    
    def __init__(self):
        self.llm_service = MultiLLMService()
    
    async def execute_agent_with_llm(
        self,
        agent: AgentInstance,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent using its configured LLM"""
        
        # Determine LLM configuration
        provider = agent.runtime_llm_provider or agent.template.llm_provider
        model = agent.runtime_llm_model or agent.template.llm_model
        
        # Prepare enhanced prompt with cross-model awareness
        system_prompt = self._prepare_cross_model_prompt(agent)
        
        # Generate response
        result = await self.llm_service.generate_completion(
            provider=provider,
            model=model,
            prompt=task,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        if result['success']:
            # Track cross-model interactions if communicating with different LLM
            await self._track_cross_model_interaction(agent, result)
            
            # Check for mythology creation
            await self._check_mythology_creation(agent, result['response'])
            
            return {
                'success': True,
                'response': result['response'],
                'llm_metadata': result['metadata']
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def _prepare_cross_model_prompt(self, agent: AgentInstance) -> str:
        """Prepare system prompt with cross-model communication guidelines"""
        
        base_prompt = agent.template.system_prompt_template
        
        # Add cross-model communication instructions
        cross_model_prompt = """
You are participating in a multi-model agent team where different agents may use different LLMs.

Important guidelines for cross-model communication:
1. Be explicit and clear in your communication
2. Avoid model-specific idioms or patterns
3. Confirm understanding when receiving information
4. Use structured formats when sharing data
5. Be aware that other models may interpret things differently

Your LLM: {provider}:{model}
Team members may be using: OpenAI, Anthropic, Meta, Mistral, or local models.
"""
        
        return f"{base_prompt}\n\n{cross_model_prompt.format(
            provider=agent.runtime_llm_provider or agent.template.llm_provider,
            model=agent.runtime_llm_model or agent.template.llm_model
        )}"
    
    async def _track_cross_model_interaction(self, agent: AgentInstance, result: Dict[str, Any]):
        """Track interactions between different LLM providers"""
        
        if not agent.team:
            return
        
        # Find other agents in team with different LLMs
        team_members = agent.team.members.exclude(id=agent.id)
        
        for member in team_members:
            member_provider = member.runtime_llm_provider or member.template.llm_provider
            agent_provider = agent.runtime_llm_provider or agent.template.llm_provider
            
            if member_provider != agent_provider:
                # Record cross-model interaction
                interaction = CrossModelInteraction.objects.create(
                    from_agent=agent,
                    to_agent=member,
                    interaction_type='data_transfer',
                    original_content=result['response'][:500],  # First 500 chars
                    interpreted_content='',  # Will be filled when received
                    from_llm=f"{agent_provider}:{agent.runtime_llm_model or agent.template.llm_model}",
                    to_llm=f"{member_provider}:{member.runtime_llm_model or member.template.llm_model}"
                )
                
                # Update agent's cross-model interactions
                agent.cross_model_interactions.append({
                    'interaction_id': str(interaction.id),
                    'timestamp': timezone.now().isoformat(),
                    'to_llm': interaction.to_llm
                })
                agent.save()
    
    async def _check_mythology_creation(self, agent: AgentInstance, response: str):
        """Check if agent response contains mythological elements"""
        
        from mythology_lab.monitoring.myth_detector import MythDetector
        
        detector = MythDetector()
        
        # Create pseudo-memory for detection
        memory_data = {
            'id': f'agent_{agent.id}_{timezone.now().timestamp()}',
            'content': response,
            'source_type': 'ai_generated',
            'metadata': {
                'agent_id': agent.id,
                'llm_provider': agent.runtime_llm_provider or agent.template.llm_provider,
                'llm_model': agent.runtime_llm_model or agent.template.llm_model
            }
        }
        
        result = detector.detect_mythology(memory_data)
        
        if result['mythology_confidence'] > 0.7:
            # Create mythology event
            MythologyEvent.objects.create(
                event_type='creation',
                original_content=response[:500],
                mutation_type=result.get('detected_patterns', ['unknown'])[0],
                agent_id=agent.id,
                agent_name=f"{agent.template.name} ({agent.runtime_llm_provider or agent.template.llm_provider})",
                confidence_score=result['mythology_confidence'],
                metadata={
                    'llm_details': {
                        'provider': agent.runtime_llm_provider or agent.template.llm_provider,
                        'model': agent.runtime_llm_model or agent.template.llm_model
                    },
                    'detection_result': result
                }
            )
```

### 5. Mythology Lab Experiment Integration

Create experiment runner for multi-LLM teams:

```python
# backend/mythology_lab/experiments/multi_llm_experiment.py

from typing import List, Dict, Any
import asyncio
from agent_orchestra.models import AgentTemplate, AgentTeam, TaskOrchestration
from agent_orchestra.services.multi_llm_agent_service import MultiLLMAgentService
from mythology_lab.experiments.myth_seeder import MythSeeder

class MultiLLMExperimentRunner:
    """Run controlled experiments with multi-LLM agent teams"""
    
    def __init__(self):
        self.agent_service = MultiLLMAgentService()
        self.myth_seeder = MythSeeder()
    
    async def create_comparison_experiment(
        self,
        experiment_name: str,
        task: str,
        team_configs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create experiment comparing multiple teams with different LLM configurations
        
        Args:
            experiment_name: Name of the experiment
            task: Task to give all teams
            team_configs: List of team configurations, each with:
                - name: Team name
                - agents: List of agent configs with template_name and llm_provider
                - team_type: 'homogeneous' or 'heterogeneous'
        """
        
        # Create orchestration
        orchestration = await TaskOrchestration.objects.acreate(
            user_id=1,  # System user
            master_task=f"Multi-LLM Experiment: {experiment_name}",
            task_analysis={'experiment': True, 'task': task}
        )
        
        # Create mythology experiment
        from mythology_lab.models import MythologyExperiment
        myth_experiment = await MythologyExperiment.objects.acreate(
            experiment_name=experiment_name,
            description=f"Multi-LLM comparison: {task}",
            test_phrase=task,
            expected_mutation="Cross-model interpretation differences"
        )
        
        teams = []
        
        for config in team_configs:
            # Create team
            team = await AgentTeam.objects.acreate(
                name=config['name'],
                orchestration=orchestration,
                team_type=config['team_type'],
                mythology_experiment=myth_experiment
            )
            
            # Create agents for team
            team_agents = []
            for i, agent_config in enumerate(config['agents']):
                template = await AgentTemplate.objects.aget(
                    name=agent_config['template_name']
                )
                
                agent = await AgentInstance.objects.acreate(
                    user_id=1,
                    template=template,
                    orchestration=orchestration,
                    assigned_task=task,
                    team=team,
                    runtime_llm_provider=agent_config.get('llm_provider', 'openai'),
                    runtime_llm_model=agent_config.get('llm_model', 'gpt-4-turbo-preview'),
                    runtime_llm_config=agent_config.get('llm_config', {})
                )
                
                team_agents.append(agent)
                
                # Set leader if first agent
                if i == 0:
                    team.leader_agent = agent
                    await team.asave()
            
            teams.append({
                'team': team,
                'agents': team_agents
            })
        
        # Execute teams in parallel
        results = await self._execute_teams_parallel(teams, task)
        
        return {
            'experiment_id': str(myth_experiment.id),
            'orchestration_id': str(orchestration.id),
            'teams': [
                {
                    'name': t['team'].name,
                    'team_id': str(t['team'].id),
                    'agents': [
                        {
                            'name': a.template.name,
                            'llm': f"{a.runtime_llm_provider}:{a.runtime_llm_model}"
                        } for a in t['agents']
                    ]
                } for t in teams
            ],
            'task': task,
            'status': 'running'
        }
    
    async def _execute_teams_parallel(self, teams: List[Dict], task: str):
        """Execute all teams in parallel"""
        
        tasks = []
        for team_data in teams:
            team_task = self._execute_team(team_data['team'], team_data['agents'], task)
            tasks.append(team_task)
        
        results = await asyncio.gather(*tasks)
        return results
    
    async def _execute_team(self, team: AgentTeam, agents: List[AgentInstance], task: str):
        """Execute a single team"""
        
        # Leader processes first
        leader = team.leader_agent
        leader_result = await self.agent_service.execute_agent_with_llm(
            leader, 
            task,
            {'role': 'leader', 'team_id': team.id}
        )
        
        # Other agents process based on leader's output
        member_tasks = []
        for agent in agents:
            if agent.id != leader.id:
                member_task = self.agent_service.execute_agent_with_llm(
                    agent,
                    f"Based on the leader's analysis: {leader_result['response'][:200]}... \n\nYour task: {task}",
                    {'role': 'member', 'team_id': team.id, 'leader_context': leader_result}
                )
                member_tasks.append(member_task)
        
        member_results = await asyncio.gather(*member_tasks)
        
        return {
            'team_id': team.id,
            'leader_result': leader_result,
            'member_results': member_results
        }
```

### 6. API Endpoints

Create endpoints for experiment management:

```python
# backend/mythology_lab/views.py - Add these views

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .experiments.multi_llm_experiment import MultiLLMExperimentRunner

class MultiLLMExperimentViewSet(viewsets.ViewSet):
    """API for multi-LLM experiments"""
    
    @action(detail=False, methods=['post'])
    async def create_comparison(self, request):
        """Create a comparison experiment between teams"""
        
        runner = MultiLLMExperimentRunner()
        
        # Example request body:
        # {
        #     "experiment_name": "GPT vs Claude vs Local Models",
        #     "task": "Analyze the market potential for AI-powered fitness apps",
        #     "teams": [
        #         {
        #             "name": "GPT-Only Team",
        #             "team_type": "homogeneous",
        #             "agents": [
        #                 {"template_name": "Research Agent", "llm_provider": "openai", "llm_model": "gpt-4"},
        #                 {"template_name": "Business Agent", "llm_provider": "openai", "llm_model": "gpt-4"},
        #                 {"template_name": "Marketing Agent", "llm_provider": "openai", "llm_model": "gpt-4"}
        #             ]
        #         },
        #         {
        #             "name": "Mixed Model Team",
        #             "team_type": "heterogeneous",
        #             "agents": [
        #                 {"template_name": "Research Agent", "llm_provider": "openai", "llm_model": "gpt-4"},
        #                 {"template_name": "Business Agent", "llm_provider": "anthropic", "llm_model": "claude-3-opus"},
        #                 {"template_name": "Marketing Agent", "llm_provider": "ollama", "llm_model": "llama2"}
        #             ]
        #         }
        #     ]
        # }
        
        result = await runner.create_comparison_experiment(
            experiment_name=request.data['experiment_name'],
            task=request.data['task'],
            team_configs=request.data['teams']
        )
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get experiment results with mythology analysis"""
        
        from mythology_lab.models import MythologyExperiment, MythologyEvent
        from agent_orchestra.models import AgentTeam, CrossModelInteraction
        
        experiment = MythologyExperiment.objects.get(pk=pk)
        teams = AgentTeam.objects.filter(mythology_experiment=experiment)
        
        results = {
            'experiment': {
                'id': str(experiment.id),
                'name': experiment.experiment_name,
                'status': 'completed' if experiment.completed else 'running'
            },
            'teams': []
        }
        
        for team in teams:
            # Get mythology events for this team
            team_agents = team.members.all()
            agent_ids = [a.id for a in team_agents]
            
            mythology_events = MythologyEvent.objects.filter(
                agent_id__in=agent_ids
            )
            
            # Get cross-model interactions
            interactions = CrossModelInteraction.objects.filter(
                from_agent__in=team_agents
            )
            
            team_result = {
                'name': team.name,
                'type': team.team_type,
                'mythology_events': mythology_events.count(),
                'cross_model_interactions': interactions.count(),
                'average_semantic_similarity': interactions.aggregate(
                    avg_similarity=models.Avg('semantic_similarity')
                )['avg_similarity'] or 1.0,
                'agents': [
                    {
                        'name': agent.template.name,
                        'llm': f"{agent.runtime_llm_provider}:{agent.runtime_llm_model}",
                        'mythology_created': mythology_events.filter(agent_id=agent.id).count()
                    }
                    for agent in team_agents
                ]
            }
            
            results['teams'].append(team_result)
        
        return Response(results)
```

### 7. Frontend Updates

Add UI for configuring multi-LLM experiments:

```tsx
// donkey-betz-frontend/src/features/mythology-lab/components/MultiLLMExperiment.tsx

import React, { useState } from 'react';
import { Card, Button, Select, Input, Table, Tag } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';

interface AgentConfig {
  template_name: string;
  llm_provider: string;
  llm_model: string;
}

interface TeamConfig {
  name: string;
  team_type: 'homogeneous' | 'heterogeneous';
  agents: AgentConfig[];
}

const LLM_PROVIDERS = [
  { value: 'openai', label: 'OpenAI (GPT)', models: ['gpt-4', 'gpt-4-turbo-preview', 'gpt-3.5-turbo'] },
  { value: 'anthropic', label: 'Anthropic (Claude)', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-2.1'] },
  { value: 'google', label: 'Google (Gemini)', models: ['gemini-pro', 'gemini-ultra'] },
  { value: 'ollama', label: 'Ollama (Local)', models: ['llama2', 'mistral', 'codellama', 'vicuna'] },
  { value: 'cohere', label: 'Cohere', models: ['command', 'command-light'] },
  { value: 'mistral', label: 'Mistral AI', models: ['mistral-tiny', 'mistral-small', 'mistral-medium'] },
];

const AGENT_TEMPLATES = [
  'Research Agent',
  'Business Agent',
  'Marketing Agent',
  'Technical Agent',
  'Financial Agent',
  'Content Agent',
  'Creative Agent',
];

export const MultiLLMExperiment: React.FC = () => {
  const [experimentName, setExperimentName] = useState('');
  const [task, setTask] = useState('');
  const [teams, setTeams] = useState<TeamConfig[]>([
    {
      name: 'Control Team (GPT-4 Only)',
      team_type: 'homogeneous',
      agents: [
        { template_name: 'Research Agent', llm_provider: 'openai', llm_model: 'gpt-4' },
        { template_name: 'Business Agent', llm_provider: 'openai', llm_model: 'gpt-4' },
        { template_name: 'Marketing Agent', llm_provider: 'openai', llm_model: 'gpt-4' },
      ]
    },
    {
      name: 'Mixed Model Team',
      team_type: 'heterogeneous',
      agents: [
        { template_name: 'Research Agent', llm_provider: 'openai', llm_model: 'gpt-4' },
        { template_name: 'Business Agent', llm_provider: 'anthropic', llm_model: 'claude-3-opus' },
        { template_name: 'Marketing Agent', llm_provider: 'ollama', llm_model: 'llama2' },
      ]
    }
  ]);

  const addTeam = () => {
    setTeams([...teams, {
      name: `Team ${teams.length + 1}`,
      team_type: 'heterogeneous',
      agents: []
    }]);
  };

  const addAgent = (teamIndex: number) => {
    const newTeams = [...teams];
    newTeams[teamIndex].agents.push({
      template_name: AGENT_TEMPLATES[0],
      llm_provider: 'openai',
      llm_model: 'gpt-4'
    });
    setTeams(newTeams);
  };

  const updateAgent = (teamIndex: number, agentIndex: number, field: keyof AgentConfig, value: string) => {
    const newTeams = [...teams];
    newTeams[teamIndex].agents[agentIndex][field] = value;
    
    // Update team type based on LLM diversity
    const providers = new Set(newTeams[teamIndex].agents.map(a => a.llm_provider));
    newTeams[teamIndex].team_type = providers.size === 1 ? 'homogeneous' : 'heterogeneous';
    
    setTeams(newTeams);
  };

  const runExperiment = async () => {
    const response = await fetch('/api/mythology/experiments/multi-llm/create_comparison/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${localStorage.getItem('authToken')}`
      },
      body: JSON.stringify({
        experiment_name: experimentName,
        task: task,
        teams: teams
      })
    });
    
    const result = await response.json();
    console.log('Experiment created:', result);
  };

  return (
    <div className="multi-llm-experiment">
      <Card title="Multi-LLM Team Experiment" className="mb-4">
        <div className="mb-4">
          <Input
            placeholder="Experiment Name"
            value={experimentName}
            onChange={(e) => setExperimentName(e.target.value)}
            className="mb-2"
          />
          <Input.TextArea
            placeholder="Task for all teams (e.g., 'Analyze the market for AI fitness apps')"
            value={task}
            onChange={(e) => setTask(e.target.value)}
            rows={3}
          />
        </div>
      </Card>

      {teams.map((team, teamIndex) => (
        <Card 
          key={teamIndex} 
          title={
            <div className="flex justify-between items-center">
              <Input
                value={team.name}
                onChange={(e) => {
                  const newTeams = [...teams];
                  newTeams[teamIndex].name = e.target.value;
                  setTeams(newTeams);
                }}
                style={{ width: 300 }}
              />
              <Tag color={team.team_type === 'homogeneous' ? 'blue' : 'purple'}>
                {team.team_type}
              </Tag>
            </div>
          }
          className="mb-4"
        >
          <Table
            dataSource={team.agents}
            columns={[
              {
                title: 'Agent Template',
                dataIndex: 'template_name',
                render: (value, _, index) => (
                  <Select
                    value={value}
                    onChange={(v) => updateAgent(teamIndex, index, 'template_name', v)}
                    style={{ width: 150 }}
                  >
                    {AGENT_TEMPLATES.map(t => (
                      <Select.Option key={t} value={t}>{t}</Select.Option>
                    ))}
                  </Select>
                )
              },
              {
                title: 'LLM Provider',
                dataIndex: 'llm_provider',
                render: (value, _, index) => (
                  <Select
                    value={value}
                    onChange={(v) => updateAgent(teamIndex, index, 'llm_provider', v)}
                    style={{ width: 150 }}
                  >
                    {LLM_PROVIDERS.map(p => (
                      <Select.Option key={p.value} value={p.value}>{p.label}</Select.Option>
                    ))}
                  </Select>
                )
              },
              {
                title: 'Model',
                dataIndex: 'llm_model',
                render: (value, record, index) => {
                  const provider = LLM_PROVIDERS.find(p => p.value === record.llm_provider);
                  return (
                    <Select
                      value={value}
                      onChange={(v) => updateAgent(teamIndex, index, 'llm_model', v)}
                      style={{ width: 150 }}
                    >
                      {provider?.models.map(m => (
                        <Select.Option key={m} value={m}>{m}</Select.Option>
                      ))}
                    </Select>
                  );
                }
              },
              {
                title: 'Action',
                render: (_, __, index) => (
                  <Button 
                    icon={<DeleteOutlined />} 
                    danger
                    onClick={() => {
                      const newTeams = [...teams];
                      newTeams[teamIndex].agents.splice(index, 1);
                      setTeams(newTeams);
                    }}
                  />
                )
              }
            ]}
            pagination={false}
          />
          <Button 
            icon={<PlusOutlined />} 
            onClick={() => addAgent(teamIndex)}
            className="mt-2"
          >
            Add Agent
          </Button>
        </Card>
      ))}

      <div className="flex gap-4">
        <Button icon={<PlusOutlined />} onClick={addTeam}>
          Add Team
        </Button>
        <Button type="primary" onClick={runExperiment}>
          Run Experiment
        </Button>
      </div>
    </div>
  );
};
```

## Implementation Steps

### Phase 1: Database & Models (Day 1)
1. Create and run migrations for new fields
2. Add AgentTeam and CrossModelInteraction models
3. Update existing models with LLM configuration

### Phase 2: LLM Provider Service (Day 2)
1. Implement BaseLLMProvider abstract class
2. Create providers for OpenAI, Anthropic, Ollama
3. Add provider for Google, Cohere, Mistral (if API keys available)
4. Test each provider independently

### Phase 3: Agent Service Updates (Day 3)
1. Update agent execution to use MultiLLMService
2. Implement cross-model interaction tracking
3. Add mythology detection for multi-LLM responses
4. Test agent execution with different providers

### Phase 4: Experiment Runner (Day 4)
1. Implement MultiLLMExperimentRunner
2. Create team comparison logic
3. Add parallel execution support
4. Integrate with Mythology Lab tracking

### Phase 5: API & Frontend (Day 5)
1. Add API endpoints for experiment management
2. Create React components for experiment configuration
3. Add results visualization
4. Test end-to-end flow

## Environment Variables Needed

Add to `.env`:
```bash
# LLM Providers
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
GOOGLE_AI_API_KEY=your_key_here
COHERE_API_KEY=your_key_here
MISTRAL_API_KEY=your_key_here
GROQ_API_KEY=your_key_here

# Local LLM
OLLAMA_BASE_URL=http://localhost:11434
```

## Testing Scenarios

### 1. Homogeneous vs Heterogeneous Teams
- Team A: All GPT-4 agents
- Team B: Mix of GPT-4, Claude, and Llama2
- Compare: Coordination efficiency, mythology creation rate

### 2. Cross-Model Communication Test
- Give teams a task requiring heavy collaboration
- Measure semantic similarity in cross-model messages
- Track communication breakdowns

### 3. Mythology Propagation Test
- Inject known myths into one agent
- Track how myths spread differently across model boundaries
- Compare mutation rates between same-model vs cross-model

### 4. Performance Comparison
- Same task to all teams
- Measure: completion time, quality scores, resource usage
- Identify optimal model combinations

## Expected Outcomes

1. **Cross-Model Friction**: Expect 10-30% semantic loss in cross-model communication
2. **Mythology Mutations**: Different models may amplify or dampen mythological elements
3. **Team Dynamics**: Homogeneous teams likely more efficient but less creative
4. **Model Strengths**: Each model will show different strengths (e.g., Claude for nuance, GPT for structure)

## Future Enhancements

1. **CrewAI Integration**: Add CrewAI as an orchestration option
2. **Dynamic Team Formation**: AI selects optimal team composition
3. **Real-time Visualization**: Live view of agent interactions
4. **Automated Analysis**: ML models to predict team performance
5. **Model Fine-tuning**: Adjust models based on team performance

This implementation provides a robust framework for experimenting with multi-LLM agent teams while leveraging the existing Mythology Lab infrastructure for tracking and analysis.