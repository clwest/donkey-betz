"""CodeJob implementation helpers extracted from core/tasks.py.

Contains _inject_github_token, _gather_repo_context,
_implement_with_claude and related constants.
"""

import logging

from core.codejobs.errors import (
    CodeJobError,
    CodeJobAnchorNotFoundError,
    CodeJobFileTooLargeError,
)

logger = logging.getLogger(__name__)

def _inject_github_token(repo_url: str, token: str) -> str:
    """Inject a GitHub token into a clone URL for authentication."""
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(repo_url)
    if parsed.hostname == 'github.com' and parsed.scheme == 'https':
        authed = parsed._replace(netloc=f'x-access-token:{token}' + chr(64) + parsed.hostname + (f':{parsed.port}' if parsed.port else ''))
        return urlunparse(authed)
    return repo_url


# ── Phase 5.1: Claude API code generation helpers ──────────────────────────



def _gather_repo_context(workdir, task_prompt, path_filters, log_fn):
    """Gather bounded repo context for Claude: architecture docs + file tree + relevant files.

    Budget (approx):
      - Architecture (CLAUDE.md + topic docs):  30K chars
      - Tree:     10K chars
      - Markers:   5K chars
      - Files:    80K chars
      - Total:   150K hard cap
    """
    import os
    import subprocess

    context_parts = []
    budget_used = 0
    ARCH_BUDGET = 30_000
    TREE_BUDGET = 10_000
    MARKER_BUDGET = 5_000
    FILE_BUDGET = 80_000

    # 0. Architecture context — CLAUDE.md + topic docs (highest priority)
    #    This prevents the LLM from creating duplicate models/apps that
    #    already exist in the codebase.
    arch_text = ''
    arch_files = [
        # CLAUDE.md is the single most important context file — contains
        # project structure, model locations, gotchas, and conventions
        ('CLAUDE.md', 15_000),
        # Topic docs are embedding-optimized subsystem descriptions
        ('docs/topics/agent-system.md', 3_000),
        ('docs/topics/content-pipeline.md', 3_000),
        ('docs/topics/infrastructure.md', 3_000),
        ('docs/topics/frontend.md', 3_000),
        ('docs/topics/personal-assistant.md', 3_000),
    ]
    # Session 1103c: was 'except Exception: pass' which silently
    # dropped highest-priority architecture context (CLAUDE.md +
    # topic docs) from the CodeJob implementation prompt on any
    # file read failure (path, encoding, permissions, transient FS
    # error). Downstream code generation would proceed without the
    # ground-truth context meant to prevent hallucinated imports
    # and duplicate subsystems — flying blind without knowing.
    arch_warnings = []
    for arch_file, max_chars in arch_files:
        arch_path = os.path.join(workdir, arch_file)
        if os.path.isfile(arch_path):
            try:
                with open(arch_path, 'r', errors='replace') as f:
                    content = f.read(max_chars)
                chunk = f'## {arch_file}\n```\n{content}\n```\n'
                if len(arch_text) + len(chunk) <= ARCH_BUDGET:
                    arch_text += chunk
            except Exception as e:
                arch_warnings.append(f'{arch_file}: {type(e).__name__}: {e}')
                log_fn(
                    'implement',
                    f'WARNING architecture file read failed: {arch_file} '
                    f'({type(e).__name__}: {e})',
                )
        else:
            # File doesn't exist — also worth knowing about, since
            # missing CLAUDE.md or topic docs degrades context quality
            arch_warnings.append(f'{arch_file}: missing from workdir')
    if arch_warnings:
        log_fn(
            'implement',
            f'Architecture context degraded: {len(arch_warnings)} '
            f'files unavailable: {arch_warnings[:5]}',
        )
    if arch_text:
        context_parts.append('# ARCHITECTURE CONTEXT (read this first)\n' + arch_text)
        budget_used += len(context_parts[-1])
        log_fn('implement', f'Architecture context: {len(arch_text)} chars from CLAUDE.md + topic docs')

    # 1. File tree (exclude heavy dirs)
    exclude_dirs = [
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        '.tox', '.mypy_cache', '.pytest_cache', 'dist', 'build',
        '.next', 'coverage', '.eggs', 'migrations',
    ]
    prune_args = ' '.join(f'-name "{d}" -prune -o' for d in exclude_dirs)
    tree_result = subprocess.run(
        f'find . {prune_args} -type f -print | sort | head -500',
        shell=True, cwd=workdir, capture_output=True, text=True, timeout=15,
    )
    file_tree = tree_result.stdout.strip()[:TREE_BUDGET]
    context_parts.append(f'## File Tree\n```\n{file_tree}\n```\n')
    budget_used += len(context_parts[-1])

    # 2. Project marker files (README, pyproject.toml, etc.)
    #    Note: CLAUDE.md already read above — skip it here
    marker_text = ''
    for marker in ['pyproject.toml', 'setup.py', 'package.json',
                    'Cargo.toml', 'go.mod', 'requirements.txt']:
        marker_path = os.path.join(workdir, marker)
        if os.path.isfile(marker_path):
            try:
                with open(marker_path, 'r', errors='replace') as f:
                    content = f.read(3000)  # first 3KB
                chunk = f'## {marker}\n```\n{content}\n```\n'
                if len(marker_text) + len(chunk) <= MARKER_BUDGET:
                    marker_text += chunk
            except Exception:
                pass
    if marker_text:
        context_parts.append(marker_text)
        budget_used += len(marker_text)

    # 3. Extract explicit file paths mentioned in the task prompt
    #    (e.g. "frontend/src/components/layout/Layout.tsx")
    import re as _path_re
    explicit_paths = set()
    # Match file paths like foo/bar/baz.ext
    for match in _path_re.finditer(r'(?:^|\s)((?:[\w.-]+/)+[\w.-]+\.(?:tsx?|jsx?|py|rs|go|css|json|md))', task_prompt):
        explicit_paths.add(match.group(1))
    if explicit_paths:
        log_fn('implement', f'Explicit file paths in task: {sorted(explicit_paths)}')

    # 4. Find relevant files via grep on task keywords
    keywords = [w for w in task_prompt.split() if len(w) > 4 and w.isalpha()][:5]
    relevant_files = set()
    for kw in keywords:
        try:
            grep_result = subprocess.run(
                f'grep -rl --include="*.py" --include="*.ts" --include="*.js" '
                f'--include="*.tsx" --include="*.jsx" --include="*.rs" --include="*.go" '
                f'-m 1 "{kw}" . 2>/dev/null | head -5',
                shell=True, cwd=workdir, capture_output=True, text=True, timeout=10,
            )
            for f in grep_result.stdout.strip().splitlines():
                if f.strip():
                    relevant_files.add(f.strip())
        except Exception:
            pass

    # Apply path_filters if set
    if path_filters:
        # Also find ALL files under the filtered paths (not just grep matches)
        for pf in path_filters:
            try:
                find_result = subprocess.run(
                    f'find ./{pf} -type f \\( -name "*.py" -o -name "*.ts" -o -name "*.tsx" '
                    f'-o -name "*.js" -o -name "*.jsx" \\) 2>/dev/null | head -20',
                    shell=True, cwd=workdir, capture_output=True, text=True, timeout=10,
                )
                for f in find_result.stdout.strip().splitlines():
                    if f.strip():
                        relevant_files.add(f.strip())
            except Exception:
                pass
        relevant_files = {
            f for f in relevant_files
            if any(f.startswith(f'./{pf}') or f.startswith(pf) for pf in path_filters)
        }

    # Add explicit paths from the task prompt (highest priority)
    for ep in explicit_paths:
        rel = f'./{ep}'
        abs_p = os.path.join(workdir, ep)
        if os.path.isfile(abs_p):
            relevant_files.add(rel)

    # 5. Read files, prioritizing explicit paths + smaller files
    #    Read FULL content for files under 500 lines (likely patch targets).
    #    These are the files Claude will actually need to generate correct anchors.
    files_budget_used = 0
    files_read = 0

    # Sort: explicit paths first, then by size (smaller first)
    def _file_sort_key(f):
        is_explicit = any(f.endswith(ep) or ep in f for ep in explicit_paths)
        try:
            size = os.path.getsize(os.path.join(workdir, f.lstrip('./')))
        except Exception:
            size = 999999
        return (0 if is_explicit else 1, size)

    for rel_path in sorted(relevant_files, key=_file_sort_key)[:15]:
        abs_path = os.path.join(workdir, rel_path.lstrip('./'))
        if not os.path.isfile(abs_path):
            continue
        try:
            with open(abs_path, 'r', errors='replace') as f:
                content = f.read()
            line_count = content.count('\n') + 1

            # For small files (<500 lines), include FULL content so Claude
            # can generate exact patch anchors. This is the key fix for
            # CODEJOB_ANCHOR_NOT_FOUND failures.
            if line_count <= 500:
                chunk = f'## {rel_path} (FULL — {line_count} lines)\n```\n{content}\n```\n'
            else:
                # For large files, include first 300 lines
                lines = content.split('\n')[:300]
                chunk = f'## {rel_path} (first 300 of {line_count} lines)\n```\n{chr(10).join(lines)}\n```\n'

            if files_budget_used + len(chunk) > FILE_BUDGET:
                # If we're over budget, try truncating this file
                if files_budget_used < FILE_BUDGET * 0.8:
                    remaining = FILE_BUDGET - files_budget_used - 200
                    chunk = f'## {rel_path} (truncated, {line_count} lines total)\n```\n{content[:remaining]}\n... [truncated]\n```\n'
                else:
                    break
            context_parts.append(chunk)
            files_budget_used += len(chunk)
            files_read += 1
        except Exception:
            pass

    log_fn('implement', f'Context: {len(file_tree.splitlines())} files in tree, {files_read} files read ({len(explicit_paths)} explicit), {budget_used + files_budget_used} chars')

    return '\n'.join(context_parts)


