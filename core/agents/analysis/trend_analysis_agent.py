"""
Trend Analysis Agent - Clean Architecture
==========================================

Session 280: Phase 3 - Agent Architecture Unification
Session 683: Added ML Integration (LSTM/Prophet for trend forecasting)

This agent provides intelligent trend analysis by analyzing patterns
across all spider data and generating actionable insights.

Tools Available:
    - generate_briefing: Generate daily or weekly intelligence briefings
    - analyze_sector: Analyze trends for a specific sector
    - find_opportunities: Find emerging opportunities from trends

Usage:
    from core.agents.analysis import TrendAnalysisAgent

    agent = TrendAnalysisAgent(user=request.user)
    result = agent.execute(
        task="Generate a daily intelligence briefing",
        context={},
        scifi_context={},
        spider_context={}
    )
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone as dt_timezone
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.report_schemas import build_provenance, format_disclaimer
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


@dataclass
class TrendReport:
    """Result from trend analysis."""
    success: bool
    report_type: str  # 'daily', 'weekly', 'sector', 'opportunity'
    generated_at: datetime
    period_start: datetime
    period_end: datetime

    # Core analysis
    top_trends: List[Dict[str, Any]] = field(default_factory=list)
    emerging_topics: List[Dict[str, Any]] = field(default_factory=list)
    declining_topics: List[Dict[str, Any]] = field(default_factory=list)

    # Sector breakdowns
    tech_highlights: List[str] = field(default_factory=list)
    market_highlights: List[str] = field(default_factory=list)
    job_highlights: List[str] = field(default_factory=list)

    # Opportunities
    opportunities: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    data_sources: List[str] = field(default_factory=list)
    total_data_points: int = 0
    confidence_score: float = 0.0

    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'report_type': self.report_type,
            'generated_at': self.generated_at.isoformat(),
            'period': {
                'start': self.period_start.isoformat(),
                'end': self.period_end.isoformat(),
            },
            'top_trends': self.top_trends,
            'emerging_topics': self.emerging_topics,
            'declining_topics': self.declining_topics,
            'highlights': {
                'tech': self.tech_highlights,
                'market': self.market_highlights,
                'jobs': self.job_highlights,
            },
            'opportunities': self.opportunities,
            'metadata': {
                'data_sources': self.data_sources,
                'total_data_points': self.total_data_points,
                'confidence_score': self.confidence_score,
            },
            'error': self.error,
        }


class TrendAnalysisAgent(BaseAgent):
    """
    Trend Analysis Agent - Spider Intelligence Analyst.

    This agent:
    1. Generates daily/weekly intelligence briefings
    2. Analyzes trends for specific sectors
    3. Identifies emerging opportunities

    It CANNOT:
    - Create content
    - Execute workflows
    """

    name = "TrendAnalysisAgent"
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution

    system_prompt = """You are TrendAnalysisAgent, the Spider Intelligence Analyst.

Your job is to transform raw spider data into actionable intelligence:
- Search for trends relevant to specific business ideas or topics
- Generate daily and weekly trend reports
- Analyze specific sectors (tech, financial, jobs, creative)
- Identify emerging opportunities and market signals

CRITICAL: When given a business idea or specific topic to analyze:
1. ALWAYS use search_trends FIRST with the business idea as the query
2. Extract key themes: gig economy, van life, mobile services, etc.
3. Look for relevant discussions and market signals

When given a general request:
1. Determine the type of analysis needed
2. Use appropriate tools (generate_briefing, analyze_sector, find_opportunities)
3. Present findings with confidence scores

Available tools:
- search_trends: USE FIRST for specific business ideas/topics - searches spider data semantically
- generate_briefing: General daily/weekly intelligence briefings
- analyze_sector: Deep dive into tech/financial/jobs/creative sectors
- find_opportunities: Find emerging opportunities from trends

