"""
cost_thresholds — S2744 ops surface for §17 Cost Protection thresholds
and enforce mode.

Closes the observation-period gate loop Chris established at S2735
(cost_protection_enforce_mode = 'monitor' → 'freeze' after observation
period + explicit approval). Provides a direct ops surface so operators
can view + set + unset thresholds and enforce mode without ORM
inspection.

Substrate reuse:
- Reads via ``cost_threshold_monitor.read_thresholds_snapshot()`` (public
  helper shipped S2743) and ``read_enforce_mode()`` (S2735 P1).
- Writes via ``SystemConfiguration.set_config()`` classmethod (already
  used by monitor_cost_thresholds callers).
- Unsets via ``SystemConfiguration.objects.filter(...).delete()`` for
  clean default restoration (no is_active=False tombstoning).

Usage examples::

    # Show current configuration (default when no flag provided):
    python manage.py cost_thresholds
    python manage.py cost_thresholds --show

    # Set a threshold (WINDOW ∈ {hour,day,month}; VALUE in USD):
    python manage.py cost_thresholds --set month 500
    python manage.py cost_thresholds --set day 100.50
    python manage.py cost_thresholds --set hour 10

    # Unset a threshold (removes SystemConfiguration row):
    python manage.py cost_thresholds --unset month

    # Set enforce mode (MODE ∈ {monitor,freeze}):
    python manage.py cost_thresholds --set-mode monitor
    python manage.py cost_thresholds --set-mode freeze

    # Unset enforce mode (removes row → reverts to default 'monitor'):
    python manage.py cost_thresholds --unset-mode

Mode meanings:
- ``monitor`` (default): threshold breaches dispatch HAI; governance
  NOT flipped. This is the S2735 P1 gate discipline default.
- ``freeze``: same as monitor at HEAD — enforcement flip is deferred
  per S2735 discipline. The S2739 P2+ ``would_freeze`` shadow log fires
  when a breach occurs, providing counterfactual observation data for
  future Chris D-verdict on Cat 1 enforcement flip readiness.

Exit codes:
- 0 — success (show, set, unset succeeded)
- 1 — validation error (invalid value, invalid window, invalid mode)
- >1 — Django/DB error (let underlying exception propagate)

Flags are mutually exclusive per invocation. Chain ops via multiple
invocations if needed.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand, CommandError

# Fixed vocabulary — keep in sync with cost_threshold_monitor.
_WINDOWS = ('hour', 'day', 'month')
_MODES = ('monitor', 'freeze')

_CONFIG_KEY_BY_WINDOW = {
    'hour': 'cost_threshold_hour_usd',
    'day': 'cost_threshold_day_usd',
    'month': 'cost_threshold_month_usd',
}
_MODE_KEY = 'cost_protection_enforce_mode'


class Command(BaseCommand):
    help = (
        'View, set, and unset §17 Cost Protection thresholds and '
        'enforce mode. Ops surface for the S2735 P1 observation-period '
        'gate discipline. See file docstring for usage examples.'
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--show',
            action='store_true',
            help='Show current thresholds + enforce mode (default when no flag)',
        )
        group.add_argument(
            '--set',
            nargs=2,
            metavar=('WINDOW', 'VALUE'),
            help=(
                'Set threshold for WINDOW ∈ {hour,day,month} to VALUE '
                '(USD, Decimal, must be > 0)'
            ),
        )
        group.add_argument(
            '--unset',
            metavar='WINDOW',
            help=(
                'Unset threshold for WINDOW ∈ {hour,day,month} '
                '(deletes SystemConfiguration row; reverts to default)'
            ),
        )
        group.add_argument(
            '--set-mode',
            metavar='MODE',
            help='Set enforce mode to MODE ∈ {monitor,freeze}',
        )
        group.add_argument(
            '--unset-mode',
            action='store_true',
            help=(
                'Unset enforce mode (deletes SystemConfiguration row; '
                "reverts to default 'monitor')"
            ),
        )

    def handle(self, *args, **options):
        if options.get('set'):
            window, raw_value = options['set']
            self._handle_set(window, raw_value)
        elif options.get('unset'):
            self._handle_unset(options['unset'])
        elif options.get('set_mode'):
            self._handle_set_mode(options['set_mode'])
        elif options.get('unset_mode'):
            self._handle_unset_mode()
        else:
            # Default when no flag provided — same as --show.
            self._handle_show()

    # ─────────────────────────── handlers ──────────────────────────── #

    def _handle_show(self):
        from core.services.cost_threshold_monitor import (
            read_thresholds_snapshot,
            read_enforce_mode,
        )
        # Determine whether the mode row is set OR defaulted to 'monitor'.
        # read_enforce_mode() returns 'monitor' both when row is absent AND
        # when row is 'monitor'. Distinguish via direct query.
        mode_row_present = self._mode_row_present()
        mode = read_enforce_mode()
        snapshot = read_thresholds_snapshot()

        lines = ['[COST_MONITOR] configuration:']
        mode_suffix = '' if mode_row_present else ' (default; unset row)'
        lines.append(f'  enforce_mode: {mode}{mode_suffix}')
        for window in _WINDOWS:
            threshold = snapshot.get(window)
            if threshold is not None:
                lines.append(f'  {window}: ${threshold:.2f}')
            else:
                lines.append(f'  {window}: unset')
        self.stdout.write('\n'.join(lines))

    def _handle_set(self, window: str, raw_value: str):
        if window not in _WINDOWS:
            raise CommandError(
                f"invalid WINDOW {window!r}; must be one of {_WINDOWS}"
            )
        value = self._parse_threshold_value(raw_value)
        from core.models.system import SystemConfiguration
        SystemConfiguration.set_config(
            key=_CONFIG_KEY_BY_WINDOW[window],
            value=str(value),
            description=(
                f'Cost protection threshold — {window} rolling window '
                f'(USD). Set via manage.py cost_thresholds.'
            ),
            category='performance',
        )
        self.stdout.write(
            f'[COST_MONITOR] set {window}=${value:.2f}'
        )

    def _handle_unset(self, window: str):
        if window not in _WINDOWS:
            raise CommandError(
                f"invalid WINDOW {window!r}; must be one of {_WINDOWS}"
            )
        from core.models.system import SystemConfiguration
        deleted, _ = SystemConfiguration.objects.filter(
            key=_CONFIG_KEY_BY_WINDOW[window],
        ).delete()
        if deleted:
            self.stdout.write(
                f'[COST_MONITOR] unset {window} '
                f'(deleted {deleted} row)'
            )
        else:
            self.stdout.write(
                f'[COST_MONITOR] unset {window} '
                f'(no row to delete; already at default)'
            )

    def _handle_set_mode(self, raw_mode: str):
        mode = raw_mode.strip().lower()
        if mode not in _MODES:
            raise CommandError(
                f"invalid MODE {raw_mode!r}; must be one of {_MODES}"
            )
        from core.models.system import SystemConfiguration
        SystemConfiguration.set_config(
            key=_MODE_KEY,
            value=mode,
            description=(
                'Cost protection enforce mode — monitor (default) or '
                'freeze. Set via manage.py cost_thresholds. Enforcement '
                'flip is deferred per S2735 P1 gate discipline; '
                "'freeze' still monitor-only at HEAD but fires the "
                'S2739 would_freeze shadow log on breach.'
            ),
            category='performance',
        )
        self.stdout.write(f'[COST_MONITOR] set enforce_mode={mode}')

    def _handle_unset_mode(self):
        from core.models.system import SystemConfiguration
        deleted, _ = SystemConfiguration.objects.filter(
            key=_MODE_KEY,
        ).delete()
        if deleted:
            self.stdout.write(
                f'[COST_MONITOR] unset enforce_mode '
                f'(deleted {deleted} row; reverts to default monitor)'
            )
        else:
            self.stdout.write(
                '[COST_MONITOR] unset enforce_mode '
                '(no row to delete; already at default monitor)'
            )

    # ──────────────────────────── helpers ──────────────────────────── #

    def _parse_threshold_value(self, raw: str) -> Decimal:
        try:
            value = Decimal(raw)
        except (InvalidOperation, ValueError) as e:
            raise CommandError(
                f'invalid VALUE {raw!r}: expected Decimal-parseable '
                f'string ({type(e).__name__})'
            )
        if not value.is_finite():
            raise CommandError(
                f'invalid VALUE {raw!r}: must be finite (got {value})'
            )
        if value <= 0:
            raise CommandError(
                f'invalid VALUE {raw!r}: must be > 0 (got {value}). '
                f'Zero or negative would fire on every cost; use --unset '
                f'to remove a threshold.'
            )
        return value

    def _mode_row_present(self) -> bool:
        from core.models.system import SystemConfiguration
        return SystemConfiguration.objects.filter(
            key=_MODE_KEY, is_active=True,
        ).exists()
