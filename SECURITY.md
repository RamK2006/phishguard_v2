# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **security@phishguard.com**

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

### What to Include

Please include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-7 days
  - High: 7-30 days
  - Medium: 30-90 days
  - Low: 90+ days

## Security Measures

### Authentication & Authorization

- **Clerk JWT**: Industry-standard JWT tokens for user authentication
- **API Keys**: Secure API key validation for extension requests
- **Role-Based Access**: Granular permission system
- **Session Management**: Secure session handling with automatic expiration

### Data Protection

- **Encryption in Transit**: TLS 1.3 for all API communications
- **Encryption at Rest**: Database encryption for sensitive data
- **Password Hashing**: Bcrypt with salt for password storage
- **API Key Storage**: Encrypted storage of API keys
- **PII Protection**: Minimal collection and secure handling of personal data

### Input Validation

- **SQL Injection Prevention**: Parameterized queries via SQLAlchemy ORM
- **XSS Protection**: Input sanitization and output encoding
- **CSRF Protection**: CSRF tokens for state-changing operations
- **Request Validation**: Pydantic models for request validation
- **URL Validation**: Strict URL parsing and validation

### Infrastructure Security

- **Container Security**: Minimal base images, regular updates
- **Network Isolation**: Service isolation via Docker networks
- **Secrets Management**: Environment variables, no hardcoded secrets
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Configuration**: Strict CORS policy
- **Security Headers**: Comprehensive security headers

### Monitoring & Logging

- **Audit Logging**: All security-relevant events logged
- **Anomaly Detection**: Monitoring for suspicious patterns
- **Error Handling**: Secure error messages (no sensitive data leakage)
- **Log Retention**: Secure log storage with retention policies

### Dependency Management

- **Regular Updates**: Automated dependency updates
- **Vulnerability Scanning**: Regular security scans
- **License Compliance**: Open source license verification
- **Supply Chain Security**: Verified package sources

## Security Best Practices for Users

### API Keys

- Never commit API keys to version control
- Rotate API keys regularly (every 90 days)
- Use different keys for development and production
- Revoke compromised keys immediately

### Deployment

- Use HTTPS/TLS for all communications
- Keep all dependencies up to date
- Use strong passwords for database and services
- Enable firewall rules
- Implement network segmentation
- Regular security audits
- Backup encryption

### Development

- Follow secure coding guidelines
- Review code for security issues
- Run security scanners in CI/CD
- Use environment variables for secrets
- Implement least privilege principle
- Regular security training

## Known Security Considerations

### Threat Intelligence APIs

- External API calls may expose URLs being scanned
- Rate limits may affect availability
- API keys must be protected

### ML Model

- Model can be fooled by adversarial examples
- Regular retraining needed for new threats
- Model files should be integrity-checked

### Browser Extension

- Extension has broad permissions for URL scanning
- Users should review permissions before installing
- Extension communicates with backend API

## Compliance

PhishGuard is designed with the following standards in mind:

- **GDPR**: Data protection and privacy
- **CCPA**: California Consumer Privacy Act
- **OWASP Top 10**: Web application security
- **CWE Top 25**: Common weakness enumeration

## Security Updates

Security updates are released as soon as possible after a vulnerability is confirmed. Users are notified via:

- GitHub Security Advisories
- Email notifications (for registered users)
- Release notes
- Security mailing list

## Bug Bounty Program

We currently do not have a formal bug bounty program, but we appreciate responsible disclosure and will acknowledge security researchers in our release notes.

## Contact

For security concerns:
- Email: security@phishguard.com
- PGP Key: [Available on request]

For general questions:
- GitHub Issues: https://github.com/yourusername/phishguard/issues
- Email: support@phishguard.com

## Acknowledgments

We thank the following security researchers for responsible disclosure:
- [List will be updated as vulnerabilities are reported and fixed]

---

Last Updated: 15-05-2026
