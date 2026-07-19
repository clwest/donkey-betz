"""Phase-0.5 router-log extraction + measurement-report analysis.

Per S2823 constitutional package (B3 §10.6.2 R4 durable-evidence discipline
+ B2 §6 SoT declaration): JSONL is the SOURCE OF TRUTH; this script reads
JSONL primarily and uses the Django `Phase0_5RouterEvent` mirror only as a
query accelerator. If a divergence between JSONL and mirror is observed,
this script REPORTS it (and does NOT reconcile) per Chris §15.4 "integrity
event, not silent reconciliation."

Usage:

    python docs/research/discovery_layer/PHASE_0_5/analyze_router_log.py \
        --router-log logs/phase_0_5_router.jsonl \
        --integrity-log logs/phase_0_5_integrity_events.jsonl \
        [--window <measurement_window_id>]  \
        [--verify-mirror]

Output: JSON report suitable for feeding Phase-0.5 measurement_report.md
§NEW abstain-analysis section (per B3 §4.2).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROUTER_DECISION = "router_decision"
WINDOW_START = "window_start"
WINDOW_END = "window_end"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                print(
                    f"[WARN] {path.name}:{line_no} JSON parse error: {exc}",
                    file=sys.stderr,
                )
    return rows


def analyze_router_log(rows: list[dict[str, Any]], window_id: str | None) -> dict[str, Any]:
    """Analyze router-log rows.

    Categorical-only per B3 §10.4 — no numeric confidence aggregation.
    Reports per-window counts + rates + abstain distribution + retrieval
    error rate (Rigby S2824 Q4 measurement-bias fix).
    """
    decisions = [r for r in rows if r.get("row_type") == ROUTER_DECISION]
    starts = [r for r in rows if r.get("row_type") == WINDOW_START]
    ends = [r for r in rows if r.get("row_type") == WINDOW_END]

    if window_id is not None:
        decisions = [r for r in decisions if r.get("measurement_window_id") == window_id]
        starts = [r for r in starts if r.get("measurement_window_id") == window_id]
        ends = [r for r in ends if r.get("measurement_window_id") == window_id]

    n = len(decisions)
    if n == 0:
        return {
            "n_routed_decisions": 0,
            "window_starts": len(starts),
            "window_ends": len(ends),
            "window_id_filter": window_id,
            "message": "No router decisions found for the specified filter.",
        }

    families = Counter(d.get("predicted_family") or "(null-abstain)" for d in decisions)
    abstain_reasons = Counter(d.get("abstain_reason") for d in decisions if d.get("abstain_reason"))
    abstain_options = Counter(d.get("abstain_option") for d in decisions if d.get("abstain_option"))
    confidence = Counter(d.get("confidence_categorical") for d in decisions)
    operator_style = Counter(d.get("operator_style") or "unknown" for d in decisions)

    retrieval_errors = [d for d in decisions if d.get("retrieval_error")]
    retrieval_error_by_type = Counter(
        d.get("retrieval_exception_type") for d in retrieval_errors
    )

    # Recommendation follow-through (per B3 §10.7 5th field).
    followed = Counter(
        d.get("router_recommendation_followed") for d in decisions
        if d.get("router_recommendation_followed") is not None
    )

    # UNCLASSIFIABLE by operator style + query length bucket (per B3 §2.3 R2).
    unclass_by_style: Counter[Any] = Counter()
    unclass_by_len_bucket: Counter[Any] = Counter()
    for d in decisions:
        if d.get("abstain_reason") == "UNCLASSIFIABLE":
            unclass_by_style[d.get("operator_style") or "unknown"] += 1
            wc = len((d.get("original_query") or "").split())
            bucket = (
                "1-2" if wc <= 2 else "3-4" if wc <= 4 else "5-8" if wc <= 8 else "9+"
            )
            unclass_by_len_bucket[bucket] += 1

    # CONTEXT_NEEDED cap breach evaluation per B3 §2.4.
    ctx_needed = [d for d in decisions if d.get("abstain_reason") == "CONTEXT_NEEDED"]
    clarify_rate = len(ctx_needed) / n
    clarify_ctx_type = Counter(
        d.get("clarify_context_type") for d in ctx_needed
        if d.get("clarify_context_type")
    )

    return {
        "n_routed_decisions": n,
        "window_id_filter": window_id,
        "window_starts": len(starts),
        "window_ends": len(ends),
        "predicted_family_distribution": dict(families),
        "abstain_reason_distribution": dict(abstain_reasons),
        "abstain_option_distribution": dict(abstain_options),
        "confidence_categorical_distribution": dict(confidence),
        "operator_style_distribution": dict(operator_style),
        "abstain_rate": (
            (abstain_reasons.get("AMBIGUOUS", 0) + abstain_reasons.get("UNCLASSIFIABLE", 0)) / n
        ),
        "ambiguous_rate": abstain_reasons.get("AMBIGUOUS", 0) / n,
        "unclassifiable_rate": abstain_reasons.get("UNCLASSIFIABLE", 0) / n,
        "context_needed_rate": abstain_reasons.get("CONTEXT_NEEDED", 0) / n,
        "clarify_rate": clarify_rate,
        "clarify_context_type_ratio": dict(clarify_ctx_type),
        "unclassifiable_by_operator_style": dict(unclass_by_style),
        "unclassifiable_by_query_length_bucket": dict(unclass_by_len_bucket),
        "retrieval_error_count": len(retrieval_errors),
        "retrieval_error_rate": len(retrieval_errors) / n,
        "retrieval_error_by_exception_type": dict(retrieval_error_by_type),
        "router_recommendation_followed_distribution": dict(followed),
    }


def analyze_integrity_events(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"n_integrity_events": 0}
    by_trigger = Counter(r.get("trigger_id") for r in rows)
    return {
        "n_integrity_events": len(rows),
        "trigger_distribution": dict(by_trigger),
        "events": [
            {
                "event_id": r.get("event_id"),
                "ts": r.get("ts"),
                "trigger_id": r.get("trigger_id"),
                "reason": r.get("reason"),
                "measurement_window_id": (r.get("context") or {}).get("measurement_window_id"),
            }
            for r in rows
        ],
    }


def verify_mirror(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Report SoT vs mirror divergence per Chris R4 (§15.4).

    NEVER silently reconciles. Returns a report — divergences are surfaced
    for a human/Rigby SIGN + Chris D-verdict per §12 evidence-integrity
    trigger MIRROR_DIVERGENCE.
    """
    jsonl_event_ids: set[str] = {
        str(r["event_id"]) for r in rows if r.get("event_id")
    }
    try:
        import django  # noqa: F401
        django.setup()
        from persistence.models import Phase0_5RouterEvent  # type: ignore
    except Exception as exc:
        return {
            "verify_mirror": "SKIPPED",
            "reason": f"Django import failed (run under `python manage.py shell`): {exc}",
        }
    model_event_ids: set[str] = {
        str(event_id)
        for event_id in Phase0_5RouterEvent.objects.values_list("event_id", flat=True)
    }
    in_jsonl_not_model = sorted(jsonl_event_ids - model_event_ids)
    in_model_not_jsonl = sorted(model_event_ids - jsonl_event_ids)
    return {
        "verify_mirror": "OK" if not (in_jsonl_not_model or in_model_not_jsonl) else "DIVERGENCE",
        "n_jsonl_events": len(jsonl_event_ids),
        "n_model_events": len(model_event_ids),
        "in_jsonl_not_model": in_jsonl_not_model[:100],
        "in_model_not_jsonl": in_model_not_jsonl[:100],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--router-log",
        type=Path,
        default=Path("logs/phase_0_5_router.jsonl"),
        help="Path to router JSONL SoT.",
    )
    parser.add_argument(
        "--integrity-log",
        type=Path,
        default=Path("logs/phase_0_5_integrity_events.jsonl"),
        help="Path to integrity-events JSONL.",
    )
    parser.add_argument(
        "--window",
        type=str,
        default=None,
        help="Filter to a specific measurement_window_id.",
    )
    parser.add_argument(
        "--verify-mirror",
        action="store_true",
        help="Also verify JSONL vs Django Phase0_5RouterEvent mirror.",
    )
    args = parser.parse_args()

    router_rows = read_jsonl(args.router_log)
    integrity_rows = read_jsonl(args.integrity_log)

    report: dict[str, Any] = {
        "router_log_analysis": analyze_router_log(router_rows, args.window),
        "integrity_events": analyze_integrity_events(integrity_rows),
    }
    if args.verify_mirror:
        report["mirror_verification"] = verify_mirror(router_rows)

    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
