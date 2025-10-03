# Detailed Investigation: Security & Authentication

## Common Issues to Investigate

### Issue 1: JWT Token Security
**Problem**: JWT tokens might be misconfigured or insecure

**Investigation Steps:**

1. **JWT Configuration Analysis**
   ```python
   # Check JWT settings
   File: backend/server/settings/auth.py
   
   Check for:
   - SECRET_KEY strength
   - TOKEN_EXPIRY times
   - REFRESH_TOKEN settings
   - Algorithm used (should be RS256 or HS256)
   ```

2. **Token Storage Investigation**
   ```
   # Frontend token storage
   File: donkey-betz-frontend/src/services/auth.ts
   
   Questions:
   - Are tokens in localStorage? (bad)
   - Are tokens in httpOnly cookies? (good)
   - Is refresh token separate from access token?
   ```

3. **Token Validation**
   ```python
   # Find token validation
   grep -r "jwt.decode\|verify_token" backend/ --include="*.py"
   
   # Check for:
   - Expiry validation
   - Signature verification
   - Audience/issuer checks
   ```

### Issue 2: API Endpoint Authorization
**Problem**: Some API endpoints might lack proper authorization

**Investigation Steps:**

1. **Permission Class Audit**
   ```bash
   # Find all API views
   find backend/api -name "*.py" -exec grep -l "APIView\|ViewSet\|api_view" {} \;
   
   # Check for permission_classes
   grep -r "permission_classes" backend/api/ --include="*.py" | grep -v "IsAuthenticated"
   
   # Find views WITHOUT permissions (security risk!)
   grep -r "class.*View\|def.*view" backend/api/ --include="*.py" -A 5 | grep -v "permission_classes"
   ```

2. **Custom Permission Analysis**
   ```python
   # Find custom permissions
   find backend -name "permissions.py" -exec cat {} \;
   
   # Look for:
   - Object-level permissions
   - User role checks
   - Business logic permissions
   ```

3. **Public Endpoint Review**
   ```bash
   # Find explicitly public endpoints
   grep -r "AllowAny\|authentication_classes.*\[\]" backend/ --include="*.py"
   
   # These should only be:
   - Login/Register
   - Password reset
   - Health checks
   - Public documentation
   ```

### Issue 3: Data Privacy & PII Protection
**Problem**: Personal data might not be properly protected

**Investigation Steps:**

1. **Encryption Implementation**
   ```python
   # Check encrypted fields
   File: backend/security/fields/encrypted_fields.py
   
   # Find usage
   grep -r "EncryptedField\|EncryptedTextField" backend/ --include="*.py"
   
   # What should be encrypted:
   - User profile data
   - Conversation content
   - API keys
   - Personal memories
   ```

2. **PII Detection Service**
   ```python
   # Check PII detection
   File: backend/security/services/pii_detector.py
   
   # Test patterns
   test_data = [
       "My SSN is 123-45-6789",
       "Call me at 555-1234",
       "Email: user@example.com",
       "Credit card: 4111111111111111"
   ]
   
   for data in test_data:
       result = pii_detector.detect(data)
       print(f"'{data}' -> PII found: {result}")
   ```

## Specific Security Queries

### Query 1: Find Security Vulnerabilities
```bash
# Find hardcoded secrets
grep -r "SECRET\|PASSWORD\|API_KEY" backend/ --include="*.py" | grep -v "os.environ\|settings\|getenv"

# Find SQL injection risks
grep -r "\.raw(\|\.extra(\|cursor.execute(" backend/ --include="*.py" | grep -v "params="

# Find XSS risks
grep -r "mark_safe\|safe.*=.*True\|autoescape.*=.*False" backend/ --include="*.py"

# Find open redirects
grep -r "redirect(request\.\|HttpResponseRedirect(request\." backend/ --include="*.py"
```

### Query 2: Authentication Flow Analysis
```bash
# Find auth endpoints
grep -r "login\|signin\|auth" backend/api/ --include="*.py" -i

# Check password handling
grep -r "make_password\|check_password\|set_password" backend/ --include="*.py"

# Find user creation
grep -r "User.objects.create\|create_user" backend/ --include="*.py"
```

### Query 3: Session Security
```python
# Django shell - Check session settings
from django.conf import settings

print(f"SESSION_COOKIE_SECURE: {settings.SESSION_COOKIE_SECURE}")  # Should be True in prod
print(f"SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")  # Should be True
print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")  # Should be True in prod
print(f"SECURE_SSL_REDIRECT: {settings.SECURE_SSL_REDIRECT}")  # Should be True in prod
```

## Security Testing

