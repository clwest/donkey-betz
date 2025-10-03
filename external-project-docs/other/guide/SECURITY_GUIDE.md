# Security Guide - Donkey Betz Platform

**Last Updated**: July 10, 2025  
**Platform Status**: 75% Complete - Production Security Measures  
**Security Level**: High - AI/ML Platform with Financial Data

## 🔐 **Security Overview**

The Donkey Betz platform handles sensitive data including:
- **Financial Data**: Real-time stock data via Polygon.io
- **Personal Data**: User profiles, conversations, memory storage
- **Business Data**: Generated business plans, proprietary strategies
- **API Keys**: Multiple third-party service integrations
- **User Content**: AI-generated images, videos, documents

## 🚨 **Critical Security Requirements**

### 1. **Environment Variables Security**

**NEVER commit sensitive data to version control**

```bash
# backend/.env (REQUIRED)
# Copy from backend/.env.example and populate with real values

# Essential Security Keys
SECRET_KEY="your-super-secret-django-key-here"  # 50+ characters
DATABASE_URL="postgresql://user:pass@localhost/db"  # Use strong passwords
REDIS_URL="redis://:password@localhost:6379"  # Enable Redis auth

# API Keys (Keep these secret!)
OPENAI_API_KEY="sk-..."  # OpenAI API key
ANTHROPIC_API_KEY="sk-ant-..."  # Anthropic Claude API key
POLYGON_API_KEY="your-polygon-key"  # Financial data API
STABILITY_KEY="sk-..."  # Stability AI for image generation

# Database Security
DB_PASSWORD="complex-secure-password-here"  # Use strong passwords
DB_HOST="localhost"  # Restrict to localhost in production
```

### 2. **Authentication & Authorization**

**Current Status**: 60% Complete - Working but needs testing

#### JWT Token Security
```python
# Settings already configured in backend/server/settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

#### Frontend Token Storage
```typescript
// React: src/services/authService.ts
// Tokens stored in localStorage with secure handling
const authToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

// Flutter: lib/services/auth_service.dart
// Tokens stored in SharedPreferences with encryption
```

### 3. **API Security**

#### Rate Limiting
```python
# Django REST Framework throttling enabled
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    }
}
```

#### CORS Configuration
```python
# Only allow specific origins
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React development
    "http://localhost:5173",  # Vite React
    "https://yourdomain.com",  # Production domain
]
```

### 4. **Database Security**

#### PostgreSQL Security
```sql
-- Create dedicated database user
CREATE USER donkey_betz_user WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE donkey_betz_db TO donkey_betz_user;

-- Enable row-level security where needed
ALTER TABLE sensitive_table ENABLE ROW LEVEL SECURITY;
```

#### pgvector Security
```python
# Vector embeddings for Memory/RAG system
# Ensure embeddings don't leak sensitive information
VECTOR_STORE_SECURITY = {
    'ANONYMIZE_EMBEDDINGS': True,
    'ENCRYPT_VECTORS': True,
    'TTL_DAYS': 365,  # Automatic cleanup
}
```

### 5. **AI/ML Security**

#### API Key Management
```python
# Secure API key rotation
API_KEY_ROTATION = {
    'OPENAI_API_KEY': 'Monthly',
    'ANTHROPIC_API_KEY': 'Monthly', 
    'POLYGON_API_KEY': 'Quarterly',
    'STABILITY_KEY': 'Monthly',
}
```

#### Content Filtering
```python
# AI-generated content security
CONTENT_SECURITY = {
    'ENABLE_CONTENT_FILTERING': True,
    'BLOCK_INAPPROPRIATE_CONTENT': True,
    'SCAN_GENERATED_IMAGES': True,
    'MONITOR_AI_RESPONSES': True,
}
```

### 6. **Financial Data Security**

#### Polygon.io Integration
```python
# Financial data handling
FINANCIAL_DATA_SECURITY = {
    'CACHE_TTL': 300,  # 5 minutes max
    'ENCRYPT_FINANCIAL_DATA': True,
    'AUDIT_FINANCIAL_QUERIES': True,
    'RATE_LIMIT_STRICT': True,
}
```

#### Stock Data Privacy
```python
# User portfolio privacy
PORTFOLIO_SECURITY = {
    'ENCRYPT_HOLDINGS': True,
    'ANONYMIZE_ANALYTICS': True,
    'RESTRICT_DATA_SHARING': True,
}
```

## 🛡️ **Security Implementations**

### 1. **Input Validation**

```python
# All API endpoints use serializers for validation
class BusinessPlanSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=5000)
    
    def validate_title(self, value):
        # Prevent XSS attacks
        if '<script>' in value.lower():
            raise serializers.ValidationError("Invalid characters detected")
        return value
```

### 2. **SQL Injection Prevention**

```python
# Django ORM prevents SQL injection by default
# All queries use parameterized statements
User.objects.filter(email=user_email)  # Safe
# Raw SQL is avoided, when necessary use:
# cursor.execute("SELECT * FROM users WHERE email = %s", [user_email])
```

### 3. **XSS Protection**

```python
# Django template auto-escaping enabled
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
        ],
    },
}]
```

### 4. **CSRF Protection**

```python
# CSRF middleware enabled
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',
    # Other middleware...
]

# API endpoints use CSRF exemption for REST API
@csrf_exempt
@api_view(['POST'])
def api_endpoint(request):
    # JWT authentication handles security
    pass
