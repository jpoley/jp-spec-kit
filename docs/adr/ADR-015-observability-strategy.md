# ADR-015: Observability Strategy (claude-trace Integration)

**Status:** Proposed
**Date:** 2025-12-04
**Author:** Platform Engineer
**Context:** task-136 - claude-trace observability tool integration
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Debugging AI agent workflows (e.g., `/jpspec:implement`, `/jpspec:validate`) is challenging because:
- **Black Box Execution** - AI decisions are opaque (why did it skip a file? why did it choose that pattern?)
- **Token Usage Mystery** - No visibility into token consumption (which agents are expensive?)
- **Performance Bottlenecks** - Slow workflows have no profiling data (which step takes 5 minutes?)
- **Failure Attribution** - When workflows fail, root cause is unclear (tool error? prompt issue? API timeout?)

**The Core Tension:** AI agents are powerful but unpredictable. Developers need observability to understand, debug, and optimize workflows.

### Business Value

**Primary Value Streams:**

1. **Debugging Efficiency** - Reduce troubleshooting time from hours to minutes
2. **Cost Optimization** - Identify and eliminate token waste (expensive prompts)
3. **Performance Optimization** - Profile workflows to find and fix bottlenecks
4. **Trust** - Transparency builds confidence in AI-assisted development

**Success Metrics:**

- Reduce workflow debugging time by 50% (from 2 hours to 1 hour)
- Identify top 3 token-heavy agents within first week
- Root cause analysis success rate >80% (can find cause of failure)
- Developer satisfaction: "Debugging workflows is manageable" (NPS >30)

---

## Decision

### Chosen Architecture: claude-trace as Primary Observability Tool

