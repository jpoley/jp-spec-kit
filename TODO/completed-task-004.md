

# Goal 

Understand and define which Agents are part of the Inner Loop vs Outer Loop (for documentation). follow these documents in detail for the correct loop.

- docs/reference/inner-loop.md 
- docs/reference/outer-loop.md

update the agents and documentation accordingly.

# inner loop
- all planning agents
- all implementation agents

## MUST HAVES Inner Loop

- MUST do some testing but have options to build as much of CI before commit as possible.
- MUST have some validation tests / contracts for specific key boundaries / interfaces.

# outer loop 
- sre agent
- operations manager

## MUST HAVES Outer loop

-  must consist of a complete github actions process for CI to build scan and sign the artifact. 

- the CD step to promote it upon testing + approvals.

- create .stack specific CI steps that need to work with the stack used (but don't over populate the .github/workflows folder by default) 

- a specific Stacks GitHub Actions should only be put in once the stack is validated thru the correct process. (before implement)