You analyze and report - you do NOT create content or execute workflows."""

    tools = [
        # Session 349: Primary tool for query-specific trend analysis
        {
            "type": "function",
            "function": {
                "name": "search_trends",
                "description": "Search for trends relevant to a specific business idea, market, or topic. USE THIS FIRST when given a business idea to analyze.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The business idea, market, or topic to find trends for (e.g., 'van life gig economy app', 'AI podcast tools', 'mobile handyman services')"
                        },
                        "categories": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["tech", "jobs", "financial", "creative", "news", "community"]
                            },
                            "description": "Categories to search (defaults to all relevant)",
                            "default": []
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_briefing",
                "description": "Generate a general intelligence briefing (daily or weekly) - use search_trends instead for specific business ideas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "briefing_type": {
                            "type": "string",
                            "description": "Type of briefing",
                            "enum": ["daily", "weekly"]
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_sector",
                "description": "Analyze trends for a specific sector",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sector": {
                            "type": "string",
                            "description": "Sector to analyze",
                            "enum": ["tech", "financial", "jobs", "creative"]
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to analyze",
                            "default": 7
                        }
                    },
                    "required": ["sector"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_opportunities",
                "description": "Find emerging opportunities from trends",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hours": {
                            "type": "integer",
                            "description": "Look back period in hours",
                            "default": 24
                        }
                    },
                    "required": []
                }
            }
        }
    ]

    # Opportunity detection keywords
    OPPORTUNITY_KEYWORDS = {
        'tech': ['new framework', 'breakthrough', 'launch', 'release', 'announced'],
        'market': ['surge', 'rally', 'breakout', 'all-time high', 'opportunity'],
        'jobs': ['hiring', 'remote', 'high salary', 'urgent', 'multiple positions'],
        'content': ['viral', 'trending', 'popular', 'featured'],
    }

    def __init__(self, user=None):
        """Initialize TrendAnalysisAgent."""
        super().__init__(user=user)
        self._intelligence_service = None
        self._semantic_search = None

    @property
    def intelligence_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._intelligence_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._intelligence_service = SpiderIntelligenceService()
        return self._intelligence_service

    @property
    def semantic_search(self):
        """Session 349: Lazy load Spider Semantic Search for query-specific trends."""
        if self._semantic_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._semantic_search = get_spider_semantic_search()
        return self._semantic_search

    # === Session 683: ML Integration Methods ===

    def _analyze_trends_with_ml(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Analyze trend data using ML models (LSTM/Prophet).

        Uses the Agent-Model Router to automatically select optimal models
        for trend forecasting and pattern detection.

        Args:
            trend_data: List of trend data points with timestamps and values

        Returns:
            Dict with ML analysis results including predictions and confidence
        """
        try:
            from core.services.agent_model_router import get_agent_model_router

            router = get_agent_model_router()

            # Build time series data from trends
            time_series_data = self._build_trend_time_series(trend_data)

            if not time_series_data.get('values'):
                return {
                    'ml_used': False,
                    'reason': 'Insufficient trend data for ML analysis'
                }

            # Route to optimal ML model (LSTM/Prophet for time series)
            result = router.auto_route(
                data=time_series_data,
                task_hint=TaskType.TIME_SERIES,
                max_models=2
            )

            return {
                'ml_used': True,
                'task_type': result.auto_selection.get('task_type', 'time_series'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'ml_insights': result.explanation,
                'prediction': result.prediction if hasattr(result, 'prediction') else None,
                'trend_direction': self._determine_trend_direction(result),
                'selection_reason': result.auto_selection.get('selection_reason', ''),
            }

        except Exception as e:
            logger.warning(f"ML analysis failed for trends: {e}")
            return {
                'ml_used': False,
                'reason': f'ML error: {str(e)}'
            }

    def _build_trend_time_series(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Session 683: Build time series data structure from trend data.

        Converts trend mentions/scores over time into ML-compatible format.

        Args:
            trend_data: List of trends with mentions, scores, timestamps

        Returns:
            Time series data dict for ML routing
        """
        if not trend_data:
            return {'timestamps': [], 'values': []}

        timestamps = []
        values = []

        for trend in trend_data:
            # Extract timestamp (may be in different formats)
            ts = trend.get('timestamp') or trend.get('created_at') or trend.get('date')
            if ts:
                if isinstance(ts, str):
                    try:
                        from dateutil import parser
                        ts = parser.parse(ts)
                    except Exception:
                        continue
                timestamps.append(ts.isoformat() if hasattr(ts, 'isoformat') else str(ts))

            # Extract value (mentions, score, or count)
            value = trend.get('mentions') or trend.get('score') or trend.get('count') or 1
            values.append(float(value))

        # If no timestamps, create synthetic ones based on position
        if not timestamps and values:
            from datetime import datetime, timedelta
            now = datetime.now()
            timestamps = [(now - timedelta(hours=i)).isoformat() for i in range(len(values), 0, -1)]

        return {
            'timestamps': timestamps,
            'values': values,
            'data_type': 'trend_mentions'
        }

    def _determine_trend_direction(self, ml_result) -> str:
        """
        Session 683: Determine overall trend direction from ML prediction.

        Args:
            ml_result: EnsemblePrediction from ML router

        Returns:
            String indicating trend direction: 'rising', 'falling', 'stable'
        """
        try:
            if hasattr(ml_result, 'prediction') and ml_result.prediction:
                pred = ml_result.prediction
                if isinstance(pred, (list, tuple)) and len(pred) >= 2:
                    # Compare last predicted vs first
                    if pred[-1] > pred[0] * 1.05:
                        return 'rising'
                    elif pred[-1] < pred[0] * 0.95:
                        return 'falling'
            return 'stable'
        except Exception:
            return 'unknown'

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute trend analysis based on the task."""
        start_time = time.time()
        tool_calls_made = []

        # Search strategy now handled universally by BaseAgent._enhance_task_with_queries()

        # Session 736: Extract spider intelligence for real-time data
        spider_intel = self._extract_spider_intelligence(spider_context)
        if spider_intel['has_data']:
            logger.info(f"🕷️ {self.name} using spider intelligence")

        with self.time_travel_session("trend_analysis", task, input_data=context):
            try:
                if not self._validate_task(task):
                    return AgentResult(
                        success=False,
                        error="Invalid or empty task",
                        agent_name=self.name
                    )

                self.record_decision(
                    decision_type="task_analysis",
                    action="Analyzing trend analysis request",
                    reasoning=f"Received task: {task[:100]}",
                    alternatives=["generate_briefing", "analyze_sector", "find_opportunities"],
                    confidence=0.9
                )

                full_prompt = self._build_intelligent_prompt(task, scifi_context, spider_context)
                logger.info(f"TrendAnalysisAgent executing: {task[:50]}...")

                gpt_response = self._call_openai(full_prompt)

                if gpt_response.get('tool_calls'):
                    for tool_call in gpt_response['tool_calls']:
                        tool_name = tool_call['name']
                        arguments = tool_call['arguments']

                        self.record_decision(
                            decision_type="tool_selection",
                            action=f"Calling {tool_name}",
                            reasoning=f"Analysis operation: {arguments}",
                            alternatives=[],
                            confidence=0.95
                        )

                        tool_result = self._execute_tool_call(tool_name, arguments)
                        tool_calls_made.append({
                            'tool': tool_name,
                            'arguments': arguments,
                            'result': tool_result
                        })

                        self.mark_decision_outcome(
                            success=tool_result.get('success', False),
                            result_summary=str(tool_result)[:100]
                        )

                    execution_time = int((time.time() - start_time) * 1000)

                    # Session 953: Build provenance from analysis results
                    sources = []
                    for tc in tool_calls_made:
                        sources.append({
                            'name': tc.get('tool', 'trend_analysis'),
                            'endpoint': 'spider_intelligence',
                            'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                            'record_count': 1,
                        })
                    if not sources:
                        sources = [{
                            'name': 'trend_analysis',
                            'endpoint': 'spider_intelligence',
                            'retrieved_at': datetime.now(dt_timezone.utc).isoformat(),
                            'record_count': 0,
                        }]
                    provenance = build_provenance(
                        report_type='analysis',
                        agent_name=self.name,
                        sources=sources,
                        stale_threshold_hours=24.0,
                    )
                    provenance.disclaimer = format_disclaimer('analysis')
                    provenance_block = provenance.to_markdown_block()

                    result = AgentResult(
                        success=True,
                        message=provenance_block + "\n\nTrend analysis completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                            'provenance': provenance.to_dict(),
                            'publishable': provenance.publishable,
                            'validation_status': provenance.validation_status,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                    # Session 861: Persist analysis to Deliverable
                    analysis_content = f"# Trend Analysis\n\n**Task:** {task}\n\n**Results:**\n"
                    for tc in tool_calls_made:
                        analysis_content += f"\n## {tc.get('tool', 'Tool')}\n{tc.get('result', {})}\n"
                    self._save_to_deliverable(
                        title=f"Trend Analysis: {task[:50]}",
                        content=analysis_content,
                        deliverable_type='analysis',
                        category='Analysis',
                        tags=['trends', 'analysis', 'intelligence'],
                        content_format='markdown',
                        metadata={
                            'task': task,
                            'tool_count': len(tool_calls_made),
                            'execution_time_ms': execution_time,
                        },
                    )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.7
                    )

                    return result

                else:
                    content = gpt_response.get('content', '')
                    result = AgentResult(
                        success=True,
                        message=content,
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

                    # Session 861: Persist conversational analysis to Deliverable
                    if content:
                        self._save_to_deliverable(
                            title=f"Trend Analysis: {task[:50]}",
                            content=content,
                            deliverable_type='analysis',
                            category='Analysis',
                            tags=['trends', 'analysis'],
                            content_format='markdown',
                            metadata={'task': task},
                        )

                    # Session 380: Learning hooks for collective intelligence
                    self._record_learning_outcome(
                        result=result,
                        task=task,
                        context=context,
                        spider_data_used=bool(spider_context),
                        scifi_context_used=bool(scifi_context)
                    )
                    self._create_execution_memory(
                        result=result,
                        task=task,
                        memory_type="success",
                        importance=0.6
                    )

                    return result

            except Exception as e:
                logger.error(f"TrendAnalysisAgent error: {e}")
                result = AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

                # Session 380: Learning hooks for collective intelligence (failures too)
                self._record_learning_outcome(
                    result=result,
                    task=task,
                    context=context,
                    spider_data_used=bool(spider_context),
                    scifi_context_used=bool(scifi_context)
                )
                self._create_execution_memory(
                    result=result,
                    task=task,
                    memory_type="failure",
                    importance=0.8
                )

                return result

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a trend analysis tool call."""
        # Session 349: Added search_trends as primary tool for business idea analysis
        if tool_name == "search_trends":
            return self._search_trends(
                query=arguments.get('query', ''),
                categories=arguments.get('categories', [])
            )

        elif tool_name == "generate_briefing":
            return self._generate_briefing(
                briefing_type=arguments.get('briefing_type', 'daily')
            )

        elif tool_name == "analyze_sector":
            return self._analyze_sector(
                sector=arguments.get('sector', 'tech'),
                days=arguments.get('days', 7)
            )

        elif tool_name == "find_opportunities":
            return self._find_opportunities(
                hours=arguments.get('hours', 24)
            )

        return super()._execute_tool_call(tool_name, arguments)

    def _search_trends(self, query: str, categories: List[str] = None) -> Dict[str, Any]:
        """
        Session 349: Search for trends relevant to a specific business idea.

        Uses semantic search across spider data to find relevant trends,
        discussions, and market signals for the given query.
        """
        logger.info(f"Searching trends for: {query[:50]}...")

        try:
            pass

            # Search spider data semantically
            results = self.semantic_search.semantic_search(
                query=query,
                category=categories[0] if categories else None,
                hours=168,  # Last 7 days
                limit=25,
                min_similarity=0.3
            )

            if not results:
                # Fallback to general trending topics
                logger.info("No semantic results, falling back to general trends")
                trends = self.intelligence_service.get_trending_topics(hours=168, limit=15)
                return {
                    'success': True,
                    'query': query,
                    'trends': trends[:10] if trends else [],
                    'discussions': [],
                    'sources': [],
                    'data_points': 0,
                    'note': 'No specific matches found, showing general trends'
                }

            # Process results into trend insights
            trends = []
            discussions = []
            sources_used = set()

            for item in results:
                sources_used.add(item.source)

                discussion = {
                    'title': item.title,
                    'description': item.description[:300] if item.description else '',
                    'url': item.url,
                    'source': item.source,
                    'category': item.category,
                    'similarity': round(item.similarity, 2) if hasattr(item, 'similarity') else 0.5
                }
                discussions.append(discussion)

                # Extract trend topics from titles
                if item.title:
                    trends.append({
                        'topic': item.title[:100],
                        'source': item.source,
                        'relevance': discussion['similarity']
                    })

            # Also get general market context
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=72, limit=5)

            return {
                'success': True,
                'query': query,
                'trends': trends[:15],
                'discussions': discussions[:20],
                'sources': list(sources_used),
                'data_points': len(results),
                'market_context': {
                    'crypto_highlights': [
                        f"{c.get('name')}: ${c.get('price', 0):,.2f} ({c.get('change_24h', 0):+.1f}%)"
                        for c in (market.get('crypto', []) if market else [])[:3]
                    ],
                    'tech_highlights': [
                        d.get('title', '')[:80]
                        for d in (tech.get('discussions', []) if tech else [])[:3]
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Error searching trends: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def _generate_briefing(self, briefing_type: str) -> Dict[str, Any]:
        """Generate an intelligence briefing."""
        logger.info(f"Generating {briefing_type} briefing...")

        try:
            from django.utils import timezone
            now = timezone.now()

            if briefing_type == 'weekly':
                hours = 168  # 7 days
                period_start = now - timedelta(days=7)
            else:
                hours = 24
                period_start = now - timedelta(hours=24)

            # Gather intelligence
            trends = self.intelligence_service.get_trending_topics(hours=hours, limit=15)
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=hours, limit=10)
            jobs = self.intelligence_service.get_job_market_summary(hours=hours, limit=10)
            summary = self.intelligence_service.get_data_summary(hours=hours)

            # Session 683: Add ML analysis for trend forecasting
            ml_insights = self._analyze_trends_with_ml(trends) if trends else {}

            # Build report
            report = TrendReport(
                success=True,
                report_type=briefing_type,
                generated_at=now,
                period_start=period_start,
                period_end=now,
                top_trends=trends[:10] if trends else [],
                tech_highlights=self._build_tech_highlights(tech),
                market_highlights=self._build_market_highlights(market),
                job_highlights=self._build_job_highlights(jobs),
                data_sources=list(summary.get('by_spider', {}).keys()) if summary else [],
                total_data_points=summary.get('total_items', 0) if summary else 0,
                confidence_score=min(1.0, (summary.get('total_items', 0) if summary else 0) / 100),
            )

            result = {
                'success': True,
                'report': report.to_dict()
            }

            # Session 683: Add ML insights to result
            if ml_insights.get('ml_used'):
                result['ml_analysis'] = {
                    'models_used': ml_insights.get('models_used', []),
                    'confidence': ml_insights.get('confidence', 0),
                    'trend_direction': ml_insights.get('trend_direction', 'unknown'),
                    'ml_insights': ml_insights.get('ml_insights', ''),
                }

            return result

        except Exception as e:
            logger.error(f"Error generating briefing: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _analyze_sector(self, sector: str, days: int) -> Dict[str, Any]:
        """Analyze trends for a specific sector."""
        logger.info(f"Analyzing sector: {sector} for {days} days")

        try:
            from django.utils import timezone
            now = timezone.now()
            hours = days * 24

            trends = self.intelligence_service.get_trending_topics(
                category=sector, hours=hours, limit=20
            )
            summary = self.intelligence_service.get_data_summary(hours=hours)

            # Sector-specific data
            highlights = []
            if sector == 'tech':
                tech = self.intelligence_service.get_tech_trends(hours=hours, limit=15)
                highlights = self._build_tech_highlights(tech)
            elif sector == 'financial':
                market = self.intelligence_service.get_market_insights()
                highlights = self._build_market_highlights(market)
            elif sector == 'jobs':
                jobs = self.intelligence_service.get_job_market_summary(hours=hours, limit=15)
                highlights = self._build_job_highlights(jobs)

            return {
                'success': True,
                'sector': sector,
                'days_analyzed': days,
                'top_trends': trends[:15] if trends else [],
                'highlights': highlights,
                'data_sources': list(summary.get('by_spider', {}).keys()) if summary else [],
                'total_data_points': summary.get('total_items', 0) if summary else 0
            }

        except Exception as e:
            logger.error(f"Error analyzing sector: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _find_opportunities(self, hours: int) -> Dict[str, Any]:
        """Find emerging opportunities."""
        logger.info(f"Finding opportunities from last {hours} hours")

        try:
            trends = self.intelligence_service.get_trending_topics(hours=hours, limit=20)
            market = self.intelligence_service.get_market_insights()
            tech = self.intelligence_service.get_tech_trends(hours=hours)
            jobs = self.intelligence_service.get_job_market_summary(hours=hours)

            opportunities = []

            # Tech opportunities
            for discussion in (tech.get('discussions', []) if tech else [])[:5]:
                title = discussion.get('title', '')
                if any(kw in title.lower() for kw in self.OPPORTUNITY_KEYWORDS['tech']):
                    opportunities.append({
                        'type': 'tech',
                        'title': title[:100],
                        'description': f"Hot tech topic from {discussion.get('source', 'unknown')}",
                        'score': discussion.get('score', 0),
                    })

            # Market opportunities
            for crypto in (market.get('crypto', []) if market else [])[:5]:
                change = crypto.get('change_24h', 0) or 0
                if change > 5:
                    opportunities.append({
                        'type': 'market',
                        'title': f"{crypto.get('name', 'Unknown')} up {change:.1f}%",
                        'description': f"Current price: ${crypto.get('price', 0):,.2f}",
                        'change': change,
                    })

            # Trending topic opportunities
            for trend in (trends[:5] if trends else []):
                if trend.get('mentions', 0) >= 3:
                    opportunities.append({
                        'type': 'trend',
                        'title': f"Hot topic: {trend.get('topic', 'Unknown')}",
                        'description': f"{trend.get('mentions', 0)} mentions",
                    })

            return {
                'success': True,
                'opportunities': opportunities[:10],
                'total_found': len(opportunities)
            }

        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_tech_highlights(self, tech: Dict) -> List[str]:
        """Build tech highlight strings."""
        if not tech:
            return []
        highlights = []
        discussions = tech.get('discussions', [])
        for d in discussions[:5]:
            title = d.get('title', '')[:80]
            source = d.get('source', 'unknown')
            score = d.get('score', 0)
            highlights.append(f"{title} ({source}, {score} points)")
        return highlights

    def _build_market_highlights(self, market: Dict) -> List[str]:
        """Build market highlight strings."""
        if not market:
            return []
        highlights = []
        for crypto in market.get('crypto', [])[:5]:
            name = crypto.get('name', 'Unknown')
            price = crypto.get('price', 0)
            change = crypto.get('change_24h', 0) or 0
            direction = "+" if change >= 0 else ""
            highlights.append(f"{name}: ${price:,.2f} ({direction}{change:.1f}%)")
        return highlights

    def _build_job_highlights(self, jobs: Dict) -> List[str]:
        """Build job market highlight strings."""
        if not jobs:
            return []
        highlights = []
        total = jobs.get('total_found', 0)
        if total:
            highlights.append(f"Found {total} remote job opportunities")
        for job in jobs.get('jobs', [])[:3]:
            title = job.get('title', '')[:60]
            company = job.get('company', 'Unknown')
            highlights.append(f"{title} at {company}")
        return highlights

    def _validate_task(self, task: str) -> bool:
        """Validate the task is appropriate for trend analysis."""
        return bool(task and task.strip())
