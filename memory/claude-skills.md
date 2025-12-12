# Claude Code Skills

Flowspec includes 17 specialized Skills that Claude automatically invokes based on task context. Skills differ from slash commands in that they are **model-invoked** (automatic) rather than user-invoked (manual).

## How Skills Work

Skills are stored in `.claude/skills/<skill-name>/SKILL.md` with:
- YAML frontmatter: `name` and `description` (critical for automatic discovery)
- Markdown content: instructions, templates, and examples

Claude automatically uses a skill when the task context matches the skill's `description`.

## Core Workflow Skills

### 1. PM Planner (`pm-planner`)

**Location**: `.claude/skills/pm-planner/SKILL.md`

**Auto-invoked when**:
- Creating or editing backlog tasks
- Breaking down features into atomic tasks
- Writing acceptance criteria
- Reviewing task quality

**Capabilities**:
- Task creation guidelines (title, description, AC)
- Atomicity rules (single PR scope, testable, independent)
- Task breakdown strategies
- Quality checklist

### 2. Architect (`architect`)

**Location**: `.claude/skills/architect/SKILL.md`

**Auto-invoked when**:
- Making architecture decisions
- Creating ADRs
- Designing system components
- Evaluating technology choices

**Capabilities**:
- ADR format and templates
- Architecture principles (separation of concerns, defense in depth)
- Technology evaluation framework
- Scalability checklist

### 3. QA Validator (`qa-validator`)

**Location**: `.claude/skills/qa-validator/SKILL.md`

**Auto-invoked when**:
- Creating test plans
- Reviewing test coverage
- Defining quality gates
- Writing E2E scenarios

**Capabilities**:
- Test pyramid guidance
- Test plan templates
- AC validation checklist
- Bug report format

### 4. SDD Methodology (`sdd-methodology`)

**Location**: `.claude/skills/sdd-methodology/SKILL.md`

**Auto-invoked when**:
- Explaining SDD workflow
- Guiding through workflow phases
- Helping with methodology decisions
- Onboarding to SDD

**Capabilities**:
- Workflow phase overview
- State transition rules
- SDD principles
- Common anti-patterns

### 5. Constitution Checker (`constitution-checker`)

**Location**: `.claude/skills/constitution-checker/SKILL.md`

**Auto-invoked when**:
- Executing `/flow:*` workflow commands
- Validating constitution completeness
- Checking tier-based enforcement rules

**Capabilities**:
- Constitution validation
- Tier-based enforcement (Light=warn, Medium=confirm, Heavy=block)
- Constitution setup guidance

## Security Skills

### 6. Security Reviewer (`security-reviewer`)

**Location**: `.claude/skills/security-reviewer/SKILL.md`

**Auto-invoked when**:
- Reviewing code for vulnerabilities
- Conducting threat modeling
- Ensuring SLSA compliance
- Performing security assessments

**Capabilities**:
- OWASP Top 10 checklist
- SLSA compliance levels
- STRIDE threat modeling
- Secure coding patterns

### 7. Security Analyst (`security-analyst`)

**Location**: `.claude/skills/security-analyst/SKILL.md`

**Auto-invoked when**:
- Classifying vulnerabilities
- Performing risk assessment
- Scoring CVSS
- Mapping to compliance frameworks

**Capabilities**:
- OWASP Top 10 and CWE classification
- CVSS v3.1 scoring methodology
- Risk quantification and business impact analysis
- Compliance mapping (SOC2, ISO27001, PCI-DSS, HIPAA)

### 8. Security CodeQL (`security-codeql`)

**Location**: `.claude/skills/security-codeql/SKILL.md`

**Auto-invoked when**:
- Analyzing CodeQL SARIF output
- Interpreting dataflow analysis
- Validating taint tracking
- Providing semantic analysis guidance

**Capabilities**:
- CodeQL SARIF interpretation
- Dataflow and taint propagation analysis
- Remediation guidance for semantic vulnerabilities
- Inter-procedural analysis insights

### 9. Security DAST (`security-dast`)

**Location**: `.claude/skills/security-dast/SKILL.md`

**Auto-invoked when**:
- Running `/flow:security_web`
- Testing web application security
- Analyzing running applications

**Capabilities**:
- Dynamic Application Security Testing (DAST)
- OWASP Top 10 vulnerability testing
- Security header analysis
- Web security issue detection

