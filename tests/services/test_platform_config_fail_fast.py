"""S3043 T1 v2 — silent-default resolver migration tests.

Three targeted tests per T1 Spec v1 §Test discipline:

1. ``get_primary_workspace`` raises ``PrimaryWorkspaceUnavailable`` when a
   workspace id is configured but the row cannot be fetched.
2. Integration smoke: ``get_primary_workspace`` returns ``None`` (not
   raises) when no primary workspace is configured at all — the
   "unconfigured" branch stays graceful.
3. ``operation_recorder.record_op`` degrades gracefully (drops the op with
   a warning, never propagates the exception) when
   ``get_primary_workspace`` raises ``PrimaryWorkspaceUnavailable``.

These are unit tests with no real DB access. The Django model layer is
mocked at the boundary so the tests exercise the exception surface
without needing a workspace fixture.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.services.platform_config import (
    PrimaryWorkspaceUnavailable,
    clear_config_cache,
    get_primary_workspace,
)


@pytest.fixture(autouse=True)
def _reset_platform_config_cache():
    """Clear the ``lru_cache`` on ``_cached_primary_workspace_id`` before and
    after each test so cache carryover from one test does not leak into the
    next. Every test in this module either mocks
    ``_cached_primary_workspace_id`` directly (bypassing the cache) or
    relies on it returning ``None``, so the reset is defensive."""
    clear_config_cache()
    yield
    clear_config_cache()


def test_get_primary_workspace_raises_when_id_configured_but_row_missing():
    """Substrate hardening: a configured workspace id that no longer
    resolves is a MISCONFIGURATION signal, not a silent None. Callers can
    still catch and degrade, but the default posture is fail-loud."""
    from django.core.exceptions import ObjectDoesNotExist

    with patch(
        "core.services.platform_config._cached_primary_workspace_id",
        return_value="00000000-0000-0000-0000-000000000000",
    ), patch(
        "core.models_skin_layer.ProjectWorkspace"
    ) as mock_ws_model:
        # Simulate the row not existing in the DB (deleted, wrong id, etc).
        mock_ws_model.objects.get.side_effect = ObjectDoesNotExist(
            "ProjectWorkspace matching query does not exist."
        )

        with pytest.raises(PrimaryWorkspaceUnavailable) as excinfo:
            get_primary_workspace()

        assert "00000000-0000-0000-0000-000000000000" in str(excinfo.value)
        assert "ObjectDoesNotExist" in str(excinfo.value)


def test_get_primary_workspace_returns_none_when_unconfigured():
    """Integration smoke: the "no config at all" case still returns
    ``None`` gracefully — this branch is not the misconfiguration signal
    the fail-fast contract covers. Confirms the two states remain
    distinguishable to callers."""
    with patch(
        "core.services.platform_config._cached_primary_workspace_id",
        return_value=None,
    ):
        assert get_primary_workspace() is None


def test_operation_recorder_drops_op_on_primary_workspace_unavailable():
    """Fire-and-forget contract: ``record_op`` must never propagate
    ``PrimaryWorkspaceUnavailable``. The op is dropped with a warning and
    the caller sees no exception. Guarantees fail-fast in the substrate
    does not cascade into every write-path caller."""
    from core.services import operation_recorder

    fake_get_primary_workspace = MagicMock(
        side_effect=PrimaryWorkspaceUnavailable(
            "test: primary workspace id=deadbeef configured but cannot "
            "be resolved: ObjectDoesNotExist: test"
        )
    )

    with patch.object(
        operation_recorder, "logger"
    ) as mock_logger, patch(
        "core.models_skin_layer.ProjectWorkspace"
    ) as mock_ws_model, patch(
        "core.services.platform_config.get_primary_workspace",
        fake_get_primary_workspace,
    ):
        # No explicit workspace_id and no is_active fallback available.
        mock_ws_model.DoesNotExist = Exception
        # record_op is sync-safe when called from a sync context; the async
        # branch does not fire in pytest's default event loop shape.
        operation_recorder.record_op(
            workspace_id=None,
            op_type="test_op",
            title="test title",
        )

        fake_get_primary_workspace.assert_called_once()
        # First warning: the PrimaryWorkspaceUnavailable branch logged its
        # own line. Second warning: the "op dropped" branch. We assert on
        # the first because it is the load-bearing evidence that the
        # exception was caught, not that any specific log line was
        # emitted.
        warning_calls = mock_logger.warning.call_args_list
        assert warning_calls, "record_op should have emitted at least one warning"
        first_fmt = warning_calls[0].args[0]
        assert "Primary workspace configured but unavailable" in first_fmt
