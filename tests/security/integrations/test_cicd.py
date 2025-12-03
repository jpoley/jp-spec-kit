"""Tests for CI/CD integration."""

import yaml

import pytest

from specify_cli.security.integrations.cicd import (
    CICDIntegration,
    generate_github_action,
    generate_gitlab_ci,
)


class TestCICDIntegration:
    """Tests for CICDIntegration."""

    @pytest.fixture
    def integration(self):
        """Create a CI/CD integration instance."""
        return CICDIntegration()

    def test_default_config(self, integration):
        """Test default configuration."""
        assert "semgrep" in integration.scanners
        assert integration.fail_on_severity == "high"
        assert integration.upload_sarif is True
        assert integration.python_version == "3.11"

    def test_generate_github_action_structure(self, integration):
        """Test GitHub Action structure."""
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        assert data["name"] == "Security Scan"
        assert "on" in data
        assert "jobs" in data
        assert "security-scan" in data["jobs"]

    def test_github_action_triggers(self, integration):
        """Test GitHub Action triggers."""
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        triggers = data["on"]
        assert "push" in triggers
        assert "pull_request" in triggers
        assert "schedule" in triggers

    def test_github_action_permissions(self, integration):
        """Test GitHub Action permissions."""
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        permissions = data["permissions"]
        assert permissions["contents"] == "read"
        assert permissions["security-events"] == "write"

    def test_github_action_steps(self, integration):
        """Test GitHub Action steps."""
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        steps = data["jobs"]["security-scan"]["steps"]
        step_names = [s.get("name") for s in steps]

        assert "Checkout code" in step_names
        assert "Set up Python" in step_names
        assert "Install dependencies" in step_names
        assert "Run security scan" in step_names

    def test_github_action_sarif_upload(self, integration):
        """Test SARIF upload step is included."""
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        steps = data["jobs"]["security-scan"]["steps"]
        sarif_step = next(
            (s for s in steps if "Upload SARIF" in s.get("name", "")), None
        )

        assert sarif_step is not None
        assert sarif_step["uses"] == "github/codeql-action/upload-sarif@v3"

    def test_github_action_without_sarif(self):
        """Test GitHub Action without SARIF upload."""
        integration = CICDIntegration(upload_sarif=False)
        config = integration.generate_github_action()
        data = yaml.safe_load(config)

        steps = data["jobs"]["security-scan"]["steps"]
        sarif_step = next(
            (s for s in steps if "Upload SARIF" in s.get("name", "")), None
        )

        assert sarif_step is None

    def test_github_action_fail_on_severity(self):
        """Test fail_on severity in command."""
        integration = CICDIntegration(fail_on_severity="critical")
        config = integration.generate_github_action()

        assert "--fail-on critical" in config

    def test_generate_gitlab_ci_structure(self, integration):
        """Test GitLab CI structure."""
        config = integration.generate_gitlab_ci()
        data = yaml.safe_load(config)

        assert "stages" in data
        assert "security" in data["stages"]
        assert "security-scan" in data

    def test_gitlab_ci_job_config(self, integration):
        """Test GitLab CI job configuration."""
        config = integration.generate_gitlab_ci()
        data = yaml.safe_load(config)

        job = data["security-scan"]
        assert job["stage"] == "security"
        assert "image" in job
        assert "script" in job

    def test_gitlab_ci_artifacts(self, integration):
        """Test GitLab CI artifacts configuration."""
        config = integration.generate_gitlab_ci()
        data = yaml.safe_load(config)

        job = data["security-scan"]
        assert "artifacts" in job
        assert "reports" in job["artifacts"]
        assert "sast" in job["artifacts"]["reports"]

    def test_gitlab_ci_rules(self, integration):
        """Test GitLab CI rules."""
        config = integration.generate_gitlab_ci()
        data = yaml.safe_load(config)

        job = data["security-scan"]
        assert "rules" in job
        assert len(job["rules"]) > 0

    def test_generate_azure_pipelines_structure(self, integration):
        """Test Azure Pipelines structure."""
        config = integration.generate_azure_pipelines()
        data = yaml.safe_load(config)

        assert "trigger" in data
        assert "pool" in data
        assert "steps" in data

    def test_azure_pipelines_steps(self, integration):
        """Test Azure Pipelines steps."""
        config = integration.generate_azure_pipelines()
        data = yaml.safe_load(config)

        steps = data["steps"]
        assert len(steps) >= 3


class TestGenerateGitHubAction:
    """Tests for generate_github_action function."""

    def test_basic_usage(self):
        """Test basic workflow generation."""
        workflow = generate_github_action()
        data = yaml.safe_load(workflow)

        assert data["name"] == "Security Scan"
        assert "security-scan" in data["jobs"]

    def test_custom_fail_on(self):
        """Test custom fail_on threshold."""
        workflow = generate_github_action(fail_on="medium")

        assert "--fail-on medium" in workflow

    def test_without_sarif(self):
        """Test without SARIF upload."""
        workflow = generate_github_action(upload_sarif=False)

        assert "Upload SARIF" not in workflow

    def test_custom_python_version(self):
        """Test custom Python version."""
        workflow = generate_github_action(python_version="3.12")
        data = yaml.safe_load(workflow)

        python_step = next(
            s
            for s in data["jobs"]["security-scan"]["steps"]
            if s.get("name") == "Set up Python"
        )
        assert python_step["with"]["python-version"] == "3.12"


class TestGenerateGitLabCI:
    """Tests for generate_gitlab_ci function."""

    def test_basic_usage(self):
        """Test basic configuration generation."""
        config = generate_gitlab_ci()
        data = yaml.safe_load(config)

        assert "security-scan" in data
        assert "stages" in data

    def test_custom_fail_on(self):
        """Test custom fail_on threshold."""
        config = generate_gitlab_ci(fail_on="low")

        assert "--fail-on low" in config

    def test_custom_python_version(self):
        """Test custom Python version."""
        config = generate_gitlab_ci(python_version="3.10")
        data = yaml.safe_load(config)

        assert "python:3.10" in data["security-scan"]["image"]
