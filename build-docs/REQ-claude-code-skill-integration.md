# Requirement: Claude Code Skill Integration for Flow Commands

**Document ID:** REQ-CLAUDE-CODE-SKILLS
**Status:** Final (All 3 Reviews Complete)
**Created:** 2026-01-11
**Author:** Analysis by Claude Opus 4.5
**Reviews:** 3/3 complete

---

## Executive Summary

FlowSpec's `/flow:*` commands (e.g., `/flow:implement`, `/flow:plan`, `/flow:validate`) do not appear as available commands in Claude Code CLI. This occurs because FlowSpec generates GitHub Copilot prompt files (`.github/prompts/*.prompt.md`) but not Claude Code skill files (`.claude/skills/*/SKILL.md`). These are incompatible formats serving different AI coding assistants.

**Root Cause:** Claude Code and GitHub Copilot use different prompt/skill registration systems with different directory structures and frontmatter formats.

**Impact:** Users of FlowSpec who use Claude Code cannot invoke `/flow:*` commands - the commands simply don't exist from Claude Code's perspective.

---

## Problem Statement

### Observed Behavior

When a user types `/flow:implement` in Claude Code within a project that has FlowSpec installed:
- The command is not recognized
- The Skill tool's available skills list does not include any `flow:*` commands
- The files exist at `.github/prompts/flow.*.prompt.md` but Claude Code cannot see them

### Expected Behavior

Users should be able to invoke `/flow:implement`, `/flow:plan`, `/flow:validate` and other FlowSpec commands natively within Claude Code, just as they can invoke `/architect`, `/security-reviewer`, or other Claude Code skills.

### Evidence

**watchtower project analysis:**

| Location | File Count | Format | Recognized by Claude Code? |
|----------|------------|--------|---------------------------|
| `.github/prompts/flow.*.prompt.md` | 18 files | GitHub Copilot | NO |
| `.claude/skills/*/SKILL.md` | 9 files | Claude Code | YES |

The 9 skills in `.claude/skills/` (architect, pm-planner, qa-validator, etc.) ARE recognized. The 18 flow commands in `.github/prompts/` are NOT recognized.

---

## Technical Analysis

### Format Comparison

#### GitHub Copilot Prompt Format (Current)

**Path:** `.github/prompts/<name>.prompt.md`

**Example:** `.github/prompts/flow.implement.prompt.md`

```yaml
---
description: Execute implementation using specialized frontend and backend engineer agents with code review.
loop: inner
---

## User Input
...
```

**Characteristics:**
- Single file per command
- YAML frontmatter with `description` and optional `loop` fields
- Path pattern: `.github/prompts/<name>.prompt.md`

#### Claude Code Skill Format (Required)

**Path:** `.claude/skills/<skill-name>/SKILL.md`

**Example:** `.claude/skills/flow-implement/SKILL.md`

```yaml
---
name: flow-implement
description: Execute implementation using specialized frontend and backend engineer agents with code review.
---

# Flow Implement Skill

You are executing the /flow:implement command...
```

**Characteristics:**
- One directory per skill with `SKILL.md` inside
- YAML frontmatter MUST have `name` and `description` fields
- `name` field determines the slash command name
- Path pattern: `.claude/skills/<skill-name>/SKILL.md`

### Key Differences

| Aspect | GitHub Copilot | Claude Code |
|--------|----------------|-------------|
| Path | `.github/prompts/<name>.prompt.md` | `.claude/skills/<name>/SKILL.md` |
| Directory structure | Flat files | One directory per skill |
| Frontmatter `name` | Not required | **Required** |
| Frontmatter `description` | Required | Required |
| Other frontmatter | `loop`, etc. | Ignored |
| Command prefix | None standardized | Skill name from `name` field |

---

## Requirements

### REQ-1: Generate Claude Code Skill Files

**Priority:** Critical

FlowSpec MUST generate Claude Code skill files for each flow command in addition to (or instead of) GitHub Copilot prompt files.

**Acceptance Criteria:**

1. For each flow command template in `templates/commands/flow/*.md`, a corresponding skill directory MUST be created at `.claude/skills/flow-<command>/SKILL.md`

2. The SKILL.md file MUST have valid YAML frontmatter with:
   - `name`: The skill name (e.g., `flow-implement`, `flow-plan`)
   - `description`: Copied from the source template's description

3. The skill file body MUST contain the full prompt content from the source template

**Example transformation:**

