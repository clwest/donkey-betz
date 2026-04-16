"""
FullStackDeveloperAgent - Builds complete features with frontend and backend.

This agent can:
- Design and implement full-stack features
- Create API endpoints with corresponding frontend components
- Handle database schema design
- Integrate frontend with backend services
- Build complete CRUD operations

Session 695: SKIN Layer Integration
- Now writes generated code to actual project workspaces
- Full audit trail of all file operations
- Rollback capability for any changes
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from .report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


def analyze_fullstack_requirements_with_ml(requirements_data: dict) -> dict:
    """Analyze full-stack requirements using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=requirements_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'architecture_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML fullstack analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class FullStackDeveloperAgent(BaseAgent):
    """Agent specialized in building complete full-stack features."""

    name = "FullStackDeveloperAgent"
    llm_timeout = 180.0  # Session 1074: TDD generation needs 3 min
    requires_system_context = True  # Session 820: Inject CLAUDE.md + critical docs

    # Session 856: Content review configuration
    actionable_config = ActionableOutputConfig(
        actions=['approve', 'revise', 'reject'],
        payload_fields=['tool_used', 'feature_name', 'backend_framework', 'frontend_framework', 'file_count']
    )

    system_prompt = """You are FullStackDeveloperAgent, an expert full-stack developer capable of building complete features.

IMPORTANT - Response Guidelines:
- Be CONCISE. Provide working code, not architecture lectures.
- For simple features: Give the code directly.
- For complex features: Brief architecture overview (3-5 lines), then code.
- Don't over-explain standard patterns.

Your capabilities:
1. Design and implement features spanning frontend and backend
2. Create RESTful API endpoints with validation
3. Build React/Vue frontend components
4. Design database schemas

Tech stack: Django, FastAPI, React, Vue, TypeScript, PostgreSQL

You have access to tools for:
- build_feature: Create a complete full-stack feature
- create_api_endpoint: Create a backend API endpoint
- create_frontend_component: Create a frontend component
- design_database_schema: Design database tables/models
- integrate_frontend_backend: Connect frontend to backend

Provide complete, working code that can be directly used."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "build_feature",
                "description": "Build a complete full-stack feature with frontend, backend, and database components.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature to build"
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed description of what the feature should do"
                        },
                        "backend_framework": {
                            "type": "string",
                            "description": "Backend framework to use",
                            "enum": ["django", "fastapi", "express", "flask"]
                        },
                        "frontend_framework": {
                            "type": "string",
                            "description": "Frontend framework to use",
                            "enum": ["react", "vue", "vanilla-js", "htmx"]
                        },
                        "database": {
                            "type": "string",
                            "description": "Database to use",
                            "enum": ["postgresql", "mysql", "sqlite", "mongodb"]
                        },
                        "include_auth": {
                            "type": "boolean",
                            "description": "Whether to include authentication",
                            "default": False
                        }
                    },
                    "required": ["feature_name", "description", "backend_framework", "frontend_framework"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_api_endpoint",
                "description": "Create a REST API endpoint with proper validation and error handling.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint_path": {
                            "type": "string",
                            "description": "API endpoint path (e.g., /api/users)"
                        },
                        "methods": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "HTTP methods to support (GET, POST, PUT, DELETE)"
                        },
                        "framework": {
                            "type": "string",
                            "description": "Backend framework",
                            "enum": ["django", "fastapi", "express", "flask"]
                        },
                        "request_schema": {
                            "type": "object",
                            "description": "Schema for request body validation"
                        },
                        "response_schema": {
                            "type": "object",
                            "description": "Schema for response format"
                        },
                        "requires_auth": {
                            "type": "boolean",
                            "description": "Whether endpoint requires authentication",
                            "default": False
                        }
                    },
                    "required": ["endpoint_path", "methods", "framework"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_frontend_component",
                "description": "Create a frontend component with proper state management and API integration.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "component_name": {
                            "type": "string",
                            "description": "Name of the component"
                        },
                        "component_type": {
                            "type": "string",
                            "description": "Type of component",
                            "enum": ["page", "form", "list", "card", "modal", "table", "dashboard"]
                        },
                        "framework": {
                            "type": "string",
                            "description": "Frontend framework",
                            "enum": ["react", "vue", "vanilla-js"]
                        },
                        "api_endpoints": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "API endpoints this component will interact with"
                        },
                        "styling": {
                            "type": "string",
                            "description": "Styling approach",
                            "enum": ["tailwind", "css-modules", "styled-components", "plain-css"],
                            "default": "tailwind"
                        },
                        "include_loading_states": {
                            "type": "boolean",
                            "description": "Include loading/error states",
                            "default": True
                        }
                    },
                    "required": ["component_name", "component_type", "framework"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "design_database_schema",
                "description": "Design database schema with models, relationships, and migrations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of entities/tables to create"
                        },
                        "relationships": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Relationships between entities (e.g., 'User has many Posts')"
                        },
                        "database": {
                            "type": "string",
                            "description": "Database type",
                            "enum": ["postgresql", "mysql", "sqlite", "mongodb"]
                        },
                        "orm": {
                            "type": "string",
                            "description": "ORM to use",
                            "enum": ["django-orm", "sqlalchemy", "prisma", "mongoose", "typeorm"]
                        },
                        "include_timestamps": {
                            "type": "boolean",
                            "description": "Include created_at/updated_at fields",
                            "default": True
                        },
                        "include_soft_delete": {
                            "type": "boolean",
                            "description": "Include soft delete capability",
                            "default": False
                        }
                    },
                    "required": ["entities", "database", "orm"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "integrate_frontend_backend",
                "description": "Create the integration layer between frontend and backend (API client, hooks, services).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "frontend_framework": {
                            "type": "string",
                            "description": "Frontend framework",
                            "enum": ["react", "vue", "vanilla-js"]
                        },
                        "api_base_url": {
                            "type": "string",
                            "description": "Base URL for API calls"
                        },
                        "endpoints": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "method": {"type": "string"},
                                    "path": {"type": "string"}
                                }
                            },
                            "description": "List of API endpoints to integrate"
                        },
                        "auth_type": {
                            "type": "string",
                            "description": "Authentication type",
                            "enum": ["jwt", "session", "api-key", "none"],
                            "default": "none"
                        },
                        "use_react_query": {
                            "type": "boolean",
                            "description": "Use React Query for data fetching (React only)",
                            "default": True
                        }
                    },
                    "required": ["frontend_framework", "api_base_url", "endpoints"]
                }
            }
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a full-stack development task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("fullstack_development", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                # Call OpenAI using BaseAgent's method
                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for full-stack development",
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 880: Write generated files to workspace
                        workspace_write_result = None
                        all_files = []
                        for res in all_results:
                            tool_data = res.get('data', {})
                            if tool_data.get('files'):
                                all_files.extend(tool_data['files'])

                        if all_files:
                            workspace_write_result = self._write_files_to_workspace(
                                files=all_files,
                                user=self.user
                            )
                            if workspace_write_result.get('written'):
                                logger.info(f"✅ [FullStackDeveloperAgent] Wrote {workspace_write_result.get('total_written', 0)} files to workspace")
                            else:
                                logger.warning(f"⚠️ [FullStackDeveloperAgent] Workspace write skipped: {workspace_write_result.get('reason', 'unknown')}")

                        # Session 856: Build descriptive message based on tool used
                        first_result = all_results[0]
                        tool_used = first_result['source']
                        tool_data = first_result.get('data', {})
                        if tool_used == 'build_feature':
                            feature_name = tool_data.get('feature_name', 'unknown')
                            backend = tool_data.get('backend_framework', '')
                            frontend = tool_data.get('frontend_framework', '')
                            file_count = tool_data.get('file_count', 0)
                            descriptive_msg = f"Full-stack feature '{feature_name}' built: {backend}/{frontend} ({file_count} files)"
                        elif tool_used == 'create_api_endpoint':
                            endpoint = tool_data.get('endpoint_path', '/api/unknown')
                            methods = tool_data.get('methods', [])
                            framework = tool_data.get('framework', '')
                            descriptive_msg = f"API endpoint created: {', '.join(methods)} {endpoint} ({framework})"
                        elif tool_used == 'create_frontend_component':
                            component = tool_data.get('component_name', 'unknown')
                            comp_type = tool_data.get('component_type', 'component')
                            framework = tool_data.get('framework', '')
                            descriptive_msg = f"Frontend {comp_type} created: {component} ({framework})"
                        elif tool_used == 'design_database_schema':
                            entities = tool_data.get('entities', [])
                            orm = tool_data.get('orm', '')
                            descriptive_msg = f"Database schema designed: {len(entities)} entities using {orm}"
                        elif tool_used == 'integrate_frontend_backend':
                            framework = tool_data.get('frontend_framework', '')
                            endpoints = tool_data.get('endpoints_count', 0)
                            descriptive_msg = f"Integration layer created: {framework} with {endpoints} API endpoints"
                        else:
                            descriptive_msg = f"Full-stack development '{tool_used}' completed"

                        # Session 880: Append workspace write info to message
                        if workspace_write_result and workspace_write_result.get('written'):
                            descriptive_msg += f" | 📁 {workspace_write_result.get('total_written', 0)} files written to workspace"

                        # Session 954: Build provenance for development output
                        from datetime import timezone
                        import time as time_module
                        provenance_sources = [{
                            'name': 'FullStackDevelopment',
                            'endpoint': 'fullstack/build',
                            'retrieved_at': time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime()),
                            'record_count': len(all_files) if all_files else len(all_results),
                        }]
                        if context:
                            provenance_sources.append({
                                'name': 'ProjectContext',
                                'endpoint': 'context/project',
                                'retrieved_at': time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime()),
                                'record_count': 1,
                            })
                        provenance = build_provenance(
                            report_type='code_generation',
                            agent_name=self.name,
                            sources=provenance_sources,
                            stale_threshold_hours=168.0,  # Code valid for 1 week
                        )
                        provenance.disclaimer = "Generated code. Review and test before deployment to production."

                        # Enrich result data for content review
                        result_data = {
                            'results': all_results,
                            'query': task,
                            'tool_used': tool_used,
                            'feature_name': tool_data.get('feature_name'),
                            'backend_framework': tool_data.get('backend_framework') or tool_data.get('framework'),
                            'frontend_framework': tool_data.get('frontend_framework'),
                            'file_count': tool_data.get('file_count', len(tool_data.get('files', []))),
                            'workspace_write': workspace_write_result,  # Session 880: Include workspace write info
                            # Session 954: Add provenance
                            'provenance': provenance.to_dict(),
                            'publishable': provenance.publishable,
                            'validation_status': provenance.validation_status,
                        }

                        # Session 1200: Synthesize tool results into real analysis
                        tool_results_list = [tc.get('result', {}) for tc in tool_calls_made]
                        synthesis = self._synthesize_tool_results(tool_calls_made, tool_results_list, task)
                        analysis_msg = synthesis if synthesis else descriptive_msg

                        result = AgentResult(
                            success=True,
                            message=analysis_msg,
                            data={**result_data, 'content': synthesis},
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution
                        )

                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=False,
                            scifi_context_used=bool(scifi_context)
                        )

                        # Session 1006: Persist output to Deliverable
                        self._save_to_deliverable(
                            title=f"Full-Stack: {tool_data.get('feature_name', task[:80])}",
                            content=analysis_msg,
                            deliverable_type='code',
                            category='Full-Stack Development',
                            tags=['fullstack', tool_used],
                            metadata={'task': task[:200], 'tool_used': tool_used, 'feature_name': tool_data.get('feature_name')},
                        )

                        return result

                # No tool calls - return GPT content directly
                content = gpt_response.get('content', 'I can help build full-stack features. Please provide more details.')
                execution_time = int((time.time() - start_time) * 1000)

                result = AgentResult(
                    success=True,
                    message=content,
                    agent_name=self.name,
                    execution_time_ms=execution_time
                )

                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=False,
                    scifi_context_used=bool(scifi_context)
                )

                return result

            except Exception as e:
                error_msg = f"Full-stack development failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "build_feature":
            return self._build_feature(**arguments)
        elif tool_name == "create_api_endpoint":
            return self._create_api_endpoint(**arguments)
        elif tool_name == "create_frontend_component":
            return self._create_frontend_component(**arguments)
        elif tool_name == "design_database_schema":
            return self._design_database_schema(**arguments)
        elif tool_name == "integrate_frontend_backend":
            return self._integrate_frontend_backend(**arguments)

        return super()._execute_tool_call(tool_name, arguments)

    def _build_feature(
        self,
        feature_name: str,
        description: str,
        backend_framework: str,
        frontend_framework: str,
        database: str = "postgresql",
        include_auth: bool = False
    ) -> Dict[str, Any]:
        """Build a complete full-stack feature."""
        client = get_openai_client()

        auth_section = """
