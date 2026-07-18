"""Phase-0 Classifier A — flat regex/keyword per family.

R3-compliant: query text only. No conversational/workspace/task context.
Output includes CONTEXT_NEEDED per R4 (distinct from AMBIGUOUS/UNCLASSIFIABLE).

Usage:
    from classifier_a import classify_a
    result = classify_a("How many spiders do we have")
    # {'family': 'COUNT', 'confidence': 'HIGH', 'matched_rules': ['count_how_many + object_noun']}

Ground truth per corpus.json rows.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

CORPUS_PATH = Path(__file__).parent / "corpus.json"

# ---------------------------------------------------------------------------
# has_literal_identifier derivation (per field_dictionary.md rule 7)
# ---------------------------------------------------------------------------

_EXT_RE = re.compile(r"\.(md|py|js|ts|tsx|json|yml|yaml|toml|sh|txt)\b", re.I)
_UPPERCASE_TOKEN_RE = re.compile(r"\b[A-Z_][A-Z0-9_]{3,}\b")  # e.g., PLATFORM_INVENTORY
_FILENAME_STEM_RE = re.compile(r"\b\d{4}_[a-z_]{5,}\b")  # e.g., 2701_docs_inventory_topology_audit
_PATH_RE = re.compile(r"[\w./-]+/[\w./-]+")


def derive_has_literal_identifier(query_text: str) -> bool:
    """Return True if query contains a literal file/path/stem token."""
    if _EXT_RE.search(query_text):
        return True
    if _PATH_RE.search(query_text):
        return True
    if _UPPERCASE_TOKEN_RE.search(query_text):
        return True
    if _FILENAME_STEM_RE.search(query_text):
        return True
    return False


# ---------------------------------------------------------------------------
# Classifier A — flat regex/keyword rules per family
# ---------------------------------------------------------------------------

# COUNT: quantifier + object noun
_COUNT_QUANTIFIER = re.compile(r"^\s*(how many|number of|count of|total)\b", re.I)
_COUNT_OBJECT = re.compile(
    r"\b(agents?|spiders?|models?|tasks?|workers?|advisors?|services?|providers?|"
    r"beats?|handlers?|schemas?|tools?|commands?|routes?|endpoints?|files?|"
    r"cogs?|body systems?)\b",
    re.I,
)

# PROCEDURAL: verb-object shape
_PROCEDURAL_VERB = re.compile(
    r"^\s*(how do i|how to|how can i|steps? to)\b",
    re.I,
)
_PROCEDURAL_IMPERATIVE = re.compile(
    r"^\s*(add|create|restart|regenerate|start|stop|configure|deploy|install|"
    r"remove|delete|update|migrate|sync|refresh|build|run)\s+(a|the|an|my)?\s*\w+",
    re.I,
)

# CONCEPTUAL: explanation/definition asks
_CONCEPTUAL_QUESTION = re.compile(
    r"^\s*(what (is|are|does)|explain|why (do|does|is|are)|how does)\b",
    re.I,
)
_CONCEPTUAL_DIFFERENCE = re.compile(r"\b(difference between|versus|vs\.?)\b", re.I)

# DISCOVERY: search/find/list shapes + about-topic bare-noun
_DISCOVERY_VERB = re.compile(
    r"^\s*(find|list|show|search|display|where (are|do i find))\b",
    re.I,
)
_DISCOVERY_ABOUT = re.compile(r"\babout\b", re.I)

# IDENTITY: literal filename/path is the whole query (or dominant)
_IDENTITY_FILENAME = re.compile(r"^\s*[\w/.\-_]+\.(md|py|js|ts|tsx|json|yml|yaml)\s*$", re.I)
_IDENTITY_STEM = re.compile(r"^\s*\d{4}_[a-z_]+\s*$", re.I)  # NNNN_stem style
_IDENTITY_UPPERCASE_ALONE = re.compile(r"^\s*[A-Z_][A-Z0-9_]{3,}\s*$")

# SELF-REFERENCE: references to doc's own name / meta-navigation
_SELF_REF_LITERAL = re.compile(
    r"^\s*(00-start|claude|readme|engineering[- _]playbook|next[- _]session|start[- _]here)\b",
    re.I,
)
_SELF_REF_NAV = re.compile(
    r"\b(next session|start (here|doc)|current (session|arc|task)|"
    r"project.?s? rules?|read (me|this) first|where do i (start|read))\b",
    re.I,
)

# CONTEXT_NEEDED: pure pronoun/definite-reference without content noun
_CONTEXT_NEEDED_PRONOUN = re.compile(
    r"^\s*(the current one|that (one|doc|file|thing)|this one|it|them|those)\s*$",
    re.I,
)


@dataclass
class ClassifierAResult:
    family: str  # COUNT / PROCEDURAL / DISCOVERY / IDENTITY / SELF-REFERENCE / CONCEPTUAL / AMBIGUOUS / UNCLASSIFIABLE / CONTEXT_NEEDED
    confidence: str  # HIGH / MEDIUM / LOW
    matched_rules: list[str] = field(default_factory=list)
    has_literal_identifier: bool = False

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "confidence": self.confidence,
            "matched_rules": self.matched_rules,
            "has_literal_identifier": self.has_literal_identifier,
        }


def classify_a(query_text: str) -> ClassifierAResult:
    """Flat regex/keyword classifier. Query text only per R3."""
    query = query_text.strip()
    hli = derive_has_literal_identifier(query)
    matched = []

    # CONTEXT_NEEDED — pure pronoun/definite reference (check first, highest priority)
    if _CONTEXT_NEEDED_PRONOUN.match(query):
        return ClassifierAResult("CONTEXT_NEEDED", "HIGH", ["pronoun_only"], hli)

    # IDENTITY — literal filename/stem is the whole query
    if _IDENTITY_FILENAME.match(query):
        matched.append("filename_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)
    if _IDENTITY_STEM.match(query):
        matched.append("stem_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)
    if _IDENTITY_UPPERCASE_ALONE.match(query):
        matched.append("uppercase_token_only")
        return ClassifierAResult("IDENTITY", "MEDIUM", matched, hli)
    # Path-style like "core/rag.py"
    if re.match(r"^\s*[\w./_-]+/[\w./_-]+\s*$", query):
        matched.append("path_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)

    # SELF-REFERENCE — literal self-name OR nav-to-pointer phrasing
    self_ref_match = False
    if _SELF_REF_LITERAL.match(query):
        matched.append("self_ref_literal")
        self_ref_match = True
    if _SELF_REF_NAV.search(query):
        matched.append("self_ref_nav")
        self_ref_match = True
    if self_ref_match:
        return ClassifierAResult("SELF-REFERENCE", "HIGH", matched, hli)

    # COUNT — quantifier + object noun (HIGH); quantifier alone (MEDIUM)
    if _COUNT_QUANTIFIER.match(query):
        matched.append("count_quantifier")
        if _COUNT_OBJECT.search(query):
            matched.append("count_object")
            return ClassifierAResult("COUNT", "HIGH", matched, hli)
        # Quantifier without object noun — could be COUNT or AMBIGUOUS
        return ClassifierAResult("AMBIGUOUS", "MEDIUM", matched, hli)

    # PROCEDURAL — verb-object shape
    procedural_match = False
    if _PROCEDURAL_VERB.match(query):
        matched.append("procedural_verb")
        procedural_match = True
    if _PROCEDURAL_IMPERATIVE.match(query):
        matched.append("procedural_imperative")
        procedural_match = True
    if procedural_match:
        return ClassifierAResult("PROCEDURAL", "HIGH" if len(matched) >= 2 or _PROCEDURAL_VERB.match(query) else "MEDIUM", matched, hli)

    # CONCEPTUAL — explanation/definition asks
    conceptual_match = False
    if _CONCEPTUAL_QUESTION.match(query):
        matched.append("conceptual_question")
        conceptual_match = True
    if _CONCEPTUAL_DIFFERENCE.search(query):
        matched.append("conceptual_difference")
        conceptual_match = True
    if conceptual_match:
        return ClassifierAResult("CONCEPTUAL", "HIGH", matched, hli)

    # DISCOVERY — verb OR 'about'
    discovery_match = False
    if _DISCOVERY_VERB.match(query):
        matched.append("discovery_verb")
        discovery_match = True
    if _DISCOVERY_ABOUT.search(query):
        matched.append("discovery_about")
        discovery_match = True
    if discovery_match:
        return ClassifierAResult("DISCOVERY", "HIGH", matched, hli)

    # Bare noun phrase — likely DISCOVERY or CONCEPTUAL (AMBIGUOUS)
    if len(query.split()) <= 4 and not hli:
        return ClassifierAResult("AMBIGUOUS", "LOW", ["bare_noun_phrase"], hli)

    # Discovery is a good catch-all for topic-noun queries with mixed tokens
    if hli:
        # Has literal identifier but no shape rule matched
        return ClassifierAResult("DISCOVERY", "LOW", ["has_literal_no_shape"], hli)

    return ClassifierAResult("UNCLASSIFIABLE", "LOW", ["no_rule_matched"], hli)


# ---------------------------------------------------------------------------
# Evaluation harness
# ---------------------------------------------------------------------------


def evaluate_against_corpus(corpus_path: Path = CORPUS_PATH) -> dict:
    """Run classifier over all corpus rows + compute per-family metrics."""
    corpus = json.loads(corpus_path.read_text())
    rows = corpus["rows"]

    results = []
    for row in rows:
        r = classify_a(row["query_text"])
        results.append({
            "query_id": row["query_id"],
            "query_text": row["query_text"],
            "intended_family": row["intended_family"],
            "secondary_family": row.get("secondary_family"),
            "predicted_family": r.family,
            "predicted_confidence": r.confidence,
            "matched_rules": r.matched_rules,
            "has_literal_identifier_derived": r.has_literal_identifier,
            "has_literal_identifier_labeled": row["has_literal_identifier"],
            "hli_match": r.has_literal_identifier == row["has_literal_identifier"],
            "provenance_tier": row["provenance_tier"],
            "misroute_consequence": row["misroute_consequence"],
        })

    # Per-family metrics
    families = ["COUNT", "PROCEDURAL", "DISCOVERY", "IDENTITY", "SELF-REFERENCE", "CONCEPTUAL"]
    per_family = {}
    for fam in families:
        # Rows where intended_family == fam
        intended = [r for r in results if r["intended_family"] == fam]
        # Correct if predicted matches intended OR (row is AMBIGUOUS ground-truth AND classifier output AMBIGUOUS/CONTEXT_NEEDED)
        tp = sum(1 for r in intended if r["predicted_family"] == fam)
        fn = len(intended) - tp
        # False positives: rows predicted as fam but not intended fam
        predicted_as = [r for r in results if r["predicted_family"] == fam]
        fp = sum(1 for r in predicted_as if r["intended_family"] != fam)
        precision = tp / (tp + fp) if (tp + fp) > 0 else None
        recall = tp / (tp + fn) if (tp + fn) > 0 else None
        f1 = (2 * precision * recall / (precision + recall)) if (precision and recall and (precision + recall) > 0) else None
        per_family[fam] = {
            "n_intended": len(intended),
            "tp": tp, "fp": fp, "fn": fn,
            "precision": precision, "recall": recall, "f1": f1,
        }

    # Confusion matrix
    all_predicted = set(r["predicted_family"] for r in results)
    all_intended = set(r["intended_family"] for r in results)
    all_labels = sorted(all_predicted | all_intended)
    confusion = {intended: {pred: 0 for pred in all_labels} for intended in all_labels}
    for r in results:
        confusion[r["intended_family"]][r["predicted_family"]] += 1

    # Ambiguity/abstention rates
    n = len(results)
    ambiguous_rate = sum(1 for r in results if r["predicted_family"] == "AMBIGUOUS") / n
    unclassifiable_rate = sum(1 for r in results if r["predicted_family"] == "UNCLASSIFIABLE") / n
    context_needed_rate = sum(1 for r in results if r["predicted_family"] == "CONTEXT_NEEDED") / n

    # AMBIGUOUS ground-truth handling: rows with secondary_family set are AMBIGUOUS ground-truth.
    # A row is "correctly handled" if classifier outputs AMBIGUOUS/CONTEXT_NEEDED/UNCLASSIFIABLE
    # OR matches intended_family or secondary_family.
    for r in results:
        row = next((row for row in rows if row["query_id"] == r["query_id"]), None)
        secondary = (row or {}).get("secondary_family")
        r["is_ambiguous_ground_truth"] = bool(secondary)
        if secondary:
            valid_outputs = {"AMBIGUOUS", "CONTEXT_NEEDED", "UNCLASSIFIABLE", r["intended_family"], secondary}
            r["ambig_gt_correct"] = r["predicted_family"] in valid_outputs
        else:
            r["ambig_gt_correct"] = None

    # HLI derivation accuracy
    hli_correct = sum(1 for r in results if r["hli_match"]) / n

    # Wrong-but-plausible (R5): predicted family matches intended answer_mode family class but wrong specific family
    # For now, we treat it as: predicted != intended AND both are "confident" (not ABSTAIN/AMBIGUOUS/UNCLASSIFIABLE/CONTEXT_NEEDED)
    wrong_but_plausible = [
        r for r in results
        if r["predicted_family"] != r["intended_family"]
        and r["predicted_family"] in families  # confident wrong family
        and r["predicted_confidence"] in ("HIGH", "MEDIUM")
    ]

    return {
        "classifier": "A_flat",
        "corpus_path": str(corpus_path),
        "n_rows": n,
        "per_family": per_family,
        "confusion_matrix": confusion,
        "ambiguous_rate": ambiguous_rate,
        "unclassifiable_rate": unclassifiable_rate,
        "context_needed_rate": context_needed_rate,
        "hli_derivation_accuracy": hli_correct,
        "wrong_but_plausible_count": len(wrong_but_plausible),
        "wrong_but_plausible_queries": [(r["query_id"], r["intended_family"], r["predicted_family"]) for r in wrong_but_plausible],
        "row_results": results,
    }


if __name__ == "__main__":
    result = evaluate_against_corpus()
    print(json.dumps({
        k: v for k, v in result.items()
        if k not in ("row_results", "confusion_matrix")
    }, indent=2, default=str))
    print()
    print("Confusion matrix (rows=intended, cols=predicted):")
    labels = sorted(set(list(result["confusion_matrix"].keys()) + [k for row in result["confusion_matrix"].values() for k in row.keys()]))
    print(f"{'':22} " + " ".join(f"{l[:10]:>10}" for l in labels))
    for intended, preds in result["confusion_matrix"].items():
        print(f"{intended:22} " + " ".join(f"{preds.get(l,0):>10}" for l in labels))
