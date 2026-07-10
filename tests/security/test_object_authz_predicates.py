"""
tests/security/test_object_authz_predicates.py — I-0302 Phase 2 predicate tests

Regression suite for `core.security.object_authz` per design brief §5. Every
predicate + queryset filter is exercised across:
- owner+access path (returns True / includes row)
- wrong-owner+deny path (returns False / excludes row)
- null-owner rule per model (§3 nullable-owner policy)
- unauthenticated user (user is None) (returns False / .none())
- null obj (returns False)
- empty queryset invariant (returns empty)
- mixed-ownership queryset returns only user's rows
- **idempotence / monotonicity: scope(scope(qs)) == scope(qs)**  (F5)

Model-specific extras:
- AgentExecution superuser carve-out (F4) — non-staff / staff / superuser / null-user
- AgentExecution queryset invariant: `Q(user=user) | Q(user__isnull=True)` — no cross-user leak to superuser
- ChatConversation dual-fallback (F3) — workspace-scoped / user-fallback / disagreement (workspace wins)
- Deliverable null-workspace (F3) — non-staff denied, staff allowed for cleanup visibility

Fixtures (per design §5):
- user_a, user_b, user_c (regular users)
- staff_user (is_staff=True, is_superuser=False)
- superuser (is_superuser=True)
- ws_a, ws_b, ws_c (workspaces per user)
"""
import uuid
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.security.object_authz import (
    can_read_agent_execution,
    can_read_chat_conversation,
    can_read_deliverable,
    can_read_document,
    can_read_initiative,
    scope_queryset_agent_execution,
    scope_queryset_chat_conversation,
    scope_queryset_deliverable,
    scope_queryset_document,
    scope_queryset_initiative,
    user_can_access_workspace,
)

User = get_user_model()


# ==========================================================================
# Fixtures
# ==========================================================================


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username=f"user_a_{uuid.uuid4().hex[:8]}", password="x")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username=f"user_b_{uuid.uuid4().hex[:8]}", password="x")


@pytest.fixture
def user_c(db):
    return User.objects.create_user(username=f"user_c_{uuid.uuid4().hex[:8]}", password="x")


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(
        username=f"staff_{uuid.uuid4().hex[:8]}", password="x", is_staff=True
    )


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username=f"su_{uuid.uuid4().hex[:8]}", password="x")


@pytest.fixture
def ws_a(user_a):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(user=user_a, name="ws_a", root_path="/tmp/ws_a")


@pytest.fixture
def ws_b(user_b):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(user=user_b, name="ws_b", root_path="/tmp/ws_b")


@pytest.fixture
def ws_c(user_c):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(user=user_c, name="ws_c", root_path="/tmp/ws_c")


# ==========================================================================
# user_can_access_workspace primitive
# ==========================================================================


class TestUserCanAccessWorkspace:
    def test_owner_can_access(self, user_a, ws_a):
        assert user_can_access_workspace(user_a, ws_a.id) is True

    def test_non_owner_cannot_access(self, user_b, ws_a):
        assert user_can_access_workspace(user_b, ws_a.id) is False

    def test_none_user_returns_false(self, ws_a):
        assert user_can_access_workspace(None, ws_a.id) is False

    def test_none_workspace_id_returns_false(self, user_a):
        assert user_can_access_workspace(user_a, None) is False

    def test_nonexistent_workspace_id_returns_false(self, user_a):
        assert user_can_access_workspace(user_a, uuid.uuid4()) is False

    def test_superuser_bypass_own_workspace(self, superuser, ws_a):
        # Superuser bypasses ownership entirely; would succeed even without owning the workspace.
        assert user_can_access_workspace(superuser, ws_a.id) is True

    def test_superuser_bypass_others_workspace(self, superuser, user_a, ws_a):
        # ws_a is owned by user_a, superuser still passes.
        assert user_can_access_workspace(superuser, ws_a.id) is True


# ==========================================================================
# Deliverable (Q7 workspace-scoped + staff carve-out for null-workspace)
# ==========================================================================


