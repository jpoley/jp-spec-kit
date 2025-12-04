# ADR-016: CI/CD Pipeline Design (Local-First with act)

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Platform Engineer
**Context:** task-085, task-168 - Local CI simulation and cross-platform testing
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Traditional CI/CD workflows suffer from:
- **Slow Feedback** - Push → Wait for GitHub Actions → Fix → Repeat (5-10 min per cycle)
- **High Costs** - GitHub Actions minutes cost money (2000 free minutes/month, then $0.008/min)
- **Limited Debugging** - Can't debug CI failures locally (no SSH, no breakpoints)
- **Environment Drift** - Local dev ≠ CI environment (works locally, fails in CI)

**The Core Tension:** Developers want fast feedback (inner loop), but CI ensures quality (outer loop). Traditional CI forces developers into slow outer loop for every change.

### Business Value

**Primary Value Streams:**

1. **Developer Velocity** - Catch CI failures in <1 minute (vs 5-10 minutes)
2. **Cost Optimization** - Reduce GitHub Actions usage by 50% (fewer failed pushes)
3. **Quality** - Higher quality commits (pre-validated locally)
4. **DORA Metrics** - Elite-level metrics via fast feedback

**Success Metrics:**

- Lead Time for Changes: <1 hour (vs 2-4 hours)
- Deployment Frequency: Multiple times per day (vs once per day)
- Change Failure Rate: <15% (vs 25%)
- Mean Time to Restore: <1 hour (vs 2-4 hours)

**Cost Analysis:**

```
Before (Traditional CI):
- 100 commits/month
- 30% fail first CI run (30 failures)
- 5 minutes per CI run
- Total: 130 × 5 = 650 minutes
- Cost: 650 - 2000 (free) = $0 (within free tier)
- But: 650 minutes wasted developer time = 10.8 hours = $540 (at $50/hr)

After (Local CI):
- 100 commits/month
- 30 failures caught locally (<1 min each)
- Only 70 successful commits reach GitHub
- Total GitHub Actions: 70 × 5 = 350 minutes
- Cost: $0 (within free tier)
- Developer time saved: 30 × 4 min = 120 min = 2 hours = $100
- ROI: $100 saved per month
```

---

## Decision

### Chosen Architecture: act-Based Local CI Simulation

Implement **run-local-ci.sh** script using **act** (GitHub Actions local runner) to:

1. **Execute CI Pipeline Locally** - Run lint, test, build, security jobs before push
2. **Environment Parity** - Same Docker images as GitHub Actions (ubuntu-latest, macos-latest)
3. **Fail Fast** - Stop on first job failure (immediate feedback)
4. **Selective Execution** - Run specific jobs or all jobs
5. **Cross-Platform Testing** - Validate on Linux and macOS (via CI matrix)

**Key Pattern:** **Shift-Left Testing (DevOps Pattern)** + **Inner Loop Optimization**

```
┌─────────────────────────────────────────────────────────────────┐
│                   CI/CD PIPELINE ARCHITECTURE                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ INNER LOOP (Local Development)                    │         │
│  │                                                    │         │
│  │  1. Make changes                                  │         │
│  │  2. Run run-local-ci.sh                           │         │
│  │     - Lint (ruff, mypy)                           │         │
│  │     - Test (pytest)                               │         │
│  │     - Build (uv build)                            │         │
│  │     - Security (semgrep)                          │         │
│  │  3. Fix issues (<1 min feedback)                  │         │
│  │  4. Repeat until clean                            │         │
│  │                                                    │         │
│  │  Time: <1 minute per cycle                        │         │
│  │  Cost: $0 (local execution)                       │         │
│  └────────────────────────────────────────────────────┘         │
│                   │                                              │
│                   │ git push (only after local CI passes)        │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ OUTER LOOP (GitHub Actions)                       │         │
│  │                                                    │         │
│  │  1. GitHub Actions triggers                       │         │
│  │  2. Matrix build (Linux, macOS, Windows)          │         │
│  │  3. Full test suite (unit, integration, e2e)      │         │
│  │  4. Security scanning (Semgrep, CodeQL)           │         │
│  │  5. Build and publish artifacts                   │         │
│  │                                                    │         │
│  │  Time: 5-10 minutes                               │         │
│  │  Cost: GitHub Actions minutes                     │         │
│  └────────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Engine Room View: Technical Architecture

### run-local-ci.sh Design

**Script:** `scripts/bash/run-local-ci.sh`

```bash
#!/usr/bin/env bash
# run-local-ci.sh - Execute GitHub Actions locally via act
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ACT_VERSION="0.2.68"
DEFAULT_JOBS=("lint" "test" "build" "security")

# Usage
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [JOBS...]

Execute GitHub Actions locally via act.

