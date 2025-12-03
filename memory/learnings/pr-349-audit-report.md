# Learnings from PR #349: Audit Report Generator

**Date**: 2025-12-03
**PR**: #349 (galway-task-214-audit-report)
**Status**: Fixes applied in branch `galway-learnings-audit-report`

## Summary

PR #349 introduced the security audit report generator with 2 code quality issues identified by Copilot review.

---

## Issues Fixed

### 1. Unused Configuration Field

**File**: `generator.py:27`
**Problem**: `include_false_positives` config field was defined but never used.

**Original code**:
```python
@dataclass
class ReportConfig:
    project_name: str = "Security Audit"
    include_false_positives: bool = False  # Never used!
    max_remediations: int = 10
```

**Fix**: Implement the functionality - check the config before skipping false positives:
```python
if triage and triage.classification.value == "FP":
    if not self.config.include_false_positives:
        continue
```

**Why it matters**:
- Dead code is confusing - readers expect it to work
- Configuration options MUST have corresponding implementation
- Unused code increases maintenance burden

**Rule to add**:
> Every configuration field MUST be used somewhere in the code. Before adding a config option, implement its functionality first or remove the field entirely.

---

### 2. HTML Output Contains Raw Markdown

**File**: `generator.py:320`
**Problem**: HTML output wrapped markdown in `<pre>` tag instead of converting it.

**Original code**:
```python
def to_html(self, report: AuditReport) -> str:
    markdown_content = self.to_markdown(report)
    html = f"""...
        <pre style="white-space: pre-wrap;">{markdown_content}</pre>
    ..."""
```

**Fix**: Implement proper markdown-to-HTML conversion:
```python
def to_html(self, report: AuditReport) -> str:
    markdown_content = self.to_markdown(report)
    html_content = self._markdown_to_html(markdown_content)  # New method
    ...
```

**Why it matters**:
- Users expect HTML output to render correctly in browsers
- Raw markdown in HTML is unreadable and unprofessional
- Each output format should be properly implemented or clearly documented as not supported

**Rule to add**:
> Output format methods MUST produce properly formatted content for their target format. If a format is not fully implemented, either:
> 1. Implement it correctly (preferred)
> 2. Remove the method entirely
> 3. Raise NotImplementedError with a clear message

---

## Additional Improvement: Variable Name Collision

**Issue discovered during fix**: Local variable `html` shadowed the `html` module import.

**Problem**:
```python
import html  # Module import

def to_html(self, report):
    html = f"""..."""  # Shadows module!
    return html
```

**Fix**: Rename local variable to `html_output`.

**Rule to add**:
> Never use variable names that shadow imported modules. Common problematic names:
> - `html`, `json`, `re`, `os`, `sys`
> - Use descriptive names like `html_output`, `json_data`, `regex_pattern`

---

## Checklist for Future PRs

Before submitting PRs with configuration or multi-format output:

- [ ] Every config field is used somewhere in the code
- [ ] All output formats produce properly formatted content
- [ ] Variable names don't shadow module imports
- [ ] Dead/unused code is removed, not left commented

---

## Files Changed

| File | Issues Fixed |
|------|--------------|
| `generator.py` | Unused config, HTML output, variable naming |

---

## References

- [PR #349](https://github.com/jpoley/jp-spec-kit/pull/349) - Original PR with Copilot review
