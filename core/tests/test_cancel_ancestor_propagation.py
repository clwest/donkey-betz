"""
Session 1098 PR #4 — Cancellation propagates to nested dispatches.
==================================================================

Rigby's priority #4 guardrails (conversation ``pa-d19c1674b936``):

- Record lineage on the execution row (parent + root)
- ``is_execution_cancelled`` walks ancestors; cancel on parent cancels
  children at their next checkpoint
- Cap ancestor walk depth; cycles abort rather than loop
- Missing ``parent_execution_id`` → behavior unchanged

Covered here:

- Direct self cancel still works (sanity — PR #3 behavior preserved)
- Parent-cancelled → child ``is_execution_cancelled`` returns True
- Root-cancelled → deep-grandchild returns True via root_execution_id
  short-circuit (no cancel set on intermediate parent)
- Cycle in parent_execution_id → walk returns False, warns, doesn't
  loop forever
- Depth cap: a 30-deep chain doesn't blow past the 25 cap
- Pre-PR-4 row (parent_execution_id=None) behaves like a root
  execution — no ancestor walk

Run::

    python manage.py test core.tests.test_cancel_ancestor_propagation -v2
"""

import uuid
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import Agent, AgentExecution
from core.services.cancel_registry import (
    _MAX_ANCESTOR_DEPTH,
    _reset_memory_registry_for_tests,
    is_execution_cancelled,
    request_execution_cancel,
)


User = get_user_model()


