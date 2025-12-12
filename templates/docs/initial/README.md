# INITIAL Feature Intake Documents

This directory contains templates for INITIAL-style feature intake documents.

## Purpose

INITIAL documents are the **canonical starting point** for any new feature-level change. They provide structured context that flows into:

- PRDs (Product Requirements Documents)
- PRPs (Product Requirements Prompts)
- Implementation tasks

## Template

- `initial-feature-template.md` - The main template for creating INITIAL documents

## Usage

1. **Copy the template** to your project's `docs/features/` directory:
   ```bash
   cp templates/docs/initial/initial-feature-template.md docs/features/<feature-slug>-initial.md
   ```

2. **Fill in each section**:
   - FEATURE: Problem, outcome, constraints, importance
   - EXAMPLES: Relevant files and behavior examples
   - DOCUMENTATION: Links to related docs and tasks
   - OTHER CONSIDERATIONS: Gotchas, dependencies, security, performance

3. **Process with `/flow:intake`**:
   ```bash
   /flow:intake docs/features/<feature-slug>-initial.md
   ```
   This creates a backlog task and task memory file.

4. **Continue with workflow**:
   - `/flow:assess` - Evaluate complexity
   - `/flow:specify` - Create detailed PRD
   - `/flow:generate-prp` - Create context bundle

## Pattern Source

Based on the context-engineering-intro patterns (archon-inspired):
- Single INITIAL doc per feature
- Structured sections for consistent intake
- Machine-parseable format for downstream automation

## Related Documentation

- [Context Engineering Guide](../../guides/context-engineering.md) (coming soon)
- [Workflow Architecture](../../guides/workflow-architecture.md)
