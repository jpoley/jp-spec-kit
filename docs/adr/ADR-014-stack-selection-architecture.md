# ADR-014: Stack Selection System Architecture

**Status**: Accepted
**Date**: 2025-12-04
**Author**: Enterprise Software Architect (Kinsale Host)
**Context**: Task-079 - Stack Selection During Init

---

## Context and Problem Statement

JP Spec Kit's `specify init` command currently scaffolds a comprehensive project structure with templates for all technology stacks (React+Go, React+Python, Full-Stack TypeScript, Mobile+Go, Data/ML Pipeline, Infrastructure, Documentation, CLI Tool, API Server).

**Problems**:
- **Cluttered projects**: All 9 stacks scaffolded by default (50+ template files)
- **Irrelevant files**: React developer sees Go templates, backend developer sees mobile files
- **Cognitive overload**: New users confused by dozens of unfamiliar stack files
- **Manual cleanup**: Users delete unneeded stacks manually (error-prone, incomplete)
- **CI/CD bloat**: Generic GitHub Actions workflow tries to detect stack at runtime
- **No guidance**: Users don't know which stack to choose

**Goal**: Enable interactive stack selection during `specify init`, scaffold only selected stack, and provide non-interactive mode for automation.

---

## Decision Drivers

1. **Reduce Clutter**: Only install files relevant to selected stack
2. **Interactive UX**: Arrow key navigation for stack selection
3. **Automation Support**: `--stack` flag for CI/batch mode
4. **Stack-Specific CI/CD**: Copy appropriate GitHub Actions workflow
5. **Escape Hatch**: Option to install all stacks (for polyglot projects)
6. **Progressive Disclosure**: Show stack descriptions before selection
7. **Validation**: Warn if selecting incompatible stacks together

---

## Considered Options

### Option 1: Post-Init Cleanup Script
**Approach**: Scaffold all stacks, then run cleanup script to remove unselected ones

**Pros**:
- Simple implementation (deletion logic)
- No changes to scaffolding logic
- Easy to test (verify deletion)

**Cons**:
- Wasteful (create then delete)
- Risk of incomplete cleanup
- User sees all files briefly (confusion)
- No stack-specific CI/CD selection

### Option 2: Conditional Scaffolding (Pre-Selection)
**Approach**: Ask stack selection first, then scaffold only selected stack

**Pros**:
- Clean (only relevant files created)
- Fast (no wasted I/O)
- Stack-specific CI/CD workflows
- Immediate clarity for users

**Cons**:
- More complex scaffolding logic
- Must maintain stack→file mappings
- Harder to test (many permutations)

### Option 3: Modular Stack Plugins
**Approach**: Each stack is a separate plugin, users install plugins for desired stacks

**Pros**:
- Maximum modularity
- Easy to add new stacks
- Users can install multiple stacks incrementally

**Cons**:
- High complexity (plugin system overhead)
- Fragmented distribution
- Harder for users to discover available stacks

---

## Decision Outcome

**Chosen Option**: **Option 2 - Conditional Scaffolding with Pre-Selection**

Ask stack selection during `specify init`, then scaffold only selected stack(s).

### Rationale

- **User Experience**: Clean, focused project structure from the start
- **Performance**: Only create relevant files (10-20 files vs. 50+)
- **CI/CD Integration**: Copy stack-specific GitHub Actions workflow
- **Maintainability**: Centralized stack configuration in `STACK_CONFIG`
- **Testability**: Verify correct files created for each stack

---

## Stack Definitions

### Stack Configuration

**File**: `src/specify_cli/stacks.py`

