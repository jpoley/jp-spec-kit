# run-local-ci.ps1 - Simulate CI/CD pipeline locally (Inner Loop)
#
# This script runs the same checks that will run in GitHub Actions CI,
# allowing you to catch issues before pushing to remote.
#
# Usage: .\scripts\powershell\run-local-ci.ps1
#

$ErrorActionPreference = "Stop"

# Track overall status
$script:OverallStatus = 0

Write-Host "========================================" -ForegroundColor Blue
Write-Host "  Local CI Simulation (Inner Loop)" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

function Print-Step {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Blue
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
    $script:OverallStatus = 1
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Step 1: Check Python version
Print-Step "Step 1: Checking Python version"
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.1[1-9]") {
        Print-Success "Python version is 3.11+"
    } else {
        Print-Error "Python version must be 3.11 or higher"
        Write-Host $pythonVersion
    }
} catch {
    Print-Error "Python is not installed or not in PATH"
}
Write-Host ""

# Step 2: Check dependencies
Print-Step "Step 2: Checking dependencies"
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Print-Success "uv is installed"
} else {
    Print-Error "uv is not installed. Install from: https://docs.astral.sh/uv/"
}
Write-Host ""

# Step 3: Sync dependencies
Print-Step "Step 3: Syncing dependencies"
try {
    uv sync
    Print-Success "Dependencies synced successfully"
} catch {
    Print-Error "Failed to sync dependencies"
}
Write-Host ""

# Step 4: Code formatting check
Print-Step "Step 4: Checking code formatting (ruff format)"
try {
    ruff format --check .
    Print-Success "Code formatting is correct"
} catch {
    Print-Warning "Code formatting issues found. Run: ruff format ."
    $script:OverallStatus = 1
}
Write-Host ""

# Step 5: Linting
Print-Step "Step 5: Running linter (ruff check)"
try {
    ruff check .
    Print-Success "Linting passed"
} catch {
    Print-Error "Linting failed. Run: ruff check . --fix"
}
Write-Host ""

# Step 6: Type checking
Print-Step "Step 6: Type checking"
if (Get-Command mypy -ErrorAction SilentlyContinue) {
    try {
        mypy src/
        Print-Success "Type checking passed"
    } catch {
        Print-Error "Type checking failed"
    }
} else {
    Print-Warning "mypy not installed, skipping type checking"
}
Write-Host ""

# Step 7: Run tests
Print-Step "Step 7: Running tests (pytest)"
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    try {
        pytest tests/ -v
        Print-Success "All tests passed"
    } catch {
        Print-Error "Tests failed"
    }
} else {
    Print-Error "pytest not installed"
}
Write-Host ""

# Step 8: Check test coverage
Print-Step "Step 8: Checking test coverage"
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    try {
        pytest tests/ --cov=src/specify_cli --cov-report=term-missing --cov-fail-under=0
        Print-Success "Coverage report generated"
    } catch {
        Print-Warning "Coverage check had issues"
    }
} else {
    Print-Warning "Skipping coverage (pytest not installed)"
}
Write-Host ""

# Step 9: Build package
Print-Step "Step 9: Building package"
try {
    uv build
    Print-Success "Package built successfully"
} catch {
    Print-Error "Package build failed"
}
Write-Host ""

# Step 10: Install and test CLI
Print-Step "Step 10: Testing CLI installation"
try {
    uv tool install . --force
    Print-Success "CLI installed successfully"

    specflow --help | Out-Null
    Print-Success "CLI is functional"
} catch {
    Print-Error "CLI installation or execution failed"
}
Write-Host ""

# Final summary
Write-Host "========================================" -ForegroundColor Blue
Write-Host "  Summary" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue

if ($script:OverallStatus -eq 0) {
    Write-Host "✓ All checks passed!" -ForegroundColor Green
    Write-Host "  Your code is ready to push." -ForegroundColor Green
} else {
    Write-Host "✗ Some checks failed." -ForegroundColor Red
    Write-Host "  Please fix the issues before pushing." -ForegroundColor Red
}
Write-Host ""

exit $script:OverallStatus
