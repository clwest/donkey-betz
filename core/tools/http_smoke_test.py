"""
PA HTTP Smoke Test Tool
=======================

Lets the PA run authenticated, multi-step HTTP smoke tests against
Railway (or local) and produce structured pass/fail reports.

Supports:
- Built-in suites (cockpit_health, cockpit_incidents_crud)
- Custom step definitions with assertions and variable capture
- SSRF allowlist (only *.railway.app, localhost, 127.0.0.1)
- Auth token resolved server-side (never from chat)

Safety limits:
- Max 50 steps per run
- 1 MB response body cap (truncated)
- 20s timeout per request
- Auth headers redacted from results
"""

import json
import logging
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from typing import Any

logger = logging.getLogger(__name__)

# ── Safety constants ────────────────────────────────────────────────────────

MAX_STEPS = 50
MAX_RESPONSE_BYTES = 1_048_576  # 1 MB
DEFAULT_TIMEOUT_MS = 20_000
ALLOWED_HOSTS_RE = re.compile(
    r'^(localhost|127\.0\.0\.1|[\w.-]+\.railway\.app)$', re.IGNORECASE
)

# ── Helpers ─────────────────────────────────────────────────────────────────


def _resolve_base_url(environment: str) -> str:
    if environment == 'local':
        return 'http://localhost:8000'
    return os.getenv(
        'RAILWAY_PUBLIC_URL',
        'https://donkey-betz-platform-production.up.railway.app',
    )


def _resolve_auth_token() -> str | None:
    return os.getenv('PA_API_TOKEN')


