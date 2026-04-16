"""
Platform Audit Agent - Internal Platform Inspection & Auditing
==============================================================

Session 857: Created to fill the gap where ResearchAgent failed.
ResearchAgent only has external research tools (web_search, spider_query).
This agent can perform INTERNAL platform audits:
- Read documentation files (CLAUDE.md, SPIDERS.md, AGENTS.md)
- Query database model counts
- Check environment variable configuration (masked)
- Inventory integrations and their status
- Generate audit reports in JSON format

This agent does NOT:
- Modify any files or settings
- Execute arbitrary code
- Access actual secret values (only checks if configured)
"""

import json
import logging
import os
import time
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig, OutputCategory, strip_simulated_tool_json
from ml.auto_selection import TaskType
from core.services.openai_client_factory import get_openai_client  # Session 1084 round 51

logger = logging.getLogger(__name__)


def analyze_audit_with_ml(audit_data: dict) -> dict:
    """Analyze audit data using ML models (ANOMALY for detecting issues)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()
        result = router.auto_route(
            data=audit_data,
            task_hint=TaskType.ANOMALY,
            max_models=2
        )
        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
        }
    except Exception as e:
        logger.warning(f"ML audit analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class PlatformAuditAgent(BaseAgent):
    """
    Agent specialized in internal platform auditing and inspection.

    This agent can:
    1. Read and analyze platform documentation
    2. Inventory integrations and check their status
    3. Query database model counts
    4. Check environment variable configuration
    5. Generate structured audit reports

    Routes here via AgentRouter when user asks about:
    - Integration inventory, API key status
    - Platform configuration audit
    - Database model counts
    - Documentation inspection
    """

    name = "PlatformAuditAgent"
    requires_system_context = True  # Inject CLAUDE.md + critical docs

    # Session 857: Content review configuration
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='review',
        default_urgency='medium',
        actions=['acknowledge', 'create_ticket', 'dismiss'],
        payload_fields=['audit_type', 'findings_count', 'issues_found']
    )

    system_prompt = """You are PlatformAuditAgent, the platform's internal auditing expert.

Your job is to inspect and audit internal platform components, configurations, and integrations.
You do NOT perform external web research - use ResearchAgent for that.

You have access to these tools:
- read_documentation: Read platform docs (CLAUDE.md, SPIDERS.md, AGENTS.md, etc.)
- inventory_integrations: List all integrations with their status
- check_env_config: Check which environment variables are configured (values masked)
- count_database_models: Count records in key database models
- generate_audit_report: Generate a structured JSON audit report

When responding to audit requests:

1. **For integration inventory** ("list all integrations", "API key status"):
   - Use inventory_integrations to get full list
   - Report which have keys configured vs missing
   - Group by category (LLM, media, spider, etc.)

2. **For configuration audits** ("check environment", "what's configured"):
   - Use check_env_config to see what's set
   - Report missing critical variables
   - Note any potential issues

3. **For documentation queries** ("what does SPIDERS.md say", "check docs"):
   - Use read_documentation to access the file
   - Summarize relevant sections
   - Answer specific questions

4. **For database audits** ("how many agents", "database stats"):
   - Use count_database_models to get counts
   - Report key metrics
   - Identify anomalies