# ── CodeJob typed exceptions ────────────────────────────────────────────────



_PROTECTED_PATHS = frozenset([
    '.env', '.env.local', '.env.production', '.env.staging',
    'secrets.yaml', 'secrets.yml', 'secrets.json',
    '.github/workflows', 'Procfile', 'Dockerfile',
    'docker-compose.yml', 'docker-compose.yaml',
])

_BINARY_EXTENSIONS = frozenset([
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.svg',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.zip', '.tar', '.gz', '.pdf', '.pyc', '.pyo',
    '.so', '.dylib', '.dll', '.exe',
])

_MAX_FILE_SIZE = 200_000       # 200KB per file (output)

_MAX_TOTAL_SIZE = 2_000_000    # 2MB total (output)

_MAX_EDIT_FILE_SIZE = 500_000  # 500KB — files larger than this are too big for safe patch editing

def _preflight_validate(workdir, files_changed, log_fn):
    """Pre-flight validation: catch hallucinated imports and broken migrations.

    Returns a list of error strings. Empty list = all clear.
    """
    import ast
    import os
    import subprocess

    errors = []

    # 1. Check Python imports against the actual codebase
    py_files = [f for f in files_changed if f.endswith('.py')]
    for rel_path in py_files:
        abs_path = os.path.join(workdir, rel_path)
        if not os.path.isfile(abs_path):
            continue

        try:
            with open(abs_path, 'r') as fh:
                source = fh.read()
            tree = ast.parse(source, filename=rel_path)
        except SyntaxError:
            continue  # Already caught by py_compile check

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                # Only check internal imports (core.*, ai_core.*, etc.)
                if not module.startswith(('core.', 'ai_core.', 'content.', 'resolve_node.')):
                    continue

                # Convert module path to file path(s) and check if they exist
                module_path = module.replace('.', '/')
                possible_paths = [
                    os.path.join(workdir, module_path + '.py'),
                    os.path.join(workdir, module_path, '__init__.py'),
                ]
                if not any(os.path.isfile(p) for p in possible_paths):
                    errors.append(
                        f'IMPORT_NOT_FOUND: {rel_path} imports from "{module}" '
                        f'but neither {module_path}.py nor {module_path}/__init__.py exists'
                    )
                    continue

                # Check if specific names exist in the module
                for alias in (node.names or []):
                    name = alias.name
                    if name == '*':
                        continue
                    # Check if the name is defined in the module file
                    module_file = None
                    for p in possible_paths:
                        if os.path.isfile(p):
                            module_file = p
                            break
                    if module_file:
                        try:
                            with open(module_file, 'r') as mf:
                                module_source = mf.read()
                            # Quick check: is the name defined in the module?
                            # Look for class/def/variable definitions
                            if (f'class {name}' not in module_source
                                    and f'def {name}' not in module_source
                                    and f'{name} =' not in module_source
                                    and f'from ' not in module_source  # re-exports
                                    ):
                                # Could be a re-export via __init__.py — check imports
                                if f'import {name}' not in module_source and f'{name}' not in module_source:
                                    errors.append(
                                        f'SYMBOL_NOT_FOUND: {rel_path} imports "{name}" from "{module}" '
                                        f'but "{name}" is not defined in {module_file}'
                                    )
                        except Exception:
                            pass  # Can't read module file — skip this check

    # 2. Check migration dependencies
    migration_files = [f for f in files_changed if '/migrations/' in f and f.endswith('.py')]
    for mig_path in migration_files:
        abs_mig = os.path.join(workdir, mig_path)
        if not os.path.isfile(abs_mig):
            continue
        try:
            with open(abs_mig, 'r') as mf:
                mig_source = mf.read()
            mig_tree = ast.parse(mig_source)

            # Find the dependencies list
            for node in ast.walk(mig_tree):
                if (isinstance(node, ast.Assign)
                        and any(isinstance(t, ast.Attribute) and t.attr == 'dependencies'
                                for t in (node.targets if hasattr(node, 'targets') else []))):
                    # This is a simple heuristic — look for tuples in the value
                    pass  # Complex AST parsing; use simpler approach below

            # Simpler: regex for dependency tuples like ('core', '0229_xxx')
            import re as _mig_re
            deps = _mig_re.findall(r"\('(\w+)',\s*'(\d{4}_\w+)'\)", mig_source)
            for app_label, dep_name in deps:
                # Check if the dependency migration exists
                dep_path = os.path.join(workdir, app_label, 'migrations', dep_name + '.py')
                if not os.path.isfile(dep_path):
                    # Also check core/migrations/ for the core app
                    alt_path = os.path.join(workdir, 'core', 'migrations', dep_name + '.py')
                    if not os.path.isfile(alt_path):
                        errors.append(
                            f'MIGRATION_DEP_MISSING: {mig_path} depends on '
                            f'({app_label}, {dep_name}) but that migration does not exist'
                        )
        except Exception as e:
            log_fn('implement', f'  Migration validation error for {mig_path}: {e}', level='warning')

    # 3. Check for new top-level app directories (already blocked by validation
    #    gate, but double-check here for defense in depth)
    for f in files_changed:
        parts = f.split('/')
        if len(parts) >= 2:
            top_dir = parts[0]
            basename = os.path.basename(f)
            if basename in ('apps.py', 'models.py') and top_dir not in (
                'core', 'ai_core', 'content', 'resolve_node', 'frontend', 'mobile', 'tools'
            ):
                errors.append(
                    f'NEW_DJANGO_APP: {f} creates a new Django app directory "{top_dir}/". '
                    f'This codebase uses a monolithic core app.'
                )

    if errors:
        log_fn('implement', f'PREFLIGHT: {len(errors)} validation error(s) found', level='warning')
        for e in errors[:5]:
            log_fn('implement', f'  PREFLIGHT: {e}', level='warning')
    else:
        log_fn('implement', 'PREFLIGHT: all validation checks passed')

    return errors


