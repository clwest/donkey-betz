"""
Session 2978: Theme Signals v1 service — Phase A.

Renders SignalCluster rows into "Buildable" and "Investable" cards for the
new Workspace tab. Deterministic strict-gate posture (Chris ratification,
spec deliverable `63ec4d1d-9425-468b-815c-b4e571e3fe44`):

- Deterministic tab routing (Investable wins ties)
- Strict quality gate: title-block regex + evidence density + confidence
- Card contract: title / why_now / evidence / so_what / confidence(+drivers)
- Investable variant adds `who_benefits_who_loses` = Phase B placeholder

TODO(Phase B): unify BUILDABLE_SOURCES + INVESTABLE_SOURCES with
`core/services/signal_aggregation_service.py` source classification once the
product-tier gate stabilises. Kept standalone here to decouple UI semantics
from raw aggregation churn (T1 zoom-out Z1, same_pr_mitigatable).
"""

from __future__ import annotations

import logging
import re
from datetime import timedelta
from typing import Any, Dict, List, Literal, Optional, Tuple

from django.utils import timezone

from core.services.evidence_display import (
    evidence_from_sample_signals,
    normalize_evidence_row,
    sort_evidence_by_relevance,
)

logger = logging.getLogger(__name__)

Tab = Literal["buildable", "investable"]
RouteResult = Literal["buildable", "investable", "neither"]

# -- Spec-lifted constants (deliverable 63ec4d1d §Phase A v1 Routing) -----

BUILDABLE_SOURCES = frozenset({
    "hackernews", "huggingface", "devto", "producthunt", "github",
    "techcrunch", "techcrunch_startups", "venturebeat", "arstechnica",
    "theverge", "wired", "mit_tech_review", "freecodecamp",
    "smashingmagazine", "kaggle",
})

INVESTABLE_SOURCES = frozenset({
    "sec_edgar", "yahoo_finance", "finnhub", "reuters_rss",
    "google_news", "newsapi", "financial", "business_news",
    "axios", "bbc", "npr", "polygon_finance",
})

CATALYST_KEYWORDS = frozenset({
    # SEC / filings
    "sec", "edgar", "8-k", "8k", "10-k", "10k", "10-q", "10q",
    "s-1", "s1", "f-1", "f1", "prospectus", "registration statement",
    # Earnings / guidance
    "earnings", "quarterly results", "q1", "q2", "q3", "q4",
    "guidance", "revenue", "eps", "margin", "outlook",
    # Macro / rates / inflation
    "cpi", "inflation", "fomc", "fed", "rate cut", "rate hike",
    "interest rates", "jobs report", "nonfarm payrolls", "pce",
    # Capital structure
    "buyback", "share repurchase", "dividend", "secondary offering",
    "dilution", "convertible notes",
})

BLOCKED_TITLE_PATTERNS: List[re.Pattern] = [
    re.compile(r"^\s*discussion\s*[,\s]+\s*link", re.IGNORECASE),
    re.compile(r"^\s*link\s*[,\s]+\s*discussion", re.IGNORECASE),
    re.compile(r"^\s*comments\s*[,\s]+\s*score", re.IGNORECASE),
    re.compile(r"^\s*score\s*[,\s]+\s*comments", re.IGNORECASE),
]

BLOCKED_LEAD_TOKENS = frozenset({"discussion", "comments", "link", "score"})

MIN_SOURCES = 3
MIN_ITEMS = 5

MIN_CONFIDENCE_BUILDABLE = 0.60
MIN_CONFIDENCE_INVESTABLE = 0.65

MAX_EVIDENCE = 7

# Pattern-type → user-facing suggested action.
_SO_WHAT_ACTION = {
    "trend_emergence": "watch",
    "demand_spike": "research",
    "opportunity_window": "build/trade",
    "knowledge_gap": "research",
    "skill_demand": "research",
    "content_gap": "build",
    "sentiment_shift": "watch",
    "market_movement": "trade",
    "competitive_signal": "research",
    "user_need": "build",
}

_PATTERN_TYPE_PROSE = {
    "trend_emergence": "Emerging trend",
    "demand_spike": "Demand spike",
    "opportunity_window": "Opportunity window",
    "knowledge_gap": "Knowledge gap surfacing",
    "skill_demand": "Skill demand rising",
    "content_gap": "Content gap",
    "sentiment_shift": "Sentiment shift",
    "market_movement": "Market movement",
    "competitive_signal": "Competitive signal",
    "user_need": "Emerging user need",
}


