"""Token-auth test helpers.

Created S3016 (Fold E) after PR #3714: `/api/initiatives/` sat in
`UnifiedTokenAuthenticationMiddleware.PUBLIC_PATHS` as a bare prefix — the
middleware short-circuited before token parsing, so Token-authenticated
callers landed as AnonymousUser and workspace-scoped querysets returned
`.none()`. All existing endpoint tests use `client.force_login()` (session
auth), so the divergence was invisible until Chris hit an empty Initiatives
tab in the browser.

`token_client_for(user)` returns a `Client` that authenticates via the
`Authorization: Token …` header, mirroring what the React frontend sends
after login. Pair with `client.force_login(user)` in a parity assertion to
guarantee both auth paths return the same shape for the same user.
"""
from __future__ import annotations

from django.test import Client
from rest_framework.authtoken.models import Token


def token_client_for(user, *, host: str = "localhost:8000") -> Client:
    """Return a Client that authenticates as `user` via Token in the header.

    Idempotent: reuses the existing DRF Token if one is already provisioned.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return Client(
        HTTP_HOST=host,
        HTTP_AUTHORIZATION=f"Token {token.key}",
    )
