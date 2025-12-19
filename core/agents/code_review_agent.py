"""
CodeReviewAgent - Reviews code for quality, security, and best practices.

This agent can:
- Review code for bugs and issues
- Check security vulnerabilities
- Analyze code complexity
- Suggest improvements
- Enforce coding standards
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_agent import BaseAgent, AgentResult


class CodeReviewAgent(BaseAgent):
    """Agent specialized in code review and quality analysis."""

    name = "CodeReviewAgent"

    system_prompt = """You are CodeReviewAgent, a senior code reviewer with expertise in multiple languages and frameworks.

IMPORTANT - Response Guidelines:
- Be CONCISE. Focus on actionable issues, not exhaustive lists.
- Prioritize: List critical issues first, skip minor style nits unless asked.
- Format as a brief list of issues with one-line fixes.
- If code is good, say so briefly - don't pad the review.

Your review capabilities:
1. Bug Detection - Logical errors, edge cases
2. Security Analysis - OWASP Top 10, injection, XSS
3. Performance Review - Inefficiencies, N+1 queries
4. Code Quality - Readability, maintainability

Review approach:
- Prioritize by severity (critical > high > medium > low)
- Provide specific line references
- Suggest concrete fixes, not just problems

You have access to tools for:
- comprehensive_review: Full code review
- security_audit: Security-focused analysis
- performance_review: Performance analysis
- style_check: Style and convention analysis
- suggest_improvements: Generate improved code

