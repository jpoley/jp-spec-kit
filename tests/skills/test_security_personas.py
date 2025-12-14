"""Tests for security expert personas.

Validates that persona files are correctly formatted and contain
required sections and knowledge.
"""

import re
from pathlib import Path

import pytest
import yaml


# Persona file paths
SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"
PERSONAS = [
    "security-analyst",
    "patch-engineer",
    "fuzzing-strategist",
    "exploit-researcher",
]


class TestPersonaFiles:
    """Test that persona files exist and are well-formed."""

    @pytest.mark.parametrize("persona_file", PERSONAS)
    def test_persona_file_exists(self, persona_file: str):
        """Test that persona file exists."""
        persona_path = SKILLS_DIR / persona_file / "SKILL.md"
        assert persona_path.exists(), f"Persona file not found: {persona_path}"

    @pytest.mark.parametrize("persona_file", PERSONAS)
    def test_persona_has_yaml_frontmatter(self, persona_file: str):
        """Test that persona has valid YAML frontmatter."""
        persona_path = SKILLS_DIR / persona_file / "SKILL.md"
        content = persona_path.read_text()

        # Check for YAML frontmatter
        assert content.startswith("---\n"), f"{persona_file} missing YAML frontmatter"

        # Extract frontmatter
        parts = content.split("---\n", 2)
        assert len(parts) >= 3, f"{persona_file} malformed YAML frontmatter"

        frontmatter = parts[1]

        # Parse YAML
        try:
            metadata = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            pytest.fail(f"{persona_file} invalid YAML: {e}")

        # Check required fields
        assert "name" in metadata, f"{persona_file} missing 'name' in frontmatter"
        assert "description" in metadata, (
            f"{persona_file} missing 'description' in frontmatter"
        )

    @pytest.mark.parametrize("persona_file", PERSONAS)
    def test_persona_has_required_sections(self, persona_file: str):
        """Test that persona has all required sections."""
        persona_path = SKILLS_DIR / persona_file / "SKILL.md"
        content = persona_path.read_text()

        required_sections = [
            "# @",  # Persona title
            "## Role",
            "## Expertise Areas",
            "## Communication Style",
            "## Tools & Methods",
            "## Use Cases",
            "## Success Criteria",
            "## References",
        ]

        for section in required_sections:
            assert section in content, f"{persona_file} missing section: {section}"

    @pytest.mark.parametrize("persona_file", PERSONAS)
    def test_persona_has_example_interactions(self, persona_file: str):
        """Test that persona has example interactions or use cases."""
        persona_path = SKILLS_DIR / persona_file / "SKILL.md"
        content = persona_path.read_text()

        # Should have either "Example Interactions" or detailed "Use Cases"
        has_examples = (
            "## Example Interactions" in content or "### 1." in content
        )  # Use case numbering
        assert has_examples, (
            f"{persona_file} missing example interactions or detailed use cases"
        )


class TestSecurityAnalystPersona:
    """Test @security-analyst persona specifics."""

    @pytest.fixture
    def persona_content(self) -> str:
        """Load @security-analyst persona content."""
        return (SKILLS_DIR / "security-analyst" / "SKILL.md").read_text()

    def test_has_owasp_knowledge(self, persona_content: str):
        """Test that persona includes OWASP Top 10 mapping."""
        assert "OWASP Top 10" in persona_content
        assert "A01:2021" in persona_content  # OWASP 2021 reference
        assert "Broken Access Control" in persona_content

    def test_has_cvss_scoring(self, persona_content: str):
        """Test that persona includes CVSS scoring methodology."""
        assert "CVSS" in persona_content
        assert "Attack Vector" in persona_content
        assert "Attack Complexity" in persona_content
        assert "Privileges Required" in persona_content

    def test_has_compliance_mapping(self, persona_content: str):
        """Test that persona includes compliance framework mapping."""
        frameworks = ["SOC2", "ISO 27001", "PCI-DSS", "HIPAA"]
        for framework in frameworks:
            assert framework in persona_content, (
                f"Missing compliance framework: {framework}"
            )

    def test_has_cwe_knowledge(self, persona_content: str):
        """Test that persona includes CWE categories."""
        cwes = ["CWE-89", "CWE-79", "CWE-22", "CWE-798", "CWE-327"]
        for cwe in cwes:
            assert cwe in persona_content, f"Missing CWE reference: {cwe}"