```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Stack:
    id: str
    name: str
    description: str
    languages: List[str]
    frameworks: List[str]
    template_files: List[str]  # Files to scaffold
    ci_workflow: str           # GitHub Actions workflow file
    dependencies: List[str]    # Other stacks this one depends on

STACK_CONFIG = {
    "react-go": Stack(
        id="react-go",
        name="React + Go (Full-Stack)",
        description="React frontend with Go backend. REST API, JWT auth, PostgreSQL.",
        languages=["TypeScript", "Go"],
        frameworks=["React", "Gin", "PostgreSQL"],
        template_files=[
            "frontend/src/App.tsx",
            "frontend/package.json",
            "backend/cmd/server/main.go",
            "backend/go.mod",
            "docker-compose.yml",
            "Dockerfile.frontend",
            "Dockerfile.backend"
        ],
        ci_workflow="templates/ci-workflows/react-go.yml",
        dependencies=[]
    ),

    "react-python": Stack(
        id="react-python",
        name="React + Python (Full-Stack)",
        description="React frontend with FastAPI backend. REST API, Pydantic models, PostgreSQL.",
        languages=["TypeScript", "Python"],
        frameworks=["React", "FastAPI", "PostgreSQL"],
        template_files=[
            "frontend/src/App.tsx",
            "frontend/package.json",
            "backend/app/main.py",
            "backend/pyproject.toml",
            "docker-compose.yml",
            "Dockerfile.frontend",
            "Dockerfile.backend"
        ],
        ci_workflow="templates/ci-workflows/react-python.yml",
        dependencies=[]
    ),

    "fullstack-typescript": Stack(
        id="fullstack-typescript",
        name="Full-Stack TypeScript",
        description="Next.js + tRPC + Prisma. Type-safe end-to-end. PostgreSQL.",
        languages=["TypeScript"],
        frameworks=["Next.js", "tRPC", "Prisma", "PostgreSQL"],
        template_files=[
            "src/pages/index.tsx",
            "src/server/router.ts",
            "prisma/schema.prisma",
            "package.json",
            "tsconfig.json",
            "docker-compose.yml"
        ],
        ci_workflow="templates/ci-workflows/fullstack-typescript.yml",
        dependencies=[]
    ),

    "mobile-go": Stack(
        id="mobile-go",
        name="Mobile + Go Backend",
        description="React Native mobile app with Go backend. REST API, push notifications.",
        languages=["TypeScript", "Go"],
        frameworks=["React Native", "Gin", "PostgreSQL"],
        template_files=[
            "mobile/App.tsx",
            "mobile/package.json",
            "backend/cmd/server/main.go",
            "backend/go.mod",
            "docker-compose.yml"
        ],
        ci_workflow="templates/ci-workflows/mobile-go.yml",
        dependencies=[]
    ),

    "data-ml-pipeline": Stack(
        id="data-ml-pipeline",
        name="Data/ML Pipeline",
        description="Apache Airflow + PySpark + MLflow. ETL, model training, deployment.",
        languages=["Python"],
        frameworks=["Airflow", "PySpark", "MLflow", "PostgreSQL"],
        template_files=[
            "dags/example_pipeline.py",
            "models/train_model.py",
            "pyproject.toml",
            "docker-compose.yml",
            "Dockerfile"
        ],
        ci_workflow="templates/ci-workflows/data-ml-pipeline.yml",
        dependencies=[]
    ),

    "infrastructure": Stack(
        id="infrastructure",
        name="Infrastructure as Code",
        description="Terraform + Kubernetes + Helm. Multi-cloud provisioning and deployment.",
        languages=["HCL", "YAML"],
        frameworks=["Terraform", "Kubernetes", "Helm"],
        template_files=[
            "terraform/main.tf",
            "terraform/variables.tf",
            "k8s/deployment.yaml",
            "helm/Chart.yaml",
            "Makefile"
        ],
        ci_workflow="templates/ci-workflows/infrastructure.yml",
        dependencies=[]
    ),

    "documentation-site": Stack(
        id="documentation-site",
        name="Documentation Site",
        description="Docusaurus or VitePress. Markdown-based docs with search and versioning.",
        languages=["TypeScript", "Markdown"],
        frameworks=["Docusaurus"],
        template_files=[
            "docs/intro.md",
            "docusaurus.config.js",
            "package.json",
            "sidebars.js"
        ],
        ci_workflow="templates/ci-workflows/documentation-site.yml",
        dependencies=[]
    ),

    "cli-tool": Stack(
        id="cli-tool",
        name="CLI Tool",
        description="Go CLI with Cobra. Cross-platform binary, config management, plugins.",
        languages=["Go"],
        frameworks=["Cobra"],
        template_files=[
            "cmd/root.go",
            "cmd/version.go",
            "go.mod",
            "Makefile",
            "goreleaser.yml"
        ],
        ci_workflow="templates/ci-workflows/cli-tool.yml",
        dependencies=[]
    ),

    "api-server": Stack(
        id="api-server",
        name="API Server (Backend-Only)",
        description="Go REST API with OpenAPI spec. JWT auth, rate limiting, PostgreSQL.",
        languages=["Go"],
        frameworks=["Gin", "PostgreSQL"],
        template_files=[
            "cmd/server/main.go",
            "api/openapi.yaml",
            "go.mod",
            "docker-compose.yml",
            "Dockerfile"
        ],
        ci_workflow="templates/ci-workflows/api-server.yml",
        dependencies=[]
    )
}
```

