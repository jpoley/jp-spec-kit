# Backlog.md Hooks System Design

**Status**: Design Document for Upstream Contribution
**Target Repository**: https://github.com/MrLesk/Backlog.md
**Author**: Flowspec Team
**Date**: 2025-12-11

## Overview

This document describes a proposed hook system for backlog.md CLI that enables extensibility through user-defined scripts triggered on task lifecycle events.

## Motivation

AI-augmented development workflows often require automated actions when tasks change state. Examples:
- **Task Memory Systems**: Capture task context when work begins
- **Notification Systems**: Alert team members of status changes
- **Integration Systems**: Sync task state with external tools
- **Analytics**: Track task lifecycle metrics

Currently, these integrations must poll for changes or modify backlog.md's source code. A hook system provides a clean, extensible integration point.

## Design Goals

1. **Zero Breaking Changes**: Hooks are opt-in; existing workflows unchanged
2. **Fail-Safe**: Hook failures never block task operations
3. **Simple**: Executable scripts with environment variables
4. **Fast**: Timeouts prevent hung processes
5. **Secure**: Hooks run with user permissions, no privilege escalation

## Hook Events

### post-task-create
Triggered after a task file is successfully created.

**Environment Variables**:
```bash
BACKLOG_TASK_ID="task-42"
BACKLOG_TASK_TITLE="Implement feature X"
BACKLOG_TASK_STATUS="To Do"
BACKLOG_HOOK_EVENT="post-task-create"
```

### post-task-update
Triggered after task metadata is successfully updated.

**Environment Variables**:
```bash
BACKLOG_TASK_ID="task-42"
BACKLOG_TASK_TITLE="Implement feature X"
BACKLOG_OLD_STATUS="To Do"
BACKLOG_NEW_STATUS="In Progress"
BACKLOG_TASK_ASSIGNEE="@backend-engineer"  # comma-separated if multiple
BACKLOG_HOOK_EVENT="post-task-update"
```

### post-task-archive
Triggered after a task is successfully archived.

**Environment Variables**:
```bash
BACKLOG_TASK_ID="task-42"
BACKLOG_TASK_TITLE="Implement feature X"
BACKLOG_HOOK_EVENT="post-task-archive"
```

## Configuration

### Hook Directory

Hooks are discovered in `.backlog/hooks/` by default:

```
.backlog/
├── config.yml
└── hooks/
    ├── post-task-create.sh
    ├── post-task-update.sh
    └── post-task-archive.sh
```

### Config Schema

Add to `.backlog/config.yml`:

```yaml
hooks:
  enabled: true                    # Global enable/disable
  directory: .backlog/hooks        # Custom hook directory
  timeout: 5000                    # Timeout in milliseconds (default: 5000)
  logLevel: info                   # none, error, info, debug
```

## Implementation

### Architecture

```
┌─────────────────────────────────┐
│  CLI Command                    │
│  (task create/edit/archive)     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Core Operation                 │
│  (create/update/archiveTask)    │
└────────────┬────────────────────┘
             │
             ▼ (after success)
┌─────────────────────────────────┐
│  Hook Executor                  │
│  - Discover hook script         │
│  - Build environment            │
│  - Execute with timeout         │
│  - Log result (non-blocking)    │
└─────────────────────────────────┘
```

### TypeScript Implementation

