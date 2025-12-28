"""
Security Configuration Validator
Validates and enforces consistent security settings across the platform
"""

import os
import re
import logging
from typing import Dict, Tuple, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validates platform security configuration"""
    
    # Patterns that indicate hardcoded secrets
    SECRET_PATTERNS = [
        r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
        r'[a-f0-9]{40}',        # 40-char hex tokens
        r'Bearer\s+[a-zA-Z0-9-_\.]+',  # Bearer tokens
        r'Token\s+[a-f0-9]{40}',  # Django tokens
    ]
    
    # Required security headers for production
    REQUIRED_SECURITY_HEADERS = {
        'SECURE_SSL_REDIRECT': True,
        'SECURE_HSTS_SECONDS': 31536000,  # 1 year
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_BROWSER_XSS_FILTER': True,
        'X_FRAME_OPTIONS': 'DENY',
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'CSRF_COOKIE_SECURE': True,
        'CSRF_COOKIE_HTTPONLY': True,
    }
    
    # Required environment variables for production
    REQUIRED_PROD_VARS = [
        'SECRET_KEY',
        'DATABASE_URL',
        'REDIS_URL',
        'ALLOWED_HOSTS',
        'CORS_ALLOWED_ORIGINS',
    ]
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all security validations"""
        self.issues = []
        self.warnings = []
        self.recommendations = []
        
        # Run individual validations
        self.validate_authentication_config()
        self.validate_cors_config()
        self.validate_security_headers()
        self.validate_websocket_security()
        self.validate_environment_variables()
        self.validate_api_security()
        self.scan_for_hardcoded_secrets()
        
        return {
            'valid': len(self.issues) == 0,
            'issues': self.issues,
            'warnings': self.warnings,
            'recommendations': self.recommendations,
            'summary': self.generate_summary()
        }
    
    def validate_authentication_config(self):
        """Validate authentication configuration"""
        # Check REST framework authentication
        rest_auth = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_AUTHENTICATION_CLASSES', [])
        
        if 'rest_framework.authentication.TokenAuthentication' not in rest_auth:
            self.warnings.append("Token authentication not configured in REST_FRAMEWORK")
        
        # Check if WebSocket authentication is enabled
        ws_auth_enabled = os.getenv('ENABLE_WEBSOCKET_AUTH', 'true').lower() == 'true'
        if not ws_auth_enabled and not settings.DEBUG:
            self.issues.append("WebSocket authentication disabled in production")
        
        # Check for secure session configuration
        if not getattr(settings, 'SESSION_COOKIE_SECURE', False) and not settings.DEBUG:
            self.issues.append("Session cookies not secure in production")
            
    def validate_cors_config(self):
        """Validate CORS configuration"""
        # Check if CORS allows all origins
        cors_all_origins = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        if cors_all_origins:
            if not settings.DEBUG:
                self.issues.append("CORS_ALLOW_ALL_ORIGINS=True in production - security risk!")
            else:
                self.warnings.append("CORS_ALLOW_ALL_ORIGINS=True in development")
        
        # Check for specific allowed origins
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if not cors_origins and not cors_all_origins:
            self.warnings.append("No CORS origins configured")
        
        # Check for wildcard origins in production
        if not settings.DEBUG:
            for origin in cors_origins:
                if '*' in origin:
                    self.issues.append(f"Wildcard CORS origin in production: {origin}")
    
    def validate_security_headers(self):
        """Validate security headers for production"""
        if settings.DEBUG:
            return  # Skip in development
        
        for header, expected_value in self.REQUIRED_SECURITY_HEADERS.items():
            current_value = getattr(settings, header, None)
            
            if current_value != expected_value:
                self.issues.append(
                    f"Security header {header} should be {expected_value}, "
                    f"currently: {current_value}"
                )
    
    def validate_websocket_security(self):
        """Validate WebSocket security configuration"""
        # Check channel layer security
        channel_layers = getattr(settings, 'CHANNEL_LAYERS', {})
        default_layer = channel_layers.get('default', {})
        
        if default_layer.get('BACKEND') == 'channels.layers.InMemoryChannelLayer':
            self.warnings.append("Using in-memory channel layer - not suitable for production")
        
        # Check Redis channel configuration
        if 'channels_redis' in str(default_layer.get('BACKEND', '')):
            redis_hosts = default_layer.get('CONFIG', {}).get('hosts', [])
            for host in redis_hosts:
                if isinstance(host, str) and 'password' not in host.lower():
                    self.warnings.append("Redis channel layer may not be password protected")
    
    def validate_environment_variables(self):
        """Validate required environment variables"""
        if settings.DEBUG:
            return  # More lenient in development
        
        for var in self.REQUIRED_PROD_VARS:
            if not os.getenv(var):
                self.issues.append(f"Required environment variable missing: {var}")
        
        # Check for default/weak values
        secret_key = getattr(settings, 'SECRET_KEY', '')
        if len(secret_key) < 50:
            self.issues.append("SECRET_KEY is too short (minimum 50 characters)")
        
        if 'change-me' in secret_key.lower() or 'django' in secret_key.lower():
            self.issues.append("SECRET_KEY appears to be a default/weak value")
    
    def validate_api_security(self):
        """Validate API security configuration"""
        # Check rate limiting
        rest_throttle = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_THROTTLE_CLASSES', [])
        if not rest_throttle:
            self.warnings.append("API rate limiting not configured")
        
        # Check API authentication requirements
        rest_permissions = getattr(settings, 'REST_FRAMEWORK', {}).get('DEFAULT_PERMISSION_CLASSES', [])
        if 'rest_framework.permissions.AllowAny' in rest_permissions:
            self.warnings.append("Default API permissions allow any user")
    
    def scan_for_hardcoded_secrets(self):
        """Scan codebase for hardcoded secrets"""
        from pathlib import Path
        
        base_dir = Path(settings.BASE_DIR)
        
        # Files to scan
        file_patterns = [
            '**/*.py', '**/*.js', '**/*.ts', '**/*.tsx', 
            '**/*.json', '**/*.html', '**/*.md'
        ]
        
        secret_files = []
        
        for pattern in file_patterns:
            for file_path in base_dir.glob(pattern):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['node_modules', 'venv', '.git', '__pycache__']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    # Check for secret patterns
                    for pattern in self.SECRET_PATTERNS:
                        if re.search(pattern, content):
                            secret_files.append(str(file_path.relative_to(base_dir)))
                            break
                            
                except (UnicodeDecodeError, PermissionError):
                    continue  # Skip binary or inaccessible files
        
        if secret_files:
            self.issues.append(f"Potential hardcoded secrets found in files: {secret_files[:5]}")
            if len(secret_files) > 5:
                self.issues.append(f"...and {len(secret_files) - 5} more files")
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        severity = "SECURE"
        if total_issues > 0:
            severity = "CRITICAL" if total_issues >= 5 else "HIGH"
        elif total_warnings > 5:
            severity = "MEDIUM"
        
        return {
            'severity': severity,
            'total_issues': total_issues,
            'total_warnings': total_warnings,
            'total_recommendations': len(self.recommendations),
            'environment': 'production' if not settings.DEBUG else 'development'
        }
    
    def get_security_score(self) -> Tuple[int, str]:
        """Calculate security score (0-100)"""
        base_score = 100
        
        # Deduct points for issues
        base_score -= len(self.issues) * 10
        base_score -= len(self.warnings) * 5
        
        # Bonus points for good practices
        if not settings.DEBUG and getattr(settings, 'SECURE_SSL_REDIRECT', False):
            base_score += 5
        
        if os.getenv('ENABLE_WEBSOCKET_AUTH', 'true').lower() == 'true':
            base_score += 5
            
        score = max(0, min(100, base_score))
        
        if score >= 90:
            grade = 'A'
        elif score >= 80:
            grade = 'B'  
        elif score >= 70:
            grade = 'C'
        elif score >= 60:
            grade = 'D'
        else:
            grade = 'F'
            
        return score, grade


def run_security_validation() -> Dict[str, Any]:
    """Run complete security validation"""
    validator = SecurityValidator()
    results = validator.validate_all()
    score, grade = validator.get_security_score()
    
    results['security_score'] = score
    results['security_grade'] = grade
    
    return results


def check_endpoint_security(view_func):
    """Decorator to check endpoint security"""
    def wrapper(*args, **kwargs):
        # Add security headers to response
        response = view_func(*args, **kwargs)
        
        # Add standard security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    return wrapper