def _validate_domain(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname or ''
    if not ALLOWED_HOSTS_RE.match(hostname):
        return False
    # Block private IP ranges (except localhost)
    if hostname not in ('localhost', '127.0.0.1'):
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            if ip.is_private:
                return False
        except ValueError:
            pass  # hostname is not an IP — fine
    return True


def _resolve_variables(template: str, variables: dict[str, str]) -> str:
    def _replace(m: re.Match) -> str:
        key = m.group(1)
        return variables.get(key, m.group(0))

    result = re.sub(r'\{\{(\w+)\}\}', _replace, template)
    # Early-fail on unresolved vars to prevent cascading 500s
    unresolved = re.search(r'\{\{(\w+)\}\}', result)
    if unresolved:
        raise ValueError(f'Unresolved variable: {{{{{unresolved.group(1)}}}}}')
    return result


def _extract_value(data: Any, path: str) -> Any:
    """Lightweight dot-notation JSONPath: $.key, $.key.nested, $.key[0].nested"""
    if not path.startswith('$'):
        return None
    parts = path.lstrip('$.').split('.')
    current = data
    for part in parts:
        if current is None:
            return None
        # Handle array index: key[0]
        idx_match = re.match(r'^(\w+)\[(\d+)\]$', part)
        if idx_match:
            key, idx = idx_match.group(1), int(idx_match.group(2))
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
            if isinstance(current, list) and idx < len(current):
                current = current[idx]
            else:
                return None
        elif isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return None
        else:
            return None
    return current


def _redact_headers(headers: dict) -> dict:
    redacted = {}
    for k, v in headers.items():
        if k.lower() in ('authorization', 'cookie', 'x-api-key'):
            redacted[k] = '***REDACTED***'
        else:
            redacted[k] = v
    return redacted


def _run_step(
    step: dict,
    variables: dict[str, str],
    base_url: str,
    auth_headers: dict[str, str],
    timeout_ms: int,
) -> dict:
    """Execute one HTTP step, run assertions and captures, return result."""
    name = step.get('name', 'unnamed')
    method = step.get('method', 'GET').upper()

    try:
        path = _resolve_variables(step.get('path', '/'), variables)
    except ValueError as e:
        return {'name': name, 'ok': False, 'error': f'Variable resolution failed: {e}'}

    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    if not _validate_domain(url):
        return {
            'name': name,
            'ok': False,
            'error': f'SSRF blocked: {urllib.parse.urlparse(url).hostname}',
        }

    # Build request: auth_headers → Content-Type → step-level headers (step overrides)
    headers = {**auth_headers, 'Content-Type': 'application/json'}
    if step.get('headers'):
        try:
            resolved_step_headers = {
                k: _resolve_variables(v, variables)
                for k, v in step['headers'].items()
            }
        except ValueError as e:
            return {'name': name, 'ok': False, 'error': f'Header variable resolution failed: {e}'}
        headers.update(resolved_step_headers)

    body = None
    if step.get('body'):
        try:
            body_str = _resolve_variables(json.dumps(step['body']), variables)
        except ValueError as e:
            return {'name': name, 'ok': False, 'error': f'Body variable resolution failed: {e}'}
        body = body_str.encode('utf-8')

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    timeout_s = min(timeout_ms / 1000, 20)

    result: dict[str, Any] = {
        'name': name,
        'method': method,
        'path': path,
        'ok': True,
        'assertions': [],
        'captures': {},
    }

    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            status = resp.status
            raw = resp.read(MAX_RESPONSE_BYTES)
            result['status'] = status
            result['latency_ms'] = int((time.monotonic() - start) * 1000)

            try:
                data = json.loads(raw)
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = raw.decode('utf-8', errors='replace')[:2000]
            result['response_preview'] = _preview(data)
    except urllib.error.HTTPError as e:
        status = e.code
        result['status'] = status
        result['latency_ms'] = int((time.monotonic() - start) * 1000)
        try:
            data = json.loads(e.read(MAX_RESPONSE_BYTES))
        except Exception:
            data = None
        result['response_preview'] = _preview(data) if data else str(e)
    except Exception as e:
        result['ok'] = False
        result['error'] = f'{type(e).__name__}: {e}'
        result['latency_ms'] = int((time.monotonic() - start) * 1000)
        return result

    # Run assertions
    for assertion in step.get('assert', []):
        a_result = _check_assertion(assertion, status, data)
        result['assertions'].append(a_result)
        if not a_result['pass']:
            result['ok'] = False

    # Run captures
    for capture in step.get('capture', []):
        var_name = capture.get('as')
        json_path = capture.get('json_path')
        if var_name and json_path and isinstance(data, (dict, list)):
            val = _extract_value(data, json_path)
            if val is not None:
                variables[var_name] = str(val)
                result['captures'][var_name] = str(val)

    return result


def _preview(data: Any, max_len: int = 500) -> Any:
    """Return a short preview of the response for the report."""
    if isinstance(data, dict):
        # Show keys + truncated values
        preview = {}
        for k, v in list(data.items())[:15]:
            if isinstance(v, (list, dict)):
                preview[k] = f"<{type(v).__name__} len={len(v)}>"
            elif isinstance(v, str) and len(v) > 80:
                preview[k] = v[:80] + '...'
            else:
                preview[k] = v
        return preview
    if isinstance(data, str):
        return data[:max_len]
    return str(data)[:max_len]


def _check_assertion(assertion: dict, status: int, data: Any) -> dict:
    """Evaluate a single assertion. Returns {'check': ..., 'pass': bool, 'detail': ...}."""
    check = assertion.get('check', '')
    expected = assertion.get('expected')

    if check == 'status':
        passed = status == expected
        return {'check': f'status == {expected}', 'pass': passed, 'detail': f'got {status}'}

    if check == 'has_key':
        key = assertion.get('key', '')
        passed = isinstance(data, dict) and key in data
        return {'check': f'has_key "{key}"', 'pass': passed, 'detail': f'keys={list(data.keys())[:10]}' if isinstance(data, dict) else 'not a dict'}

    if check == 'json_path':
        path = assertion.get('path', '')
        actual = _extract_value(data, path) if isinstance(data, (dict, list)) else None
        if assertion.get('operator') == 'gte':
            passed = actual is not None and actual >= expected
            return {'check': f'{path} >= {expected}', 'pass': passed, 'detail': f'got {actual}'}
        elif assertion.get('operator') == 'eq':
            passed = actual == expected
            return {'check': f'{path} == {expected}', 'pass': passed, 'detail': f'got {actual}'}
        elif assertion.get('operator') == 'exists':
            passed = actual is not None
            return {'check': f'{path} exists', 'pass': passed, 'detail': f'got {actual}'}
        else:
            passed = actual == expected
            return {'check': f'{path} == {expected}', 'pass': passed, 'detail': f'got {actual}'}

    if check == 'type':
        key = assertion.get('key', '')
        expected_type = assertion.get('type', '')
        val = data.get(key) if isinstance(data, dict) else None
        type_map = {'list': list, 'dict': dict, 'str': str, 'int': int, 'bool': bool}
        passed = isinstance(val, type_map.get(expected_type, object))
        return {'check': f'typeof {key} == {expected_type}', 'pass': passed, 'detail': f'got {type(val).__name__}'}

    return {'check': check, 'pass': False, 'detail': 'unknown assertion type'}


# ── Built-in suites ────────────────────────────────────────────────────────

BUILTIN_SUITES: dict[str, list[dict]] = {
    'cockpit_health': [
        {'name': 'errors', 'method': 'GET', 'path': '/api/cockpit/errors/', 'assert': [{'check': 'status', 'expected': 200}, {'check': 'has_key', 'key': 'signatures'}]},
        {'name': 'runs', 'method': 'GET', 'path': '/api/cockpit/runs/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'inbox', 'method': 'GET', 'path': '/api/cockpit/inbox/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'ops_overview', 'method': 'GET', 'path': '/api/cockpit/ops/overview/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'library_deliverables', 'method': 'GET', 'path': '/api/cockpit/library/deliverables/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'library_media', 'method': 'GET', 'path': '/api/cockpit/library/media/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'approvals', 'method': 'GET', 'path': '/api/cockpit/approvals/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'alerts', 'method': 'GET', 'path': '/api/cockpit/alerts/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'audit', 'method': 'GET', 'path': '/api/cockpit/audit/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'agents', 'method': 'GET', 'path': '/api/cockpit/agents/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'queues', 'method': 'GET', 'path': '/api/cockpit/queues/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'cost', 'method': 'GET', 'path': '/api/cockpit/cost/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'autopilot_policies', 'method': 'GET', 'path': '/api/cockpit/autopilot/policies/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'autopilot_history', 'method': 'GET', 'path': '/api/cockpit/autopilot/history/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'config', 'method': 'GET', 'path': '/api/cockpit/config/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'config_flags', 'method': 'GET', 'path': '/api/cockpit/config/flags/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'config_changes', 'method': 'GET', 'path': '/api/cockpit/config/changes/', 'assert': [{'check': 'status', 'expected': 200}]},
        {'name': 'incidents', 'method': 'GET', 'path': '/api/cockpit/incidents/', 'assert': [{'check': 'status', 'expected': 200}]},
    ],

    'cockpit_incidents_crud': [
        # 1. Create a smoke-test incident (tagged with test_run_id)
        {
            'name': 'create_incident',
            'method': 'POST',
            'path': '/api/cockpit/incidents/',
            'body': {
                'title': '[SMOKE][{{test_run_id}}] Test incident — auto-cleanup',
                'severity': 'low',
                'description': 'Automated smoke test incident. Safe to delete.',
            },
            'assert': [
                {'check': 'status', 'expected': 201},
                {'check': 'has_key', 'key': 'id'},
            ],
            'capture': [
                {'json_path': '$.id', 'as': 'incident_id'},
            ],
        },
        # 2. GET detail (initial — before any events)
        {
            'name': 'get_detail_initial',
            'depends_on': ['create_incident'],
            'method': 'GET',
            'path': '/api/cockpit/incidents/{{incident_id}}/',
            'assert': [
                {'check': 'status', 'expected': 200},
                {'check': 'has_key', 'key': 'incident'},
                {'check': 'has_key', 'key': 'events'},
                {'check': 'json_path', 'path': '$.event_count', 'operator': 'gte', 'expected': 0},
            ],
        },
        # 3. Negative test: add note without required 'text' field
        {
            'name': 'negative_note_missing_text',
            'depends_on': ['create_incident'],
            'method': 'POST',
            'path': '/api/cockpit/incidents/{{incident_id}}/events/',
            'body': {
                'event_type': 'note',
            },
            'assert': [
                {'check': 'status', 'expected': 400},
                {'check': 'json_path', 'path': '$.ok', 'operator': 'eq', 'expected': False},
            ],
        },
        # 4. Negative test: add link without required fields
        {
            'name': 'negative_link_missing_fields',
            'depends_on': ['create_incident'],
            'method': 'POST',
            'path': '/api/cockpit/incidents/{{incident_id}}/events/',
            'body': {
                'event_type': 'link',
            },
            'assert': [
                {'check': 'status', 'expected': 400},
                {'check': 'json_path', 'path': '$.ok', 'operator': 'eq', 'expected': False},
            ],
        },
        # 5. Add note event
        {
            'name': 'add_note',
            'depends_on': ['create_incident'],
            'method': 'POST',
            'path': '/api/cockpit/incidents/{{incident_id}}/events/',
            'body': {
                'event_type': 'note',
                'text': 'Smoke test note event',
            },
            'assert': [{'check': 'status', 'expected': 201}],
            'capture': [{'json_path': '$.id', 'as': 'note_event_id'}],
        },
        # 6. Add link event
        {
            'name': 'add_link',
            'depends_on': ['create_incident'],
            'method': 'POST',
            'path': '/api/cockpit/incidents/{{incident_id}}/events/',
            'body': {
                'event_type': 'link',
                'link_type': 'url',
                'link_id': 'https://example.com/smoke-test',
                'label': 'Smoke test link',
            },
            'assert': [{'check': 'status', 'expected': 201}],
            'capture': [{'json_path': '$.id', 'as': 'link_event_id'}],
        },
        # 7. Update status to resolved
        {
            'name': 'resolve_incident',
            'depends_on': ['create_incident'],
            'method': 'POST',
            'path': '/api/cockpit/incidents/{{incident_id}}/update/',
            'body': {
                'status': 'resolved',
                'resolution_summary': 'Smoke test auto-resolved [{{test_run_id}}]',
            },
            'assert': [{'check': 'status', 'expected': 200}],
        },
        # 8. Verify final state (depends on all mutation steps)
        {
            'name': 'verify_resolved',
            'depends_on': ['add_note', 'add_link', 'resolve_incident'],
            'method': 'GET',
            'path': '/api/cockpit/incidents/{{incident_id}}/',
            'assert': [
                {'check': 'status', 'expected': 200},
                {'check': 'json_path', 'path': '$.incident.status', 'operator': 'eq', 'expected': 'resolved'},
                {'check': 'json_path', 'path': '$.event_count', 'operator': 'gte', 'expected': 3},
            ],
        },
    ],
}


# ── Main entry point ───────────────────────────────────────────────────────


def run_smoke_test(payload: dict) -> dict:
    """
    Run an HTTP smoke test suite. Called by ToolDispatcher handler.

    Args:
        payload: {
            suite: str (built-in suite name) OR
            steps: list[dict] (custom steps),
            environment: "railway_prod" | "local",
            fail_fast: bool (default True)
        }

    Returns:
        {ok, passed, failed, total, environment, results: [...]}
    """
    suite_name = payload.get('suite')
    environment = payload.get('environment', 'railway_prod')
    fail_fast = payload.get('fail_fast', True)

    # Resolve steps
    if suite_name:
        steps = BUILTIN_SUITES.get(suite_name)
        if not steps:
            return {
                'ok': False,
                'error': f"Unknown suite: {suite_name}. Available: {list(BUILTIN_SUITES.keys())}",
            }
    else:
        steps = payload.get('steps', [])
        if not steps:
            return {'ok': False, 'error': 'No suite or steps provided'}

    if len(steps) > MAX_STEPS:
        return {'ok': False, 'error': f'Too many steps: {len(steps)} (max {MAX_STEPS})'}

    # Resolve environment
    base_url = _resolve_base_url(environment)
    token = _resolve_auth_token()
    auth_headers: dict[str, str] = {}
    if token:
        auth_headers['Authorization'] = f'Token {token}'

    # Run steps
    test_run_id = uuid.uuid4().hex[:12]
    variables: dict[str, str] = {'test_run_id': test_run_id}
    results = []
    passed = 0
    failed = 0
    skipped = 0
    step_outcomes: dict[str, str] = {}

    for step in steps:
        name = step.get('name', 'unnamed')

        # Check depends_on — skip if any dependency failed/skipped/missing
        depends_on = step.get('depends_on', [])
        skip = False
        for dep in depends_on:
            outcome = step_outcomes.get(dep)
            if outcome != 'passed':
                skip = True
                break

        if skip:
            step_outcomes[name] = 'skipped'
            skipped += 1
            results.append({
                'name': name,
                'ok': False,
                'skipped': True,
                'error': f"Skipped: dependency '{dep}' {outcome or 'not found'}",
            })
            continue

        timeout_ms = step.get('timeout_ms', DEFAULT_TIMEOUT_MS)
        step_result = _run_step(step, variables, base_url, auth_headers, timeout_ms)
        results.append(step_result)

        if step_result.get('ok'):
            passed += 1
            step_outcomes[name] = 'passed'
        else:
            failed += 1
            step_outcomes[name] = 'failed'
            if fail_fast:
                break

    ok = failed == 0 and skipped == 0

    logger.info(
        f"[http_smoke_test] suite={suite_name or 'custom'} env={environment} "
        f"run={test_run_id} passed={passed} failed={failed} skipped={skipped} "
        f"total={len(results)}"
    )

    return {
        'ok': ok,
        'suite': suite_name or 'custom',
        'environment': environment,
        'base_url': base_url,
        'test_run_id': test_run_id,
        'passed': passed,
        'failed': failed,
        'skipped': skipped,
        'total': len(results),
        'results': results,
    }
