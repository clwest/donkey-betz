"""
Session 471: Narrative Drift Coordinator

The main orchestrator for the Narrative Drift Detector.
Tier 1 Autonomous Situation #2

Implements the 5 Autonomous Properties:
1. Persistent Context - Narrative/NarrativeShift/NarrativeEvidence models
2. Incoming Signals - Spider data feeds
3. Internal Disagreement - 3 agent perspectives (Historian, TrendBreak, CulturalImpact)
4. Outputs with Consequences - Alerts sent to Discord, tracked for accuracy
5. Self-Renewal - Scheduled Celery tasks run forever
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

from core.agents.base_agent import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class NarrativeDriftCoordinator(BaseAgent):
    """
    Coordinates the Narrative Drift Detection system.

    Orchestrates three specialist agents:
    - NarrativeHistorianAgent: Tracks narrative history and patterns
    - TrendBreakDetectorAgent: Detects when narratives shift
    - CulturalImpactAgent: Analyzes downstream effects

    The coordinator:
    1. Runs periodic scans for narrative shifts
    2. Coordinates multi-agent analysis of detected shifts
    3. Generates and sends alerts for significant shifts
    4. Tracks system performance for learning
    """

    name = "NarrativeDriftCoordinator"
    description = "Orchestrates the Narrative Drift Detection autonomous system"

    def __init__(self, user=None):
        super().__init__(user)
        self.tools = self._build_tools()

    def _build_tools(self) -> List[Dict[str, Any]]:
        """Build the tools available to this agent."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_full_scan",
                    "description": "Run a complete narrative drift scan across all domains",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "hours_back": {
                                "type": "integer",
                                "description": "Hours of data to scan",
                                "default": 24
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_shift_with_all_agents",
                    "description": "Run multi-agent analysis on a detected shift",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "shift_id": {
                                "type": "string",
                                "description": "UUID of the NarrativeShift to analyze"
                            }
                        },
                        "required": ["shift_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "process_new_spider_data",
                    "description": "Process new spider data for narrative signals",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "spider_data_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of SpiderData UUIDs to process"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_alert",
                    "description": "Create an alert for a significant narrative event",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "alert_type": {
                                "type": "string",
                                "enum": ["shift_detected", "new_narrative", "narrative_dying", "contradictions", "high_importance"],
                                "description": "Type of alert"
                            },
                            "title": {
                                "type": "string",
                                "description": "Alert title"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Alert summary"
                            },
                            "shift_id": {
                                "type": "string",
                                "description": "Related NarrativeShift UUID (optional)"
                            },
                            "narrative_id": {
                                "type": "string",
                                "description": "Related Narrative UUID (optional)"
                            }
                        },
                        "required": ["alert_type", "title", "summary"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_system_status",
                    "description": "Get the current status of the narrative drift system",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "seed_domain_narratives",
                    "description": "Seed initial narratives for a domain from current spider data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain to seed narratives for"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of narratives to create",
                                "default": 5
                            }
                        },
                        "required": ["domain"]
                    }
                }
            }
        ]

    def _handle_tool_call(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from the LLM."""
        if tool_name == "run_full_scan":
            return self._run_full_scan(tool_input)
        elif tool_name == "analyze_shift_with_all_agents":
            return self._analyze_shift_with_all_agents(tool_input)
        elif tool_name == "process_new_spider_data":
            return self._process_new_spider_data(tool_input)
        elif tool_name == "create_alert":
            return self._create_alert(tool_input)
        elif tool_name == "get_system_status":
            return self._get_system_status(tool_input)
        elif tool_name == "seed_domain_narratives":
            return self._seed_domain_narratives(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _run_full_scan(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete narrative drift scan."""
        from core.models_narrative_drift import (
            Narrative, NarrativeShift, NarrativeEvidence,
            NarrativeDomain, NarrativeStatus
        )
        from core.models_unified_system import SpiderData

        hours_back = tool_input.get('hours_back', 24)
        cutoff = timezone.now() - timedelta(hours=hours_back)

        scan_results = {
            'scan_time': timezone.now().isoformat(),
            'hours_scanned': hours_back,
            'domains_checked': [],
            'shifts_detected': [],
            'new_narratives': [],
            'fading_narratives': [],
            'alerts_created': []
        }

        # Check each domain
        for domain_choice in NarrativeDomain.choices:
            domain = domain_choice[0]
            domain_result = self._scan_domain(domain, cutoff)
            scan_results['domains_checked'].append(domain_result)

            # Collect shifts
            scan_results['shifts_detected'].extend(domain_result.get('shifts', []))
            scan_results['new_narratives'].extend(domain_result.get('new_narratives', []))
            scan_results['fading_narratives'].extend(domain_result.get('fading', []))

        # Create alerts for significant findings
        for shift in scan_results['shifts_detected'][:3]:  # Top 3 shifts
            if shift.get('confidence', 0) >= 0.7:
                alert = self._create_alert({
                    'alert_type': 'shift_detected',
                    'title': f"Narrative Shift: {shift.get('title', 'Unknown')}",
                    'summary': shift.get('summary', 'A significant narrative shift was detected'),
                    'shift_id': shift.get('shift_id')
                })
                scan_results['alerts_created'].append(alert)

        return scan_results

    def _scan_domain(self, domain: str, cutoff: datetime) -> Dict[str, Any]:
        """Scan a single domain for narrative changes."""
        from core.models_narrative_drift import (
            Narrative, NarrativeEvidence, NarrativeStatus, NarrativeShift
        )

        result = {
            'domain': domain,
            'narratives_checked': 0,
            'shifts': [],
            'new_narratives': [],
            'fading': []
        }

        # Get active narratives in this domain
        narratives = Narrative.objects.filter(
            domain=domain,
            status__in=[NarrativeStatus.EMERGING, NarrativeStatus.DOMINANT, NarrativeStatus.SHIFTING]
        )

        result['narratives_checked'] = narratives.count()

        for narrative in narratives:
            # Get recent evidence
            recent_evidence = NarrativeEvidence.objects.filter(
                narrative=narrative,
                created_at__gte=cutoff
            )

            recent_count = recent_evidence.count()
            recent_supports = recent_evidence.filter(sentiment='supports').count()
            recent_contradicts = recent_evidence.filter(sentiment='contradicts').count()

            # Check for shift signals
            if recent_contradicts > recent_supports and recent_count >= 3:
                confidence = 0.6 + (0.1 * min(recent_contradicts - recent_supports, 4))
                shift_summary = f"'{narrative.title}' is receiving more contradicting than supporting evidence"

                # Session 506: Check if we already detected this shift recently (avoid duplicates)
                existing_shift = NarrativeShift.objects.filter(
                    old_narrative=narrative,
                    detected_at__gte=cutoff
                ).first()

                if existing_shift:
                    # Use existing shift
                    shift_id = str(existing_shift.id)
                    logger.info(f"Found existing shift for {narrative.title}: {shift_id}")
                else:
                    # Session 506: Create actual NarrativeShift record in the database!
                    # This was the bug - shifts were detected but never persisted
                    shift = NarrativeShift.objects.create(
                        old_narrative=narrative,
                        new_narrative=None,  # Will be identified by agent analysis
                        domain=domain,
                        shift_summary=shift_summary,
                        old_narrative_summary=narrative.description or narrative.title,
                        new_narrative_summary="To be determined by analysis",
                        confidence=Decimal(str(confidence)),
                        importance=Decimal('0.5'),
                        trigger_events=[f"Contradicting evidence ({recent_contradicts}) exceeds supporting ({recent_supports})"],
                        evidence_sources=[str(e.id) for e in recent_evidence[:10]]
                    )
                    shift_id = str(shift.id)
                    logger.info(f"Created new NarrativeShift for {narrative.title}: {shift_id}")

                    # Update narrative status to SHIFTING
                    narrative.status = NarrativeStatus.SHIFTING
                    narrative.save()

                result['shifts'].append({
                    'narrative_id': str(narrative.id),
                    'shift_id': shift_id,
                    'title': narrative.title,
                    'signal': 'Contradicting evidence exceeds supporting',
                    'confidence': confidence,
                    'summary': shift_summary
                })

            # Check for fading narratives
            if narrative.status == NarrativeStatus.DOMINANT and recent_count == 0:
                week_ago = cutoff - timedelta(days=7)
                older_count = NarrativeEvidence.objects.filter(
                    narrative=narrative,
                    created_at__gte=week_ago,
                    created_at__lt=cutoff
                ).count()

                if older_count > 5:
                    result['fading'].append({
                        'narrative_id': str(narrative.id),
                        'title': narrative.title,
                        'previous_activity': older_count,
                        'recent_activity': 0
                    })

        return result

    def _analyze_shift_with_all_agents(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run multi-agent analysis on a shift."""
        from core.models_narrative_drift import NarrativeShift
        from .narrative_historian_agent import NarrativeHistorianAgent
        from .trend_break_detector_agent import TrendBreakDetectorAgent
        from .cultural_impact_agent import CulturalImpactAgent

        shift_id = tool_input.get('shift_id')

        try:
            shift = NarrativeShift.objects.get(id=shift_id)
        except NarrativeShift.DoesNotExist:
            return {"error": f"Shift {shift_id} not found"}

        analyses = {
            'shift_id': str(shift.id),
            'old_narrative': shift.old_narrative.title,
            'new_narrative': shift.new_narrative.title if shift.new_narrative else None,
            'agent_analyses': {}
        }

        context = {}
        scifi_context = {}
        spider_context = {}

        # 1. Historian Analysis
        try:
            historian = NarrativeHistorianAgent(user=self.user)
            historian_task = f"Analyze the history of the narrative '{shift.old_narrative.title}' (ID: {shift.old_narrative.id}). What patterns led to this shift? Are there historical parallels?"

            historian_result = historian.execute(historian_task, context, scifi_context, spider_context)
            if historian_result.success:
                analyses['agent_analyses']['historian'] = historian_result.result
                shift.historian_analysis = historian_result.result[:2000]
        except Exception as e:
            logger.error(f"Historian analysis failed: {e}")
            analyses['agent_analyses']['historian'] = f"Error: {str(e)}"

        # 2. Trend Break Analysis
        try:
            trend_break = TrendBreakDetectorAgent(user=self.user)
            trend_task = f"Analyze the shift from '{shift.old_narrative.title}' to '{shift.new_narrative.title if shift.new_narrative else 'unknown'}'. What triggered it? How confident are we in this shift?"

            trend_result = trend_break.execute(trend_task, context, scifi_context, spider_context)
            if trend_result.success:
                analyses['agent_analyses']['trend_break'] = trend_result.result
                shift.trend_break_analysis = trend_result.result[:2000]
        except Exception as e:
            logger.error(f"Trend break analysis failed: {e}")
            analyses['agent_analyses']['trend_break'] = f"Error: {str(e)}"

        # 3. Cultural Impact Analysis
        try:
            cultural = CulturalImpactAgent(user=self.user)
            cultural_task = f"Analyze the cultural impact of this narrative shift (ID: {shift_id}). What are the second-order effects? What actions should be taken?"

            cultural_result = cultural.execute(cultural_task, context, scifi_context, spider_context)
            if cultural_result.success:
                analyses['agent_analyses']['cultural_impact'] = cultural_result.result
                shift.cultural_impact_analysis = cultural_result.result[:2000]
        except Exception as e:
            logger.error(f"Cultural impact analysis failed: {e}")
            analyses['agent_analyses']['cultural_impact'] = f"Error: {str(e)}"

        # Save updated analyses
        shift.save()

        return analyses

    def _process_new_spider_data(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process new spider data for narrative signals."""
        from core.models_narrative_drift import Narrative, NarrativeEvidence
        from core.models_unified_system import SpiderData

        spider_data_ids = tool_input.get('spider_data_ids', [])

        if not spider_data_ids:
            # Get recent unprocessed spider data
            recent = timezone.now() - timedelta(hours=6)
            spider_data_qs = SpiderData.objects.filter(
                created_at__gte=recent
            ).exclude(
                narrative_evidence__isnull=False
            )[:50]
        else:
            spider_data_qs = SpiderData.objects.filter(id__in=spider_data_ids)

        results = {
            'processed': 0,
            'matched_narratives': 0,
            'new_evidence_created': 0
        }

        for sd in spider_data_qs:
            results['processed'] += 1

            # Extract content from raw_data (SpiderData stores items in raw_data.items)
            raw_data = sd.raw_data or {}
            items = raw_data.get('items', [])

            # Build searchable content from items
            content_parts = []
            first_title = ''
            for item in items[:10]:  # Check first 10 items
                item_title = item.get('title', '')
                item_content = item.get('content', item.get('description', ''))
                if item_title:
                    content_parts.append(item_title)
                    if not first_title:
                        first_title = item_title
                if item_content:
                    content_parts.append(item_content[:200])

            content = ' '.join(content_parts).lower()

            if not content:
                continue

            # Check each active narrative for keyword matches
            narratives = Narrative.objects.filter(
                status__in=['emerging', 'dominant', 'shifting']
            )

            for narrative in narratives:
                if not narrative.keywords:
                    continue

                matched = False
                for keyword in narrative.keywords:
                    if keyword.lower() in content:
                        matched = True
                        break

                if matched:
                    results['matched_narratives'] += 1

                    # Determine sentiment (basic heuristic - could use LLM)
                    sentiment = 'neutral'
                    positive_words = ['support', 'confirm', 'prove', 'success', 'growth']
                    negative_words = ['fail', 'wrong', 'decline', 'false', 'crash']

                    pos_count = sum(1 for w in positive_words if w in content)
                    neg_count = sum(1 for w in negative_words if w in content)

                    if pos_count > neg_count:
                        sentiment = 'supports'
                    elif neg_count > pos_count:
                        sentiment = 'contradicts'

                    # Create evidence
                    NarrativeEvidence.objects.create(
                        narrative=narrative,
                        spider_data=sd,
                        source_url=sd.source_url or '',
                        source_title=first_title[:300] if first_title else sd.spider_name,
                        source_type=sd.data_type or '',
                        excerpt=content[:500],
                        sentiment=sentiment,
                        source_date=sd.created_at
                    )
                    results['new_evidence_created'] += 1

                    # Update narrative stats
                    narrative.mention_count += 1
                    narrative.last_mention = timezone.now()
                    narrative.save()

        return results

    def _create_alert(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Create a narrative alert."""
        from core.models_narrative_drift import NarrativeAlert, NarrativeShift, Narrative

        alert_type = tool_input.get('alert_type')
        title = tool_input.get('title')
        summary = tool_input.get('summary')
        shift_id = tool_input.get('shift_id')
        narrative_id = tool_input.get('narrative_id')

        shift = None
        narrative = None

        if shift_id:
            try:
                shift = NarrativeShift.objects.get(id=shift_id)
            except NarrativeShift.DoesNotExist:
                pass

        if narrative_id:
            try:
                narrative = Narrative.objects.get(id=narrative_id)
            except Narrative.DoesNotExist:
                pass

        alert = NarrativeAlert.objects.create(
            shift=shift,
            narrative=narrative,
            alert_type=alert_type,
            title=title,
            summary=summary
        )

        return {
            'alert_id': str(alert.id),
            'alert_type': alert.alert_type,
            'title': alert.title,
            'created_at': alert.created_at.isoformat()
        }

    def _get_system_status(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Get system status."""
        from core.models_narrative_drift import (
            Narrative, NarrativeShift, NarrativeEvidence, NarrativeAlert,
            NarrativeDomain, NarrativeStatus
        )

        now = timezone.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        status = {
            'timestamp': now.isoformat(),
            'narratives': {
                'total': Narrative.objects.count(),
                'by_status': {},
                'by_domain': {}
            },
            'shifts': {
                'total': NarrativeShift.objects.count(),
                'last_24h': NarrativeShift.objects.filter(detected_at__gte=day_ago).count(),
                'last_7d': NarrativeShift.objects.filter(detected_at__gte=week_ago).count()
            },
            'evidence': {
                'total': NarrativeEvidence.objects.count(),
                'last_24h': NarrativeEvidence.objects.filter(created_at__gte=day_ago).count()
            },
            'alerts': {
                'total': NarrativeAlert.objects.count(),
                'unread': NarrativeAlert.objects.filter(read=False).count(),
                'last_24h': NarrativeAlert.objects.filter(created_at__gte=day_ago).count()
            }
        }

        # Count by status
        for choice in NarrativeStatus.choices:
            count = Narrative.objects.filter(status=choice[0]).count()
            if count > 0:
                status['narratives']['by_status'][choice[0]] = count

        # Count by domain
        for choice in NarrativeDomain.choices:
            count = Narrative.objects.filter(domain=choice[0]).count()
            if count > 0:
                status['narratives']['by_domain'][choice[0]] = count

        return status

    def _seed_domain_narratives(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Seed initial narratives for a domain from spider data patterns."""
        from core.models_narrative_drift import Narrative, NarrativeDomain
        from core.models_unified_system import SpiderData

        domain = tool_input.get('domain')
        count = tool_input.get('count', 5)

        # Validate domain
        valid_domains = [choice[0] for choice in NarrativeDomain.choices]
        if domain not in valid_domains:
            return {"error": f"Invalid domain: {domain}. Valid: {valid_domains}"}

        # Map domains to spider categories
        domain_categories = {
            'politics': ['news', 'political'],
            'markets': ['financial', 'crypto'],
            'tech': ['tech', 'ai'],
            'culture': ['social', 'community'],
            'geopolitics': ['news', 'political'],
            'crypto': ['crypto', 'financial'],
            'climate': ['news', 'science'],
            'health': ['health', 'science'],
        }

        categories = domain_categories.get(domain, ['news'])

        # Get recent spider data
        recent = timezone.now() - timedelta(days=7)
        spider_data = SpiderData.objects.filter(
            spider_category__in=categories,
            created_at__gte=recent
        ).values('title').annotate(
            count=models.Count('id')
        ).order_by('-count')[:count * 2]

        created = []
        for item in spider_data:
            if len(created) >= count:
                break

            title = item['title']
            if not title or len(title) < 10:
                continue

            # Check if similar exists
            exists = Narrative.objects.filter(title__icontains=title[:30]).exists()
            if exists:
                continue

            # Create narrative from pattern
            narrative = Narrative.objects.create(
                title=title[:200],
                description=f"Auto-detected narrative from spider data: {title}",
                domain=domain,
                keywords=title.split()[:5],
                auto_detected=True
            )
            created.append({
                'id': str(narrative.id),
                'title': narrative.title
            })

        return {
            'domain': domain,
            'requested': count,
            'created': len(created),
            'narratives': created
        }

    def run_autonomous_cycle(self) -> Dict[str, Any]:
        """
        Run a complete autonomous cycle.
        Called by Celery beat schedule.
        """
        logger.info("NarrativeDriftCoordinator starting autonomous cycle...")

        cycle_result = {
            'start_time': timezone.now().isoformat(),
            'steps': []
        }

        try:
            # Step 1: Process new spider data
            spider_result = self._process_new_spider_data({})
            cycle_result['steps'].append({
                'step': 'process_spider_data',
                'result': spider_result
            })

            # Step 2: Run full scan
            # Session 506: Increased from 6h to 12h for better shift detection
            scan_result = self._run_full_scan({'hours_back': 12})
            cycle_result['steps'].append({
                'step': 'full_scan',
                'result': scan_result
            })

            # Step 3: Analyze top shifts with all agents
            for shift in scan_result.get('shifts_detected', [])[:2]:
                if shift.get('shift_id'):
                    analysis = self._analyze_shift_with_all_agents({
                        'shift_id': shift['shift_id']
                    })
                    cycle_result['steps'].append({
                        'step': f"analyze_shift_{shift['shift_id'][:8]}",
                        'result': analysis
                    })

            cycle_result['success'] = True

        except Exception as e:
            logger.error(f"Autonomous cycle failed: {e}")
            cycle_result['success'] = False
            cycle_result['error'] = str(e)

        cycle_result['end_time'] = timezone.now().isoformat()
        logger.info(f"NarrativeDriftCoordinator cycle complete: {cycle_result['success']}")

        return cycle_result

    def execute(
        self,
        task: str,
        context: Dict[str, Any],
        scifi_context: Dict[str, Any],
        spider_context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the coordinator task."""
        logger.info(f"NarrativeDriftCoordinator executing: {task[:100]}...")

        system_prompt = """You are the Narrative Drift Coordinator - the orchestrator of the Narrative Drift Detection system.

Your role:
1. Coordinate the three specialist agents (Historian, TrendBreak, CulturalImpact)
2. Run periodic scans for narrative shifts
3. Process incoming spider data for narrative signals
4. Create and manage alerts for significant events
5. Maintain system health and performance

You have access to tools for:
- Running full scans across all domains
- Coordinating multi-agent analysis of shifts
- Processing new spider data
- Creating alerts
- Getting system status
- Seeding narratives for new domains

This is a Tier 1 Autonomous Situation with:
- Persistent Context: Database models track all narratives and shifts
- Incoming Signals: Spider data feeds into the system
- Internal Disagreement: 3 agents provide different perspectives
- Outputs with Consequences: Alerts are sent and tracked
- Self-Renewal: The system runs forever via Celery schedules

Your job is to keep this system running smoothly and surfacing valuable narrative intelligence."""

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


# Need to import models for the aggregate query
from django.db import models