Be constructive and brief."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "comprehensive_review",
                "description": "Perform a comprehensive code review covering bugs, security, performance, and style.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to review"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "context": {
                            "type": "string",
                            "description": "Context about the code (what it does, where it's used)"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific areas to focus on (optional)"
                        },
                        "severity_threshold": {
                            "type": "string",
                            "description": "Minimum severity to report",
                            "enum": ["all", "low", "medium", "high", "critical"],
                            "default": "all"
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "security_audit",
                "description": "Perform a security-focused code audit identifying vulnerabilities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to audit"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "framework": {
                            "type": "string",
                            "description": "Framework being used (django, express, react, etc.)"
                        },
                        "check_categories": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Security categories to check (injection, auth, crypto, etc.)"
                        },
                        "compliance_standards": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Standards to check against (OWASP, PCI-DSS, HIPAA)"
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "performance_review",
                "description": "Analyze code for performance issues and optimization opportunities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "runtime_context": {
                            "type": "string",
                            "description": "Where/how the code runs (web server, background job, etc.)"
                        },
                        "expected_scale": {
                            "type": "string",
                            "description": "Expected data/traffic scale (small, medium, large, massive)"
                        },
                        "check_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Types of performance issues to check (complexity, memory, io, queries)"
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "style_check",
                "description": "Check code against style guidelines and conventions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to check"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "style_guide": {
                            "type": "string",
                            "description": "Style guide to follow",
                            "enum": ["pep8", "google", "airbnb", "standard", "prettier", "black", "default"]
                        },
                        "check_naming": {
                            "type": "boolean",
                            "description": "Check variable/function naming conventions",
                            "default": True
                        },
                        "check_documentation": {
                            "type": "boolean",
                            "description": "Check documentation completeness",
                            "default": True
                        }
                    },
                    "required": ["code", "language"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "suggest_improvements",
                "description": "Generate an improved version of the code with explanations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to improve"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language"
                        },
                        "improvement_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Goals for improvement (readability, performance, security, testability)"
                        },
                        "preserve_functionality": {
                            "type": "boolean",
                            "description": "Must preserve exact functionality",
                            "default": True
                        },
                        "explain_changes": {
                            "type": "boolean",
                            "description": "Include detailed explanations of changes",
                            "default": True
                        }
                    },
                    "required": ["code", "language", "improvement_goals"]
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
        """Execute a code review task."""
        import time

        start_time = time.time()
        tool_calls_made = []

        with self.time_travel_session("code_review", task, input_data=context):
            try:
                # Build prompt with attribution
                full_prompt, knowledge_attribution = self._build_prompt_with_attribution(
                    task, scifi_context, spider_context
                )

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
                            reasoning=f"Selected {tool_name} for code review",
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
                        result = AgentResult(
                            success=True,
                            message=f"Code review completed using {len(all_results)} tool(s)",
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
                content = gpt_response.get('content', 'I can help review code. Please provide the code you\'d like me to review.')
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
                error_msg = f"Code review failed: {str(e)}"
                return AgentResult(
                    success=False,
                    error=error_msg,
                    agent_name=self.name
                )

    def _execute_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool call."""

        if tool_name == "comprehensive_review":
            return self._comprehensive_review(**arguments)
        elif tool_name == "security_audit":
            return self._security_audit(**arguments)
        elif tool_name == "performance_review":
            return self._performance_review(**arguments)
        elif tool_name == "style_check":
            return self._style_check(**arguments)
        elif tool_name == "suggest_improvements":
            return self._suggest_improvements(**arguments)

        return {"error": f"Unknown tool: {tool_name}"}

    def _comprehensive_review(
        self,
        code: str,
        language: str,
        context: str = "",
        focus_areas: List[str] = None,
        severity_threshold: str = "all"
    ) -> Dict[str, Any]:
        """Perform comprehensive code review."""
        from openai import OpenAI

        client = OpenAI()

        focus_text = f"Focus especially on: {', '.join(focus_areas)}" if focus_areas else ""
        context_text = f"Context: {context}" if context else ""

        prompt = f"""Perform a comprehensive code review:

```{language}
{code}
```

{context_text}
{focus_text}
Minimum severity to report: {severity_threshold}

Review the following aspects:

1. **BUGS & LOGIC ERRORS**
   - Off-by-one errors, null checks, edge cases
   - Incorrect logic or conditions

2. **SECURITY ISSUES**
   - Input validation, injection vulnerabilities
   - Authentication/authorization issues
   - Data exposure risks

3. **PERFORMANCE**
   - Algorithmic complexity
   - Resource usage (memory, connections)
   - Inefficient patterns

4. **CODE QUALITY**
   - Readability and maintainability
   - SOLID principles adherence
   - Error handling

5. **TESTING GAPS**
   - What tests are needed
   - Edge cases to cover

For each issue found:
- Severity: critical/high/medium/low
- Location: line number(s) if possible
- Problem: clear description
- Fix: specific suggestion

End with a summary score (1-10) and overall assessment."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a thorough, constructive code reviewer. Be specific and actionable."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "language": language,
            "review_type": "comprehensive",
            "lines_reviewed": code.count('\n') + 1,
            "review": response.choices[0].message.content
        }

    def _security_audit(
        self,
        code: str,
        language: str,
        framework: str = None,
        check_categories: List[str] = None,
        compliance_standards: List[str] = None
    ) -> Dict[str, Any]:
        """Perform security audit."""
        from openai import OpenAI

        client = OpenAI()

        framework_text = f"Framework: {framework}" if framework else ""
        categories = check_categories or ["injection", "auth", "crypto", "data-exposure", "misconfiguration"]
        standards = compliance_standards or ["OWASP Top 10"]

        prompt = f"""Perform a security audit on this {language} code:

```{language}
{code}
```

{framework_text}

Check for these vulnerability categories:
{chr(10).join(f'- {cat}' for cat in categories)}

Compliance standards to consider:
{chr(10).join(f'- {std}' for std in standards)}

For each vulnerability found:
1. **Category**: Type of vulnerability
2. **Severity**: Critical/High/Medium/Low
3. **CVSS Score**: Estimated if applicable
4. **Location**: Where in code
5. **Description**: What the issue is
6. **Attack Vector**: How it could be exploited
7. **Remediation**: Specific fix with code example

Also provide:
- Overall security score (1-10)
- Priority remediation order
- Quick wins vs long-term fixes"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a security expert. Identify vulnerabilities thoroughly and provide actionable fixes."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000
        )

        return {
            "success": True,
            "language": language,
            "framework": framework,
            "audit_type": "security",
            "categories_checked": categories,
            "audit": response.choices[0].message.content
        }

    def _performance_review(
        self,
        code: str,
        language: str,
        runtime_context: str = None,
        expected_scale: str = "medium",
        check_types: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze performance issues."""
        from openai import OpenAI

        client = OpenAI()

        context_text = f"Runtime context: {runtime_context}" if runtime_context else ""
        checks = check_types or ["complexity", "memory", "io", "queries", "caching"]

        prompt = f"""Analyze performance of this {language} code:

```{language}
{code}
```

{context_text}
Expected scale: {expected_scale}

Check for these performance aspects:
{chr(10).join(f'- {check}' for check in checks)}

Analyze:
1. **Time Complexity**
   - Big-O analysis of key operations
   - Bottleneck identification

2. **Space Complexity**
   - Memory usage patterns
   - Potential memory leaks

3. **I/O Operations**
   - Database queries (N+1 problems)
   - File/network operations
   - Unnecessary I/O

4. **Caching Opportunities**
   - What can be cached
   - Cache invalidation needs

5. **Algorithmic Improvements**
   - Better data structures
   - More efficient algorithms

For each issue:
- Impact: How much it affects performance
- Scale sensitivity: When it becomes a problem
- Fix: Optimized code example

Provide overall performance score and optimization priority list."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are a performance optimization expert. Identify inefficiencies and provide optimized solutions."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=5000
        )

        return {
            "success": True,
            "language": language,
            "review_type": "performance",
            "expected_scale": expected_scale,
            "review": response.choices[0].message.content
        }

    def _style_check(
        self,
        code: str,
        language: str,
        style_guide: str = "default",
        check_naming: bool = True,
        check_documentation: bool = True
    ) -> Dict[str, Any]:
        """Check code style and conventions."""
        from openai import OpenAI

        client = OpenAI()

        naming_text = "Check naming conventions for variables, functions, and classes." if check_naming else ""
        docs_text = "Check documentation completeness (docstrings, comments, type hints)." if check_documentation else ""

        prompt = f"""Check this {language} code against {style_guide} style guide:

