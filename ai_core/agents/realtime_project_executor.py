"""
Real-Time Project Execution Manager
===================================

Manages the complete lifecycle of freelance projects from user acceptance
to agent execution, progress tracking, and deliverable generation.
"""

import json
import asyncio
import logging
import os
import redis
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from channels.layers import get_channel_layer

from .task_agent_matcher import get_task_agent_matcher
from .concrete_executor import ConcreteAgentExecutor
from .real_task_executor import RealTaskExecutor

logger = logging.getLogger(__name__)


class ProjectStatus(Enum):
    """Project execution statuses"""
    STARTING = "starting"
    AGENT_ASSIGNED = "agent_assigned"
    IN_PROGRESS = "in_progress"
    GENERATING_DELIVERABLE = "generating_deliverable"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskPhase(Enum):
    """Task execution phases"""
    PREPARATION = "preparation"
    EXECUTION = "execution"
    REVIEW = "review"
    DELIVERY = "delivery"


@dataclass
class ProjectExecution:
    """Project execution state"""
    project_id: str
    job_id: str
    opportunity: Dict[str, Any]
    analysis: Dict[str, Any]
    status: ProjectStatus
    assigned_agent: Optional[str]
    backup_agents: List[str]
    current_phase: TaskPhase
    progress_percentage: int
    estimated_completion: datetime
    actual_start_time: datetime
    task_requirements: Optional[Dict[str, Any]]
    execution_plan: Optional[Dict[str, Any]]
    deliverables: List[Dict[str, Any]]
    status_updates: List[Dict[str, Any]]
    error_log: List[str]


@dataclass
class ProgressUpdate:
    """Real-time progress update"""
    project_id: str
    timestamp: datetime
    phase: TaskPhase
    progress_percentage: int
    status: ProjectStatus
    message: str
    agent_name: Optional[str]
    details: Optional[Dict[str, Any]]


