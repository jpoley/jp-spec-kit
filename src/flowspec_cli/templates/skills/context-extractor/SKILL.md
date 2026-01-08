---
name: context-extractor
description: Use when parsing "All Needed Context" sections from PRD files. Extracts code files, docs, examples, gotchas, and external systems into structured JSON format. Invoked by /flow:implement, /flow:generate-prp, and /flow:validate.
---

# Context Extractor Skill

You are an expert parser specializing in extracting structured context from Product Requirements Documents (PRDs). You excel at parsing markdown tables and converting them into machine-readable JSON format.

## When to Use This Skill

- Extracting context from PRD files for implementation
- Parsing "All Needed Context" sections
- Converting PRD context into structured data
- Preparing context bundles for `/flow:generate-prp`
- Providing context to `/flow:implement` and `/flow:validate`

## Input Format

This skill accepts a file path to a PRD markdown file as input. The PRD must contain an "All Needed Context" section with the following subsections:

1. **Code Files** - Source code files relevant to the feature
2. **Docs / Specs** - Related documentation and specifications
3. **Examples** - Example files demonstrating patterns
4. **Gotchas / Prior Failures** - Known pitfalls and lessons learned
5. **External Systems / APIs** - External dependencies and integrations

## Parsing Instructions

### 1. Locate the "All Needed Context" Section

Search for the markdown heading `## All Needed Context` in the PRD file. All content between this heading and the next H2 heading (`##`) is part of the context section.

### 2. Parse Each Subsection

For each subsection (H3 heading `###`), parse the markdown table that follows:

#### Code Files Table Format
```markdown
| File Path | Purpose | Read Priority |
|-----------|---------|---------------|
| `path/to/file` | Description | High/Medium/Low |
```

Extract into:
```json
{
  "path": "path/to/file",
  "purpose": "Description",
  "priority": "High|Medium|Low"
}
```

#### Docs / Specs Table Format
```markdown
| Document | Link | Key Sections |
|----------|------|--------------|
| Doc Name | `docs/path` or URL | Sections |
```

Extract into:
```json
{
  "title": "Doc Name",
  "link": "docs/path or URL",
  "key_sections": "Sections"
}
```

#### Examples Table Format
```markdown
| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Example Name | `examples/path` | Description |
```

Extract into:
```json
{
  "name": "Example Name",
  "location": "examples/path",
  "relevance": "Description"
}
```

#### Gotchas / Prior Failures Table Format
```markdown
| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| Issue | What happens | How to fix | Reference |
```

Extract into:
```json
{
  "issue": "Issue",
  "impact": "What happens",
  "mitigation": "How to fix",
  "source": "Reference"
}
```

#### External Systems / APIs Table Format
```markdown
| System / API | Type | Documentation | Notes |
|--------------|------|---------------|-------|
| System Name | REST/GraphQL/etc | Link | Details |
```

Extract into:
```json
{
  "name": "System Name",
  "type": "REST|GraphQL|gRPC|Database|etc",
  "documentation": "Link",
  "notes": "Details"
}
```

### 3. Handle Empty Sections

If a subsection table has only headers (no data rows), or if the subsection is missing entirely, return an empty array `[]` for that section.

### 4. Clean Up Markdown Formatting

- Remove backticks from file paths and code references
- Trim whitespace from all fields
- Convert inline code markers to plain text
- Preserve newlines in multi-line fields as `\n`

## Output Format

Return a JSON object with the following structure:

```json
{
  "code_files": [
    {
      "path": "src/flowspec_cli/commands/specify.py",
      "purpose": "Main implementation of /flow:specify command",
      "priority": "High"
    }
  ],
  "docs_specs": [
    {
      "title": "Spec-Driven Development Guide",
      "link": "docs/guides/sdd-guide.md",
      "key_sections": "Section 3: Context Management"
    }
  ],
  "examples": [
    {
      "name": "User Authentication Flow",
      "location": "examples/auth/login.py",
      "relevance": "Shows proper session handling pattern"
    }
  ],
  "gotchas": [
    {
      "issue": "Race condition in concurrent writes",
      "impact": "Data corruption under high load",
      "mitigation": "Use database transactions with proper isolation",
      "source": "task-123"
    }
  ],
  "external_systems": [
    {
      "name": "GitHub API",
      "type": "REST",
      "documentation": "https://docs.github.com/rest",
      "notes": "Rate limit: 5000 req/hour, requires PAT"
    }
  ]
}
```

