# Functional Spec: Platform & DevSecOps

**Related Tasks**: task-085, task-136, task-168, task-171, task-184, task-195, task-196, task-197, task-249
**PRD Reference**: `docs/prd/platform-devsecops-prd.md`

---

## Requirements Traceability Matrix

| Task ID | Functional Requirements | Use Cases |
|---------|------------------------|-----------|
| task-184 | FR-SEC-001, FR-SEC-002, FR-SEC-003 | UC-1 (Secret Protection) |
| task-249 | FR-TOOL-001 to FR-TOOL-005 | UC-5 (Tool Auto-Install) |
| task-085 | FR-CI-001, FR-CI-002 | UC-2 (Fast Inner Loop) |
| task-168 | FR-CI-003 | UC-4 (Cross-Platform) |
| task-136 | FR-OBS-001 | UC-3 (Workflow Debugging) |
| task-171 | FR-DX-001 | Research phase |
| task-195 | FR-DX-002 | Deferred to P3 |
| task-196 | FR-DX-003 | Exploratory |
| task-197 | FR-DX-004 | Future enhancement |

---

## Overview

This functional specification defines behaviors for 9 platform infrastructure tasks organized into 4 domains: Security Layer, Tool Management, CI/CD, and Observability.

## Functional Requirements

### FR-SEC: Security Layer (task-184)

**FR-SEC-001**: File Protection Rules
- **Input**: File path for read/write operation
- **Output**: Allow or deny with reason
- **Rules**:
  - Block: `.env*`, `secrets/`, `credentials/`, `*.pem`, `*.key`, `*_rsa`
  - Block write: `package-lock.json`, `uv.lock`, `yarn.lock`, `pnpm-lock.yaml`
  - Block: `CLAUDE.md`, `.claude/settings.json` (without override)
- **Errors**: `Permission denied: [path] matches deny rule [rule]`

**FR-SEC-002**: Command Protection Rules
- **Input**: Shell command string
- **Output**: Allow, deny, or require confirmation
- **Rules**:
  - Block: `sudo`, `rm -rf /`, `rm -rf ~`, `dd if=`, `mkfs`, `chmod 777`
  - Confirm: `rm -rf`, `git push --force`, `DROP TABLE`
- **Errors**: `Blocked: [command] matches dangerous pattern [pattern]`

**FR-SEC-003**: Audit Logging
- **Input**: Security event (deny, override, confirm)
- **Output**: Log entry in `.specify/audit.log`
- **Rules**:
  - Format: `[ISO-timestamp] [event-type] [user] [details]`
  - Include: denied path/command, override reason if applicable
- **Errors**: Log to stderr if audit file not writable

### FR-TOOL: Tool Dependency Management (task-249)

**FR-TOOL-001**: Tool Discovery Chain
- **Input**: Tool name (e.g., "semgrep", "codeql", "act")
- **Output**: Tool path or download trigger
- **Rules**:
  - Check order: PATH → venv → cache → download
  - Cache location: `~/.cache/specify-tools/[tool]/[version]/`
- **Errors**: `Tool [name] not found and download disabled (--offline)`

**FR-TOOL-002**: Semgrep Installation
- **Input**: `semgrep` required
- **Output**: Installed semgrep in venv or cache
- **Rules**:
  - Method: `pip install semgrep==[version]`
  - Version from `.specify/versions.lock.json`
- **Errors**: `Failed to install semgrep: [pip error]`

**FR-TOOL-003**: CodeQL Installation
- **Input**: `codeql` required
- **Output**: Installed codeql binary in cache
- **Rules**:
  - Check GitHub license acceptance first
  - Download from GitHub releases
  - Verify checksum (SLSA Level 2)
- **Errors**: `CodeQL requires license acceptance. Run: [acceptance command]`

**FR-TOOL-004**: Cache Management
- **Input**: Cache operation (check, clear, evict)
- **Output**: Cache state or freed space
- **Rules**:
  - Threshold: 500MB total cache size
  - Eviction: LRU (least recently used)
  - Command: `specify tools cache --status|--clear`
- **Errors**: `Cache directory not accessible: [path]`

**FR-TOOL-005**: Offline Mode
- **Input**: `--offline` flag on any command
- **Output**: Use cached tools only
- **Rules**:
  - Never attempt network downloads
  - Fail fast if required tool not cached
- **Errors**: `Offline mode: [tool] not in cache`

### FR-CI: Local CI/CD (task-085, task-168)

