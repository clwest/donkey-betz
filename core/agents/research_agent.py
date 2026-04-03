"""
Research Agent - Specialized for Web & Spider Search ONLY
==========================================================

Session 268: Phase 2 - Research Agents
Session 304: Learning Infrastructure Integration
Session 683: Added ML Integration (DistilBERT for text analysis)
Session 872: Research Contract Integration - Structured, validated outputs

This agent searches for information. That's ALL it does.
It has NO access to creation, editing, or generation tools.

Tools Available:
    - web_search: Search the web using Serper API
    - spider_query: Query the spider network for data
    - analyze_trends: Analyze trending topics from spiders

Tools NOT Available (by design):
    - image/video/audio generation
    - editing operations
    - 3D generation

Session 872 - Research Contract:
    All research outputs now use ResearchContract for:
    - Binary status (no contradictions)
    - Specific deliverables (auto-generated)
    - Confidence with reasoning
    - Escalation paths for blocked work
"""

import logging
import re
import time
from typing import Dict, Any, List

from core.agents.base_agent import BaseAgent, AgentResult, ActionableOutputConfig
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and information gathering. Cannot create content.

    This agent:
    1. Takes a research task like "find trending AI topics"
    2. Queries web search and/or spider network
    3. Synthesizes and returns findings

    It CANNOT:
    - Generate images, videos, or audio
    - Edit any content
    - Create 3D models
    """

    name = "ResearchAgent"
    create_deliverable_on_schedule = False  # Session 1077: scheduled outputs go to AgentExecution only
    llm_timeout = 180.0  # Session 1074: Research tasks generate long outputs, need 3 min

    system_prompt = """You are ResearchAgent, a specialist in finding and analyzing information.

Your ONLY job is to research topics and gather information. You do NOT create content.
You have these tools:
- web_search: Search the web for current information
- spider_query: Query cached spider data (70 spiders, but only 15 Reddit subreddits)
- reddit_search: Search ANY Reddit subreddit in real-time (use for specific communities!)
- analyze_trends: Analyze trending topics from spider data
- query_internal_data: Query DonkeyBetz internal database (experiments, executions, initiatives, learnings)
- read_file: Read source code files from the codebase workspace
- list_files: List files matching a glob pattern (e.g., '**/*.py', 'core/agents/*.py')
- search_in_files: Search for text patterns across codebase files

CODEBASE ANALYSIS (Session 1028):
For tasks about code structure, memory usage, patterns, or implementation details:
1. Use list_files to explore directory structure
2. Use search_in_files to find relevant code patterns
3. Use read_file to examine specific files
These give you DIRECT access to the codebase — no need for external tools.

INTERNAL DATA (Session 884):
For tasks about system internals (experiments, failures, executions, initiatives), use query_internal_data:
- data_type='experiments' + filter='failed' → Get failed experiments
- data_type='experiments' + filter='halted' → Get halted experiments
- data_type='agent_executions' + filter='failed' → Get failed agent executions
- data_type='agent_learnings' → Get learning patterns
- data_type='initiatives' + filter='blocked' → Get blocked initiatives
- data_type='decision_records' → Get system decisions

DO NOT ask for CSV exports, BigQuery, or external data dumps. You have DIRECT database access.

Spider network categories:
- Tech: HackerNews, DevTo, TechCrunch, Wired, MIT Tech Review
- Jobs: RemoteOK, WeWorkRemotely, Adzuna
- Financial: CoinGecko, Yahoo Finance
- Creative: Dribbble, Behance, Unsplash
- Community: Reddit (15 cached subreddits)

Dynamic Reddit Search (Session 312):
Use reddit_search for specific communities not in spider cache:
- Combine subreddits with +: "python+learnpython+django"
- Industry subreddits: r/podcasting, r/coffee, r/photography
- Technical subs: r/reactjs, r/golang, r/rust

When given a research task:
1. For INTERNAL system analysis (experiments, failures, executions), use query_internal_data FIRST
2. For current events/news, prefer web_search
3. For trends/opportunities, prefer spider_query
4. For specific Reddit communities, use reddit_search
5. Synthesize findings into a clear summary with ACTUAL DATA

You CANNOT create images, videos, audio, or edit anything directly. Only research.

DELEGATION (Session 744):
If asked to create content, images, or perform tasks outside research, use the delegate_to_specialist tool:
- Need content/writing? Delegate to ContentWriterAgent
- Need images/logos? Delegate to ImageAgent
- Need videos? Delegate to VideoAgent
- Need financial analysis? Delegate to StockAnalystAgent
- Need code? Delegate to CodeGeneratorAgent