def _implement_with_claude(workdir, run, plan, log_fn, shell):
    """Use Claude API to generate code changes and apply them to workdir."""
    import os
    import json as json_mod

    task_prompt = plan.get('task_prompt', '') or run.plan_summary
    acceptance_criteria = plan.get('acceptance_criteria', [])
    max_patch_files = plan.get('max_patch_files', 50)
    path_filters = plan.get('path_filters', [])

    # 1. Gather context
    log_fn('implement', 'Gathering repo context...')
    repo_context = _gather_repo_context(workdir, task_prompt, path_filters, log_fn)

    # 2. Build prompt
    criteria_text = ''
    if acceptance_criteria:
        criteria_text = '\n\nAcceptance Criteria:\n' + '\n'.join(
            f'- {c}' for c in acceptance_criteria
        )

    system_prompt = (
        'You are a senior software engineer implementing code changes in a repository. '
        'You MUST respond with exactly one tool call to `apply_file_changes` and no other text. '
        'Be precise, minimal, and production-ready. Do not add unnecessary comments or TODOs. '
        f'You may modify at most {max_patch_files} files. '
        'Keep commit messages under 72 characters.\n\n'
        'CRITICAL architecture rules:\n'
        '- READ the CLAUDE.md / architecture context FIRST — it describes where models, '
        'services, and views live. Follow existing patterns.\n'
        '- NEVER create new Django apps (new top-level directories with models.py/apps.py) '
        'unless the task explicitly asks for one. This codebase uses a monolithic "core" app '
        'with split model files (core/models_*.py). New models go in existing files.\n'
        '- NEVER create models that duplicate existing ones. Check the architecture context '
        'for existing model locations before creating anything.\n'
        '- NEVER delete or gut large existing files (>100 lines removed). If you need to '
        'restructure, use patches to modify specific sections.\n'
        '- Prefer patching existing code over rewriting. The codebase is large (200K+ lines) '
        'and existing code is battle-tested.\n\n'
        'CRITICAL rules for file changes:\n'
        '- Use "create" ONLY for brand new files. Provide complete file content.\n'
        '- Use "patch" for modifying EXISTING files. Provide a JSON array of search-replace edits '
        'in the "content" field. Each edit is an object with "search" (exact existing text to find) '
        'and "replace" (text to replace it with). Include enough context lines in "search" to be unique. '
        'Example content: [{"search": "def old_func():\\n    return 1", "replace": "def old_func():\\n    return 2"}]\n'
        'IMPORTANT: Files marked "(FULL)" in the Repository Context below show their COMPLETE '
        'current content. Copy search strings EXACTLY from that content — do not guess or '
        'paraphrase. Even small differences in whitespace or quotes will cause the patch to fail.\n'
        'This is MANDATORY for existing files — NEVER use "create" on files already in the repo, '
        'as that replaces the ENTIRE file, destroying existing code.\n'
        '- Use "delete" to remove files.\n'
        '- Minimize changes. Only modify what is strictly necessary for the task.'
    )
    if path_filters:
        system_prompt += f'\n\nScope: Only modify files under these paths: {path_filters}'

    user_message = (
        f'## Task\n{task_prompt}\n'
        f'{criteria_text}\n\n'
        f'## Repository Context\n{repo_context}'
    )

    # 3. Define tool
    file_changes_tool = {
        'name': 'apply_file_changes',
        'description': 'Apply file changes to implement the task.',
        'input_schema': {
            'type': 'object',
            'required': ['changes', 'commit_message'],
            'properties': {
                'changes': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['path', 'action'],
                        'properties': {
                            'path': {
                                'type': 'string',
                                'description': 'File path relative to repo root (e.g. src/utils.py)',
                            },
                            'action': {
                                'type': 'string',
                                'enum': ['create', 'patch', 'delete'],
                                'description': 'create=new file (full content), patch=edit existing file (search-replace edits), delete=remove file',
                            },
                            'content': {
                                'type': 'string',
                                'description': 'For create: complete file content. For patch: JSON array of search-replace edits, e.g. [{"search": "old text", "replace": "new text"}]. Each "search" must be an exact substring of the existing file, unique enough to match only once.',
                            },
                        },
                    },
                },
                'commit_message': {
                    'type': 'string',
                    'description': 'Concise git commit message (max 72 chars)',
                },
            },
        },
    }

    # 4. Call Claude (with one retry on schema validation failure)
    # Session 1077: Added timeout + heartbeat to prevent indefinite hangs
    log_fn('implement', 'Calling Claude (claude-sonnet-4-6) for code generation...')
    from anthropic import Anthropic
    import concurrent.futures
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env

    _CODEGEN_TIMEOUT = 120  # seconds — hard cap on LLM call

    def _call_claude(model_name, msgs, sys_prompt, tools_list, tool_ch):
        """Blocking LLM call — run in thread with timeout."""
        return client.messages.create(
            model=model_name,
            max_tokens=16384,
            system=sys_prompt,
            messages=msgs,  # type: ignore[arg-type]
            tools=tools_list,  # type: ignore[arg-type]
            tool_choice=tool_ch,
        )

    messages: list = [{'role': 'user', 'content': user_message}]
    tool_input: dict | None = None
    attempts = 0
    max_attempts = 2

    while attempts < max_attempts:
        attempts += 1
        # Run LLM call in thread with timeout + heartbeat
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                _call_claude, 'claude-sonnet-4-6', messages, system_prompt,
                [file_changes_tool], {'type': 'tool', 'name': 'apply_file_changes'},
            )
            # Heartbeat while waiting
            start_wait = __import__('time').time()
            while True:
                try:
                    response = future.result(timeout=10)
                    break  # Got response
                except concurrent.futures.TimeoutError:
                    elapsed = int(__import__('time').time() - start_wait)
                    if elapsed >= _CODEGEN_TIMEOUT:
                        future.cancel()
                        raise TimeoutError(
                            f"Code generation timed out after {elapsed}s"
                        )
                    log_fn('implement', f'Waiting on Claude... ({elapsed}s elapsed)')

        tool_use_id = None
        for block in response.content:
            if block.type == 'tool_use' and block.name == 'apply_file_changes':
                tool_use_id = block.id
                raw = block.input
                # SDK may return a dict, a JSON string, or a Pydantic-like object
                if isinstance(raw, str):
                    tool_input = json_mod.loads(raw)
                elif isinstance(raw, dict):
                    tool_input = raw
                else:
                    tool_input = dict(raw)  # type: ignore[arg-type]
                break

        log_fn('implement', f'Tool response type: {type(tool_input).__name__}, keys: {list(tool_input.keys()) if isinstance(tool_input, dict) else "N/A"}')

        def _append_retry(error_text: str) -> None:
            """Append assistant + tool_result retry messages for Anthropic tool_use protocol."""
            messages.append({'role': 'assistant', 'content': response.content})  # type: ignore[dict-item]
            # Anthropic requires a tool_result block after every tool_use
            user_content: list = []
            if tool_use_id:
                user_content.append({
                    'type': 'tool_result',
                    'tool_use_id': tool_use_id,
                    'is_error': True,
                    'content': error_text[:500],
                })
            user_content.append({'type': 'text', 'text': error_text})
            messages.append({'role': 'user', 'content': user_content})

        if not tool_input or not tool_input.get('changes'):
            if attempts < max_attempts:
                log_fn('implement', 'No file changes returned, retrying...', level='warning')
                _append_retry(
                    'You returned no file changes. Please call apply_file_changes with the changes needed to implement the task.'
                )
                tool_input = None
                continue
            raise RuntimeError('Claude returned no file changes (LLM_NO_OUTPUT)')

        # Validate changes schema
        validation_errors = []
        changes = tool_input['changes']

        # Guard: changes must be a list of dicts
        if isinstance(changes, str):
            log_fn('implement', f'INVALID_CHANGES_SCHEMA: "changes" is a string ({len(changes)} chars), expected list[dict]. Preview: {changes[:200]}', level='warning')
            if attempts < max_attempts:
                _append_retry(
                    '"changes" must be a JSON array of objects, not a string. '
                    'Each object needs: {"path": "...", "action": "create|patch|delete", "content": "..."}. '
                    'Please call apply_file_changes again with the correct schema.'
                )
                tool_input = None
                continue
            raise RuntimeError(
                f'INVALID_CHANGES_SCHEMA: "changes" is a string after {attempts} attempts. '
                f'Preview: {changes[:200]}'
            )

        if not isinstance(changes, list):
            raise RuntimeError(
                f'INVALID_CHANGES_SCHEMA: "changes" is {type(changes).__name__}, expected list. '
                f'Value: {str(changes)[:200]}'
            )

        # Validate every element is a dict
        bad_items = [
            (i, type(c).__name__, str(c)[:80])
            for i, c in enumerate(changes)
            if not isinstance(c, dict)
        ]
        if bad_items:
            detail = '; '.join(f'[{i}] type={t} val={v}' for i, t, v in bad_items[:5])
            log_fn('implement', f'INVALID_CHANGE_ITEM: {len(bad_items)} non-dict item(s) in changes: {detail}', level='warning')
            if attempts < max_attempts:
                _append_retry(
                    f'Each element in "changes" must be an object with path/action/content keys. '
                    f'Found {len(bad_items)} invalid item(s): {detail}. '
                    f'Please call apply_file_changes again with the correct schema.'
                )
                tool_input = None
                continue
            raise RuntimeError(
                f'INVALID_CHANGE_ITEM: {len(bad_items)} non-dict item(s) after {attempts} attempts: {detail}'
            )

        if len(changes) > max_patch_files:
            validation_errors.append(f'Too many files: {len(changes)} > {max_patch_files}')

        # Detect new Django app creation — a common LLM mistake in monolithic codebases
        _new_app_signals = set()
        for change in changes:
            path = change.get('path', '')
            action = change.get('action', '')
            if action == 'create' and path.count('/') >= 1:
                top_dir = path.split('/')[0]
                basename = os.path.basename(path)
                if basename in ('apps.py', 'models.py', 'admin.py', 'urls.py', 'views.py'):
                    # Check if this is a new top-level directory (not core/ or existing apps)
                    if top_dir not in ('core', 'ai_core', 'content', 'resolve_node', 'frontend'):
                        _new_app_signals.add(top_dir)
        if _new_app_signals:
            validation_errors.append(
                f'BLOCKED: Creating new Django app(s): {_new_app_signals}. '
                f'This codebase uses a monolithic "core" app. '
                f'Add new models to core/models_*.py, views to core/views_*.py, '
                f'and management commands to core/management/commands/.'
            )

        for change in changes:
            path = change.get('path', '')
            action = change.get('action', '')
            if '..' in path or path.startswith('/'):
                validation_errors.append(f'Invalid path (traversal): {path}')
            if action in ('create', 'overwrite') and not change.get('content'):
                validation_errors.append(f'Missing content for {action} on {path}')
            ext = os.path.splitext(path)[1].lower()
            if ext in _BINARY_EXTENSIONS:
                validation_errors.append(f'Binary file not allowed: {path}')

        if validation_errors and attempts < max_attempts:
            log_fn('implement', f'Validation errors: {validation_errors}, retrying...', level='warning')
            _append_retry(
                'Validation errors:\n' + '\n'.join(f'- {e}' for e in validation_errors)
                + '\n\nPlease fix these issues and call apply_file_changes again.'
            )
            tool_input = None
            continue
        elif validation_errors:
            raise RuntimeError(f'Invalid changes after {attempts} attempts: {validation_errors}')

        break  # valid tool_input

    changes = tool_input['changes']
    commit_message = (tool_input.get('commit_message') or 'feat: implement code changes')[:72]

    log_fn('implement', f'Claude proposed {len(changes)} file change(s)')

    # 5. Apply changes with security checks
    workdir_real = os.path.realpath(workdir)
    files_changed = []
    total_written = 0

    for change in changes:
        path = change['path']
        action = change['action']
        abs_path = os.path.realpath(os.path.join(workdir, path))

        # Symlink escape check: resolved path must stay inside workdir
        if not abs_path.startswith(workdir_real + os.sep) and abs_path != workdir_real:
            log_fn('implement', f'  BLOCKED (path escape): {path}', level='warning')
            continue

        # Protected path check
        if any(path == p or path.startswith(p + '/') for p in _PROTECTED_PATHS):
            log_fn('implement', f'  BLOCKED (protected path): {path}', level='warning')
            continue

        if action == 'delete':
            if os.path.exists(abs_path):
                os.remove(abs_path)
                log_fn('implement', f'  Deleted: {path}')
                files_changed.append(path)
        elif action == 'patch':
            # Apply search-replace edits to an existing file
            raw_content = change.get('content', '')

            # Claude may return content as a list (parsed JSON) or a string
            if isinstance(raw_content, list):
                edits = raw_content
            elif isinstance(raw_content, dict):
                edits = [raw_content]
            elif isinstance(raw_content, str):
                if not raw_content.strip():
                    log_fn('implement', f'  SKIPPED (empty patch): {path}', level='warning')
                    continue
                try:
                    edits = json_mod.loads(raw_content)
                    if not isinstance(edits, list):
                        edits = [edits]
                except (json_mod.JSONDecodeError, TypeError):
                    log_fn('implement', f'  FAILED (content is not valid JSON): {path}', level='warning')
                    log_fn('implement', f'  Raw content preview: {raw_content[:200]}', level='warning')
                    continue
            else:
                log_fn('implement', f'  FAILED (unexpected content type {type(raw_content).__name__}): {path}', level='warning')
                continue

            if not edits:
                log_fn('implement', f'  SKIPPED (no edits): {path}', level='warning')
                continue
            if not os.path.exists(abs_path):
                log_fn('implement', f'  SKIPPED (patch target does not exist): {path}', level='warning')
                continue

            # Pre-read size check: fail fast for oversized files
            file_size = os.path.getsize(abs_path)
            if file_size > _MAX_EDIT_FILE_SIZE:
                raise CodeJobFileTooLargeError(
                    f'{path} is {file_size:,} bytes (limit: {_MAX_EDIT_FILE_SIZE:,}). '
                    f'Split the file or target a smaller module.',
                    path=path, size=file_size, limit=_MAX_EDIT_FILE_SIZE,
                )

            with open(abs_path, 'r') as f:
                file_text = f.read()

            original_text = file_text
            edit_count = 0
            anchor_failures = []
            for edit_idx, edit in enumerate(edits):
                search = edit.get('search', '')
                replace = edit.get('replace', '')
                if not search and replace:
                    # Session 1077: Empty search = prepend to file (Claude's way
                    # of saying "insert at the top")
                    file_text = replace + '\n' + file_text
                    edit_count += 1
                    log_fn('implement', f'  Prepended content to {path}')
                    continue
                if not search:
                    log_fn('implement', f'  SKIPPED empty search+replace in edit for {path}', level='warning')
                    continue
                if search not in file_text:
                    # Try with normalized whitespace (strip trailing spaces per line)
                    search_normalized = '\n'.join(l.rstrip() for l in search.split('\n'))
                    file_text_normalized = '\n'.join(l.rstrip() for l in file_text.split('\n'))
                    if search_normalized in file_text_normalized:
                        # Find position in normalized text and replace in original
                        idx = file_text_normalized.index(search_normalized)
                        # Map back: count newlines to find the matching original section
                        lines_before = file_text_normalized[:idx].count('\n')
                        search_line_count = search_normalized.count('\n') + 1
                        orig_lines = file_text.split('\n')
                        orig_section = '\n'.join(orig_lines[lines_before:lines_before + search_line_count])
                        file_text = file_text.replace(orig_section, replace, 1)
                        edit_count += 1
                    else:
                        # Session 1077: Try collapsing all whitespace for fuzzy match
                        import re as _ws_re
                        search_collapsed = _ws_re.sub(r'\s+', ' ', search.strip())
                        file_collapsed = _ws_re.sub(r'\s+', ' ', file_text.strip())
                        if search_collapsed and search_collapsed in file_collapsed:
                            # Find the matching region by line-by-line scanning
                            search_lines = [l.strip() for l in search.strip().split('\n') if l.strip()]
                            file_lines = file_text.split('\n')
                            for start_idx in range(len(file_lines)):
                                match_count = 0
                                for j, sl in enumerate(search_lines):
                                    if start_idx + j < len(file_lines) and sl in file_lines[start_idx + j]:
                                        match_count += 1
                                if match_count == len(search_lines):
                                    # Found fuzzy match — replace those lines
                                    end_idx = start_idx + len(search_lines)
                                    replace_lines = replace.split('\n')
                                    file_lines[start_idx:end_idx] = replace_lines
                                    file_text = '\n'.join(file_lines)
                                    edit_count += 1
                                    log_fn('implement', f'  Fuzzy-matched and patched {path} (edit #{edit_idx + 1})')
                                    break
                            else:
                                anchor_failures.append({
                                    'edit_index': edit_idx,
                                    'search_preview': search[:120],
                                    'path': path,
                                    'file_size': file_size,
                                })
                                log_fn('implement', f'  ANCHOR NOT FOUND in {path} (edit #{edit_idx + 1}): {search[:100]}', level='warning')
                        else:
                            anchor_failures.append({
                                'edit_index': edit_idx,
                                'search_preview': search[:120],
                                'path': path,
                                'file_size': file_size,
                            })
                            log_fn('implement', f'  ANCHOR NOT FOUND in {path} (edit #{edit_idx + 1}): {search[:100]}', level='warning')
                else:
                    occurrences = file_text.count(search)
                    if occurrences > 1:
                        log_fn('implement', f'  WARN: search text matches {occurrences}x in {path}, replacing first', level='warning')
                    file_text = file_text.replace(search, replace, 1)
                    edit_count += 1

            if anchor_failures:
                detail = '; '.join(
                    f'edit #{f["edit_index"]+1}: "{f["search_preview"]}"'
                    for f in anchor_failures[:3]
                )
                raise CodeJobAnchorNotFoundError(
                    f'{len(anchor_failures)}/{len(edits)} edit(s) failed for {path} ({file_size:,} bytes). '
                    f'Search text not found: {detail}',
                    path=path, file_size=file_size,
                    failed_edits=anchor_failures,
                    edits_succeeded=edit_count,
                )

            if file_text != original_text and edit_count > 0:
                size_delta = len(file_text) - len(original_text)
                if size_delta > _MAX_FILE_SIZE:
                    log_fn('implement', f'  BLOCKED (patch adds too much: +{size_delta} bytes): {path}', level='warning')
                    continue
                with open(abs_path, 'w') as f:
                    f.write(file_text)
                total_written += len(file_text)
                log_fn('implement', f'  Patched: {path} ({edit_count} edit(s))')
                files_changed.append(path)
            else:
                log_fn('implement', f'  FAILED: no edits applied to {path}', level='warning')

        elif action in ('create', 'overwrite'):
            content = change.get('content', '')
            if len(content) > _MAX_FILE_SIZE:
                raise CodeJobFileTooLargeError(
                    f'Content for {path} is {len(content):,} bytes (limit: {_MAX_FILE_SIZE:,}). '
                    f'Split into smaller files.',
                    path=path, size=len(content), limit=_MAX_FILE_SIZE,
                )
            if total_written + len(content) > _MAX_TOTAL_SIZE:
                log_fn('implement', f'  BLOCKED (total write budget exceeded): {path}', level='warning')
                continue

            os.makedirs(os.path.dirname(abs_path) or workdir, exist_ok=True)
            with open(abs_path, 'w') as f:
                f.write(content)
            total_written += len(content)
            verb = 'Created' if action == 'create' else 'Modified'
            log_fn('implement', f'  {verb}: {path}')
            files_changed.append(path)

    if not files_changed:
        raise RuntimeError('No files were actually changed after applying Claude output')

    log_fn('implement', f'{len(files_changed)} file(s) changed, {total_written} bytes written')

    # 6. Quick sanity check: verify no syntax errors in .py files
    py_changed = [f for f in files_changed if f.endswith('.py')]
    if py_changed:
        check_result = shell(
            'python -m py_compile ' + ' '.join(
                os.path.join('.', f) for f in py_changed[:20]
            ),
            cwd=workdir,
        )
        if check_result.returncode != 0:
            log_fn('implement', 'Python syntax check FAILED — changes may have errors', level='warning')

    # 6b. Pre-flight validation: catch hallucinated imports/models/migrations
    #     before they get committed and break Railway deploys.
    preflight_errors = _preflight_validate(workdir, files_changed, log_fn)
    if preflight_errors:
        error_summary = '\n'.join(f'  - {e}' for e in preflight_errors[:10])
        raise RuntimeError(
            f'PREFLIGHT_VALIDATION_FAILED: {len(preflight_errors)} issue(s) found in proposed changes. '
            f'These changes would break the deploy:\n{error_summary}'
        )

    # 7. Git add + commit
    shell('git add -A', cwd=workdir)

    # Log what git sees
    shell('git status --porcelain', cwd=workdir)

    commit_result = shell(
        f'git commit -m "{commit_message}"'
        ' --author="Code Worker <codeworker@donkeybetz.com>"',
        cwd=workdir,
    )
    if commit_result.returncode != 0:
        raise RuntimeError(f'Git commit failed: {commit_result.stderr[:300]}')

    log_fn('implement', f'Committed: {commit_message}')
    return files_changed




