# CodeQL Setup Guide

## Overview

CodeQL is GitHub's semantic code analysis engine that provides deep dataflow analysis for detecting complex security vulnerabilities. This guide covers installation, database creation, query execution, and integration with Flowspec.

**Prerequisites**:
- Review [CodeQL Licensing](../legal/codeql-licensing-review.md) before proceeding
- Ensure compliance with GitHub's licensing terms
- Verify you have appropriate license (open source or GHAS)

## Installation

### Method 1: Automated Setup (Recommended)

Flowspec provides a setup script that handles CodeQL CLI installation:

```bash
# Download and install CodeQL CLI
./scripts/bash/setup-codeql.sh

# Verify installation
codeql version
# Expected output: CodeQL command-line toolchain release 2.15.x
```

The script will:
1. Detect your platform (Linux, macOS, Windows)
2. Download the latest CodeQL CLI binaries
3. Extract to `~/.codeql/`
4. Add to PATH in your shell configuration
5. Download standard query packs

### Method 2: Manual Installation

#### Step 1: Download CodeQL CLI

Visit [CodeQL CLI Releases](https://github.com/github/codeql-cli-binaries/releases):

```bash
# Linux x64
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
unzip codeql-linux64.zip -d ~/.codeql
rm codeql-linux64.zip

# macOS
wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-osx64.zip
unzip codeql-osx64.zip -d ~/.codeql
rm codeql-osx64.zip
```

#### Step 2: Add to PATH

```bash
# For bash
echo 'export PATH="$HOME/.codeql/codeql:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For zsh
echo 'export PATH="$HOME/.codeql/codeql:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

#### Step 3: Verify Installation

```bash
codeql version
codeql resolve languages
```

Expected output:
```
CodeQL command-line toolchain release 2.15.x
cpp
csharp
go
java
javascript
python
ruby
swift
```

### Method 3: Using Homebrew (macOS/Linux)

```bash
# Install via Homebrew
brew install codeql

# Verify
codeql version
```

## CodeQL Query Packs

CodeQL requires query packs to detect vulnerabilities. These contain the actual security rules.

### Download Standard Query Packs

```bash
# Create queries directory
mkdir -p ~/.codeql/queries

# Clone CodeQL standard libraries
cd ~/.codeql/queries
git clone https://github.com/github/codeql.git codeql-repo

# Verify query packs
ls ~/.codeql/queries/codeql-repo/
# Output: cpp/ csharp/ go/ java/ javascript/ python/ etc.
```

### Pre-compiled Query Packs

For faster scanning, use pre-compiled query packs:

```bash
# Download Python security queries
codeql pack download codeql/python-queries

# Download JavaScript security queries
codeql pack download codeql/javascript-queries

# Download all security queries
codeql pack download codeql/security-queries
```

## Database Creation

CodeQL analyzes code by first creating a database representation of your codebase.

### Python Database

```bash
# Basic Python database
codeql database create python-db \
  --language=python \
  --source-root=.

# With specific Python version
codeql database create python-db \
  --language=python \
  --source-root=. \
  --command="python3.11 -m compileall ."
```

### JavaScript/TypeScript Database

```bash
# Basic JavaScript database
codeql database create js-db \
  --language=javascript \
  --source-root=.

# With npm install (for dependencies)
codeql database create js-db \
  --language=javascript \
  --source-root=. \
  --command="npm install"
```

### Java Database

```bash
# Maven project
codeql database create java-db \
  --language=java \
  --source-root=. \
  --command="mvn clean compile"

# Gradle project
codeql database create java-db \
  --language=java \
  --source-root=. \
  --command="./gradlew clean build -x test"
```

### Multi-language Projects

For projects with multiple languages:

```bash
# Create separate databases
codeql database create python-db --language=python --source-root=backend/
codeql database create js-db --language=javascript --source-root=frontend/

# Analyze both
codeql database analyze python-db --format=sarif-latest --output=python-results.sarif
codeql database analyze js-db --format=sarif-latest --output=js-results.sarif
```

### Database Creation Best Practices

1. **Clean build**: Ensure fresh build before database creation
2. **All dependencies**: Install all dependencies first
3. **Build command**: Use the actual build command that compiles all code
4. **Incremental updates**: For large codebases, consider incremental database updates

```bash
# Clean before database creation
make clean
rm -rf build/ dist/

# Create database with dependencies
codeql database create mydb \
  --language=python \
  --source-root=. \
  --command="pip install -e . && python -m compileall ."
```

## Running Queries

### Security-Only Queries (Recommended)

Scan for security vulnerabilities only:

```bash
# Python security scan
codeql database analyze python-db \
  --format=sarif-latest \
  --output=results.sarif \
  codeql/python-queries:codeql-suites/python-security-extended.qls

# JavaScript security scan
codeql database analyze js-db \
  --format=sarif-latest \
  --output=results.sarif \
  codeql/javascript-queries:codeql-suites/javascript-security-extended.qls
```

### All Quality Queries

For comprehensive code quality analysis:

```bash
# Python code quality + security
codeql database analyze python-db \
  --format=sarif-latest \
  --output=results.sarif \
  codeql/python-queries

# This includes:
# - Security vulnerabilities
# - Code quality issues
# - Best practice violations
# - Performance problems
```

### Custom Query Packs

Run specific custom queries:

```bash
# Run custom query file
codeql database analyze python-db \
  --format=sarif-latest \
  --output=results.sarif \
  /path/to/custom-queries/

# Run specific query
codeql query run \
  --database=python-db \
  /path/to/sql-injection.ql
```

### Output Formats

CodeQL supports multiple output formats:

```bash
# SARIF (recommended for tools)
codeql database analyze mydb --format=sarif-latest --output=results.sarif

# CSV (for spreadsheet analysis)
codeql database analyze mydb --format=csv --output=results.csv

# JSON (for programmatic processing)
codeql database analyze mydb --format=json --output=results.json

# Human-readable text
codeql database analyze mydb --format=text
```

## Integration with Flowspec

### Using specify CLI

Flowspec integrates CodeQL through the `specify security scan` command:

```bash
# Scan with CodeQL (requires --codeql flag)
specify security scan --scanner codeql --language python

# This will:
# 1. Create CodeQL database
# 2. Run security queries
# 3. Convert SARIF to UFFormat
# 4. Output to docs/security/findings.json
```

### Configuration File

Configure CodeQL in `.flowspec/security-config.yml`:

```yaml
scanners:
  codeql:
    enabled: false  # Disabled by default (licensing)
    languages:
      - python
      - javascript
    query_suite: security-extended
    database_dir: .codeql-db
    output_format: sarif
    fail_on:
      - critical
      - high
```

### Enabling CodeQL

After verifying licensing compliance:

```yaml
# .flowspec/security-config.yml
scanners:
  codeql:
    enabled: true  # Enable after licensing review
    languages:
      - python
```

### Unified Finding Format (UFFormat)

Flowspec converts CodeQL SARIF output to UFFormat:

```python
# CodeQL SARIF result
{
  "ruleId": "py/sql-injection",
  "level": "error",
  "message": {
    "text": "This query depends on a user-provided value."
  },
  "locations": [...]
}

# Converted to UFFormat
{
  "id": "CODEQL-CWE-89-001",
  "scanner": "codeql",
  "severity": "high",
  "title": "SQL Injection via user-provided value",
  "description": "This query depends on a user-provided value.",
  "location": {
    "file": "src/auth.py",
    "line_start": 42,
    "line_end": 45,
    "code_snippet": "..."
  },
  "cwe_id": "CWE-89",
  "dataflow": [...]  # CodeQL dataflow path
}
```

### Dataflow Analysis

CodeQL's key differentiator is dataflow analysis. UFFormat preserves this:

```json
{
  "id": "CODEQL-CWE-89-001",
  "dataflow": [
    {
      "step": 1,
      "type": "source",
      "location": {
        "file": "src/api.py",
        "line": 10,
        "snippet": "username = request.POST['username']"
      },
      "description": "User input from HTTP request"
    },
    {
      "step": 2,
      "type": "propagation",
      "location": {
        "file": "src/api.py",
        "line": 15,
        "snippet": "user_data = process_input(username)"
      },
      "description": "Data flows through function call"
    },
    {
      "step": 3,
      "type": "sink",
      "location": {
        "file": "src/db.py",
        "line": 42,
        "snippet": "cursor.execute(f'SELECT * FROM users WHERE name={user_data}')"
      },
      "description": "Dangerous sink: SQL query execution"
    }
  ]
}
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/codeql.yml
name: CodeQL Analysis

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * 1'  # Weekly Monday 8 AM

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [python, javascript]

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: /language:${{ matrix.language }}
```

### GitLab CI

```yaml
# .gitlab-ci.yml
codeql-scan:
  stage: security
  image: python:3.11
  before_script:
    - wget https://github.com/github/codeql-cli-binaries/releases/latest/download/codeql-linux64.zip
    - unzip codeql-linux64.zip
    - export PATH="$PWD/codeql:$PATH"
  script:
    - codeql database create db --language=python --source-root=.
    - codeql database analyze db --format=sarif-latest --output=results.sarif
  artifacts:
    reports:
      sast: results.sarif
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('CodeQL Analysis') {
            steps {
                sh '''
                    codeql database create db --language=python --source-root=.
                    codeql database analyze db \
                        --format=sarif-latest \
                        --output=results.sarif \
                        codeql/python-queries:codeql-suites/python-security-extended.qls
                '''

                recordIssues(
                    tools: [sarif(pattern: 'results.sarif')]
                )
            }
        }
    }
}
```

## Performance Optimization

### Database Size

CodeQL databases can be large. Optimize by:

```bash
# Exclude test files
codeql database create db \
  --language=python \
  --source-root=. \
  --exclude-path=tests/

