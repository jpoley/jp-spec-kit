# Performance Rules

Rules for model selection, context management, and efficiency.

## Model Selection Guidance

Choose models based on task complexity:

| Task Type | Recommended Model | Rationale |
|-----------|------------------|-----------|
| Quick lookups, simple edits | Haiku | Fast, cost-effective |
| Standard implementation | Sonnet | Balanced performance |
| Complex architecture, research | Opus | Deep reasoning |
| Security analysis | Opus | Thorough analysis |

### Haiku Tasks
- File lookups and searches
- Simple formatting changes
- Boilerplate generation
- Status checks

### Sonnet Tasks
- Standard feature implementation
- Bug fixes with clear scope
- Test writing
- Documentation updates

### Opus Tasks
- System architecture decisions
- Complex refactoring
- Security audits
- Ambiguous requirements analysis

## Context Management

### Keep Context Lean
- Don't load unnecessary files
- Use focused searches (Grep, Glob)
- Clear completed work from context

### Effective Tool Usage
- Use Glob for file pattern matching (not `find`)
- Use Grep for content search (not `grep` or `rg`)
- Use Read for viewing files (not `cat`)
- Use Edit for modifications (not `sed`)

### Parallel Operations
When searches are independent, run them in parallel rather than sequentially.

## MCP Optimization

### Connection Management
- Reuse MCP connections within sessions
- Close connections when done
- Handle connection failures gracefully

### Request Batching
- Batch related MCP requests when possible
- Avoid redundant queries
- Cache results within session scope

## Task Memory

Update task memory at these points:
- Session start (read and update "Current State")
- After decisions (record in "Key Decisions")
- Before session end (update what's done/next)
- After blockers (document in "Open Questions")

Keep "Critical Context" under 500 words - link to docs for details.

## Cost Awareness

- Prefer cheaper models for routine tasks
- Use expensive models only when complexity requires
- Monitor token usage on large files
- Truncate large outputs where appropriate
