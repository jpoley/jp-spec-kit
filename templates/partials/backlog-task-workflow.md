**CRITICAL**: Never edit task files directly. All operations MUST use the backlog CLI.

### Essential Commands

```bash
# Discover tasks
backlog task list --plain
backlog task <id> --plain
backlog search "<keyword>" --plain

# Start work
backlog task edit <id> -s "In Progress" -a @<agent-name>

# Track progress (mark ACs as you complete them)
backlog task edit <id> --check-ac 1
backlog task edit <id> --check-ac 2

# Add implementation notes
backlog task edit <id> --notes $'Description of what was implemented'

# Complete task (only after all ACs checked)
backlog task edit <id> -s Done
```

### Definition of Done

Before marking a task Done:
- [ ] All acceptance criteria checked
- [ ] Implementation notes added
- [ ] Tests pass locally
- [ ] Code formatted and linted
- [ ] Self-review completed
