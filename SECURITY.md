# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of flowspec seriously. If you believe you have found a security vulnerability, please report it to us through coordinated disclosure.

**Please do not report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

### Reporting Process

1. **Private Disclosure**: Use [GitHub's private vulnerability reporting](https://github.com/jpoley/flowspec/security/advisories/new) to submit security issues confidentially.

2. **Email**: Alternatively, send an email with details to the project maintainer.

### What to Include

Please provide as much information as possible:

- **Type of issue** (e.g., command injection, path traversal, credential exposure)
- **Full paths** of affected source files
- **Location** of vulnerable code (tag/branch/commit or direct URL)
- **Configuration** required to reproduce
- **Step-by-step instructions** to reproduce
- **Proof-of-concept** or exploit code (if possible)
- **Impact assessment** including potential attack scenarios

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days for critical issues

### Security Update Process

1. Security fixes are developed in private
2. A fix is tested and verified
3. A new release is published with CVE details (if applicable)
4. Public disclosure after fix is available

## Security Best Practices

When using flowspec:

- Keep flowspec updated to the latest version
- Review generated templates before committing to production
- Use environment variables for sensitive configuration
- Follow the principle of least privilege for CI/CD tokens
- Regularly audit your `.github/` configuration

## OpenSSF Scorecard

This project is monitored by [OpenSSF Scorecard](https://scorecard.dev/viewer/?uri=github.com/jpoley/flowspec) for security best practices. View our current score and security posture in the README badge.

## Acknowledgments

We appreciate responsible disclosure from the security community. Contributors who report valid security issues will be acknowledged in our release notes (with your permission).
