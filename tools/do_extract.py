#!/usr/bin/env python3
"""
Extract task bodies from core/tasks.py into domain-specific modules.

Each extracted task body becomes a helper function _impl_<task_name>()
in the appropriate domain module. The original @shared_task stays in
tasks.py as a thin wrapper calling the helper.

This preserves:
- All Celery task names (string names in decorators unchanged)
- All task signatures
- All task decorator options (bind, queue, etc.)
"""
import re
import sys
import os
from collections import defaultdict
from pathlib import Path

TASKS_FILE = Path('core/tasks.py')
MIN_BODY_LINES = 50

# Domain classification
DOMAIN_RULES = [
    ('codejobs', ['execute_code_job']),
    ('conversations', [
        'run_agent_conversation', 'run_multi_agent_conversation',
        'run_project_conversation', 'run_hive_mind_session',
        'trigger_spider_conversations', 'explore_dream_topic',
        'run_triggered_conversation', 'trigger_signal_driven_conversation',
        'summarize_conversation_task',
    ]),
    ('content', [
        'generate_self_blog', 'generate_content', 'track_content',
        'trigger_content', 'generate_podcast', 'run_source_pack',
        'run_autonomous_thinking', 'run_conceptforge',
        'generate_self_blog_deliberation', 'auto_generate_podcast',
        'content_autonomy', 'generate_step_content', 'score_episode',
        'run_autonomous_content', 'generate_pending_reviews',
        'generate_video_content', 'process_distribution',
        'generate_ai_series', 'run_narrative_drift',
        'update_narrative', 'generate_daily_betting_brief',
    ]),
    ('initiatives', [
        'dream', 'initiative', 'score_and_promote', 'advance_initiative',
        'execute_initiative', 'cleanup_junk', 'auto_triage',
        'auto_kickstart', 'cleanup_stale_dreams', 'surface_top',
        'process_initiative', 'process_approved',
    ]),
    ('agents', [
        'execute_agent_task', 'run_agent_learning', 'agent_daily_summary',
        'embed_agent', 'embed_daily_agent', 'generate_agent_dreams',
        'workspace_autopilot', 'universal_agent_workspace',
        'generate_human_attention', 'auto_process_extracted',
        'analyze_pa_tool', 'run_system_self_audit', 'agent_content_to',
        'agent_workspace_status', 'agent_think_and_synth',
        'agent_research_to', 'broadcast_learning', 'calculate_agent',
        'process_agent_activity', 'validate_knowledge',
        'cleanup_stale_agent', 'record_all_user_style',
    ]),
    ('financial', [
        'stock', 'blockchain', 'market_intelligence', 'prediction',
        'sport', 'odds', 'ml_scoring', 'train_ml', 'evaluate_and_complete',
        'snapshot_odds', 'collect_sports', 'collect_kalshi',
        'check_market_events', 'track_prediction', 'evaluate_ml',
        'run_earnings', 'daily_betting_digest', 'run_sec_filing',
        'aggregate_roi',
    ]),
    ('spiders', [
        'spider', 'run_spider', 'execute_single_spider', 'score_spider',
    ]),
    ('body_systems', [
        'check_skin', 'check_digestion', 'check_nervous', 'check_muscular',
        'check_brain', 'immune_scan', 'coordinate_body', 'check_mood',
        'check_level',
    ]),
    ('media', [
        'talking_video', 'ingest_video', 'transcribe_video',
        'assemble_chunked', 'generate_memory_embedding',
        'start_resolve', 'poll_resolve', 'run_thumbnail',
        'process_url_async',
    ]),
    ('ops', [
        'monitor_celery', 'ops_control', 'auto_approve',
        'process_trigger_events', 'trigger_project_research',
        'execute_pending_opportunity', 'retry_blocked',
        'isolate_documents', 'evaluate_pilots',
        'send_personalized', 'send_proactive',
        'scan_concerns', 'cleanup_boardroom', 'cleanup_halted',
        'sync_workflow', 'auto_complete_pilots',
        'dispatch_pending', 'run_skill_gap', 'run_design_trends',
        'run_single_project', 'execute_pilot', 'collect_training',
        'run_freelance', 'generate_opportunity_report',
        'monitor_running', 'aggregate_tool_call',
        'generate_weekly_opportunity', 'execute_scheduled',
        'evaluate_ml_model_performance',
    ]),
]


