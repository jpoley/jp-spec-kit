# Flowspec/Speckit Framework Source & Deployment Audit Prompt

> **Usage:** Run this prompt against the **Flowspec/Speckit source repository** to audit what the framework provides and how completely `init` and `dev-setup` commands deploy it to target projects.

---

## Prompt

```
Perform a comprehensive source-to-deployment audit of the Flowspec/Speckit framework. Analyze what the framework provides vs. what actually gets deployed when users run `specify init` and on this repo `dev-setup`. Generate a detailed report at `./docs/research/framework-deployment-audit.md`.

## Analysis Goals

1. **Inventory the Framework** - What commands, skills, agents, prompts, hooks, workflows, and templates does Flowspec provide?
2. **Trace Deployment Paths** - How do `init` and `dev-setup` deploy each component?
3. **Identify Deployment Gaps** - What framework features are NOT deployed or only partially deployed?
4. **Maximize Utilization** - Recommend changes to ensure all framework tools are available to users

---

## Part 1: Framework Source Inventory

### 1.1 Commands Registry

**Scan for all command definitions:**
- Search `.specify/templates/commands/` recursively for all `.md` files
- Search `.claude/commands/` patterns in framework source
- List each command with: name, description, category, file location

**Build command inventory table:**
| Command | Category | Source Location | Description | Deployed? |
|---------|----------|-----------------|-------------|-----------|

### 1.2 Skills Registry

**Scan for all skill definitions:**
- Search for `SKILL.md` files in framework templates
- Parse YAML frontmatter for `name`, `description`, `trigger` patterns
- Identify skill dependencies and requirements

**Build skills inventory table:**
| Skill | Description | Source Location | Auto-trigger Pattern | Deployed? |
|-------|-------------|-----------------|---------------------|-----------|

### 1.3 Agents Registry

**Scan for all agent definitions:**
- Search for `.agent.md` files in framework source
- Parse agent capabilities and tool access
- Map agent-to-command relationships

**Build agents inventory table:**
| Agent | Description | Source Location | Backed Commands | Deployed? |
|-------|-------------|-----------------|-----------------|-----------|

### 1.4 Prompts Registry

**Scan for all prompt definitions:**
- Search for `.prompt.md` files
- Identify which prompts are stubs vs full content
- Map prompt-to-agent relationships

**Build prompts inventory table:**
| Prompt | Lines | Source Location | Has Agent? | Deployed? |
|--------|-------|-----------------|------------|-----------|

### 1.5 Hooks Registry

**Scan for all hook definitions:**
- Parse `hooks.yaml` configurations
- List trigger events, scripts, and timeout settings
- Check default enabled state

**Build hooks inventory table:**
| Hook | Event | Script | Default Enabled | Deployed? |
|------|-------|--------|-----------------|-----------|

### 1.6 Workflow Definitions

**Analyze workflow configurations:**
- Parse `flowspec_workflow.yml` or equivalent
- List states, transitions, validation modes
- Identify quality gates

### 1.7 Memory Templates

**Scan memory/constitution templates:**
- List all memory file templates
- Identify placeholder patterns (`[PROJECT_NAME]`, `[DATE]`, etc.)
- Check for required vs optional fields

---

## Part 2: Deployment Path Analysis

### 2.1 Init Command Analysis

**Trace what `specify init` does:**
- What files/directories does it create?
- What templates does it copy vs symlink?
- What placeholders does it attempt to fill?
- What interactive prompts does it ask?
- What does it skip or leave as templates?

**Create init deployment map:**
```
Source                           -> Destination                    | Method
.specify/templates/commands/     -> .claude/commands/              | copy/symlink/skip
.specify/templates/skills/       -> .claude/skills/                | copy/symlink/skip
.specify/templates/agents/       -> .github/agents/                | copy/symlink/skip
```

### 2.2 Dev-Setup Command Analysis

**Trace what `dev-setup` does beyond init:**
- What additional configuration does it perform?
- Does it enable hooks that init leaves disabled?
- Does it customize for detected project type?
- What CI/CD templates does it generate?
- What IDE configurations does it set up?

**Create dev-setup deployment map:**
| Component | Init State | Dev-Setup Enhancement | Final State |
|-----------|------------|----------------------|-------------|

### 2.3 Deployment Gap Analysis

**For each framework component, determine:**
- Is it deployed by init? By dev-setup? Neither?
- Is it deployed as template (needs manual customization) or ready-to-use?
- Are there dependencies that must be deployed together?

**Create gap analysis table:**
| Component | Framework Has | Init Deploys | Dev-Setup Deploys | Gap |
|-----------|---------------|--------------|-------------------|-----|

---

## Part 3: Consistency Analysis

### 3.1 Cross-Reference Matrix

**Build alignment matrix across all component types:**

| Command Name | Has Skill? | Has Agent? | Has Prompt? | Fully Deployed? |
|--------------|------------|------------|-------------|-----------------|

### 3.2 Orphan Detection

**Find orphaned components:**
- Agents without matching prompts
- Prompts without matching agents (when agent is expected)
- Skills referenced but not deployed
- Hooks with missing script files

### 3.3 Stub Detection

**Find incomplete deployments:**
- Prompts with < 10 lines (likely stubs)
- Templates with unresolved placeholders
- Config files with default/empty values

---

## Part 4: Recommendations

### 4.1 Init Improvements

**What should init do that it currently doesn't:**
- Components to deploy that are currently skipped
- Placeholders to auto-fill from detected project info
- Symlinks vs copies for maintainability
- Interactive prompts to add

### 4.2 Dev-Setup Improvements

**What should dev-setup do that it currently doesn't:**
- Hooks to enable based on project type
- CI/CD templates to generate
- IDE settings to configure
- Project-specific customizations

### 4.3 Framework Improvements

**Source framework improvements needed:**
- Missing component definitions
- Inconsistent naming conventions
- Documentation gaps
- Dependency declarations

---

## Part 5: Validation Commands

### 5.1 Framework Source Validation

```bash
# Count all framework components
echo "=== Framework Source Inventory ==="
echo "Commands: $(find .specify/templates/commands -name '*.md' 2>/dev/null | wc -l)"
echo "Skills: $(find .specify/templates/skills -name 'SKILL.md' 2>/dev/null | wc -l)"
echo "Agents: $(find .specify/templates/agents -name '*.agent.md' 2>/dev/null | wc -l)"
echo "Prompts: $(find .specify/templates/prompts -name '*.prompt.md' 2>/dev/null | wc -l)"
echo "Hooks: $(grep -c 'name:' .specify/hooks/hooks.yaml 2>/dev/null || echo 0)"
```

### 5.2 Deployment Validation

```bash
# After init/dev-setup, verify deployment
echo "=== Deployed Components ==="
echo "Commands deployed: $(find .claude/commands -name '*.md' 2>/dev/null | wc -l)"
echo "Skills deployed: $(find .claude/skills -name 'SKILL.md' 2>/dev/null | wc -l)"
echo "Agents deployed: $(find .github/agents -name '*.agent.md' 2>/dev/null | wc -l)"
echo "Prompts deployed: $(find .github/prompts -name '*.prompt.md' 2>/dev/null | wc -l)"

