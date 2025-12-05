"""Tests for security scanning GitHub Actions workflows.

Tests verify:
1. Workflow YAML syntax and structure
2. Reusable workflow inputs/outputs
3. Matrix strategy configuration
4. SARIF upload configuration
5. Caching configuration
6. PR comment functionality
"""

import yaml
from pathlib import Path

import pytest


def get_on_key(workflow_data):
    """Get the 'on' key from workflow data.

    YAML parsers interpret 'on:' as boolean True, so we need to handle both cases.
    """
    return True if True in workflow_data else "on"


class TestSecurityScanReusableWorkflow:
    """Tests for .github/workflows/security-scan.yml (reusable workflow)."""

    @pytest.fixture
    def workflow_path(self):
        """Path to reusable security scan workflow."""
        return Path(".github/workflows/security-scan.yml")

    @pytest.fixture
    def workflow_data(self, workflow_path):
        """Load and parse workflow YAML."""
        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")
        with open(workflow_path) as f:
            # GitHub Actions YAML uses 'on' which is interpreted as boolean True
            # Use FullLoader to preserve the 'on' key
            return yaml.load(f, Loader=yaml.FullLoader)

    def test_workflow_exists(self, workflow_path):
        """Test that reusable workflow file exists."""
        assert workflow_path.exists(), f"Missing workflow: {workflow_path}"

    def test_workflow_is_reusable(self, workflow_data):
        """Test workflow is configured as reusable."""
        on_key = get_on_key(workflow_data)
        assert "workflow_call" in workflow_data[on_key], "Must be a reusable workflow"

    def test_workflow_inputs(self, workflow_data):
        """Test workflow has required inputs."""
        on_key = get_on_key(workflow_data)
        inputs = workflow_data[on_key]["workflow_call"]["inputs"]

        # Check required inputs
        assert "scan-type" in inputs
        assert "fail-on" in inputs
        assert "upload-sarif" in inputs
        assert "scan-path" in inputs

        # Check default values
        assert inputs["scan-type"]["default"] == "incremental"
        assert inputs["fail-on"]["default"] == "critical,high"
        assert inputs["upload-sarif"]["default"] is True
        assert inputs["scan-path"]["default"] == "."

    def test_workflow_outputs(self, workflow_data):
        """Test workflow has required outputs."""
        on_key = get_on_key(workflow_data)
        outputs = workflow_data[on_key]["workflow_call"]["outputs"]

        assert "findings-count" in outputs
        assert "critical-count" in outputs
        assert "high-count" in outputs

    def test_workflow_permissions(self, workflow_data):
        """Test workflow has correct permissions."""
        permissions = workflow_data["jobs"]["scan"]["permissions"]

        assert permissions["contents"] == "read"
        assert permissions["security-events"] == "write"
        assert permissions["pull-requests"] == "write"

    def test_workflow_timeout(self, workflow_data):
        """Test workflow has timeout configured."""
        timeout = workflow_data["jobs"]["scan"]["timeout-minutes"]
        assert timeout == 10, "Timeout should be 10 minutes"

    def test_semgrep_caching(self, workflow_data):
        """Test Semgrep binary caching is configured."""
        steps = workflow_data["jobs"]["scan"]["steps"]

        cache_step = next(
            (s for s in steps if s.get("name") == "Cache Semgrep Binary"), None
        )

        assert cache_step is not None, "Missing Semgrep cache step"
        assert cache_step["uses"] == "actions/cache@v4"
        assert "~/.local/bin/semgrep" in cache_step["with"]["path"]
        assert "semgrep-" in cache_step["with"]["key"]

    def test_sarif_upload_step(self, workflow_data):
        """Test SARIF upload step is configured."""
        steps = workflow_data["jobs"]["scan"]["steps"]

        sarif_step = next(
            (s for s in steps if s.get("name") == "Upload SARIF to GitHub Security"),
            None,
        )

        assert sarif_step is not None, "Missing SARIF upload step"
        assert sarif_step["uses"] == "github/codeql-action/upload-sarif@v3"
        assert sarif_step["with"]["sarif_file"] == "security-results.sarif"
        assert sarif_step["with"]["category"] == "jpspec-security"
        assert sarif_step["if"] == "${{ inputs.upload-sarif && always() }}"

    def test_pr_comment_step(self, workflow_data):
        """Test PR comment step is configured."""
        steps = workflow_data["jobs"]["scan"]["steps"]

        comment_step = next(
            (s for s in steps if s.get("name") == "Comment PR with Summary"), None
        )

        assert comment_step is not None, "Missing PR comment step"
        assert comment_step["uses"] == "actions/github-script@v7"
        assert "pull_request" in comment_step["if"]

    def test_artifact_upload(self, workflow_data):
        """Test scan artifacts are uploaded."""
        steps = workflow_data["jobs"]["scan"]["steps"]

        artifact_step = next(
            (s for s in steps if s.get("name") == "Upload Scan Artifacts"), None
        )

        assert artifact_step is not None, "Missing artifact upload step"
        assert artifact_step["uses"] == "actions/upload-artifact@v4"
        assert artifact_step["with"]["retention-days"] == 90

    def test_checkout_with_history(self, workflow_data):
        """Test checkout fetches full history for incremental scanning."""
        steps = workflow_data["jobs"]["scan"]["steps"]

        checkout_step = next(
            (s for s in steps if s.get("name") == "Checkout code"), None
        )

        assert checkout_step is not None
        assert checkout_step["with"]["fetch-depth"] == 0


