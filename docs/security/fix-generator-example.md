# Fix Generator Example Usage

This document demonstrates the complete workflow for automated security fix generation and application.

## Overview

The fix generator provides:
1. **Pattern Library** - Common vulnerability fix patterns for CWE-89, CWE-79, CWE-22, CWE-798, CWE-327
2. **AI-Powered Generation** - LLM-based fix generation with before/after code and unified diffs
3. **Syntax Validation** - Python and JavaScript syntax checking
4. **Patch Application** - Interactive or automated patch application with rollback support
5. **Patch Files** - Generate .patch files for version control

## Basic Usage

### 1. Generate a Fix

```python
from specify_cli.security.models import Finding, Location, Severity
from specify_cli.security.fixer import FixGenerator
from pathlib import Path

# Create a finding (typically from a security scanner)
finding = Finding(
    id="SQL-001",
    scanner="semgrep",
    severity=Severity.HIGH,
    title="SQL Injection",
    description="Unsanitized user input in SQL query",
    location=Location(
        file=Path("app/database.py"),
        line_start=42,
        line_end=42,
        code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
    ),
    cwe_id="CWE-89",
)

# Generate fix with LLM
generator = FixGenerator(llm_client=your_llm_client)
fix_result = generator.generate_fix(finding)

if fix_result.is_successful:
    print(f"Fix generated with {fix_result.confidence:.0%} confidence")
    print(f"Original: {fix_result.patch.original_code}")
    print(f"Fixed: {fix_result.patch.fixed_code}")
    print(f"Explanation: {fix_result.explanation}")
```

### 2. Apply the Fix

```python
from specify_cli.security.fixer import PatchApplicator

# Interactive mode with confirmation
applicator = PatchApplicator(create_backups=True)
apply_result = applicator.apply_fix(fix_result, confirm=True)

if apply_result.is_successful:
    print(f"✓ Applied fix to {apply_result.file_path}")
    print(f"Backup saved to: {apply_result.backup_path}")
```

### 3. Generate Patch Files

```python
from pathlib import Path

# Save patches for review/version control
patch_dir = Path("docs/security/patches")
patch_files = applicator.save_patches([fix_result], patch_dir)

print(f"Generated {len(patch_files)} patch files:")
for patch_file in patch_files:
    print(f"  - {patch_file}")
```

### 4. Rollback if Needed

```python
# Rollback a previously applied patch
success = applicator.rollback(apply_result)
if success:
    print("✓ Successfully rolled back changes")
```

## Complete Workflow Example

```python
from pathlib import Path
from specify_cli.security.models import Finding, Location, Severity
from specify_cli.security.fixer import FixGenerator, PatchApplicator

# Step 1: Create findings (typically from scanner output)
findings = [
    Finding(
        id="SQL-001",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="SQL Injection",
        description="Unsanitized user input in SQL query",
        location=Location(
            file=Path("app/database.py"),
            line_start=42,
            line_end=42,
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
        ),
        cwe_id="CWE-89",
    ),
    Finding(
        id="XSS-001",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="Cross-Site Scripting",
        description="Unescaped user input in HTML",
        location=Location(
            file=Path("app/views.js"),
            line_start=15,
            line_end=15,
            code_snippet="element.innerHTML = userInput;",
        ),
        cwe_id="CWE-79",
    ),
]

# Step 2: Generate fixes
generator = FixGenerator(llm_client=your_llm_client)
fix_results = generator.generate_fixes(findings)

# Step 3: Review fix quality
high_quality_fixes = [f for f in fix_results if f.confidence >= 0.75]
needs_review = [f for f in fix_results if f.needs_review]

print(f"Generated {len(fix_results)} fixes:")
print(f"  High quality: {len(high_quality_fixes)} (>75% confidence)")
print(f"  Needs review: {len(needs_review)}")

# Step 4: Save patch files for review
patch_dir = Path("docs/security/patches")
applicator = PatchApplicator(create_backups=True)
patch_files = applicator.save_patches(fix_results, patch_dir)
print(f"\nSaved {len(patch_files)} patch files to {patch_dir}")

# Step 5: Apply fixes (with confirmation)
apply_results = applicator.apply_multiple(fix_results, confirm=True)

successful = [r for r in apply_results if r.is_successful]
print(f"\nApplied {len(successful)} of {len(apply_results)} patches")
```

## Dry Run Mode

Test patches without modifying files:

