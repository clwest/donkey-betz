"""
Session 471: Trend Break Detector Agent

Detects when narratives shift - when the story changes.
"Something just changed in how people think about X"
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, F
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


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
    description = "Detects when narratives shift or break from established patterns"

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
            return {"error": f"Unknown tool: {tool_name}"}

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
        if narrative.keywords:
            for keyword in narrative.keywords[:3]:
                spider_data = SpiderData.objects.filter(
                    created_at__gte=window_start,
                    created_at__lte=window_end,
                    title__icontains=keyword
                )[:5]

                for sd in spider_data:
                    trigger_candidates.append({
                        'date': sd.created_at.isoformat(),
                        'source': sd.source_name or 'Spider Data',
                        'excerpt': sd.title,
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

        # Filter by keywords if provided
        if keywords:
            from django.db.models import Q
            keyword_filter = Q()
            for keyword in keywords:
                keyword_filter |= Q(title__icontains=keyword) | Q(content__icontains=keyword)
            queryset = queryset.filter(keyword_filter)

        # Map domains to spider categories
        domain_mapping = {
            'politics': ['news', 'political'],
            'markets': ['financial', 'crypto'],
            'tech': ['tech', 'ai'],
            'culture': ['social', 'community'],
            'geopolitics': ['news', 'political'],
            'crypto': ['crypto', 'financial'],
            'climate': ['news', 'science'],
            'health': ['health', 'science'],
        }

        if domain and domain in domain_mapping:
            categories = domain_mapping[domain]
            queryset = queryset.filter(spider_category__in=categories)

        results = []
        for sd in queryset.order_by('-created_at')[:20]:
            results.append({
                'id': str(sd.id),
                'title': sd.title,
                'source': sd.source_name or sd.spider_name,
                'url': sd.url,
                'created_at': sd.created_at.isoformat(),
                'category': sd.spider_category
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

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]

        result = self._execute_with_tools(messages, context)

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
