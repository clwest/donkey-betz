"""
S2800 Option B: smoke-test the 5 broken agents from S2799 Thread 1 audit.

Purpose: capture baseline failure signature per agent BEFORE fixes ship, so
we have machine-parseable evidence that post-fix behavior improved. Extends
the S2799 smoke-gate pattern to agent-level (S2799 was tool-level).

Reads S2799 finding: 4 of 5 failures are worker-restart orphans (heartbeat
thread dies with worker; cleanup watchdog marks failed at 60min stale);
1 of 5 (CodeReviewAgent) is a real agent-logic bug (no code inspection or
review completed when task has no file path).

This command dispatches each of the 5 agents with a benign task and records:
  - OK               — agent returned success=True with coherent data
  - SMOKE_FAIL       — agent returned success=False with unexpected error
  - SMOKE_MISSING    — agent returned MISSING_INPUT (post-fix behavior for
                       CodeReviewAgent — still a PASS because actionable)
  - SMOKE_TIMEOUT    — dispatch hung past our per-agent timeout
  - SMOKE_EXCEPTION  — dispatch raised an exception

Re-run post-fix to verify SMOKE_FAIL → OK / SMOKE_MISSING transitions.

Usage:
  python manage.py smoke_broken_agents_pre_fix
  python manage.py smoke_broken_agents_pre_fix --as-json
"""

import asyncio
import json
import time
import traceback
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand


# (agent_name, benign_task_prompt, notes_about_expected_failure_mode)
AGENT_SPECS = [
    (
        'CodeReviewAgent',
        'review my code',  # no file path — the S2799 Thread 1 failure pattern
        'S2799 Thread 1 finding: 76% fail rate — "No code inspection or review completed" when task has no discoverable file path or code block. Post-S2800: expects MISSING_INPUT with actionable message.',
    ),
    (
        'WorkflowAgent',
        'run a light health-check workflow',
        'S2799 Thread 1: 69% fail — 60min heartbeat timeout on worker restart. Post-S2800: worker-startup orphan-reap → transitions to cancelled, not failed.',
    ),
    (
        'WorkflowOrchestrationAgent',
        'orchestrate a short sanity workflow',
        'S2799 Thread 1: 46% fail — heartbeat timeout cluster.',
    ),
    (
        'CTOAgent',
        'give me a one-line status summary',
        'S2799 Thread 1: 46% fail — heartbeat timeout cluster.',
    ),
    (
        'AudioAgent',
        'ping — capability check only, no TTS',
        'S2799 Thread 1: 53% fail — TTS API payment wall + heartbeat timeout. Post-S2800: shipping worker-startup reap fix; TTS payment wall is a separate follow-up (config, not code).',
    ),
]


PER_AGENT_TIMEOUT_S = 30  # generous but not open-ended


def _dispatch_sync(agent_name: str, task: str):
    """Sync-callable wrapper that instantiates the router and dispatches."""
    from core.agent_router import get_agent_router
    router = get_agent_router()
    return router.route(
        agent_name=agent_name,
        task=task,
        context={'trigger_source': 'smoke_broken_agents_pre_fix'},
        create_execution_record=True,
        trigger_source='direct_dispatch',
    )


async def _dispatch_one(agent_name: str, task: str) -> Dict[str, Any]:
    """Import + dispatch a single agent with a benign task."""
    started = time.time()
    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_dispatch_sync, agent_name, task),
            timeout=PER_AGENT_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        return {
            'verdict': 'SMOKE_TIMEOUT',
            'note': f'no return within {PER_AGENT_TIMEOUT_S}s',
            'elapsed_s': time.time() - started,
        }
    except Exception as e:
        return {
            'verdict': 'SMOKE_EXCEPTION',
            'note': f'{type(e).__name__}: {str(e)[:200]}',
            'traceback': traceback.format_exc()[:500],
            'elapsed_s': time.time() - started,
        }

    elapsed = time.time() - started
    # AgentResult vs dict return — handle both
    if hasattr(result, 'success'):
        ok = getattr(result, 'success', False)
        err = getattr(result, 'error', '') or ''
        msg = getattr(result, 'message', '') or ''
        data = getattr(result, 'data', {}) or {}
    elif isinstance(result, dict):
        ok = result.get('success', False)
        err = result.get('error', '') or ''
        msg = result.get('message', '') or ''
        data = result.get('data', {}) or {}
    else:
        return {
            'verdict': 'SMOKE_EXCEPTION',
            'note': f'unexpected return type: {type(result).__name__}',
            'elapsed_s': elapsed,
        }

    if ok:
        return {'verdict': 'OK', 'msg': msg[:120], 'elapsed_s': elapsed}

    # Post-S2800: CodeReviewAgent's MISSING_INPUT is a pass (structured signal
    # replaces the terse "No code inspection or review completed").
    code = str(data.get('error_code', '')) if isinstance(data, dict) else ''
    if code == 'MISSING_INPUT' or 'MISSING_INPUT' in err:
        return {'verdict': 'SMOKE_MISSING', 'msg': msg[:120], 'elapsed_s': elapsed}

    return {'verdict': 'SMOKE_FAIL', 'msg': (msg or err)[:200], 'elapsed_s': elapsed}


async def _run(specs: List) -> List[Dict[str, Any]]:
    rows = []
    for agent_name, task, notes in specs:
        outcome = await _dispatch_one(agent_name, task)
        rows.append({
            'agent': agent_name,
            'task': task,
            **outcome,
            'notes': notes,
        })
    return rows


class Command(BaseCommand):
    help = 'S2800 Option B: smoke-test the 5 broken agents from S2799 Thread 1.'

    def add_arguments(self, parser):
        parser.add_argument('--as-json', action='store_true')

    def handle(self, *args, **options):
        rows = asyncio.run(_run(AGENT_SPECS))

        if options['as_json']:
            self.stdout.write(json.dumps(rows, indent=2, default=str))
            return

        counts = {}
        for r in rows:
            counts[r['verdict']] = counts.get(r['verdict'], 0) + 1

        self.stdout.write('')
        self.stdout.write('S2800 BROKEN-AGENT SMOKE — baseline / post-fix verification')
        self.stdout.write('=' * 78)
        for r in rows:
            marker = {
                'OK': 'PASS',
                'SMOKE_MISSING': 'MISS',
                'SMOKE_FAIL': 'FAIL',
                'SMOKE_TIMEOUT': 'TOUT',
                'SMOKE_EXCEPTION': 'EXPT',
            }.get(r['verdict'], '?')
            self.stdout.write(f'[{marker}] {r["agent"]:32} ({r.get("elapsed_s", 0):.1f}s) — {r.get("msg") or r.get("note") or ""}')
        self.stdout.write('=' * 78)
        parts = [f'{k}={v}' for k, v in sorted(counts.items())]
        self.stdout.write('  '.join(parts))
        self.stdout.write('')
        self.stdout.write('PASS = agent returned success=True.')
        self.stdout.write('MISS = agent returned MISSING_INPUT with actionable message (S2800 post-fix expected for CodeReviewAgent).')
        self.stdout.write('FAIL = unexpected failure signature — investigate.')
