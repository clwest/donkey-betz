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

    system_prompt = """You are ResearchAgent, a specialist in finding and analyzing information.

Your ONLY job is to research topics and gather information. You do NOT create content.
You have these tools:
- web_search: Search the web for current information
- spider_query: Query cached spider data (70 spiders, but only 15 Reddit subreddits)
- reddit_search: Search ANY Reddit subreddit in real-time (use for specific communities!)
- analyze_trends: Analyze trending topics from spider data

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
1. Decide whether to use web search, spider query, reddit_search, or combination
2. For current events/news, prefer web_search
3. For trends/opportunities, prefer spider_query
4. For specific Reddit communities, use reddit_search
5. Synthesize findings into a clear summary

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
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information using Serper API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 20
                        },
                        "search_type": {
                            "type": "string",
                            "description": "Type of search",
                            "enum": ["search", "news", "images"],
                            "default": "search"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
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
                            "description": "Filter results to specific topic: 'ai' for AI/ML, 'web' for web dev, 'security' for cybersecurity, 'cloud' for cloud/devops, 'design' for UI/UX/graphic design",
                            "enum": ["ai", "web", "security", "cloud", "design"],
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

    @property
    def spider_service(self):
        """Lazy-load Spider Intelligence Service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

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

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'text'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'topics_detected': self._extract_topics_from_result(result),
                'sentiment': self._extract_sentiment_from_result(result),
                'selection_reason': result.auto_selection.get('selection_reason', ''),
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

        # Session 858: Extract user context for personalized research
        user_context = context.get('user', {})
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
                # Session 744: Pass execution context for delegation support
                execution_context = {
                    'spider_context': spider_context,
                    'scifi_context': scifi_context,
                    'task': task,
                }
                gpt_response = self._call_openai(full_prompt, execution_context=execution_context)

                if gpt_response.get('tool_calls'):
                    all_results = []
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Selected {tool_name} for research",
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
                                'data': tool_result.get('data', tool_result)
                            })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    if all_results:
                        # Session 683: Add ML text analysis to research results
                        ml_analysis = {}
                        all_result_data = []
                        for r in all_results:
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

                        result_data = {
                            'results': all_results,
                            'query': task,
                            'sources_count': len(all_results),
                            # Session 872: Include Research Contract
                            'contract': research_contract,
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
                        # Build a list of key findings from the results
                        key_insights = []
                        for r in all_results[:5]:  # Top 5 results
                            data = r.get('data', r)
                            if isinstance(data, dict):
                                # Try to get title or summary from the result
                                title = data.get('title') or data.get('headline') or data.get('query', '')
                                if title:
                                    key_insights.append(str(title)[:200])
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
                        result = AgentResult(
                            success=False,
                            error="Research returned no results",
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
            if any(r.get('data', {}).get('url') or r.get('source') for r in all_results):
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
        task_lower = task.lower()
        if 'comprehensive' in task_lower or 'detailed' in task_lower:
            min_items = 10
        elif 'quick' in task_lower or 'brief' in task_lower:
            min_items = 3
        else:
            min_items = 5

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
        if 'trend' in task_lower or 'analysis' in task_lower:
            # Check if we have time-series data
            has_temporal = any(
                'timestamp' in str(r) or 'date' in str(r) or 'time' in str(r)
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
                gaps.append("ExperimentExecution logs (core.models_experiment.ExperimentExecution)")

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
            if 'ExperimentExecution' in gap or 'log' in gap.lower():
                return f"Missing: {gap}"
            if 'time-series' in gap.lower() or 'temporal' in gap.lower():
                return f"Missing: {gap}"

        return f"Missing: {data_gaps[0]}"

    def _extract_partial_findings(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract partial findings when data is insufficient."""
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

        if ml_analysis.get('ml_insights'):
            findings['ml_observation'] = ml_analysis['ml_insights']

        return findings

    def _extract_findings(
        self,
        all_results: List[Dict[str, Any]],
        ml_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract complete findings from results."""
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

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool call for research."""

        if tool_name == "web_search":
            try:
                from core.tools.web_search import WebSearchTool
                search_tool = WebSearchTool()
                # Session 348: Fixed - method is 'execute' not 'search'
                results = search_tool.execute(
                    query=arguments.get('query', ''),
                    max_results=arguments.get('num_results', 10),
                    search_type=arguments.get('search_type', 'text')  # 'text' not 'search'
                )
                # execute() returns a dict with 'success' already
                return results
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Web search failed: {str(e)}"
                }

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
                    if topic_filter == 'design':
                        # Session 274: Exclude ProductHunt from research
                        results = self.spider_service.get_tech_trends(hours=hours, limit=limit, topic_filter='design', include_producthunt=False)
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

        elif tool_name == "delegate_to_specialist":
            # Session 744: Handle delegation to specialists
            return self._handle_delegate_to_specialist(
                specialist_agent=arguments.get('specialist_agent', ''),
                task=arguments.get('task', ''),
                context=arguments.get('context', ''),
                delegation_context=getattr(self, '_current_delegation_context', {})
            )

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}. ResearchAgent only supports research tools."
            }

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