---

## Interactive Stack Selection UI

### Selection Flow

```
$ specify init my-project

Initializing my-project with Spec-Driven Development...

Select Technology Stack:
(Use arrow keys, press Enter to select, Space to toggle multiple)

  [ ] React + Go (Full-Stack)
      React frontend with Go backend. REST API, JWT auth, PostgreSQL.

  [ ] React + Python (Full-Stack)
      React frontend with FastAPI backend. REST API, Pydantic models, PostgreSQL.

  [x] Full-Stack TypeScript ← SELECTED
      Next.js + tRPC + Prisma. Type-safe end-to-end. PostgreSQL.

  [ ] Mobile + Go Backend
      React Native mobile app with Go backend. REST API, push notifications.

  [ ] Data/ML Pipeline
      Apache Airflow + PySpark + MLflow. ETL, model training, deployment.

  [ ] Infrastructure as Code
      Terraform + Kubernetes + Helm. Multi-cloud provisioning.

  [ ] Documentation Site
      Docusaurus or VitePress. Markdown-based docs with search.

  [ ] CLI Tool
      Go CLI with Cobra. Cross-platform binary, config management.

  [ ] API Server (Backend-Only)
      Go REST API with OpenAPI spec. JWT auth, rate limiting.

  [ ] ALL STACKS (Polyglot Project)
      Install all stack templates. Useful for monorepos.

> Selected: Full-Stack TypeScript

Confirm selection? (y/n): y

Creating project structure...
✓ Created memory/ (SDD artifacts)
✓ Created backlog/ (task management)
✓ Created docs/adr/ (architecture decisions)
✓ Created src/pages/ (Next.js pages)
✓ Created src/server/ (tRPC router)
✓ Created prisma/ (database schema)
✓ Created tests/ (test suites)
✓ Copied .github/workflows/fullstack-typescript.yml
✓ Copied .claude/ (commands, skills, hooks)

Project initialized successfully!

Next steps:
  1. cd my-project
  2. npm install
  3. npm run dev
  4. Open http://localhost:3000

Run '/jpspec:assess' to start Spec-Driven Development workflow.
```

### Implementation (Python + `inquirer`)

```python
import inquirer
from typing import List

def select_stack_interactive() -> List[str]:
    """Interactive stack selection with arrow key navigation."""

    # Build choices with descriptions
    choices = []
    for stack_id, stack in STACK_CONFIG.items():
        label = f"{stack.name}\n    {stack.description}"
        choices.append((label, stack_id))

    # Add "All Stacks" option
    choices.append(("ALL STACKS (Polyglot Project)\n    Install all stack templates.", "all"))

    # Use inquirer for interactive selection
    questions = [
        inquirer.Checkbox(
            'stacks',
            message="Select Technology Stack(s) (Space to toggle, Enter to confirm)",
            choices=choices,
        )
    ]

    answers = inquirer.prompt(questions)
    selected = answers['stacks']

    # If "all" selected, return all stack IDs
    if "all" in selected:
        return list(STACK_CONFIG.keys())

    return selected

def scaffold_stacks(project_path: Path, stack_ids: List[str]):
    """Scaffold only files for selected stacks."""

    for stack_id in stack_ids:
        stack = STACK_CONFIG[stack_id]

        print(f"Scaffolding {stack.name}...")

        # Copy template files
        for template_file in stack.template_files:
            src = Path("templates") / template_file
            dst = project_path / template_file

            # Create parent directories
            dst.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy(src, dst)

        # Copy CI/CD workflow
        ci_src = Path(stack.ci_workflow)
        ci_dst = project_path / ".github/workflows" / f"{stack_id}.yml"
        ci_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ci_src, ci_dst)

    print("✓ Stack scaffolding complete")
```

