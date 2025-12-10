"""Tests for security workflow files.

These tests validate that GitHub Actions workflow files follow best practices
and don't contain common security issues.
"""

import re
from pathlib import Path

import pytest
import yaml


def load_workflow(path: Path) -> dict:
    """Load a workflow file, handling YAML 1.1 'on' -> True issue."""
    with open(path) as f:
        content = f.read()
    # PyYAML interprets 'on' as True (YAML 1.1 boolean)
    # Replace 'on:' at the start of a line with '"on":'
    content = re.sub(r"^on:", '"on":', content, flags=re.MULTILINE)
    return yaml.safe_load(content)


# Path to workflow files
WORKFLOWS_DIR = Path(__file__).parent.parent.parent / ".github" / "workflows"
SECURITY_CONFIG = (
    Path(__file__).parent.parent.parent / ".github" / "security-config.yml"
)


class TestSecurityWorkflowFiles:
    """Test that security workflow files exist and are valid."""

    def test_security_scan_workflow_exists(self):
        """Test that security-scan.yml exists."""
        workflow_file = WORKFLOWS_DIR / "security-scan.yml"
        assert workflow_file.exists(), "security-scan.yml should exist"

    def test_security_workflow_exists(self):
        """Test that security.yml exists."""
        workflow_file = WORKFLOWS_DIR / "security.yml"
        assert workflow_file.exists(), "security.yml should exist"

    def test_security_parallel_workflow_exists(self):
        """Test that security-parallel.yml exists."""
        workflow_file = WORKFLOWS_DIR / "security-parallel.yml"
        assert workflow_file.exists(), "security-parallel.yml should exist"

    def test_security_config_exists(self):
        """Test that security-config.yml exists."""
        assert SECURITY_CONFIG.exists(), "security-config.yml should exist"


class TestSecurityScanWorkflow:
    """Test security-scan.yml workflow configuration."""

    @pytest.fixture
    def workflow(self):
        """Load the security-scan.yml workflow."""
        workflow_file = WORKFLOWS_DIR / "security-scan.yml"
        return load_workflow(workflow_file)

    @pytest.fixture
    def workflow_content(self):
        """Load the raw content of security-scan.yml."""
        workflow_file = WORKFLOWS_DIR / "security-scan.yml"
        return workflow_file.read_text()

    def test_workflow_is_reusable(self, workflow):
        """Test that workflow is configured as reusable."""
        assert "workflow_call" in workflow["on"], "Should be a reusable workflow"

    def test_has_required_inputs(self, workflow):
        """Test that workflow has required inputs."""
        inputs = workflow["on"]["workflow_call"]["inputs"]
        assert "fail-on" in inputs, "Should have fail-on input"
        assert "upload-sarif" in inputs, "Should have upload-sarif input"
        assert "scan-path" in inputs, "Should have scan-path input"

    def test_fail_on_default_is_critical(self, workflow):
        """Test that fail-on defaults to critical only."""
        inputs = workflow["on"]["workflow_call"]["inputs"]
        assert inputs["fail-on"]["default"] == "critical", (
            "fail-on should default to 'critical' only, not 'critical,high'"
        )

    def test_has_required_outputs(self, workflow):
        """Test that workflow has required outputs."""
        outputs = workflow["on"]["workflow_call"]["outputs"]
        assert "findings-count" in outputs, "Should have findings-count output"
        assert "critical-count" in outputs, "Should have critical-count output"
        assert "high-count" in outputs, "Should have high-count output"

    def test_has_continue_on_error(self, workflow):
        """Test that job has continue-on-error for advisory mode."""
        job = workflow["jobs"]["scan"]
        assert job.get("continue-on-error") is True, (
            "Job should have continue-on-error: true for advisory mode"
        )

    def test_has_required_permissions(self, workflow):
        """Test that job has required permissions."""
        permissions = workflow["jobs"]["scan"]["permissions"]
        assert permissions["contents"] == "read"
        assert permissions["security-events"] == "write"
        assert permissions["pull-requests"] == "write"

    def test_uses_uv_pip_install_system(self, workflow_content):
        """Test that installation uses 'uv pip install --system .' not 'uv tool install'."""
        assert "uv pip install --system ." in workflow_content, (
            "Should use 'uv pip install --system .' for local installation"
        )
        assert "uv tool install specify-cli" not in workflow_content, (
            "Should not use 'uv tool install specify-cli'"
        )

    def test_jq_has_error_handling(self, workflow_content):
        """Test that jq commands have error handling."""
        # Check each line for jq commands and ensure error handling is present
        for line in workflow_content.split("\n"):
            if "jq " in line:
                # Skip comments
                if line.strip().startswith("#"):
                    continue
                # Each jq command line should have error handling
                assert "2>/dev/null" in line or 'echo "0"' in line, (
                    f"jq command should have error handling: {line.strip()}"
                )

    def test_yq_has_checksum_verification(self, workflow_content):
        """Test that yq download includes checksum verification."""
        assert "YQ_CHECKSUM=" in workflow_content, "Should define yq checksum"
        assert "sha256sum -c" in workflow_content, (
            "Should verify checksum with sha256sum"
        )

    def test_yq_version_is_pinned(self, workflow_content):
        """Test that yq version is pinned."""
        assert 'YQ_VERSION="v4.40.5"' in workflow_content, (
            "yq should be pinned to v4.40.5"
        )


