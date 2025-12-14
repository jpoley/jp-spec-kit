# Feature Assessment: Constitution Templates with Tiered Control Levels

**Date**: 2025-12-02
**Assessed By**: Claude AI Agent
**Status**: Assessed

## Feature Overview

Implement predefined constitution templates with three tiers of control levels during `specify init`:
- **Light**: Minimal controls for startups, hobby projects, rapid prototyping
- **Medium**: Standard controls for typical business applications
- **Heavy**: Bank-level regulation, strict compliance, enterprise controls

The feature should:
1. Detect if repo is empty and auto-prompt or auto-select appropriate tier
2. Allow user selection of tier during init
3. Create initial template files (don't need to be perfect, can iterate)

## Scoring Analysis

### Complexity Score: 3.0/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Effort Days | 4/10 | ~2-3 days: Create 3 template files, modify init command to prompt/detect empty repo |
| Component Count | 3/10 | 2 components affected: init command, templates directory |
| Integration Points | 2/10 | No external integrations, pure file generation |
| **Average** | **3.0/10** | |

### Risk Score: 2.0/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Security Implications | 3/10 | Templates define security controls but feature itself has no direct security risk |
| Compliance Requirements | 2/10 | Templates ARE about compliance but implementation has no compliance requirements |
| Data Sensitivity | 1/10 | No sensitive data handling - just template text |
| **Average** | **2.0/10** | |

### Architecture Impact Score: 2.3/10

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| New Patterns | 3/10 | Tiered template selection is minor variation of existing init patterns |
| Breaking Changes | 2/10 | Additive feature - existing init behavior preserved, new option added |
| Dependencies Affected | 2/10 | Self-contained, only init command affected |
| **Average** | **2.3/10** | |

## Overall Assessment

**Total Score**: 7.3/30
**Recommendation**: Skip SDD
**Confidence**: High

### Rationale

This feature is a straightforward enhancement to the existing init command:
- No individual dimension scores >= 4 (threshold for Spec-Light)
- Total score 7.3 is well below 10 (threshold for Spec-Light)
- Clear implementation path with minimal risk
- Templates are explicitly "first draft" - iteration expected

The feature primarily involves:
1. Creating 3 YAML/markdown template files
2. Adding a `--constitution` flag to init (light/medium/heavy)
3. Detecting empty repo and prompting for tier selection
4. Copying appropriate template to project

### Key Factors

- **Complexity**: Low - file generation and CLI flag addition
- **Risk**: Minimal - no security, compliance, or data concerns in implementation
- **Impact**: Contained - only affects init command, additive change

## Recommended Implementation

### Direct Implementation Path

1. **Create template files** in `templates/constitutions/`:
   - `constitution-light.md` - Minimal controls
   - `constitution-medium.md` - Standard controls
   - `constitution-heavy.md` - Enterprise/bank-level controls

2. **Modify `specify init`** to add:
   - `--constitution {light|medium|heavy}` flag
   - Empty repo detection logic
   - Interactive prompt if no flag provided

3. **Existing Project Flow** (no constitution detected):
   - Detect existing project without `memory/constitution.md`
   - Prompt user to select tier (light/medium/heavy)
   - LLM analyzes repo structure, existing configs, README, etc.
   - LLM customizes the selected template with repo-specific details
   - Output constitution with `<!-- NEEDS_VALIDATION -->` markers
   - Inform user: "Constitution generated - please review and validate"

4. **LLM Customization Logic**:
   - Scan for: package.json, pyproject.toml, Dockerfile, CI configs, etc.
   - Detect: language, framework, existing test setup, linting, security tools
   - Incorporate findings into constitution sections
   - Add repo-specific principles based on detected patterns
   - Flag sections that were auto-generated for user review

5. **Template Content Guidelines**:

   **Light** (Startup/Hobby):
   - Basic code review required
   - Simple testing requirements
   - Minimal documentation
   - No formal compliance

   **Medium** (Standard Business):
   - PR-based workflow enforced
   - Test coverage requirements
   - DCO sign-off required
   - Basic security scanning
   - Documentation requirements

   **Heavy** (Bank/Enterprise):
   - Mandatory code review + approval
   - Strict test coverage (>80%)
   - DCO + additional sign-off
   - Security scanning + SAST/DAST
   - Compliance documentation
   - Audit trail requirements
   - No direct commits to main
   - PR approval gates

## Next Steps

Proceed directly to implementation:

```bash
# Create task for tracking
backlog task create "Implement tiered constitution templates for specify init" \
  -d "Add light/medium/heavy constitution templates with tier selection during init" \
  --ac "Create constitution-light.md template" \
  --ac "Create constitution-medium.md template" \
  --ac "Create constitution-heavy.md template" \
  --ac "Add --constitution flag to specify init command" \
  --ac "Detect empty repo and prompt for tier selection" \
  --ac "Tests for new init options" \
  -l cli,templates,enhancement \
  --priority high
```

Then implement directly - no PRD or detailed spec required.

## Override

If you want more formal specification despite the low scores:

```bash
# Force spec-light mode
/flow:assess constitution-templates --mode light

# Force full SDD workflow (not recommended for this feature)
/flow:assess constitution-templates --mode full
```

---

*Assessment generated by /flow:assess workflow*
