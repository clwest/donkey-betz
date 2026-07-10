"""
Tests for the ``cost_thresholds`` management command (S2744 §17 ops
surface).

Covers:

* ``--show`` (and default when no flag) prints current state with the
  ``[COST_MONITOR] configuration:`` header + deterministic
  enforce_mode-then-windows order.
* ``--set WINDOW VALUE`` writes to SystemConfiguration; --show reflects
  it; roundtrip works for all three windows.
* ``--unset WINDOW`` deletes the SystemConfiguration row (not
  is_active=False).
* ``--set-mode MODE`` writes to SystemConfiguration; --show shows
  without "(default)" suffix once row is present.
* ``--unset-mode`` deletes the row; --show shows "(default; unset row)"
  suffix again.
* Validation: invalid window, invalid value (non-Decimal, zero,
  negative, non-finite), invalid mode all raise CommandError.
* Flags are mutually exclusive (argparse enforces).

Test discipline:

- Real DB, real SystemConfiguration writes. No mocking of the substrate.
- Uses ``call_command`` from ``django.core.management`` to invoke the
  command exactly as ops would (Chris on the CLI).
- Captures stdout via ``StringIO`` for output assertions.

Run::

    python manage.py test core.tests.test_cost_thresholds_command -v2
"""
from __future__ import annotations

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.models.system import SystemConfiguration


_HOUR_KEY = 'cost_threshold_hour_usd'
_DAY_KEY = 'cost_threshold_day_usd'
_MONTH_KEY = 'cost_threshold_month_usd'
_MODE_KEY = 'cost_protection_enforce_mode'


class ShowTests(TestCase):
    """--show (or default) prints [COST_MONITOR] configuration block."""

    def _run(self):
        out = StringIO()
        call_command('cost_thresholds', stdout=out)
        return out.getvalue()

    def test_show_all_unset_prints_defaults(self):
        output = self._run()
        self.assertIn('[COST_MONITOR] configuration:', output)
        self.assertIn('enforce_mode: monitor (default; unset row)', output)
        self.assertIn('hour: unset', output)
        self.assertIn('day: unset', output)
        self.assertIn('month: unset', output)

    def test_show_thresholds_set_prints_values(self):
        SystemConfiguration.set_config(key=_HOUR_KEY, value='10.00')
        SystemConfiguration.set_config(key=_DAY_KEY, value='100.50')
        SystemConfiguration.set_config(key=_MONTH_KEY, value='500.00')
        output = self._run()
        self.assertIn('hour: $10.00', output)
        self.assertIn('day: $100.50', output)
        self.assertIn('month: $500.00', output)

    def test_show_deterministic_order_mode_then_windows(self):
        SystemConfiguration.set_config(key=_HOUR_KEY, value='10.00')
        output = self._run()
        idx_mode = output.find('enforce_mode:')
        idx_hour = output.find('hour:')
        idx_day = output.find('day:')
        idx_month = output.find('month:')
        # Order MUST be mode → hour → day → month
        self.assertTrue(0 <= idx_mode < idx_hour < idx_day < idx_month)

    def test_show_mode_set_hides_default_suffix(self):
        SystemConfiguration.set_config(key=_MODE_KEY, value='freeze')
        output = self._run()
        self.assertIn('enforce_mode: freeze', output)
        self.assertNotIn('(default; unset row)', output)

    def test_default_no_flag_matches_show(self):
        SystemConfiguration.set_config(key=_HOUR_KEY, value='10.00')
        out_show = StringIO()
        call_command('cost_thresholds', '--show', stdout=out_show)
        out_default = StringIO()
        call_command('cost_thresholds', stdout=out_default)
        self.assertEqual(out_show.getvalue(), out_default.getvalue())


