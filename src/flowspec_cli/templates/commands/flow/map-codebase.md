---
description: Generate bounded directory tree listings and feature maps for codebase areas.
mode: agent
loop: utility
# Loop Classification: UTILITY
# This is a utility command that can be used in either loop. It generates codebase
# maps for context and documentation but doesn't modify code or workflow state.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command generates bounded directory tree listings for relevant parts of the codebase. It creates readable maps that support PRP generation and feature context.

### Argument Parsing

Parse the user input for paths and flags:

```bash
# Expected formats:
# /flow:map-codebase src/commands           # Single path
# /flow:map-codebase src/ tests/            # Multiple paths
# /flow:map-codebase src/ --depth 3         # With depth flag
# /flow:map-codebase src/ --output docs/feature-maps/task-123.md
# /flow:map-codebase src/ --prp task-123    # Update PRP file

PATHS=""
DEPTH=3
OUTPUT=""
PRP_TASK=""

# Parse arguments
for arg in $ARGUMENTS; do
  case "$arg" in
    --depth)
      # Next arg is depth value
      ;;
    --output)
      # Next arg is output path
      ;;
    --prp)
      # Next arg is task ID
      ;;
    *)
      # Treat as path if doesn't start with --
      if [[ ! "$arg" =~ ^-- ]]; then
        PATHS="$PATHS $arg"
      fi
      ;;
  esac
done
```

### Default Values

If no arguments provided, show usage:

```
Usage: /flow:map-codebase <paths...> [options]

Options:
  --depth <n>     Maximum directory depth (default: 3)
  --output <path> Write to specific file
  --prp <task-id> Update CODEBASE SNAPSHOT in docs/prp/<task-id>.md

Examples:
  /flow:map-codebase src/
  /flow:map-codebase src/ tests/ --depth 4
  /flow:map-codebase src/commands --prp task-123
  /flow:map-codebase src/ --output docs/feature-maps/auth.md
```

### Step 1: Validate Paths

Verify all specified paths exist:

```bash
for path in $PATHS; do
  if [ ! -e "$path" ]; then
    echo "ERROR: Path not found: $path"
    exit 1
  fi
done

echo "Mapping paths: $PATHS"
echo "Depth: $DEPTH"
```

### Step 2: Generate Directory Tree

Generate a bounded directory tree for each path, excluding common non-essential directories:

```bash
# Exclusion patterns
EXCLUDES="--exclude node_modules --exclude __pycache__ --exclude .git --exclude .venv --exclude venv --exclude .mypy_cache --exclude .pytest_cache --exclude .ruff_cache --exclude dist --exclude build --exclude *.egg-info --exclude .tox --exclude coverage --exclude .coverage --exclude htmlcov"

# Generate tree for each path
for path in $PATHS; do
  echo ""
  echo "## $path"
  echo ""
  echo '```'
  # Use tree command if available, otherwise use find
  if command -v tree &> /dev/null; then
    tree -L $DEPTH $EXCLUDES --noreport "$path"
  else
    # Fallback to find + custom formatting
    find "$path" -maxdepth $DEPTH -type f -o -type d | \
      grep -v "node_modules\|__pycache__\|\.git\|\.venv\|\.mypy_cache" | \
      sort
  fi
  echo '```'
done
```

### Step 3: Identify Key Entry Points

For each mapped path, identify key entry points:

```bash
echo ""
echo "### Key Entry Points"
echo ""
echo "| Entry Point | Location | Purpose |"
echo "|-------------|----------|---------|"

# Look for common entry point patterns
for path in $PATHS; do
  # Main files
  find "$path" -maxdepth 2 -name "main.py" -o -name "main.ts" -o -name "index.ts" -o -name "index.py" -o -name "app.py" -o -name "cli.py" 2>/dev/null | while read f; do
    echo "| \`$(basename $f)\` | \`$f\` | Main entry point |"
  done

  # Command files
  find "$path" -maxdepth 3 -path "*/commands/*.py" -o -path "*/commands/*.ts" 2>/dev/null | head -5 | while read f; do
    echo "| \`$(basename $f)\` | \`$f\` | Command handler |"
  done
done
```

### Step 4: Identify Integration Points

Look for files that represent integration boundaries:

```bash
echo ""
echo "### Integration Points"
echo ""
echo "| Integration | File | Function/Method | Notes |"
echo "|-------------|------|-----------------|-------|"

