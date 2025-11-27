"""
API Helper Functions
Common utilities for API responses.
"""

from django.http import JsonResponse


def api_success(data=None, message=None, status=200):
    """Return a success response."""
    response = {'success': True}
    if data is not None:
        response.update(data)
    if message:
        response['message'] = message
    return JsonResponse(response, status=status)


def api_error(message, status=400, errors=None):
    """Return an error response."""
    response = {
        'success': False,
        'error': {'message': message}
    }
    if errors:
        response['error']['details'] = errors
    return JsonResponse(response, status=status)