# Check for unresolved placeholders
echo "=== Unresolved Placeholders ==="
grep -r '\[PROJECT' memory/ .specify/memory/ 2>/dev/null || echo "None found"
grep -r '\[DATE\]' memory/ .specify/memory/ 2>/dev/null || echo "None found"
grep -r '\[LANGUAGE' memory/ .specify/memory/ 2>/dev/null || echo "None found"

# Check hook status
echo "=== Hook Status ==="
grep -E 'enabled:\s*(true|false)' .specify/hooks/hooks.yaml 2>/dev/null

# Check for stub prompts (< 10 lines)
echo "=== Potential Stub Prompts ==="
for f in .github/prompts/*.prompt.md; do
    lines=$(wc -l < "$f" 2>/dev/null || echo 0)
    [ "$lines" -lt 10 ] && echo "$f: $lines lines"
done
```

### 5.3 Consistency Validation

```bash
# Agent-Prompt alignment
echo "=== Agent-Prompt Alignment ==="
echo "Agents:"
ls .github/agents/*.agent.md 2>/dev/null | xargs -n1 basename | sed 's/.agent.md//' | sort
echo "Prompts:"
ls .github/prompts/*.prompt.md 2>/dev/null | xargs -n1 basename | sed 's/.prompt.md//' | sort
echo "Differences:"
diff <(ls .github/agents/*.agent.md 2>/dev/null | xargs -n1 basename | sed 's/.agent.md//' | sort) \
     <(ls .github/prompts/*.prompt.md 2>/dev/null | xargs -n1 basename | sed 's/.prompt.md//' | sort) || echo "None"
```

---

## Output Format

Generate report at `./docs/research/framework-deployment-audit.md` with:

1. **Executive Summary**
   - Framework component counts (source)
   - Deployment completeness percentage
   - Critical gaps identified

2. **Framework Inventory** (Part 1 tables)
   - Commands, Skills, Agents, Prompts, Hooks, Workflows

3. **Deployment Analysis** (Part 2)
   - Init deployment map
   - Dev-setup enhancement map
   - Gap analysis

4. **Consistency Report** (Part 3)
   - Cross-reference matrix
   - Orphaned components
   - Stub detections

5. **Recommendations** (Part 4)
   - Prioritized init improvements
   - Prioritized dev-setup improvements
   - Framework source improvements

6. **Validation Results** (Part 5)
   - All validation command outputs
   - Pass/fail status for each check

---

## Key Questions This Audit Answers

### Framework Questions
1. How many total commands/skills/agents/prompts/hooks does Flowspec provide?
2. What naming conventions are used across component types?
3. Are there documented dependencies between components?
4. What placeholder patterns require user input?

### Deployment Questions
5. What percentage of framework components are deployed by init?
6. What additional components does dev-setup deploy?
7. Which components are never auto-deployed (require manual setup)?
8. Are deployed files copies or symlinks to source?

### Gap Questions
9. Which agents have no matching prompts?
10. Which prompts are stubs that need full content?
11. Which hooks are defined but disabled by default?
12. Which skills exist in templates but aren't deployed?

### Improvement Questions
13. What should init auto-fill that it currently doesn't?
14. What should dev-setup enable that it leaves disabled?
15. How can single-source-of-truth be maintained (symlinks)?
16. What project-type-specific customizations are needed?
```

---

## Comparison: This Prompt vs Installed Audit

| Aspect | Framework Audit (This) | Installed Audit |
|--------|------------------------|-----------------|
| **Target** | Flowspec source repo | Project with Flowspec installed |
| **Goal** | Inventory framework capabilities | Verify installation completeness |
| **Output** | Framework inventory + deployment gaps | Issue list with fixes |
| **Focus** | What framework provides | What project is missing |
| **Recommendations** | Improve init/dev-setup | Fix specific project issues |

## When to Use Each

- **This prompt (Framework Audit):** Run against Flowspec source to improve the framework and its deployment commands
- **Installed Audit:** Run against a project after `specify init` to find and fix installation gaps

## Expected Deliverable

The audit will produce:

```
docs/research/framework-deployment-audit.md
├── Executive Summary
│   ├── Source component counts
│   ├── Deployment percentages
│   └── Critical gap count
├── Framework Inventory
│   ├── Commands table
│   ├── Skills table
│   ├── Agents table
│   ├── Prompts table
│   └── Hooks table
├── Deployment Analysis
│   ├── Init deployment map
│   ├── Dev-setup enhancement map
│   └── Gap analysis matrix
├── Consistency Report
│   ├── Cross-reference matrix
│   ├── Orphan list
│   └── Stub list
├── Recommendations
│   ├── Init improvements (prioritized)
│   ├── Dev-setup improvements (prioritized)
│   └── Framework improvements
└── Validation Results
    └── All command outputs with status
```
