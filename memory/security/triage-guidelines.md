# Security Triage Guidelines

## Classification Rules

### True Positive (TP)
Classify as TP when:
- User input flows directly to dangerous sink (SQL, OS command, file path)
- No sanitization or validation between source and sink
- Finding matches known vulnerability patterns (e.g., SQL injection with string concatenation)
- Code lacks security controls (parameterized queries, escaping, allowlists)
- Attack scenario is feasible and realistic

### False Positive (FP)
Classify as FP when:
- Input is properly validated/sanitized before use
- Modern framework provides automatic protection (Django ORM, React auto-escaping)
- Code uses secure patterns (parameterized queries, prepared statements)
- Context makes exploitation impossible (hardcoded values, admin-only)
- Scanner misunderstood the code flow

### Needs Investigation (NI)
Classify as NI when:
- Insufficient context to determine if sanitization exists
- Complex dataflow requiring human analysis
- Partial mitigations present but uncertain if complete
- Confidence < 0.70

## Risk Scoring Formula

**risk_score = (impact × exploitability) / detection_time**

### Impact (0-10)
- **CRITICAL (9-10)**: RCE, Authentication bypass, Data breach
- **HIGH (7-8)**: SQL injection, XSS, Path traversal
- **MEDIUM (4-6)**: Information disclosure, DoS
- **LOW (1-3)**: Minor information leak
- **INFO (0)**: Best practice violations

Map from CVSS if available, otherwise estimate based on CWE.

### Exploitability (0-10)
- **10**: Public exploit available, trivial to exploit
- **8-9**: Easy to exploit, no special access needed
- **6-7**: Requires authentication or moderate skill
- **4-5**: Requires specific conditions or high skill
- **1-3**: Very difficult, requires deep knowledge

Consider:
- Attack complexity (low = higher score)
- Privileges required (none = higher score)
- User interaction (none = higher score)
- Network accessibility (remote = higher score)

### Detection Time (days)
- Use git blame to find when code was written
- More recent code = higher priority (lower denominator)
- If git unavailable, default to 30 days

**Example:**
- SQL injection (impact=8) + easy exploit (exploitability=9) + 10 days old = (8 × 9) / 10 = 7.2
- XSS (impact=7) + medium exploit (exploitability=6) + 10 days old = (7 × 6) / 10 = 4.2

## Clustering Strategy

### CWE Clustering
Group findings by CWE category when:
- 3+ findings share the same CWE
- Indicates systemic issue requiring architectural fix

Example: 5 SQL injections (CWE-89) → cluster suggests missing parameterized query policy

### File Clustering
Group findings by file when:
- 2+ findings in same file (different CWEs)
- Indicates problematic module needing refactor

Example: auth.py has SQL injection + XSS + hardcoded secret → security review needed

### Pattern Clustering
Group findings by architectural pattern when:
- Multiple findings share root cause across files
- Common patterns: "Missing input validation", "Insecure deserialization", "Insufficient logging"

Example: 8 findings all lack input validation → need framework-wide validation layer

## Explanation Format

Generate explanations in plain English for junior developers:

### What (1 sentence)
- Clear description of the vulnerability
- Avoid jargon, explain technical terms
- Example: "This code builds SQL queries by concatenating user input, allowing attackers to inject malicious SQL commands."

### Why It Matters (2-3 sentences)
- Real-world security impact
- Concrete consequences, not abstract risks
- Example: "An attacker could steal all user passwords, delete the database, or create admin accounts. This is a critical risk because the login form is publicly accessible."

### How to Exploit (TP only, 2-3 sentences)
- Specific attack scenario, not generic
- Show example payload
- Example: "An attacker enters `' OR 1=1 --` in the username field. This closes the SQL string and adds a condition that's always true, bypassing authentication."

### How to Fix (2-4 sentences)
- Concrete fix with code example
- Link to documentation or best practices
- Example: "Use parameterized queries: `cursor.execute('SELECT * FROM users WHERE username = ?', (username,))`. This prevents SQL injection by treating user input as data, not code."

Keep each section under 200 characters. Prioritize clarity over completeness.

## Interactive Triage Mode

When confirming AI decisions:

1. **Display Finding Context**
   - Show file:line with syntax highlighting
   - Show AI classification + confidence
   - Show AI reasoning

2. **Prompt for Confirmation**
   - Accept (y): Keep AI decision
   - Override (o): Provide correct classification
   - Skip (s): Come back to this later
   - More info (?): Show full code context

3. **Collect Feedback**
   - Store override reason for future prompt improvement
   - Format: `{finding_fingerprint, ai_classification, user_classification, reason}`
   - Save to `~/.specify/triage_feedback.jsonl`

## Accuracy Target

- Overall accuracy >85% on benchmark dataset
- Per-classifier accuracy >80% for specialized classifiers
- Confidence calibration: predictions with 90%+ confidence should be correct 90%+ of the time
- Findings below 70% confidence should be marked NEEDS_INVESTIGATION
