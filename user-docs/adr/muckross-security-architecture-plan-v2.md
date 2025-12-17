# Muckross Security Architecture Plan v2 (CORRECTED)

**Status:** CORRECTED - Zero API Dependencies
**Date:** 2025-12-04
**Author:** Architecture Agent

## CRITICAL CORRECTION

**Previous architecture incorrectly used Anthropic Python SDK with API keys.**

This document defines the **CORRECTED** architecture that adheres to the fundamental constraint:

> **ZERO API KEYS. ZERO LLM SDK CALLS.**
>
> All AI capabilities MUST be implemented as **skills/prompts** that native AI coding tools (Claude Code, Cursor, GitHub Copilot) execute directly.

## Command Naming Convention

All security slash commands follow the `/flow:security_*` pattern with underscores:

- `/flow:security_scan` - Run security scanners
- `/flow:security_triage` - AI-powered vulnerability triage
- `/flow:security_fix` - Generate and apply security patches
- `/flow:security_report` - Generate security audit reports

**NOT** `/flow:security-scan` (dashes are incorrect).

## Command Types: CLI vs Agentic

This system provides two types of commands:

| Type | Location | Execution | Example | Use Case |
|------|----------|-----------|---------|----------|
| **CLI (Deterministic)** | `src/specify_cli/commands/` | Python code, no LLM | `specify security scan` | Scanner orchestration, data parsing |
| **Agentic (LLM-Powered)** | `.claude/commands/` | AI coding tool executes | `/flow:security_triage` | Vulnerability analysis, fix generation |

**CLI Commands (`specify security *`):**
- Written in Python
- Deterministic behavior
- No AI/LLM involvement
- Execute scanners, parse outputs, format data
- Example: `specify security scan` runs Semgrep/Bandit

**Agentic Commands (`/flow:security_*`):**
- Written as markdown prompts
- Executed by AI coding tools (Claude Code, Cursor, etc.)
- Invoke skills for analysis, triage, reporting
- Example: `/flow:security_triage` invokes `.claude/skills/security-triage.md`

## Workflow Independence

**This is NOT part of the core flowspec workflow.**

The security commands are **optional capabilities** that any developer or security engineer can run independently:

- **Not gated by workflow state** - No required input states
- **Runs anytime** - Can be invoked on any repository at any time
- **Independent of `/flow:specify → /flow:plan → /flow:implement`** - Does not require prior workflow steps
- **Optional integration** - Can optionally integrate with backlog.md for task tracking

This is a standalone security analysis toolkit, not a required step in the SDD workflow.

## Security Memory Directory

Persistent security context is stored in `memory/security/` for consistent agent/skill/command behavior:

```
memory/security/
├── security-facts.md        # Key security facts, thresholds, policies
├── cwe-knowledge.md         # CWE categories and remediation patterns
├── scanner-config.md        # Scanner defaults and customizations
├── triage-guidelines.md     # Classification rules and examples
└── compliance-mapping.md    # OWASP, CWE, NIST mappings
```

These files are `@import`ed by skills and slash commands to provide:
- Consistent security policies across all commands
- CWE/OWASP knowledge for vulnerability classification
- Scanner configuration defaults
- Triage classification criteria
- Compliance framework mappings

## Fundamental Constraint (NON-NEGOTIABLE)

### WRONG ❌

```python
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(...)  # NEVER DO THIS
```

### RIGHT ✅

```markdown
# .claude/skills/security-triage.md
When triaging security findings, analyze each finding for:
1. True positive vs false positive classification
2. Risk severity scoring
3. Root cause clustering
4. Actionable remediation guidance
```

**The AI coding tool the user is running executes the skill natively.**

## Architecture Principles

1. **Python = Orchestration Only**
   - Run security scanners (Semgrep, Bandit, etc.)
   - Parse scanner outputs
   - Format data as JSON
   - Generate static reports

2. **AI = Skills Only**
   - Skills defined in `.claude/skills/`
   - Slash commands invoke skills
   - AI coding tool (Claude Code/Cursor/etc.) IS the LLM
   - No API calls, no SDK usage

3. **Data Flow = Files**
   - Scanner → `docs/security/findings.json`
   - Skill reads JSON → AI coding tool analyzes
   - AI coding tool writes → `docs/security/triage-results.json`
   - Python reads results → generates reports

## Component Architecture

### Layer 1: Scanner Orchestration (Python)

**Location:** `src/specify_cli/scanners/`

**Responsibilities:**
- Execute security tools (Semgrep, Bandit, etc.)
- Parse tool outputs into unified JSON format
- Write findings to `docs/security/findings.json`
- **NO AI/LLM LOGIC**

**Files:**
```
src/specify_cli/scanners/
├── __init__.py
├── base.py              # Scanner interface
├── semgrep.py           # Semgrep integration
├── bandit.py            # Bandit integration
├── models.py            # Finding data models
└── unified_format.py    # JSON schema
```

