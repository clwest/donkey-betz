# Phase 1: Critical Security Fixes (P0)

**Execution Mode:** STRICTLY SEQUENTIAL
**Duration:** 3-5 days
**Total Tasks:** 9 (covering 18 P0 issues)

---

## CRITICAL: Execute These Tasks ONE AT A TIME

Each task modifies security-critical code. Complete and verify each task before starting the next.

---

## Task Overview

| Task | Issue(s) | File(s) | Effort | Dependencies |
|------|----------|---------|--------|--------------|
| 1.1 | Credential Rotation | `.env`, external services | 4h | None |
| 1.2 | Django SECRET_KEY | `.env`, `settings.py` | 0.5h | 1.1 |
| 1.3 | ALLOWED_HOSTS | `.env`, `settings.py` | 0.5h | 1.2 |
| 1.4 | REST Framework Auth | `settings.py` | 1h | 1.3 |
| 1.5 | Remove eval() | `agent_executor.py` | 2h | None* |
| 1.6 | CSRF Protection | `views_assistant_bypass.py` | 1h | 1.4 |
| 1.7 | Debug Statements | `personal_ai_assistant.py` | 1h | None* |
| 1.8 | ffmpeg Timeouts | `views_video.py` | 2h | None* |
| 1.9 | SSRF Protection | `views_video.py` | 2h | 1.8 |

*Can technically run in parallel but sequential recommended for safety

---

## Task 1.1: Credential Rotation

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
40+ live API keys exposed in `.env` file including Stripe LIVE keys, OpenAI, Anthropic, GitHub PAT, Reddit credentials, and Coinbase private key.

### Claude Code Prompt
```
# REMEDIATION TASK 1.1: Credential Rotation

## Context
The code review found 40+ live API credentials exposed in the .env file. These need to be rotated across all services.

## Your Task
1. First, read the current .env file to inventory all credentials
2. Use `.env.example` as the placeholder template showing what's needed
3. Create documentation listing each service that needs credential rotation
4. DO NOT generate new credentials - just document what needs rotation

## Files to Modify
- Use: `.env.example` (with placeholder values)
- Create: `docs/code-review/remediation/CREDENTIAL-ROTATION-CHECKLIST.md`

## Important
- Do NOT delete or modify the actual .env file
- Do NOT commit any actual credentials
- Create a checklist the user can follow to rotate each credential manually

## Output Expected
1. `.env.example` with all required environment variables (no real values)
2. CREDENTIAL-ROTATION-CHECKLIST.md with:
   - List of all services needing rotation
   - Links to each service's credential management page
   - Priority order (Stripe first due to financial risk)
   - Verification steps for each

Begin by reading the .env file.
```

### Manual Steps After Task
1. [ ] Log into each service and rotate credentials
2. [ ] Update local .env with new values
3. [ ] Test each integration
4. [ ] Remove .env from git history (use BFG Repo Cleaner)

### Verification
```bash
# After rotating credentials, verify each service:
python scripts/test_api_keys.py
make start
# Test a feature that uses each API
```

### Completion Sign-off
- [ ] .env.example reviewed
- [ ] CREDENTIAL-ROTATION-CHECKLIST.md created
- [ ] All credentials rotated manually
- [ ] All integrations tested
- [ ] .env removed from git history

---

## Task 1.2: Django SECRET_KEY

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
Weak Django SECRET_KEY that may be compromised.

### Claude Code Prompt
```
# REMEDIATION TASK 1.2: Django SECRET_KEY

## Context
The Django SECRET_KEY needs to be regenerated with a cryptographically secure value.

## Your Task
1. Read the current settings.py to understand how SECRET_KEY is loaded
2. Generate a new secure SECRET_KEY (50+ characters, cryptographically random)
3. Update `.env.example` to show the SECRET_KEY format
4. Add validation in settings.py to ensure SECRET_KEY meets security requirements

## Files to Modify
- `core/settings.py` - Add SECRET_KEY validation
- `.env.example` - Add SECRET_KEY placeholder with format note

## Security Requirements
- Minimum 50 characters
- Must include mixed case, numbers, special characters
- Must be loaded from environment, never hardcoded

## Code to Add (settings.py)
```python
# Near the top of settings.py, after loading SECRET_KEY
import re

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ValueError("SECRET_KEY must be at least 50 characters. Generate with: python -c \"import secrets; print(secrets.token_urlsafe(64))\"")
```

## Verification
After updating, the user should run:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
# Copy output to .env as SECRET_KEY
python manage.py check
```

