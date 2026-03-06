"""
Mock Intelligence API endpoints for testing

QUARANTINED: These endpoints return synthetic data and are disabled in production.
Enable with INTELLIGENCE_VIEWS_ENABLED=true env var (or DEBUG=True).
"""

from django.conf import settings
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
import os
import random

logger = logging.getLogger(__name__)

_ENABLED = getattr(settings, 'DEBUG', False) or os.environ.get('INTELLIGENCE_VIEWS_ENABLED', '').lower() == 'true'


def _gate(request):
    """Block mock intelligence endpoints in production."""
    if not _ENABLED:
        logger.warning(
            "intelligence_views_disabled_hit route=%s user=%s referer=%s",
            request.path,
            getattr(request, 'user', 'anon'),
            request.META.get('HTTP_REFERER', '-'),
        )
        raise Http404


@csrf_exempt
@require_POST
def analyze_intelligence(request):
    """
    Mock endpoint for Universal Intelligence analysis
    Returns simulated intelligence data for testing
    """
    _gate(request)
    try:
        # Parse request body
        if request.body:
            data = json.loads(request.body or b"{}")
        else:
            data = {}

        # Generate mock intelligence response
        response = {
            "primary_action": random.choice(["STRONG_EXECUTE", "EXECUTE", "WAIT", "AVOID"]),
            "confidence": random.uniform(0.6, 0.95),
            "position_sizing": {
                "kelly_percentage": random.uniform(0.01, 0.05),
                "recommended_stake": random.randint(50, 500),
                "max_exposure": random.randint(500, 2000)
            },
            "risk_assessment": {
                "overall_risk": random.uniform(0.3, 0.7),
                "risk_factors": [
                    "Market volatility detected",
                    "Historical pattern suggests caution",
                    "Weather conditions may impact outcome"
                ][:random.randint(1, 3)],
                "mitigation_strategies": [
                    "Consider smaller position size",
                    "Set stop-loss at -2%",
                    "Monitor real-time updates"
                ][:random.randint(1, 3)]
            },
            "agent_consensus": {
                "alpha_squadron": random.uniform(0.6, 0.9),
                "bravo_squadron": random.uniform(0.5, 0.85),
                "charlie_squadron": random.uniform(0.55, 0.9),
                "delta_squadron": random.uniform(0.6, 0.88),
                "echo_squadron": random.uniform(0.65, 0.92)
            },
            "similar_scenarios": [
                {
                    "domain": random.choice(["SPORTS_BETTING", "TRADING", "CRYPTO"]),
                    "entity_id": f"scenario_{random.randint(100, 999)}",
                    "timestamp": "2024-01-15T14:30:00Z",
                    "outcome": random.choice(["SUCCESS", "FAILURE", "NEUTRAL"]),
                    "similarity": random.uniform(0.7, 0.95)
                }
                for _ in range(random.randint(1, 3))
            ],
            "cross_domain_patterns": [
                {
                    "pattern_name": random.choice([
                        "Momentum Reversal",
                        "Value Emergence",
                        "Sharp Money Movement",
                        "Public Fade Opportunity"
                    ]),
                    "confidence": random.uniform(0.7, 0.9),
                    "description": "Similar pattern detected across multiple domains",
                    "historical_success_rate": random.uniform(0.55, 0.75)
                }
                for _ in range(random.randint(1, 2))
            ],
            "memory_references": [
                f"mem_{random.randint(1000, 9999)}"
                for _ in range(random.randint(2, 5))
            ],
            "execution_plan": [
                "Monitor opening line movements",
                "Place position when confidence > 70%",
                "Set trailing stop at +5%",
                "Review after 2 hours"
            ][:random.randint(2, 4)]
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({
            "error": str(e),
            "message": "Failed to generate intelligence analysis"
        }, status=500)

@csrf_exempt
@require_POST
def search_memory(request):
    """
    Mock endpoint for memory search
    """
    _gate(request)
    try:
        # Generate mock memory search results
        response = {
            "memories": [
                {
                    "id": f"mem_{random.randint(1000, 9999)}",
                    "domain": random.choice(["SPORTS_BETTING", "TRADING", "CRYPTO"]),
                    "entity_id": f"entity_{random.randint(100, 999)}",
                    "timestamp": "2024-01-10T10:00:00Z",
                    "context": {
                        "market_conditions": "volatile",
                        "confidence": 0.75
                    },
                    "decision": random.choice(["EXECUTE", "WAIT", "AVOID"]),
                    "outcome": random.choice(["SUCCESS", "FAILURE"]),
                    "similarity_score": random.uniform(0.7, 0.95)
                }
                for _ in range(random.randint(3, 8))
            ],
            "patterns_found": [
                "Momentum Pattern",
                "Value Opportunity"
            ],
            "total_results": random.randint(10, 50)
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)

@csrf_exempt
def get_patterns(request):
    """
    Mock endpoint for pattern library
    """
    _gate(request)
    try:
        # Generate mock patterns
        patterns = [
            {
                "id": f"pattern_{random.randint(100, 999)}",
                "name": pattern_name,
                "description": "Cross-domain pattern with high success rate",
                "domains": random.sample(["SPORTS_BETTING", "TRADING", "CRYPTO", "REAL_ESTATE"],
                                       random.randint(1, 3)),
                "frequency": random.randint(10, 100),
                "success_rate": random.uniform(0.55, 0.85),
                "last_seen": "2024-01-14T12:00:00Z",
                "examples": [
                    {
                        "domain": random.choice(["SPORTS_BETTING", "TRADING"]),
                        "entity_id": f"example_{random.randint(100, 999)}",
                        "timestamp": "2024-01-12T15:30:00Z",
                        "outcome": random.choice(["SUCCESS", "FAILURE"])
                    }
                    for _ in range(random.randint(1, 3))
                ]
            }
            for pattern_name in [
                "Sharp Money Divergence",
                "Public Fade Setup",
                "Momentum Continuation",
                "Mean Reversion Signal",
                "Value Emergence Pattern"
            ]
        ]

        return JsonResponse(patterns, safe=False)

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)

@csrf_exempt
@require_POST
def submit_feedback(request):
    """
    Mock endpoint for intelligence feedback
    """
    _gate(request)
    try:
        # Just acknowledge the feedback
        return JsonResponse({
            "success": True,
            "message": "Feedback recorded successfully"
        })

    except Exception as e:
        return JsonResponse({
            "error": str(e)
        }, status=500)