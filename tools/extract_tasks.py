#!/usr/bin/env python3
"""
Extract large task bodies from core/tasks.py into domain-specific modules.

Approach:
- Parse tasks.py to find all @shared_task decorated functions
- For tasks above a size threshold, extract the function body into a helper
- Replace the original with a thin wrapper that calls the helper
- Group helpers by domain into separate modules

Usage: python tools/extract_tasks.py [--dry-run] [--min-lines 100]
"""
import re
import sys
import os
import textwrap
from pathlib import Path


TASKS_FILE = Path('core/tasks.py')
MIN_BODY_LINES = 50  # Only extract tasks with bodies >= this many lines

# Domain classification for extracted helpers
DOMAIN_RULES = [
    ('codejobs', ['execute_code_job']),
    ('conversations', [
        'run_agent_conversation', 'run_multi_agent_conversation',
        'run_project_conversation', 'run_hive_mind_session',
        'trigger_spider_conversations', 'explore_dream_topic',
    ]),
    ('content', [
        'generate_self_blog', 'generate_content', 'track_content',
        'trigger_content', 'generate_podcast', 'run_source_pack',
        'run_autonomous_thinking', 'run_conceptforge',
        'generate_self_blog_deliberation',
    ]),
    ('initiatives', [
        'dream', 'initiative', 'score_and_promote', 'advance_initiative',
        'execute_initiative', 'cleanup_junk',
    ]),
    ('agents', [
        'execute_agent_task', 'run_agent_learning', 'agent_daily_summary',
        'embed_agent', 'embed_daily_agent', 'generate_agent_dreams',
        'workspace_autopilot', 'universal_agent_workspace',
        'generate_human_attention', 'auto_process_extracted',
        'analyze_pa_tool', 'run_system_self_audit',
    ]),
    ('financial', [
        'stock', 'blockchain', 'market', 'prediction', 'sport',
        'odds', 'ml_scoring', 'train_ml', 'evaluate_and_complete_pilots',
        'snapshot_odds',
    ]),
    ('spiders', [
        'spider', 'run_spider',
    ]),
]


def classify_task(name):
    """Classify a task name into a domain."""
    name_lower = name.lower()
    for domain, patterns in DOMAIN_RULES:
        for p in patterns:
            if p.lower() in name_lower:
                return domain
    return 'misc'


def parse_tasks(lines):
    """Find all @shared_task decorated functions with their boundaries."""
    tasks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^@shared_task', line):
            decorator_start = i

            # Scan past decorators to find def
            j = i
            while j < len(lines) and not lines[j].startswith('def '):
                j += 1
            if j >= len(lines):
                i += 1
                continue

            m = re.match(r'^def\s+(\w+)\s*\((.*)', lines[j])
            if not m:
                i = j + 1
                continue

            func_name = m.group(1)

            # Find end of function body
            k = j + 1
            while k < len(lines):
                if re.match(r'^(def |class |@\w)', lines[k]) and not lines[k].startswith('    '):
                    break
                k += 1

            # Extract decorator lines and function signature
            decorator_lines = lines[decorator_start:j]
            func_def_line = lines[j]

            # Find the full signature (may span multiple lines)
            sig_end = j
            paren_depth = func_def_line.count('(') - func_def_line.count(')')
            while paren_depth > 0 and sig_end + 1 < k:
                sig_end += 1
                paren_depth += lines[sig_end].count('(') - lines[sig_end].count(')')
            sig_lines = lines[j:sig_end + 1]

            # Body starts after signature + docstring
            body_start = sig_end + 1
            body_lines = lines[body_start:k]

            tasks.append({
                'name': func_name,
                'decorator_start': decorator_start,
                'func_start': j,
                'sig_end': sig_end,
                'body_start': body_start,
                'end': k,
                'size': sum(len(l) for l in lines[decorator_start:k]),
                'body_size': sum(len(l) for l in body_lines),
                'line_count': k - decorator_start,
                'body_line_count': len(body_lines),
                'decorator_text': ''.join(decorator_lines),
                'sig_text': ''.join(sig_lines),
                'body_text': ''.join(body_lines),
                'domain': classify_task(func_name),
            })
            i = k
        else:
            i += 1
    return tasks


def main():
    dry_run = '--dry-run' in sys.argv
    min_lines = MIN_BODY_LINES
    for i, arg in enumerate(sys.argv):
        if arg == '--min-lines' and i + 1 < len(sys.argv):
            min_lines = int(sys.argv[i + 1])

    with open(TASKS_FILE) as f:
        lines = f.readlines()

    tasks = parse_tasks(lines)
    extractable = [t for t in tasks if t['body_line_count'] >= min_lines]
    extractable.sort(key=lambda x: x['size'], reverse=True)

    # Group by domain
    domains = {}
    for t in extractable:
        d = t['domain']
        if d not in domains:
            domains[d] = []
        domains[d].append(t)

    total_savings = sum(t['body_size'] for t in extractable)
    print(f"Tasks to extract: {len(extractable)} (body >= {min_lines} lines)")
    print(f"Estimated savings: {total_savings / 1024:.0f}KB")
    print(f"Domains: {', '.join(f'{d}({len(ts)})' for d, ts in sorted(domains.items()))}")
    print()

    if dry_run:
        for d, ts in sorted(domains.items()):
            print(f"\n=== {d} ({sum(t['body_size'] for t in ts)/1024:.0f}KB) ===")
            for t in ts:
                print(f"  {t['name']:<45} {t['body_line_count']:>4} lines  {t['body_size']/1024:.1f}KB")
        return

    print("DRY RUN not specified — would extract. Use --dry-run to preview.")


if __name__ == '__main__':
    main()
