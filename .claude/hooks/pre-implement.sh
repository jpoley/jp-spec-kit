#!/usr/bin/env bash
# Pre-implementation quality gates
# Ensures spec quality before /flow:implement proceeds

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1
EXIT_ERROR=2

# Default paths
SPEC_DIR="${SPEC_DIR:-docs/prd}"
ADR_DIR="${ADR_DIR:-docs/adr}"
SPEC_FILE="${SPEC_DIR}/spec.md"
PLAN_FILE="${ADR_DIR}/plan.md"
TASKS_FILE="tasks.md"

# Quality threshold
QUALITY_THRESHOLD=70

# Gate results
GATES_PASSED=true
GATE_ERRORS=()

# Parse arguments for --skip-quality-gates flag
SKIP_GATES=false
for arg in "$@"; do
    if [[ "$arg" == "--skip-quality-gates" ]]; then
        SKIP_GATES=true
        break
    fi
done

# If skip flag is set, bypass all gates with warning
if [[ "$SKIP_GATES" == "true" ]]; then
    echo -e "${YELLOW}⚠ WARNING: Quality gates bypassed with --skip-quality-gates${NC}"
    echo "This may lead to unclear requirements and implementation issues."
    echo "Logging bypass decision..."
    exit $EXIT_SUCCESS
fi

echo "Running pre-implementation quality gates..."
echo ""

#########################################
# Gate 1: Required Files Validation
#########################################
echo "Gate 1: Checking required files..."

if [[ ! -f "$SPEC_FILE" ]]; then
    GATES_PASSED=false
    GATE_ERRORS+=("${RED}✗${NC} Missing required file: $SPEC_FILE")
    GATE_ERRORS+=("  → Create spec using /flow:specify")
else
    echo -e "${GREEN}✓${NC} spec.md exists"
fi

if [[ ! -f "$PLAN_FILE" ]]; then
    GATES_PASSED=false
    GATE_ERRORS+=("${RED}✗${NC} Missing required file: $PLAN_FILE")
    GATE_ERRORS+=("  → Create plan using /flow:plan")
else
    echo -e "${GREEN}✓${NC} plan.md exists"
fi

if [[ ! -f "$TASKS_FILE" ]]; then
    GATES_PASSED=false
    GATE_ERRORS+=("${RED}✗${NC} Missing required file: $TASKS_FILE")
    GATE_ERRORS+=("  → Create tasks using /speckit:tasks")
else
    echo -e "${GREEN}✓${NC} tasks.md exists"
fi

echo ""

#########################################
# Gate 2: Spec Completeness Check
#########################################
echo "Gate 2: Checking spec completeness..."

if [[ -f "$SPEC_FILE" ]]; then
    # Define ambiguity markers to detect
    MARKERS=(
        "NEEDS CLARIFICATION"
        "\[TBD\]"
        "\[TODO\]"
        "???"
        "PLACEHOLDER"
        "<insert>"
    )

    MARKER_FOUND=false
    MARKER_LOCATIONS=()

    for marker in "${MARKERS[@]}"; do
        # Use grep to find markers with line numbers
        # -n: line numbers, -i: case insensitive
        if grep -ni "$marker" "$SPEC_FILE" > /dev/null 2>&1; then
            MARKER_FOUND=true
            # Get actual locations
            while IFS=: read -r line_num line_content; do
                MARKER_LOCATIONS+=("  - Line $line_num: $(echo "$line_content" | sed 's/^[[:space:]]*//' | cut -c1-80)")
            done < <(grep -ni "$marker" "$SPEC_FILE")
        fi
    done

    if [[ "$MARKER_FOUND" == "true" ]]; then
        GATES_PASSED=false
        GATE_ERRORS+=("${RED}✗${NC} Unresolved markers found in spec.md:")
        GATE_ERRORS+=("${MARKER_LOCATIONS[@]}")
        GATE_ERRORS+=("  → Resolve all markers before implementation")
    else
        echo -e "${GREEN}✓${NC} No unresolved markers found"
    fi

    # Check for empty spec
    if [[ ! -s "$SPEC_FILE" ]]; then
        GATES_PASSED=false
        GATE_ERRORS+=("${RED}✗${NC} spec.md is empty")
        GATE_ERRORS+=("  → Create specification using /flow:specify")
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping completeness check (spec.md not found)"
fi

echo ""

#########################################
# Gate 3: Constitutional Compliance Check
#########################################
echo "Gate 3: Checking constitutional compliance..."

