# Security & Privacy Framework

This directory contains the comprehensive privacy and security framework for the Donkey Betz platform.

## 🎯 Overview

The security framework provides:
- **Data Encryption**: Field-level encryption for sensitive data at rest
- **PII Detection**: Automatic detection and anonymization of personally identifiable information
- **User Consent**: Granular privacy controls and consent management
- **Audit Logging**: Complete audit trail of all data processing activities
- **API Security**: Rate limiting, security headers, and request validation
- **Data Export**: GDPR/CCPA compliant data export functionality
- **Account Deletion**: User-controlled account and data deletion

## 🏗️ Architecture

### Core Components

1. **Encryption Service** (`encryption.py`)
   - Handles encryption/decryption of sensitive data
   - Uses Fernet symmetric encryption
   - Provides encrypted Django field types

2. **PII Detection** (`pii_detection.py`)
   - Detects personally identifiable information in text
   - Supports anonymization with configurable levels
   - Calculates PII sensitivity scores

3. **API Anonymization** (`api_anonymization.py`)
   - Anonymizes data before sending to external APIs
   - Caches mappings for deanonymization of responses
   - Supports different anonymization levels per API provider

4. **Privacy Models** (`models.py`)
   - `UserPrivacySettings`: User privacy preferences and consent
   - `DataProcessingAuditLog`: Audit trail of all data processing
   - `PIIDetectionLog`: PII detection events
   - `PrivacyNotification`: Privacy-related notifications

5. **Security Middleware** (`middleware.py`)
   - Security headers (CSP, HSTS, etc.)
   - API rate limiting
   - Request validation and filtering
   - Privacy audit logging

6. **API Views** (`views.py`)
   - Privacy settings management
   - Data export functionality
   - Account deletion requests
   - Dashboard statistics

## 🔧 Configuration

### Environment Variables

```bash
# Required
ENCRYPTION_KEY="your-encryption-key-here"

# Optional
PRIVACY_CONFIG='{
  "pii_detection_enabled": true,
  "api_anonymization_default": true,
  "audit_retention_days": 90
}'
```

### Django Settings

The framework integrates with Django settings:

```python
# Privacy configuration
PRIVACY_CONFIG = {
    'pii_detection_enabled': True,
    'api_anonymization_default': True,
    'audit_retention_days': 90,
    'gdpr_enabled': True,
    'ccpa_enabled': True,
}

# Security middleware
MIDDLEWARE = [
    'security.middleware.SecurityHeadersMiddleware',
    'security.middleware.APIRateLimitMiddleware',
    'security.middleware.APISecurityMiddleware',
    'security.middleware.PrivacyAuditMiddleware',
    # ... other middleware
]
```

## 🚀 Usage

### 1. Encryption

```python
from security.fields import EncryptedTextField, EncryptedJSONField
from security.encryption import get_encryption_service

class MyModel(models.Model):
    sensitive_data = EncryptedTextField()
    encrypted_json = EncryptedJSONField()

# Manual encryption
encryption_service = get_encryption_service()
encrypted = encryption_service.encrypt("sensitive text")
decrypted = encryption_service.decrypt(encrypted)
```

### 2. PII Detection

```python
from security.pii_detection import get_pii_detector

detector = get_pii_detector()

# Detect PII
pii_found = detector.detect_pii("My email is john@example.com")
# Returns: {'email': ['john@example.com']}

# Anonymize text
anonymized, mapping = detector.anonymize_text("My email is john@example.com")
# Returns: ("My email is [EMAIL_0]", {"[EMAIL_0]": "john@example.com"})

# Check if anonymization is needed
should_anonymize = detector.should_anonymize(text, user_preference='sensitive')
```

### 3. API Anonymization

```python
from security.api_anonymization import get_anonymization_middleware

middleware = get_anonymization_middleware()

# Anonymize before API call
anonymized = middleware.anonymize_for_api(text, user_id, 'sensitive')

# Deanonymize API response
original = middleware.deanonymize_response(response, original_text, user_id)
```

### 4. Privacy Settings

