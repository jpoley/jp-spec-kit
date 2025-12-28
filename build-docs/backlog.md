# Backlog.md Integration - Quick Reference

This file provides quick access to Backlog.md functionality for the flowspec project.

## 🚀 Quick Commands

### View Tasks
```bash
# Kanban board (interactive)
backlog board

# Web UI (browser)
backlog browser

# Project overview
backlog overview

# Search tasks
backlog search "keyword"
```

### Manage Tasks
```bash
# Create task
backlog task create "Task title" --labels "US1,P0" --status "To Do"

# Edit task
backlog task edit task-1

# View task details
backlog task view task-1

# Archive task
backlog task archive task-1
```

### AI Integration (via Claude Code)
```
Ask Claude:
- "List all tasks in the backlog"
- "Show me task-1 details"
- "Create a new task for implementing user authentication"
- "Update task-1 to Done"
- "Search for all tasks labeled US1"
```

## 📊 Current Project Status

**Project**: flowspec
**MCP Integration**: ✅ Configured
**Tasks**: See `backlog/tasks/`

## Documentation

- **Integration Plan**: `docs/backlog-integration-plan.md`
- **Quick Start**: `docs/guides/backlog-quickstart.md`
- **User Guide**: `docs/guides/backlog-user-guide.md`
- **Commands Reference**: `docs/reference/backlog-commands.md`
- **Backlog.md Docs**: https://github.com/MrLesk/Backlog.md

## 🔧 Configuration Files

- **MCP Config**: `.mcp.json` (Backlog.md MCP server)
- **Backlog Config**: `backlog/config.yml` (Project settings)
- **Tasks**: `backlog/tasks/` (All task files)

## ✅ Integration Status

- [x] Backlog.md installed (v1.20.1)
- [x] Project initialized
- [x] MCP configured for Claude Code
- [x] Demo tasks created
- [x] Git tracking enabled
- [x] CLI functional
- [x] Documentation complete

**Status**: ✅ FULLY OPERATIONAL

## 🎯 Next Steps

1. **Ready for Use**: All components configured and working
2. **MVP Implementation**: Build task generator (see PRD)
3. **Beta Testing**: Test with real features
4. **Full Integration**: Complete US1-US5 from PRD

---

*For detailed information, see the documentation files listed above.*