Include authentication:
- JWT token authentication
- Protected routes
- Login/logout functionality""" if include_auth else ""

        prompt = f"""Build a complete full-stack feature:

Feature: {feature_name}
Description: {description}
Backend: {backend_framework}
Frontend: {frontend_framework}
Database: {database}
{auth_section}

Generate ALL of the following:

1. DATABASE SCHEMA
- Model/table definitions
- Relationships
- Migration file

2. BACKEND API
- API endpoint(s) with full CRUD operations
- Request/response validation
- Error handling
- URL routing

3. FRONTEND COMPONENT(S)
- Main component with state management
- Form handling
- API integration
- Loading/error states
- Styling with Tailwind CSS

4. INTEGRATION
- API client/service
- Types/interfaces

Format each file with:
### path/to/file.ext
```language
content
```"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a senior full-stack developer. Generate complete, production-ready code."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=10000
        )

        feature_code = response.choices[0].message.content
        files = self._parse_files(feature_code)

        return {
            "success": True,
            "feature_name": feature_name,
            "backend_framework": backend_framework,
            "frontend_framework": frontend_framework,
            "database": database,
            "code": feature_code,
            "files": files,
            "file_count": len(files)
        }

    def _create_api_endpoint(
        self,
        endpoint_path: str,
        methods: List[str],
        framework: str,
        request_schema: Dict = None,
        response_schema: Dict = None,
        requires_auth: bool = False
    ) -> Dict[str, Any]:
        """Create a REST API endpoint."""
        client = get_openai_client()

        auth_note = "Include authentication decorator/middleware." if requires_auth else ""

        prompt = f"""Create a {framework} API endpoint:

Path: {endpoint_path}
Methods: {', '.join(methods)}
Request Schema: {json.dumps(request_schema) if request_schema else 'Not specified'}
Response Schema: {json.dumps(response_schema) if response_schema else 'Not specified'}
{auth_note}

Generate:
1. View/handler function(s)
2. URL routing configuration
3. Request validation (serializers/schemas)
4. Proper error responses
5. Example usage with curl"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {framework} backend expert. Generate clean, secure API code."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "endpoint_path": endpoint_path,
            "methods": methods,
            "framework": framework,
            "requires_auth": requires_auth,
            "code": response.choices[0].message.content
        }

    def _create_frontend_component(
        self,
        component_name: str,
        component_type: str,
        framework: str,
        api_endpoints: List[str] = None,
        styling: str = "tailwind",
        include_loading_states: bool = True
    ) -> Dict[str, Any]:
        """Create a frontend component."""
        client = get_openai_client()

        api_integration = f"Integrate with API endpoints: {', '.join(api_endpoints)}" if api_endpoints else ""
        loading_note = "Include loading, error, and empty states." if include_loading_states else ""

        prompt = f"""Create a {framework} {component_type} component:

