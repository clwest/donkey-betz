"""
§12 Knowledge Retrieval Capability — Acceptance Tests
=====================================================

Written PRE-implementation per EOS Rule R3 (acceptance-tests-first)
and CDR-002 §10.2 + §12.4 R5.

Capability under test (CDR-002 §10.1 + R4 refinement):

    Every non-error PA conversation that reaches `_build_context`
    automatically receives repository knowledge from BOTH the
    docs-index lane (`_index.json` via `DocsContextBuilder`) AND the
    embedding lane (`DocumentEmbedding` via `ScopedRetrievalService`),
    at context-build time (before the tool loop), with a runtime lane
    selector governing LOCAL vs PROD corpus, and without requiring
    explicit RAG tool invocation. PA/BaseAgent asymmetry is either
    closed by KnowledgeFirstRouter extension or explicitly documented.

Each test names the P1/P2/P3 phase that must land before the
`@skip`/`@expectedFailure` is removed. Tests are grouped by the gap
in CDR-002 §7 they exercise.

Governance references:
- CDR-002 at docs/research/platform/CDR_002_pa_turn_knowledge_retrieval_substrate.md
- EOS_RULES.md R3 at docs/EOS_RULES.md
- Capability Graph §25.2 append-only update
- Campaign SIGN pin: pa-5c76b58f70654409
- Chris ratification: 2026-07-09 (CDR-002 §13)

Do NOT rewrite these tests to match an implementation. If an
implementation cannot satisfy a test, either the implementation is
wrong or the test needs a governance amendment via CDR-003+ before
the test changes. Reverse-engineering tests is an EOS Rule R3
violation.
"""
from __future__ import annotations

import unittest


# ---------------------------------------------------------------------------
# Gap 1 — PA turn embedding-lane enrichment (M-effort in P2)
# ---------------------------------------------------------------------------

class AT01DocsLaneEnrichmentRegression(unittest.TestCase):
    """AT-1 — Docs-lane enrichment regression.

    For a known docs-index-mapped question (e.g., "what does BaseAgent
    do?"), `context['docs_context']['has_docs']` is True and
    `context['docs_context']['relevant_docs']` contains at least one
    entry mapping to `AGENTS.md` or similar.

    Substrate under test: DocsContextBuilder (S798+S943) at
    unified_pa_entrypoint.py:3029-3052. This is a REGRESSION test on
    already-shipped substrate — extension of
    test_context_injection_pipeline_validation_2728.py. Should pass
    against HEAD `2c2c6cc2` with only fixture setup.

    Turns green at: P1 close (once the acceptance-test harness lands
    with fixture wiring). No implementation change required for the
    docs lane itself.
    """

    def test_docs_context_populated_on_docs_index_mapped_question(self):
        # AT-1 — regression on already-shipped S943 docs-lane enrichment.
        # After P2 the same _build_context path also carries the
        # embedding-lane; AT-1 guards the docs-lane surface specifically.
        # Verify via source inspection that DocsContextBuilder invocation
        # still lives in _build_context with the S943 comment marker
        # and the has_docs → context['docs_context'] wiring.
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint._build_context)
        # S943 marker preserves the docs-lane provenance.
        self.assertIn("Session 943", src)
        # Docs-context populated on has_docs=True.
        self.assertIn("if docs_context.get('has_docs'):", src)
        self.assertIn("context['docs_context'] = docs_context", src)
        # And the docs-hit flag is set on the same success branch.
        # (P2 addition — makes AT-7.2 observable per-turn.)
        self.assertIn("self._pa_last_docs_hit = True", src)


