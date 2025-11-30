"""
Trend Analysis Agent - Clean Architecture
==========================================

Session 280: Phase 3 - Agent Architecture Unification

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
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from core.agents.base_agent import BaseAgent, AgentResult

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

    system_prompt = """You are TrendAnalysisAgent, the Spider Intelligence Analyst.

Your job is to transform raw spider data into actionable intelligence:
- Generate daily and weekly trend reports
- Analyze specific sectors (tech, financial, jobs, creative)
- Identify emerging opportunities
- Detect market shifts and tech trends

When given a task:
1. Determine the type of analysis needed
2. Gather data from spider intelligence
3. Analyze patterns and generate insights
4. Present findings with confidence scores

Available analysis types:
- Daily Briefing: Last 24 hours of intelligence
- Weekly Report: 7-day trend analysis
- Sector Analysis: Deep dive into tech/financial/jobs/creative
- Opportunity Scan: Find emerging opportunities

You analyze and report - you do NOT create content or execute workflows."""

    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_briefing",
                "description": "Generate an intelligence briefing (daily or weekly)",
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

    @property
    def intelligence_service(self):
        """Lazy load SpiderIntelligenceService."""
        if self._intelligence_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._intelligence_service = SpiderIntelligenceService()
        return self._intelligence_service

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

                full_prompt = self._build_prompt(task, scifi_context, spider_context)
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

                    return AgentResult(
                        success=True,
                        message="Trend analysis completed",
                        data={
                            'task': task,
                            'tool_results': tool_calls_made,
                        },
                        agent_name=self.name,
                        execution_time_ms=execution_time,
                        decisions_made=self._tt_decision_count,
                        tool_calls=tool_calls_made
                    )

                else:
                    return AgentResult(
                        success=True,
                        message=gpt_response.get('content', ''),
                        data={'type': 'conversation'},
                        agent_name=self.name,
                        execution_time_ms=int((time.time() - start_time) * 1000)
                    )

            except Exception as e:
                logger.error(f"TrendAnalysisAgent error: {e}")
                return AgentResult(
                    success=False,
                    error=str(e),
                    agent_name=self.name,
                    execution_time_ms=int((time.time() - start_time) * 1000)
                )

    def _execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a trend analysis tool call."""
        if tool_name == "generate_briefing":
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

        else:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}"
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

            return {
                'success': True,
                'report': report.to_dict()
            }

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
