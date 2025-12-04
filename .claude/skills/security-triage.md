# Security Triage Skill

## Purpose

This skill enables Claude Code to perform AI-powered vulnerability triage on security findings. You will classify findings, score risk, generate explanations, and cluster related vulnerabilities.

## When to Use This Skill

- When invoked by `/jpspec:security_triage` command
- When user asks to triage security findings
- When analyzing scanner output (Semgrep, CodeQL, etc.)

## Input

Read security findings from one of:
1. `docs/security/findings.json` - Unified Finding Format (UFFormat)
2. Path specified by user
3. SARIF format files (auto-detect)

Expected format:
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

## Classification Process

For EACH finding, perform these steps:

### Step 1: Read Code Context

Read the file to get 5 lines before and after the finding:

```python
# Read context
file_path = finding["location"]["file"]
line_start = max(1, finding["location"]["line_start"] - 5)
line_end = finding["location"]["line_end"] + 5
```

### Step 2: Classify as TP/FP/NI

Apply classification rules from `memory/security/triage-guidelines.md`:

**TRUE_POSITIVE (TP)** when:
- User input flows to dangerous sink without sanitization
- No security controls present (parameterized queries, escaping)
- Attack scenario is feasible

**FALSE_POSITIVE (FP)** when:
- Proper validation/sanitization exists
- Framework provides automatic protection
- Context makes exploitation impossible

**NEEDS_INVESTIGATION (NI)** when:
- Insufficient context (confidence <0.7)
- Complex dataflow requiring human analysis

### Step 3: Assign Confidence Score

- **0.9-1.0**: Clear vulnerability pattern, no mitigations → TP
- **0.7-0.89**: Vulnerability likely, some ambiguity → TP with lower confidence
- **<0.7**: Insufficient confidence → mark as NEEDS_INVESTIGATION (NI)

### Step 4: Calculate Risk Score

Use the risk scoring formula: **risk_score = (impact × exploitability) / detection_time**

#### Impact (0-10)
Map from severity or CWE (see `memory/security/cwe-knowledge.md`):
- CRITICAL: 9-10 (RCE, auth bypass)
- HIGH: 7-8 (SQL injection, XSS)
- MEDIUM: 4-6 (info disclosure)
- LOW: 1-3 (minor issues)

#### Exploitability (0-10)
Assess based on:
- Public exploit available: 10
- Easy to exploit: 8-9
- Requires auth: 6-7
- Very difficult: 1-3

#### Detection Time (days)
Use git blame to find when code was written:

```python
import subprocess
result = subprocess.run(
    ["git", "blame", f"-L{line_start},{line_end}", "--porcelain", file_path],
    capture_output=True, text=True, check=True
)
committer_time = next(
    (line for line in result.stdout.splitlines() if line.startswith("committer-time")),
    None
)
# If needed, extract the timestamp from committer_time
```

Calculate days since commit. If git unavailable, default to 30 days.

### Step 5: Generate Plain-English Explanation

Create 4-part explanation (see `memory/security/triage-guidelines.md`):

**What** (1 sentence):
- Clear description for junior developers
- Avoid jargon

**Why It Matters** (2-3 sentences):
- Real-world security impact
- Concrete consequences

**How to Exploit** (TP only, 2-3 sentences):
- Specific attack scenario
- Example payload

**How to Fix** (2-4 sentences):
- Concrete fix with code example
- Link to documentation

Keep each section under 200 characters.

### Step 6: Determine Reasoning

Explain your classification decision in 1-2 sentences for debugging/feedback.

Example: "Classified as TP because user input from request.POST flows directly to cursor.execute() with string formatting, and no parameterized queries are used."

## Clustering Process

After classifying ALL findings:

### CWE Clustering

Group findings by CWE when:
- 3+ findings share the same CWE
- Cluster ID: `CLUSTER-CWE-{cwe_id}`

Example: 5 findings with CWE-89 → `CLUSTER-CWE-CWE-89`

### File Clustering

Group findings by file when:
- 2+ findings in same file (different CWEs or unclustered by CWE)
- Cluster ID: `CLUSTER-FILE-{filename_stem}`

Example: 3 findings in auth.py → `CLUSTER-FILE-auth`

### Pattern Clustering (Optional)

If you identify architectural patterns across multiple files:
- Create `CLUSTER-PATTERN-{pattern_name}`
- Examples: "CLUSTER-PATTERN-missing-input-validation", "CLUSTER-PATTERN-insecure-deserialization"

## Output Format

Write triage results to `docs/security/triage-results.json`:

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
      "detection_time": 17
    }
  }
]
```

Sort results by risk_score descending (highest risk first).

## Interactive Mode (Optional)

If user requests interactive confirmation:

1. Display each finding with:
   - File:line location (syntax highlighted)
   - AI classification + confidence
   - AI reasoning

2. Prompt: "Accept (y), Override (o), Skip (s), More info (?)"

3. If override:
   - Ask for correct classification (TP/FP/NI)
   - Ask for reason
   - Save feedback to `~/.specify/triage_feedback.jsonl`

4. Update classification based on user input

## Knowledge Base

Reference the following files for CWE patterns and triage guidelines:

- `memory/security/triage-guidelines.md` - Classification rules and explanation format
- `memory/security/cwe-knowledge.md` - CWE patterns and remediation guidance

## Success Criteria

- Classify all findings as TP/FP/NI with confidence scores
- Calculate risk scores using risk scoring formula
- Generate clear, actionable explanations
- Cluster related findings (3+ per cluster)
- Sort by risk score (highest first)
- Target >85% accuracy on benchmark dataset

## Example Workflow

```bash
# User runs triage command
/jpspec:security_triage

# You execute:
1. Read docs/security/findings.json
2. For each finding:
   - Read code context from file
   - Classify using triage guidelines
   - Calculate risk score using formula
   - Generate explanation
3. Cluster findings by CWE/file/pattern
4. Sort by risk_score descending
5. Write to docs/security/triage-results.json
6. Report summary to user
```

## Notes

- This is a SKILL, not Python code. You (Claude Code) execute the logic natively.
- No LLM API calls from Python. All AI reasoning happens in this skill.
- Python code only handles data structures (Finding, TriageResult) and file I/O.
- Use Read tool to view code context, Bash tool for git blame.
- Apply domain knowledge from memory/security/ guidelines.
