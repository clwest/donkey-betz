# Security, Configuration, and Infrastructure Code Review

**Platform:** Unified Donkey Betz
**Review Date:** November 25, 2025
**Reviewer:** Claude Code Security Analysis
**Scope:** Security configuration, authentication, middleware, environment management

---

## Executive Summary

This comprehensive security review of the Unified Donkey Betz platform reveals a **mixed security posture** with both significant strengths and critical vulnerabilities requiring immediate attention. The platform demonstrates mature security architecture in several areas including production-grade Django security settings, comprehensive rate limiting infrastructure, and well-designed authentication middleware. However, the review uncovered **critical P0 issues** that must be resolved before any production deployment.

The most severe finding is the presence of **live API keys and credentials committed to the `.env` file**, including OpenAI, Anthropic, Stripe (LIVE keys), Reddit, GitHub, and approximately 40+ other service credentials. This represents an immediate security breach requiring credential rotation across all affected services. Additionally, the default REST Framework permission (`AllowAny`) and CSRF exemption for all `/api/` endpoints create significant attack surface.

The infrastructure demonstrates good practices including Redis-based caching with fallback, Celery task queuing with production settings, and comprehensive logging. The authentication system supports both session and token-based auth with proper middleware layering. With the critical issues addressed, this platform could achieve production-ready security status.

---

## Scores Table

| Category | Score | Notes |
|----------|-------|-------|
| **Code Quality** | 7/10 | Well-structured, consistent patterns, good documentation |
| **Architecture** | 8/10 | Clean separation, proper middleware layering, good abstractions |
| **Security** | 3/10 | Critical credential exposure, permissive defaults offset good security framework |
| **Performance** | 7/10 | Redis caching, connection pooling, but some inefficiencies |
| **Error Handling** | 6/10 | Good API responses, but bare `except:` clauses present |
| **Testing** | 4/10 | Security validation exists but limited test coverage visible |

**Overall Security Risk: HIGH** (due to P0 credential exposure)

---

## Critical Issues (P0) - MUST FIX BEFORE PRODUCTION

### P0-001: Live API Keys Committed to Repository
- **File:** `.env` (lines 1-144)
- **Severity:** CRITICAL
- **Description:** The `.env` file contains 40+ live API keys and credentials including:
  - OpenAI API Key (line 1)
  - Anthropic API Key (line 8)
  - Stripe LIVE Secret Key (line 124) - `sk_live_*`
  - Stripe LIVE Publishable Key (line 126) - `pk_live_*`
  - GitHub PAT (line 104)
  - Reddit credentials with plaintext password (lines 63-67)
  - Coinbase private EC key (line 87)
  - Twilio credentials (lines 54-56)
  - DataDog API Key (line 99)
  - Cloudinary secrets (lines 142-144)
  - 30+ additional service keys

