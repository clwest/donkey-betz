#!/usr/bin/env python3
"""
PA Read-Only Tool Testing Script — Session 1062

Tests 17 read-only Tier 3 PA tools on Railway.

Usage:
    export PA_API_TOKEN_TEST="<token>"
    export PA_API_BASE_TEST="https://<railway-host>"  # optional, defaults to prod
    python tests/one-off/test_pa_readonly_tools.py
"""
import os
import urllib.request
import json
import time
import sys

TOKEN = os.environ.get('PA_API_TOKEN_TEST', '')
BASE = os.environ.get(
    'PA_API_BASE_TEST',
    'https://donkey-betz-platform-production.up.railway.app',
)

if not TOKEN:
    print(
        "ERROR: PA_API_TOKEN_TEST not set.\n"
        "This script needs a DRF auth token to hit the PA API.\n"
        "See docs/cleanup/TOKEN_ROTATION_PLAYBOOK.md for how to obtain one.",
        file=sys.stderr,
    )
    sys.exit(1)

# 17 read-only tools with test prompts designed to trigger each one
TESTS = [
    # Batch 1: System health & observability
    ("get_body_vitals", "Show me the body vitals for all systems with details"),
    ("check_resource_budget", "Check if I have budget for 5000 tokens"),
    ("get_system_alerts", "Show me any system alerts, warnings or critical issues"),
    ("cost_telemetry_tool", "Show me LLM cost telemetry summary and top spending agents"),
    ("status_snapshot_tool", "Give me a quick status snapshot of the entire system"),

    # Batch 2: Task & scheduling visibility
    ("scheduled_tasks_tool", "List all scheduled celery beat tasks"),
    ("task_breakdown_tool", "Show me celery task breakdown summary with failure rates"),
    ("recent_activity_tool", "What happened in the system in the last 2 hours?"),

    # Batch 3: Agent & pipeline inspection
    ("agent_introspection_tool", "Inspect the ResearchAgent - what are its capabilities and tools?"),
    ("pipeline_orchestrator_tool", "What's the current pipeline orchestration status?"),
    ("gates_tool", "List all pilot readiness gates"),
    ("pilots_tool", "Show me running pilots and pilot stats"),

    # Batch 4: Content & knowledge
    ("brainstorm_tool", "Search brainstorm sessions for anything about AI agents"),
    ("learning_patterns_tool", "Show me active learning patterns and their effectiveness"),
    ("surgical_moves_status_tool", "Show me deliberation session summary and evidence stats"),
    ("workspace_tool", "List all workspaces"),
    ("task_manager_tool", "List all opportunity tasks"),
]


def send_pa_message(message):
    """Send a message to PA and return task_id."""
    data = json.dumps({'message': message}).encode()
    req = urllib.request.Request(
        f'{BASE}/api/pa/chat/',
        data=data,
        headers={
            'Authorization': f'Token {TOKEN}',
            'Content-Type': 'application/json',
        },
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=30).read())
    return resp.get('task_id')


def poll_result(task_id, max_wait=45, interval=3):
    """Poll for PA result until complete or timeout."""
    elapsed = 0
    while elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        req = urllib.request.Request(
            f'{BASE}/api/pa/chat/status/{task_id}/',
            headers={'Authorization': f'Token {TOKEN}'},
        )
        result = json.loads(urllib.request.urlopen(req, timeout=15).read())
        status = result.get('status', '')
        if status != 'processing':
            return result, elapsed
    return {'status': 'timeout', 'content': ''}, elapsed


def run_test(tool_name, prompt):
    """Run a single PA tool test."""
    print(f"\n{'='*70}")
    print(f"TESTING: {tool_name}")
    print(f"PROMPT:  {prompt[:60]}...")
    print(f"{'='*70}")

    try:
        task_id = send_pa_message(prompt)
        if not task_id:
            print(f"  FAIL: No task_id returned")
            return 'FAIL', 'No task_id'

        print(f"  task_id: {task_id} — polling...")
        result, elapsed = poll_result(task_id)

        status = result.get('status', 'unknown')
        content = result.get('content', '') or ''
        content_len = len(content)

        print(f"  status:  {status} ({elapsed}s)")
        print(f"  length:  {content_len} chars")

        # Show first 400 chars of content
        preview = content[:400].replace('\n', '\n  ')
        print(f"  preview: {preview}")

        if status == 'timeout':
            return 'TIMEOUT', content
        elif status == 'error' or 'error' in content.lower()[:100]:
            return 'ERROR', content
        elif content_len < 50:
            return 'SPARSE', content
        else:
            return 'OK', content

    except Exception as e:
        print(f"  EXCEPTION: {e}")
        return 'EXCEPTION', str(e)


def main():
    # Allow running a subset: python test_pa_readonly_tools.py 0 4
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else len(TESTS)

    tests_to_run = TESTS[start:end]
    print(f"\nRunning {len(tests_to_run)} PA tool tests (index {start}-{end-1})")
    print(f"Target: {BASE}\n")

    results = {}
    for tool_name, prompt in tests_to_run:
        grade, content = run_test(tool_name, prompt)
        results[tool_name] = {
            'grade': grade,
            'content_len': len(content),
        }
        # Small delay between tests to avoid overwhelming PA
        time.sleep(2)

    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for tool, info in results.items():
        emoji = {'OK': 'PASS', 'SPARSE': 'WARN', 'TIMEOUT': 'TIME', 'ERROR': 'FAIL', 'EXCEPTION': 'FAIL', 'FAIL': 'FAIL'}
        print(f"  [{emoji.get(info['grade'], '????')}] {tool:<35} {info['content_len']:>5} chars  ({info['grade']})")

    ok_count = sum(1 for v in results.values() if v['grade'] == 'OK')
    print(f"\n  {ok_count}/{len(results)} passed")


if __name__ == '__main__':
    main()