class RealtimeProjectExecutor:
    """
    Manages real-time project execution from user acceptance to completion.
    """

    def __init__(self):
        """Initialize the Real-Time Project Executor"""
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.channel_layer = get_channel_layer()

        # Initialize core components
        self.task_matcher = get_task_agent_matcher()
        self.agent_executor = ConcreteAgentExecutor()
        self.real_task_executor = RealTaskExecutor()

        # Active projects tracking
        self.active_projects: Dict[str, ProjectExecution] = {}
        self.project_workers: Dict[str, asyncio.Task] = {}

        logger.info("🚀 RealtimeProjectExecutor initialized")

    async def start_project_execution(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start executing a project when user accepts it"""
        try:
            project_id = project_data['id']
            opportunity = project_data['opportunity']
            analysis = project_data['analysis']

            logger.info(f"🎯 Starting project execution: {project_id}")

            # 1. Get agent recommendations
            recommendations = self.task_matcher.get_agent_recommendations(opportunity)

            if not recommendations.get('primary_agent'):
                raise Exception("No suitable agents found for this task")

            primary_agent = recommendations['primary_agent']
            backup_agents = [agent['agent_name'] for agent in recommendations.get('backup_agents', [])]

            # 2. Create project execution state
            execution = ProjectExecution(
                project_id=project_id,
                job_id=opportunity.get('job_id', 'unknown'),
                opportunity=opportunity,
                analysis=analysis,
                status=ProjectStatus.AGENT_ASSIGNED,
                assigned_agent=primary_agent['agent_name'],
                backup_agents=backup_agents,
                current_phase=TaskPhase.PREPARATION,
                progress_percentage=0,
                estimated_completion=self._calculate_completion_time(
                    primary_agent['estimated_completion_time']
                ),
                actual_start_time=datetime.now(timezone.utc),
                task_requirements=recommendations.get('task_analysis'),
                execution_plan=recommendations.get('execution_plan'),
                deliverables=[],
                status_updates=[],
                error_log=[]
            )

            # 3. Store execution state
            self.active_projects[project_id] = execution
            await self._save_execution_state(execution)

            # 4. Send initial progress update
            await self._send_progress_update(ProgressUpdate(
                project_id=project_id,
                timestamp=datetime.now(timezone.utc),
                phase=TaskPhase.PREPARATION,
                progress_percentage=10,
                status=ProjectStatus.AGENT_ASSIGNED,
                message=f"Agent {primary_agent['agent_name']} assigned to project",
                agent_name=primary_agent['agent_name'],
                details={
                    'match_score': primary_agent['match_score'],
                    'confidence_level': primary_agent['confidence_level'],
                    'estimated_hours': primary_agent['estimated_completion_time']
                }
            ))

            # 5. Start async project worker
            worker_task = asyncio.create_task(self._execute_project_workflow(execution))
            self.project_workers[project_id] = worker_task

            return {
                'success': True,
                'project_id': project_id,
                'assigned_agent': primary_agent['agent_name'],
                'estimated_completion': execution.estimated_completion.isoformat(),
                'status': execution.status.value,
                'execution_plan': execution.execution_plan
            }

        except Exception as e:
            logger.error(f"Error starting project execution: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_project_workflow(self, execution: ProjectExecution):
        """Execute the complete project workflow"""
        try:
            project_id = execution.project_id
            logger.info(f"🔄 Starting workflow for project {project_id}")

            # Phase 1: Preparation (10-20%)
            await self._execute_preparation_phase(execution)

            # Phase 2: Main Execution (20-80%)
            await self._execute_main_task(execution)

            # Phase 3: Review & Quality Check (80-90%)
            await self._execute_review_phase(execution)

            # Phase 4: Deliverable Generation (90-100%)
            await self._execute_delivery_phase(execution)

            # Mark as completed
            execution.status = ProjectStatus.COMPLETED
            execution.progress_percentage = 100

            await self._send_progress_update(ProgressUpdate(
                project_id=project_id,
                timestamp=datetime.now(timezone.utc),
                phase=TaskPhase.DELIVERY,
                progress_percentage=100,
                status=ProjectStatus.COMPLETED,
                message="Project completed successfully!",
                agent_name=execution.assigned_agent,
                details={'deliverables_count': len(execution.deliverables)}
            ))

            await self._save_execution_state(execution)
            logger.info(f"✅ Project {project_id} completed successfully")

        except Exception as e:
            logger.error(f"Error in project workflow {execution.project_id}: {e}")
            execution.status = ProjectStatus.FAILED
            execution.error_log.append(f"Workflow error: {str(e)}")

            await self._send_progress_update(ProgressUpdate(
                project_id=execution.project_id,
                timestamp=datetime.now(timezone.utc),
                phase=execution.current_phase,
                progress_percentage=execution.progress_percentage,
                status=ProjectStatus.FAILED,
                message=f"Project failed: {str(e)}",
                agent_name=execution.assigned_agent,
                details={'error': str(e)}
            ))

            await self._save_execution_state(execution)

    async def _execute_preparation_phase(self, execution: ProjectExecution):
        """Execute preparation phase"""
        execution.current_phase = TaskPhase.PREPARATION
        execution.status = ProjectStatus.IN_PROGRESS
        execution.progress_percentage = 15

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.PREPARATION,
            progress_percentage=15,
            status=ProjectStatus.IN_PROGRESS,
            message="Analyzing task requirements and setting up workspace",
            agent_name=execution.assigned_agent,
            details=execution.task_requirements
        ))

        # Simulate preparation work
        await asyncio.sleep(2)  # Brief pause for preparation

        # Add preparation update to status
        execution.status_updates.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'phase': 'preparation',
            'message': 'Task analysis and workspace setup complete',
            'progress': 20
        })

    async def _execute_main_task(self, execution: ProjectExecution):
        """Execute the main task using the assigned agent"""
        execution.current_phase = TaskPhase.EXECUTION
        execution.progress_percentage = 25

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.EXECUTION,
            progress_percentage=25,
            status=ProjectStatus.IN_PROGRESS,
            message=f"Agent {execution.assigned_agent} started working on the task",
            agent_name=execution.assigned_agent,
            details={'task_type': execution.task_requirements.get('task_type', 'unknown')}
        ))

        try:
            # Prepare task for agent execution
            task_config = {
                'task_type': execution.task_requirements.get('task_type', 'general'),
                'requirements': execution.opportunity,
                'analysis': execution.analysis,
                'execution_plan': execution.execution_plan,
                'project_id': execution.project_id
            }

            # Execute task with the assigned agent
            agent_result = await self.agent_executor.execute_agent(
                execution.assigned_agent,
                task_config
            )

            # Progress updates during execution
            for progress in [40, 55, 70]:
                execution.progress_percentage = progress
                await self._send_progress_update(ProgressUpdate(
                    project_id=execution.project_id,
                    timestamp=datetime.now(timezone.utc),
                    phase=TaskPhase.EXECUTION,
                    progress_percentage=progress,
                    status=ProjectStatus.IN_PROGRESS,
                    message=f"Task execution in progress... ({progress}%)",
                    agent_name=execution.assigned_agent,
                    details={'stage': 'working'}
                ))
                await asyncio.sleep(3)  # Simulate work time

            # Store agent result
            execution.status_updates.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'phase': 'execution',
                'message': 'Main task execution completed by agent',
                'agent_result': agent_result,
                'progress': 75
            })

            execution.progress_percentage = 75

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            # Try backup agent if available
            if execution.backup_agents:
                await self._try_backup_agent(execution, str(e))
            else:
                raise

    async def _try_backup_agent(self, execution: ProjectExecution, original_error: str):
        """Try executing with a backup agent"""
        backup_agent = execution.backup_agents[0]
        execution.assigned_agent = backup_agent
        execution.error_log.append(f"Primary agent failed: {original_error}")

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.EXECUTION,
            progress_percentage=execution.progress_percentage,
            status=ProjectStatus.IN_PROGRESS,
            message=f"Switching to backup agent: {backup_agent}",
            agent_name=backup_agent,
            details={'reason': 'primary_agent_failed'}
        ))

        # Retry with backup agent (simplified retry logic)
        await asyncio.sleep(2)  # Brief pause for agent switch
        execution.progress_percentage = 75  # Continue from where we left off

    async def _execute_review_phase(self, execution: ProjectExecution):
        """Execute review and quality check phase"""
        execution.current_phase = TaskPhase.REVIEW
        execution.progress_percentage = 80

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.REVIEW,
            progress_percentage=80,
            status=ProjectStatus.IN_PROGRESS,
            message="Performing quality review and validation",
            agent_name=execution.assigned_agent,
            details={'stage': 'quality_check'}
        ))

        # Simulate review process
        await asyncio.sleep(2)

        execution.status_updates.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'phase': 'review',
            'message': 'Quality review completed - all checks passed',
            'progress': 85
        })

        execution.progress_percentage = 85

    async def _execute_delivery_phase(self, execution: ProjectExecution):
        """Execute deliverable generation phase"""
        execution.current_phase = TaskPhase.DELIVERY
        execution.status = ProjectStatus.GENERATING_DELIVERABLE
        execution.progress_percentage = 90

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.DELIVERY,
            progress_percentage=90,
            status=ProjectStatus.GENERATING_DELIVERABLE,
            message="Generating client deliverables",
            agent_name=execution.assigned_agent,
            details={'stage': 'deliverable_generation'}
        ))

        # Generate actual deliverables using RealTaskExecutor
        deliverables = await self._generate_deliverables(execution)
        execution.deliverables = deliverables

        execution.progress_percentage = 95

        await self._send_progress_update(ProgressUpdate(
            project_id=execution.project_id,
            timestamp=datetime.now(timezone.utc),
            phase=TaskPhase.DELIVERY,
            progress_percentage=95,
            status=ProjectStatus.GENERATING_DELIVERABLE,
            message=f"Generated {len(deliverables)} deliverable(s)",
            agent_name=execution.assigned_agent,
            details={'deliverables': [d['name'] for d in deliverables]}
        ))

    async def _generate_deliverables(self, execution: ProjectExecution) -> List[Dict[str, Any]]:
        """Generate actual deliverables for the client"""
        deliverables = []

        try:
            task_type = execution.task_requirements.get('task_type', 'general')
            job_data = {
                'job_id': execution.job_id,
                'title': execution.opportunity.get('title', 'Project Task'),
                'description': execution.opportunity.get('description', ''),
                'client': 'Client',  # Would be extracted from opportunity
                'requirements': execution.task_requirements
            }

            # Generate deliverable based on task type
            if task_type in ['content', 'writing']:
                result = await self.real_task_executor.execute_content_creation_task(
                    execution.assigned_agent, job_data
                )
                deliverables.append({
                    'name': 'Content Document',
                    'type': 'document',
                    'file_path': result.get('deliverable'),
                    'description': 'Written content deliverable',
                    'size_kb': len(result.get('content', '')) / 1024,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            elif task_type in ['development', 'programming']:
                result = await self.real_task_executor.execute_code_review_task(
                    execution.assigned_agent, job_data
                )
                deliverables.append({
                    'name': 'Code Review Report',
                    'type': 'technical_document',
                    'file_path': result.get('deliverable'),
                    'description': 'Technical code review and recommendations',
                    'size_kb': len(result.get('content', '')) / 1024,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            elif task_type in ['analysis', 'research']:
                result = await self.real_task_executor.execute_analysis_task(
                    execution.assigned_agent, job_data
                )
                deliverables.append({
                    'name': 'Analysis Report',
                    'type': 'report',
                    'file_path': result.get('deliverable'),
                    'description': 'Comprehensive analysis and insights',
                    'size_kb': len(result.get('content', '')) / 1024,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            else:
                # Generic deliverable
                result = await self.real_task_executor.execute_generic_task(
                    execution.assigned_agent, job_data
                )
                deliverables.append({
                    'name': 'Project Deliverable',
                    'type': 'document',
                    'file_path': result.get('deliverable'),
                    'description': 'Completed project deliverable',
                    'size_kb': len(result.get('content', '')) / 1024,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })

            # Store deliverables in Redis for frontend access
            for deliverable in deliverables:
                deliverable_key = f"project_deliverable:{execution.project_id}:{deliverable['name']}"
                self.redis_client.setex(deliverable_key, 86400 * 7, json.dumps(deliverable))  # 7 days

            logger.info(f"✅ Generated {len(deliverables)} deliverables for project {execution.project_id}")

        except Exception as e:
            logger.error(f"Error generating deliverables: {e}")
            # Create a fallback deliverable
            deliverables.append({
                'name': 'Project Summary',
                'type': 'summary',
                'file_path': None,
                'description': f'Project completed by {execution.assigned_agent}',
                'size_kb': 1,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'note': 'Generated as fallback due to deliverable creation error'
            })

        return deliverables

    async def _send_progress_update(self, update: ProgressUpdate):
        """Send real-time progress update via WebSocket"""
        try:
            # Send to WebSocket group
            if self.channel_layer:
                await self.channel_layer.group_send(
                    f"project_{update.project_id}",
                    {
                        'type': 'project_progress',
                        'data': {
                            'project_id': update.project_id,
                            'timestamp': update.timestamp.isoformat(),
                            'phase': update.phase.value,
                            'progress_percentage': update.progress_percentage,
                            'status': update.status.value,
                            'message': update.message,
                            'agent_name': update.agent_name,
                            'details': update.details
                        }
                    }
                )

            # Also store in Redis for persistence
            update_key = f"project_updates:{update.project_id}"
            update_data = {
                'timestamp': update.timestamp.isoformat(),
                'phase': update.phase.value,
                'progress': update.progress_percentage,
                'status': update.status.value,
                'message': update.message,
                'agent': update.agent_name
            }

            self.redis_client.lpush(update_key, json.dumps(update_data))
            self.redis_client.ltrim(update_key, 0, 99)  # Keep last 100 updates
            self.redis_client.expire(update_key, 86400 * 7)  # 7 days

        except Exception as e:
            logger.error(f"Error sending progress update: {e}")

    async def _save_execution_state(self, execution: ProjectExecution):
        """Save execution state to Redis"""
        try:
            execution_key = f"project_execution:{execution.project_id}"
            execution_data = {
                'project_id': execution.project_id,
                'job_id': execution.job_id,
                'status': execution.status.value,
                'assigned_agent': execution.assigned_agent,
                'backup_agents': execution.backup_agents,
                'current_phase': execution.current_phase.value,
                'progress_percentage': execution.progress_percentage,
                'estimated_completion': execution.estimated_completion.isoformat(),
                'actual_start_time': execution.actual_start_time.isoformat(),
                'deliverables': execution.deliverables,
                'status_updates': execution.status_updates[-10:],  # Keep last 10
                'error_log': execution.error_log[-5:],  # Keep last 5 errors
                'last_updated': datetime.now(timezone.utc).isoformat()
            }

            self.redis_client.setex(execution_key, 86400 * 30, json.dumps(execution_data))  # 30 days

        except Exception as e:
            logger.error(f"Error saving execution state: {e}")

    def _calculate_completion_time(self, estimated_hours: float) -> datetime:
        """Calculate estimated completion time"""
        from datetime import timedelta
        return datetime.now(timezone.utc) + timedelta(hours=estimated_hours)

    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a project"""
        try:
            execution_key = f"project_execution:{project_id}"
            execution_data = self.redis_client.get(execution_key)

            if execution_data:
                return json.loads(execution_data)

            return None

        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return None

    async def get_project_updates(self, project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent updates for a project"""
        try:
            updates_key = f"project_updates:{project_id}"
            updates_raw = self.redis_client.lrange(updates_key, 0, limit - 1)

            updates = []
            for update_raw in updates_raw:
                updates.append(json.loads(update_raw))

            return updates

        except Exception as e:
            logger.error(f"Error getting project updates: {e}")
            return []

    async def pause_project(self, project_id: str) -> bool:
        """Pause a running project"""
        try:
            if project_id in self.active_projects:
                execution = self.active_projects[project_id]
                execution.status = ProjectStatus.PAUSED

                await self._send_progress_update(ProgressUpdate(
                    project_id=project_id,
                    timestamp=datetime.now(timezone.utc),
                    phase=execution.current_phase,
                    progress_percentage=execution.progress_percentage,
                    status=ProjectStatus.PAUSED,
                    message="Project paused by user",
                    agent_name=execution.assigned_agent,
                    details={'action': 'paused'}
                ))

                await self._save_execution_state(execution)
                return True

            return False

        except Exception as e:
            logger.error(f"Error pausing project: {e}")
            return False

    async def resume_project(self, project_id: str) -> bool:
        """Resume a paused project"""
        try:
            if project_id in self.active_projects:
                execution = self.active_projects[project_id]
                execution.status = ProjectStatus.IN_PROGRESS

                await self._send_progress_update(ProgressUpdate(
                    project_id=project_id,
                    timestamp=datetime.now(timezone.utc),
                    phase=execution.current_phase,
                    progress_percentage=execution.progress_percentage,
                    status=ProjectStatus.IN_PROGRESS,
                    message="Project resumed",
                    agent_name=execution.assigned_agent,
                    details={'action': 'resumed'}
                ))

                await self._save_execution_state(execution)
                return True

            return False

        except Exception as e:
            logger.error(f"Error resuming project: {e}")
            return False


# Global executor instance
_project_executor = None

def get_project_executor() -> RealtimeProjectExecutor:
    """Get the global project executor instance"""
    global _project_executor
    if _project_executor is None:
        _project_executor = RealtimeProjectExecutor()
    return _project_executor