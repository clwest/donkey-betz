"""
WebSocket Token Authentication Middleware
Handles both cookie-based and token-based authentication for WebSocket connections
"""
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from urllib.parse import parse_qs

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_key):
    """Get user from token key"""
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """
    Token authentication middleware for WebSocket connections.
    Checks for token in query string parameters.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Try to get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        # If we have a token and no authenticated user from session, try token auth
        if token and (not scope.get('user') or isinstance(scope['user'], AnonymousUser)):
            scope['user'] = await get_user_from_token(token)

        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    """
    A middleware stack that adds token authentication support to WebSocket connections.
    Wraps the standard AuthMiddlewareStack.
    """
    from channels.auth import AuthMiddlewareStack
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))