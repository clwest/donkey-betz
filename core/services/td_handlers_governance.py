"""ToolDispatcher GovernanceHandlersMixin — extracted handler methods.

S2780 N22 v3: dedicated tool surface for governance-scope artifacts.
Split out from ``td_handlers_ops.py`` per S2779 V6 fold + S2780 V7 folds
A + B (semantic boundary erosion; trigger B fired for zoom_out_tool
factor-out). Establishes a discrete home for future governance-adjacent
tool handlers so ``ops_tool`` stays focused on runtime ops signal
(SLO / staleness / failure signatures / worker health).

Current handlers:

  * ``zoom_out_tool`` — read surface for ``logs/zoom_out_classifications.jsonl``.
    Rigby-consumable during joint SIGN loops per PLAYBOOK-6.10.7 + 6.10.8.
    Advisory-only by explicit design — response embeds ``advisory`` header +
    ``is_gate: false`` + ``semantics: "advisory_pattern_evidence"`` to
    prevent advisory→gate drift.
"""
from typing import Any, Dict

from core.services.td_error import _handler_error


class GovernanceHandlersMixin:
    """Mixin providing governance-scoped tool handlers."""

    def _handle_zoom_out(
        self,
        tool_name: str,
        payload: Dict[str, Any],
        user_id,
        trace_id: str,
    ) -> Dict[str, Any]:
        """Dispatch entrypoint for ``zoom_out_tool``.

        S2780 N22 v3 — factored out from ``ops_tool.zoom_out_ledger``
        (S2779) per Trigger B firing (first non-Rigby consumer). See
        ``_zoom_out_list`` for the read-path implementation.
        """
        action = payload.get('action', 'list')
        if action == 'list':
            return self._zoom_out_list(payload, trace_id)
        return _handler_error(
            action,
            'unknown_action',
            f'Unknown zoom_out_tool action: {action}',
        )

    def _zoom_out_list(
        self, payload: Dict[str, Any], trace_id: str
    ) -> Dict[str, Any]:
        """Read tail of ``logs/zoom_out_classifications.jsonl``.

        Rigby's read surface for consulting prior zoom-out folds during
        joint SIGN loops (per PLAYBOOK-6.10.7 + 6.10.8). Ships alongside
        an equivalent Chris-facing UI at ``/api/governance/zoom-out-ledger/``.

        Advisory posture is preserved in three redundant response fields
        (``advisory`` header + ``is_gate: false`` + ``semantics``) to
        prevent advisory→gate drift regardless of consumer surface. See
        the S2777 tail-wags-dog fold (which shaped the CLI companion
        ``zoom_out_streak_report``) and S2779 T1 SIGN V4 fold.

        Filters:
          session: int (exact-match on originating session)
          since_session: int (inclusive lower bound on originating session; S2793 N22 v2)
          until_session: int (inclusive upper bound on originating session; S2793 N22 v2)
          classification: enum (same_pr_actionable / same_pr_mitigatable / future_trigger)
          arc: str (substring match on arc slug)
          limit: int (default 20, max 100) — tail window

        Note: since_session/until_session narrow items[] only. The
        aggregations block (when include=aggregations) still computes over
        ALL rows to preserve longitudinal-signal semantics — see
        test_zoom_out_time_window_2793.py contract 6 for the locked invariant.

        Path-traversal defense mirrors ``_ops_recent_recycles`` — resolve
        against BASE_DIR and refuse reads that escape the tree. Malformed
        JSON lines skipped defensively; ``malformed_lines_skipped`` is
        always present in the response (even when zero).

        See PLAYBOOK-6.10.8 for the constitutional companion (write path
        via ``record_zoom_out_concern``). This handler is the read path.
        """
        import json
        import re
        from collections import Counter
        from pathlib import Path
        from django.conf import settings

        # PLAYBOOK-x.y.z (or x.y for two-level) captured verbatim from
        # concern_text of future_trigger rows for aggregation. Matches the
        # forms Rigby uses in her SIGN folds (see e.g. row 47/50 in the
        # ledger). Case-insensitive; requires at least one dot to avoid
        # picking up bare "PLAYBOOK-6".
        _PLAYBOOK_RULE_RE = re.compile(r'PLAYBOOK-\d+\.\d+(?:\.\d+)?', re.IGNORECASE)

        # Advisory language: keep in sync with
        # core/management/commands/zoom_out_streak_report.py ADVISORY_HEADER.
        ADVISORY_HEADER = (
            "Rigby SIGN zoom-out concern ledger — pattern evidence for review. "
            "Rows are longitudinal signal, not automatic escalation triggers. "
            "Any Playbook codification decision requires its own ratification."
        )

        try:
            limit = int(payload.get('limit', 20) or 20)
        except (TypeError, ValueError):
            limit = 20
        limit = max(1, min(limit, 100))

        classification_filter = payload.get('classification') or None
        arc_filter = (payload.get('arc') or '').strip() or None

        # Autofill guard: LLM commonly autofills integer params with 0
        # (see feedback_llm_autofills_boolean_params_with_false + the
        # _d14_resolve_min_session guard in td_handlers_ops). session=0
        # is never a real session number here — treat as "no filter."
        session_raw = payload.get('session')
        session_filter = None
        if session_raw is not None:
            try:
                candidate = int(session_raw)
                if candidate > 0:
                    session_filter = candidate
            except (TypeError, ValueError):
                session_filter = None

        # S2793 N22 v2: session-int window filters. Same autofill guard —
        # session=0 or negative treated as "no filter" (LLM/UI empty-input
        # normalization). Timestamp-based windows deferred as future_trigger
        # per S2793 Fold 3.
        def _parse_session_bound(raw):
            if raw is None:
                return None
            try:
                candidate = int(raw)
            except (TypeError, ValueError):
                return None
            return candidate if candidate > 0 else None

        since_session_filter = _parse_session_bound(payload.get('since_session'))
        until_session_filter = _parse_session_bound(payload.get('until_session'))

        log_path = Path(settings.BASE_DIR) / 'logs' / 'zoom_out_classifications.jsonl'
        resolved = log_path.resolve()
        base = Path(settings.BASE_DIR).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            return {
                'action': 'list',
                'log_exists': False,
                'log_path': 'logs/zoom_out_classifications.jsonl',
                'advisory': ADVISORY_HEADER,
                'is_gate': False,
                'semantics': 'advisory_pattern_evidence',
                'total_rows': 0,
                'counts_by_classification': {},
                'items': [],
                'count': 0,
                'limit': limit,
                'malformed_lines_skipped': 0,
                'note': 'log path resolved outside BASE_DIR; refusing to read',
            }

        if not resolved.exists():
            return {
                'action': 'list',
                'log_exists': False,
                'log_path': 'logs/zoom_out_classifications.jsonl',
                'advisory': ADVISORY_HEADER,
                'is_gate': False,
                'semantics': 'advisory_pattern_evidence',
                'total_rows': 0,
                'counts_by_classification': {},
                'items': [],
                'count': 0,
                'limit': limit,
                'malformed_lines_skipped': 0,
                'note': (
                    'logs/zoom_out_classifications.jsonl not present. '
                    'The record_zoom_out_concern management command emits '
                    'this file on first classified fold per PLAYBOOK-6.10.8.'
                ),
            }

        try:
            lines = resolved.read_text(errors='replace').splitlines()
        except OSError as exc:
            return {
                'action': 'list',
                'log_exists': True,
                'log_path': 'logs/zoom_out_classifications.jsonl',
                'advisory': ADVISORY_HEADER,
                'is_gate': False,
                'semantics': 'advisory_pattern_evidence',
                'total_rows': 0,
                'counts_by_classification': {},
                'items': [],
                'count': 0,
                'limit': limit,
                'malformed_lines_skipped': 0,
                'note': f'read failed: {exc!s}',
            }

        all_rows: list = []
        malformed = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                malformed += 1
                continue
            if not isinstance(row, dict):
                malformed += 1
                continue
            all_rows.append(row)

        counts = Counter(r.get('classification', 'unknown') for r in all_rows)

        filtered = all_rows
        if classification_filter:
            filtered = [r for r in filtered if r.get('classification') == classification_filter]
        if session_filter is not None:
            filtered = [r for r in filtered if r.get('session') == session_filter]
        if since_session_filter is not None:
            filtered = [
                r for r in filtered
                if isinstance(r.get('session'), int)
                and r['session'] >= since_session_filter
            ]
        if until_session_filter is not None:
            filtered = [
                r for r in filtered
                if isinstance(r.get('session'), int)
                and r['session'] <= until_session_filter
            ]
        if arc_filter:
            filtered = [r for r in filtered if arc_filter in (r.get('arc') or '')]

        recent = filtered[-limit:]

        result: Dict[str, Any] = {
            'action': 'list',
            'log_exists': True,
            'log_path': 'logs/zoom_out_classifications.jsonl',
            'advisory': ADVISORY_HEADER,
            'is_gate': False,
            'semantics': 'advisory_pattern_evidence',
            'total_rows': len(all_rows),
            'counts_by_classification': dict(counts),
            'items': recent,
            'count': len(recent),
            'limit': limit,
            'malformed_lines_skipped': malformed,
        }
        if classification_filter:
            result['classification_filter'] = classification_filter
        if session_filter is not None:
            result['session_filter'] = session_filter
        if since_session_filter is not None:
            result['since_session_filter'] = since_session_filter
        if until_session_filter is not None:
            result['until_session_filter'] = until_session_filter
        if arc_filter:
            result['arc_filter'] = arc_filter

        # S2791: opt-in aggregations for the Sign Ledger drill-down UI.
        # Advisory posture preserved — computed over ALL rows (not filter
        # window) but never affects gating; is_gate stays False.
        include_raw = payload.get('include')
        include_tokens = set()
        if isinstance(include_raw, str):
            include_tokens = {
                t.strip().lower() for t in include_raw.split(',') if t.strip()
            }
        elif isinstance(include_raw, (list, tuple)):
            include_tokens = {
                str(t).strip().lower() for t in include_raw if str(t).strip()
            }
        if 'aggregations' in include_tokens:
            arc_counter: Counter[str] = Counter()
            rule_target_counter: Counter[str] = Counter()
            sessions_seen: set[int] = set()
            for r in all_rows:
                arc = r.get('arc') or ''
                if arc:
                    arc_counter[arc] += 1
                sess = r.get('session')
                if isinstance(sess, int):
                    sessions_seen.add(sess)
                if r.get('classification') == 'future_trigger':
                    concern = r.get('concern_text') or ''
                    for m in _PLAYBOOK_RULE_RE.findall(concern):
                        rule_target_counter[m.upper()] += 1
            result['aggregations'] = {
                'top_arcs_by_count': [
                    {'arc': arc, 'count': n}
                    for arc, n in arc_counter.most_common(20)
                ],
                'future_trigger_rule_targets': [
                    {'rule_id': rid, 'count': n}
                    for rid, n in rule_target_counter.most_common()
                ],
                'sessions_covered': sorted(sessions_seen),
                'is_gate': False,
                'semantics': 'advisory_pattern_evidence',
            }
        return result