class TestSecurityWorkflow:
    """Tests for .github/workflows/security.yml (calling workflow)."""

    @pytest.fixture
    def workflow_path(self):
        """Path to main security workflow."""
        return Path(".github/workflows/security.yml")

    @pytest.fixture
    def workflow_data(self, workflow_path):
        """Load and parse workflow YAML."""
        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")
        with open(workflow_path) as f:
            # GitHub Actions YAML uses 'on' which is interpreted as boolean True
            # Use FullLoader to preserve the 'on' key
            return yaml.load(f, Loader=yaml.FullLoader)

    def test_workflow_exists(self, workflow_path):
        """Test that main security workflow exists."""
        assert workflow_path.exists(), f"Missing workflow: {workflow_path}"

    def test_workflow_triggers(self, workflow_data):
        """Test workflow has correct triggers."""
        on_key = get_on_key(workflow_data)
        triggers = workflow_data[on_key]

        assert "pull_request" in triggers
        assert "push" in triggers
        assert "schedule" in triggers
        assert "workflow_dispatch" in triggers

    def test_pr_trigger_paths(self, workflow_data):
        """Test PR trigger only runs on relevant paths."""
        on_key = get_on_key(workflow_data)
        pr_trigger = workflow_data[on_key]["pull_request"]

        assert "paths" in pr_trigger
        paths = pr_trigger["paths"]
        assert "src/**" in paths
        assert "tests/**" in paths
        assert "*.py" in paths

    def test_scheduled_scan(self, workflow_data):
        """Test nightly scheduled scan is configured."""
        on_key = get_on_key(workflow_data)
        schedule = workflow_data[on_key]["schedule"]

        assert len(schedule) > 0
        assert schedule[0]["cron"] == "0 2 * * *"  # 2 AM UTC daily

    def test_calls_reusable_workflow(self, workflow_data):
        """Test job calls reusable workflow."""
        job = workflow_data["jobs"]["security-scan"]

        assert "uses" in job
        assert job["uses"] == "./.github/workflows/security-scan.yml"

    def test_workflow_inputs(self, workflow_data):
        """Test workflow passes correct inputs to reusable workflow."""
        job = workflow_data["jobs"]["security-scan"]

        assert "with" in job
        inputs = job["with"]

        assert "scan-type" in inputs
        assert "fail-on" in inputs
        assert "upload-sarif" in inputs

    def test_permissions_inherited(self, workflow_data):
        """Test job has correct permissions."""
        job = workflow_data["jobs"]["security-scan"]

        assert "permissions" in job
        permissions = job["permissions"]

        assert permissions["contents"] == "read"
        assert permissions["security-events"] == "write"
        assert permissions["pull-requests"] == "write"


