# Security Policy

## Supported Versions

We actively support the following versions of eThekwini GIS MCP:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please follow these guidelines:

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via:

1. **Email**: Send details to [bongiwemapipa82@gmail.com]
2. **Private Security Advisory**: Use GitHub's private vulnerability reporting feature

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish by exploiting this vulnerability?
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Affected Versions**: Which versions of the software are affected
- **Environment**: Operating system, Python version, and dependency versions
- **Proof of Concept**: If possible, provide a minimal proof of concept

### Response Timeline

- **Initial Response**: We will acknowledge receipt within 48 hours
- **Assessment**: We will assess the vulnerability within 5 business days
- **Resolution**: We aim to provide a fix within 30 days for critical vulnerabilities
- **Disclosure**: We will coordinate disclosure timing with the reporter

### Security Best Practices

When using eThekwini GIS MCP:

1. **Keep Dependencies Updated**: Regularly update MCP and HTTP client libraries
2. **Network Security**: Use HTTPS endpoints and validate SSL certificates
3. **Input Validation**: Validate all input parameters before sending to APIs
4. **Rate Limiting**: Implement appropriate rate limiting for API calls
5. **Logging**: Monitor logs for suspicious activity
6. **Access Control**: Limit server access to authorized applications only

### Known Security Considerations

- The server makes HTTP requests to external ArcGIS REST APIs
- All data accessed is from public municipal open data portals
- No authentication credentials are stored or transmitted
- The server operates in read-only mode with no write operations

### Security Updates

Security updates will be:

1. Released as patch versions (e.g., 1.0.1, 1.0.2)
2. Documented in the CHANGELOG.md
3. Announced via GitHub releases
4. Tagged with security labels in the release notes

### Bug Bounty

We do not currently offer a bug bounty program, but we greatly appreciate responsible disclosure and will acknowledge contributors in our security advisories.

Thank you for helping keep eThekwini GIS MCP secure!