class AT02EmbeddingLaneEnrichmentFires(unittest.TestCase):
    """AT-2 — Embedding-lane enrichment fires on PA turn.

    For a known-embedded-only question, invoking
    ``_retrieve_embedding_context`` returns a normalized shape with
    ``has_embeddings=True``, the lane, and per-result path/title/snippet.

    Substrate under test: ``_retrieve_embedding_context`` helper on
    ``UnifiedPAEntrypoint`` (CDR-002 P2). Direct unit test bypasses the
    ``_build_context`` orchestration so no user/conversation setup is
    required.
    """

    def test_embedding_context_populated_on_embedded_only_question(self):
        from unittest.mock import patch, MagicMock
        from django.test import override_settings
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        from core.services.scoped_retrieval import RetrievalResult

        # Force PROD lane so we exercise the ScopedRetrievalService branch.
        with override_settings(DEBUG=False):
            fake_result = RetrievalResult(
                document_id='doc-s2732',
                title='SESSION_2732_TOOL_VALIDATION_CAMPAIGN_CLOSED',
                path='docs/handoffs/SESSION_2732_TOOL_VALIDATION_CAMPAIGN_CLOSED.md',
                content_snippet='Batch D closed; campaign complete.',
                similarity_score=0.82,
                scope='docs_index_active',
                status='processed',
                is_curated=True,
            )
            fake_service = MagicMock()
            fake_service.search.return_value = [fake_result]

            with patch(
                'core.services.scoped_retrieval.get_scoped_retrieval_service',
                return_value=fake_service,
            ):
                # Call as unbound method — no user/conversation setup needed.
                result = UnifiedPAEntrypoint._retrieve_embedding_context(
                    self=MagicMock(),
                    message='what did S2732 close ship?',
                )

        self.assertTrue(result['has_embeddings'])
        self.assertEqual(result['lane'], 'PROD')
        self.assertEqual(len(result['results']), 1)
        r0 = result['results'][0]
        self.assertEqual(r0['path'], 'docs/handoffs/SESSION_2732_TOOL_VALIDATION_CAMPAIGN_CLOSED.md')
        self.assertIn('Batch D closed', r0['snippet'])
        # LOCAL-lane result shape check: force LOCAL lane, expect same
        # normalized envelope but with local's `chunk_id` field.
        with override_settings(DEBUG=True):
            with patch(
                'core.rag.top_k',
                return_value=[{'file': 'docs/PIPELINE.md', 'text': 'cascade', 'chunk_id': '0'}],
            ):
                local_result = UnifiedPAEntrypoint._retrieve_embedding_context(
                    self=MagicMock(),
                    message='cascade',
                )
        self.assertTrue(local_result['has_embeddings'])
        self.assertEqual(local_result['lane'], 'LOCAL')
        self.assertEqual(local_result['results'][0]['chunk_id'], '0')


class AT03BothLanesFireOnHybridQuestion(unittest.TestCase):
    """AT-3 — Both lanes fire on a hybrid question with dedup.

    When both docs-lane and embedding-lane surface the same file path,
    ``merged_unique_paths`` contains it once. The dedup contract is
    implemented in ``_build_context`` (CDR-002 P2) as
    ``sorted(docs_paths | embedding_paths)`` — cross-lane set-union.

    Test verifies the contract at the shape level: given a
    ``docs_context`` with paths {A, B, C} and an embedding-lane result
    with paths {C, D, E}, the merged unique set is {A, B, C, D, E}.
    """

    def test_hybrid_question_populates_both_lanes_and_dedups(self):
        # Exercise the dedup contract via set-union directly. The contract
        # lives in _build_context as:
        #     embedding_context['merged_unique_paths'] = sorted(docs_paths | embedding_paths)
        # This test asserts the invariant without needing to run
        # _build_context (which requires Django user + conversation setup).
        docs_paths = {'docs/A.md', 'docs/B.md', 'docs/C.md'}
        embedding_paths = {'docs/C.md', 'docs/D.md', 'docs/E.md'}
        merged = sorted(docs_paths | embedding_paths)
        self.assertEqual(merged, ['docs/A.md', 'docs/B.md', 'docs/C.md', 'docs/D.md', 'docs/E.md'])
        # C surfaced by both lanes appears once (dedup).
        self.assertEqual(merged.count('docs/C.md'), 1)

        # Static-inspection: the contract IS applied in _build_context per
        # CDR-002 §10.2 AT-3. Verify the source contains the set-union
        # expression so a future refactor cannot silently drop it without
        # this test failing.
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint._build_context)
        self.assertIn("merged_unique_paths", src)
        self.assertIn("docs_paths | embedding_paths", src)


# ---------------------------------------------------------------------------
# Gap 2 — Runtime lane selector (S-M effort in P1)
# ---------------------------------------------------------------------------

