---
name: gather-learnings
description: Use when creating PRDs or PRPs to populate the Gotchas/Prior Failures section. Reads learning files from memory/learnings and matches entries based on file paths, keywords, or tags. Returns curated list suitable for PRD/PRP insertion.
---

# Gather Learnings Skill

You are an expert at extracting and curating relevant lessons learned from past implementations to prevent recurring mistakes. You excel at pattern matching, context analysis, and presenting actionable insights.

## When to Use This Skill

- Creating or updating Product Requirements Documents (PRDs)
- Generating Platform Requirements Packages (PRPs)
- Populating "Gotchas / Prior Failures" sections
- Researching historical context for a feature
- Identifying risks based on past failures
- Finding relevant lessons for specific code areas or technologies

## How It Works

### 1. Input Context

You will be provided with:
- **Feature description**: What is being implemented
- **File paths**: Code files involved in the implementation
- **Keywords**: Technologies, patterns, or concepts (e.g., "API", "authentication", "database migration")
- **Tags**: Specific labels (e.g., "security", "performance", "testing")

### 2. Search Strategy

Scan all files in `memory/learnings/` and match entries based on:

#### A. File Path Matching
- Extract file paths mentioned in learning documents (e.g., from "Files Changed" sections)
- Match against files involved in current feature
- Consider directory-level matches (e.g., `classifiers/` matches all classifier modules)

#### B. Keyword Matching
- Search for keywords in:
  - Learning document titles
  - Summary sections
  - Issue categories/root causes
  - Code quality rules
  - Checklists
- Use case-insensitive matching
- Consider synonyms and related terms (e.g., "lint" matches "linting", "ruff check")

#### C. Tag/Category Matching
- Match based on issue categories (e.g., "imports", "error handling", "path handling")
- Match based on technology stack (e.g., "Python", "SQL", "git")
- Match based on failure types (e.g., "CI failure", "security issue", "performance")

#### D. Contextual Relevance
- Prioritize learnings from recently created/updated files
- Weight learnings with specific file matches higher than keyword-only matches
- Consider the severity of past failures (CI failures, security issues rank higher)

### 3. Output Format

Return a curated list formatted for direct insertion into PRD/PRP "Gotchas / Prior Failures" sections:

```markdown
| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| {Brief description of issue/pitfall} | {What goes wrong} | {How to avoid it} | {memory/learnings/filename.md} |
```

**Guidelines for each column**:

- **Gotcha**: 1-2 sentence summary of the issue (specific and actionable)
- **Impact**: Concrete consequence (e.g., "CI lint failure", "False positive detections", "Git blame command fails")
- **Mitigation**: Clear, actionable prevention step (not just "be careful")
- **Source**: Relative path to learning document (e.g., `memory/learnings/pr-342-triage-engine.md`)

### 4. Prioritization

When multiple learnings match, prioritize by:
1. **Direct file path match** (highest priority)
2. **Similar failure mode** (e.g., both involve CI failures)
3. **Shared technology** (e.g., both use ruff, pytest)
4. **Recent occurrence** (newer learnings may be more relevant)
5. **Severity of past impact** (security > performance > style)

Return the top 5-8 most relevant learnings. If fewer than 3 match, include that information in the output.

## Example Invocation

### Scenario 1: New API Endpoint Feature

**Input**:
- Feature: "Add user authentication API endpoint"
- File paths: `src/api/auth.py`, `tests/test_auth.py`
- Keywords: "API", "authentication", "testing", "validation"
- Tags: "security", "backend"

**Output**:
```markdown
| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| Imports placed inside methods instead of module level | Violates PEP 8, reduces readability, hides dependencies | All imports MUST be at module level; only exception is documented circular imports | memory/learnings/pr-342-triage-engine.md |
| Missing error context in exception handlers | Silent failures make production issues hard to diagnose | Log exceptions with context using logger.error(), include relevant data | memory/learnings/pr-342-triage-engine.md |
| Input validation patterns too broad | False positives degrade classifier accuracy, security tools lose trust | Test patterns with adversarial examples; add context requirements | memory/learnings/pr-342-triage-engine.md |
```

