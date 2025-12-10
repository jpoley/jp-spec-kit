---
description: Generate and apply security patches for vulnerability findings from triage results.
---

# /jpspec:security fix - Automated Security Fix Generation

Generate secure code patches for vulnerability findings, validate syntax, and optionally apply patches.

## User Input

```text
$ARGUMENTS
```

**Expected Input**: Optional arguments:
- No arguments: Process all TP findings from latest triage
- `--finding <id>`: Fix specific finding (e.g., `--finding SQL-001`)
- `--apply`: Automatically apply patches after generation
- `--review`: Show patches for manual review before applying

**Default behavior**: Generate patches for all True Positive (TP) findings without auto-applying.

## Prerequisites

This command requires:
1. Triage results exist at `docs/security/triage-results.json`
2. Run `/jpspec:security triage` first if triage results don't exist

## Workflow Overview

1. **Load Triage Results** - Read findings from triage-results.json
2. **Filter TP Findings** - Only process True Positive findings
3. **Generate Patches** - Use security-fixer skill to create fixes
4. **Validate Patches** - Check syntax and completeness
5. **Apply Patches** - Optionally apply with confirmation
6. **Report Results** - Summary of generated/applied patches

## Execution Instructions

### Phase 1: Load and Validate Triage Results

**Report progress**: Print "Phase 1: Loading triage results..."

```bash
# Check if triage results exist
if [ ! -f "docs/security/triage-results.json" ]; then
  echo "❌ Error: Triage results not found at docs/security/triage-results.json"
  echo "Run /jpspec:security triage first to generate triage results."
  exit 1
fi

# Read and parse JSON
cat docs/security/triage-results.json
```

**Parse JSON structure**:
```json
{
  "findings": [
    {
      "id": "SQL-001",
      "cwe": "CWE-89",
      "severity": "High",
      "classification": "TP",
      "file": "src/api/users.py",
      "line": 42,
      "code": "cursor.execute(f\"SELECT * FROM users WHERE id = {user_id}\")",
      "description": "SQL injection via string formatting"
    }
  ]
}
```

**Filter for TP findings**:
- Extract findings where `classification == "TP"`
- If no TP findings, report: "No True Positive findings to fix. Triage may have classified all as FP or require human review."

**Phase 1 Success**:
```
✅ Phase 1 Complete: Loaded triage results
   Total findings: 12
   True Positives: 5
   Findings to fix: 5
```

---

### Phase 2: Generate Patches for Each Finding

**Report progress**: Print "Phase 2: Generating security patches using AI skill..."

For each True Positive finding, invoke the **security-fixer skill** to generate a patch.

#### Context for Security-Fixer Skill

Provide the following context when invoking the skill:

```markdown
# Security Fix Generation Task

## Finding Details
- **ID**: {finding.id}
- **CWE**: {finding.cwe}
- **Severity**: {finding.severity}
- **File**: {finding.file}
- **Line**: {finding.line}
- **Description**: {finding.description}

## Vulnerable Code
```{language}
{finding.code}
```

## Fix Requirements

1. Generate secure alternative using framework best practices
2. Create unified diff format patch
3. Preserve functionality and API contracts
4. Add brief comment explaining the fix
5. Ensure syntactically valid code

## Output Format

Generate a patch file with:
- File path and line numbers
- Before/after code with context
- Unified diff format (for git apply)
- Fix explanation comment

Refer to memory/security/fix-patterns.md for secure alternatives by CWE category.
```

#### Reading Source Files

For context, read the full source file:

```bash
# Read vulnerable file for context
cat {finding.file}
```

Provide 10 lines before and after the vulnerable line for context when generating the patch.

#### Generated Patch Format

Each patch should follow unified diff format:

```diff
--- a/src/api/users.py
+++ b/src/api/users.py
@@ -40,7 +40,8 @@ def get_user(user_id):
     """Retrieve user by ID."""
     conn = get_db_connection()
     cursor = conn.cursor()
-    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
+    # Security fix: Prevent SQL injection by using parameterized queries (CWE-89)
+    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
     return cursor.fetchone()
```

#### Write Patch Files

```bash
# Create patches directory
mkdir -p docs/security/patches

# Write patch file
cat > docs/security/patches/{finding.id}.patch << 'EOF'
{generated_patch}
EOF
```

