"""
Project Builder Orchestrator
Deploys and coordinates teams of specialized agents to build complete applications
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from .llm_enforcer import get_llm_enforcer
from .tools import ToolRegistry

# Import project builder agents
try:
    from backend.agents.concrete_executor import concrete_executor
    from backend.agents.project_builder_base import ProjectBuilderAgent, FullStackBuilderAgent
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import project builder agents: {e}")
    concrete_executor = None
    ProjectBuilderAgent = None
    FullStackBuilderAgent = None

logger = logging.getLogger(__name__)


class ProjectPhase(Enum):
    """Phases of project development"""
    PLANNING = "planning"
    ARCHITECTURE = "architecture"
    BACKEND_SETUP = "backend_setup"
    DATABASE_DESIGN = "database_design"
    FRONTEND_SETUP = "frontend_setup"
    API_DEVELOPMENT = "api_development"
    UI_IMPLEMENTATION = "ui_implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMPLETE = "complete"


@dataclass
class ProjectSpec:
    """Project specification from idea phase"""
    name: str
    description: str
    tech_stack: Dict[str, str]  # e.g., {"backend": "django", "frontend": "react", "db": "postgres"}
    features: List[str]
    requirements: List[str]
    timeline: Optional[str] = None


@dataclass
class AgentTask:
    """Task assigned to a specific agent"""
    agent_type: str
    task_description: str
    dependencies: List[str] = None
    output_expected: str = None
    phase: ProjectPhase = ProjectPhase.PLANNING
    status: str = "pending"
    result: Any = None


class ProjectBuilderOrchestrator:
    """
    Orchestrates multiple specialized agents to build complete projects
    """

    def __init__(self):
        self.llm_enforcer = get_llm_enforcer()
        self.active_projects = {}
        self.agent_registry = self._initialize_agent_types()

    def _initialize_agent_types(self):
        """Define specialized agent types for project building"""
        return {
            "architect": {
                "name": "System Architect",
                "skills": ["system design", "architecture patterns", "scalability"],
                "tools": ["documentation_fetcher"],
                "phases": [ProjectPhase.PLANNING, ProjectPhase.ARCHITECTURE]
            },
            "backend_developer": {
                "name": "Backend Developer",
                "skills": ["Django", "FastAPI", "REST APIs", "authentication"],
                "tools": ["documentation_fetcher", "web_search"],
                "phases": [ProjectPhase.BACKEND_SETUP, ProjectPhase.API_DEVELOPMENT]
            },
            "database_engineer": {
                "name": "Database Engineer",
                "skills": ["PostgreSQL", "MongoDB", "Redis", "data modeling"],
                "tools": ["documentation_fetcher"],
                "phases": [ProjectPhase.DATABASE_DESIGN]
            },
            "frontend_developer": {
                "name": "Frontend Developer",
                "skills": ["React", "Vue", "TypeScript", "Tailwind CSS"],
                "tools": ["documentation_fetcher", "web_search"],
                "phases": [ProjectPhase.FRONTEND_SETUP, ProjectPhase.UI_IMPLEMENTATION]
            },
            "devops_engineer": {
                "name": "DevOps Engineer",
                "skills": ["Docker", "CI/CD", "AWS", "Kubernetes"],
                "tools": ["documentation_fetcher"],
                "phases": [ProjectPhase.DEPLOYMENT]
            },
            "qa_engineer": {
                "name": "QA Engineer",
                "skills": ["testing", "Jest", "Pytest", "Cypress"],
                "tools": ["documentation_fetcher"],
                "phases": [ProjectPhase.TESTING]
            },
            "code_reviewer": {
                "name": "Code Reviewer",
                "skills": ["code quality", "best practices", "security"],
                "tools": ["web_search"],
                "phases": [ProjectPhase.TESTING, ProjectPhase.COMPLETE]
            }
        }

    async def create_project_from_idea(self, idea: str, requirements: List[str] = None) -> ProjectSpec:
        """
        Convert an app idea into a detailed project specification
        """
        logger.info(f"Creating project spec from idea: {idea[:100]}...")

        # Use LLM to analyze idea and create spec
        prompt = f"""
        Analyze this app idea and create a technical specification:

        Idea: {idea}
        Requirements: {', '.join(requirements) if requirements else 'None specified'}

        Create a detailed technical specification including:
        1. Project name (short, memorable)
        2. Tech stack recommendation (backend, frontend, database)
        3. Core features list (5-10 main features)
        4. Technical requirements
        5. Suggested timeline

        Consider modern best practices and scalability.
        """

        result = self.llm_enforcer.enforce_real_ai(
            prompt=prompt,
            agent_name="Project Architect",
            task_type="analysis",
            max_tokens=1000
        )

        if result['success']:
            # Parse the response to create ProjectSpec
            # In production, you'd parse the structured response
            spec = ProjectSpec(
                name=f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=idea,
                tech_stack={
                    "backend": "django",
                    "frontend": "react",
                    "database": "postgresql",
                    "cache": "redis"
                },
                features=requirements or ["User authentication", "Dashboard", "API"],
                requirements=["Python 3.11+", "Node.js 18+", "PostgreSQL 15+"],
                timeline="2-4 weeks"
            )

            self.active_projects[spec.name] = {
                "spec": spec,
                "phase": ProjectPhase.PLANNING,
                "agents": {},
                "tasks": [],
                "artifacts": {}
            }

            return spec

        raise Exception("Failed to create project specification")

    def plan_project_phases(self, project_spec: ProjectSpec) -> List[AgentTask]:
        """
        Create a detailed task list for all project phases
        """
        tasks = []

        # Phase 1: Architecture
        tasks.append(AgentTask(
            agent_type="architect",
            task_description="Design system architecture and create component diagram",
            output_expected="architecture.md, component_diagram.json",
            phase=ProjectPhase.ARCHITECTURE
        ))

        # Phase 2: Database Design
        tasks.append(AgentTask(
            agent_type="database_engineer",
            task_description="Design database schema and relationships",
            dependencies=["architecture"],
            output_expected="schema.sql, models.py",
            phase=ProjectPhase.DATABASE_DESIGN
        ))

        # Phase 3: Backend Setup
        tasks.append(AgentTask(
            agent_type="backend_developer",
            task_description=f"Setup {project_spec.tech_stack['backend']} project structure",
            dependencies=["database"],
            output_expected="backend/settings.py, requirements.txt",
            phase=ProjectPhase.BACKEND_SETUP
        ))

        # Phase 4: Frontend Setup
        tasks.append(AgentTask(
            agent_type="frontend_developer",
            task_description=f"Setup {project_spec.tech_stack['frontend']} project with TypeScript",
            output_expected="package.json, tsconfig.json, App.tsx",
            phase=ProjectPhase.FRONTEND_SETUP
        ))

        # Phase 5: API Development
        tasks.append(AgentTask(
            agent_type="backend_developer",
            task_description="Implement REST API endpoints",
            dependencies=["backend_setup", "database"],
            output_expected="api/views.py, api/serializers.py, urls.py",
            phase=ProjectPhase.API_DEVELOPMENT
        ))

        # Phase 6: UI Implementation
        tasks.append(AgentTask(
            agent_type="frontend_developer",
            task_description="Implement UI components and connect to API",
            dependencies=["frontend_setup", "api"],
            output_expected="components/*, pages/*, hooks/*",
            phase=ProjectPhase.UI_IMPLEMENTATION
        ))

        # Phase 7: Testing
        tasks.append(AgentTask(
            agent_type="qa_engineer",
            task_description="Write unit and integration tests",
            dependencies=["api", "ui"],
            output_expected="tests/*, cypress/*",
            phase=ProjectPhase.TESTING
        ))

        # Phase 8: Deployment
        tasks.append(AgentTask(
            agent_type="devops_engineer",
            task_description="Create Docker configuration and deployment scripts",
            dependencies=["testing"],
            output_expected="Dockerfile, docker-compose.yml, deploy.sh",
            phase=ProjectPhase.DEPLOYMENT
        ))

        return tasks

    async def deploy_agent_for_task(self, task: AgentTask, project_spec: ProjectSpec) -> Dict[str, Any]:
        """
        Deploy a specialized agent to complete a specific task
        """
        agent_info = self.agent_registry.get(task.agent_type)
        if not agent_info:
            raise ValueError(f"Unknown agent type: {task.agent_type}")

        logger.info(f"Deploying {agent_info['name']} for: {task.task_description}")

        # Get relevant documentation if needed
        doc_context = ""
        if "documentation_fetcher" in agent_info.get("tools", []):
            doc_tool = ToolRegistry.get_tool("documentation_fetcher")
            if doc_tool:
                # Fetch relevant docs based on tech stack
                if "backend" in task.agent_type:
                    framework = project_spec.tech_stack.get("backend", "django")
                elif "frontend" in task.agent_type:
                    framework = project_spec.tech_stack.get("frontend", "react")
                else:
                    framework = "python"

                doc_result = await doc_tool.fetch_documentation(
                    framework=framework,
                    topic=task.task_description[:50]
                )
                if doc_result.get("success"):
                    doc_context = f"\nDocumentation: {doc_result.get('documentation_url')}"

        # Build agent prompt
        prompt = f"""
        You are {agent_info['name']}, a specialized agent with skills in: {', '.join(agent_info['skills'])}

        Project: {project_spec.name}
        Description: {project_spec.description}
        Tech Stack: {json.dumps(project_spec.tech_stack)}

        Your Task: {task.task_description}
        Expected Output: {task.output_expected}
        {doc_context}

        Provide detailed implementation code and instructions.
        Focus on production-ready, scalable solutions.
        Use the latest best practices for the frameworks involved.
        """

        # Execute agent task
        result = self.llm_enforcer.enforce_real_ai(
            prompt=prompt,
            agent_name=agent_info['name'],
            task_type="code",
            max_tokens=2000,
            temperature=0.3  # Lower temperature for more consistent code
        )

        if result['success']:
            task.status = "completed"
            task.result = result['response']

            return {
                "success": True,
                "agent": agent_info['name'],
                "task": task.task_description,
                "output": result['response'],
                "phase": task.phase.value
            }

        task.status = "failed"
        return {
            "success": False,
            "error": result.get('error', 'Task execution failed')
        }

    async def build_project(self,
                          idea: str,
                          requirements: List[str] = None,
                          parallel_execution: bool = True,
                          use_real_agents: bool = True) -> Dict[str, Any]:
        """
        Orchestrate the complete project building process with real agents
        """
        logger.info("Starting project build orchestration...")

        # Step 1: Create project specification
        project_spec = await self.create_project_from_idea(idea, requirements)

        # Use real project building agents if available
        if use_real_agents and concrete_executor and FullStackBuilderAgent:
            logger.info("🚀 Using REAL project building agents")
            return await self._build_project_with_real_agents(project_spec)

        # Fallback to original LLM-only approach
        logger.info("📝 Using LLM-only project planning (no real execution)")
        return await self._build_project_with_llm_only(project_spec, parallel_execution)

    async def _build_project_with_real_agents(self, project_spec: ProjectSpec) -> Dict[str, Any]:
        """Build project using real agents that create actual files"""
        try:
            # Create task for the concrete executor
            build_task = {
                'type': 'fullstack',
                'task_description': f"Build a full-stack application: {project_spec.description}",
                'input': {
                    'project_name': project_spec.name,
                    'tech_stack': project_spec.tech_stack,
                    'features': project_spec.features,
                    'containerize': True,
                    'git_init': True
                }
            }

            # Execute with the concrete executor
            logger.info(f"🏗️ Deploying real agent to build: {project_spec.name}")
            result = await concrete_executor.execute_agent('fullstack_builder', build_task)

            if result['success']:
                logger.info(f"✅ Real agent successfully built project: {project_spec.name}")

                # Extract meaningful information from the real execution
                agent_result = result.get('result', {})
                implementation_metrics = result.get('implementation_metrics', {})

                return {
                    "project_name": project_spec.name,
                    "specification": {
                        "description": project_spec.description,
                        "tech_stack": project_spec.tech_stack,
                        "features": project_spec.features
                    },
                    "real_execution": True,
                    "project_path": agent_result.get('project_path'),
                    "files_created": agent_result.get('files_created', []),
                    "files_count": implementation_metrics.get('files_created', 0),
                    "commands_executed": implementation_metrics.get('commands_executed', 0),
                    "build_log": result.get('build_log', []),
                    "execution_time": result.get('execution_time', 0),
                    "ai_stats": result.get('ai_stats', {}),
                    "agent_used": result.get('agent'),
                    "build_success": agent_result.get('build_success', False),
                    "test_success": agent_result.get('test_success', False),
                    "status": "complete" if agent_result.get('success') else "partial",
                    "success": True
                }
            else:
                logger.error(f"❌ Real agent failed to build project: {result.get('error')}")

                return {
                    "project_name": project_spec.name,
                    "real_execution": True,
                    "success": False,
                    "error": result.get('error'),
                    "status": "failed"
                }

        except Exception as e:
            logger.error(f"❌ Error in real agent project building: {str(e)}")

            return {
                "project_name": project_spec.name,
                "real_execution": True,
                "success": False,
                "error": str(e),
                "status": "failed"
            }

    async def _build_project_with_llm_only(self, project_spec: ProjectSpec, parallel_execution: bool) -> Dict[str, Any]:
        """Fallback to LLM-only project planning (original approach)"""
        # Step 2: Plan all tasks
        tasks = self.plan_project_phases(project_spec)

        # Step 3: Execute tasks (LLM planning only)
        results = []
        completed_tasks = set()

        for current_phase in ProjectPhase:
            phase_tasks = [t for t in tasks if t.phase == current_phase]

            if not phase_tasks:
                continue

            logger.info(f"Executing phase: {current_phase.value}")

            if parallel_execution:
                # Execute tasks in parallel within the same phase
                phase_results = await asyncio.gather(*[
                    self.deploy_agent_for_task(task, project_spec)
                    for task in phase_tasks
                    if not task.dependencies or all(d in completed_tasks for d in task.dependencies)
                ])
                results.extend(phase_results)
            else:
                # Sequential execution
                for task in phase_tasks:
                    if task.dependencies and not all(d in completed_tasks for d in task.dependencies):
                        continue

                    result = await self.deploy_agent_for_task(task, project_spec)
                    results.append(result)

                    if result['success']:
                        completed_tasks.add(task.task_description[:20])

        # Step 4: Compile final project
        return {
            "project_name": project_spec.name,
            "specification": {
                "description": project_spec.description,
                "tech_stack": project_spec.tech_stack,
                "features": project_spec.features
            },
            "real_execution": False,
            "phases_completed": len(set(t.phase for t in tasks if t.status == "completed")),
            "tasks_completed": len([t for t in tasks if t.status == "completed"]),
            "total_tasks": len(tasks),
            "results": results,
            "status": "complete" if all(t.status == "completed" for t in tasks) else "partial"
        }

    async def generate_project_files(self, project_name: str) -> Dict[str, str]:
        """
        Generate actual project files from completed tasks
        """
        project = self.active_projects.get(project_name)
        if not project:
            raise ValueError(f"Project {project_name} not found")

        files = {}

        # This would generate actual files based on task results
        # For now, return a structure
        files = {
            "README.md": "# Project Documentation",
            "requirements.txt": "django>=4.2\ndjango-cors-headers\ndjango-rest-framework\nredis\ncelery",
            "package.json": '{"name": "frontend", "dependencies": {"react": "^18.2.0"}}',
            "docker-compose.yml": "version: '3.8'\nservices:\n  web:\n    build: .\n    ports:\n      - '8000:8000'",
        }

        return files


# Global orchestrator instance
_project_orchestrator = None


def get_project_orchestrator() -> ProjectBuilderOrchestrator:
    """Get the global project orchestrator instance"""
    global _project_orchestrator
    if _project_orchestrator is None:
        _project_orchestrator = ProjectBuilderOrchestrator()
    return _project_orchestrator