<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL REMEDIATION DRAFT.** Examples below predate the canonical PA route convention. The canonical PA endpoint is `POST /api/pa/chat/`; any `/api/assistant/chat/` or `/api/v1/assistant/chat/` example is a legacy compatibility shim. See [`docs/topics/personal-assistant.md`](../../topics/personal-assistant.md).

# Phase 2: High Priority Fixes (P1)

**Execution Mode:** MIXED (See dependency groups)
**Duration:** 1-2 weeks
**Total Tasks:** 14 task groups (covering 28 P1 issues)

---

## Dependency Groups

### Group A: Rate Limiting Chain (SEQUENTIAL)
```
2.1 → 2.2 → 2.3
```
Must complete in order - builds rate limiting infrastructure.

### Group B: Input Validation Chain (SEQUENTIAL)
```
2.4 → 2.5 → 2.6
```
Must complete in order - builds validation infrastructure.

### Group C: Error Handling Chain (SEQUENTIAL)
```
2.7 → 2.8
```
Must complete in order - standardizes error responses.

### Group D: Independent Fixes (PARALLEL)
```
2.9, 2.10, 2.11, 2.12, 2.13, 2.14 - Can run simultaneously
```
Each task modifies independent files.

---

## Task Overview

| Task | Issue(s) | Group | Effort | Can Parallelize |
|------|----------|-------|--------|-----------------|
| 2.1 | Rate Limiter Implementation | A | 4h | No |
| 2.2 | Apply Rate Limits to AI Endpoints | A | 2h | No (needs 2.1) |
| 2.3 | Apply Rate Limits to Video/Image | A | 2h | No (needs 2.2) |
| 2.4 | Create Input Validation Layer | B | 4h | No |
| 2.5 | Apply Validation to AI Assistant | B | 2h | No (needs 2.4) |
| 2.6 | Apply Validation to Image/Video | B | 2h | No (needs 2.5) |
| 2.7 | Standardize Error Response Format | C | 2h | No |
| 2.8 | Fix Information Leakage in Errors | C | 2h | No (needs 2.7) |
| 2.9 | Fix XSS Vulnerabilities | D | 4h | Yes |
| 2.10 | Fix Temp File Cleanup | D | 2h | Yes |
| 2.11 | Fix Race Conditions in Counters | D | 2h | Yes |
| 2.12 | Fix File Handle Leaks | D | 2h | Yes |
| 2.13 | Extract Hybrid ID Resolution | D | 2h | Yes |
| 2.14 | Fix N+1 Query Patterns | D | 4h | Yes |

---

## Group A: Rate Limiting Chain

### Task 2.1: Rate Limiter Implementation

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.1: Rate Limiter Implementation

## Context
A RateLimiter class exists in rate_limiter.py but isn't wired up. The auth middleware has is_rate_limited() returning False always.

## Your Task
1. Read core/rate_limiter.py to understand existing implementation
2. Read core/auth_middleware.py to see the stub
3. Wire up the rate limiter properly
4. Add configuration in settings.py for rate limits

## Files to Modify
- `core/rate_limiter.py` - Enhance if needed
- `core/auth_middleware.py` - Wire up rate limiting
- `core/settings.py` - Add rate limit configuration

## Implementation

### Settings configuration:
```python
# Rate limiting configuration
RATE_LIMITS = {
    'default': {'requests': 100, 'window': 60},  # 100 requests per minute
    'ai_generation': {'requests': 10, 'window': 60},  # 10 AI calls per minute
    'video_processing': {'requests': 5, 'window': 60},  # 5 video ops per minute
    'api_expensive': {'requests': 20, 'window': 60},  # 20 expensive ops per minute
}
```

### Auth middleware update:
```python
from core.rate_limiter import RateLimiter
from django.conf import settings

class AuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = RateLimiter()

    def is_rate_limited(self, request, limit_type='default'):
        user_id = request.user.id if request.user.is_authenticated else request.META.get('REMOTE_ADDR')
        limits = settings.RATE_LIMITS.get(limit_type, settings.RATE_LIMITS['default'])
        return self.rate_limiter.is_limited(
            key=f"{limit_type}:{user_id}",
            max_requests=limits['requests'],
            window_seconds=limits['window']
        )
```