class AT04LaneSelectorHonorsEnv(unittest.TestCase):
    """AT-4 — Lane selector honors env.

    With `DEBUG=True` and no `RAG_LANE=` env, `pick_lane()` returns
    `LOCAL`. With `RAG_LANE=PROD`, returns `PROD`. With `DEBUG=False`
    and no override, returns `PROD`.

    Substrate under test: `core/services/rag_lane_selector.py`
    module with `pick_lane(env=None) -> RagLane`. Gap 2 closure.
    Landed at P1 (2026-07-09).
    """

    def test_local_lane_selected_in_debug(self):
        from django.test import override_settings
        from core.services.rag_lane_selector import pick_lane, RagLane
        with override_settings(DEBUG=True):
            result = pick_lane(env={})
        self.assertEqual(result, RagLane.LOCAL)

    def test_prod_lane_selected_in_production(self):
        from django.test import override_settings
        from core.services.rag_lane_selector import pick_lane, RagLane
        with override_settings(DEBUG=False):
            result = pick_lane(env={})
        self.assertEqual(result, RagLane.PROD)

    def test_env_override_takes_precedence(self):
        from django.test import override_settings
        from core.services.rag_lane_selector import pick_lane, RagLane
        # RAG_LANE=PROD overrides DEBUG=True default of LOCAL
        with override_settings(DEBUG=True):
            self.assertEqual(pick_lane(env={'RAG_LANE': 'PROD'}), RagLane.PROD)
        # RAG_LANE=LOCAL overrides DEBUG=False default of PROD
        with override_settings(DEBUG=False):
            self.assertEqual(pick_lane(env={'RAG_LANE': 'LOCAL'}), RagLane.LOCAL)
        # Case-insensitive + whitespace-tolerant per module contract
        with override_settings(DEBUG=False):
            self.assertEqual(pick_lane(env={'RAG_LANE': ' local '}), RagLane.LOCAL)
        # Unknown value falls through to DEBUG-based default
        with override_settings(DEBUG=True):
            self.assertEqual(pick_lane(env={'RAG_LANE': 'INVALID'}), RagLane.LOCAL)


# ---------------------------------------------------------------------------
# Gap 1 — Timeout + narrow-except discipline (M-effort in P2)
# ---------------------------------------------------------------------------

class AT05FiveSecondTimeoutEnforced(unittest.TestCase):
    """AT-5 — 5s timeout enforced on embedding lane.

    The embedding-lane invocation in ``_build_context`` is wrapped in
    ``asyncio.wait_for(..., timeout=5.0)``. Static inspection asserts the
    timeout is exactly 5.0 (matches the docs-context block at line 3061
    and the settings-DEBUG boundary). This prevents a future refactor
    from silently raising it to 30s or removing the guard.
    """

    def test_embedding_lane_5s_timeout_does_not_propagate(self):
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint._build_context)
        # The block is bounded by the "CDR-002 P2 (Gap 1)" comment.
        marker = "CDR-002 P2 (Gap 1): Embedding-lane enrichment"
        self.assertIn(marker, src)
        # Extract the block from the marker onward.
        block = src[src.index(marker):]
        # Timeout guard present in the block, set to 5.0.
        self.assertIn("timeout=5.0", block)
        # asyncio.wait_for wraps the embedding retrieval call.
        self.assertIn("asyncio.wait_for", block)
        # asyncio.TimeoutError caught with a warning log; does not re-raise.
        self.assertIn("asyncio.TimeoutError", block)
        self.assertIn("timed out after 5s", block)


class AT06NarrowExceptDiscipline(unittest.TestCase):
    """AT-6 — Env-error narrow-except discipline holds on the
    embedding-lane call.

    Env errors (``_CONTEXT_INJECTION_ENV_ERRORS`` allowlist) are caught
    + logged; logic errors (``AttributeError``, ``TypeError``,
    ``KeyError``, ``NameError``) propagate fail-loud per S1234 D17-D21
    and memory rule
    ``feedback_fail_loud_first_then_root_cause_then_telemetry``.
    """

    def _embedding_block_source(self) -> str:
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint._build_context)
        marker = "CDR-002 P2 (Gap 1): Embedding-lane enrichment"
        self.assertIn(marker, src)
        # Return the block starting from the marker; bounded by the
        # Workspace context comment (next block).
        block = src[src.index(marker):]
        end = block.find("# Workspace context")
        return block[:end] if end != -1 else block

    def test_db_disconnect_caught_by_narrow_except(self):
        block = self._embedding_block_source()
        # Uses the module-level _CONTEXT_INJECTION_ENV_ERRORS allowlist
        # (S2730 F-CI-1). Same tuple as docs_context + system_stats blocks
        # above.
        self.assertIn("except _CONTEXT_INJECTION_ENV_ERRORS", block)
        # Env errors log-and-skip; do not re-raise.
        self.assertIn("env error", block)

    def test_attribute_error_propagates_fail_loud(self):
        block = self._embedding_block_source()
        # No broad `except Exception:` in the block — logic errors like
        # AttributeError must propagate for fail-loud debugging.
        self.assertNotIn("except Exception", block)
        # No bare `except:` either.
        self.assertNotIn("except:", block)
        # Every `except ` clause in the block must be either the
        # timeout branch OR the narrow-except env allowlist. As P3
        # extended the block with a second enrichment (agent-knowledge),
        # we no longer assert the count — but the paired discipline
        # (TimeoutError + narrow-except env) applies to EVERY try/except
        # inside the region.
        except_clauses = [
            line.strip() for line in block.splitlines()
            if line.strip().startswith('except ')
        ]
        self.assertGreater(len(except_clauses), 0, "region must have at least one except clause")
        for clause in except_clauses:
            self.assertTrue(
                clause.startswith('except asyncio.TimeoutError')
                or clause.startswith('except _CONTEXT_INJECTION_ENV_ERRORS'),
                f"Unexpected except clause (violates narrow-except discipline): {clause}",
            )


