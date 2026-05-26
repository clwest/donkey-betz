"""
FinalAppliedOverrides — per-cycle PolicyArbitrator snapshot history.

Session 1163 B-style follow-on to the Disclosure L §14 mechanism drift:
the original `record_overrides_snapshot` writer used
`SystemConfiguration.objects.update_or_create(key='policy_arbitrator_snapshot', ...)`,
which overwrote a single row each cycle and made time-travel queries
impossible. This model is the append-only per-cycle history that
Disclosure L §5 Component 4 originally described.

Each autopilot cycle's arbitrator emits one row. The
`get_latest_snapshot(at=...)` method on PolicyArbitrator queries this
table to answer either "what is configured right now?" (no `at` arg) or
"what was configured at time T?" (with `at`).

Retention: pruned to 90 days by the
`purge_finaloverrides_older_than_90d` periodic Celery task.
See narrative `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` §6.4
for the operator-facing description; Disclosure L §14.7 records the
B-style shipped state.
"""

import uuid

from django.db import models


class FinalAppliedOverrides(models.Model):
    """
    One snapshot per autopilot cycle of the active
    `autopilot_tuning:` knob overrides + their owning policy +
    priority. The arbitrator writes this row LAST in every cycle so
    it captures the post-conflict-resolution state.

    Time-travel debugging:
        FinalAppliedOverrides.objects.filter(
            cycle_ts__lte=t,
        ).order_by('-cycle_ts').first()

    Latest snapshot:
        FinalAppliedOverrides.objects.latest('cycle_ts')
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    cycle_id = models.UUIDField(
        unique=True,
        help_text=(
            "UUID identifying the autopilot cycle that produced this "
            "snapshot. Useful for joining against AutopilotAction "
            "records emitted during the same cycle."
        ),
    )

    cycle_ts = models.DateTimeField(
        db_index=True,
        help_text=(
            "Wall-clock time the arbitrator captured the snapshot, "
            "passed in by the cycle wrapper via `now` (typically "
            "django.utils.timezone.now()). Indexed for time-travel "
            "queries via `.filter(cycle_ts__lte=t).order_by('-cycle_ts').first()`."
        ),
    )

    knob_count = models.IntegerField(
        help_text=(
            "Number of knobs in the applied_values dict at the time "
            "of capture. Stored explicitly to avoid a JSONB parse on "
            "every summary query."
        ),
    )

    applied_values = models.JSONField(
        default=dict,
        help_text=(
            "Knob name → {value, owner, priority} dict. The owner "
            "field identifies the policy that wrote the knob; "
            "priority is the merge precedence the arbitrator used "
            "to resolve any same-cycle conflicts."
        ),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=(
            "Django-managed row creation timestamp. Usually within "
            "milliseconds of cycle_ts; significant divergence between "
            "the two is itself a debugging signal."
        ),
    )

    class Meta:
        db_table = 'core_final_applied_overrides'
        verbose_name = 'Final Applied Overrides Snapshot'
        verbose_name_plural = 'Final Applied Overrides Snapshots'
        indexes = [
            models.Index(fields=['-cycle_ts'], name='fao_cycle_ts_desc'),
        ]
        ordering = ['-cycle_ts']

    def __str__(self) -> str:
        return (
            f'FinalAppliedOverrides<{self.cycle_id}> '
            f'@{self.cycle_ts.isoformat() if self.cycle_ts else "<no-ts>"} '
            f'({self.knob_count} knobs)'
        )
