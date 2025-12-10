# Security Documentation

Complete documentation for `/jpspec:security` security scanning features.

## Quick Links

| Document | Description | Audience |
|----------|-------------|----------|
| [Security Quickstart](../guides/security-quickstart.md) | 5-minute getting started guide | All developers |
| [Command Reference](../reference/jpspec-security-commands.md) | Complete CLI reference | All developers |
| [CI/CD Integration](../guides/security-cicd-integration.md) | Pipeline setup examples | DevOps engineers |
| [Custom Rules Guide](../guides/security-custom-rules.md) | Writing security rules | Security teams |
| [Threat Model](../reference/security-threat-model.md) | Security boundaries | Security architects |
| [Privacy Policy](../reference/security-privacy-policy.md) | Data handling | Compliance officers |

## Getting Started

### For Developers

1. Start with [Security Quickstart](../guides/security-quickstart.md)
2. Learn commands from [Command Reference](../reference/jpspec-security-commands.md)
3. Integrate into workflow with [Workflow Integration](../guides/security-workflow-integration.md)

### For DevOps Engineers

1. Review [CI/CD Integration Guide](../guides/security-cicd-integration.md)
2. Choose your platform (GitHub Actions, GitLab, Jenkins, etc.)
3. Copy and customize the example workflows

### For Security Teams

1. Understand [Threat Model](../reference/security-threat-model.md)
2. Review [Privacy Policy](../reference/security-privacy-policy.md) for compliance
3. Create [Custom Rules](../guides/security-custom-rules.md) for your organization

## Documentation Structure

```
docs/
├── guides/
│   ├── security-quickstart.md           # 5-minute tutorial
│   ├── security-cicd-integration.md     # CI/CD examples
│   ├── security-custom-rules.md         # Rule writing guide
│   ├── security-mcp-guide.md            # MCP server integration
│   └── security-workflow-integration.md # /jpspec workflow
├── reference/
│   ├── jpspec-security-commands.md      # CLI reference
│   ├── security-threat-model.md         # Security analysis
│   └── security-privacy-policy.md       # Privacy & compliance
└── security/
    ├── README.md                        # This file
    └── DOCUMENTATION-INDEX.md           # Complete index
```

## Key Features Documented

### Security Scanning
- Multiple scanner support (Semgrep, CodeQL, Bandit, Trivy)
- SARIF/JSON/Markdown output formats
- Incremental and full scan modes
- Configurable severity thresholds

### AI-Powered Triage
- Automatic True Positive (TP) / False Positive (FP) / Needs Investigation (NI) classification
- Confidence scoring
- Plain-English explanations
- Risk prioritization

### Fix Generation
- Automated security patches
- Dry-run preview mode
- Syntax validation
- Backup creation

### Audit Reports
- Executive summaries
- OWASP Top 10 mapping
- Compliance frameworks (SOC2, ISO27001, HIPAA)
- Multiple output formats

### CI/CD Integration
- GitHub Actions workflows
- GitLab CI pipelines
- Jenkins pipelines
- Azure DevOps
- CircleCI
- Pre-commit hooks

## Compliance Coverage

| Framework | Documentation | Status |
|-----------|---------------|--------|
| OWASP Top 10 | ✅ Mapped in all reports | Complete |
| SOC2 | ✅ Covered in Privacy Policy | Complete |
| ISO27001 | ✅ Covered in Threat Model | Complete |
| HIPAA | ✅ Covered in Privacy Policy | Complete |
| PCI-DSS | ✅ Covered in Privacy Policy | Complete |
| GDPR | ✅ Covered in Privacy Policy | Complete |

## Tool Support

| Scanner | Language Support | Documentation Status |
|---------|------------------|---------------------|
| Semgrep | Python, JS, Go, Java, Ruby, PHP | ✅ Complete |
| CodeQL | Python, JS, Go, Java, C++ | ✅ Complete |
| Bandit | Python | ✅ Complete |
| Trivy | Containers, IaC | ✅ Complete |

## Example Workflows

### Development Workflow
```bash
# 1. Run scan before commit
specify security scan --quick --fail-on critical

# 2. Triage findings (Phase 2)
specify security triage results.json --interactive

# 3. Apply fixes (Phase 2)
specify security fix results.json --apply --backup

# 4. Generate report
specify security audit results.json --format markdown
```

### CI/CD Workflow
```yaml
# GitHub Actions example
- name: Security Scan
  run: specify security scan --format sarif --output results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

## Common Use Cases

1. **Pre-commit scanning**: Catch vulnerabilities before they're committed
2. **PR security gates**: Block merges with critical findings
3. **Scheduled audits**: Regular security posture assessments
4. **Compliance reporting**: Generate audit-ready security reports
5. **Custom rule enforcement**: Organization-specific security policies

## Support & Resources

- **Issues**: Report bugs or request features on GitHub
- **Discussions**: Ask questions in GitHub Discussions
- **Updates**: Check release notes for new features
- **Examples**: See CI/CD integration guide for working examples

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-05 | Initial comprehensive documentation |

## Contributing

To improve security documentation:

1. Identify gaps or inaccuracies
2. Propose changes via pull request
3. Update cross-references
4. Test all code examples
5. Update DOCUMENTATION-INDEX.md

## Related Documentation

- [JP Spec Kit Documentation](../../README.md)
- [Workflow Guide](../guides/workflow-architecture.md)
- [Agent Classification](../reference/agent-loop-classification.md)

---

**Questions?** Check the [Command Reference](../reference/jpspec-security-commands.md) or open an issue.
