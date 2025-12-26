# CORE MISSION:

if using vibe or spec driven development we MUST log key events, decisions, actions and we MUST make the spec + workflow system be flexible (by user changing it)

this is for our Inner-Loop but we should be aware of both Inner & Outer Loop in detail

# FLEXIBLE THINGS:

ok lets work out how we think about what our goals are.
agent, prompt and flowspec (workflow updates ) along with constitution and customization.  must be easy. (and we are going to let user edit these files with falcondev/workflow-editor ) so the system we build must be flexibe (and can't over scrutinize prompts at CICD time in terms of changing)
skills also are part of what needs to be flexible. 

# THINGS ALWAYS REQUIRED:

the things that stay always in our @docs/flowspec-loop.md (READ THIS)

## LOGGING 
(logging decision, events ),  outputs of steps producing some artifact.  

## BACKLOG SYSTEM

keeping backlog.md / beads up to date, and accurate thru the process 

## MEMORY SYSTEM

the task memory system.  but always track and save task state and keep agent aware of losing focus (across sessions, across time, etc). 

# RIGOR RULES
must be kept intact and documented better

# features MUST work across tools
claude code + github copilot must have same agents, prompts, mcp, /flow commands acvailable 

## Commands

there are a few key /flow commands that don't have to be part of the workflow but are critical!  (disconnected ad hoc commands)
they are:

/flow:submit-n-watch-pr -> get feedback from other agent (copilot or other) and iterate til good
/flow:timed-task - given some rules and time and a branch produce outcome.
/flow:refactor - when we need to take a full and complete refactor loop.


# Inner Loop 


Default Flowspec. (the development look) - using specs & artifacts to build quality.  flowspec and falcondev are our inner loop

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           FLOWSPEC INNER LOOP COMMAND REFERENCE                  │
├──────────────────┬───────────────┬──────────────────┬────────────────────────────┤
│     COMMAND      │  INPUT        │  OUTPUT Artifact │     PRIMARY AGENTS         │
├──────────────────┼───────────────┼──────────────────┼────────────────────────────┤
│ /flow:specify    │ To Do         │ A Spec           │ PM Planner                 │  
│ /flow:plan       │ Spec          │ Arch Docs        │ Architect, Platform Eng    │
│ /flow:implement  │ Spec & Arch   │ Working solution │ Frontend/Backend Engineers │
│ /flow:validate   │ PR            │ Merged           │ QA, Security Engineers     │
└──────────────────┴───────────────┴──────────────────┴────────────────────────────┘
```


-----

see @docs/flowspec-loop.md for outerloop and @docs/Inner-Outer-Loop.md for how it pertains to DevSecOps and CI/CD