```{language}
{code}
```

{naming_text}
{docs_text}

Evaluate:
1. **Formatting**
   - Indentation consistency
   - Line length
   - Whitespace usage

2. **Naming Conventions**
   - Variable names (descriptive, appropriate case)
   - Function names (verb-based, clear purpose)
   - Class names (noun-based, PascalCase)
   - Constants (SCREAMING_SNAKE_CASE)

3. **Documentation**
   - Function docstrings
   - Class docstrings
   - Inline comments (where needed)
   - Type hints/annotations

4. **Code Organization**
   - Import ordering
   - Function/class ordering
   - File structure

5. **Best Practices**
   - {language}-specific idioms
   - Anti-patterns to avoid

List each violation with:
- Line number
- Issue description
- Suggested fix

End with style compliance percentage."""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {language} style expert familiar with {style_guide} conventions."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=4000
        )

        return {
            "success": True,
            "language": language,
            "style_guide": style_guide,
            "review_type": "style",
            "review": response.choices[0].message.content
        }

    def _suggest_improvements(
        self,
        code: str,
        language: str,
        improvement_goals: List[str],
        preserve_functionality: bool = True,
        explain_changes: bool = True
    ) -> Dict[str, Any]:
        """Generate improved version of code."""
        from openai import OpenAI

        client = OpenAI()

        preserve_text = "IMPORTANT: Preserve exact functionality - no behavioral changes." if preserve_functionality else "You may change functionality if it improves the design."
        explain_text = "Explain each change made and why." if explain_changes else ""

        prompt = f"""Improve this {language} code:

```{language}
{code}
```

Improvement goals:
{chr(10).join(f'- {goal}' for goal in improvement_goals)}

{preserve_text}
{explain_text}

Provide:
1. **IMPROVED CODE**
   Complete improved version

2. **CHANGES MADE** (for each change)
   - What was changed
   - Why it's better
   - Before/after comparison

3. **IMPROVEMENT SUMMARY**
   - Overall improvements achieved
   - Trade-offs (if any)
   - Further improvements possible"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": f"You are a {language} refactoring expert. Improve code while maintaining correctness."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000
        )

        return {
            "success": True,
            "language": language,
            "goals": improvement_goals,
            "preserved_functionality": preserve_functionality,
            "improved_code": response.choices[0].message.content
        }
