"""CI/CD integration for security scanning.

This module provides configuration generation for CI/CD pipelines
to integrate security scanning into automated workflows.
"""

from dataclasses import dataclass, field

import yaml


@dataclass
class CICDIntegration:
    """CI/CD pipeline configuration for security scanning.

    Generates pipeline configurations for various CI/CD platforms.
    """

    scanners: list[str] = field(default_factory=lambda: ["semgrep"])
    fail_on_severity: str = "high"
    upload_sarif: bool = True
    create_issues: bool = False
    python_version: str = "3.11"
    cache_enabled: bool = True

    def generate_github_action(self) -> str:
        """Generate GitHub Actions workflow for security scanning.

        Returns:
            YAML workflow file content.
        """
        workflow = {
            "name": "Security Scan",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
                "schedule": [{"cron": "0 0 * * 1"}],  # Weekly scan
            },
            "permissions": {
                "contents": "read",
                "security-events": "write",
            },
            "jobs": {
                "security-scan": {
                    "runs-on": "ubuntu-latest",
                    "steps": self._github_steps(),
                }
            },
        }
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    def _github_steps(self) -> list[dict]:
        """Generate GitHub Actions steps."""
        steps = [
            {"name": "Checkout code", "uses": "actions/checkout@v4"},
            {
                "name": "Set up Python",
                "uses": "actions/setup-python@v5",
                "with": {"python-version": self.python_version},
            },
        ]

        if self.cache_enabled:
            steps.append(
                {
                    "name": "Cache pip packages",
                    "uses": "actions/cache@v4",
                    "with": {
                        "path": "~/.cache/pip",
                        "key": "${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}",
                    },
                }
            )

        steps.append(
            {
                "name": "Install dependencies",
                "run": "pip install specify-cli semgrep bandit",
            }
        )

        # Run security scan
        scan_cmd = f"specify security scan --fail-on {self.fail_on_severity}"
        if self.upload_sarif:
            scan_cmd += " --output security-results.sarif --format sarif"

        steps.append(
            {
                "name": "Run security scan",
                "run": scan_cmd,
                "continue-on-error": self.upload_sarif,  # Continue to upload SARIF
            }
        )

        if self.upload_sarif:
            steps.append(
                {
                    "name": "Upload SARIF to GitHub Security",
                    "uses": "github/codeql-action/upload-sarif@v3",
                    "if": "always()",
                    "with": {
                        "sarif_file": "security-results.sarif",
                        "category": "jpspec-security",
                    },
                }
            )

        return steps

    def generate_gitlab_ci(self) -> str:
        """Generate GitLab CI configuration for security scanning.

        Returns:
            YAML configuration for .gitlab-ci.yml
        """
        config = {
            "stages": ["test", "security"],
            "variables": {
                "PIP_CACHE_DIR": "$CI_PROJECT_DIR/.cache/pip",
            },
            "security-scan": {
                "stage": "security",
                "image": f"python:{self.python_version}",
                "before_script": [
                    "pip install specify-cli semgrep bandit",
                ],
                "script": [
                    f"specify security scan --fail-on {self.fail_on_severity} --output gl-sast-report.json --format json",
                ],
                "artifacts": {
                    "reports": {"sast": "gl-sast-report.json"},
                    "when": "always",
                },
                "rules": [
                    {"if": '$CI_PIPELINE_SOURCE == "merge_request_event"'},
                    {"if": '$CI_COMMIT_BRANCH == "main"'},
                ],
            },
        }

        if self.cache_enabled:
            config["security-scan"]["cache"] = {
                "paths": [".cache/pip"],
            }

        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def generate_azure_pipelines(self) -> str:
        """Generate Azure Pipelines configuration.

        Returns:
            YAML configuration for azure-pipelines.yml
        """
        config = {
            "trigger": {
                "branches": {"include": ["main", "develop"]},
            },
            "pool": {"vmImage": "ubuntu-latest"},
            "steps": [
                {
                    "task": "UsePythonVersion@0",
                    "inputs": {"versionSpec": self.python_version},
                },
                {
                    "script": "pip install specify-cli semgrep bandit",
                    "displayName": "Install security tools",
                },
                {
                    "script": f"specify security scan --fail-on {self.fail_on_severity} --output $(Build.ArtifactStagingDirectory)/security-results.sarif --format sarif",
                    "displayName": "Run security scan",
                    "continueOnError": True,
                },
                {
                    "task": "PublishBuildArtifacts@1",
                    "inputs": {
                        "pathToPublish": "$(Build.ArtifactStagingDirectory)/security-results.sarif",
                        "artifactName": "SecurityResults",
                    },
                    "condition": "always()",
                },
            ],
        }
        return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_github_action(
    fail_on: str = "high",
    upload_sarif: bool = True,
    python_version: str = "3.11",
) -> str:
    """Generate GitHub Actions workflow for security scanning.

    Args:
        fail_on: Severity threshold for failing.
        upload_sarif: Whether to upload SARIF to GitHub Security.
        python_version: Python version to use.

    Returns:
        YAML workflow content.

    Example:
        >>> workflow = generate_github_action(fail_on="high")
        >>> # Save to .github/workflows/security.yml
    """
    integration = CICDIntegration(
        fail_on_severity=fail_on,
        upload_sarif=upload_sarif,
        python_version=python_version,
    )
    return integration.generate_github_action()


def generate_gitlab_ci(
    fail_on: str = "high",
    python_version: str = "3.11",
) -> str:
    """Generate GitLab CI configuration for security scanning.

    Args:
        fail_on: Severity threshold for failing.
        python_version: Python version to use.

    Returns:
        YAML configuration content.

    Example:
        >>> config = generate_gitlab_ci(fail_on="high")
        >>> # Add to .gitlab-ci.yml
    """
    integration = CICDIntegration(
        fail_on_severity=fail_on,
        python_version=python_version,
    )
    return integration.generate_gitlab_ci()


# Template for GitHub Security Code Scanning integration README
GITHUB_SECURITY_README = """# GitHub Code Scanning Integration

This project uses JP Spec Kit security scanning with GitHub Code Scanning.

## How it works

1. Security scans run automatically on push and pull requests
2. Results are uploaded in SARIF format to GitHub Security
3. Findings appear in the Security tab of your repository
4. Pull requests show inline annotations for new findings

## Configuration

The workflow is configured in `.github/workflows/security.yml`:

- **fail_on**: Severity threshold (default: high)
- **upload_sarif**: Upload results to GitHub Security (default: true)
- **schedule**: Weekly scans on Mondays at midnight

## Viewing Results

1. Go to your repository on GitHub
2. Click the "Security" tab
3. Select "Code scanning alerts"
4. Review and triage findings

## Customization

Edit `.jpspec/security-config.yml` to customize:
- Enabled scanners
- Severity thresholds
- Path exclusions
- Custom rules
"""
