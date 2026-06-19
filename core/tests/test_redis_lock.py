"""Tests for core.services.redis_lock.

Session 1165 (COO Backlog item #3): pin the singleton_lock contract
so future refactors don't silently break stampede prevention.
"""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock

from django.core.cache import cache
from django.test import SimpleTestCase

from core.services.redis_lock import (
    LOCK_PREFIX,
    singleton_lock,
    singleton_task,
)


class SingletonLockContextManagerTests(SimpleTestCase):
    """Direct primitive — `with singleton_lock(...) as acquired`."""

    def setUp(self):
        # Ensure a clean slate for each test
        cache.delete(LOCK_PREFIX + "test-lock-A")
        cache.delete(LOCK_PREFIX + "test-lock-B")

    def tearDown(self):
        cache.delete(LOCK_PREFIX + "test-lock-A")
        cache.delete(LOCK_PREFIX + "test-lock-B")

    def test_first_acquirer_wins(self):
        with singleton_lock("test-lock-A", ttl=10) as acquired:
            self.assertTrue(acquired)

    def test_second_acquirer_is_blocked_while_first_holds(self):
        # First holder enters and stays in (doesn't exit yet)
        with singleton_lock("test-lock-A", ttl=10) as first_acquired:
            self.assertTrue(first_acquired)
            with singleton_lock("test-lock-A", ttl=10) as second_acquired:
                self.assertFalse(second_acquired)

    def test_value_stored_under_canonical_key(self):
        with singleton_lock("test-lock-A", ttl=10, value="task-id-xyz"):
            stored = cache.get(LOCK_PREFIX + "test-lock-A")
            self.assertEqual(stored, "task-id-xyz")

    def test_value_default_is_one(self):
        with singleton_lock("test-lock-A", ttl=10):
            stored = cache.get(LOCK_PREFIX + "test-lock-A")
            self.assertEqual(stored, "1")

    def test_different_names_dont_collide(self):
        with singleton_lock("test-lock-A", ttl=10) as a:
            with singleton_lock("test-lock-B", ttl=10) as b:
                self.assertTrue(a)
                self.assertTrue(b)

    def test_ttl_only_release_lock_persists_after_exit(self):
        """TTL-only contract: lock value remains in cache after the
        context exits (we do NOT explicitly delete on success).
        """
        with singleton_lock("test-lock-A", ttl=10):
            pass
        self.assertEqual(cache.get(LOCK_PREFIX + "test-lock-A"), "1")

    def test_lock_expires_after_ttl(self):
        with singleton_lock("test-lock-A", ttl=1):
            pass
        time.sleep(1.5)
        # After TTL, a new acquirer should win
        with singleton_lock("test-lock-A", ttl=10) as acquired:
            self.assertTrue(acquired)


class SingletonTaskDecoratorTests(SimpleTestCase):
    """`@singleton_task(name, ttl=...)` decorator behavior."""

    def setUp(self):
        cache.delete(LOCK_PREFIX + "test-task")

    def tearDown(self):
        cache.delete(LOCK_PREFIX + "test-task")

    def test_body_runs_when_no_collision(self):
        @singleton_task("test-task", ttl=10)
        def my_task():
            return {"ran": True, "value": 42}

        result = my_task()
        self.assertEqual(result, {"ran": True, "value": 42})

    def test_body_skipped_on_collision_returns_skipped_payload(self):
        # Pre-hold the lock
        cache.add(LOCK_PREFIX + "test-task", "other-holder", timeout=10)

        @singleton_task("test-task", ttl=10)
        def my_task():
            return {"ran": True}  # should not execute

        result = my_task()
        self.assertEqual(result["skipped"], True)
        self.assertEqual(result["reason"], "concurrent run")
        self.assertEqual(result["lock_name"], "test-task")
        # task_id is None because we didn't pass a bind=True self
        self.assertIsNone(result["task_id"])

    def test_decorator_extracts_task_id_from_bind_true_self(self):
        # Simulate @shared_task(bind=True) by passing a self-like first arg
        fake_self = MagicMock()
        fake_self.request.id = "celery-task-id-abc-123"

        @singleton_task("test-task", ttl=10)
        def my_task(self):
            return {"ran": True, "task_id_from_self": self.request.id}

        result = my_task(fake_self)
        self.assertEqual(result, {
            "ran": True,
            "task_id_from_self": "celery-task-id-abc-123",
        })
        # Lock value should carry the task_id
        self.assertEqual(
            cache.get(LOCK_PREFIX + "test-task"),
            "celery-task-id-abc-123",
        )

    def test_decorator_collision_payload_carries_task_id_when_bound(self):
        # Pre-hold the lock
        cache.add(LOCK_PREFIX + "test-task", "first-holder", timeout=10)

        fake_self = MagicMock()
        fake_self.request.id = "second-runner-id"

        @singleton_task("test-task", ttl=10)
        def my_task(self):
            return {"ran": True}

        result = my_task(fake_self)
        self.assertEqual(result["skipped"], True)
        self.assertEqual(result["task_id"], "second-runner-id")

    def test_decorator_preserves_function_metadata(self):
        @singleton_task("test-task", ttl=10)
        def my_named_task():
            """My docstring."""
            return None

        self.assertEqual(my_named_task.__name__, "my_named_task")
        self.assertEqual(my_named_task.__doc__, "My docstring.")


if __name__ == "__main__":
    unittest.main()
