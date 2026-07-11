"""
tests/security/conftest.py — pytest fixture auto-discovery for the I-0302
Phase 4 regression harness.

Re-exports the golden `tb_*` tenant-boundary fixtures so that any test in
`tests/security/` can request them as parameters without an explicit
import. See `tests/security/fixtures/tenant_boundary.py` for details.
"""
from tests.security.fixtures.tenant_boundary import (  # noqa: F401
    tb_agent,
    tb_conversations_a,
    tb_conversations_b,
    tb_deliverables_a,
    tb_deliverables_b,
    tb_documents_a,
    tb_documents_b,
    tb_execution_null_user,
    tb_executions_a,
    tb_executions_b,
    tb_golden,
    tb_initiatives_a,
    tb_initiatives_b,
    tb_superuser,
    tb_user_a,
    tb_user_b,
    tb_workspace_a,
    tb_workspace_b,
)
