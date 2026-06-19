"""Tests for core.services.retry_policy.

Session 1165 (COO Backlog item #6): pin the retry-policy contract
so future refactors don't silently break stampede prevention.
"""

from __future__ import annotations

import unittest

from django.core.cache import cache
from django.test import SimpleTestCase

from core.services.retry_policy import (
    BUDGET_KEY_PREFIX,
    COUNTDOWN_CEILING,
    COUNTDOWN_FLOOR,
    check_retry_budget,
    compute_retry_countdown,
    reset_retry_budget,
)


class ComputeRetryCountdownTests(SimpleTestCase):
    """`compute_retry_countdown` — exponential backoff helper."""

    def test_returns_int_seconds(self):
        result = compute_retry_countdown(0, base=60, jitter=False)
        self.assertIsInstance(result, int)

    def test_no_jitter_first_retry_returns_base(self):
        self.assertEqual(compute_retry_countdown(0, base=60, jitter=False), 60)

    def test_no_jitter_doubles_per_retry(self):
        # base * 2**retries
        self.assertEqual(compute_retry_countdown(0, base=30, jitter=False), 30)
        self.assertEqual(compute_retry_countdown(1, base=30, jitter=False), 60)
        self.assertEqual(compute_retry_countdown(2, base=30, jitter=False), 120)
        self.assertEqual(compute_retry_countdown(3, base=30, jitter=False), 240)

    def test_max_delay_caps_high_retries(self):
        # base=60, retries=10 → 60 * 1024 = 61440s, capped at max_delay
        self.assertEqual(
            compute_retry_countdown(10, base=60, max_delay=1800, jitter=False),
            1800,
        )

    def test_floor_protects_against_low_base(self):
        # base=1, retries=0 → 1, but floor=5
        self.assertEqual(
            compute_retry_countdown(0, base=1, jitter=False),
            COUNTDOWN_FLOOR,
        )

    def test_jitter_stays_within_25_percent_band(self):
        # With jitter, all samples should fall in [0.75 * base, 1.25 * base]
        base = 100
        samples = [
            compute_retry_countdown(0, base=base, jitter=True)
            for _ in range(200)
        ]
        for s in samples:
            self.assertGreaterEqual(s, int(base * 0.75))
            self.assertLessEqual(s, int(base * 1.25))

    def test_jitter_produces_variation(self):
        # Make sure we're not accidentally returning the same value every time
        base = 100
        samples = {
            compute_retry_countdown(0, base=base, jitter=True)
            for _ in range(50)
        }
        # Expect a spread of at least 5 distinct values across 50 samples
        self.assertGreater(len(samples), 5)

    def test_ceiling_constant_is_3600(self):
        self.assertEqual(COUNTDOWN_CEILING, 3600)

    def test_floor_constant_is_5(self):
        self.assertEqual(COUNTDOWN_FLOOR, 5)

    def test_negative_retries_clamped_to_zero(self):
        # Defensive — shouldn't happen in practice but contract is clear
        result = compute_retry_countdown(-3, base=60, jitter=False)
        self.assertEqual(result, 60)


class CheckRetryBudgetTests(SimpleTestCase):
    """`check_retry_budget` — Redis-backed sliding-window counter."""

    def setUp(self):
        # Clean slate before each test
        for suffix in ["", ":user-42", ":user-99"]:
            cache.delete(BUDGET_KEY_PREFIX + "test-budget-task" + suffix)
            cache.delete(BUDGET_KEY_PREFIX + "other-task" + suffix)

    def tearDown(self):
        for suffix in ["", ":user-42", ":user-99"]:
            cache.delete(BUDGET_KEY_PREFIX + "test-budget-task" + suffix)
            cache.delete(BUDGET_KEY_PREFIX + "other-task" + suffix)

    def test_first_call_allowed(self):
        allowed, reason = check_retry_budget("test-budget-task", max_retries=3)
        self.assertTrue(allowed)
        self.assertIn("1/3", reason)

    def test_counter_increments_per_call(self):
        for expected in range(1, 4):
            allowed, reason = check_retry_budget("test-budget-task", max_retries=3)
            self.assertTrue(allowed)
            self.assertIn(f"{expected}/3", reason)

    def test_budget_exhausted_after_max_retries(self):
        # 3 allowed calls
        for _ in range(3):
            allowed, _ = check_retry_budget("test-budget-task", max_retries=3)
            self.assertTrue(allowed)
        # 4th call should be denied (counter went to 4 > 3)
        allowed, reason = check_retry_budget("test-budget-task", max_retries=3)
        self.assertFalse(allowed)
        self.assertIn("budget_exhausted", reason)
        self.assertIn("4/3", reason)

    def test_different_task_names_have_independent_budgets(self):
        for _ in range(3):
            check_retry_budget("test-budget-task", max_retries=3)
        # `other-task` should still have a fresh budget
        allowed, reason = check_retry_budget("other-task", max_retries=3)
        self.assertTrue(allowed)
        self.assertIn("1/3", reason)

    def test_fingerprint_scopes_budget(self):
        # Exhaust budget for user-42
        for _ in range(3):
            check_retry_budget(
                "test-budget-task", max_retries=3, fingerprint="user-42"
            )
        # user-99 should still have a fresh budget
        allowed, reason = check_retry_budget(
            "test-budget-task", max_retries=3, fingerprint="user-99"
        )
        self.assertTrue(allowed)
        self.assertIn("1/3", reason)
        # Confirm user-42 is exhausted
        allowed, reason = check_retry_budget(
            "test-budget-task", max_retries=3, fingerprint="user-42"
        )
        self.assertFalse(allowed)

    def test_fingerprint_in_reason_key(self):
        _, reason = check_retry_budget(
            "test-budget-task", max_retries=10, fingerprint="user-42"
        )
        self.assertIn("user-42", reason)

    def test_reason_carries_max_retries(self):
        _, reason = check_retry_budget("test-budget-task", max_retries=7)
        self.assertIn("1/7", reason)


class ResetRetryBudgetTests(SimpleTestCase):
    """`reset_retry_budget` — manual ops escape hatch."""

    def setUp(self):
        cache.delete(BUDGET_KEY_PREFIX + "test-reset-task")

    def tearDown(self):
        cache.delete(BUDGET_KEY_PREFIX + "test-reset-task")

    def test_reset_clears_counter(self):
        # Bump the counter
        for _ in range(5):
            check_retry_budget("test-reset-task", max_retries=3)
        # Reset
        result = reset_retry_budget("test-reset-task")
        self.assertTrue(result)
        # Next check should be 1/3 again
        allowed, reason = check_retry_budget("test-reset-task", max_retries=3)
        self.assertTrue(allowed)
        self.assertIn("1/3", reason)

    def test_reset_returns_false_when_key_absent(self):
        # Nothing to reset
        result = reset_retry_budget("test-reset-task")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
