import logging
from types import SimpleNamespace
from unittest.mock import Mock, patch, PropertyMock

from django.test import SimpleTestCase

from core.agents.base_agent import AgentResult, BaseAgent
from core.agent_router import AgentRouter
from core.agents.registry import AgentRegistry
from core.tasks import _run_agent_warmup
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
        self.assertFalse(result["fallback_used"])
        self.assertIsNone(result["fallback_type"])
        self.assertEqual(result["resolution_error"], "missing_success_field")

    def test_router_unavailable_returns_resolution_metadata(self):
        agent = MinimalDelegatingAgent()

        with patch.object(BaseAgent, "agent_router", new_callable=PropertyMock, return_value=None):
            result = agent._handle_delegate_to_specialist(
                "ResearchAgent",
                "analyze the market",
                delegation_context={"spider_context": {}, "scifi_context": {}},
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "AgentRouter not available for delegation")
        self.assertEqual(result["resolution_error"], "router_unavailable")
        self.assertFalse(result["fallback_used"])
        self.assertIsNone(result["fallback_type"])

    def test_dispatch_exception_returns_resolution_metadata(self):
        agent = MinimalDelegatingAgent()

        class ExplodingRouter:
            def route(self, specialist_agent, task, context=None):
                raise RuntimeError("dispatch exploded")

        agent._agent_router = ExplodingRouter()

        with patch.object(agent, "_record_delegation", return_value=None):
            result = agent._handle_delegate_to_specialist(
                "ResearchAgent",
                "analyze the market",
                delegation_context={"spider_context": {}, "scifi_context": {}},
            )

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "dispatch exploded")
        self.assertEqual(result["resolution_error"], "RuntimeError")
        self.assertFalse(result["fallback_used"])
        self.assertIsNone(result["fallback_type"])


class DelegationLearningRecordVisibilityTests(SimpleTestCase):
    def test_record_delegation_failure_returns_learning_metadata(self):
        agent = MinimalDelegatingAgent()

        class FakeTeacherModel:
            pass

        class FakeQuerySet:
            def first(self):
                return FakeTeacherModel()

        class FakeStudentModel:
            pass

        class ExplodingSolutionManager:
            def get_or_create(self, *args, **kwargs):
                raise RuntimeError("learning write failed")

        with patch("core.models_unified_system.Agent.objects.filter", return_value=FakeQuerySet()), \
             patch("core.models_unified_system.AgentSolution.objects.get_or_create", side_effect=RuntimeError("learning write failed")), \
             patch.object(BaseAgent, "agent_model", new_callable=PropertyMock, return_value=FakeStudentModel()), \
             patch("core.agents.base_agent.logger.exception") as exception_mock:
            metadata = agent._record_delegation(
                "ResearchAgent",
                "analyze the market",
                {"success": True},
            )

        self.assertFalse(metadata["learning_record_persisted"])
        self.assertEqual(metadata["learning_record_error"], "learning write failed")
        self.assertEqual(metadata["learning_record_error_type"], "RuntimeError")
        self.assertEqual(metadata["specialist"], "ResearchAgent")
        self.assertEqual(metadata["delegating_agent"], agent.name)
        self.assertTrue(exception_mock.called)

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


