# JP Spec Kit - Makefile
# Development and maintenance commands

.PHONY: help install test lint format clean dev-validate dev-fix dev-status

# Default target
help:
	@echo "JP Spec Kit - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Development:"
	@echo "  make install          - Install dependencies with uv"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Run linter (ruff check)"
	@echo "  make format           - Format code (ruff format)"
	@echo "  make clean            - Clean build artifacts"
	@echo ""
	@echo "Development Setup Management:"
	@echo "  make dev-validate     - Validate dev setup"
	@echo "  make dev-fix          - Fix dev setup (recreate symlinks)"
	@echo "  make dev-status       - Show dev setup status"
	@echo ""
	@echo "CLI:"
	@echo "  make cli-install      - Install CLI locally"
	@echo "  make cli-uninstall    - Uninstall CLI"
	@echo ""

# ============================================================
# DEVELOPMENT COMMANDS
# ============================================================

install:
	@echo "Installing dependencies..."
	uv sync

test:
	@echo "Running tests..."
	uv run pytest tests/ -v

test-dev:
	@echo "Running development setup tests..."
	uv run pytest tests/test_command_*.py -v

lint:
	@echo "Running linter..."
	uv run ruff check .

format:
	@echo "Formatting code..."
	uv run ruff format .

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

# ============================================================
# DEVELOPMENT SETUP MANAGEMENT
# ============================================================

dev-validate:
	@echo "Validating development setup..."
	@echo ""
	@echo "Checking for non-symlink .md files in .claude/commands/..."
	@if find .claude/commands -name "*.md" -type f 2>/dev/null | grep -q .; then \
		echo "❌ ERROR: Found non-symlink .md files:"; \
		find .claude/commands -name "*.md" -type f; \
		exit 1; \
	else \
		echo "✓ All .md files are symlinks"; \
	fi
	@echo ""
	@echo "Checking for broken symlinks..."
	@if find .claude/commands -type l ! -exec test -e {} \; -print 2>/dev/null | grep -q .; then \
		echo "❌ ERROR: Found broken symlinks:"; \
		find .claude/commands -type l ! -exec test -e {} \; -print; \
		exit 1; \
	else \
		echo "✓ All symlinks resolve correctly"; \
	fi
	@echo ""
	@echo "✓ Development setup validation passed"

dev-fix:
	@echo "Fixing development setup..."
	@echo ""
	@echo "Step 1: Backing up current state..."
	@if [ -d .claude/commands/jpspec ]; then \
		echo "  - Found jpspec directory"; \
	fi
	@if [ -d .claude/commands/speckit ]; then \
		echo "  - Found speckit directory"; \
	fi
	@echo ""
	@echo "Step 2: Removing existing symlinks..."
	@rm -rf .claude/commands/jpspec .claude/commands/speckit 2>/dev/null || true
	@echo "  ✓ Removed"
	@echo ""
	@echo "Step 3: Recreating symlinks with dev-setup command..."
	@uv run specify dev-setup --force
	@echo ""
	@echo "Step 4: Validating new setup..."
	@echo "  - Checking symlinks..."
	@if find .claude/commands -name "*.md" -type f 2>/dev/null | grep -q .; then \
		echo "  ❌ Still found non-symlink files"; \
		exit 1; \
	else \
		echo "  ✓ All files are symlinks"; \
	fi
	@echo ""
	@echo "=========================================="
	@echo "✓ Development setup restored successfully"
	@echo "=========================================="

dev-status:
	@echo "=========================================="
	@echo "Development Setup Status"
	@echo "=========================================="
	@echo ""
	@echo "=== .claude/commands/ structure ==="
	@ls -la .claude/commands/ 2>/dev/null || echo "Directory does not exist"
	@echo ""
	@if [ -d .claude/commands/speckit ]; then \
		echo "=== speckit commands ==="; \
		ls -la .claude/commands/speckit/ | grep -E '\.md$$' || echo "No .md files"; \
		echo ""; \
	fi
	@if [ -d .claude/commands/jpspec ]; then \
		echo "=== jpspec commands ==="; \
		ls -la .claude/commands/jpspec/ | grep -E '\.md$$' || echo "No .md files"; \
		echo ""; \
	fi
	@echo "=== Symlink verification ==="
	@TOTAL=$$(find .claude/commands -name "*.md" 2>/dev/null | wc -l); \
	SYMLINKS=$$(find .claude/commands -name "*.md" -type l 2>/dev/null | wc -l); \
	FILES=$$(find .claude/commands -name "*.md" -type f 2>/dev/null | wc -l); \
	echo "Total .md files: $$TOTAL"; \
	echo "Symlinks: $$SYMLINKS"; \
	echo "Regular files: $$FILES"; \
	if [ $$FILES -gt 0 ]; then \
		echo ""; \
		echo "❌ WARNING: Found regular files (should be symlinks):"; \
		find .claude/commands -name "*.md" -type f; \
	fi
	@echo ""

# ============================================================
# CLI COMMANDS
# ============================================================

cli-install:
	@echo "Installing CLI..."
	uv tool install . --force
	@echo "✓ CLI installed"
	@echo ""
	@echo "Verify with: specify --version"

cli-uninstall:
	@echo "Uninstalling CLI..."
	uv tool uninstall specify-cli || true
	@echo "✓ CLI uninstalled"

# ============================================================
# CI/CD SIMULATION
# ============================================================

ci-local:
	@echo "Running local CI simulation..."
	@echo ""
	@echo "Step 1: Linting..."
	@make lint
	@echo ""
	@echo "Step 2: Testing..."
	@make test
	@echo ""
	@echo "Step 3: Development setup validation..."
	@make dev-validate
	@echo ""
	@echo "=========================================="
	@echo "✓ Local CI simulation passed"
	@echo "=========================================="
