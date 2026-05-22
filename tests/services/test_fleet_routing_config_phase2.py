"""Tests for `config/fleet_agent_routing.json` (Session 1127 Phase 2A).

Compliancesentinel was the only fleet app whose default agent
(`security_agent`) had no matching `SecurityAgent` in AGENT_MAP — Phase 2A
would silently bail for it. Per Rigby's guidance, the config now defaults
`compliancesentinel` to null (no default) and empties its allowlist;
behavior of all other apps must be unchanged.
"""
from __future__ import annotations

import pytest

from core.services.fleet_routing import _load_config, resolve


@pytest.fixture(autouse=True)
def _clear_cache():
    _load_config.cache_clear()
    yield
    _load_config.cache_clear()


def test_compliancesentinel_has_no_default():
    decision = resolve("compliancesentinel", None)
    assert decision.default_agent is None
    assert decision.resolved_agent is None


def test_compliancesentinel_empty_allowlist_force_request_downgrades():
    # Even with force mode, an empty allowlist means the request
    # downgrades — was_overridden=True so Phase 2A bails out.
    decision = resolve(
        "compliancesentinel",
        {"mode": "force", "agent": "security_agent"},
    )
    assert decision.allowlist_hit is False
    # force_allowed for compliancesentinel was never set to true, so
    # force_permitted should be False.
    assert decision.force_permitted is False
    assert decision.was_overridden is True


def test_other_apps_unchanged_contract_concierge_force_dispatches():
    # contract-concierge's force path must still resolve cleanly.
    decision = resolve(
        "contract-concierge",
        {"mode": "force", "agent": "legal_doc_drafter_agent"},
    )
    assert decision.resolved_agent == "legal_doc_drafter_agent"
    assert decision.allowlist_hit is True
    assert decision.force_permitted is True
    assert decision.was_overridden is False


def test_pitchdeckforge_hint_still_resolves():
    decision = resolve(
        "pitchdeckforge",
        {"mode": "hint", "agent": "content_writer_agent"},
    )
    assert decision.resolved_agent == "content_writer_agent"
    assert decision.allowlist_hit is True
    assert decision.was_overridden is False


def test_signal_studio_force_default_path():
    decision = resolve("signal-studio", {"mode": "force", "agent": "trend_analysis_agent"})
    assert decision.resolved_agent == "trend_analysis_agent"
    assert decision.force_permitted is True
    assert decision.allowlist_hit is True
