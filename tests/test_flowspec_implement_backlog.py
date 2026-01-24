"""Tests for /flow:implement backlog.md CLI integration.

This test module verifies that the implement command correctly integrates
with backlog.md CLI for task-driven implementation.

After the decomposition (task-580), /flow:implement is an orchestrator that
invokes composable sub-commands: /flow:gate, /flow:rigor, /flow:build,
/flow:review, /flow:pre-pr.
"""

import pytest
from pathlib import Path


@pytest.fixture
def implement_command_path():
    """Return the path to the implement.md command file."""
    return (
        Path(__file__).parent.parent / ".claude" / "commands" / "flow" / "implement.md"
    )


@pytest.fixture
def implement_command_content(implement_command_path):
    """Load the implement.md command content."""
    return implement_command_path.read_text()


@pytest.fixture
def build_command_path():
    """Return the path to the build.md command file."""
    return Path(__file__).parent.parent / ".claude" / "commands" / "flow" / "build.md"


@pytest.fixture
def build_command_content(build_command_path):
    """Load the build.md command content."""
    return build_command_path.read_text()


@pytest.fixture
def review_command_path():
    """Return the path to the review.md command file."""
    return Path(__file__).parent.parent / ".claude" / "commands" / "flow" / "review.md"


@pytest.fixture
def review_command_content(review_command_path):
    """Load the review.md command content."""
    return review_command_path.read_text()


class TestImplementCommandStructure:
    """Tests for implement.md orchestrator structure."""

    def test_command_file_exists(self, implement_command_path):
        """Verify implement.md command file exists."""
        assert implement_command_path.exists(), "implement.md command file should exist"

    def test_is_orchestrator(self, implement_command_content):
        """Verify implement.md is now an orchestrator."""
        assert "orchestrat" in implement_command_content.lower(), (
            "implement.md should be an orchestrator"
        )

    def test_has_task_discovery_phase(self, implement_command_content):
        """AC #1: Command has task discovery phase."""
        assert "Discover Tasks" in implement_command_content
        assert "backlog" in implement_command_content

    def test_references_sub_commands(self, implement_command_content):
        """Verify orchestrator references sub-commands."""
        sub_commands = [
            "/flow:gate",
            "/flow:rigor",
            "/flow:build",
            "/flow:review",
            "/flow:pre-pr",
        ]
        for cmd in sub_commands:
            assert cmd in implement_command_content, (
                f"implement.md should reference {cmd}"
            )

    def test_under_200_lines(self, implement_command_content):
        """AC #1: No single command exceeds 200 lines."""
        line_count = len(implement_command_content.splitlines())
        assert line_count <= 200, (
            f"implement.md has {line_count} lines, should be <= 200"
        )


class TestBuildCommandStructure:
    """Tests for build.md (implementation agent orchestration)."""

    def test_command_file_exists(self, build_command_path):
        """Verify build.md command file exists."""
        assert build_command_path.exists(), "build.md command file should exist"

    def test_under_200_lines(self, build_command_content):
        """AC #1: No single command exceeds 200 lines."""
        line_count = len(build_command_content.splitlines())
        assert line_count <= 200, f"build.md has {line_count} lines, should be <= 200"


class TestEngineerAgentBacklogIntegration:
    """Tests for engineer agent backlog instructions in build.md."""

    def test_frontend_engineer_present(self, build_command_content):
        """AC #2: Frontend engineer receives backlog instructions."""
        assert "@frontend-engineer" in build_command_content

    def test_backend_engineer_present(self, build_command_content):
        """AC #2: Backend engineer receives backlog instructions."""
        assert "@backend-engineer" in build_command_content

    def test_ai_ml_engineer_present(self, build_command_content):
        """AC #2: AI/ML engineer receives backlog instructions."""
        assert "@ai-ml-engineer" in build_command_content

    def test_agents_assign_themselves(self, build_command_content):
        """AC #4: Engineers assign themselves and set status to In Progress."""
        assert '-s "In Progress" -a @frontend-engineer' in build_command_content
        assert '-s "In Progress" -a @backend-engineer' in build_command_content
        assert '-s "In Progress" -a @ai-ml-engineer' in build_command_content

    def test_agents_check_acs_during_implementation(self, build_command_content):
        """AC #5: Engineers check ACs as each criterion is implemented."""
        assert "--check-ac" in build_command_content

    def test_has_pick_task_step(self, build_command_content):
        """Verify pick task step exists."""
        assert "Pick a task" in build_command_content
        assert "backlog task <task-id> --plain" in build_command_content

    def test_has_assign_step(self, build_command_content):
        """Verify assign step exists."""
        assert "Assign yourself" in build_command_content