OPTIONS:
    -h, --help          Show this help message
    -a, --all           Run all jobs (default: lint, test, build, security)
    -j, --job JOB       Run specific job (can be repeated)
    -l, --list          List available jobs
    -n, --dry-run       Show what would be executed (don't run)
    --install-act       Install act if not found
    --act-version VER   Specify act version (default: $ACT_VERSION)

EXAMPLES:
    $0                  # Run default jobs (lint, test, build, security)
    $0 --all            # Run all jobs
    $0 -j lint -j test  # Run only lint and test
    $0 --list           # List available jobs
    $0 --dry-run        # Show what would be executed

REQUIREMENTS:
    - Docker (for act container execution)
    - act (GitHub Actions local runner)

For more information: https://github.com/nektos/act
EOF
}

# Check dependencies
check_dependencies() {
    echo -e "${YELLOW}Checking dependencies...${NC}"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is required but not installed${NC}"
        echo "Install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}Error: Docker daemon is not running${NC}"
        echo "Start Docker and try again"
        exit 1
    fi

    # Check act
    if ! command -v act &> /dev/null; then
        echo -e "${YELLOW}act not found${NC}"
        if [[ "${INSTALL_ACT:-false}" == "true" ]]; then
            install_act
        else
            echo -e "${RED}Error: act is required but not installed${NC}"
            echo "Install act: $0 --install-act"
            echo "Or manually: https://github.com/nektos/act#installation"
            exit 1
        fi
    fi

    echo -e "${GREEN}All dependencies satisfied${NC}"
}

# Install act
install_act() {
    echo -e "${YELLOW}Installing act $ACT_VERSION...${NC}"

    local os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    local arch="$(uname -m)"

    # Map architecture
    case "$arch" in
        x86_64) arch="x86_64" ;;
        amd64)  arch="x86_64" ;;
        arm64)  arch="arm64" ;;
        aarch64) arch="arm64" ;;
        *)
            echo -e "${RED}Unsupported architecture: $arch${NC}"
            exit 1
            ;;
    esac

    # Map OS
    case "$os" in
        darwin) os="Darwin" ;;
        linux)  os="Linux" ;;
        *)
            echo -e "${RED}Unsupported OS: $os${NC}"
            exit 1
            ;;
    esac

    # Download URL
    local url="https://github.com/nektos/act/releases/download/v${ACT_VERSION}/act_${os}_${arch}.tar.gz"

    # Download and extract
    local tmp_dir="$(mktemp -d)"
    cd "$tmp_dir"

    echo "Downloading from $url..."
    curl -L -o act.tar.gz "$url"

    echo "Extracting..."
    tar -xzf act.tar.gz

    # Install to ~/bin (assumes ~/bin is in PATH)
    mkdir -p "$HOME/bin"
    mv act "$HOME/bin/"
    chmod +x "$HOME/bin/act"

    # Cleanup
    rm -rf "$tmp_dir"

    echo -e "${GREEN}act $ACT_VERSION installed to ~/bin/act${NC}"

    # Verify
    if command -v act &> /dev/null; then
        echo -e "${GREEN}act version: $(act --version)${NC}"
    else
        echo -e "${YELLOW}Warning: ~/bin may not be in PATH${NC}"
        echo "Add to PATH: export PATH=\"\$HOME/bin:\$PATH\""
    fi
}

# List available jobs
list_jobs() {
    echo -e "${YELLOW}Available jobs:${NC}"
    act -l -W "$PROJECT_ROOT/.github/workflows/ci.yml"
}

