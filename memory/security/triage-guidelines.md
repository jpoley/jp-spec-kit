# Security Triage Persona Guidelines

This document describes the three security triage persona variants and how to select the appropriate one for your needs.

## Overview

The security triage system provides three persona variants, each tailored to different expertise levels and use cases:

1. **Beginner** - Simple, educational explanations for developers new to security
2. **Expert** - Deep technical analysis for security professionals
3. **Compliance** - Regulatory mapping and audit evidence for compliance teams

## Persona Comparison

| Aspect | Beginner | Expert | Compliance |
|--------|----------|--------|------------|
| **Target Audience** | Junior developers, security novices | Security engineers, senior developers | Auditors, compliance teams, CISOs |
| **Language Style** | Simple, non-technical | Technical, assumes knowledge | Formal, regulatory |
| **Explanation Length** | <100 words | Detailed as needed | Structured, evidence-based |
| **Code Examples** | Basic before/after | Advanced exploitation techniques | Compliance-driven fixes |
| **Focus** | Learning and understanding | Exploitation and defense | Audit evidence and requirements |
| **References** | Beginner tutorials, OWASP basics | Research papers, CVEs, exploit DBs | Standards (PCI-DSS, SOC2, HIPAA) |

## When to Use Each Persona

### Use Beginner Mode When:
- Onboarding new developers to security practices
- Your team has limited security expertise
- You want to build security knowledge incrementally
- You need quick, actionable fixes without deep technical details
- You're explaining security issues to non-technical stakeholders

**Example Output (SQL Injection):**
```
What: Someone could trick your database into running bad commands.
Fix: Use the "?" placeholder instead of putting data directly in your query.
Learn more: https://owasp.org/www-community/attacks/SQL_Injection
```

### Use Expert Mode When:
- Your team has security expertise
- You need deep technical analysis of vulnerabilities
- You're performing penetration testing or red team exercises
- You need to understand advanced exploitation techniques
- You're designing security architectures and need to consider edge cases
- Performance implications of security controls matter

**Example Output (SQL Injection):**
```
What: CWE-89 SQL injection via unsanitized user input in prepared statement bypass.
Impact: Full database compromise, data exfiltration, privilege escalation.
Vector: POST /api/users?id=1' UNION SELECT * FROM credentials--
Exploitability: High - trivial exploit, public PoCs available
Fix: Use parameterized queries with bound parameters. For Django: User.objects.raw() with params.
Defense in Depth: WAF with SQL injection rules, least privilege DB user, query logging
```

### Use Compliance Mode When:
- Preparing for security audits (PCI-DSS, SOC2, HIPAA, ISO 27001)
- Collecting audit evidence
- Mapping findings to regulatory requirements
- Creating compliance gap analysis reports
- You need formal documentation for audit trails
- Working with QSAs, auditors, or compliance teams

**Example Output (SQL Injection):**
```
Finding: SQL Injection (CWE-89)
OWASP 2021: A03:2021 - Injection
PCI-DSS: Requirement 6.5.1 - Injection flaws
SOC2: CC7.1 - System monitoring to detect potential cyber threats
HIPAA: 164.308(a)(1)(ii)(D) - Information system activity review
Evidence: Source code at auth.py:42 shows string concatenation in SQL query
Compliance Status: Non-Compliant
Risk Rating: High
Required Remediation Timeframe: 7 days per critical vulnerability policy
Remediation: Implement parameterized queries per OWASP guidelines
Verification: Code review + re-scan + penetration test
Audit Note: Mark as non-compliant until remediated and verified
```

## Configuration

The persona is configured in your security configuration file (`.jpspec/security-config.yml`):

```yaml
triage:
  enabled: true
  persona: "expert"  # Options: "beginner", "expert", "compliance"
  confidence_threshold: 0.7
  auto_dismiss_fp: false
  cluster_similar: true
```

### Configuration Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `persona` | `beginner`, `expert`, `compliance` | `expert` | Triage output style |
| `confidence_threshold` | 0.0 - 1.0 | 0.7 | Minimum confidence for auto-classification |
| `auto_dismiss_fp` | `true`, `false` | `false` | Auto-dismiss low-confidence false positives |
| `cluster_similar` | `true`, `false` | `true` | Group related findings |

## Progressive Disclosure Pattern

The persona system implements progressive disclosure:

