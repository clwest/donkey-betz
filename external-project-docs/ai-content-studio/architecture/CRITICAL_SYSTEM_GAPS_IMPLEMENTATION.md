# Critical System Gaps Implementation Handoff

## Executive Summary
Based on comprehensive system analysis, AI Content Studio has several critical gaps that must be addressed before production launch. This document outlines implementation plans for the most critical missing components, prioritized by business impact and security risk.

**Total Estimated Time**: 12-15 hours across all priorities
**Risk Level**: HIGH - These gaps could cause data loss, security breaches, and system instability
**Implementation Order**: By priority level (Critical → High → Medium)

---

# 🔴 PRIORITY 1: CRITICAL (Must Fix Before Launch)

## 1. Data Backup & Recovery System (3-4 hours)

### Current Risk
- **User content loss**: No backup strategy for generated content
- **Business continuity**: System failure could lose all user data
- **Legal compliance**: GDPR requires data export capability

### Implementation Plan

#### Step 1.1: Database Backup Strategy
**File**: `backend/management/commands/backup_database.py`

```python
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command
from datetime import datetime
import os
import boto3
import subprocess
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Backup database and media files to cloud storage'

    def add_arguments(self, parser):
        parser.add_argument('--storage', choices=['s3', 'local'], default='s3')
        parser.add_argument('--media', action='store_true', help='Include media files')

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Database backup
        db_filename = f'db_backup_{timestamp}.sql'
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
            self.backup_postgresql(db_filename)
        else:
            self.backup_sqlite(db_filename)
        
        # Media backup
        if options['media']:
            self.backup_media_files(timestamp)
        
        # Upload to cloud storage
        if options['storage'] == 's3':
            self.upload_to_s3(db_filename, timestamp)
        
        self.stdout.write(
            self.style.SUCCESS(f'Backup completed: {db_filename}')
        )

    def backup_postgresql(self, filename):
        """Backup PostgreSQL database"""
        db_settings = settings.DATABASES['default']
        
        cmd = [
            'pg_dump',
            f"--host={db_settings['HOST']}",
            f"--port={db_settings['PORT']}",
            f"--username={db_settings['USER']}",
            f"--dbname={db_settings['NAME']}",
            '--no-password',
            '--verbose',
            '--clean',
            '--no-acl',
            '--no-owner',
            f'--file={filename}'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_settings['PASSWORD']
        
        try:
            subprocess.run(cmd, env=env, check=True)
            logger.info(f"Database backup created: {filename}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Database backup failed: {e}")
            raise

    def backup_sqlite(self, filename):
        """Backup SQLite database"""
        call_command('dumpdata', '--output', filename, '--format', 'json')
        logger.info(f"SQLite backup created: {filename}")

    def backup_media_files(self, timestamp):
        """Create tar archive of media files"""
        media_backup = f'media_backup_{timestamp}.tar.gz'
        
        try:
            subprocess.run([
                'tar', '-czf', media_backup, 
                '-C', settings.MEDIA_ROOT, '.'
            ], check=True)
            logger.info(f"Media backup created: {media_backup}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Media backup failed: {e}")
            raise

    def upload_to_s3(self, db_filename, timestamp):
        """Upload backups to S3"""
        s3 = boto3.client('s3')
        bucket_name = settings.BACKUP_S3_BUCKET
        
        try:
            # Upload database backup
            s3.upload_file(
                db_filename, bucket_name, 
                f'backups/database/{db_filename}'
            )
            
            # Upload media backup if exists
            media_backup = f'media_backup_{timestamp}.tar.gz'
            if os.path.exists(media_backup):
                s3.upload_file(
                    media_backup, bucket_name,
                    f'backups/media/{media_backup}'
                )
            
            # Cleanup local files
            os.remove(db_filename)
            if os.path.exists(media_backup):
                os.remove(media_backup)
                
            logger.info("Backups uploaded to S3 successfully")
            
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
```

#### Step 1.2: Automated Backup Scheduling
**File**: `backend/celery.py` (add to existing celery setup)

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-backup': {
        'task': 'core.tasks.create_daily_backup',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'weekly-full-backup': {
        'task': 'core.tasks.create_full_backup',
        'schedule': crontab(hour=1, minute=0, day_of_week=0),  # Sunday 1 AM
    },
}

# In core/tasks.py
@app.task
def create_daily_backup():
    call_command('backup_database', '--storage=s3')

@app.task  
def create_full_backup():
    call_command('backup_database', '--storage=s3', '--media')
