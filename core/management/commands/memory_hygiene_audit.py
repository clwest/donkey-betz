"""
memory_hygiene_audit — surface stale + cap-drift + conflict candidates for
``UserMemoryContext`` rows; supersede (never delete) with ``--apply``.

S2987 (spec ba968ac1 PR2 D4) — companion to the ``remember_tool.save``
reliability work shipped in PR1. This command exists to reconcile the
1803-vs-200 cap drift discovered at S2986 post-merge smoke: some
``UserMemoryContext`` writers bypass the ``MEMORY_MAX_ITEMS`` cap check
that the ``remember_tool`` handler enforces, so heavy users accumulate
rows unbounded. The PR2 fix at ``memory_promotion_service.py`` closes
the ongoing bypass; this command reconciles the historical drift.

Usage::

    # Report only (default) — no writes.
    python manage.py memory_hygiene_audit

    # Scope to a single user.
    python manage.py memory_hygiene_audit --user chris

    # Actually supersede the flagged rows (never DELETE).
    python manage.py memory_hygiene_audit --apply

Surfaces three finding classes:

* **Stale candidates**: is_active=True AND (last_accessed IS NULL OR
  last_accessed < now-90d) AND importance < 5. Old rows the model never
  went back to; low importance. Prunable via supersede.
* **Cap-drift candidates**: for each user, active_count > MEMORY_MAX_ITEMS.
  Reports the breakdown by source so operators can see which writer is
  the accumulation source. Auto-generated rows (``source='auto_promotion'``)
  are the typical suspect after S2987 PR2 shipped the promotion-cap fix.
* **Conflict candidates**: same user + same memory_type + >2 active rows
  with identical tags. Likely dedupe drift.

The ``--apply`` flag supersedes rows by marking them inactive
(``is_active=False``, ``superseded_at=now``, ``superseded_by=None``).
Delete is NEVER used — the audit trail is preserved.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count

from core.models import UserMemoryContext

User = get_user_model()

DEFAULT_STALE_DAYS = 90
DEFAULT_STALE_IMPORTANCE_LT = 5


class Command(BaseCommand):
    help = 'Surface stale + cap-drift + conflict UserMemoryContext candidates; supersede with --apply.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, default=None,
                            help='Scope to a single user by username.')
        parser.add_argument('--apply', action='store_true',
                            help='Supersede stale candidates. Never DELETE.')
        parser.add_argument('--stale-days', type=int, default=DEFAULT_STALE_DAYS,
                            help=f'Row is stale if last_accessed < now-N days (default: {DEFAULT_STALE_DAYS}).')
        parser.add_argument('--stale-importance-lt', type=int,
                            default=DEFAULT_STALE_IMPORTANCE_LT,
                            help=f'Only stale rows with importance < N (default: {DEFAULT_STALE_IMPORTANCE_LT}).')
        parser.add_argument('--max-items', type=int, default=None,
                            help='Override MEMORY_MAX_ITEMS for cap-drift check. Default reads env.')

    def handle(self, *args, **options):
        import os

        username = options.get('user')
        apply = options.get('apply', False)
        stale_days = options.get('stale_days', DEFAULT_STALE_DAYS)
        stale_imp_lt = options.get('stale_importance_lt', DEFAULT_STALE_IMPORTANCE_LT)
        max_items_override = options.get('max_items')
        max_items = (
            max_items_override
            if max_items_override is not None
            else int(os.environ.get('MEMORY_MAX_ITEMS', '200'))
        )

        mode = 'APPLY (supersede writes ON)' if apply else 'DRY-RUN (report only)'
        self.stdout.write(f'memory_hygiene_audit — {mode}')
        self.stdout.write(f'  stale threshold: last_accessed < now-{stale_days}d AND importance < {stale_imp_lt}')
        self.stdout.write(f'  cap threshold: active_count > {max_items}')
        self.stdout.write('')

        user_scope = None
        if username:
            try:
                user_scope = User.objects.get(username=username)
                self.stdout.write(f'  scope: user={username} (id={user_scope.id})')
            except User.DoesNotExist:
                self.stderr.write(f'user not found: {username}')
                return
        self.stdout.write('')

        stale = self._find_stale(user_scope, stale_days, stale_imp_lt)
        cap_drift = self._find_cap_drift(user_scope, max_items)
        conflicts = self._find_conflicts(user_scope)

        self._report_stale(stale)
        self._report_cap_drift(cap_drift, max_items)
        self._report_conflicts(conflicts)

        if apply:
            self._apply_supersede(stale)
        else:
            total_would_supersede = len(stale)
            self.stdout.write('')
            self.stdout.write(f'DRY-RUN: {total_would_supersede} rows would be superseded by --apply.')
            self.stdout.write('  cap-drift + conflict rows are NEVER auto-superseded — inspect manually.')

    def _find_stale(self, user_scope, stale_days: int, stale_imp_lt: int):
        cutoff = timezone.now() - timedelta(days=stale_days)
        qs = UserMemoryContext.objects.filter(
            is_active=True,
            importance__lt=stale_imp_lt,
        )
        # NULL last_accessed means never touched → definitely stale if old enough.
        from django.db.models import Q
        qs = qs.filter(Q(last_accessed__isnull=True) | Q(last_accessed__lt=cutoff))
        # But only consider rows old enough to have plausibly been touched.
        qs = qs.filter(created_at__lt=cutoff)
        if user_scope is not None:
            qs = qs.filter(user=user_scope)
        return list(qs.order_by('user__username', 'created_at'))

    def _find_cap_drift(self, user_scope, max_items: int):
        qs = UserMemoryContext.objects.filter(is_active=True)
        if user_scope is not None:
            qs = qs.filter(user=user_scope)
        by_user = (
            qs.values('user__id', 'user__username')
            .annotate(active_count=Count('id'))
            .filter(active_count__gt=max_items)
            .order_by('-active_count')
        )
        out = []
        for row in by_user:
            source_breakdown = dict(
                UserMemoryContext.objects
                .filter(user_id=row['user__id'], is_active=True)
                .values_list('source')
                .annotate(count=Count('id'))
                .values_list('source', 'count')
            )
            out.append({
                'user_id': row['user__id'],
                'username': row['user__username'],
                'active_count': row['active_count'],
                'source_breakdown': source_breakdown,
            })
        return out

    def _find_conflicts(self, user_scope):
        qs = UserMemoryContext.objects.filter(is_active=True)
        if user_scope is not None:
            qs = qs.filter(user=user_scope)
        # Group by (user, memory_type). Within each group, if a tag repeats
        # across >2 active rows, flag as a conflict candidate.
        conflicts = []
        buckets = defaultdict(list)
        for row in qs.only('id', 'user_id', 'memory_type', 'tags').iterator():
            buckets[(row.user_id, row.memory_type)].append(row)
        for (user_id, memory_type), rows in buckets.items():
            tag_counter = Counter()
            for r in rows:
                for tag in (r.tags or []):
                    tag_counter[tag] += 1
            for tag, count in tag_counter.items():
                if count > 2:
                    conflicts.append({
                        'user_id': user_id,
                        'memory_type': memory_type,
                        'tag': tag,
                        'active_count_with_tag': count,
                    })
        return conflicts

    def _report_stale(self, stale):
        self.stdout.write(self.style.NOTICE(f'STALE ({len(stale)} candidates):'))
        if not stale:
            self.stdout.write('  (none)')
        else:
            for row in stale[:20]:
                self.stdout.write(
                    f"  id={row.id} user={row.user.username} type={row.memory_type} "
                    f"imp={row.importance} last_accessed={row.last_accessed or 'NEVER'} "
                    f"content={row.content[:60]!r}"
                )
            if len(stale) > 20:
                self.stdout.write(f'  ... {len(stale) - 20} more (first 20 shown)')
        self.stdout.write('')

    def _report_cap_drift(self, cap_drift, max_items: int):
        self.stdout.write(self.style.NOTICE(
            f'CAP-DRIFT ({len(cap_drift)} users over {max_items} active rows):'
        ))
        if not cap_drift:
            self.stdout.write('  (none)')
        else:
            for row in cap_drift:
                self.stdout.write(
                    f"  user={row['username']} (id={row['user_id']}) "
                    f"active={row['active_count']}"
                )
                for source, count in sorted(
                    row['source_breakdown'].items(), key=lambda x: -x[1]
                ):
                    self.stdout.write(f"    {source}: {count}")
        self.stdout.write('')

    def _report_conflicts(self, conflicts):
        self.stdout.write(self.style.NOTICE(f'CONFLICTS ({len(conflicts)} tag-clusters):'))
        if not conflicts:
            self.stdout.write('  (none)')
        else:
            for row in conflicts[:20]:
                self.stdout.write(
                    f"  user_id={row['user_id']} type={row['memory_type']} "
                    f"tag={row['tag']!r} rows_with_tag={row['active_count_with_tag']}"
                )
            if len(conflicts) > 20:
                self.stdout.write(f'  ... {len(conflicts) - 20} more (first 20 shown)')
        self.stdout.write('')

    def _apply_supersede(self, stale):
        if not stale:
            self.stdout.write(self.style.SUCCESS('APPLY: nothing stale to supersede.'))
            return
        now = timezone.now()
        ids = [row.id for row in stale]
        # Bulk update — never DELETE.
        updated = UserMemoryContext.objects.filter(id__in=ids).update(
            is_active=False,
            superseded_at=now,
        )
        self.stdout.write(self.style.SUCCESS(
            f'APPLY: superseded {updated} stale rows (is_active=False, superseded_at=now, no delete).'
        ))
