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

Stable ``expected_outcome`` values (v2):
    - ``'success'``                      — READ_ONLY dispatched, ToolResult.ok, response is clean
    - ``'soft_error'``                   — READ_ONLY dispatched, ToolResult.ok=True, but response dict
                                            carries an inline error envelope (``ok=False`` or
                                            ``error_code`` present). Application-layer failure at
                                            HTTP 200. Introduced at v2 (S2909 substrate cleanup arc T1).
    - ``'error_captured'``               — READ_ONLY dispatched, ToolResult.ok=False (dispatcher-layer error)
    - ``'exception'``                    — READ_ONLY dispatched, handler raised
    - ``'skipped_metadata_missing'``     — unclassified, no dispatch (Q4a)
    - ``'skipped_write_gated'``          — WRITE_GATED, no dispatch at MVP
    - ``'skipped_mutation'``             — MUTATION, no dispatch
    - ``'skipped_irreversible'``         — IRREVERSIBLE, no dispatch
    - ``'skipped_bridge_unreachable'``   — READ_ONLY dispatch-eligible, but the external bridge
                                            preflight probe failed. Distinguishes "env-config
                                            issue" (bridge disabled / offline) from "real tool
                                            bug". Introduced at v2 (S2909 substrate cleanup
                                            arc T2). Bridge-per-action mapping lives in
                                            ``ToolActionMetadata.bridge`` via ``resolve_bridge``.

Migration notes — v1 → v2 (S2909 T1)
------------------------------------

Background: S2905–S2908 sweep batches surfaced a systemic pattern where
``ToolResult.ok=True`` responses carried inline ``{ok: false, error, error_code}``
envelopes (transport succeeded, tool signalled application-layer failure).
The v1 classifier read only ``ToolResult.ok`` and mis-labelled these as
``'success'``. The Fold B drift-rate trend across 3 data points (87.5% × 2 + 75%)
crossed the "3-data-point 50% floor" trigger and Chris ratified the substrate
cleanup arc at S2909 open.

**What changed:** ``_run_single_action`` now inspects the response dict when
``ToolResult.ok=True``. If the dict contains ``ok=False`` or an ``error_code``
key, the outcome is reclassified from ``'success'`` to ``'soft_error'``.

