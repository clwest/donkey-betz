"""Phase-0.5 Classifier A — MIRROR of docs/research/discovery_layer/PHASE_0/classifier_a.py

Source of truth: docs/research/discovery_layer/PHASE_0/classifier_a.py
Mirror exists solely for Python package import compatibility (docs/ subtree
is not a Python package; core/services/ is).

DRIFT DISCIPLINE (per Rigby S2824 Q1 refinement): any change to this file MUST
be mirrored back to the source AND accompanied by a Rigby SIGN cycle. The
automated drift test at core/tests/test_phase_0_5_router.py verifies
classify_a() outputs match a fixed fixture corpus between source and mirror.

Refresh cadence: if source classifier_a.py changes, re-mirror + re-run drift
test in same PR.

Chris R4 (S2823 B3 D-verdict §10.4): confidence is CATEGORICAL only
(HIGH/MEDIUM/LOW). Any attempt to add numeric confidence scoring requires
Rigby SIGN + Chris D-verdict per §10.5 evidence-integrity trigger list.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# has_literal_identifier derivation (per field_dictionary.md rule 7)
# ---------------------------------------------------------------------------

_EXT_RE = re.compile(r"\.(md|py|js|ts|tsx|json|yml|yaml|toml|sh|txt)\b", re.I)
_UPPERCASE_TOKEN_RE = re.compile(r"\b[A-Z_][A-Z0-9_]{3,}\b")
_FILENAME_STEM_RE = re.compile(r"\b\d{4}_[a-z_]{5,}\b")
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

_COUNT_QUANTIFIER = re.compile(r"^\s*(how many|number of|count of|total)\b", re.I)
_COUNT_OBJECT = re.compile(
    r"\b(agents?|spiders?|models?|tasks?|workers?|advisors?|services?|providers?|"
    r"beats?|handlers?|schemas?|tools?|commands?|routes?|endpoints?|files?|"
    r"cogs?|body systems?)\b",
    re.I,
)

_PROCEDURAL_VERB = re.compile(
    r"^\s*(how do i|how to|how can i|steps? to)\b",
    re.I,
)
_PROCEDURAL_IMPERATIVE = re.compile(
    r"^\s*(add|create|restart|regenerate|start|stop|configure|deploy|install|"
    r"remove|delete|update|migrate|sync|refresh|build|run)\s+(a|the|an|my)?\s*\w+",
    re.I,
)

_CONCEPTUAL_QUESTION = re.compile(
    r"^\s*(what (is|are|does)|explain|why (do|does|is|are)|how does)\b",
    re.I,
)
_CONCEPTUAL_DIFFERENCE = re.compile(r"\b(difference between|versus|vs\.?)\b", re.I)

_DISCOVERY_VERB = re.compile(
    r"^\s*(find|list|show|search|display|where (are|do i find))\b",
    re.I,
)
_DISCOVERY_ABOUT = re.compile(r"\babout\b", re.I)

_IDENTITY_FILENAME = re.compile(r"^\s*[\w/.\-_]+\.(md|py|js|ts|tsx|json|yml|yaml)\s*$", re.I)
_IDENTITY_STEM = re.compile(r"^\s*\d{4}_[a-z_]+\s*$", re.I)
_IDENTITY_UPPERCASE_ALONE = re.compile(r"^\s*[A-Z_][A-Z0-9_]{3,}\s*$")

_SELF_REF_LITERAL = re.compile(
    r"^\s*(00-start|claude|readme|engineering[- _]playbook|next[- _]session|start[- _]here)\b",
    re.I,
)
_SELF_REF_NAV = re.compile(
    r"\b(next session|start (here|doc)|current (session|arc|task)|"
    r"project.?s? rules?|read (me|this) first|where do i (start|read))\b",
    re.I,
)

_CONTEXT_NEEDED_PRONOUN = re.compile(
    r"^\s*(the current one|that (one|doc|file|thing)|this one|it|them|those)\s*$",
    re.I,
)


@dataclass
class ClassifierAResult:
    family: str
    confidence: str
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
    matched: list[str] = []

    if _CONTEXT_NEEDED_PRONOUN.match(query):
        return ClassifierAResult("CONTEXT_NEEDED", "HIGH", ["pronoun_only"], hli)

    if _IDENTITY_FILENAME.match(query):
        matched.append("filename_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)
    if _IDENTITY_STEM.match(query):
        matched.append("stem_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)
    if _IDENTITY_UPPERCASE_ALONE.match(query):
        matched.append("uppercase_token_only")
        return ClassifierAResult("IDENTITY", "MEDIUM", matched, hli)
    if re.match(r"^\s*[\w./_-]+/[\w./_-]+\s*$", query):
        matched.append("path_only")
        return ClassifierAResult("IDENTITY", "HIGH", matched, hli)

    self_ref_match = False
    if _SELF_REF_LITERAL.match(query):
        matched.append("self_ref_literal")
        self_ref_match = True
    if _SELF_REF_NAV.search(query):
        matched.append("self_ref_nav")
        self_ref_match = True
    if self_ref_match:
        return ClassifierAResult("SELF-REFERENCE", "HIGH", matched, hli)

    if _COUNT_QUANTIFIER.match(query):
        matched.append("count_quantifier")
        if _COUNT_OBJECT.search(query):
            matched.append("count_object")
            return ClassifierAResult("COUNT", "HIGH", matched, hli)
        return ClassifierAResult("AMBIGUOUS", "MEDIUM", matched, hli)

    procedural_match = False
    if _PROCEDURAL_VERB.match(query):
        matched.append("procedural_verb")
        procedural_match = True
    if _PROCEDURAL_IMPERATIVE.match(query):
        matched.append("procedural_imperative")
        procedural_match = True
    if procedural_match:
        confidence = "HIGH" if len(matched) >= 2 or _PROCEDURAL_VERB.match(query) else "MEDIUM"
        return ClassifierAResult("PROCEDURAL", confidence, matched, hli)

    conceptual_match = False
    if _CONCEPTUAL_QUESTION.match(query):
        matched.append("conceptual_question")
        conceptual_match = True
    if _CONCEPTUAL_DIFFERENCE.search(query):
        matched.append("conceptual_difference")
        conceptual_match = True
    if conceptual_match:
        return ClassifierAResult("CONCEPTUAL", "HIGH", matched, hli)

    discovery_match = False
    if _DISCOVERY_VERB.match(query):
        matched.append("discovery_verb")
        discovery_match = True
    if _DISCOVERY_ABOUT.search(query):
        matched.append("discovery_about")
        discovery_match = True
    if discovery_match:
        return ClassifierAResult("DISCOVERY", "HIGH", matched, hli)

    if len(query.split()) <= 4 and not hli:
        return ClassifierAResult("AMBIGUOUS", "LOW", ["bare_noun_phrase"], hli)

    if hli:
        return ClassifierAResult("DISCOVERY", "LOW", ["has_literal_no_shape"], hli)

    return ClassifierAResult("UNCLASSIFIABLE", "LOW", ["no_rule_matched"], hli)