Begin by reading core/settings.py.
```

### Verification
```bash
python manage.py check
make start
```

### Completion Sign-off
- [ ] settings.py updated with SECRET_KEY validation
- [ ] .env.example updated
- [ ] New SECRET_KEY generated and set in .env
- [ ] Django check passes

---

## Task 1.3: ALLOWED_HOSTS Fix

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
ALLOWED_HOSTS contains wildcard '*' allowing any host.

### Claude Code Prompt
```
# REMEDIATION TASK 1.3: ALLOWED_HOSTS Security

## Context
ALLOWED_HOSTS is set to '*' which allows requests from any host, enabling host header attacks.

## Your Task
1. Read current settings.py to see ALLOWED_HOSTS configuration
2. Update to use a secure default with environment variable override
3. Add validation to prevent wildcard in production

## Files to Modify
- `core/settings.py`
- `.env.example`

## Implementation
```python
# In settings.py
ALLOWED_HOSTS_STR = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',')]

# Prevent wildcard in production
if not DEBUG and '*' in ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS cannot contain '*' in production (DEBUG=False)")
```

## .env.example addition
```
# Comma-separated list of allowed hosts (no wildcards in production)
ALLOWED_HOSTS=localhost,127.0.0.1
```

Begin by reading core/settings.py.
```

### Verification
```bash
python manage.py check
make start
curl -H "Host: evil.com" http://localhost:8000/  # Should fail
```

### Completion Sign-off
- [ ] ALLOWED_HOSTS updated in settings.py
- [ ] Validation added for production
- [ ] `.env.example` updated
- [ ] Host header attack test fails as expected

---

## Task 1.4: REST Framework Authentication Default

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
REST_FRAMEWORK DEFAULT_PERMISSION_CLASSES set to AllowAny.

### Claude Code Prompt
```
# REMEDIATION TASK 1.4: REST Framework Authentication

## Context
REST Framework's DEFAULT_PERMISSION_CLASSES is set to AllowAny, making all API endpoints publicly accessible.

## Your Task
1. Read settings.py to find REST_FRAMEWORK configuration
2. Change default to IsAuthenticated
3. Identify any views that legitimately need AllowAny and add explicit decorators
4. Read key API views to understand which need public access

## Files to Modify
- `core/settings.py` - Change default permission
- Any views that need public access - Add explicit @permission_classes([AllowAny])

## Implementation

### settings.py change:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # ... rest of config
}
```

### For views that MUST be public (login, health check, etc.):
```python
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    ...
```

## Views That Likely Need AllowAny
- Login/logout endpoints
- Password reset
- Health check endpoints
- Public content endpoints (if any)

## Verification
After changes, test:
1. Unauthenticated request to protected endpoint → 401/403
2. Authenticated request → Success
3. Login endpoint still works without auth

Begin by reading core/settings.py and then identify views needing public access.
```

### Verification
```bash
python manage.py check
make start
# Test unauthenticated API call - should return 401/403
curl http://localhost:8000/api/some-endpoint/
# Test login still works
```

### Completion Sign-off
- [ ] REST_FRAMEWORK default changed to IsAuthenticated
- [ ] Public endpoints explicitly marked with AllowAny
- [ ] Unauthenticated requests properly rejected
- [ ] Login/public endpoints still work

---

## Task 1.5: Remove eval() Vulnerability

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
eval() used on user input in agent_executor.py calculate function.

