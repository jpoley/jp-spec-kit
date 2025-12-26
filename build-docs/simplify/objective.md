

we need to make flowspec more usable, less complicated, and more flexible.

it would be amazing if we let users completely customize their flow steps (with the workflow editor in falcondev )
this means we have a "default active" flowspec file but support customization of it.

it should simply be the glue that loosely binds the steps.

what are inputs: the objective / goal / feature
what are outputs: maybe an ARD or a Spec, or Code, or a Commit  (some artifact)
who does the work: which agent or squad of agents
what rules do the operate by: generally the constitution, how to log jsonl, say in branch, stay on task etc.
how much autonomy: complete thru to task completion (timed) or til step is done. 

this needs to be flexible / simple and work across tools:
the 4 most important coding tools in this order are:
1. Claude Code
2. GitHub Copilot (all variants)
3. Cursor
4. Gemini 


what good looks like:

if vibing, we still get decision & event logs in jsonl output (in .logs/decisions and .logs/events) and ADR documents for key architectural decisions made (also noting constraints and one way doors chosen) without ANY interaction.

if spec-ing - flexible setup of when we stop for guidance, and what are key artifacts + steps used (with prompts and agents to be customized). being under control

how do we do this while tracking (in backlog.md and beads) all things ti keep them visible. (and accurate)

what horrible flow looks like
@docs/horrible-flow.png