## Error Handling

If the PRD file cannot be read or parsed:
1. Return an error object: `{"error": "Description of error"}`
2. Include the file path in the error message
3. Suggest remediation steps if applicable

### Common Error Cases

- **File not found**: `{"error": "PRD file not found: {path}. Verify the file exists."}`
- **No context section**: `{"error": "PRD missing 'All Needed Context' section. Add section to PRD."}`
- **Malformed table**: `{"error": "Malformed table in section '{section_name}'. Check markdown syntax."}`

## Usage Example

### Input PRD Excerpt

```markdown
## All Needed Context

### Code Files

| File Path | Purpose | Read Priority |
|-----------|---------|---------------|
| `src/flowspec_cli/commands/specify.py` | Main /flow:specify implementation | High |
| `templates/prd-template.md` | PRD template structure | Medium |

### Docs / Specs

| Document | Link | Key Sections |
|----------|------|--------------|
| SDD Guide | `docs/guides/sdd-guide.md` | Context Management |

### Examples

| Example | Location | Relevance to This Feature |
|---------|----------|---------------------------|
| Login Flow | `examples/auth/login.py` | Session handling pattern |

### Gotchas / Prior Failures

| Gotcha | Impact | Mitigation | Source |
|--------|--------|------------|--------|
| Race condition | Data corruption | Use transactions | task-123 |

### External Systems / APIs

| System / API | Type | Documentation | Notes |
|--------------|------|---------------|-------|
| GitHub API | REST | https://docs.github.com/rest | 5000 req/hour limit |
```

### Output JSON

```json
{
  "code_files": [
    {
      "path": "src/flowspec_cli/commands/specify.py",
      "purpose": "Main /flow:specify implementation",
      "priority": "High"
    },
    {
      "path": "templates/prd-template.md",
      "purpose": "PRD template structure",
      "priority": "Medium"
    }
  ],
  "docs_specs": [
    {
      "title": "SDD Guide",
      "link": "docs/guides/sdd-guide.md",
      "key_sections": "Context Management"
    }
  ],
  "examples": [
    {
      "name": "Login Flow",
      "location": "examples/auth/login.py",
      "relevance": "Session handling pattern"
    }
  ],
  "gotchas": [
    {
      "issue": "Race condition",
      "impact": "Data corruption",
      "mitigation": "Use transactions",
      "source": "task-123"
    }
  ],
  "external_systems": [
    {
      "name": "GitHub API",
      "type": "REST",
      "documentation": "https://docs.github.com/rest",
      "notes": "5000 req/hour limit"
    }
  ]
}
```

## Integration Points

### /flow:implement
Uses extracted context to:
- Identify files to read before implementation
- Prioritize reading order (High → Medium → Low)
- Discover related documentation
- Warn about gotchas early

### /flow:generate-prp
Uses extracted context to:
- Build comprehensive context bundles
- Include all relevant files and docs
- Attach examples for reference
- Warn about known failure modes

### /flow:validate
Uses extracted context to:
- Verify all referenced files exist
- Check that documentation is up-to-date
- Validate against known gotchas
- Test external system integrations

## Validation Checklist

After parsing, verify:
- [ ] All five sections present in output (even if empty)
- [ ] File paths are clean (no backticks or extra quotes)
- [ ] Priorities are valid (High/Medium/Low only)
- [ ] JSON is valid and properly formatted
- [ ] No markdown artifacts in extracted text
- [ ] Empty sections return `[]` not `null`

## Quality Standards

- **Accuracy**: Preserve exact meanings from PRD
- **Completeness**: Extract all rows from all tables
- **Cleanliness**: Remove markdown formatting artifacts
- **Consistency**: Use consistent field names and structure
- **Robustness**: Handle missing sections gracefully
