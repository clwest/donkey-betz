"""
Agent Executor Registry - Central Execution Management

This module connects the passive agent registry with active executors.
It transforms registered agents into working systems that can execute tasks,
use tools, make API calls, and generate real deliverables.

Key Features:
- Automatic executor registration and discovery
- Dynamic executor loading and configuration
- Execution routing and load balancing
- Performance monitoring and optimization
- Real-time execution status tracking
- Integration with Django models and WebSocket updates
"""

import logging
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from django.utils import timezone

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution, AgentStatus
from agents.executors.base_executor import (
    BaseAgentExecutor,
    ExecutionContext,
    ExecutionResult,
    ExecutionStatus,
    ExecutionPriority,
    AgentExecutorRegistry
)

# Import specific executors
from agents.executors.income_builder_executor import IncomeBuilderExecutor
from agents.executors.content_creator_executor import ContentCreatorExecutor
from agents.executors.payment_processor_executor import PaymentProcessorExecutor

logger = logging.getLogger(__name__)


class ExecutorRegistrationSystem:
    """
    System for registering and managing agent executors.
    Bridges the gap between agent templates and executable implementations.
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExecutorRegistration")
        self.executor_registry = AgentExecutorRegistry()
        self.executor_mappings: Dict[str, Type[BaseAgentExecutor]] = {}
        self.execution_pool = ThreadPoolExecutor(max_workers=10)

        # Performance tracking
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0

        # Initialize executor mappings
        self._initialize_executor_mappings()
        self._register_default_executors()

        self.logger.info("Executor registration system initialized")

    def _initialize_executor_mappings(self):
        """Initialize mappings between agent names and executor classes"""

        # Core revenue-generating executors
        self.executor_mappings.update({
            'income_builder': IncomeBuilderExecutor,
            'ai_income_builder': IncomeBuilderExecutor,
            'revenue_builder': IncomeBuilderExecutor,
            'opportunity_analyzer': IncomeBuilderExecutor,

            'content_creator': ContentCreatorExecutor,
            'blog_writer': ContentCreatorExecutor,
            'copywriter': ContentCreatorExecutor,
            'social_media_creator': ContentCreatorExecutor,
            'marketing_writer': ContentCreatorExecutor,

            'payment_processor': PaymentProcessorExecutor,
            'invoice_generator': PaymentProcessorExecutor,
            'billing_manager': PaymentProcessorExecutor,
            'revenue_tracker': PaymentProcessorExecutor,
            'subscription_manager': PaymentProcessorExecutor
        })

        # Add generic mappings for common agent types
        self._add_generic_mappings()

    def _add_generic_mappings(self):
        """Add generic mappings for common agent specializations"""

        # Content-related agents use ContentCreatorExecutor
        content_agents = [
            'content_writer', 'article_writer', 'seo_writer', 'technical_writer',
            'creative_writer', 'email_writer', 'social_content_creator'
        ]
        for agent_name in content_agents:
            self.executor_mappings[agent_name] = ContentCreatorExecutor

        # Business/revenue agents use IncomeBuilderExecutor
        business_agents = [
            'business_analyzer', 'market_researcher', 'opportunity_finder',
            'freelance_advisor', 'career_coach', 'business_consultant'
        ]
        for agent_name in business_agents:
            self.executor_mappings[agent_name] = IncomeBuilderExecutor

    def _register_default_executors(self):
        """Register default executors with the registry"""

        # Get default configuration
        default_config = self._get_default_config()

        # Register priority executors
        priority_executors = [
            ('income_builder', IncomeBuilderExecutor),
            ('content_creator', ContentCreatorExecutor),
            ('payment_processor', PaymentProcessorExecutor)
        ]

        for agent_name, executor_class in priority_executors:
            try:
                executor = executor_class(agent_name, default_config)
                self.executor_registry.register_executor(agent_name, executor)
                self.logger.info(f"Registered priority executor: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to register executor {agent_name}: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for executors"""

        import os

        return {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'stripe_api_key': os.getenv('STRIPE_API_KEY'),
            'default_timeout': 300,
            'max_retries': 3,
            'enable_monitoring': True,
            'enable_caching': True,
            'output_directory': 'agent_outputs'
        }

    async def register_agent_executors_from_db(self):
        """Register executors for all active agents in the database"""

        try:
            # Get all active agent templates
            active_agents = UnifiedAgentTemplate.objects.filter(is_active=True)

            registered_count = 0
            skipped_count = 0

            for agent_template in active_agents:
                agent_name = agent_template.name.lower()

                # Skip if already registered
                if self.executor_registry.get_executor(agent_name):
                    skipped_count += 1
                    continue

                # Find appropriate executor class
                executor_class = self._find_executor_class(agent_template)

                if executor_class:
                    try:
                        # Create executor configuration from template
                        config = self._create_executor_config(agent_template)

                        # Create and register executor
                        executor = executor_class(agent_name, config)
                        self.executor_registry.register_executor(agent_name, executor)

                        registered_count += 1
                        self.logger.info(f"Registered executor for agent: {agent_name}")

                    except Exception as e:
                        self.logger.error(f"Failed to create executor for {agent_name}: {e}")
                        skipped_count += 1
                else:
                    self.logger.warning(f"No executor class found for agent: {agent_name}")
                    skipped_count += 1

            self.logger.info(
                f"Agent executor registration complete: "
                f"{registered_count} registered, {skipped_count} skipped"
            )

            return {
                'registered': registered_count,
                'skipped': skipped_count,
                'total_executors': len(self.executor_registry.list_executors())
            }

        except Exception as e:
            self.logger.error(f"Failed to register agent executors from DB: {e}")
            return {'error': str(e)}

    def _find_executor_class(self, agent_template: UnifiedAgentTemplate) -> Optional[Type[BaseAgentExecutor]]:
        """Find appropriate executor class for an agent template"""

        agent_name = agent_template.name.lower()

        # Direct mapping lookup
        if agent_name in self.executor_mappings:
            return self.executor_mappings[agent_name]

        # Specialization-based mapping
        specialization = agent_template.specialization

        specialization_mapping = {
            'content': ContentCreatorExecutor,
            'business': IncomeBuilderExecutor,
            'financial': PaymentProcessorExecutor,
            'marketing': ContentCreatorExecutor,
            'research': IncomeBuilderExecutor
        }

        if specialization in specialization_mapping:
            return specialization_mapping[specialization]

        # Capability-based mapping
        capabilities = agent_template.capabilities or []

        if any(cap in capabilities for cap in ['content_creation', 'writing', 'copywriting']):
            return ContentCreatorExecutor
        elif any(cap in capabilities for cap in ['payment_processing', 'billing', 'invoicing']):
            return PaymentProcessorExecutor
        elif any(cap in capabilities for cap in ['income_generation', 'business_analysis', 'opportunity_analysis']):
            return IncomeBuilderExecutor

        # Default to IncomeBuilderExecutor for unknown agents
        return IncomeBuilderExecutor

    def _create_executor_config(self, agent_template: UnifiedAgentTemplate) -> Dict[str, Any]:
        """Create executor configuration from agent template"""

        config = self._get_default_config()

        # Add template-specific configuration
        config.update({
            'agent_id': str(agent_template.id),
            'agent_name': agent_template.name,
            'specialization': agent_template.specialization,
            'capabilities': agent_template.capabilities or [],
            'llm_provider': agent_template.llm_provider,
            'llm_model': agent_template.llm_model,
            'llm_config': agent_template.llm_config or {},
            'system_prompt': agent_template.system_prompt,
            'required_tools': agent_template.required_tools or [],
            'optional_tools': agent_template.optional_tools or []
        })

        return config

    async def execute_agent(self,
                          agent_name: str,
                          task_data: Dict[str, Any],
                          user_id: Optional[str] = None,
                          priority: ExecutionPriority = ExecutionPriority.NORMAL,
                          timeout: int = 300) -> ExecutionResult:
        """Execute an agent with full tracking and database integration"""

        self.total_executions += 1

        try:
            # Create execution context
            context = ExecutionContext(
                task_id=f"{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.total_executions}",
                user_id=user_id,
                priority=priority,
                timeout_seconds=timeout,
                output_dir=Path(f"agent_outputs/{agent_name}"),
                metadata={'agent_name': agent_name, 'execution_number': self.total_executions}
            )

            # Create database execution record
            db_execution = await self._create_db_execution_record(agent_name, task_data, context)

            try:
                # Execute agent through registry
                result = await self.executor_registry.execute_agent(agent_name, task_data, context)

                # Update database record
                await self._update_db_execution_record(db_execution, result)

                if result.status == ExecutionStatus.COMPLETED:
                    self.successful_executions += 1
                else:
                    self.failed_executions += 1

                self.logger.info(
                    f"Agent execution completed: {agent_name} - "
                    f"Status: {result.status.value}, "
                    f"Files: {len(result.files_created)}, "
                    f"Cost: ${result.total_cost}"
                )

                return result

            except Exception as e:
                self.logger.error(f"Agent execution failed: {agent_name} - {e}")

                # Mark execution as failed in database
                if db_execution:
                    await self._mark_execution_failed(db_execution, str(e))

                self.failed_executions += 1

                # Create error result
                error_result = ExecutionResult(
                    task_id=context.task_id,
                    status=ExecutionStatus.FAILED,
                    output={'error': str(e)},
                    error_message=str(e)
                )

                return error_result

        except Exception as e:
            self.logger.error(f"Critical execution error for {agent_name}: {e}")
            self.failed_executions += 1

            # Create critical error result
            return ExecutionResult(
                task_id=f"{agent_name}_error_{self.total_executions}",
                status=ExecutionStatus.FAILED,
                output={'critical_error': str(e)},
                error_message=f"Critical error: {str(e)}"
            )

    async def _create_db_execution_record(self,
                                        agent_name: str,
                                        task_data: Dict[str, Any],
                                        context: ExecutionContext) -> Optional[AgentExecution]:
        """Create database record for execution tracking"""

        try:
            # Get agent template
            agent_template = UnifiedAgentTemplate.objects.filter(
                name__iexact=agent_name,
                is_active=True
            ).first()

            if not agent_template:
                self.logger.warning(f"No agent template found for: {agent_name}")
                return None

            # Create execution record
            execution = AgentExecution.objects.create(
                template=agent_template,
                execution_id=context.task_id,
                task_description=task_data.get('description', f'Execute {agent_name}'),
                task_type=task_data.get('task_type', 'general'),
                input_data=task_data,
                context=context.__dict__,
                status=AgentStatus.PENDING,
                priority=context.priority.name.lower(),
                estimated_completion_time=timezone.now() + timezone.timedelta(seconds=context.timeout_seconds),
                websocket_channel=context.websocket_channel or ''
            )

            return execution

        except Exception as e:
            self.logger.error(f"Failed to create DB execution record: {e}")
            return None

    async def _update_db_execution_record(self,
                                        execution: Optional[AgentExecution],
                                        result: ExecutionResult):
        """Update database execution record with results"""

        if not execution:
            return

        try:
            # Map executor status to Django model status
            status_mapping = {
                ExecutionStatus.COMPLETED: AgentStatus.COMPLETED,
                ExecutionStatus.FAILED: AgentStatus.FAILED,
                ExecutionStatus.CANCELLED: AgentStatus.CANCELLED,
                ExecutionStatus.RUNNING: AgentStatus.RUNNING,
                ExecutionStatus.PENDING: AgentStatus.PENDING
            }

            # Update execution record
            execution.status = status_mapping.get(result.status, AgentStatus.FAILED)
            execution.output_data = result.output
            execution.output_files = result.files_created
            execution.error_message = result.error_message or ''
            execution.error_details = result.error_details
            execution.warnings = result.warnings
            execution.token_usage = result.tokens_used
            execution.cost_breakdown = {k: float(v) for k, v in result.cost_breakdown.items()}
            execution.total_cost = result.total_cost
            execution.execution_time_seconds = int(result.execution_time_ms / 1000)
            execution.quality_score = result.quality_score
            execution.completed_at = timezone.now()
            execution.progress_percentage = 100 if result.status == ExecutionStatus.COMPLETED else 0

            execution.save()

            # Update agent template metrics
            execution.template.update_metrics(
                execution_time=execution.execution_time_seconds,
                success=(result.status == ExecutionStatus.COMPLETED),
                cost=result.total_cost,
                tokens=result.tokens_used
            )

        except Exception as e:
            self.logger.error(f"Failed to update DB execution record: {e}")

    async def _mark_execution_failed(self,
                                   execution: AgentExecution,
                                   error_message: str):
        """Mark execution as failed in database"""

        try:
            execution.fail_execution(error_message)
        except Exception as e:
            self.logger.error(f"Failed to mark execution as failed: {e}")

    def get_executor_stats(self) -> Dict[str, Any]:
        """Get comprehensive executor statistics"""

        registry_stats = self.executor_registry.get_registry_stats()

        return {
            'system_stats': {
                'total_executions': self.total_executions,
                'successful_executions': self.successful_executions,
                'failed_executions': self.failed_executions,
                'success_rate': (
                    self.successful_executions / max(self.total_executions, 1)
                ),
                'registered_executors': len(self.executor_registry.list_executors()),
                'available_executor_classes': len(self.executor_mappings)
            },
            'registry_stats': registry_stats,
            'executor_mappings': {
                name: cls.__name__
                for name, cls in self.executor_mappings.items()
            }
        }

    def get_agent_execution_capability(self, agent_name: str) -> Dict[str, Any]:
        """Get execution capability info for an agent"""

        agent_name_lower = agent_name.lower()
        executor = self.executor_registry.get_executor(agent_name_lower)
        executor_class = self.executor_mappings.get(agent_name_lower)

        return {
            'agent_name': agent_name,
            'has_executor': executor is not None,
            'executor_class': executor_class.__name__ if executor_class else None,
            'required_tools': executor.get_required_tools() if executor else [],
            'required_apis': executor.get_required_apis() if executor else [],
            'performance_metrics': executor.get_performance_metrics() if executor else {},
            'can_execute': executor is not None
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of executor system"""

        try:
            # Test executor registration
            executors = self.executor_registry.list_executors()

            # Test database connectivity
            db_agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()

            # Test core executors
            core_executors = ['income_builder', 'content_creator', 'payment_processor']
            core_status = {
                name: self.executor_registry.get_executor(name) is not None
                for name in core_executors
            }

            return {
                'status': 'healthy',
                'registered_executors': len(executors),
                'db_agents': db_agent_count,
                'core_executors_available': all(core_status.values()),
                'core_executor_status': core_status,
                'total_executions': self.total_executions,
                'success_rate': (
                    self.successful_executions / max(self.total_executions, 1)
                ),
                'timestamp': timezone.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }


# Global executor registration system
executor_system = ExecutorRegistrationSystem()


# Convenience functions for agent execution
async def execute_agent_by_name(agent_name: str,
                               task_data: Dict[str, Any],
                               user_id: Optional[str] = None,
                               priority: ExecutionPriority = ExecutionPriority.NORMAL) -> ExecutionResult:
    """Execute an agent by name through the registration system"""
    return await executor_system.execute_agent(agent_name, task_data, user_id, priority)


def get_agent_execution_status(agent_name: str) -> Dict[str, Any]:
    """Get execution capability status for an agent"""
    return executor_system.get_agent_execution_capability(agent_name)


def list_executable_agents() -> List[str]:
    """List all agents that have executable implementations"""
    return executor_system.executor_registry.list_executors()


async def initialize_all_agent_executors():
    """Initialize executors for all database agents"""
    return await executor_system.register_agent_executors_from_db()


def get_execution_statistics() -> Dict[str, Any]:
    """Get comprehensive execution statistics"""
    return executor_system.get_executor_stats()


async def system_health_check() -> Dict[str, Any]:
    """Perform system-wide health check"""
    return await executor_system.health_check()