#!/bin/bash
# Generate deprecated command aliases for backwards compatibility

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATES_DIR="$SCRIPT_DIR/../templates/commands"

# Command mappings: old_command -> new_command
declare -A COMMAND_MAP=(
    ["flowspec/assess.md"]="pm/assess.md"
    ["flowspec/specify.md"]="pm/define.md"
    ["flowspec/research.md"]="pm/discover.md"
    ["flowspec/plan.md"]="arch/design.md"
    ["flowspec/implement.md"]="dev/build.md"
    ["flowspec/validate.md"]="qa/verify.md"
    ["flowspec/operate.md"]="ops/deploy.md"
    ["flowspec/prune-branch.md"]="dev/cleanup.md"
    ["flowspec/security_web.md"]="sec/scan.md"
    ["flowspec/security_triage.md"]="sec/triage.md"
    ["flowspec/security_fix.md"]="sec/fix.md"
    ["flowspec/security_workflow.md"]="sec/audit.md"
    ["flowspec/security_report.md"]="sec/report.md"
)

echo "Generating deprecated command aliases..."

for old_cmd in "${!COMMAND_MAP[@]}"; do
    new_cmd="${COMMAND_MAP[$old_cmd]}"

    old_namespace=$(dirname "$old_cmd")
    old_name=$(basename "$old_cmd" .md)
    new_namespace=$(dirname "$new_cmd")
    new_name=$(basename "$new_cmd" .md)

    # Extract description from new command
    description=$(grep -m 1 "^description:" "$TEMPLATES_DIR/$new_cmd" | cut -d':' -f2- | xargs)

    # Create deprecated alias
    cat > "$TEMPLATES_DIR/${old_namespace}/_DEPRECATED_${old_name}.md" <<EOF
---
description: "[DEPRECATED] Use /${new_namespace}:${new_name} instead - ${description}"
deprecated: true
replacement: "/${new_namespace}:${new_name}"
removal_date: "2026-12-09"
---

# DEPRECATED: This command has moved

This command has been **deprecated** and will be removed on **2026-12-09**.

## New Command

Please use the new role-based command instead:

\`\`\`bash
/${new_namespace}:${new_name} [arguments]
\`\`\`

## Why the Change?

Flowspec has migrated to role-based command namespaces to improve discoverability and align commands with team roles. The \`/flowspec\` namespace contained 18+ commands, making it difficult to find relevant commands.

## Migration

Simply replace \`/${old_namespace}:${old_name}\` with \`/${new_namespace}:${new_name}\` in your workflows. The functionality is identical.

**Before**:
\`\`\`bash
/${old_namespace}:${old_name} my-feature
\`\`\`

**After**:
\`\`\`bash
/${new_namespace}:${new_name} my-feature
\`\`\`

## Role-Based Command Structure

Commands are now organized by role:

- \`/pm\` - Product Manager commands (assess, define, discover)
- \`/arch\` - Architect commands (design, decide, model)
- \`/dev\` - Developer commands (build, debug, refactor, cleanup)
- \`/sec\` - Security Engineer commands (scan, triage, fix, audit, report)
- \`/qa\` - QA Engineer commands (test, verify, review)
- \`/ops\` - SRE/DevOps commands (deploy, monitor, respond, scale)

## Learn More

- [Migration Guide](../../docs/guides/command-migration.md)
- [ADR: Role-Based Command Namespaces](../../docs/adr/ADR-role-based-command-namespaces.md)

---

**Redirecting to /${new_namespace}:${new_name}...**

{{INCLUDE:.claude/commands/${new_cmd}}}
EOF

    echo "  Created: ${old_namespace}/_DEPRECATED_${old_name}.md -> ${new_cmd}"
done

echo ""
echo "Deprecated aliases created successfully!"
echo ""
echo "Summary:"
echo "  Total aliases: ${#COMMAND_MAP[@]}"
echo "  Location: $TEMPLATES_DIR/flowspec/_DEPRECATED_*.md"
echo ""
echo "Next steps:"
echo "  1. Review generated files"
echo "  2. Create symlinks: .claude/commands/ -> templates/commands/"
echo "  3. Test deprecation warnings"
