# CodeQL Licensing Review

## Overview

This document provides a comprehensive review of GitHub CodeQL licensing terms to help teams determine when CodeQL can be used freely versus when a commercial license is required.

**Last Updated**: 2025-12-04
**Review Status**: Initial Analysis - Requires Legal Verification

## Important Legal Disclaimer

**This document provides general guidance only and does not constitute legal advice.** Always consult with your organization's legal team before using CodeQL in a commercial setting. GitHub's licensing terms may change, and this document may not reflect the most current terms.

## CodeQL Licensing Structure

CodeQL has two main licensing components:

1. **CodeQL CLI** - The command-line tool for running queries
2. **CodeQL Query Packs** - The security queries that detect vulnerabilities

### CodeQL CLI License

The CodeQL CLI is available under GitHub's [CodeQL Terms and Conditions](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md).

**Free Use Cases** (as of 2025-12-04):
- Open source projects (OSI-approved licenses)
- Academic research
- Security research on your own code
- Personal projects

**Restricted Use Cases** (may require GitHub Advanced Security license):
- Commercial software development
- Automated security scanning in CI/CD pipelines
- Integration with commercial SAST tools
- Scanning proprietary codebases at scale

### CodeQL Query Packs License

Most CodeQL query packs are released under the MIT License, which is permissive for commercial use. However, using them with the CodeQL CLI in a commercial context may still fall under the CLI's licensing restrictions.

## When CodeQL Is Free

### 1. Open Source Projects

**Qualifying Criteria**:
- Project uses an OSI-approved open source license
- Repository is publicly accessible
- Code is freely available for inspection

**Example Use Cases**:
```bash
# Scanning an MIT-licensed project on GitHub
codeql database create --language=python mydb --source-root=.
codeql database analyze mydb --format=sarif-latest --output=results.sarif
```