class TestDeliverableCanRead:
    @pytest.fixture
    def deliv_in_ws_a(self, user_a, ws_a):
        from core.models_deliverables import Deliverable

        return Deliverable.objects.create(user=user_a, workspace=ws_a, title="deliv-a")

    @pytest.fixture
    def deliv_in_ws_b(self, user_b, ws_b):
        from core.models_deliverables import Deliverable

        return Deliverable.objects.create(user=user_b, workspace=ws_b, title="deliv-b")

    @pytest.fixture
    def deliv_null_workspace(self, user_a):
        from core.models_deliverables import Deliverable

        return Deliverable.objects.create(user=user_a, workspace=None, title="deliv-orphan")

    def test_owner_can_read_own_workspace_deliverable(self, user_a, deliv_in_ws_a):
        assert can_read_deliverable(user_a, deliv_in_ws_a) is True

    def test_non_owner_cannot_read_other_workspace_deliverable(self, user_b, deliv_in_ws_a):
        assert can_read_deliverable(user_b, deliv_in_ws_a) is False

    def test_none_user_returns_false(self, deliv_in_ws_a):
        assert can_read_deliverable(None, deliv_in_ws_a) is False

    def test_none_deliverable_returns_false(self, user_a):
        assert can_read_deliverable(user_a, None) is False

    def test_null_workspace_non_staff_denied(self, user_a, deliv_null_workspace):
        # Non-staff user (even the row's user FK) cannot read workspace-null rows
        assert can_read_deliverable(user_a, deliv_null_workspace) is False

    def test_null_workspace_staff_allowed(self, staff_user, deliv_null_workspace):
        # Staff sees null-workspace rows for cleanup visibility
        assert can_read_deliverable(staff_user, deliv_null_workspace) is True


class TestDeliverableScopeQueryset:
    @pytest.fixture
    def rows(self, user_a, user_b, ws_a, ws_b):
        from core.models_deliverables import Deliverable

        Deliverable.objects.create(user=user_a, workspace=ws_a, title="a1")
        Deliverable.objects.create(user=user_a, workspace=ws_a, title="a2")
        Deliverable.objects.create(user=user_b, workspace=ws_b, title="b1")
        Deliverable.objects.create(user=user_a, workspace=None, title="orphan1")
        return Deliverable.objects.all()

    def test_none_user_returns_none(self, rows):
        assert scope_queryset_deliverable(None, rows).count() == 0

    def test_non_staff_sees_only_own_workspace_rows(self, user_a, rows):
        result = scope_queryset_deliverable(user_a, rows)
        titles = set(result.values_list("title", flat=True))
        assert titles == {"a1", "a2"}  # user_a rows in ws_a, NO orphan

    def test_non_staff_excludes_null_workspace_rows(self, user_a, rows):
        result = scope_queryset_deliverable(user_a, rows)
        assert "orphan1" not in set(result.values_list("title", flat=True))

    def test_staff_sees_own_plus_null_workspace(self, staff_user, ws_a, user_a):
        # Staff user has NO workspaces of their own → sees only null-workspace rows
        from core.models_deliverables import Deliverable

        Deliverable.objects.create(user=user_a, workspace=ws_a, title="a1")
        Deliverable.objects.create(user=user_a, workspace=None, title="orphan-visible-to-staff")
        result = scope_queryset_deliverable(staff_user, Deliverable.objects.all())
        titles = set(result.values_list("title", flat=True))
        assert "orphan-visible-to-staff" in titles
        assert "a1" not in titles  # staff has no workspace of their own

    def test_idempotent(self, user_a, rows):
        # scope(scope(qs)) == scope(qs)
        once = scope_queryset_deliverable(user_a, rows)
        twice = scope_queryset_deliverable(user_a, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))


# ==========================================================================
# ChatConversation (Q7 workspace-scoped + transitional user fallback)
# ==========================================================================