class TestParallelSecurityWorkflow:
    """Tests for .github/workflows/security-parallel.yml."""

    @pytest.fixture
    def workflow_path(self):
        """Path to parallel security workflow."""
        return Path(".github/workflows/security-parallel.yml")

    @pytest.fixture
    def workflow_data(self, workflow_path):
        """Load and parse workflow YAML."""
        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")
        with open(workflow_path) as f:
            # GitHub Actions YAML uses 'on' which is interpreted as boolean True
            # Use FullLoader to preserve the 'on' key
            return yaml.load(f, Loader=yaml.FullLoader)

    def test_workflow_exists(self, workflow_path):
        """Test that parallel workflow exists."""
        assert workflow_path.exists(), f"Missing workflow: {workflow_path}"

    def test_matrix_strategy(self, workflow_data):
        """Test matrix strategy is configured."""
        job = workflow_data["jobs"]["security-scan-matrix"]

        assert "strategy" in job
        strategy = job["strategy"]

        assert "matrix" in strategy
        assert "component" in strategy["matrix"]
        assert strategy["fail-fast"] is False  # Don't stop on first failure

    def test_matrix_components(self, workflow_data):
        """Test matrix includes expected components."""
        strategy = workflow_data["jobs"]["security-scan-matrix"]["strategy"]
        components = strategy["matrix"]["component"]

        # Should have at least these components
        assert "src/specify_cli" in components
        assert "tests" in components

    def test_component_specific_scanning(self, workflow_data):
        """Test each matrix job scans specific component path."""
        steps = workflow_data["jobs"]["security-scan-matrix"]["steps"]

        scan_step = next(
            (s for s in steps if "Run Security Scan" in s.get("name", "")), None
        )

        assert scan_step is not None
        # Check that path uses matrix.component
        assert "${{ matrix.component }}" in scan_step["run"]

    def test_sarif_per_component(self, workflow_data):
        """Test SARIF upload uses component-specific category."""
        steps = workflow_data["jobs"]["security-scan-matrix"]["steps"]

        sarif_step = next(
            (s for s in steps if "Upload SARIF" in s.get("name", "")), None
        )

        assert sarif_step is not None
        assert "category" in sarif_step["with"]
        # Should use component name in category
        assert "steps.scan.outputs.component_name" in str(sarif_step["with"]["category"])

    def test_aggregate_results_job(self, workflow_data):
        """Test aggregation job collects all results."""
        assert "aggregate-results" in workflow_data["jobs"]

        aggregate_job = workflow_data["jobs"]["aggregate-results"]

        # Should depend on matrix job
        assert "needs" in aggregate_job
        assert "security-scan-matrix" in aggregate_job["needs"]

        # Should run even if matrix jobs fail
        assert aggregate_job["if"] == "always()"

    def test_timeout_configuration(self, workflow_data):
        """Test matrix jobs have appropriate timeout."""
        job = workflow_data["jobs"]["security-scan-matrix"]

        assert "timeout-minutes" in job
        # Should be higher than standard workflow for large components
        assert job["timeout-minutes"] >= 10


