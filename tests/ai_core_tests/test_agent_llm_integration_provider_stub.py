"""Smoke test: OpenAIProvider.generate is a deprecated/unreachable stub.

Session 1217 Item 1 Bug B (audit deliverable bec077ed-…). The original method
body referenced an undefined ``messages`` variable and would have raised
NameError; the stub now raises NotImplementedError loudly so any future
caller gets a clear signal. Live OpenAI dispatch goes through
``core/services/openai_client_factory.py`` + ``AsyncLLMAdapter``.
"""

import pytest


@pytest.mark.asyncio
async def test_openai_provider_generate_raises_not_implemented(monkeypatch):
    # No real API key is needed — the stub raises before any client work.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from ai_core.agents.agent_llm_integration import OpenAIProvider

    provider = OpenAIProvider()

    with pytest.raises(NotImplementedError) as excinfo:
        await provider.generate("any prompt")

    assert "openai_client_factory" in str(excinfo.value)
