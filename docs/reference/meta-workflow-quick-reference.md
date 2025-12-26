# Meta-Workflow Quick Reference

**Version**: 1.0.0
**Last Updated**: 2025-12-26

## 3 Commands, Complete Workflow

```bash
/flow:meta-research    # Plan It   (To Do → Planned)
/flow:meta-build       # Create It (Planned → Validated)
/flow:meta-run         # Deploy It (Validated → Deployed)
```

## Meta-Workflow at a Glance

| Meta-Workflow | Sub-Workflows | Input State | Output State | Artifacts |
|---------------|---------------|-------------|--------------|-----------|
| **research** | assess<br>specify<br>research*<br>plan | To Do | Planned | Assessment<br>PRD<br>Research*<br>ADRs<br>Tasks |
| **build** | implement<br>validate | Planned | Validated | Code<br>Tests<br>QA Report<br>Security Report |
| **run** | operate | Validated | Deployed | Runbook<br>Deploy Configs |

*Research is conditional (complexity ≥ 7)

## Command Comparison

### Before (8 Commands)
```
To Do → /flow:assess → Assessed
     → /flow:specify → Specified
     → /flow:research → Researched (optional)
     → /flow:plan → Planned
     → /flow:implement → In Implementation
     → /flow:validate → Validated
     → /flow:operate → Deployed
```

### After (3 Commands)
```
To Do → /flow:meta-research → Planned
     → /flow:meta-build → Validated
     → /flow:meta-run → Deployed
```

## Usage Examples

### New Feature (Full Workflow)
```bash
git checkout -b feature/user-settings
/flow:meta-research
/flow:meta-build
/flow:meta-run
```

### Iteration (Re-run Specific Phase)
```bash
# Just re-implement after code changes
/flow:implement

# Or re-run full build atomically
/flow:meta-build
```

### Debugging (Granular Control)
```bash
# Fix specific phase
/flow:specify
/flow:plan
```

## Quality Gates (Build Workflow)

The build meta-workflow enforces these gates:

| Gate | Threshold | Blocking? |
|------|-----------|-----------|
| **Test Coverage** | 80% | Yes |
| **Security Scan** | 0 HIGH+ findings | Yes |
| **Acceptance Criteria** | 100% coverage | Yes |

## Options

### Common Options (All Meta-Workflows)
```bash
--task-id <ID>        # Specify task (default: auto-detect)
--dry-run             # Preview without execution
--verbose             # Detailed logging
```

### Research-Specific
```bash
--force-research      # Force research even if complexity < 7
--skip-research       # Skip research even if complexity ≥ 7
--light-mode          # Use lightweight templates
```

### Build-Specific
```bash
--skip-tests          # Skip test execution (not recommended)
--skip-security       # Skip security scans (not recommended)
--coverage-threshold N # Override coverage threshold (default: 80)
```

### Run-Specific
```bash
--environment <ENV>   # Target environment (default: production)
--auto-deploy         # Auto-trigger deployment (future)
```

## Cross-Tool Usage

### Claude Code
```bash
/flow:meta-research
```

### GitHub Copilot
```
@flowspec /flow:meta-research for feature X
```

### Cursor
```
@flowspec /flow:meta-build
```

### Gemini Code
```
flowspec meta-run --environment staging
```

## Decision Tree: When to Use What

```
Starting new feature?
├─ Yes → Use /flow:meta-research
└─ No
   ├─ Implementing planned feature?
   │  └─ Yes → Use /flow:meta-build
   └─ Deploying validated feature?
      └─ Yes → Use /flow:meta-run

Need fine-grained control?
└─ Use granular commands (/flow:assess, /flow:specify, etc.)

Debugging specific phase?
└─ Use granular commands

Iterating on code?
├─ Just code changes → /flow:implement
├─ Code + tests → /flow:meta-build
└─ Full re-run → /flow:meta-research
```

## Granular Commands (Still Available!)

All original commands still work:

| Command | Input State | Output State |
|---------|-------------|--------------|
| /flow:assess | To Do | Assessed |
| /flow:specify | Assessed | Specified |
| /flow:research | Specified | Researched |
| /flow:plan | Specified/Researched | Planned |
| /flow:implement | Planned | In Implementation |
| /flow:validate | In Implementation | Validated |
| /flow:operate | Validated | Deployed |
| /flow:submit-n-watch-pr | Validated/In Implementation | Validated |

## Customization

Edit `flowspec_workflow.yml` to customize:

### Example: Change Research Condition
```yaml
meta_workflows:
  research:
    sub_workflows:
      - workflow: "research"
        condition: "complexity_score >= 9"  # Stricter threshold
```

### Example: Lower Coverage Threshold
```yaml
meta_workflows:
  build:
    quality_gates:
      - type: "test_coverage"
        threshold: 70  # More lenient
```

## Troubleshooting

### Meta-workflow fails partway through
- Partial progress is preserved
- Fix the issue
- Re-run the meta-workflow (will resume)

### Quality gate fails
- Review gate failure details
- Fix the underlying issue (add tests, fix security, update ACs)
- Re-run `/flow:meta-build`

### Want to skip a sub-workflow
- Use granular commands instead
- Or customize condition in `flowspec_workflow.yml`

## Events Emitted

All meta-workflows emit events to `.logs/events/`:

```jsonl
{"event": "meta_workflow.started", ...}
{"event": "sub_workflow.started", ...}
{"event": "sub_workflow.completed", ...}
{"event": "quality_gate.validated", ...}
{"event": "meta_workflow.completed", ...}
```

## Resources

- **Migration Guide**: `docs/guides/meta-workflow-migration.md`
- **ADR**: `docs/adr/003-meta-workflow-simplification.md`
- **Command Docs**:
  - `templates/commands/flow/meta-research.md`
  - `templates/commands/flow/meta-build.md`
  - `templates/commands/flow/meta-run.md`
- **Config**: `flowspec_workflow.yml`

## Support

Questions? Check the docs or open an issue:
- Docs: `docs/guides/`
- Issues: https://github.com/jpoley/flowspec/issues

---

**Remember**: Meta-workflows simplify the common path, granular commands give you power when you need it. Choose your own adventure! 🚀
