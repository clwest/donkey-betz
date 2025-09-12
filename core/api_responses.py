"""
Standardized API Response Formats
Provides consistent response envelopes across all API endpoints
"""

from typing import Any, Dict, List, Optional, Union
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class APIResponseEnvelope:
    """Standardized API response envelope"""
    
    @staticmethod
    def success(
        data: Any = None, 
        message: str = "Success",
        meta: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_200_OK
    ) -> JsonResponse:
        """
        Create a successful API response
        
        Args:
            data: The response data
            message: Success message
            meta: Additional metadata (pagination, etc.)
            status_code: HTTP status code
            
        Returns:
            JsonResponse with standardized success format
        """
        response_data = {
            "success": True,
            "data": data,
            "message": message
        }
        
        if meta:
            response_data["meta"] = meta
            
        return JsonResponse(
            response_data,
            status=status_code,
            encoder=DjangoJSONEncoder,
            safe=False
        )
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        error_code: str = "generic_error",
        details: Optional[Union[str, Dict, List]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST
    ) -> JsonResponse:
        """
        Create an error API response
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            status_code: HTTP status code
            
        Returns:
            JsonResponse with standardized error format
        """
        response_data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            response_data["error"]["details"] = details
            
        # Log error for monitoring
        logger.warning(
            f"API Error Response: {error_code} - {message}",
            extra={
                "status_code": status_code,
                "error_code": error_code,
                "details": details
            }
        )
            
        return JsonResponse(
            response_data,
            status=status_code,
            encoder=DjangoJSONEncoder,
            safe=False
        )
    
    @staticmethod
    def paginated(
        data: List[Any],
        page: int = 1,
        limit: int = 50,
        total: int = 0,
        message: str = "Success"
    ) -> JsonResponse:
        """
        Create a paginated API response
        
        Args:
            data: List of items for current page
            page: Current page number
            limit: Items per page
            total: Total number of items
            message: Success message
            
        Returns:
            JsonResponse with standardized paginated format
        """
        total_pages = (total + limit - 1) // limit if total > 0 else 1
        has_next = page < total_pages
        has_prev = page > 1
        
        meta = {
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        }
        
        return APIResponseEnvelope.success(
            data=data,
            message=message,
            meta=meta
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> JsonResponse:
        """Create a standardized 401 Unauthorized response"""
        return APIResponseEnvelope.error(
            message=message,
            error_code="authentication_required",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    @staticmethod
    def forbidden(message: str = "Access denied") -> JsonResponse:
        """Create a standardized 403 Forbidden response"""
        return APIResponseEnvelope.error(
            message=message,
            error_code="access_denied",
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> JsonResponse:
        """Create a standardized 404 Not Found response"""
        return APIResponseEnvelope.error(
            message=message,
            error_code="not_found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        details: Optional[Dict] = None
    ) -> JsonResponse:
        """Create a standardized validation error response"""
        return APIResponseEnvelope.error(
            message=message,
            error_code="validation_error",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    @staticmethod
    def rate_limited(message: str = "Too many requests") -> JsonResponse:
        """Create a standardized rate limit response"""
        return APIResponseEnvelope.error(
            message=message,
            error_code="rate_limited",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    @staticmethod
    def server_error(
        message: str = "Internal server error",
        error_id: Optional[str] = None
    ) -> JsonResponse:
        """Create a standardized server error response"""
        details = {"error_id": error_id} if error_id else None
        
        return APIResponseEnvelope.error(
            message=message,
            error_code="server_error",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Convenience functions for common response patterns
def api_success(data=None, message="Success", **kwargs):
    """Shortcut for success response"""
    return APIResponseEnvelope.success(data, message, **kwargs)

def api_error(message, error_code="generic_error", **kwargs):
    """Shortcut for error response"""  
    return APIResponseEnvelope.error(message, error_code, **kwargs)

def api_paginated(data, **kwargs):
    """Shortcut for paginated response"""
    return APIResponseEnvelope.paginated(data, **kwargs)

def api_unauthorized(message="Authentication required"):
    """Shortcut for 401 response"""
    return APIResponseEnvelope.unauthorized(message)

def api_forbidden(message="Access denied"):
    """Shortcut for 403 response"""
    return APIResponseEnvelope.forbidden(message)

def api_not_found(message="Resource not found"):
    """Shortcut for 404 response"""
    return APIResponseEnvelope.not_found(message)

def api_validation_error(message="Validation failed", details=None):
    """Shortcut for validation error response"""
    return APIResponseEnvelope.validation_error(message, details)