---

## Non-Interactive Mode (Automation)

### CLI Flags

```bash
# Single stack selection
specify init my-project --stack fullstack-typescript

# Multiple stacks (comma-separated)
specify init my-project --stack react-go,infrastructure

# All stacks (polyglot)
specify init my-project --stack all

# Skip stack selection (prompt user later)
specify init my-project --no-stack
```

### Implementation

```python
import typer

app = typer.Typer()

@app.command()
def init(
    project_name: str,
    stack: str = typer.Option(None, help="Stack ID(s) to install (comma-separated)"),
    no_stack: bool = typer.Option(False, help="Skip stack selection (scaffold SDD only)"),
):
    """Initialize a new SDD project with optional stack selection."""

    # Create project directory
    project_path = Path(project_name)
    project_path.mkdir(exist_ok=True)

    # Scaffold base SDD structure (always)
    scaffold_sdd_base(project_path)

    # Handle stack selection
    if no_stack:
        print("⚠️  Skipping stack selection. Run 'specify add-stack <stack-id>' later.")
        return

    if stack:
        # Non-interactive mode
        if stack == "all":
            selected_stacks = list(STACK_CONFIG.keys())
        else:
            selected_stacks = stack.split(",")

        # Validate stack IDs
        invalid = [s for s in selected_stacks if s not in STACK_CONFIG]
        if invalid:
            print(f"❌ Invalid stack IDs: {', '.join(invalid)}")
            print(f"Valid options: {', '.join(STACK_CONFIG.keys())}, all")
            raise typer.Exit(1)

        scaffold_stacks(project_path, selected_stacks)
    else:
        # Interactive mode
        selected_stacks = select_stack_interactive()
        scaffold_stacks(project_path, selected_stacks)

    print(f"✓ Project '{project_name}' initialized successfully!")
```

---

## Stack-Specific CI/CD Workflows

### React + Go Workflow

**File**: `templates/ci-workflows/react-go.yml`

```yaml
name: React + Go CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  frontend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npm run build

  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go mod download
      - run: go vet ./...
      - run: go test -v ./...
      - run: go build -v ./...

  integration:
    runs-on: ubuntu-latest
    needs: [frontend, backend]
    steps:
      - uses: actions/checkout@v3
      - run: docker-compose up -d
      - run: npm run test:e2e
      - run: docker-compose down
```

### Full-Stack TypeScript Workflow

**File**: `templates/ci-workflows/fullstack-typescript.yml`

```yaml
name: Full-Stack TypeScript CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check
      - run: npm run test
      - run: npx prisma generate
      - run: npx prisma migrate deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
      - run: npm run build
      - run: npm run test:e2e
```

### Data/ML Pipeline Workflow

**File**: `templates/ci-workflows/data-ml-pipeline.yml`

```yaml
name: Data/ML Pipeline CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-dags:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest dags/ -v
      - run: airflow dags test example_pipeline 2023-01-01

  test-models:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest models/ -v
      - run: python models/train_model.py --dry-run

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install ruff
      - run: ruff check .
```

---

## Multi-Stack Projects (Monorepos)

### Scenario: Polyglot Monorepo

**Use Case**: Startup building mobile app (React Native), backend API (Go), data pipeline (Python), and documentation site (Docusaurus).