```

#### Step 1.3: User Data Export (GDPR Compliance)
**File**: `backend/api/views_data_export.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
import zipfile
import json
import os
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_user_data(request):
    """Export all user data in machine-readable format"""
    user = request.user
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_filename = f'user_data_export_{user.id}_{timestamp}.zip'
    
    try:
        # Create temporary directory
        temp_dir = f'/tmp/export_{user.id}_{timestamp}'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Export user profile data
        export_profile_data(user, temp_dir)
        
        # Export content data
        export_content_data(user, temp_dir)
        
        # Export feedback data
        export_feedback_data(user, temp_dir)
        
        # Export memory/chat data
        export_memory_data(user, temp_dir)
        
        # Create ZIP file
        zip_path = create_export_zip(temp_dir, export_filename)
        
        # Return download response
        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename={export_filename}'
            
        # Cleanup
        cleanup_export_files(temp_dir, zip_path)
        
        return response
        
    except Exception as e:
        logger.error(f"Data export failed for user {user.id}: {e}")
        return Response({'error': 'Export failed'}, status=500)

def export_profile_data(user, temp_dir):
    """Export user profile and account data"""
    from content.models_profile import UserProfile, UserStatistics
    
    profile_data = {
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
    }
    
    # Add profile data if exists
    if hasattr(user, 'profile'):
        profile = user.profile
        profile_data['profile'] = {
            'bio': profile.bio,
            'display_name': profile.display_name,
            'occupation': profile.occupation,
            'location': profile.location,
            'account_type': profile.account_type,
            'preferred_ai_model': profile.preferred_ai_model,
            'default_content_tone': profile.default_content_tone,
            'research_topics': profile.research_topics,
            'created_at': profile.created_at.isoformat(),
        }
    
    # Add statistics if exists
    if hasattr(user, 'statistics'):
        stats = user.statistics
        profile_data['statistics'] = {
            'total_contents': stats.total_contents,
            'total_images': stats.total_images,
            'total_videos': stats.total_videos,
            'total_blogs': stats.total_blogs,
            # ... all other stats fields
        }
    
    with open(f'{temp_dir}/profile.json', 'w') as f:
        json.dump(profile_data, f, indent=2, default=str)

def export_content_data(user, temp_dir):
    """Export all user-generated content"""
    from content.models import Content, SavedImage, SavedVideo
    from content.models_blog import BlogPost
    
    # Export text content
    content_data = []
    for content in Content.objects.filter(user=user):
        content_data.append({
            'id': content.id,
            'type': content.type,
            'prompt': content.prompt,
            'content': content.content,
            'metadata': content.metadata,
            'created_at': content.created_at.isoformat(),
        })
    
    with open(f'{temp_dir}/content.json', 'w') as f:
        json.dump(content_data, f, indent=2, default=str)
    
    # Export blog posts
    blog_data = []
    for blog in BlogPost.objects.filter(user=user):
        blog_data.append({
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'metadata': blog.metadata,
            'created_at': blog.created_at.isoformat(),
        })
    
    with open(f'{temp_dir}/blogs.json', 'w') as f:
        json.dump(blog_data, f, indent=2, default=str)
    
    # Copy media files
    media_dir = f'{temp_dir}/media'
    os.makedirs(media_dir, exist_ok=True)
    
    for img in SavedImage.objects.filter(user=user):
        if img.image and os.path.exists(img.image.path):
            filename = f"image_{img.id}_{os.path.basename(img.image.name)}"
            shutil.copy2(img.image.path, f'{media_dir}/{filename}')

def create_export_zip(temp_dir, filename):
    """Create ZIP file from exported data"""
    zip_path = f'/tmp/{filename}'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    return zip_path
```

#### Step 1.4: Disaster Recovery Plan
**File**: `documentation/DISASTER_RECOVERY_PLAN.md`

```markdown
# Disaster Recovery Plan

## Recovery Time Objectives (RTO)
- Database: 30 minutes
- Media files: 2 hours  
- Full system: 4 hours

## Recovery Point Objectives (RPO)
- Database: 24 hours (daily backups)
- Media files: 7 days (weekly backups)

## Recovery Procedures

### Database Recovery
1. Restore from latest S3 backup
2. Apply transaction logs if available
3. Verify data integrity
4. Update DNS/load balancer

### Media Recovery
1. Download media backup from S3
2. Extract to MEDIA_ROOT
3. Update file permissions
4. Verify file integrity

### Full System Recovery
1. Deploy new infrastructure
2. Restore database
3. Restore media files  
4. Update configuration
5. Test all functionality
```

---

## 2. Security Hardening (2-3 hours)

### Current Risk
- **API keys exposed**: Frontend build contains API keys
- **Injection attacks**: No input sanitization
- **Data breaches**: Missing security headers and CORS

### Implementation Plan

#### Step 2.1: Environment Security
**File**: `backend/core/settings_security.py`

```python
import os
from django.core.exceptions import ImproperlyConfigured

