"""
S2883 slate — agent-diagnostic family structured error-envelope migration.

Sixth real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Completes the ``td_handlers_ops.py``
bare-``{'error': ...}``-return population: post-S2883 count = 0.

**10 sites across 4 handlers / 4 tool surfaces** — Rigby's Q1 pre-code
routing-map established that Slate 3 spans 4 dedicated tools, forcing
a Fold D discipline check before any code was written (matches PLAYBOOK
amendment candidate 6.10.10 helper-enclosing-scope grep discipline
refinement from S2882 zoom-out (b)):

* ``_handle_agent_memory`` — ``agent_memory_tool`` (dispatcher L610).
  4 sites: L6782 ``invalid_params`` (missing agent_name), L6799
  ``not_found`` (agent lookup fail), L6873 ``unknown_action``
  (fallthrough), L6877 ``internal_error`` (broad ``except Exception:``).
* ``_handle_heartbeat_history`` — ``heartbeat_history_tool`` (L611).
  2 sites: L6942 ``unknown_action``, L6946 ``internal_error``.
* ``_handle_infra_health`` — ``infra_health_tool`` (L612). 2 sites:
  L7163 ``unknown_action``, L7167 ``internal_error``.
* ``_handle_search_docs`` — ``search_docs`` (L629, no ``_tool``
  suffix). 2 sites: L7615 ``invalid_params`` (missing query), L7762
  ``internal_error``.

**Helper-choice — Path 1 SPLIT (Rigby+Claude joint verdict, Chris D-approved):**

* 6 non-catch-all sites migrated to ``_handler_error`` (5-code
  taxonomy: ``invalid_params`` / ``not_found`` / ``unknown_action``).
* 4 broad-except sites migrated to ``_tool_error('internal_error', ...)``
  matching the S2879 ``_handle_spider_status`` precedent at
  ``td_handlers_ops.py:6737``. Reasoning: ``_handler_error``'s
  5-code taxonomy is explicitly locked (docstring at L48) and
  ``internal_error`` is not part of it; overloading would silently
  redefine the taxonomy contract. ``_tool_error`` is the older
  cross-tool envelope with existing ``internal_error`` adopters —
  keeping the split preserves each helper's stated contract until
  the ``td_error.py`` unification arc lands (Ledger #13, now with
  6th adopter signal reached).

**Fold C 3rd trigger:** 2-helper coexistence in a single slate
(previously observed at S2880 slate-2 and S2881 write-path). Locked
in as future consolidation forcing function.

Sites tested (10 total):

* 6 ``_handler_error`` sites — asserted via the shared
  ``_assert_migrated_envelope`` (imported from
  ``test_s2879_governance_ops_error_envelope``) to keep the contract
  single-source and force a compile-time break if the S2879 helper
  signature ever drifts.
* 4 ``_tool_error('internal_error', ...)`` sites — asserted inline
  via ``_assert_internal_error_envelope`` (local helper matching the
  S2875 ``{error, error_code, action, exception_type}`` shape).

Broad-except sites are exercised via ``unittest.mock.patch`` on
downstream ORM/import calls to raise a deterministic exception inside
each handler's ``try:`` block — the S2875 ``'not-a-uuid'`` input-trigger
pattern is not available for these handlers because their exception
paths guard ORM aggregations rather than UUID parsing.

Run::

    python manage.py test core.tests.test_s2883_agent_diag_error_envelope -v2
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


def _assert_internal_error_envelope(tc, result, *, action):
    """Shared assertion for the S2875 ``_tool_error('internal_error', ...)`` shape.

    Contract matches ``{error, error_code='internal_error', action,
    exception_type, **fields}`` as emitted by ``_tool_error`` in
    ``td_handlers_ops.py:28``. Distinct from
    ``_assert_migrated_envelope`` (which expects the S2879 5-key
    ``_handler_error`` shape with ``success=False``).
    """
    tc.assertIsInstance(result, dict)
    tc.assertEqual(result.get('error_code'), 'internal_error')
    tc.assertTrue(result.get('error'), f"expected truthy error message; got {result!r}")
    tc.assertEqual(result.get('action'), action)
    tc.assertIn('exception_type', result)


# ────────────────────────────────────────────────────────────────────────
# agent_memory_tool — 4 sites
# ────────────────────────────────────────────────────────────────────────


class AgentMemoryToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2883 ``_handle_agent_memory`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'agent_memory_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"agent_memory_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_list_without_agent_name_returns_invalid_params(self):
        """L6782: non-stats action without ``agent_name`` → ``invalid_params``."""
        result = self._dispatch({'action': 'list'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='list',
        )

    def test_list_unknown_agent_returns_not_found(self):
        """L6799: ``agent_name`` lookup miss → ``not_found``."""
        result = self._dispatch({
            'action': 'list',
            'agent_name': '__nonexistent_agent_s2883__',
        })
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='list',
        )
        self.assertEqual(
            result.get('agent_name'),
            '__nonexistent_agent_s2883__',
            "not_found envelope must echo the requested agent_name",
        )

    def test_unknown_action_returns_unknown_action(self):
        """L6873: action string not in {list, knowledge, stats}.

        Mocks ``Agent.objects.filter`` to return a fake agent so the
        agent-lookup branch (L6797-6805) short-circuits past ``not_found``
        and the request reaches the unknown_action fallthrough at L6873.
        """
        fake_agent = SimpleNamespace(name='fake_agent_s2883')
        fake_qs = SimpleNamespace(first=lambda: fake_agent)
        with patch(
            'core.models_unified_system.Agent.objects.filter',
            return_value=fake_qs,
        ):
            result = self._dispatch({
                'action': '__bogus_action_s2883__',
                'agent_name': 'fake_agent_s2883',
            })
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2883__',
        )

    def test_broad_except_returns_internal_error(self):
        """L6877: broad ``except Exception:`` → ``_tool_error('internal_error', ...)``.

        Forces the exception path by mocking ``Agent.objects.filter`` to
        raise a deterministic ``RuntimeError``. The ORM call sits inside
        the handler's ``try:`` block at L6790, so the broad-except catch
        at L6875 fires.
        """
        with patch(
            'core.models_unified_system.Agent.objects.filter',
            side_effect=RuntimeError('boom_s2883_agent_memory'),
        ):
            result = self._dispatch({
                'action': 'list',
                'agent_name': 'anything',
            })
        _assert_internal_error_envelope(self, result, action='list')
        self.assertEqual(result.get('exception_type'), 'RuntimeError')


# ────────────────────────────────────────────────────────────────────────
# heartbeat_history_tool — 2 sites
# ────────────────────────────────────────────────────────────────────────


class HeartbeatHistoryToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2883 ``_handle_heartbeat_history`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'heartbeat_history_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"heartbeat_history_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_unknown_action_returns_unknown_action(self):
        """L6942: action string not in {recent, trends}."""
        result = self._dispatch({'action': '__bogus_action_s2883__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2883__',
        )

    def test_broad_except_returns_internal_error(self):
        """L6946: broad ``except Exception:`` → ``_tool_error('internal_error', ...)``.

        Mocks ``HeartBeat.objects.order_by`` (called inside the ``try:``
        block at L6888) to raise. Import path used here is the same one
        the handler resolves via the local ``from core.models_heart
        import HeartBeat`` at L6885.
        """
        with patch(
            'core.models_heart.HeartBeat.objects.order_by',
            side_effect=RuntimeError('boom_s2883_heartbeat_history'),
        ):
            result = self._dispatch({'action': 'recent'})
        _assert_internal_error_envelope(self, result, action='recent')
        self.assertEqual(result.get('exception_type'), 'RuntimeError')


# ────────────────────────────────────────────────────────────────────────
# infra_health_tool — 2 sites
# ────────────────────────────────────────────────────────────────────────


class InfraHealthToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2883 ``_handle_infra_health`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'infra_health_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"infra_health_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_unknown_action_returns_unknown_action(self):
        """L7163: action string not in valid infra actions set."""
        result = self._dispatch({'action': '__bogus_action_s2883__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2883__',
        )
        self.assertIn('redis_health', result.get('valid_actions', []))

    def test_broad_except_returns_internal_error(self):
        """L7167: broad ``except Exception:`` → ``_tool_error('internal_error', ...)``.

        Mocks ``redis.from_url`` (called inside the ``redis_health``
        branch's outer try at L6952) to raise, forcing the broad-except
        catch at L7165.
        """
        with patch(
            'redis.from_url',
            side_effect=RuntimeError('boom_s2883_infra_health'),
        ):
            result = self._dispatch({'action': 'redis_health'})
        _assert_internal_error_envelope(self, result, action='redis_health')
        self.assertEqual(result.get('exception_type'), 'RuntimeError')


# ────────────────────────────────────────────────────────────────────────
# search_docs — 2 sites
# ────────────────────────────────────────────────────────────────────────


class SearchDocsMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2883 ``_handle_search_docs`` migration.

    Note the tool name is ``search_docs`` (no ``_tool`` suffix) — verified
    via ``tool_dispatcher.py:629`` registration during Rigby's Q1 routing-map.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'search_docs', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"search_docs dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_missing_query_returns_invalid_params(self):
        """L7615: empty or missing ``query`` → ``invalid_params``."""
        result = self._dispatch({})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='search_docs',
        )

    def test_broad_except_returns_internal_error(self):
        """L7762: broad ``except Exception:`` → ``_tool_error('internal_error', ...)``.

        Mocks ``core.rag.top_k`` to raise. The handler imports ``top_k``
        + ``CORPUS_PATH`` locally at L7654 inside the try block, so the
        broad-except catch at L7760 fires.
        """
        with patch(
            'core.rag.top_k',
            side_effect=RuntimeError('boom_s2883_search_docs'),
        ):
            result = self._dispatch({'query': 'anything'})
        _assert_internal_error_envelope(self, result, action='search_docs')
        self.assertEqual(result.get('exception_type'), 'RuntimeError')
        self.assertEqual(
            result.get('query'), 'anything',
            "internal_error envelope must echo the requested query",
        )
