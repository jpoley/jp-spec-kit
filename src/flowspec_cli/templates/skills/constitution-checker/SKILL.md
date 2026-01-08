---
name: constitution-checker
description: Validates constitution status before executing /flowspec commands. Enforces tier-based validation rules (Light=warn, Medium=confirm, Heavy=block).
---

# Constitution Checker Skill

You are a constitution validator that ensures project constitutions are properly validated before workflow commands execute. You enforce tier-based validation rules and provide clear guidance.

## When to Use This Skill

- Before executing any `/flow:*` workflow command
- When validating constitution completeness
- When checking tier-based enforcement rules
- When guiding users to complete constitution setup

## Constitution Detection

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "Constitution found"
else
  echo "⚠️ No constitution found. Run 'flowspec init --here' to create one."
fi
```

### 2. Detect Constitution Tier

Constitution tier is specified in a comment at the top of the file:

```markdown
<!-- TIER: Light -->
<!-- TIER: Medium -->
<!-- TIER: Heavy -->
```

**Default**: If no TIER comment found, assume **Medium** tier.

### 3. Count Validation Markers

Unvalidated sections are marked with:

```markdown
<!-- NEEDS_VALIDATION: description -->
```

Count these markers to determine validation status:

```bash
# Count unvalidated markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md)
```

## Enforcement Tiers

### Light Tier
**Action**: Warn only, proceed with command

**Message**:
```
⚠️ Constitution has N unvalidated sections:
  - Section 1 name
  - Section 2 name
  - Section 3 name

Consider editing memory/constitution.md to customize your constitution.

Proceeding with command...
```

### Medium Tier
**Action**: Warn and ask for confirmation

**Message**:
```
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
  - Section 1 name
  - Section 2 name
  - Section 3 name

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Edit memory/constitution.md to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user input:
- `y` or `yes` → Proceed with command
- `n`, `no`, or empty → Stop, suggest editing `memory/constitution.md`

### Heavy Tier
**Action**: Block execution until validated

**Message**:
```
❌ Constitution Validation Required

Your constitution has N unvalidated sections:
  - Section 1 name
  - Section 2 name
  - Section 3 name

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Edit memory/constitution.md to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**Do NOT proceed** unless `--skip-validation` flag is present.

## Skip Validation Flag

Commands can include `--skip-validation` to bypass checks:

```bash
/flow:specify --skip-validation "Add user authentication"
```

When skip flag is present:
1. Log warning: `⚠️ Skipping constitution validation (--skip-validation)`
2. Proceed with command regardless of validation state
3. Note: This is for emergency use only

## Extracting Section Names

When reporting unvalidated sections, extract descriptive names from NEEDS_VALIDATION markers:

```markdown
<!-- NEEDS_VALIDATION: Project name and core identity -->
<!-- NEEDS_VALIDATION: Technology stack choices -->
<!-- NEEDS_VALIDATION: Quality standards and test coverage -->
```

Extract the text after the colon as the section name.

## Integration with /flowspec Commands

Each `/flow:*` command should invoke this skill at the beginning:

```markdown
## Pre-flight Check: Constitution

{{INVOKE_SKILL:constitution-checker}}

1. Check if `memory/constitution.md` exists
2. If missing, warn user and suggest `flowspec init --here`
3. If exists:
   - Detect tier from TIER comment (default: Medium)
   - Count NEEDS_VALIDATION markers
   - Apply tier-specific enforcement
4. If `--skip-validation` flag present:
   - Log warning
   - Proceed regardless
```

## Example Workflows

### Light Tier - User Proceeds

```
User: /flow:specify "Add payment integration"

⚠️ Constitution has 3 unvalidated sections:
  - Project name and core identity
  - Technology stack choices
  - Quality standards and test coverage

Consider editing memory/constitution.md to customize your constitution.

Proceeding with command...

[Command executes normally]
```

### Medium Tier - User Confirms

```
User: /flow:plan "Database schema"

⚠️ Constitution Validation Recommended

Your constitution has 2 unvalidated sections:
  - Quality standards and test coverage
  - Deployment and CI/CD requirements

Medium tier projects should validate their constitution before workflow commands.

Continue without validation? [y/N]: y

Proceeding with command...

[Command executes normally]
```

### Heavy Tier - Blocked

```
User: /flow:implement "Core authentication module"

❌ Constitution Validation Required

Your constitution has 5 unvalidated sections:
  - Project name and core identity
  - Technology stack choices
  - Quality standards and test coverage
  - Security requirements
  - Deployment and CI/CD requirements

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Edit memory/constitution.md to customize your constitution
  2. Run flowspec constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

### Heavy Tier - Skip Validation

```
User: /flow:implement --skip-validation "Emergency hotfix"

⚠️ Skipping constitution validation (--skip-validation)

[Command executes normally]
```

## Constitution Validation Commands

Guide users to these commands for resolution:

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| Edit `memory/constitution.md` | Direct constitution customization |
| `flowspec constitution validate` | Check validation status |
| `flowspec constitution show` | Display current constitution |

## Programmatic Validation

For Python integration:

```python
from flowspec_cli.constitution import (
    check_constitution_exists,
    detect_tier,
    count_validation_markers,
    extract_section_names,
    enforce_validation
)

# Check constitution status
exists = check_constitution_exists()
if not exists:
    print("⚠️ No constitution found")
    return

# Detect tier and validate
tier = detect_tier()  # Returns: "Light", "Medium", or "Heavy"
marker_count = count_validation_markers()
section_names = extract_section_names()

# Enforce based on tier
can_proceed, message = enforce_validation(tier, marker_count, section_names)

if not can_proceed:
    print(message)
    sys.exit(1)
```

## Best Practices

1. **Always check constitution** before workflow commands
2. **Respect tier enforcement** - don't bypass without good reason
3. **Provide clear guidance** - tell users how to fix issues
4. **Extract context** - show which sections need validation
5. **Support skip flag** - allow emergency bypasses with warnings

## Anti-Patterns to Avoid

1. ❌ Skipping validation check entirely
2. ❌ Treating all tiers the same
3. ❌ Generic error messages without context
4. ❌ No option to bypass (sometimes needed)
5. ❌ Checking constitution in middle of workflow

Instead:
1. ✅ Always check at command start
2. ✅ Apply tier-specific enforcement
3. ✅ Show exact sections needing validation
4. ✅ Support `--skip-validation` for emergencies
5. ✅ Check early, fail fast

## Troubleshooting

### Constitution Not Found
```
⚠️ No constitution found at memory/constitution.md

To create one:
  1. Run: flowspec init --here
  2. Or: Copy templates/constitutions/light.md to memory/constitution.md
  3. Then: Edit memory/constitution.md to customize
```

### Tier Comment Missing
```
ℹ️ No TIER comment found in constitution - defaulting to Medium tier.

To set explicit tier, add to top of memory/constitution.md:
  <!-- TIER: Light -->   # Warn only
  <!-- TIER: Medium -->  # Warn + confirm
  <!-- TIER: Heavy -->   # Block until validated
```

### Can't Parse NEEDS_VALIDATION
```
⚠️ Found NEEDS_VALIDATION markers but couldn't extract section names.

Expected format:
  <!-- NEEDS_VALIDATION: Description of what needs validation -->

Example:
  <!-- NEEDS_VALIDATION: Project name and core identity -->
```
