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
COVERED_ACTIONS_HEADING_RE = re.compile(
    r'^#+\s+covered\s+actions\b', re.IGNORECASE | re.MULTILINE
)
BACKTICK_IDENT_RE = re.compile(r'`([a-z_][a-z0-9_]*)`')
NEXT_HEADING_RE = re.compile(r'\n#+\s+', re.MULTILINE)


SHORT_DESC_THRESHOLD_CHARS: int = 40
ACTIONS_MENTIONED_RATIO: float = 0.25


def index_validation_docs(docs_dir: Path) -> Dict[str, Any]:
    """Scan ``docs/research/tools/validation/*.md`` and index by role.

    Returns::

        {
            'substrate_stems': set[str],  # cross-cutting docs
            'per_tool_stems': dict[str, Path],  # stem → doc path
            'covered_actions_by_stem': dict[str, set[str] | None],
                # per-tool docs → set of action names mentioned under
                # a "Covered actions" heading (empty set if heading
                # present but empty; None if heading absent).
            'total_docs': int,
        }

    Missing directory returns zero-shape indices (empty dicts/sets).
    """
    substrate: Set[str] = set()
    per_tool: Dict[str, Path] = {}
    covered_by_stem: Dict[str, Optional[Set[str]]] = {}

    if not docs_dir.exists():
        return {
            'substrate_stems': substrate,
            'per_tool_stems': per_tool,
            'covered_actions_by_stem': covered_by_stem,
            'total_docs': 0,
        }

    docs = sorted(docs_dir.glob('*_validation.md'))
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
            continue
        heading_match = COVERED_ACTIONS_HEADING_RE.search(body)
        if not heading_match:
            covered_by_stem[stem] = None
            continue
        # Slice from end-of-heading to next heading (or EOF).
        after = body[heading_match.end():]
        next_heading = NEXT_HEADING_RE.search(after)
        section = after[: next_heading.start()] if next_heading else after
        actions_found = set(BACKTICK_IDENT_RE.findall(section))
        covered_by_stem[stem] = actions_found

    return {
        'substrate_stems': substrate,
        'per_tool_stems': per_tool,
        'covered_actions_by_stem': covered_by_stem,
        'total_docs': len(docs),
    }


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
        return 'agent_via_run_agent' if is_agent_via_run_agent else 'handler_only_dead'

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
        row['lints'] = lint_schema(schema)

    per_category = Counter(r['category'] for r in rows)
    per_lint: Counter = Counter()
    for r in rows:
        for lint_tag in r.get('lints', []):
            per_lint[lint_tag] += 1

    triage = build_triage_slices(rows)

    return {
        'headline': {
            'total_rows': len(rows),
            'per_category': dict(per_category),
            'per_lint': dict(per_lint),
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
    for cat, n in sorted(headline['per_category'].items(), key=lambda kv: -kv[1]):
        label = CATEGORY_LABEL.get(cat, cat)
        lines.append(f'  - `{cat}` ({label}): **{n}**')
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
    lines.append('| Tool | Wiring | Category | Lint | Handler file |')
    lines.append('|---|:-:|---|---|---|')
    for row in rows:
        wiring = (
            '✓✓' if (row['has_schema'] and row['has_handler']) else
            ('schema' if row['has_schema'] else 'handler')
        )
        cat = row.get('category', 'untested')
        cat_label = CATEGORY_LABEL.get(cat, cat)
        lints_str = ', '.join(row.get('lints', [])) or '—'
        handler_file = row.get('handler_file', '') or '—'
        lines.append(
            f"| `{row['name']}` | {wiring} | {cat_label} | {lints_str} | "
            f"`{handler_file}` |"
        )
    lines.append('')

    return '\n'.join(lines) + '\n'
