# Tool Search Tool Evaluation

**Evaluation Date**: 2025-11-28
**Status**: NOT RECOMMENDED
**Verdict**: Never (Categorical Mismatch)

---

## Executive Summary

This document evaluates whether Flowspec should add primary support for Anthropic's **tool-search-tool** feature. After extensive research, the recommendation is **NOT to add support** due to a fundamental scope mismatch: tool-search-tool is an API implementation detail for developers building Claude-powered applications, not a user-facing tool for Spec-Driven Development practitioners.

---

## What is tool-search-tool?

### Overview

**tool-search-tool** is an Anthropic Claude API feature (currently in beta) that enables Claude to dynamically discover and load tools on-demand from large catalogs, rather than loading all tool definitions into the context window upfront.

### Key Details

| Attribute | Value |
|-----------|-------|
| **Type** | API Feature (not standalone tool) |
| **Status** | Beta |
| **Provider** | Anthropic |
| **Announcement** | Late 2024 |
| **Required Header** | `advanced-tool-use-2025-11-20` |
| **Compatible Models** | Claude Opus 4.5, Sonnet 4.5 |

### Variants

Two search variants are available:

1. **`tool_search_tool_regex_20251119`** - Regex pattern search for tool names/descriptions
2. **`tool_search_tool_bm25_20251119`** - Natural language search using BM25 algorithm

