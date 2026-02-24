#!/usr/bin/env python3
"""
PA Mutation Tool Testing Script — Session 1062
Tests Tier 2 PA tools (mutations + LLM calls) on Railway.
Phase 1: Read-only actions on mutation tools
Phase 2: Actual mutations (safe ones only)
Phase 3: run_agent + legal_doc_drafter_agent
"""
import urllib.request
import json
import time
import sys

TOKEN = '43d46129f9d92d5f454c4f8fced36b744a53d248'
BASE = 'https://donkey-betz-platform-production.up.railway.app'

# Phase 1: Read-only actions on mutation-capable tools
PHASE1_TESTS = [
    ("dream_tool [read]", "Show me the top dreams sorted by score and dream stats"),
    ("content_review_tool [read]", "List content ready for review and show review stats"),
    ("legislation_tool [read]", "Search legislation data for anything about AI or artificial intelligence"),
    ("opportunity_manager_tool [read]", "List current opportunities and show opportunity stats"),
    ("deliverables_tool [read]", "List recent deliverables and show deliverable stats"),
    ("feedback_tool [read]", "Show feedback stats and list recent feedback submissions"),
]

# Phase 2: Safe mutations (low-risk, reversible)
PHASE2_TESTS = [
    ("feedback_tool [write]", "Submit feedback: The PA tool testing is going great, all read-only tools passed on first try"),
    ("deliverables_tool [save]", "Show me the most recent deliverable and save it to my saved list"),
]

# Phase 3: Agent delegation + specialized agents
PHASE3_TESTS = [
    ("run_agent", "Use the ResearchAgent to research what are the top 3 AI agent frameworks in 2026"),
    ("legal_doc_drafter_agent", "Draft a simple mutual NDA template between two companies"),
    ("research_and_create_tool", "Research the current state of AI coding assistants in 2026 and create a brief summary document"),
]


def send_pa_message(message):
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


def poll_result(task_id, max_wait=60, interval=3):
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
    print(f"\n{'='*70}")
    print(f"TESTING: {tool_name}")
    print(f"PROMPT:  {prompt[:70]}...")
    print(f"{'='*70}")

    try:
        task_id = send_pa_message(prompt)
        if not task_id:
            print(f"  FAIL: No task_id returned")
            return 'FAIL', ''

        print(f"  task_id: {task_id} -- polling...")
        result, elapsed = poll_result(task_id)

        status = result.get('status', 'unknown')
        content = result.get('content', '') or ''
        content_len = len(content)

        print(f"  status:  {status} ({elapsed}s)")
        print(f"  length:  {content_len} chars")

        preview = content[:500].replace('\n', '\n  ')
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


def run_phase(name, tests):
    print(f"\n\n{'#'*70}")
    print(f"# {name}")
    print(f"{'#'*70}")

    results = {}
    for tool_name, prompt in tests:
        grade, content = run_test(tool_name, prompt)
        results[tool_name] = {'grade': grade, 'content_len': len(content)}
        time.sleep(2)

    print(f"\n--- {name} Summary ---")
    for tool, info in results.items():
        tag = {'OK': 'PASS', 'SPARSE': 'WARN', 'TIMEOUT': 'TIME', 'ERROR': 'FAIL', 'EXCEPTION': 'FAIL', 'FAIL': 'FAIL'}
        print(f"  [{tag.get(info['grade'], '????')}] {tool:<40} {info['content_len']:>5} chars")

    ok = sum(1 for v in results.values() if v['grade'] == 'OK')
    print(f"  {ok}/{len(results)} passed")
    return results


def main():
    phase = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    if phase == 1:
        run_phase("PHASE 1: Read-only actions on mutation tools", PHASE1_TESTS)
    elif phase == 2:
        run_phase("PHASE 2: Safe mutations", PHASE2_TESTS)
    elif phase == 3:
        run_phase("PHASE 3: Agent delegation + specialized", PHASE3_TESTS)
    elif phase == 0:
        r1 = run_phase("PHASE 1: Read-only actions on mutation tools", PHASE1_TESTS)
        r2 = run_phase("PHASE 2: Safe mutations", PHASE2_TESTS)
        r3 = run_phase("PHASE 3: Agent delegation + specialized", PHASE3_TESTS)
        all_results = {**r1, **r2, **r3}
        total_ok = sum(1 for v in all_results.values() if v['grade'] == 'OK')
        print(f"\n\nGRAND TOTAL: {total_ok}/{len(all_results)} passed")


if __name__ == '__main__':
    main()
