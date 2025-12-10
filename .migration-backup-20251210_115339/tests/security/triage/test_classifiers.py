"""Tests for triage classifiers."""

from pathlib import Path
from unittest.mock import Mock


from specify_cli.security.models import Finding, Location, Severity
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.default import DefaultClassifier
from specify_cli.security.triage.classifiers.sql_injection import (
    SQLInjectionClassifier,
)
from specify_cli.security.triage.classifiers.xss import XSSClassifier
from specify_cli.security.triage.classifiers.path_traversal import (
    PathTraversalClassifier,
)
from specify_cli.security.triage.classifiers.hardcoded_secrets import (
    HardcodedSecretsClassifier,
)
from specify_cli.security.triage.classifiers.weak_crypto import WeakCryptoClassifier


def make_finding(
    title: str = "Test Finding",
    severity: Severity = Severity.HIGH,
    cwe_id: str | None = None,
    code_snippet: str = "",
    file_path: str = "test.py",
) -> Finding:
    """Create a test finding."""
    return Finding(
        id="TEST-001",
        scanner="test",
        severity=severity,
        title=title,
        description="Test description",
        location=Location(
            file=Path(file_path),
            line_start=10,
            line_end=12,
            code_snippet=code_snippet,
        ),
        cwe_id=cwe_id,
    )


class TestDefaultClassifier:
    """Tests for DefaultClassifier."""

    def test_heuristic_high_severity(self):
        """Test high severity gets needs investigation."""
        classifier = DefaultClassifier()
        finding = make_finding(severity=Severity.HIGH)

        result = classifier.classify(finding)

        assert result.classification == Classification.NEEDS_INVESTIGATION
        assert result.confidence >= 0.5

    def test_heuristic_low_severity(self):
        """Test low severity gets needs investigation."""
        classifier = DefaultClassifier()
        finding = make_finding(severity=Severity.LOW)

        result = classifier.classify(finding)

        assert result.classification == Classification.NEEDS_INVESTIGATION

    def test_with_mocked_llm(self):
        """Test classification with mocked LLM."""
        mock_llm = Mock()
        mock_llm.complete.return_value = """
        {
            "classification": "TP",
            "confidence": 0.9,
            "reasoning": "Real vulnerability"
        }
        """
        classifier = DefaultClassifier(mock_llm)
        finding = make_finding()

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE
        assert result.confidence == 0.9


