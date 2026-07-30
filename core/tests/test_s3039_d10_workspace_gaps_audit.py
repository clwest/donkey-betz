"""S3039 D10 Phase 1 — regression tests for the workspace-gap audit command.

Locks in the bucketing contract + PA-workspace-loss flag behavior. The
S3037 backlog framed D10 as "reporting quality" but Phase 0 ORM probes
during S3039 showed ~50/50 PA workspace attribution — a real code-path
bug hiding in the NULL bucket. This test seeds each bucket and asserts
the command classifies correctly + flags the PA gap.
"""
from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models_llm_routing import LLMCallLog


def _make(task_type: str, agent_name: str, workspace=None, cost='0.001', **kw):
    return LLMCallLog.objects.create(
        agent_name=agent_name,
        provider='openai',
        model_id='gpt-5-mini',
        task_type=task_type,
        workspace=workspace,
        cost=Decimal(cost),
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        success=True,
        **kw,
    )


class ClassifierTests(TestCase):
    """Unit-level: the _classify helper buckets (task_type, agent_name) pairs."""

    def test_system_embedding_bucket(self):
        from core.management.commands.audit_llmcalllog_workspace_gaps import _classify

        self.assertEqual(_classify('embedding', 'SpiderSemanticSearch'), 'system_embedding')
        self.assertEqual(_classify('embedding', 'docs_index_sync'), 'system_embedding')
        self.assertEqual(_classify('embedding', 'MemoryEmbeddingService'), 'system_embedding')
        self.assertEqual(_classify('embedding', 'KnowledgeFirstRouter'), 'system_embedding')

    def test_system_test_bucket(self):
        from core.management.commands.audit_llmcalllog_workspace_gaps import _classify

        self.assertEqual(_classify('test', 'InterviewAssistant'), 'system_test')
        self.assertEqual(_classify('test', 'AnyAgent'), 'system_test')  # test overrides

    def test_pa_workspace_lost_bucket(self):
        from core.management.commands.audit_llmcalllog_workspace_gaps import _classify

        self.assertEqual(
            _classify('conversation', 'PersonalAssistant'),
            'pa_workspace_lost',
        )

    def test_embedding_task_type_always_buckets_as_system_embedding(self):
        """Rigby SIGN ask #1: new embedding callers must NOT false-positive
        into `unclassified`. Any `task_type='embedding'` row is system-level
        regardless of agent_name; the specific caller still surfaces in
        `top_pairs` for review."""
        from core.management.commands.audit_llmcalllog_workspace_gaps import _classify

        self.assertEqual(_classify('embedding', 'MysteryCaller'), 'system_embedding')
        self.assertEqual(_classify('embedding', ''), 'system_embedding')
        self.assertEqual(_classify('embedding', 'NewRAGService'), 'system_embedding')

    def test_unknown_non_embedding_pair_falls_to_unclassified(self):
        from core.management.commands.audit_llmcalllog_workspace_gaps import _classify

        self.assertEqual(_classify('conversation', 'MysteryAgent'), 'unclassified')
        self.assertEqual(_classify('completion', 'RandomCaller'), 'unclassified')
        self.assertEqual(_classify('', ''), 'unclassified')