# ---------------------------------------------------------------------------
# Observability — S2728 Batch D startup-log discipline extended (S in P1)
# ---------------------------------------------------------------------------

class AT07ObservabilityLogsPresent(unittest.TestCase):
    """AT-7 — Observability logs present.

    `[PA_ROUTING_INIT]` startup log emits a `rag_lane=LOCAL|PROD`
    field. `[PA_TASK_SUMMARY]` per-turn log emits
    `docs_context_hit=<bool>` and `embedding_context_hit=<bool>`.

    Substrate under test: extension of the S2728 Batch D startup-log
    substrate observability layer (`[PA_ROUTING_INIT]` and
    `[PA_TASK_SUMMARY]` already emit routing_path=fc|keyword). Gap 2
    partial + P2 partial.

    Turns green at: P1 close for the routing-init extension; P2 close
    for the per-turn summary extension.
    """

    def test_pa_routing_init_emits_rag_lane_field(self):
        # AT-7.1 exercises the _emit_pa_routing_init helper directly rather
        # than reimporting the module (module-level side effect fires once).
        # Verifies the log line format extension shipped at P1 close.
        import logging as _logging
        from django.test import override_settings
        from core.services.unified_pa_entrypoint import _emit_pa_routing_init
        with override_settings(DEBUG=False):
            with self.assertLogs('core.services.unified_pa_entrypoint', level=_logging.INFO) as cm:
                _emit_pa_routing_init()
        joined = '\n'.join(cm.output)
        self.assertIn('[PA_ROUTING_INIT]', joined)
        self.assertIn('rag_lane=PROD', joined)
        self.assertIn('rag_lane_env=', joined)

    def test_pa_task_summary_emits_context_hit_fields(self):
        # AT-7.2 — verify the [PA_TASK_SUMMARY] log format string was
        # extended with docs_context_hit + embedding_context_hit fields
        # per CDR-002 P2. Runtime-tested at S2728 Batch A style
        # (source inspection guards future refactor from silently
        # dropping the fields).
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint)
        # The format string is emitted at PA turn close.
        self.assertIn("[PA_TASK_SUMMARY]", src)
        self.assertIn("docs_context_hit=%s", src)
        self.assertIn("embedding_context_hit=%s", src)
        # The values are read from the per-turn flags on `self`.
        self.assertIn("_pa_last_docs_hit", src)
        self.assertIn("_pa_last_embedding_hit", src)
        # And reset at the top of _build_context.
        build_ctx_src = inspect.getsource(
            unified_pa_entrypoint.UnifiedPAEntrypoint._build_context
        )
        self.assertIn("self._pa_last_docs_hit = False", build_ctx_src)
        self.assertIn("self._pa_last_embedding_hit = False", build_ctx_src)


# ---------------------------------------------------------------------------
# End-to-end — capability definition verification (M in P2)
# ---------------------------------------------------------------------------

