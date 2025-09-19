"""
Base Agent Executor Framework - Real Execution Engine

This module provides the core execution framework that transforms passive agent registrations
into active, revenue-generating workers. It handles API connections, tool integration,
error handling, and real deliverable generation.

Key Features:
- Async execution with real API calls
- Tool integration layer (WebSearch, file operations, API calls)
- Comprehensive error handling and retry logic
- Real deliverable creation and storage
- Performance monitoring and optimization
- API cost tracking and management
"""

import asyncio
import json
import logging
import time
import traceback
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import openai
from decimal import Decimal

# Import available tools
from core.tools.web_search import WebSearchTool
from core.tools.file_operations import FileOperationTool
from core.tools.api_connector import APIConnectorTool

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Execution status enum"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    TOOL_EXECUTION = "tool_execution"
    API_CALL = "api_call"
    GENERATING_OUTPUT = "generating_output"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class ExecutionPriority(Enum):
    """Execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class ExecutionContext:
    """Context for agent execution"""
    task_id: str
    user_id: Optional[str] = None
    priority: ExecutionPriority = ExecutionPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300
    tools_enabled: List[str] = field(default_factory=list)
    api_keys: Dict[str, str] = field(default_factory=dict)
    output_dir: Optional[Path] = None
    websocket_channel: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of agent execution"""
    task_id: str
    status: ExecutionStatus
    output: Dict[str, Any]
    files_created: List[str] = field(default_factory=list)
    api_calls_made: List[Dict[str, Any]] = field(default_factory=list)
    tools_used: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    total_cost: Decimal = Decimal('0.0')
    cost_breakdown: Dict[str, Decimal] = field(default_factory=dict)
    tokens_used: Dict[str, int] = field(default_factory=dict)
    error_message: Optional[str] = None
    error_details: Optional[Dict] = None
    warnings: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    deliverables: List[Dict[str, str]] = field(default_factory=list)