class TestChatConversationCanRead:
    @pytest.fixture
    def conv_in_ws_a(self, user_a, ws_a):
        from core.models.conversations.models import ChatConversation

        return ChatConversation.objects.create(
            user=user_a, workspace=ws_a, conversation_id="conv-a-ws"
        )

    @pytest.fixture
    def conv_user_a_no_workspace(self, user_a):
        from core.models.conversations.models import ChatConversation

        return ChatConversation.objects.create(
            user=user_a, workspace=None, conversation_id="conv-a-nows"
        )

    @pytest.fixture
    def conv_disagreement(self, user_a, ws_b):
        """Workspace and user disagree — workspace wins."""
        from core.models.conversations.models import ChatConversation

        return ChatConversation.objects.create(
            user=user_a, workspace=ws_b, conversation_id="conv-disagree"
        )

    def test_owner_workspace_scoped(self, user_a, conv_in_ws_a):
        assert can_read_chat_conversation(user_a, conv_in_ws_a) is True

    def test_wrong_workspace_denied(self, user_b, conv_in_ws_a):
        assert can_read_chat_conversation(user_b, conv_in_ws_a) is False

    def test_workspace_null_user_fallback_owner(self, user_a, conv_user_a_no_workspace):
        assert can_read_chat_conversation(user_a, conv_user_a_no_workspace) is True

    def test_workspace_null_user_fallback_wrong_user(self, user_b, conv_user_a_no_workspace):
        assert can_read_chat_conversation(user_b, conv_user_a_no_workspace) is False

    def test_none_user_returns_false(self, conv_in_ws_a):
        assert can_read_chat_conversation(None, conv_in_ws_a) is False

    def test_none_conv_returns_false(self, user_a):
        assert can_read_chat_conversation(user_a, None) is False

    def test_workspace_wins_over_user_disagreement(self, user_a, conv_disagreement):
        # conv.user=user_a but conv.workspace=ws_b (owned by user_b) — workspace wins → deny
        assert can_read_chat_conversation(user_a, conv_disagreement) is False

    def test_workspace_wins_over_user_disagreement_workspace_owner(self, user_b, conv_disagreement):
        # conv.user=user_a but conv.workspace=ws_b (owned by user_b) — user_b wins workspace check
        assert can_read_chat_conversation(user_b, conv_disagreement) is True


class TestChatConversationScopeQueryset:
    @pytest.fixture
    def rows(self, user_a, user_b, ws_a, ws_b):
        from core.models.conversations.models import ChatConversation

        ChatConversation.objects.create(user=user_a, workspace=ws_a, conversation_id="a-ws")
        ChatConversation.objects.create(user=user_a, workspace=None, conversation_id="a-nows")
        ChatConversation.objects.create(user=user_b, workspace=ws_b, conversation_id="b-ws")
        ChatConversation.objects.create(user=user_b, workspace=None, conversation_id="b-nows")
        return ChatConversation.objects.all()

    def test_none_user_returns_none(self, rows):
        assert scope_queryset_chat_conversation(None, rows).count() == 0

    def test_user_sees_own_workspace_and_own_direct(self, user_a, rows):
        result = scope_queryset_chat_conversation(user_a, rows)
        ids = set(result.values_list("conversation_id", flat=True))
        assert "a-ws" in ids
        assert "a-nows" in ids
        assert "b-ws" not in ids
        assert "b-nows" not in ids

    def test_idempotent(self, user_a, rows):
        once = scope_queryset_chat_conversation(user_a, rows)
        twice = scope_queryset_chat_conversation(user_a, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))


# ==========================================================================
# Initiative (Q7 per-user)
# ==========================================================================


class TestInitiativeCanRead:
    @pytest.fixture
    def init_owned_a(self, user_a):
        from core.models_document_registry import Initiative

        return Initiative.objects.create(name=f"init-a-{uuid.uuid4().hex[:6]}", owner=user_a)

    @pytest.fixture
    def init_null_owner(self):
        # I-0302 Phase 3 Sub-phase A1 (2026-07-10) migrated Initiative.owner
        # to NOT NULL — the DB now rejects owner=None writes. The predicate's
        # null-owner deny-by-default branch remains a defense-in-depth guard
        # for stale in-memory instances / adversarial input, so we exercise it
        # against a lightweight in-memory object rather than a persisted row.
        return SimpleNamespace(owner_id=None)

    def test_owner_can_read(self, user_a, init_owned_a):
        assert can_read_initiative(user_a, init_owned_a) is True

    def test_non_owner_denied(self, user_b, init_owned_a):
        assert can_read_initiative(user_b, init_owned_a) is False

    def test_null_owner_deny_by_default(self, user_a, init_null_owner):
        # Defense-in-depth: predicate rejects null-owner input even though A1
        # migration eliminates that class of row at the DB layer.
        assert can_read_initiative(user_a, init_null_owner) is False

    def test_none_user_returns_false(self, init_owned_a):
        assert can_read_initiative(None, init_owned_a) is False

    def test_none_initiative_returns_false(self, user_a):
        assert can_read_initiative(user_a, None) is False