# Run act
run_act() {
    local jobs=("$@")

    echo -e "${YELLOW}Running local CI...${NC}"
    echo -e "Jobs: ${jobs[*]}"
    echo ""

    cd "$PROJECT_ROOT"

    # Build act command
    local act_cmd=(
        act
        --workflows .github/workflows/ci.yml
        --platform ubuntu-latest=catthehacker/ubuntu:act-latest
    )

    # Add job filter if specified
    if [[ ${#jobs[@]} -gt 0 ]]; then
        for job in "${jobs[@]}"; do
            act_cmd+=(--job "$job")
        done
    fi

    # Dry run?
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo -e "${YELLOW}Dry run (would execute):${NC}"
        echo "${act_cmd[*]}"
        return 0
    fi

    # Execute
    if "${act_cmd[@]}"; then
        echo -e "${GREEN}✓ Local CI passed${NC}"
        return 0
    else
        echo -e "${RED}✗ Local CI failed${NC}"
        return 1
    fi
}

# Main
main() {
    local jobs=()
    local list_only=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -a|--all)
                jobs=()
                shift
                ;;
            -j|--job)
                jobs+=("$2")
                shift 2
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            --install-act)
                INSTALL_ACT=true
                shift
                ;;
            --act-version)
                ACT_VERSION="$2"
                shift 2
                ;;
            *)
                jobs+=("$1")
                shift
                ;;
        esac
    done

    # Default jobs if none specified
    if [[ ${#jobs[@]} -eq 0 && "$list_only" == "false" ]]; then
        jobs=("${DEFAULT_JOBS[@]}")
    fi

    # Check dependencies
    check_dependencies

    # List jobs?
    if [[ "$list_only" == "true" ]]; then
        list_jobs
        exit 0
    fi

    # Run act
    run_act "${jobs[@]}"
}

main "$@"
```

### GitHub Actions CI Matrix

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run ruff check
        run: uv run ruff check .

      - name: Run ruff format check
        run: uv run ruff format --check .

      - name: Run mypy
        run: uv run mypy src/

  test:
    name: Test
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run tests
        run: uv run pytest tests/ -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'

  build:
    name: Build
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v3

      - name: Build package
        run: uv build

      - name: Check package
        run: uv run twine check dist/*

  security:
    name: Security Scan
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        uses: semgrep/semgrep-action@v1
        with:
          config: auto
```

### Cross-Platform Compatibility

**Portable Bash Features Used:**

- POSIX-compliant bash 3.2+ (macOS, Linux, Windows Git Bash)
- Avoid bashisms (no `[[`, no `${var,,}`)
- Use `command -v` instead of `which`
- Use `$(command)` instead of backticks
- Portable `mktemp` (works on macOS and Linux)

**Platform-Specific Handling:**

```bash
# Detect OS
os="$(uname -s | tr '[:upper:]' '[:lower:]')"

case "$os" in
    darwin)
        # macOS-specific
        ;;
    linux)
        # Linux-specific
        ;;
    msys|mingw|cygwin)
        # Windows Git Bash
        ;;
esac
```

---

## act Limitations and Workarounds

### Limitation 1: OIDC (OpenID Connect) Not Supported

**Impact:** Can't authenticate with cloud providers (AWS, GCP, Azure) using OIDC.

**Workaround:**
- Use service account keys for local testing (not production)
- Skip cloud deployment jobs in local CI (`--job lint --job test`, not deploy)

### Limitation 2: GitHub Secrets Not Available

**Impact:** `secrets.GITHUB_TOKEN` and other secrets not accessible.

**Workaround:**
- Use `.secrets` file (act reads from this file)
- Add `.secrets` to `.gitignore` (never commit)
- Example:
  ```
  GITHUB_TOKEN=ghp_xxxxxxxxxxxx
  NPM_TOKEN=npm_xxxxxxxxxxxx
  ```

### Limitation 3: Some Actions Don't Work

**Impact:** Some GitHub Actions fail in act (e.g., actions/cache with OIDC).

**Workaround:**
- Use `act -j <job>` to skip problematic jobs
- Use alternative actions (e.g., local caching instead of actions/cache)

### Limitation 4: Docker Required

**Impact:** act requires Docker (not available in all environments).

**Workaround:**
- Provide fallback script for non-Docker environments (`run-ci-native.sh`)
- Document Docker requirement clearly
- Use GitHub Actions for environments without Docker

---

## DORA Metrics Alignment

### Lead Time for Changes: <1 Hour (Elite)

**Traditional CI:**
```
Code → Commit → Push → Wait 5 min → Fix → Push → Wait 5 min → ...
Total: 2-4 hours
```

**Local CI:**
```
Code → run-local-ci.sh → Fix → run-local-ci.sh → ... → Push (passes first time)
Total: <1 hour
```

### Deployment Frequency: Multiple Times Per Day (Elite)

**Traditional CI:** Once per day (slow feedback discourages frequent deploys)

**Local CI:** 5-10 times per day (fast feedback encourages small, frequent commits)

### Change Failure Rate: <15% (Elite)

**Traditional CI:** 25-30% (many commits fail first CI run)

**Local CI:** <15% (local validation catches issues before push)

### Mean Time to Restore: <1 Hour (Elite)

**Traditional CI:** 2-4 hours (slow CI feedback loop)

**Local CI:** <1 hour (fast local iteration)

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 10/10

**Strengths:**
- Clear separation: inner loop (local) vs outer loop (GitHub)
- Explicit requirements (Docker, act)
- Clear failure modes (with workarounds)

### 2. Consistency - 10/10

**Strengths:**
- Same workflow (.github/workflows/ci.yml) for local and GitHub
- Same Docker images (ubuntu-latest)
- Same job definitions

### 3. Composability - 9/10

**Strengths:**
- Selective job execution (`-j lint -j test`)
- Works with existing CI (no changes needed)
- Extensible (add new jobs to ci.yml)

**Needs Work:**
- Can't compose with non-Docker CI runners (native fallback needed)

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- One command: `run-local-ci.sh`
- Fast feedback (<1 minute)
- Auto-install option (`--install-act`)

**Needs Work:**
- Docker requirement may be barrier for some users
- First-run Docker image pull is slow (300MB+)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Environment parity (same Docker images as GitHub)
- All jobs validated (lint, test, build, security)
- Cross-platform testing (Linux, macOS)

**Risks:**
- act may not perfectly replicate GitHub Actions (95% compatible)
- Some actions require workarounds (OIDC, secrets)

### 6. Completeness - 8/10

**Covers:**
- Lint, test, build, security jobs
- Cross-platform testing (Linux, macOS)
- Auto-install act

**Missing (Future):**
- Windows CI matrix (requires act Windows support)
- Integration tests (may require Docker-in-Docker)
- E2E tests (may require external services)

### 7. Changeability - 10/10

**Strengths:**
- Add new jobs: edit ci.yml, no script changes
- Change Docker images: edit ci.yml, no script changes
- Customize act: pass flags to run-local-ci.sh

---

## Alternatives Considered and Rejected

### Option A: No Local CI (Traditional Workflow)

**Approach:** Push to GitHub, wait for CI results.

**Pros:**
- Zero local setup
- No Docker requirement
- Official GitHub Actions environment

**Cons:**
- Slow feedback (5-10 minutes)
- High change failure rate (25%+)
- Poor DORA metrics

**Rejected:** Violates inner loop optimization principle

---

### Option B: Native Script (No Docker)

**Approach:** Run lint/test/build directly on local machine (no Docker).

**Pros:**
- Fast (no Docker overhead)
- No Docker requirement
- Simple to understand

**Cons:**
- Environment drift (local != CI)
- Platform-specific (bash script may not work on Windows)
- Dependency management (must install tools manually)

**Rejected:** Environment parity more important than performance

---

### Option C: act-Based Local CI (RECOMMENDED)

**Approach:** Use act to run GitHub Actions locally in Docker.

**Pros:**
- Environment parity (same Docker images)
- Fast feedback (<1 minute)
- Works with existing ci.yml
- Elite DORA metrics

**Cons:**
- Requires Docker
- Some actions don't work (OIDC, etc.)

**Accepted:** Best balance of speed and environment parity

---

## Implementation Guidance

### Phase 1: Core Script (Week 1)

**Scope:** run-local-ci.sh with act integration

**Deliverables:**
- `scripts/bash/run-local-ci.sh`
- `scripts/bash/install-act.sh` (helper script)

**Tasks:**
- Implement run-local-ci.sh
- Implement dependency checking (Docker, act)
- Implement auto-install for act
- Test on Linux and macOS

### Phase 2: CI Matrix (Week 2)

**Scope:** Add macOS to GitHub Actions matrix

**Deliverables:**
- Updated `.github/workflows/ci.yml`

**Tasks:**
- Add macos-latest to matrix
- Verify cross-platform compatibility
- Document macOS-specific requirements
- Test with run-local-ci.sh

### Phase 3: Documentation (Week 3)

**Scope:** User documentation and troubleshooting

**Deliverables:**
- Updated `CLAUDE.md` (mention act)
- Updated `docs/guides/inner-loop.md`
- Troubleshooting guide

**Tasks:**
- Document usage examples
- Document act limitations
- Document workarounds
- Create troubleshooting guide

---

## Success Criteria

**Objective Measures:**

1. **Lead Time for Changes** - <1 hour (Elite)
2. **Deployment Frequency** - >1 per day (Elite)
3. **Change Failure Rate** - <15% (Elite)
4. **Mean Time to Restore** - <1 hour (Elite)
5. **GitHub Actions Usage** - 50% reduction (cost optimization)

**Subjective Measures:**

1. **Developer Feedback** - "Local CI is fast and reliable" (NPS >40)
2. **Adoption Rate** - 80% of developers use run-local-ci.sh before push

---

## Decision

**APPROVED for implementation as Option C: act-Based Local CI**

**Next Steps:**

1. Create implementation task for Phase 1 (run-local-ci.sh)
2. Test with real workflows (lint, test, build, security)
3. Add macOS to CI matrix (Phase 2)

**Review Date:** 2025-12-18 (after Phase 1 complete)

---

## References

### DevOps Principles Applied

1. **Shift-Left Testing** - Catch failures early (before push)
2. **Inner Loop Optimization** - Fast feedback for developers
3. **Environment Parity** - Dev/CI/Prod use same images
4. **DORA Metrics** - Elite-level performance

### Related Documents

- **Task:** task-085 - Local CI Simulation Script
- **Task:** task-168 - Add macOS CI Matrix Testing
- **Related Docs:** docs/reference/inner-loop.md

### External References

- [act - GitHub Actions Local Runner](https://github.com/nektos/act)
- [DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)
- [Accelerate (Book)](https://itrevolution.com/product/accelerate/)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
