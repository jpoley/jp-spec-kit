# AI Triage Engine Benchmark Dataset

## Overview

This dataset contains 115 curated security findings with ground truth labels for benchmarking the AI triage engine's classification accuracy. Each finding has been manually reviewed by security experts to determine the correct classification (TP/FP/NI).

## Methodology

### Dataset Creation Process

1. **Vulnerability Selection**: Selected real-world vulnerability patterns from common CWE categories
2. **Ground Truth Labeling**: Security experts manually classified each finding based on:
   - Code pattern analysis
   - Security impact assessment
   - Exploitability evaluation
   - Context understanding
3. **Diversity Criteria**: Ensured balanced representation across:
   - Vulnerability types (5 major CWEs)
   - Classification outcomes (TP/FP/NI mix)
   - Complexity levels (simple to complex patterns)
   - Programming languages and frameworks

### Classification Criteria

**True Positive (TP)**:
- Exploitable vulnerability exists
- User input reaches vulnerable code path
- No adequate sanitization or validation
- Clear security impact

**False Positive (FP)**:
- Appears vulnerable but protected by:
  - Parameterized queries
  - Input validation/sanitization
  - Framework protections
  - Correct use of security APIs
- OR: Scanner misidentified safe pattern

**Needs Investigation (NI)**:
- Insufficient context to determine
- Depends on runtime behavior
- Requires understanding of external dependencies
- Partial mitigations present but uncertain effectiveness

## Dataset Statistics

### Overall Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| **Total Findings** | 115 | 100% |
| SQL Injection (CWE-89) | 23 | 20% |
| XSS (CWE-79) | 23 | 20% |
| Path Traversal (CWE-22) | 23 | 20% |
| Hardcoded Secrets (CWE-798) | 23 | 20% |
| Weak Crypto (CWE-327) | 23 | 20% |

### Classification Distribution

Per category breakdown (approximate):

- **True Positives**: ~60-65% (real vulnerabilities)
- **False Positives**: ~25-30% (safe patterns)
- **Needs Investigation**: ~10-15% (uncertain cases)

This distribution reflects real-world security scanner output where most findings are actionable but some require human judgment.

## Dataset Structure

### File Format

The dataset is stored in `ground_truth.json` with the following structure:

```json
{
  "metadata": {
    "created": "2025-12-05",
    "version": "1.0",
    "expert_reviewers": ["security-expert-1"],
    "total_findings": 115
  },
  "findings": [
    {
      "id": "BENCH-XXX-001",
      "cwe_id": "CWE-XX",
      "title": "Vulnerability description",
      "scanner": "benchmark",
      "severity": "critical|high|medium|low",
      "description": "Detailed explanation",
      "file": "example.py",
      "line_start": 42,
      "line_end": 42,
      "code_snippet": "vulnerable_code_here",
      "ground_truth": {
        "classification": "TP|FP|NI",
        "reasoning": "Expert explanation",
        "severity": "actual severity"
      }
    }
  ]
}
```

### ID Convention

- `BENCH-SQL-XXX`: SQL Injection findings
- `BENCH-XSS-XXX`: Cross-Site Scripting findings
- `BENCH-PATH-XXX`: Path Traversal findings
- `BENCH-SECRET-XXX`: Hardcoded Secrets findings
- `BENCH-CRYPTO-XXX`: Weak Cryptography findings

## Vulnerability Type Details

### SQL Injection (CWE-89)

**True Positives** include:
- String concatenation in queries
- f-string interpolation
- .format() method usage
- % formatting
- Dynamic ORDER BY, LIMIT, table names
- Unsafe INSERT, UPDATE, DELETE statements

**False Positives** include:
- Parameterized queries (?, $1, :param)
- Prepared statements
- ORM-generated queries
- Named parameters

**Edge Cases** (NI):
- Query builders (depends on implementation)
- Dynamic queries with unclear sanitization
- Partial parameterization

### Cross-Site Scripting (CWE-79)

**True Positives** include:
- innerHTML with user input
- document.write()
- eval() with user data
- dangerouslySetInnerHTML in React
- javascript: protocol in hrefs
- Event handler attributes (onerror, onclick)
- jQuery html() method
- v-html in Vue