**Selection**:
```bash
specify init acme-corp --stack mobile-go,data-ml-pipeline,documentation-site
```

**Result**: Scaffolds all three stacks, combined CI/CD workflow.

### Combined Workflow Generation

When multiple stacks selected, generate combined workflow:

```yaml
name: Monorepo CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  # Mobile app (React Native)
  mobile:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./mobile
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run lint
      - run: npm run test
      - run: npx expo build:ios --non-interactive

  # Backend API (Go)
  backend:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go test -v ./...
      - run: go build -v ./...

  # Data pipeline (Python)
  data-pipeline:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./data-pipeline
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest -v

  # Documentation (Docusaurus)
  docs:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./docs
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
```

---

## Adding Stacks Post-Init

### Command: `specify add-stack`

**Use Case**: Project initialized without stack, user adds stack later.

```bash
# Add single stack
specify add-stack react-python

# Add multiple stacks
specify add-stack infrastructure,documentation-site

# Interactive selection
specify add-stack --interactive
```

**Implementation**:
```python
@app.command()
def add_stack(
    stack: str = typer.Argument(None, help="Stack ID(s) to add"),
    interactive: bool = typer.Option(False, help="Interactive stack selection"),
):
    """Add technology stack to existing project."""

    # Verify in project root
    if not Path("memory").exists():
        print("❌ Not in SDD project root (missing memory/ directory)")
        raise typer.Exit(1)

    # Get stack selection
    if interactive:
        selected_stacks = select_stack_interactive()
    elif stack:
        selected_stacks = stack.split(",")
    else:
        print("❌ Provide --stack or use --interactive")
        raise typer.Exit(1)

    # Scaffold selected stacks
    project_path = Path.cwd()
    scaffold_stacks(project_path, selected_stacks)

    print("✓ Stack(s) added successfully")
```

---

## Testing Strategy

### Unit Tests (Stack Configuration)

```python
def test_stack_config_completeness():
    """Verify all stacks have required fields."""
    for stack_id, stack in STACK_CONFIG.items():
        assert stack.id == stack_id
        assert stack.name
        assert stack.description
        assert len(stack.languages) > 0
        assert len(stack.template_files) > 0
        assert stack.ci_workflow.endswith(".yml")

def test_stack_template_files_exist():
    """Verify all template files referenced in stacks exist."""
    for stack in STACK_CONFIG.values():
        for template_file in stack.template_files:
            file_path = Path("templates") / template_file
            assert file_path.exists(), f"Missing template: {template_file}"

def test_stack_ci_workflows_exist():
    """Verify all CI workflow files exist."""
    for stack in STACK_CONFIG.values():
        ci_path = Path(stack.ci_workflow)
        assert ci_path.exists(), f"Missing CI workflow: {stack.ci_workflow}"
```

### Integration Tests (Scaffolding)

```python
def test_scaffold_single_stack(tmp_path):
    """Verify single stack scaffolding creates correct files."""
    scaffold_stacks(tmp_path, ["fullstack-typescript"])

    # Verify stack-specific files created
    assert (tmp_path / "src/pages/index.tsx").exists()
    assert (tmp_path / "prisma/schema.prisma").exists()
    assert (tmp_path / "package.json").exists()

    # Verify CI workflow copied
    assert (tmp_path / ".github/workflows/fullstack-typescript.yml").exists()

    # Verify unrelated stacks NOT created
    assert not (tmp_path / "backend/go.mod").exists()
    assert not (tmp_path / "dags").exists()

def test_scaffold_multiple_stacks(tmp_path):
    """Verify multiple stack scaffolding doesn't conflict."""
    scaffold_stacks(tmp_path, ["react-go", "documentation-site"])

    # Verify both stacks created
    assert (tmp_path / "frontend/src/App.tsx").exists()
    assert (tmp_path / "backend/cmd/server/main.go").exists()
    assert (tmp_path / "docs/intro.md").exists()

    # Verify both CI workflows present
    assert (tmp_path / ".github/workflows/react-go.yml").exists()
    assert (tmp_path / ".github/workflows/documentation-site.yml").exists()
```

