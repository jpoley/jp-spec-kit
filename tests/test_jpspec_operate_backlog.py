"""Tests for /jpspec:operate backlog.md CLI integration.

This test module verifies that the operate command correctly integrates
with backlog.md CLI for operational task management.
"""

import pytest
from pathlib import Path


@pytest.fixture
def operate_command_path():
    """Return the path to the operate.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "jpspec" / "operate.md"
    )


@pytest.fixture
def operate_command_content(operate_command_path):
    """Load the operate.md command content."""
    return operate_command_path.read_text()


class TestOperateCommandStructure:
    """Tests for operate.md command structure."""

    def test_command_file_exists(self, operate_command_path):
        """Verify operate.md command file exists."""
        assert operate_command_path.exists(), "operate.md command file should exist"

    def test_has_task_discovery_section(self, operate_command_content):
        """Verify command has task discovery section."""
        assert (
            "### Step 1: Discover Existing Operational Tasks" in operate_command_content
        )
        assert "backlog search" in operate_command_content


class TestSREAgentBacklogIntegration:
    """Tests for SRE agent backlog instructions."""

    def test_sre_agent_receives_backlog_instructions(self, operate_command_content):
        """AC #1: SRE agent receives shared backlog instructions."""
        assert "@sre-agent" in operate_command_content
        assert "## Backlog Task Management (REQUIRED)" in operate_command_content

    def test_agent_creates_operational_tasks(self, operate_command_content):
        """AC #2: Agent creates operational tasks (deployment, monitoring, alerts)."""
        # Check for CI/CD task creation
        assert "Setup CI/CD Pipeline" in operate_command_content
        assert "infrastructure,cicd" in operate_command_content

        # Check for monitoring task creation
        assert "Define SLOs and Alerting Rules" in operate_command_content
        assert "infrastructure,monitoring" in operate_command_content

        # Check for observability task creation
        assert "Implement Observability Stack" in operate_command_content
        assert "infrastructure,observability" in operate_command_content

    def test_agent_creates_kubernetes_tasks(self, operate_command_content):
        """AC #3: Agent tracks infrastructure changes as tasks."""
        assert "Kubernetes Deployment Configuration" in operate_command_content
        assert "infrastructure,kubernetes" in operate_command_content

    def test_agent_updates_task_status(self, operate_command_content):
        """AC #4: Agent updates task status as operations complete."""
        assert '-s "In Progress"' in operate_command_content
        assert "-s Done" in operate_command_content
        assert "--check-ac" in operate_command_content

    def test_runbook_tasks_created_for_alerts(self, operate_command_content):
        """AC #5: Runbook creation tasks added when alerts are defined."""
        assert "Runbook:" in operate_command_content
        assert "runbook,operations" in operate_command_content
        assert "Create runbook task for each alert" in operate_command_content


class TestOperationalTaskPatterns:
    """Tests for operational task creation patterns."""

    def test_cicd_task_has_proper_acs(self, operate_command_content):
        """Verify CI/CD task has appropriate acceptance criteria."""
        assert "Configure build pipeline with caching" in operate_command_content
        assert "Setup test pipeline" in operate_command_content
        assert "Implement deployment pipeline with rollback" in operate_command_content
        assert "SBOM generation" in operate_command_content

    def test_kubernetes_task_has_proper_acs(self, operate_command_content):
        """Verify Kubernetes task has appropriate acceptance criteria."""
        assert "deployment manifests with resource limits" in operate_command_content
        assert "HPA and pod disruption budgets" in operate_command_content
        assert "network policies and RBAC" in operate_command_content

    def test_observability_task_has_proper_acs(self, operate_command_content):
        """Verify observability task has appropriate acceptance criteria."""
        assert "Prometheus metrics" in operate_command_content
        assert "Grafana dashboards" in operate_command_content
        assert "structured logging" in operate_command_content
        assert "distributed tracing" in operate_command_content

    def test_runbook_task_has_proper_acs(self, operate_command_content):
        """Verify runbook task has appropriate acceptance criteria."""
        assert "Document initial triage steps" in operate_command_content
        assert "common causes and solutions" in operate_command_content
        assert "rollback procedure" in operate_command_content
        assert "escalation path" in operate_command_content


class TestImplementationWorkflow:
    """Tests for implementation workflow documentation."""

    def test_has_pick_task_step(self, operate_command_content):
        """Verify pick task step exists."""
        assert "Pick a task" in operate_command_content
        assert "backlog task <task-id> --plain" in operate_command_content

    def test_has_assign_and_start_step(self, operate_command_content):
        """Verify assign and start step exists."""
        assert "Assign and start" in operate_command_content
        assert "-a @sre-agent" in operate_command_content

    def test_has_check_acs_step(self, operate_command_content):
        """Verify check ACs step exists."""
        assert "Check ACs progressively" in operate_command_content

    def test_has_add_notes_step(self, operate_command_content):
        """Verify add notes step exists."""
        assert "Add notes" in operate_command_content
        assert "--notes" in operate_command_content

    def test_has_mark_complete_step(self, operate_command_content):
        """Verify mark complete step exists."""
        assert "Mark complete" in operate_command_content


class TestTaskLabels:
    """Tests for proper task labeling."""

    def test_infrastructure_label_used(self, operate_command_content):
        """Verify infrastructure label is used consistently."""
        assert operate_command_content.count("infrastructure,") >= 4

    def test_specific_labels_used(self, operate_command_content):
        """Verify specific operational labels are used."""
        labels = ["cicd", "kubernetes", "observability", "monitoring", "runbook"]
        for label in labels:
            assert label in operate_command_content, f"Label {label} should be present"