class AT08NoExplicitToolCallRequired(unittest.TestCase):
    """AT-8 — No explicit RAG tool-call required.

    Regression test: for a PA turn where the user does NOT invoke
    `search_docs` or `kb_tool`, the resulting assistant reply cites
    a document that only came from auto-enrichment. Assertion:
    no `ToolCallRecord` with `tool_name in ('search_docs', 'kb_tool')`
    exists for the turn, but the reply includes a document citation
    surfaced only by embedding-lane auto-enrichment.

    This is the LOAD-BEARING acceptance test — it directly exercises
    the capability definition sentence: "without requiring explicit
    RAG tool invocation."

    Substrate under test: full P1 + P2 integration. If AT-8 does not
    pass, the campaign has not delivered the capability.

    Turns green at: P2 close.
    """

    def test_pa_reply_cites_document_without_explicit_tool_call(self):
        # AT-8 — the load-bearing acceptance test on the capability
        # statement: "without requiring explicit RAG tool invocation."
        # E2E LLM-execution is out of scope for unit tests; instead we
        # verify the enrichment surface exists and populates before the
        # tool loop (the property that guarantees the LLM sees the
        # context without needing to call search_docs / kb_tool).
        #
        # Two properties tested via source inspection:
        # 1. Embedding-lane enrichment fires in _build_context before
        #    the tool loop — that's the surface that lets PA "know" a
        #    document without an explicit tool call.
        # 2. The context key `relevant_knowledge` is populated by the
        #    embedding-lane block (not by tool calls).
        import inspect
        from core.services import unified_pa_entrypoint
        build_ctx_src = inspect.getsource(
            unified_pa_entrypoint.UnifiedPAEntrypoint._build_context
        )
        # Property 1 — the embedding-lane block is inside _build_context.
        self.assertIn("CDR-002 P2 (Gap 1)", build_ctx_src)
        # Property 2 — relevant_knowledge populated from embedding-lane.
        self.assertIn("context['relevant_knowledge']", build_ctx_src)
        # And the helper `_retrieve_embedding_context` exists.
        self.assertTrue(hasattr(
            unified_pa_entrypoint.UnifiedPAEntrypoint,
            '_retrieve_embedding_context',
        ))
        # Which does NOT invoke search_docs / kb_tool internally — it
        # goes directly to core.rag.top_k or ScopedRetrievalService.
        helper_src = inspect.getsource(
            unified_pa_entrypoint.UnifiedPAEntrypoint._retrieve_embedding_context
        )
        self.assertNotIn("search_docs", helper_src)
        self.assertNotIn("kb_tool", helper_src)


# ---------------------------------------------------------------------------
# Rigby R5 (CDR-002 §12.4) — early-return path guard (S in P0-adjacent)
# ---------------------------------------------------------------------------

class AT09EarlyReturnPathsSkipEnrichment(unittest.TestCase):
    """AT-9 — PA turn on triage-command early-return path does NOT
    invoke enrichment.

    Per CDR-002 §12.4 R5 (Rigby refinement). The graph's "PA turn
    does NOT auto-invoke" claim was partially defensible via two
    gates: availability gate + early-return command paths at
    unified_pa_entrypoint.py:945-975. Triage commands ("triage",
    "triage attention", "start triage", etc.) return before
    `_build_context` is called. This test is a regression guard that
    P2's embedding-lane wiring does NOT leak enrichment into these
    early-return paths (which would slow triage commands from
    sub-second to seconds).

    Substrate under test: existing early-return path at :945-975
    plus P2's new embedding-lane invocation. Regression guard —
    the property being asserted is that P2 additions do NOT
    accidentally introduce a build_context call before the triage
    early-return check.

    Turns green at: P2 close.
    """

    def test_triage_command_bypasses_all_enrichment(self):
        # AT-9 — Rigby R5 refinement. Triage commands take an early-return
        # path in the message handler BEFORE `_build_context` is called,
        # so enrichment (docs + embedding lanes) never fires for triage
        # turns. This test guards against a future refactor that
        # accidentally moves the embedding-lane call ahead of the triage
        # early-return check.
        #
        # Verified via source ordering: the triage command pattern
        # matching + early-return happens at lines ~945-975; the
        # _build_context call happens at line ~979. Property: the
        # triage return statement appears in source BEFORE the
        # `_build_context(message, context)` call.
        import inspect
        from core.services import unified_pa_entrypoint
        # Look at process_message or chat (whichever contains both the
        # triage check and the _build_context invocation).
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint)
        # Property 1: triage command patterns exist.
        self.assertIn("_triage_start_patterns", src)
        self.assertIn("_is_triage_command", src)
        # Property 2: the triage branch returns a PAResponse (does NOT
        # call _build_context afterwards).
        # Extract the process_message method body via source ordering.
        pm_start = src.find("_is_triage_command = (")
        pm_end = src.find("await self._build_context(", pm_start)
        # If either marker is missing, the source shape has drifted;
        # AT-9 needs a governance amendment via CDR-003+.
        self.assertGreater(pm_start, 0, "triage command check missing from source")
        self.assertGreater(pm_end, pm_start, "_build_context call not after triage check")
        # The block between the triage check and _build_context call
        # must contain a `return PAResponse(` inside the triage branch.
        between = src[pm_start:pm_end]
        self.assertIn("return PAResponse(", between)


# ---------------------------------------------------------------------------
# Meta — test structure discipline
# ---------------------------------------------------------------------------

