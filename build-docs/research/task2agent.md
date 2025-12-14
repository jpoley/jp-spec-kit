# Multi-Agent Task Assignment & Dispatch in `flowspec` (Single-Block Version)

This is a self-contained design and implementation sketch for:

- Assigning specific tasks to specific coding agents (e.g. `task-001` and `task-002` → `@claude`, `task-003` and `task-004` → `@gemini`), and having this visible in Backlog.md.
- Adding a dispatch mechanism that:
  - Reads backlog tasks
  - Figures out which agent should handle each one
  - Spawns the right agent tool (Claude, Gemini, etc.) with an appropriate prompt and repo context
  - Optionally creates a branch and opens a PR when the work is done

The key question you asked: “Is it only the dispatch service that’s missing?”  
Short answer: the dispatch runtime is the main missing piece, but you also want a tiny bit of metadata wiring and a small agent-registry config file to make it clean.

---

## 1. What Already Works Today

### 1.1 Backlog and Task Representation

You already have:

- Backlog.md as the task manager, with tasks stored as markdown files such as:
    backlog/task-001 - Implement OAuth.md

- Backlog tasks can contain:
  - Title, description, acceptance criteria
  - Assignee(s)
  - Labels
  - Status (e.g. Todo, In Progress, Done)
  - Priority

Because Backlog.md already supports assignees and labels, you can represent agent ownership today by:

- Assignee: `@claude` or `@gemini`
- Or label: `agent:claude`, `agent:gemini`

This is enough for:

- Filtering in CLI (e.g. list all `@claude` tasks)
- Displaying clearly in board / web UI

So: marking “this task is for @claude, that one is for @gemini” is already solved via existing fields. No core changes needed just to annotate tasks.

---

## 2. What’s Actually Missing

You want a pipeline that goes from:

1. Spec (flowspec) → generated tasks (Backlog.md)
2. Tasks → associated agent (Claude or Gemini)
3. Agent → actual work in the repo
4. Work → branch + PR
5. PR state → task status

The parts that are missing:

1. Agent metadata wiring in the **task generation flow** (so that agent info is attached at creation time, not hacked in later).
2. An **agent registry configuration** (like `agents.yml`) that defines how each logical agent is invoked.
3. A **dispatcher/orchestrator** command that:
   - Reads backlog tasks
   - Picks the correct agent
   - Spawns the appropriate agent CLI with a prompt and repo context
   - Manages git branches, tests, and PRs
   - Syncs status back to Backlog.md

The bulk of the work is in (2) and (3), but (1) makes it much cleaner to use.

---

## 3. Step 1 – Make “Agent Per Task” First-Class

### 3.1 How to Store the Agent Field

Two straightforward patterns:

1. Use assignee as the agent routing:
   - Assignee: `@claude`
   - Assignee: `@gemini`

2. Use a label:
   - Labels: `agent:claude`
   - Labels: `agent:gemini`

Recommended approach:

- Treat assignee as the primary mapping (e.g. `@claude`, `@gemini`).
- Optionally add a label `agent:claude` / `agent:gemini` for clarity and filtering.

This keeps your Backlog.md UX clean and obvious (“assignee looks like a person, but it’s actually a bot/agent”).

### 3.2 Wire Agent Metadata into flowspec Task Generation

Where flowspec converts specs into tasks (e.g. via `/speckit.tasks` or equivalent), extend the template to accept an optional `agent` field.

For each generated task:

- Set Assignee: `@<agent>` if `agent` is defined.
- Optionally add a label `agent:<agent>`.

This can be driven by:

- A config file that maps sections or tags to agents, like:
    backend → claude
    frontend → gemini
    infra → claude
- Or explicit `agent: "claude"` fields inside your spec definitions.

The net effect: tasks come out of the generator already tagged with the right agent, no manual editing required.

---

## 4. Step 2 – Introduce an `agents.yml` Registry

You don’t want to hard-code the behavior for Claude vs Gemini vs others inside your dispatcher. Instead, you define a small registry file in the repo, e.g. `agents.yml`.

