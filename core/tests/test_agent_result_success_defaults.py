from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from core.agents.base_agent import AgentResult, BaseAgent
from core.tasks_agents import _impl_workspace_autopilot_tick


class MinimalDelegatingAgent(BaseAgent):
    name = "MinimalDelegatingAgent"

    def execute(self, task, context, scifi_context, spider_context):
        return AgentResult(success=True, message="ok", agent_name=self.name)


class DelegateSpecialistResultTests(SimpleTestCase):
    def test_missing_success_field_defaults_to_failure(self):
        agent = MinimalDelegatingAgent()

        class FakeRouter:
            def route(self, specialist_agent, task, context=None):
                return {"message": "ok", "data": {"value": 1}}

        agent._agent_router = FakeRouter()

        with patch.object(agent, "_record_delegation", return_value=None):
            result = agent._handle_delegate_to_specialist(
                "ResearchAgent",
                "analyze the market",
                delegation_context={"spider_context": {}, "scifi_context": {}},
            )

        self.assertFalse(result["success"])
        self.assertIn("missing success field", result["error"])
        self.assertEqual(result["specialist"], "ResearchAgent")

    def test_explicit_success_is_preserved(self):
        agent = MinimalDelegatingAgent()

        class FakeRouter:
            def route(self, specialist_agent, task, context=None):
                return {"success": True, "message": "ok", "data": {"value": 1}}

        agent._agent_router = FakeRouter()

        with patch.object(agent, "_record_delegation", return_value=None):
            result = agent._handle_delegate_to_specialist(
                "ResearchAgent",
                "analyze the market",
                delegation_context={"spider_context": {}, "scifi_context": {}},
            )

        self.assertTrue(result["success"])
        self.assertEqual(result["specialist_response"], "ok")


class WorkspaceAutopilotResultTests(SimpleTestCase):
    def test_missing_success_field_counts_as_failure(self):
        class FakeManager:
            def filter(self, *args, **kwargs):
                return self

            def update(self, **kwargs):
                return 0

            def first(self):
                return FakeUser()

        class FakeUser:
            pass

        class FakeUserModel:
            objects = FakeManager()

        class FakeTriggerManager:
            def filter(self, *args, **kwargs):
                return self

            def update(self, **kwargs):
                return 0

        class FakeTrigger:
            objects = FakeTriggerManager()
            instances = []

            @classmethod
            def get_pending_triggers(cls, limit, category=None, min_priority=None):
                return [cls()]

            def __init__(self):
                self.id = 123
                self.title = "Review trigger"
                self.description = "Review this item"
                self.target_agent = "ResearchAgent"
                self.target_category = None
                self.trigger_type = "spider_security_alert"
                self.context_data = {"raw_item": {"summary": "trigger summary"}}
                self.status = "pending"
                self.completed_at = None
                self.execution_time_ms = None
                self.result_summary = ""
                self.execution_id = None
                self.queued_at = None
                self.started_at = None
                self.error_message = ""
                self.saved_fields = []
                FakeTrigger.instances.append(self)

            def save(self, update_fields=None):
                self.saved_fields.append(update_fields)

            def get_trigger_type_display(self):
                return "Spider Security Alert"

        class FakeWorkspaceTriggerType:
            SPIDER_SECURITY_ALERT = "spider_security_alert"
            SPIDER_DEPENDENCY_UPDATE = "spider_dependency_update"
            SPIDER_BUG_PATTERN = "spider_bug_pattern"
            SPIDER_BEST_PRACTICE = "spider_best_practice"
            SPIDER_CODE_INSIGHT = "spider_code_insight"
            AGENT_REFACTOR_SUGGESTION = "agent_refactor_suggestion"
            AGENT_TEST_NEEDED = "agent_test_needed"
            AGENT_DOC_NEEDED = "agent_doc_needed"
            AGENT_OPTIMIZATION = "agent_optimization"

        class FakeAgent:
            def __init__(self, user=None):
                self.user = user

            def execute(self, task, context, scifi_context, spider_context):
                return {"summary": "processed"}

        class FakeAgentRouter:
            def __init__(self, *args, **kwargs):
                pass

            def get_agent_class(self, agent_name):
                return FakeAgent if agent_name == "ResearchAgent" else None

        with patch("core.models_skin_layer.WorkspaceTrigger", FakeTrigger), \
             patch("core.models_skin_layer.WorkspaceTriggerType", FakeWorkspaceTriggerType), \
             patch("django.contrib.auth.get_user_model", return_value=FakeUserModel), \
             patch("core.agent_router.AgentRouter", FakeAgentRouter), \
             patch("core.services.priority.governor.should_dispatch", return_value=SimpleNamespace(proceed=True, reason="governor_off", detail=None)), \
             patch("django.utils.timezone.now", return_value=SimpleNamespace()):
            results = _impl_workspace_autopilot_tick(
                budget_per_tick=1,
                min_priority=None,
                category=None,
                dry_run=False,
            )

        self.assertEqual(results["triggers_processed"], 1)
        self.assertEqual(results["triggers_failed"], 1)
        self.assertEqual(results["triggers_succeeded"], 0)
        self.assertEqual(results["executions"][0]["success"], False)
        self.assertIn("missing success field", FakeTrigger.instances[0].error_message)
