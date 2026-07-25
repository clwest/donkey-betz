"""On-demand signal-dispatch harness — Session 2934 A7.

Companion to ``resend_signal_dispatch`` (S2933 retry lever). Where
``resend_signal_dispatch`` re-runs a specific prior dispatch, this
command **synthesizes a new dispatch for any cluster on-demand** so
new rules can be exercised without waiting for natural cluster
promotion (S2934 open observed 0.58% active-cluster rate — natural
fires are slow).

Rigby SIGN safety conditions (S2934 open):
    * ``--cluster-id`` required — no batch mode
    * Idempotent guard — a matching in-flight/succeeded dispatch
      within the guard window blocks re-dispatch unless ``--force``
    * Manual dispatches labeled ``scan_run_id='manual'`` so they
      never contaminate reactive-pipeline analytics
    * No background scanning — this fires exactly one cluster

S2947 A8: shared logic lives in
``SignalDispatchService.create_manual_dispatch``; this CLI is a thin
wrapper so it stays behavior-identical to the manual-dispatch button
in the Workspace Signal Dispatches tab.

Examples:
    python manage.py dispatch_signal --cluster-id <uuid>
    python manage.py dispatch_signal --cluster-id <uuid> --rule-key opportunity_window__opportunity_scoring
    python manage.py dispatch_signal --cluster-id <uuid> --force --sync
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Synthesize a SignalDispatch for a specific cluster on-demand. "
        "Companion to resend_signal_dispatch; enables rule verification "
        "without waiting for natural cluster promotion."
    )

    def add_arguments(self, parser):
        from core.services.signal_dispatch_service import (
            DEFAULT_MANUAL_GUARD_WINDOW_MINUTES,
        )

        parser.add_argument(
            '--cluster-id',
            required=True,
            help='SignalCluster UUID to dispatch for (required).',
        )
        parser.add_argument(
            '--rule-key',
            help=(
                'Rule key from SIGNAL_DISPATCH_RULES. If omitted, the '
                'command picks the rule matching cluster.pattern_type. '
                'Errors if 0 or 2+ rules match.'
            ),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=(
                'Bypass the idempotent guard. Without --force, a matching '
                'in-flight/succeeded dispatch within the guard window blocks '
                're-dispatch.'
            ),
        )
        parser.add_argument(
            '--sync',
            action='store_true',
            help='Execute inline instead of enqueuing to Celery.',
        )
        parser.add_argument(
            '--guard-window-minutes',
            type=int,
            default=DEFAULT_MANUAL_GUARD_WINDOW_MINUTES,
            help=(
                f'Idempotent guard window (default {DEFAULT_MANUAL_GUARD_WINDOW_MINUTES}min). '
                'A prior non-failed dispatch for (cluster, rule_key) within this '
                'window blocks re-dispatch unless --force.'
            ),
        )

    def handle(self, *args, **opts):
        from core.services.signal_dispatch_service import SignalDispatchService

        service = SignalDispatchService()
        result = service.create_manual_dispatch(
            cluster_id=opts['cluster_id'],
            rule_key=opts.get('rule_key'),
            force=opts['force'],
            guard_window_minutes=opts['guard_window_minutes'],
            sync=opts['sync'],
        )

        if not result.get('success'):
            raise CommandError(result.get('error') or 'manual dispatch failed')

        self.stdout.write(
            f"Created manual dispatch {result['dispatch_id']} "
            f"(cluster={result['cluster_id']}, rule={result['rule_key']}, "
            f"agent={result['agent_name']})"
        )
        if 'sync_result' in result:
            self.stdout.write(f"Sync result: {result['sync_result']}")
        else:
            self.stdout.write("Enqueued to Celery (long_running queue)")
