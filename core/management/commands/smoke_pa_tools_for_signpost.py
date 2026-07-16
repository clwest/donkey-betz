"""
S2799: smoke-test PA tools that will be signposted in Rigby's system prompt.

Ship shape B (joint Claude+Rigby SIGN): iterate Rigby's top-15 zero-fire schema
picks with safe read-only dispatch actions she named at T2, capture pass/empty/
fail/blocked, so the S2799 signpost slice only signposts tools that actually
work when invoked. Prevents amplifying broken tools by giving them prompt
routing hints before validation.

Verdicts:
  - OK          — dispatch returned coherent JSON with non-empty data
  - SMOKE_EMPTY — dispatched cleanly but returned empty (data not populated yet;
                  still signpostable — Rigby will honestly report emptiness on
                  invocation)
  - SMOKE_FAIL  — handler exception or ToolResult.ok=False; not signposted
  - SMOKE_BLOCKED — no safe read-only action variant exists; excluded from smoke

Usage:
  python manage.py smoke_pa_tools_for_signpost
  python manage.py smoke_pa_tools_for_signpost --as-json
"""

import asyncio
import json
import traceback
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


# (tool_name, action, extra_payload_args)
SMOKE_SPECS: List[Tuple[str, str, Dict[str, Any]]] = [
    ('rigby_shift_brief_tool', 'generate', {'window': '24h'}),
    ('employee_tool', 'status', {'employee': 'rigby', 'job': 'docs_manager', 'window': '7d'}),
    ('zoom_out_tool', 'list', {'limit': 5}),
    ('learning_tool', 'stats', {'limit': 10}),
    ('learning_patterns_tool', 'stats', {'limit': 10}),
    ('workflow_run_tool', 'list', {'limit': 5}),
    ('gates_tool', 'stats', {'limit': 10}),
    ('pilots_tool', 'stats', {'limit': 10}),
    ('revenue_tracker_tool', 'stats', {}),
    ('self_awareness_tool', 'metrics', {'limit': 5}),
    ('brainstorm_tool', 'stats', {'limit': 10}),
    ('ops_digest_tool', 'generate', {'window': '24h'}),
    ('heartbeat_history_tool', 'recent', {'limit': 5}),
    ('surgical_moves_status_tool', 'status', {'verbose': False}),
]

# Tools with no safe read-only action variant (all mutations require IDs
# we don't have at smoke time). Excluded from smoke; noted in output.
BLOCKED: List[Tuple[str, str]] = [
    ('mission_verdict', 'all actions (certify/reject/defer) require mission_id — write-only'),
]


def _classify_result(tool_result) -> Tuple[str, Optional[str]]:
    """Return (verdict, note). Note: ToolResult's payload is on .result (not .data)."""
    if not tool_result.ok:
        err = getattr(tool_result, 'error_message', None) or getattr(tool_result, 'error_code', None) or 'ToolResult.ok=False'
        return 'SMOKE_FAIL', str(err)[:400]

    payload = getattr(tool_result, 'result', None)
    if payload is None:
        return 'SMOKE_EMPTY', 'result payload is None'
    if isinstance(payload, dict):
        if not payload:
            return 'SMOKE_EMPTY', 'result payload is empty dict'
        # Some handlers wrap emptiness in a status envelope (e.g. {"status":"ok","items":[]}).
        # Heuristic: if payload has recognizable "empty" markers, count as EMPTY.
        if all(v in (None, [], {}, 0, '') for k, v in payload.items() if k not in ('status', 'ok')):
            return 'SMOKE_EMPTY', f'result payload has only status/ok keys with empty values: {list(payload.keys())}'
    if isinstance(payload, list) and not payload:
        return 'SMOKE_EMPTY', 'result payload is empty list'
    return 'OK', None


async def _run_smokes(user_id) -> List[Dict[str, Any]]:
    dispatcher = ToolDispatcher()
    rows: List[Dict[str, Any]] = []

    for tool_name, action, extra in SMOKE_SPECS:
        payload = {'action': action, **extra}
        try:
            result = await dispatcher.execute(
                tool_name=tool_name,
                payload=payload,
                user_id=user_id,
                agent_name='SmokeCheck',
                record_telemetry=False,
            )
            verdict, note = _classify_result(result)
            data_summary = _summarize_data(getattr(result, 'result', None))
            rows.append({
                'tool': tool_name,
                'action': action,
                'verdict': verdict,
                'note': note,
                'data_summary': data_summary,
            })
        except Exception as e:
            rows.append({
                'tool': tool_name,
                'action': action,
                'verdict': 'SMOKE_FAIL',
                'note': f'exception: {type(e).__name__}: {str(e)[:200]}',
                'data_summary': None,
                'traceback': traceback.format_exc()[:800],
            })

    for tool_name, reason in BLOCKED:
        rows.append({
            'tool': tool_name,
            'action': None,
            'verdict': 'SMOKE_BLOCKED',
            'note': reason,
            'data_summary': None,
        })

    return rows


def _summarize_data(data) -> Optional[str]:
    if data is None:
        return None
    if isinstance(data, dict):
        keys = list(data.keys())[:8]
        return f'dict with {len(data)} keys: {keys}'
    if isinstance(data, list):
        return f'list of {len(data)}'
    return f'{type(data).__name__}: {str(data)[:80]}'


class Command(BaseCommand):
    help = 'S2799: smoke-test PA tools before signposting them in Rigbys system prompt.'

    def add_arguments(self, parser):
        parser.add_argument('--as-json', action='store_true', help='emit JSON only')
        parser.add_argument('--user', default='chris', help='username to dispatch as (default: chris)')

    def handle(self, *args, **options):
        user = User.objects.filter(username=options['user']).first()
        if not user:
            self.stderr.write(f'user not found: {options["user"]}')
            return
        rows = asyncio.run(_run_smokes(user.id))

        if options['as_json']:
            self.stdout.write(json.dumps(rows, indent=2, default=str))
            return

        # Human-readable table
        counts = {'OK': 0, 'SMOKE_EMPTY': 0, 'SMOKE_FAIL': 0, 'SMOKE_BLOCKED': 0}
        for r in rows:
            counts[r['verdict']] = counts.get(r['verdict'], 0) + 1

        self.stdout.write('')
        self.stdout.write('S2799 PA TOOL SMOKE — signpost eligibility')
        self.stdout.write('=' * 72)
        for r in rows:
            verdict = r['verdict']
            marker = {'OK': 'PASS', 'SMOKE_EMPTY': 'EMPTY', 'SMOKE_FAIL': 'FAIL', 'SMOKE_BLOCKED': 'BLOCK'}.get(verdict, '?')
            self.stdout.write(f'[{marker:5}] {r["tool"]:35} action={r["action"] or "-":10} — {r.get("data_summary") or r.get("note") or ""}')
        self.stdout.write('=' * 72)
        self.stdout.write(f'PASS={counts["OK"]}  EMPTY={counts["SMOKE_EMPTY"]}  FAIL={counts["SMOKE_FAIL"]}  BLOCK={counts["SMOKE_BLOCKED"]}')
        self.stdout.write('')
        self.stdout.write('Signposts earned by: PASS + EMPTY. Not signposted: FAIL + BLOCK.')
        if counts['SMOKE_FAIL'] >= 4:
            self.stdout.write('')
            self.stdout.write('WARN: SMOKE_FAIL >= 4/14 = future_trigger fired for Option-B (fix broken agents/tools) next session.')
