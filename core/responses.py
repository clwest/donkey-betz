"""
Standardized API response helpers.
Phase 2 High Priority - Task 2.7

Provides consistent response formats across all API endpoints.
"""

from django.http import JsonResponse
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# SUCCESS RESPONSES
# =============================================================================

def success_response(
    data: Any = None,
    message: str = None,
    status: int = 200,
    **extra_fields
) -> JsonResponse:
    """
    Return standardized success response.

    Args:
        data: Response data payload
        message: Optional success message
        status: HTTP status code (default 200)
        **extra_fields: Additional fields to include in response

    Returns:
        JsonResponse with success=True
    """
    response = {'success': True}

    if message:
        response['message'] = message

    if data is not None:
        response['data'] = data

    # Add any extra fields
    response.update(extra_fields)

    return JsonResponse(response, status=status)


def created_response(data: Any = None, message: str = "Resource created successfully") -> JsonResponse:
    """Return 201 Created response."""
    return success_response(data=data, message=message, status=201)


def accepted_response(data: Any = None, message: str = "Request accepted for processing") -> JsonResponse:
    """Return 202 Accepted response (for async operations)."""
    return success_response(data=data, message=message, status=202)


def no_content_response() -> JsonResponse:
    """Return 204 No Content response."""
    return JsonResponse({}, status=204)


# =============================================================================
# ERROR RESPONSES
# =============================================================================

def error_response(
    message: str,
    status: int = 400,
    error_code: str = None,
    details: Dict = None,
    log_error: bool = True,
    log_level: str = 'warning'
) -> JsonResponse:
    """
    Return standardized error response.

    Args:
        message: User-friendly error message (safe to display)
        status: HTTP status code
        error_code: Machine-readable error code (e.g., 'VALIDATION_ERROR')
        details: Additional error details (safe to display)
        log_error: Whether to log the error
        log_level: Log level ('debug', 'info', 'warning', 'error')

    Returns:
        JsonResponse with success=False
    """
    response = {
        'success': False,
        'error': message
    }

    if error_code:
        response['error_code'] = error_code

    if details:
        response['details'] = details

    if log_error:
        log_msg = f"API Error [{status}]: {message}"
        if error_code:
            log_msg += f" (code: {error_code})"

        log_func = getattr(logger, log_level, logger.warning)
        log_func(log_msg)

    return JsonResponse(response, status=status)


# =============================================================================
# COMMON ERROR RESPONSES
# =============================================================================

def validation_error(message: str, field: str = None, details: Dict = None) -> JsonResponse:
    """
    Return validation error response (400).

    Args:
        message: Error message
        field: Name of the invalid field
        details: Additional validation details
    """
    error_details = details or {}
    if field:
        error_details['field'] = field

    return error_response(
        message=message,
        status=400,
        error_code='VALIDATION_ERROR',
        details=error_details if error_details else None
    )


def not_found_error(resource: str = 'Resource', identifier: str = None) -> JsonResponse:
    """
    Return not found error response (404).

    Args:
        resource: Type of resource (e.g., 'Image', 'Video', 'Project')
        identifier: Optional identifier of the resource
    """
    if identifier:
        message = f'{resource} with ID {identifier} not found'
    else:
        message = f'{resource} not found'

    return error_response(
        message=message,
        status=404,
        error_code='NOT_FOUND',
        log_level='info'
    )


def unauthorized_error(message: str = 'Authentication required') -> JsonResponse:
    """Return unauthorized error response (401)."""
    return error_response(
        message=message,
        status=401,
        error_code='UNAUTHORIZED',
        log_level='info'
    )


def forbidden_error(message: str = 'You do not have permission to access this resource') -> JsonResponse:
    """Return forbidden error response (403)."""
    return error_response(
        message=message,
        status=403,
        error_code='FORBIDDEN',
        log_level='warning'
    )


def method_not_allowed_error(allowed_methods: list = None) -> JsonResponse:
    """
    Return method not allowed error response (405).

    Args:
        allowed_methods: List of allowed HTTP methods
    """
    details = {'allowed_methods': allowed_methods} if allowed_methods else None

    return error_response(
        message='Method not allowed',
        status=405,
        error_code='METHOD_NOT_ALLOWED',
        details=details,
        log_level='info'
    )


def rate_limit_error(retry_after: int = 60) -> JsonResponse:
    """
    Return rate limit exceeded error response (429).

    Args:
        retry_after: Seconds until the client can retry
    """
    response = error_response(
        message='Rate limit exceeded. Please wait before making more requests.',
        status=429,
        error_code='RATE_LIMITED',
        details={'retry_after': retry_after},
        log_level='warning'
    )
    response['Retry-After'] = str(retry_after)
    return response


def conflict_error(message: str = 'Resource conflict') -> JsonResponse:
    """Return conflict error response (409)."""
    return error_response(
        message=message,
        status=409,
        error_code='CONFLICT'
    )


def payload_too_large_error(max_size: str = None) -> JsonResponse:
    """
    Return payload too large error response (413).

    Args:
        max_size: Maximum allowed size (e.g., '10MB')
    """
    message = 'Request payload is too large'
    if max_size:
        message += f'. Maximum allowed size is {max_size}'

    return error_response(
        message=message,
        status=413,
        error_code='PAYLOAD_TOO_LARGE'
    )


def unprocessable_entity_error(message: str = 'Unable to process the request') -> JsonResponse:
    """Return unprocessable entity error response (422)."""
    return error_response(
        message=message,
        status=422,
        error_code='UNPROCESSABLE_ENTITY'
    )


