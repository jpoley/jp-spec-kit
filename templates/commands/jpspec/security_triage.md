# /jpspec:security_triage - AI-Powered Vulnerability Triage

## Purpose

Perform AI-powered triage of security findings from scanners (Semgrep, CodeQL, etc.). Classify findings as true/false positives, calculate risk scores, generate explanations, and cluster related vulnerabilities.

## Prerequisites

- Security scan has been run (via `/jpspec:validate` or manual scan)
- Findings exist in `docs/security/findings.json` (Unified Finding Format)

## Workflow

### 1. Invoke Security Triage Skill

Execute the security triage skill to analyze all findings:

```markdown
I will now triage the security findings using the Security Triage Skill.

@skill security-triage
```

The skill will:
1. Read findings from `docs/security/findings.json`
2. For each finding:
   - Read code context (5 lines before/after)
   - Classify as TP/FP/NI using triage guidelines
   - Calculate risk score: (impact × exploitability) / detection_time
   - Generate plain-English explanation (What/Why/How)
3. Cluster findings by CWE, file, or architectural pattern
4. Sort by risk score (highest first)
5. Write results to `docs/security/triage-results.json`

### 2. Report Summary

After triage completes, provide a summary:

```markdown
## Triage Summary

**Total Findings**: {total}
**Classifications**:
- True Positives (TP): {tp_count} ({tp_percent}%)
- False Positives (FP): {fp_count} ({fp_percent}%)
- Needs Investigation (NI): {ni_count} ({ni_percent}%)

**Top 5 Risks** (by risk score):
1. [{finding_id}] {title} - Risk: {risk_score} ({classification})
2. ...

**Clusters Identified**:
- CLUSTER-CWE-CWE-89: {count} SQL injection findings
- CLUSTER-FILE-auth: {count} issues in auth.py
- ...

**Recommendations**:
1. Address {tp_count} true positives starting with highest risk scores
2. Review {ni_count} uncertain findings (NI) with security expert
3. Fix systemic issues identified in clusters
4. Dismiss {fp_count} false positives

Results saved to: `docs/security/triage-results.json`
```

### 3. Interactive Mode (Optional)

If user requests interactive confirmation:

```markdown
Do you want to review and confirm AI classifications? (y/n)
```

If yes, for each finding marked NI or with confidence <0.9:

1. Display finding details:
   ```
   Finding: SEMGREP-CWE-89-001
   File: src/auth.py:42-45
   Classification: TP (confidence: 0.85)

   Code:
   40: def login(request):
   41:     username = request.POST['username']
   42:     query = f"SELECT * FROM users WHERE username = '{username}'"
   43:     cursor.execute(query)
   44:     ...

   AI Reasoning: User input from request.POST flows directly to cursor.execute()
   with f-string formatting. No parameterized queries used.

   [y] Accept  [o] Override  [s] Skip  [?] More info
   ```

2. Handle user response:
   - **y (Accept)**: Keep AI classification
   - **o (Override)**: Prompt for correct classification and reason, update result
   - **s (Skip)**: Move to next finding
   - **? (More info)**: Show full code context (20 lines)

3. Save feedback for overrides to `~/.specify/triage_feedback.jsonl`

### 4. Update Backlog Tasks (If Requested)

Optionally create backlog tasks for true positives:

```bash
# For each TP with high risk score (>5.0)
backlog task create "Fix {title}" \
  --description "Finding: {finding_id}\nSeverity: {severity}\nCWE: {cwe_id}\n\n{explanation.what}\n\n{explanation.how_to_fix}" \
  --label security \
  --label urgent \
  --assignee @secure-by-design-engineer
```

## Input Format

Expects findings in `docs/security/findings.json` (Unified Finding Format):