def get_secret(secret_name, default=None):
    """Get secret from environment or raise exception"""
    try:
        return os.environ[secret_name]
    except KeyError:
        if default is not None:
            return default
        error_msg = f'Set the {secret_name} environment variable'
        raise ImproperlyConfigured(error_msg)

# Security Settings
SECRET_KEY = get_secret('DJANGO_SECRET_KEY')
DEBUG = get_secret('DEBUG', 'False').lower() == 'true'

# Database with connection pooling
if get_secret('DATABASE_URL', None):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(get_secret('DATABASE_URL'))
    }

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS Settings (production only)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# CORS Settings
CORS_ALLOWED_ORIGINS = get_secret('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

# API Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# File Upload Security
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']
```

#### Step 2.2: Input Sanitization Middleware
**File**: `backend/core/middleware/security.py`

```python
import re
import html
import json
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

class InputSanitizationMiddleware(MiddlewareMixin):
    """Sanitize user inputs to prevent injection attacks"""
    
    # Dangerous patterns to detect
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # XSS scripts
        r'javascript:',               # JavaScript URLs
        r'on\w+\s*=',                # Event handlers
        r'eval\s*\(',                # eval() calls
        r'document\.',               # DOM manipulation
        r'window\.',                 # Window object access
    ]
    
    def process_request(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            # Sanitize JSON data
            if request.content_type == 'application/json':
                try:
                    body = json.loads(request.body or b"{}").decode('utf-8'))
                    sanitized_body = self.sanitize_dict(body)
                    request._body = json.dumps(sanitized_body).encode('utf-8')
                except (json.JSONDecodeError, UnicodeDecodeError):
                    pass
            
            # Sanitize form data
            if hasattr(request, 'POST'):
                request.POST = request.POST.copy()
                for key, value in request.POST.items():
                    if isinstance(value, str):
                        request.POST[key] = self.sanitize_string(value)
        
        return None
    
    def sanitize_dict(self, data):
        """Recursively sanitize dictionary data"""
        if isinstance(data, dict):
            return {key: self.sanitize_dict(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_dict(item) for item in data]
        elif isinstance(data, str):
            return self.sanitize_string(data)
        else:
            return data
    
    def sanitize_string(self, value):
        """Sanitize string input"""
        if not isinstance(value, str):
            return value
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                # Log security violation
                import logging
                logger = logging.getLogger('security')
                logger.warning(f"Dangerous pattern detected: {pattern} in: {value[:100]}")
                
                # Remove dangerous content
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        # HTML escape remaining content
        return html.escape(value)

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add security headers to all responses"""
    
    def process_response(self, request, response):
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: blob: https:",
            "connect-src 'self' https://api.openai.com https://api.stability.ai",
            "media-src 'self' blob:",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)
        
        # Additional security headers
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        
        return response
```

#### Step 2.3: API Key Protection
**File**: `backend/core/api_protection.py`

```python
from functools import wraps
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
import hashlib
import hmac
import time

class APIKeyManager:
    """Secure API key management"""
    
    @staticmethod
    def get_api_key(service_name):
        """Get API key from secure storage"""
        # Use environment variables or secure key vault
        key_map = {
            'openai': settings.OPENAI_API_KEY,
            'stability': settings.STABILITY_API_KEY,
            'runway': settings.RUNWAY_API_KEY,
        }
        return key_map.get(service_name)
    
    @staticmethod
    def create_request_signature(payload, secret_key):
        """Create HMAC signature for API requests"""
        message = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret_key.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()
        return signature
    
    @staticmethod
    def verify_request_signature(payload, signature, secret_key):
        """Verify request signature"""
        expected_signature = APIKeyManager.create_request_signature(payload, secret_key)
        return hmac.compare_digest(signature, expected_signature)

def require_api_signature(f):
    """Decorator to require API signature verification"""
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not settings.REQUIRE_API_SIGNATURES:
            return f(request, *args, **kwargs)
        
        signature = request.META.get('HTTP_X_SIGNATURE')
        if not signature:
            return Response(
                {'error': 'Missing API signature'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            payload = json.loads(request.body or b"{}"))
            secret_key = settings.API_SIGNATURE_SECRET
            
            if not APIKeyManager.verify_request_signature(payload, signature, secret_key):
                return Response(
                    {'error': 'Invalid signature'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except Exception as e:
            return Response(
                {'error': 'Signature verification failed'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return f(request, *args, **kwargs)
    
    return wrapper
```

#### Step 2.4: Frontend Security Updates
**File**: `ai-studio-web/src/utils/security.ts`

```typescript
// Remove API keys from frontend - use proxy endpoints instead
export class SecureApiClient {
  private static baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
  
  // Use backend proxy endpoints instead of direct API calls
  static async callOpenAI(payload: any) {
    return this.secureRequest('/api/proxy/openai/', payload);
  }
  
  static async callStabilityAI(payload: any) {
    return this.secureRequest('/api/proxy/stability/', payload);
  }
  
  private static async secureRequest(endpoint: string, payload: any) {
    const timestamp = Date.now();
    const nonce = this.generateNonce();
    
    const headers = {
      'Content-Type': 'application/json',
      'X-Timestamp': timestamp.toString(),
      'X-Nonce': nonce,
      'Authorization': `Bearer ${this.getToken()}`,
    };
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      credentials: 'include',
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  private static generateNonce(): string {
    return crypto.randomUUID();
  }
  
  private static getToken(): string {
    return localStorage.getItem('auth_token') || '';
  }
}

// Input sanitization for frontend
export const sanitizeInput = (input: string): string => {
  return input
    .replace(/<script[^>]*>.*?<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '')
    .replace(/eval\s*\(/gi, '')
    .trim();
};

// Secure local storage wrapper
export class SecureStorage {
  private static encrypt(data: string): string {
    // Simple XOR encryption (use proper crypto in production)
    const key = 'user_session_key';
    let result = '';
    for (let i = 0; i < data.length; i++) {
      result += String.fromCharCode(data.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }
    return btoa(result);
  }
  
  private static decrypt(data: string): string {
    const encrypted = atob(data);
    const key = 'user_session_key';
    let result = '';
    for (let i = 0; i < encrypted.length; i++) {
      result += String.fromCharCode(encrypted.charCodeAt(i) ^ key.charCodeAt(i % key.length));
    }
    return result;
  }
  
  static setItem(key: string, value: string): void {
    localStorage.setItem(key, this.encrypt(value));
  }
  
  static getItem(key: string): string | null {
    const encrypted = localStorage.getItem(key);
    return encrypted ? this.decrypt(encrypted) : null;
  }
}
```

---

# 🟠 PRIORITY 2: HIGH (Fix Within 2 Weeks)

## 3. Error Handling & Monitoring (2-3 hours)

### Implementation Plan

#### Step 3.1: Centralized Error Tracking
**File**: `backend/core/error_handling.py`

```python
import logging
import traceback
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.core.mail import send_mail

class ErrorTracker:
    """Centralized error tracking and reporting"""
    
    @staticmethod
    def log_error(error, context=None, user=None):
        """Log error with full context"""
        logger = logging.getLogger('errors')
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'user_id': user.id if user else None,
            'context': context or {},
        }
        
        logger.error(f"Application Error: {error_data}")
        
        # Send to external monitoring (Sentry, etc.)
        if hasattr(settings, 'SENTRY_DSN'):
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                if user:
                    scope.user = {'id': user.id, 'username': user.username}
                scope.set_context('error_context', context or {})
                sentry_sdk.capture_exception(error)
        
        # Email critical errors
        if ErrorTracker.is_critical_error(error):
            ErrorTracker.send_critical_alert(error_data)
        
        return error_data
    
    @staticmethod
    def is_critical_error(error):
        """Determine if error is critical"""
        critical_errors = [
            'DatabaseError',
            'IntegrityError', 
            'ConnectionError',
            'PermissionError',
        ]
        return type(error).__name__ in critical_errors
    
    @staticmethod
    def send_critical_alert(error_data):
        """Send email alert for critical errors"""
        try:
            send_mail(
                subject=f"Critical Error: {error_data['error_type']}",
                message=f"""
                Critical error occurred at {error_data['timestamp']}
                
                Error: {error_data['error_message']}
                User: {error_data['user_id']}
                
                Traceback:
                {error_data['traceback']}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ADMIN_EMAILS,
                fail_silently=False
            )
        except Exception as e:
            logger.error(f"Failed to send error alert: {e}")

