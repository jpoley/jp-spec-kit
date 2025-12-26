

# Flowspec Command Structure and Simplified Workflows

## Existing Flowspec Command Structure

Flowspec’s current design defines a distinct command for each phase of a spec-driven development workflow. Each command (prefixed with `/flow`) corresponds to a specific stage and state transition in the feature lifecycle[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aassess%20%20%20%E2%94%82,%E2%94%82%20Architect%2C%20Platform%20Eng%20%E2%94%82)[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent):

- **`/flow:init`** – _(Project initialization)_ Establishes project “constitution” and principles. This one-time setup seeds high-level guidelines but is not tied to a specific feature flow.
    
- **`/flow:assess`** – _(Assessment)_ Scores the feature’s complexity across dimensions, helping decide if a _Simple_, _Medium_, or _Full_ workflow is needed. It does not change the task’s state (informational output only)[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aassess%20%20%20%E2%94%82,%E2%94%82%20Architect%2C%20Platform%20Eng%20%E2%94%82).
    
- **`/flow:specify`** – _(Specification)_ Turns a new feature task from “To Do” into a **Specified** state by generating requirements documentation (e.g. PRD and functional specs)[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aspecify%20%20%E2%94%82%20To,%E2%94%82%20Architect%2C%20Platform%20Eng). This is akin to a product management step (handled by a “PM Planner” agent).
    
- **`/flow:research`** – _(Research & validation)_ An **optional** deep-dive that takes a Specified feature to **Researched** state by gathering additional context – e.g. competitive analysis or technical research – using specialized research/validation agents[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aspecify%20%20%E2%94%82%20To,%E2%94%82%20Architect%2C%20Platform%20Eng).
    
- **`/flow:plan`** – _(Technical planning)_ Moves a Specified (or Researched) task to **Planned** state by producing technical design artifacts – detailed technical specs, architecture decision records, and design docs[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aresearch%20%E2%94%82%20Specified%20,%E2%94%82%20Frontend%2FBackend). This is essentially an architecting phase.
    
- **`/flow:implement`** – _(Implementation)_ Advances a Planned feature to **In Progress** by generating the actual code, unit tests, and related documentation[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent). (This uses coding agents acting as “Frontend/Backend Engineers”.)
    
- **`/flow:validate`** – _(Validation)_ Takes an In Progress feature to **Validated** state by running QA checks, generating test reports, and performing security scans[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent). It ensures the implemented code meets acceptance criteria before deployment.
    
- **`/flow:operate`** – _(Operationalization)_ Final stage that transitions a Validated feature to **Deployed**. It produces operational artifacts like deployment configs and runbooks, and marks the task “Done”[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent). This is analogous to an SRE/deployment step.
    

