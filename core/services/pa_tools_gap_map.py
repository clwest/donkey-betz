"""S2795 N24 — PA tools validation-coverage gap map.

Pure-logic module (no Django imports at module scope) that cross-
references three sources of truth for the PA tool surface:

  1. ``core.services.pa_tool_schemas.PA_TOOL_SCHEMAS`` — schemas the LLM sees.
  2. ``core.services.tool_dispatcher.ToolDispatcher._tool_handlers`` — runtime
     name→handler registry.
  3. ``docs/research/tools/validation/*_validation.md`` — the 18 validation
     docs produced by the S2728→S2732 campaign.

Produces a triage-friendly categorization + a cheap schema-quality lint +
3-5 recommended validation slices, so Chris can decide which surfaces
merit dedicated per-tool validation without pre-committing to another
five-session sweep.

**Categories emitted (per Rigby S2795 T1 SIGN F1+F2):**

  * ``validated_full`` — per-tool doc exists AND its "Covered actions"
    checklist lists every action in the tool's schema enum. (No docs
    match this state today; reserved for future docs that add explicit
    action-coverage checklists.)
  * ``validated_partial`` — per-tool doc + "Covered actions" checklist,
    but only a subset of schema actions listed.
  * ``validated_doc_exists_unknown`` — per-tool doc exists but no
    "Covered actions" section, so action-level coverage is unknown.
    The 8 existing per-tool docs sit here today.
  * ``covered_substrate_only`` — no per-tool doc, but the tool is
    touched by one of the cross-cutting substrate docs (retry_behavior,
    payload_size_limits, etc.). Weaker signal — substrate validates
    infra, NOT per-tool invariants. (Rigby F2 rename from
    "validated_cross_cutting" to avoid false confidence.)
  * ``untested`` — no validation doc.
  * ``orphan_schema`` — schema exists, no dispatcher handler. LLM can
    call the tool; nothing answers. (Only ``run_agent`` today —
    intentional meta-tool decomposition, filtered separately.)
  * ``meta_no_handler`` — ``run_agent`` and other by-design meta-tools.
  * ``agent_via_run_agent`` — handler exists but no schema; reachable
    via ``run_agent(agent_name=…)`` (44 agents today, by design).
  * ``agent_via_run_agent_validated`` — S3045: agent-via-run_agent tool
    with a per-tool validation doc authored from RaaS dispatch evidence.
    Distinct from ``validated_full`` because these tools have no schema
    (no Covered actions coverage possible); the audit metric surfaces
    them via a ``RaaS-validated`` rollup rather than folding into
    ``validated_full``.
  * ``handler_only_dead`` — handler exists, no schema, not reachable via
    ``run_agent`` — dead registration.

**Schema quality lint tags (per Rigby S2795 T1 SIGN F5):**

  * ``missing_description``
  * ``short_description`` (< 40 chars)
  * ``no_properties``
  * ``no_required``
  * ``actions_not_mentioned_in_description`` (< 25% of enum values
    appear verbatim in description)

**Triage slices (per Rigby S2795 T1 SIGN F3):**

Groups ``untested`` tools by handler file (natural runtime-derived
grouping — no hand-curated themes). Emits the top 3-5 slices by
untested count with rationale + estimated session count (~1 session
per 4 tools per S2728→S2732 pace: 4-tool batch per session).
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


# ── Substrate docs — cross-cutting concerns, not per-tool coverage ───
#
# Rigby S2795 T1 SIGN F2: docs like ``retry_behavior_validation.md`` or
# ``payload_size_limits_validation.md`` reduce risk platform-wide but do
# NOT validate per-tool invariants; treating them as "validated" is a
# false-confidence signal. Kept as a hand-curated set because the count
# is small (10) and the classification is about semantic content, not
# filename pattern.
SUBSTRATE_DOC_STEMS: Set[str] = {
    'canonical_authority_helpers',
    'celery_worker_lifecycle',
    'context_injection_pipeline',
    'orm_helper_defaults',
    'pa_use_function_calling_env',
    'payload_size_limits',
    'rag_retrieval_path',
    'retrieval_limits_hidden_filters',
    'retry_behavior',
    'worker_cache_behavior',
}


# Meta tools that legitimately have no dispatcher handler (intercepted
# at ``unified_pa_entrypoint`` before the dispatcher). Kept in sync
# with the same set in ``build_pa_tool_audit._collect_findings``.
META_NO_HANDLER: Set[str] = {'run_agent'}


# Regexes for validation-doc parsing.
#
# T1b (S2904) loosened the "Covered actions" heading match to accept
# optional numbering ("## 2. Covered actions") without changing the
# recommended bare form ("## Covered actions"). Rejects word-order
# mismatches like "## Actions covered". Change: Rigby SIGN D-2, ledger
# row 163 forward-carry ZO-Q3.
COVERED_ACTIONS_HEADING_RE = re.compile(
    r'^#+\s+(?:\d+\s*[\.\)\-–—:]?\s*)?covered\s+actions\b',
    re.IGNORECASE | re.MULTILINE,
)
BACKTICK_IDENT_RE = re.compile(r'`([a-z_][a-z0-9_]*)`')
NEXT_HEADING_RE = re.compile(r'\n#+\s+', re.MULTILINE)

# T1b (S2904) template-compliance regexes — frontmatter field
# extraction. Presence-not-exact per Rigby ZO-Q9 (extra keys allowed).
FRONTMATTER_FIELD_RE = re.compile(
    r'^\*\*([A-Za-z][A-Za-z0-9 /_-]*):\*\*\s*(.*?)\s*$',
    re.MULTILINE,
)
FRONTMATTER_DIVIDER_RE = re.compile(r'^---\s*$', re.MULTILINE)
HEADING_RE = re.compile(r'^(#+)\s+(.*?)\s*$', re.MULTILINE)
TEMPLATE_VERSION_VALID_RE = re.compile(r'^v\d+$')

SHORT_DESC_THRESHOLD_CHARS: int = 40
ACTIONS_MENTIONED_RATIO: float = 0.25


# ── Ledger #5 substrate (S2938) — schema-vs-handler consistency lint ─
#
# 3-cycle promotion trigger (S2935/S2936/S2937) for the
# "schema-under-describes-handler" drift class. Tier 1 MVP: two
# parse-based lints, high precision, no LLM. Tier 2 (envelope-JSON
# parse) and Tier 3 (semantic distance between prose and field names)
# deferred to separate ships per Rigby S2938 T0 SIGN AGREE.

# Number-word → int for docstring action-count detection.
_NUMBER_WORD_TO_INT: Dict[str, int] = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
}

# Matches "four actions" / "5 actions" / "3 action" (single/plural).
# Case-insensitive at use site.
_DOCSTRING_ACTION_COUNT_RE = re.compile(
    r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+actions?\b',
    re.IGNORECASE,
)

# Negative-claim patterns per Rigby S2938 T0 Q3 refinement — module
# docstring assertions that constrain runtime behavior. When one of
# these fires, the corresponding _EVIDENCE_SIGNATURES entry is scanned
# in the handler source; a hit means the docstring claim contradicts
# runtime and drift is flagged.
_NEGATIVE_CLAIM_PATTERNS: Dict[str, re.Pattern] = {
    'dispatch': re.compile(
        r"\b(no\s+agent\s+dispatch|no\s+dispatch|does\s+not\s+dispatch|doesn'?t\s+dispatch|no\s+async\s+dispatch)\b",
        re.IGNORECASE,
    ),
    'mutation': re.compile(
        r'\b(no\s+state\s+mutation|no\s+mutation|read[-\s]?only|side[-\s]?effect\s+free)\b',
        re.IGNORECASE,
    ),
    'feature_flag': re.compile(
        r'\b(no\s+feature\s+flag|no\s+settings\s+flag|always\s+live)\b',
        re.IGNORECASE,
    ),
}

# Handler-source signatures that contradict the corresponding negative
# claim. Rigby S2938 T0 Q3: dispatch detection must include curated
# service-layer functions since celery primitives may live one call
# deep from the handler (e.g. ``rigby_mission_delegation.delegate_work_item``
# is what the handler calls; the ``.apply_async()`` lives inside).
_EVIDENCE_SIGNATURES: Dict[str, re.Pattern] = {
    'dispatch': re.compile(
        r'\.apply_async\(|\.delay\(|\bsend_task\(|'
        r'\brigby_mission_delegation\b|\bdelegate_work_item\(',
    ),
    'mutation': re.compile(
        r'\.save\(|\.delete\(|\bupdate_or_create\(|\bbulk_create\(|'
        r'\bget_or_create\(',
    ),
    'feature_flag': re.compile(
        r'getattr\(settings\s*,|from\s+django\.conf\s+import\s+settings|'
        r'\bos\.environ\b',
    ),
}

# T1b (S2904) template-compliance canon.
TEMPLATE_VARIANTS: Set[str] = {'sweep', 'protocol'}

# S2942 Ledger #41 — two-metric scoreboard classification.
#
# Frontmatter fields declared in per-tool validation docs to signal
# execution posture + mutation dry_run readiness. Both fields are
# opt-in per-tool; missing values normalize to ``'unknown'`` (no
# silent defaults). Extends T1b frontmatter capture without changing
# T1b compliance semantics.
#
# Enum values (verbatim, case-insensitive at parse time):
#
# * Execution mode:
#   - ``live``       — action was invoked live and observed end-to-end.
#   - ``analyzed``   — action was audited from code/schema only.
# * Mutation safety:
#   - ``dry_run_supported``  — handler exposes ``dry_run=true`` no-write path.
#   - ``unsafe_no_dry_run``  — mutation lacks dry_run; can't safely live-verify.
EXECUTION_MODES: Set[str] = {'live', 'analyzed'}
MUTATION_SAFETY_VALUES: Set[str] = {'dry_run_supported', 'unsafe_no_dry_run'}
UNKNOWN_LABEL: str = 'unknown'

# Alias-tolerant required-field spec per variant. Each required field
# is a tuple of alias patterns; presence of ANY alias satisfies the
# check. Per Rigby SIGN B edit (presence-not-exact).
_SWEEP_REQUIRED_FIELDS: List[Tuple[str, Tuple[str, ...]]] = [
    ('tool', ('Tool',)),
    ('schema', ('Schema',)),
    ('handler', ('Handler', 'Main handler')),
    ('register_site', ('Register site',)),
    ('session', ('Session', 'Session validated')),
    ('head', ('HEAD at validation',)),
    ('ship_shape', ('Ship shape', 'Report status')),
    ('category_upgrade', ('Category upgrade target',)),
    ('rigby_sign', ('Rigby SIGN', 'Rigby cross-check')),
    ('template_variant', ('Template variant',)),
    ('template_version', ('Template version',)),
]
_PROTOCOL_REQUIRED_FIELDS: List[Tuple[str, Tuple[str, ...]]] = [
    ('tool', ('Tool',)),
    ('schema', ('Schema',)),
    ('handler', ('Handler', 'Main handler')),
    ('register_site', ('Register site',)),
    ('session', ('Session', 'Session validated')),
    ('head', ('HEAD at validation',)),
    ('ship_shape', ('Ship shape', 'Report status')),
    ('rigby_sign', ('Rigby SIGN', 'Rigby cross-check')),
    ('template_variant', ('Template variant',)),
    ('template_version', ('Template version',)),
]

# Mandatory ## sections per variant. Matched by prefix on the heading
# title text (case-sensitive) so variant titles like
# "## 5. Failure / empty-state / staleness / attribution notes" match
# the "## 5. Failure" prefix.
_SWEEP_MANDATORY_SECTIONS: List[Tuple[str, str]] = [
    ('purpose', '1. Purpose'),
    ('covered_actions', 'Covered actions'),  # matched via loosened regex separately
    ('schema_notes', '3. Schema notes'),
    ('golden_path', '4. Golden-path'),
    ('failure', '5. Failure'),
    ('evidence', '6. Evidence'),
    ('related', 'Related'),
]
_PROTOCOL_MANDATORY_SECTIONS: List[Tuple[str, str]] = [
    ('intended_purpose', '1. Intended purpose'),
    ('rigby_belief', "2. Rigby's belief"),
    ('schema_claim', '3. Schema claim'),
    ('handler_behavior', '4. Handler behavior'),
    ('findings', 'Findings'),
    ('verdict', 'Verdict'),
]


def index_validation_docs(docs_dir: Path) -> Dict[str, Any]:
    """Scan ``docs/research/tools/validation/*.md`` and index by role.

    Files whose name starts with ``_`` are excluded (T1b S2904 Rigby
    SIGN D-1 mitigation — the canonical template file
    ``_TEMPLATE_per_tool_validation.md`` lives elsewhere but the
    convention is enforced here as well).

    Returns::

        {
            'substrate_stems': set[str],  # cross-cutting docs
            'per_tool_stems': dict[str, Path],  # stem → doc path
            'covered_actions_by_stem': dict[str, set[str] | None],
                # per-tool docs → set of action names mentioned under
                # a "Covered actions" heading (empty set if heading
                # present but empty; None if heading absent).
            'template_version_by_stem': dict[str, str | None],  # T1b
            'template_variant_by_stem': dict[str, str | None],  # T1b
            'frontmatter_fields_by_stem': dict[str, set[str]],  # T1b
            'heading_titles_by_stem': dict[str, list[str]],  # T1b
            'total_docs': int,
        }

    Missing directory returns zero-shape indices (empty dicts/sets).
    """
    substrate: Set[str] = set()
    per_tool: Dict[str, Path] = {}
    covered_by_stem: Dict[str, Optional[Set[str]]] = {}
    template_version: Dict[str, Optional[str]] = {}
    template_variant: Dict[str, Optional[str]] = {}
    frontmatter_fields: Dict[str, Set[str]] = {}
    heading_titles: Dict[str, List[str]] = {}
    # S2942 Ledger #41 — two-metric scoreboard fields.
    execution_mode: Dict[str, str] = {}
    mutation_safety: Dict[str, str] = {}

    if not docs_dir.exists():
        return {
            'substrate_stems': substrate,
            'per_tool_stems': per_tool,
            'covered_actions_by_stem': covered_by_stem,
            'template_version_by_stem': template_version,
            'template_variant_by_stem': template_variant,
            'frontmatter_fields_by_stem': frontmatter_fields,
            'heading_titles_by_stem': heading_titles,
            'execution_mode_by_stem': execution_mode,
            'mutation_safety_by_stem': mutation_safety,
            'total_docs': 0,
        }

    # T1b S2904 Rigby SIGN D-1: exclude leading-underscore files
    # (canonical template file convention).
    docs = sorted(
        p for p in docs_dir.glob('*_validation.md')
        if not p.name.startswith('_')
    )
    for md in docs:
        stem = md.stem
        if stem.endswith('_validation'):
            stem = stem[: -len('_validation')]
        if stem in SUBSTRATE_DOC_STEMS:
            substrate.add(stem)
            continue
        per_tool[stem] = md
        try:
            body = md.read_text(encoding='utf-8', errors='replace')
        except OSError:
            covered_by_stem[stem] = None
            template_version[stem] = None
            template_variant[stem] = None
            frontmatter_fields[stem] = set()
            heading_titles[stem] = []
            execution_mode[stem] = UNKNOWN_LABEL
            mutation_safety[stem] = UNKNOWN_LABEL
            continue

        # Covered-actions extraction (S2795 F1 + T1b loosened regex).
        heading_match = COVERED_ACTIONS_HEADING_RE.search(body)
        if heading_match:
            after = body[heading_match.end():]
            next_heading = NEXT_HEADING_RE.search(after)
            section = after[: next_heading.start()] if next_heading else after
            covered_by_stem[stem] = set(BACKTICK_IDENT_RE.findall(section))
        else:
            covered_by_stem[stem] = None

        # T1b frontmatter capture — from top of file to first ``---``
        # divider on its own line. Presence-not-exact (ZO-Q9).
        divider = FRONTMATTER_DIVIDER_RE.search(body)
        frontmatter_block = body[:divider.start()] if divider else body
        fm_fields: Dict[str, str] = {}
        for match in FRONTMATTER_FIELD_RE.finditer(frontmatter_block):
            key = match.group(1).strip()
            value = match.group(2).strip()
            fm_fields[key] = value
        frontmatter_fields[stem] = set(fm_fields.keys())
        template_version[stem] = fm_fields.get('Template version') or None
        template_variant[stem] = fm_fields.get('Template variant') or None

        # S2942 Ledger #41 — two-metric scoreboard fields (opt-in per
        # tool). Missing or out-of-enum values normalize to 'unknown'
        # so there is no silent default (per plan §2.1 acceptance).
        exec_raw = (fm_fields.get('Execution mode') or '').strip().lower()
        execution_mode[stem] = exec_raw if exec_raw in EXECUTION_MODES else UNKNOWN_LABEL
        safety_raw = (fm_fields.get('Mutation safety') or '').strip().lower()
        mutation_safety[stem] = (
            safety_raw if safety_raw in MUTATION_SAFETY_VALUES else UNKNOWN_LABEL
        )

        # T1b heading titles — all ##-level and deeper for section-
        # presence checks. Case-sensitive so protocol/sweep title
        # variants remain distinguishable.
        heading_titles[stem] = [
            m.group(2).strip() for m in HEADING_RE.finditer(body)
        ]

    return {
        'substrate_stems': substrate,
        'per_tool_stems': per_tool,
        'covered_actions_by_stem': covered_by_stem,
        'template_version_by_stem': template_version,
        'template_variant_by_stem': template_variant,
        'frontmatter_fields_by_stem': frontmatter_fields,
        'heading_titles_by_stem': heading_titles,
        'execution_mode_by_stem': execution_mode,
        'mutation_safety_by_stem': mutation_safety,
        'total_docs': len(docs),
    }


def evaluate_template_compliance(
    stem: str,
    docs_index: Dict[str, Any],
) -> Dict[str, Any]:
    """T1b S2904 — evaluate a per-tool doc against v1 template spec.

    Ratchet semantics per T1b ship-shape §3:

    - No ``Template version:`` field → ``warn`` (legacy advisory).
    - ``Template version:`` present but value doesn't match ``^v\\d+$``
      → ``fail`` with ``template_version_invalid`` (Rigby SIGN C edit).
    - ``Template variant:`` present but not in ``{sweep, protocol}``
      → ``fail`` with ``template_variant_invalid``.
    - ``Template version: v1`` + valid variant + all mandatory sections
      present + all required frontmatter fields present (alias-tolerant,
      presence-not-exact) → ``pass``.
    - Any section/field missing under a valid v1 declaration → ``fail``
      with per-missing-item lint tags.

    Returns::

        {
            'verdict': 'pass' | 'warn' | 'fail',
            'variant': str | None,
            'missing': list[str],  # lint tags, empty for pass/warn
        }
    """
    per_tool = docs_index.get('per_tool_stems') or {}
    if stem not in per_tool:
        # Not a per-tool doc; no verdict.
        return {'verdict': 'warn', 'variant': None, 'missing': []}

    version = (docs_index.get('template_version_by_stem') or {}).get(stem)
    variant = (docs_index.get('template_variant_by_stem') or {}).get(stem)

    if version is None:
        # Legacy: advisory warn only, no missing-item enumeration.
        return {'verdict': 'warn', 'variant': variant, 'missing': []}

    missing: List[str] = []

    if not TEMPLATE_VERSION_VALID_RE.match(version):
        missing.append('template_version_invalid')
        return {'verdict': 'fail', 'variant': variant, 'missing': missing}

    if variant not in TEMPLATE_VARIANTS:
        missing.append('template_variant_invalid')
        return {'verdict': 'fail', 'variant': variant, 'missing': missing}

    # v1 semantics implemented below. Add new version branches here.
    if version == 'v1':
        required_fields = (
            _SWEEP_REQUIRED_FIELDS if variant == 'sweep'
            else _PROTOCOL_REQUIRED_FIELDS
        )
        mandatory_sections = (
            _SWEEP_MANDATORY_SECTIONS if variant == 'sweep'
            else _PROTOCOL_MANDATORY_SECTIONS
        )

        present_fields = (
            docs_index.get('frontmatter_fields_by_stem') or {}
        ).get(stem, set())
        for slot, aliases in required_fields:
            if not any(a in present_fields for a in aliases):
                missing.append(f'template_v1_missing_frontmatter_{slot}')

        heading_titles = (
            docs_index.get('heading_titles_by_stem') or {}
        ).get(stem, [])

        # Covered-actions section uses the loosened regex; other
        # sections match by title-prefix (case-sensitive on the
        # normalized heading title).
        covered = (docs_index.get('covered_actions_by_stem') or {}).get(stem)
        for slot, title_prefix in mandatory_sections:
            if slot == 'covered_actions':
                if covered is None:
                    missing.append('template_v1_missing_covered_actions')
                continue
            found = any(
                title.startswith(title_prefix) for title in heading_titles
            )
            if not found:
                missing.append(f'template_v1_missing_{slot}')

    if missing:
        return {'verdict': 'fail', 'variant': variant, 'missing': missing}
    return {'verdict': 'pass', 'variant': variant, 'missing': []}


def find_matching_doc_stem(
    tool_name: str, per_tool_stems: Dict[str, Any]
) -> Optional[str]:
    """Match a tool name to a per-tool validation doc stem.

    Order of match strategies:
      1. Exact match on tool name.
      2. Exact match on tool name minus ``_tool`` suffix.
      3. Doc stem contains ``tool_name`` minus ``_tool`` suffix
         (e.g. ``session_tool`` → ``session_tool``; ``kb_tool`` →
         ``kb_ingest`` via containment).
    """
    if tool_name in per_tool_stems:
        return tool_name
    stem_without_suffix = (
        tool_name[: -len('_tool')] if tool_name.endswith('_tool') else tool_name
    )
    if stem_without_suffix in per_tool_stems:
        return stem_without_suffix
    # Loose containment — the base stem appears as prefix or as an
    # underscore-separated segment inside a doc stem.
    for doc_stem in per_tool_stems:
        if doc_stem == stem_without_suffix:
            return doc_stem
        if doc_stem.startswith(stem_without_suffix + '_'):
            return doc_stem
        if ('_' + stem_without_suffix) in doc_stem:
            return doc_stem
    return None


def classify_tool(
    tool_name: str,
    has_schema: bool,
    has_handler: bool,
    schema_actions: Iterable[str],
    docs_index: Dict[str, Any],
    is_agent_via_run_agent: bool = False,
) -> str:
    """Return a single category tag for the tool.

    See module docstring for the full list of categories.
    """
    if tool_name in META_NO_HANDLER:
        return 'meta_no_handler'
    if has_schema and not has_handler:
        return 'orphan_schema'
    if has_handler and not has_schema:
        if is_agent_via_run_agent:
            # S3045: agent-via-run_agent tools have no dedicated PA tool
            # schema (they're reached via `run_agent(agent_name=...)`),
            # so they never enter the schema+handler validation-coverage
            # path below. But they CAN have per-tool validation docs
            # authored from runtime dispatch evidence. When such a doc
            # exists, classify as ``agent_via_run_agent_validated`` so
            # the audit metric reflects RaaS validation without
            # inflating ``validated_full`` (which still requires
            # schema+handler + Covered actions coverage).
            per_tool = docs_index.get('per_tool_stems', {})
            if find_matching_doc_stem(tool_name, per_tool) is not None:
                return 'agent_via_run_agent_validated'
            return 'agent_via_run_agent'
        return 'handler_only_dead'

    # Both schema + handler present: assess validation coverage.
    per_tool = docs_index.get('per_tool_stems', {})
    covered_by_stem = docs_index.get('covered_actions_by_stem', {})
    matched_stem = find_matching_doc_stem(tool_name, per_tool)
    if matched_stem is not None:
        covered = covered_by_stem.get(matched_stem)
        actions_set = set(schema_actions) if schema_actions else set()
        if covered is None:
            return 'validated_doc_exists_unknown'
        if not actions_set:
            # Non-action-multiplexed tool with covered_actions heading;
            # any coverage counts as "full" (no unmapped actions).
            return 'validated_full'
        missing = actions_set - covered
        return 'validated_full' if not missing else 'validated_partial'
    # No per-tool doc.
    # covered_substrate_only would need substrate doc body-scan to
    # confirm the tool is called out by name — we don't do that scan
    # (F2 mitigation: substrate docs don't validate per-tool invariants
    # anyway). Emit ``untested`` as the honest signal.
    return 'untested'


def lint_schema(schema: Optional[Dict[str, Any]]) -> List[str]:
    """Return schema-quality lint tags (Rigby S2795 F5 mitigation).

    Empty list = no lints. Advisory only; does not gate anything.
    """
    if not schema:
        return []
    lints: List[str] = []
    description = (schema.get('description') or '').strip()
    if not description:
        lints.append('missing_description')
    elif len(description) < SHORT_DESC_THRESHOLD_CHARS:
        lints.append('short_description')

    parameters = schema.get('parameters', {}) or {}
    properties = parameters.get('properties', {}) or {}
    required = parameters.get('required', []) or []
    if not properties:
        lints.append('no_properties')
    if not required:
        lints.append('no_required')

    action_prop = properties.get('action') or {}
    actions = list(action_prop.get('enum', []) or [])
    if actions and description:
        desc_lower = description.lower()
        mentioned = sum(1 for a in actions if a.lower() in desc_lower)
        threshold = max(1, int(len(actions) * ACTIONS_MENTIONED_RATIO))
        if mentioned < threshold:
            lints.append('actions_not_mentioned_in_description')
    return lints


def lint_schema_vs_handler(
    schema: Optional[Dict[str, Any]],
    handler_source: str,
    handler_docstring: str,
) -> List[str]:
    """Return schema-vs-handler consistency lint tags (Ledger #5 substrate).

    S2938 Tier 1 MVP per Rigby T0 SIGN AGREE. Two lints, both parse-based
    and precision-first (false negatives acceptable; false positives are
    the failure mode to avoid). Advisory only; does not gate anything.

    Lints emitted:

      * ``handler_drift_action_count`` — module docstring names an action
        count (via number word or digit followed by "action(s)") that
        disagrees with ``schema.parameters.properties.action.enum``
        length. Silent when docstring omits the count claim.

      * ``handler_drift_negative_claim_{dispatch,mutation,feature_flag}``
        — module docstring asserts a negative behavioral claim (e.g.
        "No agent dispatch", "read-only", "always live") but the handler
        source contains a contradicting evidence signature (celery
        primitives, ORM writes, settings/env reads, or curated
        service-layer functions like ``rigby_mission_delegation``).

    Deferred to Tier 2 (separate ship): envelope-JSON top-level-key
    parity check against schema description text. See module docstring.
    """
    if not schema or not handler_docstring:
        return []
    lints: List[str] = []

    # ── Lint 1: docstring action-count vs schema enum length ─────────
    parameters = schema.get('parameters', {}) or {}
    properties = parameters.get('properties', {}) or {}
    action_prop = properties.get('action') or {}
    schema_actions = list(action_prop.get('enum', []) or [])
    if schema_actions:
        match = _DOCSTRING_ACTION_COUNT_RE.search(handler_docstring)
        if match:
            raw = match.group(1).lower()
            claimed = _NUMBER_WORD_TO_INT.get(raw)
            if claimed is None:
                try:
                    claimed = int(raw)
                except ValueError:
                    claimed = None
            if claimed is not None and claimed != len(schema_actions):
                lints.append('handler_drift_action_count')

    # ── Lint 2: docstring negative claim vs handler-source evidence ──
    if handler_source:
        for domain, claim_re in _NEGATIVE_CLAIM_PATTERNS.items():
            if not claim_re.search(handler_docstring):
                continue
            evidence_re = _EVIDENCE_SIGNATURES.get(domain)
            if evidence_re is None:
                continue
            if evidence_re.search(handler_source):
                lints.append(f'handler_drift_negative_claim_{domain}')

    return lints


def _handler_file_for(handler_file_str: str) -> str:
    """Bucket handler_file into a short slug for grouping.

    ``core/services/td_handlers_content.py`` → ``td_handlers_content``.
    ``core/services/tool_dispatcher.py`` → ``tool_dispatcher``.
    Anything else → ``other``.
    """
    if not handler_file_str:
        return 'other'
    p = Path(handler_file_str)
    stem = p.stem
    if stem.startswith('td_handlers_') or stem == 'tool_dispatcher':
        return stem
    return 'other'


def build_triage_slices(
    rows: List[Dict[str, Any]],
    max_slices: int = 5,
    min_untested_per_slice: int = 3,
) -> List[Dict[str, Any]]:
    """Fold F3 mitigation: group untested tools by handler file + emit
    top-N slices with rationale and estimated session count.

    Estimated sessions assume ~4 tools per session, matching the
    S2728→S2732 4-tools-per-batch pace (18 tools in 4 batches over 5
    sessions).

    Returns a list of dicts, each shaped::

        {
            'theme': 'td_handlers_content',
            'tools': ['blog_tool', 'campaign_tool', …],
            'untested_count': N,
            'rationale': 'These N untested tools all dispatch through …',
            'est_sessions': ceil(N / 4),
        }
    """
    import math

    by_file: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        if row.get('category') != 'untested':
            continue
        bucket = _handler_file_for(row.get('handler_file') or '')
        by_file[bucket].append(row['name'])

    slices: List[Dict[str, Any]] = []
    ranked = sorted(by_file.items(), key=lambda kv: -len(kv[1]))
    for theme, tools in ranked:
        if len(tools) < min_untested_per_slice:
            continue
        slices.append({
            'theme': theme,
            'tools': sorted(tools),
            'untested_count': len(tools),
            'rationale': (
                f"{len(tools)} untested tools dispatch through "
                f"`{theme}`. Grouping keeps validation-cycle setup cost "
                f"low — one handler file, consistent primitives."
            ),
            'est_sessions': math.ceil(len(tools) / 4),
        })
        if len(slices) >= max_slices:
            break
    return slices


def build_gap_map(
    rows: List[Dict[str, Any]],
    docs_index: Dict[str, Any],
    schemas_by_name: Dict[str, Dict[str, Any]],
    run_agent_targets: Set[str],
) -> Dict[str, Any]:
    """Enrich each row with ``category`` + ``lints`` + return summary.

    Input ``rows`` are the shape produced by
    ``build_pa_tool_audit.Command._inspect``.

    Mutates rows in place. Returns::

        {
            'headline': {
                'total_rows': N,
                'per_category': Counter,
                'per_lint': Counter,
            },
            'triage_slices': list[dict],
            'validation_doc_totals': dict,  # from docs_index
        }
    """
    for row in rows:
        name = row['name']
        schema = schemas_by_name.get(name)
        is_agent_via = (
            row['has_handler']
            and not row['has_schema']
            and name in run_agent_targets
        )
        category = classify_tool(
            tool_name=name,
            has_schema=row['has_schema'],
            has_handler=row['has_handler'],
            schema_actions=row.get('actions', []),
            docs_index=docs_index,
            is_agent_via_run_agent=is_agent_via,
        )
        row['category'] = category
        row['lints'] = lint_schema(schema) + lint_schema_vs_handler(
            schema,
            row.get('handler_source', '') or '',
            row.get('handler_docstring', '') or '',
        )

        # T1b S2904 — template-compliance evaluation. Only per-tool
        # docs get a meaningful verdict; tools without a doc land as
        # warn-with-no-missing.
        matched_stem = find_matching_doc_stem(
            name, docs_index.get('per_tool_stems') or {}
        )
        if matched_stem is not None:
            compliance = evaluate_template_compliance(matched_stem, docs_index)
        else:
            compliance = {'verdict': 'warn', 'variant': None, 'missing': []}
        row['template_compliance'] = compliance['verdict']
        row['template_variant'] = compliance['variant']
        row['template_missing'] = compliance['missing']

        # S2942 Ledger #41 — two-metric scoreboard per row. Tools with
        # no matched validation doc get 'unknown' (no silent default).
        if matched_stem is not None:
            row['execution_mode'] = (
                docs_index.get('execution_mode_by_stem') or {}
            ).get(matched_stem, UNKNOWN_LABEL)
            row['mutation_safety'] = (
                docs_index.get('mutation_safety_by_stem') or {}
            ).get(matched_stem, UNKNOWN_LABEL)
        else:
            row['execution_mode'] = UNKNOWN_LABEL
            row['mutation_safety'] = UNKNOWN_LABEL

    per_category = Counter(r['category'] for r in rows)
    per_lint: Counter = Counter()
    for r in rows:
        for lint_tag in r.get('lints', []):
            per_lint[lint_tag] += 1
        for missing_tag in r.get('template_missing', []):
            per_lint[missing_tag] += 1

    per_template_compliance = Counter(
        r.get('template_compliance', 'warn') for r in rows
    )

    # S2942 Ledger #41 — headline scoreboard aggregates.
    per_execution_mode = Counter(
        r.get('execution_mode', UNKNOWN_LABEL) for r in rows
    )
    per_mutation_safety = Counter(
        r.get('mutation_safety', UNKNOWN_LABEL) for r in rows
    )

    triage = build_triage_slices(rows)

    return {
        'headline': {
            'total_rows': len(rows),
            'per_category': dict(per_category),
            'per_lint': dict(per_lint),
            'per_template_compliance': dict(per_template_compliance),
            # S2942 Ledger #41 — Metric A (live read-only) + Metric B
            # (mutation-under-dry_run) surfaced as per-value tallies.
            'per_execution_mode': dict(per_execution_mode),
            'per_mutation_safety': dict(per_mutation_safety),
        },
        'triage_slices': triage,
        'validation_doc_totals': {
            'total_docs': docs_index.get('total_docs', 0),
            'substrate_docs': len(docs_index.get('substrate_stems', set())),
            'per_tool_docs': len(docs_index.get('per_tool_stems', {})),
            'per_tool_docs_with_covered_actions': sum(
                1 for v in docs_index.get('covered_actions_by_stem', {}).values()
                if v is not None
            ),
            'per_tool_docs_with_template_version': sum(
                1 for v in (
                    docs_index.get('template_version_by_stem') or {}
                ).values()
                if v is not None
            ),
            # S2942 Ledger #41 — count of per-tool docs that opted into
            # each scoreboard field.
            'per_tool_docs_with_execution_mode': sum(
                1 for v in (
                    docs_index.get('execution_mode_by_stem') or {}
                ).values()
                if v != UNKNOWN_LABEL
            ),
            'per_tool_docs_with_mutation_safety': sum(
                1 for v in (
                    docs_index.get('mutation_safety_by_stem') or {}
                ).values()
                if v != UNKNOWN_LABEL
            ),
        },
    }


# ── Rendering helpers for the extended audit doc ─────────────────────


CATEGORY_LABEL: Dict[str, str] = {
    'validated_full': 'validated (full)',
    'validated_partial': 'validated (partial)',
    'validated_doc_exists_unknown': 'validated (doc, unknown coverage)',
    'covered_substrate_only': 'substrate only',
    'untested': 'untested',
    'orphan_schema': 'orphan schema',
    'meta_no_handler': 'meta (no handler by design)',
    'agent_via_run_agent': 'agent (via run_agent)',
    'agent_via_run_agent_validated': 'agent via run_agent (validated)',
    'handler_only_dead': 'dead handler',
}


def render_gap_map_markdown(
    rows: List[Dict[str, Any]],
    summary: Dict[str, Any],
    docs_index: Dict[str, Any],
) -> str:
    """Render a standalone gap-map markdown artifact.

    Used with ``build_pa_tool_audit --gap-only --output <path>``.
    """
    lines: List[str] = []
    lines.append(
        '<!-- DOC-AUTOGEN: regenerated by '
        '`python manage.py build_pa_tool_audit --gap-only`. Do not hand-edit. -->'
    )
    lines.append('')
    lines.append('# PA Tools — Validation Coverage Gap Map')
    lines.append('')
    lines.append(
        '**Sources of truth (cross-referenced live):** '
        '`core.services.pa_tool_schemas.PA_TOOL_SCHEMAS` + '
        '`core.services.tool_dispatcher.ToolDispatcher._tool_handlers` + '
        '`docs/research/tools/validation/*_validation.md`.'
    )
    lines.append('')
    lines.append(
        '**Advisory posture:** this map lists what has validation '
        'evidence and what does not. It is NOT a burn-down queue; '
        'triage slices below are decision aids, not commitments. '
        'Chris picks what to validate. (S2795 F3 mitigation.)'
    )
    lines.append('')

    lines.append('## Headline')
    lines.append('')
    headline = summary['headline']
    lines.append(f"- **Total tool names:** {headline['total_rows']}")
    lines.append('- **Per-category breakdown:**')
    per_cat = headline['per_category']
    for cat, n in sorted(per_cat.items(), key=lambda kv: -kv[1]):
        label = CATEGORY_LABEL.get(cat, cat)
        lines.append(f'  - `{cat}` ({label}): **{n}**')
    # S3045 RaaS-validated rollup: sum of ``validated_full`` +
    # ``agent_via_run_agent_validated``. Categories stay distinct so the
    # architectural difference (schema+handler vs run_agent-dispatched)
    # remains visible; the rollup is a decision-velocity aid, not a
    # metric redefinition.
    raas_validated = (
        per_cat.get('validated_full', 0)
        + per_cat.get('agent_via_run_agent_validated', 0)
    )
    lines.append(
        f'- **RaaS-validated** (`validated_full` + '
        f'`agent_via_run_agent_validated`): **{raas_validated}**'
    )
    lines.append('')

    lines.append('## Validation-doc corpus')
    lines.append('')
    v = summary['validation_doc_totals']
    lines.append(f"- **Total `*_validation.md` files:** {v['total_docs']}")
    lines.append(
        f"- **Substrate (cross-cutting) docs:** {v['substrate_docs']} — "
        "reduce risk platform-wide but do NOT validate per-tool invariants "
        "(S2795 F2 rename)."
    )
    lines.append(
        f"- **Per-tool docs:** {v['per_tool_docs']} — of which "
        f"{v['per_tool_docs_with_covered_actions']} have an explicit "
        "'Covered actions' section (F1 checklist)."
    )
    template_version_count = v.get('per_tool_docs_with_template_version', 0)
    lines.append(
        f"- **Per-tool docs with `Template version` marker:** "
        f"{template_version_count} (T1b S2904 opt-in ratchet — legacy "
        "docs without the marker stay `warn` advisory)."
    )
    lines.append('')

    # T1b (S2904) template-compliance summary.
    per_tc = headline.get('per_template_compliance') or {}
    if per_tc:
        lines.append('## Template compliance (T1b)')
        lines.append('')
        lines.append(
            'Ratchet-and-warn per T1b ship-shape §3. `warn` is advisory '
            '(legacy docs without `Template version:` marker); `pass` = '
            'v1-conformant; `fail` = v1 marker present but mandatory '
            'section/frontmatter missing.'
        )
        lines.append('')
        for verdict, n in sorted(per_tc.items(), key=lambda kv: -kv[1]):
            lines.append(f'- `{verdict}`: **{n}**')
        fail_rows = [r for r in rows if r.get('template_compliance') == 'fail']
        if fail_rows:
            lines.append('')
            lines.append('**Failing docs (T1b blocking):**')
            for r in fail_rows:
                missing_str = ', '.join(r.get('template_missing', [])) or '?'
                lines.append(f'- `{r["name"]}` — {missing_str}')
        lines.append('')

    # S2942 Ledger #41 — two-metric scoreboard: Execution mode + Mutation safety.
    per_em = headline.get('per_execution_mode') or {}
    per_ms = headline.get('per_mutation_safety') or {}
    if per_em or per_ms:
        lines.append('## Two-metric scoreboard (S2942 Ledger #41)')
        lines.append('')
        lines.append(
            'Opt-in per-tool frontmatter classification. Missing fields '
            'land as `unknown` (no silent default per plan §2.1 acceptance).'
        )
        lines.append('')
        em_with = v.get('per_tool_docs_with_execution_mode', 0)
        ms_with = v.get('per_tool_docs_with_mutation_safety', 0)
        lines.append(
            f'- **Metric A — `Execution mode:` opt-ins:** {em_with} of '
            f"{v['per_tool_docs']} per-tool docs."
        )
        for value, n in sorted(per_em.items(), key=lambda kv: -kv[1]):
            lines.append(f'  - `{value}`: **{n}** tools')
        lines.append(
            f'- **Metric B — `Mutation safety:` opt-ins:** {ms_with} of '
            f"{v['per_tool_docs']} per-tool docs."
        )
        for value, n in sorted(per_ms.items(), key=lambda kv: -kv[1]):
            lines.append(f'  - `{value}`: **{n}** tools')
        lines.append('')

    if headline.get('per_lint'):
        lines.append('## Schema quality lints (F5 advisory column)')
        lines.append('')
        for tag, n in sorted(headline['per_lint'].items(), key=lambda kv: -kv[1]):
            lines.append(f'- `{tag}`: **{n}** tools')
        lines.append('')

    lines.append('## Triage slices (F3 decision aid — pick, do not queue)')
    lines.append('')
    slices = summary['triage_slices']
    if not slices:
        lines.append('_No untested-tool groups met the threshold._')
    else:
        for s in slices:
            lines.append(
                f"### `{s['theme']}` — {s['untested_count']} untested "
                f"(~{s['est_sessions']} session{'s' if s['est_sessions'] != 1 else ''} at 4/session)"
            )
            lines.append('')
            lines.append(f"_{s['rationale']}_")
            lines.append('')
            for t in s['tools']:
                lines.append(f'- `{t}`')
            lines.append('')

    # Per-tool detail table
    lines.append('## Per-tool coverage table')
    lines.append('')
    lines.append(
        '| Tool | Wiring | Category | Template | Lint | Handler file |'
    )
    lines.append('|---|:-:|---|:-:|---|---|')
    for row in rows:
        wiring = (
            '✓✓' if (row['has_schema'] and row['has_handler']) else
            ('schema' if row['has_schema'] else 'handler')
        )
        cat = row.get('category', 'untested')
        cat_label = CATEGORY_LABEL.get(cat, cat)
        lints_str = ', '.join(row.get('lints', [])) or '—'
        handler_file = row.get('handler_file', '') or '—'
        tc = row.get('template_compliance', 'warn')
        tc_glyph = {'pass': '✓', 'warn': 'warn', 'fail': '✗'}.get(tc, tc)
        lines.append(
            f"| `{row['name']}` | {wiring} | {cat_label} | {tc_glyph} | "
            f"{lints_str} | `{handler_file}` |"
        )
    lines.append('')

    return '\n'.join(lines) + '\n'