class TestPatchEngineerPersona:
    """Test @patch-engineer persona specifics."""

    @pytest.fixture
    def persona_content(self) -> str:
        """Load @patch-engineer persona content."""
        return (SKILLS_DIR / "patch-engineer" / "SKILL.md").read_text()

    def test_has_fix_patterns(self, persona_content: str):
        """Test that persona includes security fix patterns."""
        patterns = [
            "SQL Injection Fixes",
            "XSS Fixes",
            "Path Traversal Fixes",
            "Cryptographic Fixes",
            "Secrets Management",
        ]
        for pattern in patterns:
            assert pattern in persona_content, f"Missing fix pattern: {pattern}"

    def test_has_language_specific_guidance(self, persona_content: str):
        """Test that persona includes language-specific guidance."""
        languages = ["Python", "JavaScript", "Java", "Go"]
        for lang in languages:
            assert lang in persona_content, (
                f"Missing language-specific guidance: {lang}"
            )

    def test_has_fix_review_checklist(self, persona_content: str):
        """Test that persona includes fix review checklist."""
        assert "Fix Review Checklist" in persona_content
        checklist_items = ["Correctness", "Completeness", "Quality", "Testing"]
        for item in checklist_items:
            assert item in persona_content, f"Missing checklist item: {item}"

    def test_has_quality_scoring(self, persona_content: str):
        """Test that persona includes fix quality scoring."""
        assert "Fix Quality Scoring" in persona_content
        assert "10/10" in persona_content  # Score scale
        assert "Excellent" in persona_content  # Quality descriptor


class TestFuzzingStrategistPersona:
    """Test @fuzzing-strategist persona specifics."""

    @pytest.fixture
    def persona_content(self) -> str:
        """Load @fuzzing-strategist persona content."""
        return (SKILLS_DIR / "fuzzing-strategist" / "SKILL.md").read_text()

    def test_has_fuzzing_tools(self, persona_content: str):
        """Test that persona includes fuzzing tools."""
        tools = ["AFL++", "libFuzzer", "Honggfuzz", "Atheris", "OSS-Fuzz"]
        for tool in tools:
            assert tool in persona_content, f"Missing fuzzing tool: {tool}"

    def test_has_fuzzing_methodologies(self, persona_content: str):
        """Test that persona includes fuzzing methodologies."""
        methodologies = [
            "Coverage-Guided",
            "Grammar-Based",
            "Mutation-Based",
        ]
        for method in methodologies:
            assert method in persona_content, f"Missing fuzzing methodology: {method}"

    def test_has_target_analysis(self, persona_content: str):
        """Test that persona includes target analysis guidance."""
        assert "Good Fuzzing Targets" in persona_content
        assert "Poor Fuzzing Targets" in persona_content

    def test_has_harness_templates(self, persona_content: str):
        """Test that persona includes fuzzing harness templates."""
        assert "harness" in persona_content.lower()
        # Should have code examples
        assert "```cpp" in persona_content or "```c" in persona_content
        assert "```python" in persona_content


class TestExploitResearcherPersona:
    """Test @exploit-researcher persona specifics."""

    @pytest.fixture
    def persona_content(self) -> str:
        """Load @exploit-researcher persona content."""
        return (SKILLS_DIR / "exploit-researcher" / "SKILL.md").read_text()

    def test_has_attack_surface_analysis(self, persona_content: str):
        """Test that persona includes attack surface analysis."""
        assert "Attack Surface" in persona_content
        assert "External Attack Surface" in persona_content
        assert "Internal Attack Surface" in persona_content

    def test_has_exploit_techniques(self, persona_content: str):
        """Test that persona includes exploit techniques."""
        techniques = [
            "SQL injection exploitation",
            "XSS exploitation",
            "Path traversal exploitation",
        ]
        for technique in techniques:
            assert technique.lower() in persona_content.lower(), (
                f"Missing exploit technique: {technique}"
            )

    def test_has_vulnerability_chaining(self, persona_content: str):
        """Test that persona includes vulnerability chaining."""
        assert "Vulnerability Chaining" in persona_content
        assert "chain" in persona_content.lower()

    def test_has_attack_scenarios(self, persona_content: str):
        """Test that persona includes attack scenario templates."""
        assert "Attack Scenario" in persona_content
        assert "Attacker Profile" in persona_content
        assert "Impact Assessment" in persona_content

    def test_has_business_impact_guidance(self, persona_content: str):
        """Test that persona includes business impact analysis."""
        assert "Business Impact" in persona_content
        assert "Financial" in persona_content
        assert "Reputation" in persona_content