class TestInitiativeScopeQueryset:
    @pytest.fixture
    def rows(self, user_a, user_b):
        # I-0302 Phase 3 Sub-phase A1 (2026-07-10) makes Initiative.owner
        # NOT NULL — the orphan-row leg of the old fixture is now impossible
        # by DB invariant, so this fixture models mixed ownership across two
        # real users only. The predicate's null-owner defense-in-depth is
        # covered separately in TestInitiativeCanRead::test_null_owner_deny_by_default.
        from core.models_document_registry import Initiative

        Initiative.objects.create(name=f"a1-{uuid.uuid4().hex[:6]}", owner=user_a)
        Initiative.objects.create(name=f"a2-{uuid.uuid4().hex[:6]}", owner=user_a)
        Initiative.objects.create(name=f"b1-{uuid.uuid4().hex[:6]}", owner=user_b)
        return Initiative.objects.all()

    def test_none_user_returns_none(self, rows):
        assert scope_queryset_initiative(None, rows).count() == 0

    def test_owner_sees_own_only(self, user_a, rows):
        result = scope_queryset_initiative(user_a, rows)
        assert result.count() == 2
        assert all(row.owner_id == user_a.id for row in result)

    def test_not_null_invariant(self, rows):
        # Confirms the A1 schema invariant that this fixture depends on:
        # no null-owner rows can exist in the DB post-migration.
        assert rows.filter(owner__isnull=True).count() == 0

    def test_idempotent(self, user_a, rows):
        once = scope_queryset_initiative(user_a, rows)
        twice = scope_queryset_initiative(user_a, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))


# ==========================================================================
# AgentExecution (Q7 per-user + superuser carve-out for null-user)
# ==========================================================================


class TestAgentExecutionCanRead:
    @pytest.fixture
    def agent(self):
        from core.models_unified_system import Agent

        return Agent.objects.create(name=f"agent-{uuid.uuid4().hex[:6]}", agent_type="test")

    @pytest.fixture
    def exec_user_a(self, user_a, agent):
        from core.models_unified_system import AgentExecution

        return AgentExecution.objects.create(user=user_a, agent=agent, task="user-a task")

    @pytest.fixture
    def exec_null_user(self, agent):
        from core.models_unified_system import AgentExecution

        return AgentExecution.objects.create(user=None, agent=agent, task="system-context task")

    def test_owner_can_read(self, user_a, exec_user_a):
        assert can_read_agent_execution(user_a, exec_user_a) is True

    def test_non_owner_denied(self, user_b, exec_user_a):
        assert can_read_agent_execution(user_b, exec_user_a) is False

    def test_null_user_non_staff_denied(self, user_a, exec_null_user):
        # Regular non-staff cannot see null-user (system-context) runs
        assert can_read_agent_execution(user_a, exec_null_user) is False

    def test_null_user_staff_denied(self, staff_user, exec_null_user):
        # Staff (non-superuser) also cannot see — carve-out is superuser only per F4
        assert can_read_agent_execution(staff_user, exec_null_user) is False

    def test_null_user_superuser_allowed(self, superuser, exec_null_user):
        # Superuser sees null-user (system-context) runs
        assert can_read_agent_execution(superuser, exec_null_user) is True

    def test_none_user_returns_false(self, exec_user_a):
        assert can_read_agent_execution(None, exec_user_a) is False

    def test_none_execution_returns_false(self, user_a):
        assert can_read_agent_execution(user_a, None) is False