**Verification**:
- Check your project's LICENSE file
- Verify it matches an [OSI-approved license](https://opensource.org/licenses/)
- Ensure repository is public

### 2. Academic and Research Use

**Qualifying Criteria**:
- Use for educational purposes
- Non-commercial research
- Academic publications

**Example Use Cases**:
- University course assignments
- PhD research on code analysis
- Publishing security research papers

### 3. Security Research

**Qualifying Criteria**:
- Analyzing your own code or systems
- Responsible disclosure of vulnerabilities
- Non-commercial security testing

**Example Use Cases**:
- Bug bounty programs (on authorized targets)
- Personal security audits
- CVE research and disclosure

## When CodeQL Requires a License

### 1. Commercial Software Development

If you're developing proprietary software for commercial purposes, you likely need GitHub Advanced Security (GHAS).

**Indicators You Need a License**:
- Closed-source codebase
- Commercial product or service
- For-profit organization
- Internal security scanning at scale

**Cost Structure** (as of 2025-12-04):
- Included with GitHub Enterprise Cloud
- GitHub Advanced Security add-on required
- Pricing based on active committers
- Contact GitHub Sales for pricing

### 2. CI/CD Integration

**Automated Scanning Restrictions**:
- Continuous integration pipelines
- Pre-commit hooks with CodeQL
- Automated pull request scanning
- Scheduled security scans

**Why It's Restricted**:
GitHub's licensing terms generally require GHAS for automated scanning in commercial contexts, even if individual scans would be free.

### 3. Third-Party Commercial Tools

**Restricted Integrations**:
- Embedding CodeQL in a commercial SAST product
- Offering CodeQL scanning as a service
- Reselling CodeQL capabilities
- White-labeling CodeQL analysis

**Compliance Requirements**:
- Contact GitHub for redistribution rights
- May require special partnership agreements
- Enterprise licensing typically required

## GitHub Advanced Security (GHAS)

### What's Included

GHAS provides:
- Unlimited CodeQL scanning
- Secret scanning
- Dependency review
- Security advisories
- GitHub Security Lab support

### Pricing Model

**Per Active Committer**:
- Count of unique committers in the last 90 days
- Across all repositories with GHAS enabled
- Billed monthly or annually

**Example Calculation**:
```
Organization with 50 active committers:
- 50 committers × $49/committer/month = $2,450/month
- Annual: ~$29,400/year

(Pricing is approximate and subject to change)
```

### When GHAS Is Required

You need GHAS for:
- Private repositories (commercial use)
- Automated scanning in CI/CD
- Enterprise-scale security programs
- Integration with GitHub Security features

## Alternatives for Restricted Scenarios

If CodeQL licensing doesn't fit your use case, consider these alternatives:

### 1. Semgrep

**License**: LGPL 2.1 (open source)
**Pros**:
- Permissive licensing for commercial use
- Simpler query language (YAML-based)
- Fast scanning performance
- No GitHub dependency

**Cons**:
- Less sophisticated dataflow analysis
- Smaller query library
- May miss complex vulnerabilities

**Integration with jp-spec-kit**:
```bash
specify security scan --scanner semgrep
```

### 2. Bandit (Python)

**License**: Apache 2.0
**Pros**:
- Free for all uses
- Python-specific
- Fast and lightweight

**Cons**:
- Python only
- Limited dataflow analysis
- High false positive rate

### 3. SonarQube Community Edition

**License**: LGPL 3.0
**Pros**:
- Free community edition
- Multi-language support
- Quality + security analysis

**Cons**:
- Community edition limited
- Enterprise features require license
- Self-hosted infrastructure required

### 4. Commercial SAST Alternatives

For organizations requiring advanced features:
- **Snyk Code** - Developer-first SAST
- **Checkmarx** - Enterprise SAST platform
- **Veracode** - Application security platform
- **Fortify** - Mature SAST solution

## Recommended Approach for jp-spec-kit

### For Open Source Projects

**Recommended**: Use CodeQL with standard queries

```bash
# Install CodeQL CLI
./scripts/setup-codeql.sh

# Run scan
specify security scan --scanner codeql --language python

# Results integrated into UFFormat
cat docs/security/findings.json
```

### For Commercial Projects

**Recommended Decision Tree**:

1. **Have GitHub Enterprise with GHAS?**
   - Yes → Use CodeQL (licensed)
   - No → Continue to step 2

2. **Need advanced dataflow analysis?**
   - Yes → Purchase GHAS or use commercial SAST
   - No → Use Semgrep (free)

3. **Budget for security tools?**
   - Yes → Consider Snyk, Checkmarx, etc.
   - No → Use Semgrep + manual review

### Hybrid Approach

**Recommended for Most Teams**:

```yaml
# .flowspec/security-config.yml
scanners:
  - name: semgrep
    enabled: true
    # Free for all uses

  - name: codeql
    enabled: false
    # Enable if licensed or open source

  - name: bandit
    enabled: true
    languages: [python]
    # Free supplement for Python
```

## Compliance Checklist

Before using CodeQL in production:

- [ ] Review [GitHub CodeQL Terms](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md)
- [ ] Determine if your use case is commercial
- [ ] Check if you have GitHub Advanced Security
- [ ] Verify open source license (if applicable)
- [ ] Consult with legal team for commercial use
- [ ] Document licensing decision in project
- [ ] Set up license compliance monitoring

## References

### Official Documentation

- [CodeQL CLI Binaries License](https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md)
- [GitHub Advanced Security](https://docs.github.com/en/get-started/learning-about-github/about-github-advanced-security)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [GitHub Pricing](https://github.com/pricing)

### Legal Resources

- [OSI Approved Licenses](https://opensource.org/licenses/)
- [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
- [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)

### Community Discussions

- [CodeQL Licensing on GitHub Community](https://github.community/c/code-security/)
- [Stack Overflow: CodeQL Licensing Questions](https://stackoverflow.com/questions/tagged/codeql)

## Getting Legal Approval

### Information to Provide Legal Team

When requesting approval to use CodeQL:

1. **Project Details**:
   - Is this open source or proprietary?
   - What license does the project use?
   - Is the repository public or private?

2. **Usage Pattern**:
   - Manual scans vs. automated CI/CD?
   - How many developers will use it?
   - Integration with other tools?

3. **GitHub Status**:
   - Do we have GitHub Enterprise?
   - Do we have Advanced Security enabled?
   - What's our current GitHub plan?

4. **Alternatives Considered**:
   - Why CodeQL over Semgrep/alternatives?
   - What features require CodeQL specifically?
   - Cost-benefit analysis?

### Sample Legal Request Template

```markdown
Subject: Legal Review Request - CodeQL Usage

We are evaluating GitHub CodeQL for security scanning in [PROJECT_NAME].

**Project Details**:
- Type: [Open Source / Proprietary]
- License: [MIT / Proprietary / etc.]
- Repository: [Public / Private]

**Intended Usage**:
- Automated CI/CD scanning: [Yes / No]
- Number of developers: [X]
- Integration method: [CLI / GitHub Actions / etc.]

**Current GitHub Status**:
- Plan: [Free / Team / Enterprise]
- Advanced Security: [Yes / No]

**Questions for Legal**:
1. Can we use CodeQL under our current GitHub plan?
2. Do we need to purchase GitHub Advanced Security?
3. Are there any compliance concerns?
4. Should we use an alternative tool instead?

Please advise on legal compliance and next steps.
```

## Conclusion

CodeQL is a powerful tool for semantic code analysis, but its licensing requires careful consideration:

- **Open source projects**: Generally free to use
- **Commercial projects**: Likely requires GitHub Advanced Security
- **Alternative**: Semgrep offers similar capabilities with permissive licensing

**Final Recommendation**: Always verify current licensing terms with GitHub and consult your legal team before deploying CodeQL in production.

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-12-04 | Initial licensing review | AI Security Team |

---

**Note**: This document reflects licensing terms as of 2025-12-04. GitHub may update terms at any time. Always verify current terms at https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md