1. **Start with appropriate level** - Begin with the persona matching your team's expertise
2. **Reference other personas** - Each skill file cross-references others for more/less detail
3. **Learn and advance** - Beginners can graduate to expert mode as they gain experience
4. **Context switching** - Switch personas per project (compliance audit vs. feature dev)

## Persona Output Differences

### Finding Structure

All personas report the same finding structure, but with different detail levels:

**Beginner:**
- What (simple explanation)
- Why it matters (everyday terms)
- How to fix (step-by-step)
- Learn more (tutorial links)

**Expert:**
- Vulnerability analysis (CWE, CVSS, attack vector)
- Technical description (data flow, execution path)
- Exploitation analysis (PoC, prerequisites, known exploits)
- Remediation (immediate fix + defense in depth + performance)
- References (research, CVEs, exploit tools)

**Compliance:**
- Classification (CWE, OWASP, severity, CVSS)
- Regulatory impact (PCI-DSS, SOC2, HIPAA, ISO, GDPR)
- Evidence (location, discovery date, scanner)
- Compliance status (compliant/non-compliant, risk rating)
- Remediation (required actions, verification, responsible party, target date)
- Audit notes (control effectiveness, compensating controls, verification steps)

## Skill File Locations

Persona skills are implemented as Claude Code skills in:

```
.claude/skills/security-reviewer/
├── SKILL.md                           # Base security reviewer skill
├── security-triage-beginner.md        # Beginner persona
├── security-triage-expert.md          # Expert persona
└── security-triage-compliance.md      # Compliance persona
```

## Using Personas in Commands

Security triage commands should read the persona configuration and invoke the appropriate skill:

```markdown
# In .claude/commands/jpspec/security-triage.md

## Select Persona

Based on configuration in `.jpspec/security-config.yml`:

- If `persona: beginner` → Invoke `security-triage-beginner` skill
- If `persona: expert` → Invoke `security-triage-expert` skill
- If `persona: compliance` → Invoke `security-triage-compliance` skill
- If no persona specified → Default to `security-triage-expert`

## Invoke Skill

Use the selected persona skill to analyze findings and provide output in the appropriate format.
```

## Best Practices

### For Team Leads

1. **Assess team expertise** - Choose persona matching current skill level
2. **Plan progression** - Start beginner, move to expert as team learns
3. **Context matters** - Use compliance persona for audits, expert for daily work
4. **Document choices** - Record why you chose a particular persona

### For Individual Developers

1. **Be honest about expertise** - Using expert mode doesn't make you an expert
2. **Start simple** - Beginner mode helps build mental models
3. **Learn progressively** - Graduate to expert mode as you understand concepts
4. **Ask questions** - If expert mode is confusing, drop back to beginner

### For Security Teams

1. **Use expert mode** - Leverage technical depth and exploitation analysis
2. **Switch to compliance** - Use compliance mode for audit season
3. **Train developers** - Point them to beginner resources
4. **Review configurations** - Ensure teams use appropriate personas

### For Compliance Teams

1. **Default to compliance mode** - Structured for audit requirements
2. **Collect evidence** - Use formal audit evidence format
3. **Track remediation** - Monitor timeframes and verification steps
4. **Map requirements** - Connect findings to specific regulatory requirements

## Extending Personas

To add a new persona:

1. **Create skill file** - `.claude/skills/security-reviewer/security-triage-{name}.md`
2. **Follow pattern** - Use existing personas as templates
3. **Update config** - Add persona option to configuration schema
4. **Update commands** - Add persona selection logic to triage commands
5. **Document** - Add persona description to this file

## References

### Related Documentation
- [ADR-006: AI Triage Engine Design](../../docs/adr/ADR-006-ai-triage-engine-design.md)
- [Security Configuration Schema](../../docs/security/config-schema.yaml)
- [Security Commands Guide](../../docs/security/commands.md)

### Persona Skills
- [Beginner Persona](../../.claude/skills/security-reviewer/security-triage-beginner.md)
- [Expert Persona](../../.claude/skills/security-reviewer/security-triage-expert.md)
- [Compliance Persona](../../.claude/skills/security-reviewer/security-triage-compliance.md)

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [PCI-DSS](https://www.pcisecuritystandards.org/)
- [SOC2](https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/serviceorganization-smanagement.html)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [ISO 27001](https://www.iso.org/standard/27001)
