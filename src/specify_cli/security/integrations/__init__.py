"""Security integrations for workflow and external systems.

This module provides integrations for:
- Backlog task creation from security findings
- Pre-commit hook configuration
- CI/CD pipeline integration (GitHub Actions, GitLab CI)
"""

from specify_cli.security.integrations.backlog import (
    BacklogIntegration,
    FindingTask,
    create_tasks_from_findings,
)
from specify_cli.security.integrations.hooks import (
    PreCommitConfig,
    generate_precommit_config,
)
from specify_cli.security.integrations.cicd import (
    CICDIntegration,
    generate_github_action,
    generate_gitlab_ci,
)

__all__ = [
    # Backlog
    "BacklogIntegration",
    "FindingTask",
    "create_tasks_from_findings",
    # Hooks
    "PreCommitConfig",
    "generate_precommit_config",
    # CI/CD
    "CICDIntegration",
    "generate_github_action",
    "generate_gitlab_ci",
]