### Layer 2: AI Skills (Markdown Prompts)

**Location:** `.claude/skills/`

**Responsibilities:**
- Define AI behaviors for security tasks
- Invoked by native AI coding tools
- **NO Python code in skills**

**Files:**
```
.claude/skills/
├── security-triage.md           # Classify findings (TP/FP/NI)
├── security-fixer.md            # Generate code patches
├── security-reporter.md         # Write audit reports
├── security-triage-beginner.md  # Simple explanations
├── security-triage-expert.md    # Technical deep-dive
├── security-triage-compliance.md # Audit-focused
└── security-cluster.md          # Root cause analysis
```

### Layer 3: Slash Commands (Command Definitions)

**Location:** `.claude/commands/`

**Responsibilities:**
- Entry points for security workflows
- Invoke appropriate skills
- Chain multiple skills if needed

**Files:**
```
.claude/commands/
├── flowspec-security_scan.md     # Run scanners → findings.json
├── flowspec-security_triage.md   # Invoke security-triage.md skill
├── flowspec-security_fix.md      # Invoke security-fixer.md skill
├── flowspec-security_report.md   # Invoke security-reporter.md skill
└── flowspec-security.md          # Main command (orchestrates all)
```

### Layer 4: Configuration System (Python + YAML)

**Location:** `src/specify_cli/config/`

**Responsibilities:**
- Load security policies from YAML
- Provide config to scanners
- Validate rule syntax
- **NO AI/LLM LOGIC**

**Files:**
```
src/specify_cli/config/
├── __init__.py
├── security_config.py    # Config loader
├── policy_validator.py   # YAML validation
└── defaults.yaml         # Default policies
```

## Data Flow

### 1. Scanning Phase (Python)

```bash
/flow:security_scan
```

**Flow:**
1. Slash command executes Python CLI
2. Python runs scanners (Semgrep, Bandit)
3. Python writes `docs/security/findings.json`

```json
{
  "findings": [
    {
      "id": "semgrep-001",
      "rule_id": "python.django.security.injection.sql.sql-injection",
      "severity": "ERROR",
      "file": "src/views.py",
      "line": 42,
      "code": "User.objects.raw(query)",
      "message": "SQL injection vulnerability"
    }
  ]
}
```

### 2. Triage Phase (AI Skill)

```bash
/flow:security_triage
```

**Flow:**
1. Slash command invokes `.claude/skills/security-triage.md`
2. **AI coding tool** (Claude Code) reads the skill
3. **AI coding tool** reads `docs/security/findings.json`
4. **AI coding tool** analyzes each finding:
   - Classifies as TP/FP/NI
   - Scores risk severity
   - Clusters by root cause
   - Generates explanations
5. **AI coding tool** writes `docs/security/triage-results.json`

```json
{
  "triaged_findings": [
    {
      "finding_id": "semgrep-001",
      "classification": "TRUE_POSITIVE",
      "confidence": 0.95,
      "risk_score": 9.2,
      "cluster": "sql-injection",
      "explanation": "This is a genuine SQL injection vulnerability...",
      "remediation": "Use parameterized queries or ORM methods..."
    }
  ]
}
```

### 3. Fix Generation Phase (AI Skill)

```bash
/flow:security_fix
```

**Flow:**
1. Slash command invokes `.claude/skills/security-fixer.md`
2. **AI coding tool** reads triage results
3. **AI coding tool** generates patches:
   - Reads vulnerable code
   - Creates secure alternative
   - Writes unified diff format
4. **AI coding tool** writes `docs/security/patches/`

```diff
--- a/src/views.py
+++ b/src/views.py
@@ -39,7 +39,7 @@

 def get_user(request):
     username = request.GET.get('username')
-    users = User.objects.raw(f"SELECT * FROM users WHERE username = '{username}'")
+    users = User.objects.filter(username=username)
     return render(request, 'user.html', {'users': users})
```

### 4. Reporting Phase (Python + AI Skill)

```bash
/flow:security_report
```

**Flow:**
1. Slash command invokes `.claude/skills/security-reporter.md`
2. **AI coding tool** reads triage results and patches
3. **AI coding tool** generates markdown report
4. **AI coding tool** writes `docs/security/audit-report.md`
5. Python CLI formats as HTML/PDF (optional)

## Task Breakdown (CORRECTED)

### task-212: Build AI-Powered Vulnerability Triage Engine ✅

**CORRECTED Implementation:**

1. **Python Code (Orchestration Only):**
   - `src/specify_cli/scanners/unified_format.py` - Define JSON schema
   - `src/specify_cli/scanners/semgrep.py` - Write findings.json
   - **NO AI LOGIC IN PYTHON**