class TestPersonaIntegration:
    """Test that personas work together cohesively."""

    def test_all_personas_reference_each_other(self):
        """Test that personas reference each other appropriately."""
        for persona_file in PERSONAS:
            content = (SKILLS_DIR / persona_file / "SKILL.md").read_text()

            # Each persona should reference at least 2 other personas
            # Check for both @persona-name and "persona name" formats
            other_personas = [p for p in PERSONAS if p != persona_file]
            references = sum(
                1
                for p in other_personas
                if f"@{p}" in content or p.replace("-", " ") in content.lower()
            )

            assert references >= 2, (
                f"{persona_file} should reference at least 2 other personas (found {references})"
            )

    def test_consistent_formatting(self):
        """Test that all personas follow consistent formatting."""
        for persona_file in PERSONAS:
            content = (SKILLS_DIR / persona_file / "SKILL.md").read_text()

            # Check consistent section markers
            assert re.search(r"^## ", content, re.MULTILINE), (
                f"{persona_file} missing level-2 headers"
            )
            assert re.search(r"^### ", content, re.MULTILINE), (
                f"{persona_file} missing level-3 headers"
            )

            # Check for code examples
            assert "```" in content, f"{persona_file} missing code examples"


class TestDocumentation:
    """Test that persona documentation exists and is complete."""

    def test_persona_guide_exists(self):
        """Test that security personas guide exists."""
        docs_path = Path(__file__).parent.parent.parent / "user-docs" / "user-guides"
        guide_path = docs_path / "security-personas.md"
        assert guide_path.exists(), "Security personas guide not found"

    def test_guide_documents_all_personas(self):
        """Test that guide documents all personas."""
        docs_path = Path(__file__).parent.parent.parent / "user-docs" / "user-guides"
        guide_content = (docs_path / "security-personas.md").read_text()

        for persona_file in PERSONAS:
            persona_name = persona_file.replace(".md", "")
            assert f"@{persona_name}" in guide_content, (
                f"Guide missing documentation for @{persona_name}"
            )

    def test_guide_has_usage_examples(self):
        """Test that guide includes usage examples."""
        docs_path = Path(__file__).parent.parent.parent / "user-docs" / "user-guides"
        guide_content = (docs_path / "security-personas.md").read_text()

        assert "## Examples" in guide_content
        assert "```" in guide_content  # Code examples


class TestProgressiveDisclosure:
    """Test progressive disclosure implementation."""

    def test_personas_not_in_main_skills(self):
        """Test that personas are separate from main skills."""
        # Main skills should reference personas but not duplicate content
        main_triage_skill = SKILLS_DIR / "security-triage.md"

        if main_triage_skill.exists():
            content = main_triage_skill.read_text()

            # Should reference personas but not duplicate their full content
            for persona_file in PERSONAS:
                persona_name = persona_file.replace(".md", "")
                # Should mention persona
                assert f"@{persona_name}" in content or persona_name in content, (
                    f"Main skill should reference @{persona_name}"
                )

    def test_personas_are_independent_files(self):
        """Test that each persona is its own file."""
        for persona_file in PERSONAS:
            persona_path = SKILLS_DIR / persona_file / "SKILL.md"
            assert persona_path.exists()
            assert persona_path.is_file()

            # Each persona should be substantial (>5KB)
            file_size = persona_path.stat().st_size
            assert file_size > 5000, (
                f"{persona_file} too small ({file_size} bytes), should be >5KB"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
