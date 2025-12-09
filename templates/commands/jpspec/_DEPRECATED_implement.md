---
description: "[DEPRECATED] Use /dev:build instead - Execute implementation using specialized frontend and backend engineer agents with code review."
deprecated: true
replacement: "/dev:build"
removal_date: "2026-12-09"
---

# DEPRECATED: This command has moved

This command has been **deprecated** and will be removed on **2026-12-09**.

## New Command

Please use the new role-based command instead:

```bash
/dev:build [arguments]
```

## Why the Change?

Specflow has migrated to role-based command namespaces to improve discoverability and align commands with team roles. The `/jpspec` namespace contained 18+ commands, making it difficult to find relevant commands.

## Migration

Simply replace `/jpspec:implement` with `/dev:build` in your workflows. The functionality is identical.

**Before**:
```bash
/jpspec:implement my-feature
```

**After**:
```bash
/dev:build my-feature
```

## Role-Based Command Structure

Commands are now organized by role:

- `/pm` - Product Manager commands (assess, define, discover)
- `/arch` - Architect commands (design, decide, model)
- `/dev` - Developer commands (build, debug, refactor, cleanup)
- `/sec` - Security Engineer commands (scan, triage, fix, audit, report)
- `/qa` - QA Engineer commands (test, verify, review)
- `/ops` - SRE/DevOps commands (deploy, monitor, respond, scale)

## Learn More

- [Migration Guide](../../docs/guides/command-migration.md)
- [ADR: Role-Based Command Namespaces](../../docs/adr/ADR-role-based-command-namespaces.md)

---

**Redirecting to /dev:build...**

{{INCLUDE:.claude/commands/dev/build.md}}
