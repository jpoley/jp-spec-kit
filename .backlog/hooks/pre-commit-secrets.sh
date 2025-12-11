#!/usr/bin/env bash
# Pre-commit hook: Scan Task Memory files for potential secrets
#
# This hook scans staged Task Memory files for patterns that might indicate
# secrets (API keys, passwords, tokens, etc.) to prevent accidental commits.
#
# Exit codes:
#   0 - No secrets detected or no memory files staged
#   1 - Potential secrets detected (blocks commit)

set -euo pipefail

# Get list of staged Task Memory files
MEMORY_FILES=$(git diff --cached --name-only | grep -E 'backlog/memory/.*\.md$' || true)

if [ -z "$MEMORY_FILES" ]; then
    # No Task Memory files staged, nothing to check
    exit 0
fi

echo "🔒 Scanning Task Memory files for potential secrets..."

# Secret patterns to detect (case-insensitive)
SECRET_PATTERNS=(
    'api[_-]?key'
    'apikey'
    'password'
    'passwd'
    'secret'
    'token'
    'private[_-]?key'
    'access[_-]?key'
    'client[_-]?secret'
    'bearer[[:space:]]+'
    'authorization:[[:space:]]*basic'
    'aws[_-]?access'
    'ssh[_-]?key'
    'BEGIN[[:space:]]+PRIVATE[[:space:]]+KEY'
    'BEGIN[[:space:]]+RSA[[:space:]]+PRIVATE[[:space:]]+KEY'
)

# Build grep pattern (case-insensitive, extended regex)
PATTERN=$(IFS='|'; echo "${SECRET_PATTERNS[*]}")

SECRETS_FOUND=0

# Check each staged memory file
for file in $MEMORY_FILES; do
    if [ -f "$file" ]; then
        # Use git show to get staged content (not working tree)
        if git show ":$file" | grep -iE "$PATTERN" > /dev/null 2>&1; then
            echo "⚠️  Potential secret detected in: $file"

            # Show context lines (without revealing actual secrets)
            echo "   Matching lines (review carefully):"
            git show ":$file" | grep -iE -n "$PATTERN" | head -5 | sed 's/^/   /'

            if [ $(git show ":$file" | grep -iE "$PATTERN" | wc -l) -gt 5 ]; then
                echo "   ... and more matches"
            fi

            SECRETS_FOUND=1
        fi
    fi
done

if [ $SECRETS_FOUND -eq 1 ]; then
    echo ""
    echo "❌ Commit blocked: Potential secrets detected in Task Memory"
    echo ""
    echo "If these are false positives:"
    echo "  1. Review the files carefully"
    echo "  2. Use git commit --no-verify to bypass this check"
    echo ""
    echo "If these are real secrets:"
    echo "  1. Remove them from Task Memory files"
    echo "  2. Use environment variables or secure vaults instead"
    echo "  3. Never commit secrets to version control"
    echo ""
    exit 1
fi

echo "✅ No secrets detected in Task Memory files"
exit 0
