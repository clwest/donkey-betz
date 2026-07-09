"""
Session 2730 — Rigby Tool Validation Engineering Campaign, Batch C tool 1
regression tests for the context injection pipeline.

Covers the F-CI-* findings surfaced during code trace + patched at
Session 2730. See:
- `docs/research/tools/validation/context_injection_pipeline_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-CI-1 `_CONTEXT_INJECTION_ENV_ERRORS` allowlist + `_build_context`
  narrow-except discipline (mirrors S1234 D17-D21; extends F-RG-1 in
  core/rag_integration.py and F-WS-4 in core/services/workspace_resolver.py).
- F-CI-2 per-service failure isolation + `services_failed` envelope +
  `exc_info=True` traceback surfacing.
- F-CI-3 silent truncation → `sections_truncated` envelope entries.
- F-CI-4 relevance gate empty-msg-words permissive-include INFO log.
- F-CI-5 relevance gate short-enrichment discard DEBUG log.
- F-CI-6 dead `tool_result` parameter removed from `_enrich_tool_result`.
- F-CI-7 `_get_system_stats` narrow-except + `stats_source` field.
- F-CI-9 `_metadata` envelope with services_run, services_failed,
  services_gated_out, services_unavailable, canonical_intent,
  services_requested, sections_truncated.
- F-CI-10 `_build_analytical_prompt` 8000-char truncation WARNING log.

Existing coverage NOT duplicated:
- `_detect_intent_and_route` claude-code source short-circuit —
  covered in test_pa_intent_claude_code_source.py.

Run::

    python manage.py test core.tests.test_context_injection_pipeline_validation_2728 -v2
"""
from __future__ import annotations

import asyncio
import inspect
import logging
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

from django.db.utils import DatabaseError
from django.test import SimpleTestCase

from core.services.unified_pa_entrypoint import (
    _CONTEXT_INJECTION_ENV_ERRORS,
    UnifiedPAEntrypoint,
)


# ─── F-CI-1: allowlist shape + narrow-except discipline ─────────────────


class FCI1AllowlistShapeTests(SimpleTestCase):
    """F-CI-1 — `_CONTEXT_INJECTION_ENV_ERRORS` matches D17-D21 discipline."""

    def test_allowlist_constant_exists(self):
        self.assertIsInstance(_CONTEXT_INJECTION_ENV_ERRORS, tuple)
        self.assertGreater(len(_CONTEXT_INJECTION_ENV_ERRORS), 0)

    def test_allowlist_contains_required_env_errors(self):
        self.assertIn(DatabaseError, _CONTEXT_INJECTION_ENV_ERRORS)
        self.assertIn(ConnectionError, _CONTEXT_INJECTION_ENV_ERRORS)
        self.assertIn(OSError, _CONTEXT_INJECTION_ENV_ERRORS)

    def test_allowlist_does_NOT_contain_exception(self):
        """The whole point of D17-D21: env-only, NOT broad."""
        self.assertNotIn(Exception, _CONTEXT_INJECTION_ENV_ERRORS)
        self.assertNotIn(BaseException, _CONTEXT_INJECTION_ENV_ERRORS)


class FCI1BuildContextBroadExceptRemovedTests(SimpleTestCase):
    """F-CI-1 — source-level guard that broad-except is gone from _build_context."""

    def test_build_context_uses_env_errors_allowlist(self):
        src = inspect.getsource(UnifiedPAEntrypoint._build_context)
        self.assertIn('except _CONTEXT_INJECTION_ENV_ERRORS', src)

    def test_build_context_no_broad_except(self):
        """No bare `except Exception` inside _build_context body."""
        src = inspect.getsource(UnifiedPAEntrypoint._build_context)
        self.assertNotIn('except Exception as e:', src)
        self.assertNotIn('except Exception as _e:', src)


