"""
ToolDispatcher CodeJobHandlersMixin — extracted handler methods.
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




class CodeJobHandlersMixin:
    """Mixin providing handler methods for ToolDispatcher."""

    def _handle_code_job(self, tool_name, payload, user_id, trace_id):
        """Submit and manage remote code jobs. Actions: submit, status, logs, cancel, list, list_repos, add_repo"""
        action = payload.get('action', 'status')
        logger.info(f"[{trace_id}] code_job_tool action={action!r} keys={list(payload.keys())}")
        if action == 'submit':
            return self._code_job_submit(payload, user_id, trace_id)
        elif action == 'status':
            return self._code_job_status(payload, user_id)
        elif action == 'logs':
            return self._code_job_logs(payload, user_id)
        elif action == 'cancel':
            return self._code_job_cancel(payload, user_id)
        elif action == 'list':
            return self._code_job_list(payload, user_id)
        elif action == 'list_repos':
            return self._code_job_list_repos(payload, user_id)
        elif action == 'add_repo':
            return self._code_job_add_repo(payload, user_id)
        return {'error': f'Unknown code_job_tool action: {action}'}

    def _code_job_submit(self, payload, user_id, trace_id):
        from core.models import ExecutionRun, Repo
        repo_slug = payload.get('repo_slug', '')
        task_prompt = payload.get('task_prompt', '')
        if not repo_slug:
            return {'error': 'repo_slug is required'}
        if not task_prompt:
            return {'error': 'task_prompt is required'}
        repo = None
        for r in Repo.objects.filter(is_active=True):
            if r.get_repo_slug() == repo_slug or r.name == repo_slug:
                repo = r
                break
        if not repo:
            return {'error': f'Repo "{repo_slug}" not in allowlist or disabled'}
        mode = payload.get('mode', 'dry_run')
        base_branch = payload.get('base_branch', repo.default_base_branch or 'main')
        conversation_id = payload.get('conversation_id', '')
        max_runtime = min(int(payload.get('max_runtime_seconds', repo.max_runtime_seconds)), 1800)
        plan_json = {
            'version': 'code_worker_v1', 'mode': mode,
            'title': task_prompt[:200], 'task_prompt': task_prompt,
            'acceptance_criteria': payload.get('acceptance_criteria', []),
            'test_command': payload.get('test_command', '') or repo.test_command,
            'lint_command': payload.get('lint_command', '') or repo.lint_command,
            'install_command': repo.install_command,
            'max_runtime_seconds': max_runtime,
            'steps': [
                {'id': s} for s in ['clone', 'implement', 'test', 'lint', 'push', 'pr']
            ],
        }
        user = None
        if user_id:
            from django.contrib.auth import get_user_model
            user = get_user_model().objects.filter(id=user_id).first()
        run = ExecutionRun.objects.create(
            repo=repo, repo_url=repo.repo_url, base_branch=base_branch,
            plan_json=plan_json, plan_summary=task_prompt[:500],
            steps_total=6, conversation_id=conversation_id,
            created_by=user, status='queued',
        )
        run.generate_working_branch()
        try:
            from core.tasks import execute_code_job
            task = execute_code_job.apply_async(args=[str(run.id)], queue='code_jobs')
            run.celery_task_id = task.id
            run.save(update_fields=['celery_task_id'])
        except Exception as e:
            logger.warning('Could not dispatch code job: %s', e)
        job_id = str(run.id)
        return {
            'submitted': True, 'job_id': job_id, 'status': 'queued',
            'mode': mode, 'working_branch': run.working_branch,
            'repo': repo_slug, 'task_prompt': task_prompt[:200],
            'next_commands': [
                f'code_job_tool(action="status", job_id="{job_id}")',
                f'code_job_tool(action="logs", job_id="{job_id}", after_sequence=0)',
                f'code_job_tool(action="cancel", job_id="{job_id}")',
            ],
        }

    def _code_job_status(self, payload, user_id):
        from core.models import ExecutionRun
        job_id = payload.get('job_id') or payload.get('id', '')
        if not job_id:
            # Session 1077: Smart inference — GPT often drops job_id.
            # Fall back to the most recent job for this user.
            if user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.filter(id=user_id).first()
                if user:
                    latest = ExecutionRun.objects.filter(created_by=user).order_by('-created_at').first()
                    if latest:
                        job_id = str(latest.id)
            if not job_id:
                return {'error': 'job_id is required'}
        try:
            run = ExecutionRun.objects.select_related('repo').get(id=job_id)
        except ExecutionRun.DoesNotExist:
            return {'error': f'Job {job_id} not found'}
        elapsed = None
        if run.started_at:
            from django.utils import timezone
            end = run.completed_at or timezone.now()
            elapsed = round((end - run.started_at).total_seconds(), 1)
        return {
            'job_id': str(run.id), 'status': run.status,
            'progress': f'{run.progress * 100:.0f}%',
            'current_step': run.current_step,
            'steps': f'{run.steps_completed}/{run.steps_total}',
            'branch': run.working_branch,
            'pr_url': run.pr_url or None, 'pr_number': run.pr_number,
            'error': run.error_message or None,
            'failure_reason': run.failure_reason_code or None,
            'elapsed_seconds': elapsed,
            'task_prompt': run.plan_summary[:200] if run.plan_summary else '',
        }

    def _code_job_logs(self, payload, user_id):
        from core.models import ExecutionRun, CodeJobLog
        job_id = payload.get('job_id') or payload.get('id', '')
        if not job_id:
            return {'error': 'job_id is required'}
        try:
            run = ExecutionRun.objects.get(id=job_id)
        except ExecutionRun.DoesNotExist:
            return {'error': f'Job {job_id} not found'}
        after_seq = int(payload.get('after_sequence', 0))
        limit = min(int(payload.get('limit', 30)), 100)
        logs = CodeJobLog.objects.filter(
            run=run, sequence__gt=after_seq,
        ).order_by('sequence')[:limit]
        return {
            'job_id': str(run.id), 'status': run.status,
            'log_count': CodeJobLog.objects.filter(run=run).count(),
            'logs': [f'[{log.step}] {log.message}' for log in logs],
        }

    def _code_job_cancel(self, payload, user_id):
        from core.models import ExecutionRun
        job_id = payload.get('job_id') or payload.get('id', '')
        if not job_id:
            return {'error': 'job_id is required'}
        try:
            run = ExecutionRun.objects.get(id=job_id)
        except ExecutionRun.DoesNotExist:
            return {'error': f'Job {job_id} not found'}
        if run.is_terminal:
            return {'error': f'Job already terminal: {run.status}'}
        if run.celery_task_id:
            try:
                from core.celery import app
                app.control.revoke(run.celery_task_id, terminate=True)
            except Exception:
                pass
        run.cancel()
        return {'cancelled': True, 'job_id': str(run.id), 'status': 'canceled'}

    def _code_job_list(self, payload, user_id):
        from core.models import ExecutionRun
        qs = ExecutionRun.objects.filter(
            plan_json__version='code_worker_v1',
        ).select_related('repo').order_by('-created_at')
        status = payload.get('status') or payload.get('status_filter')
        if status and status not in ('all', '*'):
            qs = qs.filter(status=status)
        limit = min(int(payload.get('limit', 10)), 50)
        runs = qs[:limit]
        return {
            'total': qs.count(),
            'jobs': [{
                'job_id': str(r.id), 'status': r.status,
                'task': r.plan_summary[:80] if r.plan_summary else '',
                'branch': r.working_branch, 'pr_url': r.pr_url or None,
                'created': r.created_at.strftime('%Y-%m-%d %H:%M') if r.created_at else '',
            } for r in runs],
        }

    def _code_job_list_repos(self, payload, user_id):
        from core.models import Repo
        repos = Repo.objects.all().order_by('name')
        return {
            'repos': [{
                'id': str(r.id),
                'name': r.name,
                'slug': r.get_repo_slug(),
                'repo_url': r.repo_url,
                'default_branch': r.default_base_branch,
                'is_active': r.is_active,
                'test_command': r.test_command or '(auto-detect)',
                'lint_command': r.lint_command or '(auto-detect)',
                'max_runtime_seconds': r.max_runtime_seconds,
            } for r in repos],
            'total': repos.count(),
        }

    def _code_job_add_repo(self, payload, user_id):
        from core.models import Repo
        repo_url = payload.get('repo_url', '').strip()
        name = payload.get('name', '').strip()
        if not repo_url:
            return {'error': 'repo_url is required (e.g. https://github.com/owner/repo)'}
        if not repo_url.startswith('https://github.com/'):
            return {'error': 'Only GitHub repos are supported (must start with https://github.com/)'}
        # Auto-derive name from URL if not provided
        if not name:
            name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        # Check if already exists
        existing = Repo.objects.filter(repo_url=repo_url).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                existing.save(update_fields=['is_active'])
                return {
                    'reactivated': True,
                    'id': str(existing.id),
                    'name': existing.name,
                    'slug': existing.get_repo_slug(),
                }
            return {'error': f'Repo already exists and is active: {existing.name} ({existing.get_repo_slug()})'}
        repo = Repo.objects.create(
            name=name,
            repo_url=repo_url.rstrip('/'),
            default_base_branch=payload.get('default_branch', 'main'),
            test_command=payload.get('test_command', ''),
            lint_command=payload.get('lint_command', ''),
            max_runtime_seconds=int(payload.get('max_runtime_seconds', 600)),
            is_active=True,
        )
        return {
            'created': True,
            'id': str(repo.id),
            'name': repo.name,
            'slug': repo.get_repo_slug(),
            'repo_url': repo.repo_url,
            'default_branch': repo.default_base_branch,
            'is_active': True,
        }

    def _handle_claude_code(self, tool_name, payload, user_id, trace_id):
        """Spawn autonomous Claude Code engineering session. Reads files, writes code, creates PRs."""
        # Accept multiple param names — LLM may use different keys
        task_description = (
            payload.get('task')
            or payload.get('task_description')
            or payload.get('description')
            or payload.get('prompt')
            or payload.get('message')
            or ''
        )
        if not task_description:
            # Log what we actually received for debugging
            import logging
            logging.getLogger(__name__).warning(
                f"[claude_code_tool] No task found in payload keys: {list(payload.keys())} | trace={trace_id}"
            )
            return {'error': f'task description is required. Received keys: {list(payload.keys())}'}

        # Auto-inject conversation_id from the PA context if not explicitly set
        conversation_id = payload.get('conversation_id')
        if not conversation_id and hasattr(self, '_conversation_id'):
            conversation_id = self._conversation_id

        from core.tasks import claude_code_engineer_task
        task = claude_code_engineer_task.delay(
            task_description=task_description,
            conversation_id=conversation_id,
            requested_by='rigby',
        )

        return {
            'status': 'dispatched',
            'task_id': str(task.id),
            'message': f'Claude Code engineering session started. Task ID: {task.id}. Results will be posted to the conversation when complete.',
        }