**Phase 2 Success**:
```
✅ Phase 2 Complete: Generated 5 patches
   SQL-001: docs/security/patches/SQL-001.patch
   XSS-001: docs/security/patches/XSS-001.patch
   PATH-001: docs/security/patches/PATH-001.patch
   SECRET-001: docs/security/patches/SECRET-001.patch
   CRYPTO-001: docs/security/patches/CRYPTO-001.patch
```

---

### Phase 3: Validate Generated Patches

**Report progress**: Print "Phase 3: Validating patch syntax and completeness..."

For each generated patch:

1. **Syntax validation** - Ensure patch format is valid
2. **File existence** - Verify target file exists
3. **Dry-run application** - Test patch applies cleanly

```bash
# Check patch format
if ! grep -q '^---' docs/security/patches/{finding.id}.patch; then
  echo "⚠️  Warning: Patch {finding.id}.patch may have invalid format"
fi

# Dry-run patch application
git apply --check docs/security/patches/{finding.id}.patch 2>&1
```

**Validation results**:
- **Valid**: Patch format correct, applies cleanly
- **Warning**: Patch format valid but may have conflicts
- **Error**: Patch is malformed or cannot apply

**Phase 3 Success**:
```
✅ Phase 3 Complete: Patch validation results
   Valid: 4 patches
   Warnings: 1 patch (SQL-001: line offset)
   Errors: 0 patches
```

If any patches have errors, halt and report which patches failed validation.

---

### Phase 4: Apply Patches (Optional)

**Report progress**: Print "Phase 4: Applying patches..."

**Important**: Only execute this phase if `--apply` flag provided or user confirms.

#### Request Confirmation

If `--apply` not provided, ask user:

```
Generated 5 patches in docs/security/patches/

Apply patches now? [y/N]:
```

- If user enters `y` or `yes`: Proceed with application
- If user enters anything else: Skip to Phase 5

#### Apply Each Patch

```bash
# Apply patch
git apply docs/security/patches/{finding.id}.patch

# Check if successful
if [ $? -eq 0 ]; then
  echo "✅ Applied: {finding.id}.patch"
else
  echo "❌ Failed: {finding.id}.patch (conflicts or errors)"
fi
```

**Conflict handling**:
- If patch fails to apply, keep patch file for manual review
- Don't abort entire process - continue with remaining patches
- Report which patches failed at the end

**Phase 4 Success**:
```
✅ Phase 4 Complete: Applied 4/5 patches
   Applied: SQL-001, XSS-001, PATH-001, CRYPTO-001
   Failed: SECRET-001 (manual review required)

Manual review needed for:
- docs/security/patches/SECRET-001.patch (merge conflict at line 18)
```

---

### Phase 5: Update Triage Results

**Report progress**: Print "Phase 5: Updating triage results with fix status..."

Update `docs/security/triage-results.json` to mark fixed findings:

```python
# Pseudocode for updating JSON
for finding in applied_patches:
    finding['fixed'] = True
    finding['fix_date'] = current_timestamp
    finding['patch_file'] = f"docs/security/patches/{finding['id']}.patch"

# Write updated JSON
write_json('docs/security/triage-results.json', triage_results)
```

**Phase 5 Success**:
```
✅ Phase 5 Complete: Updated triage results
   Marked 4 findings as fixed
```

---

### Phase 6: Generate Fix Summary Report

**Report progress**: Print "Phase 6: Generating fix summary report..."

Create human-readable report at `docs/security/fix-summary.md`:

```markdown
# Security Fix Summary

**Generated**: {timestamp}
**Triage Source**: docs/security/triage-results.json

## Overview

- **Total TP Findings**: 5
- **Patches Generated**: 5
- **Patches Applied**: 4
- **Manual Review Needed**: 1

## Successfully Fixed

### SQL-001: SQL Injection in user authentication
- **File**: src/api/users.py
- **Line**: 42
- **Severity**: High
- **Fix**: Replaced string formatting with parameterized queries
- **Patch**: docs/security/patches/SQL-001.patch
- **Status**: ✅ Applied

### XSS-001: Cross-Site Scripting in user comments
- **File**: src/views/comments.py
- **Line**: 87
- **Severity**: High
- **Fix**: Added output encoding using Flask escape()
- **Patch**: docs/security/patches/XSS-001.patch
- **Status**: ✅ Applied

[... additional findings ...]

## Requires Manual Review

### SECRET-001: Hardcoded API key in config
- **File**: src/config.py
- **Line**: 12
- **Severity**: Critical
- **Fix**: Moved to environment variable
- **Patch**: docs/security/patches/SECRET-001.patch
- **Status**: ⚠️ Merge conflict - manual review required
- **Notes**: Conflict at line 18 - config structure changed since scan

## Next Steps

1. Review and manually apply failed patches:
   - docs/security/patches/SECRET-001.patch

2. Run tests to verify fixes don't break functionality:
   ```bash
   pytest tests/
   ```

3. Re-run security scan to verify fixes:
   ```bash
   /jpspec:security scan
   ```

4. Commit changes:
   ```bash
   git add -A
   git commit -m "fix: apply security patches from triage (4/5 applied)"
   ```
```