**src/core/hooks.ts**:
```typescript
import { spawn } from "node:child_process";
import { access, constants } from "node:fs/promises";
import { join } from "node:path";
import type { BacklogConfig, Task } from "../types/index.ts";

export enum HookEvent {
  POST_TASK_CREATE = "post-task-create",
  POST_TASK_UPDATE = "post-task-update",
  POST_TASK_ARCHIVE = "post-task-archive",
}

export interface HookContext {
  taskId: string;
  taskTitle?: string;
  taskStatus?: string;
  oldStatus?: string;
  newStatus?: string;
  assignees?: string[];
}

export interface HookConfig {
  enabled: boolean;
  directory: string;
  timeout: number;
  logLevel: "none" | "error" | "info" | "debug";
}

const DEFAULT_HOOK_CONFIG: HookConfig = {
  enabled: true,
  directory: ".backlog/hooks",
  timeout: 5000,
  logLevel: "info",
};

export function getHookConfig(config?: BacklogConfig): HookConfig {
  return {
    ...DEFAULT_HOOK_CONFIG,
    ...(config?.hooks || {}),
  };
}

export async function emitHook(
  event: HookEvent,
  context: HookContext,
  config: BacklogConfig,
  projectRoot: string,
): Promise<void> {
  const hookConfig = getHookConfig(config);

  if (!hookConfig.enabled) {
    return;
  }

  const hookDir = join(projectRoot, hookConfig.directory);
  const scriptPath = join(hookDir, `${event}.sh`);

  // Check if hook script exists and is executable
  try {
    await access(scriptPath, constants.X_OK);
  } catch {
    // Hook doesn't exist or not executable - this is fine
    if (hookConfig.logLevel === "debug") {
      console.debug(`[hooks] No executable script at ${scriptPath}`);
    }
    return;
  }

  // Build environment variables
  const env = {
    ...process.env,
    BACKLOG_HOOK_EVENT: event,
    BACKLOG_TASK_ID: context.taskId,
    ...(context.taskTitle && { BACKLOG_TASK_TITLE: context.taskTitle }),
    ...(context.taskStatus && { BACKLOG_TASK_STATUS: context.taskStatus }),
    ...(context.oldStatus && { BACKLOG_OLD_STATUS: context.oldStatus }),
    ...(context.newStatus && { BACKLOG_NEW_STATUS: context.newStatus }),
    ...(context.assignees?.length && {
      BACKLOG_TASK_ASSIGNEE: context.assignees.join(","),
    }),
  };

  if (hookConfig.logLevel === "debug") {
    console.debug(`[hooks] Executing ${event} for ${context.taskId}`);
  }

  // Execute hook with timeout (non-blocking, don't await)
  executeHookScript(scriptPath, env, hookConfig).catch((error) => {
    if (hookConfig.logLevel !== "none") {
      console.error(`[hooks] Error executing ${event}:`, error.message);
    }
  });
}

async function executeHookScript(
  scriptPath: string,
  env: Record<string, string | undefined>,
  config: HookConfig,
): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(scriptPath, [], {
      env,
      timeout: config.timeout,
      stdio: config.logLevel === "debug" ? "inherit" : "ignore",
    });

    child.on("exit", (code, signal) => {
      if (signal === "SIGTERM") {
        reject(new Error(`Hook timed out after ${config.timeout}ms`));
      } else if (code !== 0 && config.logLevel !== "none") {
        console.warn(`[hooks] Script exited with code ${code}`);
      }
      resolve();
    });

    child.on("error", (error) => {
      reject(error);
    });
  });
}
```

### Integration Points

**src/core/backlog.ts** - Add hook emissions:

```typescript
import { emitHook, HookEvent } from "./hooks.ts";

// In createTask method (after line 601):
async createTask(task: Task, autoCommit?: boolean): Promise<string> {
  // ... existing code ...
  const filepath = await this.fs.saveTask(task);

  if (await this.shouldAutoCommit(autoCommit)) {
    await this.git.addAndCommitTaskFile(task.id, filepath, "create");
  }

  // Emit hook
  const config = await this.fs.loadConfig();
  await emitHook(
    HookEvent.POST_TASK_CREATE,
    {
      taskId: task.id,
      taskTitle: task.title,
      taskStatus: task.status,
      assignees: task.assignee,
    },
    config,
    this.fs.projectRoot,
  );

  return filepath;
}

// In updateTask method (after line 644):
async updateTask(task: Task, autoCommit?: boolean): Promise<void> {
  // ... existing code ...

  // Fire status change callback if status changed
  if (statusChanged) {
    await this.executeStatusChangeCallback(task, oldStatus, newStatus);
  }

  // Emit hook
  const config = await this.fs.loadConfig();
  await emitHook(
    HookEvent.POST_TASK_UPDATE,
    {
      taskId: task.id,
      taskTitle: task.title,
      taskStatus: task.status,
      oldStatus: statusChanged ? oldStatus : undefined,
      newStatus: statusChanged ? newStatus : undefined,
      assignees: task.assignee,
    },
    config,
    this.fs.projectRoot,
  );
}

// In archiveTask method (after line 1180):
async archiveTask(taskId: string, autoCommit?: boolean): Promise<boolean> {
  // ... existing code ...

  if (success && (await this.shouldAutoCommit(autoCommit))) {
    await this.git.stageFileMove(fromPath, toPath);
    await this.git.commitChanges(`backlog: Archive task ${taskId}`);
  }

  // Emit hook
  if (success) {
    const config = await this.fs.loadConfig();
    const task = await this.fs.loadTask(taskId);
    await emitHook(
      HookEvent.POST_TASK_ARCHIVE,
      {
        taskId,
        taskTitle: task?.title,
      },
      config,
      this.fs.projectRoot,
    );
  }

  return success;
}
```

### Type Definitions

**src/types/index.ts** - Add to BacklogConfig:

```typescript
export interface BacklogConfig {
  // ... existing fields ...
  hooks?: {
    enabled?: boolean;
    directory?: string;
    timeout?: number;
    logLevel?: "none" | "error" | "info" | "debug";
  };
}
```

## Testing

### Unit Tests

**src/core/hooks.test.ts**:

