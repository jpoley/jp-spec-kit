# Failure Learnings

This document tracks significant implementation failures and the lessons learned. Each failure is documented to prevent repeating the same mistakes.

---

## Failure #1: Hardcoded Meta-Workflows (December 2024)

### What I Got Completely Wrong

1. ❌ **Misunderstood the objective** - Created hardcoded "Research/Build/Run" meta-workflows instead of USER-CUSTOMIZABLE orchestration
2. ❌ **Followed flawed analysis** - analysis-flowspec.md suggests consolidation, but that defeats the purpose (same as spec-kit)
3. ❌ **Removed functionality** - Didn't include /flow:submit-n-review-pr which is CRITICAL
4. ❌ **Ignored rigor rules** - No logging, ADRs, or constitution enforcement
5. ❌ **Wrong integration** - Used bash scripts instead of MCP
6. ❌ **Security vulnerabilities** - bash eval(), curl pipes
7. ❌ **Skipped validation** - Didn't run CI/CD checks before PR

### The Fundamental Mistake

I tried to REPLACE the commands with 3 hardcoded ones. That's the OPPOSITE of what "flexible orchestration" means.

### What I Should Have Done

1. **Read flowspec-loop.md FIRST** - It defines the core mission: 4 commands ARE flowspec
2. **Understood Inner vs Outer Loop** - Flowspec = Inner Loop ONLY (Outer Loop = falcondev)
3. **Recognized "glue" means orchestration** - NOT hardcoded workflows, but flexible user-defined sequences
4. **Preserved ALL commands** - Add orchestration ON TOP, don't replace
5. **Enforced rigor rules** - Logging, ADRs, constitution from day one
6. **Used MCP** - Not bash scripts for backlog integration
7. **Fixed security** - No eval(), no curl pipes
8. **Validated before PR** - Run all CI/CD checks locally first

### Key Lessons

**Mission-Critical Documents:**
- flowspec-loop.md defines THE MISSION (4 core commands)
- Inner/Outer Loop distinction is fundamental
- "Glue that loosely binds" = orchestration layer, NOT consolidation

**Architecture Principles:**
- Never remove existing functionality
- Add layers ON TOP, don't replace
- User customization ≠ hardcoded simplification
- Flexible = user-editable, not fewer options

**Process Requirements:**
- Always use MCP for backlog (never bash)
- Always enforce rigor rules (logging, ADRs, constitution)
- Always validate with CI/CD before PR
- Always check security (no eval, no curl pipes)

---

*Add new failures below with incrementing numbers and clear lessons learned.*
