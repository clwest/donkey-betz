"""Phase-0 Classifier B — two-axis subject × relationship composition.

Per S2821 §7.5 candidate B:
- Subject types: {OBJECT, DOC, CONCEPT, PROCEDURE, POINTER}
- Relationships: {LOCATE, EXPLAIN, DISCOVER, RETURN_CANONICAL, EXECUTE, POINT}
  (POINT added per S2821 Q8 evidence — distinct from LOCATE)

Composed intent → family mapping tests collapse candidates:
- IDENTITY + SELF-REFERENCE-C3 → (DOC, LOCATE) — collapse candidate
- POINT distinct from LOCATE

R3-compliant: query text only.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

CORPUS_PATH = Path(__file__).parent / "corpus.json"

# Reuse HLI derivation from Classifier A
from classifier_a import derive_has_literal_identifier  # noqa: E402


# ---------------------------------------------------------------------------
# Axis 1: subject type detection
# ---------------------------------------------------------------------------

# DOC: literal filename OR uppercase-stem token dominant
_DOC_FILENAME = re.compile(r"\.(md|py|js|ts|tsx|json|yml|yaml|toml)\b", re.I)
_DOC_STEM = re.compile(r"\d{4}_[a-z_]{5,}", re.I)  # 2701_docs_inventory...
_DOC_PATH = re.compile(r"[\w./_-]+/[\w./_-]+")
_DOC_TITLE_TOKEN = re.compile(r"\b[A-Z_][A-Z0-9_]{3,}\b")  # PLATFORM_INVENTORY

# OBJECT: platform-atomic nouns (agent, spider, model, task, worker, etc.)
_OBJECT_NOUNS = re.compile(
    r"\b(agents?|spiders?|models?|tasks?|workers?|advisors?|services?|providers?|"
    r"beats?|handlers?|schemas?|tools?|commands?|routes?|endpoints?|"
    r"cogs?|body systems?|initiatives?|deliverables?)\b",
    re.I,
)

# POINTER: nav-to phrasing (start doc, next session, current arc)
_POINTER_PHRASE = re.compile(
    r"\b(next session|start (here|doc)|current (session|arc|task|one)|"
    r"start[- _]next[- _]session|project.?s? rules?|read (me|this) first|"
    r"where do i (start|read))\b",
    re.I,
)

# PROCEDURE: verb-object shape or how-to
_PROCEDURE_HOWTO = re.compile(r"^\s*(how do i|how to|how can i|steps? to)\b", re.I)
_PROCEDURE_IMPERATIVE = re.compile(
    r"^\s*(add|create|restart|regenerate|start|stop|configure|deploy|install|"
    r"remove|delete|update|migrate|sync|refresh|build|run)\s+",
    re.I,
)

# CONCEPT: what/why/explain + non-object noun
_CONCEPT_QUESTION = re.compile(
    r"^\s*(what (is|are|does)|explain|why (do|does|is|are)|how does)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Axis 2: relationship detection
# ---------------------------------------------------------------------------

# LOCATE: user knows what they want; wants to find it
_LOCATE_VERB = re.compile(r"^\s*(where (is|do i find)|find|search)\b", re.I)

# EXPLAIN: user wants understanding
_EXPLAIN_VERB = re.compile(r"^\s*(what (is|are|does)|explain|why|how does)\b", re.I)

# DISCOVER: user wants to learn what exists (list, show, browse)
_DISCOVER_VERB = re.compile(r"^\s*(list|show|display)\b", re.I)

# RETURN_CANONICAL: quantifier ask → return authoritative source
_RETURN_CANONICAL_VERB = re.compile(
    r"^\s*(how many|number of|count of|total)\b", re.I
)

# EXECUTE: verb-object imperative on procedure
_EXECUTE_VERB = re.compile(
    r"^\s*(how do i|how to|how can i)\s+(add|create|restart|regenerate|start|stop|"
    r"configure|deploy|install|remove|delete|update|migrate|sync|refresh|build|run)\b",
    re.I,
)
_EXECUTE_BARE_IMPERATIVE = re.compile(
    r"^\s*(add|create|restart|regenerate|start|stop|configure|deploy|install|"
    r"remove|delete|update|migrate|sync|refresh|build|run)\s+",
    re.I,
)

# POINT: user wants the pointer, not the pointed-to
_POINT_REF = re.compile(
    r"\b(start (here|doc)|next session|00-start|point (me )?to|"
    r"read (me|this) first|where do i (start|read))\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Composition: (subject, relationship) → family
# ---------------------------------------------------------------------------

_COMPOSITION_MAP = {
    # OBJECT + RETURN_CANONICAL → COUNT (canonical inventory ask)
    ("OBJECT", "RETURN_CANONICAL"): "COUNT",
    # OBJECT + DISCOVER → DISCOVERY (list all X)
    ("OBJECT", "DISCOVER"): "DISCOVERY",
    # OBJECT + EXECUTE → PROCEDURAL (add a new spider)
    ("OBJECT", "EXECUTE"): "PROCEDURAL",
    # OBJECT + LOCATE → DISCOVERY (find agent router)
    ("OBJECT", "LOCATE"): "DISCOVERY",
    # OBJECT + EXPLAIN → CONCEPTUAL (what is an advisor)
    ("OBJECT", "EXPLAIN"): "CONCEPTUAL",
    # DOC + LOCATE → IDENTITY (return the doc)
    ("DOC", "LOCATE"): "IDENTITY",
    # DOC + RETURN_CANONICAL → IDENTITY (name it, return it)
    ("DOC", "RETURN_CANONICAL"): "IDENTITY",
    # DOC + POINT → SELF-REFERENCE (return the pointer to the doc)
    ("DOC", "POINT"): "SELF-REFERENCE",
    # DOC + EXPLAIN → CONCEPTUAL (why do we have X and Y)
    ("DOC", "EXPLAIN"): "CONCEPTUAL",
    # DOC + DISCOVER → DISCOVERY (find related docs)
    ("DOC", "DISCOVER"): "DISCOVERY",
    # POINTER + POINT → SELF-REFERENCE (return the pointer)
    ("POINTER", "POINT"): "SELF-REFERENCE",
    # POINTER + LOCATE → SELF-REFERENCE (locate the pointer)
    ("POINTER", "LOCATE"): "SELF-REFERENCE",
    # PROCEDURE + EXECUTE → PROCEDURAL
    ("PROCEDURE", "EXECUTE"): "PROCEDURAL",
    # PROCEDURE + EXPLAIN → PROCEDURAL (how do I X)
    ("PROCEDURE", "EXPLAIN"): "PROCEDURAL",
    # CONCEPT + EXPLAIN → CONCEPTUAL
    ("CONCEPT", "EXPLAIN"): "CONCEPTUAL",
    # CONCEPT + LOCATE → DISCOVERY
    ("CONCEPT", "LOCATE"): "DISCOVERY",
}


@dataclass
class ClassifierBResult:
    family: str
    subject: str  # DOC / OBJECT / CONCEPT / PROCEDURE / POINTER / UNKNOWN
    relationship: str  # LOCATE / EXPLAIN / DISCOVER / RETURN_CANONICAL / EXECUTE / POINT / UNKNOWN
    confidence: str
    matched_subject_rules: list[str] = field(default_factory=list)
    matched_relationship_rules: list[str] = field(default_factory=list)
    has_literal_identifier: bool = False

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "subject": self.subject,
            "relationship": self.relationship,
            "confidence": self.confidence,
            "matched_subject_rules": self.matched_subject_rules,
            "matched_relationship_rules": self.matched_relationship_rules,
            "has_literal_identifier": self.has_literal_identifier,
        }


def detect_subject(query: str) -> tuple[str, list[str]]:
    """Return (subject_type, matched_rules). UNKNOWN if no rule fires."""
    matched = []

    # POINTER — highest priority (pronoun-references + nav phrasing)
    if _POINTER_PHRASE.search(query):
        matched.append("pointer_phrase")
        return "POINTER", matched

    # DOC — filename/stem/path/uppercase token
    doc_signals = 0
    if _DOC_FILENAME.search(query):
        matched.append("doc_filename")
        doc_signals += 1
    if _DOC_STEM.search(query):
        matched.append("doc_stem")
        doc_signals += 1
    if _DOC_PATH.search(query):
        matched.append("doc_path")
        doc_signals += 1
    if _DOC_TITLE_TOKEN.search(query):
        matched.append("doc_title_token")
        doc_signals += 1

    # PROCEDURE — how-to phrasing
    if _PROCEDURE_HOWTO.match(query):
        matched.append("procedure_howto")
        return "PROCEDURE", matched
    if _PROCEDURE_IMPERATIVE.match(query):
        matched.append("procedure_imperative")
        return "PROCEDURE", matched

    # CONCEPT — what/why/explain WITHOUT object noun
    if _CONCEPT_QUESTION.match(query) and not _OBJECT_NOUNS.search(query):
        matched.append("concept_question_no_object")
        return "CONCEPT", matched

    # OBJECT — platform atomic nouns
    if _OBJECT_NOUNS.search(query):
        matched.append("object_noun")
        # If also has doc signals, prefer OBJECT for count-style asks, DOC for identity
        if doc_signals > 0 and _RETURN_CANONICAL_VERB.match(query):
            # "How many spiders" — OBJECT wins (returns canonical DOC downstream)
            return "OBJECT", matched
        return "OBJECT", matched

    # DOC — fallback if doc signals present but nothing else
    if doc_signals > 0:
        return "DOC", matched

    # CONCEPT — what/why/explain even with object noun (fallback)
    if _CONCEPT_QUESTION.match(query):
        matched.append("concept_question")
        return "CONCEPT", matched

    return "UNKNOWN", matched


def detect_relationship(query: str) -> tuple[str, list[str]]:
    """Return (relationship, matched_rules). UNKNOWN if no rule fires."""
    matched = []

    # POINT (highest priority — nav-to-pointer)
    if _POINT_REF.search(query):
        matched.append("point_ref")
        return "POINT", matched

    # EXECUTE (imperative or how-do-i-verb)
    if _EXECUTE_VERB.match(query):
        matched.append("execute_verb")
        return "EXECUTE", matched
    if _EXECUTE_BARE_IMPERATIVE.match(query):
        matched.append("execute_bare_imperative")
        return "EXECUTE", matched

    # RETURN_CANONICAL (count query)
    if _RETURN_CANONICAL_VERB.match(query):
        matched.append("return_canonical_quantifier")
        return "RETURN_CANONICAL", matched

    # DISCOVER (list/show)
    if _DISCOVER_VERB.match(query):
        matched.append("discover_verb")
        return "DISCOVER", matched

    # LOCATE (where/find/search)
    if _LOCATE_VERB.match(query):
        matched.append("locate_verb")
        return "LOCATE", matched

    # EXPLAIN (what/why)
    if _EXPLAIN_VERB.match(query):
        matched.append("explain_verb")
        return "EXPLAIN", matched

    return "UNKNOWN", matched


def classify_b(query_text: str) -> ClassifierBResult:
    """Two-axis classifier. Query text only per R3."""
    query = query_text.strip()
    hli = derive_has_literal_identifier(query)

    subject, subj_rules = detect_subject(query)
    relationship, rel_rules = detect_relationship(query)

    # If both known → look up composition
    if subject != "UNKNOWN" and relationship != "UNKNOWN":
        composed = _COMPOSITION_MAP.get((subject, relationship))
        if composed:
            return ClassifierBResult(
                family=composed,
                subject=subject,
                relationship=relationship,
                confidence="HIGH",
                matched_subject_rules=subj_rules,
                matched_relationship_rules=rel_rules,
                has_literal_identifier=hli,
            )
        # Known subject + relationship but not in composition map → LOW confidence
        return ClassifierBResult(
            family="AMBIGUOUS",
            subject=subject,
            relationship=relationship,
            confidence="LOW",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=rel_rules,
            has_literal_identifier=hli,
        )

    # Only subject known — infer relationship from subject
    if subject == "DOC" and relationship == "UNKNOWN":
        # Bare DOC token → LOCATE (return the doc)
        return ClassifierBResult(
            family="IDENTITY",
            subject="DOC",
            relationship="LOCATE",
            confidence="HIGH",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=["inferred_from_bare_doc"],
            has_literal_identifier=hli,
        )
    if subject == "POINTER" and relationship == "UNKNOWN":
        return ClassifierBResult(
            family="SELF-REFERENCE",
            subject="POINTER",
            relationship="POINT",
            confidence="HIGH",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=["inferred_from_bare_pointer"],
            has_literal_identifier=hli,
        )
    if subject == "OBJECT" and relationship == "UNKNOWN":
        # Bare OBJECT noun-phrase → DISCOVERY (LOCATE the docs about it)
        return ClassifierBResult(
            family="DISCOVERY",
            subject="OBJECT",
            relationship="LOCATE",
            confidence="MEDIUM",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=["inferred_from_bare_object"],
            has_literal_identifier=hli,
        )
    if subject == "PROCEDURE" and relationship == "UNKNOWN":
        return ClassifierBResult(
            family="PROCEDURAL",
            subject="PROCEDURE",
            relationship="EXECUTE",
            confidence="HIGH",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=["inferred_from_bare_procedure"],
            has_literal_identifier=hli,
        )
    if subject == "CONCEPT" and relationship == "UNKNOWN":
        return ClassifierBResult(
            family="CONCEPTUAL",
            subject="CONCEPT",
            relationship="EXPLAIN",
            confidence="MEDIUM",
            matched_subject_rules=subj_rules,
            matched_relationship_rules=["inferred_from_bare_concept"],
            has_literal_identifier=hli,
        )

    # Only relationship known — sparse; usually AMBIGUOUS
    if subject == "UNKNOWN" and relationship != "UNKNOWN":
        return ClassifierBResult(
            family="AMBIGUOUS",
            subject="UNKNOWN",
            relationship=relationship,
            confidence="LOW",
            matched_subject_rules=[],
            matched_relationship_rules=rel_rules,
            has_literal_identifier=hli,
        )

    # Neither known — CONTEXT_NEEDED if query is pure reference; else UNCLASSIFIABLE
    if re.match(r"^\s*(the current one|that one|this one|it|them)\s*$", query, re.I):
        return ClassifierBResult(
            family="CONTEXT_NEEDED",
            subject="UNKNOWN",
            relationship="UNKNOWN",
            confidence="HIGH",
            has_literal_identifier=hli,
        )

    return ClassifierBResult(
        family="UNCLASSIFIABLE",
        subject="UNKNOWN",
        relationship="UNKNOWN",
        confidence="LOW",
        has_literal_identifier=hli,
    )


# ---------------------------------------------------------------------------
# Evaluation harness (mirrors classifier_a)
# ---------------------------------------------------------------------------


def evaluate_against_corpus(corpus_path: Path = CORPUS_PATH) -> dict:
    corpus = json.loads(corpus_path.read_text())
    rows = corpus["rows"]

    results = []
    for row in rows:
        r = classify_b(row["query_text"])
        results.append({
            "query_id": row["query_id"],
            "query_text": row["query_text"],
            "intended_family": row["intended_family"],
            "secondary_family": row.get("secondary_family"),
            "predicted_family": r.family,
            "predicted_subject": r.subject,
            "predicted_relationship": r.relationship,
            "predicted_confidence": r.confidence,
            "matched_subject_rules": r.matched_subject_rules,
            "matched_relationship_rules": r.matched_relationship_rules,
            "has_literal_identifier_derived": r.has_literal_identifier,
            "has_literal_identifier_labeled": row["has_literal_identifier"],
            "hli_match": r.has_literal_identifier == row["has_literal_identifier"],
            "provenance_tier": row["provenance_tier"],
            "misroute_consequence": row["misroute_consequence"],
        })

    families = ["COUNT", "PROCEDURAL", "DISCOVERY", "IDENTITY", "SELF-REFERENCE", "CONCEPTUAL"]
    per_family = {}
    for fam in families:
        intended = [r for r in results if r["intended_family"] == fam]
        tp = sum(1 for r in intended if r["predicted_family"] == fam)
        fn = len(intended) - tp
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

    all_predicted = set(r["predicted_family"] for r in results)
    all_intended = set(r["intended_family"] for r in results)
    all_labels = sorted(all_predicted | all_intended)
    confusion = {intended: {pred: 0 for pred in all_labels} for intended in all_labels}
    for r in results:
        confusion[r["intended_family"]][r["predicted_family"]] += 1

    n = len(results)
    ambiguous_rate = sum(1 for r in results if r["predicted_family"] == "AMBIGUOUS") / n
    unclassifiable_rate = sum(1 for r in results if r["predicted_family"] == "UNCLASSIFIABLE") / n
    context_needed_rate = sum(1 for r in results if r["predicted_family"] == "CONTEXT_NEEDED") / n
    hli_correct = sum(1 for r in results if r["hli_match"]) / n

    wrong_but_plausible = [
        r for r in results
        if r["predicted_family"] != r["intended_family"]
        and r["predicted_family"] in families
        and r["predicted_confidence"] in ("HIGH", "MEDIUM")
    ]

    # AMBIGUOUS ground-truth handling
    for r in results:
        row = next((row for row in rows if row["query_id"] == r["query_id"]), None)
        secondary = (row or {}).get("secondary_family")
        r["is_ambiguous_ground_truth"] = bool(secondary)
        if secondary:
            valid = {"AMBIGUOUS", "CONTEXT_NEEDED", "UNCLASSIFIABLE", r["intended_family"], secondary}
            r["ambig_gt_correct"] = r["predicted_family"] in valid
        else:
            r["ambig_gt_correct"] = None

    # Two-axis collapse candidate verification: IDENTITY + SELF-REFERENCE-C3 → (DOC, LOCATE)?
    identity_rows = [r for r in results if r["intended_family"] == "IDENTITY"]
    id_doc_locate_hits = sum(1 for r in identity_rows if r["predicted_subject"] == "DOC" and r["predicted_relationship"] == "LOCATE")
    id_collapse_evidence = {
        "n_identity_rows": len(identity_rows),
        "n_predicted_as_doc_locate": id_doc_locate_hits,
        "collapse_support": id_doc_locate_hits / len(identity_rows) if identity_rows else 0,
    }
    selfref_rows = [r for r in results if r["intended_family"] == "SELF-REFERENCE"]
    sr_doc_locate_hits = sum(1 for r in selfref_rows if r["predicted_subject"] == "DOC" and r["predicted_relationship"] == "LOCATE")
    sr_collapse_evidence = {
        "n_selfref_rows": len(selfref_rows),
        "n_predicted_as_doc_locate": sr_doc_locate_hits,
        "collapse_support": sr_doc_locate_hits / len(selfref_rows) if selfref_rows else 0,
    }

    # POINT distinct from LOCATE?
    point_hits = sum(1 for r in results if r["predicted_relationship"] == "POINT")
    locate_hits = sum(1 for r in results if r["predicted_relationship"] == "LOCATE")

    return {
        "classifier": "B_two_axis",
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
        "collapse_candidate_identity_doc_locate": id_collapse_evidence,
        "collapse_candidate_selfref_doc_locate": sr_collapse_evidence,
        "point_vs_locate": {"point_hits": point_hits, "locate_hits": locate_hits, "point_distinct": point_hits > 0},
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