- **Impact:** Complete compromise of all connected services; potential financial loss via Stripe; account takeover across all platforms; data breach exposure
- **Recommendation:**
  1. **IMMEDIATELY** rotate ALL exposed credentials
  2. Remove `.env` from git history using `git filter-branch` or BFG Repo Cleaner
  3. Add `.env` to `.gitignore` (verify it's there)
  4. Use a secrets manager (AWS Secrets Manager, HashiCorp Vault, or 1Password Secrets Automation)
  5. Implement pre-commit hooks to prevent future secret commits

```bash
# Example: Add to .gitignore
.env
.env.local
*.key
*_credentials.json
```

### P0-002: Weak Django SECRET_KEY
- **File:** `.env` (line 27)
- **Severity:** CRITICAL
- **Description:** `SECRET_KEY=super-secret-donkey-business` is a weak, guessable secret key
- **Impact:** Session hijacking, CSRF token prediction, cryptographic signature forgery
- **Recommendation:** Generate a strong random key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### P0-003: REST Framework Default Permissions Set to AllowAny
- **File:** `core/settings.py` (lines 385-387)
- **Severity:** CRITICAL
- **Description:**
```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.AllowAny',  # Temporarily allow all requests
],
```
- **Impact:** All API endpoints are publicly accessible without authentication
- **Recommendation:** Change to `IsAuthenticated` and explicitly use `AllowAny` only where needed:
```python
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated',
],
```

### P0-004: ALLOWED_HOSTS Contains Wildcard
- **File:** `.env` (line 43)
- **Severity:** CRITICAL
- **Description:** `ALLOWED_HOSTS=localhost,127.0.0.1,192.168.10.104,*`
- **Impact:** Host header injection attacks, cache poisoning, password reset poisoning
- **Recommendation:** Remove wildcard `*` and specify exact hosts:
```
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.10.104
```

---

## High Priority Issues (P1) - Fix Soon

### P1-001: CSRF Disabled for All API Endpoints
- **File:** `core/middleware.py` (lines 23-26)
- **Severity:** HIGH
- **Description:** CSRF protection is disabled for ALL `/api/` paths:
```python
if request.path.startswith('/api/'):
    setattr(request, '_dont_enforce_csrf_checks', True)
    return None
```
- **Impact:** Cross-site request forgery attacks on state-changing API endpoints
- **Recommendation:** Only exempt token-authenticated requests, not all API requests

### P1-002: Password Logged in Login View
- **File:** `core/auth_views.py` (line 32)
- **Severity:** HIGH
- **Description:** Password length is logged on every login attempt:
```python
logger.info(f"Login attempt - Username: {username}, Password: {'*' * len(password) if password else 'None'}")
```
- **Impact:** Password length exposure in logs; timing side-channel for password guessing
- **Recommendation:** Remove password-related logging entirely:
```python
logger.info(f"Login attempt - Username: {username}")
```

### P1-003: Bare Except Clauses Hide Errors
- **File:** `core/auth_views.py` (lines 53-57, 100-103)
- **Severity:** HIGH
- **Description:** Multiple bare `except:` clauses silently catch all exceptions
- **Impact:** Security errors may be silently ignored; debugging becomes difficult
- **Recommendation:** Catch specific exceptions:
```python
except UserProfile.DoesNotExist:
    credits = 10000
    subscription = 'premium'
```

### P1-004: Debug Template Setting Always True
- **File:** `core/settings.py` (line 159)
- **Severity:** HIGH
- **Description:** Template debug is hardcoded to `True`:
```python
'debug': True,  # Disable template caching in development
```
- **Impact:** Template errors expose full stack traces in production
- **Recommendation:** Make conditional on DEBUG setting:
```python
'debug': DEBUG,
```

### P1-005: Rate Limiting Not Implemented
- **File:** `core/auth_middleware.py` (lines 310-314)
- **Severity:** HIGH
- **Description:** The `is_rate_limited` method is a stub returning `False`:
```python
def is_rate_limited(self, client_ip, endpoint, limit, window):
    """Check if client is rate limited (stub - implement with Redis)"""
    return False
```
- **Impact:** No actual rate limiting on authentication endpoints; brute force attacks possible
- **Recommendation:** Implement using Django's cache or the existing `RateLimiter` class from `rate_limiter.py`

### P1-006: Encryption Key Stored in Plaintext
- **File:** `.env` (lines 4-6)
- **Severity:** HIGH
- **Description:** Fernet encryption keys stored in `.env`:
```
ENCRYPTION_KEY="[REDACTED - ROTATED]"
ENCRYPTION_KEY_BACKUP="[REDACTED - ROTATED]"
```
- **Impact:** If `.env` is compromised, all encrypted data can be decrypted
- **Recommendation:** Use a hardware security module (HSM) or cloud KMS for encryption key storage

---

## Medium Priority Issues (P2) - Normal Development

### P2-001: Token in Query String (Development Mode)
- **File:** `core/auth_middleware.py` (lines 118-120)
- **Severity:** MEDIUM
- **Description:** Tokens can be passed via query parameter in DEBUG mode:
```python
if settings.DEBUG:
    return request.GET.get('token')
```
- **Impact:** Tokens may be logged in server logs, browser history, referrer headers
- **Recommendation:** Consider removing this feature entirely; use header-based auth only

### P2-002: Information Disclosure in Error Messages
- **File:** `core/auth_views.py` (lines 72-73)
- **Severity:** MEDIUM
- **Description:** Failed login reveals the attempted username:
```python
return Response(
    {'detail': f'Invalid credentials for user: {username}'},
```
- **Impact:** Username enumeration attacks
- **Recommendation:** Use generic message: `"Invalid credentials"`

### P2-003: Overly Permissive CORS Regex Patterns
- **File:** `core/settings.py` (lines 413-417)
- **Severity:** MEDIUM
- **Description:** Regex patterns allow any Vercel/Netlify subdomain:
```python
r"^https://.*\.vercel\.app$",
r"^https://.*\.netlify\.app$",
```
- **Impact:** Malicious sites on these platforms could make cross-origin requests
- **Recommendation:** Use specific deployment URLs when known

### P2-004: Missing Input Validation
- **File:** `core/auth_views.py` (lines 238-245)
- **Severity:** MEDIUM
- **Description:** Profile update accepts any field from request.data without validation:
```python
for field in update_fields:
    if field in request.data:
        setattr(profile, field, request.data[field])
```
- **Impact:** Potential type confusion or unexpected data storage
- **Recommendation:** Use Django REST Framework serializers with validation

### P2-005: Session Cookie Age Too Long
- **File:** `core/settings.py` (line 652)
- **Severity:** MEDIUM
- **Description:** Session cookie age is 2 weeks (1209600 seconds)
- **Impact:** Increased window for session theft
- **Recommendation:** Reduce to 1 week or less for sensitive applications

### P2-006: CSP Allows Unsafe-Inline
- **File:** `core/settings.py` (lines 667-668)
- **Severity:** MEDIUM
- **Description:** Content Security Policy allows unsafe-inline for scripts and styles
- **Impact:** XSS attacks via inline scripts remain possible
- **Recommendation:** Migrate to nonce-based CSP

---

## Low Priority Issues (P3) - Nice to Have

### P3-001: Duplicate Import Statement
- **File:** `core/settings.py` (lines 12, 23)
- **Severity:** LOW
- **Description:** `import os` appears twice
- **Impact:** Code cleanliness
- **Recommendation:** Remove duplicate import

### P3-002: Inconsistent Token Header Naming
- **File:** Multiple files
- **Severity:** LOW
- **Description:** Token headers use both `X-API-Key` and `Authorization`
- **Impact:** Potential confusion in client implementations
- **Recommendation:** Standardize on one approach (prefer `Authorization: Bearer <token>`)

### P3-003: Hardcoded User Agent String
- **File:** `.env` (line 65)
- **Severity:** LOW
- **Description:** User-Agent string for Reddit API is hardcoded with specific Chrome version
- **Impact:** May be flagged as suspicious by Reddit's anti-bot systems
- **Recommendation:** Make configurable and keep updated

### P3-004: Debug Logging Verbose
- **File:** `core/settings.py` (lines 550-561)
- **Severity:** LOW
- **Description:** File logging at DEBUG level in production could create large log files
- **Impact:** Disk space consumption, potential performance impact
- **Recommendation:** Set file handler to INFO in production

---

## Positive Findings

### Well-Designed Security Infrastructure
1. **Comprehensive Middleware Stack** (`core/auth_middleware.py`):
   - Security headers middleware with HSTS, X-Frame-Options, CSP
   - API logging middleware for audit trails
   - Well-structured authentication flow

2. **Rate Limiting Framework** (`core/rate_limiter.py`):
   - Token bucket algorithm implementation
   - Per-service configurable limits
   - Burst protection with cooldown periods
   - HTTP rate limit headers in responses

3. **Environment Security Module** (`core/security.py`):
   - Encryption support for sensitive values
   - Environment validation system
   - Sensitive key masking for logs
   - Production configuration validation

4. **Django Security Settings** (`core/settings.py` lines 626-676):
   - HSTS enabled with preload
   - Secure cookie settings for production
   - X-Frame-Options DENY
   - Content-Type nosniff
   - XSS filter enabled
   - Referrer-Policy configured

5. **WebSocket Authentication** (`core/auth_middleware.py`):
   - Token validation for WebSocket connections
   - Configurable auth requirements
   - Proper close codes for auth failures

6. **Password Validation**:
   - All Django password validators enabled
   - Configurable minimum length (default 12)

7. **File Upload Protection**:
   - Maximum file size limits configured
   - Allowed extensions whitelist

---

## Detailed Findings

### Finding 1: Exposed Production Stripe Keys
- **File:** `.env`
- **Lines:** 124-126
- **Severity:** P0 - CRITICAL
- **Description:** Live Stripe keys with `sk_live_` and `pk_live_` prefixes are committed
- **Impact:** Financial transactions can be initiated; customer payment data at risk; potential regulatory compliance violation (PCI-DSS)
- **Recommendation:**
  1. Immediately rotate keys in Stripe Dashboard
  2. Review Stripe logs for unauthorized access
  3. Notify affected parties if compromise suspected
- **Code:**
```env
STRIPE_SECRET_KEY="[REDACTED - ROTATION REQUIRED]"
STRIPE_PUBLISHABLE_KEY="pk_live_51S3KGRICc9cY4M3SxX8wSaIjlvFiuWorJFURkLbic0yrK6QRy8pzsXXtymZjAY7ZC5YkzJEXA5HTvlAcMC7SbIXz00KOvmAiQr"
```

### Finding 2: Reddit Credentials with Plaintext Password
- **File:** `.env`
- **Lines:** 63-67
- **Severity:** P0 - CRITICAL
- **Description:** Reddit username and password stored in plaintext
- **Impact:** Account takeover; if password reused, lateral movement possible
- **Code:**
```env
REDDIT_USERNAME="Photo-dad2017"
REDDIT_PASSWORD="[REDACTED - ROTATION REQUIRED]"
```

### Finding 3: Coinbase EC Private Key Exposed
- **File:** `.env`
- **Lines:** 87
- **Severity:** P0 - CRITICAL
- **Description:** Full EC private key in PEM format
- **Impact:** Complete control over Coinbase integrations; potential financial loss
- **Code:**
```env
COINBASE_PRIVATE_KEY="[PRIVATE_KEY_REDACTED_AND_ROTATED]"
```

### Finding 4: GitHub Personal Access Token
- **File:** `.env`
- **Line:** 104
- **Severity:** P0 - CRITICAL
- **Description:** GitHub PAT with undefined scope
- **Impact:** Repository access; potential supply chain attacks
- **Code:**
```env
GITHUB_TOKEN="github_pat_[REDACTED - ROTATED]"
```

### Finding 5: Universal API CSRF Bypass
- **File:** `core/middleware.py`
- **Lines:** 23-26
- **Severity:** P1 - HIGH
- **Description:** All API endpoints exempt from CSRF protection regardless of authentication method
- **Impact:** State-changing requests can be forged from malicious sites
- **Recommendation:** Only exempt token-authenticated requests:
```python
def process_view(self, request, view_func, view_args, view_kwargs):
    # Only exempt if using token authentication
    if request.META.get('HTTP_X_API_KEY') or \
       request.META.get('HTTP_AUTHORIZATION', '').startswith(('Token ', 'Bearer ')):
        setattr(request, '_dont_enforce_csrf_checks', True)
        return None

    # Keep CSRF for session-based API requests
    return None
```

---

## Files Reviewed Summary Table

| File | Lines | Status | Issues Found |
|------|-------|--------|--------------|
| `core/settings.py` | 871 | Reviewed | P0: 1, P1: 2, P2: 3, P3: 1 |
| `core/urls.py` | 500+ | Reviewed | Exposed endpoints noted |
| `.env` | 144 | Reviewed | P0: 4 (40+ credentials) |
| `.env.example` | 365 | Reviewed | Template with placeholders - OK |
| `Makefile` | 241 | Reviewed | Clean, no secrets |
| `core/auth_middleware.py` | 366 | Reviewed | P1: 1, P2: 1 |
| `core/middleware.py` | 175 | Reviewed | P1: 1 |
| `core/auth_views.py` | 351 | Reviewed | P1: 2, P2: 1 |
| `core/security.py` | 403 | Reviewed | Well-designed |
| `core/rate_limiter.py` | 317 | Reviewed | Good implementation |
| `core/mobile_authentication.py` | 54 | Reviewed | Clean, appropriate |

---

## Remediation Priority Matrix

| Priority | Count | Estimated Effort | Risk if Not Fixed |
|----------|-------|------------------|-------------------|
| P0 - Critical | 4 | 2-4 hours | Complete system compromise |
| P1 - High | 6 | 4-8 hours | Significant vulnerability |
| P2 - Medium | 6 | 8-16 hours | Moderate risk |
| P3 - Low | 4 | 2-4 hours | Minimal risk |

---

## Immediate Action Items

1. **TODAY:** Rotate ALL exposed API keys (40+ services)
2. **TODAY:** Change Stripe keys and review transaction logs
3. **TODAY:** Regenerate Django SECRET_KEY
4. **THIS WEEK:** Remove `.env` from git history
5. **THIS WEEK:** Change REST Framework default permissions
6. **THIS WEEK:** Implement actual rate limiting on auth endpoints
7. **BEFORE PRODUCTION:** Full security audit and penetration test

---

## Conclusion

The Unified Donkey Betz platform has a solid security architecture foundation with well-designed middleware, rate limiting, and environment management systems. However, the critical credential exposure in `.env` represents an immediate and severe security risk that requires urgent remediation. Once the P0 and P1 issues are addressed, this platform can achieve a strong security posture suitable for production deployment.

**Report Generated:** November 25, 2025
**Classification:** CONFIDENTIAL - Contains security vulnerability details
