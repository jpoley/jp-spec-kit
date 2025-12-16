# Command Objective: `flowspec init`

## Summary
Initialize a new Specify project from the latest templates, with support for multiple AI agents, constitution tiers, and validation modes.

## Objective
Provide a comprehensive project initialization experience that:
1. Creates a properly structured SDD project
2. Supports multiple AI assistants (Claude, Copilot, Gemini, etc.)
3. Offers constitution tiers (light/medium/heavy) for different governance needs
4. Configures validation modes for workflow transitions
5. Sets up all necessary tooling and templates

## Features

### Core Features
1. **Two-stage template download** - Fetches base spec-kit + flowspec extension
2. **Multi-agent support** - Can initialize for multiple AI agents simultaneously
3. **Constitution tiers** - Light (startup), Medium (business), Heavy (enterprise)
4. **Validation mode configuration** - Per-transition validation settings
5. **Git repository initialization** - Optional git repo setup
6. **Hooks scaffolding** - Creates hook files with defaults
7. **Repo-facts generation** - Creates memory/repo-facts.md

### Command Options
```bash
flowspec init <project-name> [OPTIONS]
flowspec init . --ai claude                    # Current directory
flowspec init --here --ai claude               # Alternative syntax
flowspec init my-project --ai claude,copilot   # Multiple agents
flowspec init my-project --constitution medium
flowspec init my-project --no-git
flowspec init my-project --light               # Spec-light mode
```

### Key Options
| Option | Description |
|--------|-------------|
| `--ai` | AI assistant(s) - comma-separated |
| `--constitution` | Tier: light, medium, heavy |
| `--no-git` | Skip git initialization |
| `--force` | Skip confirmation on non-empty dirs |
| `--light` | Use spec-light mode |
| `--validation-mode` | Set all validations: none/keyword/pull-request |
| `--no-validation-prompts` | Skip prompts, use NONE for all |

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec init test-project --ai claude --constitution light --no-validation-prompts` | Creates project | Creates complete project | PASS |
| Two-stage download | Base + extension | Working | PASS |
| Constitution setup | Creates memory/constitution.md | Working | PASS |
| Hooks scaffolding | Creates hook files | Working | PASS |
| Git initialization | Creates .git | Working | PASS |
| Source repo detection | Blocks in flowspec repo | Working (detects .flowspec-source) | PASS |

## Acceptance Criteria
- [x] Downloads base spec-kit templates
- [x] Downloads flowspec extension templates
- [x] Merges templates with extension precedence
- [x] Creates constitution based on tier selection
- [x] Initializes git repository (unless --no-git)
- [x] Scaffolds hooks configuration
- [x] Generates flowspec_workflow.yml
- [x] Creates repo-facts.md
- [x] Supports multiple AI agents
- [x] Supports current directory initialization
- [x] Detects and blocks in flowspec source repo