### Claude Code Prompt
```
# REMEDIATION TASK 1.5: Remove eval() Vulnerability

## Context
CRITICAL: The calculate tool in agent_executor.py uses eval() on user input, allowing arbitrary code execution.

## Your Task
1. Read intelligence/agent_executor.py to find the calculate function
2. Replace eval() with a safe expression evaluator
3. Test the fix maintains calculation functionality

## Files to Modify
- `intelligence/agent_executor.py`

## Safe Implementation Options

### Option 1: ast.literal_eval (for simple expressions)
```python
import ast
import operator

def safe_eval(expression: str) -> float:
    """Safely evaluate mathematical expressions."""
    # Define allowed operators
    operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            return operators[type(node.op)](left, right)
        elif isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            return operators[type(node.op)](operand)
        else:
            raise ValueError(f"Unsupported operation: {type(node)}")

    try:
        tree = ast.parse(expression, mode='eval')
        return _eval(tree.body)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}") from e
```

### Option 2: Use numexpr library (if more complex math needed)
```python
import numexpr as ne

def calculate(self, expression: str, **kwargs) -> Dict:
    try:
        # numexpr safely evaluates numerical expressions
        result = ne.evaluate(expression)
        return {"result": float(result)}
    except Exception as e:
        return {"error": f"Invalid expression: {str(e)}"}
```

## Important
- The replacement must handle basic math: +, -, *, /, ** (power)
- Should NOT allow: function calls, imports, attribute access
- Must return helpful error for invalid input

Begin by reading intelligence/agent_executor.py.
```

### Verification
```bash
python manage.py check
# Test safe calculations work
python -c "from intelligence.agent_executor import AgentExecutor; e = AgentExecutor(); print(e.calculate('2 + 2'))"
# Test malicious input is blocked
python -c "from intelligence.agent_executor import AgentExecutor; e = AgentExecutor(); print(e.calculate('__import__(\"os\").system(\"ls\")'))"
```

### Completion Sign-off
- [ ] eval() removed from calculate function
- [ ] Safe expression evaluator implemented
- [ ] Basic math operations work
- [ ] Malicious input is blocked

---

## Task 1.6: CSRF Protection

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
@csrf_exempt on assistant chat endpoint.

### Claude Code Prompt
```
# REMEDIATION TASK 1.6: CSRF Protection for Assistant

## Context
The assistant chat endpoint uses @csrf_exempt, bypassing Django's CSRF protection.

## Your Task
1. Read core/views_assistant_bypass.py to understand current implementation
2. Remove @csrf_exempt decorator
3. Ensure frontend sends CSRF token with requests
4. Verify the authenticatedFetch helper in frontend handles CSRF

## Files to Review/Modify
- `core/views_assistant_bypass.py` - Remove @csrf_exempt
- `ai_core/templates/ai_image_studio.html` - Verify CSRF token is sent

## Implementation

### Remove @csrf_exempt:
```python
# REMOVE this line:
# @csrf_exempt

# The view should just be:
@require_http_methods(["POST"])
def assistant_chat_bypass(request):
    ...
```

### Verify Frontend (should already exist):
```javascript
// In authenticatedFetch or similar:
headers: {
    'X-CSRFToken': getCookie('csrftoken'),
    ...
}
```

## If frontend doesn't send CSRF token:
```javascript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
```

Begin by reading core/views_assistant_bypass.py.
```

### Verification
```bash
make start
# Test assistant chat still works (with CSRF token)
# Test without CSRF token - should return 403
```

### Completion Sign-off
- [ ] @csrf_exempt removed from views_assistant_bypass.py
- [ ] Frontend verified to send CSRF token
- [ ] Assistant chat works with proper CSRF
- [ ] Requests without CSRF are rejected

---

## Task 1.7: Remove Debug Print Statements

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
Debug print statements in production code may leak sensitive information.

### Claude Code Prompt
```
# REMEDIATION TASK 1.7: Remove Debug Print Statements

## Context
Debug print statements in personal_ai_assistant_enhanced.py may expose sensitive information in production logs.

## Your Task
1. Read personal_ai_assistant_enhanced.py and find all print statements
2. Convert appropriate ones to proper logging
3. Remove unnecessary debug prints
4. Ensure no sensitive data is logged

## Files to Modify
- `core/personal_ai_assistant_enhanced.py`

## Guidelines

### Replace print with logging:
```python
import logging
logger = logging.getLogger(__name__)

