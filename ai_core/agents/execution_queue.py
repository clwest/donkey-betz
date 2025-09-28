"""
Agent Execution Queue with Priority Management
Ensures high-value tasks are processed first
"""
import asyncio
import json
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging
from dataclasses import dataclass, field
import heapq

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Task priority levels"""
    URGENT = 1      # Income opportunities, arbitrage
    HIGH = 2        # Analysis tasks, recommendations
    MEDIUM = 3      # Content generation
    LOW = 4         # Background analysis
    MAINTENANCE = 5 # System tasks


@dataclass(order=True)
class AgentTask:
    """Prioritized task for agent execution"""
    priority: int
    task_id: str = field(compare=False)
    agent_name: str = field(compare=False)
    task_data: Dict[str, Any] = field(compare=False)
    created_at: datetime = field(compare=False)
    spider_data: Optional[Dict[str, Any]] = field(compare=False, default=None)
    callback_channel: Optional[str] = field(compare=False, default=None)


class AgentExecutionQueue:
    """
    Priority queue system for agent task execution.
    Ensures high-value opportunities are processed first.
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

        # In-memory priority queue for fast access
        self.task_queue = []

        # Task categorization for priority assignment
        self.priority_rules = {
            'income_builder': Priority.URGENT,
            'arbitrage_hunter': Priority.URGENT,
            'opportunity_scanner': Priority.URGENT,
            'revenue_generator': Priority.URGENT,
            'sports_analytics': Priority.HIGH,
            'betting_optimizer': Priority.HIGH,
            'trading_bot': Priority.HIGH,
            'crypto_trader': Priority.HIGH,
            'content_creator': Priority.MEDIUM,
            'viral_content': Priority.MEDIUM,
            'seo_optimizer': Priority.LOW,
            'sentiment_analyzer': Priority.LOW
        }

        self.running = False
        self.executor_task = None

        # Metrics
        self.metrics = {
            'tasks_queued': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'avg_execution_time': 0,
            'by_priority': {p.name: 0 for p in Priority}
        }

    async def start(self):
        """Start the execution queue processor"""
        if self.running:
            return

        logger.info("🚀 Starting Agent Execution Queue...")
        self.running = True

        # Start background processor
        self.executor_task = asyncio.create_task(self._process_queue())

        # Load any pending tasks from Redis
        await self._restore_queue_from_redis()

        logger.info("✅ Execution queue started")

    async def stop(self):
        """Stop the execution queue"""
        self.running = False
        if self.executor_task:
            self.executor_task.cancel()
        logger.info("🛑 Execution queue stopped")

    async def add_task(self, agent_name: str, task_data: Dict[str, Any],
                      priority: Optional[Priority] = None,
                      spider_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a task to the execution queue.

        Args:
            agent_name: Name of the agent to execute
            task_data: Task parameters
            priority: Optional priority override
            spider_data: Optional spider data for context

        Returns:
            Task ID for tracking
        """
        # Generate task ID
        task_id = f"task_{agent_name}_{datetime.now().timestamp()}"

        # Determine priority
        if priority is None:
            # Auto-assign based on agent type
            for keyword, auto_priority in self.priority_rules.items():
                if keyword in agent_name.lower():
                    priority = auto_priority
                    break
            else:
                priority = Priority.MEDIUM

        # Create task
        task = AgentTask(
            priority=priority.value,
            task_id=task_id,
            agent_name=agent_name,
            task_data=task_data,
            created_at=datetime.now(),
            spider_data=spider_data
        )

        # Add to priority queue
        heapq.heappush(self.task_queue, task)

        # Store in Redis for persistence
        await self._persist_task_to_redis(task)

        # Update metrics
        self.metrics['tasks_queued'] += 1
        self.metrics['by_priority'][priority.name] += 1

        # Notify processor
        self.redis_client.publish('queue:notify', task_id)

        logger.info(f"📥 Queued task {task_id} for {agent_name} with priority {priority.name}")

        return task_id

    async def _process_queue(self):
        """Main queue processing loop"""
        while self.running:
            try:
                if self.task_queue:
                    # Get highest priority task
                    task = heapq.heappop(self.task_queue)

                    # Execute task
                    await self._execute_task(task)
                else:
                    # No tasks, wait for notification
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error processing queue: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task: AgentTask):
        """Execute a single task"""
        start_time = datetime.now()

        try:
            logger.info(f"🏃 Executing {task.agent_name} - Priority: {Priority(task.priority).name}")

            # Import executor
            from ai_core.agents.concrete_executor import concrete_executor

            # Prepare execution context
            execution_params = {
                'agent_name': task.agent_name,
                'task': {
                    'input': task.task_data,
                    'spider_data': task.spider_data
                }
            }

            # Execute agent
            result = await concrete_executor.execute_agent(**execution_params)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()

            # Store result
            await self._store_result(task.task_id, result)

            # Notify callback if provided
            if task.callback_channel:
                self.redis_client.publish(task.callback_channel, json.dumps({
                    'task_id': task.task_id,
                    'status': 'completed',
                    'result': result,
                    'execution_time': execution_time
                }))

            # Update metrics
            self.metrics['tasks_completed'] += 1
            self._update_avg_execution_time(execution_time)

            logger.info(f"✅ Task {task.task_id} completed in {execution_time:.2f}s")

        except Exception as e:
            logger.error(f"❌ Task {task.task_id} failed: {e}")
            self.metrics['tasks_failed'] += 1

            # Store error
            await self._store_result(task.task_id, {
                'success': False,
                'error': str(e)
            })

    async def _persist_task_to_redis(self, task: AgentTask):
        """Store task in Redis for persistence"""
        task_data = {
            'task_id': task.task_id,
            'agent_name': task.agent_name,
            'priority': task.priority,
            'task_data': task.task_data,
            'spider_data': task.spider_data,
            'created_at': task.created_at.isoformat(),
            'callback_channel': task.callback_channel
        }

        # Store in Redis with expiry
        self.redis_client.setex(
            f"queue:task:{task.task_id}",
            3600,  # 1 hour TTL
            json.dumps(task_data)
        )

        # Add to pending set
        self.redis_client.sadd('queue:pending', task.task_id)

    async def _restore_queue_from_redis(self):
        """Restore pending tasks from Redis on startup"""
        try:
            pending_ids = self.redis_client.smembers('queue:pending')

            for task_id in pending_ids:
                task_data = self.redis_client.get(f"queue:task:{task_id}")
                if task_data:
                    data = json.loads(task_data)
                    task = AgentTask(
                        priority=data['priority'],
                        task_id=data['task_id'],
                        agent_name=data['agent_name'],
                        task_data=data['task_data'],
                        created_at=datetime.fromisoformat(data['created_at']),
                        spider_data=data.get('spider_data'),
                        callback_channel=data.get('callback_channel')
                    )
                    heapq.heappush(self.task_queue, task)

            if pending_ids:
                logger.info(f"📦 Restored {len(pending_ids)} pending tasks from Redis")

        except Exception as e:
            logger.error(f"Error restoring queue: {e}")

    async def _store_result(self, task_id: str, result: Dict[str, Any]):
        """Store task execution result"""
        # Store in Redis
        self.redis_client.setex(
            f"queue:result:{task_id}",
            3600,  # 1 hour TTL
            json.dumps(result)
        )

        # Remove from pending set
        self.redis_client.srem('queue:pending', task_id)

        # Add to completed set
        self.redis_client.sadd('queue:completed', task_id)

    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time metric"""
        current_avg = self.metrics['avg_execution_time']
        total_tasks = self.metrics['tasks_completed']

        # Calculate new average
        new_avg = ((current_avg * (total_tasks - 1)) + execution_time) / total_tasks
        self.metrics['avg_execution_time'] = new_avg

    async def get_status(self) -> Dict[str, Any]:
        """Get queue status and metrics"""
        return {
            'running': self.running,
            'queue_size': len(self.task_queue),
            'metrics': self.metrics,
            'top_tasks': [
                {
                    'task_id': task.task_id,
                    'agent': task.agent_name,
                    'priority': Priority(task.priority).name
                }
                for task in sorted(self.task_queue)[:5]
            ]
        }

    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a completed task"""
        result_data = self.redis_client.get(f"queue:result:{task_id}")
        if result_data:
            return json.loads(result_data)
        return None


# Global queue instance
execution_queue = AgentExecutionQueue()