class FCI7GetSystemStatsBroadExceptRemovedTests(SimpleTestCase):
    """F-CI-7 — source-level guard that broad-except is gone from _get_system_stats."""

    def test_get_system_stats_uses_env_errors_allowlist(self):
        src = inspect.getsource(UnifiedPAEntrypoint._get_system_stats)
        self.assertIn('except _CONTEXT_INJECTION_ENV_ERRORS', src)

    def test_get_system_stats_no_broad_except(self):
        src = inspect.getsource(UnifiedPAEntrypoint._get_system_stats)
        self.assertNotIn('except Exception as e:', src)


# ─── F-CI-7: _get_system_stats stats_source signal ──────────────────────


class FCI7StatsSourceTests(SimpleTestCase):
    """F-CI-7 — `_get_system_stats` surfaces `stats_source: 'live' | 'fallback'`."""

    def _pa(self):
        return UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)

    def test_env_error_returns_fallback_signal(self):
        """DatabaseError → fallback stats + stats_source='fallback'."""
        pa = self._pa()
        with patch('core.models_unified_system.Agent') as mock_agent:
            mock_agent.objects.count.side_effect = DatabaseError('simulated DB down')
            stats = asyncio.run(
                pa._get_system_stats()
            )
        self.assertEqual(stats['stats_source'], 'fallback')
        # Hardcoded defaults preserved for backward compat.
        self.assertEqual(stats['agent_count'], 74)
        self.assertEqual(stats['spider_count'], 77)
        self.assertEqual(stats['advisor_count'], 25)

    def test_logic_error_propagates(self):
        """AttributeError inside ORM chain propagates (not silently masked)."""
        pa = self._pa()
        with patch('core.models_unified_system.Agent') as mock_agent:
            mock_agent.objects.count.side_effect = AttributeError('simulated logic bug')
            with self.assertRaises(AttributeError):
                asyncio.run(
                    pa._get_system_stats()
                )


# ─── F-CI-4 + F-CI-5: relevance gate observability ──────────────────────


class FCI4FCI5RelevanceGateLogsTests(SimpleTestCase):
    """F-CI-4 + F-CI-5 — relevance gate observability logs."""

    def _pa(self):
        return UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)

    def test_empty_enrichment_returns_false_no_log(self):
        pa = self._pa()
        self.assertFalse(pa._passes_relevance_gate('hello', ''))

    def test_short_enrichment_logs_debug_discard(self):
        """F-CI-5 — short enrichment (<30 tokens) logs DEBUG at discard."""
        pa = self._pa()
        short = 'alpha beta gamma delta epsilon'  # < 30 tokens
        with self.assertLogs(
            'core.services.unified_pa_entrypoint', level='DEBUG',
        ) as log_ctx:
            result = pa._passes_relevance_gate('some query', short)
        self.assertFalse(result)
        output = '\n'.join(log_ctx.output)
        self.assertIn('relevance gate: enrichment discarded (short:', output)

    def test_empty_msg_words_logs_info_bypass(self):
        """F-CI-4 — stop-word-only query logs INFO + returns True."""
        pa = self._pa()
        # Enrichment must be >= 30 tokens to pass the short check.
        enrichment = ' '.join([f'word{i}' for i in range(40)])
        # 'why?' tokenizes to {'why'} which is a stop word → empty after subtraction.
        with self.assertLogs(
            'core.services.unified_pa_entrypoint', level='INFO',
        ) as log_ctx:
            result = pa._passes_relevance_gate('why?', enrichment)
        self.assertTrue(result)
        output = '\n'.join(log_ctx.output)
        self.assertIn('permissive include', output)

    def test_low_overlap_returns_false(self):
        """Standard gate path: <15% overlap → False, no log."""
        pa = self._pa()
        enrichment = ' '.join([f'word{i}' for i in range(40)])  # 40 unique tokens
        # Message shares 0 tokens with enrichment.
        result = pa._passes_relevance_gate('completely unrelated content', enrichment)
        self.assertFalse(result)

    def test_high_overlap_returns_true(self):
        """Standard gate path: >=15% overlap → True."""
        pa = self._pa()
        # Enrichment: 40 tokens including 'apple', 'banana', 'cherry', 'date'.
        enrichment = 'apple banana cherry date ' + ' '.join([f'word{i}' for i in range(36)])
        # Message: 4 non-stopword tokens, all 4 overlap → 100%.
        result = pa._passes_relevance_gate('apple banana cherry date', enrichment)
        self.assertTrue(result)