def classify_task(name):
    name_lower = name.lower()
    for domain, patterns in DOMAIN_RULES:
        for p in patterns:
            if p.lower() in name_lower:
                return domain
    return 'misc'


def parse_tasks(lines):
    """Find all @shared_task decorated functions."""
    tasks = []
    i = 0
    while i < len(lines):
        if not re.match(r'^@shared_task', lines[i]):
            i += 1
            continue

        decorator_start = i

        # Find def line
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

        # Find full signature (handle multi-line)
        # Strip inline comments before counting parens to avoid
        # comments like "# Session 902: Link to HiveMindSession (signal provenance)"
        # throwing off the paren depth.
        def _code_parens(line):
            """Count net parens ignoring # comments and string literals."""
            code = re.sub(r'#.*$', '', line)  # strip comment
            return code.count('(') - code.count(')')

        sig_end = j
        paren_depth = _code_parens(lines[j])
        while paren_depth > 0 and sig_end + 1 < len(lines):
            sig_end += 1
            paren_depth += _code_parens(lines[sig_end])

        # Find end of function
        k = sig_end + 1
        while k < len(lines):
            stripped = lines[k]
            if re.match(r'^(def |class |@\w|[A-Z_][A-Z_0-9]*\s*=)', stripped) and not stripped.startswith('    '):
                break
            k += 1

        # Check body size
        body_start = sig_end + 1
        body_lines = k - body_start
        body_text = ''.join(lines[body_start:k])

        if body_lines >= MIN_BODY_LINES:
            # Extract signature params
            sig_text = ''.join(lines[j:sig_end + 1])
            # Parse params: find everything between the first '(' and the last '):'
            # Use rfind to handle parens inside comments/defaults
            first_paren = sig_text.index('(')
            # Find the closing ')' that precedes ':'
            last_paren = sig_text.rfind(')')
            params_str = sig_text[first_paren + 1:last_paren].strip() if last_paren > first_paren else ''
            # Check if bound task (self parameter)
            is_bound = params_str.startswith('self')

            tasks.append({
                'name': func_name,
                'decorator_start': decorator_start,
                'func_start': j,
                'sig_end': sig_end,
                'body_start': body_start,
                'end': k,
                'body_lines': body_lines,
                'body_text': body_text,
                'decorator_text': ''.join(lines[decorator_start:j]),
                'sig_text': sig_text,
                'full_text': ''.join(lines[decorator_start:k]),
                'params_str': params_str,
                'is_bound': is_bound,
                'domain': classify_task(func_name),
            })

        i = k

    return tasks


def also_extract_private_helpers(lines):
    """Find large private helper functions (not tasks) to extract."""
    helpers = []
    # Known large helpers to extract to codejobs
    codejob_helpers = {
        '_inject_github_token', '_gather_repo_context', '_implement_with_claude',
    }
    # Known constants/frozensets
    codejob_constants = {
        '_PROTECTED_PATHS', '_BINARY_EXTENSIONS', '_MAX_FILE_SIZE',
        '_MAX_TOTAL_SIZE', '_MAX_EDIT_FILE_SIZE',
    }

    i = 0
    while i < len(lines):
        line = lines[i]
        # Match top-level private function defs
        m = re.match(r'^def (_\w+)\s*\(', line)
        if m and m.group(1) in codejob_helpers:
            func_name = m.group(1)
            k = i + 1
            while k < len(lines):
                if re.match(r'^(def |class |@\w|_\w+\s*=)', lines[k]) and not lines[k].startswith('    '):
                    break
                k += 1
            helpers.append({
                'name': func_name,
                'start': i,
                'end': k,
                'text': ''.join(lines[i:k]),
                'domain': 'codejobs',
            })
            i = k
            continue

        # Match constant assignments
        cm = re.match(r'^(_\w+)\s*=', line)
        if cm and cm.group(1) in codejob_constants:
            k = i + 1
            # Constants may span multiple lines (frozensets)
            bracket_depth = line.count('[') + line.count('(') + line.count('{')
            bracket_depth -= line.count(']') + line.count(')') + line.count('}')
            while bracket_depth > 0 and k < len(lines):
                bracket_depth += lines[k].count('[') + lines[k].count('(') + lines[k].count('{')
                bracket_depth -= lines[k].count(']') + lines[k].count(')') + lines[k].count('}')
                k += 1
            helpers.append({
                'name': cm.group(1),
                'start': i,
                'end': k,
                'text': ''.join(lines[i:k]),
                'domain': 'codejobs',
            })
            i = k
            continue

        # Skip AGENT_WORKSPACE_REGISTRY — stays in tasks.py
        # (referenced by multiple tasks; moved by task body extraction already)

        i += 1

    # Also extract CodeJob error classes
    i = 0
    while i < len(lines):
        m = re.match(r'^class (CodeJob\w*)\(', lines[i])
        if m:
            k = i + 1
            while k < len(lines):
                if re.match(r'^(def |class |@\w|#\s*──)', lines[k]) and not lines[k].startswith('    '):
                    break
                k += 1
            helpers.append({
                'name': m.group(1),
                'start': i,
                'end': k,
                'text': ''.join(lines[i:k]),
                'domain': 'codejobs',
            })
            i = k
        else:
            i += 1

    return helpers


