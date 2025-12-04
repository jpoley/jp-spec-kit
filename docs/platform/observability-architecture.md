# Observability Architecture - claude-trace Integration

**Date:** 2025-12-04
**Related Tasks:** task-136
**Related ADRs:** ADR-015-observability-strategy

---

## Overview

JP Spec Kit integrates **claude-trace** as the primary observability tool for debugging AI agent workflows, optimizing token usage, and profiling performance.

### Key Capabilities

1. **Trace Collection** - Capture all operations (file ops, tool calls, API requests)
2. **Visualization** - Web UI for exploring traces (timeline, call graphs)
3. **Analysis** - Search, filter, analyze (find slow operations, expensive prompts)
4. **Privacy-First** - Local-only storage (no external transmission)

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│ OBSERVABILITY ARCHITECTURE                           │
│                                                      │
│  ┌────────────────────────────────────┐             │
│  │ Claude Code (JP Spec Kit)         │             │
│  │ - /jpspec:implement                │             │
│  │ - File ops (Read, Write, Edit)     │             │
│  │ - Tool calls (Bash, Grep, Glob)    │             │
│  │ - API requests (Claude API)        │             │
│  └────────────┬───────────────────────┘             │
│               │ Emit traces                          │
│  ┌────────────▼───────────────────────┐             │
│  │ claude-trace Agent                 │             │
│  │ - Intercept operations             │             │
│  │ - Capture metadata (duration, tokens)│           │
│  │ - Write to SQLite DB               │             │
│  └────────────┬───────────────────────┘             │
│               │ Store traces                         │
│  ┌────────────▼───────────────────────┐             │
│  │ ~/.claude-trace/traces.db          │             │
│  │ - Indexed by session, timestamp    │             │
│  │ - Retention: 30 days               │             │
│  └────────────┬───────────────────────┘             │
│               │ Query traces                         │
│  ┌────────────▼───────────────────────┐             │
│  │ claude-trace Web UI                │             │
│  │ - Timeline view                    │             │
│  │ - Token usage dashboard            │             │
│  │ - Search/filter                    │             │
│  └────────────────────────────────────┘             │
└──────────────────────────────────────────────────────┘
```

---

## Trace Data Model

```typescript
interface Trace {
  trace_id: string;           // UUID
  session_id: string;         // Claude Code session
  parent_id: string | null;   // Nested operations
  timestamp: string;          // ISO 8601
  duration_ms: number;        // Operation duration
  operation: string;          // Read, Write, Bash, etc.
  status: "success" | "error" | "timeout";

  details: {
    tool: string;
    path?: string;
    command?: string;
    result?: string;          // Truncated
  };

  tokens: {
    input: number;
    output: number;
    total: number;
    cost_usd: number;
  };

  metadata: {
    agent?: string;           // e.g., "backend-engineer"
    task_id?: string;         // e.g., "task-085"
    workflow_phase?: string;  // e.g., "/jpspec:implement"
  };
}
```

---

## Usage Patterns

### Pattern 1: Debug Failed Workflow

**Scenario:** `/jpspec:implement` failed after 10 minutes.

**Steps:**
1. Open claude-trace UI: `claude-trace serve`
2. Filter by status: error
3. Review timeline to find failure point
4. Inspect error trace details

**Time Saved:** 55 min (1 hour → 5 min)

### Pattern 2: Optimize Token Usage

**Scenario:** High Claude API costs ($50/month).

**Steps:**
1. Open token usage dashboard
2. Sort by agent/operation
3. Identify top consumers (e.g., `Read` on large files)
4. Optimize (use `Grep` instead of `Read`)

**Cost Saved:** $20/month (40% reduction)

### Pattern 3: Profile Performance

**Scenario:** Workflow takes 15 minutes.

**Steps:**
1. View timeline
2. Identify bottlenecks (e.g., `pytest` takes 8 min)
3. Optimize (cache test results, parallelize)

**Time Saved:** 8 min (15 min → 7 min, 53% faster)

---

## Privacy and Security

### Privacy Guarantees

1. **Local-Only** - Traces stored in `~/.claude-trace/traces.db` (no network)
2. **Redaction** - Secrets automatically redacted (API keys, passwords)
3. **Exclusion** - .env, secrets/ never traced
4. **Retention** - Auto-purge after 30 days

### Secret Redaction

**Patterns Redacted:**
- AWS keys: `AKIA[0-9A-Z]{16}`
- GitHub tokens: `ghp_[a-zA-Z0-9]{36}`
- Passwords: `password = "..."`

**Before:** `export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE`
**After:** `export AWS_ACCESS_KEY_ID=[REDACTED:AWS_KEY]`

---

## Integration Configuration

**File:** `.claude/settings.json`

```json
{
  "observability": {
    "enabled": true,
    "trace_tool": "claude-trace",
    "capture": {
      "file_operations": true,
      "tool_calls": true,
      "api_requests": true
    },
    "retention_days": 30,
    "privacy": {
      "redact_secrets": true,
      "exclude_paths": ["**/.env", "**/secrets/**"]
    }
  }
}
```

---

## Known Issues

### Issue #46: Indexing Hangs

**Symptom:** `claude-trace serve` hangs with 10,000+ traces.

**Workaround:**
```bash
# Disable full-text search
claude-trace config set fts_enabled false

# Or purge old traces
claude-trace purge --older-than "7 days"
```

### Issue #48: M1/M2 Mac Compatibility

**Symptom:** `npm install -g claude-trace` fails on Apple Silicon.

**Workaround:**
```bash
# Use Rosetta
arch -x86_64 npm install -g claude-trace

# Or build from source
git clone https://github.com/cyanheads/claude-trace
cd claude-trace && npm install && npm run build && npm link
```

---

## Success Metrics

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Debugging Time | 2 hours | 1 hour | 50% reduction |
| Token Visibility | 0% | 100% | Full attribution |
| Root Cause Analysis | 50% | 80% | Traceable |
| Privacy Compliance | N/A | 100% | Zero leaks |

---

## Implementation Phases

### Phase 1: Documentation (Week 1)
- Create docs/guides/claude-trace-integration.md
- Installation instructions
- Usage examples
- Troubleshooting

### Phase 2: Testing (Week 2)
- Test with /jpspec:implement
- Verify privacy (redaction)
- Validate query API

### Phase 3: Optimization (Week 3)
- Identify bottlenecks
- Optimize token usage
- Update workflow docs
