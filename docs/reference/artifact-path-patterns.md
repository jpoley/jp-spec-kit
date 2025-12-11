# Artifact Path Patterns Reference

This document describes the path pattern variables used in workflow artifact definitions.

## Overview

Workflow transitions define input and output artifacts using path patterns. These patterns support variable substitution to enable dynamic file paths based on the feature being developed.

## Path Pattern Variables

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{feature}` | Feature name slug (lowercase, hyphenated) | `user-authentication` |
| `{NNN}` | Zero-padded 3-digit number | `001`, `002`, `042` |
| `{slug}` | Title slug (defaults to feature if not provided) | `oauth-strategy` |

## Standard Artifact Locations

### Assessment Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| Assessment Report | `./docs/assess/{feature}-assessment.md` | `./docs/assess/user-auth-assessment.md` |

### Specification Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| PRD | `./docs/prd/{feature}.md` | `./docs/prd/user-auth.md` |
| Backlog Tasks | `./backlog/tasks/*.md` | `./backlog/tasks/task-123-*.md` |

### Research Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| Research Report | `./docs/research/{feature}-research.md` | `./docs/research/user-auth-research.md` |
| Business Validation | `./docs/research/{feature}-validation.md` | `./docs/research/user-auth-validation.md` |

### Architecture Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| ADR | `./docs/adr/ADR-{NNN}-{slug}.md` | `./docs/adr/ADR-001-oauth-strategy.md` |
| Platform Design | `./docs/platform/{feature}-platform.md` | `./docs/platform/user-auth-platform.md` |

### Implementation Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| Source Code | `./src/` | Project-specific |
| Tests | `./tests/` | Project-specific |
| AC Coverage | `./tests/ac-coverage.json` | Fixed location |

### Validation Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| QA Report | `./docs/qa/{feature}-qa-report.md` | `./docs/qa/user-auth-qa-report.md` |
| Security Report | `./docs/security/{feature}-security.md` | `./docs/security/user-auth-security.md` |

### Deployment Artifacts
| Artifact Type | Path Pattern | Example |
|--------------|--------------|---------|
| Deployment Manifest | `./deploy/` | Project-specific |

## Usage in Code

```python
from specify_cli.workflow import Artifact

# Create artifact with path pattern
artifact = Artifact(
    type="adr",
    path="./docs/adr/ADR-{NNN}-{slug}.md",
    required=True,
    multiple=True,
)

# Resolve path with actual values
resolved = artifact.resolve_path(
    feature="user-auth",
    number=1,
    slug="oauth-strategy",
)
# Result: "./docs/adr/ADR-001-oauth-strategy.md"
```

## Pattern Matching

Artifacts support pattern matching to verify if a file matches the expected pattern:

```python
artifact = Artifact(type="adr", path="./docs/adr/ADR-{NNN}-{slug}.md")

# Check if files match pattern
artifact.matches_pattern("./docs/adr/ADR-001-oauth.md")  # True
artifact.matches_pattern("./docs/adr/ADR-042-jwt.md")    # True
artifact.matches_pattern("./docs/prd/feature.md")        # False
```

## Wildcard Support

Path patterns support glob-style wildcards:

| Pattern | Matches |
|---------|---------|
| `*.md` | Any markdown file |
| `./docs/adr/ADR-*.md` | Any ADR file |
| `./backlog/tasks/*.md` | Any task file |

## Best Practices

1. **Use lowercase, hyphenated slugs**: Convert "User Authentication" to `user-authentication`
2. **Use {NNN} for sequential numbering**: ADRs, task IDs
3. **Use {feature} for feature-specific paths**: Keeps artifacts organized by feature
4. **Use {slug} when title differs from feature**: For ADR titles that are more specific

## See Also

- [Workflow Artifact Flow](./workflow-artifact-flow.md)
- [TransitionSchema API](../api/workflow/transition.md)
- [flowspec_workflow.yml Configuration](../configuration/workflow-config.md)