class BaseAgentExecutor(ABC):
    """
    Base class for all agent executors.

    This class provides the core infrastructure for transforming agent registrations
    into working executors that can:
    - Make real API calls
    - Use real tools
    - Generate real deliverables
    - Handle errors gracefully
    - Track performance and costs
    """

    def __init__(self, agent_name: str, config: Dict[str, Any]):
        self.agent_name = agent_name
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{agent_name}")

        # Initialize execution tracking
        self.execution_history: List[ExecutionResult] = []
        self.current_execution: Optional[ExecutionContext] = None

        # Initialize tool connections
        self.tools = self._initialize_tools()

        # Initialize API connections
        self.api_clients = self._initialize_api_clients()

        # Performance metrics
        self.total_executions = 0
        self.successful_executions = 0
        self.total_cost = Decimal('0.0')
        self.avg_execution_time = 0.0

        self.logger.info(f"Initialized {agent_name} executor with {len(self.tools)} tools")

    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize real tools for the agent"""
        tools = {}

        # Web Search Tool
        try:
            tools['web_search'] = WebSearchTool()
            if hasattr(tools['web_search'], 'is_configured') and tools['web_search'].is_configured:
                self.logger.info(f"{self.agent_name}: Web search tool initialized")
            else:
                self.logger.warning(f"{self.agent_name}: Web search tool not configured")
        except Exception as e:
            self.logger.warning(f"{self.agent_name}: Failed to initialize web search: {e}")

        # File Operations Tool
        try:
            tools['file_ops'] = FileOperationTool()
            self.logger.info(f"{self.agent_name}: File operations tool initialized")
        except Exception as e:
            self.logger.warning(f"{self.agent_name}: Failed to initialize file operations: {e}")

        # API Connector Tool
        try:
            tools['api_connector'] = APIConnectorTool()
            self.logger.info(f"{self.agent_name}: API connector tool initialized")
        except Exception as e:
            self.logger.warning(f"{self.agent_name}: Failed to initialize API connector: {e}")

        return tools

    def _initialize_api_clients(self) -> Dict[str, Any]:
        """Initialize API clients with proper authentication"""
        clients = {}

        # OpenAI Client
        try:
            openai_key = self.config.get('openai_api_key') or self._get_env_var('OPENAI_API_KEY')
            if openai_key:
                clients['openai'] = openai.OpenAI(api_key=openai_key)
                self.logger.info(f"{self.agent_name}: OpenAI client initialized")
            else:
                self.logger.warning(f"{self.agent_name}: OpenAI API key not found")
        except Exception as e:
            self.logger.error(f"{self.agent_name}: Failed to initialize OpenAI client: {e}")

        # Stripe Client (for payment processing agents)
        try:
            import stripe
            stripe_key = self.config.get('stripe_api_key') or self._get_env_var('STRIPE_API_KEY')
            if stripe_key:
                stripe.api_key = stripe_key
                clients['stripe'] = stripe
                self.logger.info(f"{self.agent_name}: Stripe client initialized")
        except ImportError:
            self.logger.warning(f"{self.agent_name}: Stripe not installed")
        except Exception as e:
            self.logger.error(f"{self.agent_name}: Failed to initialize Stripe client: {e}")

        # Additional API clients can be added here

        return clients

    def _get_env_var(self, var_name: str) -> Optional[str]:
        """Get environment variable safely"""
        import os
        return os.getenv(var_name)

    async def execute(self,
                     task_data: Dict[str, Any],
                     context: ExecutionContext) -> ExecutionResult:
        """
        Main execution entry point. This method orchestrates the entire execution process.
        """
        start_time = time.time()
        self.current_execution = context

        result = ExecutionResult(
            task_id=context.task_id,
            status=ExecutionStatus.INITIALIZING,
            output={}
        )

        try:
            self.logger.info(f"{self.agent_name}: Starting execution for task {context.task_id}")

            # Update status
            result.status = ExecutionStatus.INITIALIZING
            await self._notify_status_update(result)

            # Pre-execution setup
            await self._pre_execution_setup(task_data, context, result)

            # Main execution logic (implemented by subclasses)
            result.status = ExecutionStatus.RUNNING
            await self._notify_status_update(result)

            execution_output = await self._execute_agent_logic(task_data, context, result)
            result.output.update(execution_output)

            # Post-execution processing
            await self._post_execution_processing(task_data, context, result)

            # Mark as completed
            result.status = ExecutionStatus.COMPLETED
            result.quality_score = await self._assess_quality(result)

            # Update performance metrics
            self.total_executions += 1
            self.successful_executions += 1

            self.logger.info(f"{self.agent_name}: Successfully completed task {context.task_id}")

        except Exception as e:
            self.logger.error(f"{self.agent_name}: Execution failed for task {context.task_id}: {e}")
            self.logger.error(traceback.format_exc())

            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.error_details = {
                'exception_type': type(e).__name__,
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }

            # Attempt retry if configured
            if context.max_retries > 0:
                self.logger.info(f"{self.agent_name}: Retrying task {context.task_id}")
                context.max_retries -= 1
                result.status = ExecutionStatus.RETRYING
                await asyncio.sleep(2 ** (3 - context.max_retries))  # Exponential backoff
                return await self.execute(task_data, context)

        finally:
            # Calculate execution time
            end_time = time.time()
            result.execution_time_ms = int((end_time - start_time) * 1000)

            # Update average execution time
            if self.total_executions > 0:
                self.avg_execution_time = (
                    (self.avg_execution_time * (self.total_executions - 1) + result.execution_time_ms)
                    / self.total_executions
                )

            # Store execution history
            self.execution_history.append(result)

            # Final status notification
            await self._notify_status_update(result)

            self.current_execution = None

        return result

    async def _pre_execution_setup(self,
                                  task_data: Dict[str, Any],
                                  context: ExecutionContext,
                                  result: ExecutionResult) -> None:
        """Pre-execution setup and validation"""

        # Create output directory if specified
        if context.output_dir:
            context.output_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"{self.agent_name}: Created output directory {context.output_dir}")

        # Validate required tools are available
        required_tools = self.get_required_tools()
        for tool_name in required_tools:
            if tool_name not in self.tools:
                result.warnings.append(f"Required tool {tool_name} not available")
            elif not getattr(self.tools[tool_name], 'is_configured', True):
                result.warnings.append(f"Required tool {tool_name} not properly configured")

        # Validate API access if needed
        required_apis = self.get_required_apis()
        for api_name in required_apis:
            if api_name not in self.api_clients:
                result.warnings.append(f"Required API {api_name} not available")

    async def _post_execution_processing(self,
                                       task_data: Dict[str, Any],
                                       context: ExecutionContext,
                                       result: ExecutionResult) -> None:
        """Post-execution processing and cleanup"""

        # Calculate total cost
        result.total_cost = sum(result.cost_breakdown.values())
        self.total_cost += result.total_cost

        # Store deliverables if any files were created
        if result.files_created:
            for file_path in result.files_created:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    result.deliverables.append({
                        'file_path': str(file_path),
                        'file_name': file_path_obj.name,
                        'file_size': file_path_obj.stat().st_size,
                        'created_at': datetime.now().isoformat()
                    })

        self.logger.info(
            f"{self.agent_name}: Execution completed - "
            f"Tools used: {len(result.tools_used)}, "
            f"Files created: {len(result.files_created)}, "
            f"Cost: ${result.total_cost}"
        )

    async def _assess_quality(self, result: ExecutionResult) -> float:
        """Assess the quality of the execution result"""
        score = 0.5  # Base score

        # Check if execution was successful
        if result.status == ExecutionStatus.COMPLETED:
            score += 0.2

        # Check if deliverables were created
        if result.files_created:
            score += 0.2

        # Check if tools were used effectively
        if result.tools_used:
            score += 0.1

        # Penalize for warnings
        score -= len(result.warnings) * 0.05

        # Penalize for high cost (if over budget)
        if result.total_cost > Decimal('1.0'):
            score -= 0.1

        return max(0.0, min(1.0, score))

    async def _notify_status_update(self, result: ExecutionResult) -> None:
        """Notify external systems of status updates"""
        try:
            if self.current_execution and self.current_execution.websocket_channel:
                # Send WebSocket update (if WebSocket system is available)
                status_update = {
                    'task_id': result.task_id,
                    'agent_name': self.agent_name,
                    'status': result.status.value,
                    'progress': self._calculate_progress(result),
                    'timestamp': datetime.now().isoformat()
                }
                # WebSocket sending logic would go here
                self.logger.debug(f"{self.agent_name}: Status update: {status_update}")
        except Exception as e:
            self.logger.warning(f"{self.agent_name}: Failed to send status update: {e}")

    def _calculate_progress(self, result: ExecutionResult) -> int:
        """Calculate execution progress percentage"""
        if result.status == ExecutionStatus.PENDING:
            return 0
        elif result.status == ExecutionStatus.INITIALIZING:
            return 10
        elif result.status == ExecutionStatus.RUNNING:
            return 30
        elif result.status == ExecutionStatus.TOOL_EXECUTION:
            return 50
        elif result.status == ExecutionStatus.API_CALL:
            return 70
        elif result.status == ExecutionStatus.GENERATING_OUTPUT:
            return 90
        elif result.status == ExecutionStatus.COMPLETED:
            return 100
        else:
            return 0

    # Abstract methods that subclasses must implement

    @abstractmethod
    async def _execute_agent_logic(self,
                                  task_data: Dict[str, Any],
                                  context: ExecutionContext,
                                  result: ExecutionResult) -> Dict[str, Any]:
        """
        Execute the core agent logic. This is where the actual work happens.

        Args:
            task_data: Input data for the task
            context: Execution context with settings and constraints
            result: Result object to update with progress

        Returns:
            Dictionary containing the execution output
        """
        pass

    @abstractmethod
    def get_required_tools(self) -> List[str]:
        """Return list of tools required by this agent"""
        pass

    @abstractmethod
    def get_required_apis(self) -> List[str]:
        """Return list of APIs required by this agent"""
        pass

    # Helper methods for common operations

    async def web_search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform web search using real search tool"""
        if 'web_search' not in self.tools:
            raise RuntimeError("Web search tool not available")

        try:
            # Use the existing web search tool with proper parameters
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.tools['web_search'].execute, query, 'text', max_results
            )

            # Track tool usage
            if hasattr(self.current_execution, 'task_id'):
                execution_result = next(
                    (r for r in self.execution_history if r.task_id == self.current_execution.task_id),
                    None
                )
                if execution_result and 'web_search' not in execution_result.tools_used:
                    execution_result.tools_used.append('web_search')

            # Convert to expected format if needed
            if result.get('success') and 'data' in result:
                return {
                    'success': True,
                    'results': result['data'].get('results', []),
                    'query': query,
                    'timestamp': result.get('timestamp')
                }
            else:
                return result

        except Exception as e:
            self.logger.error(f"{self.agent_name}: Web search failed: {e}")
            # Return a fallback result instead of raising
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'query': query
            }

    async def call_openai_api(self,
                             prompt: str,
                             model: str = "gpt-5-mini",
                             max_tokens: int = 1000,
                             temperature: float = 0.7) -> Dict[str, Any]:
        """Make OpenAI API call with cost tracking"""
        if 'openai' not in self.api_clients:
            raise RuntimeError("OpenAI client not available")

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.api_clients['openai'].chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=max_tokens,
                    temperature=temperature
                )
            )

            # Track API usage and cost
            if hasattr(self.current_execution, 'task_id'):
                execution_result = next(
                    (r for r in self.execution_history if r.task_id == self.current_execution.task_id),
                    None
                )
                if execution_result:
                    # Track tokens
                    execution_result.tokens_used['input'] = response.usage.prompt_tokens
                    execution_result.tokens_used['output'] = response.usage.completion_tokens
                    execution_result.tokens_used['total'] = response.usage.total_tokens

                    # Calculate cost (approximate)
                    input_cost = Decimal(response.usage.prompt_tokens) * Decimal('0.00001')
                    output_cost = Decimal(response.usage.completion_tokens) * Decimal('0.00003')
                    execution_result.cost_breakdown['openai'] = input_cost + output_cost

                    # Track API call
                    execution_result.api_calls_made.append({
                        'api': 'openai',
                        'model': model,
                        'tokens': response.usage.total_tokens,
                        'cost': float(input_cost + output_cost),
                        'timestamp': datetime.now().isoformat()
                    })

            return {
                'content': response.choices[0].message.content,
                'model': model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            self.logger.error(f"{self.agent_name}: OpenAI API call failed: {e}")
            raise

    async def create_file(self,
                         file_path: str,
                         content: str,
                         encoding: str = 'utf-8') -> str:
        """Create a file with given content"""
        try:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path_obj, 'w', encoding=encoding) as f:
                f.write(content)

            # Track file creation
            if hasattr(self.current_execution, 'task_id'):
                execution_result = next(
                    (r for r in self.execution_history if r.task_id == self.current_execution.task_id),
                    None
                )
                if execution_result:
                    execution_result.files_created.append(str(file_path_obj))
                    if 'file_ops' not in execution_result.tools_used:
                        execution_result.tools_used.append('file_ops')

            self.logger.info(f"{self.agent_name}: Created file {file_path}")
            return str(file_path_obj)

        except Exception as e:
            self.logger.error(f"{self.agent_name}: File creation failed: {e}")
            raise

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this executor"""
        success_rate = (
            self.successful_executions / self.total_executions
            if self.total_executions > 0 else 0.0
        )

        return {
            'agent_name': self.agent_name,
            'total_executions': self.total_executions,
            'successful_executions': self.successful_executions,
            'success_rate': success_rate,
            'avg_execution_time_ms': self.avg_execution_time,
            'total_cost': float(self.total_cost),
            'tools_available': list(self.tools.keys()),
            'apis_available': list(self.api_clients.keys()),
            'last_execution': (
                self.execution_history[-1].task_id if self.execution_history else None
            )
        }


class AgentExecutorRegistry:
    """Registry for managing agent executors"""

    def __init__(self):
        self.executors: Dict[str, BaseAgentExecutor] = {}
        self.logger = logging.getLogger(f"{__name__}.Registry")

    def register_executor(self, agent_name: str, executor: BaseAgentExecutor):
        """Register an agent executor"""
        self.executors[agent_name] = executor
        self.logger.info(f"Registered executor for agent: {agent_name}")

    def get_executor(self, agent_name: str) -> Optional[BaseAgentExecutor]:
        """Get executor by agent name"""
        return self.executors.get(agent_name)

    def list_executors(self) -> List[str]:
        """List all registered executors"""
        return list(self.executors.keys())

    async def execute_agent(self,
                          agent_name: str,
                          task_data: Dict[str, Any],
                          context: ExecutionContext) -> ExecutionResult:
        """Execute an agent by name"""
        executor = self.get_executor(agent_name)
        if not executor:
            raise ValueError(f"No executor registered for agent: {agent_name}")

        return await executor.execute(task_data, context)

    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_executions = sum(e.total_executions for e in self.executors.values())
        successful_executions = sum(e.successful_executions for e in self.executors.values())
        total_cost = sum(e.total_cost for e in self.executors.values())

        return {
            'total_executors': len(self.executors),
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'success_rate': (
                successful_executions / total_executions if total_executions > 0 else 0.0
            ),
            'total_cost': float(total_cost),
            'executors': {
                name: executor.get_performance_metrics()
                for name, executor in self.executors.items()
            }
        }


# Global executor registry
executor_registry = AgentExecutorRegistry()