if [[ -f "$SPEC_FILE" ]]; then
    CONSTITUTIONAL_VIOLATIONS=()

    # Check for DCO sign-off mention
    if ! grep -qi "sign-off\|DCO\|git commit -s" "$SPEC_FILE"; then
        CONSTITUTIONAL_VIOLATIONS+=("  - Missing DCO sign-off requirement mention")
    fi

    # Check for test mention (from constitution: Test-First is NON-NEGOTIABLE)
    if ! grep -qi "test\|testing\|pytest\|TDD" "$SPEC_FILE"; then
        CONSTITUTIONAL_VIOLATIONS+=("  - No mention of testing requirements")
    fi

    # Check for acceptance criteria
    if ! grep -qi "acceptance criteria\|acceptance criterion" "$SPEC_FILE"; then
        CONSTITUTIONAL_VIOLATIONS+=("  - No acceptance criteria defined")
    fi

    if [[ ${#CONSTITUTIONAL_VIOLATIONS[@]} -gt 0 ]]; then
        GATES_PASSED=false
        GATE_ERRORS+=("${RED}✗${NC} Constitutional compliance violations found:")
        GATE_ERRORS+=("${CONSTITUTIONAL_VIOLATIONS[@]}")
        GATE_ERRORS+=("  → Ensure spec follows constitutional requirements in memory/constitution.md")
    else
        echo -e "${GREEN}✓${NC} Constitutional compliance verified"
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping constitutional check (spec.md not found)"
fi

echo ""

#########################################
# Gate 4: Spec Quality Threshold Check
#########################################
echo "Gate 4: Checking spec quality threshold (>= $QUALITY_THRESHOLD)..."

if [[ -f "$SPEC_FILE" ]]; then
    # Try to use the quality scorer if available
    if command -v specify > /dev/null 2>&1; then
        # Run quality check
        QUALITY_OUTPUT=$(specify quality "$SPEC_FILE" --json 2>&1 || true)

        # Try to parse score from JSON output
        if command -v jq > /dev/null 2>&1; then
            QUALITY_SCORE=$(echo "$QUALITY_OUTPUT" | jq -r '.overall_score // empty' 2>/dev/null || echo "")
        else
            # Fallback: try to extract score from output
            QUALITY_SCORE=$(echo "$QUALITY_OUTPUT" | grep -oP 'overall_score["\s:]+\K[\d.]+' || echo "")
        fi

        if [[ -n "$QUALITY_SCORE" ]]; then
            # Compare scores (bash doesn't do floating point, so use bc or awk)
            if command -v bc > /dev/null 2>&1; then
                SCORE_OK=$(echo "$QUALITY_SCORE >= $QUALITY_THRESHOLD" | bc -l)
            else
                # Fallback: use awk for comparison
                SCORE_OK=$(awk -v score="$QUALITY_SCORE" -v threshold="$QUALITY_THRESHOLD" 'BEGIN { print (score >= threshold) ? 1 : 0 }')
            fi

            if [[ "$SCORE_OK" -eq 1 ]]; then
                echo -e "${GREEN}✓${NC} Quality score: $QUALITY_SCORE/100 (threshold: $QUALITY_THRESHOLD)"
            else
                GATES_PASSED=false
                GATE_ERRORS+=("${RED}✗${NC} Quality score: $QUALITY_SCORE/100 (threshold: $QUALITY_THRESHOLD)")

                # Try to extract recommendations
                if command -v jq > /dev/null 2>&1; then
                    RECOMMENDATIONS=$(echo "$QUALITY_OUTPUT" | jq -r '.recommendations[]? // empty' 2>/dev/null || true)
                    if [[ -n "$RECOMMENDATIONS" ]]; then
                        GATE_ERRORS+=("  Recommendations:")
                        while IFS= read -r rec; do
                            GATE_ERRORS+=("  - $rec")
                        done <<< "$RECOMMENDATIONS"
                    fi
                fi

                GATE_ERRORS+=("  → Improve spec quality using /speckit:clarify")
            fi
        else
            echo -e "${YELLOW}⚠${NC} Could not parse quality score from output"
            echo "  Skipping quality threshold check"
        fi
    else
        echo -e "${YELLOW}⚠${NC} 'specify' command not found, skipping quality scorer"
        echo "  Install with: uv tool install . --force"
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping quality check (spec.md not found)"
fi

echo ""
echo "=========================================="

# Print results
if [[ "$GATES_PASSED" == "true" ]]; then
    echo -e "${GREEN}✅ All quality gates passed. Proceeding with implementation.${NC}"
    exit $EXIT_SUCCESS
else
    echo -e "${RED}❌ Quality gates failed:${NC}"
    echo ""
    for error in "${GATE_ERRORS[@]}"; do
        echo -e "$error"
    done
    echo ""
    echo -e "${YELLOW}Run with --skip-quality-gates to bypass (NOT RECOMMENDED).${NC}"
    exit $EXIT_FAILURE
fi
