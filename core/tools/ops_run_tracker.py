"""
OpsRunTracker — context manager for structured ops run observability.

Usage:
    with OpsRunTracker('Ops Control Loop', 'ops_loop', 'beat') as tracker:
        tracker.step('deploy_verify', lambda: run_smoke_test(...))
        tracker.info('extra context', {'key': 'value'})
"""
import logging
import traceback

from django.utils import timezone

logger = logging.getLogger(__name__)


class OpsRunTracker:
    """Wraps a multi-step operation, creating OpsRun + OpsRunEvent records."""

    def __init__(self, title: str, run_type: str, triggered_by: str):
        self.title = title
        self.run_type = run_type
        self.triggered_by = triggered_by
        self.run = None
        self._event_count = 0
        self._fail_count = 0

    def __enter__(self):
        from core.models_ops_runs import OpsRun
        self.run = OpsRun.objects.create(
            title=self.title,
            run_type=self.run_type,
            triggered_by=self.triggered_by,
            status='running',
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.run is None:
            return False

        if exc_type is not None:
            self.run.status = 'failed'
            self._emit('step_fail', f'Unhandled: {exc_type.__name__}', {
                'error': str(exc_val)[:500],
            })
        elif self._fail_count > 0:
            self.run.status = 'partial' if self._event_count > self._fail_count else 'failed'
        else:
            self.run.status = 'passed'

        self.run.finished_at = timezone.now()
        self.run.event_count = self._event_count
        self.run.fail_count = self._fail_count
        self.run.save(update_fields=['status', 'finished_at', 'event_count', 'fail_count', 'summary'])
        return False  # don't suppress exceptions

    def step(self, label: str, fn):
        """Run fn, emitting step_start / step_pass or step_fail events. Returns fn result."""
        self._emit('step_start', label)
        try:
            result = fn()
            self._emit('step_pass', label, {'result': _safe_summary(result)})
            return result
        except Exception as e:
            self._fail_count += 1
            self._emit('step_fail', label, {
                'error': str(e)[:500],
                'traceback': traceback.format_exc()[-500:],
            })
            return {'ok': False, 'error': str(e)[:200]}

    def info(self, label: str, detail=None):
        """Emit an informational event."""
        self._emit('info', label, detail or {})

    def set_summary(self, summary: dict):
        """Set the final summary payload on the OpsRun."""
        if self.run:
            self.run.summary = summary

    @property
    def ops_run_id(self):
        return str(self.run.id) if self.run else None

    def _emit(self, event_type: str, label: str, detail=None):
        from core.models_ops_runs import OpsRunEvent
        if self.run is None:
            return
        self._event_count += 1
        try:
            OpsRunEvent.objects.create(
                run=self.run,
                event_type=event_type,
                label=label,
                detail=detail or {},
            )
        except Exception as e:
            logger.warning("[OpsRunTracker] Failed to emit event: %s", e)


def _safe_summary(result):
    """Truncate large result dicts for event detail storage."""
    if isinstance(result, dict):
        return {k: str(v)[:200] for k, v in list(result.items())[:20]}
    if isinstance(result, (str, int, float, bool)):
        return result
    return str(result)[:500]
