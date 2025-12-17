

# task setup hygiene
- must have a clear and documented plan of action.  (if we dont then ask)
- must plan inter task dependencies first (to plan task order chain)
- must have clear and testable acceptance criteria.  
- must use sub agents as much as possible (in parallel)
- must use git worktree with matching branch name
- branch naming must include hostname / task-# / slug-description
- all decisions made must get logged into jsonl format (with traceability to task)
- use backlog for human tasks, and always link to beads and use beads to and things off to agentic task lists.
- when progressing thru workflow the agent MUST always track and know what comes next when one step completes (be specifc in task of current flow status and whats next)

# task freeze - or push. (add task freeze /flow:freeze comamnd )
- must continuously update task memory with key facts / things to know specific on task
- need to keep the repo (remote) up to date with code + facts
- make sure code is in a working state when freeze, but doesn't have to be complete

# task validation
- always run /flow:validate on all aspects of the work
- must have traceability of all decisions in jsonl, clear documentation, and passing tests
- always lint code and perform SAST
- always check coding style + rules
- always check that every CI will pass
- always rebase from main so we have ZERO merge conflicts
- ensure that acceptance criteria are met
- must update task status as we go ( a PR must include task updates ) 
- must clean up beads statuses

# task push
- push a PR
- ensure that DCO + all CI fails - if not fix it (on same PR)
- wait for copilot to provide comments
- review and fix each comment -in a new branch ( adding -v2 -v3 etc )
- when ready for a new PR (close old PR and push new one with updated branch)
- repeat this process until we have zero copilot comments. (then its ready for human review)