# Compress database
codeql database bundle --output=db.zip db/
```

### Incremental Analysis

For large codebases, use incremental analysis:

```bash
# Initial full scan
codeql database create db-full --language=python --source-root=.
codeql database analyze db-full --output=baseline.sarif

# Subsequent incremental scans
codeql database create db-incremental --language=python --source-root=. --mode=update
codeql database analyze db-incremental --output=incremental.sarif
```

### Query Performance

Optimize query execution:

```bash
# Use security-only queries (faster)
codeql database analyze db \
  --format=sarif-latest \
  --output=results.sarif \
  codeql/python-queries:codeql-suites/python-security-extended.qls

# Parallel execution
codeql database analyze db \
  --format=sarif-latest \
  --output=results.sarif \
  --threads=4 \
  codeql/python-queries
```

## Troubleshooting

### Issue: "Database creation failed"

**Symptom**: Database creation exits with error

**Solutions**:
```bash
# Ensure clean build
make clean

# Install all dependencies first
pip install -e .

# Use explicit build command
codeql database create db \
  --language=python \
  --source-root=. \
  --command="python -m compileall ."
```

### Issue: "No code detected"

**Symptom**: Database created but empty

**Solutions**:
```bash
# Check language detection
codeql resolve languages

# Verify source root
codeql database create db \
  --language=python \
  --source-root=./src \
  --overwrite
