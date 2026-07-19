"""Phase-0.5 accuracy analysis — wrapper over Phase-0 analyze.py against PHASE_0_5/corpus.json.

Per B1 §6 step 7 + Rigby S2825 SIGN Q1 refinement (2026-07-19):
Avoid mutating PHASE_0/analyze.py; author a Phase-0.5-local wrapper that
runs the same Classifier A + B evaluation logic against a corpus JSON of
this phase's choosing.

Usage (default: PHASE_0_5/corpus.json):

    python docs/research/discovery_layer/PHASE_0_5/analyze.py
    python docs/research/discovery_layer/PHASE_0_5/analyze.py --corpus docs/research/discovery_layer/PHASE_0_5/combined_corpus.json

Output: JSON accuracy report (per-family + provenance-tier stratified) —
authoritative for §2.2 stop-condition band verdict per Rigby S2825 Q2 SIGN.

The `analyze_router_log.py` companion in this directory analyzes live
router JSONL SoT (retrieval_error_rate + abstain distribution + operator
style distribution) — those are diagnostics for §10.4 methodology-back-to-
SIGN triggers, NOT the §2.2 verdict input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
PHASE_0_DIR = HERE.parent / "PHASE_0"

# Make Phase-0 classifier modules importable
sys.path.insert(0, str(PHASE_0_DIR))

from classifier_a import evaluate_against_corpus as eval_a  # noqa: E402
from classifier_b import evaluate_against_corpus as eval_b  # noqa: E402


STARTING_PRIORS = {
    "COUNT":          {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "PROCEDURAL":     {"consequence": "MEDIUM", "classifier_floor": 0.75, "substrate_floor": 0.70},
    "DISCOVERY":      {"consequence": "LOW",    "classifier_floor": 0.70, "substrate_floor": 0.60},
    "IDENTITY":       {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "SELF-REFERENCE": {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "CONCEPTUAL":     {"consequence": "LOW",    "classifier_floor": 0.70, "substrate_floor": 0.60},
}


def build_report(corpus_path: Path) -> dict:
    corpus = json.loads(corpus_path.read_text())
    a = eval_a(corpus_path)
    b = eval_b(corpus_path)

    families = ["COUNT", "PROCEDURAL", "DISCOVERY", "IDENTITY", "SELF-REFERENCE", "CONCEPTUAL"]
    side_by_side = {}
    for fam in families:
        pa = a["per_family"].get(fam, {"n_intended": 0, "f1": 0.0, "precision": 0.0, "recall": 0.0})
        pb = b["per_family"].get(fam, {"n_intended": 0, "f1": 0.0, "precision": 0.0, "recall": 0.0})
        prior = STARTING_PRIORS[fam]
        f1_a = pa["f1"] or 0.0
        f1_b = pb["f1"] or 0.0
        side_by_side[fam] = {
            "n": pa["n_intended"],
            "consequence": prior["consequence"],
            "classifier_floor_prior": prior["classifier_floor"],
            "a_f1": f1_a,
            "b_f1": f1_b,
            "a_meets_floor": f1_a >= prior["classifier_floor"],
            "b_meets_floor": f1_b >= prior["classifier_floor"],
            "a_precision": pa["precision"],
            "a_recall": pa["recall"],
            "b_precision": pb["precision"],
            "b_recall": pb["recall"],
            "delta_f1_b_minus_a": f1_b - f1_a,
        }

    per_tier_a = a.get("per_tier", {})
    per_tier_b = b.get("per_tier", {})

    def detect_operator_style(row):
        src = (row.get("provenance_source") or "").lower()
        rationale = (row.get("label_rationale") or "").lower()[:80]
        if "chris" in src or "chatui_conversation_search" in src or rationale.startswith("chris"):
            return "chris"
        if "benchmark" in src or rationale.startswith("claude"):
            return "claude"
        if "pa_task_summary" in src or rationale.startswith("rigby"):
            return "rigby"
        return None

    per_operator_style = {}
    for row in corpus["rows"]:
        style = detect_operator_style(row)
        if style is None:
            continue
        per_operator_style.setdefault(style, {"n": 0, "correct_a": 0, "correct_b": 0})
        per_operator_style[style]["n"] += 1
        row_a = next((r for r in a["row_results"] if r["query_id"] == row["query_id"]), None)
        row_b = next((r for r in b["row_results"] if r["query_id"] == row["query_id"]), None)

        def row_correct(rr):
            if not rr:
                return False
            if rr.get("is_ambiguous_ground_truth"):
                return bool(rr.get("ambig_gt_correct"))
            return rr["predicted_family"] == rr["intended_family"]

        if row_correct(row_a):
            per_operator_style[style]["correct_a"] += 1
        if row_correct(row_b):
            per_operator_style[style]["correct_b"] += 1

    for style, agg in per_operator_style.items():
        if agg["n"] > 0:
            agg["accuracy_a"] = agg["correct_a"] / agg["n"]
            agg["accuracy_b"] = agg["correct_b"] / agg["n"]

    report = {
        "corpus_path": str(corpus_path),
        "schema_version": corpus.get("schema_version"),
        "session": corpus.get("session"),
        "phase": corpus.get("phase"),
        "row_count": len(corpus["rows"]),
        "provenance_summary": corpus.get("provenance_summary", {}),
        "operator_style_balance": corpus.get("operator_style_balance", {}),
        "per_family": side_by_side,
        "per_provenance_tier_a": per_tier_a,
        "per_provenance_tier_b": per_tier_b,
        "per_operator_style": per_operator_style,
        "wrong_but_plausible": {
            "a": {"count": a["wrong_but_plausible_count"], "queries": a["wrong_but_plausible_queries"]},
            "b": {"count": b["wrong_but_plausible_count"], "queries": b["wrong_but_plausible_queries"]},
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        type=Path,
        default=HERE / "corpus.json",
        help="Path to Phase-0.5 corpus JSON (default: PHASE_0_5/corpus.json).",
    )
    args = parser.parse_args()

    if not args.corpus.exists():
        print(f"[ERROR] corpus not found: {args.corpus}", file=sys.stderr)
        return 1

    report = build_report(args.corpus)
    print(json.dumps(report, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