Always produce output as structured JSON when generating reports.
Include counts, categorizations, and actionable findings."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "read_documentation",
                "description": "Read a platform documentation file. Available: CLAUDE.md, SPIDERS.md, AGENTS.md, SERVICES.md, ARCHITECTURE.md, CAPABILITIES.md",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_name": {
                            "type": "string",
                            "description": "Document name to read",
                            "enum": ["CLAUDE.md", "SPIDERS.md", "AGENTS.md", "SERVICES.md", "ARCHITECTURE.md", "CAPABILITIES.md", "00-START-NEXT-SESSION.md"]
                        },
                        "section": {
                            "type": "string",
                            "description": "Optional: specific section to extract (e.g., 'Spider Categories', 'Quick Stats')"
                        }
                    },
                    "required": ["doc_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "inventory_integrations",
                "description": "Get inventory of all platform integrations with their configuration status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category",
                            "enum": ["all", "llm", "media", "spider", "payment", "infrastructure"]
                        },
                        "status_filter": {
                            "type": "string",
                            "description": "Filter by status",
                            "enum": ["all", "configured", "missing", "error"]
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_env_config",
                "description": "Check which environment variables are configured (values are masked for security)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category of env vars to check",
                            "enum": ["all", "api_keys", "database", "redis", "feature_flags"]
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "count_database_models",
                "description": "Count records in key database models",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "models": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of model names to count. Options: Agent, AgentExecution, AgentMemory, SpiderData, Conversation, User, ImageHistory, VideoHistory"
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_audit_report",
                "description": "Generate a comprehensive audit report in JSON format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "audit_type": {
                            "type": "string",
                            "description": "Type of audit to perform",
                            "enum": ["integrations", "configuration", "database", "comprehensive"]
                        },
                        "include_recommendations": {
                            "type": "boolean",
                            "description": "Include actionable recommendations",
                            "default": True
                        }
                    },
                    "required": ["audit_type"]
                }
            }
        }
    ]

    def __init__(self, user=None, health_check_mode: bool = False):
        super().__init__(user=user, health_check_mode=health_check_mode)

    def execute(
        self,
        task: str,
        context: Dict[str, Any] = None,
        scifi_context: Dict[str, Any] = None,
        spider_context: Dict[str, Any] = None
    ) -> AgentResult:
        """Execute platform audit task."""
        start_time = time.time()
        context = context or {}

        logger.info(f"🔍 PlatformAuditAgent executing: {task[:100]}...")

        try:
            # Call OpenAI with tools
            result = self._call_openai_with_tools(task, context)

            execution_time = int((time.time() - start_time) * 1000)

            # Session 1006: Persist output to Deliverable
            self._save_to_deliverable(
                title=f"Platform Audit: {task[:80]}",
                content=result.get('message', 'Audit completed'),
                deliverable_type='analysis',
                category='Platform Audit',
                tags=['audit', 'platform'],
                metadata={'task': task[:200]},
            )

            return AgentResult(
                success=True,
                message=result.get('message', 'Audit completed'),
                data=result.get('data', {}),
                agent_name=self.name,
                execution_time_ms=execution_time,
                decisions_made=self._tt_decision_count,
                tool_calls=result.get('tool_calls', []),
                quality_tier='gold' if result.get('data') else 'silver',
                output_category=OutputCategory.ANALYSIS.value,
                confidence=0.9
            )

        except Exception as e:
            logger.error(f"PlatformAuditAgent error: {e}", exc_info=True)
            execution_time = int((time.time() - start_time) * 1000)
            return AgentResult(
                success=False,
                message=f"Audit failed: {str(e)}",
                error=str(e),
                agent_name=self.name,
                execution_time_ms=execution_time,
                quality_tier='bronze',
                output_category=OutputCategory.ANALYSIS.value
            )

    def _call_openai_with_tools(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Call OpenAI and handle tool calls."""
        # Session 1084 round 51: custom 120s timeout dropped — factory enforces 90s read centrally
        client = get_openai_client(api_key=os.getenv('OPENAI_API_KEY'))

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task}
        ]

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            tools=self.get_tools_with_delegation(),
            tool_choice="auto",
            max_completion_tokens=4000,
        )

        assistant_message = response.choices[0].message
        tool_calls_made = []

        # Handle tool calls
        if assistant_message.tool_calls:
            messages.append(assistant_message)

            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                logger.info(f"   Tool call: {function_name}({arguments})")

                # Execute the tool
                tool_result = self._execute_tool(function_name, arguments)
                tool_calls_made.append({
                    'tool': function_name,
                    'arguments': arguments,
                    'result_preview': str(tool_result)[:200],
                    'result_full': tool_result,  # Session 1090: kept for fallback formatter
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, default=str)
                })

            # Session 1090: Tell GPT to synthesize tool results into prose,
            # not echo raw JSON.  Without this instruction, gpt-5-mini
            # returns the tool call arguments verbatim.
            messages.append({
                "role": "user",
                "content": (
                    "Now synthesize all the tool results above into a clear, "
                    "readable audit report in markdown. Use sections with headers. "
                    "Do NOT output raw JSON — write prose with bullet points. "
                    "Include: Executive Summary, Integration Health, Configuration "
                    "Status, Database Health, Top Risks, and Green Checks."
                ),
            })

            # Get final response after tool calls
            final_response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                max_completion_tokens=4000,
            )

            # Session 1090: gpt-5-mini (reasoning model) may put the
            # synthesis in .output_text or nested content rather than
            # .choices[0].message.content.  Try multiple paths.
            final_msg = final_response.choices[0].message
            synthesis = final_msg.content or ''
            if not synthesis and hasattr(final_response, 'output_text'):
                synthesis = final_response.output_text or ''
            if not synthesis:
                # Fallback: format tool results as markdown ourselves
                synthesis = self._format_tool_results_as_markdown(tool_calls_made)
                logger.warning("PlatformAuditAgent: GPT returned empty synthesis, using fallback formatter")

            return {
                'message': synthesis,
                'data': {'tool_results': tool_calls_made},
                'tool_calls': tool_calls_made
            }

        return {
            'message': strip_simulated_tool_json(assistant_message.content),
            'data': {},
            'tool_calls': []
        }

    def _format_tool_results_as_markdown(self, tool_calls: list) -> str:
        """Fallback: format raw tool results into readable markdown.

        Session 1090: gpt-5-mini consistently returns empty synthesis,
        so this formatter produces the deliverable content directly.
        """
        parts = ["# Platform Audit Report\n"]

        for tc in tool_calls:
            tool = tc.get('tool', 'unknown')
            data = tc.get('result_full', {})
            if not isinstance(data, dict):
                continue

            if tool == 'inventory_integrations':
                total = data.get('total', 0)
                configured = data.get('configured', 0)
                missing = data.get('missing', 0)
                parts.append(f"## Integration Health\n")
                parts.append(f"- **{configured}/{total}** integrations configured, **{missing}** missing\n")
                for intg in data.get('integrations', []):
                    status = 'configured' if intg.get('configured') else 'MISSING'
                    parts.append(f"- {intg.get('name', '?')} ({intg.get('category', '?')}): **{status}**")
                parts.append("")

            elif tool == 'check_env_config':
                parts.append("## Environment Configuration\n")
                for category, keys in data.items():
                    if isinstance(keys, dict):
                        for key, info in keys.items():
                            if isinstance(info, dict):
                                status = 'Set' if info.get('configured') else 'MISSING'
                                parts.append(f"- `{key}`: **{status}**")
                            else:
                                parts.append(f"- {key}: {str(info)[:80]}")
                parts.append("")

            elif tool == 'count_database_models':
                parts.append("## Database Health\n")
                for model, info in data.items():
                    if isinstance(info, dict):
                        if 'count' in info:
                            parts.append(f"- **{model}**: {info['count']:,} records")
                        elif 'error' in info:
                            parts.append(f"- **{model}**: error — {info['error'][:60]}")
                parts.append("")

            elif tool == 'generate_audit_report':
                report = data.get('report', data)
                if isinstance(report, dict):
                    summary = report.get('summary', '')
                    if summary:
                        parts.append(f"## Executive Summary\n{summary}\n")
                    risks = report.get('risks', report.get('top_risks', []))
                    if risks:
                        parts.append("## Top Risks")
                        for r in (risks[:5] if isinstance(risks, list) else []):
                            parts.append(f"- {r}")
                        parts.append("")
                    green = report.get('green_checks', report.get('strengths', []))
                    if green:
                        parts.append("## Green Checks")
                        for g in (green[:5] if isinstance(green, list) else []):
                            parts.append(f"- {g}")
                        parts.append("")

        return '\n'.join(parts)

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return its result."""
        if tool_name == "read_documentation":
            return self._read_documentation(arguments.get('doc_name'), arguments.get('section'))
        elif tool_name == "inventory_integrations":
            return self._inventory_integrations(arguments.get('category', 'all'), arguments.get('status_filter', 'all'))
        elif tool_name == "check_env_config":
            return self._check_env_config(arguments.get('category', 'all'))
        elif tool_name == "count_database_models":
            return self._count_database_models(arguments.get('models', []))
        elif tool_name == "generate_audit_report":
            return self._generate_audit_report(arguments.get('audit_type'), arguments.get('include_recommendations', True))
        else:
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, arguments)

    def _read_documentation(self, doc_name: str, section: str = None) -> Dict[str, Any]:
        """Read a documentation file."""
        import os

        # Map doc names to paths
        doc_paths = {
            'CLAUDE.md': 'CLAUDE.md',
            '00-START-NEXT-SESSION.md': '00-START-NEXT-SESSION.md',
            'SPIDERS.md': 'docs/SPIDERS.md',
            'AGENTS.md': 'docs/AGENTS.md',
            'SERVICES.md': 'docs/SERVICES.md',
            'ARCHITECTURE.md': 'docs/ARCHITECTURE.md',
            'CAPABILITIES.md': 'docs/CAPABILITIES.md',
        }

        if doc_name not in doc_paths:
            return {"error": f"Unknown document: {doc_name}"}

        try:
            from django.conf import settings
            base_path = settings.BASE_DIR
            file_path = os.path.join(base_path, doc_paths[doc_name])

            with open(file_path, 'r') as f:
                content = f.read()

            # If section specified, try to extract it
            if section:
                lines = content.split('\n')
                in_section = False
                section_content = []

                for line in lines:
                    if section.lower() in line.lower() and line.startswith('#'):
                        in_section = True
                        section_content.append(line)
                    elif in_section:
                        if line.startswith('#') and section.lower() not in line.lower():
                            break
                        section_content.append(line)

                if section_content:
                    content = '\n'.join(section_content)

            # Truncate if too long
            if len(content) > 10000:
                content = content[:10000] + "\n\n... (truncated, document continues)"

            return {
                "document": doc_name,
                "section": section,
                "content": content,
                "length": len(content)
            }
        except Exception as e:
            return {"error": str(e)}

    def _inventory_integrations(self, category: str = 'all', status_filter: str = 'all') -> Dict[str, Any]:
        """Get inventory of platform integrations."""
        integrations = []

        # LLM Providers
        llm_providers = [
            ('OpenAI', 'OPENAI_API_KEY', 'llm'),
            ('Anthropic', 'ANTHROPIC_API_KEY', 'llm'),
            ('Together AI', 'TOGETHER_AI_API_KEY', 'llm'),
            ('Google Gemini', 'GEMINI_API_KEY', 'llm'),
            ('DeepSeek', 'DEEPSEEK_API_KEY', 'llm'),
            ('Groq', 'GROQ_API_KEY', 'llm'),
        ]

        # Media Generation
        media_providers = [
            ('Stability AI', 'STABILITY_API_KEY', 'media'),
            ('Runway ML', 'RUNWAY_API_KEY', 'media'),
            ('ElevenLabs', 'ELEVENLABS_API_KEY', 'media'),
            ('Replicate', 'REPLICATE_API_KEY', 'media'),
        ]

        # Infrastructure
        infra = [
            ('PostgreSQL', 'DATABASE_URL', 'infrastructure'),
            ('Redis', 'REDIS_URL', 'infrastructure'),
        ]

        # Payment & Search
        other = [
            ('Stripe', 'STRIPE_SECRET_KEY', 'payment'),
            ('Serper', 'SERPER_API_KEY', 'spider'),
            ('NewsAPI', 'NEWS_API_KEY', 'spider'),
            ('Polygon.io', 'POLYGON_API_KEY', 'spider'),
            ('Etherscan', 'ETHERSCAN_API_KEY', 'spider'),
            ('The Odds API', 'THEODDS_API_KEY', 'spider'),
            ('GitHub', 'GITHUB_TOKEN', 'spider'),
        ]

        all_integrations = llm_providers + media_providers + infra + other

        for name, env_var, cat in all_integrations:
            if category != 'all' and cat != category:
                continue

            is_configured = bool(os.getenv(env_var))
            status = 'configured' if is_configured else 'missing'

            if status_filter != 'all' and status != status_filter:
                continue

            integrations.append({
                'name': name,
                'env_var': env_var,
                'category': cat,
                'configured': is_configured,
                'status': status
            })

        return {
            'total': len(integrations),
            'configured': sum(1 for i in integrations if i['configured']),
            'missing': sum(1 for i in integrations if not i['configured']),
            'integrations': integrations
        }

    def _check_env_config(self, category: str = 'all') -> Dict[str, Any]:
        """Check environment variable configuration."""
        env_categories = {
            'api_keys': [
                'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'STABILITY_API_KEY',
                'SERPER_API_KEY', 'STRIPE_SECRET_KEY', 'GEMINI_API_KEY',
                'TOGETHER_AI_API_KEY', 'RUNWAY_API_KEY', 'ELEVENLABS_API_KEY'
            ],
            'database': ['DATABASE_URL', 'DB_HOST', 'DB_NAME', 'DB_USER'],
            'redis': ['REDIS_URL', 'REDIS_HOST', 'CELERY_BROKER_URL'],
            'feature_flags': [
                'ENABLE_SPORTS_ANALYTICS', 'ENABLE_SELF_AWARENESS',
                'ENABLE_WEBSOCKETS', 'DEBUG'
            ]
        }

        results = {}
        categories_to_check = [category] if category != 'all' else env_categories.keys()

        for cat in categories_to_check:
            if cat not in env_categories:
                continue
            results[cat] = {}
            for var in env_categories[cat]:
                value = os.getenv(var)
                if value:
                    # Mask the value for security
                    if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var or 'PASSWORD' in var:
                        masked = value[:4] + '***' + value[-4:] if len(value) > 8 else '***'
                    else:
                        masked = value[:20] + '...' if len(value) > 20 else value
                    results[cat][var] = {'configured': True, 'value_preview': masked}
                else:
                    results[cat][var] = {'configured': False, 'value_preview': None}

        return results

    def _count_database_models(self, models: List[str] = None) -> Dict[str, Any]:
        """Count records in database models."""
        from django.apps import apps

        model_mappings = {
            'Agent': ('agents', 'Agent'),
            'AgentExecution': ('core', 'AgentExecution'),
            'AgentMemory': ('core', 'AgentMemory'),
            'SpiderData': ('core', 'SpiderData'),
            'Conversation': ('core', 'Conversation'),
            'User': ('core', 'User'),
            'ImageHistory': ('core', 'ImageHistory'),
            'VideoHistory': ('core', 'VideoHistory'),
        }

        if not models:
            models = list(model_mappings.keys())

        counts = {}
        for model_name in models:
            if model_name not in model_mappings:
                counts[model_name] = {'error': 'Unknown model'}
                continue

            try:
                app_label, model_class_name = model_mappings[model_name]
                model = apps.get_model(app_label, model_class_name)
                counts[model_name] = {'count': model.objects.count()}
            except Exception as e:
                counts[model_name] = {'error': str(e)}

        return counts

    def _generate_audit_report(self, audit_type: str, include_recommendations: bool = True) -> Dict[str, Any]:
        """Generate a comprehensive audit report."""
        from datetime import datetime

        report = {
            'audit_type': audit_type,
            'generated_at': datetime.now().isoformat(),
            'agent': self.name,
        }

        if audit_type in ['integrations', 'comprehensive']:
            report['integrations'] = self._inventory_integrations()

        if audit_type in ['configuration', 'comprehensive']:
            report['configuration'] = self._check_env_config()

        if audit_type in ['database', 'comprehensive']:
            report['database'] = self._count_database_models()

        if include_recommendations:
            recommendations = []

            # Check for missing critical integrations
            if 'integrations' in report:
                missing = [i['name'] for i in report['integrations'].get('integrations', []) if not i['configured']]
                if missing:
                    recommendations.append({
                        'priority': 'high',
                        'finding': f"Missing API keys for: {', '.join(missing)}",
                        'action': 'Configure these environment variables in production'
                    })

            report['recommendations'] = recommendations

        return report
