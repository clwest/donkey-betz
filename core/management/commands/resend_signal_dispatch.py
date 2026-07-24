"""Manual retry lever for the SignalDispatch pipeline (S2933 A3 v1).

Rigby SIGN Q3 F-BLOCKING constraint: the dispatch pipeline must not
strand clusters after transient failure. This command reinstates the
bounded retry path — pick a specific dispatch by id, or retry any
`failed` dispatch for a (cluster, rule_key) pair. Creates a NEW
SignalDispatch row (audit history preserved).

Examples:
    python manage.py resend_signal_dispatch --dispatch-id <uuid>
    python manage.py resend_signal_dispatch --cluster-id <uuid> --rule-key trend_emergence__trend_analysis
    python manage.py resend_signal_dispatch --list-failed
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Re-fire a signal-dispatch that previously failed or was rejected."

    def add_arguments(self, parser):
        parser.add_argument('--dispatch-id', help='UUID of a prior SignalDispatch row to re-run')
        parser.add_argument('--cluster-id', help='SignalCluster UUID (paired with --rule-key)')
        parser.add_argument('--rule-key', help='Rule key from SIGNAL_DISPATCH_RULES (paired with --cluster-id)')
        parser.add_argument(
            '--list-failed', action='store_true',
            help='List failed/rejected dispatches (last 20) and exit',
        )
        parser.add_argument(
            '--sync', action='store_true',
            help='Execute inline instead of enqueuing to Celery',
        )

    def handle(self, *args, **opts):
        from core.models_signal_dispatch import SignalDispatch
        from core.models_signal_intelligence import SignalCluster
        from core.services.signal_dispatch_service import (
            SignalDispatchService, get_rule,
        )

        if opts['list_failed']:
            rows = (
                SignalDispatch.objects
                .filter(outcome__in=('failed', 'rejected_agent_missing', 'rejected_unknown_rule'))
                .order_by('-dispatched_at')[:20]
            )
            for r in rows:
                self.stdout.write(
                    f"{r.dispatched_at.isoformat()}  {r.id}  {r.rule_key}  "
                    f"cluster={r.signal_cluster_id}  outcome={r.outcome}  err={r.error_summary[:80]}"
                )
            return

        dispatch_id = opts.get('dispatch_id')
        cluster_id = opts.get('cluster_id')
        rule_key = opts.get('rule_key')

        service = SignalDispatchService()

        if dispatch_id:
            src = SignalDispatch.objects.select_related('signal_cluster').get(id=dispatch_id)
            rule_key = src.rule_key
            cluster = src.signal_cluster
        elif cluster_id and rule_key:
            cluster = SignalCluster.objects.get(id=cluster_id)
        else:
            raise CommandError(
                'Provide either --dispatch-id or both --cluster-id and --rule-key '
                '(or --list-failed).'
            )

        rule = get_rule(rule_key)
        if rule is None:
            raise CommandError(f"Rule '{rule_key}' not in SIGNAL_DISPATCH_RULES")

        new_dispatch = SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='queued',
            input_payload=service._build_payload(rule, cluster),
            scan_run_id='',
        )
        self.stdout.write(f"Created retry dispatch {new_dispatch.id}")

        if opts['sync']:
            result = service.execute_dispatch(str(new_dispatch.id))
            self.stdout.write(f"Sync result: {result}")
        else:
            from core.tasks import dispatch_agent_for_signal_cluster
            dispatch_agent_for_signal_cluster.delay(str(new_dispatch.id))
            self.stdout.write("Enqueued to Celery (long_running queue)")
