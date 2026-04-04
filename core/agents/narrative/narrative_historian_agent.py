"""
Session 471: Narrative Historian Agent

Tracks and catalogs narratives over time.
"What stories have people believed, and when?"
"""

import logging
from typing import Dict, Any, List
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def analyze_narrative_with_ml(narrative_data: dict) -> dict:
    """Analyze narrative patterns using ML models (Text)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use TEXT task type for narrative analysis
        result = router.auto_route(
            data=narrative_data,
            task_hint=TaskType.TEXT,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'text'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'narrative_patterns': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML narrative analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class NarrativeHistorianAgent(BaseAgent):
    """
    Tracks narratives over time and maintains historical context.

    Responsibilities:
    1. Catalog known narratives and their evolution
    2. Track narrative strength over time
    3. Identify historical patterns
    4. Provide context for current events
    """

    name = "NarrativeHistorianAgent"
    description = "Tracks and catalogs narratives over time, providing historical context"
    system_prompt = """You are the Narrative Historian Agent - an expert at tracking how stories and beliefs evolve over time.

Your role:
1. Catalog known narratives and their evolution
2. Track narrative strength over time
3. Identify historical patterns
4. Provide context for current events

You answer the question: "What stories have people believed, and when?"

You have access to:
- The narrative database showing tracked narratives
- Historical evidence for each narrative
- Pattern detection tools