**False Positives** include:
- textContent assignment
- Escaped template literals
- createElement + textContent
- jQuery text() method
- Vue normal interpolation
- DOMPurify sanitization

**Edge Cases** (NI):
- Server-side templates (depends on engine)
- Framework defaults (need verification)

### Path Traversal (CWE-22)

**True Positives** include:
- Direct path concatenation
- os.path.join with user input
- f-string path construction
- open() with user path
- Path() / operator
- Archive extraction without validation
- sendfile with user path
- os.remove with user path

**False Positives** include:
- realpath + startswith validation
- Whitelist validation
- send_from_directory
- basename extraction
- UUID-based filenames
- secure_filename() usage

**Edge Cases** (NI):
- Custom sanitization (may have bypasses)
- Regex validation (depends on completeness)
- Partial mitigations

### Hardcoded Secrets (CWE-798)

**True Positives** include:
- AWS access keys
- Database passwords
- API keys
- JWT secrets
- SSH private keys
- Encryption keys
- OAuth secrets
- Admin credentials
- GitHub tokens
- SMTP passwords
- Session secret keys

**False Positives** include:
- Environment variable reads
- Config file references
- Public keys
- Password hashes (not passwords)
- Secrets manager API calls

**Edge Cases** (NI):
- Example/placeholder values
- Constants that might be secrets
- Base64 encoded strings (need decoding)

### Weak Cryptography (CWE-327)

**True Positives** include:
- MD5 for password hashing
- SHA1 for passwords
- DES encryption
- ECB mode
- RC4 cipher
- Weak RSA keys (<2048 bits)
- NULL cipher suites
- Insecure random (random module)
- No salt in hashes
- Static IVs
- Custom crypto implementations
- Old TLS versions
- Disabled certificate validation

**False Positives** include:
- bcrypt password hashing
- SHA256 for file integrity
- RSA 4096 bits
- AES-256-GCM
- secrets module
- Random IV generation
- Modern TLS (1.2+)

**Edge Cases** (NI):
- Third-party crypto libraries (unknown quality)
- Algorithms with weak parameters

## Benchmark Usage

### Running the Benchmark

```bash
python scripts/benchmark_triage.py \
  --dataset tests/fixtures/benchmark_dataset/ground_truth.json \
  --report docs/reports/triage-benchmark.md
```

### Expected Accuracy

Based on the classifier heuristics and AI capabilities:

- **Overall Target**: >85% accuracy
- **Per-Classifier Targets**:
  - SQL Injection: >90% (strong heuristics)
  - XSS: >85% (good pattern matching)
  - Path Traversal: >80% (some edge cases)
  - Hardcoded Secrets: >90% (clear patterns)
  - Weak Crypto: >85% (well-defined)

### Failure Analysis

Common failure modes to watch for:

1. **False Negatives**: Classifying TP as FP
   - Context-dependent vulnerabilities
   - Novel attack patterns
   - Subtle injection points

2. **False Positives**: Classifying FP as TP
   - Over-aggressive pattern matching
   - Missing sanitization functions
   - Framework protections not recognized

3. **Over-cautious**: Classifying clear TP/FP as NI
   - Conservative confidence thresholds
   - LLM uncertainty
   - Insufficient heuristic coverage

## Maintenance

### Updating the Dataset

When adding new findings:

1. Ensure diversity across categories
2. Include expert reasoning in ground_truth
3. Update metadata counts
4. Re-run benchmark to verify impact
5. Document any new patterns discovered

### Version History

- **v1.0** (2025-12-05): Initial dataset with 115 findings across 5 CWE categories

## References

- CWE-89: SQL Injection - https://cwe.mitre.org/data/definitions/89.html
- CWE-79: Cross-Site Scripting - https://cwe.mitre.org/data/definitions/79.html
- CWE-22: Path Traversal - https://cwe.mitre.org/data/definitions/22.html
- CWE-798: Hardcoded Credentials - https://cwe.mitre.org/data/definitions/798.html
- CWE-327: Weak Crypto - https://cwe.mitre.org/data/definitions/327.html
- OWASP Top 10: https://owasp.org/www-project-top-ten/
