"""Tests for per-transition validation mode flags in CLI init command.

Tests cover:
- Default behavior with no flags (all NONE)
- Setting individual transition modes (none, keyword, pull-request)
- The --no-validation-prompts flag behavior
- Invalid mode values are handled properly (warning + default to NONE)
- Generated jpspec_workflow.yml file has correct content
"""

from pathlib import Path

import yaml

from specify_cli import generate_jpspec_workflow_yml, WORKFLOW_TRANSITIONS


class TestGenerateJpspecWorkflowYml:
    """Tests for generate_jpspec_workflow_yml function."""

    def test_default_behavior_no_flags(self, tmp_path: Path):
        """Test default behavior with no flags generates all NONE modes."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        assert workflow_file.exists(), "Workflow file should be created"

        content = workflow_file.read_text()
        # All transitions should have NONE validation
        for t in WORKFLOW_TRANSITIONS:
            assert f"name: {t['name']}" in content
            assert "validation: NONE" in content

    def test_default_behavior_with_none_dict(self, tmp_path: Path):
        """Test behavior with None transition_modes dict."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes=None)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        assert workflow_file.exists()

        content = workflow_file.read_text()
        # All transitions should have NONE validation (default)
        assert content.count("validation: NONE") == len(WORKFLOW_TRANSITIONS)

    def test_default_behavior_with_empty_dict(self, tmp_path: Path):
        """Test behavior with empty transition_modes dict."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes={})

        workflow_file = tmp_path / "jpspec_workflow.yml"
        assert workflow_file.exists()

        content = workflow_file.read_text()
        # All transitions should have NONE validation (default)
        assert content.count("validation: NONE") == len(WORKFLOW_TRANSITIONS)


class TestIndividualTransitionModes:
    """Tests for setting individual transition validation modes."""

    def test_single_transition_none_mode(self, tmp_path: Path):
        """Test setting single transition to none mode."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes={"assess": "none"})

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        # All should be NONE since default is NONE
        assert content.count("validation: NONE") == len(WORKFLOW_TRANSITIONS)

    def test_single_transition_keyword_mode(self, tmp_path: Path):
        """Test setting single transition to keyword mode."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes={"assess": "keyword"})

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        # Parse YAML to check specific transition
        # Skip comment lines and parse the YAML
        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assess_transition = next(
            t for t in config["transitions"] if t["name"] == "assess"
        )
        assert assess_transition["validation"] == 'KEYWORD["APPROVED"]'

    def test_single_transition_pull_request_mode(self, tmp_path: Path):
        """Test setting single transition to pull-request mode."""
        generate_jpspec_workflow_yml(
            tmp_path, transition_modes={"implement": "pull-request"}
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        implement_transition = next(
            t for t in config["transitions"] if t["name"] == "implement"
        )
        assert implement_transition["validation"] == "PULL_REQUEST"

    def test_pull_request_underscore_variant(self, tmp_path: Path):
        """Test pull_request (underscore variant) is accepted."""
        generate_jpspec_workflow_yml(
            tmp_path, transition_modes={"validate": "pull_request"}
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        validate_transition = next(
            t for t in config["transitions"] if t["name"] == "validate"
        )
        assert validate_transition["validation"] == "PULL_REQUEST"

    def test_multiple_transitions_different_modes(self, tmp_path: Path):
        """Test setting multiple transitions to different modes."""
        generate_jpspec_workflow_yml(
            tmp_path,
            transition_modes={
                "assess": "keyword",
                "research": "none",
                "specify": "pull-request",
                "plan": "keyword",
                "implement": "pull-request",
                "validate": "none",
                "operate": "keyword",
            },
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        expected = {
            "assess": 'KEYWORD["APPROVED"]',
            "research": "NONE",
            "specify": "PULL_REQUEST",
            "plan": 'KEYWORD["APPROVED"]',
            "implement": "PULL_REQUEST",
            "validate": "NONE",
            "operate": 'KEYWORD["APPROVED"]',
        }

        for t in config["transitions"]:
            assert t["validation"] == expected[t["name"]]

    def test_custom_keyword_format_preserved(self, tmp_path: Path):
        """Test that custom keyword format like KEYWORD["custom"] is preserved."""
        generate_jpspec_workflow_yml(
            tmp_path, transition_modes={"assess": 'keyword["READY"]'}
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assess_transition = next(
            t for t in config["transitions"] if t["name"] == "assess"
        )
        assert assess_transition["validation"] == 'KEYWORD["READY"]'


class TestNoValidationPromptsFlag:
    """Tests for --no-validation-prompts flag behavior."""

    def test_no_validation_prompts_sets_all_to_none(self, tmp_path: Path):
        """Test that no_validation_prompts effectively sets all modes to none."""
        # Simulating the behavior when --no-validation-prompts is used
        # The CLI would set all transition modes to 'none' explicitly
        transition_modes = {
            "assess": "none",
            "research": "none",
            "specify": "none",
            "plan": "none",
            "implement": "none",
            "validate": "none",
            "operate": "none",
        }
        generate_jpspec_workflow_yml(tmp_path, transition_modes=transition_modes)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        assert content.count("validation: NONE") == len(WORKFLOW_TRANSITIONS)


class TestInvalidModeHandling:
    """Tests for invalid mode values."""

    def test_invalid_mode_defaults_to_none(self, tmp_path: Path, capsys):
        """Test that invalid mode values default to NONE with warning."""
        generate_jpspec_workflow_yml(
            tmp_path, transition_modes={"assess": "invalid-mode"}
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assess_transition = next(
            t for t in config["transitions"] if t["name"] == "assess"
        )
        # Invalid mode should default to NONE
        assert assess_transition["validation"] == "NONE"

    def test_multiple_invalid_modes(self, tmp_path: Path):
        """Test multiple invalid modes all default to NONE."""
        generate_jpspec_workflow_yml(
            tmp_path,
            transition_modes={
                "assess": "bad-mode",
                "research": "another-invalid",
                "specify": "not-a-mode",
            },
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        for t in config["transitions"]:
            if t["name"] in ["assess", "research", "specify"]:
                assert t["validation"] == "NONE"


class TestGeneratedFileContent:
    """Tests for the structure and content of generated jpspec_workflow.yml."""

    def test_file_has_correct_header_comments(self, tmp_path: Path):
        """Test that generated file has proper header comments."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        assert "# JPSpec Workflow Configuration" in content
        assert "# Generated by: specify init" in content
        assert "# Validation modes:" in content
        assert "#   NONE - No gate" in content
        assert '#   KEYWORD["<string>"]' in content
        assert "#   PULL_REQUEST - Require PR to be merged" in content

    def test_file_has_version(self, tmp_path: Path):
        """Test that generated file has version field."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assert config["version"] == "1.0"

    def test_all_transitions_present(self, tmp_path: Path):
        """Test that all workflow transitions are present in generated file."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assert len(config["transitions"]) == len(WORKFLOW_TRANSITIONS)

        expected_names = {t["name"] for t in WORKFLOW_TRANSITIONS}
        actual_names = {t["name"] for t in config["transitions"]}
        assert expected_names == actual_names

    def test_transition_has_required_fields(self, tmp_path: Path):
        """Test that each transition has name, from, to, and validation fields."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        for transition in config["transitions"]:
            assert "name" in transition
            assert "from" in transition
            assert "to" in transition
            assert "validation" in transition

    def test_transition_from_to_states_match_config(self, tmp_path: Path):
        """Test that transition from/to states match WORKFLOW_TRANSITIONS config."""
        generate_jpspec_workflow_yml(tmp_path)

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        transitions_by_name = {t["name"]: t for t in WORKFLOW_TRANSITIONS}

        for t in config["transitions"]:
            expected = transitions_by_name[t["name"]]
            assert t["from"] == expected["from"]
            assert t["to"] == expected["to"]


class TestModeNormalization:
    """Tests for mode string normalization."""

    def test_uppercase_mode_normalized(self, tmp_path: Path):
        """Test that uppercase mode strings are normalized."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes={"assess": "NONE"})

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        assess_transition = next(
            t for t in config["transitions"] if t["name"] == "assess"
        )
        assert assess_transition["validation"] == "NONE"

    def test_mixed_case_mode_normalized(self, tmp_path: Path):
        """Test that mixed case mode strings are normalized."""
        generate_jpspec_workflow_yml(tmp_path, transition_modes={"research": "Keyword"})

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        research_transition = next(
            t for t in config["transitions"] if t["name"] == "research"
        )
        assert research_transition["validation"] == 'KEYWORD["APPROVED"]'

    def test_pull_request_hyphen_normalized(self, tmp_path: Path):
        """Test that pull-request with hyphen is normalized."""
        generate_jpspec_workflow_yml(
            tmp_path, transition_modes={"specify": "Pull-Request"}
        )

        workflow_file = tmp_path / "jpspec_workflow.yml"
        content = workflow_file.read_text()

        yaml_content = "\n".join(
            line for line in content.split("\n") if not line.startswith("#")
        )
        config = yaml.safe_load(yaml_content)

        specify_transition = next(
            t for t in config["transitions"] if t["name"] == "specify"
        )
        assert specify_transition["validation"] == "PULL_REQUEST"


