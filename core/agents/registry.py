"""
Agent Registry System - Unified Agent Discovery and Orchestration

This module provides the centralized registry for managing and discovering agents
in the Unified Donkey Betz Platform. It bridges the database models with runtime
agent orchestration, enabling dynamic agent discovery, routing, and execution.

Features:
- Dynamic agent discovery and routing
- Capability-based agent selection
- Load balancing and performance tracking
- Cache-optimized for high performance
- Integration with Django models and ML pipeline

Session 392: Migrated from agents/registry.py to core/agents/registry.py
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone

# Updated import path - use canonical location
from core.models.agents_registry import (
    UnifiedAgentTemplate,
    AgentExecution,
    AgentSpecialization,
    AgentStatus,
    AgentPriority
)

logger = logging.getLogger(__name__)


@dataclass
class AgentCapability:
    """Represents an agent capability with metadata"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    success_rate: float = 0.0
    avg_execution_time: float = 0.0


@dataclass
class AgentPerformanceStats:
    """Agent performance statistics"""
    agent_id: str
    total_executions: int
    success_rate: float
    avg_response_time: float
    last_execution: Optional[datetime]
    load_factor: float = 0.0


@dataclass
class RegistryStats:
    """Registry-wide statistics"""
    total_agents: int
    active_agents: int
    total_executions: int
    avg_success_rate: float
    popular_specializations: Dict[str, int]