# Instead of:
print(f"Processing message: {message}")

# Use:
logger.debug(f"Processing message for project {project_id}")
# Note: Don't log full message content, just metadata
```

### Remove entirely:
- Prints that dump full request/response data
- Prints showing API keys or tokens
- Prints showing user credentials

### Keep as logging:
- Error conditions (logger.error)
- Important state changes (logger.info)
- Debugging checkpoints (logger.debug)

## Sensitive Data to NEVER Log
- API keys/tokens
- User passwords
- Full prompt content (may contain PII)
- Full API responses (may contain sensitive data)

Begin by reading core/personal_ai_assistant_enhanced.py and searching for print statements.
```

### Verification
```bash
python manage.py check
make start
# Run assistant and check console - no sensitive data should print
```

### Completion Sign-off
- [ ] All print statements reviewed
- [ ] Sensitive prints removed
- [ ] Appropriate prints converted to logging
- [ ] No sensitive data in logs

---

## Task 1.8: ffmpeg Timeout Protection

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
subprocess.run() calls to ffmpeg lack timeout, can hang indefinitely.

### Claude Code Prompt
```
# REMEDIATION TASK 1.8: ffmpeg Timeout Protection

## Context
All ffmpeg subprocess calls lack timeout parameters, risking hung processes on corrupt files or infinite streams.

## Your Task
1. Read core/views_video.py and find all subprocess.run() calls
2. Add timeout parameter to each (recommend 300 seconds for video ops)
3. Add proper timeout exception handling
4. Consider adding a configurable timeout in settings

## Files to Modify
- `core/views_video.py`
- `core/settings.py` (optional - add FFMPEG_TIMEOUT setting)

## Implementation

### Add timeout to subprocess calls:
```python
# Instead of:
result = subprocess.run(cmd, capture_output=True, text=True)

# Use:
try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=settings.FFMPEG_TIMEOUT  # or 300 if not configurable
    )
except subprocess.TimeoutExpired:
    logger.error(f"ffmpeg operation timed out after {settings.FFMPEG_TIMEOUT}s")
    return JsonResponse({
        'success': False,
        'error': 'Video processing timed out. The file may be too large or corrupted.'
    }, status=408)
```

### Settings addition (optional but recommended):
```python
# In settings.py
FFMPEG_TIMEOUT = int(os.getenv('FFMPEG_TIMEOUT', 300))  # 5 minutes default
```

## Timeout Recommendations by Operation
- Quick operations (trim, extract frame): 60s
- Standard operations (upscale, color grade): 300s
- Long operations (concatenate many videos): 600s

Begin by reading core/views_video.py and finding subprocess calls.
```

### Verification
```bash
python manage.py check
make start
# Test video operations still work
# Test timeout with corrupt file (if available)
```

### Completion Sign-off
- [ ] All subprocess.run() calls have timeout
- [ ] Timeout exception handling added
- [ ] User-friendly timeout error messages
- [ ] Video operations still work normally

---

## Task 1.9: SSRF Protection

### Status: [ ] NOT STARTED / [ ] IN PROGRESS / [ ] COMPLETE

### Issue
URLs downloaded without validation, allowing SSRF attacks.

### Claude Code Prompt
```
# REMEDIATION TASK 1.9: SSRF Protection for URL Downloads

## Context
Video downloads accept any URL without validation, allowing Server-Side Request Forgery (SSRF) attacks to access internal resources.

## Your Task
1. Read core/views_video.py to find URL download functions
2. Implement URL validation with domain allowlist
3. Block private/internal IP ranges
4. Add the validation to all URL download points

## Files to Modify
- `core/views_video.py`
- Create: `core/utils/url_validator.py` (new utility)

## Implementation

### Create url_validator.py:
```python
"""URL validation to prevent SSRF attacks."""
import ipaddress
import socket
from urllib.parse import urlparse
from django.conf import settings

