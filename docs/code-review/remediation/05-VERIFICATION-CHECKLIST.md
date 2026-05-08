<!-- DOC-POINTER-V1 -->
> **⚠ HISTORICAL REMEDIATION CHECKLIST.** curl examples below predate the canonical PA route convention. The canonical PA endpoint is `POST /api/pa/chat/`; `/api/assistant/chat/` and `/api/v1/assistant/chat/` are legacy compatibility shims only. See [`docs/topics/personal-assistant.md`](../../topics/personal-assistant.md).

# Final Verification Checklist

Use this checklist after completing all remediation phases to verify the fixes are working correctly.

---

## Pre-Verification Setup

```bash
# Ensure clean state
git status  # Should be clean or all changes committed
make stop   # Stop any running services

# Fresh start
make start
```

---

## 1. Security Verification

### 1.1 Credential Security
- [ ] `.env` file NOT in git: `git ls-files .env` (should return nothing)
- [ ] New SECRET_KEY is 50+ characters
- [ ] API keys rotated (test each integration)
- [ ] No credentials in any committed file: `git log -p | grep -i "api_key\|secret\|password"` (manual review)

### 1.2 Authentication & Authorization
```bash
# Test unauthenticated access is blocked
curl -X POST http://localhost:8000/api/images/generate/ \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
# Expected: 401 or 403
```

- [ ] Unauthenticated API requests return 401/403
- [ ] Login endpoints still work without auth
- [ ] Health check endpoint accessible

### 1.3 CSRF Protection
```bash
# Test CSRF is enforced (should fail)
curl -X POST http://localhost:8000/api/assistant/chat/ \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=testsession" \
  -d '{"message": "test"}'
# Expected: 403 CSRF verification failed
```

- [ ] CSRF required on state-changing endpoints
- [ ] CSRF token properly passed from frontend

### 1.4 Input Validation
```bash
# Test injection attempt is blocked
curl -X POST http://localhost:8000/api/images/generate/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: [token]" \
  -H "Cookie: sessionid=[session]" \
  -d '{"prompt": "<script>alert(1)</script>"}'
# Expected: Sanitized or rejected
```

- [ ] XSS attempts sanitized
- [ ] Path traversal blocked
- [ ] SQL injection prevented
- [ ] eval() removed from agent system

### 1.5 Rate Limiting
```bash
# Test rate limiting (run rapidly)
for i in {1..20}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:8000/api/images/generate/ \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: [token]" \
    -H "Cookie: sessionid=[session]" \
    -d '{"prompt": "test"}'
done
# Expected: Eventually returns 429
```

- [ ] Rate limiting kicks in after threshold
- [ ] Different limits for different endpoints
- [ ] Retry-After header included in 429 responses

### 1.6 SSRF Protection
- [ ] URL downloads validate against allowlist
- [ ] Private IPs blocked
- [ ] Internal resources inaccessible

---

## 2. Functionality Verification

### 2.1 Image Generation
```bash
# Via UI or API
# Test: Generate an image with prompt "A sunset over mountains"
```
- [ ] Image generates successfully
- [ ] Image saved to database
- [ ] Image appears in project gallery
- [ ] Sequential number assigned

### 2.2 Image Operations
- [ ] Upscale works
- [ ] Background removal works
- [ ] Batch operations work
- [ ] Search & replace works

### 2.3 Video Generation
- [ ] Image-to-video works
- [ ] Video polling works
- [ ] Video appears in gallery
- [ ] Project association correct

### 2.4 Video Operations
- [ ] Video upscale works
- [ ] Color grading works
- [ ] Trim/concatenate works
- [ ] ffmpeg doesn't hang (timeout working)

### 2.5 Audio Generation
- [ ] Text-to-speech works
- [ ] Sound effects work
- [ ] Audio saved correctly

### 2.6 3D Model Generation
- [ ] Image-to-3D works
- [ ] GLB/STL export works
- [ ] Mesh repair works

### 2.7 AI Assistant
- [ ] Chat responds correctly
- [ ] Tool execution works
- [ ] Context maintained
- [ ] No debug prints in console

### 2.8 Project Management
- [ ] Create project works
- [ ] Delete project works
- [ ] Assets associate correctly
- [ ] Soft delete works

---

## 3. Error Handling Verification

### 3.1 User-Friendly Errors
```bash
# Test with invalid input
curl -X POST http://localhost:8000/api/images/generate/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: [token]" \
  -H "Cookie: sessionid=[session]" \
  -d '{}'
# Expected: Clear error message, not stack trace
```

