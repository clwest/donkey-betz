"""
ToolDispatcher GatewayHandlersMixin — extracted handler methods.
"""

"""
Tool Dispatcher - Centralized Tool Execution with No Silent Failures
=====================================================================

Session 931: Created to solve the "tool exists != tool works" problem.

Every tool call goes through this dispatcher which:
1. Wraps execution in try/catch
2. Measures latency
3. Generates trace_id for debugging
4. Returns structured result (never fails silently)

Usage:
    from core.services.tool_dispatcher import get_tool_dispatcher

    dispatcher = get_tool_dispatcher()
    result = await dispatcher.execute(
        tool_name="human_decisions_tool",
        payload={"action": "list"},
        user_id=user.id
    )

    # Result is always structured:
    # {
    #     "ok": True/False,
    #     "tool": "human_decisions_tool",
    #     "latency_ms": 234,
    #     "error_code": None,
    #     "error_message": None,
    #     "trace_id": "abc123",
    #     "result": {...}
    # }
"""

import logging
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)


# Error codes for structured failures
class ToolErrorCode:
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_TIMEOUT = "TOOL_TIMEOUT"
    TOOL_EXCEPTION = "TOOL_EXCEPTION"
    TOOL_INVALID_PAYLOAD = "TOOL_INVALID_PAYLOAD"
    TOOL_PERMISSION_DENIED = "TOOL_PERMISSION_DENIED"
    TOOL_DEPENDENCY_FAILED = "TOOL_DEPENDENCY_FAILED"
    AGENT_EXECUTION_FAILED = "AGENT_EXECUTION_FAILED"


@dataclass
class ToolResult:
    """Structured result from tool execution."""
    ok: bool
    tool: str
    latency_ms: int
    error_code: Optional[str]
    error_message: Optional[str]
    trace_id: str
    result: Optional[Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)




class GatewayHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    def _handle_repo(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Read-only codebase introspection: tree, read_file, search, git_info."""
        import os
        import subprocess

        action = payload.get('action', 'tree')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Security: block reading secrets
        BLOCKED_FILES = {'.env', '.env.local', '.env.production', 'credentials.json', 'secrets.yaml'}
        BLOCKED_DIRS = {'.git/objects', '.git/refs', 'node_modules', '.venv', '__pycache__'}

        def _safe_path(rel_path: str) -> str:
            """Resolve path and ensure it's within project root."""
            if not rel_path:
                return project_root
            full = os.path.normpath(os.path.join(project_root, rel_path))
            if not full.startswith(project_root):
                raise ValueError('Path outside project root')
            basename = os.path.basename(full)
            if basename in BLOCKED_FILES:
                raise ValueError(f'Access denied: {basename}')
            for bd in BLOCKED_DIRS:
                if bd in full:
                    raise ValueError(f'Access denied: {bd}')
            return full

        try:
            if action == 'tree':
                rel_path = payload.get('path', '')
                depth = min(payload.get('depth', 2), 4)
                full_path = _safe_path(rel_path)
                if not os.path.isdir(full_path):
                    return {'error': f'Not a directory: {rel_path}'}

                entries = []
                for root, dirs, files in os.walk(full_path):
                    # Calculate depth relative to full_path
                    rel = os.path.relpath(root, full_path)
                    level = 0 if rel == '.' else rel.count(os.sep) + 1
                    if level >= depth:
                        dirs.clear()
                        continue
                    # Skip blocked dirs
                    dirs[:] = sorted([d for d in dirs if d not in {'.git', 'node_modules', '.venv', '__pycache__', 'dist', '.next'}])
                    display_root = os.path.relpath(root, project_root)
                    for d in dirs:
                        entries.append(f'{display_root}/{d}/')
                    for f in sorted(files)[:50]:  # cap files per dir
                        if f not in BLOCKED_FILES:
                            entries.append(f'{display_root}/{f}')
                    if len(entries) > 500:
                        entries.append('... (truncated at 500 entries)')
                        break

                return {'action': 'tree', 'path': rel_path or '.', 'depth': depth, 'entries': entries, 'count': len(entries)}

            elif action == 'read_file':
                rel_path = payload.get('path', '')
                if not rel_path:
                    return {'error': 'path is required for read_file'}
                max_lines = min(payload.get('max_lines', 200), 500)
                start_line = max(int(payload.get('start_line', 0)), 0)
                full_path = _safe_path(rel_path)
                if not os.path.isfile(full_path):
                    return {'error': f'File not found: {rel_path}'}

                size = os.path.getsize(full_path)
                if size > 500_000:
                    return {'error': f'File too large: {size} bytes. Use search instead.'}

                with open(full_path, 'r', errors='replace') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i < start_line:
                            continue
                        if len(lines) >= max_lines:
                            break
                        lines.append(f'{i + 1}: {line.rstrip(chr(10))}')

                total_lines = sum(1 for _ in open(full_path, 'r', errors='replace'))
                end_line = start_line + len(lines)
                return {
                    'action': 'read_file',
                    'path': rel_path,
                    'start_line': start_line,
                    'end_line': end_line,
                    'lines': len(lines),
                    'total_lines': total_lines,
                    'truncated': end_line < total_lines,
                    'content': '\n'.join(lines),
                }

            elif action == 'search':
                query = payload.get('query', '')
                if not query:
                    return {'error': 'query is required for search'}
                search_path = payload.get('path', '')
                file_type = payload.get('file_type', '')
                full_path = _safe_path(search_path)

                cmd = ['grep', '-rn', '--include=*', '-l', query, full_path]
                if file_type:
                    cmd = ['grep', '-rn', f'--include=*.{file_type}', '-l', query, full_path]

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, cwd=project_root)
                    files = [os.path.relpath(f, project_root) for f in result.stdout.strip().split('\n') if f]
                    files = [f for f in files if not any(bd in f for bd in BLOCKED_DIRS) and os.path.basename(f) not in BLOCKED_FILES]

                    # Get matching lines from first few files
                    matches = []
                    for fpath in files[:10]:
                        cmd2 = ['grep', '-n', query, os.path.join(project_root, fpath)]
                        r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=5)
                        for line in r2.stdout.strip().split('\n')[:5]:
                            if line:
                                matches.append(f'{fpath}:{line}')

                    return {
                        'action': 'search',
                        'query': query,
                        'files_matched': len(files),
                        'files': files[:30],
                        'sample_matches': matches[:30],
                    }
                except subprocess.TimeoutExpired:
                    return {'error': 'Search timed out (10s limit)'}

            elif action == 'git_info':
                result = {}
                try:
                    r = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    result['branch'] = r.stdout.strip()
                except Exception:
                    result['branch'] = 'unknown'

                try:
                    r = subprocess.run(['git', 'log', '--oneline', '-10'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    result['recent_commits'] = r.stdout.strip().split('\n')
                except Exception:
                    result['recent_commits'] = []

                try:
                    r = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, cwd=project_root, timeout=5)
                    lines = r.stdout.strip().split('\n') if r.stdout.strip() else []
                    result['modified_files'] = len(lines)
                    result['status'] = lines[:20]
                except Exception:
                    result['modified_files'] = 0
                    result['status'] = []

                return {'action': 'git_info', **result}

            return {'error': f'Unknown repo_tool action: {action}'}

        except ValueError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': f'repo_tool error: {str(e)}'}

    # ── Analytics / Event Queries ────────────────────────────────────────────

    def _handle_analytics(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Query DeliverableEvents and ATR-24h metrics."""
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Min, Q

        action = payload.get('action', 'events_summary')

        try:
            from core.models_deliverables import Deliverable, DeliverableEvent

            if action == 'events_summary':
                days = payload.get('days', 7)
                since = timezone.now() - timedelta(days=days)

                events = DeliverableEvent.objects.filter(created_at__gte=since)
                by_type = list(events.values('event_type').annotate(count=Count('id')).order_by('-count'))
                by_source = list(events.values('source').annotate(count=Count('id')).order_by('-count'))
                total = events.count()

                return {
                    'action': 'events_summary',
                    'days': days,
                    'total_events': total,
                    'by_type': by_type,
                    'by_source': by_source,
                }

            elif action == 'atr_dashboard':
                # Reuse the stage3_dashboard view logic
                from core.views_deliverables import stage3_dashboard
                from django.test import RequestFactory
                from django.contrib.auth.models import AnonymousUser

                rf = RequestFactory()
                request = rf.get('/api/deliverables/stage3-dashboard/')
                request.user = AnonymousUser()
                response = stage3_dashboard(request)

                import json
                data = json.loads(response.content)
                return {'action': 'atr_dashboard', **data.get('dashboard', {})}

            elif action == 'events_query':
                days = payload.get('days', 7)
                limit = min(payload.get('limit', 50), 200)
                since = timezone.now() - timedelta(days=days)

                qs = DeliverableEvent.objects.filter(created_at__gte=since)

                event_type = payload.get('event_type')
                if event_type:
                    qs = qs.filter(event_type=event_type)

                deliverable_id = payload.get('deliverable_id')
                if deliverable_id:
                    qs = qs.filter(deliverable_id=deliverable_id)

                qs = qs.order_by('-created_at')[:limit]
                events = [
                    {
                        'id': str(e.id),
                        'event_type': e.event_type,
                        'deliverable_id': str(e.deliverable_id),
                        'deliverable_title': e.deliverable.title if e.deliverable else None,
                        'source': e.source,
                        'created_at': e.created_at.isoformat(),
                        'metadata': e.metadata or {},
                    }
                    for e in qs.select_related('deliverable')
                ]
                return {'action': 'events_query', 'count': len(events), 'events': events}

            return {'error': f'Unknown analytics_tool action: {action}'}

        except Exception as e:
            return {'error': f'analytics_tool error: {str(e)}'}

    # ── Discord Bot Introspection ────────────────────────────────────────────

    def _handle_discord(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Inspect Discord bot: commands, cogs, slot usage."""
        import os
        import re

        action = payload.get('action', 'status')
        bot_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'core', 'services', 'discord_bot.py'
        )

        try:
            if not os.path.isfile(bot_file):
                return {'error': 'discord_bot.py not found'}

            with open(bot_file, 'r') as f:
                content = f.read()

            if action == 'status':
                # Extract slot usage from comments
                slot_match = re.search(r'(\d+)\s*slots?\s*used', content)
                slots_used = int(slot_match.group(1)) if slot_match else None

                # Count cogs
                cog_classes = re.findall(r'class\s+(\w+)\(commands\.Cog\)', content)

                # Count app_commands
                slash_commands = re.findall(r'@app_commands\.command\(name=["\'](\w+)', content)
                groups = re.findall(r'app_commands\.Group\(name=["\'](\w+)', content)
                subcommands = re.findall(r'@(\w+)\.command\(name=["\'](\w+)', content)

                # Guild ID
                guild_match = re.search(r'GUILD_ID\s*=\s*(\d+)', content)
                guild_id = guild_match.group(1) if guild_match else None

                return {
                    'action': 'status',
                    'file': 'core/services/discord_bot.py',
                    'file_lines': content.count('\n') + 1,
                    'slots_used': slots_used,
                    'slots_limit': 100,
                    'slots_remaining': (100 - slots_used) if slots_used else None,
                    'sync_mode': 'guild_only',
                    'guild_id': guild_id,
                    'cog_count': len(cog_classes),
                    'top_level_commands': len(slash_commands),
                    'command_groups': len(groups),
                    'subcommands': len(subcommands),
                }

            elif action == 'commands':
                # Extract all slash commands
                slash_commands = re.findall(r'@app_commands\.command\(name=["\'](\w+)["\'](?:,\s*description=["\']([^"\']*)["\'])?\)', content)
                groups = re.findall(r'(\w+)\s*=\s*app_commands\.Group\(name=["\'](\w+)["\'](?:,\s*description=["\']([^"\']*)["\'])?\)', content)

                # Build group -> subcommands map
                group_vars = {g[0]: g[1] for g in groups}
                subcommands = re.findall(r'@(\w+)\.command\(name=["\'](\w+)["\']', content)
                group_subs = {}
                for var, sub_name in subcommands:
                    group_name = group_vars.get(var, var)
                    if group_name not in group_subs:
                        group_subs[group_name] = []
                    group_subs[group_name].append(sub_name)

                top_level = [{'name': f'/{c[0]}', 'description': c[1] if len(c) > 1 else ''} for c in slash_commands]
                grouped = [
                    {'group': f'/{g[1]}', 'description': g[2] if len(g) > 2 else '', 'subcommands': group_subs.get(g[1], [])}
                    for g in groups
                ]

                return {
                    'action': 'commands',
                    'top_level': top_level,
                    'top_level_count': len(top_level),
                    'groups': grouped,
                    'groups_count': len(grouped),
                    'total_subcommands': sum(len(g['subcommands']) for g in grouped),
                }

            elif action == 'cogs':
                cog_classes = re.findall(r'class\s+(\w+)\(commands\.Cog\)', content)
                return {'action': 'cogs', 'cogs': cog_classes, 'count': len(cog_classes)}

            return {'error': f'Unknown discord_tool action: {action}'}

        except Exception as e:
            return {'error': f'discord_tool error: {str(e)}'}

    # ── Mobile App Introspection ─────────────────────────────────────────────

    def _handle_mobile(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Inspect the React Native / Expo mobile app."""
        import os
        import json as json_mod

        action = payload.get('action', 'project_status')
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        mobile_root = os.path.join(project_root, 'mobile')

        try:
            if not os.path.isdir(mobile_root):
                return {'error': 'No mobile/ directory found in project root'}

            if action == 'project_status':
                result = {'action': 'project_status', 'path': 'mobile/'}

                # Read package.json
                pkg_path = os.path.join(mobile_root, 'package.json')
                if os.path.isfile(pkg_path):
                    with open(pkg_path, 'r') as f:
                        pkg = json_mod.load(f)
                    result['name'] = pkg.get('name', 'unknown')
                    result['version'] = pkg.get('version', 'unknown')
                    deps = pkg.get('dependencies', {})
                    result['expo_version'] = deps.get('expo', 'not found')
                    result['react_native_version'] = deps.get('react-native', 'not found')
                    result['navigation'] = 'react-navigation' if '@react-navigation/native' in deps else 'expo-router' if 'expo-router' in deps else 'unknown'
                    result['total_dependencies'] = len(deps)

                # Read app.config.ts or app.json
                for cfg_name in ['app.config.ts', 'app.config.js', 'app.json']:
                    cfg_path = os.path.join(mobile_root, cfg_name)
                    if os.path.isfile(cfg_path):
                        result['config_file'] = cfg_name
                        break

                # Check EAS config
                eas_path = os.path.join(mobile_root, 'eas.json')
                if os.path.isfile(eas_path):
                    with open(eas_path, 'r') as f:
                        eas = json_mod.load(f)
                    result['eas_profiles'] = list(eas.get('build', {}).keys())

                return result

            elif action == 'screens':
                screens_dir = os.path.join(mobile_root, 'src', 'screens')
                if not os.path.isdir(screens_dir):
                    return {'error': 'No src/screens/ directory found'}

                screens = []
                for f in sorted(os.listdir(screens_dir)):
                    if f.endswith('.tsx') or f.endswith('.ts'):
                        fpath = os.path.join(screens_dir, f)
                        size = os.path.getsize(fpath)
                        # Check if it's a placeholder
                        with open(fpath, 'r') as fh:
                            first_500 = fh.read(500)
                        is_placeholder = 'Placeholder' in first_500 or 'Coming soon' in first_500.lower()
                        screens.append({
                            'file': f,
                            'name': f.replace('.tsx', '').replace('.ts', ''),
                            'size_bytes': size,
                            'status': 'placeholder' if is_placeholder else 'implemented',
                        })

                # Also check screen registry
                registry_path = os.path.join(mobile_root, 'src', 'navigation', 'screenRegistry.ts')
                routes = []
                if os.path.isfile(registry_path):
                    with open(registry_path, 'r') as f:
                        import re
                        reg_content = f.read()
                    route_matches = re.findall(r"'(/[^']*)'.*?:\s*(\w+)", reg_content)
                    routes = [{'route': r[0], 'component': r[1]} for r in route_matches]

                return {
                    'action': 'screens',
                    'screens': screens,
                    'count': len(screens),
                    'implemented': sum(1 for s in screens if s['status'] == 'implemented'),
                    'placeholders': sum(1 for s in screens if s['status'] == 'placeholder'),
                    'routes': routes,
                }

            elif action == 'api_modules':
                api_dir = os.path.join(mobile_root, 'src', 'api')
                if not os.path.isdir(api_dir):
                    return {'error': 'No src/api/ directory found'}

                modules = []
                for f in sorted(os.listdir(api_dir)):
                    if f.endswith('.ts') or f.endswith('.tsx'):
                        fpath = os.path.join(api_dir, f)
                        size = os.path.getsize(fpath)
                        modules.append({'file': f, 'size_bytes': size})

                return {'action': 'api_modules', 'modules': modules, 'count': len(modules)}

            elif action == 'dependencies':
                pkg_path = os.path.join(mobile_root, 'package.json')
                if not os.path.isfile(pkg_path):
                    return {'error': 'No package.json found'}
                with open(pkg_path, 'r') as f:
                    pkg = json_mod.load(f)
                deps = pkg.get('dependencies', {})
                dev_deps = pkg.get('devDependencies', {})
                # Return key deps only
                key_packages = [
                    'expo', 'react-native', 'react', '@react-navigation/native',
                    '@react-navigation/drawer', 'expo-router', 'zustand',
                    'axios', '@sentry/react-native', 'expo-notifications',
                    'expo-secure-store', '@react-native-async-storage/async-storage',
                ]
                key_deps = {k: deps.get(k, dev_deps.get(k, 'not installed')) for k in key_packages}
                return {
                    'action': 'dependencies',
                    'total_deps': len(deps),
                    'total_dev_deps': len(dev_deps),
                    'key_packages': key_deps,
                }

            return {'error': f'Unknown mobile_tool action: {action}'}

        except Exception as e:
            return {'error': f'mobile_tool error: {str(e)}'}

    def _handle_vip_invite(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Manage VIP magic-link invites for demo viewers."""
        from django.contrib.auth import get_user_model
        from core.models_vip_invite import VIPInvite
        from django.conf import settings as django_settings

        User = get_user_model()
        action = payload.get('action', 'list')

        try:
            if action == 'list':
                invites = VIPInvite.objects.select_related('created_by', 'redeemed_by').all()[:20]
                return {
                    'action': 'list',
                    'total': VIPInvite.objects.count(),
                    'invites': [{
                        'id': str(inv.id),
                        'label': inv.label,
                        'is_valid': inv.is_valid,
                        'token_expires_at': inv.token_expires_at.isoformat(),
                        'redeemed_by': inv.redeemed_by.username if inv.redeemed_by else None,
                        'revoked': inv.revoked_at is not None,
                        'created_by': inv.created_by.username,
                    } for inv in invites],
                }

            elif action == 'create':
                label = payload.get('label', '')
                admin_user = User.objects.filter(is_superuser=True).first()
                if not admin_user:
                    return {'error': 'No admin user found to create invite'}

                invite = VIPInvite.objects.create(created_by=admin_user, label=label)
                base_url = getattr(django_settings, 'FRONTEND_URL', 'https://donkey-betz-platform-production.up.railway.app')
                accept_url = f"{base_url.rstrip('/')}/vip/accept?token={invite.token}"

                return {
                    'action': 'create',
                    'id': str(invite.id),
                    'token': invite.token,
                    'accept_url': accept_url,
                    'token_expires_at': invite.token_expires_at.isoformat(),
                    'account_expires_at': invite.account_expires_at.isoformat(),
                    'label': invite.label,
                }

            elif action == 'revoke':
                invite_id = payload.get('id', '')
                if not invite_id:
                    return {'error': 'Provide invite id to revoke'}
                try:
                    invite = VIPInvite.objects.get(id=invite_id)
                except VIPInvite.DoesNotExist:
                    return {'error': f'Invite {invite_id} not found'}
                if invite.revoked_at:
                    return {'error': 'Already revoked'}

                from django.utils import timezone
                invite.revoked_at = timezone.now()
                invite.save(update_fields=['revoked_at'])
                if invite.redeemed_by:
                    invite.redeemed_by.is_active = False
                    invite.redeemed_by.save(update_fields=['is_active'])

                return {'action': 'revoke', 'id': str(invite.id), 'status': 'revoked'}

            else:
                return {'error': f'Unknown action: {action}. Use list, create, or revoke.'}

        except Exception as e:
            logger.error(f"[VIP_INVITE] Error: {e}", exc_info=True)
            return {'error': str(e)}


    # ── Session 1100: Cockpit Tool — Celery ops dashboard ───────────────────────
    def _handle_cockpit(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Celery ops cockpit: beat schedule, task status, worker health, queue depths, failures."""
        action = payload.get('action', 'help')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            if action == 'help':
                return {
                    'tool': 'cockpit_tool',
                    'actions': [
                        'beat_schedule — list all Celery Beat periodic tasks',
                        'task_status — check a specific task by ID',
                        'worker_health — active workers, queues, concurrency',
                        'recent_failures — failed tasks with errors',
                        'queue_lengths — current queue depths',
                        'trigger_task — manually dispatch an allowlisted Celery task',
                    ],
                }

            if action == 'beat_schedule':
                from django_celery_beat.models import PeriodicTask
                tasks = PeriodicTask.objects.select_related(
                    'interval', 'crontab'
                ).order_by('name')[:limit]
                return {
                    'action': 'beat_schedule',
                    'total': PeriodicTask.objects.count(),
                    'tasks': [{
                        'name': t.name,
                        'task': t.task,
                        'enabled': t.enabled,
                        'schedule': str(t.interval or t.crontab or 'custom'),
                        'last_run_at': t.last_run_at.isoformat() if t.last_run_at else None,
                        'total_run_count': t.total_run_count,
                        'queue': t.queue or 'default',
                    } for t in tasks],
                }

            if action == 'task_status':
                task_id = payload.get('task_id', '')
                if not task_id:
                    return {'error': 'Provide task_id to check status'}
                from core.models_celery_telemetry import CeleryTaskEvent
                event = CeleryTaskEvent.objects.filter(
                    task_id=task_id
                ).order_by('-started_at').first()
                if event:
                    return {
                        'action': 'task_status',
                        'source': 'celery_event',
                        'task_id': task_id,
                        'task_name': event.task_name,
                        'status': event.status,
                        'started_at': event.started_at.isoformat() if event.started_at else None,
                        'finished_at': event.finished_at.isoformat() if event.finished_at else None,
                        'duration_seconds': event.duration_seconds,
                        'worker': event.worker,
                        'queue': event.queue,
                        'error_message': event.error_message,
                        'rss_mb_start': event.rss_mb_start,
                        'rss_mb_end': event.rss_mb_end,
                    }
                # Fallback: check via Celery AsyncResult (works for freshly dispatched tasks)
                from core.celery import app as celery_app
                result = celery_app.AsyncResult(task_id)
                return {
                    'action': 'task_status',
                    'source': 'async_result',
                    'task_id': task_id,
                    'status': result.status,
                    'ready': result.ready(),
                    'successful': result.successful() if result.ready() else None,
                    'result_preview': str(result.result)[:500] if result.ready() else None,
                    'note': 'CeleryTaskEvent not yet recorded — task may still be queued or starting',
                }

            if action == 'worker_health':
                from core.celery import app as celery_app
                inspector = celery_app.control.inspect(timeout=5)
                active = inspector.active() or {}
                stats = inspector.stats() or {}
                workers = []
                for worker_name, worker_stats in stats.items():
                    pool = worker_stats.get('pool', {})
                    workers.append({
                        'name': worker_name,
                        'active_tasks': len(active.get(worker_name, [])),
                        'concurrency': pool.get('max-concurrency', 'unknown'),
                        'pool': pool.get('implementation', 'unknown'),
                        'prefetch_count': worker_stats.get('prefetch_count', 0),
                    })
                return {'action': 'worker_health', 'workers': workers}

            if action == 'recent_failures':
                from core.models_celery_telemetry import CeleryTaskEvent
                qs = CeleryTaskEvent.objects.filter(status='FAILURE').order_by('-started_at')
                queue_filter = payload.get('queue')
                if queue_filter:
                    qs = qs.filter(queue=queue_filter)
                failures = qs[:limit]
                return {
                    'action': 'recent_failures',
                    'count': len(failures),
                    'failures': [{
                        'task_name': f.task_name,
                        'task_id': f.task_id,
                        'started_at': f.started_at.isoformat() if f.started_at else None,
                        'error_type': f.error_type,
                        'error_message': (f.error_message or '')[:300],
                        'queue': f.queue,
                        'worker': f.worker,
                        'duration_seconds': f.duration_seconds,
                    } for f in failures],
                }

            if action == 'queue_lengths':
                from core.celery import app as celery_app
                inspector = celery_app.control.inspect(timeout=5)
                active = inspector.active() or {}
                reserved = inspector.reserved() or {}
                queues = {}
                for worker_name in set(list(active) + list(reserved)):
                    for task in active.get(worker_name, []):
                        q = task.get('delivery_info', {}).get('routing_key', 'unknown')
                        queues.setdefault(q, {'active': 0, 'reserved': 0})
                        queues[q]['active'] += 1
                    for task in reserved.get(worker_name, []):
                        q = task.get('delivery_info', {}).get('routing_key', 'unknown')
                        queues.setdefault(q, {'active': 0, 'reserved': 0})
                        queues[q]['reserved'] += 1
                return {'action': 'queue_lengths', 'queues': queues}

            if action == 'trigger_task':
                task_name = payload.get('task_name', '').strip()
                if not task_name:
                    return {'error': 'Provide task_name to trigger'}

                # Whitelist of safe tasks the PA can trigger on demand
                ALLOWED_TASKS = {
                    'core.tasks.sync_congress_data',
                    'core.tasks.run_all_spiders',
                    'core.tasks.check_system_health',
                    'core.tasks.run_signal_aggregation',
                    'core.tasks.generate_self_blog_deliberation_task',
                    'core.tasks.backfill_spider_embeddings',
                    'core.tasks.check_content_diversity',
                    'core.tasks.run_body_system_check',
                }

                if task_name not in ALLOWED_TASKS:
                    return {
                        'error': f'Task not in allowlist: {task_name}',
                        'allowed_tasks': sorted(ALLOWED_TASKS),
                    }

                from core.celery import app as celery_app
                queue = payload.get('queue', '') or 'long_running'
                result = celery_app.send_task(task_name, queue=queue)
                task_id = str(result.id)

                # Create CeleryTaskEvent immediately so task_status doesn't
                # fall through to AsyncResult (which always returns PENDING)
                try:
                    from core.models_celery_telemetry import CeleryTaskEvent
                    CeleryTaskEvent.objects.create(
                        task_id=task_id,
                        task_name=task_name,
                        queue=queue,
                        status='QUEUED',
                    )
                except Exception:
                    pass  # non-critical — telemetry signal will create on worker pickup

                return {
                    'action': 'trigger_task',
                    'task_name': task_name,
                    'task_id': task_id,
                    'queue': queue,
                    'status': 'dispatched',
                }

            return {'error': f'Unknown cockpit_tool action: {action}'}

        except Exception as e:
            logger.error(f"[COCKPIT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1100: Narrative Tool — drift, shifts, evidence, alerts ─────────
    def _handle_narrative(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Narrative drift analysis: narratives, shifts, evidence, alerts."""
        action = payload.get('action', 'help')
        limit = min(int(payload.get('limit', 10)), 30)
        domain = payload.get('category') or payload.get('domain')  # accept both, model field is 'domain'

        try:
            if action == 'help':
                return {
                    'tool': 'narrative_tool',
                    'actions': [
                        'narratives — list tracked narratives',
                        'shifts — recent narrative shifts/drift detections',
                        'evidence — evidence items for a specific narrative',
                        'alerts — narrative alerts (Discord notifications)',
                    ],
                }

            from core.models_narrative_drift import (
                Narrative, NarrativeShift, NarrativeEvidence, NarrativeAlert,
            )

            if action == 'narratives':
                qs = Narrative.objects.all().order_by('-updated_at')
                if domain:
                    qs = qs.filter(domain=domain)
                narratives = qs[:limit]
                return {
                    'action': 'narratives',
                    'total': qs.count(),
                    'narratives': [{
                        'id': str(n.id),
                        'title': n.title,
                        'domain': n.domain,
                        'status': n.status,
                        'confidence': float(n.confidence) if n.confidence else None,
                        'evidence_count': NarrativeEvidence.objects.filter(narrative=n).count(),
                        'updated_at': n.updated_at.isoformat() if hasattr(n, 'updated_at') and n.updated_at else None,
                    } for n in narratives],
                }

            if action == 'shifts':
                qs = NarrativeShift.objects.select_related('old_narrative').order_by('-detected_at')
                if domain:
                    qs = qs.filter(domain=domain)
                shifts = qs[:limit]
                return {
                    'action': 'shifts',
                    'count': len(shifts),
                    'shifts': [{
                        'id': str(s.id),
                        'narrative': s.old_narrative.title if s.old_narrative else 'Unknown',
                        'domain': s.domain,
                        'shift_summary': (s.shift_summary or '')[:200],
                        'confidence': float(s.confidence) if s.confidence else None,
                        'importance': float(s.importance) if s.importance else None,
                        'trend_break_analysis': (s.trend_break_analysis or '')[:200],
                        'cultural_impact_analysis': (s.cultural_impact_analysis or '')[:200],
                        'detected_at': s.detected_at.isoformat() if s.detected_at else None,
                    } for s in shifts],
                }

            if action == 'evidence':
                narrative_id = payload.get('narrative_id', '')
                if not narrative_id:
                    return {'error': 'Provide narrative_id for evidence lookup'}
                evidence = NarrativeEvidence.objects.filter(
                    narrative_id=narrative_id
                ).order_by('-created_at')[:limit]
                return {
                    'action': 'evidence',
                    'narrative_id': narrative_id,
                    'count': len(evidence),
                    'evidence': [{
                        'id': str(e.id),
                        'source_title': e.source_title or '',
                        'source_url': e.source_url or '',
                        'source_type': e.source_type or '',
                        'sentiment': e.sentiment,
                        'strength': float(e.strength) if e.strength else None,
                        'excerpt': (e.excerpt or '')[:200],
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in evidence],
                }

            if action == 'alerts':
                alerts = NarrativeAlert.objects.order_by('-created_at')[:limit]
                return {
                    'action': 'alerts',
                    'count': len(alerts),
                    'alerts': [{
                        'id': str(a.id),
                        'title': a.title or '',
                        'alert_type': a.alert_type,
                        'summary': (a.summary or a.message or '')[:200],
                        'sent_to_discord': a.sent_to_discord,
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                    } for a in alerts],
                }

            return {'error': f'Unknown narrative_tool action: {action}'}

        except Exception as e:
            logger.error(f"[NARRATIVE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Proactive Tool ──────────────────────────────────────
    def _handle_proactive(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Proactive alerts, notifications, suggestions, automations."""
        action = payload.get('action', 'dashboard')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import (
                ProactiveAlert, ProactiveNotification, SmartSuggestion, AutomatedAction,
            )

            if action == 'alerts':
                alerts = ProactiveAlert.objects.filter(is_active=True).order_by('-last_triggered', '-created_at')[:limit]
                return {
                    'action': 'alerts',
                    'count': len(alerts),
                    'alerts': [{
                        'id': str(a.id),
                        'name': a.name,
                        'alert_type': a.alert_type,
                        'condition': a.condition,
                        'is_active': a.is_active,
                        'trigger_count': a.trigger_count,
                        'last_triggered': a.last_triggered.isoformat() if a.last_triggered else None,
                        'check_frequency': a.check_frequency,
                    } for a in alerts],
                }

            if action == 'notifications':
                qs = ProactiveNotification.objects.order_by('-created_at')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                notifs = qs[:limit]
                return {
                    'action': 'notifications',
                    'count': len(notifs),
                    'notifications': [{
                        'id': str(n.id),
                        'title': n.title,
                        'message': (n.message or '')[:200],
                        'notification_type': n.notification_type,
                        'priority': n.priority,
                        'is_read': n.is_read,
                        'delivery_status': n.delivery_status,
                        'created_at': n.created_at.isoformat() if n.created_at else None,
                    } for n in notifs],
                }

            if action == 'suggestions':
                qs = SmartSuggestion.objects.filter(status='pending').order_by('-confidence_score')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                suggestions = qs[:limit]
                return {
                    'action': 'suggestions',
                    'count': len(suggestions),
                    'suggestions': [{
                        'id': str(s.id),
                        'title': s.title,
                        'suggestion_type': s.suggestion_type,
                        'category': s.category,
                        'confidence_score': float(s.confidence_score) if s.confidence_score else None,
                        'estimated_revenue_impact': float(s.estimated_revenue_impact) if s.estimated_revenue_impact else None,
                        'effort_level': s.effort_level,
                        'status': s.status,
                    } for s in suggestions],
                }

            if action == 'automations':
                automations = AutomatedAction.objects.filter(is_active=True).order_by('-last_executed')[:limit]
                return {
                    'action': 'automations',
                    'count': len(automations),
                    'automations': [{
                        'id': str(a.id),
                        'name': a.name,
                        'action_type': a.action_type,
                        'trigger_type': a.trigger_type,
                        'is_active': a.is_active,
                        'total_executions': a.total_executions,
                        'successful_executions': a.successful_executions,
                        'last_executed': a.last_executed.isoformat() if a.last_executed else None,
                    } for a in automations],
                }

            if action == 'dashboard':
                unread = ProactiveNotification.objects.filter(is_read=False)
                if user_id:
                    unread = unread.filter(user_id=user_id)
                return {
                    'action': 'dashboard',
                    'unread_notifications': unread.count(),
                    'active_alerts': ProactiveAlert.objects.filter(is_active=True).count(),
                    'pending_suggestions': SmartSuggestion.objects.filter(status='pending').count(),
                    'active_automations': AutomatedAction.objects.filter(is_active=True).count(),
                }

            if action == 'mark_read':
                notif_id = payload.get('notification_id', '') or payload.get('id', '')
                if not notif_id:
                    return {'error': 'notification_id required for mark_read'}
                updated = ProactiveNotification.objects.filter(id=notif_id, is_read=False).update(is_read=True)
                return {'action': 'mark_read', 'notification_id': notif_id, 'updated': updated > 0}

            if action == 'bulk_ack':
                # Mark multiple notifications as read by filter
                priority = payload.get('priority', '')
                notification_type = payload.get('notification_type', '')
                max_items = min(int(payload.get('max_items', 50)), 200)
                qs = ProactiveNotification.objects.filter(is_read=False)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                if priority:
                    qs = qs.filter(priority=priority)
                if notification_type:
                    qs = qs.filter(notification_type=notification_type)
                # Order by oldest first
                ids_to_ack = list(qs.order_by('created_at').values_list('id', flat=True)[:max_items])
                updated = ProactiveNotification.objects.filter(id__in=ids_to_ack).update(is_read=True)
                return {
                    'action': 'bulk_ack',
                    'acknowledged': updated,
                    'filters': {'priority': priority or 'all', 'notification_type': notification_type or 'all'},
                }

            if action == 'dismiss':
                notif_id = payload.get('notification_id', '') or payload.get('id', '')
                if not notif_id:
                    return {'error': 'notification_id required for dismiss'}
                updated = ProactiveNotification.objects.filter(id=notif_id).update(
                    is_read=True, delivery_status='dismissed'
                )
                return {'action': 'dismiss', 'notification_id': notif_id, 'dismissed': updated > 0}

            return {'error': f'Unknown proactive_tool action: {action}. Valid: dashboard, alerts, notifications, suggestions, automations, mark_read, bulk_ack, dismiss'}

        except Exception as e:
            logger.error(f"[PROACTIVE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Distribution Tool ───────────────────────────────────
    def _handle_distribution(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Content distribution platforms, listings, revenue."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import DistributionPlatform, ContentDistribution
            from django.db.models import Sum, Count

            if action == 'platforms':
                platforms = DistributionPlatform.objects.filter(is_active=True).order_by('name')[:limit]
                return {
                    'action': 'platforms',
                    'count': len(platforms),
                    'platforms': [{
                        'id': str(p.id),
                        'name': p.name,
                        'platform_type': p.platform_type,
                        'commission_percent': float(p.commission_percent) if p.commission_percent else None,
                        'is_active': p.is_active,
                    } for p in platforms],
                }

            if action == 'listings':
                qs = ContentDistribution.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                listings = qs[:limit]
                return {
                    'action': 'listings',
                    'count': len(listings),
                    'listings': [{
                        'id': str(d.id),
                        'title': d.title or '',
                        'platform_account': str(d.platform_account) if d.platform_account else '',
                        'content_type': d.content_type,
                        'status': d.status,
                        'price': float(d.price) if d.price else None,
                        'revenue': float(d.revenue) if d.revenue else 0,
                        'sales': d.sales or 0,
                        'views': d.views or 0,
                        'listed_at': d.listed_at.isoformat() if d.listed_at else None,
                    } for d in listings],
                }

            if action == 'revenue':
                qs = ContentDistribution.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                revenue_by_platform = list(
                    qs.values('platform_account')
                    .annotate(total_revenue=Sum('revenue'), total_sales=Sum('sales'))
                    .order_by('-total_revenue')
                )
                return {
                    'action': 'revenue',
                    'platforms': [{
                        'platform': str(r['platform_account'] or 'Unknown'),
                        'total_revenue': float(r['total_revenue'] or 0),
                        'total_sales': r['total_sales'] or 0,
                    } for r in revenue_by_platform],
                }

            if action == 'stats':
                qs = ContentDistribution.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                agg = qs.aggregate(
                    total_revenue=Sum('revenue'),
                    total_sales=Sum('sales'),
                    total_views=Sum('views'),
                )
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                return {
                    'action': 'stats',
                    'total_listings': qs.count(),
                    'total_revenue': float(agg['total_revenue'] or 0),
                    'total_sales': agg['total_sales'] or 0,
                    'total_views': agg['total_views'] or 0,
                    'by_status': status_counts,
                    'active_platforms': DistributionPlatform.objects.filter(is_active=True).count(),
                }

            return {'error': f'Unknown distribution_tool action: {action}'}

        except Exception as e:
            logger.error(f"[DISTRIBUTION] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Calendar Tool ───────────────────────────────────────
    def _handle_calendar(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Content channels and episodes."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_autonomous_studio import ContentChannel, ChannelEpisode
            from django.db.models import Count
            from django.utils import timezone

            if action == 'channels':
                qs = ContentChannel.objects.order_by('-total_episodes_created')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                channels = qs[:limit]
                return {
                    'action': 'channels',
                    'count': len(channels),
                    'channels': [{
                        'id': str(c.id),
                        'name': c.name,
                        'topic_domain': (c.topic_domain or '')[:100],
                        'content_frequency': c.content_frequency,
                        'platform': c.platform,
                        'status': getattr(c, 'status', 'active'),
                        'total_episodes_created': c.total_episodes_created or 0,
                        'next_content_due': c.next_content_due.isoformat() if getattr(c, 'next_content_due', None) else None,
                    } for c in channels],
                }

            if action == 'episodes':
                qs = ChannelEpisode.objects.select_related('channel').order_by('-created_at')
                channel_id = payload.get('channel_id')
                if channel_id:
                    qs = qs.filter(channel_id=channel_id)
                episodes = qs[:limit]
                return {
                    'action': 'episodes',
                    'count': len(episodes),
                    'episodes': [{
                        'id': str(e.id),
                        'title': e.title or '',
                        'topic': e.topic or '',
                        'channel': e.channel.name if e.channel else '',
                        'intent_type': getattr(e, 'intent_type', ''),
                        'performance_score': float(e.performance_score) if e.performance_score else None,
                        'created_at': e.created_at.isoformat() if hasattr(e, 'created_at') and e.created_at else None,
                    } for e in episodes],
                }

            if action == 'upcoming':
                now = timezone.now()
                upcoming = ContentChannel.objects.filter(
                    next_content_due__gt=now
                ).order_by('next_content_due')[:limit]
                return {
                    'action': 'upcoming',
                    'count': len(upcoming),
                    'upcoming': [{
                        'id': str(c.id),
                        'name': c.name,
                        'platform': c.platform,
                        'next_content_due': c.next_content_due.isoformat() if c.next_content_due else None,
                    } for c in upcoming],
                }

            if action == 'stats':
                channels = ContentChannel.objects.all()
                if user_id:
                    channels = channels.filter(user_id=user_id)
                episodes = ChannelEpisode.objects.all()
                platform_counts = dict(channels.values_list('platform').annotate(c=Count('id')).values_list('platform', 'c'))
                return {
                    'action': 'stats',
                    'total_channels': channels.count(),
                    'total_episodes': episodes.count(),
                    'by_platform': platform_counts,
                }

            return {'error': f'Unknown calendar_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CALENDAR] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Experiment Tool ─────────────────────────────────────
    def _handle_experiment(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """A/B tests and experiment results."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_unified_system import ABTest, ABTestVariant
            from django.db.models import Count

            if action == 'tests':
                qs = ABTest.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                tests = qs[:limit]
                return {
                    'action': 'tests',
                    'count': len(tests),
                    'tests': [{
                        'id': str(t.id),
                        'name': t.name,
                        'test_type': t.test_type,
                        'status': t.status,
                        'primary_metric': t.primary_metric,
                        'start_date': t.start_date.isoformat() if t.start_date else None,
                        'statistical_significance': float(t.statistical_significance) if t.statistical_significance else None,
                    } for t in tests],
                }

            if action == 'results':
                test_id = payload.get('test_id', '')
                if not test_id:
                    return {'error': 'Provide test_id for results'}
                test = ABTest.objects.filter(id=test_id).first()
                if not test:
                    return {'error': f'ABTest {test_id} not found'}
                variants = ABTestVariant.objects.filter(test=test).order_by('created_at')
                return {
                    'action': 'results',
                    'test': {
                        'id': str(test.id),
                        'name': test.name,
                        'test_type': test.test_type,
                        'status': test.status,
                        'hypothesis': test.hypothesis or '',
                        'primary_metric': test.primary_metric,
                        'conclusion': test.conclusion or '',
                        'statistical_significance': float(test.statistical_significance) if test.statistical_significance else None,
                    },
                    'variants': [{
                        'id': str(v.id),
                        'name': v.name,
                        'is_control': v.is_control,
                        'traffic_percentage': float(v.traffic_percentage) if v.traffic_percentage else None,
                        'config': v.config,
                    } for v in variants],
                }

            if action == 'stats':
                qs = ABTest.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                type_counts = dict(qs.values_list('test_type').annotate(c=Count('id')).values_list('test_type', 'c'))
                return {
                    'action': 'stats',
                    'total_tests': qs.count(),
                    'by_status': status_counts,
                    'by_type': type_counts,
                }

            return {'error': f'Unknown experiment_tool action: {action}'}

        except Exception as e:
            logger.error(f"[EXPERIMENT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Podcast Tool ────────────────────────────────────────
    def _handle_podcast(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Podcast shows, episodes, scripts."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_podcast_studio import PodcastShow, PodcastEpisode
            from django.db.models import Sum, Count

            if action == 'shows':
                qs = PodcastShow.objects.order_by('-episode_count')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                shows = qs[:limit]
                return {
                    'action': 'shows',
                    'count': len(shows),
                    'shows': [{
                        'id': str(s.id),
                        'name': s.name,
                        'format': s.format,
                        'participant_count': s.participant_count or 0,
                        'episode_count': s.episode_count or 0,
                        'total_listens': s.total_listens or 0,
                    } for s in shows],
                }

            if action == 'episodes':
                qs = PodcastEpisode.objects.select_related('show').order_by('-created_at')
                show_id = payload.get('show_id')
                if show_id:
                    qs = qs.filter(show_id=show_id)
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                episodes = qs[:limit]
                return {
                    'action': 'episodes',
                    'count': len(episodes),
                    'episodes': [{
                        'id': str(e.id),
                        'title': e.title or '',
                        'topic': e.topic or '',
                        'show': e.show.name if e.show else '',
                        'status': e.status,
                        'progress_percent': e.progress_percent or 0,
                        'audio_duration_seconds': e.audio_duration_seconds,
                        'listen_count': e.listen_count or 0,
                        'created_at': e.created_at.isoformat() if e.created_at else None,
                    } for e in episodes],
                }

            if action == 'scripts':
                episode_id = payload.get('episode_id', '')
                if not episode_id:
                    return {'error': 'Provide episode_id for scripts'}
                ep = PodcastEpisode.objects.filter(id=episode_id).first()
                if not ep:
                    return {'error': f'PodcastEpisode {episode_id} not found'}
                return {
                    'action': 'scripts',
                    'episode_id': str(ep.id),
                    'title': ep.title or '',
                    'script': (ep.script or '')[:3000],
                }

            if action == 'stats':
                shows = PodcastShow.objects.all()
                episodes = PodcastEpisode.objects.all()
                if user_id:
                    shows = shows.filter(user_id=user_id)
                    episodes = episodes.filter(user_id=user_id)
                agg = episodes.aggregate(total_listens=Sum('listen_count'))
                status_counts = dict(episodes.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                return {
                    'action': 'stats',
                    'total_shows': shows.count(),
                    'total_episodes': episodes.count(),
                    'total_listens': agg['total_listens'] or 0,
                    'by_status': status_counts,
                }

            return {'error': f'Unknown podcast_tool action: {action}'}

        except Exception as e:
            logger.error(f"[PODCAST] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Campaign Tool ───────────────────────────────────────
    def _handle_campaign(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Campaigns and deliverables."""
        action = payload.get('action', 'list')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_campaign import Campaign, CampaignDeliverable
            from django.db.models import Count

            if action == 'list':
                qs = Campaign.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                if user_id:
                    qs = qs.filter(user_id=user_id)
                campaigns = qs[:limit]
                return {
                    'action': 'list',
                    'count': len(campaigns),
                    'campaigns': [{
                        'id': str(c.id),
                        'name': c.name,
                        'status': c.status,
                        'budget_tier': c.budget_tier,
                        'client_name': c.client_name or '',
                        'product_name': c.product_name or '',
                        'progress_percent': c.progress_percent or 0,
                        'created_at': c.created_at.isoformat() if c.created_at else None,
                    } for c in campaigns],
                }

            if action == 'detail':
                campaign_id = payload.get('campaign_id', '')
                if not campaign_id:
                    return {'error': 'Provide campaign_id for detail'}
                campaign = Campaign.objects.filter(id=campaign_id).first()
                if not campaign:
                    return {'error': f'Campaign {campaign_id} not found'}
                deliverables = CampaignDeliverable.objects.filter(campaign=campaign).order_by('created_at')
                return {
                    'action': 'detail',
                    'campaign': {
                        'id': str(campaign.id),
                        'name': campaign.name,
                        'status': campaign.status,
                        'budget_tier': campaign.budget_tier,
                        'client_name': campaign.client_name or '',
                        'product_name': campaign.product_name or '',
                        'progress_percent': campaign.progress_percent or 0,
                    },
                    'deliverables': [{
                        'id': str(d.id),
                        'name': d.name,
                        'deliverable_type': d.deliverable_type,
                        'status': d.status,
                        'platform': d.platform or '',
                    } for d in deliverables],
                }

            if action == 'stats':
                qs = Campaign.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                tier_counts = dict(qs.values_list('budget_tier').annotate(c=Count('id')).values_list('budget_tier', 'c'))
                return {
                    'action': 'stats',
                    'total_campaigns': qs.count(),
                    'by_status': status_counts,
                    'by_budget_tier': tier_counts,
                }

            return {'error': f'Unknown campaign_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CAMPAIGN] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Audit Tool ──────────────────────────────────────────
    def _handle_audit(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Audit findings, wiring defects, citation violations."""
        action = payload.get('action', 'findings')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            if action == 'findings' or action == 'p0_summary':
                from core.models_audit_tracking import AuditFinding
                qs = AuditFinding.objects.order_by('-created_at')
                if action == 'p0_summary':
                    qs = qs.filter(priority__in=['P0', 'P1']).exclude(status='resolved')
                else:
                    priority_filter = payload.get('priority')
                    if priority_filter:
                        qs = qs.filter(priority=priority_filter)
                    status_filter = payload.get('status')
                    if status_filter:
                        qs = qs.filter(status=status_filter)
                findings = qs[:limit]
                return {
                    'action': action,
                    'count': len(findings),
                    'findings': [{
                        'id': str(f.id),
                        'finding_id': f.finding_id or '',
                        'title': f.title,
                        'priority': f.priority,
                        'category': f.category,
                        'status': f.status,
                        'impact': (f.impact or '')[:200],
                        'assigned_agent': f.assigned_agent or '',
                    } for f in findings],
                }

            if action == 'wiring_defects':
                from core.models_orchestration import WiringDefect
                qs = WiringDefect.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter == 'resolved':
                    qs = qs.filter(is_resolved=True)
                elif status_filter == 'unresolved':
                    qs = qs.filter(is_resolved=False)
                defects = qs[:limit]
                return {
                    'action': 'wiring_defects',
                    'count': len(defects),
                    'defects': [{
                        'id': str(d.id),
                        'defect_type': d.defect_type,
                        'agent_name': d.agent_name or '',
                        'object_type': d.object_type or '',
                        'is_resolved': d.is_resolved,
                        'created_at': d.created_at.isoformat() if d.created_at else None,
                    } for d in defects],
                }

            if action == 'citations':
                from core.models_orchestration import CitationViolation
                qs = CitationViolation.objects.order_by('-created_at')
                defects = qs[:limit]
                return {
                    'action': 'citations',
                    'count': len(defects),
                    'violations': [{
                        'id': str(v.id),
                        'violation_type': v.violation_type,
                        'agent_name': v.agent_name or '',
                        'provided_sources': v.provided_sources or 0,
                        'required_sources': v.required_sources or 0,
                        'was_blocked': v.was_blocked,
                        'is_resolved': v.is_resolved,
                        'created_at': v.created_at.isoformat() if v.created_at else None,
                    } for v in defects],
                }

            return {'error': f'Unknown audit_tool action: {action}'}

        except Exception as e:
            logger.error(f"[AUDIT] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: ConceptForge Tool ───────────────────────────────────
    def _handle_conceptforge(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """ConceptForge pipeline runs, stages, artifacts."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_conceptforge import ConceptForgeRun, ConceptForgeStageRun, ConceptForgeArtifact
            from django.db.models import Count, Avg

            if action == 'runs':
                qs = ConceptForgeRun.objects.order_by('-created_at')
                status_filter = payload.get('status')
                if status_filter:
                    qs = qs.filter(status=status_filter)
                runs = qs[:limit]
                return {
                    'action': 'runs',
                    'count': len(runs),
                    'runs': [{
                        'id': str(r.id),
                        'source_type': r.source_type,
                        'source_title': (r.source_title or '')[:100],
                        'domain': r.domain or '',
                        'status': r.status,
                        'quality_score': float(r.quality_score) if r.quality_score else None,
                        'duration_ms': r.duration_ms,
                        'created_at': r.created_at.isoformat() if r.created_at else None,
                    } for r in runs],
                }

            if action == 'run_detail':
                run_id = payload.get('run_id', '')
                if not run_id:
                    return {'error': 'Provide run_id for run_detail'}
                run = ConceptForgeRun.objects.filter(id=run_id).first()
                if not run:
                    return {'error': f'ConceptForgeRun {run_id} not found'}
                stages = ConceptForgeStageRun.objects.filter(run=run).order_by('stage_order')
                artifacts = ConceptForgeArtifact.objects.filter(run=run).order_by('created_at')
                return {
                    'action': 'run_detail',
                    'run': {
                        'id': str(run.id),
                        'source_type': run.source_type,
                        'source_title': run.source_title or '',
                        'domain': run.domain or '',
                        'status': run.status,
                        'quality_score': float(run.quality_score) if run.quality_score else None,
                        'duration_ms': run.duration_ms,
                    },
                    'stages': [{
                        'stage_name': s.stage_name,
                        'agent_used': s.agent_used or '',
                        'status': s.status,
                        'duration_ms': s.duration_ms,
                    } for s in stages],
                    'artifacts': [{
                        'id': str(a.id),
                        'name': a.name,
                        'kind': a.kind,
                        'is_primary': a.is_primary,
                    } for a in artifacts],
                }

            if action == 'stats':
                qs = ConceptForgeRun.objects.all()
                agg = qs.aggregate(avg_quality=Avg('quality_score'))
                status_counts = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
                source_counts = dict(qs.values_list('source_type').annotate(c=Count('id')).values_list('source_type', 'c'))
                return {
                    'action': 'stats',
                    'total_runs': qs.count(),
                    'avg_quality_score': float(agg['avg_quality'] or 0),
                    'by_status': status_counts,
                    'by_source_type': source_counts,
                }

            return {'error': f'Unknown conceptforge_tool action: {action}'}

        except Exception as e:
            logger.error(f"[CONCEPTFORGE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Profile Tool ────────────────────────────────────────
    def _handle_profile(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """Extended user profile and skills."""
        action = payload.get('action', 'profile')

        try:
            if action == 'profile':
                from core.models import ExtendedUserProfile
                profile = ExtendedUserProfile.objects.filter(user_id=user_id).first() if user_id else None
                if not profile:
                    return {'action': 'profile', 'profile': None, 'message': 'No extended profile found'}
                return {
                    'action': 'profile',
                    'profile': {
                        'full_name': profile.full_name or '',
                        'location': profile.location or '',
                        'timezone': profile.timezone or '',
                        'current_title': profile.current_title or '',
                        'years_experience': profile.years_experience,
                        'experience_level': profile.experience_level or '',
                        'skills': profile.skills or [],
                        'certifications': profile.certifications or [],
                        'remote_preference': profile.remote_preference or '',
                        'profile_completeness': profile.profile_completeness or 0,
                    },
                }

            if action == 'skills':
                from core.models_user_learning import UserSkill
                qs = UserSkill.objects.order_by('-confidence', '-last_demonstrated')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                skills = qs[:50]
                return {
                    'action': 'skills',
                    'count': len(skills),
                    'skills': [{
                        'id': str(s.id),
                        'skill_name': s.skill_name,
                        'category': s.category or '',
                        'proficiency_level': s.proficiency_level or '',
                        'evidence_count': s.evidence_count or 0,
                        'confidence': float(s.confidence) if s.confidence else None,
                        'last_demonstrated': s.last_demonstrated.isoformat() if s.last_demonstrated else None,
                    } for s in skills],
                }

            if action == 'learning_summary':
                from core.models_user_learning import UserSkill
                from django.db.models import Count, Avg
                qs = UserSkill.objects.all()
                if user_id:
                    qs = qs.filter(user_id=user_id)
                agg = qs.aggregate(avg_proficiency=Avg('confidence'))
                category_counts = dict(qs.values_list('category').annotate(c=Count('id')).values_list('category', 'c'))
                return {
                    'action': 'learning_summary',
                    'total_skills': qs.count(),
                    'avg_confidence': float(agg['avg_proficiency'] or 0),
                    'by_category': category_counts,
                }

            # Gap 9: User preferences CRUD
            if action == 'preferences':
                from core.models import EnhancedUserProfile
                from django.contrib.auth import get_user_model
                User = get_user_model()

                user = User.objects.filter(id=user_id).first() if user_id else None
                if not user:
                    return {'action': 'preferences', 'error': 'No user context'}

                enhanced, _ = EnhancedUserProfile.objects.get_or_create(user=user)

                return {
                    'action': 'preferences',
                    'preferences': {
                        'long_term_goals': enhanced.long_term_goals or [],
                        'current_projects': enhanced.current_projects or [],
                        'quarterly_objectives': enhanced.quarterly_objectives or {},
                        'learning_style': enhanced.learning_style or '',
                        'communication_style': enhanced.communication_style or '',
                        'decision_framework': enhanced.decision_framework or '',
                        'current_learning_goals': enhanced.current_learning_goals or [],
                        'personal_values': enhanced.personal_values or [],
                        'delegation_preferences': enhanced.delegation_preferences or {},
                        'work_schedule': enhanced.work_schedule or {},
                        'time_zone': enhanced.time_zone or '',
                        'privacy_level': enhanced.privacy_level or '',
                    },
                }

            if action == 'update_preferences':
                from core.models import EnhancedUserProfile
                from django.contrib.auth import get_user_model
                User = get_user_model()

                user = User.objects.filter(id=user_id).first() if user_id else None
                if not user:
                    return {'action': 'update_preferences', 'error': 'No user context'}

                enhanced, _ = EnhancedUserProfile.objects.get_or_create(user=user)

                updates = payload.get('updates', {})
                ALLOWED_FIELDS = {
                    'long_term_goals', 'current_projects', 'quarterly_objectives',
                    'learning_style', 'communication_style', 'decision_framework',
                    'current_learning_goals', 'personal_values', 'delegation_preferences',
                    'work_schedule', 'time_zone', 'privacy_level',
                }

                # Support both single field+value and bulk updates dict
                if not updates and payload.get('field') and payload.get('value') is not None:
                    updates = {payload['field']: payload['value']}

                applied = {}
                for field, value in updates.items():
                    if field in ALLOWED_FIELDS:
                        setattr(enhanced, field, value)
                        applied[field] = value

                if applied:
                    enhanced.save()

                return {
                    'action': 'update_preferences',
                    'updated_fields': list(applied.keys()),
                    'count': len(applied),
                    'success': len(applied) > 0,
                }

            # Gap 10: Scoped preference views by desk/module
            if action == 'desk_preferences':
                from core.models import EnhancedUserProfile, ExtendedUserProfile
                from django.contrib.auth import get_user_model
                User = get_user_model()

                desk = payload.get('desk', 'general').strip().lower()
                user = User.objects.filter(id=user_id).first() if user_id else None
                if not user:
                    return {'action': 'desk_preferences', 'error': 'No user context'}

                enhanced = EnhancedUserProfile.objects.filter(user=user).first()
                extended = ExtendedUserProfile.objects.filter(user=user).first()

                base = {
                    'desk': desk,
                    'communication_style': getattr(enhanced, 'communication_style', '') if enhanced else '',
                    'long_term_goals': getattr(enhanced, 'long_term_goals', []) if enhanced else [],
                }

                DESK_PROJECTIONS = {
                    'sports': {
                        'fields': ['decision_framework', 'current_learning_goals'],
                        'context': 'Sports betting preferences and risk tolerance',
                    },
                    'stocks': {
                        'fields': ['decision_framework', 'current_learning_goals', 'current_projects'],
                        'context': 'Investment preferences and market interests',
                    },
                    'content': {
                        'fields': ['learning_style', 'communication_style', 'current_projects'],
                        'context': 'Content tone, style, and topic preferences',
                    },
                    'general': {
                        'fields': ['long_term_goals', 'work_schedule', 'current_learning_goals', 'delegation_preferences'],
                        'context': 'General platform preferences',
                    },
                }

                projection = DESK_PROJECTIONS.get(desk, DESK_PROJECTIONS['general'])
                for field in projection['fields']:
                    val = getattr(enhanced, field, None) if enhanced else None
                    if val is None and extended:
                        val = getattr(extended, field, None)
                    base[field] = val or ([] if field in ('current_learning_goals', 'current_projects', 'long_term_goals', 'personal_values') else ({} if field in ('work_schedule', 'delegation_preferences', 'quarterly_objectives') else ''))

                base['context'] = projection['context']
                base['available_desks'] = list(DESK_PROJECTIONS.keys())

                return {'action': 'desk_preferences', **base}

            return {'error': f'Unknown profile_tool action: {action}. Valid: profile, skills, learning_summary, preferences, update_preferences, desk_preferences'}

        except Exception as e:
            logger.error(f"[PROFILE] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: Self-Awareness Tool ─────────────────────────────────
    def _handle_self_awareness(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """System self-awareness metrics, reports, evolution."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 10)), 30)

        try:
            from self_awareness.models import SystemMetrics, SelfAnalysisReport, SystemEvolution

            if action == 'metrics':
                latest = SystemMetrics.objects.order_by('-timestamp').first()
                if not latest:
                    return {'action': 'metrics', 'metrics': None, 'message': 'No metrics recorded yet'}
                return {
                    'action': 'metrics',
                    'metrics': {
                        'timestamp': latest.timestamp.isoformat() if latest.timestamp else None,
                        'cpu_usage': float(latest.cpu_usage) if latest.cpu_usage else None,
                        'memory_usage': float(latest.memory_usage) if latest.memory_usage else None,
                        'active_agents': latest.active_agents,
                        'pending_tasks': latest.pending_tasks,
                        'error_count': latest.error_count,
                        'self_analysis_score': float(latest.self_analysis_score) if latest.self_analysis_score else None,
                    },
                }

            if action == 'reports':
                reports = SelfAnalysisReport.objects.order_by('-timestamp')[:limit]
                return {
                    'action': 'reports',
                    'count': len(reports),
                    'reports': [{
                        'id': str(r.id) if hasattr(r, 'id') else str(r.timestamp),
                        'analysis_type': r.analysis_type,
                        'score': float(r.score) if r.score else None,
                        'critical_issues': r.critical_issues,
                        'warning_issues': r.warning_issues,
                        'confidence': float(r.confidence) if r.confidence else None,
                        'timestamp': r.timestamp.isoformat() if r.timestamp else None,
                    } for r in reports],
                }

            if action == 'evolution':
                evolutions = SystemEvolution.objects.order_by('-timestamp')[:limit]
                return {
                    'action': 'evolution',
                    'count': len(evolutions),
                    'evolutions': [{
                        'id': str(e.id) if hasattr(e, 'id') else str(e.timestamp),
                        'evolution_type': e.evolution_type,
                        'status': e.status,
                        'title': e.title or '',
                        'confidence_score': float(e.confidence_score) if e.confidence_score else None,
                        'priority': e.priority or '',
                        'timestamp': e.timestamp.isoformat() if e.timestamp else None,
                    } for e in evolutions],
                }

            if action == 'stats':
                reports = SelfAnalysisReport.objects.all()
                evolutions = SystemEvolution.objects.all()
                latest_metrics = SystemMetrics.objects.order_by('-timestamp').first()
                return {
                    'action': 'stats',
                    'total_reports': reports.count(),
                    'total_evolutions': evolutions.count(),
                    'latest_self_analysis_score': float(latest_metrics.self_analysis_score) if latest_metrics and latest_metrics.self_analysis_score else None,
                }

            if action == 'collect':
                # Gather live metrics from existing models and write a SystemMetrics snapshot
                from django.utils import timezone as tz
                from datetime import timedelta
                now = tz.now()
                one_hour = now - timedelta(hours=1)

                from core.models import AgentExecution
                from core.models_celery_telemetry import CeleryTaskEvent

                active_agents = AgentExecution.objects.filter(
                    status='running', created_at__gte=one_hour
                ).count()
                completed_1h = CeleryTaskEvent.objects.filter(
                    status='SUCCESS', finished_at__gte=one_hour
                ).count()
                failed_1h = CeleryTaskEvent.objects.filter(
                    status='FAILURE', finished_at__gte=one_hour
                ).count()
                pending = CeleryTaskEvent.objects.filter(
                    status='STARTED', finished_at__isnull=True, started_at__gte=one_hour
                ).count()

                snapshot = SystemMetrics.objects.create(
                    cpu_usage=0.0,       # not measurable on Railway
                    memory_usage=0.0,    # not measurable on Railway
                    disk_usage=0.0,      # not measurable on Railway
                    active_agents=active_agents,
                    pending_tasks=pending,
                    completed_tasks=completed_1h,
                    error_count=failed_1h,
                )
                return {
                    'action': 'collect',
                    'snapshot_id': str(snapshot.pk),
                    'timestamp': snapshot.timestamp.isoformat(),
                    'active_agents': active_agents,
                    'pending_tasks': pending,
                    'completed_tasks_1h': completed_1h,
                    'errors_1h': failed_1h,
                    'message': 'Metrics snapshot recorded',
                }

            return {'error': f'Unknown self_awareness_tool action: {action}. Valid: metrics, reports, evolution, stats, collect'}

        except Exception as e:
            logger.error(f"[SELF_AWARENESS] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Session 1035-W2: ATS Tool ────────────────────────────────────────────
    def _handle_ats(self, tool_name: str, payload: Dict[str, Any], user_id: Optional[int], trace_id: str) -> Dict[str, Any]:
        """ATS keyword mappings, resume optimizations, templates."""
        action = payload.get('action', 'stats')
        limit = min(int(payload.get('limit', 20)), 50)

        try:
            from core.models_ats_optimization import ATSKeywordMapping, ResumeOptimizationLog, PersonaResumeTemplate
            from django.db.models import Sum, Avg, Count

            if action == 'keywords':
                qs = ATSKeywordMapping.objects.order_by('-job_frequency')
                category_filter = payload.get('category')
                if category_filter:
                    qs = qs.filter(category=category_filter)
                keywords = qs[:limit]
                return {
                    'action': 'keywords',
                    'count': len(keywords),
                    'keywords': [{
                        'id': str(k.id),
                        'canonical': k.canonical,
                        'category': k.category or '',
                        'variations': (k.variations or [])[:3],
                        'resume_frequency': float(k.resume_frequency) if k.resume_frequency else None,
                        'job_frequency': float(k.job_frequency) if k.job_frequency else None,
                        'interview_correlation': float(k.interview_correlation) if k.interview_correlation else None,
                    } for k in keywords],
                }

            if action == 'optimizations':
                qs = ResumeOptimizationLog.objects.order_by('-created_at')
                if user_id:
                    qs = qs.filter(user_id=user_id)
                opts = qs[:limit]
                return {
                    'action': 'optimizations',
                    'count': len(opts),
                    'optimizations': [{
                        'id': str(o.id),
                        'job_title_target': o.job_title_target or '',
                        'industry': o.industry or '',
                        'initial_ats_score': float(o.initial_ats_score) if o.initial_ats_score else None,
                        'final_ats_score': float(o.final_ats_score) if o.final_ats_score else None,
                        'current_stage': o.current_stage or '',
                        'revenue_cents': o.revenue_cents or 0,
                    } for o in opts],
                }

            if action == 'templates':
                templates = PersonaResumeTemplate.objects.filter(is_active=True).order_by('name')[:limit]
                return {
                    'action': 'templates',
                    'count': len(templates),
                    'templates': [{
                        'id': str(t.id),
                        'name': t.name,
                        'industry': t.industry or '',
                        'experience_level': t.experience_level or '',
                        'template_type': t.template_type or '',
                        'price_cents': t.price_cents or 0,
                        'avg_ats_score_improvement': float(t.avg_ats_score_improvement) if t.avg_ats_score_improvement else None,
                    } for t in templates],
                }

            if action == 'stats':
                keywords = ATSKeywordMapping.objects.all()
                opts = ResumeOptimizationLog.objects.all()
                if user_id:
                    opts = opts.filter(user_id=user_id)
                agg = opts.aggregate(
                    total_revenue=Sum('revenue_cents'),
                    avg_init=Avg('initial_ats_score'),
                    avg_final=Avg('final_ats_score'),
                )
                avg_init = agg['avg_init']
                avg_final = agg['avg_final']
                avg_improvement = float((avg_final or 0) - (avg_init or 0)) if avg_init and avg_final else None
                return {
                    'action': 'stats',
                    'total_keywords': keywords.count(),
                    'total_optimizations': opts.count(),
                    'avg_score_improvement': avg_improvement,
                    'total_revenue_cents': agg['total_revenue'] or 0,
                    'active_templates': PersonaResumeTemplate.objects.filter(is_active=True).count(),
                }

            return {'error': f'Unknown ats_tool action: {action}'}

        except Exception as e:
            logger.error(f"[ATS] {action} error: {e}", exc_info=True)
            return {'error': str(e)}

    # ── Remote Code Worker ──────────────────────────────────────────────────

