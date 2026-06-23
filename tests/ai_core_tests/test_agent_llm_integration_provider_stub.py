"""Session 1222 P1 (B2 follow-on) — lock-in test for the OpenAIProvider removal.

The Session 1217 PR #2507 audit (Item 1 Bug B) replaced ``OpenAIProvider.generate``
with a deprecation stub raising ``NotImplementedError`` while we waited for
telemetry confirmation that nothing in production actually invoked it.
Session 1222 P1 verification (AgentExecution + LLMCallEvent, all-time, all
``real_*`` agents + concrete_executor) returned **zero rows** — and the
``enable_agent_with_llm``-attached ``generate_llm_response`` /
``process_with_llm`` methods have **zero callers** across the codebase.

The class was therefore removed in Session 1222 P1. This test catches any
future regression that re-introduces it (intentionally or via a half-applied
revert). The previous version of this test asserted the stub raised
``NotImplementedError``; with the class gone, the contract becomes "not
importable from this module."
"""

import importlib


def test_openai_provider_no_longer_importable():
    """``OpenAIProvider`` was removed from this module in Session 1222 P1.
    A future re-introduction (intentional or accidental) should fail this
    test loudly before landing on main."""
    from ai_core.agents import agent_llm_integration as module

    assert not hasattr(module, 'OpenAIProvider'), (
        "OpenAIProvider was re-introduced into ai_core.agents.agent_llm_integration "
        "after Session 1222 P1 deleted it. Live OpenAI dispatch must continue to "
        "route through core/services/openai_client_factory + AsyncLLMAdapter, "
        "not this module."
    )


def test_singleton_default_provider_excludes_openai(monkeypatch):
    """The default-provider selector no longer has an ``'openai'`` branch.
    Even when ``OPENAI_API_KEY`` is set (the legacy trigger), the default
    must fall through to ``'anthropic'`` or ``'mock'``."""
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-fake-key-for-test')
    monkeypatch.delenv('ANTHROPIC_API_KEY', raising=False)

    from ai_core.agents import agent_llm_integration as module
    importlib.reload(module)

    assert module.agent_llm_integration.default_provider == 'mock', (
        "Default provider must fall through to 'mock' when no ANTHROPIC_API_KEY "
        "is set — OpenAI is no longer a valid default in this module."
    )
    assert 'openai' not in module.agent_llm_integration.providers, (
        "providers dict must not contain an 'openai' key after Session 1222 P1."
    )


def test_anthropic_and_mock_providers_still_registered():
    """``AnthropicProvider`` and ``MockLLMProvider`` are intentionally
    preserved for any future caller that wants this surface; only the
    OpenAI branch was removed."""
    from ai_core.agents.agent_llm_integration import agent_llm_integration

    assert 'anthropic' in agent_llm_integration.providers
    assert 'mock' in agent_llm_integration.providers
