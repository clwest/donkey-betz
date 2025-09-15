"""
Task Delegation Orchestrator
Parses action plans and automatically delegates tasks to appropriate agents
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

@dataclass
class ExtractedTask:
    id: str
    title: str
    description: str
    agent_type: str
    phase: str
    day_range: str
    priority: TaskPriority
    dependencies: List[str]
    estimated_duration: timedelta
    platform_tools: List[str]
    success_metrics: Dict[str, Any]
    metadata: Dict[str, Any]

class TaskDelegationOrchestrator:

    # Agent mapping for task delegation
    AGENT_MAPPING = {
        # Content & Creative
        "brand identity": "ai-content-studio",
        "logo": "image-video-pipeline",
        "design": "image-video-pipeline",
        "content creation": "content-creator",
        "service descriptions": "content-creator",
        "email templates": "content-creator",
        "faq": "content-creator",
        "knowledge base": "content-creator",

        # Research & Analysis
        "market analysis": "research-agent",
        "competitor": "research-agent",
        "value proposition": "research-agent",
        "potential clients": "research-agent",
        "analytics": "monitoring-dashboard-builder",
        "ml analytics": "ml-pipeline",

        # Revenue & Business
        "payment": "revenue-activation-orchestrator",
        "pricing": "revenue-activation-orchestrator",
        "invoicing": "revenue-activation-orchestrator",
        "subscription": "revenue-activation-orchestrator",
        "revenue engine": "revenue-activation-orchestrator",

        # Marketing & Outreach
        "marketing": "marketing-agent",
        "social media": "marketing-agent",
        "promotion": "marketing-agent",
        "outreach": "opportunity-pipeline-orchestrator",
        "proposals": "opportunity-pipeline-orchestrator",

        # Automation & Development
        "automation": "coding-agent",
        "workflow": "agent-orchestra-ui-refactor",
        "onboarding": "platform-design-convergence",
        "integration": "intelligent-prompting-integrator",

        # Optimization & Scaling
        "optimization": "redis-cache-optimizer",
        "performance": "monitoring-dashboard-builder",
        "scale": "system-unification-architect",
        "growth": "opportunity-pipeline-orchestrator"
    }

    def __init__(self):
        self.tasks: List[ExtractedTask] = []
        self.execution_queue: List[ExtractedTask] = []
        self.completed_tasks: List[ExtractedTask] = []
        self.task_status: Dict[str, TaskStatus] = {}

    def parse_action_plan(self, plan_content: str) -> List[ExtractedTask]:
        """Parse the action plan and extract actionable tasks"""
        tasks = []

        # More flexible patterns for markdown variations
        phase_pattern = r"###\s*Phase\s*(\d+):\s*([^\n(]+)(?:\s*\(Week\s*(\d+)\))?"
        day_pattern = r"####\s*Day\s*(\d+)(?:-(\d+))?:?\s*([^\n]*)"
        # Handle both ** and plain text tasks
        task_patterns = [
            r"✅\s*\*\*([^*]+)\*\*\s*([^\n]*)",  # Bold markdown
            r"✅\s*([^-\n]+)(?:\s*-\s*([^\n]+))?",  # Plain text with optional dash
            r"^\s*-\s*\*\*([^*]+)\*\*\s*([^\n]*)",  # Bullet with bold
            r"^\s*-\s*([A-Z][^:\n]+):\s*([^\n]+)"  # Bullet with title case
        ]
        subtask_pattern = r"^\s*-\s*([^\n]+)"

        current_phase = "Phase 1: Foundation"  # Default phase
        current_day_range = "Day 1-7"  # Default range

        lines = plan_content.split('\n')
        i = 0
        task_counter = 0

        while i < len(lines):
            line = lines[i]

            # Check for phase
            phase_match = re.match(phase_pattern, line)
            if phase_match:
                phase_num, phase_name, week = phase_match.groups()
                current_phase = f"Phase {phase_num}: {phase_name.strip()}"

            # Check for day range
            day_match = re.match(day_pattern, line)
            if day_match:
                day_start, day_end, day_desc = day_match.groups()
                current_day_range = f"Day {day_start}" + (f"-{day_end}" if day_end else "")

            # Check for main task with multiple patterns
            task_found = False
            for pattern in task_patterns:
                task_match = re.match(pattern, line)
                if task_match:
                    task_found = True
                    task_title = task_match.group(1).strip()
                    task_desc = task_match.group(2).strip() if len(task_match.groups()) > 1 and task_match.group(2) else ""

                        # Extract subtasks
                    subtasks = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith('-'):
                        subtask_match = re.match(subtask_pattern, lines[j])
                        if subtask_match:
                            subtasks.append(subtask_match.group(1).strip())
                        j += 1

                    # Determine agent type
                    agent_type = self._determine_agent(task_title, task_desc, subtasks)

                    # Extract platform tools mentioned
                    platform_tools = self._extract_platform_tools(task_title + " " + task_desc + " ".join(subtasks))

                    # Create task
                    task_counter += 1
                    task = ExtractedTask(
                        id=f"task_{task_counter:03d}",
                        title=task_title,
                        description=task_desc or f"Execute: {task_title}",
                        agent_type=agent_type,
                        phase=current_phase,
                        day_range=current_day_range,
                        priority=TaskPriority.HIGH if "critical" in task_title.lower() else TaskPriority.MEDIUM,
                        dependencies=[],
                        estimated_duration=timedelta(hours=2),
                        platform_tools=platform_tools,
                        success_metrics={
                            "completion": True,
                            "quality_check": True
                        },
                        metadata={
                            "subtasks": subtasks,
                            "original_line": line
                        }
                    )
                    tasks.append(task)

                    # Skip processed subtasks
                    i = j - 1
                    break  # Found a match, move to next line

            i += 1

        self.tasks = tasks
        return tasks

    def _determine_agent(self, title: str, desc: str, subtasks: List[str]) -> str:
        """Determine which agent should handle this task"""
        combined_text = (title + " " + desc + " " + " ".join(subtasks)).lower()

        for keyword, agent in self.AGENT_MAPPING.items():
            if keyword in combined_text:
                return agent

        return "general-purpose"

    def _extract_platform_tools(self, text: str) -> List[str]:
        """Extract mentioned platform tools"""
        tools = []
        tool_patterns = [
            "AI Content Studio",
            "Research Agent",
            "Content-Creator Agent",
            "Revenue Engine",
            "Marketing Agent",
            "ML Analytics",
            "Coding Agent",
            "Agent Network",
            "Distribution System",
            "Outreach Automation",
            "Platform Analytics"
        ]

        for tool in tool_patterns:
            if tool.lower() in text.lower():
                tools.append(tool)

        return tools

    def _determine_priority(self, phase: str, title: str) -> TaskPriority:
        """Determine task priority based on phase and content"""
        if "first client" in title.lower() or "revenue" in title.lower():
            return TaskPriority.CRITICAL
        elif "Phase 1" in phase or "foundation" in title.lower():
            return TaskPriority.HIGH
        elif "Phase 2" in phase or "launch" in title.lower():
            return TaskPriority.HIGH
        elif "optimization" in title.lower() or "scale" in title.lower():
            return TaskPriority.MEDIUM
        else:
            return TaskPriority.LOW

    def _identify_dependencies(self, title: str, existing_tasks: List[ExtractedTask]) -> List[str]:
        """Identify task dependencies"""
        dependencies = []

        # Common dependency patterns
        if "payment" in title.lower() or "revenue engine" in title.lower():
            for task in existing_tasks:
                if "brand" in task.title.lower() or "setup" in task.title.lower():
                    dependencies.append(task.id)

        if "first client" in title.lower():
            for task in existing_tasks:
                if "outreach" in task.title.lower() or "content" in task.title.lower():
                    dependencies.append(task.id)

        if "scale" in title.lower() or "optimization" in title.lower():
            for task in existing_tasks:
                if "first client" in task.title.lower():
                    dependencies.append(task.id)

        return dependencies

    def _estimate_duration(self, day_range: str) -> timedelta:
        """Estimate task duration from day range"""
        if not day_range or day_range == "Unspecified":
            return timedelta(days=1)

        match = re.match(r"Day (\d+)-?(\d+)?", day_range)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            return timedelta(days=end - start + 1)

        return timedelta(days=1)

    def _extract_metrics(self, title: str, desc: str) -> Dict[str, Any]:
        """Extract success metrics from task description"""
        metrics = {}

        # Revenue metrics
        revenue_match = re.search(r"\$(\d+[,\d]*)", title + " " + desc)
        if revenue_match:
            metrics["target_revenue"] = int(revenue_match.group(1).replace(",", ""))

        # Client metrics
        client_match = re.search(r"(\d+)\+?\s*(?:clients?|customers?)", title + " " + desc, re.I)
        if client_match:
            metrics["target_clients"] = int(client_match.group(1))

        # Percentage metrics
        percent_match = re.search(r"(\d+)%", title + " " + desc)
        if percent_match:
            metrics["target_percentage"] = int(percent_match.group(1))

        return metrics

    def create_execution_queue(self) -> List[ExtractedTask]:
        """Create an execution queue respecting dependencies"""
        self.execution_queue = []
        remaining_tasks = self.tasks.copy()
        completed_ids = set()

        while remaining_tasks:
            # Find tasks with no pending dependencies
            ready_tasks = []
            for task in remaining_tasks:
                if all(dep in completed_ids for dep in task.dependencies):
                    ready_tasks.append(task)

            if not ready_tasks and remaining_tasks:
                # Circular dependency or no tasks ready, take the highest priority
                ready_tasks = [min(remaining_tasks, key=lambda t: t.priority.value)]

            # Sort by priority
            ready_tasks.sort(key=lambda t: t.priority.value)

            for task in ready_tasks:
                self.execution_queue.append(task)
                completed_ids.add(task.id)
                remaining_tasks.remove(task)

        return self.execution_queue

    def delegate_task(self, task: ExtractedTask) -> Dict[str, Any]:
        """Delegate a task to the appropriate agent"""
        delegation = {
            "task_id": task.id,
            "agent": task.agent_type,
            "command": self._generate_agent_command(task),
            "context": {
                "title": task.title,
                "description": task.description,
                "phase": task.phase,
                "priority": task.priority.name,
                "platform_tools": task.platform_tools,
                "success_metrics": task.success_metrics
            },
            "scheduled_for": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + task.estimated_duration).isoformat()
        }

        self.task_status[task.id] = TaskStatus.IN_PROGRESS

        return delegation

    def _generate_agent_command(self, task: ExtractedTask) -> str:
        """Generate the command to execute for this agent"""
        commands = {
            "ai-content-studio": f"Create {task.title.lower()} with requirements: {task.description}",
            "research-agent": f"Research and analyze: {task.title}. Focus on: {task.description}",
            "content-creator": f"Generate content for: {task.title}. Details: {task.description}",
            "revenue-activation-orchestrator": f"Configure revenue system: {task.title}. Setup: {task.description}",
            "marketing-agent": f"Execute marketing task: {task.title}. Campaign details: {task.description}",
            "opportunity-pipeline-orchestrator": f"Process opportunity: {task.title}. Pipeline: {task.description}",
            "coding-agent": f"Implement automation: {task.title}. Requirements: {task.description}",
            "general-purpose": f"Execute task: {task.title}. Instructions: {task.description}"
        }

        return commands.get(task.agent_type, commands["general-purpose"])

    def execute_next_batch(self, batch_size: int = 3) -> List[Dict[str, Any]]:
        """Execute the next batch of tasks from the queue"""
        if not self.execution_queue:
            self.create_execution_queue()

        batch = []
        tasks_to_execute = []

        # Get tasks that are ready to execute
        for task in self.execution_queue[:batch_size * 2]:  # Check more tasks for dependencies
            if self.task_status.get(task.id) != TaskStatus.COMPLETED:
                if all(self.task_status.get(dep) == TaskStatus.COMPLETED for dep in task.dependencies):
                    tasks_to_execute.append(task)
                    if len(tasks_to_execute) >= batch_size:
                        break

        # Delegate tasks
        for task in tasks_to_execute:
            delegation = self.delegate_task(task)
            batch.append(delegation)

        return batch

    def mark_task_complete(self, task_id: str, success: bool = True, results: Dict[str, Any] = None):
        """Mark a task as complete"""
        self.task_status[task_id] = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        # Find and move task to completed list
        for task in self.execution_queue:
            if task.id == task_id:
                if success:
                    self.completed_tasks.append(task)
                break

    def get_progress_report(self) -> Dict[str, Any]:
        """Get current progress report"""
        total_tasks = len(self.tasks)
        completed = sum(1 for status in self.task_status.values() if status == TaskStatus.COMPLETED)
        in_progress = sum(1 for status in self.task_status.values() if status == TaskStatus.IN_PROGRESS)
        failed = sum(1 for status in self.task_status.values() if status == TaskStatus.FAILED)

        return {
            "total_tasks": total_tasks,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total_tasks - completed - in_progress - failed,
            "completion_percentage": (completed / total_tasks * 100) if total_tasks > 0 else 0,
            "status_breakdown": {
                phase: {
                    "total": sum(1 for t in self.tasks if t.phase == phase),
                    "completed": sum(1 for t in self.completed_tasks if t.phase == phase)
                }
                for phase in set(t.phase for t in self.tasks)
            }
        }