### Test 1: Authentication Bypass Attempts
```python
# test_auth_bypass.py
import requests

base_url = "http://localhost:8000"

# Try accessing protected endpoint without token
response = requests.get(f"{base_url}/api/memory/search/")
print(f"No auth: {response.status_code}")  # Should be 401

# Try with invalid token
headers = {"Authorization": "Bearer invalid_token"}
response = requests.get(f"{base_url}/api/memory/search/", headers=headers)
print(f"Invalid token: {response.status_code}")  # Should be 401

# Try with expired token
headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."}
response = requests.get(f"{base_url}/api/memory/search/", headers=headers)
print(f"Expired token: {response.status_code}")  # Should be 401
```

### Test 2: SQL Injection Tests
```python
# test_sql_injection.py
payloads = [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "1' UNION SELECT * FROM accounts_user --",
    "' OR 1=1 --"
]

for payload in payloads:
    # Test search endpoint
    response = requests.get(f"/api/memory/search/?q={payload}")
    if "error" not in response.text.lower() and response.status_code == 200:
        print(f"Possible SQL injection with: {payload}")
```

### Test 3: XSS Testing
```python
# test_xss.py
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert('XSS')>",
    "javascript:alert('XSS')",
    "<svg onload=alert('XSS')>"
]

for payload in xss_payloads:
    # Test user input fields
    data = {"message": payload}
    response = requests.post("/api/chat/message/", json=data, headers=auth_headers)
    
    # Check if payload is escaped in response
    if payload in response.text:
        print(f"Possible XSS vulnerability with: {payload}")
```

## Critical Security Files

1. **Authentication Core**
   - `backend/accounts/auth/jwt_auth.py` - JWT implementation
   - `backend/accounts/auth/backends.py` - Auth backends
   - `backend/api/accounts/views/auth_views.py` - Auth endpoints

2. **Security Middleware**
   - `backend/server/middleware/security_middleware.py` - Security headers
   - `backend/security/middleware/rate_limit.py` - Rate limiting
   - `backend/security/middleware/audit.py` - Audit logging

3. **Encryption & Privacy**
   - `backend/security/services/encryption_service.py` - Encryption logic
   - `backend/security/services/pii_detector.py` - PII detection
   - `backend/security/models/audit_log.py` - Audit trail

## Common Security Issues and Fixes

### Issue: Weak JWT Secret
```python
# Bad - weak secret
SECRET_KEY = "my-secret-key"

# Good - strong secret
import secrets
SECRET_KEY = secrets.token_urlsafe(64)

# Or from environment
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY not set")
```

### Issue: Missing HTTPS Enforcement
```python
# settings/production.py
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Issue: Unencrypted Sensitive Data
```python
# Add encryption to sensitive fields
from security.fields import EncryptedTextField

class UserProfile(models.Model):
    # Bad
    # ssn = models.CharField(max_length=11)
    
    # Good
    ssn = EncryptedTextField(max_length=11, null=True, blank=True)
    
    # Also encrypt in queries
    def get_decrypted_ssn(self):
        return self.ssn  # Automatically decrypted by field
```

## Security Hardening Checklist

### API Security
```python
# Implement rate limiting
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class StrictRateThrottle(UserRateThrottle):
    rate = '100/hour'

class MyAPIView(APIView):
    throttle_classes = [StrictRateThrottle]
    permission_classes = [IsAuthenticated]
```

### Input Validation
```python
# Strong input validation
from django.core.validators import RegexValidator
from rest_framework import serializers

class UserInputSerializer(serializers.Serializer):
    # Whitelist allowed characters
    name = serializers.CharField(
        max_length=100,
        validators=[RegexValidator(r'^[a-zA-Z0-9\s\-\.]+$')]
    )
    
    # Validate specific formats
    phone = serializers.CharField(
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    
    def validate(self, data):
        # Additional validation
        if self.pii_detector.has_pii(data.get('name')):
            raise ValidationError("Name contains PII")
        return data
```

### Audit Logging
```python
# Comprehensive audit logging
from security.models import AuditLog

class AuditMixin:
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        AuditLog.objects.create(
            user=request.user,
            action='CREATE',
            model=self.get_serializer().Meta.model.__name__,
            object_id=response.data.get('id'),
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            data=request.data
        )
        
        return response
```

## Security Monitoring

### Real-time Security Monitoring
```python
# monitor_security.py
from django.core.cache import cache
from datetime import datetime, timedelta

def monitor_auth_failures():
    # Track failed login attempts
    failed_attempts = cache.get('failed_auth_attempts', {})
    
    for ip, attempts in failed_attempts.items():
        if len(attempts) > 5:
            recent = [a for a in attempts if a > datetime.now() - timedelta(minutes=10)]
            if len(recent) > 5:
                alert(f"Possible brute force from {ip}")
                block_ip(ip)

def monitor_suspicious_queries():
    # Check for SQL injection patterns in logs
    with open('backend/logs/django.log', 'r') as f:
        for line in f:
            if any(pattern in line for pattern in ['UNION', 'DROP TABLE', 'OR 1=1']):
                alert(f"Possible SQL injection attempt: {line}")
```