"""
CodeGeneratorAgent - Generates code, creates files, and builds projects.

This agent can:
- Generate code from specifications
- Create file structures for projects
- Analyze existing codebases
- Refactor and improve code
- Generate tests for code
"""

import re
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult


class CodeGeneratorAgent(BaseAgent):
    """Agent specialized in generating code and building projects."""

    name = "CodeGeneratorAgent"

    system_prompt = """You are CodeGeneratorAgent, an expert software developer and code generator.

IMPORTANT - Response Guidelines:
- Be CONCISE. Provide working code, not essays about code.
- For simple requests: Generate the code directly with minimal explanation.
- Only explain complex architectural decisions, not obvious patterns.
- Keep comments in code minimal and meaningful.

Your capabilities:
1. Generate clean, production-ready code from specifications
2. Create complete file structures for new projects
3. Follow best practices for the target language/framework

When generating code:
- Write clean, well-documented code
- Follow language-specific conventions
- Include error handling
- Consider security implications

You have access to tools for:
- generate_code: Generate code from specifications
- create_project_structure: Create a complete project with files
- analyze_code: Analyze existing code for patterns/issues
- refactor_code: Improve existing code
- generate_tests: Create tests for code

Provide the code first, then a brief usage example if needed."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_code",
                "description": "Generate code from a specification or description. Use this for creating functions, classes, modules, or code snippets.",
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
        }
    ]

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute a code generation task."""
        import time

        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        with self.time_travel_session("code_generation", task, input_data=context):
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
                            reasoning=f"Selected {tool_name} for code generation",
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
                        # Format the code output nicely
                        code_output = tool_result.get('code', tool_result.get('refactored_code', ''))

                        result = AgentResult(
                            success=True,
                            message=f"Code generation completed using {len(all_results)} tool(s)",
                            data={
                                'results': all_results,
                                'query': task
                            },
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

                        return result

                # No tool calls - return GPT content directly
                content = gpt_response.get('content', 'I can help with code generation. Please provide more details.')
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
                error_msg = f"Code generation failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "generate_code":
            return self._generate_code(
                specification=arguments.get("specification", ""),
                language=arguments.get("language", "python"),
                framework=arguments.get("framework"),
                include_tests=arguments.get("include_tests", False),
                include_docs=arguments.get("include_docs", True)
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

        return {"error": f"Unknown tool: {tool_name}"}

    def _generate_code(
        self,
        specification: str,
        language: str,
        framework: Optional[str] = None,
        include_tests: bool = False,
        include_docs: bool = True
    ) -> Dict[str, Any]:
        """Generate code from a specification using GPT."""
        from openai import OpenAI

        client = OpenAI()

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

        return {
            "success": True,
            "language": language,
            "framework": framework,
            "code": generated_code,
            "specification": specification
        }

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
        from openai import OpenAI

        client = OpenAI()

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

        return {
            "success": True,
            "project_name": project_name,
            "project_type": project_type,
            "description": description,
            "structure": project_structure,
            "files": files,
            "file_count": len(files)
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
        from openai import OpenAI

        client = OpenAI()

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
        from openai import OpenAI

        client = OpenAI()

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
        from openai import OpenAI

        client = OpenAI()

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