2. **AI Skill:**
   - `.claude/skills/security-triage.md` - Triage instructions
   - Skill tells AI how to classify findings
   - AI coding tool executes skill natively

3. **Slash Command:**
   - `.claude/commands/flow-security_triage.md`
   - Invokes security-triage skill
   - Reads findings.json → writes triage-results.json

**Output:**
- `docs/security/triage-results.json` (written by AI coding tool)
- **ZERO API CALLS**

### task-213: Implement Automated Fix Generation and Patch Application ✅

**CORRECTED Implementation:**

1. **AI Skill:**
   - `.claude/skills/security-fixer.md` - Fix generation instructions
   - Skill tells AI how to generate patches
   - AI coding tool creates actual patches

2. **Slash Command:**
   - `.claude/commands/flow-security_fix.md`
   - Invokes security-fixer skill
   - Reads triage-results.json → writes patches/

3. **Python Code (Application Only):**
   - `src/specify_cli/commands/security_fix.py` - Apply patches
   - Uses `patch` or `git apply`
   - **NO AI LOGIC**

**Output:**
- `docs/security/patches/*.patch` (written by AI coding tool)
- Applied changes to source files (by Python)

### task-221: Implement Security Expert Personas ✅

**CORRECTED Implementation:**

1. **AI Skills (Variants):**
   - `.claude/skills/security-triage-beginner.md` - Simple language
   - `.claude/skills/security-triage-expert.md` - Technical depth
   - `.claude/skills/security-triage-compliance.md` - Audit focus

2. **Configuration:**
   - `docs/security/config.yaml` - Persona selection
   ```yaml
   security:
     triage_persona: "expert"  # beginner|expert|compliance
   ```

3. **Slash Command:**
   - `.claude/commands/flow-security_triage.md`
   - Reads config → invokes appropriate skill variant

**Output:**
- Triage results with persona-specific explanations

### task-280: Benchmark AI Triage Engine Accuracy ✅

**CORRECTED Implementation:**

1. **Labeled Dataset:**
   - `tests/security/benchmark/labeled-findings.json`
   - Human-labeled ground truth (TP/FP/NI)

2. **Benchmark Script (Python):**
   - `scripts/benchmark-triage.py`
   - Runs AI triage skill via CLI
   - Compares output vs. labels
   - Calculates precision/recall/F1

3. **AI Skill Execution:**
   - Script invokes `/flow:security_triage`
   - **AI coding tool** executes skill
   - Python measures accuracy of results

**Output:**
- `docs/security/benchmark-results.json`
- Metrics: precision, recall, F1, confusion matrix

### task-217: Build Security Configuration System ✅

**CORRECTED Implementation:**

1. **Python Code:**
   - `src/specify_cli/config/security_config.py` - YAML loader
   - `src/specify_cli/config/policy_validator.py` - Schema validation
   - **NO AI LOGIC**

2. **Configuration Files:**
   - `docs/security/config.yaml` - Project policies
   - `src/specify_cli/config/defaults.yaml` - Default rules

3. **Integration:**
   - Scanners read config
   - Skills receive config as context

**Output:**
- Config system used by scanners and skills

### task-223: Implement Custom Security Rules System ✅

**CORRECTED Implementation:**

1. **Python Code:**
   - `src/specify_cli/scanners/custom_rules.py` - Rule manager
   - Load rules from `docs/security/rules/`

2. **Rule Format:**
   - Semgrep YAML rules
   - Custom Python validators

3. **Integration:**
   - Scanners load custom rules
   - Findings include rule metadata

**Output:**
- `docs/security/rules/` directory
- Custom rules executed during scan

### task-252: Implement Security Policy as Code Configuration ✅

**CORRECTED Implementation:**

1. **Policy Files:**
   - `docs/security/policies/` - YAML policy definitions
   - Define severity thresholds, ignore patterns, etc.

2. **Python Code:**
   - `src/specify_cli/config/policy_engine.py` - Policy evaluator
   - Apply policies to findings
   - **NO AI LOGIC**

3. **Integration:**
   - Triage skill receives policy context
   - AI considers policies when classifying

**Output:**
- Policy-aware triage results

### task-214: Build Security Audit Report Generator ✅

**CORRECTED Implementation:**

1. **AI Skill:**
   - `.claude/skills/security-reporter.md` - Report instructions
   - Skill tells AI how to structure reports
   - AI coding tool generates markdown

2. **Slash Command:**
   - `.claude/commands/flow-security_report.md`
   - Invokes security-reporter skill
   - Reads triage-results.json → writes audit-report.md

3. **Python Code (Formatting Only):**
   - `src/specify_cli/commands/security_report.py` - HTML/PDF export
   - Uses Pandoc or similar
   - **NO AI LOGIC**

**Output:**
- `docs/security/audit-report.md` (by AI)
- `docs/security/audit-report.html` (by Python)