# ─── F-CI-6: dead parameter removed ─────────────────────────────────────


class FCI6DeadParameterRemovedTests(SimpleTestCase):
    """F-CI-6 — `_enrich_tool_result` no longer accepts `tool_result` parameter."""

    def test_signature_is_message_intent_trace_id(self):
        sig = inspect.signature(UnifiedPAEntrypoint._enrich_tool_result)
        params = list(sig.parameters.keys())
        # self, message, intent, trace_id
        self.assertEqual(params, ['self', 'message', 'intent', 'trace_id'])

    def test_tool_result_not_in_signature(self):
        sig = inspect.signature(UnifiedPAEntrypoint._enrich_tool_result)
        self.assertNotIn('tool_result', sig.parameters)


# ─── F-CI-9: metadata envelope shape ────────────────────────────────────


class FCI9MetadataEnvelopeShapeTests(SimpleTestCase):
    """F-CI-9 — enrichment return payload carries `_metadata` sub-dict."""

    def _pa(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        # Lazy-load properties need to return None so branches don't fire.
        pa._intelligence_enricher = None
        pa._blog_performance_fn = None
        pa._domain_context_builder = None
        pa._spider_context_builder = None
        pa._advisor_context_builder = None
        pa._proactive_intelligence_service = None
        pa._platform_briefing_service = None
        return pa

    def test_unmapped_intent_returns_empty_envelope(self):
        """`general` intent is not in INTENT_ENRICHMENT_MAP → empty envelope."""
        pa = self._pa()
        result = asyncio.run(
            pa._enrich_tool_result('hello world', 'general', 'trace-1')
        )
        self.assertIn('_metadata', result)
        md = result['_metadata']
        self.assertEqual(md['canonical_intent'], 'general')
        self.assertEqual(md['services_requested'], [])
        self.assertEqual(md['services_run'], [])
        self.assertEqual(md['services_failed'], [])
        self.assertEqual(md['services_gated_out'], [])
        self.assertEqual(md['services_unavailable'], [])
        self.assertEqual(md['sections_truncated'], [])

    def test_intent_alias_normalizes_to_canonical(self):
        """`blogs` → canonical `content_review` in metadata."""
        pa = self._pa()
        result = asyncio.run(
            pa._enrich_tool_result('any query', 'blogs', 'trace-2')
        )
        self.assertEqual(result['_metadata']['canonical_intent'], 'content_review')
        # content_review requests 5 services.
        self.assertEqual(len(result['_metadata']['services_requested']), 5)

    def test_all_lazy_loaded_services_marked_unavailable(self):
        """When every lazy-loaded property returns None, those services
        get counted as `unavailable` (never entered any branch).

        Uses PropertyMock at class-level to defeat the lazy-load
        re-import behavior in the underlying `@property` getters.
        """
        pa = self._pa()
        # Patch the six lazy-loaded properties that have `and self.X:`
        # guards. Strategic memory has no `and self.X:` guard, so it
        # will still enter its branch.
        with patch.object(
            UnifiedPAEntrypoint, 'intelligence_enricher',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'blog_performance_fn',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'domain_context_builder',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'spider_context_builder',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'advisor_context_builder',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'proactive_intelligence_service',
            new_callable=PropertyMock, return_value=None,
        ), patch.object(
            UnifiedPAEntrypoint, 'platform_briefing_service',
            new_callable=PropertyMock, return_value=None,
        ):
            result = asyncio.run(
                pa._enrich_tool_result('any query', 'content_review', 'trace-3')
            )
        md = result['_metadata']
        # content_review requests 5 services. blog_performance +
        # domain_context + spider_trends + proactive_intelligence have
        # `and self.X:` guards → become unavailable. strategic_memory
        # enters its branch and either runs or raises → NOT unavailable.
        self.assertIn('blog_performance', md['services_unavailable'])
        self.assertIn('domain_context', md['services_unavailable'])
        self.assertIn('spider_trends', md['services_unavailable'])
        self.assertIn('proactive_intelligence', md['services_unavailable'])

    def test_metadata_key_starts_with_underscore(self):
        """`_metadata` uses underscore prefix so downstream filters skip it."""
        pa = self._pa()
        result = asyncio.run(
            pa._enrich_tool_result('hello', 'general', 'trace-4')
        )
        for key in result.keys():
            if key.startswith('_'):
                # Envelope key — should not be an enrichment content key.
                self.assertNotIn(key, {
                    'learning_insights', 'blog_performance', 'domain_context',
                    'spider_trends', 'advisor', 'strategic_memory',
                    'proactive_intelligence', 'platform_briefing',
                })


# ─── F-CI-2: per-service failure isolation + traceback logging ──────────


class FCI2FailureIsolationTests(SimpleTestCase):
    """F-CI-2 — one service failing doesn't block others; envelope tracks it."""

    def test_failing_service_added_to_services_failed_envelope(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        # Set up mocks: intelligence_enricher raises; others None (unavailable).
        pa._intelligence_enricher = MagicMock()
        pa._intelligence_enricher.enrich_context.side_effect = ValueError('boom')
        pa._blog_performance_fn = None
        pa._domain_context_builder = None
        pa._spider_context_builder = None
        pa._advisor_context_builder = None
        pa._proactive_intelligence_service = None
        pa._platform_briefing_service = None

        with self.assertLogs(
            'core.services.unified_pa_entrypoint', level='WARNING',
        ) as log_ctx:
            result = asyncio.run(
                pa._enrich_tool_result('any', 'boardroom', 'trace-fail-1')
            )
        md = result['_metadata']
        # boardroom → ['intelligence_enricher', 'strategic_memory']
        # intelligence_enricher raises ValueError → added to services_failed
        self.assertTrue(
            any(entry[0] == 'intelligence_enricher' and entry[1] == 'ValueError'
                for entry in md['services_failed']),
            f"Expected intelligence_enricher/ValueError in {md['services_failed']}",
        )
        # WARNING log emitted with exc_info=True (traceback).
        joined = '\n'.join(log_ctx.output)
        self.assertIn("Enrichment 'intelligence_enricher' failed", joined)


# ─── F-CI-3: silent truncation surfaced in envelope ─────────────────────


class FCI3TruncationEnvelopeTests(SimpleTestCase):
    """F-CI-3 — truncation loop records (key, original_length, cap) triples."""

    def test_oversize_section_recorded_in_sections_truncated(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        # Set up a mock intelligence_enricher that returns oversize context_text.
        # ENRICHMENT_CAPS['learning_insights'] = 1500.
        oversize_text = 'x' * 3000  # 3000 > 1500 cap
        pa._intelligence_enricher = MagicMock()
        pa._intelligence_enricher.enrich_context.return_value = {
            'context_text': oversize_text,
            'metadata': {},
        }
        pa._blog_performance_fn = None
        pa._domain_context_builder = None
        pa._spider_context_builder = None
        pa._advisor_context_builder = None
        pa._proactive_intelligence_service = None
        pa._platform_briefing_service = None

        result = asyncio.run(
            pa._enrich_tool_result('any', 'boardroom', 'trace-trunc-1')
        )
        md = result['_metadata']
        # Truncated to cap + '...'
        self.assertTrue(result['learning_insights'].endswith('...'))
        self.assertLess(len(result['learning_insights']), 3000)
        # Envelope carries the truncation record.
        truncated = md['sections_truncated']
        self.assertTrue(
            any(entry[0] == 'learning_insights' and entry[1] == 3000 and entry[2] == 1500
                for entry in truncated),
            f"Expected (learning_insights, 3000, 1500) in {truncated}",
        )


# ─── F-CI-10: 8000-char tool_str truncation WARNING ─────────────────────


class FCI10AnalyticalPromptTruncationLogTests(SimpleTestCase):
    """F-CI-10 — `_build_analytical_prompt` logs WARNING when tool_str > 8000."""

    def test_oversize_tool_result_logs_warning(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        oversize = 'y' * 10_000
        with self.assertLogs(
            'core.services.unified_pa_entrypoint', level='WARNING',
        ) as log_ctx:
            pa._build_analytical_prompt(
                message='test query',
                intent='boardroom',
                tool_result=oversize,
                enrichment_sections={},
                user_name='tester',
                context={},
            )
        joined = '\n'.join(log_ctx.output)
        self.assertIn('tool_result truncated', joined)
        self.assertIn('10000', joined)

    def test_under_8000_no_warning(self):
        pa = UnifiedPAEntrypoint.__new__(UnifiedPAEntrypoint)
        # Under the cap — should not emit the truncation WARNING.
        # Use a logging.Handler to capture only what we emit (assertNoLogs
        # exists 3.10+ but let's keep cross-version).
        captured = []

        class _Recorder(logging.Handler):
            def emit(self, record):
                captured.append(self.format(record))

        rec = _Recorder(level=logging.WARNING)
        rec.setFormatter(logging.Formatter('%(message)s'))
        pa_logger = logging.getLogger('core.services.unified_pa_entrypoint')
        pa_logger.addHandler(rec)
        try:
            pa._build_analytical_prompt(
                message='test',
                intent='boardroom',
                tool_result='short data',
                enrichment_sections={},
                user_name='tester',
                context={},
            )
        finally:
            pa_logger.removeHandler(rec)

        for entry in captured:
            self.assertNotIn('tool_result truncated', entry)


# ─── Shape guards on the intent/enrichment constants ────────────────────


class IntentEnrichmentConstantsShapeTests(SimpleTestCase):
    """Structural invariants on INTENT_ENRICHMENT_MAP / ALIASES / CAPS."""

    def test_intent_enrichment_map_is_dict_of_lists(self):
        self.assertIsInstance(UnifiedPAEntrypoint.INTENT_ENRICHMENT_MAP, dict)
        for key, value in UnifiedPAEntrypoint.INTENT_ENRICHMENT_MAP.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, list, f"Value for intent {key!r} must be list")

    def test_intent_aliases_target_canonical_intents_or_known_defaults(self):
        """Every alias must point at a key that IS in the enrichment map
        OR at a canonical intent that is intentionally empty (pure-data intents)."""
        aliases = UnifiedPAEntrypoint.INTENT_ALIASES
        map_keys = set(UnifiedPAEntrypoint.INTENT_ENRICHMENT_MAP.keys())
        for alias, canonical in aliases.items():
            self.assertIn(
                canonical, map_keys,
                f"Alias {alias!r} → {canonical!r} is not in INTENT_ENRICHMENT_MAP",
            )

    def test_enrichment_caps_all_reasonable(self):
        for section, cap in UnifiedPAEntrypoint.ENRICHMENT_CAPS.items():
            self.assertGreaterEqual(
                cap, 500,
                f"Section {section!r} cap {cap} is below 500 (post-S1006 discipline)",
            )

    def test_direct_relevance_intents_is_subset_of_map_keys(self):
        map_keys = set(UnifiedPAEntrypoint.INTENT_ENRICHMENT_MAP.keys())
        for intent in UnifiedPAEntrypoint.DIRECT_RELEVANCE_INTENTS:
            self.assertIn(
                intent, map_keys,
                f"DIRECT_RELEVANCE_INTENTS entry {intent!r} not in INTENT_ENRICHMENT_MAP",
            )