class TestAgentExecutionScopeQueryset:
    @pytest.fixture
    def agent(self):
        from core.models_unified_system import Agent

        return Agent.objects.create(name=f"agent-{uuid.uuid4().hex[:6]}", agent_type="test")

    @pytest.fixture
    def rows(self, user_a, user_b, user_c, agent):
        from core.models_unified_system import AgentExecution

        AgentExecution.objects.create(user=user_a, agent=agent, task="a1")
        AgentExecution.objects.create(user=user_a, agent=agent, task="a2")
        AgentExecution.objects.create(user=user_b, agent=agent, task="b1")
        AgentExecution.objects.create(user=user_c, agent=agent, task="c1")
        AgentExecution.objects.create(user=None, agent=agent, task="sys1")
        AgentExecution.objects.create(user=None, agent=agent, task="sys2")
        return AgentExecution.objects.all()

    def test_none_user_returns_none(self, rows):
        assert scope_queryset_agent_execution(None, rows).count() == 0

    def test_non_staff_sees_own_only(self, user_a, rows):
        result = scope_queryset_agent_execution(user_a, rows)
        tasks = set(result.values_list("task", flat=True))
        assert tasks == {"a1", "a2"}

    def test_staff_sees_own_only(self, staff_user, rows):
        # Regular staff has no rows of own, and superuser carve-out doesn't apply
        result = scope_queryset_agent_execution(staff_user, rows)
        assert result.count() == 0

    def test_superuser_sees_own_plus_null_user(self, superuser, rows):
        result = scope_queryset_agent_execution(superuser, rows)
        tasks = set(result.values_list("task", flat=True))
        # superuser owns no rows in fixture, so only null-user rows
        assert tasks == {"sys1", "sys2"}

    def test_superuser_does_not_see_other_users_rows(self, superuser, rows):
        # F4 amendment invariant: superuser gets Q(user=user) | Q(user__isnull=True),
        # NOT "sees everything regardless of user not null"
        result = scope_queryset_agent_execution(superuser, rows)
        tasks = set(result.values_list("task", flat=True))
        assert "a1" not in tasks
        assert "b1" not in tasks
        assert "c1" not in tasks

    def test_idempotent_non_staff(self, user_a, rows):
        once = scope_queryset_agent_execution(user_a, rows)
        twice = scope_queryset_agent_execution(user_a, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))

    def test_idempotent_superuser(self, superuser, rows):
        once = scope_queryset_agent_execution(superuser, rows)
        twice = scope_queryset_agent_execution(superuser, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))

    def test_superuser_exactness_own_plus_null_only(self, superuser, user_a, agent):
        """Per Rigby SIGN F3 amendment: superuser MUST see (own + null-user) ONLY.

        Explicit 3-row invariant test: superuser's own + other-user's + null-user.
        Superuser scope MUST return exactly {superuser-own, null-user}, NEVER
        broadening to include other users' non-null rows.
        """
        from core.models_unified_system import AgentExecution

        AgentExecution.objects.create(user=superuser, agent=agent, task="su-own")
        AgentExecution.objects.create(user=user_a, agent=agent, task="user-a-owned")
        AgentExecution.objects.create(user=None, agent=agent, task="null-user")
        result = scope_queryset_agent_execution(superuser, AgentExecution.objects.all())
        tasks = set(result.values_list("task", flat=True))
        assert tasks == {"su-own", "null-user"}, (
            f"Superuser scope must be exactly Q(user=user) | Q(user__isnull=True); "
            f"got tasks={tasks}. If 'user-a-owned' is in the set, superuser scope was "
            f"broadened to include foreign-user rows (F4 amendment invariant broken)."
        )


# ==========================================================================
# Document (Q7 per-user)
# ==========================================================================


class TestDocumentCanRead:
    @pytest.fixture
    def doc_user_a(self, user_a):
        from content.models import Document, DocumentType

        return Document.objects.create(
            title=f"doc-a-{uuid.uuid4().hex[:6]}",
            owner=user_a,
            document_type=DocumentType.KNOWLEDGE if hasattr(DocumentType, "KNOWLEDGE") else "knowledge",
        )

    def test_owner_can_read(self, user_a, doc_user_a):
        assert can_read_document(user_a, doc_user_a) is True

    def test_non_owner_denied(self, user_b, doc_user_a):
        assert can_read_document(user_b, doc_user_a) is False

    def test_none_user_returns_false(self, doc_user_a):
        assert can_read_document(None, doc_user_a) is False

    def test_none_doc_returns_false(self, user_a):
        assert can_read_document(user_a, None) is False


class TestDocumentScopeQueryset:
    @pytest.fixture
    def rows(self, user_a, user_b):
        from content.models import Document, DocumentType

        dt = DocumentType.KNOWLEDGE if hasattr(DocumentType, "KNOWLEDGE") else "knowledge"
        Document.objects.create(title=f"a1-{uuid.uuid4().hex[:6]}", owner=user_a, document_type=dt)
        Document.objects.create(title=f"a2-{uuid.uuid4().hex[:6]}", owner=user_a, document_type=dt)
        Document.objects.create(title=f"b1-{uuid.uuid4().hex[:6]}", owner=user_b, document_type=dt)
        return Document.objects.all()

    def test_none_user_returns_none(self, rows):
        assert scope_queryset_document(None, rows).count() == 0

    def test_owner_sees_own_only(self, user_a, rows):
        result = scope_queryset_document(user_a, rows)
        assert result.count() == 2
        assert all(row.owner_id == user_a.id for row in result)

    def test_idempotent(self, user_a, rows):
        once = scope_queryset_document(user_a, rows)
        twice = scope_queryset_document(user_a, once)
        assert set(once.values_list("id", flat=True)) == set(twice.values_list("id", flat=True))
