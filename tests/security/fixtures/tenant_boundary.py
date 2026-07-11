"""
tests/security/fixtures/tenant_boundary.py — Golden 5-model tenant boundary
fixture set for the I-0302 Phase 4 regression harness.

Contract refs:
  docs/research/implementation/tenant_boundary_lockdown/I-030203_phase4_harness_architecture.md §2
  I-030201 §11 (@ops_aggregate_allowed substrate)
  I-030202 predicate module design (Phase 2 wiring targets)

Design (per Rigby SIGN F2, confidence 0.75):
- Shared baseline: 2 regular users + 1 superuser + 2 workspaces
- Per-model: N=3 rows per user (immutable — mutating tests build on top)
- AgentExecution: +1 null-user row (Session 642 superuser carve-out probe)

The `tb_` prefix ("tenant boundary") prevents collision with per-file
fixtures used by the Phase 3 sub-phase wiring tests
(`test_i0302_[a2|b|c1|d1|d2]_*.py`), which have their own `user_a`/`user_b`
scopes and should not be affected by this module.

Exposed via `tests/security/conftest.py` — every test under
`tests/security/` picks up `tb_*` fixtures automatically.
"""
from __future__ import annotations

import uuid

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


# --------------------------------------------------------------------------
# Users
# --------------------------------------------------------------------------