These commands are tightly integrated with a task tracking system (backlog.md and “beads”). Each `/flow:*` invocation not only uses AI to produce the phase’s deliverables, but also updates the task’s status in the backlog and commits the artifacts in the proper format[github.com](https://github.com/jpoley/flowspec#:~:text=,agents%20that)[github.com](https://github.com/jpoley/flowspec#:~:text=work%20but%20do%20not%20integrate,integrated%20workflow%20with%20task%20tracking). The design is rigorous and comprehensive – ensuring that for every feature, all steps from specification to deployment are documented and tracked. However, it also means the user must navigate **7 different phase commands** (plus `init`), and understand their ordering and prerequisites (e.g. you must `/flow:specify` before `/flow:plan`, etc.). This granularity, while thorough, introduces some **complexity and duplication** in both usage and implementation:

- Several steps overlap or are optional. For example, both **specification and research** deal with gathering knowledge before coding; in practice not every feature needs a separate research step. Similarly, **assessment** is a preliminary advisory step – helpful, but not producing a new artifact or state change.
    
- The codebase must support multiple adjacent states (Specified vs. Researched) and branch logic depending on whether a step was skipped. (Indeed, `/flow:plan` accepts input in Specified _or_ Researched state[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aresearch%20%E2%94%82%20Specified%20,%E2%94%82%20Frontend%2FBackend).) This adds complexity to state management.
    
- There appear to be legacy or parallel ways to run flowspec without the integrated `/flow` commands. The documentation notes that older spec-kit style commands “work but do not integrate with backlog.md” and recommends using `/flow:*` for full task tracking[github.com](https://github.com/jpoley/flowspec#:~:text=work%20but%20do%20not%20integrate,integrated%20workflow%20with%20task%20tracking). Maintaining both modes is technical debt that complicates the tool.
    

In summary, the existing command structure covers the full software development lifecycle with dedicated commands for each phase. This ensures completeness, but at the cost of **verbosity and potential over-engineering**. We can improve this by consolidating the functionality into three broader workflows – **Research**, **Build**, and **Run** – which map to logical high-level stages and simplify the user experience.

## Research Workflow

**Objective:** The **Research** workflow encompasses all upfront analysis and design activities needed to go from an idea to a well-defined, build-ready plan. Its goal is to clearly answer _“What are we building and why, and how will we approach it?”_ before any code is written. This phase ensures that requirements are understood and the solution is planned out.

**Mapped Existing Commands:** The Research workflow would unify the functionality of several current commands that deal with pre-implementation work:

- `/flow:assess` – Complexity scoring and workflow decision (Simple/Medium/Full) for the feature.
    
- `/flow:specify` – Requirements specification (e.g. producing the PRD and functional spec) for the feature.
    
- `/flow:research` – (If needed) In-depth research or validation of requirements, edge cases, or domain knowledge.
    
- `/flow:plan` – Technical design and planning (producing technical spec, architecture decisions, etc.).
    
- _(Optionally, even `/flow:init` – establishing project principles – falls under upfront planning context, though it’s a one-time project setup.)_
    

By grouping these, the **Research workflow** handles everything from initial feature definition through architectural design. In practice, that could mean a single command (or guided sequence) that runs through specification and planning steps in one go, only performing the deeper research or complexity scoring if warranted. For example, a simplified `flowspec research "Build a new user settings page"` could internally perform the specify → (optional research) → plan steps as appropriate, instead of requiring the user to invoke each `/flow:` command in sequence.

**Improvements Through Simplification:** This consolidation would significantly streamline the early project stages:

- **Clarity & Ease of Use:** Developers no longer need to remember four or five separate commands and their order. A single **Research** workflow naturally covers “define and design” tasks. This reduces cognitive load and chances of error (e.g. skipping a needed step). It aligns with how developers think: first figure out **what** to build, before moving to how to build it.
    
- **Automated Flow Control:** The tool can internally decide which sub-steps to run based on context. For instance, it could automatically run a complexity assessment and decide to generate either a brief design or a full spec package. This eliminates the manual trigger of `/flow:assess` and interpretation of its results by the user – the workflow itself can branch to _Light_ or _Full_ mode as needed.
    
- **Reduced Duplication in Code:** Many of these commands share similar operations under the hood: reading the backlog/task state, feeding context to AI agents, writing to docs, and updating the task state. Merging them into one workflow allows reuse of that logic in one place. For example, instead of separate implementations for adding PRD content versus technical specs, a unified flow can call common routines to append to the appropriate docs and commit changes. This consolidation would cut down on repeated code for handling file I/O, version control, and task state transitions for each phase.
    
- **Eliminating Optional-State Overhead:** Currently, having both _Specified_ and _Researched_ states (and two commands to reach them) is an extra granularity that might not be justified for every project. By treating research as an optional sub-step of the broader Research workflow, the model can be simplified – possibly using just a “Designed” state after this workflow. This avoids maintaining multiple near-identical states and the branching logic to handle them. Any insights from research can be folded into the specification or design artifacts directly, rather than tracked as a separate phase.
    
- **Addressing Over-Engineering:** By simplifying upfront workflows, we acknowledge that not every feature needs an exhaustive multi-document treatment. The new structure could allow a **scalable approach**: the Research workflow can be light-weight (quick spec only) or thorough (full spec + research + ADRs) depending on complexity, without the user having to explicitly call extra commands. This adaptability makes the design less rigid. It also makes it easier to maintain the tool – fewer top-level commands and states means fewer points of failure. We also reduce the technical debt of the old spec-kit compatibility: instead of supporting a parallel non-integrated specify/plan process, all users would go through this one Research workflow, ensuring backlog integration every time.
    

## Build Workflow

**Objective:** The **Build** workflow covers the implementation phase – writing the code, tests, and related documentation – and the verification phase – ensuring the code meets quality standards. In short, this workflow’s goal is to turn the approved design into a working, validated product increment. It answers the question _“Are we building it right?”_ by delivering the feature and checking it against acceptance criteria.

**Mapped Existing Commands:** This corresponds to the middle stages of the current process, primarily two commands:

- `/flow:implement` – generating or writing the actual code for the feature (and unit tests, etc.), moving the task to an In Progress state with new source code in `src/`[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent).
    
- `/flow:validate` – running tests, QA checks, and security scans on the implemented feature, resulting in a Validated state if all checks pass[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent).
    

In a combined **Build** workflow, these two steps become part of one continuous phase. The workflow would encompass coding and testing together. For example, a single `flowspec build` command could trigger the code generation and then automatically run the validation suite (rather than requiring the developer to call a separate validate step after coding is done).

**Improvements Through Simplification:** Merging implementation and validation yields a more efficient and robust development process:

- **End-to-End Development in One Step:** Treating “build” as one workflow emphasizes that code is not truly “done” until it’s tested. The tool can generate code and then immediately execute the tests and analysis. This automates what is usually a tight loop anyway – developers write code and then run tests. By integrating `/flow:implement` and `/flow:validate`, we remove the manual gap between them. It ensures that no one forgets to validate, and it can surface issues immediately. For instance, the Build workflow could fail early if tests don’t pass or security checks find issues, prompting the developer to iterate, rather than marking the feature as complete prematurely.
    
- **Streamlined State Management:** In the current model, there are two distinct states (“In Progress” and “Validated”) with an explicit command transition. Under a unified Build workflow, we could simplify this to a single **“Built”** state (or simply consider the feature still In Progress until the build workflow finishes all steps). This would reduce the number of hand-offs in the state machine. The task would go from Planned to Done (or to a single intermediate dev-complete state) in one workflow, rather than two transitions. Fewer intermediate states mean less complexity tracking in code and in the backlog.
    
- **Consolidated Logic and Tools:** Both implement and validate steps involve interacting with development tools and repositories – writing files, running linters/tests, updating the backlog, committing results. Combining them avoids duplicating those routines. For example, currently `/flow:implement` likely creates a commit with code changes, and `/flow:validate` might create another commit or update artifacts (like a QA report in `docs/qa/`). In a unified Build phase, these can be part of one controlled commit or series of atomic commits handled by one command flow. The Build workflow can share context between coding and testing; e.g., the same AI agent that wrote the code could be prompted to assist in generating test cases, and then those tests are executed – all within one command session. This reuse of context is harder when the steps are split across separate invocations.
    
- **Reduction of Overhead:** From a user’s perspective, having to run `implement` and then `validate` is extra overhead, especially if they logically consider both as part of “development.” The simplified Build command improves developer experience by doing “all the work to get a shippable increment” at once. It also opens opportunities for optimization – for instance, if minor code changes are made, the Build workflow could be smart enough to rerun only relevant tests or skip regeneration of unchanged parts, etc., which is easier to manage within one combined workflow than across distinct commands.
    
- **Quality Enforcement:** By design, the Build workflow ensures that code and tests always come together. This helps enforce the rule (present in the current docs) that implementation isn’t complete until code **and** docs **and** tests are delivered[github.com](https://github.com/jpoley/flowspec#:~:text=Every%20,deliverables)[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%20%20Documents%20,%E2%94%82%20%E2%94%94%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%B4%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%B4%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%80%E2%94%98). In the current setup, if a developer ran `/flow:implement` and stopped, they might omit running `/flow:validate` – leaving the feature in a half-done state. A single Build stage removes that possibility, improving consistency and reliability of the development process.
    

In essence, the Build workflow consolidation simplifies both usage and internals: one phase to handle everything from coding to verification, reducing command count and integrating all the necessary checks automatically.

## Run Workflow

**Objective:** The **Run** workflow handles deployment and operational readiness of the feature. Its purpose is to ensure the new feature is not just built, but also **released and maintainable in production**. This covers tasks like preparing deployment configurations, documentation for operations (runbooks), and potentially monitoring setups – answering _“How do we run and support it in live environments?”_.

**Mapped Existing Commands:** This corresponds chiefly to the final command in the current suite:

- `/flow:operate` – which takes a validated feature and produces the artifacts for deployment and maintenance, moving the task to Deployed/Done[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent). This typically creates or updates things like the service runbook (`docs/runbooks/[feature]-runbook.md`), deployment YAMLs/Infrastructure-as-Code, and notes on monitoring or rollback, as suggested by the documentation.
    

The **Run** workflow essentially encapsulates what `/flow:operate` does today. Since this was already a single step, the mapping doesn’t involve merging multiple commands – rather, it’s about positioning it clearly as one of the three core workflows.

**Improvements Through Simplification:** While the Run stage was not as fragmented as the earlier parts, reframing it as one of three primary workflows still brings some benefits:

- **Emphasis on Deployment as a First-Class Phase:** In the current design, `operate` is the last in a long list of commands. By elevating **Run** as a top-level workflow, we underscore the importance of operational tasks. This makes it clearer to developers that “running in production” is a major focus area, not an afterthought. The simplified structure helps communicate that after build, you must explicitly handle deployment/operations (rather than assuming a feature is done after code and tests). It also aligns with DevOps thinking (you build it, you run it).
    
- **Consistency and Integration:** Under the hood, a Run workflow can tie up loose ends from the earlier phases. For example, it can ensure any final state changes are recorded (mark tasks complete, archive or tag the feature branch, etc.), and that all deployment artifacts are in place. In a unified workflow model, the Run command could also automatically trigger deployment scripts or continuous deployment pipelines if configured. In the current setup, it’s unclear if `/flow:operate` actually deploys or just documents the deployment – a refined Run workflow could be extended to initiate real deployment actions (or at least integrate with deployment tools) as part of the automation. This would eliminate any gap where a developer might have to manually deploy after generating the runbook.
    
- **Elimination of Redundancy:** If there were any separate manual steps around release (for instance, writing a runbook by hand or updating configurations outside flowspec), the Run workflow consolidates them. Since flowspec already uses an SRE agent to generate ops artifacts[github.com](https://github.com/jpoley/flowspec#:~:text=%E2%94%82%20%2Fflow%3Aimplement%E2%94%82%20Planned%20%20,%E2%94%82%20SRE%20Agent), the new structure would continue to leverage that but could also remove any duplicative checks. (For example, if validation and operate both might run some static analysis or checks, those can be clearly delineated – Build does QA, Run handles ops only.) This makes each workflow’s responsibility clearer and avoids overlapping concerns.
    
- **Technical Debt Reduction:** Focusing on a single Run command means the code paths related to finalizing a feature are contained. Currently, once `/flow:operate` finishes, the feature is “Done.” The new model doesn’t change that outcome, but by grouping under **Run** we ensure any legacy or alternate deployment mechanisms are unnecessary. If there were alternate ways to mark tasks done (outside flowspec), those can be deprecated in favor of always using the Run workflow to conclude a feature’s lifecycle. This simplifies maintenance: for example, the backlog task closure and documentation finalization happens in one known place.
    

**Overall Design Improvement:** Breaking the flowspec functionality into **Research, Build, and Run** workflows makes the system more **approachable** and maintainable without losing capability. Each of the three workflows corresponds to a natural grouping of development activities:

- _Research = “plan it”_,
    
- _Build = “create it”_,
    
- _Run = “deploy it”_.
    

This improves clarity by mapping to concepts developers already understand, while **reducing the number of commands** from seven to three. The simplified structure avoids the pitfalls of the current design — where fine-grained phases can lead to duplication and confusion — by consolidating related steps and trimming excess states. For example, rather than juggling states like _Specified/Researched/Planned_ which have overlapping meaning, the Research workflow can output a single comprehensive design package ready for build. Rather than two commands for coding and testing, one Build workflow ensures delivery is test-verified. This not only streamlines the user experience but also cuts down on the internal complexity (fewer command implementations and state transitions to maintain).

Finally, this reorganization addresses current weaknesses such as **over-engineering** (too many moving parts for the user to orchestrate) and potential **inconsistencies** (features proceeding without all steps, or older non-integrated flows causing divergence). By consolidating into three core workflows, flowspec can eliminate those edge cases and focus on a clean, actionable sequence. The result is a more **cohesive CLI design** that retains all the power of spec-driven, AI-assisted development, but in a clearer, more maintainable form. Each workflow is clearly delineated, easier to invoke, and easier to extend or adjust as the tool evolves – providing a strong foundation free of the duplicated logic and technical debt present in the current design.