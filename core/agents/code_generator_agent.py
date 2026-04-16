"""
CodeGeneratorAgent - Generates code, creates files, and builds projects.

This agent can:
- Generate code from specifications
- Create file structures for projects
- Analyze existing codebases
- Refactor and improve code
- Generate tests for code
"""

import logging
import re
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


def analyze_code_requirements_with_ml(code_data: dict) -> dict:
    """Analyze code requirements using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=code_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'code_analysis': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML code analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class CodeGeneratorAgent(BaseAgent):
    """Agent specialized in generating code and building projects."""

    name = "CodeGeneratorAgent"  # Session 830: Multi-turn enabled

    system_prompt = """You are CodeGeneratorAgent, an expert software developer who can DIRECTLY modify codebases.

CRITICAL - You have REAL FILE SYSTEM ACCESS:
You can read, write, and edit actual files in the project workspace. When asked to fix code or make changes:
1. ALWAYS use read_file first to see the current code
2. Use edit_file for targeted changes (preferred) or write_file for new files
3. Use list_files and search_in_files to explore the codebase

NEVER just output code snippets when asked to fix something - actually use your file tools to make the changes!

CRITICAL - FILE PATHS FROM TASK:
When your task includes "Relevant File Locations:" or mentions specific file paths like:
- `intelligence/tasks.py:19`
- `core/views.py:95`

You MUST:
1. Use read_file to read THOSE SPECIFIC FILES first
2. Use edit_file to modify THOSE SPECIFIC FILES
3. NEVER create new files like "generated_1.py" - edit the actual target files!

Your file operation tools:
- read_file: Read file contents (USE THIS FIRST to understand existing code)
- write_file: Create new files or completely replace existing files
- edit_file: Make surgical changes by replacing specific text (PREFERRED for fixes)
- list_files: Explore project structure
- search_in_files: Find where things are defined/used

Your code generation tools:
- generate_code: Generate code from specifications (for NEW code only)
- create_project_structure: Scaffold new projects
- analyze_code: Analyze code quality
- refactor_code: Improve existing code
- generate_tests: Create tests

WORKFLOW for fixing code issues:
1. Extract file paths from the task (look for "Relevant File Locations" or file:line patterns)
2. read_file to see the actual code at those paths
3. edit_file to make the specific fix (find exact text to replace)
4. Verify the change was successful

IMPORTANT RULES:
- Be CONCISE. Provide working code, not essays.
- For edit_file: The old_text must match EXACTLY what's in the file
- Always read a file before trying to edit it
- If old_text isn't found, re-read the file and try again with exact text
- NEVER create generic files like generated_1.py, output.py, etc.
- ALWAYS edit the actual source files mentioned in the task

