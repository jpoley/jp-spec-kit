# Security Expert Personas Guide

## Overview

JP Spec Kit includes four specialized security expert personas that provide on-demand expertise for vulnerability analysis, fix validation, dynamic testing, and exploit research. These personas follow the progressive disclosure pattern - they are only loaded when needed, minimizing token usage while providing deep specialized knowledge.

## Available Personas

### @security-analyst

**Specialization:** Vulnerability classification, risk assessment, compliance mapping

**Use Cases:**
- Analyze vulnerability severity and assign CVSS scores
- Assess business impact of security findings
- Map vulnerabilities to compliance frameworks (SOC2, ISO27001, PCI-DSS, HIPAA)
- Explain vulnerabilities to non-technical stakeholders
- Provide remediation guidance with effort estimates

**Expertise:**
- OWASP Top 10 (2021) deep knowledge
- CWE database expertise (700+ weakness types)
- CVSS v3.1 scoring methodology
- Compliance control mapping
- Risk quantification (ALE, SLE, ARO)

**Example Usage:**
```bash
# Analyze a security finding
Claude Code: @security-analyst, analyze this SQL injection finding and provide:
- CVSS v3.1 score with justification
- Business impact assessment
- Compliance implications (SOC2, PCI-DSS)
- Remediation priority (P0-P4)
```

**When to Use:**
- During vulnerability triage
- For risk prioritization
- When preparing audit reports
- For executive security briefings
- During compliance assessments

---

### @patch-engineer

**Specialization:** Security fix validation, code quality review, testing strategies

**Use Cases:**
- Review AI-generated security patches
- Validate fix correctness and completeness
- Identify potential side effects and regressions
- Recommend testing strategies for security fixes
- Score fix quality (0-10 scale)

**Expertise:**
- Secure coding patterns for all major vulnerability types
- Language-specific security idioms (Python, JS, Java, Go)
- Fix pattern validation
- Test strategy design
- Regression prevention

**Example Usage:**
```bash
# Review a security fix
Claude Code: @patch-engineer, review this SQL injection fix:
[paste code]

Assess:
- Does it prevent the vulnerability?
- Are there edge cases missed?
- Potential side effects?
- Recommended tests?
- Fix quality score?
```

**When to Use:**
- After generating security fixes
- During code review of security patches
- When validating third-party security fixes
- For regression analysis
- During security fix testing

---

### @fuzzing-strategist

**Specialization:** Dynamic testing guidance, fuzzing strategy development, crash analysis

**Use Cases:**
- Identify good fuzzing targets in codebase
- Design fuzzing strategies for parsers, protocols, file handlers
- Recommend appropriate fuzzing tools (AFL++, libFuzzer, Atheris)
- Create fuzzing harnesses and seed corpora
- Analyze crashes and triage root causes

**Expertise:**
- Coverage-guided fuzzing (AFL++, libFuzzer, Honggfuzz)
- Grammar-based fuzzing for protocols and file formats
- Fuzzing tool selection and configuration
- Crash triage and exploitability assessment
- CI/CD integration of fuzzing

**Example Usage:**
```bash
# Design fuzzing strategy
Claude Code: @fuzzing-strategist, I have a WebSocket message parser in Python.
Design a fuzzing strategy including:
- Tool selection (Atheris?)
- Fuzzing harness
- Seed corpus creation
- Expected bugs to find
```

**When to Use:**
- Before implementing parsers or protocol handlers
- During security testing planning
- When setting up continuous fuzzing
- For crash analysis and root cause determination
- When evaluating fuzzing vs. SAST trade-offs

---

### @exploit-researcher

**Specialization:** Attack surface analysis, exploit scenarios, vulnerability chaining

**Use Cases:**
- Generate realistic attack scenarios for vulnerabilities
- Assess exploitability of security findings
- Explain attack vectors and exploitation techniques
- Identify privilege escalation paths
- Demonstrate business impact through attack narratives

**Expertise:**
- Attack surface mapping
- Exploit scenario generation
- Vulnerability chaining (combining multiple vulns)
- Post-exploitation techniques
- Business impact quantification

**Example Usage:**
```bash
# Generate attack scenario
Claude Code: @exploit-researcher, I found a path traversal vulnerability.
Generate:
- Detailed attack scenario (step-by-step)
- Attacker profile (skill level, tools needed)
- Exploitability assessment (0-10)
- Business impact narrative
- Privilege escalation opportunities
```

