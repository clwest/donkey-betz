"""
Session 471: Trend Break Detector Agent

Detects when narratives shift - when the story changes.
"Something just changed in how people think about X"
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult
from ml.auto_selection import TaskType

logger = logging.getLogger(__name__)


def detect_trend_breaks_with_ml(trend_data: dict) -> dict:
    """Detect trend breaks and anomalies using ML models (Anomaly)."""
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

        # Use ANOMALY task type for trend break detection
        result = router.auto_route(
            data=trend_data,
            task_hint=TaskType.ANOMALY,
            max_models=2
        )

        return {
            'ml_used': True,
            'task_type': result.auto_selection.get('task_type', 'anomaly'),
            'models_used': result.models_used,
            'confidence': round(result.confidence, 2),
            'ml_insights': result.explanation,
            'anomalies_detected': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML trend break detection failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


class TrendBreakDetectorAgent(BaseAgent):
    """
    Detects when narratives shift or break from their established patterns.

    Responsibilities:
    1. Monitor narrative strength changes
    2. Detect sudden shifts in sentiment
    3. Identify trigger events
    4. Flag potential narrative breaks
    """

    name = "TrendBreakDetectorAgent"
    create_deliverable_on_schedule = True  # Fixed: was False (Session 1077), outputs were lost in AgentExecution
    description = "Detects when narratives shift or break from established patterns"
    system_prompt = """You are the Trend Break Detector Agent - an expert at identifying when narratives shift or change direction.

Your role:
1. Monitor narrative strength changes
2. Detect sudden shifts in sentiment
3. Identify trigger events that cause shifts
4. Flag potential narrative breaks

You answer the question: "Something just changed in how people think about X - what happened?"

You have access to:
- Narrative strength tracking over time
- Sentiment analysis of evidence
- Shift detection algorithms
- Event correlation tools