class TestCodeReviewerBacklogIntegration:
    """Tests for code reviewer backlog instructions in review.md."""

    def test_command_file_exists(self, review_command_path):
        """Verify review.md command file exists."""
        assert review_command_path.exists(), "review.md command file should exist"

    def test_under_200_lines(self, review_command_content):
        """AC #1: No single command exceeds 200 lines."""
        line_count = len(review_command_content.splitlines())
        assert line_count <= 200, f"review.md has {line_count} lines, should be <= 200"

    def test_frontend_reviewer_present(self, review_command_content):
        """AC #7: Frontend code reviewer verifies AC completion."""
        assert "@frontend-code-reviewer" in review_command_content

    def test_backend_reviewer_present(self, review_command_content):
        """AC #7: Backend code reviewer verifies AC completion."""
        assert "@backend-code-reviewer" in review_command_content

    def test_reviewers_can_uncheck_acs(self, review_command_content):
        """AC #7: Reviewers can uncheck ACs if not satisfied."""
        assert "--uncheck-ac" in review_command_content


class TestComposableCommands:
    """Tests for composable command architecture."""

    @pytest.fixture
    def flow_commands_dir(self):
        """Return path to flow commands directory."""
        return Path(__file__).parent.parent / ".claude" / "commands" / "flow"

    def test_gate_command_exists(self, flow_commands_dir):
        """Verify gate.md command file exists."""
        gate_path = flow_commands_dir / "gate.md"
        assert gate_path.exists(), "gate.md command file should exist"

    def test_rigor_command_exists(self, flow_commands_dir):
        """Verify rigor.md command file exists."""
        rigor_path = flow_commands_dir / "rigor.md"
        assert rigor_path.exists(), "rigor.md command file should exist"

    def test_pre_pr_command_exists(self, flow_commands_dir):
        """Verify pre-pr.md command file exists."""
        pre_pr_path = flow_commands_dir / "pre-pr.md"
        assert pre_pr_path.exists(), "pre-pr.md command file should exist"

    def test_all_commands_under_200_lines(self, flow_commands_dir):
        """AC #1: No single command exceeds 200 lines."""
        new_commands = ["gate.md", "rigor.md", "build.md", "review.md", "pre-pr.md"]
        for cmd_name in new_commands:
            cmd_path = flow_commands_dir / cmd_name
            if cmd_path.exists():
                content = cmd_path.read_text()
                line_count = len(content.splitlines())
                assert line_count <= 200, (
                    f"{cmd_name} has {line_count} lines, should be <= 200"
                )


class TestAgentIdentities:
    """Tests to verify all agent identities are present across commands."""

    def test_all_engineer_identities_in_build(self, build_command_content):
        """Verify all engineer agent identities are in build.md."""
        engineers = [
            "@frontend-engineer",
            "@backend-engineer",
            "@ai-ml-engineer",
        ]
        for agent in engineers:
            assert agent in build_command_content, (
                f"Agent {agent} should be present in build.md"
            )

    def test_all_reviewer_identities_in_review(self, review_command_content):
        """Verify all reviewer agent identities are in review.md."""
        reviewers = [
            "@frontend-code-reviewer",
            "@backend-code-reviewer",
        ]
        for agent in reviewers:
            assert agent in review_command_content, (
                f"Agent {agent} should be present in review.md"
            )