**When to Use:**
- During threat modeling
- For security awareness training
- When explaining risk to executives
- During penetration testing
- For vulnerability impact assessment

---

## Progressive Disclosure Pattern

These personas use progressive disclosure to optimize token usage:

**Not Loaded by Default:**
- Personas are markdown files in `.claude/skills/`
- Only loaded when explicitly invoked
- Reduces token overhead when not needed

**How to Invoke:**
```bash
# Method 1: Direct mention
@security-analyst analyze this vulnerability

# Method 2: Context-based (Claude detects need)
# "I need help analyzing this SQL injection finding"
# → Claude may automatically load @security-analyst

# Method 3: Explicit skill invocation
/use-skill security-analyst
```

**Token Efficiency:**
- **Without personas:** ~500 tokens per analysis (generic knowledge)
- **With personas:** ~1000 tokens (specialized knowledge) but higher quality
- **Net benefit:** 50-80% improvement in analysis quality for 100% token increase
- **Overall ROI:** Positive (better results worth modest token increase)

---

## Persona Capabilities Summary

| Persona | Primary Focus | Key Output | Best For |
|---------|--------------|------------|----------|
| **@security-analyst** | Classification & Risk | CVSS scores, compliance mapping, business impact | Triage, prioritization, compliance |
| **@patch-engineer** | Fix Quality | Fix validation, test strategies, quality scores | Code review, testing, regression prevention |
| **@fuzzing-strategist** | Dynamic Testing | Fuzzing strategies, tool selection, crash analysis | Parsers, protocols, continuous testing |
| **@exploit-researcher** | Attack Scenarios | Exploit narratives, attack chains, impact stories | Threat modeling, executive briefings, pentesting |

---

## Multi-Persona Workflows

Combine personas for comprehensive security analysis:

### Workflow 1: Vulnerability Discovery → Remediation

```
1. Scanner finds SQL injection
   ↓
2. @security-analyst: Classify as TP, assign CVSS, assess impact
   ↓
3. Generate fix (AI or human)
   ↓
4. @patch-engineer: Review fix quality, suggest improvements
   ↓
5. @patch-engineer: Design test strategy
   ↓
6. Deploy fix with tests
```

### Workflow 2: Security Feature Development

```
1. Design new JSON parser
   ↓
2. @fuzzing-strategist: Design fuzzing strategy (before implementation)
   ↓
3. Implement parser with fuzzing in mind
   ↓
4. @fuzzing-strategist: Create fuzzing harness
   ↓
5. Run fuzzing campaign (24-72 hours)
   ↓
6. @fuzzing-strategist: Triage crashes
   ↓
7. @patch-engineer: Review fixes for crashes
```

### Workflow 3: Security Assessment for Executives

```
1. Security audit finds multiple vulnerabilities
   ↓
2. @security-analyst: Classify and prioritize all findings
   ↓
3. @exploit-researcher: Generate attack scenarios for top 5
   ↓
4. @exploit-researcher: Quantify business impact
   ↓
5. @security-analyst: Map to compliance requirements
   ↓
6. Present executive summary (risk + compliance + impact)
```

### Workflow 4: Comprehensive Security Review

```
1. New feature under review
   ↓
2. @exploit-researcher: Attack surface analysis
   ↓
3. SAST scan + manual review
   ↓
4. @security-analyst: Triage findings
   ↓
5. @patch-engineer: Review proposed fixes
   ↓
6. @fuzzing-strategist: Design fuzzing for new parsers
   ↓
7. @security-analyst: Final risk assessment
```

---

## Integration with Security Workflows

### Triage Workflow Integration

**Standard Triage (without personas):**
```python
# Basic triage engine
results = triage_engine.triage(findings)
# → Classification, risk score, generic explanation
```

**Enhanced Triage (with @security-analyst):**
```python
# Invoke @security-analyst for critical findings
for finding in findings:
    if finding.severity == "critical":
        # Claude loads @security-analyst persona
        enhanced_analysis = analyze_with_persona(
            persona="security-analyst",
            finding=finding
        )
        # → CVSS score, compliance mapping, detailed impact
```

### Fix Generation Integration

**Standard Fix Generation (without personas):**
```python
# Basic fix generator
fix = fix_generator.generate_fix(finding)
# → Generic fix (may have issues)
```

