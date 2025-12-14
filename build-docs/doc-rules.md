# Documentation Organization Rules

## Key Folders

| Folder | Purpose | Audience |
|--------|---------|----------|
| `./build-docs/` | Internal docs for BUILDING flowspec | Builders/Contributors |
| `./user-docs/` | Published docs for USING flowspec | Users/Consumers |
| `./backlog/` | Task backlog for building flowspec | Builders |
| `./archive/` | Historical/archived content | Builders |

## build-docs/ Directory Structure

All directories in `build-docs/` are for **internal builder use only** (not published/installed).

| Directory | Purpose |
|-----------|---------|
| `adr/` | Architecture Decision Records |
| `assess/` | Assessment documents for features/proposals |
| `audit/` | Audit documents and cleanup plans |
| `case-studies/` | Case studies of implementations |
| `design/` | Design documents and diagrams |
| `diagrams/` | Visual diagrams and exports |
| `evaluations/` | Tool and feature evaluations |
| `examples/` | Example configurations (constitutions, workflows, hooks) |
| `legal/` | Legal reviews and licensing |
| `media/` | Media files (logos, images) |
| `platform/` | Platform design docs (integrations, CI/CD, infrastructure) |
| `prd/` | Product Requirements Documents |
| `qa/` | QA reports and summaries |
| `reference/` | Reference documentation for builders |
| `reports/` | Implementation reports and analyses |
| `research/` | Research documents (competitor analysis, technology research) |
| `runbooks/` | Operational runbooks and recovery procedures |
| `security/` | Security documentation, policies, threat models |
| `specs/` | Technical specifications |
| `upstream-contributions/` | Plans for contributing to upstream projects |
| `building/` | **DEPRECATED** - See README.md for migration map |

## user-docs/ Directory Structure

All content in `user-docs/` is **published and user-facing** (100% clear for every aspect of using flowspec).

| Directory | Purpose |
|-----------|---------|
| `user-guides/` | Step-by-step guides for using flowspec |
| Root files | Quick start, installation, configuration |

## Categorization Guidelines

When adding new documents, use this decision tree:

1. **Is it for users/consumers?** → `user-docs/`
2. **Is it a decision record?** → `build-docs/adr/`
3. **Is it requirements/objectives?** → `build-docs/prd/`
4. **Is it a technical specification?** → `build-docs/specs/`
5. **Is it research/evaluation?** → `build-docs/research/` or `build-docs/evaluations/`
6. **Is it a recovery/operations procedure?** → `build-docs/runbooks/`
7. **Is it platform/integration design?** → `build-docs/platform/`
8. **Is it security-related?** → `build-docs/security/`
9. **Is it an implementation report?** → `build-docs/reports/`
10. **Default for builder docs** → Categorize by content type above
