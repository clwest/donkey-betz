"""
Agent Orchestration Layer
Enables multi-agent collaboration and complex workflows
"""
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import redis

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents a task for an agent"""
    task_id: str
    agent_name: str
    task_type: str
    input_data: Dict[str, Any]
    dependencies: List[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Workflow:
    """Represents a multi-agent workflow"""
    workflow_id: str
    name: str
    description: str
    tasks: List[AgentTask]
    status: str = "pending"
    created_at: datetime = None
    completed_at: Optional[datetime] = None


class AgentOrchestrationLayer:
    """Orchestrates multi-agent collaboration and workflows"""

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

        # Get concrete executor for agent execution
        self.executor = None
        self._initialize_executor()

        # Active workflows
        self.workflows = {}

        # Task execution queue
        self.task_queue = asyncio.Queue()

        # Start task processor
        self.processor_task = None

        logger.info("Agent Orchestration Layer initialized")

    def _initialize_executor(self):
        """Initialize the concrete executor"""
        try:
            from ai_core.agents.concrete_executor import concrete_executor
            self.executor = concrete_executor
            logger.info("Connected to concrete executor")
        except Exception as e:
            logger.error(f"Failed to initialize executor: {e}")

    async def start(self):
        """Start the orchestration layer"""
        if not self.processor_task:
            self.processor_task = asyncio.create_task(self._task_processor())
            logger.info("Started task processor")

    async def stop(self):
        """Stop the orchestration layer"""
        if self.processor_task:
            self.processor_task.cancel()
            await self.processor_task
            logger.info("Stopped task processor")

    async def create_workflow(self, name: str, description: str,
                            tasks: List[Dict[str, Any]]) -> Workflow:
        """Create a new multi-agent workflow"""
        workflow_id = f"workflow_{datetime.now().timestamp()}"

        # Convert task dicts to AgentTask objects
        agent_tasks = []
        for i, task_dict in enumerate(tasks):
            task = AgentTask(
                task_id=f"{workflow_id}_task_{i}",
                agent_name=task_dict['agent'],
                task_type=task_dict.get('type', 'general'),
                input_data=task_dict.get('input', {}),
                dependencies=task_dict.get('dependencies', [])
            )
            agent_tasks.append(task)

        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            tasks=agent_tasks,
            created_at=datetime.now()
        )

        self.workflows[workflow_id] = workflow

        # Store in Redis for persistence
        self.redis_client.setex(
            f"workflow:{workflow_id}",
            86400,  # 24 hour TTL
            json.dumps(asdict(workflow), default=str)
        )

        logger.info(f"Created workflow {workflow_id} with {len(agent_tasks)} tasks")
        return workflow

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            return {
                'success': False,
                'error': f'Workflow {workflow_id} not found'
            }

        workflow = self.workflows[workflow_id]
        workflow.status = "running"

        # Execute tasks respecting dependencies
        results = {}

        for task in workflow.tasks:
            # Wait for dependencies
            if task.dependencies:
                await self._wait_for_dependencies(task.dependencies, results)

            # Execute task
            task.status = "running"
            task.started_at = datetime.now()

            try:
                result = await self._execute_task(task, results)
                task.result = result
                task.status = "completed"
                results[task.task_id] = result
            except Exception as e:
                task.error = str(e)
                task.status = "failed"
                logger.error(f"Task {task.task_id} failed: {e}")

            task.completed_at = datetime.now()

        workflow.status = "completed"
        workflow.completed_at = datetime.now()

        return {
            'success': True,
            'workflow_id': workflow_id,
            'results': results,
            'status': workflow.status
        }

    async def _execute_task(self, task: AgentTask,
                          previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single task"""
        if not self.executor:
            raise Exception("Executor not available")

        # Prepare input with results from dependencies
        enhanced_input = task.input_data.copy()

        if task.dependencies:
            enhanced_input['dependency_results'] = {
                dep: previous_results.get(dep, {})
                for dep in task.dependencies
            }

        # Execute agent
        result = await self.executor.execute_agent(
            agent_name=task.agent_name,
            task={'input': enhanced_input}
        )

        return result

    async def _wait_for_dependencies(self, dependencies: List[str],
                                    results: Dict[str, Any]):
        """Wait for task dependencies to complete"""
        max_wait = 60  # seconds
        start_time = datetime.now()

        while True:
            all_complete = all(dep in results for dep in dependencies)

            if all_complete:
                return

            if (datetime.now() - start_time).seconds > max_wait:
                raise TimeoutError(f"Dependencies {dependencies} timed out")

            await asyncio.sleep(0.5)

    async def _task_processor(self):
        """Process tasks from the queue"""
        while True:
            try:
                task = await self.task_queue.get()
                await self._execute_task(task, {})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Task processor error: {e}")

    async def create_opportunity_workflow(self, user_skills: List[str]) -> Workflow:
        """Create a workflow for finding and applying to opportunities"""
        tasks = [
            {
                'agent': 'opportunity_scanner_agent',
                'type': 'scan',
                'input': {'skills': user_skills}
            },
            {
                'agent': 'job_matcher_agent',
                'type': 'match',
                'input': {'skills': user_skills},
                'dependencies': ['workflow_*_task_0']
            },
            {
                'agent': 'ai_proposal_engine',
                'type': 'generate_proposal',
                'input': {},
                'dependencies': ['workflow_*_task_1']
            },
            {
                'agent': 'automated_job_bot',
                'type': 'apply',
                'input': {},
                'dependencies': ['workflow_*_task_2']
            }
        ]

        return await self.create_workflow(
            name="Opportunity Hunter",
            description="Find and apply to matching opportunities",
            tasks=tasks
        )

    async def create_content_workflow(self, topic: str) -> Workflow:
        """Create a workflow for content creation and distribution"""
        tasks = [
            {
                'agent': 'viral_content_agent',
                'type': 'research',
                'input': {'topic': topic}
            },
            {
                'agent': 'content_creator_agent',
                'type': 'create',
                'input': {'topic': topic},
                'dependencies': ['workflow_*_task_0']
            },
            {
                'agent': 'seo_optimizer_agent',
                'type': 'optimize',
                'input': {},
                'dependencies': ['workflow_*_task_1']
            },
            {
                'agent': 'social_media_agent',
                'type': 'distribute',
                'input': {},
                'dependencies': ['workflow_*_task_2']
            }
        ]

        return await self.create_workflow(
            name="Content Pipeline",
            description="Create and distribute viral content",
            tasks=tasks
        )

    async def create_trading_workflow(self, capital: float) -> Workflow:
        """Create a workflow for trading analysis and execution"""
        tasks = [
            {
                'agent': 'market_analysis_agent',
                'type': 'analyze',
                'input': {'markets': ['stocks', 'crypto', 'forex']}
            },
            {
                'agent': 'trading_bot_agent',
                'type': 'identify_opportunities',
                'input': {'capital': capital},
                'dependencies': ['workflow_*_task_0']
            },
            {
                'agent': 'portfolio_manager_agent',
                'type': 'risk_assessment',
                'input': {},
                'dependencies': ['workflow_*_task_1']
            },
            {
                'agent': 'crypto_trader_agent',
                'type': 'execute_trades',
                'input': {'capital': capital},
                'dependencies': ['workflow_*_task_2']
            }
        ]

        return await self.create_workflow(
            name="Trading Strategy",
            description="Analyze markets and execute trades",
            tasks=tasks
        )

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow"""
        if workflow_id not in self.workflows:
            return {'error': 'Workflow not found'}

        workflow = self.workflows[workflow_id]

        return {
            'workflow_id': workflow_id,
            'name': workflow.name,
            'status': workflow.status,
            'tasks': [
                {
                    'task_id': task.task_id,
                    'agent': task.agent_name,
                    'status': task.status,
                    'error': task.error
                }
                for task in workflow.tasks
            ],
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None
        }

    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        active = []

        for workflow_id, workflow in self.workflows.items():
            if workflow.status in ['pending', 'running']:
                active.append(self.get_workflow_status(workflow_id))

        return active


# Singleton instance
agent_orchestrator = AgentOrchestrationLayer()


# Helper functions
async def create_and_execute_workflow(name: str, description: str,
                                     tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create and immediately execute a workflow"""
    workflow = await agent_orchestrator.create_workflow(name, description, tasks)
    return await agent_orchestrator.execute_workflow(workflow.workflow_id)


async def execute_opportunity_workflow(user_skills: List[str]) -> Dict[str, Any]:
    """Execute a complete opportunity finding workflow"""
    workflow = await agent_orchestrator.create_opportunity_workflow(user_skills)
    return await agent_orchestrator.execute_workflow(workflow.workflow_id)