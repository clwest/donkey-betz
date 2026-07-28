"""Session 3016 (Fold E): Regression guard for PR #3714 — Token-auth parity
on `/api/initiatives/`.

Locks the exact scenario Chris hit in the browser: token in localStorage,
React frontend sends `Authorization: Token …`, middleware short-circuits
before token parsing (bare-prefix in PUBLIC_PATHS), request.user stays
AnonymousUser, `scope_queryset_initiative` returns `.none()`, endpoint
returns count=0 even though the same user via session auth sees N.

The fix (PR #3714) moved `/api/initiatives/` from PUBLIC_PATHS to
OPTIONAL_AUTH_PATHS. This test asserts session-auth and Token-auth return
the same count + first-page item ids for the same user + workspace filter.
Failure signals the bare-prefix regression has come back or the middleware
optional-auth path has broken.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from core.models_document_registry import Initiative
from core.models_skin_layer import ProjectWorkspace
from core.tests.helpers.token_auth import token_client_for


User = get_user_model()

INITIATIVES_URL = "/api/initiatives/"


class InitiativesListAuthParityTests(TestCase):
    """PR #3714 regression: session-auth and Token-auth return identical shapes."""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="init_parity_user",
            email="init_parity_user@example.com",
            password="test-pw",
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name="init-parity-workspace",
            root_path="/tmp/init-parity",
        )
        # Seed a few initiatives owned by user + scoped to workspace
        for i in range(3):
            Initiative.objects.create(
                name=f"Init parity {i}",
                description="regression seed",
                status=Initiative.Status.ACTIVE,
                owner=self.user,
                target_workspace=self.workspace,
            )

    def _session_client(self) -> Client:
        c = Client(HTTP_HOST="localhost:8000")
        c.force_login(self.user)
        return c

    def _extract_ids(self, body: dict) -> list[str]:
        # Endpoint shape: {"initiatives": [{"id": ...}, ...], "count": N}
        return [str(row["id"]) for row in body.get("initiatives", [])]

    def test_token_and_session_auth_return_identical_shape(self) -> None:
        params = {"workspace": str(self.workspace.id), "limit": 50}

        session_resp = self._session_client().get(INITIATIVES_URL, data=params)
        token_resp = token_client_for(self.user).get(INITIATIVES_URL, data=params)

        self.assertEqual(session_resp.status_code, 200)
        self.assertEqual(token_resp.status_code, 200)

        session_body = session_resp.json()
        token_body = token_resp.json()

        # Parity: both auth modes see the same user's initiatives
        self.assertEqual(session_body["count"], 3)
        self.assertEqual(token_body["count"], session_body["count"])
        self.assertEqual(self._extract_ids(token_body), self._extract_ids(session_body))

    def test_token_auth_alone_returns_owned_initiatives_not_empty(self) -> None:
        """Direct S3015 scenario — Token-auth in isolation must not return count=0."""
        resp = token_client_for(self.user).get(
            INITIATIVES_URL,
            data={"workspace": str(self.workspace.id), "limit": 50},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["count"], 3)
        self.assertEqual(len(body["initiatives"]), 3)

    def test_anonymous_still_returns_empty_200(self) -> None:
        """OPTIONAL_AUTH_PATHS contract — anon caller still reaches the view,
        but scope_queryset_initiative(AnonymousUser) returns .none() → count=0.
        Locks the 'safe to expose publicly' half of the PR #3714 fix so a
        future migration back to PUBLIC_PATHS (or a broader auth change) that
        would leak other users' data becomes a visible regression.
        """
        anon = Client(HTTP_HOST="localhost:8000")
        resp = anon.get(
            INITIATIVES_URL,
            data={"workspace": str(self.workspace.id), "limit": 50},
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["count"], 0)
        self.assertEqual(body["initiatives"], [])
