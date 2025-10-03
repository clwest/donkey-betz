# Section 9: Security & Authentication
**Agent Name: Security Auditor**

## Scope Overview
This section covers security implementations including authentication, authorization, data privacy, encryption, and overall security posture of the platform.

### Primary Directories:
- `backend/accounts/` - User management and authentication
- `backend/security/` - Security implementations
- `backend/api/accounts/` - Auth API endpoints
- Security middleware and settings

## Analysis Instructions for Claude Code Agent

### 1. Authentication System
**Investigate:**
- `backend/accounts/models/user.py` - User model
- `backend/accounts/auth/` - Auth backends
- `backend/api/accounts/views/auth_views.py` - Auth endpoints
- JWT token implementation

**Key Questions:**
- What auth methods exist?
- How are passwords hashed?
- How are tokens generated?
- What is the session management?

### 2. Authorization & Permissions
**Investigate:**
- Django permission system usage
- Custom permission classes
- `backend/*/permissions.py` - Permission implementations
- Role-based access control

**Key Questions:**
- What permission levels exist?
- How are permissions checked?
- What roles are defined?
- How is access controlled?

### 3. API Security
**Investigate:**
- `backend/server/middleware/security_middleware.py` - Security headers
- CORS configuration
- API authentication requirements
- Rate limiting implementation

**Key Questions:**
- What security headers are set?
- How is CORS configured?
- What endpoints require auth?
- How is rate limiting enforced?

### 4. Data Privacy & GDPR
**Investigate:**
- `backend/security/privacy/` - Privacy implementations
- `backend/security/services/pii_detector.py` - PII detection
- `backend/security/services/encryption_service.py` - Encryption
- User data controls

**Key Questions:**
- How is PII detected?
- What data is encrypted?
- How can users export data?
- What deletion options exist?

### 5. Encryption Implementation
**Investigate:**
- `backend/security/fields/encrypted_fields.py` - Encrypted fields
- Encryption key management
- Data at rest encryption
- TLS/SSL configuration

**Key Questions:**
- What is encrypted?
- How are keys managed?
- What algorithms are used?
- Is TLS enforced?

### 6. Input Validation & Sanitization
**Investigate:**
- Serializer validation
- SQL injection prevention
- XSS protection
- File upload validation

**Key Questions:**
- How is input validated?
- What sanitization exists?
- How are files validated?
- What size limits exist?

### 7. Secret Management
**Investigate:**
- Environment variable usage
- `backend/.env.example` - Required secrets
- API key storage
- Secret rotation procedures

**Key Questions:**
- Where are secrets stored?
- How are they accessed?
- What rotation exists?
- How are they protected?

### 8. Audit Logging
**Investigate:**
- `backend/security/models/audit_log.py` - Audit models
- `backend/security/services/audit_service.py` - Audit logging
- What actions are logged
- Log retention policies

**Key Questions:**
- What is audited?
- How long are logs kept?
- Who can access logs?
- What details are logged?

### 9. Security Monitoring
**Investigate:**
- Failed login tracking
- Suspicious activity detection
- Security alerts
- Incident response

**Key Questions:**
- What is monitored?
- How are threats detected?
- What alerts exist?
- What is the response plan?

### 10. Third-party Security
**Investigate:**
- Dependency scanning
- API key security
- OAuth implementations
- Webhook verification

**Key Questions:**
- How are deps scanned?
- How are APIs secured?
- What OAuth flows exist?
- How are webhooks verified?

## Critical Files to Review
1. `backend/accounts/auth/jwt_auth.py` - JWT implementation
2. `backend/security/services/encryption_service.py` - Encryption logic
3. `backend/security/middleware/security_middleware.py` - Security headers
4. `backend/security/services/pii_detector.py` - Privacy detection
5. `backend/server/settings/security.py` - Security settings

## Security Components
1. **Authentication** - JWT tokens, session management
2. **Authorization** - RBAC, Django permissions
3. **Encryption** - Field-level, at-rest encryption
4. **Privacy** - PII detection, GDPR compliance
5. **Audit** - Comprehensive logging
6. **Monitoring** - Threat detection
7. **Validation** - Input sanitization
8. **Headers** - Security headers, CORS

## Expected Outputs from Analysis
1. Security architecture diagram
2. Authentication flow chart
3. Permission matrix
4. Vulnerability assessment
5. GDPR compliance report
6. Encryption inventory
7. Secret management audit
8. Security recommendations

## Special Considerations
- JWT token expiration and refresh
- Password complexity requirements
- Two-factor authentication support
- Session fixation prevention
- CSRF protection status
- SQL injection risks
- XSS vulnerability scan
- Dependency vulnerabilities
- API key exposure risks
- Production security hardening