Adopt **claude-trace** (https://github.com/cyanheads/claude-trace) as the recommended observability tool for JP Spec Kit, providing:

1. **Trace Collection** - Capture all Claude Code operations (file reads, writes, tool calls, API requests)
2. **Visualization** - Web UI for exploring traces (timeline, call graphs, token usage)
3. **Analysis** - Search, filter, and analyze traces (find slow operations, expensive prompts)
4. **Privacy-First** - Local-only traces (no external data transmission)
5. **Zero-Code Integration** - Works via `.claude/settings.json` configuration (no code changes)

**Key Pattern:** **Distributed Tracing (Observability Pattern)** + **Structured Logging**

```
┌─────────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY ARCHITECTURE                     │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ Claude Code (JP Spec Kit)                         │         │
│  │ - /jpspec:implement (agents running)              │         │
│  │ - File operations (Read, Write, Edit)             │         │
│  │ - Tool calls (Bash, Glob, Grep)                   │         │
│  │ - API requests (Anthropic Claude API)             │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│                   │ Emit traces                                  │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ claude-trace Agent                                │         │
│  │ - Intercept operations                            │         │
│  │ - Capture metadata (timestamp, duration, tokens)  │         │
│  │ - Write to local SQLite DB                        │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│                   │ Store traces                                 │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ Trace Database (~/.claude-trace/traces.db)        │         │
│  │ - Indexed by session, timestamp, operation        │         │
│  │ - Retention: 30 days (configurable)               │         │
│  └────────────────┬───────────────────────────────────┘         │
│                   │                                              │
│                   │ Query traces                                 │
│                   │                                              │
│  ┌────────────────▼───────────────────────────────────┐         │
│  │ claude-trace Web UI (http://localhost:3000)       │         │
│  │ - Timeline view (operations over time)            │         │
│  │ - Call graph (operation dependencies)             │         │
│  │ - Token usage (by agent, by operation)            │         │
│  │ - Search/filter (find slow operations)            │         │
│  └────────────────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Engine Room View: Technical Architecture

### Integration Configuration

**File:** `.claude/settings.json`

```json
{
  "observability": {
    "enabled": true,
    "trace_tool": "claude-trace",
    "trace_level": "info",
    "capture": {
      "file_operations": true,
      "tool_calls": true,
      "api_requests": true,
      "agent_decisions": true
    },
    "retention_days": 30,
    "privacy": {
      "redact_secrets": true,
      "redact_patterns": [
        "AKIA[0-9A-Z]{16}",
        "ghp_[a-zA-Z0-9]{36}",
        "password\\s*=\\s*['\"][^'\"]+['\"]"
      ],
      "exclude_paths": [
        "**/.env",
        "**/secrets/**",
        "**/*.pem"
      ]
    }
  }
}
```

### Trace Data Model

**Trace Structure:**

```typescript
interface Trace {
  trace_id: string;           // Unique trace ID (UUID)
  session_id: string;         // Claude Code session ID
  parent_id: string | null;   // Parent trace ID (for nested operations)
  timestamp: string;          // ISO 8601 timestamp
  duration_ms: number;        // Operation duration
  operation: string;          // Operation type (Read, Write, Bash, etc.)
  status: "success" | "error" | "timeout";

  // Operation details
  details: {
    tool: string;             // Tool name (Read, Write, Bash, etc.)
    path?: string;            // File path (for file operations)
    command?: string;         // Command (for Bash)
    pattern?: string;         // Pattern (for Grep, Glob)
    result?: string;          // Operation result (truncated)
  };

  // Token usage
  tokens: {
    input: number;            // Input tokens
    output: number;           // Output tokens
    total: number;            // Total tokens
    cost_usd: number;         // Estimated cost
  };

  // Metadata
  metadata: {
    agent?: string;           // Agent name (e.g., "backend-engineer")
    task_id?: string;         // Backlog task ID (e.g., "task-085")
    workflow_phase?: string;  // Workflow phase (e.g., "/jpspec:implement")
    tags: string[];           // User-defined tags
  };
}
```

**Example Trace:**

```json
{
  "trace_id": "01928374-abcd-4567-8901-234567890abc",
  "session_id": "session-2025-12-04-10-00-00",
  "parent_id": null,
  "timestamp": "2025-12-04T10:15:30Z",
  "duration_ms": 1250,
  "operation": "Read",
  "status": "success",
  "details": {
    "tool": "Read",
    "path": "/home/user/project/src/main.py",
    "result": "# Python code (truncated)..."
  },
  "tokens": {
    "input": 150,
    "output": 2000,
    "total": 2150,
    "cost_usd": 0.01075
  },
  "metadata": {
    "agent": "backend-engineer",
    "task_id": "task-085",
    "workflow_phase": "/jpspec:implement",
    "tags": ["backend", "implementation"]
  }
}
```

### Usage Patterns

#### Pattern 1: Debugging Failed Workflow

**Scenario:** `/jpspec:implement` failed after 10 minutes, no clear error message.

**Steps:**
1. Open claude-trace UI: `claude-trace serve`
2. Navigate to http://localhost:3000
3. Filter by session (last session) and status (error)
4. Review timeline to find failure point
5. Inspect error trace details (tool output, API response)
6. Root cause: CodeQL timeout (5 minutes exceeded)

**Benefit:** Reduced debugging time from 1 hour (trial and error) to 5 minutes (direct trace inspection).

#### Pattern 2: Identifying Token Waste

**Scenario:** Claude Code usage costs $50/month, want to reduce.

**Steps:**
1. Open claude-trace UI
2. Navigate to "Token Usage" dashboard
3. Sort by agent/operation
4. Identify top consumers:
   - `backend-engineer` agent: 80% of tokens
   - `Read` operations on large files (5000+ lines)
5. Optimization:
   - Use `Grep` instead of `Read` for searches
   - Implement file size limits (skip files >2000 lines)

**Benefit:** Reduced token usage by 40%, saving $20/month.

#### Pattern 3: Performance Profiling

**Scenario:** `/jpspec:implement` takes 15 minutes, want to optimize.

**Steps:**
1. Open claude-trace UI
2. View timeline for slow session
3. Identify bottlenecks:
   - `Bash` (pytest): 8 minutes (test suite too slow)
   - `Read` operations: 3 minutes (reading 50+ files)
   - `Edit` operations: 2 minutes (serialized edits)
4. Optimization:
   - Parallelize `Read` operations
   - Cache test results
   - Use `Edit` batching

**Benefit:** Reduced workflow time from 15 minutes to 7 minutes (53% improvement).

---

## Installation and Setup

### Prerequisites

- Node.js 16+ (for claude-trace)
- SQLite 3+ (for trace storage)
- Claude Code (JP Spec Kit)

### Installation Steps

```bash
# 1. Install claude-trace
npm install -g claude-trace

# 2. Initialize trace database
claude-trace init

# 3. Configure Claude Code (add to .claude/settings.json)
# See "Integration Configuration" section above

# 4. Start trace collection (automatic on next Claude Code session)
# Traces are written to ~/.claude-trace/traces.db

# 5. View traces
claude-trace serve
# Open http://localhost:3000 in browser
```

### Verification

```bash
# Check trace collection
claude-trace stats

# Output:
# Total traces: 1,234
# Sessions: 15
# Token usage: 150,000 tokens
# Storage: 5.2 MB

# Query recent traces
claude-trace query --since "1 hour ago" --status error

# Output:
# 3 errors found:
# - Bash timeout (task-085)
# - File not found (task-136)
# - API rate limit (task-249)
```

---

## Privacy and Security

### Privacy Guarantees

1. **Local-Only Storage** - Traces stored in `~/.claude-trace/traces.db` (SQLite)
2. **No External Transmission** - Zero network requests (no telemetry, no analytics)
3. **Redaction** - Secrets automatically redacted (API keys, passwords)
4. **Retention Policy** - Auto-delete traces after 30 days (configurable)

### Secret Redaction

**Redaction Patterns:**

```json
{
  "privacy": {
    "redact_secrets": true,
    "redact_patterns": [
      "AKIA[0-9A-Z]{16}",
      "ghp_[a-zA-Z0-9]{36}",
      "glpat-[a-zA-Z0-9_-]{20,}",
      "password\\s*=\\s*['\"][^'\"]+['\"]",
      "api[_-]?key\\s*=\\s*['\"][^'\"]+['\"]"
    ]
  }
}
```

**Before Redaction:**
```
Bash command: export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```

**After Redaction:**
```
Bash command: export AWS_ACCESS_KEY_ID=[REDACTED:AWS_KEY]
```

### File Exclusion

**Excluded Paths (Never Traced):**

- `.env`, `.env.*` (environment variables)
- `secrets/`, `credentials/` (secret directories)
- `*.pem`, `*.key`, `id_rsa*` (private keys)

### Data Retention

**Default Policy:** 30 days

**Custom Retention:**

```bash
# Set retention to 7 days
claude-trace config set retention_days 7

# Purge old traces immediately
claude-trace purge --older-than "30 days"

# Purge all traces (clean slate)
claude-trace purge --all
```

---

## Known Issues and Workarounds

### Issue #46: Indexing Hangs on Large Traces

**Symptom:** `claude-trace serve` hangs when loading sessions with 10,000+ traces.

**Cause:** SQLite full-text search indexing without pagination.

**Workaround:**
```bash
# Disable full-text search
claude-trace config set fts_enabled false

# Or: Purge old traces before serving
claude-trace purge --older-than "7 days"
claude-trace serve
```

### Issue #48: Native Binary Compatibility (M1/M2 Macs)

**Symptom:** `npm install -g claude-trace` fails on Apple Silicon Macs.

**Cause:** Native dependencies (better-sqlite3) not pre-compiled for arm64.

**Workaround:**
```bash
# Use Rosetta 2 (x86_64 emulation)
arch -x86_64 npm install -g claude-trace

# Or: Build from source
git clone https://github.com/cyanheads/claude-trace
cd claude-trace
npm install
npm run build
npm link
```

---

## Integration with JP Spec Kit Workflows

### /jpspec:implement Integration

**Auto-Tagging:**

```json
{
  "metadata": {
    "workflow_phase": "/jpspec:implement",
    "task_id": "task-085",
    "agents": ["backend-engineer", "code-reviewer"]
  }
}
```

**Query Examples:**

```bash
# Find all traces for task-085
claude-trace query --task task-085

# Find slow operations in /jpspec:implement
claude-trace query --workflow "/jpspec:implement" --duration ">5000"

# Find errors by backend-engineer agent
claude-trace query --agent "backend-engineer" --status error
```

### Backlog Integration

**Trace Workflow Context:**

When working on backlog tasks, claude-trace automatically captures:
- Task ID (e.g., `task-085`)
- Acceptance criteria progress (AC #1, AC #2)
- Implementation plan step (Step 1/5)

**Query by Task State:**

```bash
# Find traces for tasks "In Progress"
claude-trace query --task-status "In Progress"

# Find traces for High priority tasks
claude-trace query --task-priority High
```

### Troubleshooting Workflow

**Recommended Workflow:**

1. **Capture traces** during normal Claude Code sessions (automatic)
2. **Review traces** when workflows fail or perform poorly
3. **Identify patterns** (which agents are slow? which operations fail?)
4. **Optimize** based on findings (refactor prompts, cache results, etc.)
5. **Validate** improvements with before/after trace comparison

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 10/10

**Strengths:**
- Clear trace data model (what is captured, when, why)
- Explicit privacy guarantees (local-only, redaction)
- Clear integration points (.claude/settings.json)

### 2. Consistency - 9/10

**Strengths:**
- All operations traced uniformly (file ops, tool calls, API requests)
- Consistent redaction across all trace types
- Consistent query interface (filter by agent, task, status)

**Improvement:**
- Standardize metadata schema across agent types

### 3. Composability - 10/10

**Strengths:**
- Works with any Claude Code workflow (zero code changes)
- Integrates with existing tools (backlog, /jpspec commands)
- Query API enables custom analysis scripts

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Zero-code integration (configure and run)
- Web UI for easy trace exploration
- Clear documentation and examples

**Needs Work:**
- First-time setup could be smoother (npm install issues on M1 Macs)
- Web UI performance with large trace databases

### 5. Correctness (Validation) - 8/10

**Strengths:**
- Captures all operations (comprehensive)
- Redaction prevents secret leaks
- Local-only storage (privacy guaranteed)

**Risks:**
- Trace overhead may slow operations (mitigated by async writes)
- Database corruption (mitigated by SQLite reliability)

### 6. Completeness - 8/10

**Covers:**
- Trace collection, storage, visualization
- Privacy (redaction, retention, local-only)
- Integration with workflows and backlog

**Missing (Future):**
- Distributed tracing (multi-machine workflows)
- Real-time streaming (live trace updates)
- Export to OpenTelemetry format

### 7. Changeability - 10/10

**Strengths:**
- Add new trace fields: extend schema, backward compatible
- Add new redaction patterns: edit config, no code changes
- Change retention policy: update config, apply immediately

---

## Alternatives Considered and Rejected

### Option A: No Observability (Status Quo)

**Approach:** Rely on Claude Code headless mode and manual log inspection.

**Pros:**
- Zero setup (works today)
- No external dependencies

**Cons:**
- Debugging is trial-and-error (slow, frustrating)
- No token usage visibility (cost optimization impossible)
- No performance profiling (bottlenecks unknown)

**Rejected:** Insufficient for production workflows

---

### Option B: OpenTelemetry Integration

**Approach:** Instrument Claude Code with OpenTelemetry, send traces to Jaeger/Zipkin.

**Pros:**
- Industry-standard tracing (interoperable)
- Rich visualization tools (Jaeger UI)
- Distributed tracing support

**Cons:**
- Requires external infrastructure (Jaeger backend)
- Complex setup (OTLP collectors, exporters)
- Privacy concerns (traces leave local machine)

**Rejected:** Over-engineered for CLI tool

---

### Option C: claude-trace Integration (RECOMMENDED)

**Approach:** Use claude-trace as recommended observability tool.

**Pros:**
- Purpose-built for Claude Code
- Local-only (privacy guaranteed)
- Zero-code integration
- Active development (community support)

**Cons:**
- Requires Node.js (additional dependency)
- Not industry-standard (no interoperability)

**Accepted:** Best balance of usability and privacy

---

## Implementation Guidance

### Phase 1: Documentation (Week 1)

**Scope:** Create user documentation and integration guide

**Deliverables:**
- `docs/guides/claude-trace-integration.md`
- Installation instructions
- Usage examples
- Troubleshooting guide

**Tasks:**
- Document installation steps
- Create example .claude/settings.json
- Document known issues (#46, #48)
- Write troubleshooting workflow guide

### Phase 2: Integration Testing (Week 2)

**Scope:** Validate claude-trace with real workflows

**Deliverables:**
- Test with /jpspec:implement workflow
- Test with backlog task execution
- Verify privacy (redaction, retention)

**Tasks:**
- Run /jpspec:implement with tracing enabled
- Inspect traces in claude-trace UI
- Validate redaction (no secrets in traces)
- Test query API (filter by task, agent, status)

### Phase 3: Optimization (Week 3)

**Scope:** Use traces to optimize workflows

**Deliverables:**
- Performance optimization recommendations
- Token usage optimization recommendations
- Updated workflow documentation

**Tasks:**
- Identify top 3 performance bottlenecks
- Identify top 3 token-heavy operations
- Propose optimizations
- Validate improvements with traces

---

## Success Criteria

**Objective Measures:**

1. **Debugging Time Reduction** - 50% reduction (2 hours → 1 hour)
2. **Token Visibility** - 100% of tokens attributed to agents/operations
3. **Root Cause Analysis** - 80% of failures traceable to root cause
4. **Privacy Compliance** - Zero secrets leaked in traces

**Subjective Measures:**

1. **Developer Feedback** - "Debugging is manageable" (NPS >30)
2. **Adoption Rate** - 80% of users enable tracing within first month

---

## Decision

**APPROVED for integration as recommended observability tool**

**Next Steps:**

1. Create documentation task (Phase 1)
2. Test with real workflows (Phase 2)
3. Optimize based on findings (Phase 3)

**Review Date:** 2025-12-18 (after Phase 1 complete)

---

## References

### Observability Principles Applied

1. **Distributed Tracing** - Capture all operations with correlation IDs
2. **Structured Logging** - Consistent schema for all traces
3. **Privacy by Design** - Local-only storage, automatic redaction
4. **Retention Policies** - Auto-purge old data

### Related Documents

- **Task:** task-136 - Add Primary Support for claude-trace Observability Tool
- **Related Docs:** docs/reference/outer-loop.md (observability section)

### External References

- [claude-trace Repository](https://github.com/cyanheads/claude-trace)
- [OpenTelemetry](https://opentelemetry.io/)
- [Distributed Tracing Patterns](https://microservices.io/patterns/observability/distributed-tracing.html)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