@pytest.fixture
def tb_user_a(db):
    return User.objects.create_user(
        username=f"tb-user-a-{uuid.uuid4().hex[:6]}",
        email=f"tb-a-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def tb_user_b(db):
    return User.objects.create_user(
        username=f"tb-user-b-{uuid.uuid4().hex[:6]}",
        email=f"tb-b-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
    )


@pytest.fixture
def tb_superuser(db):
    return User.objects.create_user(
        username=f"tb-super-{uuid.uuid4().hex[:6]}",
        email=f"tb-s-{uuid.uuid4().hex[:6]}@example.com",
        password="pw",
        is_superuser=True,
        is_staff=True,
    )


# --------------------------------------------------------------------------
# Workspaces
# --------------------------------------------------------------------------


@pytest.fixture
def tb_workspace_a(tb_user_a):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(
        user=tb_user_a, name=f"tb-ws-a-{uuid.uuid4().hex[:6]}"
    )


@pytest.fixture
def tb_workspace_b(tb_user_b):
    from core.models_skin_layer import ProjectWorkspace

    return ProjectWorkspace.objects.create(
        user=tb_user_b, name=f"tb-ws-b-{uuid.uuid4().hex[:6]}"
    )


# --------------------------------------------------------------------------
# Initiative (per-user; NOT NULL owner post Sub-phase A1)
# --------------------------------------------------------------------------


@pytest.fixture
def tb_initiatives_a(tb_user_a):
    from core.models_document_registry import Initiative

    return [
        Initiative.objects.create(
            name=f"tb-init-a-{i}-{uuid.uuid4().hex[:6]}", owner=tb_user_a
        )
        for i in range(3)
    ]


@pytest.fixture
def tb_initiatives_b(tb_user_b):
    from core.models_document_registry import Initiative

    return [
        Initiative.objects.create(
            name=f"tb-init-b-{i}-{uuid.uuid4().hex[:6]}", owner=tb_user_b
        )
        for i in range(3)
    ]


# --------------------------------------------------------------------------
# AgentExecution (per-user + Session 642 null-user superuser carve-out)
# --------------------------------------------------------------------------


@pytest.fixture
def tb_agent(db):
    from core.models_unified_system import Agent

    return Agent.objects.create(
        name=f"tb-agent-{uuid.uuid4().hex[:6]}", agent_type="test"
    )


@pytest.fixture
def tb_executions_a(tb_user_a, tb_agent):
    from core.models_unified_system import AgentExecution

    return [
        AgentExecution.objects.create(
            user=tb_user_a, agent=tb_agent, status="completed", task=f"tb-a-{i}"
        )
        for i in range(3)
    ]


@pytest.fixture
def tb_executions_b(tb_user_b, tb_agent):
    from core.models_unified_system import AgentExecution

    return [
        AgentExecution.objects.create(
            user=tb_user_b, agent=tb_agent, status="completed", task=f"tb-b-{i}"
        )
        for i in range(3)
    ]


@pytest.fixture
def tb_execution_null_user(tb_agent):
    """Session 642 system-context AgentExecution row.

    Regular users must NEVER see this row. Superusers MUST see it (the
    documented carve-out from the predicate module).
    """
    from core.models_unified_system import AgentExecution

    return AgentExecution.objects.create(
        user=None, agent=tb_agent, status="completed", task="tb-null-user"
    )


# --------------------------------------------------------------------------
# ChatConversation (workspace-scoped; also has direct `user=` fallback)
# --------------------------------------------------------------------------


@pytest.fixture
def tb_conversations_a(tb_user_a):
    from core.models import ChatConversation

    rows = []
    for i in range(3):
        conv_id = f"tb-conv-a-{i}-{uuid.uuid4().hex[:8]}"
        ChatConversation.objects.create(
            user=tb_user_a,
            conversation_id=conv_id,
            user_message=f"tb-a-{i}",
            assistant_response="",
            source="test",
            platform="web",
        )
        rows.append(conv_id)
    return rows


@pytest.fixture
def tb_conversations_b(tb_user_b):
    from core.models import ChatConversation

    rows = []
    for i in range(3):
        conv_id = f"tb-conv-b-{i}-{uuid.uuid4().hex[:8]}"
        ChatConversation.objects.create(
            user=tb_user_b,
            conversation_id=conv_id,
            user_message=f"tb-b-{i}",
            assistant_response="",
            source="test",
            platform="web",
        )
        rows.append(conv_id)
    return rows


# --------------------------------------------------------------------------
# Deliverable (workspace-scoped)
# --------------------------------------------------------------------------


@pytest.fixture
def tb_deliverables_a(tb_user_a, tb_workspace_a):
    from core.models_deliverables import Deliverable

    return [
        Deliverable.objects.create(
            user=tb_user_a,
            workspace=tb_workspace_a,
            title=f"tb-deliv-a-{i}-{uuid.uuid4().hex[:6]}",
            deliverable_type="text",
            content=f"content a-{i}",
        )
        for i in range(3)
    ]


@pytest.fixture
def tb_deliverables_b(tb_user_b, tb_workspace_b):
    from core.models_deliverables import Deliverable

    return [
        Deliverable.objects.create(
            user=tb_user_b,
            workspace=tb_workspace_b,
            title=f"tb-deliv-b-{i}-{uuid.uuid4().hex[:6]}",
            deliverable_type="text",
            content=f"content b-{i}",
        )
        for i in range(3)
    ]


# --------------------------------------------------------------------------
# Document (per-user)
# --------------------------------------------------------------------------


@pytest.fixture
def tb_documents_a(tb_user_a):
    from content.models import Document

    return [
        Document.objects.create(
            owner=tb_user_a,
            title=f"tb-doc-a-{i}-{uuid.uuid4().hex[:6]}",
            document_type="text",
            raw_content=f"content a-{i}",
        )
        for i in range(3)
    ]


@pytest.fixture
def tb_documents_b(tb_user_b):
    from content.models import Document

    return [
        Document.objects.create(
            owner=tb_user_b,
            title=f"tb-doc-b-{i}-{uuid.uuid4().hex[:6]}",
            document_type="text",
            raw_content=f"content b-{i}",
        )
        for i in range(3)
    ]


# --------------------------------------------------------------------------
# Combined golden fixture — all-in-one setup for matrix runner
# --------------------------------------------------------------------------


@pytest.fixture
def tb_golden(
    tb_user_a,
    tb_user_b,
    tb_superuser,
    tb_workspace_a,
    tb_workspace_b,
    tb_initiatives_a,
    tb_initiatives_b,
    tb_executions_a,
    tb_executions_b,
    tb_execution_null_user,
    tb_conversations_a,
    tb_conversations_b,
    tb_deliverables_a,
    tb_deliverables_b,
    tb_documents_a,
    tb_documents_b,
):
    """One-call bundle of the full 5-model tenant-boundary fixture graph.

    Use this fixture in matrix cells that need the complete data shape:
    two isolated users, one superuser, per-model N=3 owned rows per user,
    plus one null-user AgentExecution for the Session 642 carve-out probe.
    """
    return {
        "user_a": tb_user_a,
        "user_b": tb_user_b,
        "superuser": tb_superuser,
        "workspace_a": tb_workspace_a,
        "workspace_b": tb_workspace_b,
        "initiatives_a": tb_initiatives_a,
        "initiatives_b": tb_initiatives_b,
        "executions_a": tb_executions_a,
        "executions_b": tb_executions_b,
        "execution_null_user": tb_execution_null_user,
        "conversations_a": tb_conversations_a,
        "conversations_b": tb_conversations_b,
        "deliverables_a": tb_deliverables_a,
        "deliverables_b": tb_deliverables_b,
        "documents_a": tb_documents_a,
        "documents_b": tb_documents_b,
    }