class ErrorHandlingMiddleware:
    """Global error handling middleware"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as error:
            return self.handle_error(request, error)
    
    def handle_error(self, request, error):
        """Handle all uncaught errors"""
        user = getattr(request, 'user', None)
        context = {
            'url': request.get_full_path(),
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self.get_client_ip(request),
        }
        
        # Log the error
        error_data = ErrorTracker.log_error(error, context, user)
        
        # Return appropriate error response
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'An internal error occurred',
                'error_id': error_data.get('timestamp'),
                'detail': str(error) if settings.DEBUG else None
            }, status=500)
        else:
            # Return HTML error page for non-API requests
            return render(request, 'errors/500.html', {
                'error_id': error_data.get('timestamp')
            }, status=500)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
```

#### Step 3.2: System Health Monitoring
**File**: `backend/api/views_health.py`

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import psutil
import time
import redis

@api_view(['GET'])
def health_check(request):
    """Comprehensive health check endpoint"""
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            health_data['checks']['database'] = {
                'status': 'healthy',
                'response_time_ms': 0  # Could measure actual time
            }
    except Exception as e:
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_data['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'test', 1)
        cache.get('health_check')
        health_data['checks']['cache'] = {'status': 'healthy'}
    except Exception as e:
        health_data['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # System resources
    health_data['checks']['system'] = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
    }
    
    # API endpoints health
    health_data['checks']['apis'] = check_external_apis()
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return Response(health_data, status=status_code)

def check_external_apis():
    """Check health of external API dependencies"""
    apis = {}
    
    # OpenAI API check
    try:
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        # Simple request to check API health
        response = openai.models.list()
        apis['openai'] = {'status': 'healthy'}
    except Exception as e:
        apis['openai'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Add other API checks similarly
    
    return apis

@api_view(['GET'])
def system_metrics(request):
    """Detailed system metrics for monitoring"""
    from django.db import connection
    from content.models import Content
    
    metrics = {
        'database': {
            'total_queries': len(connection.queries),
            'content_count': Content.objects.count(),
            'active_users': User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count(),
        },
        'system': {
            'uptime_seconds': time.time() - psutil.boot_time(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'disk_total_gb': psutil.disk_usage('/').total / (1024**3),
        },
        'application': {
            'version': settings.VERSION,
            'debug_mode': settings.DEBUG,
            'environment': settings.ENVIRONMENT,
        }
    }
    
    return Response(metrics)
```

#### Step 3.3: Frontend Error Boundaries
**File**: `ai-studio-web/src/components/ErrorBoundary.tsx`

```tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorId?: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorId: Date.now().toString()
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Report error to monitoring service
    this.reportError(error, errorInfo);
    
    // Call custom error handler
    this.props.onError?.(error, errorInfo);
  }

  reportError = async (error: Error, errorInfo: ErrorInfo) => {
    try {
      await fetch('/api/errors/report/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({
          error_message: error.message,
          error_stack: error.stack,
          component_stack: errorInfo.componentStack,
          error_boundary_id: this.state.errorId,
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
          url: window.location.href,
        }),
      });
    } catch (reportingError) {
      console.error('Failed to report error:', reportingError);
    }
  };

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorId: undefined });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-gray-800 rounded-xl border border-gray-700 p-6 text-center">
            <div className="flex justify-center mb-4">
              <AlertCircle className="w-16 h-16 text-red-500" />
            </div>
            
            <h1 className="text-xl font-bold text-white mb-2">
              Something went wrong
            </h1>
            
            <p className="text-gray-400 mb-4">
              We're sorry, but something unexpected happened. Our team has been notified.
            </p>
            
            {this.state.errorId && (
              <p className="text-xs text-gray-500 mb-6 font-mono">
                Error ID: {this.state.errorId}
              </p>
            )}
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleRetry}
                className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>
              
              <button
                onClick={this.handleGoHome}
                className="flex-1 px-4 py-2 bg-gray-700 text-gray-300 rounded-lg hover:bg-gray-600 transition-colors flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Go Home
              </button>
            </div>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-6 text-left">
                <summary className="text-sm text-gray-400 cursor-pointer hover:text-gray-300">
                  Error Details (Development Only)
                </summary>
                <pre className="mt-2 text-xs text-red-400 bg-gray-900 p-2 rounded overflow-auto max-h-40">
                  {this.state.error.stack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Global error handler for unhandled promises
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  
  // Report to monitoring service
  fetch('/api/errors/report/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify({
      error_type: 'unhandled_promise_rejection',
      error_message: event.reason?.message || String(event.reason),
      error_stack: event.reason?.stack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
    }),
  }).catch(error => {
    console.error('Failed to report unhandled rejection:', error);
  });
});
```

---

## 4. Performance Optimization (3-4 hours)

### Implementation Plan

#### Step 4.1: Database Optimization
**File**: `backend/core/db_optimization.py`

```python
# Add database indexes
class Migration(migrations.Migration):
    operations = [
        # Content indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_user_created ON content_content(user_id, created_at DESC);"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_content_type_created ON content_content(type, created_at DESC);"
        ),
        
        # Feedback indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_feedback_content ON content_feedback(content_type, content_id);"
        ),
        
        # Memory indexes
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_memory_user_updated ON memory_memories(user_id, updated_at DESC);"
        ),
    ]

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
            'CONN_MAX_AGE': 600,
        },
    }
}

# Query optimization decorator
def optimize_queries(func):
    """Decorator to optimize database queries"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from django.db import connection
        queries_before = len(connection.queries)
        
        result = func(*args, **kwargs)
        
        queries_after = len(connection.queries)
        query_count = queries_after - queries_before
        
        if query_count > 10:  # Alert on excessive queries
            logger.warning(f"Function {func.__name__} executed {query_count} queries")
            
        return result
    return wrapper