DELEGATION (Session 744):
If you need something outside your expertise, use delegate_to_specialist:
- Research → ResearchAgent
- Documentation → ContentWriterAgent
- Code review → CodeReviewAgent"""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_code",
                "description": "Generate NEW code from a specification. ONLY use for creating NEW files. For fixing existing code, use read_file + edit_file instead!",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "specification": {
                            "type": "string",
                            "description": "Detailed description of what the code should do"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (python, javascript, typescript, etc.)",
                            "enum": ["python", "javascript", "typescript", "html", "css", "sql", "bash", "go", "rust", "java"]
                        },
                        "framework": {
                            "type": "string",
                            "description": "Optional framework context (django, react, vue, fastapi, express, etc.)"
                        },
                        "target_file": {
                            "type": "string",
                            "description": "File path to write the generated code to (e.g., 'core/services/my_service.py')"
                        },
                        "include_tests": {
                            "type": "boolean",
                            "description": "Whether to include unit tests",
                            "default": False
                        },
                        "include_docs": {
                            "type": "boolean",
                            "description": "Whether to include docstrings/comments",
                            "default": True
                        }
                    },
                    "required": ["specification", "language"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_project_structure",
                "description": "Create a complete project with directory structure and files. Use this to scaffold new projects.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project"
                        },
                        "project_type": {
                            "type": "string",
                            "description": "Type of project to create",
                            "enum": ["python-package", "django-app", "fastapi-app", "react-app", "vue-app", "node-api", "cli-tool", "library"]
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of what the project does"
                        },
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of features/modules to include"
                        },
                        "include_docker": {
                            "type": "boolean",
                            "description": "Include Docker configuration",
                            "default": False
                        },
                        "include_ci": {
                            "type": "boolean",
                            "description": "Include CI/CD configuration (GitHub Actions)",
                            "default": False
                        }
                    },
                    "required": ["project_name", "project_type", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_code",
                "description": "Analyze code for patterns, issues, architecture, and improvement opportunities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to analyze"
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["architecture", "security", "performance", "code-quality", "all"]
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language of the code"
                        }
                    },
                    "required": ["code", "analysis_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "refactor_code",
                "description": "Refactor existing code to improve quality, performance, or readability.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to refactor"
                        },
                        "refactor_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Goals for refactoring (e.g., 'improve readability', 'reduce complexity', 'add type hints')"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "preserve_api": {
                            "type": "boolean",
                            "description": "Whether to preserve the public API/interface",
                            "default": True
                        }
                    },
                    "required": ["code", "refactor_goals"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_tests",
                "description": "Generate comprehensive tests for existing code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to generate tests for"
                        },
                        "test_framework": {
                            "type": "string",
                            "description": "Testing framework to use",
                            "enum": ["pytest", "unittest", "jest", "mocha", "vitest", "go-test"]
                        },
                        "coverage_target": {
                            "type": "string",
                            "description": "Target coverage level",
                            "enum": ["basic", "comprehensive", "edge-cases"],
                            "default": "comprehensive"
                        },
                        "include_mocks": {
                            "type": "boolean",
                            "description": "Include mock objects for dependencies",
                            "default": True
                        }
                    },
                    "required": ["code", "test_framework"]
                }
            }
        },
        # ================================================================
        # SESSION 830: REAL FILE OPERATION TOOLS
        # These tools actually read/write to the codebase via SKIN layer
        # ================================================================
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file from the workspace. Use this to understand existing code before making changes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file relative to workspace root (e.g., 'core/models.py', 'frontend/src/App.tsx')"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write or create a file in the workspace. Use this to create new files or completely replace existing files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file relative to workspace root"
                        },
                        "content": {
                            "type": "string",
                            "description": "Complete content to write to the file"
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of what this file does or why it's being created"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "edit_file",
                "description": "Make a targeted edit to an existing file by replacing specific text. Use this for surgical changes rather than rewriting entire files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the file relative to workspace root"
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The exact text to find and replace (must match exactly)"
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The new text to replace it with"
                        },
                        "description": {
                            "type": "string",
                            "description": "Brief description of what this edit does"
                        }
                    },
                    "required": ["file_path", "old_text", "new_text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in the workspace matching a pattern. Use this to explore the codebase structure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to match files (e.g., '**/*.py', 'core/agents/*.py', 'frontend/src/**/*.tsx')",
                            "default": "**/*"
                        },
                        "directory": {
                            "type": "string",
                            "description": "Optional subdirectory to search in"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_in_files",
                "description": "Search for a text pattern across files in the workspace. Use this to find where something is defined or used.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "search_text": {
                            "type": "string",
                            "description": "Text or pattern to search for"
                        },
                        "file_pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter which files to search (e.g., '**/*.py')",
                            "default": "**/*"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 20
                        }
                    },
                    "required": ["search_text"]
                }
            }
        }
    ]

    def _extract_file_paths_from_task(self, task: str) -> List[str]:
        """
        Session 881: Extract file paths mentioned in the task.

        Looks for patterns like:
        - `intelligence/tasks.py:19`
        - - `core/views_ecosystem_activation.py:95`
        - Relevant File Locations: sections
        """
        file_paths = []

        # Pattern 1: `file_path:line_number` or `file_path`
        backtick_pattern = r'`([a-zA-Z0-9_/\-\.]+\.(?:py|js|ts|tsx|jsx|json|yaml|yml|md|txt|html|css|sql))'
        matches = re.findall(backtick_pattern, task)
        file_paths.extend(matches)

        # Pattern 2: - `path` bullet points
        bullet_pattern = r'-\s*`([^`]+)`'
        matches = re.findall(bullet_pattern, task)
        for m in matches:
            # Clean up line numbers
            clean_path = m.split(':')[0]
            if '.' in clean_path:
                file_paths.append(clean_path)

        # Deduplicate while preserving order
        seen = set()
        unique_paths = []
        for p in file_paths:
            if p not in seen:
                seen.add(p)
                unique_paths.append(p)

        return unique_paths

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute a code generation task with MULTI-TURN TOOL SUPPORT.

        Session 830: Enhanced to loop until LLM stops requesting tools.
        This allows read→edit workflows where the agent:
        1. Reads a file to understand the code
        2. Makes edits based on what it read
        3. Optionally verifies the changes
        """
        import time
        import json

        start_time = time.time()
        tool_calls_made = []
        all_results = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 830: Multi-turn configuration
        MAX_TOOL_ITERATIONS = 5  # Prevent infinite loops
        iteration = 0

        # Session 881: Extract file paths from task to guide the agent
        target_files = self._extract_file_paths_from_task(task)
        if target_files:
            logger.info(f"📁 Session 881: Extracted target files from task: {target_files}")

        with self.time_travel_session("code_generation", task, input_data=context):
            try:
                # Session 529: Use intelligent prompting
                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                knowledge_attribution = None  # Legacy compatibility

                # Session 881: Enhance task with explicit file instructions if targets found
                enhanced_task = task
                if target_files:
                    file_list = ', '.join(target_files)
                    enhanced_task = f"""TARGET FILES TO MODIFY: {file_list}

IMPORTANT: You MUST use read_file and edit_file on these specific files. Do NOT create new files.

{task}"""

                # Session 830: Build conversation history for multi-turn
                conversation_history = [
                    {"role": "user", "content": enhanced_task}
                ]

                final_message = None

                # Session 830: MULTI-TURN TOOL LOOP
                while iteration < MAX_TOOL_ITERATIONS:
                    iteration += 1

                    # Call OpenAI with conversation history
                    gpt_response = self._call_openai(
                        full_prompt,
                        conversation_history=conversation_history if iteration > 1 else None
                    )

                    # Check if LLM wants to call tools
                    if not gpt_response.get('tool_calls'):
                        # No more tool calls - LLM is done
                        final_message = gpt_response.get('content', '')
                        logger.info(f"🔄 {self.name} completed after {iteration} iteration(s), {len(tool_calls_made)} tool call(s)")
                        break

                    # Process tool calls
                    tool_results_for_history = []

                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']
                        tool_call_id = tool_call.get('id', f'call_{len(tool_calls_made)}')

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Iteration {iteration}: Selected {tool_name}",
                            confidence=0.95
                        )

                        # Execute the tool
                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result,
                            'iteration': iteration
                        })

                        if tool_result.get('success'):
                            all_results.append({
                                'source': tool_name,
                                'data': tool_result
                            })

                        # Log file operations
                        if tool_name in ['read_file', 'write_file', 'edit_file']:
                            status = '✅' if tool_result.get('success') else '❌'
                            file_info = tool_result.get('file_path', 'unknown')
                            if not tool_result.get('success'):
                                file_info += f" - {tool_result.get('error', 'no error details')}"
                            logger.info(f"  {status} {tool_name}: {file_info}")

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                        # Prepare tool result for conversation history
                        # Truncate large content to avoid token limits
                        result_for_history = {**tool_result}
                        if 'content' in result_for_history and len(str(result_for_history['content'])) > 2000:
                            result_for_history['content'] = result_for_history['content'][:2000] + '\n... (truncated)'

                        tool_results_for_history.append({
                            'tool_call_id': tool_call_id,
                            'tool_name': tool_name,
                            'result': result_for_history
                        })

                    # Add assistant's tool calls to history
                    conversation_history.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": tr['tool_call_id'],
                                "type": "function",
                                "function": {
                                    "name": tr['tool_name'],
                                    "arguments": json.dumps(tool_calls_made[-len(tool_results_for_history):][i]['arguments'])
                                }
                            }
                            for i, tr in enumerate(tool_results_for_history)
                        ]
                    })

                    # Add tool results to history
                    for tr in tool_results_for_history:
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tr['tool_call_id'],
                            "content": json.dumps(tr['result'])
                        })

                # Build final result
                execution_time = int((time.time() - start_time) * 1000)

                if all_results:
                    result = AgentResult(
                        success=True,
                        message=final_message or f"Completed {len(tool_calls_made)} tool call(s) in {iteration} iteration(s)",
                        data={
                            'results': all_results,
                            'query': task,
                            'iterations': iteration,
                            'tools_used': list(set(tc['tool'] for tc in tool_calls_made))
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made,
                        knowledge_attribution=knowledge_attribution
                    )
                else:
                    # No tool calls at all - return GPT content directly
                    result = AgentResult(
                        success=True,
                        message=final_message or 'I can help with code generation. Please provide more details.',
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

                # Session 1006: Persist output to Deliverable
                if all_results:
                    tools_used = list(set(tc['tool'] for tc in tool_calls_made))
                    self._save_to_deliverable(
                        title=f"Generated Code: {task[:80]}",
                        content=result.message,
                        deliverable_type='code',
                        category='Code Generation',
                        tags=['code'] + tools_used[:3],
                        metadata={'task': task[:200], 'tools_used': tools_used, 'iterations': iteration},
                    )

                return result

            except Exception as e:
                error_msg = f"Code generation failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        # Session 744: Handle delegation to specialists first
        if tool_name == "generate_code":
            return self._generate_code(
                specification=arguments.get("specification", ""),
                language=arguments.get("language", "python"),
                framework=arguments.get("framework"),
                include_tests=arguments.get("include_tests", False),
                include_docs=arguments.get("include_docs", True),
                target_file=arguments.get("target_file")  # Session 881: Persist to file
            )

        elif tool_name == "create_project_structure":
            return self._create_project_structure(
                project_name=arguments.get("project_name", "my-project"),
                project_type=arguments.get("project_type", "python-package"),
                description=arguments.get("description", ""),
                features=arguments.get("features", []),
                include_docker=arguments.get("include_docker", False),
                include_ci=arguments.get("include_ci", False)
            )

        elif tool_name == "analyze_code":
            return self._analyze_code(
                code=arguments.get("code", ""),
                analysis_type=arguments.get("analysis_type", "all"),
                language=arguments.get("language", "python")
            )

        elif tool_name == "refactor_code":
            return self._refactor_code(
                code=arguments.get("code", ""),
                refactor_goals=arguments.get("refactor_goals", []),
                language=arguments.get("language", "python"),
                preserve_api=arguments.get("preserve_api", True)
            )

        elif tool_name == "generate_tests":
            return self._generate_tests(
                code=arguments.get("code", ""),
                test_framework=arguments.get("test_framework", "pytest"),
                coverage_target=arguments.get("coverage_target", "comprehensive"),
                include_mocks=arguments.get("include_mocks", True)
            )

        # ================================================================
        # SESSION 830: REAL FILE OPERATION TOOLS
        # ================================================================
        elif tool_name == "read_file":
            return self._read_file(
                file_path=arguments.get("file_path", "")
            )

        elif tool_name == "write_file":
            return self._write_file(
                file_path=arguments.get("file_path", ""),
                content=arguments.get("content", ""),
                description=arguments.get("description", "")
            )

        elif tool_name == "edit_file":
            return self._edit_file(
                file_path=arguments.get("file_path", ""),
                old_text=arguments.get("old_text", ""),
                new_text=arguments.get("new_text", ""),
                description=arguments.get("description", "")
            )

        elif tool_name == "list_files":
            return self._list_files(
                pattern=arguments.get("pattern", "**/*"),
                directory=arguments.get("directory", "")
            )

        elif tool_name == "search_in_files":
            return self._search_in_files(
                search_text=arguments.get("search_text", ""),
                file_pattern=arguments.get("file_pattern", "**/*"),
                max_results=arguments.get("max_results", 20)
            )

        # Session 988: Fall through to BaseAgent for web_search + delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _generate_code(
        self,
        specification: str,
        language: str,
        framework: Optional[str] = None,
        include_tests: bool = False,
        include_docs: bool = True,
        target_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate code from a specification using GPT.

        Session 881: Added target_file parameter to persist generated code.
        """
        client = get_openai_client()

        framework_context = f" using {framework}" if framework else ""
        docs_instruction = "Include comprehensive docstrings and comments." if include_docs else "Keep comments minimal."
        test_instruction = "Also generate unit tests." if include_tests else ""

        prompt = f"""Generate {language} code{framework_context} for the following specification:

{specification}

Requirements:
- Write clean, production-ready code
- Follow {language} best practices and conventions
- Include proper error handling
- {docs_instruction}
{test_instruction}

Return the code in a properly formatted code block."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are an expert {language} developer. Generate clean, efficient, well-documented code."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        generated_code = response.choices[0].message.content

        # Session 881: Extract actual code from markdown code blocks
        code_match = re.search(r'```(?:\w+)?\n(.*?)\n```', generated_code, re.DOTALL)
        clean_code = code_match.group(1) if code_match else generated_code

        result = {
            "success": True,
            "language": language,
            "framework": framework,
            "code": generated_code,
            "specification": specification
        }

        # Session 881: If target_file specified, write the code to that file
        if target_file:
            write_result = self._write_file(
                file_path=target_file,
                content=clean_code,
                description=f"Generated {language} code: {specification[:100]}"
            )
            result['file_written'] = write_result.get('success', False)
            result['file_path'] = target_file
            if write_result.get('success'):
                logger.info(f"✅ Generated code written to {target_file}")
            else:
                result['write_error'] = write_result.get('error')

        return result

    def _create_project_structure(
        self,
        project_name: str,
        project_type: str,
        description: str,
        features: List[str],
        include_docker: bool,
        include_ci: bool
    ) -> Dict[str, Any]:
        """Create a project structure with all necessary files."""
        client = get_openai_client()

        prompt = f"""Create a complete project structure for:

Project Name: {project_name}
Type: {project_type}
Description: {description}
Features: {', '.join(features) if features else 'Basic setup'}
Include Docker: {include_docker}
Include CI/CD: {include_ci}

Generate:
1. Directory structure (show as tree)
2. Content for each essential file
3. README.md with setup instructions
4. Configuration files (package.json/requirements.txt/pyproject.toml as appropriate)
{f'5. Dockerfile and docker-compose.yml' if include_docker else ''}
{f'6. GitHub Actions workflow (.github/workflows/ci.yml)' if include_ci else ''}

Format each file as:
### filename.ext
```language
content
```"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert software architect. Create well-structured, production-ready project scaffolds."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=8000
        )

        project_structure = response.choices[0].message.content

        # Parse the structure into files
        files = self._parse_project_files(project_structure)

        # Session 881: Actually write the generated files to workspace
        files_written = 0
        write_errors = []
        for file_info in files:
            file_path = f"{project_name}/{file_info['filename']}"
            write_result = self._write_file(
                file_path=file_path,
                content=file_info['content'],
                description=f"Project scaffold: {project_name}"
            )
            if write_result.get('success'):
                files_written += 1
                logger.info(f"✅ Created {file_path}")
            else:
                write_errors.append({
                    'file': file_path,
                    'error': write_result.get('error')
                })

        return {
            "success": True,
            "project_name": project_name,
            "project_type": project_type,
            "description": description,
            "structure": project_structure,
            "files": files,
            "file_count": len(files),
            "files_written": files_written,
            "write_errors": write_errors if write_errors else None
        }

    def _parse_project_files(self, content: str) -> List[Dict[str, str]]:
        """Parse the generated project structure into individual files."""
        files = []

        # Pattern to match ### filename.ext followed by code block
        pattern = r'###\s+([^\n]+)\n```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)

        for filename, language, code in matches:
            files.append({
                "filename": filename.strip(),
                "language": language or "text",
                "content": code.strip()
            })

        return files

    def _analyze_code(
        self,
        code: str,
        analysis_type: str,
        language: str
    ) -> Dict[str, Any]:
        """Analyze code for various quality metrics."""
        client = get_openai_client()

        analysis_prompts = {
            "architecture": "Analyze the code architecture, design patterns used, and structural organization.",
            "security": "Identify potential security vulnerabilities, injection risks, and unsafe practices.",
            "performance": "Analyze performance characteristics, identify bottlenecks, and suggest optimizations.",
            "code-quality": "Evaluate code quality, readability, maintainability, and adherence to best practices.",
            "all": "Provide a comprehensive analysis covering architecture, security, performance, and code quality."
        }

        prompt = f"""Analyze the following {language} code:

```{language}
{code}
```

{analysis_prompts.get(analysis_type, analysis_prompts['all'])}

Provide:
1. Summary of findings
2. Specific issues identified (with line numbers if applicable)
3. Recommendations for improvement
4. Severity rating (critical/high/medium/low) for each issue"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a senior {language} code reviewer with expertise in security, performance, and best practices."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        analysis = response.choices[0].message.content

        return {
            "success": True,
            "analysis_type": analysis_type,
            "language": language,
            "analysis": analysis,
            "code_length": len(code),
            "line_count": code.count('\n') + 1
        }

    def _refactor_code(
        self,
        code: str,
        refactor_goals: List[str],
        language: str,
        preserve_api: bool
    ) -> Dict[str, Any]:
        """Refactor code based on specified goals."""
        client = get_openai_client()

        api_note = "IMPORTANT: Preserve the public API/interface - only internal implementation should change." if preserve_api else "You may change the API if it improves the design."

        prompt = f"""Refactor the following {language} code:

```{language}
{code}
```

Refactoring goals:
{chr(10).join(f'- {goal}' for goal in refactor_goals)}

{api_note}

Provide:
1. The refactored code
2. Explanation of changes made
3. Benefits of the refactoring
4. Any breaking changes (if API was modified)"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {language} refactoring expert. Improve code while maintaining correctness."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        refactored = response.choices[0].message.content

        return {
            "success": True,
            "goals": refactor_goals,
            "language": language,
            "preserved_api": preserve_api,
            "refactored_code": refactored,
            "original_lines": code.count('\n') + 1
        }

    def _generate_tests(
        self,
        code: str,
        test_framework: str,
        coverage_target: str,
        include_mocks: bool
    ) -> Dict[str, Any]:
        """Generate tests for the given code."""
        client = get_openai_client()

        coverage_instructions = {
            "basic": "Cover the main happy path scenarios.",
            "comprehensive": "Cover happy paths, error cases, and boundary conditions.",
            "edge-cases": "Focus on edge cases, error handling, and unusual inputs."
        }

        mock_instruction = "Use mocks/stubs for external dependencies." if include_mocks else "Use real implementations where possible."

        prompt = f"""Generate {test_framework} tests for the following code:

```
{code}
```

Requirements:
- Use {test_framework} testing framework
- {coverage_instructions.get(coverage_target, coverage_instructions['comprehensive'])}
- {mock_instruction}
- Include descriptive test names
- Add comments explaining what each test verifies

Generate complete, runnable test code."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a test engineering expert specializing in {test_framework}. Generate thorough, maintainable tests."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        tests = response.choices[0].message.content

        return {
            "success": True,
            "test_framework": test_framework,
            "coverage_target": coverage_target,
            "includes_mocks": include_mocks,
            "tests": tests
        }

    # ================================================================
    # SESSION 830: REAL FILE OPERATION IMPLEMENTATIONS
    # These methods actually interact with the filesystem via SKIN layer
    # ================================================================

    def _read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file from the workspace.

        Session 884: Prefers codebase workspace for reading actual source code.
        Falls back to active workspace if codebase workspace not available.
        """
        if not file_path:
            return {"success": False, "error": "file_path is required"}

        manager = self._get_workspace_manager()
        if not manager:
            return {"success": False, "error": "WorkspaceManager not available"}

        # Session 884: Prefer codebase workspace for reading source files
        workspace = manager.get_codebase_workspace()
        workspace_type = "codebase"

        # Fall back to active workspace if no codebase workspace
        if not workspace:
            workspace = manager.get_active_workspace()
            workspace_type = "active"

        if not workspace:
            return {
                "success": False,
                "error": "No workspace available. Run 'python manage.py setup_codebase_workspace' to enable codebase access."
            }

        content = manager.read_file(workspace, file_path)
        if content is None:
            # Session 884: If codebase workspace failed, try active workspace as fallback
            if workspace_type == "codebase":
                fallback_workspace = manager.get_active_workspace()
                if fallback_workspace and fallback_workspace.id != workspace.id:
                    content = manager.read_file(fallback_workspace, file_path)
                    if content is not None:
                        return {
                            "success": True,
                            "file_path": file_path,
                            "content": content,
                            "lines": len(content.split('\n')),
                            "size": len(content),
                            "workspace": fallback_workspace.name,
                            "workspace_type": "fallback"
                        }

            return {
                "success": False,
                "error": f"File not found or unreadable: {file_path}",
                "workspace": workspace.name,
                "workspace_path": workspace.root_path,
                "hint": "Ensure the file path is relative to the workspace root"
            }

        return {
            "success": True,
            "file_path": file_path,
            "content": content,
            "lines": len(content.split('\n')),
            "size": len(content),
            "workspace": workspace.name,
            "workspace_type": workspace_type
        }

    def _capture_code_artifact(self, kind: str, target_path: str, content: str,
                               content_before: str = '', description: str = ''):
        """Persist code output as a reviewable CodeArtifact when workspace write fails."""
        try:
            from core.models_code_artifacts import CodeArtifact
            artifact = CodeArtifact.objects.create(
                agent_name=self.name,
                trace_id=getattr(self, '_current_trace_id', ''),
                kind=kind,
                target_path=target_path,
                content=content,
                content_before=content_before,
                description=description,
            )
            logger.info(f"Captured CodeArtifact {artifact.id} for {target_path} ({kind})")
            return artifact
        except Exception as e:
            logger.error(f"Failed to capture CodeArtifact for {target_path}: {e}")
            return None

    def _write_file(
        self,
        file_path: str,
        content: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Write or create a file in the workspace.

        Session 884: Prefers codebase workspace for writing source files.
        Falls back to active workspace for generated content.
        """
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        if not content:
            return {"success": False, "error": "content is required"}

        manager = self._get_workspace_manager()
        if not manager:
            artifact = self._capture_code_artifact('file_create', file_path, content, description=description)
            result = {"success": False, "error": "WorkspaceManager not available"}
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        # Session 884: Prefer codebase workspace for source files
        workspace = manager.get_codebase_workspace()
        workspace_type = "codebase"

        # Fall back to active workspace if no codebase workspace or if it doesn't allow writes
        if not workspace or not workspace.allow_file_write:
            workspace = manager.get_active_workspace()
            workspace_type = "active"

        if not workspace:
            artifact = self._capture_code_artifact('file_create', file_path, content, description=description)
            result = {
                "success": False,
                "error": "No workspace available. Run 'python manage.py setup_codebase_workspace' to enable codebase access."
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        if not workspace.allow_file_write:
            artifact = self._capture_code_artifact('file_create', file_path, content, description=description)
            result = {
                "success": False,
                "error": "Workspace does not allow file writes",
                "workspace": workspace.name,
                "hint": "Run 'python manage.py setup_codebase_workspace' without --read-only to enable writes"
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        # Use WorkspaceManager to write with audit trail
        agent_task = description or f"Writing {file_path}"
        operation = manager.write_file(
            workspace=workspace,
            file_path=file_path,
            content=content,
            agent_name=self.name,
            agent_task=agent_task
        )

        if operation.success:
            logger.info(f"✅ {self.name} wrote {file_path} ({len(content)} bytes)")
            return {
                "success": True,
                "file_path": file_path,
                "operation_id": str(operation.id),
                "lines_written": len(content.split('\n')),
                "bytes_written": len(content),
                "workspace": workspace.name,
                "workspace_path": workspace.root_path,
                "can_rollback": operation.can_rollback
            }
        else:
            logger.error(f"❌ {self.name} failed to write {file_path}: {operation.error_message}")
            artifact = self._capture_code_artifact('file_create', file_path, content, description=description)
            result = {
                "success": False,
                "error": operation.error_message,
                "file_path": file_path,
                "workspace": workspace.name
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

    def _edit_file(
        self,
        file_path: str,
        old_text: str,
        new_text: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Make a targeted edit to a file by replacing specific text.

        Session 884: Prefers codebase workspace for editing source files.
        """
        if not file_path:
            return {"success": False, "error": "file_path is required"}
        if not old_text:
            return {"success": False, "error": "old_text is required"}

        manager = self._get_workspace_manager()
        if not manager:
            artifact = self._capture_code_artifact('file_edit', file_path, new_text, content_before=old_text, description=description)
            result = {"success": False, "error": "WorkspaceManager not available"}
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        # Session 884: Prefer codebase workspace for source files
        workspace = manager.get_codebase_workspace()
        workspace_type = "codebase"

        # Fall back to active workspace if no codebase workspace or if it doesn't allow writes
        if not workspace or not workspace.allow_file_write:
            workspace = manager.get_active_workspace()
            workspace_type = "active"

        if not workspace:
            artifact = self._capture_code_artifact('file_edit', file_path, new_text, content_before=old_text, description=description)
            result = {
                "success": False,
                "error": "No workspace available. Run 'python manage.py setup_codebase_workspace' to enable codebase access."
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        if not workspace.allow_file_write:
            artifact = self._capture_code_artifact('file_edit', file_path, new_text, content_before=old_text, description=description)
            result = {
                "success": False,
                "error": "Workspace does not allow file writes",
                "workspace": workspace.name,
                "hint": "Run 'python manage.py setup_codebase_workspace' without --read-only to enable writes"
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

        # Read current content
        current_content = manager.read_file(workspace, file_path)
        if current_content is None:
            # Logic error, NOT workspace availability — don't capture artifact
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "workspace": workspace.name
            }

        # Check if old_text exists in the file
        if old_text not in current_content:
            # Logic error, NOT workspace availability — don't capture artifact
            return {
                "success": False,
                "error": "old_text not found in file. The text must match exactly.",
                "file_path": file_path,
                "file_lines": len(current_content.split('\n')),
                "hint": "Use read_file first to see the exact content"
            }

        # Perform the replacement
        new_content = current_content.replace(old_text, new_text, 1)  # Replace only first occurrence

        # Write the modified content
        agent_task = description or f"Editing {file_path}"
        operation = manager.write_file(
            workspace=workspace,
            file_path=file_path,
            content=new_content,
            agent_name=self.name,
            agent_task=agent_task
        )

        if operation.success:
            lines_changed = abs(len(new_text.split('\n')) - len(old_text.split('\n')))
            logger.info(f"✅ {self.name} edited {file_path}")
            return {
                "success": True,
                "file_path": file_path,
                "operation_id": str(operation.id),
                "old_text_length": len(old_text),
                "new_text_length": len(new_text),
                "lines_changed": lines_changed,
                "workspace": workspace.name,
                "can_rollback": operation.can_rollback
            }
        else:
            artifact = self._capture_code_artifact('file_edit', file_path, new_text, content_before=old_text, description=description)
            result = {
                "success": False,
                "error": operation.error_message,
                "file_path": file_path
            }
            if artifact:
                result["artifact_id"] = str(artifact.id)
                result["artifact_captured"] = True
            return result

    def _list_files(
        self,
        pattern: str = "**/*",
        directory: str = ""
    ) -> Dict[str, Any]:
        """List files in the workspace matching a pattern."""
        manager = self._get_workspace_manager()
        if not manager:
            return {"success": False, "error": "WorkspaceManager not available"}

        workspace = manager.get_codebase_workspace()
        if not workspace:
            workspace = manager.get_active_workspace()
        if not workspace:
            return {
                "success": False,
                "error": "No active workspace. Register a workspace first."
            }

        # Construct the full pattern
        if directory:
            full_pattern = f"{directory.rstrip('/')}/{pattern}"
        else:
            full_pattern = pattern

        try:
            files = manager.list_files(workspace, full_pattern)
            return {
                "success": True,
                "pattern": full_pattern,
                "files": files[:100],  # Limit to 100 files
                "count": len(files),
                "workspace": workspace.name,
                "truncated": len(files) > 100
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pattern": full_pattern
            }

    def _search_in_files(
        self,
        search_text: str,
        file_pattern: str = "**/*",
        max_results: int = 20
    ) -> Dict[str, Any]:
        """Search for text across files in the workspace."""
        import re
        from pathlib import Path

        if not search_text:
            return {"success": False, "error": "search_text is required"}

        manager = self._get_workspace_manager()
        if not manager:
            return {"success": False, "error": "WorkspaceManager not available"}

        workspace = manager.get_codebase_workspace()
        if not workspace:
            workspace = manager.get_active_workspace()
        if not workspace:
            return {
                "success": False,
                "error": "No active workspace. Register a workspace first."
            }

        results = []
        root = Path(workspace.root_path)

        # Skip common directories
        skip_dirs = {'node_modules', '__pycache__', '.git', 'venv', '.venv', 'dist', 'build'}

        try:
            for file_path in root.glob(file_pattern):
                if any(skip in file_path.parts for skip in skip_dirs):
                    continue

                if not file_path.is_file():
                    continue

                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if search_text in content:
                        rel_path = str(file_path.relative_to(root))
                        lines = content.split('\n')

                        # Find matching lines
                        matches = []
                        for i, line in enumerate(lines, 1):
                            if search_text in line:
                                matches.append({
                                    'line_number': i,
                                    'content': line.strip()[:200]  # Truncate long lines
                                })
                                if len(matches) >= 5:  # Max 5 matches per file
                                    break

                        results.append({
                            'file': rel_path,
                            'matches': matches,
                            'match_count': len([1 for l in lines if search_text in l])
                        })

                        if len(results) >= max_results:
                            break

                except Exception:
                    continue

            return {
                "success": True,
                "search_text": search_text,
                "pattern": file_pattern,
                "results": results,
                "total_files_with_matches": len(results),
                "workspace": workspace.name,
                "truncated": len(results) >= max_results
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
