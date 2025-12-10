# AI Triage Engine Benchmark Report

**Date**: 2025-12-05
**Dataset Version**: 1.0
**Total Findings**: 115

## Executive Summary

- **Overall Accuracy**: 57.39% (66/115 correct)
- **Target**: 85% accuracy
- **Status**: ✗ FAIL

### Quick Metrics

| Metric | Value |
|--------|-------|
| Accuracy | 57.39% |
| TP Precision | 93.02% |
| TP Recall | 56.34% |
| TP F1 Score | 70.18% |
| FP Precision | 62.96% |
| FP Recall | 53.12% |
| FP F1 Score | 57.63% |

## Per-Classifier Accuracy

| CWE | Description | Accuracy | Correct/Total |
|-----|-------------|----------|---------------|
| CWE-22 | Path Traversal | ✗ 47.83% | 11/23 |
| CWE-327 | Weak Cryptography | ✗ 43.48% | 10/23 |
| CWE-79 | Cross-Site Scripting | ✗ 47.83% | 11/23 |
| CWE-798 | Hardcoded Secrets | ✗ 60.87% | 14/23 |
| CWE-89 | SQL Injection | ✓ 86.96% | 20/23 |

## Confusion Matrix

|  | Predicted TP | Predicted FP | Predicted NI |
|---|--------------|--------------|--------------|
| **Actual TP** | 40 ✓ | 8 ✗ | 23 ~ |
| **Actual FP** | 2 ✗ | 17 ✓ | 13 ~ |
| **Actual NI** | 1 ~ | 2 ~ | 9 ✓ |

Legend:
- ✓ Correct classification
- ✗ Incorrect classification
- ~ Partial credit (NI is uncertain)

## Detailed Metrics

### True Positive Detection

| Metric | Value | Description |
|--------|-------|-------------|
| Precision | 93.02% | Of predicted TPs, how many are actually TP? |
| Recall | 56.34% | Of actual TPs, how many did we find? |
| F1 Score | 70.18% | Harmonic mean of precision and recall |

- True Positives: 40 (correctly identified vulnerabilities)
- False Positives: 3 (incorrectly flagged safe code)
- False Negatives: 31 (missed real vulnerabilities) ⚠️
- True Negatives: 41 (correctly identified safe code)

### False Positive Detection

| Metric | Value | Description |
|--------|-------|-------------|
| Precision | 62.96% | Of predicted FPs, how many are actually FP? |
| Recall | 53.12% | Of actual FPs, how many did we catch? |
| F1 Score | 57.63% | Harmonic mean of precision and recall |

## Failure Analysis

**Total Failures**: 49 (42.6%)

### Failure Breakdown by Type


#### TP → NI (23 failures)


**BENCH-SQL-004** (CWE-89)

- Ground Truth: TP
- Predicted: NI
- Confidence: 50%
- Code: `query = "SELECT * FROM products WHERE category = '%s'" % category`
- Reasoning: Could not determine query construction method.


**BENCH-XSS-009** (CWE-79)

- Ground Truth: TP
- Predicted: NI
- Confidence: 50%
- Code: `link.href = 'javascript:' + userCode;`
- Reasoning: Could not determine if output is properly encoded.


**BENCH-XSS-010** (CWE-79)

- Ground Truth: TP
- Predicted: NI
- Confidence: 50%
- Code: `img.setAttribute('onerror', errorHandler);`
- Reasoning: Could not determine if output is properly encoded.


**BENCH-XSS-012** (CWE-79)

- Ground Truth: TP
- Predicted: NI
- Confidence: 50%
- Code: `window.location.href = redirectUrl;`
- Reasoning: Could not determine if output is properly encoded.


**BENCH-XSS-013** (CWE-79)

- Ground Truth: TP
- Predicted: NI
- Confidence: 50%
- Code: `$('#content').html(userHtml);`
- Reasoning: Could not determine if output is properly encoded.


_... and 18 more similar failures_

#### FP → NI (13 failures)


**BENCH-SQL-007** (CWE-89)

- Ground Truth: FP
- Predicted: NI
- Confidence: 50%
- Code: `users = User.objects.filter(username=username)`
- Reasoning: Could not determine query construction method.


**BENCH-SQL-012** (CWE-89)

- Ground Truth: FP
- Predicted: NI
- Confidence: 60%
- Code: `cursor.execute("SELECT * FROM users WHERE email = :email", {'email': email})`
- Reasoning: Found execute() call. Check if query uses parameterized queries with params argument or string concatenation.


**BENCH-XSS-014** (CWE-79)

- Ground Truth: FP
- Predicted: NI
- Confidence: 50%
- Code: `$('#username').text(user.name);`
- Reasoning: Could not determine if output is properly encoded.


**BENCH-XSS-017** (CWE-79)