When analyzing narratives, consider:
- How narratives emerge, grow dominant, and fade
- Historical parallels to current events
- The lifecycle of public beliefs
- Leading indicators of narrative shifts"""

    def __init__(self, user=None):
        super().__init__(user)
        self.tools = self._build_tools()

    def _build_tools(self) -> List[Dict[str, Any]]:
        """Build the tools available to this agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_narrative_history",
                    "description": "Get the history of a specific narrative over time",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative to analyze"
                            },
                            "days_back": {
                                "type": "integer",
                                "description": "How many days of history to retrieve",
                                "default": 30
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_similar_historical_narratives",
                    "description": "Find narratives from the past that are similar to current ones",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic or keywords to search for"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Domain to search in (politics, markets, tech, etc.)"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "catalog_new_narrative",
                    "description": "Catalog a newly detected narrative",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Short title for the narrative"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the narrative"
                            },
                            "domain": {
                                "type": "string",
                                "description": "Domain (politics, markets, tech, culture, geopolitics, crypto, climate, health)"
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords that indicate this narrative"
                            }
                        },
                        "required": ["title", "description", "domain"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_dominant_narratives",
                    "description": "Get currently dominant narratives by domain",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain to filter by (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of narratives to return",
                                "default": 10
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_narrative_evidence",
                    "description": "Add evidence to a narrative from spider data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative"
                            },
                            "excerpt": {
                                "type": "string",
                                "description": "Relevant text excerpt"
                            },
                            "source_url": {
                                "type": "string",
                                "description": "URL of the source"
                            },
                            "sentiment": {
                                "type": "string",
                                "enum": ["supports", "contradicts", "neutral"],
                                "description": "How this evidence relates to the narrative"
                            }
                        },
                        "required": ["narrative_id", "excerpt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_narrative_lifecycle",
                    "description": "Analyze where a narrative is in its lifecycle (emerging, dominant, fading, dead)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative"
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            }
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the LLM."""
        if tool_name == "get_narrative_history":
            return self._get_narrative_history(tool_input)
        elif tool_name == "find_similar_historical_narratives":
            return self._find_similar_narratives(tool_input)
        elif tool_name == "catalog_new_narrative":
            return self._catalog_new_narrative(tool_input)
        elif tool_name == "get_dominant_narratives":
            return self._get_dominant_narratives(tool_input)
        elif tool_name == "update_narrative_evidence":
            return self._update_narrative_evidence(tool_input)
        elif tool_name == "analyze_narrative_lifecycle":
            return self._analyze_narrative_lifecycle(tool_input)

        else:
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, tool_input)

    def _get_narrative_history(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get the history of a specific narrative."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence

        narrative_id = tool_input.get('narrative_id')
        days_back = tool_input.get('days_back', 30)

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        cutoff = timezone.now() - timedelta(days=days_back)

        # Get evidence over time
        evidence = NarrativeEvidence.objects.filter(
            narrative=narrative,
            created_at__gte=cutoff
        ).order_by('created_at')

        # Build timeline
        timeline = []
        for ev in evidence:
            timeline.append({
                'date': ev.created_at.isoformat(),
                'sentiment': ev.sentiment,
                'strength': float(ev.strength),
                'source': ev.source_title or ev.source_url[:50] if ev.source_url else 'Unknown'
            })

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'description': narrative.description,
            'status': narrative.status,
            'current_strength': float(narrative.confidence),
            'mention_count': narrative.mention_count,
            'first_detected': narrative.first_detected.isoformat(),
            'strength_history': narrative.strength_history[-30:] if narrative.strength_history else [],
            'recent_evidence': timeline[-20:]
        }

    def _find_similar_narratives(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Find narratives similar to the given topic."""
        from core.models_narrative_drift import Narrative

        topic = tool_input.get('topic', '')
        domain = tool_input.get('domain')

        # Search by keywords and title
        queryset = Narrative.objects.all()

        if domain:
            queryset = queryset.filter(domain=domain)

        # Simple keyword matching (could use embeddings in future)
        keywords = topic.lower().split()
        matches = []

        for narrative in queryset[:100]:
            score = 0
            narrative_text = f"{narrative.title} {narrative.description}".lower()

            for keyword in keywords:
                if keyword in narrative_text:
                    score += 1
                if narrative.keywords and keyword in [k.lower() for k in narrative.keywords]:
                    score += 2

            if score > 0:
                matches.append({
                    'id': str(narrative.id),
                    'title': narrative.title,
                    'status': narrative.status,
                    'domain': narrative.domain,
                    'relevance_score': score,
                    'mention_count': narrative.mention_count
                })

        # Sort by relevance
        matches.sort(key=lambda x: -x['relevance_score'])

        return {
            'query': topic,
            'domain_filter': domain,
            'matches': matches[:10]
        }

    def _catalog_new_narrative(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new narrative entry."""
        from core.models_narrative_drift import Narrative, NarrativeDomain

        title = tool_input.get('title')
        description = tool_input.get('description')
        domain = tool_input.get('domain', 'tech')
        keywords = tool_input.get('keywords', [])

        # Validate domain
        valid_domains = [choice[0] for choice in NarrativeDomain.choices]
        if domain not in valid_domains:
            domain = 'tech'

        # Check for duplicate
        existing = Narrative.objects.filter(title__iexact=title).first()
        if existing:
            return {
                'status': 'exists',
                'narrative_id': str(existing.id),
                'message': f"Narrative '{title}' already exists"
            }

        narrative = Narrative.objects.create(
            title=title,
            description=description,
            domain=domain,
            keywords=keywords,
            auto_detected=True
        )

        return {
            'status': 'created',
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'domain': narrative.domain
        }

    def _get_dominant_narratives(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get currently dominant narratives."""
        from core.models_narrative_drift import Narrative, NarrativeStatus

        domain = tool_input.get('domain')
        limit = tool_input.get('limit', 10)

        queryset = Narrative.objects.filter(
            status__in=[NarrativeStatus.DOMINANT, NarrativeStatus.SHIFTING]
        ).order_by('-mention_count', '-confidence')

        if domain:
            queryset = queryset.filter(domain=domain)

        narratives = []
        for n in queryset[:limit]:
            narratives.append({
                'id': str(n.id),
                'title': n.title,
                'domain': n.domain,
                'status': n.status,
                'confidence': float(n.confidence),
                'mention_count': n.mention_count,
                'last_mention': n.last_mention.isoformat() if n.last_mention else None
            })

        return {
            'domain_filter': domain,
            'count': len(narratives),
            'narratives': narratives
        }

    def _update_narrative_evidence(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Add evidence to a narrative."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence

        narrative_id = tool_input.get('narrative_id')
        excerpt = tool_input.get('excerpt')
        source_url = tool_input.get('source_url', '')
        sentiment = tool_input.get('sentiment', 'supports')

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        # Create evidence
        evidence = NarrativeEvidence.objects.create(
            narrative=narrative,
            excerpt=excerpt[:1000],
            source_url=source_url,
            sentiment=sentiment,
            strength=Decimal('0.6') if sentiment == 'supports' else Decimal('0.4')
        )

        # [SESSION 475] Add provenance tracking
        try:
            from core.services.provenance_tracker import create_narrative_evidence_provenance
            create_narrative_evidence_provenance(
                evidence_id=str(evidence.id),
                spider_data_provenance_id=None,  # Link to spider data if available
                narrative_id=str(narrative.id),
                evidence_strength=sentiment,
                metadata={'source_url': source_url, 'agent': 'NarrativeHistorianAgent'}
            )
        except Exception as prov_e:
            logger.warning(f"Failed to create evidence provenance: {prov_e}")

        # Update narrative stats
        narrative.mention_count += 1
        narrative.last_mention = timezone.now()
        if narrative.mention_count > narrative.peak_mentions:
            narrative.peak_mentions = narrative.mention_count
            narrative.peak_date = timezone.now()
        narrative.save()

        return {
            'evidence_id': str(evidence.id),
            'narrative_title': narrative.title,
            'new_mention_count': narrative.mention_count
        }

    def _analyze_narrative_lifecycle(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze where a narrative is in its lifecycle."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence, NarrativeStatus

        narrative_id = tool_input.get('narrative_id')

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        # Calculate lifecycle metrics
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        recent_evidence = NarrativeEvidence.objects.filter(
            narrative=narrative,
            created_at__gte=week_ago
        ).count()

        older_evidence = NarrativeEvidence.objects.filter(
            narrative=narrative,
            created_at__gte=month_ago,
            created_at__lt=week_ago
        ).count()

        # Determine lifecycle stage
        if narrative.mention_count < 5:
            stage = NarrativeStatus.EMERGING
            stage_reason = "Low total mentions, newly detected"
        elif recent_evidence > older_evidence / 3:
            stage = NarrativeStatus.DOMINANT
            stage_reason = "High recent activity, narrative is active"
        elif recent_evidence < older_evidence / 10 and older_evidence > 0:
            stage = NarrativeStatus.FADING
            stage_reason = "Activity declining significantly"
        elif recent_evidence == 0 and (now - narrative.last_mention).days > 14 if narrative.last_mention else True:
            stage = NarrativeStatus.DEAD
            stage_reason = "No recent mentions, narrative appears dead"
        else:
            stage = NarrativeStatus.SHIFTING
            stage_reason = "Activity pattern suggests transition"

        # Update narrative status
        old_status = narrative.status
        narrative.status = stage
        narrative.save()

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'previous_status': old_status,
            'current_status': stage,
            'status_reason': stage_reason,
            'recent_evidence_count': recent_evidence,
            'older_evidence_count': older_evidence,
            'total_mentions': narrative.mention_count,
            'days_since_last_mention': (now - narrative.last_mention).days if narrative.last_mention else None
        }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the historian analysis task."""
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("narrative_history_analysis", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting narrative history analysis",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip analysis", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            logger.info(f"NarrativeHistorianAgent executing: {task[:100]}...")

        system_prompt = """You are the Narrative Historian Agent - a specialist in tracking and cataloging narratives over time.

Your role:
1. Track what stories people believe and when they started believing them
2. Identify when narratives emerge, peak, and fade
3. Find historical parallels to current events
4. Provide context for understanding narrative shifts

You have access to tools for:
- Getting narrative history and evidence
- Finding similar historical narratives
- Cataloging new narratives
- Analyzing narrative lifecycles

When analyzing narratives, consider:
- How long has this story been around?
- Is it growing stronger or weaker?
- What events caused it to emerge?
- Are there historical parallels?

Provide clear, analytical responses about narrative history and patterns."""

        # Build full prompt with system and task
        full_prompt = f"{system_prompt}\n\nTask: {task}"

        # Call GPT using BaseAgent's _call_openai
        try:
            gpt_response = self._call_openai(full_prompt)

            # Process response - extract content and handle any tool calls
            content = gpt_response.get('content', '')
            tool_calls = gpt_response.get('tool_calls', [])

            # Process tool calls if any
            tool_results = []
            tool_calls_made = []
            for tc in tool_calls:
                tool_calls_made.append({'name': tc['name'], 'input': tc['arguments']})
                tool_result = self._handle_tool_call(tc['name'], tc['arguments'])
                tool_results.append(tool_result)

            # Synthesize tool results if GPT content was empty
            if tool_results and not content:
                content = self._synthesize_tool_results(tool_calls_made, tool_results, task)
            message = content or "Narrative history analysis complete"

            result = AgentResult(
                success=True,
                message=message,
                data={'tool_results': tool_results, 'analysis': message, 'full_text': message},
                agent_name=self.name
            )

            if message and len(message) > 100:
                self._save_to_deliverable(
                    title=f"Narrative History: {task[:50]}",
                    content=message,
                    deliverable_type='analysis',
                    category='Analysis',
                    tags=['narrative', 'history', 'analysis', 'patterns'],
                    content_format='markdown',
                    metadata={'task': task},
                )
        except Exception as e:
            logger.error(f"NarrativeHistorianAgent error: {e}")
            result = AgentResult(
                success=False,
                error=str(e),
                agent_name=self.name
            )

        # Record learning outcome for collective intelligence
        try:
            self._record_learning_outcome(
                task=task,
                result=result,
                success=result.success if hasattr(result, 'success') else True,
                context={
                    'agent_type': self.__class__.__name__,
                    'execution_time_ms': result.execution_time_ms if hasattr(result, 'execution_time_ms') else 0,
                }
            )
        except Exception as le:
            logger.warning(f"Failed to record learning outcome: {le}")

        return result
