---
id: task-213
title: Implement Automated Fix Generation and Patch Application
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-05 23:13'
labels:
  - security
  - implement
  - ai
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build AI-powered code patch generator for common vulnerability patterns. Enables /jpspec:security fix command.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Fix pattern library for SQL injection, XSS, path traversal, secrets, crypto
- [x] #2 AI generates patches with before/after code and unified diff
- [x] #3 Syntax validation of generated patches
- [x] #4 Patch application workflow with confirmation
- [ ] #5 Fix quality >75% (correct or mostly correct)
- [x] #6 Generate .patch files for each finding
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Automated Fix Generation and Patch Application

### Architecture Reference
- ADR-006: AI Triage Engine Design (fix generation section)
- Existing: src/specify_cli/security/fixer/generator.py (skeleton exists)
- Pattern: Strategy Pattern (different fix strategies per CWE)

### Current State Analysis
The fix generator has:
- FixGenerator class with LLM integration
- Pattern library support (FixPatternLibrary)
- Basic code context extraction
- Patch generation structure
- Syntax validation hooks

### Implementation Steps

#### Step 1: Complete Fix Pattern Library (4-6 hours)
**Files:**
- src/specify_cli/security/fixer/patterns.py
- Create pattern definitions for 5 CWE categories

**Tasks:**
1. SQL Injection (CWE-89) patterns
   - Raw SQL concatenation → Parameterized queries
   - String formatting in SQL → Prepared statements
   - ORM raw queries → ORM safe methods
   - Examples for: Python (psycopg2, SQLAlchemy), Node.js (pg, mysql2)
2. XSS (CWE-79) patterns
   - innerHTML assignment → textContent/innerText
   - Unescaped template variables → Escaped output
   - React dangerouslySetInnerHTML → Safe rendering
   - Examples for: React, Vue, vanilla JS, Jinja2
3. Path Traversal (CWE-22) patterns
   - Direct path concatenation → Path sanitization
   - User-controlled paths → Whitelist validation
   - Examples for: Python (pathlib), Node.js (path.join)
4. Hardcoded Secrets (CWE-798) patterns
   - Inline secrets → Environment variables
   - Config file secrets → Secret management (AWS SSM, Azure Key Vault)
   - Examples for: Python (os.environ), Node.js (process.env)
5. Weak Cryptography (CWE-327) patterns
   - MD5/SHA1 → SHA256/Argon2/bcrypt
   - ECB mode → GCM mode
   - Short keys → 256-bit keys
   - Examples for: Python (cryptography), Node.js (crypto)

**Pattern Structure:**
```python
FixPattern(
    cwe_id="CWE-89",
    name="SQL Injection - Parameterized Query",
    description="Replace string concatenation with parameterized queries",
    fix_template="Use ? placeholders and pass values separately",
    before_pattern=r".*cursor\.execute.*\+.*",
    after_template="cursor.execute(query, (param1, param2))",
    examples=[...],
    confidence=0.9
)
```

**Validation:**
- Create 20+ patterns total (4 per CWE)
- Test pattern matching against known vulnerable code

#### Step 2: Enhance AI Fix Generation (4-6 hours)
**Files:**
- src/specify_cli/security/fixer/generator.py

**Tasks:**
1. Improve fix generation prompt
   - Include finding description and CWE details
   - Provide code context (10 lines before/after)
   - Include pattern library guidance
   - Request step-by-step fix explanation
   - Specify language-specific best practices
2. Add multi-shot prompting
   - Include 2-3 examples from pattern library
   - Show before/after for similar vulnerabilities
3. Implement fix validation
   - Check syntax (use ast.parse for Python, esprima for JS)
   - Verify fix doesn't break functionality (heuristics)
   - Check fix actually addresses the vulnerability
4. Add confidence scoring
   - High (0.9-1.0): Pattern match + AI confirmation
   - Medium (0.7-0.9): AI-generated, validated syntax
   - Low (<0.7): AI-generated, unvalidated or uncertain

**Validation:**
- Generate fixes for 30 known vulnerabilities
- Verify syntax is valid
- Manual review of fix quality

#### Step 3: Implement Unified Diff Generation (2-3 hours)
**Files:**
- src/specify_cli/security/fixer/generator.py
- src/specify_cli/security/fixer/models.py

**Tasks:**
1. Implement patch file generation
   - Use difflib.unified_diff for Python
   - Generate .patch files in docs/security/patches/
   - Include context lines (3 lines before/after)
2. Add patch metadata
   - Finding ID, CWE, severity
   - Original scanner, triage result
   - Fix confidence score
   - Timestamp
3. Implement before/after preview
   - Show original code with line numbers
   - Show fixed code with line numbers
   - Highlight changed lines
4. Add patch validation
   - Verify patch can be applied (dry-run)
   - Check for merge conflicts
   - Validate file still exists

**Validation:**
- Generate patches for 10 findings
- Verify patches apply cleanly
- Test on modified files (detect conflicts)

#### Step 4: Implement Patch Application Workflow (3-4 hours)
**Files:**
- src/specify_cli/security/fixer/applicator.py (new)
- src/specify_cli/security/fixer/generator.py

**Tasks:**
1. Create PatchApplicator class
   - apply_patch(patch: Patch, dry_run: bool) method
   - Use subprocess to run: patch -p1 < patchfile
   - Fallback: manual file modification if patch fails
2. Implement confirmation workflow
   - Show patch preview with syntax highlighting
   - Display confidence score and warnings
   - Prompt: "Apply this patch? (y/n/e=edit/s=skip)"
   - Allow editing patch before applying