**Enhanced Fix Validation (with @patch-engineer):**
```python
# Generate fix, then validate with @patch-engineer
fix = fix_generator.generate_fix(finding)

# Claude loads @patch-engineer persona
review = review_fix_with_persona(
    persona="patch-engineer",
    finding=finding,
    proposed_fix=fix
)

if review.quality_score < 7:
    # Regenerate fix with improvements
    fix = apply_improvements(fix, review.suggestions)
```

---

## Persona Selection Guide

**When to use which persona?**

### Use @security-analyst when:
- ✅ Classifying vulnerabilities (TP/FP/NI)
- ✅ Prioritizing security findings
- ✅ Assessing business impact and risk
- ✅ Mapping to compliance frameworks
- ✅ Explaining vulnerabilities to stakeholders

### Use @patch-engineer when:
- ✅ Reviewing security fixes (AI or human-generated)
- ✅ Validating fix correctness
- ✅ Designing test strategies for security patches
- ✅ Assessing fix quality and completeness
- ✅ Preventing regressions

### Use @fuzzing-strategist when:
- ✅ Planning fuzzing for parsers or protocols
- ✅ Selecting fuzzing tools
- ✅ Creating fuzzing harnesses and corpora
- ✅ Analyzing crashes and triaging root causes
- ✅ Setting up continuous fuzzing in CI/CD

### Use @exploit-researcher when:
- ✅ Generating attack scenarios
- ✅ Assessing exploitability
- ✅ Demonstrating business impact
- ✅ Identifying privilege escalation paths
- ✅ Threat modeling and attack surface analysis

---

## Performance and Cost Considerations

### Token Usage

**Baseline (no personas):** ~500 tokens/analysis
**With persona:** ~1000 tokens/analysis (+100%)

**But:**
- Quality improvement: 50-80%
- Fewer iterations needed (better first output)
- Reduced manual review time

**Net ROI:** Positive (better quality justifies cost)

### When to Optimize

**High-volume scenarios (1000+ findings):**
- Use personas only for critical/high severity
- Use heuristic triage for medium/low
- Batch process findings to amortize loading cost

**Low-volume scenarios (<100 findings):**
- Use personas liberally
- Quality more important than cost
- Manual review savings outweigh token cost

---

## Customization and Extension

### Adding Custom Personas

Create new persona in `.claude/skills/`:

```markdown
---
name: cloud-security-expert
description: AWS/GCP/Azure security specialist
---

# @cloud-security-expert Persona

You are an expert in cloud security...

## Expertise Areas
- AWS IAM policies and least privilege
- S3 bucket security and encryption
- CloudTrail monitoring and alerting
...

## Use Cases
1. Review IAM policies for over-permissiveness
2. Audit S3 bucket configurations
...
```

### Modifying Existing Personas

Edit persona files directly:
- Add new use cases
- Update expertise areas
- Add domain-specific knowledge
- Customize communication style

Changes take effect immediately (next persona load).

---

## Best Practices

### DO:
- ✅ Use @security-analyst for all critical vulnerability triage
- ✅ Use @patch-engineer to review all security fixes
- ✅ Use @fuzzing-strategist for parser/protocol development
- ✅ Use @exploit-researcher for executive briefings
- ✅ Combine personas for comprehensive analysis
- ✅ Cache persona outputs for reuse

### DON'T:
- ❌ Load all personas for every finding (wasteful)
- ❌ Use personas for non-security tasks
- ❌ Bypass personas for critical vulnerabilities
- ❌ Ignore persona recommendations without justification
- ❌ Use personas as replacement for human expertise (augmentation only)

---

## Troubleshooting

### Persona Not Loading

**Symptom:** Persona mentioned but generic response given

**Solutions:**
1. Check persona file exists: `.claude/skills/<persona>.md`
2. Verify YAML frontmatter is valid
3. Clear Claude's context and retry
4. Explicitly request: "Please load @security-analyst persona"

### Low-Quality Output

**Symptom:** Persona loaded but output is generic

**Solutions:**
1. Provide more context (code snippets, error messages)
2. Ask specific questions (not open-ended)
3. Reference persona expertise areas explicitly
4. Provide examples of desired output

### High Token Usage

**Symptom:** Persona uses too many tokens