### Scenario 2: Code Quality Hook

**Input**:
- Feature: "Pre-commit quality gates"
- File paths: `.claude/hooks/pre-commit.py`
- Keywords: "ruff", "format", "lint", "pytest", "CI"
- Tags: "testing", "quality"

**Output**:
```markdown
| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| File modified after local validation but before commit | CI lint check fails even if local checks passed | Run full validation chain immediately before commit: ruff format → ruff format --check → ruff check → pytest | memory/learnings/pr-448-quality-gates-failure.md |
| Unused constants/variables defined "just in case" | CI lint fails, code review rejects | Only define what you use; review all variables before commit | memory/learnings/pr-448-quality-gates-failure.md |
| Incomplete implementations leaving calculated but unused variables | Dead code, unclear intent | Complete implementations fully; delete unused calculations | memory/learnings/pr-448-quality-gates-failure.md |
```

### Scenario 3: No Matches

**Input**:
- Feature: "Update documentation structure"
- File paths: `docs/guides/new-guide.md`
- Keywords: "documentation", "markdown"
- Tags: "docs"

**Output**:
```markdown
No specific gotchas found in memory/learnings/ for this feature.

Consider reviewing:
- General code quality standards in memory/code-standards.md
- Test quality standards in memory/test-quality-standards.md
```

## Learning File Format

Learning files in `memory/learnings/` typically follow this structure:

```markdown
# Learnings from {Context}: {Title}

**Date**: {ISO date}
**PR**: #{number} ({branch-name})
**Status**: {Current status}

## Summary
{Brief overview of what happened}

## Issue Categories / Root Causes
### {Category Name}
**Problem**: {Description}
**Files affected**: {List of files}
**Why it matters**: {Impact explanation}
**Rule to add**: {Prevention guideline}

## Checklist for Future
- [ ] {Prevention item 1}
- [ ] {Prevention item 2}

## Files Changed
| File | Issues Fixed |
|------|--------------|
| {path} | {description} |
```

## Integration Points

This skill is invoked by:

1. **`/flow:specify`**: When creating PRDs, automatically populate gotchas section
2. **`/flow:generate-prp`**: When generating PRPs, gather relevant learnings
3. **Manual invocation**: When updating existing PRDs/PRPs with new context

## Usage Pattern

```bash
# Example agent invocation (internal)
@gather-learnings --files "src/api/auth.py,tests/test_auth.py" \
                  --keywords "API,authentication,validation" \
                  --tags "security,backend"

# Returns gotchas table ready for insertion into PRD
```

## Quality Checklist

Before returning learnings:

- [ ] Each entry is specific and actionable (not generic)
- [ ] Mitigation steps are concrete (not "be careful")
- [ ] Source links are correct relative paths
- [ ] Entries are sorted by relevance (file match > keyword match)
- [ ] Limited to 5-8 most relevant (avoid overwhelming)
- [ ] If few/no matches, explicitly state that

## Edge Cases

### Multiple Matches from Same File
- Consolidate related learnings from the same source
- Summarize if more than 3 issues from same learning doc

### Learnings with Multiple Categories
- Match against each category independently
- Return the learning once with the highest-relevance category

### Outdated Learnings
- All learnings are valid unless superseded
- If a learning references deprecated tools/patterns, note that in output

## Best Practices

1. **Be specific**: "Run ruff format before commit" beats "Follow linting standards"
2. **Be actionable**: Include exact commands or checklist items
3. **Be concise**: One-line summaries for gotcha/impact/mitigation
4. **Be traceable**: Always link to source learning document
5. **Be relevant**: Better to return 2 highly relevant items than 10 loosely related ones

## Anti-Patterns to Avoid

- **Don't** return generic advice not grounded in actual past failures
- **Don't** include learnings with no clear connection to the current feature
- **Don't** create vague mitigations like "test thoroughly" or "review code"
- **Don't** overwhelm with every possible learning (prioritize ruthlessly)
- **Don't** skip the source link (traceability is critical)

---

**Skill Version**: 1.0
**Last Updated**: 2025-12-16
**Maintainer**: Flowspec Core Team
