"""
Session 1064: Test LUNGS hard-limit blocking in LLMEnforcer.

Verifies that when budget is exhausted with enforce_hard_limit=True,
enforce_real_ai() returns a structured error dict without exceptions.
"""
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase, override_settings


class LungsHardLimitTest(SimpleTestCase):
    """Test LUNGS budget enforcement in LLMEnforcer."""

    def setUp(self):
        from core.llm_enforcer import LLMEnforcer
        self.enforcer = LLMEnforcer()

    @override_settings(LUNGS_ENFORCE_HARD_LIMIT=True)
    def test_lungs_hard_limit_blocks_llm_call(self):
        """When LUNGS returns can_breathe=False, enforce_real_ai returns structured error."""
        mock_lungs = MagicMock()
        mock_lungs.can_breathe.return_value = (False, "System daily budget exhausted")

        with patch('core.services.lungs.get_lungs_monitor', return_value=mock_lungs):
            result = self.enforcer.enforce_real_ai(
                prompt="Test prompt",
                context="Test context",
                agent_name="TestAgent",
                task_type="test",
            )

        # Verify structured error shape
        self.assertFalse(result['success'])
        self.assertTrue(result['blocked_by_lungs'])
        self.assertIn('error', result)
        self.assertIn('Budget exhausted', result['error'])
        self.assertIn('response', result)
        self.assertEqual(result['agent'], 'TestAgent')
        self.assertIn('call_id', result)

    @override_settings(LUNGS_ENFORCE_HARD_LIMIT=False)
    def test_lungs_disabled_skips_budget_check(self):
        """When LUNGS_ENFORCE_HARD_LIMIT=False, budget check is skipped entirely."""
        mock_lungs = MagicMock()
        mock_lungs.can_breathe.return_value = (False, "Budget exhausted")

        with patch('core.services.lungs.get_lungs_monitor', return_value=mock_lungs):
            # With LUNGS disabled, even if can_breathe returns False,
            # the call should proceed past LUNGS (and succeed or fail at LLM)
            result = self.enforcer.enforce_real_ai(
                prompt="Test prompt",
                context="Test context",
                agent_name="TestAgent",
                task_type="test",
            )

        # Should NOT be blocked by LUNGS
        self.assertNotEqual(result.get('blocked_by_lungs'), True)

    def test_lungs_error_does_not_block(self):
        """If LUNGS itself throws, LLM call proceeds normally (not blocked)."""
        def broken_lungs():
            raise RuntimeError("LUNGS database unavailable")

        with patch('core.services.lungs.get_lungs_monitor', side_effect=broken_lungs):
            result = self.enforcer.enforce_real_ai(
                prompt="Test prompt",
                context="Test context",
                agent_name="TestAgent",
                task_type="test",
            )

        # Should NOT be blocked by LUNGS — the call proceeds past the try/except
        self.assertNotEqual(result.get('blocked_by_lungs'), True)