### End-to-End Tests (CLI)

```python
def test_init_with_stack_flag(tmp_path):
    """Verify specify init --stack creates project correctly."""
    os.chdir(tmp_path)

    result = subprocess.run([
        "specify", "init", "test-project",
        "--stack", "fullstack-typescript"
    ], capture_output=True)

    assert result.returncode == 0
    assert Path("test-project/src/pages/index.tsx").exists()
    assert Path("test-project/.github/workflows/fullstack-typescript.yml").exists()

def test_add_stack_command(tmp_path):
    """Verify specify add-stack adds to existing project."""
    # Initialize without stack
    os.chdir(tmp_path)
    subprocess.run(["specify", "init", "test-project", "--no-stack"])

    # Add stack
    os.chdir("test-project")
    result = subprocess.run([
        "specify", "add-stack", "react-python"
    ], capture_output=True)

    assert result.returncode == 0
    assert Path("frontend/src/App.tsx").exists()
    assert Path("backend/app/main.py").exists()
```

---

## Consequences

### Positive

- **Reduced Clutter**: Users see only relevant stack files (10-20 vs. 50+)
- **Clear Intent**: Project structure immediately reveals technology choices
- **Stack-Specific CI/CD**: Workflows optimized for selected stack
- **Progressive Disclosure**: Users not overwhelmed by all stacks at once
- **Automation Support**: `--stack` flag enables CI/batch initialization
- **Polyglot Support**: Can select multiple stacks for monorepos

### Negative

- **More Complex Logic**: Conditional scaffolding vs. simple copy-all
- **Template Maintenance**: Must update stack→file mappings when adding templates
- **Testing Overhead**: Need to test all stack combinations
- **User Decisions**: Users must choose stack upfront (analysis paralysis risk)

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Wrong stack selected | Project mismatch | `specify add-stack` command allows correction |
| Missing files after selection | Broken project | Comprehensive integration tests per stack |
| Stack definitions outdated | Irrelevant templates | Regular review of stack configs (quarterly) |
| Users don't know which stack | Confusion | Detailed descriptions in selection UI |
| Multi-stack conflicts | File collisions | Validate stack compatibility before scaffolding |

---

## Future Enhancements

### Community-Contributed Stacks

Allow community to contribute stack definitions via PR:

```python
# File: stacks-community.py

COMMUNITY_STACKS = {
    "django-react": Stack(
        id="django-react",
        name="Django + React",
        description="Django REST Framework backend with React frontend.",
        contributed_by="@contributor",
        ...
    )
}
```

### Stack Recommendations Based on Project Type

Analyze user input to recommend stack:

```python
def recommend_stack(project_description: str) -> str:
    """Use LLM to recommend stack based on description."""

    prompt = f"""
    Given project description: "{project_description}"

    Recommend best technology stack from:
    {list(STACK_CONFIG.keys())}

    Consider:
    - Problem domain (web, mobile, data, infrastructure)
    - Team size and skills
    - Performance requirements
    - Deployment target

    Return stack ID only.
    """

    recommendation = call_llm(prompt)
    return recommendation
```

Usage:
```bash
$ specify init --describe "E-commerce platform with 50k daily users"

Analyzing project requirements...
Recommended stack: react-go (Full-Stack with horizontal scaling capability)

Accept recommendation? (y/n): y
```

### Stack Migration Tool

Enable migration between stacks:

```bash
# Migrate from React+Python to React+Go
specify migrate-stack --from react-python --to react-go

# Preview changes before applying
specify migrate-stack --from react-python --to react-go --dry-run
```

---

## References

- **Task-079**: Stack Selection During Init
- **Inquirer.py**: https://github.com/magmax/python-inquirer
- **Typer CLI Framework**: https://typer.tiangolo.com/
- **GitHub Actions**: https://docs.github.com/actions

---

**Decision**: The conditional scaffolding with pre-selection approach provides the cleanest user experience, reduces project clutter by 60%+, and enables stack-specific CI/CD workflows while supporting both interactive and automated initialization.
