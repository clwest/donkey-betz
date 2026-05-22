"""Tests for `core.services.fleet_routing_dispatch` (Session 1127 Phase 2A).

Covers the Phase 2A dispatch bridge between `fleet_routing.resolve()` and
`AgentRouter`:

- snake_case → AGENT_MAP-key resolution (explicit map + naïve fallback)
- `should_force_dispatch()` gate logic (all 5 safety gates)
- `apply_force_dispatch()` bails when resolved_agent isn't in AGENT_MAP
- `derive_hint_for_context()` hint-mode rules (allowlist, override, force)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.services.fleet_routing import RoutingDecision
from core.services.fleet_routing_dispatch import (
    SNAKE_TO_AGENT_MAP_KEY,
    _naive_snake_to_pascal,
    apply_force_dispatch,
    derive_hint_for_context,
    resolve_to_agent_map_key,
    should_force_dispatch,
)


# ─── resolve_to_agent_map_key ─────────────────────────────────────────────


class TestResolveToAgentMapKey:
    def test_explicit_map_hit(self):
        assert resolve_to_agent_map_key("legal_doc_drafter_agent") == "LegalDocDrafterAgent"
        assert resolve_to_agent_map_key("seo_optimizer_agent") == "SEOOptimizerAgent"
        assert resolve_to_agent_map_key("content_writer_agent") == "ContentWriterAgent"

    def test_none_input_returns_none(self):
        assert resolve_to_agent_map_key(None) is None
        assert resolve_to_agent_map_key("") is None

    def test_unknown_snake_falls_back_to_naive_pascal(self):
        # Naive fallback — the dispatcher verifies AGENT_MAP membership
        # before actually routing, so a wrong guess can't misroute.
        assert resolve_to_agent_map_key("totally_unknown_agent") == "TotallyUnknownAgent"

    def test_seo_acronym_preserved_via_explicit_map(self):
        # The naïve fallback would mangle SEO to "SeoOptimizerAgent";
        # the explicit map prevents that.
        assert resolve_to_agent_map_key("seo_optimizer_agent") == "SEOOptimizerAgent"
        assert _naive_snake_to_pascal("seo_optimizer_agent") == "SeoOptimizerAgent"

    def test_security_agent_intentionally_unmapped(self):
        # Phase 2A: no SecurityAgent class in AGENT_MAP. Naive fallback
        # produces a non-existent class name; dispatcher will bail.
        assert "security_agent" not in SNAKE_TO_AGENT_MAP_KEY
        # naïve fallback still returns something — that's by design;
        # downstream AGENT_MAP check filters it.
        assert resolve_to_agent_map_key("security_agent") == "SecurityAgent"


# ─── should_force_dispatch ────────────────────────────────────────────────


class TestShouldForceDispatch:
    def _decision(self, **overrides):
        defaults = dict(
            app_slug="contract-concierge",
            requested={"mode": "force", "agent": "legal_doc_drafter_agent", "role": None},
            default_agent="legal_doc_drafter_agent",
            resolved_agent="legal_doc_drafter_agent",
            allowlist_hit=True,
            force_permitted=True,
            was_overridden=False,
        )
        defaults.update(overrides)
        return RoutingDecision(**defaults)

    def test_full_force_path(self):
        assert should_force_dispatch(self._decision()) is True

    def test_none_decision(self):
        assert should_force_dispatch(None) is False

    def test_hint_mode_never_force_dispatches(self):
        d = self._decision(
            requested={"mode": "hint", "agent": "legal_doc_drafter_agent", "role": None}
        )
        assert should_force_dispatch(d) is False

    def test_force_not_permitted_bails(self):
        d = self._decision(force_permitted=False)
        assert should_force_dispatch(d) is False

    def test_not_allowlisted_bails(self):
        d = self._decision(allowlist_hit=False)
        assert should_force_dispatch(d) is False

    def test_overridden_bails(self):
        d = self._decision(was_overridden=True, override_reason="not_allowlisted")
        assert should_force_dispatch(d) is False

    def test_no_resolved_agent_bails(self):
        d = self._decision(resolved_agent=None)
        assert should_force_dispatch(d) is False


# ─── apply_force_dispatch ─────────────────────────────────────────────────


class TestApplyForceDispatch:
    def _good_decision(self):
        return RoutingDecision(
            app_slug="contract-concierge",
            requested={"mode": "force", "agent": "legal_doc_drafter_agent", "role": None},
            default_agent="legal_doc_drafter_agent",
            resolved_agent="legal_doc_drafter_agent",
            allowlist_hit=True,
            force_permitted=True,
            was_overridden=False,
        )

    def test_dispatches_to_agent_map_key(self):
        user = MagicMock()
        fake_result = MagicMock(success=True, message="drafted", content="drafted", error=None)

        with patch("core.agent_router.AgentRouter") as mock_router_cls:
            instance = mock_router_cls.return_value
            instance.is_valid_agent.return_value = True
            instance.route.return_value = fake_result

            out = apply_force_dispatch(
                user=user,
                message="draft an NDA",
                decision=self._good_decision(),
                context={"workspace_id": "abc"},
                conversation_id="conv-1",
            )

            assert out is not None
            assert out["routed_to"] == "LegalDocDrafterAgent"
            assert out["intent"] == "fleet_force_dispatch"
            assert out["_phase2_dispatched"] is True
            assert out["_phase2_agent_map_key"] == "LegalDocDrafterAgent"
            assert out["tool_runs"][0]["source"] == "fleet_force_dispatch"
            instance.route.assert_called_once()
            call_kwargs = instance.route.call_args.kwargs
            assert call_kwargs["agent_name"] == "LegalDocDrafterAgent"
            assert call_kwargs["task"] == "draft an NDA"
            assert call_kwargs["context"]["_fleet_force_dispatch"] is True
            assert call_kwargs["trigger_source"] == "user_chat"

    def test_bails_when_resolved_agent_not_in_agent_map(self):
        user = MagicMock()

        with patch("core.agent_router.AgentRouter") as mock_router_cls:
            instance = mock_router_cls.return_value
            instance.is_valid_agent.return_value = False

            decision = RoutingDecision(
                app_slug="compliancesentinel",
                requested={"mode": "force", "agent": "security_agent", "role": None},
                default_agent=None,
                resolved_agent="security_agent",
                allowlist_hit=True,
                force_permitted=True,
                was_overridden=False,
            )
            out = apply_force_dispatch(
                user=user,
                message="audit me",
                decision=decision,
                context={},
                conversation_id="conv-x",
            )
            assert out is None
            instance.route.assert_not_called()

    def test_bails_when_router_raises(self):
        from core.agent_router import AgentNotFoundError

        user = MagicMock()
        with patch("core.agent_router.AgentRouter") as mock_router_cls:
            instance = mock_router_cls.return_value
            instance.is_valid_agent.return_value = True
            instance.route.side_effect = AgentNotFoundError("nope")

            out = apply_force_dispatch(
                user=user,
                message="draft an NDA",
                decision=self._good_decision(),
                context={},
                conversation_id="conv-1",
            )
            assert out is None


# ─── derive_hint_for_context ──────────────────────────────────────────────


class TestDeriveHintForContext:
    def _hint_decision(self, **overrides):
        defaults = dict(
            app_slug="pitchdeckforge",
            requested={"mode": "hint", "agent": "content_writer_agent", "role": None},
            default_agent="content_writer_agent",
            resolved_agent="content_writer_agent",
            allowlist_hit=True,
            force_permitted=False,
            was_overridden=False,
        )
        defaults.update(overrides)
        return RoutingDecision(**defaults)

    def test_none_decision(self):
        assert derive_hint_for_context(None) is None

    def test_happy_path_yields_hint(self):
        hint = derive_hint_for_context(self._hint_decision())
        assert hint is not None
        assert hint["agent_map_key"] == "ContentWriterAgent"
        assert hint["snake_name"] == "content_writer_agent"
        assert hint["app_slug"] == "pitchdeckforge"

    def test_overridden_bails(self):
        d = self._hint_decision(was_overridden=True, override_reason="not_allowlisted")
        assert derive_hint_for_context(d) is None

    def test_not_allowlisted_bails(self):
        d = self._hint_decision(allowlist_hit=False)
        assert derive_hint_for_context(d) is None

    def test_force_mode_does_not_demote_to_hint(self):
        # Rigby's rule: force already had its chance upstream; don't
        # silently demote to a hint here.
        d = self._hint_decision(
            requested={"mode": "force", "agent": "content_writer_agent", "role": None}
        )
        assert derive_hint_for_context(d) is None

    def test_unresolvable_snake_bails(self):
        # naïve fallback returns "ZzzzAgent" — not in explicit map, so
        # `resolve_to_agent_map_key` returns it but AGENT_MAP would
        # reject. derive_hint accepts the naïve guess so that the
        # downstream tool dispatcher (which uses snake_name, not the
        # AGENT_MAP key) can still try — that's fine because if the
        # snake_name isn't a registered tool either, it'll just no-op.
        # However if resolved_agent is empty, we MUST bail.
        d = self._hint_decision(resolved_agent=None)
        assert derive_hint_for_context(d) is None


@pytest.fixture(autouse=True)
def _clear_fleet_routing_cache():
    """Ensure each test sees a fresh routing config (no leakage)."""
    from core.services.fleet_routing import _load_config
    _load_config.cache_clear()
    yield
    _load_config.cache_clear()