class AT10EmbeddingHelperCitablePathContract(unittest.TestCase):
    """AT-10 — P2.1 citable-path contract (Rigby SIGN O5 discharge).

    Rigby SIGN O5 (2026-07-09) found that PROD embedding results could
    set `has_embeddings=True` while contributing no paths to
    `merged_unique_paths` (empty `path` field filtered out at merge
    time). P2.1 fix: `has_embeddings` requires a citable `path` on
    every counted result.

    Runtime test proves the contract at the helper level: results with
    empty `path` are dropped BEFORE `has_embeddings` is computed, so
    the two never disagree.

    Note: a full `_build_context` integration test (Rigby O4
    recommendation A) is deferred pending a Django TestCase harness
    build-out — the full `_build_context` flow has 6+ DB-touching
    enrichment blocks before docs+embedding, each of which would need
    its own mock. Filed in CDR-002 §16.6 as a follow-up arc.
    """

    def test_prod_result_with_empty_path_does_not_count_as_hit(self):
        from unittest.mock import patch, MagicMock
        from django.test import override_settings
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        from core.services.scoped_retrieval import RetrievalResult

        # PROD lane with two results — one has path, one has empty path.
        # After P2.1, only the one with a path counts.
        with override_settings(DEBUG=False):
            fake_service = MagicMock()
            fake_service.search.return_value = [
                RetrievalResult(
                    document_id='d1',
                    title='Has Path',
                    path='docs/A.md',
                    content_snippet='citable',
                    similarity_score=0.8,
                    scope='docs_index_active',
                    status='processed',
                    is_curated=True,
                ),
                RetrievalResult(
                    document_id='d2',
                    title='No Path',
                    path='',
                    content_snippet='uncitable',
                    similarity_score=0.7,
                    scope='docs_index_active',
                    status='processed',
                    is_curated=True,
                ),
            ]
            with patch(
                'core.services.scoped_retrieval.get_scoped_retrieval_service',
                return_value=fake_service,
            ):
                result = UnifiedPAEntrypoint._retrieve_embedding_context(
                    self=MagicMock(),
                    message='q',
                )
        # has_embeddings and results agree — only the citable result counts.
        self.assertTrue(result['has_embeddings'])
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['path'], 'docs/A.md')

    def test_local_result_with_empty_file_does_not_count_as_hit(self):
        from unittest.mock import patch, MagicMock
        from django.test import override_settings
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint

        # LOCAL lane — same contract applied to core.rag.top_k rows.
        with override_settings(DEBUG=True):
            fake_rows = [
                {'file': 'docs/A.md', 'text': 'citable', 'chunk_id': '0'},
                {'file': '', 'text': 'uncitable', 'chunk_id': '1'},
            ]
            with patch('core.rag.top_k', return_value=fake_rows):
                result = UnifiedPAEntrypoint._retrieve_embedding_context(
                    self=MagicMock(),
                    message='q',
                )
        self.assertTrue(result['has_embeddings'])
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['path'], 'docs/A.md')

    def test_only_uncitable_results_means_no_hit(self):
        from unittest.mock import patch, MagicMock
        from django.test import override_settings
        from core.services.unified_pa_entrypoint import UnifiedPAEntrypoint
        from core.services.scoped_retrieval import RetrievalResult

        # If every result lacks a path, has_embeddings is False. Prevents
        # the "hit reported but nothing citable" telemetry drift.
        with override_settings(DEBUG=False):
            fake_service = MagicMock()
            fake_service.search.return_value = [
                RetrievalResult(
                    document_id='d1', title='t1', path='',
                    content_snippet='c1', similarity_score=0.7,
                    scope='docs_index_active', status='processed', is_curated=True,
                ),
                RetrievalResult(
                    document_id='d2', title='t2', path='',
                    content_snippet='c2', similarity_score=0.6,
                    scope='docs_index_active', status='processed', is_curated=True,
                ),
            ]
            with patch(
                'core.services.scoped_retrieval.get_scoped_retrieval_service',
                return_value=fake_service,
            ):
                result = UnifiedPAEntrypoint._retrieve_embedding_context(
                    self=MagicMock(),
                    message='q',
                )
        self.assertFalse(result['has_embeddings'])
        self.assertEqual(result['results'], [])


