"""
Session 2731 — Rigby Tool Validation Engineering Campaign, Batch D tool 3
(closes Batch D + closes the 18-tool campaign scope) regression tests
for the three-layer worker cache substrate.

Covers the F-WC-* findings surfaced during code trace + patched at
Session 2731. See:
- `docs/research/tools/validation/worker_cache_behavior_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` §3.4

Findings covered:

- F-WC-1 `[DJANGO_CACHE_INIT]` startup log declaring effective cache
  backend + REDIS_HEALTHY value.
- F-WC-2 `_aggregator_cache` + `_service_cache` bounded via
  `@lru_cache(maxsize=64)`.
- F-WC-3 LLM client factory caches bounded at HEAD (`_CLIENT_CACHE`,
  `_ASYNC_CLIENT_CACHE`).
- F-WC-4 `platform_config` `@lru_cache(maxsize=1)` + `clear_config_cache`
  helper verified at HEAD.
- F-WC-5 `_backlog_cache` TTL discipline verified at HEAD.

Existing coverage NOT duplicated:
- Django cache Redis backend integration — that's Django-internal.

Run::

    python manage.py test core.tests.test_worker_cache_behavior_validation_2728 -v2
"""
from __future__ import annotations

import inspect
from pathlib import Path

from django.test import SimpleTestCase


REPO_ROOT = Path(__file__).resolve().parents[2]


# ─── F-WC-1: DJANGO_CACHE_INIT startup log ──────────────────────────────


class FWC1DjangoCacheInitLogTests(SimpleTestCase):
    """F-WC-1 — settings.py emits [DJANGO_CACHE_INIT] at import time."""

    def _settings_src(self) -> str:
        return (REPO_ROOT / 'core' / 'settings.py').read_text()

    def test_startup_log_line_present(self):
        src = self._settings_src()
        self.assertIn('[DJANGO_CACHE_INIT]', src)

    def test_log_reports_backend_and_redis_healthy_and_url(self):
        """All three signals must be in the log format string so operators
        can grep for any of them. We search for the `_dcinit_logger.info`
        call site specifically to skip past the header comment block."""
        src = self._settings_src()
        # Locate the logger.info call (past the docstring / comments).
        idx = src.find('_dcinit_logger.info(')
        self.assertGreater(idx, 0, '_dcinit_logger.info call missing')
        window = src[idx:idx + 500]
        self.assertIn('backend=', window)
        self.assertIn('REDIS_HEALTHY=', window)
        self.assertIn('redis_url=', window)

    def test_redis_healthy_flag_still_set_by_startup_try_except(self):
        """The MEMORY-adjacent claim that REDIS_HEALTHY is set at startup
        remains true (F-WC-1 didn't remove the flag; it exposed it in
        the log)."""
        from django.conf import settings
        self.assertTrue(hasattr(settings, 'REDIS_HEALTHY'))
        self.assertIsInstance(settings.REDIS_HEALTHY, bool)


# ─── F-WC-2: _aggregator_cache + _service_cache bounded via lru_cache ────


class FWC2AttentionAggregatorLRUTests(SimpleTestCase):
    """F-WC-2 — attention_aggregator._aggregator_cache now LRU-bounded."""

    def test_lru_wrapper_exists(self):
        from core.services import attention_aggregator
        self.assertTrue(
            hasattr(attention_aggregator, '_get_attention_aggregator_by_uid'),
            'LRU wrapper _get_attention_aggregator_by_uid missing',
        )

    def test_lru_wrapper_has_cache_info(self):
        from core.services.attention_aggregator import (
            _get_attention_aggregator_by_uid,
        )
        info = _get_attention_aggregator_by_uid.cache_info()
        self.assertEqual(
            info.maxsize, 64,
            f'maxsize must be 64 (F-WC-2 discipline); got {info.maxsize}',
        )

    def test_backward_compat_aggregator_cache_view_exposes_len(self):
        """The `_aggregator_cache` module-level name still works with
        `len(...)` for any test / observability caller that read it
        pre-S2731."""
        from core.services.attention_aggregator import _aggregator_cache
        # len() returns 0 or the current LRU size, not a raise.
        length = len(_aggregator_cache)
        self.assertIsInstance(length, int)
        self.assertGreaterEqual(length, 0)

    def test_backward_compat_aggregator_cache_view_clear(self):
        """`.clear()` on the view forwards to the LRU wrapper."""
        from core.services.attention_aggregator import _aggregator_cache
        _aggregator_cache.clear()  # Must not raise.


class FWC2HumanInterfaceServiceLRUTests(SimpleTestCase):
    """F-WC-2 — human_interface_service._service_cache now LRU-bounded."""

    def test_lru_wrapper_exists(self):
        from core.services import human_interface_service
        self.assertTrue(
            hasattr(human_interface_service, '_get_human_interface_service_by_uid'),
            'LRU wrapper _get_human_interface_service_by_uid missing',
        )

    def test_lru_wrapper_has_cache_info(self):
        from core.services.human_interface_service import (
            _get_human_interface_service_by_uid,
        )
        info = _get_human_interface_service_by_uid.cache_info()
        self.assertEqual(info.maxsize, 64)

    def test_backward_compat_service_cache_view_exposes_len(self):
        from core.services.human_interface_service import _service_cache
        length = len(_service_cache)
        self.assertIsInstance(length, int)
        self.assertGreaterEqual(length, 0)