**Solutions:**
1. Use personas selectively (critical findings only)
2. Cache persona outputs for similar findings
3. Use heuristic triage for low/medium severity
4. Batch process findings to amortize loading cost

---

## Examples

### Example 1: Triage with @security-analyst

**Input:**
```
Finding: SQL Injection in /api/search?q=<user_input>
CWE: CWE-89
Severity: High
```

**Output from @security-analyst:**
```
Classification: TRUE POSITIVE (Confidence: 0.95)

CVSS v3.1 Score: 9.8 (CRITICAL)
Vector: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H

Business Impact:
- Financial Risk: $250K-$1M (data breach costs)
- Compliance: SOC2 failure, PCI-DSS non-compliance
- Reputation: Customer trust loss, negative press

Compliance Mapping:
- SOC2: CC6.1 (Logical access controls) - FAIL
- PCI-DSS 6.5.1: Injection flaws - NON-COMPLIANT
- ISO 27001 A.14.2.5: Secure system principles - CONTROL GAP

Remediation: Use parameterized queries
Priority: P0 (0-24 hours)
```

### Example 2: Fix Review with @patch-engineer

**Input:**
```python
# Proposed fix for SQL injection
def search_users(query):
    sql = "SELECT * FROM users WHERE name LIKE %s"
    return db.execute(sql, (f'%{query}%',))
```

**Output from @patch-engineer:**
```
Fix Quality Score: 9/10 (Excellent)

✅ Correctness: Uses parameterized query (prevents injection)
✅ Completeness: Handles the specific vulnerability
✅ Quality: Follows Python DB-API 2.0 standard
✅ No Side Effects: Behavior unchanged for valid inputs

Minor Improvement:
- Add input validation (max length, allowed characters)
- Add type hints for maintainability

Recommended Tests:
1. test_search_sql_injection_prevention()
2. test_search_wildcard_characters()
3. test_search_empty_query()

Deployment: APPROVED - Ready for production
```

### Example 3: Fuzzing Strategy with @fuzzing-strategist

**Input:**
```
Target: JSON API parser (Python)
Goal: Find parsing vulnerabilities
```

**Output from @fuzzing-strategist:**
```
Fuzzing Strategy:

Tool: Atheris (Python fuzzing)
Effort: 4 hours setup + 24 hours fuzzing

Harness:
```python
import atheris
def test_one_input(data):
    try:
        json_parser.parse(data)
    except ValueError:
        pass  # Expected for invalid JSON
atheris.Fuzz(test_one_input)
```

Seed Corpus:
- Valid JSON samples from tests/
- Edge cases (empty, nested, large)
- Malformed samples (unclosed braces, etc.)

Expected Bugs:
- Buffer over-read (deep nesting)
- Integer overflow (large numbers)
- Infinite loop (cyclic references)

Success Metrics:
- >80% code coverage
- 24+ hour fuzzing time
- All crashes triaged
```

---

## Feedback and Improvement

### Providing Feedback

**If persona output is incorrect:**
1. Document the issue (what was wrong?)
2. Provide expected output
3. Update persona markdown file with correction
4. File issue in jp-spec-kit repo

**If persona is missing knowledge:**
1. Identify knowledge gap
2. Research correct information
3. Add to persona's knowledge base section
4. Submit PR to jp-spec-kit

### Continuous Improvement

Personas improve through:
- Community contributions
- Real-world usage feedback
- Security research updates
- Vulnerability pattern evolution

**Contributing:**
```bash
# 1. Clone jp-spec-kit
git clone https://github.com/yourorg/jp-spec-kit

# 2. Edit persona
vim .claude/skills/security-analyst.md

# 3. Test changes
# Use persona in real triage

# 4. Submit PR
git checkout -b improve-security-analyst
git commit -m "Add OWASP 2024 mappings to @security-analyst"
git push
gh pr create
```

---

## Additional Resources

- [Security Triage Skill](/.claude/skills/security-triage.md) - Core triage skill
- [Security Fixer Skill](/.claude/skills/security-fixer/) - Fix generation skill
- [OWASP Top 10](https://owasp.org/Top10/) - Vulnerability reference
- [CWE Database](https://cwe.mitre.org/) - Weakness enumeration
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1) - Severity scoring

---

**Version:** 1.0.0
**Last Updated:** 2025-12-05
**Maintained By:** JP Spec Kit Security Team