```

### 5. **Content Security Policy**

```python
# CSP headers for web security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

## 🔧 **Security Configuration**

### Production Settings

```python
# backend/server/settings.py (Production)
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'api.yourdomain.com']

# HTTPS Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# CSRF Security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
```

### Development Settings

```python
# backend/server/settings.py (Development)
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.10.104']

# Allow HTTP for development
SECURE_SSL_REDIRECT = False
```

## 🚨 **Security Vulnerabilities & Fixes**

### 1. **Authentication System (60% Complete)**

**Issues Identified:**
- API access sometimes blocked with "Authentication credentials were not provided"
- JWT token refresh mechanism needs testing
- Frontend token storage needs encryption

**Fixes Applied:**
```python
# backend/server/settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 2. **Memory/RAG System (50% Complete)**

**Security Concerns:**
- Vector search returning 0 results (potential data leak)
- Embeddings not properly secured
- Memory content not encrypted

**Recommended Fixes:**
```python
# Encrypt sensitive memory content
def encrypt_memory_content(content):
    from cryptography.fernet import Fernet
    key = settings.MEMORY_ENCRYPTION_KEY
    fernet = Fernet(key)
    return fernet.encrypt(content.encode()).decode()

# Secure vector search
def secure_vector_search(query, user_id):
    # Only search user's own memories
    return Memory.objects.filter(user=user_id).vector_search(query)
```

### 3. **API Key Exposure**

**Prevention Measures:**
```python
# Never log API keys
import logging
logger = logging.getLogger(__name__)

def api_call_with_key(api_key, endpoint):
    # Don't log the actual key
    logger.info(f"API call to {endpoint} with key: {'*' * len(api_key)}")
    return make_api_call(api_key, endpoint)
```

## 🔐 **Access Control**

### Role-Based Permissions

```python
# Custom permission classes
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to the owner
        return obj.owner == request.user

class IsAgentOrchestrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('agent_orchestra.can_orchestrate')
```

### API Endpoint Security

```python
# Secure API endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def secure_endpoint(request):
    # Validate user has permission
    if not request.user.has_perm('required_permission'):
        return Response({'error': 'Insufficient permissions'}, 
                       status=403)
    
    # Process request securely
    return Response({'success': True})
```

## 🛡️ **Security Monitoring**

### 1. **Audit Logging**

```python
# Security audit log
LOGGING = {
    'version': 1,
    'handlers': {
        'security_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'security.log',
        },
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
        },
    },
}
```

### 2. **Failed Login Monitoring**

```python
# Monitor failed login attempts
@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    logger.warning(f"Failed login attempt for {credentials.get('email')} "
                  f"from {request.META.get('REMOTE_ADDR')}")
```

### 3. **API Usage Monitoring**

```python
# Monitor API usage patterns
class APIUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Log API usage
        if request.path.startswith('/api/'):
            logger.info(f"API call: {request.method} {request.path} "
                       f"by {request.user}")
        
        response = self.get_response(request)
        return response
```

## 🚨 **Security Incident Response**

### 1. **Immediate Actions**

```bash
# If security breach detected:
1. Immediately rotate all API keys
2. Force logout all users
3. Review access logs
4. Notify users if data compromised
5. Apply security patches
```

### 2. **API Key Rotation**

```python
# Automated key rotation script
def rotate_api_keys():
    # Generate new keys
    new_keys = generate_new_keys()
    
    # Update environment
    update_environment_variables(new_keys)
    
    # Restart services
    restart_services()
    
    # Notify administrators
    send_security_notification("API keys rotated successfully")
```

### 3. **Data Breach Response**

```python
# Data breach response protocol
def handle_data_breach():
    # 1. Contain the breach
    disable_affected_endpoints()
    
    # 2. Assess the damage
    audit_logs = analyze_security_logs()
    
    # 3. Notify stakeholders
    notify_users_of_breach()
    
    # 4. Remediate
    apply_security_patches()
    
    # 5. Monitor
    increase_security_monitoring()
```

## 🔧 **Security Checklist**

### Pre-Production Checklist

- [ ] **Environment Variables**: All sensitive data in .env files
- [ ] **HTTPS**: SSL certificates installed and configured
- [ ] **Database**: Strong passwords, restricted access
- [ ] **API Keys**: Rotated and secured
- [ ] **Authentication**: JWT tokens properly configured
- [ ] **Rate Limiting**: Implemented for all endpoints
- [ ] **Input Validation**: All user inputs validated
- [ ] **CORS**: Properly configured for production domains
- [ ] **Logging**: Security events logged and monitored
- [ ] **Backups**: Encrypted backups of sensitive data
- [ ] **Penetration Testing**: Security testing completed
- [ ] **Code Review**: Security-focused code review completed

### Ongoing Security Maintenance

- [ ] **Monthly**: Rotate API keys
- [ ] **Weekly**: Review security logs
- [ ] **Daily**: Monitor failed login attempts
- [ ] **Quarterly**: Security audit and penetration testing
- [ ] **As Needed**: Apply security patches immediately

## 📞 **Security Contacts**

**Security Team**: security@donkeybetz.com  
**Emergency**: security-emergency@donkeybetz.com  
**Bug Bounty**: security-research@donkeybetz.com  

---

**⚠️ IMPORTANT**: This security guide must be updated whenever new features are added or security configurations change. Always prioritize security over functionality.

**🔒 REMEMBER**: Security is not a one-time setup but an ongoing process. Regular audits and updates are essential for maintaining platform security.