def _impl_execute_code_job(self, run_id: str):
    """Execute a code job: clone repo, implement changes, test, push, open PR.

    This is the main Celery task for the Remote Code Worker pipeline.
    Runs on the dedicated 'code_jobs' queue with concurrency=1.

    See: docs/designs/remote-code-worker-contract.md
    """
    from core.models import ExecutionRun, CodeJobLog

    try:
        run = ExecutionRun.objects.select_related('repo').get(id=run_id)
    except ExecutionRun.DoesNotExist:
        logger.error('[CodeWorker] Run %s not found', run_id)
        return {'error': 'Run not found'}

    if run.is_terminal:
        logger.info('[CodeWorker] Run %s already terminal: %s', run_id, run.status)
        return {'status': run.status}

    def log(step, message, level='info'):
        seq = CodeJobLog.objects.filter(run=run).count()
        CodeJobLog.objects.create(
            run=run, sequence=seq, step=step,
            level=level, message=message,
        )
        getattr(logger, level, logger.info)(
            '[CodeWorker:%s] [%s] %s', str(run.id)[:8], step, message
        )

    plan = run.plan_json or {}
    mode = plan.get('mode', 'dry_run')
    is_dry_run = (mode == 'dry_run')

    import os
    import shutil
    import subprocess
    import tempfile
    import urllib.request
    import urllib.error
    import json as json_mod

    github_token = os.environ.get('GITHUB_TOKEN', '')

    def shell(cmd, cwd=None, timeout=300):
        """Run a shell command, log output, return CompletedProcess."""
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'},
        )
        for line in (result.stdout or '').strip().splitlines()[:30]:
            log(run.current_step or 'shell', f'  {line}')
        for line in (result.stderr or '').strip().splitlines()[:15]:
            log(run.current_step or 'shell', f'  [stderr] {line}')
        return result

    workdir = None

    # Ensure base_branch is never empty
    if not run.base_branch:
        run.base_branch = (run.repo.default_base_branch if run.repo else '') or 'main'
        run.save(update_fields=['base_branch'])

    try:
        run.start()
        log('start', f'Starting code job for {run.repo_url} @ {run.base_branch} (mode={mode})')

        # ── Step 1: Clone ────────────────────────────────────────────────
        run.set_step('cloning', 0.1)

        if is_dry_run:
            log('clone', f'[DRY RUN] Would clone {run.repo_url} — skipping')
        else:
            if not github_token:
                raise RuntimeError('GITHUB_TOKEN not configured — cannot clone')

            # Preflight: check token has write access
            repo_slug = run.repo.get_repo_slug() if run.repo else ''
            if not repo_slug and run.repo_url:
                repo_slug = run.repo_url.rstrip('/').split('github.com/')[-1].replace('.git', '')
            if repo_slug:
                try:
                    req = urllib.request.Request(
                        f'https://api.github.com/repos/{repo_slug}',
                        headers={
                            'Authorization': f'token {github_token}',
                            'Accept': 'application/vnd.github+json',
                        },
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        repo_info = json_mod.loads(resp.read())
                        perms = repo_info.get('permissions', {})

                        # Check token scopes from response header
                        scopes_header = resp.getheader('X-OAuth-Scopes', '')
                        scopes = [s.strip() for s in scopes_header.split(',') if s.strip()]
                        log('clone', f'Token scopes: {scopes or "(fine-grained PAT — no X-OAuth-Scopes)"}')

                        if not perms.get('push'):
                            raise RuntimeError(
                                f'GITHUB_TOKEN lacks write access to {repo_slug}. '
                                f'Permissions: {perms}. Update the PAT to include repo scope.'
                            )

                        # Classic PATs: verify 'repo' scope is present
                        if scopes and 'repo' not in scopes:
                            log('clone', f'WARNING: Token missing "repo" scope (has: {scopes}). Push may fail.', level='warning')

                        log('clone', f'Token verified: push={perms.get("push")}, admin={perms.get("admin")}')
                except urllib.error.HTTPError as e:
                    raise RuntimeError(f'GitHub API preflight failed (HTTP {e.code}): token may be invalid')
                except RuntimeError:
                    raise
                except Exception as e:
                    log('clone', f'Preflight check skipped: {e}', level='warning')

            # Build authenticated clone URL (token injected at runtime)
            repo_url = run.repo_url
            auth_url = _inject_github_token(repo_url, github_token)

            workdir = tempfile.mkdtemp(prefix=f'codejob-{str(run.id)[:8]}-')
            log('clone', f'Cloning {run.repo_url} (branch={run.base_branch}) into temp workspace')

            result = shell(
                f'git clone --depth 50 --branch {run.base_branch} {auth_url} repo',
                cwd=workdir, timeout=120,
            )
            if result.returncode != 0:
                raise RuntimeError(f'Clone failed (exit {result.returncode}): {result.stderr[:500]}')

            workdir = os.path.join(workdir, 'repo')
            log('clone', 'Clone successful')

            # Set git identity (container has no global config)
            shell('git config user.name "Code Worker"', cwd=workdir)
            shell('git config user.email "codeworker@donkeybetz.com"', cwd=workdir)

            # Ensure origin remote uses authenticated URL for push
            shell(f'git remote set-url origin {auth_url}', cwd=workdir)

            # Create working branch
            branch = run.working_branch or run.generate_working_branch()
            result = shell(f'git checkout -b {branch}', cwd=workdir)
            if result.returncode != 0:
                raise RuntimeError(f'Branch creation failed: {result.stderr[:300]}')
            log('clone', f'Created branch: {branch}')

        run.steps_completed = 1

        # ── Step 2: Implement ────────────────────────────────────────────
        run.set_step('implementing', 0.3)

        if is_dry_run:
            log('implement', f'[DRY RUN] Task: {run.plan_summary[:200]} — skipping')
        else:
            # Phase 5.1: Claude API code generation
            log('implement', 'Phase 5.1 codegen path enabled (sha=a932294d, mode=search-replace-v2)')
            log('implement', f'Task: {run.plan_summary[:200]}')
            assert workdir is not None, 'workdir must be set after clone'
            try:
                changed_files = _implement_with_claude(workdir, run, plan, log, shell)
                run.changed_files = changed_files
                run.save(update_fields=['changed_files'])
            except CodeJobError:
                raise  # typed exceptions pass through with their error code
            except Exception as impl_err:
                reason = 'LLM_NO_OUTPUT' if 'LLM_NO_OUTPUT' in str(impl_err) else 'IMPLEMENT_FAILED'
                raise RuntimeError(f'Implementation failed ({reason}): {impl_err}') from impl_err

        run.steps_completed = 2

        # ── Step 3: Test ─────────────────────────────────────────────────
        run.set_step('testing', 0.5)
        test_cmd = plan.get('test_command', '') or ''

        if is_dry_run:
            log('test', f'[DRY RUN] Would run tests: {test_cmd or "auto-detect"} — skipping')
            run.test_summary = {'command': test_cmd or 'skipped', 'exit_code': 0, 'note': 'dry_run'}
        elif test_cmd:
            # Validate against allowlist
            from core.models import Repo
            if test_cmd not in Repo.ALLOWED_TEST_COMMANDS:
                log('test', f'Test command not in allowlist: {test_cmd}', level='warning')
                run.test_summary = {'command': test_cmd, 'exit_code': -1, 'note': 'not in allowlist — skipped'}
            else:
                log('test', f'Running: {test_cmd}')
                result = shell(test_cmd, cwd=workdir, timeout=300)
                run.test_summary = {
                    'command': test_cmd,
                    'exit_code': result.returncode,
                    'stdout_tail': (result.stdout or '')[-2000:],
                    'stderr_tail': (result.stderr or '')[-1000:],
                }
                if result.returncode != 0:
                    log('test', f'Tests FAILED (exit {result.returncode})', level='warning')
                else:
                    log('test', 'Tests passed')
        else:
            log('test', 'No test command configured — skipping')
            run.test_summary = {'command': 'none', 'exit_code': 0, 'note': 'no test command'}

        run.steps_completed = 3
        run.save(update_fields=['test_summary'])

        # ── Step 4: Lint ─────────────────────────────────────────────────
        run.set_step('linting', 0.7)
        lint_cmd = plan.get('lint_command', '') or ''

        if is_dry_run:
            log('lint', f'[DRY RUN] Would lint: {lint_cmd or "none"} — skipping')
        elif lint_cmd:
            from core.models import Repo
            if lint_cmd not in Repo.ALLOWED_LINT_COMMANDS:
                log('lint', f'Lint command not in allowlist: {lint_cmd}', level='warning')
            else:
                log('lint', f'Running: {lint_cmd}')
                result = shell(lint_cmd, cwd=workdir, timeout=120)
                if result.returncode != 0:
                    log('lint', f'Lint warnings/errors (exit {result.returncode})', level='warning')
                else:
                    log('lint', 'Lint passed')
        else:
            log('lint', 'No lint command configured — skipping')

        run.steps_completed = 4

        # ── Step 5: Push ─────────────────────────────────────────────────
        run.set_step('pushing', 0.85)

        if is_dry_run:
            log('push', f'[DRY RUN] Would push branch: {run.working_branch} — skipping')
        else:
            log('push', f'Pushing branch: {run.working_branch}')
            result = shell(
                f'git push origin {run.working_branch}',
                cwd=workdir, timeout=60,
            )
            if result.returncode != 0:
                raise RuntimeError(f'Push failed (exit {result.returncode}): {result.stderr[:500]}')

            # Capture commit SHA
            sha_result = shell('git rev-parse HEAD', cwd=workdir)
            if sha_result.returncode == 0:
                run.commit_sha = sha_result.stdout.strip()[:40]
                run.save(update_fields=['commit_sha'])

            log('push', f'Push successful (sha: {run.commit_sha[:8]})')

        run.steps_completed = 5

        # ── Step 6: Create PR ────────────────────────────────────────────
        run.set_step('pushing', 0.95)  # reuse pushing state for PR

        if is_dry_run:
            log('pr', '[DRY RUN] Would create PR — skipping')
        else:
            if not github_token:
                log('pr', 'No GITHUB_TOKEN — skipping PR creation', level='warning')
            else:
                # Extract owner/repo from URL
                # https://github.com/clwest/donkey-betz-platform → clwest/donkey-betz-platform
                repo_slug = run.repo.get_repo_slug() if run.repo else ''
                if not repo_slug and run.repo_url:
                    repo_slug = run.repo_url.rstrip('/').split('github.com/')[-1].replace('.git', '')

                log('pr', f'Creating PR: {run.working_branch} → {run.base_branch} on {repo_slug}')

                pr_body = (
                    f'## Code Job: {str(run.id)[:8]}\n\n'
                    f'**Task:** {run.plan_summary[:500]}\n\n'
                )
                acceptance = plan.get('acceptance_criteria', [])
                if acceptance:
                    pr_body += '**Acceptance Criteria:**\n'
                    for criterion in acceptance:
                        pr_body += f'- [ ] {criterion}\n'
                    pr_body += '\n'

                test_info = run.test_summary or {}
                if test_info.get('exit_code') is not None:
                    status = 'passed' if test_info['exit_code'] == 0 else 'FAILED'
                    pr_body += f'**Tests:** {status} (`{test_info.get("command", "")}`)\n\n'

                pr_body += f'---\n*Auto-generated by Remote Code Worker*\n'

                pr_title = f'[CodeWorker] {run.plan_summary[:80]}'

                pr_data = json_mod.dumps({
                    'title': pr_title,
                    'head': run.working_branch,
                    'base': run.base_branch,
                    'body': pr_body,
                }).encode()

                req = urllib.request.Request(
                    f'https://api.github.com/repos/{repo_slug}/pulls',
                    data=pr_data,
                    headers={
                        'Authorization': f'token {github_token}',
                        'Accept': 'application/vnd.github+json',
                        'Content-Type': 'application/json',
                    },
                    method='POST',
                )
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        pr_resp = json_mod.loads(resp.read())
                        run.pr_url = pr_resp.get('html_url', '')
                        run.pr_number = pr_resp.get('number')
                        run.save(update_fields=['pr_url', 'pr_number'])
                        log('pr', f'PR created: {run.pr_url}')
                except urllib.error.HTTPError as e:
                    error_body = e.read().decode()[:500]
                    log('pr', f'PR creation failed (HTTP {e.code}): {error_body}', level='error')
                    # Don't fail the whole job — push succeeded
                except Exception as e:
                    log('pr', f'PR creation error: {e}', level='error')

        run.steps_completed = 6

        # ── Capture diff and mark success ────────────────────────────────
        diff_text = ''
        changed_files = []
        if workdir and not is_dry_run:
            diff_result = shell('git diff HEAD~1..HEAD', cwd=workdir)
            diff_text = (diff_result.stdout or '')[:500_000]

            status_result = shell('git diff --name-only HEAD~1..HEAD', cwd=workdir)
            changed_files = [f.strip() for f in (status_result.stdout or '').splitlines() if f.strip()]

        run.succeed(
            diff=diff_text or f'# {"Dry run" if is_dry_run else "No diff"} — mode={mode}',
            changed=changed_files,
            log=f'Pipeline completed successfully (mode={mode}).',
        )
        run.progress = 1.0
        run.save(update_fields=['progress'])

        log('complete', f'Pipeline completed (mode={mode}, steps=6/6)')

        # Post result to conversation if specified
        if run.conversation_id:
            try:
                from core.services.collaboration_protocol import post_structured_message
                # Session 1077: Clickable PR link in chat
                pr_info = ''
                if run.pr_url:
                    label = f'#{run.pr_number}' if run.pr_number else 'View PR'
                    pr_info = f'\n\n**PR Ready for Review:** [{label}]({run.pr_url})\n*Click to review and merge →*'
                post_structured_message(
                    user=run.created_by,
                    conversation_id=run.conversation_id,
                    msg_type='RESULT',
                    title=f'Code Job {str(run.id)[:8]}: {"Succeeded" if not is_dry_run else "Dry run complete"}',
                    body=(
                        f'**Task:** {run.plan_summary[:200]}\n'
                        f'**Branch:** `{run.working_branch}`\n'
                        f'**Mode:** {mode}\n'
                        f'**Files changed:** {len(changed_files)}{pr_info}'
                    ),
                    source='code-worker',
                )
            except Exception as e:
                log('notify', f'Could not post to conversation: {e}', level='warning')

        return {'status': 'succeeded', 'run_id': str(run.id), 'pr_url': run.pr_url or ''}

    except Exception as e:
        logger.exception('[CodeWorker] Run %s failed: %s', run_id, e)
        log('error', f'Job failed: {e}', level='error')
        is_infra = isinstance(e, (RuntimeError, OSError, subprocess.TimeoutExpired))
        err_str = str(e)

        # Map typed CodeJob exceptions directly to their error code
        if isinstance(e, CodeJobError):
            reason = e.code
        elif isinstance(e, subprocess.TimeoutExpired):
            reason = 'TIMEOUT'
        elif 'Clone failed' in err_str:
            reason = 'CLONE_FAILED'
        elif 'Push failed' in err_str:
            reason = 'PUSH_FAILED'
        elif 'INVALID_CHANGES_SCHEMA' in err_str:
            reason = 'INVALID_CHANGES_SCHEMA'
        elif 'INVALID_CHANGE_ITEM' in err_str:
            reason = 'INVALID_CHANGE_ITEM'
        elif 'IMPLEMENT_FAILED' in err_str:
            reason = 'IMPLEMENT_FAILED'
        elif 'LLM_NO_OUTPUT' in err_str:
            reason = 'LLM_NO_OUTPUT'
        else:
            reason = 'INTERNAL_EXCEPTION'
        run.fail(
            error=str(e),
            reason_code=reason,
            error_type=type(e).__name__,
            is_infra=is_infra,
        )
        return {'status': 'error', 'error': str(e)}
    finally:
        # Clean up temp workspace
        if workdir:
            try:
                parent = os.path.dirname(workdir)
                # workdir might be /tmp/codejob-xxx/repo — clean the parent
                cleanup_dir = parent if parent.startswith(tempfile.gettempdir()) else workdir
                if os.path.exists(cleanup_dir):
                    shutil.rmtree(cleanup_dir)
                    log('cleanup', f'Removed workspace: {cleanup_dir}')
            except Exception:
                pass


# ==================== RAG RETRIEVAL CANARY ====================



