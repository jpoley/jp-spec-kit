"""Tests for fix pattern library."""

import pytest

from specify_cli.security.fixer.patterns import (
    FixPatternLibrary,
    DEFAULT_PATTERN_LIBRARY,
)


class TestFixPatternLibrary:
    """Tests for FixPatternLibrary."""

    def test_default_patterns_loaded(self):
        """Test default patterns are loaded on init."""
        library = FixPatternLibrary()

        assert "CWE-89" in library.patterns
        assert "CWE-79" in library.patterns
        assert "CWE-22" in library.patterns
        assert "CWE-798" in library.patterns
        assert "CWE-327" in library.patterns

    def test_get_pattern_exists(self):
        """Test getting an existing pattern."""
        library = FixPatternLibrary()
        pattern = library.get_pattern("CWE-89")

        assert pattern is not None
        assert pattern.name == "SQL Injection"
        assert len(pattern.examples) > 0

    def test_get_pattern_not_exists(self):
        """Test getting a non-existent pattern."""
        library = FixPatternLibrary()
        pattern = library.get_pattern("CWE-999")

        assert pattern is None

    def test_add_pattern(self):
        """Test adding a custom pattern."""
        from specify_cli.security.fixer.models import FixPattern

        library = FixPatternLibrary()
        custom = FixPattern(
            cwe_id="CWE-123",
            name="Custom Vuln",
            description="Custom fix",
            vulnerable_pattern="bad",
            fix_template="good",
        )

        library.add_pattern(custom)

        assert library.get_pattern("CWE-123") == custom


class TestSQLInjectionPattern:
    """Tests for SQL injection fix pattern."""

    @pytest.fixture
    def pattern(self):
        """Get SQL injection pattern."""
        return DEFAULT_PATTERN_LIBRARY.get_pattern("CWE-89")

    def test_has_examples(self, pattern):
        """Test pattern has examples."""
        assert len(pattern.examples) >= 2

    def test_python_example(self, pattern):
        """Test Python fix example."""
        python_examples = [e for e in pattern.examples if e["language"] == "python"]
        assert len(python_examples) > 0

        example = python_examples[0]
        assert "+" in example["before"] or 'f"' in example["before"]
        assert "?" in example["after"] or "execute" in example["after"]


class TestXSSPattern:
    """Tests for XSS fix pattern."""

    @pytest.fixture
    def pattern(self):
        """Get XSS pattern."""
        return DEFAULT_PATTERN_LIBRARY.get_pattern("CWE-79")

    def test_has_examples(self, pattern):
        """Test pattern has examples."""
        assert len(pattern.examples) >= 2

    def test_innerhtml_example(self, pattern):
        """Test innerHTML fix example."""
        innerhtml_example = next(
            (e for e in pattern.examples if "innerHTML" in e["before"]),
            None,
        )
        assert innerhtml_example is not None
        assert "textContent" in innerhtml_example["after"]


class TestPathTraversalPattern:
    """Tests for path traversal fix pattern."""

    @pytest.fixture
    def pattern(self):
        """Get path traversal pattern."""
        return DEFAULT_PATTERN_LIBRARY.get_pattern("CWE-22")

    def test_has_fix_template(self, pattern):
        """Test pattern has fix template."""
        assert "resolve" in pattern.fix_template.lower()
        assert (
            "is_relative_to" in pattern.fix_template
            or "startswith" in pattern.fix_template
        )


class TestHardcodedSecretsPattern:
    """Tests for hardcoded secrets fix pattern."""

    @pytest.fixture
    def pattern(self):
        """Get hardcoded secrets pattern."""
        return DEFAULT_PATTERN_LIBRARY.get_pattern("CWE-798")

    def test_has_examples(self, pattern):
        """Test pattern has examples."""
        assert len(pattern.examples) >= 1

    def test_env_var_example(self, pattern):
        """Test environment variable fix."""
        assert (
            "os.environ" in pattern.fix_template
            or "process.env" in pattern.fix_template
        )


class TestWeakCryptoPattern:
    """Tests for weak crypto fix pattern."""

    @pytest.fixture
    def pattern(self):
        """Get weak crypto pattern."""
        return DEFAULT_PATTERN_LIBRARY.get_pattern("CWE-327")

    def test_has_examples(self, pattern):
        """Test pattern has examples."""
        assert len(pattern.examples) >= 1

    def test_bcrypt_recommendation(self, pattern):
        """Test bcrypt is recommended."""
        assert "bcrypt" in pattern.fix_template.lower()