- Ground Truth: FP
- Predicted: NI
- Confidence: 50%
- Code: `<div>{{ username }}</div>`
- Reasoning: Could not determine if output is properly encoded.


**BENCH-XSS-021** (CWE-79)

- Ground Truth: FP
- Predicted: NI
- Confidence: 60%
- Code: `element.innerHTML = DOMPurify.sanitize(userHtml);`
- Reasoning: Found both dangerous sink (innerhtml) and encoding (sanitize). Cannot verify that encoding is applied to the dangerous sink. Manual review required.


_... and 8 more similar failures_

#### TP → FP (8 failures)


**BENCH-SECRET-004** (CWE-798)

- Ground Truth: TP
- Predicted: FP
- Confidence: 70%
- Code: `jwt.encode(payload, 'my-secret-key', algorithm='HS256')`
- Reasoning: Low entropy (3.03 bits/char). Likely not a real secret.


**BENCH-SECRET-008** (CWE-798)

- Ground Truth: TP
- Predicted: FP
- Confidence: 70%
- Code: `AES_KEY = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f'`
- Reasoning: Low entropy (3.01 bits/char). Likely not a real secret.


**BENCH-SECRET-010** (CWE-798)

- Ground Truth: TP
- Predicted: FP
- Confidence: 70%
- Code: `ADMIN_USER = 'admin'
ADMIN_PASS = 'Admin123!'`
- Reasoning: Low entropy (3.38 bits/char). Likely not a real secret.


**BENCH-SECRET-018** (CWE-798)

- Ground Truth: TP
- Predicted: FP
- Confidence: 70%
- Code: `redis_client = Redis(host='localhost', password='RedisPass123')`
- Reasoning: Low entropy (3.19 bits/char). Likely not a real secret.


**BENCH-SECRET-022** (CWE-798)

- Ground Truth: TP
- Predicted: FP
- Confidence: 70%
- Code: `config = {
    'apiKey': 'AIzaSyD...XXXX',
    'authDomain': 'app.firebaseapp.com',
    'projectId':...`
- Reasoning: Low entropy (2.90 bits/char). Likely not a real secret.


_... and 3 more similar failures_

#### FP → TP (2 failures)


**BENCH-XSS-006** (CWE-79)

- Ground Truth: FP
- Predicted: TP
- Confidence: 80%
- Code: `div.innerHTML = `<span>${escapeHtml(username)}</span>`;`
- Reasoning: Found dangerous sink: innerhtml. This pattern is vulnerable to XSS if input is not sanitized.


**BENCH-SECRET-014** (CWE-798)

- Ground Truth: FP
- Predicted: TP
- Confidence: 80%
- Code: `PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkq...
-----END PUBLIC KEY-----'''`
- Reasoning: High entropy (3.78 bits/char) secret in production code. This appears to be a real hardcoded credential.


#### NI → FP (2 failures)


**BENCH-SECRET-019** (CWE-798)

- Ground Truth: NI
- Predicted: FP
- Confidence: 70%
- Code: `API_TOKEN = 'abc123xyz'`
- Reasoning: Low entropy (3.17 bits/char). Likely not a real secret.


**BENCH-CRYPTO-023** (CWE-327)

- Ground Truth: NI
- Predicted: FP
- Confidence: 70%
- Code: `hash = argon2.hash_password(password, time_cost=1, memory_cost=8)`
- Reasoning: Safe algorithm detected: argon2.


#### NI → TP (1 failures)


**BENCH-SECRET-023** (CWE-798)

- Ground Truth: NI
- Predicted: TP
- Confidence: 80%
- Code: `TOKEN = 'YWRtaW46cGFzc3dvcmQxMjM='`
- Reasoning: High entropy (4.22 bits/char) secret in production code. This appears to be a real hardcoded credential.


## Recommendations


### CRITICAL: Accuracy Below Target (57.39% < 85%)

Priority improvements needed:

1. **CWE-327 (Weak Cryptography)**: 43.48% accuracy
   - Review classifier heuristics
   - Add more training examples
   - Improve LLM prompt

1. **CWE-79 (Cross-Site Scripting)**: 47.83% accuracy
   - Review classifier heuristics
   - Add more training examples
   - Improve LLM prompt

1. **CWE-22 (Path Traversal)**: 47.83% accuracy
   - Review classifier heuristics
   - Add more training examples
   - Improve LLM prompt

1. **CWE-798 (Hardcoded Secrets)**: 60.87% accuracy
   - Review classifier heuristics
   - Add more training examples
   - Improve LLM prompt


2. **False Negative Risk**: 8 real vulnerabilities classified as FP
   - Review conservative thresholds
   - Add patterns for missed vulnerability types


3. **False Positive Risk**: 2 safe patterns classified as TP
   - Add detection for safe patterns
   - Improve sanitization recognition