class TestSQLInjectionClassifier:
    """Tests for SQLInjectionClassifier."""

    def test_supported_cwes(self):
        """Test supported CWE list."""
        classifier = SQLInjectionClassifier()
        assert "CWE-89" in classifier.supported_cwes

    def test_heuristic_parameterized_query(self):
        """Test parameterized query detected as FP."""
        classifier = SQLInjectionClassifier()
        finding = make_finding(
            cwe_id="CWE-89",
            code_snippet='cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))',
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE
        assert result.confidence >= 0.7

    def test_heuristic_string_concatenation(self):
        """Test string concatenation detected as TP."""
        classifier = SQLInjectionClassifier()
        finding = make_finding(
            cwe_id="CWE-89",
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE
        assert result.confidence >= 0.7

    def test_heuristic_fstring(self):
        """Test f-string detected as TP."""
        classifier = SQLInjectionClassifier()
        finding = make_finding(
            cwe_id="CWE-89",
            code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE


class TestXSSClassifier:
    """Tests for XSSClassifier."""

    def test_supported_cwes(self):
        """Test supported CWE list."""
        classifier = XSSClassifier()
        assert "CWE-79" in classifier.supported_cwes

    def test_heuristic_innerhtml(self):
        """Test innerHTML detected as TP."""
        classifier = XSSClassifier()
        finding = make_finding(
            cwe_id="CWE-79",
            code_snippet="element.innerHTML = userInput",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE

    def test_heuristic_textcontent(self):
        """Test textContent detected as FP."""
        classifier = XSSClassifier()
        finding = make_finding(
            cwe_id="CWE-79",
            code_snippet="element.textContent = userInput",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE

    def test_heuristic_dangerouslysetinnerhtml(self):
        """Test React dangerouslySetInnerHTML detected as TP."""
        classifier = XSSClassifier()
        finding = make_finding(
            cwe_id="CWE-79",
            code_snippet="<div dangerouslySetInnerHTML={{__html: userInput}} />",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE


class TestPathTraversalClassifier:
    """Tests for PathTraversalClassifier."""

    def test_supported_cwes(self):
        """Test supported CWE list."""
        classifier = PathTraversalClassifier()
        assert "CWE-22" in classifier.supported_cwes

    def test_heuristic_realpath_validation(self):
        """Test realpath validation detected as FP."""
        classifier = PathTraversalClassifier()
        finding = make_finding(
            cwe_id="CWE-22",
            code_snippet="path = os.path.realpath(user_path)\nif path.startswith(base_dir):",
        )

        result = classifier.classify(finding)

        # Should detect validation
        assert result.classification in (
            Classification.FALSE_POSITIVE,
            Classification.NEEDS_INVESTIGATION,
        )

    def test_heuristic_open_without_validation(self):
        """Test open() without validation detected as TP."""
        classifier = PathTraversalClassifier()
        finding = make_finding(
            cwe_id="CWE-22",
            code_snippet="with open(user_path) as f:\n    data = f.read()",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE


class TestHardcodedSecretsClassifier:
    """Tests for HardcodedSecretsClassifier."""

    def test_supported_cwes(self):
        """Test supported CWE list."""
        classifier = HardcodedSecretsClassifier()
        assert "CWE-798" in classifier.supported_cwes

    def test_heuristic_dummy_value(self):
        """Test dummy/placeholder value detected as FP."""
        classifier = HardcodedSecretsClassifier()
        finding = make_finding(
            cwe_id="CWE-798",
            code_snippet='API_KEY = "your-api-key-here"',
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE
        assert (
            "placeholder" in result.reasoning.lower()
            or "dummy" in result.reasoning.lower()
        )

    def test_heuristic_test_file(self):
        """Test secret in test file detected as FP."""
        classifier = HardcodedSecretsClassifier()
        finding = make_finding(
            cwe_id="CWE-798",
            code_snippet='SECRET_KEY = "a1b2c3d4e5f6g7h8i9j0"',
            file_path="tests/test_auth.py",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE
        assert "test" in result.reasoning.lower()

    def test_heuristic_high_entropy_secret(self):
        """Test high-entropy secret in prod detected as TP."""
        classifier = HardcodedSecretsClassifier()
        # High entropy string
        finding = make_finding(
            cwe_id="CWE-798",
            code_snippet='API_KEY = "sk-aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5"',
            file_path="src/config.py",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE


class TestWeakCryptoClassifier:
    """Tests for WeakCryptoClassifier."""

    def test_supported_cwes(self):
        """Test supported CWE list."""
        classifier = WeakCryptoClassifier()
        assert "CWE-327" in classifier.supported_cwes

    def test_heuristic_md5_security(self):
        """Test MD5 for security detected as TP."""
        classifier = WeakCryptoClassifier()
        finding = make_finding(
            cwe_id="CWE-327",
            code_snippet="password_hash = hashlib.md5(password.encode()).hexdigest()",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.TRUE_POSITIVE

    def test_heuristic_md5_checksum(self):
        """Test MD5 for checksum detected as FP."""
        classifier = WeakCryptoClassifier()
        finding = make_finding(
            cwe_id="CWE-327",
            code_snippet="file_checksum = hashlib.md5(file_contents).hexdigest()",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE
        assert "checksum" in result.reasoning.lower()

    def test_heuristic_aes256(self):
        """Test AES-256 detected as FP."""
        classifier = WeakCryptoClassifier()
        finding = make_finding(
            cwe_id="CWE-327",
            code_snippet="cipher = AES.new(key, AES.MODE_GCM)",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE

    def test_heuristic_bcrypt(self):
        """Test bcrypt detected as FP."""
        classifier = WeakCryptoClassifier()
        finding = make_finding(
            cwe_id="CWE-327",
            code_snippet="hashed = bcrypt.hashpw(password, bcrypt.gensalt())",
        )

        result = classifier.classify(finding)

        assert result.classification == Classification.FALSE_POSITIVE