When analyzing potential shifts, consider:
- The magnitude of change (is this noise or a real shift?)
- The trigger events (what caused this?)
- The evidence quality (how reliable are our sources?)
- The confidence level (how sure are we this is a real shift?)"""

    def __init__(self, user=None):
        super().__init__(user)
        self.tools = self._build_tools()

    def _build_tools(self) -> List[Dict[str, Any]]:
        """Build the tools available to this agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "scan_for_shifts",
                    "description": "Scan all narratives for potential shifts in the last N hours",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hours_back": {
                                "type": "integer",
                                "description": "How many hours back to scan",
                                "default": 24
                            },
                            "domain": {
                                "type": "string",
                                "description": "Domain to filter by (optional)"
                            },
                            "min_confidence": {
                                "type": "number",
                                "description": "Minimum confidence for shift detection (0-1)",
                                "default": 0.6
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "detect_contradiction_spike",
                    "description": "Detect when contradicting evidence suddenly increases for a narrative",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative to analyze"
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "identify_trigger_events",
                    "description": "Identify events that may have triggered a narrative shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "narrative_id": {
                                "type": "string",
                                "description": "UUID of the narrative"
                            },
                            "shift_date": {
                                "type": "string",
                                "description": "Date when shift was detected (ISO format)"
                            }
                        },
                        "required": ["narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_narrative_momentum",
                    "description": "Compare momentum between old and new narratives",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "old_narrative_id": {
                                "type": "string",
                                "description": "UUID of the declining narrative"
                            },
                            "new_narrative_id": {
                                "type": "string",
                                "description": "UUID of the rising narrative"
                            }
                        },
                        "required": ["old_narrative_id", "new_narrative_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_shift_record",
                    "description": "Create a record of a detected narrative shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "old_narrative_id": {
                                "type": "string",
                                "description": "UUID of the old narrative"
                            },
                            "new_narrative_id": {
                                "type": "string",
                                "description": "UUID of the new narrative (optional)"
                            },
                            "shift_summary": {
                                "type": "string",
                                "description": "Summary of what changed"
                            },
                            "old_narrative_summary": {
                                "type": "string",
                                "description": "What people believed before"
                            },
                            "new_narrative_summary": {
                                "type": "string",
                                "description": "What people believe now"
                            },
                            "trigger_events": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Events that triggered this shift"
                            },
                            "confidence": {
                                "type": "number",
                                "description": "Confidence in this shift (0-1)"
                            },
                            "importance": {
                                "type": "number",
                                "description": "Importance of this shift (0-1)"
                            }
                        },
                        "required": ["old_narrative_id", "shift_summary", "old_narrative_summary", "new_narrative_summary"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_recent_spider_data",
                    "description": "Get recent spider data that might indicate narrative shifts",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain to filter by"
                            },
                            "hours_back": {
                                "type": "integer",
                                "description": "Hours of data to retrieve",
                                "default": 24
                            },
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keywords to search for"
                            }
                        }
                    }
                }
            }
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the LLM."""
        if tool_name == "scan_for_shifts":
            return self._scan_for_shifts(tool_input)
        elif tool_name == "detect_contradiction_spike":
            return self._detect_contradiction_spike(tool_input)
        elif tool_name == "identify_trigger_events":
            return self._identify_trigger_events(tool_input)
        elif tool_name == "compare_narrative_momentum":
            return self._compare_narrative_momentum(tool_input)
        elif tool_name == "create_shift_record":
            return self._create_shift_record(tool_input)
        elif tool_name == "get_recent_spider_data":
            return self._get_recent_spider_data(tool_input)

        else:
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, tool_input)

    def _scan_for_shifts(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Scan for potential narrative shifts."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence, NarrativeStatus

        hours_back = tool_input.get('hours_back', 24)
        domain = tool_input.get('domain')
        min_confidence = tool_input.get('min_confidence', 0.6)

        cutoff = timezone.now() - timedelta(hours=hours_back)

        # Get narratives with recent activity
        queryset = Narrative.objects.filter(last_mention__gte=cutoff)
        if domain:
            queryset = queryset.filter(domain=domain)

        potential_shifts = []

        for narrative in queryset:
            # Get recent vs older evidence
            recent = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=cutoff
            )

            week_ago = cutoff - timedelta(days=7)
            older = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=week_ago,
                created_at__lt=cutoff
            )

            recent_count = recent.count()
            older_count = older.count()

            # Count contradictions
            recent_contradicts = recent.filter(sentiment='contradicts').count()
            older_contradicts = older.filter(sentiment='contradicts').count()

            # Detect shift signals
            shift_signals = []
            confidence = 0.0

            # Signal 1: Sudden drop in mentions
            if older_count > 10 and recent_count < older_count * 0.3:
                shift_signals.append("Sudden drop in mentions")
                confidence += 0.3

            # Signal 2: Spike in contradictions
            if recent_count > 0:
                recent_contra_rate = recent_contradicts / recent_count
                older_contra_rate = older_contradicts / older_count if older_count > 0 else 0

                if recent_contra_rate > older_contra_rate + 0.2:
                    shift_signals.append("Spike in contradicting evidence")
                    confidence += 0.3

            # Signal 3: Strength history shows decline
            if narrative.strength_history and len(narrative.strength_history) >= 3:
                recent_strength = narrative.strength_history[-3:]
                if all(recent_strength[i] > recent_strength[i+1] for i in range(len(recent_strength)-1)):
                    shift_signals.append("Declining strength trend")
                    confidence += 0.2

            # Signal 4: Status already shifting
            if narrative.status == NarrativeStatus.SHIFTING:
                shift_signals.append("Already flagged as shifting")
                confidence += 0.2

            if confidence >= min_confidence and shift_signals:
                potential_shifts.append({
                    'narrative_id': str(narrative.id),
                    'title': narrative.title,
                    'domain': narrative.domain,
                    'status': narrative.status,
                    'shift_signals': shift_signals,
                    'confidence': min(confidence, 1.0),
                    'recent_mentions': recent_count,
                    'older_mentions': older_count,
                    'recent_contradictions': recent_contradicts
                })

        # Sort by confidence
        potential_shifts.sort(key=lambda x: -x['confidence'])

        return {
            'scan_period_hours': hours_back,
            'domain_filter': domain,
            'potential_shifts_found': len(potential_shifts),
            'shifts': potential_shifts[:10]
        }

    def _detect_contradiction_spike(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Detect spikes in contradicting evidence."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence

        narrative_id = tool_input.get('narrative_id')

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        now = timezone.now()
        periods = [
            ('last_24h', now - timedelta(hours=24), now),
            ('prev_24h', now - timedelta(hours=48), now - timedelta(hours=24)),
            ('last_week', now - timedelta(days=7), now),
            ('prev_week', now - timedelta(days=14), now - timedelta(days=7)),
        ]

        analysis = {}
        for period_name, start, end in periods:
            total = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=start,
                created_at__lt=end
            ).count()

            contradicts = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=start,
                created_at__lt=end,
                sentiment='contradicts'
            ).count()

            analysis[period_name] = {
                'total': total,
                'contradictions': contradicts,
                'contradiction_rate': contradicts / total if total > 0 else 0
            }

        # Detect spike
        spike_detected = False
        spike_magnitude = 0.0

        if analysis['last_24h']['contradiction_rate'] > analysis['prev_24h']['contradiction_rate'] + 0.15:
            spike_detected = True
            spike_magnitude = analysis['last_24h']['contradiction_rate'] - analysis['prev_24h']['contradiction_rate']

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'analysis': analysis,
            'spike_detected': spike_detected,
            'spike_magnitude': spike_magnitude,
            'interpretation': 'Significant increase in contradicting evidence detected' if spike_detected else 'No significant contradiction spike'
        }

    def _identify_trigger_events(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Identify events that may have triggered a shift."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence
        from core.models_unified_system import SpiderData

        narrative_id = tool_input.get('narrative_id')
        shift_date_str = tool_input.get('shift_date')

        try:
            narrative = Narrative.objects.get(id=narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Narrative {narrative_id} not found"}

        # Parse shift date or use recent window
        if shift_date_str:
            try:
                shift_date = datetime.fromisoformat(shift_date_str.replace('Z', '+00:00'))
            except ValueError:
                shift_date = timezone.now()
        else:
            shift_date = timezone.now()

        # Look for evidence around the shift
        window_start = shift_date - timedelta(days=3)
        window_end = shift_date + timedelta(days=1)

        # Get contradicting evidence as potential triggers
        contradicting = NarrativeEvidence.objects.filter(
            narrative=narrative,
            created_at__gte=window_start,
            created_at__lte=window_end,
            sentiment='contradicts'
        ).order_by('-strength')[:10]

        trigger_candidates = []
        for ev in contradicting:
            trigger_candidates.append({
                'date': ev.created_at.isoformat(),
                'source': ev.source_title or ev.source_url[:50] if ev.source_url else 'Unknown',
                'excerpt': ev.excerpt[:200] if ev.excerpt else '',
                'strength': float(ev.strength)
            })

        # Also look at spider data with relevant keywords
        # Session 737: Fixed to use proper SpiderData fields
        if narrative.keywords:
            for keyword in narrative.keywords[:3]:
                # Search in spider_name and embedding_text instead of title
                spider_data = SpiderData.objects.filter(
                    created_at__gte=window_start,
                    created_at__lte=window_end,
                ).filter(
                    embedding_text__icontains=keyword
                )[:5]

                for sd in spider_data:
                    # Extract title from raw_data JSON
                    raw_data = sd.raw_data or {}
                    items = raw_data.get('items', [])
                    title = 'Spider Data'
                    if items and len(items) > 0:
                        first_item = items[0] if isinstance(items[0], dict) else {}
                        title = first_item.get('title') or first_item.get('headline') or 'Spider Data'

                    trigger_candidates.append({
                        'date': sd.created_at.isoformat(),
                        'source': sd.spider_name or 'Spider Data',
                        'excerpt': title,
                        'strength': 0.5
                    })

        return {
            'narrative_id': str(narrative.id),
            'title': narrative.title,
            'analysis_window': {
                'start': window_start.isoformat(),
                'end': window_end.isoformat()
            },
            'trigger_candidates': trigger_candidates[:15]
        }

    def _compare_narrative_momentum(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Compare momentum between two narratives."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence

        old_id = tool_input.get('old_narrative_id')
        new_id = tool_input.get('new_narrative_id')

        try:
            old_narrative = Narrative.objects.get(id=old_id)
        except Narrative.DoesNotExist:
            return {"error": f"Old narrative {old_id} not found"}

        try:
            new_narrative = Narrative.objects.get(id=new_id)
        except Narrative.DoesNotExist:
            return {"error": f"New narrative {new_id} not found"}

        now = timezone.now()
        week_ago = now - timedelta(days=7)

        def calculate_momentum(narrative):
            recent = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=week_ago
            )

            supports = recent.filter(sentiment='supports').count()
            contradicts = recent.filter(sentiment='contradicts').count()
            total = recent.count()

            # Calculate momentum score
            if total == 0:
                return 0.0

            support_ratio = supports / total
            momentum = support_ratio * (total / 10)  # Scale by activity

            return min(momentum, 1.0)

        old_momentum = calculate_momentum(old_narrative)
        new_momentum = calculate_momentum(new_narrative)

        return {
            'comparison': {
                'old_narrative': {
                    'id': str(old_narrative.id),
                    'title': old_narrative.title,
                    'momentum': old_momentum,
                    'status': old_narrative.status,
                    'mention_count': old_narrative.mention_count
                },
                'new_narrative': {
                    'id': str(new_narrative.id),
                    'title': new_narrative.title,
                    'momentum': new_momentum,
                    'status': new_narrative.status,
                    'mention_count': new_narrative.mention_count
                }
            },
            'momentum_shift': new_momentum - old_momentum,
            'interpretation': 'New narrative gaining momentum' if new_momentum > old_momentum else 'Old narrative still dominant'
        }

    def _create_shift_record(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create a NarrativeShift record."""
        from core.models_narrative_drift import Narrative, NarrativeShift

        old_narrative_id = tool_input.get('old_narrative_id')
        new_narrative_id = tool_input.get('new_narrative_id')
        shift_summary = tool_input.get('shift_summary')
        old_summary = tool_input.get('old_narrative_summary')
        new_summary = tool_input.get('new_narrative_summary')
        trigger_events = tool_input.get('trigger_events', [])
        confidence = tool_input.get('confidence', 0.5)
        importance = tool_input.get('importance', 0.5)

        try:
            old_narrative = Narrative.objects.get(id=old_narrative_id)
        except Narrative.DoesNotExist:
            return {"error": f"Old narrative {old_narrative_id} not found"}

        new_narrative = None
        if new_narrative_id:
            try:
                new_narrative = Narrative.objects.get(id=new_narrative_id)
            except Narrative.DoesNotExist:
                pass

        shift = NarrativeShift.objects.create(
            old_narrative=old_narrative,
            new_narrative=new_narrative,
            domain=old_narrative.domain,
            shift_summary=shift_summary,
            old_narrative_summary=old_summary,
            new_narrative_summary=new_summary,
            trigger_events=trigger_events,
            confidence=Decimal(str(confidence)),
            importance=Decimal(str(importance))
        )

        # [SESSION 475] Add provenance tracking
        try:
            from core.services.provenance_tracker import create_narrative_shift_provenance
            create_narrative_shift_provenance(
                shift_id=str(shift.id),
                domain=shift.domain,
                confidence=float(confidence),
                importance=float(importance),
                metadata={
                    'old_narrative': old_narrative.title,
                    'new_narrative': new_narrative.title if new_narrative else None,
                    'agent': 'TrendBreakDetectorAgent'
                }
            )
        except Exception as prov_e:
            logger.warning(f"Failed to create shift provenance: {prov_e}")

        return {
            'shift_id': str(shift.id),
            'old_narrative': old_narrative.title,
            'new_narrative': new_narrative.title if new_narrative else None,
            'domain': shift.domain,
            'confidence': float(shift.confidence),
            'importance': float(shift.importance)
        }

    def _get_recent_spider_data(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent spider data for narrative analysis."""
        from core.models_unified_system import SpiderData

        domain = tool_input.get('domain')
        hours_back = tool_input.get('hours_back', 24)
        keywords = tool_input.get('keywords', [])

        cutoff = timezone.now() - timedelta(hours=hours_back)

        queryset = SpiderData.objects.filter(created_at__gte=cutoff)

        # Filter by spider_name if domain provided (map domains to spider names)
        domain_spider_mapping = {
            'politics': ['bbc', 'cnn', 'reuters', 'npr'],
            'markets': ['coingecko', 'yahoofinance', 'polygon', 'finnhub', 'kalshi'],
            'tech': ['hackernews', 'techcrunch', 'theverge', 'devto', 'github'],
            'culture': ['reddit', 'bluesky'],
            'geopolitics': ['bbc', 'reuters', 'defenseone'],
            'crypto': ['coingecko', 'cryptonews'],
            'climate': ['bbc', 'cnn', 'sciencedaily'],
            'health': ['mobihealthnews', 'sciencedaily'],
        }

        if domain and domain in domain_spider_mapping:
            spider_names = domain_spider_mapping[domain]
            queryset = queryset.filter(spider_name__in=spider_names)

        results = []
        for sd in queryset.order_by('-created_at')[:20]:
            # Session 737: Extract title/content from raw_data JSON field
            raw_data = sd.raw_data or {}
            items = raw_data.get('items', [])

            # Get first item's title if available
            title = 'No title'
            content_preview = ''
            url = sd.source_url

            if items and len(items) > 0:
                first_item = items[0] if isinstance(items[0], dict) else {}
                title = first_item.get('title') or first_item.get('headline') or 'No title'
                content_preview = first_item.get('content', '')[:200] if first_item.get('content') else ''
                url = first_item.get('url') or first_item.get('link') or sd.source_url

            results.append({
                'id': str(sd.id),
                'title': title,
                'source': sd.spider_name,
                'url': url,
                'created_at': sd.created_at.isoformat(),
                'content_preview': content_preview,
                'data_type': sd.data_type
            })

        return {
            'hours_back': hours_back,
            'domain_filter': domain,
            'keyword_filter': keywords,
            'count': len(results),
            'data': results
        }

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the trend break detection task."""
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("trend_break_detection", task, input_data=context):
            self.record_decision(
                decision_type="analysis",
                action="Starting trend break detection",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip detection", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            logger.info(f"TrendBreakDetectorAgent executing: {task[:100]}...")

        system_prompt = """You are the Trend Break Detector Agent - a specialist in detecting when narratives shift.

Your role:
1. Monitor narratives for signs of change
2. Detect when the dominant story starts breaking down
3. Identify what triggered the shift
4. Flag significant narrative breaks for further analysis

You have access to tools for:
- Scanning for potential shifts across all narratives
- Detecting spikes in contradicting evidence
- Identifying trigger events
- Comparing momentum between old and new narratives
- Creating shift records

Key signals to watch for:
- Sudden drops in mentions (people stopped talking about it)
- Spikes in contradicting evidence (people started disagreeing)
- Declining strength over time (gradual loss of conviction)
- New competing narratives gaining momentum

When you detect a shift, be specific about:
- What changed
- What might have caused it
- How confident you are
- How important this shift is

Provide clear, analytical responses about narrative shifts."""

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
            message = content or "Trend break detection complete"

            result = AgentResult(
                success=True,
                message=message,
                data={'tool_results': tool_results, 'analysis': message, 'full_text': message},
                agent_name=self.name
            )
        except Exception as e:
            logger.error(f"TrendBreakDetectorAgent error: {e}")
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

        if result.success and len(result.message) > 100:
            self._save_to_deliverable(
                title=f"Trend Break Detection: {task[:80]}",
                content=result.message,
                deliverable_type='analysis',
                category='Trend Analysis',
                tags=['trend_break', 'narrative'],
                metadata={'task': task[:200]},
            )

        return result