Component: {component_name}
Framework: {framework}
Styling: {styling}
{api_integration}
{loading_note}

Generate:
1. Main component with proper state management
2. TypeScript types/interfaces (if using TypeScript)
3. API integration hooks/functions
4. Complete styling with {styling}
5. Error boundary handling"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {framework} frontend expert. Generate modern, accessible components."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "component_name": component_name,
            "component_type": component_type,
            "framework": framework,
            "styling": styling,
            "code": response.choices[0].message.content
        }

    def _design_database_schema(
        self,
        entities: List[str],
        database: str,
        orm: str,
        relationships: List[str] = None,
        include_timestamps: bool = True,
        include_soft_delete: bool = False
    ) -> Dict[str, Any]:
        """Design database schema."""
        client = get_openai_client()

        rel_text = '\n'.join(f"- {r}" for r in relationships) if relationships else "No explicit relationships specified"
        timestamp_note = "Include created_at and updated_at fields." if include_timestamps else ""
        soft_delete_note = "Include soft delete (deleted_at field)." if include_soft_delete else ""

        prompt = f"""Design a database schema:

Entities: {', '.join(entities)}
Relationships:
{rel_text}
Database: {database}
ORM: {orm}
{timestamp_note}
{soft_delete_note}

Generate:
1. Complete model definitions for each entity
2. Relationship definitions (foreign keys, many-to-many)
3. Indexes for common queries
4. Migration file(s)
5. Example queries for common operations"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a database architect expert in {orm}. Design efficient, normalized schemas."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "entities": entities,
            "database": database,
            "orm": orm,
            "schema": response.choices[0].message.content
        }

    def _integrate_frontend_backend(
        self,
        frontend_framework: str,
        api_base_url: str,
        endpoints: List[Dict],
        auth_type: str = "none",
        use_react_query: bool = True
    ) -> Dict[str, Any]:
        """Create frontend-backend integration layer."""
        client = get_openai_client()

        query_note = "Use React Query for data fetching and caching." if use_react_query and frontend_framework == "react" else ""

        prompt = f"""Create API integration layer:

Frontend: {frontend_framework}
Base URL: {api_base_url}
Auth Type: {auth_type}
{query_note}

Endpoints:
{json.dumps(endpoints, indent=2)}

Generate:
1. API client configuration (axios/fetch setup)
2. Authentication handling (if applicable)
3. API service functions for each endpoint
4. TypeScript types for request/response
5. Custom hooks for data fetching (React) or composables (Vue)
6. Error handling utilities"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {frontend_framework} integration expert. Generate clean, type-safe API clients."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "frontend_framework": frontend_framework,
            "api_base_url": api_base_url,
            "endpoints_count": len(endpoints),
            "auth_type": auth_type,
            "code": response.choices[0].message.content
        }

    def _parse_files(self, content: str) -> List[Dict[str, str]]:
        """Parse generated content into individual files."""
        files = []
        pattern = r'###\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        for filename, language, code in matches:
            files.append({
                "filename": filename.strip(),
                "language": language or "text",
                "content": code.strip()
            })

        return files

    # =========================================================================
    # SESSION 695: SKIN LAYER INTEGRATION
    # Workspace methods are now inherited from BaseAgent.
    # All agents can use execute_with_workspace() to write files.
    # =========================================================================
