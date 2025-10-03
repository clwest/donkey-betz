# API Endpoint Fix Rollback Commands

## Quick Rollback (One-liners)

### 1. Revert APPEND_SLASH setting
```bash
# Remove the APPEND_SLASH = False line from settings.py
sed -i '' '/^# URL configuration - disable APPEND_SLASH/,+1d' backend/core/settings.py
```

### 2. Revert URL pattern changes
```bash
# Restore original assistant URL patterns
git checkout HEAD -- backend/api/urls.py
```

### 3. Revert rate limiting changes
```bash
# Remove assistant chat rate limit
git checkout HEAD -- backend/api/middleware/rate_limiting.py
```

## Full Rollback
```bash
# Revert all changes at once
git checkout HEAD -- backend/core/settings.py backend/api/urls.py backend/api/middleware/rate_limiting.py
```

## Alternative Quick Fix
If you prefer to keep APPEND_SLASH=True (default Django behavior):
```python
# In backend/core/settings.py, add:
APPEND_SLASH = True

# Then use only trailing slash URLs in all API calls:
# /api/assistant/chat/ (with slash)
```

## Emergency Disable
```bash
# Temporarily disable rate limiting if causing issues
echo "RATE_LIMITING_ENABLED = False" >> backend/core/settings.py
```