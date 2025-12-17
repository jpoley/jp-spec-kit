# Learnings: Example Skill Implementation Pattern

**Date**: 2025-12-16
**Context**: Creating gather-learnings skill (task-501)
**Status**: Template/Example

## Summary

This learning file demonstrates the expected format for documenting lessons learned. It serves as a template for future learning documentation.

## Issue Categories

### 1. Skill Documentation Structure

**Problem**: Skills need clear metadata and usage patterns for effective invocation.

**Files affected**:
- `.claude/skills/*/SKILL.md`

**Why it matters**:
- AI agents need clear invocation patterns
- Users need to understand when to use which skill
- Consistency across skills improves maintainability

**Rule to add**:
> Every skill MUST include:
> 1. YAML frontmatter with name and description
> 2. "When to Use This Skill" section
> 3. Clear input/output examples
> 4. Integration points with workflow commands
> 5. Quality checklist

### 2. Learning File Metadata

**Problem**: Learning files need consistent structure for machine parsing.

**Why it matters**:
- Skills like gather-learnings need to parse learning files programmatically
- Consistent structure enables automated extraction
- Metadata helps with relevance scoring

**Rule to add**:
> Learning files MUST include:
> 1. Title following "Learnings: {Context}: {Description}" or "Lessons Learned: {Description}"
> 2. Metadata section with Date, PR/Task, Status
> 3. Summary section (brief overview)
> 4. Issue Categories with Problem/Files/Why/Rule structure
> 5. Checklist for future prevention
> 6. Optional: Files Changed table

### 3. Keyword Coverage

**Problem**: Learning files need rich keywords for effective matching.

**Files affected**:
- `memory/learnings/*.md`

**Why it matters**:
- gather-learnings skill relies on keyword matching
- Poor keyword coverage means relevant learnings get missed
- Technology names, patterns, and failure modes should be explicit

**Rule to add**:
> Include explicit mentions of:
> 1. File paths or directory patterns
> 2. Technology names (e.g., "pytest", "ruff", "FastAPI")
> 3. Failure modes (e.g., "CI failure", "import error", "timeout")
> 4. Patterns/anti-patterns (e.g., "early return", "broad regex")

## Checklist for Future Learning Documentation

Before committing a new learning file:

- [ ] Includes Date, PR/Task, Status in metadata
- [ ] Has clear Summary section
- [ ] Issue categories include Problem/Files/Why/Rule
- [ ] File paths are relative to repo root
- [ ] Technology names explicitly mentioned
- [ ] Prevention checklist included
- [ ] Specific, actionable rules (not generic advice)

## Files Changed

| File | Purpose |
|------|---------|
| `.claude/skills/gather-learnings/SKILL.md` | New skill for extracting relevant learnings |
| `memory/learnings/example-skill-implementation.md` | Template demonstrating learning file format |

## Example Gotcha Extraction

**From this learning file**:

| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| Skills lack clear metadata and invocation patterns | AI agents can't determine when to use skill, users confused | Include YAML frontmatter, "When to Use" section, examples, integration points | memory/learnings/example-skill-implementation.md |
| Learning files without consistent structure | Automated parsing fails, skills can't extract relevant lessons | Follow standard structure: metadata, summary, issue categories, checklist | memory/learnings/example-skill-implementation.md |
| Missing keywords in learning files | gather-learnings skill can't match relevant learnings | Explicitly mention file paths, technologies, failure modes, patterns | memory/learnings/example-skill-implementation.md |

## Tags

`skills`, `documentation`, `metadata`, `templates`, `gather-learnings`

## Related

- Task: task-501 (Implement gather-learnings helper skill)
- Task: task-500 (Add Known Gotchas section to templates)
- Skill: `.claude/skills/gather-learnings/SKILL.md`
