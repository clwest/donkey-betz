# SSL/TLS Configuration Documentation

## Overview

This document provides comprehensive guidance for SSL/TLS certificate configuration and management for the Donkey Betz platform. The implementation includes automated certificate generation, renewal, and monitoring using Let's Encrypt with Certbot.

## Architecture

### Components

1. **Nginx Reverse Proxy**: Handles SSL termination and security headers
2. **Let's Encrypt + Certbot**: Automated SSL certificate management
3. **Django Backend**: HTTPS security configuration and CORS
4. **Docker Compose**: Containerized SSL services
5. **Monitoring & Automation**: Scripts for renewal, testing, and monitoring

### SSL Flow

```
Internet -> Nginx (SSL Termination) -> Django Backend
```

## Initial Setup

### Prerequisites

- Domain name pointed to your server (A record for donkeybetz.com and www.donkeybetz.com)
- Docker and Docker Compose installed
- Ports 80 and 443 open on your server
- DNS propagation completed

### Environment Variables

Create or update `.env` file in the backend directory:

```bash
# SSL Configuration
SSL_DOMAIN=donkeybetz.com
SSL_EMAIL=admin@donkeybetz.com
SSL_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SSL_EMAIL_RECIPIENT=admin@donkeybetz.com
SSL_ALERT_DAYS=30

# Django HTTPS Settings
SECURE_SSL_REDIRECT=True
ALLOWED_HOSTS=localhost,127.0.0.1,donkeybetz.com,www.donkeybetz.com
ALLOWED_ORIGINS=https://donkeybetz.com,https://www.donkeybetz.com
```

### Step 1: Generate SSL Certificate

```bash
# Generate production certificate
./scripts/generate_ssl_cert.sh

# For testing, use staging server
./scripts/generate_ssl_cert.sh --staging

# With custom domain and email
./scripts/generate_ssl_cert.sh --domain yourdomain.com --email admin@yourdomain.com
```

### Step 2: Start Services

```bash
# Start all services including SSL
docker-compose --profile production up -d

# Verify services are running
docker-compose ps
```

### Step 3: Test SSL Configuration

```bash
# Run comprehensive SSL tests
./scripts/test_ssl.sh

# Test specific domain
./scripts/test_ssl.sh --domain yourdomain.com

# Verbose output
./scripts/test_ssl.sh --verbose
```

### Step 4: Setup Automation

```bash
# Setup automated renewal and monitoring
./scripts/setup_ssl_cron.sh

# This will:
# - Create cron jobs for renewal (twice daily)
# - Create cron jobs for monitoring (daily)
# - Setup log rotation
# - Create SSL management script
```

## Configuration Details

### Nginx Configuration

**Location**: `nginx/nginx.conf`

**Key Features**:
- HTTP to HTTPS redirect
- SSL/TLS 1.2 and 1.3 support
- Strong cipher suites
- OCSP stapling
- Security headers (HSTS, CSP, etc.)
- WebSocket over SSL (WSS)
- Development SSL port (8443)

**Security Headers**:
```nginx
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss:; object-src 'none'; base-uri 'self'; form-action 'self';" always;
```

### Django Configuration

**Location**: `backend/server/settings.py`

**HTTPS Settings**:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 63072000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

**CORS Configuration**:
```python
CORS_ALLOWED_ORIGINS = [
    "https://donkeybetz.com",
    "https://www.donkeybetz.com",
]

ALLOWED_HOSTS = [
    "donkeybetz.com",
    "www.donkeybetz.com",
]
```

### Docker Compose Configuration

**SSL Services**:
```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"
    - "8443:8443"  # Development SSL
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - ./certbot/conf:/etc/letsencrypt:ro
    - ./certbot/www:/var/www/certbot:ro
    - ./nginx/ssl:/etc/nginx/ssl:ro

certbot:
  image: certbot/certbot:latest
  volumes:
    - ./certbot/conf:/etc/letsencrypt
    - ./certbot/www:/var/www/certbot
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

## Certificate Management

### Manual Certificate Generation

```bash
# Generate new certificate
./scripts/generate_ssl_cert.sh

# Generate with custom settings
./scripts/generate_ssl_cert.sh \
  --domain yourdomain.com \
  --email admin@yourdomain.com \
  --staging

# Force renewal
./scripts/generate_ssl_cert.sh --force-renewal
```

### Automatic Renewal

**Setup**:
```bash
./scripts/setup_ssl_cron.sh
```

**Manual Renewal**:
```bash
# Test renewal (dry run)
./scripts/renew_ssl_cert.sh --dry-run

# Force renewal
./scripts/renew_ssl_cert.sh

# Renewal with custom settings
./scripts/renew_ssl_cert.sh \
  --domain yourdomain.com \
  --webhook https://hooks.slack.com/your/webhook
```

**Cron Jobs**:
- Renewal: `0 0,12 * * *` (twice daily)
- Monitoring: `0 8 * * *` (daily at 8 AM)

### Certificate Monitoring

```bash
# Check certificate status
./scripts/monitor_ssl_cert.sh

