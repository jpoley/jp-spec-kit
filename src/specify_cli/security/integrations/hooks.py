"""Pre-commit hook integration for security scanning.

This module provides configuration generation for pre-commit hooks
that run security scans before commits.
"""

from dataclasses import dataclass, field

import yaml


@dataclass
class PreCommitConfig:
    """Pre-commit hook configuration for security scanning.

    Generates .pre-commit-config.yaml entries for security hooks.
    """

    enabled_scanners: list[str] = field(default_factory=lambda: ["semgrep", "bandit"])
    fail_on_severity: str = "high"
    exclude_patterns: list[str] = field(default_factory=list)
    additional_args: dict[str, list[str]] = field(default_factory=dict)

    def to_yaml(self) -> str:
        """Generate pre-commit configuration YAML.

        Returns:
            YAML string for .pre-commit-config.yaml
        """
        hooks = []

        # Semgrep hook
        if "semgrep" in self.enabled_scanners:
            semgrep_hook = {
                "id": "semgrep",
                "name": "semgrep security scan",
                "entry": "semgrep scan --config auto",
                "language": "python",
                "types": ["python", "javascript", "typescript"],
                "pass_filenames": False,
            }
            if "semgrep" in self.additional_args:
                semgrep_hook["entry"] += " " + " ".join(self.additional_args["semgrep"])
            hooks.append(semgrep_hook)

        # Bandit hook
        if "bandit" in self.enabled_scanners:
            bandit_hook = {
                "id": "bandit",
                "name": "bandit security scan",
                "entry": "bandit -r",
                "language": "python",
                "types": ["python"],
                "pass_filenames": True,
            }
            if "bandit" in self.additional_args:
                bandit_hook["entry"] += " " + " ".join(self.additional_args["bandit"])
            hooks.append(bandit_hook)

        # jpspec security hook
        jpspec_hook = {
            "id": "jpspec-security",
            "name": "jpspec security scan",
            "entry": f"specify security scan --fail-on {self.fail_on_severity}",
            "language": "python",
            "types": ["python", "javascript", "typescript"],
            "pass_filenames": False,
            "stages": ["pre-commit"],
        }
        hooks.append(jpspec_hook)

        config = {
            "repos": [
                {
                    "repo": "local",
                    "hooks": hooks,
                }
            ]
        }

        if self.exclude_patterns:
            config["exclude"] = "|".join(self.exclude_patterns)

        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def to_dict(self) -> dict:
        """Convert configuration to dictionary.

        Returns:
            Configuration dictionary.
        """
        return {
            "enabled_scanners": self.enabled_scanners,
            "fail_on_severity": self.fail_on_severity,
            "exclude_patterns": self.exclude_patterns,
            "additional_args": self.additional_args,
        }


def generate_precommit_config(
    scanners: list[str] | None = None,
    fail_on: str = "high",
    exclude: list[str] | None = None,
) -> str:
    """Generate pre-commit configuration for security scanning.

    Args:
        scanners: List of scanners to enable (default: semgrep, bandit).
        fail_on: Severity threshold for failing (critical/high/medium/low).
        exclude: Patterns to exclude from scanning.

    Returns:
        YAML configuration string.

    Example:
        >>> config = generate_precommit_config(
        ...     scanners=["semgrep", "bandit"],
        ...     fail_on="high",
        ...     exclude=["node_modules/*", "*.test.py"]
        ... )
        >>> print(config)
    """
    config = PreCommitConfig(
        enabled_scanners=scanners or ["semgrep", "bandit"],
        fail_on_severity=fail_on,
        exclude_patterns=exclude or [],
    )
    return config.to_yaml()


def generate_husky_config() -> str:
    """Generate Husky (npm) pre-commit hook configuration.

    Returns:
        Shell script content for .husky/pre-commit
    """
    return """#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Run security scan before commit
echo "Running security scan..."
specify security scan --fail-on high

# Exit with the scan's exit code
exit $?
"""


def generate_lefthook_config() -> str:
    """Generate Lefthook configuration for security scanning.

    Returns:
        YAML configuration for lefthook.yml
    """
    config = {
        "pre-commit": {
            "commands": {
                "security-scan": {
                    "glob": "*.{py,js,ts,tsx}",
                    "run": "specify security scan --fail-on high {staged_files}",
                }
            }
        }
    }
    return yaml.dump(config, default_flow_style=False, sort_keys=False)