```

### Issue: "Query pack not found"

**Symptom**: `codeql database analyze` can't find queries

**Solutions**:
```bash
# Download query pack
codeql pack download codeql/python-queries

# Use absolute path
codeql database analyze db \
  --format=sarif-latest \
  --output=results.sarif \
  ~/.codeql/queries/codeql-repo/python/ql/src/codeql-suites/python-security-extended.qls
```

### Issue: "Out of memory"

**Symptom**: CodeQL crashes with OOM error

**Solutions**:
```bash
# Increase heap size
export CODEQL_RAM=16384  # 16GB

# Analyze specific directories only
codeql database create db \
  --source-root=src/ \
  --language=python
```

## Best Practices

1. **Licensing First**: Always verify licensing before production use
2. **Security Queries**: Use `security-extended` query suite for vulnerability scanning
3. **Clean Builds**: Always start with a clean build environment
4. **Version Control**: Commit `.codeql/database-schema.json` for reproducibility
5. **CI/CD Integration**: Run CodeQL on every PR and weekly scheduled scans
6. **Dataflow Analysis**: Leverage CodeQL's dataflow paths for triage
7. **Incremental Scans**: Use incremental mode for large codebases
8. **Performance**: Exclude test files and use parallel execution

## Additional Resources

### Official Documentation
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [CodeQL CLI Reference](https://codeql.github.com/docs/codeql-cli/)
- [Query Help](https://codeql.github.com/codeql-query-help/)

### Learning Resources
- [CodeQL Learning Lab](https://github.com/github/codeql-learning-catalog)
- [CodeQL for Security Researchers](https://securitylab.github.com/tools/codeql)
- [Writing CodeQL Queries](https://codeql.github.com/docs/writing-codeql-queries/)

### Community
- [CodeQL GitHub Discussions](https://github.com/github/codeql/discussions)
- [Security Lab](https://securitylab.github.com/)
- [CodeQL Slack](https://codeql.slack.com)

### Flowspec Resources
- [CodeQL Licensing Review](../legal/codeql-licensing-review.md)
- [Security CI/CD Integration](./security-cicd-integration.md)
- [Dataflow Analysis Patterns](../../memory/security/dataflow-analysis.md)
- [CodeQL Analysis Skill](../../.claude/skills/security-codeql.md)

## Next Steps

After setting up CodeQL:

1. **Verify Licensing**: Ensure compliance with [licensing review](../legal/codeql-licensing-review.md)
2. **Run First Scan**: Create database and run security queries
3. **Review Results**: Use [security-codeql skill](../../.claude/skills/security-codeql.md) to interpret findings
4. **CI/CD Integration**: Add to your pipeline with [security-cicd-integration guide](./security-cicd-integration.md)
5. **Custom Queries**: Learn to write custom queries for your specific needs

---

**Last Updated**: 2025-12-04
**Maintained By**: Flowspec Security Team