### task-216: Integrate /flow:security with Workflow and Backlog ✅

**CORRECTED Implementation:**

1. **Optional Workflow Integration:**
   - Security commands are NOT required workflow steps
   - Can optionally add to `flowspec_workflow.yml` if desired
   - Example (optional):
   ```yaml
   workflows:
     security:
       command: "/flow:security"
       agents: ["security-triage", "security-fixer"]
       input_states: []  # No required input states
       output_state: "Security Reviewed"
   ```

2. **Optional Backlog Integration:**
   - Security findings can optionally create tasks
   - Tasks track fix implementation
   - `/flow:security` can optionally update task status

3. **Python Code:**
   - `src/specify_cli/commands/security.py` - Backlog integration
   - Create tasks from findings
   - Update task status

**Output:**
- Security findings tracked in backlog.md

### task-218: Write Comprehensive Security Commands Documentation ✅

**CORRECTED Implementation:**

1. **Documentation Files:**
   - `docs/guides/security-quickstart.md`
   - `docs/guides/security-triage.md`
   - `docs/guides/security-fix-generation.md`
   - `docs/reference/security-commands.md`

2. **Content:**
   - Command usage examples
   - Skill descriptions
   - Configuration guide
   - Troubleshooting

**Output:**
- Complete security documentation

### task-220: Resolve Relationship with task-198 Unified Vulnerability Scanner ✅

**CORRECTED Implementation:**

1. **Analysis:**
   - Review task-198 requirements
   - Identify overlaps and differences
   - Document integration points

2. **Integration Plan:**
   - Muckross security = AI-powered triage
   - task-198 scanner = Multi-tool orchestration
   - Muckross consumes task-198 scanner outputs

3. **Documentation:**
   - `docs/architecture/scanner-integration.md`
   - Define interfaces between systems

**Output:**
- Clear integration strategy

## Skills to be Created

All skills in `.claude/skills/`:

1. **security-triage.md** - Core triage logic
   - Classify findings (TP/FP/NI)
   - Risk scoring
   - Root cause clustering
   - Remediation guidance

2. **security-fixer.md** - Patch generation
   - Read vulnerable code
   - Generate secure alternatives
   - Create unified diffs

3. **security-reporter.md** - Report generation
   - Structured audit reports
   - Executive summaries
   - Technical details

4. **security-triage-beginner.md** - Beginner persona
   - Simple explanations
   - Link to learning resources
   - Basic remediation steps

5. **security-triage-expert.md** - Expert persona
   - Technical deep-dive
   - CVE references
   - Advanced exploitation scenarios

6. **security-triage-compliance.md** - Compliance persona
   - Regulatory mapping (OWASP, CWE)
   - Audit requirements
   - Evidence collection

7. **security-cluster.md** - Root cause analysis
   - Group related findings
   - Identify systemic issues
   - Prioritize fixes

## Slash Commands to be Created

All commands in `.claude/commands/`:

1. **flowspec-security_scan.md** - Run scanners
2. **flowspec-security_triage.md** - Invoke triage skill
3. **flowspec-security_fix.md** - Invoke fixer skill
4. **flowspec-security_report.md** - Invoke reporter skill
5. **flowspec-security.md** - Main orchestrator

## Configuration Files

1. **docs/security/config.yaml** - Project security config
   ```yaml
   security:
     triage_persona: "expert"
     severity_threshold: "medium"
     ignore_patterns:
       - "test/**"
     custom_rules_dir: "docs/security/rules/"
   ```

2. **src/specify_cli/config/defaults.yaml** - Default policies
   ```yaml
   defaults:
     scanners:
       - semgrep
       - bandit
     output_format: "json"
   ```

## Success Criteria

- [ ] All 11 tasks updated with corrected implementation plans
- [ ] Architecture document created (this file)
- [ ] **ZERO API DEPENDENCIES** confirmed in all tasks
- [ ] Skills list defined (7 skills)
- [ ] Slash commands list defined (5 commands)
- [ ] Data flow documented (files-based)
- [ ] All tasks labeled `workflow:Planned`

## Verification Checklist

- [ ] No `from anthropic import` in any Python file
- [ ] No `api_key` in any config file
- [ ] All AI logic in `.claude/skills/` (markdown only)
- [ ] All Python code is orchestration/formatting only
- [ ] Skills invoked by slash commands
- [ ] Data flows through JSON files
- [ ] AI coding tool (Claude Code) executes skills natively

## Next Steps

1. Update all 11 task implementation plans
2. Add `workflow:Planned` labels
3. Commit architecture document
4. Create PR for review
5. After approval: Begin implementation starting with task-212

---

**CONFIRMATION: ZERO API DEPENDENCIES ✅**

This architecture contains NO LLM API calls, NO SDK usage, and NO API keys. All AI capabilities are implemented as native skills for AI coding tools.