def build_wrapper(task):
    """Build a thin wrapper for a task that calls the extracted helper."""
    domain = task['domain']
    name = task['name']
    module = 'core.codejobs.implementation' if domain == 'codejobs' else f'core.tasks_{domain}'

    params = task['params_str']
    # Build call args (strip type hints and defaults)
    call_args = []
    for p in re.split(r',(?![^()\[\]{}]*[)\]}])', params):
        p = p.strip()
        if not p or p == '/':
            continue
        # Get just the param name
        param_name = re.split(r'[\s:=]', p)[0].strip().rstrip(',')
        if param_name and param_name != '*':
            call_args.append(param_name)

    args_str = ', '.join(call_args)
    import_line = f'    from {module} import _impl_{name}'
    call_line = f'    return _impl_{name}({args_str})'

    return f'{import_line}\n{call_line}\n'


def main():
    dry_run = '--dry-run' in sys.argv

    with open(TASKS_FILE) as f:
        lines = f.readlines()
        original_content = ''.join(lines)

    tasks = parse_tasks(lines)
    helpers = also_extract_private_helpers(lines)

    print(f"Found {len(tasks)} extractable tasks, {len(helpers)} helpers")

    # Group by domain
    domain_tasks = defaultdict(list)
    for t in tasks:
        domain_tasks[t['domain']].append(t)

    domain_helpers = defaultdict(list)
    for h in helpers:
        domain_helpers[h['domain']].append(h)

    all_domains = set(list(domain_tasks.keys()) + list(domain_helpers.keys()))

    for d in sorted(all_domains):
        t_count = len(domain_tasks.get(d, []))
        h_count = len(domain_helpers.get(d, []))
        t_size = sum(len(t['body_text']) for t in domain_tasks.get(d, []))
        h_size = sum(len(h['text']) for h in domain_helpers.get(d, []))
        print(f"  {d}: {t_count} tasks ({t_size/1024:.0f}KB) + {h_count} helpers ({h_size/1024:.0f}KB)")

    if dry_run:
        print("\n--dry-run: no files modified")
        return

    # 1. Generate domain module files
    for domain in sorted(all_domains):
        if domain == 'codejobs':
            continue  # codejobs go into core/codejobs/implementation.py

        module_path = Path(f'core/tasks_{domain}.py')
        parts = [
            f'"""Extracted task implementations for {domain} domain.\n\n'
            f'Auto-generated by tools/do_extract.py — do not edit section markers.\n'
            f'Each _impl_<name> function contains the body of the corresponding\n'
            f'@shared_task in core/tasks.py.\n"""\n'
            f'from typing import Any, Dict, List, Optional, Tuple, Union  # noqa: F401\n\n'
        ]

        # Add helpers first
        for h in domain_helpers.get(domain, []):
            parts.append(f'\n{h["text"]}\n')

        # Add task implementations
        for t in domain_tasks.get(domain, []):
            # Build impl function
            params = t['params_str']
            body = t['body_text']
            # If params contain inline comments, the closing ): would be eaten.
            # Strip trailing comment from last param line.
            params = re.sub(r'#[^\n]*$', '', params).rstrip()
            if '\n' in params:
                parts.append(f'\ndef _impl_{t["name"]}(\n{params}\n):\n')
            else:
                parts.append(f'\ndef _impl_{t["name"]}({params}):\n')
            parts.append(body)
            parts.append('\n')

        content = ''.join(parts)
        module_path.write_text(content)
        print(f"  Created {module_path} ({len(content)/1024:.0f}KB)")

    # Handle codejobs domain separately → core/codejobs/implementation.py
    if 'codejobs' in all_domains:
        impl_path = Path('core/codejobs/implementation.py')
        parts = [
            '"""CodeJob implementation helpers extracted from core/tasks.py.\n\n'
            'Contains _inject_github_token, _gather_repo_context,\n'
            '_implement_with_claude and related constants.\n"""\n\n'
            'from core.codejobs.errors import (\n'
            '    CodeJobError,\n'
            '    CodeJobAnchorNotFoundError,\n'
            '    CodeJobFileTooLargeError,\n'
            ')\n\n'
        ]
        for h in domain_helpers.get('codejobs', []):
            if 'class CodeJob' in h['text']:
                continue  # Already in errors.py
            parts.append(f'{h["text"]}\n')

        for t in domain_tasks.get('codejobs', []):
            params = t['params_str']
            body = t['body_text']
            params = re.sub(r'#[^\n]*$', '', params).rstrip()
            if '\n' in params:
                parts.append(f'\ndef _impl_{t["name"]}(\n{params}\n):\n')
            else:
                parts.append(f'\ndef _impl_{t["name"]}({params}):\n')
            parts.append(body)
            parts.append('\n')

        content = ''.join(parts)
        impl_path.write_text(content)
        print(f"  Created {impl_path} ({len(content)/1024:.0f}KB)")

    # 2. Modify tasks.py — replace task bodies with wrappers
    # Build a list of replacements sorted by line number (reverse order for safe editing)
    replacements = []

    for t in tasks:
        wrapper = build_wrapper(t)
        replacements.append({
            'start': t['body_start'],
            'end': t['end'],
            'replacement': wrapper,
            'name': t['name'],
        })

    # Add helper removals (replace with import)
    for h in helpers:
        if 'class CodeJob' in h['text']:
            # Replace class defs with imports
            replacements.append({
                'start': h['start'],
                'end': h['end'],
                'replacement': '',  # Will be handled by import block
                'name': h['name'],
            })
        else:
            replacements.append({
                'start': h['start'],
                'end': h['end'],
                'replacement': '',
                'name': h['name'],
            })

    # Sort by start line ascending for forward-pass assembly
    replacements.sort(key=lambda x: x['start'])

    # Build output in a single forward pass to avoid index-shift bugs
    new_lines = []
    i = 0
    for r in replacements:
        # Copy lines before this replacement
        new_lines.extend(lines[i:r['start']])
        # Insert the replacement text
        if r['replacement']:
            new_lines.append(r['replacement'])
        i = r['end']
    # Copy remaining lines after last replacement
    new_lines.extend(lines[i:])

    # Add imports for codejobs errors at top of file (after existing imports)
    # Find the right place to insert
    import_block = (
        'from core.codejobs.errors import (\n'
        '    CodeJobError,\n'
        '    CodeJobAnchorNotFoundError,\n'
        '    CodeJobFileTooLargeError,\n'
        ')\n'
    )

    # Find a good insertion point (after the last top-level import)
    insert_at = None
    for idx, line in enumerate(new_lines):
        if line.startswith('from ') or line.startswith('import '):
            insert_at = idx + 1
        if idx > 50:
            break
    if insert_at:
        new_lines.insert(insert_at, import_block)

    # Remove the section comment for CodeJob errors if it's now empty
    new_content = ''.join(new_lines)

    # Clean up excessive blank lines (more than 2 consecutive)
    new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)

    TASKS_FILE.write_text(new_content)
    print(f"\n  Updated {TASKS_FILE}: {len(new_content)/1024:.0f}KB (was {len(original_content)/1024:.0f}KB)")
    print(f"  Savings: {(len(original_content) - len(new_content))/1024:.0f}KB")


if __name__ == '__main__':
    main()