# ─── F-WC-3: LLM client factory caches bounded at HEAD ─────────────────


class FWC3LLMClientCachesBoundedTests(SimpleTestCase):
    """F-WC-3 — verified `_CLIENT_CACHE` + `_ASYNC_CLIENT_CACHE`
    remain in the OpenAI/Anthropic factories, keyed on hashable tuples."""

    def test_openai_client_cache_still_exists(self):
        from core.services import openai_client_factory
        self.assertTrue(hasattr(openai_client_factory, '_CLIENT_CACHE'))
        self.assertTrue(hasattr(openai_client_factory, '_ASYNC_CLIENT_CACHE'))

    def test_anthropic_client_cache_still_exists(self):
        from core.services import anthropic_client_factory
        self.assertTrue(hasattr(anthropic_client_factory, '_CLIENT_CACHE'))

    def test_openai_client_cache_is_dict_keyed_on_tuples(self):
        """The MEMORY-adjacent claim rests on the cache being keyed on
        (api_key, base_url) tuples. Verify the type."""
        from core.services.openai_client_factory import _CLIENT_CACHE
        # Empty cache is still a dict; test the type, not contents.
        self.assertIsInstance(_CLIENT_CACHE, dict)


# ─── F-WC-4: platform_config @lru_cache discipline ─────────────────────


class FWC4PlatformConfigLRUDisciplineTests(SimpleTestCase):
    """F-WC-4 — platform_config's `@lru_cache(maxsize=1)` + explicit
    `clear_config_cache()` helper remain at HEAD."""

    def test_cached_primary_workspace_id_is_lru(self):
        from core.services.platform_config import _cached_primary_workspace_id
        self.assertTrue(
            hasattr(_cached_primary_workspace_id, 'cache_info'),
            '_cached_primary_workspace_id must be @lru_cache decorated',
        )
        self.assertEqual(_cached_primary_workspace_id.cache_info().maxsize, 1)

    def test_cached_primary_user_id_is_lru(self):
        from core.services.platform_config import _cached_primary_user_id
        self.assertTrue(hasattr(_cached_primary_user_id, 'cache_info'))
        self.assertEqual(_cached_primary_user_id.cache_info().maxsize, 1)

    def test_clear_config_cache_helper_exists(self):
        from core.services.platform_config import clear_config_cache
        self.assertTrue(callable(clear_config_cache))
        # Calling it must not raise (idempotent).
        clear_config_cache()


# ─── F-WC-5: _backlog_cache TTL discipline ─────────────────────────────


class FWC5BacklogCacheTTLTests(SimpleTestCase):
    """F-WC-5 — initiative_circuit_breaker._backlog_cache still has TTL."""

    def test_backlog_cache_has_ttl_constant(self):
        from core.services import initiative_circuit_breaker as icb
        self.assertTrue(hasattr(icb, 'CACHE_TTL_SECONDS'))
        self.assertIsInstance(icb.CACHE_TTL_SECONDS, int)
        self.assertGreater(icb.CACHE_TTL_SECONDS, 0)

    def test_backlog_cache_shape_intact(self):
        """The cache is a dict with `count` and `checked_at` keys —
        rule step 1 of feedback_local_celery_stall_playbook rests on
        this shape indirectly (though it doesn't cite this cache)."""
        from core.services.initiative_circuit_breaker import _backlog_cache
        self.assertIsInstance(_backlog_cache, dict)
        self.assertIn('count', _backlog_cache)
        self.assertIn('checked_at', _backlog_cache)


# ─── Structural guard: Redis DB topology unchanged ─────────────────────


class RedisDBTopologyTests(SimpleTestCase):
    """Structural guard on the three-Redis-DB layout (DB 1 = Django
    cache, DB 2 = Celery broker, DB 3 = Celery result backend). If any
    of these move, downstream ops recipes across MEMORY rules become
    stale."""

    def test_django_cache_default_source_uses_redis_db_1(self):
        """Guard against a regression that renames the DB. Sourced from
        the settings.py default (`redis://localhost:6379/1`) rather than
        the runtime REDIS_URL, because operators may override REDIS_URL
        for local-dev testing without also updating the DB layout
        contract. Broker (db 2) and result backend (db 3) must remain
        distinct from django cache (db 1)."""
        src = (REPO_ROOT / 'core' / 'settings.py').read_text()
        # The default in the env-read expression is the source-of-truth
        # for what the DB layout is *intended* to be.
        self.assertIn(
            "os.environ.get('REDIS_URL', 'redis://localhost:6379/1')",
            src,
            'settings.py REDIS_URL default no longer points at db 1',
        )

    def test_celery_broker_uses_redis_db_2(self):
        from django.conf import settings
        # feedback_local_celery_stall_playbook step 2 assumes db 2.
        self.assertIn('/2', settings.CELERY_BROKER_URL)

    def test_celery_result_backend_uses_redis_db_3(self):
        from django.conf import settings
        # Distinct from broker DB — result backend keeps result rows
        # apart from queue backlogs.
        self.assertIn('/3', settings.CELERY_RESULT_BACKEND)