**What did NOT change (Fold Q4 mitigation, per Rigby T0 SIGN):**
Per-tool validation docs under ``docs/research/tools/validation/*.md`` are
hand-authored evidence narratives — the harness does NOT auto-regenerate them.
Post-backfill, harness artifact JSON may show many actions flipped from
``'success'`` → ``'soft_error'`` while the corresponding validation docs still
narrate "SUCCESS" in their post-merge live-dispatch sections. This is a KNOWN
new parity-gap type (harness ↔ validation-doc drift, distinct from the
existing schema ↔ doc parity gate at Fold B). Follow-up substrate row is
queued in the Rigby Tool Gap Ledger; a lightweight lint may be added in a
future arc. Do NOT bulk-update validation docs as part of T1 — that would
break MVP discipline and the arc's anti-scope-creep constraint.

**Backfill scope:** all in-class tools (broadened from Rigby T0 SIGN Q3
narrow evidentiary scope of 15 sweep-covered tools; contract-version bump
requires uniform v2 artifact set — mixed v1/v2 would be worse). Analysis
focus stays on the 15 sweep-covered tools per Fold B measurement scope.
Post-implementation SIGN Q2 AGREE.

Migration notes — T2 (bridge availability precheck)
---------------------------------------------------

**What T2 adds:** external-bridge preflight probes that short-circuit
dispatch for READ_ONLY actions whose bridge is unreachable. New stable
``expected_outcome='skipped_bridge_unreachable'``. Bridge dependency is
declared on the per-action ``ToolActionMetadata.bridge`` field (via
``core.services.tool_action_metadata.resolve_bridge``).

**Probe discipline (per Rigby T2 SIGN Q4 fold #1 — critical):** probes
call the SAME client the tool uses, never a re-derived URL. Env-var
sprawl (``RESOLVE_NODE_URL`` vs ``DAVINCI_BRIDGE_URL``) means a re-derived
probe would hit the wrong port and false-positive-skip healthy tools.

**Probe timeouts (per Rigby T2 SIGN Q2 REVISE):** 5s for resolve_node
(matches ``ResolveNodeClient`` internal timeout); 3s for obs (short
because the ``_obs_enabled()`` env gate short-circuits before HTTP).

**Cache:** results cached on the ``Command`` instance for the duration
of a single harness invocation (one probe per bridge per run).

**Reachability semantics (per Rigby T2 SIGN Q4 fold #3):** "reachable"
means network/HTTP responded — the probe does NOT inspect application
health. A bridge returning HTTP 500 counts as reachable; the tool
dispatch will then surface application-layer errors as ``soft_error``,
which is the correct distinction.

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

HARNESS_VERSION = 'v2'


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
                    if a['expected_outcome']
                    in ('success', 'soft_error', 'error_captured')
                ),
                'soft_error_count': sum(
                    1 for a in artifact['actions']
                    if a['expected_outcome'] == 'soft_error'
                ),
                'skipped_bridge_unreachable_count': sum(
                    1 for a in artifact['actions']
                    if a['expected_outcome'] == 'skipped_bridge_unreachable'
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
            total_dispatched = (
                summary_rows
                and sum(r['read_only_dispatched'] for r in summary_rows)
            ) or 0
            total_soft_errors = (
                summary_rows
                and sum(r.get('soft_error_count', 0) for r in summary_rows)
            ) or 0
            total_bridge_skips = (
                summary_rows
                and sum(
                    r.get('skipped_bridge_unreachable_count', 0)
                    for r in summary_rows
                )
            ) or 0
            total_missing_meta = (
                summary_rows
                and sum(r['skipped_metadata_missing'] for r in summary_rows)
            ) or 0
            self.stdout.write(self.style.SUCCESS(
                f'Wrote {output_dir.relative_to(REPO_ROOT)}/summary.json '
                f'({len(targets)} tool(s), '
                f'{total_dispatched} READ_ONLY dispatched '
                f'[{total_soft_errors} soft_error / '
                f'{total_bridge_skips} bridge_unreachable], '
                f'{total_missing_meta} skipped for missing metadata)'
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
        from core.services.tool_action_metadata import (
            resolve_bridge,
            resolve_safety,
        )

        artifacts: List[Dict[str, Any]] = []
        for name in targets:
            schema = schema_by_name.get(name) or {}
            actions = _schema_actions(schema)
            action_rows: List[Dict[str, Any]] = []
            for action in actions:
                safety_class, source = resolve_safety(name, action)
                bridge = resolve_bridge(name, action)
                row = await self._run_single_action(
                    dispatcher=dispatcher,
                    tool_name=name,
                    action=action,
                    safety_class=safety_class,
                    resolution_source=source,
                    bridge=bridge,
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
        bridge: Optional[str] = None,
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

        # T2 bridge preflight (S2909 arc): if action depends on an external
        # bridge, probe the bridge once (cached per-harness-run) and short-
        # circuit dispatch if unreachable. Distinguishes env-config outages
        # from real tool bugs. See module docstring "Migration notes — T2".
        if bridge:
            reachable, probe_reason = self._probe_bridge(bridge)
            if not reachable:
                return {
                    'action': action,
                    'safety_class': safety_class,
                    'resolution_source': resolution_source,
                    'input_profile': 'skipped_no_dispatch',
                    'expected_outcome': 'skipped_bridge_unreachable',
                    'status_code': None,
                    'latency_ms': 0,
                    'response_shape_keys': [],
                    'notes': f'bridge={bridge}; {probe_reason}',
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
        response_dict: Optional[Dict[str, Any]] = None
        if isinstance(result.result, dict):
            response_dict = result.result
            response_keys = sorted(response_dict.keys())

        # v2 classifier (S2909 T1): reclassify transport-success + inline
        # error-envelope as 'soft_error'. Distinguishes application-layer
        # failure at HTTP 200 from clean success. See module docstring
        # "Migration notes — v1 → v2" for background.
        if outcome == 'success' and response_dict is not None:
            if response_dict.get('ok') is False or 'error_code' in response_dict:
                outcome = 'soft_error'

        note_bits: List[str] = []
        if not result.ok:
            err_code = getattr(result, 'error_code', None) or ''
            err_msg = getattr(result, 'error_message', None) or ''
            if err_code:
                note_bits.append(f'error_code={err_code}')
            if err_msg:
                note_bits.append(f'msg={err_msg[:120]}')
        elif outcome == 'soft_error' and response_dict is not None:
            inline_code = response_dict.get('error_code') or ''
            inline_err = response_dict.get('error') or ''
            if inline_code:
                note_bits.append(f'inline_error_code={inline_code}')
            if isinstance(inline_err, str) and inline_err:
                note_bits.append(f'inline_msg={inline_err[:120]}')
            elif isinstance(inline_err, dict):
                nested_code = inline_err.get('code') or ''
                nested_msg = inline_err.get('msg') or inline_err.get('message') or ''
                if nested_code:
                    note_bits.append(f'inline_error_nested_code={nested_code}')
                if isinstance(nested_msg, str) and nested_msg:
                    note_bits.append(f'inline_msg={nested_msg[:120]}')

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

    # -------------------------------------------------------------- bridges

    def _probe_bridge(self, bridge_name: str) -> tuple[bool, str]:
        """Preflight-probe an external bridge (T2, S2909 arc).

        Cached on the ``Command`` instance for one harness invocation. Each
        probe reuses the SAME client the corresponding tool uses (per Rigby
        T2 SIGN Q4 fold #1 — never re-derive URLs, or env-var sprawl like
        ``RESOLVE_NODE_URL`` vs ``DAVINCI_BRIDGE_URL`` would false-positive
        skip healthy tools).

        Returns:
            ``(reachable: bool, reason: str)``. ``reachable=True`` on any
            HTTP response (even 4xx/5xx — application state is out of scope
            per Q4 fold #3); ``reachable=False`` only on env-config gates
            or network-level failures (``RequestException`` / status=0).
        """
        cache = getattr(self, '_bridge_probe_cache', None)
        if cache is None:
            cache = {}
            self._bridge_probe_cache = cache
        if bridge_name in cache:
            return cache[bridge_name]

        if bridge_name == 'obs':
            from core.views_obs import _obs_bridge_request, _obs_enabled
            if not _obs_enabled():
                result = (False, 'OBS_ENABLED env not set')
            else:
                try:
                    status, _data, _latency = _obs_bridge_request(
                        'GET', '/health', timeout=3,
                    )
                    if status > 0:
                        result = (True, '')
                    else:
                        result = (False, 'obs bridge network unreachable')
                except Exception as exc:  # noqa: BLE001
                    result = (
                        False,
                        f'obs bridge probe raised: '
                        f'{type(exc).__name__}: {str(exc)[:120]}',
                    )
        elif bridge_name == 'resolve_node':
            try:
                from core.agents.resolve_agent import ResolveNodeClient
                # ResolveNodeClient.health_check() uses its own 5s timeout
                # and catches RequestException internally — it returns
                # ``{'status': 'offline', ...}`` only when the network call
                # failed. Any other value means HTTP responded.
                probe_result = ResolveNodeClient().health_check()
                probe_status = (probe_result or {}).get('status')
                if probe_status == 'offline':
                    err = (probe_result or {}).get('error') or 'no detail'
                    result = (
                        False,
                        f'resolve_node bridge offline: {str(err)[:120]}',
                    )
                else:
                    result = (True, '')
            except Exception as exc:  # noqa: BLE001
                result = (
                    False,
                    f'resolve_node bridge probe raised: '
                    f'{type(exc).__name__}: {str(exc)[:120]}',
                )
        else:
            # Unknown bridge name — do NOT block dispatch; treat as
            # reachable so a metadata typo can't accidentally short-circuit
            # legitimate tools. Surface via notes so it shows up in review.
            result = (True, f'unknown bridge name {bridge_name!r} — probe skipped')

        cache[bridge_name] = result
        return result

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