**FR-CI-001**: Local GitHub Actions Execution
- **Input**: `run-local-ci.sh [options]`
- **Output**: CI job results matching GitHub Actions
- **Rules**:
  - Use `act` for local execution
  - Support: `--job lint`, `--job test`, `--job build`, `--job security`
  - Default: run all jobs
- **Errors**: `act not installed. Run: specify tools install act`

**FR-CI-002**: Environment Parity
- **Input**: Local CI execution
- **Output**: Results matching GitHub Actions
- **Rules**:
  - Use same Docker images (ubuntu-latest → catthehacker/ubuntu:act-latest)
  - Mount secrets from `.secrets` file (gitignored)
  - Set same environment variables
- **Errors**: `Docker not running. Start Docker and retry.`

**FR-CI-003**: Cross-Platform Matrix (task-168)
- **Input**: CI workflow definition
- **Output**: Matrix with ubuntu-latest, macos-latest
- **Rules**:
  - Skip platform-specific tests with `[skip-macos]` marker
  - Use `runs-on: ${{ matrix.os }}`
- **Errors**: `macOS runner not available in act. Use GitHub Actions for macOS.`

### FR-OBS: Observability (task-136)

**FR-OBS-001**: claude-trace Integration
- **Input**: User request for observability setup
- **Output**: Documentation and troubleshooting guide
- **Rules**:
  - Document trace collection setup
  - Provide query examples for common debugging scenarios
  - Include token usage tracking guidance
- **Errors**: N/A (documentation deliverable)

### FR-DX: Developer Experience (task-171, task-195, task-196, task-197)

**FR-DX-001**: MCP Documentation Research (task-171)
- **Input**: Research request
- **Output**: Evaluation report on MCP alternatives
- **Rules**:
  - Evaluate context7, devdocs-mcp, custom solutions
  - Criteria: coverage, latency, reliability
- **Errors**: N/A (research deliverable)

**FR-DX-002**: Plugin Packaging (task-195) - Deferred
**FR-DX-003**: Output Styles (task-196) - Exploratory
**FR-DX-004**: Statusline (task-197) - Future

## Use Cases

### UC-1: Developer Protected from Committing Secrets
**Actor**: Developer editing files
**Preconditions**: permissions.deny configured
**Flow**:
1. Developer attempts to read `.env` file
2. System blocks with clear error
3. Developer uses proper secrets management instead
**Postconditions**: Sensitive files never exposed

### UC-2: Fast Inner Loop with Local CI
**Actor**: Developer iterating on code
**Preconditions**: act installed, Docker running
**Flow**:
1. Developer runs `./scripts/run-local-ci.sh --job lint`
2. Lint completes in <30 seconds
3. Developer fixes issues immediately
4. Re-runs lint, passes
5. Commits with confidence
**Postconditions**: CI issues caught before push

### UC-3: Debugging Complex Workflow
**Actor**: Developer with failing /jpspec command
**Preconditions**: claude-trace configured
**Flow**:
1. Command fails with unclear error
2. Developer queries trace: `claude-trace query --last`
3. Sees agent decision chain, identifies issue
4. Fixes input, re-runs successfully
**Postconditions**: Issue diagnosed in minutes not hours

### UC-4: Cross-Platform Team Development
**Actor**: Team with Linux and macOS developers
**Preconditions**: CI matrix configured
**Flow**:
1. Developer on macOS commits code
2. CI runs on both ubuntu-latest and macos-latest
3. Catches platform-specific issue
4. Developer fixes before merge
**Postconditions**: Code works on all team platforms

### UC-5: Tool Auto-Installation
**Actor**: New developer running security scan
**Preconditions**: Semgrep not installed
**Flow**:
1. Developer runs `/jpspec:validate`
2. System detects Semgrep not installed
3. Prompts: "Semgrep required. Install now? [Y/n]"
4. Downloads and installs to cache
5. Scan proceeds automatically
**Postconditions**: Zero manual tool setup

## Data Entities

### Security Rule
```yaml
rule_id: string
pattern: glob | regex
action: deny | confirm | allow
scope: read | write | execute
message: string
```

### Tool Installation
```yaml
tool_name: string
version: semver
install_method: pip | binary | npm
checksum: sha256
installed_at: timestamp
last_used: timestamp
```

### Audit Log Entry
```yaml
timestamp: ISO-8601
event_type: deny | override | confirm
user: string
resource: path | command
rule_id: string
outcome: blocked | allowed
reason: string (optional)
```