# Check specific aspects
./scripts/monitor_ssl_cert.sh --check expiry
./scripts/monitor_ssl_cert.sh --check chain
./scripts/monitor_ssl_cert.sh --check config
./scripts/monitor_ssl_cert.sh --check headers

# Generate monitoring report
./scripts/monitor_ssl_cert.sh --report
```

## SSL Management Script

**Location**: `scripts/ssl_manager.sh`

**Usage**:
```bash
# Show certificate status
./scripts/ssl_manager.sh status

# Generate new certificate
./scripts/ssl_manager.sh generate

# Renew certificate
./scripts/ssl_manager.sh renew

# Test SSL configuration
./scripts/ssl_manager.sh test

# Monitor certificate
./scripts/ssl_manager.sh monitor

# Show logs
./scripts/ssl_manager.sh logs
```

## Testing and Validation

### Local Testing

**Development SSL**:
```bash
# Access development site with self-signed cert
https://localhost:8443

# Generate self-signed certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/localhost.key \
  -out nginx/ssl/localhost.crt \
  -subj "/C=US/ST=Development/L=Local/O=Development/CN=localhost"
```

### Production Testing

**SSL Configuration Test**:
```bash
# Run comprehensive SSL tests
./scripts/test_ssl.sh

# Test with verbose output
./scripts/test_ssl.sh --verbose --output ssl-test-report.log
```

**Test Results**:
- SSL certificate validity
- Protocol support (TLS 1.2, 1.3)
- Security headers
- HTTPS redirect
- WebSocket over SSL
- Cipher suites
- Application endpoints

### SSL Labs Testing

**Online Testing**:
- Visit: https://www.ssllabs.com/ssltest/analyze.html?d=donkeybetz.com
- Target grade: A or A+

**API Testing**:
```bash
# Check SSL Labs grade
curl -s "https://api.ssllabs.com/api/v3/analyze?host=donkeybetz.com" | jq '.endpoints[0].grade'
```

## Monitoring and Alerting

### Log Files

**Locations**:
- Renewal logs: `/var/log/ssl-renewal.log`
- Monitor logs: `/var/log/ssl-monitor.log`
- Nginx logs: `/var/log/nginx/`

**Log Rotation**:
```bash
# Automatic rotation configured in /etc/logrotate.d/ssl-certificates
# Daily rotation, 30 days retention
```

### Notifications

**Webhook (Slack)**:
```bash
export SSL_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**Email**:
```bash
export SSL_EMAIL_RECIPIENT="admin@donkeybetz.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

### Alert Conditions

**Certificate Expiry**:
- 30 days: Warning
- 7 days: Urgent
- 0 days: Critical

**Other Alerts**:
- Chain validation failures
- Weak cipher detection
- Missing security headers
- HTTP not redirecting to HTTPS

## Troubleshooting

### Common Issues

**1. Certificate Generation Fails**

```bash
# Check DNS resolution
dig donkeybetz.com

# Check domain accessibility
curl -I http://donkeybetz.com

# Test with staging server
./scripts/generate_ssl_cert.sh --staging

# Check Docker logs
docker-compose logs certbot
```

**2. Certificate Not Loading**

```bash
# Check certificate files
ls -la ./certbot/conf/live/donkeybetz.com/

# Test Nginx configuration
docker-compose exec nginx nginx -t

# Reload Nginx
docker-compose exec nginx nginx -s reload
```

**3. HTTPS Not Working**

```bash
# Check port 443 is open
nc -z donkeybetz.com 443

# Check Nginx logs
docker-compose logs nginx

# Test SSL connection
openssl s_client -connect donkeybetz.com:443
```

**4. Certificate Renewal Fails**

```bash
# Check renewal dry run
./scripts/renew_ssl_cert.sh --dry-run

# Check certificate expiry
./scripts/monitor_ssl_cert.sh --check expiry

# Force renewal
./scripts/generate_ssl_cert.sh --force-renewal
```

### Debug Commands

```bash
# Check SSL certificate details
openssl x509 -in /path/to/certificate.crt -text -noout

# Test SSL connection
openssl s_client -servername donkeybetz.com -connect donkeybetz.com:443

# Check certificate chain
openssl s_client -showcerts -servername donkeybetz.com -connect donkeybetz.com:443

# Test specific TLS version
openssl s_client -tls1_2 -servername donkeybetz.com -connect donkeybetz.com:443
```

## Security Best Practices

### Certificate Security

1. **Strong Key Size**: Use 2048-bit RSA or 256-bit ECDSA
2. **Certificate Transparency**: Enabled by default with Let's Encrypt
3. **Key Rotation**: Regular certificate renewal (every 90 days)
4. **Secure Storage**: Protect private keys with proper permissions

### Configuration Security

1. **Disable Weak Protocols**: No SSL, TLS 1.0, TLS 1.1
2. **Strong Cipher Suites**: ECDHE with AES-GCM
3. **OCSP Stapling**: Enabled for performance and privacy
4. **Security Headers**: HSTS, CSP, and other protective headers

### Monitoring Security

1. **Certificate Expiry**: Monitor 30 days before expiry
2. **Chain Validation**: Regular validation of certificate chain
3. **Configuration Testing**: Automated SSL configuration testing
4. **Log Monitoring**: Review SSL-related logs regularly

## Performance Optimization

### SSL Performance

1. **Session Resumption**: SSL session caching enabled
2. **OCSP Stapling**: Reduces certificate validation overhead
3. **HTTP/2**: Enabled for improved performance
4. **Compression**: Gzip compression for text content

### Monitoring Performance

```bash
# Test SSL handshake time
curl -w "%{time_connect},%{time_appconnect},%{time_total}" -o /dev/null -s https://donkeybetz.com