Example `agents.yml`:

    agents:
      claude:
        type: "cli"              # could be "cli", "http", "mcp", etc.
        command: ["claude"]      # base command for the agent
        mode: "code"             # e.g. "code", "chat", "task"
        args:
          - "--read-repo"        # example flag; adjust to reality
          - "--no-stream"
        prompt_style: "coding-task"  # optional; lets you choose prompt templates

      gemini:
        type: "cli"
        command: ["gemini"]
        mode: "code"
        args: []
        prompt_style: "coding-task"

This gives you:

- A clean mapping from logical name (claude, gemini) to how to invoke the actual tool.
- The ability to add more tools later (copilot, cursor, openrouter, etc.) without changing dispatch code.

Your dispatcher will:

- Load `agents.yml`
- When it sees a task assigned to `@claude`, it looks up `claude` in `agents.yml` to know which command and flags to use.

---

## 5. Step 3 – Design a `specify dispatch` CLI

Add a new command in flowspec (or a sibling script):

- Name suggestion: `specify dispatch`

### 5.1 Example CLI Usage

Dispatch a specific task:

- `specify dispatch task-001`

Dispatch tasks by agent and status:

- `specify dispatch --agent claude --status todo --limit 1`
- `specify dispatch --agent gemini --status todo --limit 3`

Dispatch by label:

- `specify dispatch --label agent:claude --status todo`

Helpful flags:

- `--dry-run` – print what you would do (which tasks, which agent, which branch) without executing anything.
- `--no-git` – call the agent but do not create branches or PRs.
- `--branch-prefix` – e.g. `agent/` so branch becomes `agent/claude/task-001-implement-oauth`.
- `--update-status` – automatically adjust Backlog.md status.

### 5.2 Dispatcher Responsibilities

For each task selected by the command:

1. Read task metadata:
   - Use Backlog.md CLI in some machine-readable format, for example:
        backlog task show task-001 --plain
   - Parse out:
     - task-id
     - title
     - description
     - acceptance criteria
     - assignee(s)
     - labels
     - status

2. Determine the agent:
   - If assignee is `@claude` → agent `claude`.
   - If assignee is `@gemini` → agent `gemini`.
   - If no assignee, fall back to label `agent:claude` or `agent:gemini`.
   - If still unknown, either:
     - Fail with a clear error (“no agent assigned”).
     - Or use a default agent specified via CLI or config.

3. Optionally create a git branch:
   - Branch naming pattern:
        agent/<agent>/<task-id>-slug
   - Example:
        agent/claude/task-001-implement-oauth

4. Build the agent prompt:
   - Prepare a structured prompt including:
     - Task ID and title
     - Full description
     - Acceptance criteria
     - Any constraints or coding standards
     - Instructions to:
       - Work only within the repo
       - Implement code following the acceptance criteria
       - Prepare the changes so they can be committed and pushed
       - Reference the task ID in commit messages and/or PR

   - You can store this as a template in the repo, like `dispatch-prompt-template.md`, and fill in placeholders.

5. Invoke the agent CLI:
   - From `agents.yml`, get:
     - `command` (e.g. `["claude"]`)
     - `args` (e.g. `["code", "--read-repo"]`)
   - Build the command line, and feed it your constructed prompt. Depending on the tool:
     - Pass prompt as an argument (e.g. `--message "<prompt>"`)
     - Or write prompt to stdin and have the CLI read from stdin.

6. Post-agent actions (git + tests + PR):
   - Run tests if appropriate (`npm test`, `go test ./...`, etc.).
   - If tests pass:
     - Check `git status` for modifications.
     - Commit with a message like:
          task-001: Implement OAuth flow
     - Push branch to origin.
     - Use `gh pr create` (or direct API) to open a PR:
          gh pr create --title "task-001 - Implement OAuth" --body "Implements task-001" --head agent/claude/task-001-implement-oauth

   - If tests fail:
     - You can:
       - Still open a PR and mark failing status via labels / description.
       - Or skip PR and log the failure somewhere, updating the task with a “failed” note.