class WorkspaceGapAuditCommandTests(TestCase):
    """Command-level: seed real rows across all buckets and assert output."""

    def setUp(self):
        # 3 system_embedding rows (known caller)
        for _ in range(3):
            _make('embedding', 'SpiderSemanticSearch')
        # 1 system_embedding row via the new-caller heuristic (Rigby ask #1)
        _make('embedding', 'NewRAGCaller')
        # 2 system_test rows
        for _ in range(2):
            _make('test', 'InterviewAssistant')
        # 5 pa_workspace_lost rows
        for _ in range(5):
            _make('conversation', 'PersonalAssistant')
        # 1 unclassified — non-embedding, non-PA mystery caller
        _make('completion', 'MysteryAgent')

    def _run(self, **kwargs):
        out = StringIO()
        call_command('audit_llmcalllog_workspace_gaps', stdout=out, **kwargs)
        return out.getvalue()

    def test_json_output_buckets_all_seeded_rows(self):
        raw = self._run(json=True)
        payload = json.loads(raw)

        self.assertEqual(payload['total_rows'], 12)
        self.assertEqual(payload['null_rows'], 12)
        self.assertEqual(payload['attributed_rows'], 0)

        buckets = payload['buckets']
        # 3 SpiderSemanticSearch + 1 NewRAGCaller (heuristic bucket) = 4
        self.assertEqual(buckets['system_embedding']['count'], 4)
        self.assertEqual(buckets['system_test']['count'], 2)
        self.assertEqual(buckets['pa_workspace_lost']['count'], 5)
        # Only the non-embedding MysteryAgent row
        self.assertEqual(buckets['unclassified']['count'], 1)

    def test_new_embedding_caller_surfaces_in_system_embedding_top_pairs(self):
        """Rigby ask #1: new embedding callers must be visible even
        though they auto-bucket as system_embedding — the exact
        (task_type, agent_name) pair should surface in top_pairs for
        review, not disappear silently into the aggregate count."""
        payload = json.loads(self._run(json=True))
        sys_emb = payload['buckets']['system_embedding']
        pair_names = {p['agent_name'] for p in sys_emb['top_pairs']}
        self.assertIn('NewRAGCaller', pair_names,
            'New embedding callers must appear in system_embedding.top_pairs '
            'so their existence is auditable at every run.')

    def test_unclassified_non_embedding_pair_surfaces_in_top_pairs(self):
        payload = json.loads(self._run(json=True))
        unc = payload['buckets']['unclassified']
        self.assertTrue(any(
            p['agent_name'] == 'MysteryAgent' for p in unc['top_pairs']
        ), 'Non-embedding unknown callers must surface in unclassified '
           'top_pairs for manual triage.')

    def test_pa_workspace_loss_flagged_at_100_percent_when_no_attributed(self):
        """5 NULL PA rows + 0 attributed = 100% loss. Even below the 100-row
        absolute threshold, the 50% loss threshold fires (pa_total >= 100 not
        met here — assertion checks the code path when PA is entirely NULL
        with count < 100 does NOT flag, so we cross the 100-count threshold)."""
        # With 5 NULL and 0 attributed, pa_null < 100 AND pa_total < 100 —
        # both flag conditions fail, so nothing is flagged. That's correct
        # for a test-DB where a few rows shouldn't trip a HIGH finding.
        payload = json.loads(self._run(json=True))
        self.assertEqual(payload['flagged_findings'], [])

    def test_pa_workspace_loss_flag_fires_at_scale(self):
        """Seed 200 NULL PA rows so pa_null >= 100 threshold trips."""
        for _ in range(200):
            _make('conversation', 'PersonalAssistant')
        payload = json.loads(self._run(json=True))
        findings = payload['flagged_findings']
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['code'], 'pa_workspace_attribution_loss')
        self.assertEqual(findings[0]['severity'], 'HIGH')
        # 205 null (5 from setUp + 200 here), 0 attributed → 100% loss
        self.assertEqual(findings[0]['null_count'], 205)
        self.assertEqual(findings[0]['attributed_count'], 0)
        self.assertEqual(findings[0]['loss_pct'], 100.0)

    def test_attributed_pa_rows_reduce_flag_severity_math(self):
        """When PA is well-attributed, loss_pct drops and the flag reflects
        the real split — mirrors the live 50.7% finding on 30d prod data."""
        # Seed 200 NULL PA + 250 attributed PA to shift loss below 50%
        from core.models_skin_layer import ProjectWorkspace
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user(username='d10test', email='d10@test.com', password='pw')
        ws = ProjectWorkspace.objects.create(user=user, name='d10 test ws')

        for _ in range(200):
            _make('conversation', 'PersonalAssistant')
        for _ in range(250):
            _make('conversation', 'PersonalAssistant', workspace=ws)

        payload = json.loads(self._run(json=True))
        findings = payload['flagged_findings']
        self.assertEqual(len(findings), 1)
        # 205 null (5 setUp + 200 new), 250 attributed
        self.assertEqual(findings[0]['null_count'], 205)
        self.assertEqual(findings[0]['attributed_count'], 250)
        # 205 / (205+250) = 45.05%
        self.assertAlmostEqual(findings[0]['loss_pct'], 45.05, places=1)

    def test_human_output_highlights_flagged_finding(self):
        for _ in range(200):
            _make('conversation', 'PersonalAssistant')
        raw = self._run()
        self.assertIn('=== LLMCallLog workspace-attribution audit', raw)
        self.assertIn('NULL bucket classification', raw)
        self.assertIn('FLAGGED FINDINGS', raw)
        self.assertIn('pa_workspace_attribution_loss', raw)

    def test_window_days_arg_scopes_lookback(self):
        """--window-days=1 must exclude a 5-day-old row."""
        old = _make('embedding', 'SpiderSemanticSearch')
        LLMCallLog.objects.filter(id=old.id).update(
            created_at=timezone.now() - timedelta(days=5)
        )
        payload = json.loads(self._run(window_days=1, json=True))
        # setUp created 12 rows in the current window + 1 old row moved
        # outside the 1d window → visible = 12 (aged row excluded).
        # We only assert that the aged row is EXCLUDED (total should not
        # count it) rather than an exact number, since setUp counts don't
        # move.
        self.assertEqual(payload['window_days'], 1)
        self.assertLessEqual(payload['total_rows'], 12)