class AgentResolutionVisibilityTests(SimpleTestCase):
    def test_warmup_exposes_router_fallback_metadata(self):
        class WarmupAgent:
            pass

        def fake_get_agent_class(agent_name):
            fake_get_agent_class.last_resolution_metadata = {
                "fallback_used": True,
                "fallback_type": "router_lookup",
                "resolution_error": None,
                "resolution_source": "router_lookup",
            }
            return WarmupAgent

        fake_get_agent_class.last_resolution_metadata = {
            "fallback_used": True,
            "fallback_type": "router_lookup",
            "resolution_error": None,
            "resolution_source": "router_lookup",
        }

        with patch("core.tasks._get_agent_class", new=fake_get_agent_class):
            result = _run_agent_warmup("ResearchAgent")

        self.assertTrue(result["success"])
        self.assertTrue(result["resolution_metadata"]["fallback_used"])
        self.assertEqual(result["resolution_metadata"]["fallback_type"], "router_lookup")
        self.assertEqual(result["resolution_metadata"]["resolution_source"], "router_lookup")

    def test_route_by_query_attaches_thinking_fallback_metadata(self):
        router = AgentRouter()
        router._semantic_router = SimpleNamespace(
            route_query=lambda query: SimpleNamespace(
                agent_name="UnknownAgent",
                confidence=0.1,
                method="semantic",
            )
        )

        with patch.object(router, "route", return_value=AgentResult(success=True, message="ok", data={"value": 1})) as route_mock:
            result = router.route_by_query("find something", context={"foo": "bar"})

        route_mock.assert_called_once()
        self.assertTrue(result.data["resolution_metadata"]["fallback_used"])
        self.assertEqual(result.data["resolution_metadata"]["fallback_type"], "thinking_agent")
        self.assertEqual(result.data["resolution_metadata"]["fallback_reason"], "unknown_agent")
        self.assertEqual(result.data["resolution_metadata"]["confidence"], 0.1)
        self.assertEqual(result.data["resolution_metadata"]["resolution_error"], "semantic_router_suggested_unknown_agent")

    def test_route_attaches_dynamic_persona_fallback_metadata(self):
        class FakeAgentModelManager:
            def filter(self, *args, **kwargs):
                return self

            def exists(self):
                return True

        class FakeAgentModel:
            objects = FakeAgentModelManager()

        class FakeControlEntry:
            @staticmethod
            def is_blocked(agent_name):
                return False

        class FakePersonaAgent:
            def __init__(self, persona_name="", user=None, health_check_mode=False):
                self.name = persona_name
                self.user = user
                self.health_check_mode = health_check_mode

            def execute(self, task, context, scifi_context, spider_context):
                return AgentResult(success=True, message="persona ok", data={"summary": "done"}, agent_name=self.name)

        class NoOpPriorityDecision:
            matched = False
            matched_via = "none"
            priority_name = None

        def noop(*args, **kwargs):
            return None

        from contextlib import contextmanager

        @contextmanager
        def noop_ctx(*args, **kwargs):
            yield

        router = AgentRouter()
        router._complete_execution = noop
        router._record_user_learning = noop
        router._record_agent_learning_interaction = noop

        pre_gathered = {
            "gathered": True,
            "scifi_context": {},
            "spider_context": {},
            "learning_context": {},
            "advisor_context": {},
            "feedback_context": {},
            "knowledge_context": {},
            "workspace_context": {},
            "docs_context": {},
            "user_context": {},
            "risk_context": {},
            "user_docs_context": {},
        }

        with patch("core.models_unified_system.Agent", FakeAgentModel), \
             patch("core.models_unified_system.AgentControlEntry", FakeControlEntry), \
             patch("core.agents.dynamic_persona_agent.DynamicPersonaAgent", FakePersonaAgent), \
             patch("core.services.priority.enforce.check_priority", return_value=NoOpPriorityDecision()), \
             patch("core.services.priority.enforce.log_decision", return_value=None), \
             patch("core.services.priority.semaphore.acquire_for_decision", noop_ctx), \
             patch.object(router, "_create_execution_record", return_value=SimpleNamespace(id="exec-1")), \
             patch.object(router, "_get_scifi_context", return_value={}), \
             patch.object(router, "_get_spider_context", return_value={}), \
             patch.object(router, "_get_learning_context", return_value={}), \
             patch.object(router, "_get_advisor_context", return_value={}), \
             patch.object(router, "_get_feedback_context", return_value={}), \
             patch.object(router, "_get_knowledge_context", return_value={}), \
             patch.object(router, "_get_workspace_context", return_value={}), \
             patch.object(router, "_get_docs_context", return_value={}), \
             patch.object(router, "_get_user_context", return_value={}), \
             patch.object(router, "_get_risk_aware_context", return_value={}), \
             patch.object(router, "_get_user_documents_context", return_value={}):
            result = router.route(
                "HiddenPersonaAgent",
                "do something",
                context={},
                pre_gathered_context=pre_gathered,
                create_execution_record=False,
                existing_execution_record=SimpleNamespace(id="exec-1"),
            )

        self.assertTrue(result.data["resolution_metadata"]["fallback_used"])
        self.assertEqual(result.data["resolution_metadata"]["fallback_type"], "dynamic_persona")
        self.assertEqual(result.data["resolution_metadata"]["fallback_reason"], "db_persona")
        self.assertEqual(result.data["resolution_metadata"]["resolution_error"], "agent_not_in_agent_map")


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