Always delegate tasks you cannot perform yourself rather than refusing."""

    tools = [
        # web_search tool definition removed — handled by BaseAgent fallback (Session 1090)
        {
            "type": "function",
            "function": {
                "name": "spider_query",
                "description": "Query the spider network for data from 70 spiders across 24 sources",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for spider data"
                        },
                        "category": {
                            "type": "string",
                            "description": "Filter by spider category",
                            "enum": ["tech", "financial", "jobs", "news", "social", "creative", "crypto"],
                            "default": None
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 72
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 20
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_trends",
                "description": "Analyze trending topics from spider data. Use topic_filter to focus on specific areas like 'ai' for AI/ML content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to analyze",
                            "enum": ["tech", "financial", "jobs", "creative", "all"],
                            "default": "all"
                        },
                        "topic_filter": {
                            "type": "string",
                            # Session 957: Added '3d' filter for 3D design/modeling content
                            "description": "Filter results to specific topic: 'ai' for AI/ML, 'web' for web dev, 'security' for cybersecurity, 'cloud' for cloud/devops, 'design' for UI/UX/graphic design, '3d' for 3D modeling/design",
                            "enum": ["ai", "web", "security", "cloud", "design", "3d"],
                            "default": None
                        },
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 24
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top trends to return",
                            "default": 10
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "reddit_search",
                "description": "Search ANY Reddit subreddit in real-time. Use for specific communities not cached by spider_query. Supports combining subreddits with + (e.g., 'python+django+flask').",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "subreddits": {
                            "type": "string",
                            "description": "Subreddit(s) to search, joined with +. Use 'all' for all of Reddit.",
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max results to return",
                            "default": 25
                        },
                        "sort": {
                            "type": "string",
                            "description": "Sort order",
                            "enum": ["relevance", "hot", "top", "new"],
                            "default": "relevance"
                        },
                        "time_filter": {
                            "type": "string",
                            "description": "Time period to search",
                            "enum": ["hour", "day", "week", "month", "year", "all"],
                            "default": "month"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        # Session 884: Internal data query tool - query DonkeyBetz database directly
        {
            "type": "function",
            "function": {
                "name": "query_internal_data",
                "description": "Query internal DonkeyBetz database for experiments, agent executions, initiatives, and other system data. Use this for internal analytics instead of asking for data exports.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "data_type": {
                            "type": "string",
                            "description": "Type of internal data to query",
                            "enum": [
                                "experiments",
                                "agent_executions",
                                "initiatives",
                                "agent_learnings",
                                "deliverables",
                                "conversations",
                                "spider_data_stats",
                                "conceptforge_runs",
                                "decision_records"
                            ]
                        },
                        "filter": {
                            "type": "string",
                            "description": "Filter condition: 'failed', 'halted', 'recent', 'all', 'blocked', 'active'",
                            "default": "recent"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max records to return",
                            "default": 20,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "For 'recent' filter, how many days back to look",
                            "default": 7
                        },
                        "include_details": {
                            "type": "boolean",
                            "description": "Include full details vs summary only",
                            "default": True
                        }
                    },
                    "required": ["data_type"]
                }
            }
        },
        # ================================================================
        # SESSION 1028: READ-ONLY CODEBASE TOOLS
        # Copied from CodeGeneratorAgent — no write/edit tools
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

    # Session 763: Mission Control configuration
    # Session 856: Enhanced payload_fields to include actionable insights for human review
    actionable_config = ActionableOutputConfig(
        enabled=True,
        item_type='insight',
        default_urgency='medium',
        min_confidence=0.0,
        actions=[
            {'id': 'deep_dive', 'label': 'Deep Dive', 'style': 'primary', 'description': 'Queue deeper research'},
            {'id': 'share', 'label': 'Share', 'style': 'success', 'description': 'Share with team'},
            {'id': 'archive', 'label': 'Archive', 'style': 'secondary', 'description': 'Save for later'},
            {'id': 'dismiss', 'label': 'Dismiss', 'style': 'danger', 'description': 'Not relevant'},
        ],
        # Session 856: Include fields that DecisionDetailModal can render
        payload_fields=['key_insights', 'sources_count', 'topics', 'sentiment', 'recommended_stance', 'rationale'],
        max_items_per_hour=5
    )

    def __init__(self, user=None):
        super().__init__(user)
        self._spider_service = None
        self._search_service = None
        self._iterative_attempts = []  # Track search attempts for provenance
        self._evidence_cards = []  # Session 1103: Citation cards for ClaimsPack bridge

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    # === Iterative Search (Session 1103) ===

    def _iterative_search(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Session 1103: Direct iterative search bypassing GPT for query selection.

        Calls SearchStrategyService to generate query variants, executes them
        directly via web_search and spider_query, evaluates results, and retries
        with broader/narrower queries if insufficient.

        Returns:
            {
                'results': [...],       # All collected results
                'attempts': [...],      # Attempt log with queries and outcomes
                'sufficient': bool,     # Whether enough on-topic results were found
                'quality_score': int,   # 0-100 quality assessment
                'tool_calls': [...],    # Tool call records for provenance
            }
        """
        from core.services.search_strategy_service import (
            generate_query_plan,
            evaluate_search_results,
        )

        workspace_brief = context.get('workspace_brief', {}) if isinstance(context, dict) else {}
        if not isinstance(workspace_brief, dict):
            workspace_brief = {}

        all_results = []
        all_tool_calls = []
        attempts = []

        # Round 1: Generate query plan from SearchStrategyService
        query_plan = generate_query_plan(task, workspace_brief, max_queries=6)
        if not query_plan:
            # Fallback: use task itself as a single query
            query_plan = [{'query': self._extract_search_query(task), 'strategy': 'fallback', 'priority': 1}]

        round_results = self._execute_search_round(query_plan, all_tool_calls)
        all_results.extend(round_results)

        attempts.append({
            'round': 1,
            'strategy': 'initial',
            'queries': [q['query'] for q in query_plan],
            'results_count': len(round_results),
            'strategies_used': list({q['strategy'] for q in query_plan}),
        })

        # Evaluate results
        evaluation = evaluate_search_results(query_plan, round_results, task)

        # Round 2: Retry if insufficient
        if not evaluation.get('sufficient') and evaluation.get('next_queries'):
            next_queries = evaluation['next_queries']
            round_results = self._execute_search_round(next_queries, all_tool_calls)
            all_results.extend(round_results)

            attempts.append({
                'round': 2,
                'strategy': evaluation.get('recommendation', 'retry'),
                'queries': [q['query'] for q in next_queries],
                'results_count': len(round_results),
            })

            # Re-evaluate with all results
            evaluation = evaluate_search_results(query_plan, all_results, task)

        # Round 3: Last resort broadening if still insufficient
        if not evaluation.get('sufficient') and len(attempts) < 3:
            from core.services.search_strategy_service import _extract_keywords
            keywords = _extract_keywords(task)
            broader = ' '.join(sorted(keywords)[:2])
            broaden_queries = [
                {'query': f"{broader} latest news 2026", 'strategy': 'broaden_last_resort'},
                {'query': f"{broader} overview analysis", 'strategy': 'broaden_last_resort'},
            ]
            round_results = self._execute_search_round(broaden_queries, all_tool_calls)
            all_results.extend(round_results)

            attempts.append({
                'round': 3,
                'strategy': 'broaden_last_resort',
                'queries': [q['query'] for q in broaden_queries],
                'results_count': len(round_results),
            })

            evaluation = evaluate_search_results(query_plan, all_results, task)

        self._iterative_attempts = attempts

        logger.info(
            "[IterativeSearch] %s: %d rounds, %d total results, quality=%d, sufficient=%s",
            task[:60], len(attempts), len(all_results),
            evaluation.get('quality_score', 0), evaluation.get('sufficient', False),
        )

        return {
            'results': all_results,
            'attempts': attempts,
            'sufficient': evaluation.get('sufficient', False),
            'quality_score': evaluation.get('quality_score', 0),
            'tool_calls': all_tool_calls,
        }

    def _execute_search_round(
        self,
        queries: List[Dict[str, Any]],
        tool_calls_log: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute a round of search queries via web_search and spider_query."""
        results = []

        for q in queries:
            query_text = q.get('query', '')
            if not query_text:
                continue

            # Web search
            try:
                web_result = self._execute_tool_call('web_search', {
                    'query': query_text,
                    'num_results': 8,
                })
                if not isinstance(web_result, dict):
                    web_result = {'success': False, 'data': web_result}
                tool_calls_log.append({
                    'tool': 'web_search',
                    'arguments': {'query': query_text},
                    'result': web_result,
                    'strategy': q.get('strategy', 'unknown'),
                })
                if web_result.get('success'):
                    data = web_result.get('data', web_result)
                    if isinstance(data, dict) and 'results' in data:
                        results.extend(data['results'])
                    elif isinstance(data, list):
                        results.extend(data)
            except Exception as e:
                logger.warning("web_search failed for %r: %s", query_text[:60], e)

            # Spider query (only for first 3 queries to avoid over-querying)
            source_hint = q.get('source_hint', 'search')
            if source_hint != 'search' or q.get('priority', 99) <= 3:
                try:
                    spider_result = self._execute_tool_call('spider_query', {
                        'query': query_text,
                        'hours': 72,
                        'limit': 10,
                    })
                    if not isinstance(spider_result, dict):
                        spider_result = {'success': False, 'data': spider_result}
                    tool_calls_log.append({
                        'tool': 'spider_query',
                        'arguments': {'query': query_text},
                        'result': spider_result,
                        'strategy': q.get('strategy', 'unknown'),
                    })
                    if spider_result.get('success'):
                        data = spider_result.get('data', spider_result)
                        if isinstance(data, list):
                            results.extend(data)
                        elif isinstance(data, dict):
                            results.extend(data.get('results', data.get('data', [])))
                except Exception as e:
                    logger.warning("spider_query failed for %r: %s", query_text[:60], e)

        return results

    # === Session 683: ML Integration Methods ===

    def _analyze_text_with_ml(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Analyze research text using ML models (DistilBERT).

        Uses the Agent-Model Router to automatically select optimal models
        for text classification, sentiment analysis, and topic extraction.

        Args:
            research_results: List of research results with text content

        Returns:
            Dict with ML analysis results including topics and sentiment
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build text data from research results
            text_data = self._build_research_text_data(research_results)

            if not text_data.get('texts'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient text data for ML analysis'
                }

            # Route to optimal ML model (DistilBERT for text)
            result = router.auto_route(
                data=text_data,
                task_hint=TaskType.TEXT,
                max_models=2
            )

            auto_sel = result.auto_selection if isinstance(result.auto_selection, dict) else {}
            return {
                'ml_used': True,
                'task_type': auto_sel.get('task_type', 'text'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'topics_detected': self._extract_topics_from_result(result),
                'sentiment': self._extract_sentiment_from_result(result),
                'selection_reason': auto_sel.get('selection_reason', ''),
            }

        except Exception as e:
            logger.warning(f"ML text analysis failed: {e}")
            return {
                'ml_used': False,
                'reason': f'ML error: {str(e)}'
            }

    def _build_research_text_data(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Build text data structure from research results.

        Extracts titles, descriptions, and content from research results.

        Args:
            research_results: List of research results from web/spider search

        Returns:
            Text data dict for ML routing
        """
        texts = []
        metadata = []

        for result in research_results:
            # Handle different result formats
            if isinstance(result, dict):
                # Extract text content
                text_parts = []
                if result.get('title'):
                    text_parts.append(result['title'])
                if result.get('description'):
                    text_parts.append(result['description'])
                if result.get('snippet'):
                    text_parts.append(result['snippet'])
                if result.get('selftext'):
                    text_parts.append(result['selftext'][:500])
                if result.get('content'):
                    text_parts.append(result['content'][:500])

                if text_parts:
                    texts.append(' '.join(text_parts))
                    metadata.append({
                        'source': result.get('source', 'unknown'),
                        'url': result.get('url', ''),
                    })

            elif isinstance(result, str):
                texts.append(result)
                metadata.append({'source': 'raw_text'})

        return {
            'texts': texts,
            'metadata': metadata,
            'data_type': 'research_content'
        }

    def _extract_topics_from_result(self, ml_result) -> List[str]:
        """
        Session 683: Extract detected topics from ML result.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            List of detected topic strings
        """
        try:
            if hasattr(ml_result, 'explanation') and ml_result.explanation:
                # Parse topics from explanation if present
                explanation = ml_result.explanation
                if 'topic' in explanation.lower():
                    # Simple extraction - may need refinement
                    return [explanation.split(':')[-1].strip()[:100]]
            return []
        except Exception:
            return []

    def _extract_sentiment_from_result(self, ml_result) -> str:
        """
        Session 683: Extract sentiment from ML result.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            Sentiment string: 'positive', 'negative', 'neutral', or 'mixed'
        """
        try:
            if hasattr(ml_result, 'score') and ml_result.score is not None:
                score = ml_result.score
                if isinstance(score, (int, float)):
                    if score > 0.6:
                        return 'positive'
                    elif score < 0.4:
                        return 'negative'
                    else:
                        return 'neutral'
            return 'unknown'
        except Exception:
            return 'unknown'

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """
        Execute research based on the task.

        Session 858: Now receives user context via context['user'] for personalized research.
        - User's interests and learning goals influence search priorities
        - Memory summary provides past research patterns
        """
        start_time = time.time()
        tool_calls_made = []
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 875: Ensure context is a dict (defensive fix for list being passed)
        if not isinstance(context, dict):
            logger.warning(f"ResearchAgent received non-dict context (type={type(context).__name__}), using empty dict")
            context = {}

        # Session 858: Extract user context for personalized research
        # Session 1102: Guard against stringified context values (JSON default=str
        # can turn non-serializable objects into strings)
        user_context = context.get('user', {})
        if not isinstance(user_context, dict):
            user_context = {}
        self._user_context = user_context

        # Session 858: Enhance task with user context for personalized research
        if user_context and user_context.get('has_user_context'):
            user_name = user_context.get('name', '')
            research_interests = user_context.get('research_interests', [])
            memory_summary = user_context.get('memory_summary', '')

            # Build user context addition to task
            user_context_parts = []
            if user_name:
                user_context_parts.append(f"Researching for: {user_name}")
            if research_interests:
                interests_text = ", ".join(research_interests[:5]) if isinstance(research_interests, list) else str(research_interests)
                user_context_parts.append(f"User's research interests: {interests_text}")
            if memory_summary:
                user_context_parts.append(f"Past research patterns: {memory_summary[:150]}...")

            if user_context_parts:
                task = f"{task}\n\n[User Context: {'; '.join(user_context_parts)}]"
                logger.info(f"📚 Session 858: Enhanced research task with user context for {user_name or 'user'}")

        # Session 1103: Iterative search replaces GPT-mediated query selection.
        # SearchStrategyService generates queries directly; GPT only synthesizes results.

        # Session 529: Build intelligent prompt with full context
        self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

        with self.time_travel_session("research", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing research request",
                    reasoning=f"Received task: {task[:100]}",
                    confidence=0.9
                )

                # Session 401: Use prompt with attribution for transparency
                full_prompt, knowledge_attribution = self._build_prompt_with_attribution(task, scifi_context, spider_context)

                # === Session 1103: Iterative Search — bypass GPT for query selection ===
                # Run direct searches first, then pass results to GPT for synthesis only.
                iterative = self._iterative_search(task, context)
                iterative_results = iterative.get('results', [])
                tool_calls_made = iterative.get('tool_calls', [])

                self.record_decision(
                    decision_type="iterative_search",
                    action=f"Direct search: {len(iterative.get('attempts', []))} rounds, {len(iterative_results)} results",
                    reasoning=f"Quality={iterative.get('quality_score', 0)}, sufficient={iterative.get('sufficient', False)}",
                    confidence=0.95,
                )

                if iterative_results:
                    # Format pre-gathered results as structured evidence cards
                    evidence_block = self._format_results_for_synthesis(iterative_results, task)
                    synthesis_prompt = (
                        f"{full_prompt}\n\n"
                        f"{evidence_block}\n\n"
                        f"[SYNTHESIS INSTRUCTIONS]\n"
                        f"You have been given evidence cards [E1], [E2], etc. from real sources.\n"
                        f"Produce a structured research brief with these REQUIREMENTS:\n"
                        f"1. Executive summary (2-3 sentences)\n"
                        f"2. Key findings — cite at least 3 evidence cards by ID (e.g. [E1], [E3])\n"
                        f"3. Include at least 2 direct quotes or statistics from the evidence cards\n"
                        f"4. For each claim you make, reference the evidence card that supports it\n"
                        f"5. Include source URLs for your top 3 citations\n"
                        f"6. Identify 1-2 gaps or areas needing deeper research\n"
                        f"DO NOT make claims not supported by the evidence cards.\n"
                        f"DO NOT search for additional information — use only what is provided.\n"
                    )
                    # Call GPT without tools — synthesis only (no tool_choice)
                    saved_tools = self.tools
                    self.tools = []
                    try:
                        gpt_response = self._call_openai(synthesis_prompt)
                    finally:
                        self.tools = saved_tools
                    # Wrap iterative results into the standard all_results format
                    all_results = [{'source': 'iterative_search', 'data': iterative_results}]
                else:
                    # Fallback: no iterative results — let GPT try with tools
                    logger.warning("[IterativeSearch] No results from direct search, falling back to GPT-mediated search")
                    execution_context = {
                        'spider_context': spider_context,
                        'scifi_context': scifi_context,
                        'task': task,
                    }
                    gpt_response = self._call_openai(full_prompt, execution_context=execution_context)
                    all_results = []

                    # Process GPT tool calls (legacy path)
                    if gpt_response.get('tool_calls'):
                        for tool_call in gpt_response['tool_calls']:
                            tool_name = tool_call['name']
                            arguments = tool_call['arguments']
                            tool_result = self._execute_tool_call(tool_name, arguments)
                            if not isinstance(tool_result, dict):
                                tool_result = {'success': False, 'data': tool_result, 'error': 'non-dict tool result'}
                            tool_calls_made.append({
                                'tool': tool_name,
                                'arguments': arguments,
                                'result': tool_result,
                            })
                            if tool_result.get('success'):
                                all_results.append({'source': tool_name, 'data': tool_result.get('data', tool_result)})
                            elif tool_result.get('data'):
                                all_results.append({'source': tool_name, 'data': tool_result.get('data'), 'partial': True})

                if all_results:
                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:  # Always true here but preserves structure for else-failure path
                        # Session 683: Add ML text analysis to research results
                        ml_analysis = {}
                        all_result_data = []
                        for r in all_results:
                            # Session 881: Defensive check - r might be a list in edge cases
                            if isinstance(r, list):
                                all_result_data.extend(r)
                                continue
                            if not isinstance(r, dict):
                                continue
                            data = r.get('data', r)
                            if isinstance(data, list):
                                all_result_data.extend(data)
                            elif isinstance(data, dict):
                                if 'results' in data:
                                    all_result_data.extend(data['results'])
                                else:
                                    all_result_data.append(data)

                        if all_result_data:
                            ml_analysis = self._analyze_text_with_ml(all_result_data)

                        # Session 872: Build Research Contract for structured output
                        research_contract = self._build_research_contract(
                            task=task,
                            all_results=all_results,
                            ml_analysis=ml_analysis,
                            tool_calls_made=tool_calls_made
                        )

                        # Session 1103: Build ClaimsPack-compatible claims from evidence
                        research_claims = self._build_claims_from_evidence(
                            iterative_results if iterative_results else [],
                            task,
                        )

                        result_data = {
                            'results': all_results,
                            'query': task,
                            'sources_count': len(all_results),
                            # Session 872: Include Research Contract
                            'contract': research_contract,
                            # Session 1103: Include iterative search attempts for provenance
                            'attempts': self._iterative_attempts,
                            # Session 1103: Evidence cards for ClaimsPack bridge
                            'evidence_claims': research_claims,
                        }

                        # Add ML analysis if performed
                        if ml_analysis.get('ml_used'):
                            result_data['ml_analysis'] = {
                                'models_used': ml_analysis.get('models_used', []),
                                'confidence': ml_analysis.get('confidence', 0),
                                'topics_detected': ml_analysis.get('topics_detected', []),
                                'sentiment': ml_analysis.get('sentiment', 'unknown'),
                                'ml_insights': ml_analysis.get('ml_insights', ''),
                            }
                            # Session 856: Surface ML insights for human review
                            result_data['topics'] = ml_analysis.get('topics_detected', [])
                            result_data['sentiment'] = ml_analysis.get('sentiment', 'unknown')

                        # Session 856: Extract key insights for human review
                        # Session 958: Fixed to handle nested structures from analyze_trends
                        # (topics, discussions, projects, results arrays)
                        key_insights = []
                        for r in all_results[:5]:  # Top 5 results
                            # Session 881: Defensive check - r might be a list
                            if isinstance(r, list):
                                for item in r[:2]:  # Take first 2 items from list
                                    if isinstance(item, dict):
                                        title = item.get('title') or item.get('headline') or ''
                                        if title:
                                            key_insights.append(str(title)[:200])
                                continue
                            if not isinstance(r, dict):
                                continue
                            data = r.get('data', r)
                            if isinstance(data, dict):
                                # Try to get title or summary from the result
                                title = data.get('title') or data.get('headline') or data.get('query', '')
                                if title:
                                    key_insights.append(str(title)[:200])
                                else:
                                    # Session 958: Handle nested arrays from analyze_trends
                                    # Check for 'topics', 'discussions', 'projects', 'results' arrays
                                    nested_arrays = ['topics', 'discussions', 'projects', 'results', 'items']
                                    for array_key in nested_arrays:
                                        if array_key in data and isinstance(data[array_key], list):
                                            for nested_item in data[array_key][:3]:  # Top 3 from each array
                                                if isinstance(nested_item, dict):
                                                    # Extract title from nested dict
                                                    nested_title = (
                                                        nested_item.get('title') or
                                                        nested_item.get('topic') or
                                                        nested_item.get('name') or
                                                        nested_item.get('headline') or
                                                        nested_item.get('keyword', '')
                                                    )
                                                    if nested_title and len(nested_title) > 5:
                                                        # Add source context
                                                        source_name = r.get('source', '')
                                                        url = nested_item.get('url', '')
                                                        if url:
                                                            key_insights.append(f"[{nested_title[:150]}]({url})")
                                                        else:
                                                            key_insights.append(str(nested_title)[:200])
                                                elif isinstance(nested_item, str) and len(nested_item) > 5:
                                                    key_insights.append(nested_item[:200])
                                            break  # Found content in one array, move to next result
                            elif isinstance(data, str) and data:
                                key_insights.append(data[:200])

                        # Add ML insights as a key insight if available
                        if ml_analysis.get('ml_insights'):
                            key_insights.insert(0, ml_analysis['ml_insights'][:300])

                        result_data['key_insights'] = key_insights[:5]  # Max 5 insights

                        # Session 872: Build summary from contract status
                        contract_status = research_contract.get('status', 'UNKNOWN')
                        contract_confidence = research_contract.get('confidence', 0)
                        confidence_reason = research_contract.get('confidence_reason', '')

                        summary_parts = [f"Research on: {task[:100]}"]
                        summary_parts.append(f"Status: {contract_status}")
                        summary_parts.append(f"Confidence: {contract_confidence:.0%}")
                        if contract_status == 'BLOCKED':
                            blocked_on = research_contract.get('blocked_on', 'Unknown')
                            summary_parts.append(f"Blocked: {blocked_on[:100]}")
                        elif key_insights:
                            summary_parts.append(f"Key finding: {key_insights[0][:100]}")

                        research_summary = ". ".join(summary_parts)

                        result = AgentResult(
                            success=True,
                            message=research_summary,
                            data=result_data,
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            decisions_made=self._tt_decision_count,
                            tool_calls=tool_calls_made,
                            knowledge_attribution=knowledge_attribution  # Session 401
                        )

                        # === Session 304: Learning Infrastructure ===
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=True,  # Always uses spider data
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="success",
                            importance=0.6
                        )

                        # Share knowledge about research patterns
                        sources_used = [r['source'] for r in all_results]
                        self._share_knowledge(
                            knowledge_type='trend',
                            title=f"Research: {task[:60]}",
                            knowledge_value={
                                'query': task,
                                'sources_used': sources_used,
                                'result_count': len(all_results),
                                'success': True
                            },
                            confidence=0.75
                        )

                        # Session 763: Create Mission Control attention item
                        self._maybe_create_attention_item(result, task, context)

                        # Session 861: Persist research findings to Deliverable
                        research_content = f"# Research: {task}\n\n"
                        research_content += f"**Sources:** {len(all_results)}\n\n"
                        if key_insights:
                            research_content += "## Key Insights\n"
                            for i, insight in enumerate(key_insights, 1):
                                research_content += f"{i}. {insight}\n"
                            research_content += "\n"
                        if ml_analysis.get('sentiment') and ml_analysis['sentiment'] != 'unknown':
                            research_content += f"**Sentiment:** {ml_analysis['sentiment']}\n"
                        if ml_analysis.get('topics_detected'):
                            research_content += f"**Topics:** {', '.join(ml_analysis['topics_detected'])}\n"

                        self._save_to_deliverable(
                            title=f"Research: {task[:100]}",
                            content=research_content,
                            deliverable_type='research',
                            category='Research',
                            tags=['research'] + ml_analysis.get('topics_detected', [])[:3],
                            content_format='markdown',
                            metadata={
                                'query': task,
                                'sources_count': len(all_results),
                                'sources_used': sources_used,
                                'sentiment': ml_analysis.get('sentiment', 'unknown'),
                                'ml_used': ml_analysis.get('ml_used', False),
                            },
                        )

                        return result
                    else:
                        # Session 990: Include tool errors in failure message
                        tool_errors = []
                        for tc in tool_calls_made:
                            err = tc.get('result', {}).get('error')
                            if err:
                                tool_errors.append(f"{tc['tool']}: {err}")
                        error_detail = "; ".join(tool_errors) if tool_errors else "No tools returned results"
                        result = AgentResult(
                            success=False,
                            error=f"Research returned no results ({error_detail})",
                            agent_name=self.name,
                            execution_time_ms=execution_time,
                            tool_calls=tool_calls_made
                        )

                        # Record failure for learning
                        self._record_learning_outcome(
                            result=result,
                            task=task,
                            context=context,
                            spider_data_used=True,
                            scifi_context_used=bool(scifi_context)
                        )

                        self._create_execution_memory(
                            result=result,
                            task=task,
                            memory_type="failure",
                            importance=0.7
                        )

                        return result
                else:
                    # Session 757: Return rich conversation data for Memory Palace display
                    response_content = gpt_response.get('content', '')
                    return AgentResult(
                        success=True,
                        message=response_content,
                        data={
                            'type': 'conversation',
                            'content_type': 'research_response',
                            'response': response_content,
                            'query': task,
                        },
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        knowledge_attribution=knowledge_attribution  # Session 401
                    )

            except Exception as e:
                logger.error(f"ResearchAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _format_results_for_synthesis(self, results: List[Dict[str, Any]], task: str) -> str:
        """
        Session 1103: Build structured evidence cards from search results for GPT synthesis.

        Instead of passing raw blobs, extracts the best quote/stat from each result
        and formats as citation cards with URLs. GPT synthesizes from these cards,
        producing output with real citations.
        """
        cards = []
        seen_urls = set()
        card_idx = 0

        for item in results[:30]:
            if not isinstance(item, dict):
                continue

            title = str(item.get('title') or item.get('headline') or item.get('name', '')).strip()
            snippet = str(item.get('snippet') or item.get('description') or item.get('content', '')).strip()
            url = str(item.get('url') or item.get('link') or item.get('source_url', '')).strip()

            if not snippet and not title:
                continue

            # Deduplicate by canonical URL (strip UTM params)
            canonical_url = re.sub(r'[?&]utm_\w+=[^&]*', '', url).rstrip('?&') if url else ''
            if canonical_url and canonical_url in seen_urls:
                continue
            if canonical_url:
                seen_urls.add(canonical_url)

            # Extract the best quote or statistic from the snippet
            evidence = self._extract_best_evidence(snippet)
            card_idx += 1

            card = f"[E{card_idx}] "
            if evidence['type'] == 'statistic':
                card += f'STAT: "{evidence["text"]}"'
            elif evidence['type'] == 'quote':
                card += f'QUOTE: "{evidence["text"]}"'
            else:
                card += f'FINDING: {evidence["text"]}'

            card += f'\n  Source: {title}' if title else ''
            card += f'\n  URL: {url}' if url else ''
            cards.append(card)

        # Store cards for ClaimsPack bridge
        self._evidence_cards = cards

        if not cards:
            return "(No evidence found from search results)"

        from core.services.search_strategy_service import extract_topic_from_task
        clean_topic = extract_topic_from_task(task)

        header = f"=== {len(cards)} EVIDENCE CARDS for: {clean_topic[:100]} ==="
        footer = "=== END EVIDENCE CARDS ==="
        return f"{header}\n\n" + '\n\n'.join(cards[:12]) + f"\n\n{footer}"

    def _extract_best_evidence(self, text: str) -> Dict[str, Any]:
        """
        Session 1103: Extract the best quote, statistic, or key finding from a snippet.

        Prioritizes: numbers/statistics > quoted text > key claims.
        """
        if not text:
            return {'type': 'finding', 'text': '(no content)'}

        # Look for statistics (numbers with context)
        stat_patterns = [
            r'(\d+(?:\.\d+)?%[^.]*\.)',           # "26% more completed tasks."
            r'(\$[\d,.]+\s*(?:billion|million|trillion)[^.]*\.)',  # "$2.5 billion market."
            r'(\d+(?:\.\d+)?x\s+[^.]*\.)',          # "3.5x faster than..."
            r'(\d{1,3}(?:,\d{3})+\s+[^.]*\.)',     # "4,867 developers..."
        ]
        for pattern in stat_patterns:
            match = re.search(pattern, text)
            if match and len(match.group(1)) > 15:
                return {'type': 'statistic', 'text': match.group(1).strip()[:250]}

        # Look for quoted text
        quote_match = re.search(r'"([^"]{20,200})"', text)
        if quote_match:
            return {'type': 'quote', 'text': quote_match.group(1).strip()}

        # Fall back to first meaningful sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 30 and not sent.lower().startswith(('click', 'subscribe', 'sign up', 'learn more')):
                return {'type': 'finding', 'text': sent[:250]}

        return {'type': 'finding', 'text': text[:250]}

    def _build_claims_from_evidence(self, results: List[Dict[str, Any]], task: str) -> List[Dict[str, Any]]:
        """
        Session 1103: Bridge evidence cards to ClaimsPack-compatible claims.

        Converts raw search results into SpiderClaim-shaped dicts that
        ContentWriterAgent can use for citation in the content pipeline.
        """
        from core.services.content_claims import make_claim_id
        from core.services.search_strategy_service import extract_topic_from_task

        claims = []
        seen_urls = set()
        clean_topic = extract_topic_from_task(task)

        # Session 1103: Build topic keywords for relevance filtering
        from core.services.search_strategy_service import _extract_keywords
        topic_keywords = _extract_keywords(clean_topic)

        for item in results[:30]:  # Scan more, filter down
            if not isinstance(item, dict):
                continue

            title = str(item.get('title') or item.get('headline') or '').strip()
            snippet = str(item.get('snippet') or item.get('description') or item.get('content', '')).strip()
            url = str(item.get('url') or item.get('link') or item.get('source_url', '')).strip()

            if not snippet or not url:
                continue

            canonical = re.sub(r'[?&]utm_\w+=[^&]*', '', url).rstrip('?&')
            if canonical in seen_urls:
                continue

            # Session 1103: Relevance filter — require minimum keyword overlap
            # between topic and the source title+snippet. Prevents garbage from
            # broad search rounds (gaming forums, support pages, etc.)
            combined_text = f"{title} {snippet}".lower()
            keyword_hits = sum(1 for kw in topic_keywords if kw in combined_text)
            if topic_keywords and keyword_hits < 2:
                continue  # Skip off-topic results

            seen_urls.add(canonical)

            evidence = self._extract_best_evidence(snippet)
            claim_id = make_claim_id(url, title)

            # Map evidence type to claim_type
            claim_type = 'factual' if evidence['type'] == 'statistic' else 'analytical'
            confidence = 0.7 if evidence['type'] == 'statistic' else 0.5

            claims.append({
                'claim_id': claim_id,
                'claim_text': evidence['text'],
                'source_url': url,
                'source_title': title,
                'evidence_excerpt': snippet[:300],
                'confidence': confidence,
                'claim_type': claim_type,
                'evidence_type': evidence['type'],
            })

            if len(claims) >= 12:  # Cap at 12 quality claims
                break

        logger.info("[ClaimsBridge] Built %d claims from research for: %s", len(claims), clean_topic[:60])
        return claims

    def _extract_search_query(self, task: str) -> str:
        """Extract a concise web search query from a verbose task description."""
        # Try to find an explicit topic after common research prefixes
        patterns = [
            r'(?:research|investigate|look into|find out about|analyze)\s+(.{10,120}?)(?:\.|$)',
            r'(?:about|regarding|on|for)\s+(.{10,120}?)(?:\.|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, task, re.IGNORECASE)
            if match:
                fragment = match.group(1).strip().rstrip(',.')
                return fragment

        # Fallback: strip common task prefixes
        cleaned = re.sub(
            r'^(perform|conduct|do|run|create|generate)\s+(a\s+)?'
            r'(comprehensive\s+|detailed\s+|thorough\s+)?'
            r'(research|investigation|analysis|report)\s+'
            r'(for|on|of|about|into)\s+',
            '', task, flags=re.IGNORECASE
        ).strip()

        if cleaned and len(cleaned) > 5:
            return cleaned[:120]

        return task[:100]

    # === Session 872: Research Contract Methods ===

    def _build_research_contract(
        self,
        task: str,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any],
        tool_calls_made: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Session 872: Build a Research Contract from research results.

        Enforces:
        - Binary status (no contradictions)
        - Specific deliverables
        - Confidence with reasoning
        - Escalation paths

        Args:
            task: Original research task
            all_results: Results from tool calls
            ml_analysis: ML analysis results
            tool_calls_made: Record of tool calls

        Returns:
            ResearchContract as dict
        """
        from core.contracts.research_contract import (
            ResearchContract,
            ResearchStatus,
            generate_deliverables_from_goal
        )

        # Determine status based on results
        has_results = bool(all_results)
        has_sufficient_data = self._assess_data_sufficiency(all_results, task)

        # Calculate confidence
        confidence, confidence_reason = self._calculate_research_confidence(
            all_results, ml_analysis, has_sufficient_data
        )

        # Auto-generate specific deliverables
        deliverables = generate_deliverables_from_goal(task)

        # Determine which deliverables are complete
        deliverables_complete = []
        if has_results:
            # Mark basic deliverables as complete if we have data
            if len(all_results) > 0:
                deliverables_complete.append(deliverables[0])  # Summary
            if len(all_results) >= 3:
                deliverables_complete.append(deliverables[1])  # Key findings
            # Session 881: Defensive check - r might be a list in edge cases
            if any(
                (isinstance(r, dict) and (r.get('data', {}).get('url') if isinstance(r.get('data'), dict) else False or r.get('source')))
                for r in all_results
            ):
                deliverables_complete.append(deliverables[2])  # Sources

        # Identify data gaps
        data_gaps = self._identify_data_gaps(all_results, task)

        # Build sources list
        sources_used = []
        for tc in tool_calls_made:
            sources_used.append(f"{tc['tool']}: {tc.get('arguments', {}).get('query', 'N/A')[:50]}")

        # Identify related agents that might be needed
        related_agents = self._identify_related_agents(task, data_gaps)

        try:
            if not has_results:
                # FAILED: No results at all
                contract = ResearchContract.create(
                    goal=task,
                    status=ResearchStatus.FAILED,
                    owner=self.name,
                    confidence=0.1,
                    confidence_reason="No results returned from any source",
                    deliverables=deliverables,
                    deliverables_complete=[],
                    data_gaps=["All data sources returned empty results"],
                    escalation_path="Retry with different search terms or escalate to DataExportAgent",
                    related_agents=['DataExportAgent', 'SystemAdminAgent']
                )
            elif not has_sufficient_data:
                # BLOCKED: Have some results but not enough
                blocked_on = self._determine_blocking_reason(data_gaps)
                contract = ResearchContract.create_blocked(
                    goal=task,
                    owner=self.name,
                    blocked_on=blocked_on,
                    escalation_path=f"If no additional data in 24h -> escalate to {related_agents[0] if related_agents else 'SystemAdminAgent'}",
                    inputs_required=data_gaps,
                    confidence_reason=confidence_reason,
                    deliverables=deliverables,
                    deliverables_complete=deliverables_complete,
                    findings=self._extract_partial_findings(all_results, ml_analysis),
                    sources_used=sources_used,
                    data_gaps=data_gaps,
                    related_agents=related_agents,
                    next_trigger=f"{related_agents[0] if related_agents else 'DataExportAgent'} provides missing data"
                )
            else:
                # COMPLETE: Have sufficient data
                contract = ResearchContract.create_complete(
                    goal=task,
                    owner=self.name,
                    deliverables=deliverables,
                    findings=self._extract_findings(all_results, ml_analysis),
                    confidence=confidence,
                    confidence_reason=confidence_reason,
                    recommendations=self._generate_recommendations(all_results, ml_analysis, task),
                    sources_used=sources_used,
                    data_gaps=data_gaps if data_gaps else [],
                    related_agents=related_agents
                )

            return contract.to_dict()

        except ValueError as e:
            # Contract validation failed - return error contract
            logger.warning(f"Research contract validation failed: {e}")
            return {
                'contract_type': 'research',
                'contract_version': '1.0',
                'status': 'FAILED',
                'goal': task,
                'owner': self.name,
                'confidence': 0.1,
                'confidence_reason': f"Contract validation failed: {str(e)}",
                'error': str(e)
            }

    def _assess_data_sufficiency(
        self,
        all_results: List[Dict[str, Any]],
        task: str
    ) -> bool:
        """
        Assess if we have sufficient data to complete the research.

        Session 874: Now includes auto-spawn reflex when data is insufficient.

        Returns True if data is sufficient, False if blocked.
        """
        if not all_results:
            # Session 874: Auto-spawn reflex for empty results
            self._trigger_auto_spawn_reflex(
                data_type='spider_data',
                current_count=0,
                required_count=5,
                context={'task': task, 'reason': 'empty_results'}
            )
            return False

        # Count total data points
        total_items = 0
        for result in all_results:
            # Session 881: Defensive check - result might be a list in edge cases
            if isinstance(result, list):
                total_items += len(result)
                continue
            if not isinstance(result, dict):
                continue
            data = result.get('data', result)
            if isinstance(data, list):
                total_items += len(data)
            elif isinstance(data, dict):
                if 'results' in data:
                    total_items += len(data['results'])
                else:
                    total_items += 1

        # Minimum threshold for "sufficient" data
        # Adjust based on task complexity
        # Session 957: Lowered thresholds significantly - having ANY results is useful
        # BLOCKED should only happen when we have literally nothing
        task_lower = task.lower()
        if 'comprehensive' in task_lower or 'detailed' in task_lower:
            min_items = 5  # Was 8, lowered to 5
        elif 'quick' in task_lower or 'brief' in task_lower:
            min_items = 1  # Was 2, lowered to 1
        elif 'trend' in task_lower or 'current' in task_lower:
            min_items = 1  # Session 957: Trend queries should work with any data
        else:
            min_items = 1  # Was 3→2→1: any results are useful, web_search fallback helps

        is_sufficient = total_items >= min_items

        # Session 874: Auto-spawn reflex when data is insufficient
        if not is_sufficient:
            # Determine data type from task
            data_type = self._infer_data_type_from_task(task_lower)
            self._trigger_auto_spawn_reflex(
                data_type=data_type,
                current_count=total_items,
                required_count=min_items,
                context={'task': task, 'reason': 'insufficient_data'}
            )

        return is_sufficient

    def _trigger_auto_spawn_reflex(
        self,
        data_type: str,
        current_count: int,
        required_count: int,
        context: Dict[str, Any]
    ) -> None:
        """
        Session 874: Auto-spawn reflex - when data is insufficient, spawn agents/spiders.

        This is the "missing reflex" identified by ChatGPT:
        "They all note '77 is small.' But no one triggers: DataExpansionAgent."
        "That's a missing reflex."

        Now we have it: when data is insufficient, we spawn.
        """
        try:
            from core.services.auto_spawner_service import auto_spawn_if_needed

            spawn_result = auto_spawn_if_needed(
                data_type=data_type,
                current_count=current_count,
                required_count=required_count,
                context={
                    **context,
                    'triggered_by': self.name,
                    'topic': context.get('task', 'research'),
                }
            )

            if spawn_result.get('spawned'):
                logger.info(
                    f"🔄 [Session 874] AUTO-SPAWN REFLEX: {data_type} had {current_count}/{required_count}, "
                    f"spawned {len(spawn_result.get('task_ids', []))} tasks"
                )
                # Store spawn info for inclusion in contract
                if not hasattr(self, '_auto_spawn_results'):
                    self._auto_spawn_results = []
                self._auto_spawn_results.append(spawn_result)
            else:
                logger.debug(
                    f"[Session 874] Auto-spawn skipped: {spawn_result.get('reason', 'sufficient data')}"
                )

        except ImportError:
            logger.warning("[Session 874] AutoSpawnerService not available")
        except Exception as e:
            logger.warning(f"[Session 874] Auto-spawn reflex failed: {e}")

    def _infer_data_type_from_task(self, task_lower: str) -> str:
        """Infer the data type from task description."""
        if 'job' in task_lower or 'career' in task_lower or 'salary' in task_lower:
            return 'job_listings'
        elif 'market' in task_lower or 'competitor' in task_lower:
            return 'market_trends'
        elif 'trend' in task_lower or 'news' in task_lower:
            return 'market_trends'
        else:
            return 'spider_data'

    def _calculate_research_confidence(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any],
        has_sufficient_data: bool
    ) -> tuple:
        """
        Calculate confidence score and reason.

        Returns:
            Tuple of (confidence: float, reason: str)
        """
        if not all_results:
            return 0.1, "No results - cannot assess confidence"

        if not has_sufficient_data:
            return 0.3, "Insufficient data for reliable conclusions"

        # Start with base confidence
        confidence = 0.5

        # Boost for multiple sources
        source_count = len(all_results)
        if source_count >= 3:
            confidence += 0.15
        elif source_count >= 2:
            confidence += 0.1

        # Boost for ML analysis
        if ml_analysis.get('ml_used'):
            confidence += 0.1
            if ml_analysis.get('confidence', 0) > 0.7:
                confidence += 0.1

        # Boost for diverse source types
        source_types = set()
        for r in all_results:
            source_types.add(r.get('source', 'unknown'))
        if len(source_types) >= 2:
            confidence += 0.1

        confidence = min(confidence, 0.95)  # Cap at 95%

        # Build reason
        reasons = []
        if source_count >= 3:
            reasons.append(f"{source_count} sources consulted")
        if ml_analysis.get('ml_used'):
            reasons.append("ML analysis applied")
        if len(source_types) >= 2:
            reasons.append(f"{len(source_types)} source types")

        if not reasons:
            reasons.append("Limited data available")

        reason = f"{self._confidence_to_label(confidence)} - {', '.join(reasons)}"

        return confidence, reason

    def _confidence_to_label(self, confidence: float) -> str:
        """Convert confidence score to label."""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium"
        elif confidence >= 0.4:
            return "Low"
        else:
            return "Very Low"

    def _identify_data_gaps(
        self,
        all_results: List[Dict[str, Any]],
        task: str
    ) -> List[str]:
        """Identify what data is missing."""
        gaps = []
        task_lower = task.lower()

        # Check for common data needs
        # Session 957: Only require temporal data for explicit time-series analysis requests
        # Simple "current trends" queries don't need temporal data - they just need current info
        time_series_keywords = ['over time', 'historical', 'timeline', 'progression', 'evolution',
                                'change over', 'trend analysis', 'time series', 'compare periods']
        needs_temporal = any(kw in task_lower for kw in time_series_keywords)

        if needs_temporal and all_results:  # Only check if we actually have results to check
            # Check if we have time-series data
            # Session 957: Include 'created' to match 'created_at' fields in spider data
            has_temporal = any(
                'timestamp' in str(r) or 'date' in str(r) or 'time' in str(r) or 'created' in str(r)
                for r in all_results
            )
            if not has_temporal:
                gaps.append("Time-series data for trend analysis")

        if 'competitor' in task_lower or 'market' in task_lower:
            if len(all_results) < 3:
                gaps.append("Additional competitor/market data sources")

        if 'experiment' in task_lower or 'execution' in task_lower:
            # Check for execution logs
            has_execution_data = any(
                'execution' in str(r).lower() or 'log' in str(r).lower()
                for r in all_results
            )
            if not has_execution_data:
                gaps.append("Experiment data (core.models.Experiment, AgentExecution)")

        if not all_results:
            gaps.append("Primary data sources returned no results")

        return gaps

    def _identify_related_agents(
        self,
        task: str,
        data_gaps: List[str]
    ) -> List[str]:
        """Identify agents that might help with data gaps."""
        agents = []
        task_lower = task.lower()
        gaps_str = ' '.join(data_gaps).lower()

        if 'export' in gaps_str or 'log' in gaps_str or 'execution' in gaps_str:
            agents.append('DataExportAgent')

        if 'competitor' in task_lower or 'market' in task_lower:
            agents.append('CompetitorAnalysisAgent')

        if 'trend' in task_lower or 'analysis' in task_lower:
            agents.append('TrendAnalysisAgent')

        if 'user' in task_lower or 'customer' in task_lower:
            agents.append('CustomerResearchAgent')

        if not agents:
            agents.append('DataExportAgent')  # Default fallback

        return agents

    def _determine_blocking_reason(self, data_gaps: List[str]) -> str:
        """Determine the primary blocking reason."""
        if not data_gaps:
            return "Insufficient data for reliable conclusions"

        # Prioritize specific data gaps
        for gap in data_gaps:
            if 'Experiment' in gap or 'log' in gap.lower():
                return f"Missing: {gap}"
            if 'time-series' in gap.lower() or 'temporal' in gap.lower():
                return f"Missing: {gap}"

        return f"Missing: {data_gaps[0]}"

    def _extract_partial_findings(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract partial findings when data is insufficient.
        Session 958: Fixed to handle nested structures (topics, discussions, etc.)
        """
        findings = {
            'status': 'Partial - awaiting additional data',
            'preliminary_observations': []
        }

        for result in all_results[:3]:  # Top 3
            data = result.get('data', result)
            if isinstance(data, dict):
                if data.get('title') or data.get('query'):
                    findings['preliminary_observations'].append(
                        data.get('title') or data.get('query', 'Unknown')
                    )
                else:
                    # Session 958: Check nested arrays
                    for array_key in ['topics', 'discussions', 'projects', 'results']:
                        if array_key in data and isinstance(data[array_key], list):
                            for item in data[array_key][:2]:
                                if isinstance(item, dict):
                                    title = (
                                        item.get('title') or item.get('topic') or
                                        item.get('name') or item.get('headline', '')
                                    )
                                    if title:
                                        findings['preliminary_observations'].append(title[:200])

        if ml_analysis.get('ml_insights'):
            findings['ml_observation'] = ml_analysis['ml_insights']

        return findings

    def _extract_findings(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract complete findings from results.
        Session 958: Fixed to handle nested structures (topics, discussions, projects, results).
        """
        findings = {
            'summary': '',
            'key_points': [],
            'sources_summary': {}
        }

        # Summarize by source
        for result in all_results:
            source = result.get('source', 'unknown')
            data = result.get('data', result)

            if source not in findings['sources_summary']:
                findings['sources_summary'][source] = []

            if isinstance(data, dict):
                title = data.get('title') or data.get('headline') or data.get('query', '')
                if title:
                    findings['sources_summary'][source].append(title[:200])
                    findings['key_points'].append(title[:200])
                else:
                    # Session 958: Handle nested arrays from analyze_trends and similar tools
                    nested_arrays = ['topics', 'discussions', 'projects', 'results', 'items']
                    for array_key in nested_arrays:
                        if array_key in data and isinstance(data[array_key], list):
                            for nested_item in data[array_key][:5]:  # Top 5 from each array
                                if isinstance(nested_item, dict):
                                    nested_title = (
                                        nested_item.get('title') or
                                        nested_item.get('topic') or
                                        nested_item.get('name') or
                                        nested_item.get('headline') or
                                        nested_item.get('keyword', '')
                                    )
                                    if nested_title and len(nested_title) > 3:
                                        # Include URL if available for context
                                        url = nested_item.get('url', '')
                                        if url:
                                            formatted = f"[{nested_title[:150]}]({url})"
                                        else:
                                            formatted = nested_title[:200]
                                        findings['sources_summary'][source].append(formatted)
                                        findings['key_points'].append(formatted)
                                elif isinstance(nested_item, str) and len(nested_item) > 3:
                                    findings['sources_summary'][source].append(nested_item[:200])
                                    findings['key_points'].append(nested_item[:200])

        # Add ML insights
        if ml_analysis.get('ml_insights'):
            findings['ml_analysis'] = ml_analysis['ml_insights']

        if ml_analysis.get('sentiment') and ml_analysis['sentiment'] != 'unknown':
            findings['sentiment'] = ml_analysis['sentiment']

        if ml_analysis.get('topics_detected'):
            findings['topics'] = ml_analysis['topics_detected']

        # Build summary
        point_count = len(findings['key_points'])
        source_count = len(findings['sources_summary'])
        findings['summary'] = f"Analyzed {point_count} data points from {source_count} sources."

        return findings

    def _generate_recommendations(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any],
        task: str
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Based on result count
        if len(all_results) >= 5:
            recommendations.append("Consider deeper analysis on top 3 findings")
        elif len(all_results) < 3:
            recommendations.append("Expand search to additional sources for validation")

        # Based on ML analysis
        sentiment = ml_analysis.get('sentiment', 'unknown')
        if sentiment == 'positive':
            recommendations.append("Sentiment is positive - explore opportunities")
        elif sentiment == 'negative':
            recommendations.append("Sentiment is negative - investigate concerns")

        # Based on task type
        task_lower = task.lower()
        if 'trend' in task_lower:
            recommendations.append("Monitor these trends over next 7-14 days")
        if 'competitor' in task_lower:
            recommendations.append("Schedule follow-up competitive analysis in 30 days")

        if not recommendations:
            recommendations.append("Review findings and determine next steps")

        return recommendations[:5]  # Max 5 recommendations

    # ================================================================
    # SESSION 1028: READ-ONLY CODEBASE TOOLS
    # Copied from CodeGeneratorAgent — no write/edit methods
    # ================================================================

    def _read_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a file from the workspace.

        Session 1028: Copied from CodeGeneratorAgent.
        Prefers codebase workspace for reading actual source code.
        Falls back to active workspace if codebase workspace not available.
        """
        if not file_path:
            return {"success": False, "error": "file_path is required"}

        manager = self._get_workspace_manager()
        if not manager:
            return {"success": False, "error": "WorkspaceManager not available"}

        # Prefer codebase workspace for reading source files
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
            # If codebase workspace failed, try active workspace as fallback
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

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for research."""

        if tool_name == "web_search":
            # Session 1090: Deprecated — fall through to BaseAgent universal handler
            logger.warning(f"[{self.__class__.__name__}] web_search is deprecated — falling through to BaseAgent handler")
            return super()._execute_tool_call(tool_name, arguments)

        elif tool_name == "spider_query":
            try:
                results = self.spider_service.search_spider_data(
                    query=arguments.get('query', ''),
                    category=arguments.get('category'),
                    hours=arguments.get('hours', 72),
                    limit=arguments.get('limit', 20)
                )
                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Spider query failed: {str(e)}"
                }

        elif tool_name == "analyze_trends":
            try:
                category = arguments.get('category', 'all')
                hours = arguments.get('hours', 24)
                limit = arguments.get('limit', 10)
                # Session 272: Extract topic filter from arguments or query
                topic_filter = arguments.get('topic_filter')

                if category == 'tech':
                    # Session 274: Exclude ProductHunt from research (shown separately in Trending Now cards)
                    results = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter=topic_filter, include_producthunt=False)
                elif category == 'creative':
                    # Session 272: For design queries, use get_tech_trends with design filter
                    # since it has topic filtering logic; fallback to creative_trends otherwise
                    # Session 957: Added '3d' topic filter for 3D design/modeling content
                    if topic_filter in ('design', '3d'):
                        # Session 274: Exclude ProductHunt from research
                        results = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter=topic_filter, include_producthunt=False)
                    else:
                        results = self.spider_service.get_creative_trends(hours=hours, limit=limit)
                elif category == 'jobs':
                    results = self.spider_service.get_job_market_summary(hours=hours, limit=limit)
                elif category == 'financial':
                    results = self.spider_service.get_market_insights()
                else:
                    # Session 272: For 'all' category, get trending topics AND tech discussions
                    # This provides both topic summaries AND clickable article links
                    # Session 274: Exclude ProductHunt from research (shown separately in Trending Now cards)
                    trending_topics = self.spider_service.get_trending_topics(hours=hours, limit=limit)
                    tech_trends = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter=topic_filter, include_producthunt=False)

                    results = {
                        'topics': trending_topics,
                        'discussions': tech_trends.get('discussions', []),
                        'projects': tech_trends.get('projects', []),  # Now only GitHub, no ProductHunt
                        'sources': tech_trends.get('sources', {}),
                        'last_updated': tech_trends.get('last_updated')
                    }

                return {
                    'success': True,
                    'data': results
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Trend analysis failed: {str(e)}"
                }

        elif tool_name == "reddit_search":
            # Session 312: Dynamic Reddit search for ANY subreddit
            return self._reddit_dynamic_search(
                query=arguments.get('query', ''),
                subreddits=arguments.get('subreddits', 'all'),
                limit=arguments.get('limit', 25),
                sort=arguments.get('sort', 'relevance'),
                time_filter=arguments.get('time_filter', 'month')
            )

        elif tool_name == "query_internal_data":
            # Session 884: Query internal DonkeyBetz database
            return self._query_internal_data(
                data_type=arguments.get('data_type', ''),
                filter_type=arguments.get('filter', 'recent'),
                limit=arguments.get('limit', 20),
                days_back=arguments.get('days_back', 7),
                include_details=arguments.get('include_details', True)
            )

        # Session 1028: Read-only codebase tools
        elif tool_name == "read_file":
            return self._read_file(file_path=arguments.get("file_path", ""))

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

        # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
        return super()._execute_tool_call(tool_name, arguments)

    def _reddit_dynamic_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25,
        sort: str = 'relevance',
        time_filter: str = 'month'
    ) -> Dict[str, Any]:
        """
        Session 312: Dynamic Reddit search for ANY subreddit.

        First tries the registered RedditSearchTool (requires API credentials).
        Falls back to public JSON endpoint if credentials aren't configured.
        """
        try:
            # Try the registered RedditSearchTool first (uses PRAW with full API)
            from core.tools import ToolRegistry
            reddit_tool = ToolRegistry.get_tool('reddit_api')

            if reddit_tool and reddit_tool.is_configured:
                logger.info(f"Using RedditSearchTool for: {query} in r/{subreddits}")
                result = reddit_tool.execute(
                    query=query,
                    search_type='posts',
                    subreddit=subreddits,
                    limit=limit,
                    sort=sort,
                    time_filter=time_filter
                )
                if result.get('success'):
                    return result

            # Fallback: Use public JSON endpoint (no auth required)
            logger.info(f"Using public Reddit JSON for: {query} in r/{subreddits}")
            return self._reddit_public_json_search(query, subreddits, limit)

        except Exception as e:
            logger.error(f"Reddit dynamic search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }

    def _reddit_public_json_search(
        self,
        query: str,
        subreddits: str = 'all',
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Session 312: Fallback Reddit search using public JSON endpoints.
        Works without API credentials.
        """
        import requests
        from datetime import datetime

        try:
            headers = {
                'User-Agent': 'DonkeyBetz-Research/1.0 (AI Content Studio; Educational Research)'
            }

            url = f"https://www.reddit.com/r/{subreddits}/search.json"
            params = {
                'q': query,
                'limit': min(limit, 100),
                'restrict_sr': 'true' if subreddits != 'all' else 'false',
                'sort': 'relevance',
                't': 'month'
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                results = []
                for post in posts:
                    post_data = post.get('data', {})
                    results.append({
                        'id': post_data.get('id', ''),
                        'title': post_data.get('title', ''),
                        'selftext': post_data.get('selftext', '')[:500],
                        'subreddit': post_data.get('subreddit', ''),
                        'url': f"https://reddit.com{post_data.get('permalink', '')}",
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': datetime.fromtimestamp(
                            post_data.get('created_utc', 0)
                        ).isoformat() if post_data.get('created_utc') else None,
                        'author': post_data.get('author', '[deleted]'),
                    })

                logger.info(f"Public Reddit search returned {len(results)} results")

                return {
                    'success': True,
                    'data': {
                        'query': query,
                        'subreddit': subreddits,
                        'results': results,
                        'total_results': len(results),
                        'source': 'reddit_public_json',
                        'timestamp': datetime.now().isoformat()
                    }
                }

            elif response.status_code == 429:
                return {
                    'success': False,
                    'error': "Reddit rate limit reached. Try again in a few minutes."
                }
            else:
                return {
                    'success': False,
                    'error': f"Reddit returned status {response.status_code}"
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': "Reddit search timed out"
            }
        except Exception as e:
            logger.error(f"Public Reddit JSON search failed: {e}")
            return {
                'success': False,
                'error': f"Reddit search failed: {str(e)}"
            }

    # =========================================================================
    # Session 884: Internal Data Query Tool
    # =========================================================================

    def _query_internal_data(
        self,
        data_type: str,
        filter_type: str = 'recent',
        limit: int = 20,
        days_back: int = 7,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Session 884: Query internal DonkeyBetz database.

        This enables ResearchAgent to analyze internal system data like
        experiments, agent executions, initiatives, etc. without asking
        for external data exports.

        Args:
            data_type: Type of data to query (experiments, agent_executions, etc.)
            filter_type: Filter to apply (failed, halted, recent, all, blocked, active)
            limit: Max records to return
            days_back: For 'recent' filter, how many days to look back
            include_details: Include full details vs summary

        Returns:
            Dict with success status and queried data
        """
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Avg, Q

        try:
            now = timezone.now()
            recent_cutoff = now - timedelta(days=days_back)
            results = []
            summary = {}

            if data_type == 'experiments':
                from core.models import Experiment

                # Build query based on filter
                queryset = Experiment.objects.all()

                if filter_type == 'failed':
                    queryset = queryset.filter(status='failure')
                elif filter_type == 'halted':
                    queryset = queryset.filter(is_halted=True)
                elif filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)
                elif filter_type == 'active':
                    queryset = queryset.filter(status='running')

                queryset = queryset.order_by('-created_at')[:limit]

                # Get summary stats
                all_experiments = Experiment.objects.all()
                status_counts = dict(all_experiments.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count'))

                summary = {
                    'total_experiments': all_experiments.count(),
                    'status_distribution': status_counts,
                    'halted_count': all_experiments.filter(is_halted=True).count(),
                    'failure_rate': f"{(status_counts.get('failure', 0) / max(all_experiments.count(), 1)) * 100:.1f}%",
                }

                for exp in queryset:
                    record = {
                        'id': str(exp.id),
                        'name': exp.name,
                        'status': exp.status,
                        'is_halted': exp.is_halted,
                        'created_at': exp.created_at.isoformat() if exp.created_at else None,
                    }
                    if include_details:
                        record.update({
                            'hypothesis': exp.hypothesis[:500] if exp.hypothesis else None,
                            'halt_reason': exp.halt_reason[:300] if exp.halt_reason else None,
                            'halted_by': exp.halted_by,
                            'result_summary': exp.result_summary[:500] if exp.result_summary else None,
                            'learnings': exp.learnings[:500] if exp.learnings else None,
                            'primary_kpi': exp.primary_kpi,
                        })
                    results.append(record)

            elif data_type == 'agent_executions':
                from core.models import AgentExecution

                queryset = AgentExecution.objects.select_related('agent')

                if filter_type == 'failed':
                    queryset = queryset.filter(status='failed')
                elif filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)

                queryset = queryset.order_by('-created_at')[:limit]

                # Summary stats
                all_executions = AgentExecution.objects.all()
                status_counts = dict(all_executions.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count'))

                summary = {
                    'total_executions': all_executions.count(),
                    'status_distribution': status_counts,
                    'failure_rate': f"{(status_counts.get('failed', 0) / max(all_executions.count(), 1)) * 100:.1f}%",
                    'avg_execution_time_ms': all_executions.aggregate(
                        avg=Avg('execution_time_ms')
                    )['avg'] or 0,
                }

                for exec_record in queryset:
                    record = {
                        'id': str(exec_record.id),
                        'agent_name': exec_record.agent.name if exec_record.agent else 'Unknown',
                        'status': exec_record.status,
                        'execution_time_ms': exec_record.execution_time_ms,
                        'created_at': exec_record.created_at.isoformat() if exec_record.created_at else None,
                    }
                    if include_details:
                        record.update({
                            'task': exec_record.task[:300] if exec_record.task else None,
                            'error_message': exec_record.error_message[:500] if exec_record.error_message else None,
                            'tokens_used': exec_record.tokens_used,
                        })
                    results.append(record)

            elif data_type == 'initiatives':
                from core.models_document_registry import Initiative

                queryset = Initiative.objects.all()

                # Session 923: Fix - Initiative model has status field, not blocked field
                if filter_type == 'blocked':
                    queryset = queryset.filter(status='BLOCKED')
                elif filter_type == 'active':
                    queryset = queryset.filter(status='ACTIVE')
                elif filter_type == 'stalled':
                    # Stalled = active but no updates in 7+ days
                    queryset = queryset.filter(status='ACTIVE', updated_at__lte=recent_cutoff)
                elif filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)

                queryset = queryset.order_by('-updated_at')[:limit]

                all_initiatives = Initiative.objects.all()
                summary = {
                    'total_initiatives': all_initiatives.count(),
                    'active_count': all_initiatives.filter(status='ACTIVE').count(),
                    'blocked_count': all_initiatives.filter(status='BLOCKED').count(),
                    'completed_count': all_initiatives.filter(status='COMPLETED').count(),
                    'archived_count': all_initiatives.filter(status='ARCHIVED').count(),
                }

                for init in queryset:
                    record = {
                        'id': str(init.id),
                        'name': init.name[:200],
                        'status': init.status,
                        'current_stage': init.current_stage,
                        'completion_percentage': init.completion_percentage,
                        'updated_at': init.updated_at.isoformat() if init.updated_at else None,
                    }
                    if include_details:
                        # Session 923: Fixed - 'blocked' is not a field, use status
                        record.update({
                            'parent_topic': init.parent_topic[:200] if init.parent_topic else None,
                            'is_blocked': init.status == 'BLOCKED',
                            'program': init.program,
                            'purpose': init.purpose,
                        })
                    results.append(record)

            elif data_type == 'agent_learnings':
                from core.models_unified_system import AgentLearning

                queryset = AgentLearning.objects.all()

                if filter_type == 'failed':
                    queryset = queryset.filter(learning_type='failure_pattern')
                elif filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)

                queryset = queryset.order_by('-created_at')[:limit]

                all_learnings = AgentLearning.objects.all()
                type_counts = dict(all_learnings.values('learning_type').annotate(
                    count=Count('id')
                ).values_list('learning_type', 'count'))

                summary = {
                    'total_learnings': all_learnings.count(),
                    'type_distribution': type_counts,
                    'applied_count': all_learnings.filter(applied=True).count(),
                }

                for learning in queryset:
                    record = {
                        'id': str(learning.id),
                        'agent_name': learning.agent_name,
                        'learning_type': learning.learning_type,
                        'confidence': learning.confidence,
                        'applied': learning.applied,
                        'created_at': learning.created_at.isoformat() if learning.created_at else None,
                    }
                    if include_details:
                        record['description'] = learning.description[:500] if learning.description else None
                    results.append(record)

            elif data_type == 'deliverables':
                from core.models_deliverables import Deliverable

                queryset = Deliverable.objects.all()

                if filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)

                queryset = queryset.order_by('-created_at')[:limit]

                all_deliverables = Deliverable.objects.all()
                summary = {
                    'total_deliverables': all_deliverables.count(),
                    'with_initiative': all_deliverables.filter(initiative__isnull=False).count(),
                }

                for deliv in queryset:
                    record = {
                        'id': str(deliv.id),
                        'title': deliv.title[:200] if deliv.title else None,
                        'deliverable_type': deliv.deliverable_type,
                        'status': deliv.status,
                        'created_at': deliv.created_at.isoformat() if deliv.created_at else None,
                    }
                    if include_details and deliv.initiative:
                        record['initiative_name'] = deliv.initiative.name[:100]
                    results.append(record)

            elif data_type == 'spider_data_stats':
                from core.models import SpiderData

                # Get aggregated stats rather than individual records
                recent_data = SpiderData.objects.filter(created_at__gte=recent_cutoff)

                spider_counts = dict(recent_data.values('spider_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:20].values_list('spider_name', 'count'))

                summary = {
                    'total_records': SpiderData.objects.count(),
                    'records_last_n_days': recent_data.count(),
                    'days_queried': days_back,
                    'spider_activity': spider_counts,
                    'active_spiders': len(spider_counts),
                }

                # Return top spiders as results
                for spider_name, count in spider_counts.items():
                    results.append({
                        'spider_name': spider_name,
                        'record_count': count,
                        'period': f'last {days_back} days',
                    })

            elif data_type == 'decision_records':
                from core.models_decision_records import DecisionRecord

                queryset = DecisionRecord.objects.all()

                if filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)
                elif filter_type == 'failed':
                    queryset = queryset.filter(was_successful=False)

                queryset = queryset.order_by('-created_at')[:limit]

                all_decisions = DecisionRecord.objects.all()
                success_counts = {
                    'successful': all_decisions.filter(was_successful=True).count(),
                    'failed': all_decisions.filter(was_successful=False).count(),
                    'unknown': all_decisions.filter(was_successful__isnull=True).count(),
                }
                type_counts = dict(all_decisions.values('decision_type').annotate(
                    count=Count('id')
                ).values_list('decision_type', 'count'))

                summary = {
                    'total_decisions': all_decisions.count(),
                    'success_distribution': success_counts,
                    'type_distribution': type_counts,
                }

                for decision in queryset:
                    record = {
                        'id': str(decision.id),
                        'agent_name': decision.agent_name,
                        'decision_type': decision.decision_type,
                        'action': decision.action[:200] if decision.action else None,
                        'was_successful': decision.was_successful,
                        'created_at': decision.created_at.isoformat() if decision.created_at else None,
                    }
                    if include_details:
                        record['reasoning'] = decision.reasoning[:500] if decision.reasoning else None
                        record['outcome_notes'] = decision.outcome_notes[:300] if decision.outcome_notes else None
                    results.append(record)

            elif data_type == 'agents':
                # Session 990: Support querying agent registry
                from core.models_unified_system import Agent

                queryset = Agent.objects.all()

                if filter_type == 'active':
                    queryset = queryset.filter(is_active=True)
                elif filter_type == 'recent':
                    queryset = queryset.filter(created_at__gte=recent_cutoff)

                queryset = queryset.order_by('name')[:limit]

                all_agents = Agent.objects.all()
                summary = {
                    'total_agents': all_agents.count(),
                    'active_count': all_agents.filter(is_active=True).count(),
                }

                for agent in queryset:
                    record = {
                        'id': str(agent.id),
                        'name': agent.name,
                        'is_active': agent.is_active,
                    }
                    if include_details:
                        record['description'] = (agent.description[:300] if agent.description else None)
                        record['agent_type'] = getattr(agent, 'agent_type', None)
                    results.append(record)

            else:
                return {
                    'success': False,
                    'error': f"Unknown data_type: {data_type}. Supported: experiments, agent_executions, initiatives, agent_learnings, deliverables, spider_data_stats, decision_records, agents"
                }

            logger.info(f"[Session 884] Internal data query: {data_type} filter={filter_type} returned {len(results)} records")

            return {
                'success': True,
                'data': {
                    'data_type': data_type,
                    'filter': filter_type,
                    'limit': limit,
                    'days_back': days_back,
                    'record_count': len(results),
                    'summary': summary,
                    'records': results,
                    'queried_at': now.isoformat(),
                }
            }

        except ImportError as e:
            logger.error(f"Import error querying internal data: {e}")
            return {
                'success': False,
                'error': f"Model not available: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error querying internal data: {e}")
            return {
                'success': False,
                'error': f"Internal data query failed: {str(e)}"
            }