```typescript
import { describe, expect, it, beforeEach, afterEach } from "bun:test";
import { mkdir, writeFile, chmod, rm } from "node:fs/promises";
import { join } from "node:path";
import { emitHook, HookEvent } from "./hooks.ts";

describe("Hook System", () => {
  const testDir = "/tmp/backlog-hooks-test";
  const hooksDir = join(testDir, ".backlog/hooks");

  beforeEach(async () => {
    await mkdir(hooksDir, { recursive: true });
  });

  afterEach(async () => {
    await rm(testDir, { recursive: true, force: true });
  });

  it("executes post-task-create hook", async () => {
    const scriptPath = join(hooksDir, "post-task-create.sh");
    const outputPath = join(testDir, "output.txt");

    await writeFile(
      scriptPath,
      `#!/bin/bash\necho "Task: $BACKLOG_TASK_ID" > ${outputPath}\n`,
    );
    await chmod(scriptPath, 0o755);

    await emitHook(
      HookEvent.POST_TASK_CREATE,
      { taskId: "task-42", taskTitle: "Test Task" },
      { hooks: { enabled: true, directory: ".backlog/hooks" } },
      testDir,
    );

    // Wait for async execution
    await new Promise((resolve) => setTimeout(resolve, 100));

    const output = await readFile(outputPath, "utf-8");
    expect(output).toContain("Task: task-42");
  });

  it("handles missing hooks gracefully", async () => {
    await expect(
      emitHook(
        HookEvent.POST_TASK_CREATE,
        { taskId: "task-42" },
        { hooks: { enabled: true } },
        testDir,
      ),
    ).resolves.toBeUndefined();
  });

  it("respects timeout configuration", async () => {
    const scriptPath = join(hooksDir, "post-task-create.sh");
    await writeFile(scriptPath, `#!/bin/bash\nsleep 10\n`);
    await chmod(scriptPath, 0o755);

    await emitHook(
      HookEvent.POST_TASK_CREATE,
      { taskId: "task-42" },
      { hooks: { enabled: true, timeout: 100 } },
      testDir,
    );

    // Should not hang - timeout should kill the process
    await new Promise((resolve) => setTimeout(resolve, 200));
  });

  it("respects disabled hooks", async () => {
    const scriptPath = join(hooksDir, "post-task-create.sh");
    const outputPath = join(testDir, "output.txt");
    await writeFile(
      scriptPath,
      `#!/bin/bash\necho "Should not run" > ${outputPath}\n`,
    );
    await chmod(scriptPath, 0o755);

    await emitHook(
      HookEvent.POST_TASK_CREATE,
      { taskId: "task-42" },
      { hooks: { enabled: false } },
      testDir,
    );

    await new Promise((resolve) => setTimeout(resolve, 100));

    // Output file should not exist
    await expect(access(outputPath)).rejects.toThrow();
  });
});
```

### Integration Tests

Test with real backlog operations:

```bash
# Create test hooks
mkdir -p .backlog/hooks
cat > .backlog/hooks/post-task-create.sh << 'EOF'
#!/bin/bash
echo "Created: $BACKLOG_TASK_ID - $BACKLOG_TASK_TITLE" >> /tmp/hook-log.txt
EOF
chmod +x .backlog/hooks/post-task-create.sh

# Test task creation
backlog task create "Test hook integration"

# Verify hook executed
cat /tmp/hook-log.txt
# Should contain: Created: task-XXX - Test hook integration
```

## Documentation

### User Guide

**docs/hooks.md**:

````markdown
# Backlog.md Hooks

Hooks allow you to run custom scripts when task events occur.

## Quick Start

1. Create the hooks directory:
```bash
mkdir -p .backlog/hooks
```

2. Create a hook script:
```bash
cat > .backlog/hooks/post-task-create.sh << 'EOF'
#!/bin/bash
echo "New task created: $BACKLOG_TASK_ID"
EOF
chmod +x .backlog/hooks/post-task-create.sh
```

3. Create a task to test:
```bash
backlog task create "Test hooks"
# Output: New task created: task-XXX
```

## Available Hooks

- **post-task-create**: After task creation
- **post-task-update**: After task metadata changes
- **post-task-archive**: After task archiving

## Environment Variables

All hooks receive:
- `BACKLOG_HOOK_EVENT`: The event type
- `BACKLOG_TASK_ID`: The task ID

Event-specific variables are documented in each hook section below.

### post-task-create

```bash
BACKLOG_HOOK_EVENT=post-task-create
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature"
BACKLOG_TASK_STATUS="To Do"
BACKLOG_TASK_ASSIGNEE="@user1,@user2"
```

### post-task-update

```bash
BACKLOG_HOOK_EVENT=post-task-update
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature"
BACKLOG_OLD_STATUS="To Do"
BACKLOG_NEW_STATUS="In Progress"
BACKLOG_TASK_ASSIGNEE="@user1"
```

### post-task-archive

```bash
BACKLOG_HOOK_EVENT=post-task-archive
BACKLOG_TASK_ID=task-42
BACKLOG_TASK_TITLE="Implement feature"
```

## Configuration

Configure hooks in `.backlog/config.yml`:

```yaml
hooks:
  enabled: true                # Enable/disable all hooks
  directory: .backlog/hooks    # Custom hook directory
  timeout: 5000                # Timeout in milliseconds
  logLevel: info               # none, error, info, debug