**Source:** `templates/commands/flow/implement.md`
```yaml
---
description: Execute implementation using specialized frontend and backend engineer agents with code review.
loop: inner
---
## User Input
$ARGUMENTS
...
```

**Generated:** `.claude/skills/flow-implement/SKILL.md`
```yaml
---
name: flow-implement
description: Execute implementation using specialized frontend and backend engineer agents with code review.
---
# Flow Implement

## User Input
$ARGUMENTS
...
```

### REQ-2: Support Both Formats (Optional)

**Priority:** Medium

FlowSpec MAY continue generating GitHub Copilot prompt files for users who use GitHub Copilot. However, Claude Code skill files MUST be generated regardless.

**Options:**
1. Generate both formats always (recommended for max compatibility)
2. Generate only Claude Code format (simpler, but breaks Copilot users)
3. Make format selection configurable in `flowspec_workflow.yml`

### REQ-3: Installation/Deployment Update

**Priority:** Critical

The FlowSpec installation process (whatever mechanism deploys FlowSpec to consumer projects) MUST be updated to:

1. Create the `.claude/skills/flow-<command>/` directory structure
2. Generate proper `SKILL.md` files with correct frontmatter
3. Preserve existing skill files (don't overwrite user customizations)

### REQ-4: Template Structure

**Priority:** High

Create a mapping or transformation logic that:

1. Reads `templates/commands/flow/*.md` files
2. Extracts the `description` from frontmatter
3. Generates `name` field from the filename (e.g., `implement.md` -> `flow-implement`)
4. Produces the `.claude/skills/flow-<command>/SKILL.md` output

### REQ-5: Naming Convention

**Priority:** High

Flow command skills MUST follow this naming convention:

- Skill directory: `.claude/skills/flow-<command>/`
- Skill name field: `flow-<command>` (with hyphen, not colon)
- Invocation: `/flow-<command>` (Claude Code will interpret this)

**Note:** Claude Code uses the `name` field for the slash command. The colon (`:`) may need to be replaced with a hyphen (`-`) for compatibility. Testing required.

**Alternatively**, if colons are supported:
- Skill name field: `flow:<command>`
- Invocation: `/flow:<command>`

---

## Implementation Approach

### Option A: Build-Time Generation (Recommended)

Add a build step to FlowSpec that:

1. Reads all `templates/commands/flow/*.md` files
2. For each file, generates a corresponding skill directory and SKILL.md
3. Outputs to `templates/skills/flow-<command>/SKILL.md`
4. These are then deployed alongside other skills

**Pros:**
- Clean separation of source and generated files
- Easy to maintain
- Works with existing deployment mechanisms

**Cons:**
- Requires build step
- Generated files may get out of sync if build is skipped

### Option B: Symlink Strategy

Create symlinks from `.claude/skills/flow-<command>/SKILL.md` to the source templates, with a wrapper that adds the proper frontmatter.

**Pros:**
- No build step needed
- Always in sync

**Cons:**
- Symlinks don't work well across repos (deployment issue)
- Frontmatter transformation is complex with symlinks

### Option C: Deployment Script Enhancement

Modify the deployment/installation script to:

1. Copy templates to `.github/prompts/` (existing behavior)
2. ALSO copy/transform templates to `.claude/skills/` (new behavior)

**Pros:**
- Minimal changes to existing structure
- Works at deployment time

**Cons:**
- Logic split between templates and deployment script

---

## Reference Implementation

Below is a complete reference implementation of the generation script. This can be used directly or adapted.

### Python Version (Recommended)

```python
#!/usr/bin/env python3
"""
Generate Claude Code skills from FlowSpec command templates.

Usage:
    python scripts/generate-claude-skills.py

This reads templates/commands/flow/*.md and generates
templates/skills/flow-*/SKILL.md with proper Claude Code frontmatter.
"""

import os
import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown file."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, parts[2].lstrip()


def generate_skill_name(filename: str) -> str:
    """Convert filename to skill name: implement.md -> flow-implement"""
    name = Path(filename).stem
    # Replace underscores with hyphens for consistency
    name = name.replace('_', '-')
    return f"flow-{name}"


def generate_skill_content(source_path: Path) -> str:
    """Generate Claude Code skill content from source template."""
    content = source_path.read_text()
    frontmatter, body = extract_frontmatter(content)

    skill_name = generate_skill_name(source_path.name)
    description = frontmatter.get('description', f'FlowSpec {skill_name} command')

    return f"""---
name: {skill_name}
description: {description}
---

# {skill_name.replace('-', ' ').title()}

{body}
"""


def main():
    # Paths
    repo_root = Path(__file__).parent.parent
    source_dir = repo_root / 'templates' / 'commands' / 'flow'
    output_dir = repo_root / 'templates' / 'skills'

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        sys.exit(1)

    # Find all command templates (skip partials starting with _)
    templates = [f for f in source_dir.glob('*.md') if not f.name.startswith('_')]

    print(f"Found {len(templates)} command templates")

    generated = 0
    errors = 0

    for template in sorted(templates):
        skill_name = generate_skill_name(template.name)
        skill_dir = output_dir / skill_name
        skill_file = skill_dir / 'SKILL.md'

        try:
            # Create skill directory
            skill_dir.mkdir(parents=True, exist_ok=True)

            # Generate skill content
            content = generate_skill_content(template)

            # Write skill file
            skill_file.write_text(content)

            print(f"  Generated: {skill_file.relative_to(repo_root)}")
            generated += 1

        except Exception as e:
            print(f"  ERROR: Failed to generate {skill_name}: {e}")
            errors += 1

    print(f"\nSummary: {generated} generated, {errors} errors")

    if errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### Bash Version (Alternative)

```bash
#!/bin/bash
# Generate Claude Code skills from FlowSpec command templates
# Usage: ./scripts/generate-claude-skills.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SOURCE_DIR="$REPO_ROOT/templates/commands/flow"
OUTPUT_DIR="$REPO_ROOT/templates/skills"

if [ ! -d "$SOURCE_DIR" ]; then
    echo "ERROR: Source directory not found: $SOURCE_DIR"
    exit 1
fi

GENERATED=0
ERRORS=0

for template in "$SOURCE_DIR"/*.md; do
    # Skip partials (files starting with _)
    filename=$(basename "$template")
    if [[ "$filename" == _* ]]; then
        continue
    fi

    # Generate skill name: implement.md -> flow-implement
    name="${filename%.md}"
    name="${name//_/-}"  # Replace underscores with hyphens
    skill_name="flow-$name"

    skill_dir="$OUTPUT_DIR/$skill_name"
    skill_file="$skill_dir/SKILL.md"

    # Extract description from frontmatter
    description=$(sed -n '/^---$/,/^---$/{ /^description:/p }' "$template" | sed 's/^description:[[:space:]]*//')

    if [ -z "$description" ]; then
        description="FlowSpec $skill_name command"
    fi

    # Extract body (everything after second ---)
    body=$(sed '1,/^---$/d; 1,/^---$/d' "$template")

    # Create skill directory and file
    mkdir -p "$skill_dir"

    cat > "$skill_file" << EOF
---
name: $skill_name
description: $description
---

# ${skill_name//-/ }

$body
EOF

    echo "  Generated: templates/skills/$skill_name/SKILL.md"
    GENERATED=$((GENERATED + 1))
done

echo ""
echo "Summary: $GENERATED generated, $ERRORS errors"

if [ $ERRORS -gt 0 ]; then
    exit 1
fi
```

### Makefile Target

Add to `Makefile`:

```makefile
# Generate Claude Code skills from flow command templates
.PHONY: generate-claude-skills
generate-claude-skills:
	@echo "Generating Claude Code skills..."
	@python scripts/generate-claude-skills.py
	@echo "Done."

# Add to build dependencies
.PHONY: build
build: generate-claude-skills
	# ... existing build steps ...
```

---

## Testing Strategy

### Test 1: Skill File Generation

**Verify:** FlowSpec generates valid skill files

```bash
# After running FlowSpec build/install
ls -la .claude/skills/flow-*/SKILL.md

# Expected: One directory per flow command
# flow-assess/SKILL.md
# flow-implement/SKILL.md
# flow-plan/SKILL.md
# flow-validate/SKILL.md
# etc.
```

### Test 2: Frontmatter Validation

**Verify:** Each SKILL.md has required frontmatter

```bash
# Check for required 'name' field
for skill in .claude/skills/flow-*/SKILL.md; do
  if ! grep -q "^name:" "$skill"; then
    echo "FAIL: $skill missing 'name' field"
  fi
done

# Check for required 'description' field
for skill in .claude/skills/flow-*/SKILL.md; do
  if ! grep -q "^description:" "$skill"; then
    echo "FAIL: $skill missing 'description' field"
  fi
done
```

### Test 3: Claude Code Recognition

**Verify:** Claude Code recognizes the skills

1. Open Claude Code in a project with FlowSpec installed
2. Type `/flow-` and observe autocomplete suggestions
3. Expected: All flow commands appear as suggestions
4. Alternative: Check the Skill tool's available skills list in the system prompt

```bash
# In Claude Code conversation, the system prompt includes:
# Available skills:
# - flow-implement: Execute implementation...
# - flow-plan: Create implementation plans...
# etc.
```

### Test 4: Skill Invocation

**Verify:** Skills execute correctly when invoked

1. In Claude Code, type `/flow-implement task-123`
2. Expected: The skill loads and begins execution
3. Verify: The skill content matches the source template

### Test 5: Round-Trip Test

**Verify:** End-to-end from FlowSpec source to Claude Code execution

```bash
# 1. Clean slate
rm -rf .claude/skills/flow-*

# 2. Run FlowSpec install/deploy
flowspec init  # or whatever the install command is

# 3. Verify files created
test -f .claude/skills/flow-implement/SKILL.md || echo "FAIL: flow-implement not created"

# 4. Start Claude Code and verify /flow-implement works
# (manual verification or automated if Claude Code has a test mode)
```

### Combined Test Harness

Save this as `scripts/test-claude-skills.sh` and run after generation:

```bash
#!/bin/bash
# Complete test harness for Claude Code skill generation
# Usage: ./scripts/test-claude-skills.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKILLS_DIR="$REPO_ROOT/templates/skills"

echo "===== Claude Code Skills Test Harness ====="
echo ""

TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Count skill directories
echo "Test 1: Skill directory count"
EXPECTED=18
ACTUAL=$(ls -d "$SKILLS_DIR"/flow-*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$ACTUAL" -eq "$EXPECTED" ]; then
    echo "  PASS: Found $ACTUAL skill directories (expected $EXPECTED)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: Found $ACTUAL skill directories (expected $EXPECTED)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 2: Each directory has SKILL.md
echo "Test 2: SKILL.md files exist"
MISSING=0
for dir in "$SKILLS_DIR"/flow-*/; do
    if [ ! -f "$dir/SKILL.md" ]; then
        echo "  FAIL: Missing SKILL.md in $dir"
        MISSING=$((MISSING + 1))
    fi
done
if [ "$MISSING" -eq 0 ]; then
    echo "  PASS: All skill directories have SKILL.md"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: $MISSING directories missing SKILL.md"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 3: All SKILL.md have 'name:' field
echo "Test 3: name: field present"
MISSING=0
for skill in "$SKILLS_DIR"/flow-*/SKILL.md; do
    if ! grep -q "^name:" "$skill" 2>/dev/null; then
        echo "  FAIL: Missing name: in $skill"
        MISSING=$((MISSING + 1))
    fi
done
if [ "$MISSING" -eq 0 ]; then
    echo "  PASS: All skills have name: field"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: $MISSING skills missing name: field"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 4: All SKILL.md have 'description:' field
echo "Test 4: description: field present"
MISSING=0
for skill in "$SKILLS_DIR"/flow-*/SKILL.md; do
    if ! grep -q "^description:" "$skill" 2>/dev/null; then
        echo "  FAIL: Missing description: in $skill"
        MISSING=$((MISSING + 1))
    fi
done
if [ "$MISSING" -eq 0 ]; then
    echo "  PASS: All skills have description: field"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: $MISSING skills missing description: field"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 5: Frontmatter starts with ---
echo "Test 5: YAML frontmatter format"
INVALID=0
for skill in "$SKILLS_DIR"/flow-*/SKILL.md; do
    if ! head -1 "$skill" 2>/dev/null | grep -q "^---$"; then
        echo "  FAIL: Invalid frontmatter start in $skill"
        INVALID=$((INVALID + 1))
    fi
done
if [ "$INVALID" -eq 0 ]; then
    echo "  PASS: All skills have valid frontmatter format"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: $INVALID skills have invalid frontmatter"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Test 6: name: matches directory name
echo "Test 6: name: matches directory"
MISMATCHED=0
for dir in "$SKILLS_DIR"/flow-*/; do
    skill_file="$dir/SKILL.md"
    expected_name=$(basename "$dir")
    actual_name=$(grep "^name:" "$skill_file" 2>/dev/null | sed 's/^name:[[:space:]]*//')
    if [ "$expected_name" != "$actual_name" ]; then
        echo "  FAIL: Directory $expected_name has name: $actual_name"
        MISMATCHED=$((MISMATCHED + 1))
    fi
done
if [ "$MISMATCHED" -eq 0 ]; then
    echo "  PASS: All skill names match directory names"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo "  FAIL: $MISMATCHED name mismatches"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

# Summary
echo ""
echo "===== Summary ====="
echo "Tests passed: $TESTS_PASSED"
echo "Tests failed: $TESTS_FAILED"
echo ""

if [ "$TESTS_FAILED" -gt 0 ]; then
    echo "OVERALL: FAILED"
    exit 1
else
    echo "OVERALL: PASSED"
    exit 0
fi
```

---

## Definition of Done

The implementation is complete when ALL of the following are true:

### For the Implementer

- [ ] Generation script created and tested (`scripts/generate-claude-skills.py`)
- [ ] Makefile target added (`make generate-claude-skills`)
- [ ] All 18 skill files generated without errors
- [ ] Test harness passes (`scripts/test-claude-skills.sh`)
- [ ] Validation script passes (`scripts/validate-claude-skills.sh`)
- [ ] Manual test: `/flow-implement` works in Claude Code
- [ ] Manual test: All 18 `/flow-*` commands appear in skill list
- [ ] Documentation updated (README mentions Claude Code support)
- [ ] PR created with all changes

### For the Reviewer

- [ ] Generation script is idempotent (running twice produces same result)
- [ ] No broken symlinks introduced
- [ ] Existing skills not affected
- [ ] Test harness included in PR
- [ ] CI passes (if applicable)

### For Release

- [ ] Changelog updated
- [ ] Version bumped (minor version)
- [ ] Tag created
- [ ] Release notes mention Claude Code skill support

---

## Files to Modify in FlowSpec

Based on repository structure analysis:

### Specific Files to Modify

1. **`Makefile`** (line ~50-100 area)
   - Add new target: `generate-claude-skills`
   - Add dependency to main `build` target
   - Example: `make generate-claude-skills`

2. **`scripts/` directory** (create new script)
   - Create: `scripts/generate-claude-skills.sh` or `scripts/generate-claude-skills.py`
   - Responsibility: Transform command templates to skill format

3. **`templates/skills/`** (add new directories)
   - Create: `templates/skills/flow-<command>/SKILL.md` for each command
   - These are the generated outputs

4. **Installation mechanism** (identify and update)
   - If `flowspec init` command exists: Update its logic
   - If deployment script exists: Add skill file copying
   - If symlink-based: Add new symlinks

### New Files to Create

1. **Generation Script:**
   ```
   scripts/generate-claude-skills.sh
   ```
   OR
   ```
   scripts/generate-claude-skills.py
   ```

2. **Generated Skill Directories (18 total):**
   ```
   templates/skills/flow-assess/SKILL.md
   templates/skills/flow-custom/SKILL.md
   templates/skills/flow-generate-prp/SKILL.md
   templates/skills/flow-implement/SKILL.md
   templates/skills/flow-init/SKILL.md
   templates/skills/flow-intake/SKILL.md
   templates/skills/flow-map-codebase/SKILL.md
   templates/skills/flow-plan/SKILL.md
   templates/skills/flow-research/SKILL.md
   templates/skills/flow-reset/SKILL.md
   templates/skills/flow-security-fix/SKILL.md
   templates/skills/flow-security-report/SKILL.md
   templates/skills/flow-security-triage/SKILL.md
   templates/skills/flow-security-web/SKILL.md
   templates/skills/flow-security-workflow/SKILL.md
   templates/skills/flow-specify/SKILL.md
   templates/skills/flow-submit-n-watch-pr/SKILL.md
   templates/skills/flow-validate/SKILL.md
   ```

---

## Error Handling

### Generation Errors

If template parsing fails during skill generation:

1. **Missing frontmatter:** Skip file, log warning
2. **Missing description field:** Use filename as fallback description
3. **Invalid YAML:** Fail loudly with clear error message
4. **File permission errors:** Fail with actionable message

### Deployment Errors

1. **Target directory doesn't exist:** Create it automatically
2. **File already exists:**
   - If identical: Skip (idempotent)
   - If different: Warn and offer to overwrite (with backup)
3. **Symlink broken:** Remove and recreate

### Validation Script

Create `scripts/validate-claude-skills.sh`:

```bash
#!/bin/bash
# Validate all generated Claude Code skills

ERRORS=0

for skill_dir in .claude/skills/flow-*/; do
  skill_file="$skill_dir/SKILL.md"

  if [ ! -f "$skill_file" ]; then
    echo "ERROR: Missing SKILL.md in $skill_dir"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check for YAML frontmatter
  if ! head -1 "$skill_file" | grep -q "^---$"; then
    echo "ERROR: $skill_file missing YAML frontmatter start"
    ERRORS=$((ERRORS + 1))
  fi

  # Check for name field
  if ! grep -q "^name:" "$skill_file"; then
    echo "ERROR: $skill_file missing 'name' field"
    ERRORS=$((ERRORS + 1))
  fi

  # Check for description field
  if ! grep -q "^description:" "$skill_file"; then
    echo "ERROR: $skill_file missing 'description' field"
    ERRORS=$((ERRORS + 1))
  fi
done

if [ $ERRORS -eq 0 ]; then
  echo "All Claude Code skills validated successfully"
  exit 0
else
  echo "Found $ERRORS validation errors"
  exit 1
fi
```

---

## Rollback Plan

If the implementation causes issues:

### Immediate Rollback

```bash
# Remove generated skill files
rm -rf .claude/skills/flow-*

# Restore from git if needed
git checkout -- .claude/skills/
```

### Version-Based Rollback

If FlowSpec is versioned:

```bash
# Downgrade to previous version
pip install flowspec==<previous-version>
# OR
git checkout v<previous-version>

# Re-run installation
flowspec init
```

### Consumer Project Rollback

For projects like watchtower that have FlowSpec installed:

```bash
# Remove flow skills only
rm -rf .claude/skills/flow-*

# Keep other skills intact
# .claude/skills/architect/, .claude/skills/pm-planner/, etc. remain
```

---

## Version/Release Integration

### Semantic Versioning Impact

This is a **feature addition** (new capability), not a breaking change:
- **Version bump:** Minor version (e.g., 1.2.0 -> 1.3.0)
- **Breaking:** No - existing functionality unchanged
- **Additive:** Yes - new files generated

### Release Checklist

1. [ ] All 18 skill files generated correctly
2. [ ] Validation script passes
3. [ ] Manual test in fresh project
4. [ ] Documentation updated (README, CHANGELOG)
5. [ ] Migration guide for existing users
6. [ ] Tag release with version number

### Changelog Entry

```markdown
## [1.X.0] - 2026-XX-XX

### Added
- Claude Code skill integration for all /flow:* commands
- Generated skills appear in Claude Code's available skills list
- Users can now invoke /flow-implement, /flow-plan, etc. natively

### Technical
- New generation script: scripts/generate-claude-skills.sh
- Added 18 skill files to templates/skills/flow-*/
- Makefile target: make generate-claude-skills
```

---

## Migration Path

For existing FlowSpec users (like watchtower):

### Step 1: Update FlowSpec

Pull latest FlowSpec version with this fix

### Step 2: Re-run FlowSpec Installation

```bash
flowspec init  # or appropriate install command
```

This should now generate both:
- `.github/prompts/flow.*.prompt.md` (for GitHub Copilot)
- `.claude/skills/flow-*/SKILL.md` (for Claude Code)

### Step 3: Verify

```bash
ls .claude/skills/flow-*/SKILL.md
```

### Step 4: Test

Open Claude Code and type `/flow-` to see autocomplete suggestions.

---

## Success Criteria

The fix is considered complete when:

1. **Generation:** FlowSpec generates valid `.claude/skills/flow-*/SKILL.md` files
2. **Frontmatter:** Each skill has valid `name` and `description` in YAML frontmatter
3. **Recognition:** Claude Code lists flow skills in its available skills
4. **Invocation:** Users can invoke `/flow-implement`, `/flow-plan`, etc. in Claude Code
5. **Content:** Skill content matches the source template functionality
6. **No Regression:** GitHub Copilot prompts continue to work (if supporting both)

---

## Open Questions

1. **Colon vs Hyphen:** Does Claude Code support colons in skill names (`flow:implement`) or must we use hyphens (`flow-implement`)?

2. **Namespace Collision:** Will `flow-implement` conflict with any existing skill names?

3. **Partial Install:** Should users be able to install only specific flow commands as skills?

4. **Upgrade Path:** How do we handle users who have customized their `.claude/skills/` directory?

5. **Dual Format Maintenance:** If generating both formats, how do we ensure they stay in sync?

---

## Appendix: Command Mapping

| Template Source | GitHub Copilot Path | Claude Code Path |
|-----------------|---------------------|------------------|
| `templates/commands/flow/assess.md` | `.github/prompts/flow.assess.prompt.md` | `.claude/skills/flow-assess/SKILL.md` |
| `templates/commands/flow/implement.md` | `.github/prompts/flow.implement.prompt.md` | `.claude/skills/flow-implement/SKILL.md` |
| `templates/commands/flow/plan.md` | `.github/prompts/flow.plan.prompt.md` | `.claude/skills/flow-plan/SKILL.md` |
| `templates/commands/flow/validate.md` | `.github/prompts/flow.validate.prompt.md` | `.claude/skills/flow-validate/SKILL.md` |
| `templates/commands/flow/specify.md` | `.github/prompts/flow.specify.prompt.md` | `.claude/skills/flow-specify/SKILL.md` |
| `templates/commands/flow/research.md` | `.github/prompts/flow.research.prompt.md` | `.claude/skills/flow-research/SKILL.md` |
| `templates/commands/flow/init.md` | `.github/prompts/flow.init.prompt.md` | `.claude/skills/flow-init/SKILL.md` |
| `templates/commands/flow/intake.md` | `.github/prompts/flow.intake.prompt.md` | `.claude/skills/flow-intake/SKILL.md` |
| `templates/commands/flow/reset.md` | `.github/prompts/flow.reset.prompt.md` | `.claude/skills/flow-reset/SKILL.md` |
| `templates/commands/flow/custom.md` | `.github/prompts/flow.custom.prompt.md` | `.claude/skills/flow-custom/SKILL.md` |
| `templates/commands/flow/generate-prp.md` | `.github/prompts/flow.generate-prp.prompt.md` | `.claude/skills/flow-generate-prp/SKILL.md` |
| `templates/commands/flow/map-codebase.md` | `.github/prompts/flow.map-codebase.prompt.md` | `.claude/skills/flow-map-codebase/SKILL.md` |
| `templates/commands/flow/submit-n-watch-pr.md` | `.github/prompts/flow.submit-n-watch-pr.prompt.md` | `.claude/skills/flow-submit-n-watch-pr/SKILL.md` |
| `templates/commands/flow/security_fix.md` | `.github/prompts/flow.security_fix.prompt.md` | `.claude/skills/flow-security-fix/SKILL.md` |
| `templates/commands/flow/security_report.md` | `.github/prompts/flow.security_report.prompt.md` | `.claude/skills/flow-security-report/SKILL.md` |
| `templates/commands/flow/security_triage.md` | `.github/prompts/flow.security_triage.prompt.md` | `.claude/skills/flow-security-triage/SKILL.md` |
| `templates/commands/flow/security_web.md` | `.github/prompts/flow.security_web.prompt.md` | `.claude/skills/flow-security-web/SKILL.md` |
| `templates/commands/flow/security_workflow.md` | `.github/prompts/flow.security_workflow.prompt.md` | `.claude/skills/flow-security-workflow/SKILL.md` |
**Total:** 18 flow commands requiring skill generation

---

## Decision Log Reference

All analysis decisions are logged at:
- `watchtower/.logs/decisions/2026-01-11-flowspec-claude-code-skills.jsonl`

**Decision IDs:** FLOW-SKILL-001 through FLOW-SKILL-009

| ID | Phase | Summary |
|----|-------|---------|
| FLOW-SKILL-001 | analysis | Root cause identified: GitHub Copilot vs Claude Code format mismatch |
| FLOW-SKILL-002 | analysis | Fix must be in FlowSpec, not consumer projects |
| FLOW-SKILL-003 | analysis | Claude Code requires `name:` and `description:` in frontmatter |
| FLOW-SKILL-004 | analysis | Requirement doc placed in FlowSpec build-docs/ |
| FLOW-SKILL-005 | analysis | Testing: verify skills appear in Claude Code skill list |
| FLOW-SKILL-006 | review | Verified count: 18 flow command templates |
| FLOW-SKILL-007 | review | Verified frontmatter format from working skill file |
| FLOW-SKILL-008 | review | Added reference implementation scripts for actionability |
| FLOW-SKILL-009 | final | Document marked final after 3 review passes |
