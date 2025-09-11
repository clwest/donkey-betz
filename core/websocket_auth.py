"""
WebSocket authentication middleware for token-based auth.
"""
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.middleware import BaseMiddleware


@database_sync_to_async
def get_user_from_token(token_key):
    """Get user from token key."""
    try:
        token = Token.objects.select_related('user').get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that supports token authentication for WebSockets.
    """
    
    async def __call__(self, scope, receive, send):
        # Try to get token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            # Fall back to session auth if available
            if 'user' not in scope or scope['user'] is None:
                scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)


def TokenAuthMiddlewareStack(inner):
    """Convenience wrapper for applying token auth middleware."""
    return TokenAuthMiddleware(inner)