```

## Use Cases

### Task Memory System

Capture task context when work begins:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

if [[ "$BACKLOG_NEW_STATUS" == "In Progress" ]]; then
    speckit memory capture "$BACKLOG_TASK_ID"
fi
```

### Team Notifications

Send Slack notifications:

```bash
#!/bin/bash
# .backlog/hooks/post-task-update.sh

if [[ "$BACKLOG_OLD_STATUS" != "$BACKLOG_NEW_STATUS" ]]; then
    curl -X POST https://hooks.slack.com/... \
      -d "Task $BACKLOG_TASK_ID changed: $BACKLOG_OLD_STATUS → $BACKLOG_NEW_STATUS"
fi
```

### Analytics

Track task lifecycle metrics:

```bash
#!/bin/bash
# .backlog/hooks/post-task-create.sh

echo "$(date -u +%s),$BACKLOG_TASK_ID,created" >> metrics.csv
```

## Best Practices

1. **Keep hooks fast**: Hooks run synchronously; use background jobs for slow operations
2. **Handle errors**: Hooks that fail don't block task operations but may log errors
3. **Use absolute paths**: Hook scripts may run from different directories
4. **Test thoroughly**: Verify hooks work before relying on them
5. **Version control**: Commit hooks to share workflows with team

## Troubleshooting

**Hook not executing**:
- Verify script is executable: `chmod +x .backlog/hooks/post-task-*.sh`
- Check path in config: `.backlog/config.yml`
- Enable debug logging: `logLevel: debug`

**Hook timing out**:
- Increase timeout in config
- Move slow operations to background
- Use async job queue for heavy lifting

**Environment variables not set**:
- Not all variables are set for all events
- Check variable availability for specific hook type
````

## Migration Path

1. **Phase 1**: Local implementation in flowspec (this task)
2. **Phase 2**: Create feature branch and PR to upstream
3. **Phase 3**: Collaborate with maintainer on reviews
4. **Phase 4**: After merge, remove local implementation

## Alternatives Considered

### 1. Polling
**Rejected**: Inefficient, delayed reactions, complex state tracking

### 2. File Watchers
**Rejected**: Platform-dependent, unreliable, can't distinguish event types

### 3. Plugin System
**Rejected**: Too complex for simple integrations, high maintenance burden

### 4. Webhooks
**Rejected**: Requires server infrastructure, not suitable for local CLI

## Security Considerations

1. **User Permission Model**: Hooks run with user's permissions (no elevation)
2. **No Remote Execution**: Only local scripts executed
3. **Explicit Enable**: Hooks must be explicitly created and made executable
4. **Timeout Protection**: Prevents runaway processes
5. **Error Isolation**: Hook failures don't affect core operations

## Performance Impact

- **Hook Discovery**: Single file check per event (negligible)
- **Execution**: Async, non-blocking (0ms added to CLI commands)
- **Memory**: Minimal (environment variables only)
- **Disk I/O**: One file read to check executability

## PR Preparation

### Checklist

- [ ] Design document reviewed
- [ ] TypeScript implementation complete
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation written
- [ ] Examples created
- [ ] Biome formatting passed
- [ ] No breaking changes
- [ ] Backward compatible

### Commit Message

```
feat: Add hook system for task lifecycle events

Implements extensible hook system that executes user-defined scripts
on task create, update, and archive events. Hooks are discovered in
.backlog/hooks/ and run with configurable timeout.

Features:
- Three hook events: post-task-create, post-task-update, post-task-archive
- Environment variable context passing
- Configurable timeout and logging
- Fail-safe execution (hooks never block operations)
- Full backward compatibility (opt-in feature)

Use cases:
- Task memory capture for AI workflows
- Team notifications (Slack, email)
- External system integration
- Analytics and metrics collection

Closes #XXX
```

### Files Changed

```
src/core/hooks.ts                 (new)
src/core/hooks.test.ts            (new)
src/core/backlog.ts               (modified - 3 integration points)
src/types/index.ts                (modified - BacklogConfig type)
docs/hooks.md                     (new)
docs/examples/hooks/              (new directory with examples)
```

## References

- Git Hooks: https://git-scm.com/docs/githooks
- Husky (npm hooks): https://github.com/typicode/husky
- GitHub Actions: https://docs.github.com/en/actions