# -- Routing --------------------------------------------------------------


def _has_catalyst_keyword(keywords: List[str], title: str) -> bool:
    text_hay = (title or "").lower()
    for kw in keywords or []:
        low = str(kw or "").lower()
        for cat in CATALYST_KEYWORDS:
            if cat in low or cat in text_hay:
                return True
    return False


def route_cluster(cluster) -> RouteResult:
    """Deterministic tab routing. Investable wins ties.

    Investable if: any source in INVESTABLE_SOURCES, OR any catalyst kw in
    title/keywords. Buildable if: any source in BUILDABLE_SOURCES. Else neither.
    """
    sb = cluster.source_breakdown or {}
    source_names = set(sb.keys()) if isinstance(sb, dict) else set()
    keywords = list(cluster.keywords or [])

    if source_names & INVESTABLE_SOURCES:
        return "investable"
    if _has_catalyst_keyword(keywords, cluster.name or ""):
        return "investable"
    if source_names & BUILDABLE_SOURCES:
        return "buildable"
    return "neither"


# -- Quality gate ---------------------------------------------------------


def _title_blocked(name: str) -> bool:
    if not name:
        return True
    for pat in BLOCKED_TITLE_PATTERNS:
        if pat.search(name):
            return True
    lowered = name.lower().strip()
    tokens = [t for t in re.split(r"[,\s]+", lowered) if t]
    if not tokens:
        return True
    if tokens[0] in BLOCKED_LEAD_TOKENS:
        meaningful = [
            t for t in tokens if t not in BLOCKED_LEAD_TOKENS and len(t) > 2
        ]
        if len(meaningful) < 2:
            return True
    return False


def _evidence_dense_enough(cluster) -> bool:
    sb = cluster.source_breakdown or {}
    n_sources = len(sb.keys()) if isinstance(sb, dict) else 0
    n_items = len(cluster.spider_data_ids or [])
    return n_sources >= MIN_SOURCES or n_items >= MIN_ITEMS


def _confidence_threshold_for(tab: RouteResult) -> float:
    if tab == "investable":
        return MIN_CONFIDENCE_INVESTABLE
    return MIN_CONFIDENCE_BUILDABLE


def passes_quality_gate(
    cluster, route: RouteResult, min_confidence_override: Optional[float] = None
) -> Tuple[bool, str]:
    """Return (passed, reason_code). Reason codes: ok / title_blocked /
    evidence_fail / conf_fail / routed_neither."""
    if route == "neither":
        return False, "routed_neither"
    if _title_blocked(cluster.name or ""):
        return False, "title_blocked"
    if not _evidence_dense_enough(cluster):
        return False, "evidence_fail"
    threshold = (
        min_confidence_override
        if min_confidence_override is not None
        else _confidence_threshold_for(route)
    )
    if float(cluster.confidence or 0) < threshold:
        return False, "conf_fail"
    return True, "ok"


# -- Evidence extraction --------------------------------------------------


def _items_from_row(row) -> List[Dict[str, Any]]:
    """Extract raw_data['items'] defensively (list-shaped raw_data → [])."""
    raw = getattr(row, "raw_data_dict", None)
    if raw is None:
        raw = row.raw_data
    if not isinstance(raw, dict):
        return []
    items = raw.get("items") or []
    if not isinstance(items, list):
        return []
    return items


def _extract_evidence_from_row_items(row, items, out: List[Dict[str, Any]], max_items: int) -> bool:
    """Append valid evidence entries from a row's items list.

    Each entry passes through ``normalize_evidence_row``, which applies
    URL sanitization (Bluesky ``at://`` transform + http/https allowlist)
    and source-label mapping (raw slug → display label). Rows where the
    normalized title AND url are both empty are silently skipped. Returns
    True when ``out`` is full.
    """
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get("title") or item.get("headline") or item.get("name")
        url = item.get("url") or item.get("link") or item.get("source_url")
        if not title and not url:
            continue
        row_entry = normalize_evidence_row(
            title=title,
            url=url,
            source=item.get("source") or row.spider_name,
            published=item.get("published"),
        )
        if row_entry is None:
            continue
        out.append(row_entry)
        if len(out) >= max_items:
            return True
    return False


