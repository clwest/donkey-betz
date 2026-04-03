"""
Session 471: Narrative Drift Coordinator
Session 683: Added ML Integration (DistilBERT for text classification)

The main orchestrator for the Narrative Drift Detector.
Tier 1 Autonomous Situation #2

Implements the 5 Autonomous Properties:
1. Persistent Context - Narrative/NarrativeShift/NarrativeEvidence models
2. Incoming Signals - Spider data feeds
3. Internal Disagreement - 3 agent perspectives (Historian, TrendBreak, CulturalImpact)
4. Outputs with Consequences - Alerts sent to Discord, tracked for accuracy
5. Self-Renewal - Scheduled Celery tasks run forever
"""

import logging
import re
import json
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from core.agents.base_agent import BaseAgent, AgentResult, strip_simulated_tool_json
from ml.auto_selection import TaskType

# Session 895: Timeout for sub-agent executions to prevent coordinator hangs
# Extended to 5 min to accommodate thinking models (GPT-5.1, o1, o3)
SUB_AGENT_TIMEOUT = 300  # 5 minutes per sub-agent

logger = logging.getLogger(__name__)


# =============================================================================
# Session 683: ML Integration Helpers
# =============================================================================

def analyze_narrative_text_with_ml(text_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze narrative text using ML models (DistilBERT for text classification).

    Args:
        text_data: Dict with 'texts' key containing list of text samples

    Returns:
        Dict with ML analysis results
    """
    try:
        from core.services.agent_model_router import get_agent_model_router
        router = get_agent_model_router()

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
            'sentiment_score': result.score if hasattr(result, 'score') else None,
            'text_features': result.prediction if hasattr(result, 'prediction') else None,
        }
    except Exception as e:
        logger.warning(f"ML narrative analysis failed: {e}")
        return {'ml_used': False, 'reason': f'ML error: {str(e)}'}


# =============================================================================
# Session 509: Domain-Specific Source Weighting
# =============================================================================
# Problem: All domains were pulling evidence from same general sources.
# Solution: Boost confidence for domain-appropriate sources.

DOMAIN_SOURCE_WEIGHTS = {
    'climate': {
        'preferred': [
            'noaa.gov', 'epa.gov', 'nature.com', 'sciencedaily.com',
            'climate.gov', 'ipcc.ch', 'carbonbrief.org', 'insideclimatenews.org',
            'climatecentral.org', 'grist.org'
        ],
        'weight_boost': 1.5,  # 50% confidence boost for preferred sources
        'penalty_sources': ['scarymommy.com', 'eater.com', 'variety.com'],
        'penalty': 0.5  # 50% confidence reduction for irrelevant sources
    },
    'markets': {
        'preferred': [
            'bloomberg.com', 'sec.gov', 'wsj.com', 'reuters.com',
            'ft.com', 'cnbc.com', 'marketwatch.com', 'finance.yahoo.com',
            'barrons.com', 'investopedia.com', 'seeking alpha'
        ],
        'weight_boost': 1.3,
        'penalty_sources': [],
        'penalty': 0.7
    },
    'health': {
        'preferred': [
            'nih.gov', 'cdc.gov', 'who.int', 'statnews.com',
            'webmd.com', 'healthline.com', 'mayoclinic.org', 'nejm.org',
            'jamanetwork.com', 'thelancet.com', 'medscape.com'
        ],
        'weight_boost': 1.4,
        'penalty_sources': [],
        'penalty': 0.6
    },
    'crypto': {
        'preferred': [
            'coindesk.com', 'cointelegraph.com', 'decrypt.co',
            'theblock.co', 'bitcoinmagazine.com', 'cryptoslate.com',
            'messari.io', 'defipulse.com', 'dappradar.com'
        ],
        'weight_boost': 1.3,
        'penalty_sources': [],
        'penalty': 0.7
    },
    'tech': {
        'preferred': [
            'techcrunch.com', 'theverge.com', 'wired.com', 'arstechnica.com',
            'technologyreview.com', 'venturebeat.com', 'zdnet.com',
            'engadget.com', 'hackernews.com', 'dev.to'
        ],
        'weight_boost': 1.2,
        'penalty_sources': [],
        'penalty': 0.8
    },
    'politics': {
        'preferred': [
            'politico.com', 'thehill.com', 'rollcall.com', 'c-span.org',
            'congress.gov', 'whitehouse.gov', 'apnews.com', 'npr.org',
            'realclearpolitics.com', 'fivethirtyeight.com'
        ],
        'weight_boost': 1.3,
        'penalty_sources': [],
        'penalty': 0.7
    },
    'geopolitics': {
        'preferred': [
            'foreignaffairs.com', 'cfr.org', 'brookings.edu', 'rand.org',
            'bbc.com', 'aljazeera.com', 'dw.com', 'reuters.com',
            'economist.com', 'stratfor.com'
        ],
        'weight_boost': 1.3,
        'penalty_sources': [],
        'penalty': 0.7
    },
    'culture': {
        'preferred': [
            'nytimes.com', 'newyorker.com', 'theatlantic.com', 'vox.com',
            'slate.com', 'buzzfeed.com', 'vice.com', 'rollingstone.com'
        ],
        'weight_boost': 1.2,
        'penalty_sources': [],
        'penalty': 0.8
    }
}


def get_source_weight(source_url: str, domain: str) -> tuple:
    """
    Calculate source weight for a given URL and domain.

    Returns:
        tuple: (multiplier, is_preferred, is_penalized)
        - multiplier: float to multiply confidence by
        - is_preferred: bool if source is preferred for domain
        - is_penalized: bool if source is inappropriate for domain
    """
    if not source_url or not domain:
        return (1.0, False, False)

    source_lower = source_url.lower()
    domain_config = DOMAIN_SOURCE_WEIGHTS.get(domain.lower(), {})

    # Check preferred sources
    preferred = domain_config.get('preferred', [])
    for pref_source in preferred:
        if pref_source in source_lower:
            return (domain_config.get('weight_boost', 1.2), True, False)

    # Check penalty sources
    penalty_sources = domain_config.get('penalty_sources', [])
    for penalty_source in penalty_sources:
        if penalty_source in source_lower:
            return (domain_config.get('penalty', 0.5), False, True)

    # Neutral source
    return (1.0, False, False)


# =============================================================================
# Session 506: Enhanced Sentiment Detection System
# =============================================================================

class NarrativeSentimentAnalyzer:
    """
    Sophisticated sentiment analyzer for narrative evidence.

    Features:
    - Domain-specific keyword dictionaries
    - Weighted scoring (some words are stronger signals)
    - Negation detection ("not successful" → negative)
    - Phrase matching for complex expressions
    """

    # Base sentiment words with weights (1.0 = normal, 2.0 = strong signal)
    POSITIVE_WORDS = {
        # Strong positive signals (weight 2.0)
        'breakthrough': 2.0, 'revolutionary': 2.0, 'unprecedented': 2.0,
        'skyrocket': 2.0, 'surge': 2.0, 'soar': 2.0, 'boom': 2.0,
        'triumph': 2.0, 'victory': 2.0, 'milestone': 2.0,

        # Standard positive signals (weight 1.0)
        'success': 1.0, 'successful': 1.0, 'succeed': 1.0,
        'growth': 1.0, 'growing': 1.0, 'grow': 1.0,
        'increase': 1.0, 'increasing': 1.0, 'rise': 1.0, 'rising': 1.0,
        'improve': 1.0, 'improvement': 1.0, 'improving': 1.0,
        'gain': 1.0, 'gains': 1.0, 'positive': 1.0,
        'confirm': 1.0, 'confirmed': 1.0, 'validates': 1.0,
        'prove': 1.0, 'proven': 1.0, 'evidence': 1.0,
        'support': 1.0, 'supports': 1.0, 'backed': 1.0,
        'achieve': 1.0, 'achievement': 1.0, 'accomplished': 1.0,
        'benefit': 1.0, 'beneficial': 1.0, 'advantage': 1.0,
        'progress': 1.0, 'advance': 1.0, 'advancing': 1.0,
        'adopt': 1.0, 'adoption': 1.0, 'embrace': 1.0,
        'optimistic': 1.0, 'optimism': 1.0, 'confidence': 1.0,
        'bullish': 1.0, 'rally': 1.0, 'recovery': 1.0,
        'exceed': 1.0, 'exceeds': 1.0, 'outperform': 1.0,
        'innovation': 1.0, 'innovative': 1.0, 'transform': 1.0,

        # Mild positive signals (weight 0.5)
        'good': 0.5, 'better': 0.5, 'best': 0.5,
        'up': 0.5, 'higher': 0.5, 'strong': 0.5,
        'stable': 0.5, 'steady': 0.5, 'solid': 0.5,
    }

    NEGATIVE_WORDS = {
        # Strong negative signals (weight 2.0)
        'crash': 2.0, 'collapse': 2.0, 'catastrophe': 2.0, 'disaster': 2.0,
        'plunge': 2.0, 'plummet': 2.0, 'tank': 2.0, 'tumble': 2.0,
        'crisis': 2.0, 'catastrophic': 2.0, 'devastating': 2.0,
        'debunk': 2.0, 'debunked': 2.0, 'disprove': 2.0, 'disproven': 2.0,
        'fraud': 2.0, 'scam': 2.0, 'hoax': 2.0,

        # Standard negative signals (weight 1.0)
        'fail': 1.0, 'failure': 1.0, 'failed': 1.0, 'failing': 1.0,
        'decline': 1.0, 'declining': 1.0, 'decrease': 1.0, 'decreasing': 1.0,
        'drop': 1.0, 'dropping': 1.0, 'fall': 1.0, 'falling': 1.0,
        'wrong': 1.0, 'incorrect': 1.0, 'false': 1.0, 'untrue': 1.0,
        'reject': 1.0, 'rejected': 1.0, 'deny': 1.0, 'denied': 1.0,
        'lose': 1.0, 'loss': 1.0, 'lost': 1.0, 'losing': 1.0,
        'problem': 1.0, 'issue': 1.0, 'concern': 1.0, 'worried': 1.0,
        'struggle': 1.0, 'struggling': 1.0, 'trouble': 1.0,
        'criticize': 1.0, 'criticism': 1.0, 'critics': 1.0,
        'doubt': 1.0, 'doubtful': 1.0, 'skeptic': 1.0, 'skeptical': 1.0,
        'pessimistic': 1.0, 'bearish': 1.0, 'downturn': 1.0,
        'warning': 1.0, 'warn': 1.0, 'caution': 1.0, 'risk': 1.0,
        'threat': 1.0, 'threaten': 1.0, 'danger': 1.0, 'dangerous': 1.0,
        'abandon': 1.0, 'abandoned': 1.0, 'halt': 1.0, 'halted': 1.0,
        'delay': 1.0, 'delayed': 1.0, 'setback': 1.0,
        'overrated': 1.0, 'overhyped': 1.0, 'bubble': 1.0,

        # Mild negative signals (weight 0.5)
        'bad': 0.5, 'worse': 0.5, 'worst': 0.5,
        'down': 0.5, 'lower': 0.5, 'weak': 0.5,
        'slow': 0.5, 'slower': 0.5, 'stall': 0.5,
    }

    # Domain-specific sentiment modifiers
    DOMAIN_KEYWORDS = {
        'tech': {
            'positive': {'disrupting': 1.5, 'scaling': 1.0, 'adoption': 1.0, 'launch': 1.0, 'release': 0.5},
            'negative': {'bug': 1.0, 'vulnerability': 1.5, 'breach': 2.0, 'outage': 1.5, 'deprecated': 1.0}
        },
        'markets': {
            'positive': {'rally': 1.5, 'bull': 1.0, 'profit': 1.0, 'dividend': 0.5, 'upgrade': 1.0},
            'negative': {'bear': 1.0, 'recession': 2.0, 'inflation': 1.0, 'layoff': 1.5, 'bankruptcy': 2.0}
        },
        'politics': {
            'positive': {'bipartisan': 1.0, 'reform': 0.5, 'pass': 0.5, 'approve': 1.0, 'unity': 1.0},
            'negative': {'scandal': 2.0, 'impeach': 2.0, 'gridlock': 1.0, 'polariz': 1.0, 'corrupt': 2.0}
        },
        'crypto': {
            'positive': {'moon': 1.5, 'hodl': 0.5, 'institutional': 1.0, 'mainstream': 1.0, 'whale': 0.5},
            'negative': {'rug': 2.0, 'hack': 2.0, 'exploit': 2.0, 'dump': 1.5, 'ponzi': 2.0}
        },
        'climate': {
            'positive': {'renewable': 1.0, 'sustainable': 1.0, 'carbon neutral': 1.5, 'green': 0.5},
            'negative': {'emission': 0.5, 'pollut': 1.0, 'warming': 0.5, 'extreme weather': 1.5}
        },
        'health': {
            'positive': {'cure': 2.0, 'treatment': 1.0, 'vaccine': 1.0, 'breakthrough': 2.0, 'recovery': 1.0},
            'negative': {'outbreak': 2.0, 'pandemic': 1.5, 'side effect': 1.0, 'death': 1.5, 'mortality': 1.5}
        },
    }

    # Negation words that flip sentiment
    NEGATION_WORDS = {'not', 'no', 'never', 'neither', 'nobody', 'nothing',
                      'nowhere', 'hardly', 'barely', 'scarcely', "n't", "don't",
                      "doesn't", "didn't", "won't", "wouldn't", "couldn't", "shouldn't"}

    # Phrases that indicate contradiction to a narrative
    CONTRADICTION_PHRASES = [
        'actually', 'in reality', 'contrary to', 'despite claims',
        'myth', 'misconception', 'not true', 'overstated', 'exaggerated',
        'fails to', 'unable to', 'unlikely to', 'won\'t happen',
        'not going to', 'overblown', 'hype', 'misleading'
    ]

    @classmethod
    def analyze(cls, content: str, domain: str = None, narrative_title: str = None) -> Tuple[str, float]:
        """
        Analyze content sentiment with respect to a narrative.

        Returns:
            Tuple of (sentiment, confidence)
            - sentiment: 'supports', 'contradicts', or 'neutral'
            - confidence: 0.0 to 1.0
        """
        if not content:
            return 'neutral', 0.0

        content_lower = content.lower()
        words = re.findall(r'\b\w+\b', content_lower)

        pos_score = 0.0
        neg_score = 0.0

        # Check for negation context (within 3 words)
        def is_negated(word_idx: int) -> bool:
            start = max(0, word_idx - 3)
            context = words[start:word_idx]
            return any(neg in context for neg in cls.NEGATION_WORDS)

        # Score base sentiment words
        for i, word in enumerate(words):
            negated = is_negated(i)

            if word in cls.POSITIVE_WORDS:
                weight = cls.POSITIVE_WORDS[word]
                if negated:
                    neg_score += weight  # Negated positive = negative
                else:
                    pos_score += weight

            elif word in cls.NEGATIVE_WORDS:
                weight = cls.NEGATIVE_WORDS[word]
                if negated:
                    pos_score += weight * 0.5  # Negated negative = mild positive
                else:
                    neg_score += weight

        # Add domain-specific scoring
        if domain and domain.lower() in cls.DOMAIN_KEYWORDS:
            domain_words = cls.DOMAIN_KEYWORDS[domain.lower()]
            for word in words:
                if word in domain_words.get('positive', {}):
                    pos_score += domain_words['positive'][word]
                elif word in domain_words.get('negative', {}):
                    neg_score += domain_words['negative'][word]

        # Check for contradiction phrases (strong signal for 'contradicts')
        for phrase in cls.CONTRADICTION_PHRASES:
            if phrase in content_lower:
                neg_score += 1.5

        # Calculate final sentiment
        total_score = pos_score + neg_score

        if total_score < 1.0:
            # Not enough signal
            return 'neutral', 0.0

        # Determine sentiment based on score ratio
        if pos_score > neg_score * 1.3:  # Need 30% more positive to be "supports"
            confidence = min(1.0, (pos_score - neg_score) / (total_score + 1))
            return 'supports', confidence
        elif neg_score > pos_score * 1.3:  # Need 30% more negative to be "contradicts"
            confidence = min(1.0, (neg_score - pos_score) / (total_score + 1))
            return 'contradicts', confidence
        else:
            # Mixed signals
            return 'neutral', 0.0


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
            # Session 1002C: Fall through to BaseAgent for web_search, spider_query, delegation
            return super()._execute_tool_call(tool_name, tool_input)

    def _run_full_scan(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complete narrative drift scan."""
        from core.models_narrative_drift import (
            NarrativeDomain
        )

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

            # Session 509: Use weighted strength instead of raw counts
            # This gives more weight to evidence from domain-appropriate sources
            from django.db.models import Sum
            support_evidence = recent_evidence.filter(sentiment='supports')
            contradict_evidence = recent_evidence.filter(sentiment='contradicts')

            # Sum weighted strengths (default 0.5 if no strength set)
            support_strength = support_evidence.aggregate(
                total=Sum('strength')
            )['total'] or Decimal('0')
            contradict_strength = contradict_evidence.aggregate(
                total=Sum('strength')
            )['total'] or Decimal('0')

            # Also track raw counts for logging
            recent_supports = support_evidence.count()
            recent_contradicts = contradict_evidence.count()

            # Check for shift signals using weighted strength
            # Contradicting evidence must outweigh supporting by 20%
            if contradict_strength > support_strength * Decimal('1.2') and recent_count >= 3:
                # Calculate confidence based on strength differential
                strength_diff = float(contradict_strength - support_strength)
                confidence = min(0.95, 0.6 + (0.1 * strength_diff))
                shift_summary = (
                    f"'{narrative.title}' is receiving more contradicting evidence "
                    f"(weighted: {float(contradict_strength):.2f} vs {float(support_strength):.2f})"
                )

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
                    # Session 509: Validate shift with mythology validator before creating
                    from core.agents.narrative.narrative_mythology_validator import (
                        narrative_mythology_validator
                    )
                    from urllib.parse import urlparse

                    # Count unique sources for corroboration check
                    unique_sources = set()
                    for e in contradict_evidence:
                        if e.source_url:
                            parsed = urlparse(e.source_url)
                            unique_sources.add(parsed.netloc)

                    unique_source_count = len(unique_sources)

                    # Validate the shift
                    shift_validation = narrative_mythology_validator.validate_shift(
                        shift_data={'title': narrative.title, 'domain': domain},
                        evidence_count=recent_contradicts,
                        unique_source_count=unique_source_count
                    )

                    # Adjust confidence based on validation
                    adjusted_confidence = confidence + shift_validation['confidence_adjustment']
                    adjusted_confidence = max(0.1, min(0.95, adjusted_confidence))

                    # Determine if shift is verified (enough unique sources)
                    is_verified = shift_validation['verified']

                    # Session 506: Create actual NarrativeShift record in the database!
                    # This was the bug - shifts were detected but never persisted
                    shift = NarrativeShift.objects.create(
                        old_narrative=narrative,
                        new_narrative=None,  # Will be identified by agent analysis
                        domain=domain,
                        shift_summary=shift_summary,
                        old_narrative_summary=narrative.description or narrative.title,
                        new_narrative_summary="To be determined by analysis",
                        confidence=Decimal(str(adjusted_confidence)),
                        importance=Decimal('0.5'),
                        trigger_events=[
                            f"Contradicting evidence ({recent_contradicts}) exceeds supporting ({recent_supports})",
                            f"Unique sources: {unique_source_count}",
                            f"Verified: {is_verified}"
                        ],
                        evidence_sources=[str(e.id) for e in recent_evidence[:10]],
                        verified=is_verified  # Session 509: Set verification status
                    )
                    shift_id = str(shift.id)

                    # Log verification status
                    if is_verified:
                        logger.info(
                            f"✅ Created VERIFIED NarrativeShift for {narrative.title}: "
                            f"{shift_id} ({unique_source_count} sources)"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Created UNVERIFIED NarrativeShift for {narrative.title}: "
                            f"{shift_id} (only {unique_source_count} source(s))"
                        )

                    # Update narrative status to SHIFTING
                    narrative.status = NarrativeStatus.SHIFTING
                    narrative.save()

                result['shifts'].append({
                    'narrative_id': str(narrative.id),
                    'shift_id': shift_id,
                    'title': narrative.title,
                    'signal': 'Contradicting evidence exceeds supporting',
                    'confidence': adjusted_confidence if 'adjusted_confidence' in dir() else confidence,
                    'summary': shift_summary,
                    'verified': is_verified if 'is_verified' in dir() else False,
                    'unique_sources': unique_source_count if 'unique_source_count' in dir() else 0
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

        # 1. Historian Analysis - Session 895: Added timeout protection
        try:
            historian = NarrativeHistorianAgent(user=self.user)
            historian_task = f"Analyze the history of the narrative '{shift.old_narrative.title}' (ID: {shift.old_narrative.id}). What patterns led to this shift? Are there historical parallels?"

            def execute_historian():
                return historian.execute(historian_task, context, scifi_context, spider_context)

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_historian)
                historian_result = future.result(timeout=SUB_AGENT_TIMEOUT)

            if historian_result.success:
                analyses['agent_analyses']['historian'] = historian_result.message
                shift.historian_analysis = historian_result.message[:2000]
        except FuturesTimeoutError:
            logger.warning(f"⏰ NarrativeHistorianAgent timed out after {SUB_AGENT_TIMEOUT}s")
            analyses['agent_analyses']['historian'] = f"Timeout after {SUB_AGENT_TIMEOUT}s"
        except Exception as e:
            logger.error(f"Historian analysis failed: {e}")
            analyses['agent_analyses']['historian'] = f"Error: {str(e)}"

        # 2. Trend Break Analysis - Session 895: Added timeout protection
        try:
            trend_break = TrendBreakDetectorAgent(user=self.user)
            trend_task = f"Analyze the shift from '{shift.old_narrative.title}' to '{shift.new_narrative.title if shift.new_narrative else 'unknown'}'. What triggered it? How confident are we in this shift?"

            def execute_trend_break():
                return trend_break.execute(trend_task, context, scifi_context, spider_context)

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_trend_break)
                trend_result = future.result(timeout=SUB_AGENT_TIMEOUT)

            if trend_result.success:
                analyses['agent_analyses']['trend_break'] = trend_result.message
                shift.trend_break_analysis = trend_result.message[:2000]
        except FuturesTimeoutError:
            logger.warning(f"⏰ TrendBreakDetectorAgent timed out after {SUB_AGENT_TIMEOUT}s")
            analyses['agent_analyses']['trend_break'] = f"Timeout after {SUB_AGENT_TIMEOUT}s"
        except Exception as e:
            logger.error(f"Trend break analysis failed: {e}")
            analyses['agent_analyses']['trend_break'] = f"Error: {str(e)}"

        # 3. Cultural Impact Analysis - Session 895: Added timeout protection
        try:
            cultural = CulturalImpactAgent(user=self.user)
            cultural_task = f"Analyze the cultural impact of this narrative shift (ID: {shift_id}). What are the second-order effects? What actions should be taken?"

            def execute_cultural():
                return cultural.execute(cultural_task, context, scifi_context, spider_context)

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_cultural)
                cultural_result = future.result(timeout=SUB_AGENT_TIMEOUT)

            if cultural_result.success:
                analyses['agent_analyses']['cultural_impact'] = cultural_result.message
                shift.cultural_impact_analysis = cultural_result.message[:2000]
        except FuturesTimeoutError:
            logger.warning(f"⏰ CulturalImpactAgent timed out after {SUB_AGENT_TIMEOUT}s")
            analyses['agent_analyses']['cultural_impact'] = f"Timeout after {SUB_AGENT_TIMEOUT}s"
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

                    # Session 506: Use enhanced sentiment analyzer
                    # Features: 100+ weighted keywords, domain-specific terms,
                    # negation detection, contradiction phrases
                    sentiment, confidence = NarrativeSentimentAnalyzer.analyze(
                        content=content,
                        domain=narrative.domain,
                        narrative_title=narrative.title
                    )

                    # Session 509: Apply domain-specific source weighting
                    source_url = sd.source_url or ''
                    source_weight, is_preferred, is_penalized = get_source_weight(
                        source_url, narrative.domain
                    )

                    # Session 509: Mythology validation before storing evidence
                    from core.agents.narrative.narrative_mythology_validator import (
                        narrative_mythology_validator
                    )

                    # Get existing evidence count for corroboration check
                    existing_count = NarrativeEvidence.objects.filter(
                        narrative=narrative,
                        sentiment=sentiment
                    ).count()

                    validation = narrative_mythology_validator.validate_evidence(
                        source_url=source_url,
                        content=content,
                        domain=narrative.domain,
                        existing_evidence_count=existing_count
                    )

                    # Skip invalid evidence
                    if not validation['valid']:
                        logger.warning(
                            f"🚫 Rejected evidence for {narrative.domain}: "
                            f"{validation['warnings']}"
                        )
                        if 'rejected_evidence' not in results:
                            results['rejected_evidence'] = 0
                        results['rejected_evidence'] += 1
                        continue

                    # Apply validation multiplier to source weight
                    combined_multiplier = source_weight * validation['confidence_multiplier']

                    # Apply source weight to strength (capped at 1.0)
                    base_strength = 0.5 + (confidence * 0.3)  # 0.5 to 0.8 range
                    weighted_strength = min(1.0, base_strength * combined_multiplier)

                    # Log penalized or unreliable sources for debugging
                    if is_penalized:
                        logger.info(
                            f"⚠️ Penalized source for {narrative.domain}: {source_url[:50]} "
                            f"(weight: {source_weight})"
                        )

                    if validation['warnings']:
                        logger.info(
                            f"⚠️ Mythology warnings for {narrative.domain}: "
                            f"{validation['warnings']}"
                        )

                    # Create evidence with weighted strength
                    NarrativeEvidence.objects.create(
                        narrative=narrative,
                        spider_data=sd,
                        source_url=source_url,
                        source_title=first_title[:300] if first_title else sd.spider_name,
                        source_type=sd.data_type or '',
                        excerpt=content[:500],
                        sentiment=sentiment,
                        strength=Decimal(str(round(weighted_strength, 2))),
                        source_date=sd.created_at
                    )
                    results['new_evidence_created'] += 1

                    # Track source quality in results
                    if is_preferred or validation['is_authoritative']:
                        if 'preferred_sources' not in results:
                            results['preferred_sources'] = 0
                        results['preferred_sources'] += 1

                    if validation['verified']:
                        if 'verified_evidence' not in results:
                            results['verified_evidence'] = 0
                        results['verified_evidence'] += 1

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
            data_type__in=categories,
            created_at__gte=recent
        ).values('embedding_text').annotate(
            count=models.Count('id')
        ).order_by('-count')[:count * 2]

        created = []
        for item in spider_data:
            if len(created) >= count:
                break

            title = item['embedding_text']
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

    def _analyze_evidence_with_ml(self, evidence_texts: List[str], domain: str = None) -> Dict[str, Any]:
        """
        Session 683: Analyze narrative evidence using ML models.

        Uses DistilBERT for text classification to detect:
        - Sentiment patterns across evidence
        - Topic clustering
        - Anomalous narratives

        Args:
            evidence_texts: List of evidence text excerpts
            domain: Optional narrative domain for context

        Returns:
            Dict with ML analysis results
        """
        if not evidence_texts or len(evidence_texts) < 2:
            return {'ml_used': False, 'reason': 'Insufficient evidence texts'}

        try:
            # Build text data for ML analysis
            text_data = {
                'texts': evidence_texts[:50],  # Limit to 50 samples
                'domain': domain,
                'analysis_type': 'narrative_classification'
            }

            ml_result = analyze_narrative_text_with_ml(text_data)

            if ml_result.get('ml_used'):
                logger.info(
                    f"ML narrative analysis: {len(evidence_texts)} texts, "
                    f"models={ml_result.get('models_used')}, "
                    f"confidence={ml_result.get('confidence')}"
                )

            return ml_result

        except Exception as e:
            logger.warning(f"ML evidence analysis failed: {e}")
            return {'ml_used': False, 'reason': f'ML error: {str(e)}'}

    def _build_evidence_texts_for_ml(self, narrative_id: str, hours_back: int = 24) -> List[str]:
        """
        Session 683: Build list of evidence texts for ML analysis.

        Args:
            narrative_id: UUID of the narrative
            hours_back: Hours to look back for evidence

        Returns:
            List of evidence text excerpts
        """
        from core.models_narrative_drift import NarrativeEvidence

        try:
            cutoff = timezone.now() - timedelta(hours=hours_back)
            evidence = NarrativeEvidence.objects.filter(
                narrative_id=narrative_id,
                created_at__gte=cutoff
            ).values_list('excerpt', flat=True)[:50]

            return [e for e in evidence if e and len(e) > 20]

        except Exception as e:
            logger.warning(f"Failed to build evidence texts: {e}")
            return []

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
        import time
        from openai import OpenAI
        from django.conf import settings

        start_time = time.time()
        scifi_context = scifi_context or {}
        spider_context = spider_context or {}

        # Session 750: Time Travel integration
        with self.time_travel_session("narrative_drift_coordination", task, input_data=context):
            self.record_decision(
                decision_type="planning",
                action="Starting narrative drift coordination",
                reasoning=f"Processing task: {task[:100] if task else 'No task specified'}",
                alternatives=["Skip coordination", "Defer to human", "Consult other agents"],
                confidence=0.8
            )

            # Session 736: Extract spider intelligence for real-time data
            spider_intel = self._extract_spider_intelligence(spider_context)
            if spider_intel['has_data']:
                logger.info(f"🕷️ {self.name} using spider intelligence: {len(spider_intel['trends'])} trends")

            # Session 529: Build intelligent prompt with full context
            self._intelligent_context = self._build_intelligent_prompt(task, scifi_context, spider_context)

            logger.info(f"NarrativeDriftCoordinator executing: {task[:100]}...")

        # Use class-level system_prompt with additional instruction
        full_prompt = self.system_prompt + "\n\nAnalyze the task and decide which tool(s) to call. If no tools are needed, just respond with your analysis."

        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            messages = [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": task}
            ]

            # Call OpenAI with tools
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=messages,
                tools=self.get_tools_with_delegation(),
                tool_choice="auto",
                max_completion_tokens=2000
            )

            assistant_message = response.choices[0].message
            tool_calls_results = []

            # Handle tool calls if any
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    try:
                        tool_args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        tool_args = {}

                    logger.info(f"Executing tool: {tool_name}")
                    tool_result = self._handle_tool_call(tool_name, tool_args)
                    tool_calls_results.append({
                        'tool': tool_name,
                        'result': tool_result
                    })

            execution_time = int((time.time() - start_time) * 1000)

            # Session 683: Run ML analysis on any narrative evidence found
            ml_analysis = {'ml_used': False}
            try:
                # Get recent evidence texts for ML analysis
                from core.models_narrative_drift import Narrative, NarrativeEvidence
                from datetime import timedelta

                recent_narratives = Narrative.objects.filter(
                    status__in=['emerging', 'dominant', 'shifting']
                )[:5]

                all_evidence_texts = []
                for narrative in recent_narratives:
                    evidence_texts = self._build_evidence_texts_for_ml(
                        str(narrative.id), hours_back=24
                    )
                    all_evidence_texts.extend(evidence_texts)

                if all_evidence_texts:
                    ml_analysis = self._analyze_evidence_with_ml(
                        all_evidence_texts[:50],
                        domain=recent_narratives[0].domain if recent_narratives else None
                    )
            except Exception as e:
                logger.warning(f"ML integration in execute failed: {e}")

            cleaned_message = strip_simulated_tool_json(assistant_message.content) or "Task executed successfully"

            result = AgentResult(
                success=True,
                agent_name=self.name,
                message=cleaned_message,
                data={
                    'tool_calls': tool_calls_results,
                    'response': cleaned_message,
                    'ml_analysis': ml_analysis  # Session 683: ML insights
                },
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"NarrativeDriftCoordinator execution failed: {e}")
            execution_time = int((time.time() - start_time) * 1000)
            result = AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
                execution_time_ms=execution_time
            )

        # Record learning outcome for collective intelligence
        try:
            self._record_learning_outcome(
                task=task,
                result=result,
                success=result.success,
                context={
                    'agent_type': self.__class__.__name__,
                    'execution_time_ms': result.execution_time_ms,
                }
            )
        except Exception as le:
            logger.warning(f"Failed to record learning outcome: {le}")

        return result


# Need to import models for the aggregate query
from django.db import models
