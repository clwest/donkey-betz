from types import SimpleNamespace

import pytest

import ai_core.spiders.spider_orchestrator as spider_orchestrator
import ai_core.spiders.spider_registry as spider_registry_module
import channels.layers as channels_layers


class _FakeSpider:
    async def start(self):
        return None

    async def get_collected_data(self):
        return []


class _FakeSpiderRegistry:
    def get_spider_class(self, spider_name):
        return object()

    def create_spider_instance(self, **kwargs):
        return _FakeSpider()


class _FakeChannelLayer:
    def __init__(self):
        self.group_send_calls = []

    async def group_send(self, group, payload):
        self.group_send_calls.append((group, payload))


@pytest.mark.asyncio
async def test_job_spiders_reports_mock_fallback_metadata(monkeypatch):
    monkeypatch.setattr(spider_registry_module, "SpiderRegistry", _FakeSpiderRegistry)
    async def _mock_opportunities(spider_name):
        return [{"platform": spider_name, "title": f"Mock {spider_name}"}]

    monkeypatch.setattr(spider_orchestrator, "generate_mock_job_opportunities", _mock_opportunities)
    monkeypatch.setattr(channels_layers, "get_channel_layer", lambda: _FakeChannelLayer())

    async def _noop_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(spider_orchestrator.asyncio, "sleep", _noop_sleep)

    result = await spider_orchestrator._activate_job_spiders_async()

    assert result["success"] is True
    assert result["fallback_used"] is True
    assert result["fallback_type"] == "mock_opportunities"
    assert result["real_data_failed"] is True
    assert result["partial_failure"] is True
    assert result["error_type"] == "no_real_data"
    assert result["collection_error"] == "no_real_data"
    assert len(result["collection_errors"]) == 5
    assert all(entry["fallback_type"] == "mock_opportunities" for entry in result["collection_errors"])


@pytest.mark.asyncio
async def test_job_spiders_keeps_clean_metadata_on_real_success(monkeypatch):
    class _RealSpider:
        async def start(self):
            return None

        async def get_collected_data(self):
            return [{"platform": "toptal", "title": "Real opportunity"}]

    class _RealSpiderRegistry(_FakeSpiderRegistry):
        def create_spider_instance(self, **kwargs):
            return _RealSpider()

    monkeypatch.setattr(spider_registry_module, "SpiderRegistry", _RealSpiderRegistry)
    monkeypatch.setattr(spider_orchestrator, "generate_mock_job_opportunities", pytest.fail)
    monkeypatch.setattr(channels_layers, "get_channel_layer", lambda: _FakeChannelLayer())

    async def _noop_sleep(*args, **kwargs):
        return None

    monkeypatch.setattr(spider_orchestrator.asyncio, "sleep", _noop_sleep)

    result = await spider_orchestrator._activate_job_spiders_async()

    assert result["success"] is True
    assert result["fallback_used"] is False
    assert result["fallback_type"] is None
    assert result["real_data_failed"] is False
    assert result["partial_failure"] is False
    assert result["collection_errors"] == []