- [ ] Missing fields return helpful message
- [ ] Invalid IDs return 404 with message
- [ ] Server errors don't expose internals

### 3.2 Error Logging
- [ ] Errors logged server-side with details
- [ ] Client receives generic message
- [ ] No sensitive data in logs

---

## 4. Performance Verification

### 4.1 Database Queries
```bash
# Enable query logging temporarily
# Check for N+1 queries on gallery pages
```
- [ ] Gallery loads without N+1 queries
- [ ] List views use select_related/prefetch_related

### 4.2 File Handling
- [ ] Temp files cleaned up after operations
- [ ] File handles properly closed
- [ ] No resource leaks

### 4.3 Timeouts
- [ ] ffmpeg operations timeout after limit
- [ ] API calls have timeouts
- [ ] No hung processes

---

## 5. Code Quality Verification

### 5.1 Linting
```bash
flake8 core/ content/ agents/ intelligence/
# Expected: No errors (or only acceptable warnings)
```
- [ ] No critical linting errors

### 5.2 Type Checking
```bash
mypy core/ --ignore-missing-imports
# Expected: No critical errors
```
- [ ] Type hints on public APIs

### 5.3 Django Checks
```bash
python manage.py check
python manage.py check --deploy
# Expected: No critical issues
```
- [ ] Django check passes
- [ ] Deploy check passes (or acceptable warnings)

---

## 6. Test Coverage Verification

### 6.1 Run All Tests
```bash
pytest --cov=core --cov=content --cov=agents --cov-report=html
# Open htmlcov/index.html
```

- [ ] All tests pass
- [ ] Coverage report generated

### 6.2 Coverage Targets
| Module | Target | Actual |
|--------|--------|--------|
| Models | 70% | ___% |
| Views | 60% | ___% |
| Agents | 70% | ___% |
| Providers | 70% | ___% |
| **Overall** | **70%** | **___%** |

- [ ] Overall coverage ≥ 70%
- [ ] No critical paths untested

---

## 7. Documentation Verification

- [ ] CLAUDE.md updated with changes
- [ ] API documentation current
- [ ] Architecture docs reflect new structure
- [ ] README current

---

## 8. Git & Deployment Verification

### 8.1 Git Status
```bash
git status
git log --oneline -10
```
- [ ] All changes committed
- [ ] Commit messages descriptive
- [ ] No sensitive data in history

### 8.2 Tags Created
```bash
git tag
```
- [ ] v1.0-security-phase1 (after Phase 1)
- [ ] v1.1-p1-fixes (after Phase 2)
- [ ] v1.2-architecture (after Phase 3)
- [ ] v2.0-remediated (after Phase 4)

### 8.3 Branch Status
- [ ] All work merged to main (or ready for PR)
- [ ] Feature branches cleaned up

---

## 9. Final Score Assessment

### Before Remediation
| Category | Score |
|----------|-------|
| Code Quality | 6.9/10 |
| Architecture | 7.3/10 |
| Security | 5.1/10 |
| Performance | 6.3/10 |
| Error Handling | 7.1/10 |
| Testing | 3.5/10 |
| **OVERALL** | **6.0/10** |

### After Remediation (Target)
| Category | Target | Actual |
|----------|--------|--------|
| Code Quality | 8.0/10 | ___/10 |
| Architecture | 8.5/10 | ___/10 |
| Security | 8.5/10 | ___/10 |
| Performance | 7.5/10 | ___/10 |
| Error Handling | 8.0/10 | ___/10 |
| Testing | 7.5/10 | ___/10 |
| **OVERALL** | **8.0/10** | **___/10** |

---

## 10. Sign-Off

### Verification Complete
- [ ] All security checks pass
- [ ] All functionality works
- [ ] All tests pass
- [ ] Coverage targets met
- [ ] Documentation updated

### Approved By
- **Reviewer:** _________________
- **Date:** _________________
- **Notes:** _________________

---

## Post-Remediation Actions

1. [ ] Schedule regular security reviews (quarterly)
2. [ ] Set up CI/CD with test gates
3. [ ] Configure automated dependency updates
4. [ ] Enable error monitoring (Sentry, etc.)
5. [ ] Set up performance monitoring
6. [ ] Plan production deployment

---

## Emergency Rollback

If critical issues discovered post-remediation:

```bash
# Rollback to pre-remediation state
git checkout [pre-remediation-commit]

# Or rollback specific phase
git checkout v1.0-security-phase1  # Just security fixes
```

Keep pre-remediation backup available for 30 days minimum.

---

**Congratulations on completing the code review remediation!** 🎉

The codebase should now be significantly more secure, maintainable, and testable.
