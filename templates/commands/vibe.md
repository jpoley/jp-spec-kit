---
description: Casual development mode with minimal ceremony - just logs and light documentation.
---

## User Input

```text
$ARGUMENTS
```

Consider the user input to understand what they want to build.

## Vibe Mode

This is **casual development mode** - less rigor, faster iteration. Use this when:
- Exploring an idea
- Quick prototyping
- Small fixes that don't need full SDD workflow
- Learning or experimenting

### What's Required (Always)

1. **Log significant decisions** to `.logs/decisions/`
2. **Log events** to `.logs/events/`

### What's Encouraged (But Not Blocking)

- Brief notes about what you're building
- A simple plan (even just bullet points)
- Basic tests if touching existing code

### What's NOT Required

- Formal PRD or spec documents
- Backlog task creation
- Workflow state management
- Constitution validation
- Full rigor rule compliance

## Execution

### Step 1: Quick Context Check

```bash
# Create logs directories if needed
mkdir -p .logs/decisions .logs/events

# Note the date for logging
TODAY=$(date +%Y-%m-%d)
echo "Vibe mode started: $TODAY"
```

### Step 2: Capture Intent

Before coding, briefly note what you're doing:

```bash
# Log the session start
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","type":"vibe_session","description":"'"${ARGUMENTS:-casual development}"'"}' >> ".logs/events/${TODAY}.jsonl"
```

### Step 3: Do The Work

Now just code! Build what the user wants. As you work:

**Log significant decisions** (technology choices, trade-offs):
```bash
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","decision":"chose X over Y","rationale":"because Z"}' >> ".logs/decisions/${TODAY}.jsonl"
```

**If you hit something worth remembering**, jot it down in `.logs/notes.md` or similar.

### Step 4: Wrap Up

When done, log completion:
```bash
echo '{"timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","type":"vibe_complete","summary":"what was accomplished"}' >> ".logs/events/${TODAY}.jsonl"
```

## Guidelines

### Good Vibe Habits

- **Commit often** - small commits are easier to understand
- **Brief commit messages** - no need for elaborate formatting
- **Log decisions** - future you will thank present you
- **Test critical paths** - at least manually verify it works

### When to Escalate to Full SDD

Consider `/flow:assess` if:
- The work grows larger than expected
- Multiple people need to coordinate
- It touches security or compliance areas
- You realize you need formal requirements

### What We Skip

| Full SDD | Vibe Mode |
|----------|-----------|
| `/flow:assess` | Just start |
| `/flow:specify` | Brief notes |
| `/flow:plan` | Mental model |
| `/flow:implement` | Just code |
| `/flow:validate` | Quick test |
| Backlog tasks | Optional |
| Workflow states | None |
| Rigor rules | Logging only |

## Output

When complete, summarize:
```
## Vibe Session Complete

**What was built**: [brief description]

**Key decisions**: [any logged decisions]

**Files changed**: [list main files]

**Next steps**: [if any]
```

---

*Vibe mode: Less ceremony, more building. Log decisions, ship code.*