def extract_evidence_from_cluster(cluster, max_items: int = MAX_EVIDENCE) -> List[Dict[str, Any]]:
    """Flatten evidence for one cluster: primary spider_data_ids path,
    with ``sample_signals`` as fallback when primary yields zero items.

    Primary — ``LegacySpiderData.raw_data['items']`` across cluster rows:
      title: item.get('title') or item.get('headline') or item.get('name')
      url:   item.get('url')   or item.get('link')     or item.get('source_url')

    Skip items where both title AND url are missing. Skip rows where
    ``raw_data`` is not dict-shaped (defends against list-shaped payloads).
    Fallback — ``SignalCluster.sample_signals`` (only when primary is empty):
    Chris ratified Option B at S2979 — sample_signals is lower-integrity
    (mixed source/url pairings, blobby text) so it stays a fallback, never
    preferred over the primary path.
    Results are relevance-sorted (clickable before unclickable, real
    titles before placeholders).
    """
    from core.models_unified_system import LegacySpiderData

    out: List[Dict[str, Any]] = []
    ids = cluster.spider_data_ids or []
    if ids:
        for row in LegacySpiderData.objects.filter(id__in=ids):
            if _extract_evidence_from_row_items(row, _items_from_row(row), out, max_items):
                break
    if not out:
        out = evidence_from_sample_signals(cluster.sample_signals, max_items)
    return sort_evidence_by_relevance(out)


def _prefetch_evidence_for_clusters(clusters) -> Dict[str, List[Dict[str, Any]]]:
    """Batch-fetch evidence for all survivor clusters in one query.

    Applies the same primary/fallback logic as ``extract_evidence_from_cluster``
    but issues a single ``LegacySpiderData.objects.filter(id__in=...)`` for
    the union of ``spider_data_ids`` across all survivors. Returns
    ``{cluster_id: [evidence...]}`` pre-computed. Eliminates N+1 across the
    survivors loop when rendering >1 card (A2 SIGN Z-A2 fold #1).
    """
    from core.models_unified_system import LegacySpiderData

    all_ids: List[str] = []
    per_cluster: Dict[str, List[str]] = {}
    for c in clusters:
        ids = [str(i) for i in (c.spider_data_ids or [])]
        per_cluster[str(c.id)] = ids
        all_ids.extend(ids)

    row_by_id: Dict[str, Any] = {}
    if all_ids:
        row_by_id = {
            str(row.id): row
            for row in LegacySpiderData.objects.filter(id__in=list(set(all_ids)))
        }

    out: Dict[str, List[Dict[str, Any]]] = {}
    for c in clusters:
        cid = str(c.id)
        evidence: List[Dict[str, Any]] = []
        for i in per_cluster.get(cid, []):
            row = row_by_id.get(i)
            if row is None:
                continue
            if _extract_evidence_from_row_items(row, _items_from_row(row), evidence, MAX_EVIDENCE):
                break
        if not evidence:
            evidence = evidence_from_sample_signals(c.sample_signals, MAX_EVIDENCE)
        out[cid] = sort_evidence_by_relevance(evidence)
    return out


# -- Card shaping ---------------------------------------------------------


def _derive_why_now(cluster) -> str:
    """Phase A deterministic template: pattern-type + source count + top-3
    source names + item count. Replaced (not restructured) in Phase B."""
    prose = _PATTERN_TYPE_PROSE.get(cluster.pattern_type or "", "Signal")
    sb = cluster.source_breakdown or {}
    if not isinstance(sb, dict):
        sb = {}
    source_names = list(sb.keys())
    top_sources = source_names[:3]
    n_sources = len(source_names)
    n_items = len(cluster.spider_data_ids or [])
    if top_sources:
        srcs = ", ".join(top_sources)
        if n_sources > 3:
            srcs += f" (+{n_sources - 3} more)"
        return f"{prose} across {n_sources} source(s): {srcs}. {n_items} item(s) observed."
    return f"{prose} — {n_items} item(s) observed."