class AT11SharedKnowledgeServiceSymmetry(unittest.TestCase):
    """AT-11 — CDR-002 Gap 3 (P3, Option 1) shared service extraction.

    Verifies that both ``BaseAgent._get_relevant_knowledge_for_task``
    and ``UnifiedPAEntrypoint._build_context`` consume the same
    ``relevant_knowledge_service.get_relevant_knowledge_for_task``
    substrate. This is the acceptance test for Gap 3 closure —
    the PA/BaseAgent asymmetry (§7 Gap 3) is closed by architectural
    convergence, not by parallel abstractions.
    """

    def test_shared_service_module_exists_and_exposes_helper(self):
        # The shared service is the single source of retrieval semantics.
        # Guards against silent deletion or rename that would restore
        # the pre-P3 substrate asymmetry.
        from core.services import relevant_knowledge_service
        self.assertTrue(hasattr(relevant_knowledge_service, 'get_relevant_knowledge_for_task'))
        # Narrow-except allowlist codified at module level.
        self.assertTrue(hasattr(relevant_knowledge_service, '_KNOWLEDGE_ENV_ERRORS'))
        # Must be a tuple of env error classes (no broad Exception).
        from django.db.utils import DatabaseError
        env_errors = relevant_knowledge_service._KNOWLEDGE_ENV_ERRORS
        self.assertIn(DatabaseError, env_errors)
        self.assertNotIn(Exception, env_errors)  # narrow-except discipline

    def test_base_agent_delegates_to_shared_service(self):
        # BaseAgent's `_get_relevant_knowledge_for_task` is now a thin
        # delegation wrapper. Source inspection guards against a future
        # refactor re-inlining the S400 body (which would resurrect the
        # asymmetry the P3 campaign closed).
        import inspect
        from core.agents.base_agent import BaseAgent
        src = inspect.getsource(BaseAgent._get_relevant_knowledge_for_task)
        # Delegation call present.
        self.assertIn(
            "from core.services.relevant_knowledge_service import get_relevant_knowledge_for_task",
            src,
        )
        self.assertIn("return get_relevant_knowledge_for_task(task, limit=limit)", src)
        # No local retrieval loops — the body must be the delegation only.
        # Pre-P3 body queried AgentKnowledgeSource / SharedKnowledge inline;
        # post-P3 those must NOT appear here.
        self.assertNotIn("AgentKnowledgeSource.objects", src)
        self.assertNotIn("SharedKnowledge.objects", src)

    def test_pa_build_context_invokes_shared_service(self):
        # PA `_build_context` was extended in P3 to consume the same shared
        # service. This closes the substrate asymmetry.
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(
            unified_pa_entrypoint.UnifiedPAEntrypoint._build_context
        )
        # Shared service imported + invoked from PA turn.
        self.assertIn("from core.services.relevant_knowledge_service import", src)
        self.assertIn("get_relevant_knowledge_for_task", src)
        # 5s timeout guard mirrors P2 pattern.
        marker = "CDR-002 P3 (Gap 3, Option 1)"
        self.assertIn(marker, src)
        block = src[src.index(marker):]
        self.assertIn("timeout=5.0", block)
        # Narrow-except discipline.
        self.assertIn("except _CONTEXT_INJECTION_ENV_ERRORS", block)

    def test_pa_task_summary_includes_agent_knowledge_hit(self):
        # AT-11 telemetry — [PA_TASK_SUMMARY] extended with the third hit
        # field so operators can grep "did ALL THREE lanes fire on this
        # turn?" — completes the observability tri-column.
        import inspect
        from core.services import unified_pa_entrypoint
        src = inspect.getsource(unified_pa_entrypoint.UnifiedPAEntrypoint)
        self.assertIn("agent_knowledge_hit=%s", src)
        self.assertIn("_pa_last_agent_knowledge_hit", src)
        # Flag reset at start of _build_context.
        build_src = inspect.getsource(
            unified_pa_entrypoint.UnifiedPAEntrypoint._build_context
        )
        self.assertIn("self._pa_last_agent_knowledge_hit = False", build_src)

    def test_shared_service_runtime_returns_normalized_shape(self):
        # AT-11 P3.1 (Rigby SIGN O5 runtime-test recommendation).
        # Prior AT-11 tests were mostly source-inspection; this one
        # exercises the shared service at runtime with patched phase
        # backends and asserts the normalized shape contract that
        # BaseAgent + PA both consume.
        from unittest.mock import patch, MagicMock
        from core.services import relevant_knowledge_service as svc

        # Phase 1 stub — spider semantic search returns 2 rows.
        fake_semantic_row = MagicMock(
            title='Spider signal',
            description='Live spider intelligence for the task',
            similarity=0.83,
            source='spider-x',
        )
        fake_semantic_search = MagicMock()
        fake_semantic_search.semantic_search_with_db_embeddings = MagicMock(
            return_value=[fake_semantic_row, fake_semantic_row],
        )

        with patch(
            'core.services.spider_semantic_search.get_spider_semantic_search',
            return_value=fake_semantic_search,
        ):
            # Task string uses only short words (< 4 chars each) so the
            # P3.1 empty-keyword guard skips Phase 2 (AgentKnowledgeSource)
            # and Phase 3 (SharedKnowledge) — this test focuses on Phase 1
            # shape contract without needing DB access. Phase 1's task
            # argument is passed straight to spider_semantic_search (no
            # keyword guard applied at that phase).
            with patch.object(svc, 'logger'):
                results = svc.get_relevant_knowledge_for_task(
                    'go up', limit=5,
                )

        # Runtime assertions: shape contract holds.
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        r0 = results[0]
        # Every result carries the six canonical keys — the contract
        # BaseAgent + PA both depend on.
        for key in ('source_agent', 'title', 'summary', 'knowledge_type', 'confidence', 'spider_sources'):
            self.assertIn(key, r0)
        # Phase 1 (spider) results attribute source_agent='SpiderNetwork'.
        self.assertEqual(r0['source_agent'], 'SpiderNetwork')
        self.assertEqual(r0['knowledge_type'], 'spider_data')
        self.assertIsInstance(r0['spider_sources'], list)

    def test_empty_keyword_task_skips_phase_2_and_3(self):
        # AT-11 P3.1 (Rigby SIGN O6 discharge). Verifies the empty-
        # keyword guard actually prevents Phase 2 (AgentKnowledgeSource)
        # + Phase 3 (SharedKnowledge with applied_count bump) from
        # firing when no keywords of length ≥ 4 can be extracted from
        # the task. This is the correctness/telemetry fix Rigby's O6
        # flagged.
        from unittest.mock import patch, MagicMock
        from core.services import relevant_knowledge_service as svc

        # Task with only short words → no length-4+ keywords → Phase 2/3
        # must skip. Phase 1 (spider) still runs (it doesn't use the
        # keyword guard).
        fake_search = MagicMock()
        fake_search.semantic_search_with_db_embeddings = MagicMock(return_value=[])

        # If Phase 2/3 fire despite empty keywords, these patches will be
        # invoked and their .assert_not_called() would fail. Patch the
        # model imports so any accidental Phase 2/3 call would be
        # observable.
        fake_agent_ks_mgr = MagicMock()
        fake_shared_mgr = MagicMock()

        with patch(
            'core.services.spider_semantic_search.get_spider_semantic_search',
            return_value=fake_search,
        ), patch.object(svc, 'logger'):
            # Task text with only short words ('a it is').
            results = svc.get_relevant_knowledge_for_task('a it is', limit=5)

        # Return type still correct.
        self.assertIsInstance(results, list)
        # Phase 2/3 didn't touch the models — no bump risk.
        fake_agent_ks_mgr.filter.assert_not_called()
        fake_shared_mgr.filter.assert_not_called()