class RegistryResolutionVisibilityTests(SimpleTestCase):
    def test_execute_agent_injects_resolution_metadata(self):
        class FakeTemplate:
            llm_provider = "openai"
            llm_model = "gpt-5-mini"
            llm_config = {}
            capabilities = []
            required_tools = []
            specialization = "general"
            name = "ResearchAgent"

            def update_metrics(self, *args, **kwargs):
                return None

        class FakeExecution:
            def __init__(self, **kwargs):
                self.kwargs = kwargs
                self.id = "exec-99"
                self.status = None
                self.save_calls = 0

            def save(self):
                self.save_calls += 1

        class FakeAgentTemplateManager:
            def get(self, *args, **kwargs):
                return FakeTemplate()

        class FakeExecutionManager:
            def __init__(self):
                self.calls = []

            def create(self, **kwargs):
                self.calls.append(kwargs)
                return FakeExecution(**kwargs)

        registry = AgentRegistry.__new__(AgentRegistry)
        registry.logger = logging.getLogger(__name__)
        registry._last_resolution_metadata = {
            "fallback_used": True,
            "fallback_type": "registry_error",
            "resolution_error": "RuntimeError: lookup failed",
            "resolution_source": "error",
        }

        agent_template_manager = FakeAgentTemplateManager()
        execution_manager = FakeExecutionManager()

        with patch("core.models.agents_registry.UnifiedAgentTemplate.objects", agent_template_manager), \
             patch("core.models.agents_registry.AgentExecution.objects", execution_manager), \
             patch("core.services.context_tracking.build_context_tracking", return_value={"injected": True}):
            execution_id = registry.execute_agent("ResearchAgent", {"task": "inspect"})

        self.assertEqual(execution_id, "exec-99")
        self.assertEqual(execution_manager.calls[0]["input_data"]["_resolution_metadata"]["fallback_used"], True)
        self.assertEqual(execution_manager.calls[0]["input_data"]["_resolution_metadata"]["fallback_type"], "registry_error")

    def test_execute_agent_missing_template_returns_structured_failure(self):
        from core.models.agents_registry import UnifiedAgentTemplate as ModelTemplate

        class FakeAgentTemplateManager:
            def get(self, *args, **kwargs):
                raise ModelTemplate.DoesNotExist("missing")

        registry = AgentRegistry.__new__(AgentRegistry)
        registry.logger = logging.getLogger(__name__)
        registry._last_resolution_metadata = {
            "fallback_used": False,
            "fallback_type": None,
            "resolution_error": None,
            "resolution_source": "init",
        }

        with patch("core.models.agents_registry.UnifiedAgentTemplate.objects", FakeAgentTemplateManager()):
            result = registry.execute_agent("ResearchAgent", {"task": "inspect"})

        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertEqual(result["failure_type"], "missing_template")
        self.assertEqual(result["agent_name"], "ResearchAgent")
        self.assertEqual(result["resolution_error"], "UnifiedAgentTemplate.DoesNotExist")
        self.assertEqual(result["resolution_metadata"]["fallback_type"], "registry_miss")

    def test_execute_agent_execution_error_returns_structured_failure(self):
        class FakeTemplate:
            llm_provider = "openai"
            llm_model = "gpt-5-mini"
            llm_config = {}
            capabilities = []
            required_tools = []
            specialization = "general"
            name = "ResearchAgent"

            def update_metrics(self, *args, **kwargs):
                return None

        class FakeExecutionManager:
            def __init__(self):
                self.calls = []

            def create(self, **kwargs):
                raise RuntimeError("execution exploded")

        class FakeAgentTemplateManager:
            def get(self, *args, **kwargs):
                return FakeTemplate()

        registry = AgentRegistry.__new__(AgentRegistry)
        registry.logger = logging.getLogger(__name__)
        registry._last_resolution_metadata = {
            "fallback_used": False,
            "fallback_type": None,
            "resolution_error": None,
            "resolution_source": "init",
        }

        with patch("core.models.agents_registry.UnifiedAgentTemplate.objects", FakeAgentTemplateManager()), \
             patch("core.models.agents_registry.AgentExecution.objects", FakeExecutionManager()), \
             patch("core.services.context_tracking.build_context_tracking", return_value={"injected": True}):
            result = registry.execute_agent("ResearchAgent", {"task": "inspect"})

        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertEqual(result["failure_type"], "execution_error")
        self.assertEqual(result["agent_name"], "ResearchAgent")
        self.assertIn("execution exploded", result["error"])
        self.assertEqual(result["resolution_metadata"]["fallback_type"], "registry_error")