```python
# Dry run - validate patches without applying
applicator = PatchApplicator(dry_run=True)
results = applicator.apply_multiple(fix_results, confirm=False)

for result in results:
    if result.status == ApplyStatus.SUCCESS:
        print(f"✓ {result.file_path} - patch would apply cleanly")
    elif result.status == ApplyStatus.CONFLICT:
        print(f"⚠ {result.file_path} - conflict detected")
```

## Pattern-Based Fixes (No LLM Required)

The fix generator can work without an LLM using pattern matching:

```python
# No LLM - uses pattern library only
generator = FixGenerator()  # llm_client=None
fix_result = generator.generate_fix(finding)

# Will return pattern-based guidance even if exact match not found
print(fix_result.explanation)  # Shows fix pattern guidance
```

## Fix Quality Metrics

The generator provides confidence scores to assess fix quality:

- **High confidence (0.9-1.0)**: Pattern match + AI confirmation, valid syntax
- **Medium confidence (0.7-0.9)**: AI-generated, validated syntax
- **Low confidence (<0.7)**: Uncertain or failed validation

```python
# Check fix quality
if fix_result.confidence >= 0.75:
    print("High quality fix - safe to apply")
elif fix_result.needs_review:
    print("Manual review recommended")
    for warning in fix_result.warnings:
        print(f"  ⚠ {warning}")
```

## Supported Vulnerability Types

### CWE-89: SQL Injection
- String concatenation → Parameterized queries
- String formatting → Prepared statements
- ORM raw queries → ORM safe methods

### CWE-79: Cross-Site Scripting (XSS)
- innerHTML → textContent
- Unescaped templates → Escaped output
- dangerouslySetInnerHTML → Safe rendering

### CWE-22: Path Traversal
- Direct path concatenation → Path sanitization
- User-controlled paths → Whitelist validation

### CWE-798: Hardcoded Secrets
- Inline secrets → Environment variables
- Config file secrets → Secret management

### CWE-327: Weak Cryptography
- MD5/SHA1 → SHA256/Argon2/bcrypt
- ECB mode → GCM mode
- Short keys → 256-bit keys

## Testing Fix Quality (AC #5)

To verify fix quality >75%:

```python
# Run on 30+ real vulnerabilities
test_findings = load_test_findings()  # Your vulnerability dataset
generator = FixGenerator(llm_client=your_llm_client)
fix_results = generator.generate_fixes(test_findings)

# Calculate quality metrics
total = len(fix_results)
high_quality = len([f for f in fix_results if f.confidence >= 0.75])
quality_rate = high_quality / total if total > 0 else 0.0

print(f"Fix quality: {quality_rate:.1%}")
print(f"High quality fixes: {high_quality}/{total}")

# Manual review
for result in fix_results[:10]:  # Review sample
    print(f"\nFinding: {result.finding_id}")
    print(f"Confidence: {result.confidence:.0%}")
    if result.patch:
        print(f"Original: {result.patch.original_code[:50]}...")
        print(f"Fixed: {result.patch.fixed_code[:50]}...")
    # Manually verify correctness
```

## Integration with Security Scanner

```python
from specify_cli.security.orchestrator import SecurityOrchestrator
from specify_cli.security.fixer import FixGenerator, PatchApplicator

# Run security scan
orchestrator = SecurityOrchestrator()
scan_result = orchestrator.scan(Path("."))

# Generate fixes for all findings
generator = FixGenerator(llm_client=your_llm_client)
fix_results = generator.generate_fixes(scan_result.findings)

# Apply high-confidence fixes automatically
applicator = PatchApplicator(create_backups=True)
auto_apply = [f for f in fix_results if f.confidence >= 0.9]
manual_review = [f for f in fix_results if 0.7 <= f.confidence < 0.9]

# Auto-apply high confidence
applicator.apply_multiple(auto_apply, confirm=False)

# Save patches for manual review
patch_dir = Path("docs/security/patches/manual-review")
applicator.save_patches(manual_review, patch_dir)

print(f"Auto-applied: {len(auto_apply)} fixes")
print(f"Manual review: {len(manual_review)} patches in {patch_dir}")
```

## See Also

- [Fix Pattern Library](../reference/fix-patterns.md)
- [Security Scanner Integration](../guides/security-scanner.md)
- [ADR-006: AI Triage Engine Design](../../memory/adr/adr-006-ai-triage-engine.md)