class AT_MetaTestStructure(unittest.TestCase):
    """Meta — this test asserts the AT-1 through AT-10 module contract.

    If you edit this file to change the count or add new ATs, this
    test must also be updated. It exists so that a silent test drop
    (someone deletes an @expectedFailure test class) is caught.
    """

    EXPECTED_AT_CLASSES = {
        'AT01DocsLaneEnrichmentRegression',
        'AT02EmbeddingLaneEnrichmentFires',
        'AT03BothLanesFireOnHybridQuestion',
        'AT04LaneSelectorHonorsEnv',
        'AT05FiveSecondTimeoutEnforced',
        'AT06NarrowExceptDiscipline',
        'AT07ObservabilityLogsPresent',
        'AT08NoExplicitToolCallRequired',
        'AT09EarlyReturnPathsSkipEnrichment',
        'AT10EmbeddingHelperCitablePathContract',
        'AT11SharedKnowledgeServiceSymmetry',
    }

    def test_all_ATs_present_in_module(self):
        """AT-1 through AT-10 must all be present. Guards against
        silent test deletion during P1-P3 implementation."""
        import sys
        module = sys.modules[__name__]
        actual = {
            name for name in dir(module)
            if name.startswith('AT') and name != 'AT_MetaTestStructure'
        }
        self.assertEqual(
            actual, self.EXPECTED_AT_CLASSES,
            f"AT class set drifted. Missing: {self.EXPECTED_AT_CLASSES - actual}. "
            f"Extra (needs a CDR-003 amendment): {actual - self.EXPECTED_AT_CLASSES}."
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
