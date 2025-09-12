"""
Memory Access Control System
Ensures proper user authentication and authorization for personal memories
"""

import logging
from typing import Optional, Dict, Any, List
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.core.exceptions import PermissionDenied
from functools import wraps

logger = logging.getLogger(__name__)

class MemoryAccessController:
    """
    Controls access to personal memories with strict authentication
    """
    
    @staticmethod
    def verify_user_access(user: Optional[User], requested_user_id: Optional[int] = None) -> bool:
        """
        Verify user has access to requested memories
        
        Args:
            user: Django user object from request
            requested_user_id: ID of user whose memories are being accessed
        
        Returns:
            True if access allowed, False otherwise
        """
        if not user or not user.is_authenticated:
            logger.warning("Unauthenticated user attempted to access personal memories")
            return False
        
        # If no specific user requested, they can access their own
        if requested_user_id is None:
            return True
            
        # Users can only access their own memories
        if user.id != requested_user_id:
            logger.warning(f"User {user.id} attempted to access memories of user {requested_user_id}")
            return False
            
        return True
    
    @staticmethod
    def get_user_id_from_request(request: HttpRequest) -> Optional[int]:
        """
        Extract user ID from authenticated request
        
        Args:
            request: Django HTTP request
            
        Returns:
            User ID if authenticated, None otherwise
        """
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        return request.user.id
    
    @staticmethod
    def filter_personal_results(results: List[Dict[str, Any]], user_id: int) -> List[Dict[str, Any]]:
        """
        Filter results to only include memories accessible to user
        
        Args:
            results: List of memory search results
            user_id: ID of requesting user
            
        Returns:
            Filtered results
        """
        filtered = []
        for result in results:
            metadata = result.get('metadata', {})
            
            # Check if memory belongs to user
            owner_id = metadata.get('owner_id')
            if owner_id and str(owner_id) != str(user_id):
                logger.debug(f"Filtered out memory owned by user {owner_id}, requested by {user_id}")
                continue
                
            # Check if memory is marked as private
            if metadata.get('is_private', False) and metadata.get('namespace') == 'personal':
                if not owner_id or str(owner_id) != str(user_id):
                    logger.debug(f"Filtered out private memory, user {user_id} not authorized")
                    continue
            
            filtered.append(result)
        
        logger.info(f"Filtered {len(results)} results to {len(filtered)} for user {user_id}")
        return filtered

def require_personal_memory_access(view_func):
    """
    Decorator to require authentication for personal memory access
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required for personal memory access")
        
        # Add user_id to kwargs if not present
        if 'user_id' not in kwargs:
            kwargs['user_id'] = request.user.id
            
        return view_func(request, *args, **kwargs)
    
    return wrapper

def log_memory_access(user_id: int, query: str, results_count: int, access_type: str = 'search'):
    """
    Log memory access attempts for audit trail
    
    Args:
        user_id: ID of user accessing memories
        query: Search query or action performed  
        results_count: Number of results returned
        access_type: Type of access (search, view, edit, delete)
    """
    logger.info(f"MEMORY_ACCESS: User {user_id} performed {access_type} with query '{query[:50]}...' - {results_count} results")

def validate_memory_namespace(namespace: str, user_authenticated: bool) -> bool:
    """
    Validate that user can access requested namespace
    
    Args:
        namespace: Memory namespace being accessed
        user_authenticated: Whether user is authenticated
        
    Returns:
        True if access allowed, False otherwise
    """
    # Public namespaces accessible to all
    if namespace in ['public', 'system']:
        return True
        
    # Personal and agent_memory require authentication  
    if namespace in ['personal', 'agent_memory']:
        if not user_authenticated:
            logger.warning(f"Unauthenticated access attempted to {namespace} namespace")
            return False
        return True
    
    # Unknown namespace - deny by default
    logger.warning(f"Access attempted to unknown namespace: {namespace}")
    return False

class MemoryAccessMiddleware:
    """
    Django middleware to enforce memory access controls
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add access controller to request for easy access in views
        request.memory_access = MemoryAccessController()
        
        response = self.get_response(request)
        return response