## Verification
- Rate limiter should use Redis for storage
- Should track by user ID for authenticated, IP for anonymous
- Should return 429 Too Many Requests when limit exceeded

Begin by reading core/rate_limiter.py and core/auth_middleware.py.
```

### Verification
```bash
python manage.py check
make start
# Test rate limiting works
```

### Completion Sign-off
- [ ] Rate limiter configured
- [ ] Settings added
- [ ] Middleware wired up
- [ ] Returns 429 on limit exceeded

---

### Task 2.2: Apply Rate Limits to AI Endpoints

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.2: Apply Rate Limits to AI Endpoints

## Context
Now that rate limiting is implemented (Task 2.1), apply it to AI generation endpoints.

## Your Task
1. Identify all AI generation endpoints in views_assistant_bypass.py and views_image.py
2. Apply 'ai_generation' rate limit to these endpoints
3. Add appropriate error responses for rate-limited requests

## Files to Modify
- `core/views_assistant_bypass.py`
- `core/views_image.py` (AI-related endpoints)

## Implementation

### Create a decorator for rate limiting:
```python
# In core/decorators.py (create if doesn't exist)
from functools import wraps
from django.http import JsonResponse
from core.auth_middleware import get_rate_limiter

def rate_limit(limit_type='default'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if is_rate_limited(request, limit_type):
                return JsonResponse({
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait before making more requests.',
                    'retry_after': 60
                }, status=429)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

### Apply to AI endpoints:
```python
from core.decorators import rate_limit

@rate_limit('ai_generation')
def assistant_chat_bypass(request):
    ...

@rate_limit('ai_generation')
def generate_image(request):
    ...
```

Begin by reading core/views_assistant_bypass.py and identifying endpoints.
```

### Verification
```bash
# Test rapid requests get rate limited
for i in {1..15}; do curl -X POST http://localhost:8000/api/assistant/chat/; done
# Should see 429 responses after limit
```

### Completion Sign-off
- [ ] Rate limit decorator created
- [ ] Applied to AI assistant endpoints
- [ ] Applied to image generation endpoints
- [ ] 429 responses working

---

### Task 2.3: Apply Rate Limits to Video/Image Operations

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.3: Apply Rate Limits to Video/Image Operations

## Context
Apply rate limiting to expensive video and image processing operations.

## Your Task
1. Identify expensive operations in views_video.py and views_image.py
2. Apply 'video_processing' rate limit to video operations
3. Apply 'api_expensive' rate limit to image operations that call external APIs

## Files to Modify
- `core/views_video.py`
- `core/views_image.py`

## Operations to Rate Limit

### Video (video_processing limit - 5/min):
- Video generation (Runway ML)
- Video upscaling
- Video concatenation
- Color grading

### Image (api_expensive limit - 20/min):
- Image generation (Stability AI)
- Image upscaling
- Background removal
- Image-to-3D conversion

Begin by reading core/views_video.py and core/views_image.py to identify expensive operations.
```

### Verification
```bash
make start
# Test video rate limiting
# Test image rate limiting
```

### Completion Sign-off
- [ ] Video operations rate limited
- [ ] Image operations rate limited
- [ ] Different limits applied appropriately
- [ ] All operations still work within limits

---

## Group B: Input Validation Chain

### Task 2.4: Create Input Validation Layer

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.4: Create Input Validation Layer

## Context
Input validation is inconsistent across the codebase. Create a centralized validation layer.

## Your Task
1. Create core/validators.py with common validation functions
2. Include validators for: prompts, file paths, URLs, IDs, numeric ranges
3. Create Pydantic models or Django serializers for complex inputs

## Files to Create/Modify
- Create: `core/validators.py`
- Create: `core/schemas.py` (Pydantic models for request validation)

## Implementation

### core/validators.py:
```python
"""Centralized input validation utilities."""
import re
import os
from typing import Optional, Tuple
from urllib.parse import urlparse

# Maximum lengths
MAX_PROMPT_LENGTH = 10000
MAX_FILENAME_LENGTH = 255
MAX_PATH_LENGTH = 4096

def validate_prompt(prompt: str) -> Tuple[bool, Optional[str]]:
    """Validate AI prompt input."""
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"
    if len(prompt) > MAX_PROMPT_LENGTH:
        return False, f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH}"
    # Check for potential injection patterns
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, "Prompt contains potentially dangerous content"
    return True, None

def validate_file_path(path: str, must_exist: bool = False, allowed_extensions: list = None) -> Tuple[bool, Optional[str]]:
    """Validate file path for safety."""
    if not path:
        return False, "Path cannot be empty"
    if len(path) > MAX_PATH_LENGTH:
        return False, "Path exceeds maximum length"
    # Prevent path traversal
    if '..' in path or path.startswith('/'):
        normalized = os.path.normpath(path)
        if '..' in normalized:
            return False, "Path traversal not allowed"
    # Check extension if specified
    if allowed_extensions:
        ext = os.path.splitext(path)[1].lower()
        if ext not in allowed_extensions:
            return False, f"File extension not allowed. Allowed: {allowed_extensions}"
    if must_exist and not os.path.exists(path):
        return False, "File does not exist"
    return True, None

def validate_uuid(value: str) -> Tuple[bool, Optional[str]]:
    """Validate UUID format."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    if uuid_pattern.match(value):
        return True, None
    return False, "Invalid UUID format"

def validate_numeric_id(value: str) -> Tuple[bool, Optional[int]]:
    """Validate and convert numeric ID."""
    try:
        num = int(value)
        if num < 1:
            return False, "ID must be positive"
        return True, num
    except (ValueError, TypeError):
        return False, "Invalid numeric ID"

def validate_numeric_range(value: float, min_val: float = None, max_val: float = None) -> Tuple[bool, Optional[str]]:
    """Validate numeric value is within range."""
    if min_val is not None and value < min_val:
        return False, f"Value must be at least {min_val}"
    if max_val is not None and value > max_val:
        return False, f"Value must be at most {max_val}"
    return True, None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove path components
    filename = os.path.basename(filename)
    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    return filename
```

Begin implementation.
```

### Verification
```bash
python -c "from core.validators import validate_prompt; print(validate_prompt('test'))"
python -c "from core.validators import validate_file_path; print(validate_file_path('../../../etc/passwd'))"
```

### Completion Sign-off
- [ ] validators.py created
- [ ] All validation functions implemented
- [ ] Path traversal prevented
- [ ] Injection patterns blocked

---

### Task 2.5: Apply Validation to AI Assistant

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.5: Apply Validation to AI Assistant

## Context
Apply the new validation layer to AI Assistant inputs.

## Your Task
1. Read core/personal_ai_assistant_enhanced.py
2. Apply validation to all user inputs
3. Add validation to views_assistant_bypass.py

## Files to Modify
- `core/personal_ai_assistant_enhanced.py`
- `core/views_assistant_bypass.py`

## Key Validation Points
- User messages/prompts
- Project IDs
- Image/video references
- Tool parameters

Begin by reading the files and identifying all input points.
```

### Completion Sign-off
- [ ] Prompt validation applied
- [ ] ID validation applied
- [ ] Tool parameter validation applied
- [ ] Invalid inputs return helpful errors

---

### Task 2.6: Apply Validation to Image/Video

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.6: Apply Validation to Image/Video Operations

## Context
Apply validation layer to image and video processing inputs.

## Your Task
1. Apply validators to views_image.py
2. Apply validators to views_video.py
3. Validate file paths, URLs, and numeric parameters

## Files to Modify
- `core/views_image.py`
- `core/views_video.py`

Begin by identifying all input points in these files.
```

### Completion Sign-off
- [ ] Image operations validated
- [ ] Video operations validated
- [ ] File paths validated
- [ ] URLs validated

---

## Group C: Error Handling Chain

### Task 2.7: Standardize Error Response Format

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.7: Standardize Error Response Format

## Context
Error responses are inconsistent across the codebase. Create a standard format.

## Your Task
1. Create core/responses.py with standard response helpers
2. Define consistent error response structure
3. Include appropriate HTTP status codes

## Files to Create/Modify
- Create: `core/responses.py`

## Implementation

```python
"""Standardized API response helpers."""
from django.http import JsonResponse
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

def success_response(data: Any = None, message: str = None, status: int = 200) -> JsonResponse:
    """Return standardized success response."""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return JsonResponse(response, status=status)

def error_response(
    message: str,
    status: int = 400,
    error_code: str = None,
    details: dict = None,
    log_error: bool = True
) -> JsonResponse:
    """Return standardized error response."""
    response = {
        'success': False,
        'error': message
    }
    if error_code:
        response['error_code'] = error_code
    if details:
        response['details'] = details

    if log_error:
        logger.warning(f"API Error: {message} (code: {error_code})")

    return JsonResponse(response, status=status)

# Common error responses
def validation_error(message: str, field: str = None) -> JsonResponse:
    """Return validation error response."""
    details = {'field': field} if field else None
    return error_response(message, status=400, error_code='VALIDATION_ERROR', details=details)

def not_found_error(resource: str = 'Resource') -> JsonResponse:
    """Return not found error response."""
    return error_response(f'{resource} not found', status=404, error_code='NOT_FOUND')

def rate_limit_error(retry_after: int = 60) -> JsonResponse:
    """Return rate limit error response."""
    return error_response(
        'Rate limit exceeded. Please wait before making more requests.',
        status=429,
        error_code='RATE_LIMITED',
        details={'retry_after': retry_after}
    )

def server_error(log_message: str = None) -> JsonResponse:
    """Return generic server error (don't expose internal details)."""
    if log_message:
        logger.error(f"Server error: {log_message}")
    return error_response(
        'An unexpected error occurred. Please try again later.',
        status=500,
        error_code='SERVER_ERROR',
        log_error=False  # Already logged above
    )
```

Begin implementation.
```

### Completion Sign-off
- [ ] responses.py created
- [ ] Standard response helpers implemented
- [ ] Consistent error codes defined

---

### Task 2.8: Fix Information Leakage in Errors

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.8: Fix Information Leakage in Errors

## Context
Error messages expose internal details to clients. Fix to return generic messages.

## Your Task
1. Find all places that return exception details to clients
2. Replace with generic error messages using the new responses.py
3. Ensure internal details are logged server-side only

## Files to Modify
- `core/views_image.py`
- `core/views_video.py`
- `core/views_assistant_bypass.py`
- `core/personal_ai_assistant_enhanced.py`

## Pattern to Fix
```python
# BAD - exposes internal details:
except Exception as e:
    return JsonResponse({'error': str(e)}, status=500)

# GOOD - generic message, log details:
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    return server_error()
```

Begin by searching for exception handling patterns.
```

### Completion Sign-off
- [ ] Internal details no longer returned to client
- [ ] Errors properly logged server-side
- [ ] Generic messages shown to users

---

## Group D: Independent Fixes (Can Run in PARALLEL)

### Task 2.9: Fix XSS Vulnerabilities

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.9: Fix XSS Vulnerabilities

## Context
Multiple innerHTML usages without sanitization create XSS vulnerabilities.

## Your Task
1. Read ai_image_studio.html and find all innerHTML usages
2. Apply escapeHtml() from common.js consistently
3. Use textContent where HTML is not needed

## Files to Modify
- `ai_core/templates/ai_image_studio.html`

## Patterns to Fix

### For dynamic text that shouldn't contain HTML:
```javascript
// BAD
element.innerHTML = userProvidedText;

// GOOD
element.textContent = userProvidedText;
```

### For content that needs limited HTML:
```javascript
// BAD
element.innerHTML = `<div>${userPrompt}</div>`;

// GOOD
element.innerHTML = `<div>${escapeHtml(userPrompt)}</div>`;
```

### escapeHtml function (should exist in common.js):
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

Begin by reading the template and finding innerHTML usages.
```

### Completion Sign-off
- [ ] All innerHTML usages reviewed
- [ ] escapeHtml applied where needed
- [ ] textContent used where possible
- [ ] No user input rendered unsanitized

---

### Task 2.10: Fix Temp File Cleanup

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.10: Fix Temp File Cleanup

## Context
Temporary files created during video processing aren't consistently cleaned up.

## Your Task
1. Create a context manager for temp file handling
2. Apply to views_video.py operations
3. Ensure cleanup happens even on errors

## Files to Create/Modify
- Create: `core/utils/temp_files.py`
- Modify: `core/views_video.py`

## Implementation

```python
"""Temp file management utilities."""
import os
import tempfile
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

@contextmanager
def temp_file(suffix='', prefix='donkey_', delete=True):
    """Context manager for temporary files with guaranteed cleanup."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    try:
        yield path
    finally:
        if delete:
            try:
                if os.path.exists(path):
                    os.unlink(path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {path}: {e}")

@contextmanager
def temp_directory(prefix='donkey_', delete=True):
    """Context manager for temporary directories with guaranteed cleanup."""
    path = tempfile.mkdtemp(prefix=prefix)
    try:
        yield path
    finally:
        if delete:
            try:
                import shutil
                if os.path.exists(path):
                    shutil.rmtree(path)
            except Exception as e:
                logger.warning(f"Failed to delete temp dir {path}: {e}")
```

### Usage in views:
```python
from core.utils.temp_files import temp_file

def process_video(request):
    with temp_file(suffix='.mp4') as temp_path:
        # Download to temp_path
        # Process
        # Move to final location
        pass
    # temp_path automatically deleted, even on error
```

Begin implementation.
```

### Completion Sign-off
- [ ] temp_files.py created
- [ ] Applied to video operations
- [ ] Cleanup happens on success and error
- [ ] No temp file leaks

---

### Task 2.11: Fix Race Conditions in Counters

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.11: Fix Race Conditions in Counters

## Context
Counter increments in models have race conditions when multiple requests update simultaneously.

## Your Task
1. Find counter update patterns in content/models.py
2. Replace with F() expressions for atomic updates
3. Add select_for_update() where needed

## Files to Modify
- `content/models.py`
- Any views that update counters

## Pattern to Fix
```python
# BAD - race condition:
obj.view_count = obj.view_count + 1
obj.save()

# GOOD - atomic update:
from django.db.models import F

ModelClass.objects.filter(pk=obj.pk).update(view_count=F('view_count') + 1)

# Or with select_for_update for complex operations:
with transaction.atomic():
    obj = ModelClass.objects.select_for_update().get(pk=obj.pk)
    obj.view_count += 1
    obj.some_complex_operation()
    obj.save()
```

Begin by reading content/models.py and finding counter patterns.
```

### Completion Sign-off
- [ ] Counter patterns identified
- [ ] F() expressions applied
- [ ] select_for_update used where needed
- [ ] Race conditions eliminated

---

### Task 2.12: Fix File Handle Leaks

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.12: Fix File Handle Leaks

## Context
Some file operations don't properly close file handles.

## Your Task
1. Find file open() calls without context managers
2. Convert to 'with' statements
3. Apply to replicate_provider.py and other affected files

## Files to Modify
- `content/replicate_provider.py`
- Other files with file operations

## Pattern to Fix
```python
# BAD - file handle leak:
f = open(path, 'rb')
data = f.read()
# f never closed!

# GOOD - context manager:
with open(path, 'rb') as f:
    data = f.read()
# f automatically closed
```

Begin by searching for open() calls.
```

### Completion Sign-off
- [ ] All open() calls reviewed
- [ ] Context managers applied
- [ ] No file handle leaks

---

### Task 2.13: Extract Hybrid ID Resolution

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.13: Extract Hybrid ID Resolution

## Context
Hybrid ID resolution (supporting both UUIDs and numeric IDs like "image 5") is duplicated across 6+ locations.

## Your Task
1. Create centralized utility in core/utils/id_resolver.py
2. Find all duplicate implementations
3. Replace with calls to centralized utility

## Files to Create/Modify
- Create: `core/utils/id_resolver.py`
- Modify: Files with duplicate ID resolution

## Implementation

```python
"""Centralized hybrid ID resolution."""
import re
from typing import Optional, Tuple, Union
from uuid import UUID

def resolve_content_id(
    identifier: str,
    model_class,
    user=None,
    project=None
) -> Tuple[Optional[object], Optional[str]]:
    """
    Resolve hybrid identifier to model instance.

    Supports:
    - Full UUID: "550e8400-e29b-41d4-a716-446655440000"
    - Numeric: "5", "image 5", "#5"
    - Natural language: "the fifth image", "image number 5"

    Returns: (instance, error_message)
    """
    if not identifier:
        return None, "No identifier provided"

    identifier = str(identifier).strip()

    # Try UUID first
    try:
        uuid_obj = UUID(identifier)
        instance = model_class.objects.filter(id=uuid_obj).first()
        if instance:
            return instance, None
    except ValueError:
        pass

    # Extract numeric ID
    numeric_patterns = [
        r'^#?(\d+)$',  # "5" or "#5"
        r'(?:image|video|model|asset)\s*#?\s*(\d+)',  # "image 5", "video #3"
        r'(?:the\s+)?(\d+)(?:st|nd|rd|th)?',  # "the 5th", "3rd"
        r'number\s*(\d+)',  # "number 5"
    ]

    for pattern in numeric_patterns:
        match = re.search(pattern, identifier, re.IGNORECASE)
        if match:
            seq_num = int(match.group(1))
            # Build query
            queryset = model_class.objects.all()
            if user:
                queryset = queryset.filter(user=user)
            if project:
                queryset = queryset.filter(project=project)

            # Try sequential_number field first
            if hasattr(model_class, 'sequential_number'):
                instance = queryset.filter(sequential_number=seq_num).first()
                if instance:
                    return instance, None

            # Fall back to ordering by created_at
            instance = queryset.order_by('created_at')[seq_num - 1:seq_num].first()
            if instance:
                return instance, None

            return None, f"No {model_class.__name__} found with number {seq_num}"

    return None, f"Could not parse identifier: {identifier}"
```

Begin by finding duplicate implementations.
```

### Completion Sign-off
- [ ] id_resolver.py created
- [ ] All duplicates found
- [ ] Replaced with centralized calls
- [ ] All ID resolution still works

---

### Task 2.14: Fix N+1 Query Patterns

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Claude Code Prompt
```
# REMEDIATION TASK 2.14: Fix N+1 Query Patterns

## Context
Several views have N+1 query issues, causing database performance problems.

## Your Task
1. Identify N+1 patterns in views and agents
2. Add select_related() and prefetch_related() appropriately
3. Test query counts before and after

## Files to Modify
- `core/views_image.py`
- `core/views_video.py`
- `intelligence/agent_orchestrator.py`

## Common N+1 Patterns to Fix

```python
# BAD - N+1 query:
images = ImageHistory.objects.filter(user=user)
for image in images:
    print(image.project.name)  # Extra query for each image!

# GOOD - eager loading:
images = ImageHistory.objects.filter(user=user).select_related('project')
for image in images:
    print(image.project.name)  # No extra query

# For many-to-many or reverse foreign keys:
projects = Project.objects.prefetch_related('images', 'videos')
```

## Finding N+1 Queries
Look for patterns like:
- Loops that access related objects
- Template tags accessing related objects
- Serializers accessing nested objects

Begin by analyzing query patterns in the views.
```

### Completion Sign-off
- [ ] N+1 patterns identified
- [ ] select_related applied
- [ ] prefetch_related applied
- [ ] Query counts improved

---

## Phase 2 Completion Checklist

Before moving to Phase 3:

### Group A Complete
- [ ] 2.1 Rate limiter implemented
- [ ] 2.2 AI endpoints rate limited
- [ ] 2.3 Video/Image endpoints rate limited

### Group B Complete
- [ ] 2.4 Validation layer created
- [ ] 2.5 AI Assistant validated
- [ ] 2.6 Image/Video validated

### Group C Complete
- [ ] 2.7 Standard error format
- [ ] 2.8 Information leakage fixed

### Group D Complete
- [ ] 2.9 XSS vulnerabilities fixed
- [ ] 2.10 Temp file cleanup
- [ ] 2.11 Race conditions fixed
- [ ] 2.12 File handle leaks fixed
- [ ] 2.13 Hybrid ID centralized
- [ ] 2.14 N+1 queries fixed

### Platform Verification
- [ ] `python manage.py check` passes
- [ ] `make start` succeeds
- [ ] All features still work
- [ ] Rate limiting working
- [ ] Validation working

---

## Next Steps

After completing ALL Phase 2 tasks:

1. Update progress in `00-REMEDIATION-ORCHESTRATOR.md`
2. Create git tag: `git tag -a v1.1-p1-fixes -m "Phase 2 high priority fixes complete"`
3. Proceed to `03-PHASE3-ARCHITECTURE.md`
