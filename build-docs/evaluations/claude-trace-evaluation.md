# Claude-Trace Evaluation

**Evaluation Date**: 2025-11-28
**Status**: NOT RECOMMENDED
**Verdict**: Not Now (Stability Issues + Scope Concerns)

---

## Executive Summary

This document evaluates whether Flowspec should add primary support for **claude-trace**, a tool that intercepts and records API communications between Claude Code and Anthropic's API. After extensive research, the recommendation is **NOT to add support at this time** due to critical stability issues (14 open bugs) and misalignment with Flowspec's Spec-Driven Development mission.

---

## What is claude-trace?

### Overview

**claude-trace** is a debugging and observability tool that intercepts all API traffic between Claude Code CLI and Anthropic's servers, generating self-contained HTML reports of the interactions.

### Key Details

| Attribute | Value |
|-----------|-------|
| **Repository** | [github.com/badlogic/lemmy/tree/main/apps/claude-trace](https://github.com/badlogic/lemmy/tree/main/apps/claude-trace) |
| **Installation** | `npm install -g @mariozechner/claude-trace` |
| **License** | MIT |
| **Language** | TypeScript/Node.js |
| **Part Of** | Lemmy monorepo |
| **Author** | Mario Zechner (@badlogic) |

### What It Reveals

| Data Type | Description |
|-----------|-------------|
| **System Prompts** | The full system prompt sent to Claude |
| **Tool Definitions** | All tools available to Claude |
| **Tool Outputs** | Results from tool invocations |
| **Token Usage** | Input/output tokens, cache hits |
| **Thinking Blocks** | Claude's internal reasoning (when enabled) |
| **Raw HTTP Traffic** | Complete request/response payloads |

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Terminal                            │
│  $ claude-trace -- claude "your prompt"                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    claude-trace                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Interceptor Module                      │   │
│  │  • Injected via Node.js --require flag              │   │
│  │  • Patches HTTP/HTTPS modules                       │   │
│  │  • Captures all Anthropic API traffic               │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Report Generator                        │   │
│  │  • Parses captured traffic                          │   │
│  │  • Generates self-contained HTML                    │   │
│  │  • Optional: AI-powered indexing                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code CLI                           │
│  (Runs normally, unaware of interception)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Anthropic API                              │
└─────────────────────────────────────────────────────────────┘
```

### Technical Implementation

1. **Interception Mechanism**:
   ```bash
   node --require ./interceptor.js $(which claude) "prompt"
   ```

2. **HTTP Patching**: Monkey-patches Node's `http` and `https` modules

3. **Traffic Capture**: Records all requests/responses to Anthropic endpoints

4. **Report Generation**: Creates single-file HTML with embedded CSS/JS

### Usage Examples

```bash
# Basic tracing
claude-trace -- claude "explain this code"

# With AI-powered indexing
claude-trace --index -- claude "refactor this function"

# Specify output directory
claude-trace --output ./traces -- claude "write tests"
```

---

## Current State Analysis

### Open Issues (Critical)

| Issue # | Severity | Description |
|---------|----------|-------------|
| #48 | **Critical** | Native binary compatibility broken |
| #46 | **Critical** | Hangs indefinitely with `--index` flag |
| #37 | **High** | macOS failures |
| #38 | **High** | Crash on certain payloads |
| #33 | **High** | Memory issues with large traces |
| #32 | **Medium** | UI rendering bugs |

**Total Open Issues**: 14

### Maintenance Status

| Indicator | Value | Assessment |
|-----------|-------|------------|
| Last Commit | August 2025 | Recent |
| Open Issues | 14 | High |
| Issue Response | Variable | Inconsistent |
| Release Cadence | Irregular | Concerning |
| Standalone Project | No (monorepo) | Risk |

### Dependencies

```json
{
  "dependencies": {
    "commander": "^11.x",
    "marked": "^9.x",
    "highlight.js": "^11.x"
  },
  "peerDependencies": {
    "node": ">=18.0.0"
  }
}
```

**Risk Assessment**: Low dependency count, but relies on Node.js module loading internals that could break with Node updates.

---

## Analysis: Fit for Flowspec

### Potential Value

| Benefit | Description |
|---------|-------------|
| **Workflow Debugging** | See what /flow:* commands send to Claude |
| **Agent Observability** | Understand multi-agent coordination |
| **Learning Tool** | See how Claude Code works internally |
| **Issue Diagnosis** | Debug unexpected behavior |

### Concerns

| Issue | Impact |
|-------|--------|
| **Stability** | 14 open bugs make it unreliable |
| **Scope** | Debugging tool, not workflow tool |
| **Maintenance** | Part of monorepo, unclear priority |
| **Fragility** | Interception hacks could break |
| **Narrow Use** | Only Claude Code, not other AI agents |

### Alignment Assessment

| Flowspec Goal | claude-trace Contribution |
|------------------|---------------------------|
| Write better specs | None |
| Generate better tasks | None |
| Track progress | None |
| Implement faster | Marginal (debugging) |
| Validate quality | None |

**Conclusion**: claude-trace provides debugging capabilities, not workflow enhancement. It helps understand *how* Claude Code works, not *how to use it better*.

---

## Decision: NOT RECOMMENDED (Not Now)

### Primary Reasons

#### 1. Critical Stability Issues

The tool has 14 open issues including:

```
#48 - Native binary compatibility broken
      └── Core functionality broken on some systems

#46 - Hangs indefinitely with --index flag
      └── Key feature unusable

#37 - macOS failures
      └── Significant platform excluded

#38, #33, #32 - Various crashes
      └── Unreliable for production use
```

**Impact**: Cannot recommend a tool that crashes, hangs, or fails on major platforms.

#### 2. Misalignment with SDD Mission

| Flowspec Mission | claude-trace Reality |
|--------------------|--------------------|
| Improve developer productivity | Provides debugging info |
| Streamline SDD workflows | No workflow integration |
| Reduce friction | Adds complexity |
| Enable best practices | Debugging tool only |

#### 3. Limited Applicability

```
Flowspec supports:
├── Claude Code (claude-trace works)
├── Other AI agents (claude-trace doesn't work)
├── CLI workflows (claude-trace adds friction)
└── Team collaboration (claude-trace is local only)
```

#### 4. Maintenance Risk

| Risk | Description |
|------|-------------|
| **Monorepo dependency** | Not standalone, updates tied to larger project |
| **Interception fragility** | Node.js internals could change |
| **Claude Code updates** | Could break compatibility |
| **Support burden** | Flowspec would need to troubleshoot |

#### 5. Existing Alternatives

| Need | Existing Solution |
|------|-------------------|
| See Claude's responses | Claude Code terminal output |
| Track implementation | Backlog.md task notes |
| Debug workflows | Claude Code verbose mode |
| Quality validation | /flow:validate |

---

## Verdict: Not Now

### Reconsideration Criteria

claude-trace could be reconsidered if:

| Criterion | Target |
|-----------|--------|
| Open issues | < 5 critical bugs |
| Stability | No crashes/hangs on major platforms |
| Maintenance | Monthly releases, responsive issues |
| Standalone | Separate from monorepo |
| Value prop | Clear SDD workflow integration |

### Timeline

| Milestone | Action |
|-----------|--------|
| Q1 2026 | Re-evaluate if criteria met |
| If stable | Consider "Recommended Tool" status (not primary) |
| If value shown | Develop integration guide |

---

## Alternative Approaches

### 1. Document Existing Observability

Create `docs/guides/debugging-workflows.md`:

```markdown
## Debugging /flow:* Workflows

### Enable Verbose Output
Claude Code provides verbose output by default. To see more detail:
- Watch the terminal for tool calls and responses
- Check the summary at the end of each command

### Use Backlog.md for Tracking
- Add implementation notes to tasks
- Track decisions and reasoning
- Review completed tasks for context

### Leverage /flow:validate
- Run validation to check implementation
- Review generated reports
- Use findings to improve workflows
```

### 2. Create Troubleshooting Guide

Add `docs/reference/troubleshooting.md`:

```markdown
## Common Issues

### Slash Command Not Working
1. Check CLAUDE.md is in project root
2. Verify command syntax: /flow:command
3. Review Claude Code version compatibility

### Unexpected Agent Behavior
1. Check task description clarity
2. Review acceptance criteria
3. Examine implementation plan

### Performance Issues
1. Break large tasks into smaller ones
2. Use specific, focused prompts
3. Leverage task dependencies
```

### 3. Add Workflow Observability Task Template

If users need deep debugging, create template for:
- Capturing workflow decisions
- Documenting agent interactions
- Recording implementation choices

---

## What "Primary Support" Would Have Meant

If approved, primary support would include:

| Component | Description |
|-----------|-------------|
| **Documentation** | `docs/guides/claude-trace-integration.md` |
| **CLAUDE.md Section** | Installation and usage instructions |
| **Troubleshooting** | Common issues and solutions |
| **Quick Start** | Recommended installation |
| **Support** | Answering user questions |

### Maintenance Burden

| Activity | Frequency | Effort |
|----------|-----------|--------|
| Documentation updates | Per claude-trace release | Medium |
| Compatibility testing | Per Claude Code release | High |
| User support | Ongoing | Medium |
| Issue triage | Ongoing | Low |

---

## References

### Primary Sources

- [GitHub Repository](https://github.com/badlogic/lemmy/tree/main/apps/claude-trace)
- [npm Package](https://www.npmjs.com/package/@mariozechner/claude-trace)
- [Open Issues](https://github.com/badlogic/lemmy/issues?q=is%3Aopen+is%3Aissue+label%3Aclaude-trace)

### Related Tools

- [Claude Code](https://github.com/anthropics/claude-code) - Anthropic's official CLI
- [Lemmy](https://github.com/badlogic/lemmy) - Parent monorepo

### Alternative Observability Tools

- Claude Code's built-in output
- Backlog.md task tracking
- Git commit history for implementation trail

---

## Appendix: Example Output (For Reference)

### Captured System Prompt (Truncated)

```
You are Claude Code, Anthropic's official CLI...
You have access to the following tools:
- Read: Read files from filesystem
- Write: Write files to filesystem
- Bash: Execute shell commands
- Edit: Edit existing files
...
```

### Captured Tool Call

```json
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "Read",
  "input": {
    "file_path": "/home/user/project/src/main.ts"
  }
}
```

### Generated Report Structure

```
trace-2025-11-28/
├── index.html          # Self-contained report
├── conversations/
│   ├── conv-001.json   # Raw conversation data
│   └── conv-002.json
└── summary.json        # Token usage, timing
```

---

**Document Author**: Claude (via Flowspec evaluation workflow)
**Review Status**: Complete
**Next Review**: Q1 2026 (if stability improves)