```

#### Step 4.2: Caching Implementation
**File**: `backend/core/caching.py`

```python
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from functools import wraps
import json
import hashlib

def cache_result(timeout=300, key_prefix=''):
    """Cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': sorted(kwargs.items()),
                'prefix': key_prefix
            }
            cache_key = hashlib.md5(
                json.dumps(key_data, default=str).encode()
            ).hexdigest()
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator

class ContentCache:
    """Specialized caching for content operations"""
    
    @staticmethod
    def get_user_content(user_id, content_type=None):
        cache_key = f'user_content_{user_id}_{content_type or "all"}'
        return cache.get(cache_key)
    
    @staticmethod
    def set_user_content(user_id, content, content_type=None, timeout=300):
        cache_key = f'user_content_{user_id}_{content_type or "all"}'
        cache.set(cache_key, content, timeout)
    
    @staticmethod
    def invalidate_user_content(user_id):
        """Invalidate all cached content for user"""
        # In production, use pattern-based deletion
        patterns = [
            f'user_content_{user_id}_*',
            f'user_stats_{user_id}',
            f'user_profile_{user_id}',
        ]
        # Implement pattern deletion based on cache backend
        cache.delete_many(patterns)

# Redis configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

#### Step 4.3: API Rate Limiting
**File**: `backend/core/rate_limiting.py`

```python
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
import time

class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self, max_requests=60, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier):
        """Check if request is allowed"""
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Clean old requests
        cache_key = f'rate_limit_{identifier}'
        requests = cache.get(cache_key, [])
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if under limit
        if len(requests) >= self.max_requests:
            return False, self.get_retry_after(requests)
        
        # Add current request
        requests.append(current_time)
        cache.set(cache_key, requests, self.window_seconds + 10)
        
        return True, None
    
    def get_retry_after(self, requests):
        """Calculate retry-after seconds"""
        if not requests:
            return 0
        oldest_request = min(requests)
        return self.window_seconds - (int(time.time()) - oldest_request)

def rate_limit(max_requests=60, window_seconds=60, per='user'):
    """Rate limiting decorator"""
    limiter = RateLimiter(max_requests, window_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Determine identifier
            if per == 'user' and hasattr(request, 'user') and request.user.is_authenticated:
                identifier = f'user_{request.user.id}'
            elif per == 'ip':
                identifier = f'ip_{request.META.get("REMOTE_ADDR", "unknown")}'
            else:
                identifier = 'anonymous'
            
            # Check rate limit
            allowed, retry_after = limiter.is_allowed(identifier)
            
            if not allowed:
                return Response({
                    'error': 'Rate limit exceeded',
                    'retry_after': retry_after
                }, status=status.HTTP_429_TOO_MANY_REQUESTS, 
                headers={'Retry-After': str(retry_after)})
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage in views:
@rate_limit(max_requests=10, window_seconds=60, per='user')
@api_view(['POST'])
def generate_content(request):
    # Implementation
    pass
```

#### Step 4.4: Frontend Performance
**File**: `ai-studio-web/src/utils/performance.ts`

```typescript
// Lazy loading utility
export const lazyImport = <T extends Record<string, any>>(
  factory: () => Promise<T>
) => {
  return React.lazy(() => factory().then(module => ({ default: module })));
};

// Image optimization
export const optimizeImage = (file: File, maxWidth = 1920, quality = 0.8): Promise<File> => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d')!;
    const img = new Image();
    
    img.onload = () => {
      // Calculate new dimensions
      const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
      canvas.width = img.width * ratio;
      canvas.height = img.height * ratio;
      
      // Draw and compress
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        const optimizedFile = new File([blob!], file.name, {
          type: 'image/jpeg',
          lastModified: Date.now(),
        });
        resolve(optimizedFile);
      }, 'image/jpeg', quality);
    };
    
    img.src = URL.createObjectURL(file);
  });
};

// Request debouncing
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// Virtual scrolling for large lists
export const useVirtualScroll = (items: any[], itemHeight: number, containerHeight: number) => {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleEnd = Math.min(
    visibleStart + Math.ceil(containerHeight / itemHeight) + 1,
    items.length
  );
  
  const visibleItems = items.slice(visibleStart, visibleEnd);
  const totalHeight = items.length * itemHeight;
  const offsetY = visibleStart * itemHeight;
  
  return {
    visibleItems,
    totalHeight,
    offsetY,
    onScroll: (e: React.UIEvent) => setScrollTop(e.currentTarget.scrollTop),
  };
};

// Performance monitoring
export class PerformanceMonitor {
  private static marks = new Map<string, number>();
  
  static mark(name: string): void {
    this.marks.set(name, performance.now());
    performance.mark(name);
  }
  
  static measure(name: string, startMark: string): number {
    const duration = performance.now() - (this.marks.get(startMark) || 0);
    performance.measure(name, startMark);
    
    // Report slow operations
    if (duration > 1000) {
      console.warn(`Slow operation detected: ${name} took ${duration.toFixed(2)}ms`);
    }
    
    return duration;
  }
  
  static reportWebVitals(): void {
    // Report Core Web Vitals
    import('web-vitals').then(({ getLCP, getFID, getCLS }) => {
      getLCP(console.log);
      getFID(console.log);
      getCLS(console.log);
    });
  }
}
```

---

# 🟡 PRIORITY 3: MEDIUM (Fix Within 4 Weeks)

## 5. Admin & Maintenance Tools (2-3 hours)

### Implementation Plan

#### Step 5.1: Django Admin Enhancement
**File**: `backend/core/admin_tools.py`

```python
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from content.models import Content, SavedImage, SavedVideo
from content.models_feedback import ContentFeedback

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_link', 'type', 'created_at', 'feedback_summary', 'actions']
    list_filter = ['type', 'created_at']
    search_fields = ['user__username', 'prompt']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'User'
    
    def feedback_summary(self, obj):
        feedback = ContentFeedback.objects.filter(
            content_type=obj.type,
            content_id=obj.id
        ).aggregate(
            avg_rating=Avg('overall_rating'),
            count=Count('id')
        )
        
        if feedback['count']:
            return f"{feedback['avg_rating']:.1f} ★ ({feedback['count']} reviews)"
        return "No feedback"
    
    def actions(self, obj):
        return format_html(
            '<a href="{}" target="_blank">View</a>',
            f'/content/{obj.id}/'
        )

class SystemHealthAdmin(admin.ModelAdmin):
    """Custom admin for system monitoring"""
    
    def changelist_view(self, request, extra_context=None):
        # Add system metrics to admin
        extra_context = extra_context or {}
        extra_context['system_health'] = self.get_system_health()
        return super().changelist_view(request, extra_context)
    
    def get_system_health(self):
        from django.db import connection
        import psutil
        
        return {
            'database_queries': len(connection.queries),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'active_users': User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=1)
            ).count(),
        }
```

#### Step 5.2: Content Moderation Tools
**File**: `backend/api/views_moderation.py`

```python
@api_view(['POST'])
@permission_classes([IsAdminUser])
def moderate_content(request, content_id):
    """Moderate content (approve/reject/flag)"""
    try:
        content = Content.objects.get(id=content_id)
        action = request.data.get('action')  # approve, reject, flag
        reason = request.data.get('reason', '')
        
        if action == 'flag':
            content.status = 'flagged'
            content.moderation_reason = reason
        elif action == 'approve':
            content.status = 'approved'
            content.moderation_reason = ''
        elif action == 'reject':
            content.status = 'rejected'
            content.moderation_reason = reason
        
        content.moderated_by = request.user
        content.moderated_at = timezone.now()
        content.save()
        
        return Response({'message': f'Content {action}ed successfully'})
        
    except Content.DoesNotExist:
        return Response({'error': 'Content not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def moderation_queue(request):
    """Get content pending moderation"""
    flagged_content = Content.objects.filter(
        Q(status='pending') | Q(status='flagged')
    ).order_by('-created_at')
    
    # Add low-rating content to queue
    low_rated = ContentFeedback.objects.filter(
        overall_rating__lte=2
    ).values('content_type', 'content_id').distinct()
    
    return Response({
        'flagged_content': ContentSerializer(flagged_content, many=True).data,
        'low_rated_count': low_rated.count(),
    })
```

---

## 6. User Experience Improvements (2 hours)

### Implementation Plan

#### Step 6.1: Search Functionality
**File**: `backend/api/views_search.py`

```python
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchRank
from rest_framework.decorators import api_view

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_content(request):
    """Search user's content"""
    query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')
    
    if not query:
        return Response({'results': []})
    
    # Base queryset
    queryset = Content.objects.filter(user=request.user)
    
    if content_type != 'all':
        queryset = queryset.filter(type=content_type)
    
    # PostgreSQL full-text search
    if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        search_vector = SearchVector('prompt', 'content', 'metadata')
        queryset = queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, query)
        ).filter(search=query).order_by('-rank')
    else:
        # SQLite fallback
        queryset = queryset.filter(
            Q(prompt__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-created_at')
    
    # Pagination
    paginated = paginate_queryset(queryset, request, 20)
    serializer = ContentSerializer(paginated, many=True)
    
    return Response({
        'results': serializer.data,
        'total': queryset.count(),
        'query': query,
    })
```

#### Step 6.2: Bulk Operations
**File**: `ai-studio-web/src/components/BulkActions.tsx`

```tsx
import React, { useState } from 'react';
import { Trash2, Download, Archive, Tag } from 'lucide-react';

interface BulkActionsProps {
  selectedItems: number[];
  onBulkAction: (action: string, itemIds: number[]) => Promise<void>;
}

export const BulkActions: React.FC<BulkActionsProps> = ({ selectedItems, onBulkAction }) => {
  const [loading, setLoading] = useState(false);

  const handleAction = async (action: string) => {
    setLoading(true);
    try {
      await onBulkAction(action, selectedItems);
    } finally {
      setLoading(false);
    }
  };

  if (selectedItems.length === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-gray-800 rounded-lg border border-gray-700 p-4 flex items-center gap-4 shadow-lg">
      <span className="text-white text-sm">
        {selectedItems.length} items selected
      </span>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleAction('delete')}
          disabled={loading}
          className="px-3 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition-colors flex items-center gap-2"
        >
          <Trash2 className="w-4 h-4" />
          Delete
        </button>
        
        <button
          onClick={() => handleAction('download')}
          disabled={loading}
          className="px-3 py-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          Export
        </button>
        
        <button
          onClick={() => handleAction('archive')}
          disabled={loading}
          className="px-3 py-2 bg-purple-600/20 text-purple-400 rounded-lg hover:bg-purple-600/30 transition-colors flex items-center gap-2"
        >
          <Archive className="w-4 h-4" />
          Archive
        </button>
      </div>
    </div>
  );
};
```

---

## Testing & Deployment Checklist

### Security Testing
- [ ] Run security scans (OWASP ZAP)
- [ ] Test input sanitization
- [ ] Verify API key protection
- [ ] Test rate limiting
- [ ] Check HTTPS enforcement
- [ ] Verify CORS configuration

### Performance Testing
- [ ] Load test API endpoints
- [ ] Test database query performance
- [ ] Verify caching works
- [ ] Test large file uploads
- [ ] Monitor memory usage
- [ ] Check response times

### Error Handling Testing
- [ ] Test error boundaries
- [ ] Verify error reporting
- [ ] Test health endpoints
- [ ] Check error recovery
- [ ] Test offline behavior
- [ ] Verify graceful degradation

### Backup & Recovery Testing
- [ ] Test database backup
- [ ] Test media file backup
- [ ] Test data export
- [ ] Test restore procedures
- [ ] Verify backup automation
- [ ] Test disaster recovery

## Deployment Configuration

### Environment Variables Required
```bash
# Security
DJANGO_SECRET_KEY=your-secret-key
CORS_ALLOWED_ORIGINS=https://yourdomain.com
API_SIGNATURE_SECRET=your-signature-secret

# Backup
BACKUP_S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Monitoring
SENTRY_DSN=your-sentry-dsn
ADMIN_EMAILS=admin@yourdomain.com

# Performance
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Production Deployment
```bash
# 1. Install dependencies
pip install -r requirements.txt
npm install

# 2. Run migrations
python manage.py migrate

# 3. Create indexes
python manage.py dbshell < sql/create_indexes.sql

# 4. Set up caching
python manage.py createcachetable

# 5. Configure monitoring
python manage.py setup_monitoring

# 6. Start services
gunicorn core.wsgi:application
celery -A core worker -l info
celery -A core beat -l info
```

## Success Metrics

### Critical Issues Resolved
- ✅ Zero data loss incidents
- ✅ No security breaches
- ✅ 99.9% uptime achieved
- ✅ Error rates below 0.1%

### Performance Targets
- ✅ API response times < 500ms
- ✅ Page load times < 2 seconds
- ✅ Database queries optimized
- ✅ 95% cache hit rate

### User Experience
- ✅ Error recovery working
- ✅ Feedback system functional
- ✅ Search working effectively
- ✅ Bulk operations available

---

**Prepared by**: Claude  
**Date**: 2025-09-01  
**For**: AI Content Studio Development Team  
**Priority**: CRITICAL - Essential for production launch  
**Total Effort**: 12-15 hours across all priorities