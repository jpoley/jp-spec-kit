# CWE Knowledge Base

## SQL Injection (CWE-89, CWE-564)

### Detection Patterns
- String concatenation or interpolation in SQL queries
- User input flows to `execute()`, `query()`, `raw()`
- Dynamic query building without parameterization

### True Positive Indicators
- No use of parameterized queries or prepared statements
- Direct interpolation: `f"SELECT * FROM users WHERE id = {user_id}"`
- String concatenation: `"SELECT * FROM users WHERE name = '" + name + "'"`

### False Positive Indicators
- ORM usage (Django ORM, SQLAlchemy with session.query)
- Parameterized queries: `execute("SELECT * FROM users WHERE id = ?", (user_id,))`
- Input validation with strict allowlist before query

### Remediation
Use parameterized queries or prepared statements. Never build queries with string concatenation.

---

## Cross-Site Scripting (CWE-79, CWE-80)

### Detection Patterns
- User input rendered in HTML without escaping
- innerHTML, dangerouslySetInnerHTML, write() with user data
- Template rendering without auto-escape

### True Positive Indicators
- Direct HTML injection: `element.innerHTML = userInput`
- Disabled auto-escaping in templates: `{{ var | safe }}`
- JavaScript generation with user data: `var x = "${userInput}"`

### False Positive Indicators
- Framework with auto-escaping (React, Vue, Django templates)
- Explicit escaping: `escape(userInput)` or `html.escape()`
- Content Security Policy blocks inline scripts
- Output is not user-facing (logs, internal APIs)

### Remediation
Use frameworks with auto-escaping. For manual HTML generation, escape all user input. Implement CSP.

---

## Path Traversal (CWE-22, CWE-23, CWE-36, CWE-73)

### Detection Patterns
- User input used in file path operations
- open(), read_file(), include() with user-controlled paths
- No path validation or canonicalization

### True Positive Indicators
- Direct path concatenation: `open(f"/uploads/{filename}")`
- No validation of `../` sequences
- User controls full path, not just filename

### False Positive Indicators
- Path canonicalization and in-bounds check: resolve path with `os.path.realpath()` and verify it remains under the allowed base directory (e.g., `/uploads/`)
- User input is filename only, directory is hardcoded

### Remediation
Validate paths against allowlist. Use `os.path.basename()` to strip directory components. Check canonical path is within allowed directory.

---

## Hardcoded Secrets (CWE-798, CWE-259, CWE-321, CWE-522)

### Detection Patterns
- Literals that look like passwords, API keys, tokens
- Variable names like `password`, `api_key`, `secret`
- High-entropy strings (base64, hex)

### True Positive Indicators
- Actual credentials: `password = "admin123"`
- API keys: `api_key = "sk_live_abcdef12345"`
- Tokens with real format: `token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."`

### False Positive Indicators
- Example/dummy values: `password = "YOUR_PASSWORD_HERE"`
- Test credentials in test files: `test_password = "test123"`
- Encrypted/hashed values (not plaintext)
- Public keys (not secret keys)

### Remediation
Use environment variables or secret management systems (AWS Secrets Manager, HashiCorp Vault). Never commit secrets to version control.

---

## Weak Cryptography (CWE-327, CWE-328, CWE-326, CWE-916)

### Detection Patterns
- Use of deprecated algorithms (MD5, SHA1, DES, RC4)
- Weak key sizes (RSA <2048 bits, AES <128 bits)
- Insecure modes (ECB)

### True Positive Indicators
- MD5 or SHA1 for password hashing: `hashlib.md5(password)`
- DES encryption: `Cipher(algorithms.DES(key))`
- Small key sizes: `RSA.generate(512)`

### False Positive Indicators
- MD5/SHA1 for non-security purposes (checksums, ETags)
- Comment or documentation mentioning weak crypto
- Already using strong crypto (SHA256, bcrypt, AES-256-GCM)

### Remediation
- Password hashing: bcrypt, Argon2, scrypt
- Symmetric encryption: AES-256-GCM
- Hashing: SHA-256 or SHA-3
- Asymmetric: RSA 2048+ bits, ECDSA

---

## Confidence Calibration

### High Confidence (90-100%)
- Clear vulnerability pattern present
- No mitigations detected
- Known exploitable CWE
- Multiple indicators align

### Medium Confidence (70-89%)
- Vulnerability pattern present
- Some mitigations but incomplete
- Context suggests exploitability
- One or two conflicting indicators

### Low Confidence (50-69%)
- Weak vulnerability indicators
- Significant mitigations present
- Ambiguous context
- Missing dataflow information

Mark findings with below 70% confidence as NEEDS_INVESTIGATION.

---

## Common False Positive Causes

1. **Framework protection not detected**: Django ORM prevents SQL injection but scanner flags it
2. **Context misunderstanding**: Admin-only endpoint flagged but requires authentication
3. **Sanitization elsewhere**: Input validated in middleware but scanner checks endpoint only
4. **Test code**: Test files often have intentionally insecure code
5. **Comments and documentation**: Scanner finds "SQL injection" in a comment
6. **Dead code**: Code is unreachable or never executed

---

## Dataflow Analysis Heuristics

When analyzing code flow:

1. **Trace input sources**: HTTP params, form data, URL paths, cookies, headers
2. **Identify sinks**: SQL execute, file operations, system calls, HTML rendering
3. **Check sanitization layers**: Validation, escaping, allowlists between source and sink
4. **Consider framework protections**: Auto-escaping, ORM, CSP, CORS
5. **Evaluate attack surface**: Public endpoint vs authenticated, external vs internal

If dataflow is unclear, classify as NEEDS_INVESTIGATION rather than guessing.

---

## CWE to Impact Mapping

| CWE Category | Default Impact | Notes |
|--------------|----------------|-------|
| Injection (CWE-89, 78, 79) | 8-9 | High impact, often remote exploitation |
| Path Traversal (CWE-22) | 7-8 | Can expose sensitive files |
| Authentication (CWE-287, 798) | 9-10 | Critical, full account takeover |
| Cryptography (CWE-327, 328) | 6-8 | Depends on what's being protected |
| Information Disclosure (CWE-200) | 4-6 | Depends on sensitivity of data |
| DoS (CWE-400, 770) | 3-5 | Availability impact |
| Best Practices (CWE-1004) | 1-2 | No direct security impact |

Adjust based on context and CVSS if available.