```python
from security.models import UserPrivacySettings

# Get or create privacy settings
settings, created = UserPrivacySettings.objects.get_or_create(user=user)

# Check consent
if settings.api_processing_consent:
    # OK to send to APIs
    pass

# Log data processing
from security.models import DataProcessingAuditLog
DataProcessingAuditLog.objects.create(
    user=user,
    action='api_call',
    api_provider='openai',
    data_anonymized=True,
    details={'model': 'gpt-4'}
)
```

## 🔒 Security Features

### 1. Data Protection
- **Encryption at Rest**: Sensitive fields encrypted in database
- **PII Detection**: Automatic detection of personal information
- **Anonymization**: Configurable data anonymization before API calls
- **Secure Deletion**: Cryptographic erasure of encrypted data

### 2. Access Control
- **Rate Limiting**: Per-user and per-endpoint rate limits
- **Request Validation**: Automatic filtering of malicious requests
- **Security Headers**: Comprehensive security headers (CSP, HSTS, etc.)
- **CSRF Protection**: Enhanced CSRF protection for forms

### 3. Audit & Compliance
- **Complete Audit Trail**: All data processing activities logged
- **Data Export**: GDPR/CCPA compliant data export
- **Right to Erasure**: User-controlled account deletion
- **Consent Management**: Granular consent tracking

## 📊 Compliance

### GDPR Compliance
- ✅ **Right to Access**: Data export functionality
- ✅ **Right to Rectification**: Profile editing capabilities
- ✅ **Right to Erasure**: Account deletion with 30-day grace period
- ✅ **Right to Portability**: JSON data export
- ✅ **Right to Object**: Opt-out controls for data processing
- ✅ **Data Minimization**: PII detection and anonymization
- ✅ **Consent**: Explicit consent for API processing
- ✅ **Accountability**: Comprehensive audit logging

### CCPA Compliance
- ✅ **Right to Know**: Data export shows what data is collected
- ✅ **Right to Delete**: Account deletion functionality
- ✅ **Right to Opt-Out**: Privacy preference controls
- ✅ **Non-Discrimination**: No service degradation for privacy choices

## 🧪 Testing

### Compliance Check
```bash
python manage.py check_compliance
```

### Manual Testing
```python
# Test encryption
from security.encryption import get_encryption_service
service = get_encryption_service()
encrypted = service.encrypt("test")
assert service.decrypt(encrypted) == "test"

# Test PII detection
from security.pii_detection import get_pii_detector
detector = get_pii_detector()
result = detector.detect_pii("Contact me at test@example.com")
assert 'email' in result
```

## 🚨 Security Considerations

### Encryption Key Management
- **Never commit encryption keys** to version control
- **Use different keys** for different environments
- **Backup encryption keys** securely
- **Rotate keys periodically** (requires data re-encryption)

### Rate Limiting
- **Monitor rate limit violations** for abuse patterns
- **Adjust limits** based on usage patterns
- **Consider user tiers** for different rate limits

### Audit Log Retention
- **Configure retention period** based on compliance requirements
- **Archive old logs** to reduce database size
- **Monitor log volume** for storage planning

## 🔧 Maintenance

### Key Rotation
```bash
# Generate new key
python manage.py generate_encryption_key

# Update environment variable
# Re-encrypt existing data (manual process)
```

### Audit Log Cleanup
```bash
# Clean up old audit logs
python manage.py cleanup_audit_logs --days 90
```

### Privacy Settings Migration
```bash
# Migrate privacy settings for existing users
python manage.py migrate_privacy_settings
```

## 📚 Related Documentation

- [GDPR Compliance Guide](gdpr-compliance.md)
- [API Security Best Practices](api-security.md)
- [Encryption Key Management](encryption-guide.md)
- [Privacy by Design Principles](privacy-by-design.md)

## 🆘 Support

For security-related issues:
1. **Security Vulnerabilities**: Report immediately to security team
2. **Privacy Questions**: Refer to privacy policy and this documentation
3. **Implementation Issues**: Check compliance status with `check_compliance` command

## 📄 License

This security framework is part of the Donkey Betz platform and follows the same licensing terms.