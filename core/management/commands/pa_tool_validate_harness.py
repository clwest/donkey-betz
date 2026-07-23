"""pa_tool_validate_harness — auto-harness for the PA Tools Sweep.

Enumerates PA tool schemas, classifies each action by safety, dispatches
READ_ONLY actions in-process against ``ToolDispatcher``, captures response +
latency + shape, and emits a per-tool JSON artifact + summary rollup.

Ratified at S2902 (Row 161 substrate arc, T1a Phase 1) via Claude+Rigby joint
SIGN + Chris green-light. The four design decisions locked in this cycle:

1. **Safety enum** (Q1): 4 values from :mod:`core.services.tool_action_metadata`.
2. **Metadata field set** (Q2): 3 fields per action; env/deps encoded in notes.
3. **Fold B parity** (Q3): ``--check-doc-schema-parity`` exits non-zero on
   ``schema.actions ⊆ doc.covered_actions`` mismatch; escalation recommendation
   emitted to artifact + stdout. NO ``PA_TOOLS_GAP_MAP.md`` mutation
   (preserves DOC-AUTOGEN contract — gap-map regen picks it up naturally).
4. **Unclassified default** (Q4a): missing metadata → ``status='skipped'``,
   ``reason='metadata_missing'``, no dispatch attempted. Full schema action
   inventory still enumerated so the artifact isn't a silent hole.

Non-goals (per T1a §2 + parent §2):
    - NOT an HTTP-surface tester.
    - NOT an auth-boundary tester (runs with ``user_id=None`` by default).
    - NOT a mutation exerciser (MUTATION + IRREVERSIBLE actions are skipped).
    - NOT a replacement for ``http_smoke_test``; output schema is superset-
      compatible so future work can feed harness output into smoke replay.

Anti-goal (T1c Fold D): the harness verifies **every** in-class tool
regardless of doc-status. ``validated_full`` is a doc-status label, not
runtime confidence.

In-class filter (T1c Fold A boundary):
    ``has_schema=True AND has_handler=True AND name != 'run_agent'``
The 44 ``agent_via_run_agent`` handlers (schema-less) are excluded because
``run_agent`` is intercepted at ``unified_pa_entrypoint.py:2236`` before the
dispatcher and rewrites ``tool_name`` — validating them here would double-
count via the rewrite boundary.

Usage::

    python manage.py pa_tool_validate_harness ops_tool
    python manage.py pa_tool_validate_harness --all-in-class
    python manage.py pa_tool_validate_harness --check-doc-schema-parity
    python manage.py pa_tool_validate_harness --summary-only --all-in-class
    python manage.py pa_tool_validate_harness ops_tool --check    # dry-run

Output artifacts (stable filenames — no timestamps in path per zoom-out
mitigation; timestamp + git_sha live inside ``run_metadata`` block):

    docs/audits/pa_tools/harness_output/<tool_name>.json
    docs/audits/pa_tools/harness_output/summary.json

Artifact schema v1 — frozen contract for T1b consumers
-------------------------------------------------------

Per T1a §5 + S2902 post-scaffold SIGN (Rigby zoom-out on artifact versioning),
these fields are STABLE for ``HARNESS_VERSION == 'v1'``. Adding new fields is
backward-compatible; renaming, removing, or changing types requires a MINOR
version bump (``'v2'``) with a migration note in this docstring block and a
substrate-arc-scoped SIGN.

Per-tool artifact::

    {
      "tool_name": str,
      "harness_version": "v1",
      "run_metadata": {"generated_at": str, "git_sha": str},
      "schema_action_count": int,
      "actions": [
        {
          "action": str,
          "safety_class": str | null,       # SafetyClass value or null if unclassified
          "resolution_source": str,          # 'action' | 'tool_default' | 'unclassified'
          "input_profile": str,              # 'minimal_safe_args_v1' | 'skipped_no_dispatch'
          "expected_outcome": str,           # see stable set below
          "status_code": int | null,
          "latency_ms": int,
          "response_shape_keys": list[str],
          "notes": str | null,
        },
        ...
      ]
    }

Stable ``expected_outcome`` values (v1):
    - ``'success'``                      — READ_ONLY dispatched, ToolResult.ok
    - ``'error_captured'``               — READ_ONLY dispatched, ToolResult.ok=False
    - ``'exception'``                    — READ_ONLY dispatched, handler raised
    - ``'skipped_metadata_missing'``     — unclassified, no dispatch (Q4a)
    - ``'skipped_write_gated'``          — WRITE_GATED, no dispatch at MVP
    - ``'skipped_mutation'``             — MUTATION, no dispatch
    - ``'skipped_irreversible'``         — IRREVERSIBLE, no dispatch

Summary rollup::

    {
      "harness_version": "v1",
      "run_metadata": {"generated_at": str, "git_sha": str},
      "in_class_total": int,
      "targets_run": int,
      "parity_mismatches": list[{tool_name, doc_stem, missing_actions, reason, escalation_recommendation}],
      "top_missing_metadata": list[{tool_name, missing_action_count}],
      "tools": list[{tool_name, action_count, read_only_dispatched, skipped_metadata_missing, skipped_write_gated, artifact_sha256}],
    }
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import subprocess
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from django.core.management.base import BaseCommand, CommandError


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / 'docs' / 'audits' / 'pa_tools' / 'harness_output'

HARNESS_VERSION = 'v1'


# ── Git SHA helper (matches the ``platform_inventory._git_sha`` pattern) ────


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ['git', '-C', str(REPO_ROOT), 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return '(unavailable)'


# ── Command ─────────────────────────────────────────────────────────────────


class Command(BaseCommand):
    help = (
        'Run the PA tool validation harness — dispatch READ_ONLY actions '
        'in-process, capture response + latency, emit JSON artifacts. '
        'T1a Phase 1 ship of the Row 161 substrate arc.'
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            'tool_name',
            nargs='?',
            default=None,
            help='Specific tool to harness. Omit + pass --all-in-class to run all.',
        )
        parser.add_argument(
            '--all-in-class',
            action='store_true',
            help='Run harness against every in-class tool (Fold A filter).',
        )
        parser.add_argument(
            '--check-doc-schema-parity',
            action='store_true',
            help=(
                'Fold B: verify schema.actions ⊆ doc.covered_actions for tools '
                'that have a per-tool validation doc. Non-zero exit on mismatch.'
            ),
        )
        parser.add_argument(
            '--summary-only',
            action='store_true',
            help=(
                'Skip writing per-tool JSON artifacts; write summary.json only. '
                'Useful for CI/lint invocations where per-tool churn is unwanted.'
            ),
        )
        parser.add_argument(
            '--output',
            type=str,
            default=None,
            help=(
                'Override output directory (default: '
                'docs/audits/pa_tools/harness_output/). Path resolved relative '
                'to repo root when not absolute.'
            ),
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Dry-run: print artifacts to stdout instead of writing files.',
        )

    # ------------------------------------------------------------------ handle

    def handle(self, *args: Any, **opts: Any) -> None:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        from core.services.tool_dispatcher import ToolDispatcher
        from core.services.pa_tools_gap_map import (
            find_matching_doc_stem,
            index_validation_docs,
        )

        tool_name: Optional[str] = opts.get('tool_name')
        all_in_class: bool = bool(opts.get('all_in_class'))
        parity_gate: bool = bool(opts.get('check_doc_schema_parity'))
        summary_only: bool = bool(opts.get('summary_only'))
        dry_run: bool = bool(opts.get('check'))

        # Standalone parity mode: flag set AND no target AND no --all-in-class.
        # Runs parity check across ALL in-class tools, skips harness dispatch.
        standalone_parity: bool = (
            parity_gate and not tool_name and not all_in_class
        )

        if not tool_name and not all_in_class and not parity_gate:
            raise CommandError(
                'Pass either <tool_name> positional arg OR --all-in-class '
                'OR --check-doc-schema-parity.'
            )

        # Enumerate all tools + build in-class set.
        dispatcher = ToolDispatcher()
        schema_by_name: Dict[str, Dict[str, Any]] = {
            str(s.get('name', '')): s
            for s in PA_TOOL_SCHEMAS
            if s.get('name')
        }
        handler_names: Set[str] = set(dispatcher._tool_handlers.keys())  # noqa: SLF001
        in_class_names: Set[str] = self._compute_in_class(
            schema_by_name=schema_by_name, handler_names=handler_names
        )

        # Resolve target list.
        if tool_name:
            if tool_name not in in_class_names:
                # Explicit tool — surface why it's excluded.
                reason = self._exclusion_reason(
                    tool_name, schema_by_name, handler_names
                )
                raise CommandError(
                    f"'{tool_name}' is not in-class for the harness: {reason}"
                )
            targets = [tool_name]
        else:
            targets = sorted(in_class_names)

        # Parity check (Fold B) — can be run standalone.
        docs_index = index_validation_docs(
            REPO_ROOT / 'docs' / 'research' / 'tools' / 'validation'
        )
        parity_mismatches = self._run_parity_check(
            targets=targets,
            schema_by_name=schema_by_name,
            docs_index=docs_index,
        )
        if standalone_parity:
            self._report_parity(parity_mismatches, dry_run=dry_run)
            if parity_mismatches:
                raise CommandError(
                    f'schema↔doc parity mismatch on '
                    f'{len(parity_mismatches)} tool(s). See report above.'
                )
            return

        # Resolve output directory.
        output_dir = self._resolve_output_dir(opts.get('output'))

        # Dispatch harness runs.
        artifacts = asyncio.run(
            self._run_harness_for_targets(
                dispatcher=dispatcher,
                targets=targets,
                schema_by_name=schema_by_name,
            )
        )

        # Write per-tool artifacts (unless --summary-only).
        summary_rows: List[Dict[str, Any]] = []
        for artifact in artifacts:
            tool_hash = _sha256_json(artifact)
            summary_rows.append({
                'tool_name': artifact['tool_name'],
                'action_count': len(artifact['actions']),
                'read_only_dispatched': sum(
                    1 for a in artifact['actions']
                    if a['expected_outcome'] in ('success', 'error_captured')
                ),
                'skipped_metadata_missing': sum(
                    1 for a in artifact['actions']
                    if a['expected_outcome'] == 'skipped_metadata_missing'
                ),
                'skipped_write_gated': sum(
                    1 for a in artifact['actions']
                    if a['expected_outcome'] == 'skipped_write_gated'
                ),
                'artifact_sha256': tool_hash,
            })
            if summary_only:
                continue
            if dry_run:
                self.stdout.write(f'--- {artifact["tool_name"]}.json ---')
                self.stdout.write(json.dumps(artifact, indent=2))
                continue
            _write_json(
                output_dir / f'{artifact["tool_name"]}.json',
                artifact,
            )

        # Metadata coverage report (zoom-out mitigation).
        top_missing = self._top_missing_metadata_report(artifacts)

        summary = {
            'harness_version': HARNESS_VERSION,
            'run_metadata': {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'git_sha': _git_sha(),
            },
            'in_class_total': len(in_class_names),
            'targets_run': len(targets),
            'parity_mismatches': parity_mismatches,
            'top_missing_metadata': top_missing,
            'tools': summary_rows,
        }
        if dry_run:
            self.stdout.write('--- summary.json ---')
            self.stdout.write(json.dumps(summary, indent=2))
        else:
            _write_json(output_dir / 'summary.json', summary)
            self.stdout.write(self.style.SUCCESS(
                f'Wrote {output_dir.relative_to(REPO_ROOT)}/summary.json '
                f'({len(targets)} tool(s), '
                f'{summary_rows and sum(r["read_only_dispatched"] for r in summary_rows) or 0} '
                f'READ_ONLY dispatched, '
                f'{summary_rows and sum(r["skipped_metadata_missing"] for r in summary_rows) or 0} '
                f'skipped for missing metadata)'
            ))

        # Fold B: non-zero exit gated on the explicit --check-doc-schema-parity
        # flag. Default runs record mismatches to the summary artifact but do
        # NOT block — the flag is the CI-style gate (T1c §11 Fold B language:
        # "block the heading-fix bundle if any of the 8 tools show drift").
        # A default-mode blow-up would prevent all downstream sweep work if a
        # single tool drifted, which is not the intended semantic.
        if parity_mismatches and opts.get('check_doc_schema_parity'):
            raise CommandError(
                f'schema↔doc parity mismatch on '
                f'{len(parity_mismatches)} tool(s). '
                f'See summary.parity_mismatches or rerun with '
                f'--check-doc-schema-parity for the standalone report.'
            )

    # ------------------------------------------------------------ in-class

    @staticmethod
    def _compute_in_class(
        *,
        schema_by_name: Dict[str, Dict[str, Any]],
        handler_names: Set[str],
    ) -> Set[str]:
        """Return the set of tool names eligible for harness dispatch.

        Fold A filter: must have BOTH a schema and a handler AND must not be
        the ``run_agent`` meta-tool. The 44 ``agent_via_run_agent`` handlers
        are excluded implicitly because they have no schema.
        """
        return {
            name
            for name in schema_by_name.keys() & handler_names
            if name != 'run_agent'
        }

    @staticmethod
    def _exclusion_reason(
        tool_name: str,
        schema_by_name: Dict[str, Dict[str, Any]],
        handler_names: Set[str],
    ) -> str:
        if tool_name == 'run_agent':
            return 'meta-tool (Fold A): intercepted at unified_pa_entrypoint before dispatcher'
        has_schema = tool_name in schema_by_name
        has_handler = tool_name in handler_names
        if not has_schema and not has_handler:
            return 'unknown tool (no schema, no handler)'
        if not has_schema:
            return 'handler-only (schema-less; reachable only via run_agent meta-tool)'
        if not has_handler:
            return 'schema without registered handler (orphan schema)'
        return 'unknown exclusion reason'

    # -------------------------------------------------------------- dispatch

    async def _run_harness_for_targets(
        self,
        *,
        dispatcher: Any,
        targets: List[str],
        schema_by_name: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        from core.services.tool_action_metadata import resolve_safety

        artifacts: List[Dict[str, Any]] = []
        for name in targets:
            schema = schema_by_name.get(name) or {}
            actions = _schema_actions(schema)
            action_rows: List[Dict[str, Any]] = []
            for action in actions:
                safety_class, source = resolve_safety(name, action)
                row = await self._run_single_action(
                    dispatcher=dispatcher,
                    tool_name=name,
                    action=action,
                    safety_class=safety_class,
                    resolution_source=source,
                )
                action_rows.append(row)
            artifacts.append({
                'tool_name': name,
                'harness_version': HARNESS_VERSION,
                'run_metadata': {
                    'generated_at': datetime.now(timezone.utc).isoformat(),
                    'git_sha': _git_sha(),
                },
                'schema_action_count': len(actions),
                'actions': action_rows,
            })
        return artifacts

    async def _run_single_action(
        self,
        *,
        dispatcher: Any,
        tool_name: str,
        action: str,
        safety_class: Optional[str],
        resolution_source: str,
    ) -> Dict[str, Any]:
        # Q4a: unclassified → skip entirely.
        if safety_class is None:
            return {
                'action': action,
                'safety_class': None,
                'resolution_source': resolution_source,
                'input_profile': 'skipped_no_dispatch',
                'expected_outcome': 'skipped_metadata_missing',
                'status_code': None,
                'latency_ms': 0,
                'response_shape_keys': [],
                'notes': (
                    'metadata missing — no dispatch attempted. Author an entry '
                    'in TOOL_ACTION_METADATA or TOOL_DEFAULTS to include.'
                ),
            }

        # WRITE_GATED / MUTATION / IRREVERSIBLE: skip dispatch at MVP.
        # T1a §3 allows schema-edge testing for WRITE_GATED but the joint
        # SIGN cycle deferred that pattern until we have metadata density
        # to distinguish "auth-only gated" from "requires-required-args".
        if safety_class != 'READ_ONLY':
            return {
                'action': action,
                'safety_class': safety_class,
                'resolution_source': resolution_source,
                'input_profile': 'skipped_no_dispatch',
                'expected_outcome': f'skipped_{safety_class.lower()}',
                'status_code': None,
                'latency_ms': 0,
                'response_shape_keys': [],
                'notes': f'{safety_class} — not exercised at T1a MVP',
            }

        # READ_ONLY: dispatch with minimal safe payload.
        payload = {'action': action}
        start = time.time()
        try:
            result = await dispatcher.execute(
                tool_name=tool_name,
                payload=payload,
                user_id=None,
                agent_name='HarnessRunner',
                record_telemetry=False,
            )
        except Exception as exc:  # noqa: BLE001 — capture is the point
            latency_ms = int((time.time() - start) * 1000)
            return {
                'action': action,
                'safety_class': safety_class,
                'resolution_source': resolution_source,
                'input_profile': 'minimal_safe_args_v1',
                'expected_outcome': 'exception',
                'status_code': None,
                'latency_ms': latency_ms,
                'response_shape_keys': [],
                'notes': f'{type(exc).__name__}: {str(exc)[:200]}',
            }
        latency_ms = int((time.time() - start) * 1000)

        outcome = 'success' if result.ok else 'error_captured'
        response_keys: List[str] = []
        if isinstance(result.result, dict):
            response_keys = sorted(result.result.keys())
        note_bits: List[str] = []
        if not result.ok:
            err_code = getattr(result, 'error_code', None) or ''
            err_msg = getattr(result, 'error_message', None) or ''
            if err_code:
                note_bits.append(f'error_code={err_code}')
            if err_msg:
                note_bits.append(f'msg={err_msg[:120]}')

        return {
            'action': action,
            'safety_class': safety_class,
            'resolution_source': resolution_source,
            'input_profile': 'minimal_safe_args_v1',
            'expected_outcome': outcome,
            'status_code': 200 if result.ok else 500,
            'latency_ms': latency_ms,
            'response_shape_keys': response_keys,
            'notes': '; '.join(note_bits) if note_bits else None,
        }

    # --------------------------------------------------------------- parity

    def _run_parity_check(
        self,
        *,
        targets: List[str],
        schema_by_name: Dict[str, Dict[str, Any]],
        docs_index: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Fold B: for each target that has a matching per-tool validation
        doc, verify ``schema.actions ⊆ doc.covered_actions``.

        Returns the list of mismatches; empty list means clean parity.
        """
        from core.services.pa_tools_gap_map import find_matching_doc_stem

        per_tool_stems = docs_index.get('per_tool_stems', {})
        covered_by_stem = docs_index.get('covered_actions_by_stem', {})

        mismatches: List[Dict[str, Any]] = []
        for name in targets:
            schema = schema_by_name.get(name) or {}
            schema_actions = set(_schema_actions(schema))
            if not schema_actions:
                continue
            matched_stem = find_matching_doc_stem(name, per_tool_stems)
            if matched_stem is None:
                continue  # No per-tool doc — nothing to compare against.
            covered = covered_by_stem.get(matched_stem)
            if covered is None:
                # Doc exists but no `## Covered actions` heading — that's the
                # exact case T1c §11 Fold B calls out.
                mismatches.append({
                    'tool_name': name,
                    'doc_stem': matched_stem,
                    'missing_actions': sorted(schema_actions),
                    'reason': 'no_covered_actions_heading',
                    'escalation_recommendation': (
                        'promote_to_sweep (heading absent — cannot verify parity)'
                    ),
                })
                continue
            missing = schema_actions - covered
            if missing:
                mismatches.append({
                    'tool_name': name,
                    'doc_stem': matched_stem,
                    'missing_actions': sorted(missing),
                    'reason': 'schema_actions_not_in_doc',
                    'escalation_recommendation': (
                        'promote_to_sweep (doc drift — schema has new actions '
                        'not covered by the validation report)'
                    ),
                })
        return mismatches

    def _report_parity(
        self,
        mismatches: List[Dict[str, Any]],
        *,
        dry_run: bool,
    ) -> None:
        if not mismatches:
            self.stdout.write(self.style.SUCCESS(
                'schema↔doc parity clean — no mismatches.'
            ))
            return
        self.stdout.write(self.style.WARNING(
            f'schema↔doc parity mismatches: {len(mismatches)} tool(s).'
        ))
        for m in mismatches:
            self.stdout.write(f'  · {m["tool_name"]} ({m["reason"]})')
            self.stdout.write(f'      doc_stem: {m["doc_stem"]}')
            self.stdout.write(
                f'      missing_actions: {", ".join(m["missing_actions"])}'
            )
            self.stdout.write(
                f'      → {m["escalation_recommendation"]}'
            )

    # ---------------------------------------------------- missing-meta rpt

    @staticmethod
    def _top_missing_metadata_report(
        artifacts: List[Dict[str, Any]],
        top_n: int = 10,
    ) -> List[Dict[str, Any]]:
        counts: Counter = Counter()
        for art in artifacts:
            missing = sum(
                1 for a in art['actions']
                if a['expected_outcome'] == 'skipped_metadata_missing'
            )
            if missing:
                counts[art['tool_name']] = missing
        return [
            {'tool_name': name, 'missing_action_count': n}
            for name, n in counts.most_common(top_n)
        ]

    # --------------------------------------------------------------- paths

    @staticmethod
    def _resolve_output_dir(override: Optional[str]) -> Path:
        if not override:
            return DEFAULT_OUTPUT_DIR
        target = Path(override)
        if not target.is_absolute():
            target = REPO_ROOT / target
        return target


# ── Small helpers ───────────────────────────────────────────────────────────


def _schema_actions(schema: Dict[str, Any]) -> List[str]:
    params = schema.get('parameters', {}) or {}
    props = params.get('properties', {}) or {}
    action_prop = props.get('action') or {}
    return list(action_prop.get('enum', []) or [])


def _sha256_json(obj: Dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True).encode('utf-8')
    ).hexdigest()[:16]


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