def server_error(
    log_message: str = None,
    user_message: str = 'An unexpected error occurred. Please try again later.'
) -> JsonResponse:
    """
    Return generic server error response (500).

    IMPORTANT: Never expose internal details to the client.

    Args:
        log_message: Internal error message (logged but not returned)
        user_message: Safe message to show to the user
    """
    if log_message:
        logger.error(f"Server error: {log_message}")

    return error_response(
        message=user_message,
        status=500,
        error_code='SERVER_ERROR',
        log_error=False  # Already logged above
    )


def safe_error_message(exception: Exception, context: str = None) -> str:
    """
    Convert an exception to a safe user-facing error message.

    Phase 2 P1: Prevents information leakage by not exposing internal details.

    Args:
        exception: The exception that was raised
        context: Optional context for the error (e.g., 'image generation', 'video processing')

    Returns:
        A safe, user-friendly error message
    """
    # Log the full error for debugging
    if context:
        logger.error(f"Error in {context}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"Error: {str(exception)}", exc_info=True)

    # Map common exception types to user-friendly messages
    exception_messages = {
        'ConnectionError': 'Unable to connect to the service. Please try again.',
        'TimeoutError': 'The operation timed out. Please try again.',
        'FileNotFoundError': 'The requested file was not found.',
        'PermissionError': 'Permission denied. Please check your access rights.',
        'ValueError': 'Invalid input provided. Please check your data.',
        'KeyError': 'Missing required data. Please check your input.',
        'TypeError': 'Invalid data type provided.',
        'JSONDecodeError': 'Invalid JSON format received.',
        'ValidationError': 'Input validation failed. Please check your data.',
    }

    exception_type = type(exception).__name__

    # Check for known exception types
    for error_type, message in exception_messages.items():
        if error_type in exception_type:
            return message

    # For API-related errors, extract safe portions
    error_str = str(exception).lower()
    if 'api' in error_str or 'key' in error_str or 'auth' in error_str:
        return 'Service authentication failed. Please try again later.'
    if 'rate' in error_str and 'limit' in error_str:
        return 'Rate limit exceeded. Please wait before trying again.'
    if 'network' in error_str or 'connection' in error_str:
        return 'Network error. Please check your connection and try again.'

    # Default safe message
    if context:
        return f'An error occurred during {context}. Please try again later.'
    return 'An unexpected error occurred. Please try again later.'


def handle_exception(
    exception: Exception,
    context: str = None,
    status: int = 500
) -> JsonResponse:
    """
    Handle an exception and return a safe JsonResponse.

    Phase 2 P1: Provides consistent, safe error handling across all endpoints.

    Args:
        exception: The exception that was raised
        context: Optional context for the error
        status: HTTP status code (default 500)

    Returns:
        JsonResponse with safe error message

    Example:
        try:
            result = risky_operation()
        except Exception as e:
            return handle_exception(e, context='image generation')
    """
    safe_message = safe_error_message(exception, context)

    return error_response(
        message=safe_message,
        status=status,
        error_code='SERVER_ERROR' if status == 500 else 'ERROR',
        log_error=False  # Already logged in safe_error_message
    )


def service_unavailable_error(
    message: str = 'Service temporarily unavailable. Please try again later.',
    retry_after: int = None
) -> JsonResponse:
    """
    Return service unavailable error response (503).

    Args:
        message: User-friendly message
        retry_after: Optional seconds until service is expected to be available
    """
    details = {'retry_after': retry_after} if retry_after else None

    response = error_response(
        message=message,
        status=503,
        error_code='SERVICE_UNAVAILABLE',
        details=details
    )

    if retry_after:
        response['Retry-After'] = str(retry_after)

    return response


# =============================================================================
# AI/ML SPECIFIC RESPONSES
# =============================================================================

def generation_started_response(
    task_id: str,
    message: str = 'Generation started',
    poll_url: str = None,
    estimated_time: int = None
) -> JsonResponse:
    """
    Return response for async generation task started.

    Args:
        task_id: Unique identifier for the task
        message: Status message
        poll_url: URL to poll for status
        estimated_time: Estimated time in seconds
    """
    data = {'task_id': task_id}

    if poll_url:
        data['poll_url'] = poll_url

    if estimated_time:
        data['estimated_time_seconds'] = estimated_time

    return success_response(
        data=data,
        message=message,
        status=202
    )


def generation_complete_response(
    result: Any,
    task_id: str = None,
    processing_time: float = None,
    cost: float = None
) -> JsonResponse:
    """
    Return response for completed generation task.

    Args:
        result: The generated result
        task_id: Task identifier
        processing_time: Time taken in seconds
        cost: Cost of the operation
    """
    data = {'result': result}

    if task_id:
        data['task_id'] = task_id

    if processing_time is not None:
        data['processing_time_seconds'] = round(processing_time, 2)

    if cost is not None:
        data['cost'] = round(cost, 4)

    return success_response(data=data)


def credit_insufficient_error(
    required: int = None,
    available: int = None
) -> JsonResponse:
    """
    Return insufficient credits error response.

    Args:
        required: Credits required for operation
        available: Credits available to user
    """
    message = 'Insufficient credits for this operation'
    details = {}

    if required is not None:
        details['credits_required'] = required
    if available is not None:
        details['credits_available'] = available

    return error_response(
        message=message,
        status=402,
        error_code='INSUFFICIENT_CREDITS',
        details=details if details else None
    )


# =============================================================================
# BATCH OPERATION RESPONSES
# =============================================================================

def batch_response(
    results: list,
    total: int = None,
    successful: int = None,
    failed: int = None
) -> JsonResponse:
    """
    Return response for batch operations.

    Args:
        results: List of individual operation results
        total: Total number of items processed
        successful: Number of successful operations
        failed: Number of failed operations
    """
    data = {'results': results}

    if total is not None:
        data['total'] = total
    if successful is not None:
        data['successful'] = successful
    if failed is not None:
        data['failed'] = failed

    return success_response(data=data)