class TestShellInjectionPrevention:
    """Test that workflows don't have shell injection vulnerabilities."""

    @pytest.fixture
    def workflow_files(self):
        """Get all security workflow files."""
        return [
            WORKFLOWS_DIR / "security-scan.yml",
            WORKFLOWS_DIR / "security.yml",
            WORKFLOWS_DIR / "security-parallel.yml",
        ]

    def test_no_direct_interpolation_in_run_steps(self, workflow_files):
        """Test that run steps use env blocks instead of direct interpolation.

        Direct interpolation like ${{ inputs.foo }} in run scripts is vulnerable
        to shell injection. Instead, values should be passed via env blocks.
        """
        # Patterns that are dangerous in run: blocks
        dangerous_patterns = [
            r"\$\{\{\s*inputs\.\w+\s*\}\}",  # ${{ inputs.foo }}
            r"\$\{\{\s*matrix\.\w+\s*\}\}",  # ${{ matrix.foo }}
        ]

        for workflow_file in workflow_files:
            if not workflow_file.exists():
                continue

            workflow = load_workflow(workflow_file)

            # Check each job
            for job_name, job in workflow.get("jobs", {}).items():
                for step in job.get("steps", []):
                    run_script = step.get("run", "")
                    step_name = step.get("name", "unnamed")

                    # Check for dangerous patterns in run script
                    for pattern in dangerous_patterns:
                        matches = re.findall(pattern, run_script)
                        assert not matches, (
                            f"Shell injection risk in {workflow_file.name}, "
                            f"job '{job_name}', step '{step_name}': "
                            f"Found direct interpolation {matches}. "
                            f"Use env: block instead."
                        )

    def test_env_blocks_used_for_inputs(self, workflow_files):
        """Test that steps use env blocks for passing inputs to scripts."""
        for workflow_file in workflow_files:
            if not workflow_file.exists():
                continue

            workflow = load_workflow(workflow_file)

            for job_name, job in workflow.get("jobs", {}).items():
                for step in job.get("steps", []):
                    # If step has a run script that uses variables
                    run_script = step.get("run", "")
                    if "$" in run_script and "SCAN" in run_script.upper():
                        # Should have env block
                        env = step.get("env", {})
                        # At least one of these should be in env
                        has_env_vars = any(
                            key in env for key in ["SCAN_PATH", "FAIL_ON", "COMPONENT"]
                        )
                        # Only check steps that seem to be scan-related
                        if "specify security scan" in run_script:
                            assert has_env_vars, (
                                f"Step '{step.get('name')}' in {workflow_file.name} "
                                f"should use env blocks for inputs"
                            )


class TestSecurityConfig:
    """Test security-config.yml configuration."""

    @pytest.fixture
    def config(self):
        """Load the security-config.yml."""
        with open(SECURITY_CONFIG) as f:
            return yaml.safe_load(f)

    def test_has_security_section(self, config):
        """Test that config has security section."""
        assert "security" in config, "Should have security section"

    def test_fail_on_is_single_severity(self, config):
        """Test that fail-on is a single severity, not comma-separated."""
        fail_on = config["security"]["fail-on"]
        assert "," not in str(fail_on), (
            "fail-on should be single severity, not comma-separated"
        )
        assert fail_on in ["critical", "high", "medium", "low"], (
            f"fail-on should be valid severity, got: {fail_on}"
        )

    def test_upload_sarif_is_boolean(self, config):
        """Test that upload-sarif is a boolean."""
        upload_sarif = config["security"]["upload-sarif"]
        assert isinstance(upload_sarif, bool), "upload-sarif should be boolean"

    def test_scan_path_is_string(self, config):
        """Test that scan-path is a string."""
        scan_path = config["security"]["scan-path"]
        assert isinstance(scan_path, str), "scan-path should be string"


class TestWorkflowYamlValidity:
    """Test that all workflow YAML files are valid."""

    @pytest.fixture
    def all_workflow_files(self):
        """Get all workflow files."""
        return list(WORKFLOWS_DIR.glob("*.yml"))

    def test_all_workflows_are_valid_yaml(self, all_workflow_files):
        """Test that all workflow files are valid YAML."""
        for workflow_file in all_workflow_files:
            try:
                load_workflow(workflow_file)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {workflow_file.name}: {e}")

    def test_all_workflows_have_name(self, all_workflow_files):
        """Test that all workflows have a name."""
        for workflow_file in all_workflow_files:
            workflow = load_workflow(workflow_file)
            assert "name" in workflow, f"{workflow_file.name} should have a name"

    def test_all_workflows_have_on_trigger(self, all_workflow_files):
        """Test that all workflows have an 'on' trigger."""
        for workflow_file in all_workflow_files:
            workflow = load_workflow(workflow_file)
            assert "on" in workflow, f"{workflow_file.name} should have 'on' trigger"

    def test_all_workflows_have_jobs(self, all_workflow_files):
        """Test that all workflows have jobs."""
        for workflow_file in all_workflow_files:
            workflow = load_workflow(workflow_file)
            assert "jobs" in workflow, f"{workflow_file.name} should have jobs"
            assert len(workflow["jobs"]) > 0, (
                f"{workflow_file.name} should have at least one job"
            )