class AncestorCancelPropagationTests(TestCase):
    """PR #4 — cancel on any ancestor cancels the current execution."""

    def setUp(self):
        _reset_memory_registry_for_tests()
        self.user = User.objects.create_user(
            username='ancestor-cancel-test',
            email='ancestor@example.com',
            password='x',
        )
        self.agent, _ = Agent.objects.get_or_create(
            name='TestLineageAgent',
            defaults={'description': 'test', 'specialization': 'test'},
        )

    def _mk(self, parent=None, root=None):
        """Create an AgentExecution with optional lineage pointers."""
        return AgentExecution.objects.create(
            agent=self.agent,
            user=self.user,
            task='lineage-test',
            status='in_progress',
            parent_execution_id=parent,
            root_execution_id=root,
        )

    def _no_redis(self):
        """Force in-memory registry path for deterministic tests."""
        return mock.patch(
            'core.services.cancel_registry._get_redis', return_value=None,
        )

    # ── Self-cancel still works (PR #3 behavior preserved) ─────────────

    def test_self_cancel_still_works(self):
        run = self._mk()
        with self._no_redis():
            self.assertFalse(is_execution_cancelled(run.id))
            request_execution_cancel(run.id, reason='self')
            self.assertTrue(is_execution_cancelled(run.id))

    # ── Parent cancel propagates to child ──────────────────────────────

    def test_parent_cancel_propagates_to_child(self):
        parent = self._mk()
        # Set parent's root to itself (what _create_execution_record does).
        AgentExecution.objects.filter(id=parent.id).update(
            root_execution_id=parent.id,
        )
        child = self._mk(parent=parent.id, root=parent.id)

        with self._no_redis():
            self.assertFalse(is_execution_cancelled(child.id))
            request_execution_cancel(parent.id, reason='parent cancelled')
            self.assertTrue(
                is_execution_cancelled(child.id),
                'child must see parent cancel via ancestor walk',
            )

    def test_child_cancel_does_not_cancel_parent(self):
        """Cancel flows DOWN the tree, not up. A cancelled child must
        not mark its parent as cancelled."""
        parent = self._mk()
        AgentExecution.objects.filter(id=parent.id).update(
            root_execution_id=parent.id,
        )
        child = self._mk(parent=parent.id, root=parent.id)

        with self._no_redis():
            request_execution_cancel(child.id, reason='child cancelled')
            self.assertTrue(is_execution_cancelled(child.id))
            self.assertFalse(
                is_execution_cancelled(parent.id),
                'parent must not be affected by child cancel',
            )

    # ── Deep chain: grandchild sees root cancel ────────────────────────

    def test_grandchild_sees_root_cancel(self):
        """A 3-deep chain: cancelling the root cancels the grandchild."""
        root = self._mk()
        AgentExecution.objects.filter(id=root.id).update(
            root_execution_id=root.id,
        )
        child = self._mk(parent=root.id, root=root.id)
        grand = self._mk(parent=child.id, root=root.id)

        with self._no_redis():
            request_execution_cancel(root.id, reason='root cancelled')
            self.assertTrue(is_execution_cancelled(grand.id))
            self.assertTrue(is_execution_cancelled(child.id))
            self.assertTrue(is_execution_cancelled(root.id))

    def test_intermediate_cancel_stops_at_that_level(self):
        """Cancel on the middle node cancels the leaf but NOT the root."""
        root = self._mk()
        AgentExecution.objects.filter(id=root.id).update(
            root_execution_id=root.id,
        )
        middle = self._mk(parent=root.id, root=root.id)
        leaf = self._mk(parent=middle.id, root=root.id)

        with self._no_redis():
            request_execution_cancel(middle.id)
            self.assertTrue(is_execution_cancelled(leaf.id))
            self.assertTrue(is_execution_cancelled(middle.id))
            self.assertFalse(
                is_execution_cancelled(root.id),
                'root must not see middle-cancel',
            )

    # ── Safety: cycles + depth cap ────────────────────────────────────

    def test_cycle_in_ancestry_aborts_walk(self):
        """Pathological data: A → B → A. The walk must not loop."""
        a = self._mk()
        b = self._mk(parent=a.id)
        # Create cycle: a.parent = b.id
        AgentExecution.objects.filter(id=a.id).update(
            parent_execution_id=b.id,
        )

        with self._no_redis():
            # Neither is cancelled yet — walk should terminate False.
            self.assertFalse(is_execution_cancelled(a.id))
            self.assertFalse(is_execution_cancelled(b.id))

            # Cancel something OUTSIDE the cycle — still False.
            c = self._mk()
            request_execution_cancel(c.id)
            self.assertFalse(is_execution_cancelled(a.id))
            self.assertFalse(is_execution_cancelled(b.id))

    def test_depth_cap_respected(self):
        """A 30-deep chain doesn't loop past the 25 cap. Cancelling the
        root is beyond reach from the bottom — returns False per the
        'inconclusive' spec."""
        prev = self._mk()
        AgentExecution.objects.filter(id=prev.id).update(
            root_execution_id=prev.id,
        )
        deepest = prev
        for _ in range(_MAX_ANCESTOR_DEPTH + 5):
            deepest = self._mk(parent=deepest.id, root=prev.id)

        with self._no_redis():
            # Cancel the very root.
            request_execution_cancel(prev.id)
            # From the deepest node, root is beyond the cap.
            # The check should return False (inconclusive), not loop.
            self.assertFalse(is_execution_cancelled(deepest.id))
            # But the root itself IS cancelled.
            self.assertTrue(is_execution_cancelled(prev.id))

    # ── Pre-PR-4 compatibility: no parent_id == root behavior ─────────

    def test_no_parent_id_behaves_like_root(self):
        """Row with parent_execution_id=None (pre-migration or root) must
        only check its own cancel state. No ancestor walk, no crash."""
        run = self._mk(parent=None, root=None)
        with self._no_redis():
            self.assertFalse(is_execution_cancelled(run.id))
            request_execution_cancel(run.id)
            self.assertTrue(is_execution_cancelled(run.id))

    def test_missing_execution_row_returns_false(self):
        """An execution_id that doesn't exist in the DB returns False —
        no ancestor walk possible, no crash."""
        with self._no_redis():
            self.assertFalse(is_execution_cancelled(uuid.uuid4()))