7. Update task status in Backlog.md:
   - When dispatcher starts the task:
        backlog task edit task-001 --status "In Progress"
   - After opening the PR:
        backlog task edit task-001 --status "Review" --label "pr:<number-or-url>"
   - When the PR merges (could be handled separately by a webhook or a poller):
        backlog task edit task-001 --status "Done"

This closes the loop: task lifecycle is reflected in the backlog as the code moves from work → review → merged.

---

## 6. Step 4 – Implementation Skeleton

You could implement the dispatcher in Python (or Go, TS, whatever). In Python, a minimal structure might be:

- `load_agents_config(path="agents.yml")`
- `list_or_get_tasks(args)`  (filters by id, agent, label, status)
- `resolve_agent(task)`      (assignee/label → agent name)
- `create_branch(task, agent_name)`
- `build_prompt(task, agent_name)`
- `run_agent(agent_config, prompt, workdir)`
- `run_tests()`
- `commit_and_push(task, agent_name, branch_name)`
- `create_pr(task, branch_name) -> pr_url`
- `update_task_status(task, new_status, extra_info)`

Flow for `specify dispatch task-001`:

1. Parse CLI args → `task_ids = ["task-001"]`
2. For each `task_id`:
   - `task = read_task_metadata("task-001")`
   - `agent_name = resolve_agent(task)`  (e.g. `claude`)
   - `agent_config = agents[agent_name]`
   - `branch_name = create_branch(task, agent_name)` (unless `--no-git`)
   - `prompt = build_prompt(task, agent_name)`
   - `run_agent(agent_config, prompt, workdir=".")`
   - `run_tests()`
   - `commit_and_push(task, agent_name, branch_name)`
   - `pr_url = create_pr(task, branch_name)`
   - `update_task_status(task.id, "Review", {"pr_url": pr_url})`

You can start with `--dry-run` mode that just prints all of the above decisions so you can tweak the behavior before wiring in the actual `claude` / `gemini` CLIs and git commands.

---

## 7. Step 5 – Status Feedback Model

To keep everything easy to reason about inside Backlog.md:

- Use a simple status model:
  - `Todo`
  - `In Progress`
  - `Review`
  - `Done`
  - (Optional) `Failed` for agent or CI failures

- Use a few stable labels:
  - `agent:claude` / `agent:gemini`
  - `pr:<number>` or `pr:<url>`
  - `ci:failed` / `ci:passed` if you want to track CI results

The dispatcher just updates these fields using Backlog.md’s CLI. The Kanban/board UI will automatically surface the lifecycle without any code changes in the UI.

---

## 8. So, Is It “Only the Dispatch Service”?

Breaking it down:

Already present:
- Backlog.md with assignees and labels.
- A repo structure that can accommodate multiple agents (Claude, Gemini, etc.).
- The ability to manually assign tasks to agent-like assignees (e.g. `@claude`, `@gemini`).

Missing pieces:

1. Small but important template/metadata changes:
   - Extend flowspec’s task generation so that tasks come out with:
     - Assignee: `@claude` / `@gemini` (and possibly label `agent:claude` / `agent:gemini`).

2. An `agents.yml` registry file:
   - Defines how each logical agent is actually invoked (CLI command, args, mode, prompt style).

3. The actual dispatcher/orchestrator:
   - A `specify dispatch` (or equivalent) command that:
     - Reads tasks from Backlog.md
     - Resolves the correct agent
     - Runs that agent with a constructed prompt and repo context
     - Manages git branches and PRs
     - Updates task status and labels

So: it’s not literally “only a dispatch service,” but the **main missing thing is the dispatch/orchestration layer**, plus two relatively small pieces of configuration and template wiring that make agent assignment first-class and predictable.

If you want, the next layer of detail would be:
- A concrete CLI spec for `specify dispatch` (argument table, examples).
- A first-pass Python script for dispatch that you can drop straight into the repo and iterate on.
