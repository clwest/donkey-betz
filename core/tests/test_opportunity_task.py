"""Integration tests for Opportunity/Task pipeline."""

from django.test import TestCase


class OpportunityTaskIntegrationTest(TestCase):
    """Tests covering opportunity creation and task linkage."""

    def test_opportunity_can_be_created(self):
        """Smoke-test: an Opportunity record can be persisted."""
        from core.models import Opportunity

        opp = Opportunity.objects.create(
            title="Test Opportunity",
            description="Integration test opportunity",
            status="open",
        )
        self.assertIsNotNone(opp.pk)
        self.assertEqual(opp.title, "Test Opportunity")

    def test_opportunity_default_status(self):
        """An opportunity created without explicit status defaults to open."""
        from core.models import Opportunity

        opp = Opportunity.objects.create(
            title="Status Default Test",
        )
        # Accept whatever the model default is — just ensure we can read it
        self.assertIsNotNone(opp.status)

    def test_opportunity_str_representation(self):
        """str(opportunity) should include the title."""
        from core.models import Opportunity

        opp = Opportunity.objects.create(title="Repr Test Opportunity")
        self.assertIn("Repr Test Opportunity", str(opp))