for path in $PATHS; do
  # API route files
  find "$path" -maxdepth 3 -name "routes*.py" -o -name "routes*.ts" -o -name "api*.py" 2>/dev/null | head -3 | while read f; do
    echo "| API | \`$f\` | - | REST/GraphQL endpoints |"
  done

  # Database files
  find "$path" -maxdepth 3 -name "models*.py" -o -name "database*.py" -o -name "db*.py" 2>/dev/null | head -3 | while read f; do
    echo "| Database | \`$f\` | - | Data models |"
  done

  # Config files
  find "$path" -maxdepth 2 -name "config*.py" -o -name "settings*.py" 2>/dev/null | head -2 | while read f; do
    echo "| Config | \`$f\` | - | Configuration |"
  done
done
```

### Step 5: Output Handling

Based on flags, write output to appropriate destination:

#### Option A: Standard Output (default)

If no `--output` or `--prp` flag, print to stdout:

```
Codebase Map Generated
======================

[Directory tree output]
[Key Entry Points table]
[Integration Points table]

Copy this output to your PRP or documentation.
```

#### Option B: Write to File (--output flag)

```bash
if [ -n "$OUTPUT" ]; then
  # Ensure directory exists
  mkdir -p "$(dirname $OUTPUT)"

  # Write header
  echo "# Codebase Map" > "$OUTPUT"
  echo "" >> "$OUTPUT"
  echo "> Generated by /flow:map-codebase" >> "$OUTPUT"
  echo "> Generated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$OUTPUT"
  echo "" >> "$OUTPUT"

  # Append tree output
  # ... (tree generation)

  echo ""
  echo "Map written to: $OUTPUT"
fi
```

#### Option C: Update PRP File (--prp flag)

```bash
if [ -n "$PRP_TASK" ]; then
  PRP_FILE="docs/prp/$PRP_TASK.md"

  if [ ! -f "$PRP_FILE" ]; then
    echo "ERROR: PRP file not found: $PRP_FILE"
    echo "Run /flow:generate-prp $PRP_TASK first"
    exit 1
  fi

  echo "Updating CODEBASE SNAPSHOT in: $PRP_FILE"

  # Replace content between CODEBASE SNAPSHOT markers
  # ... (sed/awk replacement logic)

  echo "PRP updated successfully"
fi
```

### Step 6: File Type Summary

Generate a summary of file types found:

```bash
echo ""
echo "### File Type Summary"
echo ""
echo "| Extension | Count |"
echo "|-----------|-------|"

for path in $PATHS; do
  find "$path" -type f -name "*.*" | \
    grep -v "node_modules\|__pycache__\|\.git" | \
    sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10 | \
    while read count ext; do
      echo "| .$ext | $count |"
    done
done
```

### Output Format

The complete output format is:

```markdown
# Codebase Map

> Generated by /flow:map-codebase
> Paths: src/commands tests/
> Depth: 3
> Generated at: 2024-01-15T10:30:00Z

## Directory Tree

### src/commands

```
src/commands/
├── flow/
│   ├── assess.md
│   ├── implement.md
│   └── specify.md
├── dev/
│   └── debug.md
└── README.md
```

### tests/

```
tests/
├── unit/
│   └── test_commands.py
└── integration/
    └── test_flow.py
```

## Key Entry Points

| Entry Point | Location | Purpose |
|-------------|----------|---------|
| `main.py` | `src/main.py` | CLI entry point |
| `assess.md` | `src/commands/flow/assess.md` | Assessment command |

## Integration Points

| Integration | File | Function/Method | Notes |
|-------------|------|-----------------|-------|
| CLI | `src/cli.py` | `main()` | Typer CLI |
| Commands | `src/commands/` | - | Slash commands |

## File Type Summary

| Extension | Count |
|-----------|-------|
| .py | 45 |
| .md | 23 |
| .yml | 8 |
```

### Example Usage

```bash
# Map a single directory
/flow:map-codebase src/

# Map multiple directories with custom depth
/flow:map-codebase src/ tests/ --depth 4

# Update a PRP file's CODEBASE SNAPSHOT section
/flow:map-codebase src/commands --prp task-123

# Save to a specific file
/flow:map-codebase src/ --output docs/feature-maps/authentication.md
```

## Deliverables

This command produces:
1. **Directory Tree**: Bounded tree listing of specified paths
2. **Key Entry Points**: Table of main entry files
3. **Integration Points**: Table of integration boundaries
4. **File Type Summary**: Count of file types

Output can be:
- Displayed in terminal (default)
- Written to a file (`--output`)
- Inserted into a PRP file (`--prp`)
