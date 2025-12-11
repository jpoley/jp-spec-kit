# Constitution Customization Examples

These examples show how to customize constitution templates for different tech stacks and project types.

## Available Examples

| Tech Stack | File | Description |
|------------|------|-------------|
| Python/FastAPI | [python-fastapi.md](python-fastapi.md) | Python web API with FastAPI, pytest, ruff |
| TypeScript/Next.js | [typescript-nextjs.md](typescript-nextjs.md) | TypeScript web app with Next.js, Jest, ESLint |
| Go API | [go-api.md](go-api.md) | Go HTTP API with chi, go test, golangci-lint |
| Rust CLI | [rust-cli.md](rust-cli.md) | Rust CLI with clap, cargo test, clippy |

## What These Examples Show

Each example demonstrates:

1. **Before**: Template sections with placeholders
2. **After**: Fully customized sections for specific tech stack
3. **repo-facts.md**: Example output from `/speckit:constitution`
4. **Key Customization Points**: What makes this constitution unique
5. **Common Variations**: Optional sections for different scenarios

## Using These Examples

### Step 1: Generate Constitution Template

```bash
# Initialize constitution for your project
specify init

# Run constitution detection
/speckit:constitution
```

### Step 2: Review Generated Constitution

```bash
# Validate constitution
specify constitution validate

# View constitution
cat .specify/memory/constitution.md

# Check detected facts
cat .specify/memory/repo-facts.md
```

### Step 3: Apply Customizations

1. Find the example closest to your tech stack
2. Compare your generated constitution to the example
3. Add/modify sections as needed
4. Keep the comment markers (`<!-- SECTION:NAME:BEGIN -->`)
5. Validate after changes: `specify constitution validate`

### Step 4: Verify

```bash
# Ensure constitution is valid
specify constitution validate

# Test with a slash command
/flow:specify
```

## Constitution Sections

Common sections across tech stacks:

| Section | Purpose |
|---------|---------|
| `TECH_STACK` | Languages, frameworks, tools |
| `QUALITY` | Coverage thresholds, code standards |
| `TESTING` | Test frameworks, coverage tools |
| `CODE_QUALITY` | Linters, formatters, type checkers |
| `CICD` | CI/CD platform, workflows |
| `SECURITY` | Security requirements and tools |

Tech-stack specific sections:

| Section | Used In | Purpose |
|---------|---------|---------|
| `API` | Python, Go | API design standards |
| `FRONTEND` | TypeScript/Next.js | Frontend-specific standards |
| `PERFORMANCE` | TypeScript, Rust | Performance thresholds |
| `CLI` | Rust | CLI-specific requirements |
| `ERROR_HANDLING` | Go, Rust | Error handling patterns |
| `DATABASE` | Python, Go | Database standards |
| `OBSERVABILITY` | Go, Python | Logging, metrics, tracing |

## Customization Guidelines

### DO

- Keep section markers (`<!-- SECTION:NAME:BEGIN -->` and `<!-- SECTION:NAME:END -->`)
- Add new sections relevant to your project
- Be specific (versions, tool names, thresholds)
- Include rationale for critical decisions
- Reference external standards (WCAG, RFC, etc.)

### DON'T

- Remove section markers (breaks validation)
- Use vague requirements ("good coverage")
- Contradict detected repo-facts.md
- Add unnecessary complexity
- Duplicate information across sections

## Example Customization Workflow

```bash
# 1. Generate constitution
specify init
/speckit:constitution

# 2. View Python example
cat docs/examples/constitutions/python-fastapi.md

# 3. Edit constitution
vim .specify/memory/constitution.md

# 4. Validate
specify constitution validate

# 5. Commit
git add .specify/memory/constitution.md
git commit -s -m "docs: customize constitution for Python/FastAPI"
```

## Contributing Examples

To add a new example:

1. Create `{language}-{framework}.md` in this directory
2. Follow the structure of existing examples:
   - **Before**: Show template with placeholders
   - **After**: Show customized sections
   - **repo-facts.md**: Show detection output
   - **Key Customization Points**: Explain decisions
   - **Usage**: How to apply the example
3. Add entry to the table in this README
4. Include common variations if applicable

### Example Template

```markdown
# [Language] [Framework] Project Constitution Example

## Before: Template

\`\`\`markdown
[Show template section]
\`\`\`

## After: Customized

\`\`\`markdown
[Show customized section]
\`\`\`

## repo-facts.md Generated

\`\`\`yaml
[Show detection output]
\`\`\`

## Key Customization Points

1. Point 1
2. Point 2

## Usage

[How to use this example]
```

## FAQ

### Q: Can I have multiple constitutions?

**A**: No. Each project should have one constitution in `.specify/memory/constitution.md`. However, you can customize sections extensively for different components.

### Q: What if my tech stack isn't shown?

**A**: Use the closest example and customize. The constitution is flexible - add sections as needed for your stack.

### Q: Can I remove sections?

**A**: Yes, but keep the section markers. You can empty a section but keep the comments:

```markdown
<!-- SECTION:FRONTEND:BEGIN -->
<!-- Not applicable to this project -->
<!-- SECTION:FRONTEND:END -->
```

### Q: How do I handle monorepos?

**A**: Create sections for each component:

```markdown
## Technology Stack

<!-- SECTION:TECH_STACK:BEGIN -->
### Backend
- Python 3.11+ with FastAPI

### Frontend
- TypeScript 5.0+ with Next.js

### Shared
- pnpm workspaces
- Turborepo for builds
<!-- SECTION:TECH_STACK:END -->
```

### Q: What if detected facts are wrong?

**A**: Manually edit `.specify/memory/repo-facts.md`. Detection is a starting point, not authoritative.

### Q: Do I need to re-run detection after changes?

**A**: No. Detection only runs once during initialization. Manual edits are preserved.