# Monitor SSL performance
./scripts/test_ssl.sh --domain donkeybetz.com | grep "time"
```

## Production Deployment

### Pre-Deployment Checklist

- [ ] DNS records configured (A record for domain and www)
- [ ] Domain ownership verified
- [ ] Environment variables set
- [ ] SSL scripts tested
- [ ] Backup and recovery procedures in place

### Deployment Steps

1. **Setup Environment**:
   ```bash
   # Configure environment variables
   cp .env.example .env
   # Edit .env with your domain and email
   ```

2. **Generate Certificate**:
   ```bash
   ./scripts/generate_ssl_cert.sh
   ```

3. **Start Services**:
   ```bash
   docker-compose --profile production up -d
   ```

4. **Verify Configuration**:
   ```bash
   ./scripts/test_ssl.sh
   ```

5. **Setup Automation**:
   ```bash
   ./scripts/setup_ssl_cron.sh
   ```

6. **Monitor and Maintain**:
   ```bash
   ./scripts/ssl_manager.sh status
   ```

### Post-Deployment Monitoring

- Monitor certificate expiry dates
- Check SSL Labs grade monthly
- Review security headers quarterly
- Update SSL configuration as needed

## Maintenance and Updates

### Regular Tasks

**Daily**:
- Automated monitoring runs
- Log review (if alerts received)

**Weekly**:
- Review SSL monitoring reports
- Check certificate expiry status

**Monthly**:
- Run comprehensive SSL tests
- Review and update security headers
- Check SSL Labs grade

**Quarterly**:
- Review and update SSL configuration
- Update cipher suites if needed
- Review and update security policies

### Updates and Upgrades

1. **Nginx Updates**: Update Docker image and test configuration
2. **Certbot Updates**: Update to latest Certbot version
3. **Security Updates**: Apply security patches promptly
4. **Configuration Updates**: Review and update SSL settings

## Support and Resources

### Documentation

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Django HTTPS Settings](https://docs.djangoproject.com/en/stable/topics/security/#ssl-https)

### Testing Tools

- [SSL Labs Server Test](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [Cipherli.st](https://cipherli.st/)

### Emergency Contacts

- SSL Certificate Issues: admin@donkeybetz.com
- Infrastructure Issues: devops@donkeybetz.com
- Security Issues: security@donkeybetz.com

## Appendix

### Environment Variables Reference

```bash
# SSL Configuration
SSL_DOMAIN=donkeybetz.com              # Primary domain
SSL_EMAIL=admin@donkeybetz.com         # Let's Encrypt email
SSL_WEBHOOK_URL=https://hooks.slack.com/... # Webhook for notifications
SSL_EMAIL_RECIPIENT=admin@donkeybetz.com     # Email for alerts
SSL_ALERT_DAYS=30                      # Days before expiry to alert
SSL_LOG_FILE=/var/log/ssl-monitor.log  # Log file location

# SMTP Settings (for email notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Django Settings
SECURE_SSL_REDIRECT=True
ALLOWED_HOSTS=localhost,127.0.0.1,donkeybetz.com,www.donkeybetz.com
ALLOWED_ORIGINS=https://donkeybetz.com,https://www.donkeybetz.com
```

### Script Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `generate_ssl_cert.sh` | Generate SSL certificates | `./scripts/generate_ssl_cert.sh [options]` |
| `renew_ssl_cert.sh` | Renew SSL certificates | `./scripts/renew_ssl_cert.sh [options]` |
| `test_ssl.sh` | Test SSL configuration | `./scripts/test_ssl.sh [options]` |
| `monitor_ssl_cert.sh` | Monitor SSL certificates | `./scripts/monitor_ssl_cert.sh [options]` |
| `setup_ssl_cron.sh` | Setup automation | `./scripts/setup_ssl_cron.sh` |
| `ssl_manager.sh` | Unified SSL management | `./scripts/ssl_manager.sh [command]` |

### Common Error Codes

| Error | Description | Solution |
|-------|-------------|----------|
| `Connection refused` | Port 443 not open | Check firewall settings |
| `Certificate not found` | Certificate files missing | Regenerate certificate |
| `Nginx config test failed` | Configuration error | Check nginx.conf syntax |
| `DNS resolution failed` | Domain not resolving | Check DNS settings |
| `Rate limit exceeded` | Too many cert requests | Wait or use staging |

---

**Document Version**: 1.0  
**Last Updated**: July 2025  
**Next Review**: October 2025