### Performance Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Token Usage | 100% | 15% | 85% reduction |
| Accuracy (Opus 4) | 49% | 74% | +25 points |
| Accuracy (Opus 4.5) | 79.5% | 88.1% | +8.6 points |

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  (Your code that calls Claude API)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Claude API                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Tool Search Tool                        │   │
│  │  • Receives search query from Claude                 │   │
│  │  • Searches tool catalog (regex or BM25)            │   │
│  │  • Returns 3-5 relevant tool references             │   │
│  │  • Auto-expands to full definitions                 │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Tool Definitions Catalog                     │
│  (10+ tools with defer_loading: true)                       │
└─────────────────────────────────────────────────────────────┘
```

### Integration Flow

1. **Define tools with deferred loading**:
   ```json
   {
     "name": "get_weather",
     "description": "Get current weather for a location",
     "defer_loading": true,
     "input_schema": { ... }
   }
   ```

2. **Claude uses tool-search-tool** to find relevant tools based on user query

3. **API returns tool references** (3-5 most relevant matches)

4. **References auto-expand** to full tool definitions

5. **Claude selects and invokes** the discovered tools

### Use Case

Designed for applications with large tool catalogs (10+ tools) where:
- Loading all tools exceeds context limits
- Tool selection accuracy degrades with many options
- Token costs need optimization

---

## Analysis: Fit for Flowspec

### What Flowspec IS

| Category | Description |
|----------|-------------|
| **Purpose** | Spec-Driven Development toolkit |
| **Primary Users** | Developers practicing SDD |
| **Components** | CLI, templates, slash commands |
| **Integration** | Backlog.md, Claude Code |
| **Workflows** | /flow:specify, /flow:plan, /flow:implement, etc. |

### What tool-search-tool IS

| Category | Description |
|----------|-------------|
| **Purpose** | API optimization for large tool catalogs |
| **Primary Users** | Developers building Claude-powered applications |
| **Components** | API feature with beta headers |
| **Integration** | Claude API calls |
| **Workflows** | Application development, not end-user workflows |

### Comparison Matrix

| Aspect | Flowspec | tool-search-tool |
|--------|-------------|------------------|
| **Audience** | SDD practitioners | API developers |
| **Abstraction Level** | User workflows | API implementation |
| **Interaction Model** | CLI/slash commands | HTTP API calls |
| **Value Proposition** | Productivity | Token optimization |
| **Integration Point** | Claude Code (as user) | Claude API (as developer) |

---

## Decision: NOT RECOMMENDED

### Primary Reason: Scope Mismatch

Flowspec and tool-search-tool operate at fundamentally different abstraction levels:

```
┌────────────────────────────────────────────────────────────┐
│                    User Layer                               │
│  Flowspec users execute workflows via Claude Code       │
│  (/flow:specify, /flow:plan, etc.)                    │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                Application Layer                            │
│  Claude Code (Anthropic's CLI)                             │
│  May or may not use tool-search-tool internally            │
└────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────┐
│                    API Layer                                │
│  tool-search-tool operates here                            │
│  Flowspec has no presence at this layer                 │
└────────────────────────────────────────────────────────────┘
```

### Detailed Reasoning

#### 1. No Integration Path

Flowspec does not make Claude API calls. It provides:
- Slash commands that Claude Code executes
- Templates that structure workflows
- Task management via Backlog.md

There is literally nothing to integrate. tool-search-tool requires:
- Direct API calls with beta headers
- Tool definitions with `defer_loading: true`
- Application code that processes tool search results

#### 2. Wrong Audience

| Flowspec User | tool-search-tool User |
|-----------------|----------------------|
| Wants to write specs faster | Wants to optimize API token usage |
| Uses Claude Code as a tool | Builds applications that use Claude |
| Consumes AI capabilities | Implements AI capabilities |

#### 3. User Confusion

If Flowspec documented tool-search-tool:
- Users would ask: "How do I use this?"
- Answer: "You don't — it's for API developers"
- Result: Confusion about Flowspec's purpose

#### 4. Maintenance Burden

| Concern | Impact |
|---------|--------|
| Beta status | Could change without notice |
| API updates | Would require tracking Anthropic changes |
| Support questions | No actionable answers for Flowspec users |
| Documentation drift | Would become outdated quickly |

#### 5. Precedent Concern

Adding tool-search-tool would suggest Flowspec documents all Claude API features. This is not the project's mission.

---

## Verdict: Never

This is a **categorical mismatch**, not a timing issue.

### Never vs Not Now

| Verdict | Criteria |
|---------|----------|
| **Never** | Fundamental scope mismatch that won't change |
| **Not Now** | Good fit but timing/stability issues |

tool-search-tool will **always** be an API implementation detail. Even if it:
- Becomes stable (exits beta)
- Is widely adopted
- Shows strong performance

It will remain irrelevant to Flowspec users because they don't build Claude API applications.

---

## Alternative Approaches

If the underlying goal is "help users discover and use the right tools," consider:

### 1. Improve Command Documentation

```markdown
## Available Workflows

| Command | Purpose | When to Use |
|---------|---------|-------------|
| /flow:specify | Create feature specs | Starting new features |
| /flow:plan | Architecture planning | After spec approval |
| /flow:implement | Code generation | After planning |
| /flow:validate | Quality checks | Before PR |
| /flow:operate | DevOps/SRE tasks | Deployment |
```

### 2. Add Help Command

Create `/flow:help` that explains:
- Available commands and their purposes
- Recommended workflow progression
- Common use cases and examples

### 3. Workflow Tutorial

Create `docs/guides/flowspec-workflow-tutorial.md`:
- Step-by-step guide through a feature
- When to use each command
- Tips for effective SDD

### 4. Command Discovery in CLI

Enhance `specify` CLI with:
```bash
specify workflows    # List available workflows
specify help plan    # Get help for specific workflow
```

---

## References

### Official Documentation

- [Introducing advanced tool use on the Claude Developer Platform | Anthropic](https://www.anthropic.com/engineering/advanced-tool-use)
- [Tool search tool - Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)

### Related Resources

- [GitHub - anthropics/claude-code](https://github.com/anthropics/claude-code)
- [Inside Claude Code's Web Tools: WebFetch vs WebSearch](https://mikhail.io/2025/10/claude-code-web-tools/)
- [Discover tools that work with Claude](https://www.anthropic.com/news/connectors-directory)

---

## Appendix: API Example (For Reference Only)

This is what tool-search-tool usage looks like at the API level:

```python
import anthropic

client = anthropic.Anthropic()

# Define tools with deferred loading
tools = [
    {
        "name": "get_weather",
        "description": "Get weather for a location",
        "defer_loading": True,  # Key flag
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    },
    # ... many more tools
]

# Make API call with beta header
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    betas=["advanced-tool-use-2025-11-20"],  # Required
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}]
)
```

This code would be written by developers building Claude-powered applications, not by Flowspec users.

---

**Document Author**: Claude (via Flowspec evaluation workflow)
**Review Status**: Complete
**Next Review**: Not applicable (Never verdict)
