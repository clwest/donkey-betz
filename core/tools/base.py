"""
Base Tool Class for Agent Tools

This module defines the base interface for all tools that agents can use.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """Abstract base class for all agent tools."""
    
    name: str = "base_tool"
    description: str = "Base tool interface"
    requires_auth: bool = False
    tool_type: str = "general"
    
    def __init__(self):
        """Initialize the tool."""
        self.logger = logging.getLogger(f"tools.{self.name}")
        self.is_configured = self._check_configuration()
        
        if not self.is_configured:
            self.logger.warning(f"{self.name} is not properly configured")
    
    @abstractmethod
    def _check_configuration(self) -> bool:
        """Check if the tool is properly configured."""
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """Execute the tool's main functionality."""
        pass
    
    def validate_input(self, *args, **kwargs) -> bool:
        """Validate input parameters."""
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about this tool."""
        return {
            'name': self.name,
            'description': self.description,
            'type': self.tool_type,
            'requires_auth': self.requires_auth,
            'is_configured': self.is_configured,
            'capabilities': self.get_capabilities()
        }
    
    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this tool provides."""
        return []
    
    def format_result(self, success: bool, data: Any = None, error: str = None) -> Dict[str, Any]:
        """Format tool execution result."""
        result = {
            'success': success,
            'tool': self.name
        }
        
        if data is not None:
            result['data'] = data
        
        if error:
            result['error'] = error
            self.logger.error(f"Tool error: {error}")
        
        return result