# Allowed domains for video downloads
ALLOWED_VIDEO_DOMAINS = getattr(settings, 'ALLOWED_VIDEO_DOMAINS', [
    'cdn.runwayml.com',
    'storage.googleapis.com',
    'res.cloudinary.com',
    's3.amazonaws.com',
    # Add other legitimate CDN domains
])

# Private IP ranges to block
PRIVATE_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
    ipaddress.ip_network('127.0.0.0/8'),
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local
    ipaddress.ip_network('::1/128'),  # IPv6 localhost
]

def is_private_ip(ip_str: str) -> bool:
    """Check if IP is in private range."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in network for network in PRIVATE_RANGES)
    except ValueError:
        return True  # Invalid IP, treat as private for safety

def validate_url(url: str, check_domain: bool = True) -> tuple[bool, str]:
    """
    Validate URL for safe downloading.

    Returns: (is_valid, error_message)
    """
    try:
        parsed = urlparse(url)

        # Must be http or https
        if parsed.scheme not in ('http', 'https'):
            return False, "URL must use http or https"

        # Must have a hostname
        if not parsed.hostname:
            return False, "URL must have a valid hostname"

        # Check domain allowlist
        if check_domain and parsed.hostname not in ALLOWED_VIDEO_DOMAINS:
            return False, f"Domain not allowed: {parsed.hostname}"

        # Resolve hostname and check for private IPs
        try:
            ip = socket.gethostbyname(parsed.hostname)
            if is_private_ip(ip):
                return False, "URL resolves to private IP address"
        except socket.gaierror:
            return False, "Could not resolve hostname"

        return True, ""

    except Exception as e:
        return False, f"Invalid URL: {str(e)}"
```

### Use in views_video.py:
```python
from core.utils.url_validator import validate_url

def download_video(request):
    url = request.POST.get('url')

    is_valid, error = validate_url(url)
    if not is_valid:
        return JsonResponse({'success': False, 'error': error}, status=400)

    # Proceed with download...
```

Begin by reading core/views_video.py to find all URL download locations.
```

### Verification
```bash
python manage.py check
make start
# Test valid URL download works
# Test blocked domain is rejected
# Test private IP is rejected (e.g., http://127.0.0.1/)
```

### Completion Sign-off
- [ ] url_validator.py created
- [ ] All URL download points validated
- [ ] Private IPs blocked
- [ ] Allowed domains configurable
- [ ] Legitimate downloads still work

---

## Phase 1 Completion Checklist

Before moving to Phase 2, verify ALL of the following:

### Security Fixes
- [ ] 1.1 All credentials rotated
- [ ] 1.2 Strong SECRET_KEY generated and validated
- [ ] 1.3 ALLOWED_HOSTS properly configured
- [ ] 1.4 REST Framework requires authentication by default
- [ ] 1.5 eval() replaced with safe evaluator
- [ ] 1.6 CSRF protection enabled on assistant
- [ ] 1.7 Debug prints removed/converted to logging
- [ ] 1.8 ffmpeg timeout protection added
- [ ] 1.9 SSRF protection implemented

### Platform Verification
- [ ] `python manage.py check` passes
- [ ] `make start` succeeds
- [ ] All existing features still work:
  - [ ] Image generation
  - [ ] Video generation
  - [ ] Audio generation
  - [ ] 3D model generation
  - [ ] AI Assistant chat
- [ ] API authentication working correctly
- [ ] No sensitive data in logs

### Git Status
- [ ] All changes committed with descriptive messages
- [ ] .env removed from git history
- [ ] No credentials in any committed files

---

## Next Steps

After completing ALL Phase 1 tasks:

1. Update progress in `00-REMEDIATION-ORCHESTRATOR.md`
2. Create git tag: `git tag -a v1.0-security-phase1 -m "Phase 1 security fixes complete"`
3. Proceed to `02-PHASE2-HIGH-PRIORITY.md`

---

**REMINDER:** Execute these tasks ONE AT A TIME. Do not proceed to the next task until the current one is fully verified.