### 10. Security Triage (`security-triage`)

**Location**: `.claude/skills/security-triage/SKILL.md`

**Auto-invoked when**:
- Running `/flow:security_triage`
- Triaging security findings
- Analyzing scanner output

**Capabilities**:
- AI-powered vulnerability triage
- Risk scoring and classification
- Vulnerability clustering
- Finding explanations and prioritization

### 11. Security Custom Rules (`security-custom-rules`)

**Location**: `.claude/skills/security-custom-rules/SKILL.md`

**Auto-invoked when**:
- Creating custom security rules
- Defining organization-specific checks
- Reducing false positives
- Running `/flow:security_custom_rules`

**Capabilities**:
- Semgrep rule creation
- Bandit rule development (Python)
- Custom rule testing and validation
- Organization-specific security standards

### 12. Security Fixer (`security-fixer`)

**Location**: `.claude/skills/security-fixer/SKILL.md`

**Auto-invoked when**:
- Generating security patches
- Fixing vulnerabilities
- Creating remediation code

**Capabilities**:
- Automated vulnerability remediation
- Patch generation (SQL injection, XSS, path traversal, CSRF)
- Unified diff creation
- Patch quality validation

### 13. Security Reporter (`security-reporter`)

**Location**: `.claude/skills/security-reporter/SKILL.md`

**Auto-invoked when**:
- Generating security audit reports
- Analyzing scan results
- Calculating security posture
- Creating OWASP compliance assessments

**Capabilities**:
- Comprehensive security audit reports
- Vulnerability aggregation
- Security posture calculation
- Remediation prioritization
- Executive security summaries

### 14. Security Workflow (`security-workflow`)

**Location**: `.claude/skills/security-workflow/SKILL.md`

**Auto-invoked when**:
- Creating tasks from security findings
- Integrating security into workflow
- Managing security remediation tracking

**Capabilities**:
- Backlog task creation from findings
- Security workflow integration
- Vulnerability-to-task mapping
- Security fix prioritization

## Advanced Security Skills

### 15. Exploit Researcher (`exploit-researcher`)

**Location**: `.claude/skills/exploit-researcher/SKILL.md`

**Auto-invoked when**:
- Analyzing attack surfaces
- Generating exploit scenarios
- Chaining vulnerabilities
- Demonstrating business impact

**Capabilities**:
- Attack surface mapping
- Exploit scenario development
- Vulnerability chaining
- Proof-of-concept (PoC) creation
- Privilege escalation analysis

### 16. Fuzzing Strategist (`fuzzing-strategist`)

**Location**: `.claude/skills/fuzzing-strategist/SKILL.md`

**Auto-invoked when**:
- Designing fuzzing strategies
- Selecting fuzzing tools
- Analyzing crashes
- Integrating fuzzing into CI/CD

**Capabilities**:
- Coverage-guided fuzzing (AFL++, libFuzzer)
- Grammar-based fuzzing
- Fuzzing tool selection and configuration
- Crash triage and root cause analysis
- CI/CD fuzzing integration

### 17. Patch Engineer (`patch-engineer`)

**Location**: `.claude/skills/patch-engineer/SKILL.md`

**Auto-invoked when**:
- Reviewing security fixes
- Validating patch correctness
- Preventing regressions
- Assessing fix quality

**Capabilities**:
- Security fix validation
- Language-specific secure coding patterns
- Testing strategy design for fixes
- Regression prevention
- Performance impact assessment

## Creating Custom Skills

To add a new skill:

1. Create directory: `.claude/skills/<skill-name>/`
2. Create `SKILL.md` with frontmatter:
   ```yaml
   ---
   name: my-skill
   description: Use when [context that triggers this skill]
   ---
   ```
3. Add instructions, templates, and examples in Markdown

## Skills vs. Other Claude Code Features

| Feature | Invocation | Use Case |
|---------|------------|----------|
| **Skills** | Automatic (model-invoked) | Domain expertise, templates, guidelines |
| **Slash Commands** | Manual (`/command`) | Explicit workflows, multi-step processes |
| **Subagents** | Manual (Task tool) | Parallel execution, isolated context |
| **Hooks** | Automatic (event-based) | Validation, formatting, safety checks |