class SetTests(TestCase):
    """--set WINDOW VALUE roundtrips through SystemConfiguration."""

    def _run_set(self, window: str, value: str):
        out = StringIO()
        call_command('cost_thresholds', '--set', window, value, stdout=out)
        return out.getvalue()

    def test_set_month_creates_config_row(self):
        output = self._run_set('month', '500')
        self.assertIn('set month=$500.00', output)
        row = SystemConfiguration.objects.get(key=_MONTH_KEY)
        self.assertEqual(row.value, '500')
        self.assertEqual(row.category, 'performance')
        self.assertTrue(row.is_active)

    def test_set_accepts_two_decimal_value(self):
        self._run_set('day', '100.50')
        row = SystemConfiguration.objects.get(key=_DAY_KEY)
        self.assertEqual(row.value, '100.50')

    def test_set_all_three_windows_roundtrip(self):
        self._run_set('hour', '10')
        self._run_set('day', '100')
        self._run_set('month', '1000')
        out = StringIO()
        call_command('cost_thresholds', stdout=out)
        rendered = out.getvalue()
        self.assertIn('hour: $10.00', rendered)
        self.assertIn('day: $100.00', rendered)
        self.assertIn('month: $1000.00', rendered)

    def test_set_invalid_window_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set', 'year', '5000')
        self.assertIn("invalid WINDOW 'year'", str(ctx.exception))

    def test_set_non_decimal_value_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set', 'hour', 'not-a-number')
        self.assertIn("invalid VALUE 'not-a-number'", str(ctx.exception))

    def test_set_zero_raises_with_guardrail_message(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set', 'hour', '0')
        msg = str(ctx.exception)
        self.assertIn('must be > 0', msg)
        self.assertIn('fire on every cost', msg)

    def test_set_negative_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set', 'hour', '-5')
        self.assertIn('must be > 0', str(ctx.exception))

    def test_set_non_finite_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set', 'hour', 'inf')
        self.assertIn('must be finite', str(ctx.exception))


class UnsetTests(TestCase):
    """--unset WINDOW deletes SystemConfiguration row."""

    def test_unset_deletes_row(self):
        SystemConfiguration.set_config(key=_HOUR_KEY, value='10.00')
        self.assertTrue(
            SystemConfiguration.objects.filter(key=_HOUR_KEY).exists()
        )
        out = StringIO()
        call_command('cost_thresholds', '--unset', 'hour', stdout=out)
        self.assertIn('unset hour', out.getvalue())
        self.assertIn('deleted 1 row', out.getvalue())
        self.assertFalse(
            SystemConfiguration.objects.filter(key=_HOUR_KEY).exists()
        )

    def test_unset_absent_row_is_noop_with_message(self):
        out = StringIO()
        call_command('cost_thresholds', '--unset', 'month', stdout=out)
        self.assertIn('unset month', out.getvalue())
        self.assertIn('no row to delete', out.getvalue())

    def test_unset_invalid_window_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--unset', 'century')
        self.assertIn("invalid WINDOW 'century'", str(ctx.exception))


class SetModeTests(TestCase):
    """--set-mode writes SystemConfiguration row."""

    def test_set_mode_monitor(self):
        out = StringIO()
        call_command('cost_thresholds', '--set-mode', 'monitor', stdout=out)
        self.assertIn('set enforce_mode=monitor', out.getvalue())
        row = SystemConfiguration.objects.get(key=_MODE_KEY)
        self.assertEqual(row.value, 'monitor')

    def test_set_mode_freeze(self):
        out = StringIO()
        call_command('cost_thresholds', '--set-mode', 'freeze', stdout=out)
        self.assertIn('set enforce_mode=freeze', out.getvalue())
        row = SystemConfiguration.objects.get(key=_MODE_KEY)
        self.assertEqual(row.value, 'freeze')

    def test_set_mode_case_insensitive(self):
        call_command('cost_thresholds', '--set-mode', 'FREEZE')
        row = SystemConfiguration.objects.get(key=_MODE_KEY)
        self.assertEqual(row.value, 'freeze')

    def test_set_mode_invalid_raises(self):
        with self.assertRaises(CommandError) as ctx:
            call_command('cost_thresholds', '--set-mode', 'paranoid')
        self.assertIn("invalid MODE 'paranoid'", str(ctx.exception))


class UnsetModeTests(TestCase):
    """--unset-mode deletes the SystemConfiguration row."""

    def test_unset_mode_deletes_row(self):
        SystemConfiguration.set_config(key=_MODE_KEY, value='freeze')
        self.assertTrue(
            SystemConfiguration.objects.filter(key=_MODE_KEY).exists()
        )
        out = StringIO()
        call_command('cost_thresholds', '--unset-mode', stdout=out)
        self.assertIn('unset enforce_mode', out.getvalue())
        self.assertIn('deleted 1 row', out.getvalue())
        self.assertIn('reverts to default monitor', out.getvalue())
        self.assertFalse(
            SystemConfiguration.objects.filter(key=_MODE_KEY).exists()
        )

    def test_unset_mode_absent_is_noop_with_message(self):
        out = StringIO()
        call_command('cost_thresholds', '--unset-mode', stdout=out)
        self.assertIn('no row to delete', out.getvalue())
        self.assertIn('already at default monitor', out.getvalue())


class MutualExclusionTests(TestCase):
    """argparse enforces mutual exclusion of flags."""

    def test_set_and_unset_together_raises(self):
        with self.assertRaises((SystemExit, CommandError)):
            call_command(
                'cost_thresholds',
                '--set', 'hour', '10',
                '--unset', 'day',
            )

    def test_set_and_set_mode_together_raises(self):
        with self.assertRaises((SystemExit, CommandError)):
            call_command(
                'cost_thresholds',
                '--set', 'hour', '10',
                '--set-mode', 'freeze',
            )


class EndToEndTests(TestCase):
    """Full ops workflow: set thresholds + mode → show → unset → show."""

    def test_full_ops_cycle(self):
        # Initial state — all unset.
        out1 = StringIO()
        call_command('cost_thresholds', stdout=out1)
        self.assertIn('hour: unset', out1.getvalue())
        self.assertIn('enforce_mode: monitor (default; unset row)', out1.getvalue())

        # Configure hour + day thresholds + freeze mode.
        call_command('cost_thresholds', '--set', 'hour', '5.00')
        call_command('cost_thresholds', '--set', 'day', '50.00')
        call_command('cost_thresholds', '--set-mode', 'freeze')

        # Show mid-state.
        out2 = StringIO()
        call_command('cost_thresholds', stdout=out2)
        rendered = out2.getvalue()
        self.assertIn('enforce_mode: freeze', rendered)
        self.assertNotIn('(default; unset row)', rendered)
        self.assertIn('hour: $5.00', rendered)
        self.assertIn('day: $50.00', rendered)
        self.assertIn('month: unset', rendered)

        # Unset everything.
        call_command('cost_thresholds', '--unset', 'hour')
        call_command('cost_thresholds', '--unset', 'day')
        call_command('cost_thresholds', '--unset-mode')

        # Back to initial state.
        out3 = StringIO()
        call_command('cost_thresholds', stdout=out3)
        self.assertEqual(out1.getvalue(), out3.getvalue())
