# Flowspec Improvement Specs v1

**Source**: Analysis of [everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Anthropic hackathon winner, 10+ months production use.

**Purpose**: Extract actionable improvements to make flowspec cleaner, simpler, and more efficient.

**Status**: DRAFT - Research Phase

---

## Executive Summary

After 5 analysis passes comparing flowspec with the hackathon-winning `everything-claude-code` repository, we've identified **15 major improvement opportunities** across these categories:

| Category | Improvement Count | Priority |
|----------|-------------------|----------|
| Architecture Simplification | 4 | Critical |
| Session & Context Management | 3 | High |
| Agent Orchestration | 3 | High |
| Developer Experience | 3 | Medium |
| Testing & Verification | 2 | Medium |

**Key Insight**: `everything-claude-code` achieves more with less. Their commands average ~100 lines; flowspec's `/flow:implement` is 1,400+ lines. Simplicity is the winning pattern.

---

## SPEC-001: Command Decomposition

### Problem

Flowspec commands are monolithic and difficult to maintain:

| Command | Flowspec Lines | everything-claude-code Equivalent |
|---------|----------------|-----------------------------------|
| `/flow:implement` | 1,419 | `/tdd` (200) + `/plan` (90) + `/code-review` (50) |
| `/flow:plan` | ~400 | `/plan` (90) |
| `/flow:validate` | ~600 | `/verify` (50) |

### Solution

Decompose large commands into focused, composable units.

**Current Structure**:
```
/flow:implement
  └── Phase 0: Quality Gate (150 lines)
  └── Phase 0.1: Rigor Rules (300 lines)
  └── Phase 0.5: PRP Loading (100 lines)
  └── Phase 1: Implementation (400 lines)
  └── Phase 2: Code Review (200 lines)
  └── Phase 3: Integration (50 lines)
  └── Phase 4: Pre-PR Validation (200 lines)
```

**Proposed Structure**:
```
/flow:implement  (50 lines - orchestrator only)
  └── Calls: /flow:gate (quality validation)
  └── Calls: /flow:rigor (rigor rule enforcement)
  └── Calls: /flow:build (frontend + backend in parallel)
  └── Calls: /flow:review (code review)
  └── Calls: /flow:pre-pr (validation checklist)
```

### New Commands to Create

| Command | Purpose | Lines Target |
|---------|---------|--------------|
| `/flow:gate` | Quality gate validation | ~50 |
| `/flow:rigor` | Rigor rule enforcement | ~100 |
| `/flow:build` | Parallel implementation orchestration | ~100 |
| `/flow:review` | Code review with AC verification | ~100 |
| `/flow:pre-pr` | Pre-PR validation checklist | ~100 |

### Acceptance Criteria

- [ ] No single command exceeds 200 lines
- [ ] Each command has ONE clear responsibility
- [ ] Commands are composable via orchestration
- [ ] Backward compatibility: `/flow:implement` still works

---

## SPEC-002: Orchestration Command Pattern

### Problem

Flowspec lacks a way to chain agents sequentially with context handoff.

### Solution

Adopt the `/orchestrate` pattern from everything-claude-code.

**New Command**: `/flow:orchestrate`

```markdown
---
description: Sequential agent workflow for complex tasks with context handoff
---

# /flow:orchestrate [workflow-type] [task-description]

## Workflow Types

### feature
Full feature implementation workflow:
```
planner -> tdd-guide -> code-reviewer -> security-reviewer
```

### bugfix
Bug investigation and fix workflow:
```
explorer -> tdd-guide -> code-reviewer
```

### refactor
Safe refactoring workflow:
```
architect -> code-reviewer -> tdd-guide
```

### security
Security-focused review:
```
security-reviewer -> code-reviewer -> architect
```

## Handoff Document Format

Between agents, create structured handoff:

```markdown
## HANDOFF: [previous-agent] -> [next-agent]

### Context
[Summary of what was done]

### Findings
[Key discoveries or decisions]

### Files Modified
[List of files touched]

### Open Questions
[Unresolved items for next agent]

### Recommendations
[Suggested next steps]
```
```

### Acceptance Criteria

- [ ] Handoff documents persist between agents
- [ ] Parallel execution supported for independent agents
- [ ] Final report aggregates all agent outputs
- [ ] Custom workflows via `custom <agents> <description>`

---

## SPEC-003: Session Persistence Hooks

### Problem

Flowspec loses context when sessions end or context compacts. Critical state is lost:
- What was being worked on
- Decisions made and why
- Files modified
- Open questions

### Solution

Implement session persistence hooks like everything-claude-code.

**New Hooks**:

```json
{
  "SessionStart": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "node .claude/hooks/session-start.js"
    }]
  }],
  "SessionEnd": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "node .claude/hooks/session-end.js"
    }]
  }],
  "PreCompact": [{
    "matcher": "*",
    "hooks": [{
      "type": "command",
      "command": "node .claude/hooks/pre-compact.js"
    }]
  }]
}
```

**Session State File** (`.flowspec/session-state.json`):

```json
{
  "lastActivity": "2025-01-24T10:30:00Z",
  "activeTask": "task-543",
  "workingFiles": ["src/cli.py", "tests/test_cli.py"],
  "decisions": [
    {"what": "Use Click for CLI", "why": "Better composability"}
  ],
  "openQuestions": ["How to handle config precedence?"],
  "checkpoint": "abc123"
}
```

### Implementation

**session-start.js**:
```javascript
const state = loadState('.flowspec/session-state.json');
if (state && state.activeTask) {
  console.log(`[Session] Resuming task: ${state.activeTask}`);
  console.log(`[Session] Files: ${state.workingFiles.join(', ')}`);
  console.log(`[Session] Open questions: ${state.openQuestions.length}`);
}
```

**session-end.js**:
```javascript
const state = {
  lastActivity: new Date().toISOString(),
  activeTask: extractTaskFromBranch(),
  workingFiles: getModifiedFiles(),
  decisions: extractDecisionsFromLog()
};
saveState('.flowspec/session-state.json', state);
```

### Acceptance Criteria

- [ ] State persists across session restarts
- [ ] State preserved before context compaction
- [ ] Clear summary displayed on session start
- [ ] Node.js based for cross-platform support

---

## SPEC-004: Continuous Learning Skill

### Problem

Flowspec doesn't extract reusable patterns from sessions. Each session starts from scratch without learning from past solutions.

### Solution

Implement continuous learning with automatic pattern extraction.

**New Skill**: `.claude/skills/continuous-learning/SKILL.md`

```markdown
---
name: continuous-learning
description: Extract reusable patterns from sessions and save as learned skills
---

# Continuous Learning Skill

## How It Works

Runs as a Stop hook at session end:

1. **Session Evaluation**: Check if session has 10+ messages
2. **Pattern Detection**: Identify extractable patterns
3. **Skill Extraction**: Save to `~/.claude/skills/learned/`

## Pattern Types

| Pattern | Description |
|---------|-------------|
| `error_resolution` | How specific errors were resolved |
| `user_corrections` | Patterns from user corrections |
| `workarounds` | Solutions to framework/library quirks |
| `debugging_techniques` | Effective debugging approaches |
| `project_specific` | Project-specific conventions |
```

**New Command**: `/flow:learn`

```markdown
# /flow:learn - Extract Reusable Patterns

Analyze current session and extract patterns worth saving.

## What to Extract

1. **Error Resolution Patterns**
   - What error occurred?
   - What was the root cause?
   - What fixed it?

2. **Debugging Techniques**
   - Non-obvious debugging steps
   - Tool combinations that worked

3. **Workarounds**
   - Library quirks
   - API limitations
   - Version-specific fixes

## Output

Create skill file at `.claude/skills/learned/[pattern-name].md`:

```markdown
# [Descriptive Pattern Name]

**Extracted:** [Date]
**Context:** [When this applies]

## Problem
[What problem this solves]

## Solution
[The pattern/technique/workaround]

## Example
[Code example if applicable]
```
```

### Acceptance Criteria

- [ ] Patterns extracted automatically at session end
- [ ] Manual extraction via `/flow:learn` command
- [ ] Learned skills loaded on session start
- [ ] Skill files are human-readable and editable

---

## SPEC-005: Strategic Compaction

### Problem

Context compaction happens at arbitrary points, often mid-task, losing important context.

### Solution

Implement strategic compaction suggestions at logical boundaries.

**New Skill**: `.claude/skills/strategic-compact/SKILL.md`

```markdown
---
name: strategic-compact
description: Suggest manual /compact at logical workflow boundaries
---

# Strategic Compact Skill

## Why Strategic Compaction?

Auto-compaction triggers arbitrarily:
- Often mid-task, losing important context
- No awareness of logical task boundaries

Strategic compaction at logical boundaries:
- **After exploration, before execution** - Compact research, keep implementation plan
- **After completing a milestone** - Fresh start for next phase
- **Before major context shifts** - Clear exploration context

## Suggestion Triggers

1. **Tool call threshold**: After 50 Edit/Write operations
2. **Phase completion**: After /flow:plan completes
3. **Manual request**: Via /flow:compact
```

**Hook Implementation**:

```json
{
  "PreToolUse": [{
    "matcher": "Edit|Write",
    "hooks": [{
      "type": "command",
      "command": "node .claude/hooks/suggest-compact.js"
    }]
  }]
}
```

**suggest-compact.js**:
```javascript
const THRESHOLD = parseInt(process.env.COMPACT_THRESHOLD || '50');
const count = incrementToolCount();

if (count === THRESHOLD) {
  console.error('[Strategic Compact] 50 edits reached');
  console.error('[Strategic Compact] Consider: /compact');
}
if (count > THRESHOLD && (count - THRESHOLD) % 25 === 0) {
  console.error(`[Strategic Compact] ${count} edits - context growing`);
}
```

### Acceptance Criteria

- [ ] Suggestions at configurable thresholds (default: 50)
- [ ] State saved before compaction
- [ ] Suggestions are non-blocking
- [ ] Clear messaging about what will be preserved

---

## SPEC-006: Modular Rules Architecture

### Problem

Flowspec's rules are embedded in commands and CLAUDE.md imports, making them hard to maintain and override.

### Solution

Extract rules into modular, standalone files like everything-claude-code.

**Current State**:
```
CLAUDE.md
  └── @import memory/critical-rules.md (253 lines)
  └── @import memory/code-standards.md
  └── @import .claude/partials/flow/_rigor-rules.md
```

**Proposed State**:
```
.claude/rules/
  ├── security.md          # No hardcoded secrets, injection prevention
  ├── coding-style.md      # Immutability, file limits, naming
  ├── testing.md           # TDD, coverage requirements
  ├── git-workflow.md      # Commit format, PR process
  ├── agents.md            # When to delegate to subagents
  ├── performance.md       # Model selection, context management
  └── rigor.md             # Workflow quality gates (extracted from _rigor-rules.md)
```

**Example**: `.claude/rules/agents.md`

```markdown
# Agent Orchestration Rules

## Immediate Agent Usage (No User Prompt Needed)

| Trigger | Agent |
|---------|-------|
| Complex feature requests | planner |
| Code just written/modified | code-reviewer |
| Bug fix or new feature | tdd-guide |
| Architectural decision | architect |

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis
2. Agent 2: Performance review
3. Agent 3: Type checking

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```
```

### Acceptance Criteria

- [ ] Each rule file < 100 lines
- [ ] Rules independently loadable
- [ ] Override mechanism per-project
- [ ] CLAUDE.md becomes leaner

---

## SPEC-007: Model Selection Guidance

### Problem

Flowspec doesn't provide clear guidance on when to use different models (Haiku/Sonnet/Opus).

### Solution

Add explicit model selection rules based on everything-claude-code patterns.

**New File**: `.claude/rules/performance.md`

```markdown
# Performance Optimization

## Model Selection Strategy

### Haiku (90% of Sonnet capability, 3x cost savings)
- Lightweight agents with frequent invocation
- Pair programming and code generation
- Worker agents in multi-agent systems
- Quick lookups and simple tasks

### Sonnet (Best coding model)
- Main development work
- Orchestrating multi-agent workflows
- Complex coding tasks
- Default for most operations

### Opus (Deepest reasoning)
- Complex architectural decisions
- Maximum reasoning requirements
- Research and analysis tasks
- Multi-step planning

## Context Window Management

**Critical**: Don't enable all MCPs at once.

Rule of thumb:
- 20-30 MCPs configured total
- Under 10 enabled per project
- Under 80 tools active

Use `disabledMcpServers` in project config:

```json
{
  "disabledMcpServers": [
    "unused-server-1",
    "unused-server-2"
  ]
}
```

## Agent Tool Specification

Agents should declare their tools explicitly:

```markdown
---
name: planner
tools: Read, Grep, Glob
model: opus
---
```

This prevents tool bloat in delegated tasks.
```

### Acceptance Criteria

- [ ] Clear decision tree for model selection
- [ ] Agent definitions include `model` field
- [ ] MCP management guidance documented
- [ ] Cost optimization patterns explicit

---

## SPEC-008: Cross-Platform Hook Scripts

### Problem

Flowspec hooks are bash-only, limiting Windows compatibility.

### Solution

Rewrite hooks in Node.js for cross-platform support.

**Current**:
```
.claude/hooks/
  ├── session-start.sh          # Bash
  ├── post-tool-use-format-python.sh
  ├── pre-tool-use-git-safety.py
  └── run-hook.sh
```

**Proposed**:
```
.claude/hooks/
  ├── lib/
  │   ├── utils.js              # Cross-platform utilities
  │   └── package-manager.js    # PM detection
  ├── session-start.js          # Node.js
  ├── session-end.js
  ├── pre-compact.js
  ├── suggest-compact.js
  ├── evaluate-session.js
  └── format-python.js
```

**Shared Utilities** (`lib/utils.js`):

```javascript
const path = require('path');
const fs = require('fs');
const os = require('os');

function getSessionsDir() {
  return path.join(os.homedir(), '.claude', 'sessions');
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function findFiles(dir, pattern, options = {}) {
  // Cross-platform file search
}

module.exports = { getSessionsDir, ensureDir, findFiles };
```

### Acceptance Criteria

- [ ] All hooks work on Windows, macOS, Linux
- [ ] Shared utility library for common operations
- [ ] No bash dependencies in hook execution
- [ ] Python hooks converted to Node.js or called via `node`

---

## SPEC-009: Verification Loop Command

### Problem

Verification is embedded in `/flow:implement` (200+ lines). Should be standalone for reuse.

### Solution

Create dedicated `/flow:verify` command.

**New Command**: `/flow:verify`

```markdown
---
description: Comprehensive verification before PR or at checkpoints
---

# /flow:verify [quick|full]

## Verification Phases

### Phase 1: Build Verification
```bash
# Check if project builds
npm run build 2>&1 | tail -20
```
If build fails, STOP and fix.

### Phase 2: Type Check
```bash
# Python
uv run pyright . 2>&1 | head -30

# TypeScript
npx tsc --noEmit 2>&1 | head -30
```

### Phase 3: Lint Check
```bash
# Python
uv run ruff check . 2>&1 | head -30

# TypeScript
npm run lint 2>&1 | head -30
```

### Phase 4: Test Suite
```bash
# Run tests with coverage
pytest --cov 2>&1 | tail -50
```

Report:
- Total tests: X
- Passed: X
- Failed: X
- Coverage: X%

### Phase 5: Security Scan
```bash
# Check for secrets
grep -rn "sk-" --include="*.py" . | head -10

# Check for console.log
grep -rn "console.log" --include="*.ts" src/ | head -10
```

### Phase 6: Diff Review
```bash
git diff --stat
git diff HEAD~1 --name-only
```

## Output Format

```
VERIFICATION REPORT
==================

Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]

Overall:   [READY/NOT READY] for PR
```
```

### Acceptance Criteria

- [ ] Standalone command, not embedded in implement
- [ ] Quick mode (build + lint + tests only)
- [ ] Full mode (all 6 phases)
- [ ] Clear pass/fail report

---

## SPEC-010: Checkpoint Command

### Problem

No way to create named save points and compare against them.

### Solution

Add `/flow:checkpoint` command.

**New Command**: `/flow:checkpoint`

```markdown
---
description: Create or verify named checkpoints in workflow
---

# /flow:checkpoint [create|verify|list] [name]

## Create Checkpoint

1. Run `/flow:verify quick` to ensure clean state
2. Create git stash or commit with checkpoint name
3. Log checkpoint to `.flowspec/checkpoints.log`:

```bash
echo "$(date +%Y-%m-%d-%H:%M) | $NAME | $(git rev-parse --short HEAD)" >> .flowspec/checkpoints.log
```

## Verify Against Checkpoint

Compare current state to checkpoint:
- Files added since checkpoint
- Files modified since checkpoint
- Test pass rate now vs then
- Coverage now vs then

```
CHECKPOINT COMPARISON: $NAME
============================
Files changed: X
Tests: +Y passed / -Z failed
Coverage: +X% / -Y%
Build: [PASS/FAIL]
```

## Workflow

```
[Start] --> /flow:checkpoint create "feature-start"
   |
[Implement] --> /flow:checkpoint create "core-done"
   |
[Test] --> /flow:checkpoint verify "core-done"
   |
[Refactor] --> /flow:checkpoint create "refactor-done"
   |
[PR] --> /flow:checkpoint verify "feature-start"
```
```

### Acceptance Criteria

- [ ] Named checkpoints with git SHA
- [ ] Comparison reports changes since checkpoint
- [ ] List all checkpoints with status
- [ ] Clear old checkpoints (keep last 5)

---

## SPEC-011: Simplified CLAUDE.md

### Problem

Flowspec's CLAUDE.md is ~800 lines with many @imports, making it slow to load and hard to understand.

### Solution

Slim down CLAUDE.md to essentials, move details to rules and skills.

**Current CLAUDE.md Structure**:
```markdown
# Flowspec - Claude Code Configuration (800+ lines)
├── Project Overview
├── Essential Commands
├── Slash Commands (detailed)
├── Default Development Mode
├── INITIAL Document Workflow
├── Engineering Subagents
├── Workflow Configuration
├── @import memory/critical-rules.md (253 lines)
├── @import .claude/partials/flow/_rigor-rules.md
├── Project Structure
├── @import memory/code-standards.md
├── @import memory/test-quality-standards.md
├── Task Management
├── Documentation References
├── @import memory/mcp-configuration.md
├── Environment Variables
├── @import memory/claude-hooks.md
├── @import memory/claude-checkpoints.md
├── @import memory/claude-skills.md
├── @import memory/claude-thinking.md
└── Quick Troubleshooting
```

**Proposed CLAUDE.md Structure** (target: 200 lines):
```markdown
# Flowspec - Claude Code Configuration

## Project Overview
[Brief: 50 words max]

## Essential Commands
```bash
pytest tests/
ruff check . && ruff format .
backlog task list --plain
```

## Slash Commands
| Command | Purpose |
|---------|---------|
| /flow:implement | Implementation with review |
| /flow:plan | Create implementation plan |
...

## Quick Reference
- Tests: `pytest tests/`
- Lint: `ruff check . --fix`
- Tasks: `backlog task list`

## Structure
```
src/         # CLI source
tests/       # Test suite
templates/   # Project templates
```

## Troubleshooting
- Dependencies: `uv sync --force`
- CLI: `uv tool install . --force`
```

**Move to `.claude/rules/`**:
- critical-rules.md -> `.claude/rules/critical.md`
- code-standards.md -> `.claude/rules/coding-style.md`
- rigor-rules.md -> `.claude/rules/rigor.md`

### Acceptance Criteria

- [ ] CLAUDE.md under 200 lines
- [ ] No embedded code examples > 10 lines
- [ ] Rules moved to `.claude/rules/`
- [ ] @imports reduced to essential only

---

## SPEC-012: Agent Definitions Cleanup

### Problem

Agent definitions are verbose with embedded instructions that should be in skills.

**Current** (`backend-engineer.md`): ~400 lines with full context inline
**Target**: ~50 lines referencing skills

### Solution

Slim agents to metadata + skill references.

**Current Structure**:
```markdown
---
name: backend-engineer
tools: Read, Write, Edit, Glob, Grep, Bash
---

# AGENT CONTEXT: Senior Backend Engineer
[400 lines of inline instructions]
```

**Proposed Structure**:
```markdown
---
name: backend-engineer
description: Backend implementation - APIs, databases, Python, business logic
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
skills:
  - coding-standards
  - backend-patterns
  - tdd-workflow
  - security-review
---

# Backend Engineer

You are a Senior Backend Engineer. Follow the skills listed above.

## Backlog Task Management

@import .claude/partials/backlog-task-workflow.md

## Pre-Completion Checklist

- [ ] No unused imports
- [ ] All inputs validated
- [ ] Types annotated
- [ ] Tests pass
```

### Acceptance Criteria

- [ ] Agent files under 100 lines
- [ ] Skills referenced, not duplicated
- [ ] Consistent structure across all agents
- [ ] Model specified per agent

---

## SPEC-013: TDD Command

### Problem

Flowspec lacks a dedicated TDD workflow command.

### Solution

Add `/flow:tdd` command inspired by everything-claude-code.

**New Command**: `/flow:tdd`

```markdown
---
description: Test-driven development workflow - tests first, then implement
---

# /flow:tdd [feature-description]

## TDD Cycle

```
RED -> GREEN -> REFACTOR -> REPEAT

RED:      Write failing test
GREEN:    Write minimal code to pass
REFACTOR: Improve code, keep tests passing
REPEAT:   Next feature/scenario
```

## Workflow

### Step 1: Define Interface (SCAFFOLD)
```python
def calculate_score(data: MarketData) -> float:
    raise NotImplementedError()
```

### Step 2: Write Failing Test (RED)
```python
def test_high_score_for_liquid_market():
    market = MarketData(volume=100000, spread=0.01)
    score = calculate_score(market)
    assert score > 80
```

### Step 3: Run Test (Verify FAIL)
```bash
pytest tests/test_score.py -x
# Should FAIL - not implemented yet
```

### Step 4: Write Minimal Implementation (GREEN)
```python
def calculate_score(data: MarketData) -> float:
    return min(data.volume / 1000, 100)
```

### Step 5: Run Test (Verify PASS)
```bash
pytest tests/test_score.py -x
# Should PASS
```

### Step 6: Refactor (IMPROVE)
[Improve code while keeping tests green]

### Step 7: Check Coverage
```bash
pytest --cov --cov-report=term-missing
# Target: 80%+
```

## Best Practices

DO:
- Write test FIRST
- Verify test FAILS before implementing
- Write minimal code to pass
- Refactor only after green

DON'T:
- Write implementation before tests
- Skip running tests
- Write too much code at once
```

### Acceptance Criteria

- [ ] Clear RED-GREEN-REFACTOR cycle
- [ ] Coverage verification step
- [ ] Integrates with `/flow:implement`
- [ ] Examples for Python, TypeScript, Go

---

## SPEC-014: Plugin Architecture

### Problem

Flowspec requires manual installation. No way to share configurations easily.

### Solution

Add plugin manifest for Claude Code plugin system.

**New File**: `.claude-plugin/plugin.json`

```json
{
  "name": "flowspec",
  "description": "Spec-Driven Development toolkit with multi-agent orchestration",
  "author": {
    "name": "Jason Poley",
    "url": "https://github.com/jpoley"
  },
  "homepage": "https://github.com/jpoley/flowspec",
  "license": "MIT",
  "keywords": [
    "sdd",
    "spec-driven-development",
    "agents",
    "workflow",
    "backlog"
  ],
  "commands": "./templates/commands",
  "skills": "./templates/skills",
  "agents": "./templates/agents"
}
```

**New File**: `.claude-plugin/marketplace.json`

```json
{
  "plugins": {
    "flowspec": {
      "name": "Flowspec",
      "version": "0.4.0",
      "description": "Spec-Driven Development toolkit",
      "path": "."
    }
  }
}
```

**Installation**:
```bash
# Plugin installation (future)
/plugin marketplace add jpoley/flowspec
/plugin install flowspec@flowspec
```

### Acceptance Criteria

- [ ] Plugin manifest created
- [ ] Marketplace manifest created
- [ ] README documents plugin installation
- [ ] Templates organized for plugin structure

---

## SPEC-015: Hook Test Suite

### Problem

Flowspec hooks aren't tested. Breaking changes go undetected.

### Solution

Add Node.js test suite for hooks.

**New Structure**:
```
.claude/hooks/
  ├── tests/
  │   ├── run-all.js
  │   ├── lib/
  │   │   ├── utils.test.js
  │   │   └── package-manager.test.js
  │   └── hooks/
  │       ├── session-start.test.js
  │       ├── suggest-compact.test.js
  │       └── evaluate-session.test.js
```

**Test Example** (`tests/hooks/suggest-compact.test.js`):

```javascript
const { test, describe, beforeEach } = require('node:test');
const assert = require('node:assert');
const { suggestCompact, incrementCount, resetCount } = require('../../suggest-compact');

describe('suggest-compact', () => {
  beforeEach(() => {
    resetCount();
  });

  test('suggests at threshold', () => {
    for (let i = 0; i < 49; i++) incrementCount();
    assert.strictEqual(suggestCompact(), false);
    incrementCount();
    assert.strictEqual(suggestCompact(), true);
  });

  test('suggests every 25 after threshold', () => {
    for (let i = 0; i < 50; i++) incrementCount();
    for (let i = 0; i < 24; i++) incrementCount();
    assert.strictEqual(suggestCompact(), false);
    incrementCount();
    assert.strictEqual(suggestCompact(), true);
  });
});
```

**Run Tests**:
```bash
node .claude/hooks/tests/run-all.js
```

### Acceptance Criteria

- [ ] Test suite for all hooks
- [ ] Tests run with `node tests/run-all.js`
- [ ] Coverage for edge cases
- [ ] CI integration possible

---

## Implementation Priority

### Phase 1: Critical (Do First)
1. **SPEC-001**: Command Decomposition
2. **SPEC-011**: Simplified CLAUDE.md
3. **SPEC-006**: Modular Rules Architecture
4. **SPEC-012**: Agent Definitions Cleanup

### Phase 2: High Priority
5. **SPEC-003**: Session Persistence Hooks
6. **SPEC-005**: Strategic Compaction
7. **SPEC-009**: Verification Loop Command
8. **SPEC-002**: Orchestration Command Pattern

### Phase 3: Medium Priority
9. **SPEC-004**: Continuous Learning Skill
10. **SPEC-007**: Model Selection Guidance
11. **SPEC-008**: Cross-Platform Hook Scripts
12. **SPEC-013**: TDD Command

### Phase 4: Enhancement
13. **SPEC-010**: Checkpoint Command
14. **SPEC-014**: Plugin Architecture
15. **SPEC-015**: Hook Test Suite

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| CLAUDE.md lines | ~800 | <200 |
| Largest command lines | 1,419 | <200 |
| Agent file lines | ~400 | <100 |
| Cross-platform hooks | 0% | 100% |
| Hook test coverage | 0% | 80% |
| Session persistence | None | Full |

---

## References

- [everything-claude-code](https://github.com/affaan-m/everything-claude-code) - Source of patterns
- [Shorthand Guide](https://x.com/affaanmustafa/status/2012378465664745795) - Setup and foundations
- [Longform Guide](https://x.com/affaanmustafa/status/2014040193557471352) - Advanced patterns

---

*Generated: 2025-01-24*
*Version: 1.0*
*Status: DRAFT - For Review*