3. Implement batch application
   - Apply multiple patches in order
   - Track success/failure for each
   - Generate summary report
4. Add rollback mechanism
   - Create backups before applying (.orig files)
   - Implement undo functionality
   - Store patch history in .specify/patch_history.json

**Validation:**
- Apply 5 patches to test repository
- Test rollback functionality
- Test conflict detection and handling

#### Step 5: Language-Specific Fix Strategies (4-5 hours)
**Files:**
- src/specify_cli/security/fixer/strategies/ (new directory)
- Create: python_fixer.py, javascript_fixer.py, go_fixer.py

**Tasks:**
1. Implement Python fix strategy
   - Detect web framework (Flask, Django, FastAPI)
   - Use framework-specific patterns
   - Handle import additions (add missing libraries)
   - Respect PEP 8 style
2. Implement JavaScript/TypeScript strategy
   - Detect framework (React, Vue, Express)
   - Handle JSX syntax
   - Use ESLint-compatible formatting
3. Implement Go fix strategy
   - Detect standard library vs. third-party
   - Follow Go idioms
   - Handle package imports
4. Add language detection
   - Use file extension + content analysis
   - Select appropriate strategy
   - Fallback to generic strategy

**Validation:**
- Test fixes in Python, JS, Go codebases
- Verify fixes are idiomatic for each language

#### Step 6: Fix Quality Metrics (2-3 hours)
**Files:**
- src/specify_cli/security/fixer/validator.py (new)
- src/specify_cli/security/fixer/models.py

**Tasks:**
1. Implement syntax validation
   - Python: ast.parse()
   - JavaScript: run eslint or esprima
   - Go: run go vet
2. Implement semantic validation (heuristics)
   - Check fix actually addresses vulnerability
   - Verify no new security issues introduced
   - Check functionality preserved (no broken imports)
3. Add fix quality scoring
   - Syntax valid: +30 points
   - Pattern match: +30 points
   - AI confidence: +20 points
   - Semantic checks pass: +20 points
   - Total: 0-100 score
4. Generate fix report
   - List all fixes with scores
   - Highlight low-quality fixes for manual review
   - Include warnings and limitations

**Validation:**
- Score 20 generated fixes
- Verify scores correlate with manual assessment

#### Step 7: Integration and Testing (3-4 hours)
**Files:**
- tests/security/test_fix_generator.py
- tests/security/test_patch_applicator.py
- tests/security/test_integration.py

**Tasks:**
1. Create end-to-end test
   - Generate finding → Generate fix → Apply patch → Verify result
2. Test error handling
   - Invalid code context
   - Patch application failures
   - Syntax errors in generated fixes
3. Test rollback
   - Apply patch → Verify applied → Rollback → Verify reverted
4. Performance testing
   - 10 fixes should generate in <1 minute
5. Quality testing
   - Manual review of 30 generated fixes
   - Target: >75% correct or mostly correct

**Validation:**
- All tests pass
- Coverage >75%
- Fix quality meets target

### Dependencies
- Anthropic Python SDK (for LLM)
- difflib (stdlib) for patch generation
- patch command (system) for application
- ast (stdlib) for Python syntax validation
- subprocess for external tool integration

### Success Criteria
- [ ] Fix pattern library covers 5 CWE categories with 4+ patterns each
- [ ] AI generates syntactically valid fixes >95% of time
- [ ] Fix quality >75% (correct or mostly correct)
- [ ] Patches apply cleanly >90% of time
- [ ] Unified diff format matches GNU patch standard
- [ ] Rollback mechanism works reliably

### Risks & Mitigations
**Risk:** Generated fixes break functionality
**Mitigation:** 
- Conservative fix generation (minimal changes)
- Syntax validation before suggesting
- Dry-run mode by default
- Create backups before applying

**Risk:** Patch conflicts with recent code changes
**Mitigation:**
- Detect conflicts before applying
- Offer manual resolution
- Allow patch editing

**Risk:** Fix quality below 75%
**Mitigation:**
- Extensive pattern library reduces AI reliance
- Multi-shot prompting improves AI output
- Interactive mode allows manual refinement
- Confidence scores help users decide

### Estimated Effort
**Total: 22-31 hours (3-4 days)**
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Implemented automated fix generation and patch application for security vulnerabilities.

### Components Delivered

1. **Fix Pattern Library** (`patterns.py`)
   - 5 CWE categories: SQL injection, XSS, path traversal, hardcoded secrets, weak crypto
   - Before/after examples for Python and JavaScript

2. **AI Fix Generator** (`generator.py`)
   - LLM-powered fix generation with pattern guidance
   - Unified diff generation using difflib
   - Syntax validation for Python and JavaScript

3. **Patch Applicator** (`applicator.py`) - PR #568
   - PatchApplicator class with apply/rollback
   - Support for git apply and manual fallback
   - Backup creation and history tracking
   - Batch application support

4. **Test Coverage**
   - 57 tests covering all fixer modules
   - Models, patterns, generator, and applicator

### Files Changed
- `src/specify_cli/security/fixer/patterns.py`
- `src/specify_cli/security/fixer/generator.py`
- `src/specify_cli/security/fixer/models.py`
- `src/specify_cli/security/fixer/applicator.py` (new)
- `src/specify_cli/security/fixer/__init__.py`
- `tests/security/fixer/test_*.py`

### Note on AC#5
Fix quality >75% requires empirical validation with real vulnerabilities.
Follow-up task created for quality testing.
<!-- SECTION:NOTES:END -->