class TestWorkflowTransitionsConfig:
    """Tests for WORKFLOW_TRANSITIONS configuration."""

    def test_all_transitions_have_required_keys(self):
        """Test that all WORKFLOW_TRANSITIONS have required keys."""
        required_keys = {"name", "from", "to", "default"}
        for t in WORKFLOW_TRANSITIONS:
            assert required_keys.issubset(t.keys()), f"Transition {t} missing keys"

    def test_all_defaults_are_none(self):
        """Test that all default validation modes are NONE."""
        for t in WORKFLOW_TRANSITIONS:
            assert t["default"] == "NONE", (
                f"Transition {t['name']} has non-NONE default"
            )

    def test_expected_transitions_exist(self):
        """Test that expected transitions are defined."""
        expected = [
            "assess",
            "research",
            "specify",
            "plan",
            "implement",
            "validate",
            "operate",
        ]
        actual = [t["name"] for t in WORKFLOW_TRANSITIONS]
        assert actual == expected

    def test_transition_state_chain(self):
        """Test that transitions form a proper state chain."""
        expected_chain = [
            ("To Do", "Assessed"),
            ("Assessed", "Researched"),
            ("Researched", "Specified"),
            ("Specified", "Planned"),
            ("Planned", "In Implementation"),
            ("In Implementation", "Validated"),
            ("Validated", "Deployed"),
        ]

        actual_chain = [(t["from"], t["to"]) for t in WORKFLOW_TRANSITIONS]
        assert actual_chain == expected_chain