class TestWorkflowSyntax:
    """Tests for workflow YAML syntax validity."""

    @pytest.mark.parametrize(
        "workflow_file",
        [
            ".github/workflows/security-scan.yml",
            ".github/workflows/security.yml",
            ".github/workflows/security-parallel.yml",
        ],
    )
    def test_yaml_syntax(self, workflow_file):
        """Test workflow YAML syntax is valid."""
        workflow_path = Path(workflow_file)

        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")

        with open(workflow_path) as f:
            try:
                yaml.load(f, Loader=yaml.FullLoader)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {workflow_file}: {e}")

    @pytest.mark.parametrize(
        "workflow_file",
        [
            ".github/workflows/security-scan.yml",
            ".github/workflows/security.yml",
            ".github/workflows/security-parallel.yml",
        ],
    )
    def test_required_fields(self, workflow_file):
        """Test workflow has required top-level fields."""
        workflow_path = Path(workflow_file)

        if not workflow_path.exists():
            pytest.skip(f"Workflow file not found: {workflow_path}")

        with open(workflow_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        assert "name" in data, f"{workflow_file} missing 'name' field"
        # YAML parsers interpret 'on:' as boolean True
        on_key = get_on_key(data)
        assert on_key in data, f"{workflow_file} missing 'on' field"
        assert "jobs" in data, f"{workflow_file} missing 'jobs' field"


class TestWorkflowIntegration:
    """Integration tests for security workflows."""

    def test_reusable_workflow_called_correctly(self):
        """Test main workflow calls reusable workflow with correct parameters."""
        security_yml = Path(".github/workflows/security.yml")
        reusable_yml = Path(".github/workflows/security-scan.yml")

        if not security_yml.exists() or not reusable_yml.exists():
            pytest.skip("Workflow files not found")

        with open(security_yml) as f:
            security_data = yaml.load(f, Loader=yaml.FullLoader)

        with open(reusable_yml) as f:
            reusable_data = yaml.load(f, Loader=yaml.FullLoader)

        # Get inputs from calling workflow
        calling_inputs = security_data["jobs"]["security-scan"]["with"]

        # Get expected inputs from reusable workflow
        on_key = get_on_key(reusable_data)
        expected_inputs = reusable_data[on_key]["workflow_call"]["inputs"]

        # Check all expected inputs are provided
        for input_name in expected_inputs.keys():
            assert (
                input_name in calling_inputs
            ), f"Missing input: {input_name} in calling workflow"

    def test_cache_keys_consistent(self):
        """Test cache keys are consistent across workflows."""
        workflows = [
            ".github/workflows/security-scan.yml",
            ".github/workflows/security-parallel.yml",
        ]

        cache_keys = []

        for workflow_file in workflows:
            workflow_path = Path(workflow_file)
            if not workflow_path.exists():
                continue

            with open(workflow_path) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)

            # Find cache steps
            for job in data["jobs"].values():
                steps = job.get("steps", [])
                for step in steps:
                    if step.get("uses", "").startswith("actions/cache@"):
                        key = step["with"]["key"]
                        if "semgrep" in key:
                            cache_keys.append(key)

        # All Semgrep cache keys should use same pattern
        if cache_keys:
            assert all(
                "semgrep-" in key for key in cache_keys
            ), "Inconsistent Semgrep cache keys"


class TestPerformanceOptimizations:
    """Tests for workflow performance optimizations."""

    def test_pip_cache_enabled(self):
        """Test pip cache is enabled in workflows."""
        workflow_path = Path(".github/workflows/security-scan.yml")

        if not workflow_path.exists():
            pytest.skip("Workflow file not found")

        with open(workflow_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        steps = data["jobs"]["scan"]["steps"]

        # Find Python setup step
        python_step = next(
            (s for s in steps if s.get("name") == "Setup Python"), None
        )

        assert python_step is not None
        assert python_step["with"].get("cache") == "pip"

    def test_semgrep_cache_size_acceptable(self):
        """Test Semgrep cache configuration is under 50MB (per AC)."""
        workflow_path = Path(".github/workflows/security-scan.yml")

        if not workflow_path.exists():
            pytest.skip("Workflow file not found")

        with open(workflow_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        steps = data["jobs"]["scan"]["steps"]

        cache_step = next(
            (s for s in steps if "Cache Semgrep" in s.get("name", "")), None
        )

        assert cache_step is not None

        # Cache path should be just the binary, not the entire ~/.cache/semgrep
        # which keeps it under 50MB
        cache_path = cache_step["with"]["path"]
        assert "~/.local/bin/semgrep" in cache_path
        assert "~/.cache/semgrep" not in cache_path


class TestSecurityConfiguration:
    """Tests for security-specific configurations."""

    def test_fail_on_critical_by_default(self):
        """Test workflows fail on critical/high by default."""
        workflow_path = Path(".github/workflows/security.yml")

        if not workflow_path.exists():
            pytest.skip("Workflow file not found")

        with open(workflow_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        inputs = data["jobs"]["security-scan"]["with"]

        # Should fail on at least critical,high
        fail_on = inputs.get("fail-on", "")
        assert "critical" in fail_on.lower()

    def test_sarif_upload_enabled_by_default(self):
        """Test SARIF upload is enabled by default."""
        workflow_path = Path(".github/workflows/security.yml")

        if not workflow_path.exists():
            pytest.skip("Workflow file not found")

        with open(workflow_path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)

        inputs = data["jobs"]["security-scan"]["with"]

        assert inputs.get("upload-sarif") is True
