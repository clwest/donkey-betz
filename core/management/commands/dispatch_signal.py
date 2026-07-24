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

Examples:
    python manage.py dispatch_signal --cluster-id <uuid>
    python manage.py dispatch_signal --cluster-id <uuid> --rule-key opportunity_window__opportunity_scoring
    python manage.py dispatch_signal --cluster-id <uuid> --force --sync
"""
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

MANUAL_SCAN_RUN_ID = 'manual'
DEFAULT_GUARD_WINDOW_MINUTES = 5


class Command(BaseCommand):
    help = (
        "Synthesize a SignalDispatch for a specific cluster on-demand. "
        "Companion to resend_signal_dispatch; enables rule verification "
        "without waiting for natural cluster promotion."
    )

    def add_arguments(self, parser):
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
            default=DEFAULT_GUARD_WINDOW_MINUTES,
            help=(
                f'Idempotent guard window (default {DEFAULT_GUARD_WINDOW_MINUTES}min). '
                'A prior non-failed dispatch for (cluster, rule_key) within this '
                'window blocks re-dispatch unless --force.'
            ),
        )

    def handle(self, *args, **opts):
        from core.models_signal_dispatch import SignalDispatch
        from core.models_signal_intelligence import SignalCluster
        from core.services.signal_dispatch_service import (
            SIGNAL_DISPATCH_RULES,
            SignalDispatchService,
            get_rule,
        )

        cluster_id = opts['cluster_id']
        rule_key = opts.get('rule_key')
        force = opts['force']
        sync = opts['sync']
        guard_minutes = opts['guard_window_minutes']

        try:
            cluster = SignalCluster.objects.get(id=cluster_id)
        except SignalCluster.DoesNotExist as e:
            raise CommandError(f"SignalCluster {cluster_id} not found") from e

        if rule_key:
            rule = get_rule(rule_key)
            if rule is None:
                raise CommandError(f"Rule '{rule_key}' not in SIGNAL_DISPATCH_RULES")
            if rule.pattern_type != cluster.pattern_type:
                raise CommandError(
                    f"Rule '{rule_key}' targets pattern_type='{rule.pattern_type}' "
                    f"but cluster has pattern_type='{cluster.pattern_type}'"
                )
        else:
            matches = [r for r in SIGNAL_DISPATCH_RULES if r.pattern_type == cluster.pattern_type]
            if not matches:
                raise CommandError(
                    f"No rule in SIGNAL_DISPATCH_RULES matches pattern_type="
                    f"'{cluster.pattern_type}'. Pass --rule-key explicitly or add a rule."
                )
            if len(matches) > 1:
                keys = ', '.join(r.key for r in matches)
                raise CommandError(
                    f"Multiple rules match pattern_type='{cluster.pattern_type}': "
                    f"{keys}. Pass --rule-key explicitly."
                )
            rule = matches[0]

        if not force:
            since = timezone.now() - timedelta(minutes=guard_minutes)
            blocker = SignalDispatch.objects.filter(
                signal_cluster=cluster,
                rule_key=rule.key,
                dispatched_at__gte=since,
            ).exclude(outcome='failed').first()
            if blocker is not None:
                raise CommandError(
                    f"Idempotent guard: dispatch {blocker.id} for "
                    f"(cluster={cluster_id}, rule={rule.key}) exists within "
                    f"{guard_minutes}min window (outcome={blocker.outcome}). "
                    f"Pass --force to override."
                )

        service = SignalDispatchService()
        new_dispatch = SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='queued',
            input_payload=service._build_payload(rule, cluster),
            scan_run_id=MANUAL_SCAN_RUN_ID,
        )
        self.stdout.write(
            f"Created manual dispatch {new_dispatch.id} "
            f"(cluster={cluster_id}, rule={rule.key}, agent={rule.agent_name})"
        )

        if sync:
            result = service.execute_dispatch(str(new_dispatch.id))
            self.stdout.write(f"Sync result: {result}")
        else:
            from core.tasks import dispatch_agent_for_signal_cluster
            dispatch_agent_for_signal_cluster.delay(str(new_dispatch.id))
            self.stdout.write("Enqueued to Celery (long_running queue)")
