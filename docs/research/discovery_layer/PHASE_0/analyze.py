"""Phase-0 comprehensive analysis — combines Classifier A + B outputs.

Produces:
- Side-by-side per-family metrics
- Wrong-but-plausible catalog (R5 priority)
- Context-needed analysis per R4 (query-text-only, then post-hoc labeling)
- Per-family gate evaluation vs §7.6 starting priors (R2)
- Provenance-tier stratified accuracy (do P1 vs P2 vs P3 behave differently?)
"""
from __future__ import annotations

import json
from pathlib import Path

from classifier_a import evaluate_against_corpus as eval_a
from classifier_b import evaluate_against_corpus as eval_b

HERE = Path(__file__).parent
CORPUS_PATH = HERE / "corpus.json"


# S2821 §7.6 starting priors (Chris R2: NOT optimization targets)
STARTING_PRIORS = {
    "COUNT":          {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "PROCEDURAL":     {"consequence": "MEDIUM", "classifier_floor": 0.75, "substrate_floor": 0.70},
    "DISCOVERY":      {"consequence": "LOW",    "classifier_floor": 0.70, "substrate_floor": 0.60},
    "IDENTITY":       {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "SELF-REFERENCE": {"consequence": "HIGH",   "classifier_floor": 0.90, "substrate_floor": 0.85},
    "CONCEPTUAL":     {"consequence": "LOW",    "classifier_floor": 0.70, "substrate_floor": 0.60},
}


def build_report():
    a = eval_a()
    b = eval_b()
    corpus = json.loads(CORPUS_PATH.read_text())
    rows_by_id = {r["query_id"]: r for r in corpus["rows"]}

    # Per-family side-by-side
    families = ["COUNT", "PROCEDURAL", "DISCOVERY", "IDENTITY", "SELF-REFERENCE", "CONCEPTUAL"]
    side_by_side = {}
    for fam in families:
        pa = a["per_family"][fam]
        pb = b["per_family"][fam]
        prior = STARTING_PRIORS[fam]
        # F1 vs classifier_floor
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

    # Wrong-but-plausible catalog (R5)
    wbp = {
        "a": {
            "count": a["wrong_but_plausible_count"],
            "queries": a["wrong_but_plausible_queries"],
        },
        "b": {
            "count": b["wrong_but_plausible_count"],
            "queries": b["wrong_but_plausible_queries"],
        },
    }

    # Context-needed analysis (R4): rows where either classifier output CONTEXT_NEEDED
    # + post-hoc labeling of rows we WOULD have flagged as context-needed given corpus data.
    context_needed_actual = []
    for row in corpus["rows"]:
        row_a = next(r for r in a["row_results"] if r["query_id"] == row["query_id"])
        row_b = next(r for r in b["row_results"] if r["query_id"] == row["query_id"])
        # Post-hoc: rows with secondary_family set AND strict=null AND query is context-dependent
        posthoc_context_needed = bool(row.get("secondary_family")) and row["known_correct_target_strict"] is None
        entry = {
            "query_id": row["query_id"],
            "query_text": row["query_text"],
            "intended_family": row["intended_family"],
            "secondary_family": row.get("secondary_family"),
            "classifier_a_output": row_a["predicted_family"],
            "classifier_b_output": row_b["predicted_family"],
            "posthoc_context_needed": posthoc_context_needed,
            # Context type (Rigby refinement): categorize
            "context_type": None,
        }
        # Categorize context type
        qt = row["query_text"].lower()
        if any(w in qt for w in ["current", "this", "that", "it"]) and len(qt.split()) <= 4:
            entry["context_type"] = "conversational"  # pronoun/definite ref
        elif "models" in qt and "how many" in qt:
            entry["context_type"] = "operational"  # scope ambiguity (which type of model)
        elif "session" in qt and any(str(i) in qt for i in range(2000, 3000)):
            entry["context_type"] = "operational"  # which artifact of the session
        elif len(qt.split()) <= 3 and any(w in qt for w in ["spider network", "morning brief"]):
            entry["context_type"] = "operational"  # bare noun scope ambiguity
        # else: leave None
        context_needed_actual.append(entry)

    context_needed_summary = {
        "n_posthoc_flagged": sum(1 for e in context_needed_actual if e["posthoc_context_needed"]),
        "n_classifier_a_flagged": sum(1 for e in context_needed_actual if e["classifier_a_output"] == "CONTEXT_NEEDED"),
        "n_classifier_b_flagged": sum(1 for e in context_needed_actual if e["classifier_b_output"] == "CONTEXT_NEEDED"),
        "by_type": {
            "conversational": sum(1 for e in context_needed_actual if e.get("context_type") == "conversational"),
            "operational": sum(1 for e in context_needed_actual if e.get("context_type") == "operational"),
            "repository": sum(1 for e in context_needed_actual if e.get("context_type") == "repository"),
        },
        "posthoc_flagged_queries": [e["query_id"] for e in context_needed_actual if e["posthoc_context_needed"]],
    }

    # Provenance-tier stratified accuracy
    tier_accuracy = {"P1": {}, "P2": {}, "P3": {}}
    for tier in ["P1", "P2", "P3"]:
        tier_ids = {r["query_id"] for r in corpus["rows"] if r["provenance_tier"] == tier}
        a_correct = sum(1 for r in a["row_results"] if r["query_id"] in tier_ids and r["predicted_family"] == r["intended_family"])
        b_correct = sum(1 for r in b["row_results"] if r["query_id"] in tier_ids and r["predicted_family"] == r["intended_family"])
        tier_accuracy[tier] = {
            "n": len(tier_ids),
            "a_accuracy": a_correct / len(tier_ids) if tier_ids else 0,
            "b_accuracy": b_correct / len(tier_ids) if tier_ids else 0,
        }

    # Recommended floor calibration (R2: evidence-forward)
    calibration_notes = {}
    for fam in families:
        s = side_by_side[fam]
        max_observed = max(s["a_f1"], s["b_f1"])
        prior = s["classifier_floor_prior"]
        if max_observed >= prior:
            calibration_notes[fam] = f"prior {prior:.2f} met (max observed {max_observed:.2f}); keep or tighten"
        elif max_observed >= 0.85:
            calibration_notes[fam] = f"prior {prior:.2f} slightly missed (max {max_observed:.2f}); consider softening to 0.85"
        elif max_observed >= 0.60:
            calibration_notes[fam] = f"prior {prior:.2f} materially missed (max {max_observed:.2f}); recommend recalibration"
        else:
            calibration_notes[fam] = f"prior {prior:.2f} SEVERELY missed (max {max_observed:.2f}); classifier fundamentally weak on this family"

    return {
        "classifier_side_by_side": side_by_side,
        "wrong_but_plausible": wbp,
        "context_needed": {
            "summary": context_needed_summary,
            "per_row": context_needed_actual,
        },
        "provenance_tier_stratified_accuracy": tier_accuracy,
        "gate_calibration_recommendations": calibration_notes,
        "collapse_candidates_b": {
            "identity_to_doc_locate": b["collapse_candidate_identity_doc_locate"],
            "selfref_to_doc_locate": b["collapse_candidate_selfref_doc_locate"],
        },
        "point_vs_locate_b": b["point_vs_locate"],
        "raw_a": {k: v for k, v in a.items() if k not in ("row_results", "confusion_matrix")},
        "raw_b": {k: v for k, v in b.items() if k not in ("row_results", "confusion_matrix")},
        "a_confusion": a["confusion_matrix"],
        "b_confusion": b["confusion_matrix"],
    }


if __name__ == "__main__":
    r = build_report()
    print(json.dumps(r, indent=2, default=str))