def _confidence_drivers(cluster) -> str:
    sb = cluster.source_breakdown or {}
    if not isinstance(sb, dict) or not sb:
        return "no source signal"
    parts = [f"{name} × {n}" for name, n in sorted(sb.items(), key=lambda p: -p[1])]
    return ", ".join(parts)


def cluster_to_card(
    cluster,
    tab: Tab,
    evidence_override: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Shape a cluster into a card. When `evidence_override` is provided
    (batch prefetch path), skip the per-cluster DB fetch."""
    evidence = (
        evidence_override
        if evidence_override is not None
        else extract_evidence_from_cluster(cluster)
    )
    card: Dict[str, Any] = {
        "id": str(cluster.id),
        "title": cluster.name or "(untitled)",
        "why_now": _derive_why_now(cluster),
        "why_now_note": "(Phase A template — expanded in Phase B)",
        "evidence": evidence,
        "so_what": _SO_WHAT_ACTION.get(cluster.pattern_type or "", "watch"),
        "confidence": round(float(cluster.confidence or 0), 3),
        "confidence_drivers": _confidence_drivers(cluster),
        "pattern_type": cluster.pattern_type or "",
        "detected_at": (
            cluster.detected_at.isoformat() if cluster.detected_at else None
        ),
    }
    if tab == "investable":
        card["who_benefits_who_loses"] = {
            "status": "coming_in_phase_b",
            "message": "Sector + example tickers coming in Phase B",
        }
    return card


# -- Public entrypoint ----------------------------------------------------

MAX_DAYS = 30
MAX_LIMIT = 50
DEFAULT_DAYS = 7
DEFAULT_LIMIT = 20


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


def get_theme_signals(
    tab: Tab = "buildable",
    days: int = DEFAULT_DAYS,
    limit: int = DEFAULT_LIMIT,
    min_confidence: Optional[float] = None,
) -> Dict[str, Any]:
    """Load recent clusters, apply routing + quality gate, shape into cards.

    Returns:
      {tab, days, limit, cards, total_scanned, total_survived,
       gate_reasons: {title_blocked, evidence_fail, conf_fail, routed_other_tab}}
    """
    from core.models import SignalCluster

    tab_value = "investable" if tab == "investable" else "buildable"
    days_c = _clamp(int(days or DEFAULT_DAYS), 1, MAX_DAYS)
    limit_c = _clamp(int(limit or DEFAULT_LIMIT), 1, MAX_LIMIT)
    conf_override: Optional[float] = None
    if min_confidence is not None:
        conf_override = max(0.0, min(1.0, float(min_confidence)))

    cutoff = timezone.now() - timedelta(days=days_c)
    qs = SignalCluster.objects.filter(detected_at__gte=cutoff).order_by("-detected_at")

    total_scanned = 0
    gate_reasons = {
        "title_blocked": 0,
        "evidence_fail": 0,
        "conf_fail": 0,
        "routed_other_tab": 0,
    }
    survivors = []
    for cluster in qs.iterator():
        total_scanned += 1
        route = route_cluster(cluster)
        if route != tab_value:
            # If it belongs to the other tab (or neither), account for it.
            if route in ("buildable", "investable"):
                gate_reasons["routed_other_tab"] += 1
            # routed_neither counted below via passes_quality_gate
        passed, reason = passes_quality_gate(cluster, route, conf_override)
        if not passed:
            if reason in gate_reasons:
                gate_reasons[reason] += 1
            continue
        if route != tab_value:
            # Passed its own gate but not this tab; already counted above.
            continue
        survivors.append(cluster)
        if len(survivors) >= limit_c:
            break

    # Batch-fetch all LegacySpiderData for survivors in ONE query, eliminates
    # per-card DB roundtrip. See A2 SIGN Z-A2 fold #1.
    prefetched = _prefetch_evidence_for_clusters(survivors)
    cards = [
        cluster_to_card(c, tab_value, evidence_override=prefetched.get(str(c.id), []))
        for c in survivors
    ]
    return {
        "tab": tab_value,
        "days": days_c,
        "limit": limit_c,
        "min_confidence_applied": (
            conf_override if conf_override is not None
            else _confidence_threshold_for(tab_value)
        ),
        "cards": cards,
        "total_scanned": total_scanned,
        "total_survived": len(cards),
        "gate_reasons": gate_reasons,
    }
