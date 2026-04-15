"""
Secure Environment Variable Management System
Provides secure handling of sensitive configuration data
"""

import os
import base64
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class SecureEnvironmentManager:
    """
    Manages secure environment variables with encryption and validation
    """
    
    # List of sensitive keys that should never be logged
    SENSITIVE_KEYS = [
        'SECRET_KEY', 'PASSWORD', 'TOKEN', 'API_KEY', 'PRIVATE_KEY',
        'ACCESS_KEY', 'SECRET', 'CREDENTIAL', 'AUTH', 'CERTIFICATE'
    ]
    
    # Required keys for production
    REQUIRED_PRODUCTION_KEYS = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'ALLOWED_HOSTS',
        'CORS_ALLOWED_ORIGINS',
    ]
    
    def __init__(self, environment: str = 'development'):
        """
        Initialize the secure environment manager
        
        Args:
            environment: Current environment (development, staging, production)
        """
        self.environment = environment
        self.is_production = environment == 'production'
        self._cache = {}
        self._encryption_key = self._get_or_create_encryption_key()
        
    def _get_or_create_encryption_key(self) -> Optional[bytes]:
        """
        Get or create an encryption key for sensitive data
        """
        key_file = Path.home() / '.donkey_betz' / 'encryption.key'
        
        try:
            # Create directory if it doesn't exist
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            if key_file.exists():
                # Read existing key
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Set restrictive permissions
                os.chmod(key_file, 0o600)
                logger.info("Generated new encryption key")
                return key
        except Exception as e:
            logger.warning(f"Could not manage encryption key: {str(e)}")
            # Fall back to environment-based key
            env_key = os.getenv('ENCRYPTION_KEY')
            if env_key:
                return env_key.encode()
            return None
    
    def encrypt_value(self, value: str) -> str:
        """
        Encrypt a sensitive value
        
        Args:
            value: The value to encrypt
            
        Returns:
            Base64 encoded encrypted value
        """
        if not self._encryption_key:
            return value  # Return unencrypted if no key available
            
        try:
            f = Fernet(self._encryption_key)
            encrypted = f.encrypt(value.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            return value
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """
        Decrypt a sensitive value
        
        Args:
            encrypted_value: Base64 encoded encrypted value
            
        Returns:
            Decrypted value
        """
        if not self._encryption_key:
            return encrypted_value  # Return as-is if no key available
            
        try:
            f = Fernet(self._encryption_key)
            decoded = base64.b64decode(encrypted_value.encode())
            decrypted = f.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            # If decryption fails, assume it's not encrypted
            return encrypted_value
    
    def get(self, key: str, default: Any = None, required: bool = False) -> Any:
        """
        Get an environment variable with optional decryption
        
        Args:
            key: Environment variable name
            default: Default value if not found
            required: Whether this variable is required
            
        Returns:
            The environment variable value
            
        Raises:
            ImproperlyConfigured: If required variable is missing
        """
        # Check cache first
        if key in self._cache:
            return self._cache[key]
        
        # Get from environment
        value = os.getenv(key)
        
        if value is None:
            if required or (self.is_production and key in self.REQUIRED_PRODUCTION_KEYS):
                raise ImproperlyConfigured(
                    f"Required environment variable '{key}' is not set. "
                    f"Please check your .env file or environment configuration."
                )
            value = default
        else:
            # Decrypt if it's a sensitive key and appears encrypted
            if self._is_sensitive_key(key) and self._looks_encrypted(value):
                value = self.decrypt_value(value)
        
        # Cache the value
        self._cache[key] = value
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get a boolean environment variable
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Boolean value
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get an integer environment variable
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Integer value
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            logger.warning(f"Invalid integer value for {key}: {value}")
            return default
    
    def get_list(self, key: str, default: List = None, separator: str = ',') -> List:
        """
        Get a list from an environment variable
        
        Args:
            key: Environment variable name
            default: Default value if not found
            separator: String separator for list items
            
        Returns:
            List of values
        """
        value = self.get(key, '')
        if not value:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check required keys
        for key in self.REQUIRED_PRODUCTION_KEYS:
            if self.is_production:
                try:
                    value = self.get(key, required=True)
                    if not value:
                        results['errors'].append(f"Required key '{key}' is empty")
                        results['valid'] = False
                except ImproperlyConfigured as e:
                    results['errors'].append(str(e))
                    results['valid'] = False
            else:
                # In development, just warn if missing
                if not os.getenv(key):
                    results['warnings'].append(f"Key '{key}' is not set (required in production)")
        
        # Check for exposed secrets
        for key in os.environ:
            if self._is_sensitive_key(key):
                value = os.getenv(key)
                if value and len(value) > 20 and not self._looks_encrypted(value):
                    results['warnings'].append(
                        f"Sensitive key '{key}' appears to be unencrypted. "
                        "Consider using encryption for additional security."
                    )
        
        # Check DEBUG setting in production
        if self.is_production:
            if self.get_bool('DEBUG', False):
                results['errors'].append("DEBUG is True in production!")
                results['valid'] = False
        
        # Check HTTPS enforcement
        if self.is_production:
            if not self.get_bool('SECURE_SSL_REDIRECT', False):
                results['warnings'].append("HTTPS redirect not enabled in production")
            if not self.get_bool('SESSION_COOKIE_SECURE', False):
                results['warnings'].append("Session cookies not secure in production")
            if not self.get_bool('CSRF_COOKIE_SECURE', False):
                results['warnings'].append("CSRF cookies not secure in production")
        
        # Check CORS configuration
        cors_all_origins = self.get_bool('CORS_ALLOW_ALL_ORIGINS', False)
        if cors_all_origins:
            if self.is_production:
                results['errors'].append("CORS_ALLOW_ALL_ORIGINS is True in production!")
                results['valid'] = False
            else:
                results['warnings'].append("CORS_ALLOW_ALL_ORIGINS is True - only use in development")
        
        # Check WebSocket authentication
        if not self.get_bool('ENABLE_WEBSOCKET_AUTH', True):
            if self.is_production:
                results['errors'].append("WebSocket authentication disabled in production!")
                results['valid'] = False
            else:
                results['warnings'].append("WebSocket authentication disabled - enable for production")
        
        # Info messages
        results['info'].append(f"Environment: {self.environment}")
        results['info'].append(f"Encryption: {'Enabled' if self._encryption_key else 'Disabled'}")
        
        return results
    
    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if a key name indicates sensitive data
        
        Args:
            key: Environment variable name
            
        Returns:
            True if the key appears to be sensitive
        """
        key_upper = key.upper()
        return any(sensitive in key_upper for sensitive in self.SENSITIVE_KEYS)
    
    def _looks_encrypted(self, value: str) -> bool:
        """
        Check if a value appears to be encrypted
        
        Args:
            value: The value to check
            
        Returns:
            True if the value looks encrypted
        """
        # Check for base64 encoded encrypted data pattern
        if len(value) > 100 and '=' in value:
            try:
                base64.b64decode(value)
                return True
            except Exception as _e:
                logger.warning(
                    "security._looks_encrypted: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )
        return False
    
    def mask_sensitive_value(self, key: str, value: Any) -> str:
        """
        Mask sensitive values for logging
        
        Args:
            key: The key name
            value: The value to mask
            
        Returns:
            Masked value safe for logging
        """
        if value is None:
            return 'None'
        
        if not self._is_sensitive_key(key):
            return str(value)
        
        value_str = str(value)
        if len(value_str) <= 8:
            return '***'
        
        # Show first 4 and last 4 characters
        return f"{value_str[:4]}...{value_str[-4:]}"
    
    def export_safe_config(self) -> Dict[str, str]:
        """
        Export configuration with sensitive values masked
        
        Returns:
            Dictionary of configuration suitable for logging
        """
        config = {}
        for key in os.environ:
            if key.startswith('DJANGO_') or key.startswith('VITE_') or \
               key in self.REQUIRED_PRODUCTION_KEYS or \
               any(prefix in key for prefix in ['ENABLE_', 'MAX_', 'MIN_']):
                value = os.getenv(key)
                config[key] = self.mask_sensitive_value(key, value)
        return config


# Global instance
_env_manager = None

def get_env_manager() -> SecureEnvironmentManager:
    """
    Get the global environment manager instance
    
    Returns:
        SecureEnvironmentManager instance
    """
    global _env_manager
    if _env_manager is None:
        environment = os.getenv('ENVIRONMENT', 'development')
        _env_manager = SecureEnvironmentManager(environment)
    return _env_manager


# Convenience functions
def env(key: str, default: Any = None, required: bool = False) -> Any:
    """Convenience function to get environment variable"""
    return get_env_manager().get(key, default, required)

def env_bool(key: str, default: bool = False) -> bool:
    """Convenience function to get boolean environment variable"""
    return get_env_manager().get_bool(key, default)

def env_int(key: str, default: int = 0) -> int:
    """Convenience function to get integer environment variable"""
    return get_env_manager().get_int(key, default)

def env_list(key: str, default: List = None, separator: str = ',') -> List:
    """Convenience function to get list environment variable"""
    return get_env_manager().get_list(key, default, separator)

def validate_environment() -> Dict[str, Any]:
    """Validate current environment configuration"""
    return get_env_manager().validate_configuration()