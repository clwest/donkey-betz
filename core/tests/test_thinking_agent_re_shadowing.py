"""Session 1092: Regression test for ThinkingAgent `re` UnboundLocalError.

Bug: _validate_data_integrity had a redundant `import re` inside an
`if 'halted' in concern_text...` branch. Python's compiler then treats
`re` as a local variable for the entire function, shadowing the
module-level `import re`. When concerns hit the second branch
(`pending dream`) without hitting the first, `re` was unbound at line 736
→ UnboundLocalError → 4 ThinkingAgent failures / 24h.

Fix: remove the redundant local `import re` so the function uses the
module-level one. This test exercises the path that triggered the bug.
"""

from django.test import SimpleTestCase

from core.agents.thinking_agent import ThinkingAgent


class TestValidateDataIntegrityNoUnboundLocal(SimpleTestCase):
    def setUp(self):
        # Build instance without running BaseAgent.__init__ (avoids touching
        # services we don't need for this pure-Python validation test).
        self.agent = ThinkingAgent.__new__(ThinkingAgent)

    def test_pending_dream_concern_alone_does_not_unboundlocal(self):
        """The exact failure path: a concern that hits the second branch
        but not the first must not raise UnboundLocalError on `re`."""
        result = {
            'concerns': [
                {'concern': 'There are 250 pending dreams blocking the queue'},
            ],
        }
        context = {'dream_stats': {'pending_decision': 5}}

        # Pre-fix: this raised
        # UnboundLocalError: cannot access local variable 're' ...
        # Post-fix: completes without error and surfaces the hallucination
        # warning since 250 != 5.
        out = self.agent._validate_data_integrity(result, context)
        self.assertIn('_data_integrity_warnings', out)
        warnings = out['_data_integrity_warnings']
        self.assertTrue(any('pending dreams' in w for w in warnings))

    def test_halted_experiment_concern_still_works(self):
        """The first branch (which used to be the only path that bound `re`)
        must still flag hallucinated halted-experiment numbers."""
        result = {
            'concerns': [
                {'concern': '500 halted experiments in the pipeline'},
            ],
        }
        context = {'pipeline_stats': {'experiments': {'halted': 2}}}
        out = self.agent._validate_data_integrity(result, context)
        warnings = out.get('_data_integrity_warnings', [])
        self.assertTrue(
            any('halted experiments' in w for w in warnings),
            f'Expected halted-experiment hallucination warning, got: {warnings}',
        )

    def test_both_branches_in_same_call(self):
        """Original safe path before the bug — both branches fire in one call.
        Must keep working after the redundant local import is removed."""
        result = {
            'concerns': [
                {'concern': '999 halted experiments and 8000 pending dreams'},
            ],
        }
        context = {
            'pipeline_stats': {'experiments': {'halted': 1}},
            'dream_stats': {'pending_decision': 3},
        }
        out = self.agent._validate_data_integrity(result, context)
        warnings = out.get('_data_integrity_warnings', [])
        # Both hallucinations should be flagged
        self.assertTrue(any('halted' in w for w in warnings))
        self.assertTrue(any('pending dreams' in w for w in warnings))

    def test_no_concerns_returns_clean(self):
        result = {'concerns': []}
        out = self.agent._validate_data_integrity(result, {})
        self.assertNotIn('_data_integrity_warnings', out)