```json
[
  {
    "id": "SEMGREP-CWE-89-001",
    "scanner": "semgrep",
    "severity": "high",
    "title": "SQL Injection in login query",
    "description": "User input concatenated into SQL query",
    "location": {
      "file": "src/auth.py",
      "line_start": 42,
      "line_end": 45,
      "code_snippet": "query = f\"SELECT * FROM users WHERE username = '{username}'\""
    },
    "cwe_id": "CWE-89",
    "cvss_score": 8.5
  }
]
```

## Output Format

Writes triage results to `docs/security/triage-results.json`:

```json
[
  {
    "finding_id": "SEMGREP-CWE-89-001",
    "classification": "TP",
    "confidence": 0.95,
    "risk_score": 4.2,
    "explanation": {
      "what": "SQL query built with string concatenation of user input",
      "why_it_matters": "Attacker can inject SQL commands to steal passwords, delete data, or bypass authentication",
      "how_to_exploit": "Enter ' OR 1=1 -- in username field to bypass login",
      "how_to_fix": "Use parameterized query: cursor.execute('SELECT * FROM users WHERE username = ?', (username,))"
    },
    "cluster_id": "CLUSTER-CWE-CWE-89",
    "cluster_type": "cwe",
    "ai_reasoning": "User input from request.POST flows to cursor.execute with f-string. No parameterized queries used.",
    "metadata": {
      "impact": 8,
      "exploitability": 9,
      "detection_time": 90
    }
  }
]
```

Results are sorted by `risk_score` descending (highest risk first).

## Command Options

```bash
/jpspec:security_triage [options]

Options:
  --input PATH          Path to findings file (default: docs/security/findings.json)
  --output PATH         Path to output file (default: docs/security/triage-results.json)
  --interactive         Enable interactive mode for confirmation
  --create-tasks        Create backlog tasks for high-risk TPs
  --min-confidence N    Only show findings with confidence >= N (default: 0.0)
```

## Integration with /jpspec:validate

This command is typically run as part of the validation workflow:

```bash
# 1. Run security scan
/jpspec:validate --security

# 2. Triage findings
/jpspec:security_triage --interactive

# 3. Fix true positives
# (Manual or via /jpspec:implement with security tasks)

# 4. Re-scan to verify fixes
/jpspec:validate --security
```

## Skills Used

- **security-triage**: Main triage logic (classification, risk scoring, explanation generation)

## Memory References

- `memory/security/triage-guidelines.md`: Classification rules, risk scoring, explanation format
- `memory/security/cwe-knowledge.md`: CWE patterns, true/false positive indicators, remediation guidance

## Example Usage

### Basic Triage

```bash
/jpspec:security_triage
```

Output:
```
Triaging 47 security findings...

[==================================================] 47/47

Triage Summary:
- True Positives: 12 (26%)
- False Positives: 31 (66%)
- Needs Investigation: 4 (8%)

Top 5 Risks:
1. SEMGREP-CWE-89-001: SQL injection in login - Risk: 8.4 (TP)
2. SEMGREP-CWE-22-003: Path traversal in file upload - Risk: 6.7 (TP)
3. SEMGREP-CWE-798-002: Hardcoded AWS key - Risk: 5.2 (TP)
4. CODEQL-CWE-79-001: XSS in search results - Risk: 4.1 (TP)
5. SEMGREP-CWE-327-001: MD5 password hashing - Risk: 3.8 (TP)

Clusters:
- CLUSTER-CWE-CWE-89: 5 SQL injection findings
- CLUSTER-FILE-auth: 3 issues in auth.py

Results saved to: docs/security/triage-results.json
```

### Interactive Mode

```bash
/jpspec:security_triage --interactive
```

Prompts for confirmation on uncertain findings and allows overrides.

### Create Tasks for High-Risk Findings

```bash
/jpspec:security_triage --create-tasks
```

Automatically creates backlog tasks for TP findings with risk_score > 5.0.

## Notes

- This command uses the **security-triage skill**, not Python LLM API calls
- All AI reasoning happens in Claude Code natively
- Python code only handles data structures and file I/O
- Target accuracy: >85% classification correctness
- Use interactive mode for critical systems or when confidence is low