class AgentRegistry:
    """
    Centralized agent registry for discovery, routing, and orchestration.

    This class provides the runtime interface to the agent system, bridging
    Django models with the execution environment.
    """

    def __init__(self, cache_timeout: int = 300):
        self.cache_timeout = cache_timeout
        self.logger = logging.getLogger(__name__)
        self._performance_cache: Dict[str, AgentPerformanceStats] = {}
        self._last_cache_refresh = datetime.now()
        self._last_resolution_metadata = {
            'fallback_used': False,
            'fallback_type': None,
            'resolution_error': None,
            'resolution_source': 'init',
        }

        # Initialize registry
        self._refresh_agent_cache()

    def _refresh_agent_cache(self):
        """Refresh agent cache from database"""
        try:
            # Cache all active agents - only serialize primitive data, not relations
            active_agents = UnifiedAgentTemplate.objects.filter(
                is_active=True
            ).values(
                'id', 'name', 'display_name', 'specialization',
                'capabilities', 'routing_keywords', 'system_prompt',
                'llm_provider', 'llm_model', 'llm_config',
                'performance_metrics', 'is_active', 'is_verified',
                'created_at', 'updated_at'
            )

            # Convert QuerySet to dict indexed by name
            agent_data = {}
            for agent in active_agents:
                # Convert UUID to string for JSON serialization
                agent_copy = dict(agent)
                agent_copy['id'] = str(agent_copy['id'])

                # Store by name for easy lookup
                agent_name = agent_copy['name']
                agent_data[agent_name] = agent_copy

            cache.set('agent_registry_data', agent_data, self.cache_timeout)
            self._last_cache_refresh = datetime.now()
            self.logger.info(f"Refreshed agent cache with {len(agent_data)} agents")

        except Exception as e:
            self.logger.error(f"Failed to refresh agent cache: {e}")

    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent by name"""
        try:
            # Try cache first
            agent_data = cache.get('agent_registry_data', {})

            if agent_name in agent_data:
                self._last_resolution_metadata = {
                    'fallback_used': False,
                    'fallback_type': None,
                    'resolution_error': None,
                    'resolution_source': 'cache_hit',
                }
                return agent_data[agent_name]

            # Cache miss - refresh and try again
            self._refresh_agent_cache()
            agent_data = cache.get('agent_registry_data', {})

            self._last_resolution_metadata = {
                'fallback_used': False,
                'fallback_type': None,
                'resolution_error': None,
                'resolution_source': 'cache_refresh',
            }
            return agent_data.get(agent_name)

        except Exception as e:
            self._last_resolution_metadata = {
                'fallback_used': False,
                'fallback_type': 'registry_error',
                'resolution_error': f"{type(e).__name__}: {e}",
                'resolution_source': 'error',
            }
            self.logger.debug(
                "Agent registry lookup failed: %s",
                {**self._last_resolution_metadata, 'agent_name': agent_name},
            )
            return None

    def list_agents(self,
                   specialization: Optional[str] = None,
                   capabilities: Optional[List[str]] = None,
                   active_only: bool = True) -> List[Dict[str, Any]]:
        """List agents with optional filters"""
        try:
            agent_data = cache.get('agent_registry_data', {})

            if not agent_data:
                self._refresh_agent_cache()
                agent_data = cache.get('agent_registry_data', {})

            agents = list(agent_data.values())

            # Apply filters
            if specialization:
                agents = [a for a in agents if a['specialization'] == specialization]

            if capabilities:
                agents = [
                    a for a in agents
                    if any(cap in a.get('capabilities', []) for cap in capabilities)
                ]

            return agents

        except Exception as e:
            self.logger.error(f"Error listing agents: {e}")
            return []

    def find_best_agent(self,
                       task_description: str,
                       required_capabilities: List[str] = None,
                       preferred_specialization: str = None) -> Optional[Dict[str, Any]]:
        """Find the best agent for a given task using intelligent routing"""
        try:
            agents = self.list_agents()

            if not agents:
                return None

            scored_agents = []

            for agent in agents:
                score = self._calculate_agent_score(
                    agent, task_description, required_capabilities, preferred_specialization
                )
                if score > 0:
                    scored_agents.append((agent, score))

            if not scored_agents:
                return None

            # Sort by score (descending) and return best match
            scored_agents.sort(key=lambda x: x[1], reverse=True)
            best_agent = scored_agents[0][0]

            self.logger.info(
                f"Selected agent '{best_agent['name']}' "
                f"(score: {scored_agents[0][1]:.2f}) for task"
            )

            return best_agent

        except Exception as e:
            self.logger.error(f"Error finding best agent: {e}")
            return None

    def _calculate_agent_score(self,
                             agent: Dict[str, Any],
                             task_description: str,
                             required_capabilities: List[str] = None,
                             preferred_specialization: str = None) -> float:
        """Calculate relevance score for an agent given a task"""
        score = 0.0

        # Specialization match
        if preferred_specialization and agent['specialization'] == preferred_specialization:
            score += 10.0

        # Capability match
        if required_capabilities:
            agent_caps = agent.get('capabilities', [])
            matching_caps = set(required_capabilities) & set(agent_caps)
            score += len(matching_caps) * 5.0

        # Keyword matching
        keywords = agent.get('routing_keywords', [])
        task_lower = task_description.lower()

        for keyword in keywords:
            if keyword.lower() in task_lower:
                score += 2.0

        # Performance bonus (if verified)
        if agent.get('is_verified'):
            score += 3.0

        # Performance metrics
        metrics = agent.get('performance_metrics', {})
        success_rate = metrics.get('success_rate', 0.5)
        score += success_rate * 5.0

        return score

    def register_agent(self, agent_name: str, agent_config: Dict[str, Any]) -> bool:
        """Register a new agent dynamically"""
        try:
            # Check if agent already exists
            existing = UnifiedAgentTemplate.objects.filter(name=agent_name).first()

            if existing:
                self.logger.warning(f"Agent {agent_name} already exists")
                return False

            # Create new agent template
            agent = UnifiedAgentTemplate.objects.create(
                name=agent_name,
                display_name=agent_config.get('display_name', agent_name),
                description=agent_config.get('description', ''),
                specialization=agent_config.get('specialization', AgentSpecialization.RESEARCH),
                capabilities=agent_config.get('capabilities', []),
                system_prompt=agent_config.get('system_prompt', ''),
                routing_keywords=agent_config.get('routing_keywords', []),
                llm_provider=agent_config.get('llm_provider', 'openai'),
                llm_model=agent_config.get('llm_model', 'gpt-5-mini'),
                llm_config=agent_config.get('llm_config', {}),
                is_active=True
            )

            # Refresh cache
            self._refresh_agent_cache()

            self.logger.info(f"Successfully registered agent: {agent_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_name}: {e}")
            return False

    def execute_agent(self,
                     agent_name: str,
                     task_data: Dict[str, Any],
                     priority: str = AgentPriority.NORMAL) -> Optional[str]:
        """Execute an agent with given task data"""
        try:
            agent_template = UnifiedAgentTemplate.objects.get(name=agent_name, is_active=True)
            task_data = dict(task_data or {})
            task_data['_resolution_metadata'] = getattr(
                self,
                '_last_resolution_metadata',
                {
                    'fallback_used': False,
                    'fallback_type': None,
                    'resolution_error': None,
                    'resolution_source': 'registry_execute',
                }
            )
            self.logger.debug(
                "Registry execution resolution metadata: %s",
                {**task_data['_resolution_metadata'], 'agent_name': agent_name},
            )

            # Session 758: Build context tracking for Integration Health observability
            try:
                from core.services.context_tracking import build_context_tracking
                task = task_data.get('task', '') or str(task_data)[:200]
                context_tracking = build_context_tracking(agent_name, task)
                task_data['context_injected'] = context_tracking
            except Exception as e:
                self.logger.debug(f"Context tracking unavailable: {e}")

            # Create execution record
            execution = AgentExecution.objects.create(
                template=agent_template,
                input_data=task_data,
                priority=priority,
                status=AgentStatus.PENDING
            )

            # Here you would integrate with your actual execution engine
            # For now, we'll mark as initialized
            execution.status = AgentStatus.INITIALIZING
            execution.save()

            # Convert UUID to string for JSON serialization
            execution_id_str = str(execution.id)
            self.logger.info(f"Initiated execution of agent {agent_name} (ID: {execution_id_str})")
            return execution_id_str

        except UnifiedAgentTemplate.DoesNotExist:
            self._last_resolution_metadata = {
                'fallback_used': False,
                'fallback_type': 'registry_miss',
                'resolution_error': 'UnifiedAgentTemplate.DoesNotExist',
                'resolution_source': 'missing_template',
            }
            self.logger.debug(
                "Registry execution lookup miss: %s",
                {**self._last_resolution_metadata, 'agent_name': agent_name},
            )
            return {
                'success': False,
                'error': f"Unknown agent template: {agent_name}",
                'resolution_error': 'UnifiedAgentTemplate.DoesNotExist',
                'failure_type': 'missing_template',
                'agent_name': agent_name,
                'agent_id': None,
                'resolution_metadata': dict(self._last_resolution_metadata),
            }
        except Exception as e:
            self._last_resolution_metadata = {
                'fallback_used': False,
                'fallback_type': 'registry_error',
                'resolution_error': f"{type(e).__name__}: {e}",
                'resolution_source': 'execution_error',
            }
            self.logger.debug(
                "Registry execution failed: %s",
                {**self._last_resolution_metadata, 'agent_name': agent_name},
            )
            return {
                'success': False,
                'error': str(e),
                'resolution_error': f"{type(e).__name__}: {e}",
                'failure_type': 'execution_error',
                'agent_name': agent_name,
                'agent_id': None,
                'resolution_metadata': dict(self._last_resolution_metadata),
            }

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent execution"""
        try:
            execution = AgentExecution.objects.get(id=execution_id)

            return {
                'id': execution.id,
                'agent_name': execution.template.name,
                'status': execution.status,
                'priority': execution.priority,
                'input_data': execution.input_data,
                'output_data': execution.output_data,
                'error_message': execution.error_message,
                'started_at': execution.started_at,
                'completed_at': execution.completed_at,
                'execution_time_ms': (getattr(execution, 'execution_time_seconds', 0) or 0) * 1000 if hasattr(execution, 'execution_time_seconds') and getattr(execution, 'execution_time_seconds', None) is not None else 0
            }

        except AgentExecution.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error getting execution status: {e}")
            return None

    def get_agent_capabilities(self, agent_name: str) -> List[AgentCapability]:
        """Get detailed capabilities for an agent"""
        agent = self.get_agent(agent_name)
        if not agent:
            return []

        capabilities = []
        for cap_name in agent.get('capabilities', []):
            # This would be enhanced with actual capability metadata
            capability = AgentCapability(
                name=cap_name,
                description=f"Capability: {cap_name}",
                input_types=["text", "json"],
                output_types=["text", "json"],
                success_rate=0.85,  # Would be calculated from metrics
                avg_execution_time=2.5  # Would be calculated from metrics
            )
            capabilities.append(capability)

        return capabilities

    def get_registry_stats(self) -> RegistryStats:
        """Get comprehensive registry statistics"""
        try:
            # Get basic counts
            total_agents = UnifiedAgentTemplate.objects.count()
            active_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
            total_executions = AgentExecution.objects.count()

            # Calculate average success rate
            completed_executions = AgentExecution.objects.filter(
                status=AgentStatus.COMPLETED
            ).count()
            avg_success_rate = completed_executions / total_executions if total_executions > 0 else 0.0

            # Get popular specializations
            specialization_counts = UnifiedAgentTemplate.objects.filter(
                is_active=True
            ).values('specialization').annotate(
                count=Count('id')
            ).order_by('-count')

            popular_specializations = {
                item['specialization']: item['count']
                for item in specialization_counts[:10]
            }

            return RegistryStats(
                total_agents=total_agents,
                active_agents=active_agents,
                total_executions=total_executions,
                avg_success_rate=avg_success_rate,
                popular_specializations=popular_specializations
            )

        except Exception as e:
            self.logger.error(f"Error calculating registry stats: {e}")
            return RegistryStats(
                total_agents=0,
                active_agents=0,
                total_executions=0,
                avg_success_rate=0.0,
                popular_specializations={}
            )

    def health_check(self) -> Dict[str, Any]:
        """Perform registry health check"""
        try:
            stats = self.get_registry_stats()
            cache_status = cache.get('agent_registry_data') is not None

            return {
                'status': 'healthy',
                'active_agents': stats.active_agents,
                'cache_healthy': cache_status,
                'last_cache_refresh': self._last_cache_refresh.isoformat(),
                'avg_success_rate': stats.avg_success_rate,
                'timestamp': timezone.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }


# Global registry instance - singleton pattern
_registry_instance = None

def get_agent_registry() -> AgentRegistry:
    """Get the global agent registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AgentRegistry()
    return _registry_instance


# Convenience functions for common operations
def get_agent(name: str) -> Optional[Dict[str, Any]]:
    """Get agent by name (convenience function)"""
    return get_agent_registry().get_agent(name)


def list_agents(specialization: str = None) -> List[Dict[str, Any]]:
    """List agents (convenience function)"""
    return get_agent_registry().list_agents(specialization=specialization)


def find_best_agent(task: str, capabilities: List[str] = None) -> Optional[Dict[str, Any]]:
    """Find best agent for task (convenience function)"""
    return get_agent_registry().find_best_agent(task, capabilities)


def execute_agent(name: str, task_data: Dict[str, Any]) -> Optional[str]:
    """Execute agent (convenience function)"""
    return get_agent_registry().execute_agent(name, task_data)


# Initialize the global registry
agent_registry = get_agent_registry()