Write report to `docs/security/fix-summary.md`.

**Phase 6 Success**:
```
✅ Phase 6 Complete: Fix summary report generated
   Report: docs/security/fix-summary.md
```

---

## Final Summary

Display comprehensive summary:

```
================================================================================
SECURITY FIX WORKFLOW COMPLETE
================================================================================

Triage Results: docs/security/triage-results.json
True Positive Findings: 5

Patch Generation:
✅ Generated: 5 patches
   Location: docs/security/patches/

Patch Application:
✅ Applied: 4 patches
⚠️  Manual Review: 1 patch (SECRET-001)

Fix Summary Report:
📄 docs/security/fix-summary.md

Next Steps:
1. Review failed patches and apply manually
2. Run tests: pytest tests/
3. Re-run security scan: /jpspec:security scan
4. Commit fixes: git commit -m "fix: security patches"
================================================================================
```

---

## Error Handling

### No Triage Results

```
❌ Error: Triage results not found

Required file: docs/security/triage-results.json

Run triage first:
  /jpspec:security triage

Then retry:
  /jpspec:security fix
```

### No True Positives

```
✅ No fixes needed

All findings were classified as False Positives or require human review.

Triage results: docs/security/triage-results.json
```

### Patch Generation Failed

```
❌ Error: Failed to generate patch for {finding.id}

Finding details:
- File: {file}
- Line: {line}
- CWE: {cwe}

Possible causes:
- Source file was modified since scan
- Complex code pattern requires manual fix
- Insufficient context for AI patch generation

Next steps:
1. Review finding manually
2. Create custom patch
3. Re-run: /jpspec:security fix --finding {finding.id}
```

### Patch Application Failed

```
⚠️  Warning: Patch {finding.id} failed to apply

Patch file: docs/security/patches/{finding.id}.patch

Possible causes:
- Source file changed since patch generation
- Merge conflict with other changes
- Line numbers shifted

Next steps:
1. Review patch file manually
2. Apply patch with conflict resolution:
   git apply --reject docs/security/patches/{finding.id}.patch
3. Resolve conflicts in *.rej files
```

---

## Help Text

**Command**: `/jpspec:security fix [options]`

**Purpose**: Generate and apply security patches for vulnerability findings from triage.

**Options**:
- (no arguments): Process all TP findings from latest triage
- `--finding <id>`: Fix specific finding (e.g., `--finding SQL-001`)
- `--apply`: Automatically apply patches after generation
- `--review`: Show patches for review before applying

**Examples**:

```bash
# Generate patches for all TP findings (no auto-apply)
/jpspec:security fix

# Generate and apply all patches
/jpspec:security fix --apply

# Fix specific finding
/jpspec:security fix --finding SQL-001

# Generate patches with review
/jpspec:security fix --review
```

**Prerequisites**:
- Triage results must exist: `docs/security/triage-results.json`
- Run `/jpspec:security triage` first if needed

**Output**:
- Patch files: `docs/security/patches/{finding-id}.patch`
- Fix summary: `docs/security/fix-summary.md`
- Updated triage results: `docs/security/triage-results.json`

**Workflow**:
1. Load triage results and filter TP findings
2. Generate patches using security-fixer skill
3. Validate patch syntax and applicability
4. Apply patches (with confirmation)
5. Update triage results
6. Generate fix summary report

**See Also**:
- `/jpspec:security scan` - Run security scanners
- `/jpspec:security triage` - Classify and prioritize findings
- `memory/security/fix-patterns.md` - Common fix patterns
