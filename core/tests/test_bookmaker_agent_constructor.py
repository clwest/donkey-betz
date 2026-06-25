"""Session 1231 — BookmakerAgent constructor accepts user= kwarg.

Pre-fix the standard router dispatch path
(``core/agent_router.py:1045`` → ``agent_class(user=self.user)``)
raised ``BookmakerAgent.__init__() got an unexpected keyword argument
'user'`` every time, because BookmakerAgent's ``__init__(self)``
accepted zero kwargs. Surfaced by the Session 1231 full-AGENT_MAP
smoke (`smoke_id=9321b9a13397`).

Post-fix BookmakerAgent matches the standard agent contract:
constructable with no args (legacy) or with ``user=`` (router-driven).

Run::

    python manage.py test core.tests.test_bookmaker_agent_constructor -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

from core.agents.bookmaker_agent import BookmakerAgent


User = get_user_model()


class BookmakerAgentConstructorTests(SimpleTestCase):

    def test_legacy_no_args_construction_still_works(self):
        agent = BookmakerAgent()
        self.assertEqual(agent.name, "Vegas AI")
        self.assertIsNone(agent.user)

    def test_router_driven_user_kwarg_construction(self):
        """The dispatcher at agent_router.py:1045 calls
        agent_class(user=self.user); BookmakerAgent must accept it."""
        sentinel = object()
        agent = BookmakerAgent(user=sentinel)
        self.assertIs(agent.user, sentinel)
        self.assertEqual(agent.name, "Vegas AI")

    def test_constructor_absorbs_extra_kwargs(self):
        """Future-proof against new dispatcher kwargs (e.g.,
        persona_name, trace_id) without raising."""
        agent = BookmakerAgent(user=None, trace_id="abc", persona_name="x")
        self.assertEqual(agent.name, "Vegas AI")


class BookmakerAgentDispatcherIntegrationTests(TestCase):

    def test_constructable_with_real_user(self):
        """End-to-end: build with a real ORM user the way the router does."""
        user = User.objects.create_user(
            username=f"bookmaker-test-{uuid.uuid4().hex[:8]}",
            email="bm@example.com",
            password="x",
        )
        agent = BookmakerAgent(user=user)
        self.assertEqual(agent.user, user)
