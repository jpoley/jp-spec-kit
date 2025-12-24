"""CLI utilities for logging events from shell scripts.

Provides command-line interface for logging events and decisions
from shell hooks and other non-Python scripts.

Usage:
    # Log session start
    python -m flowspec_cli.logging.cli session-start

    # Log session end
    python -m flowspec_cli.logging.cli session-end

    # Log a decision
    python -m flowspec_cli.logging.cli decision \
        --decision "Use PostgreSQL" \
        --context "Choosing database" \
        --rationale "ACID compliance"

    # Log a custom event
    python -m flowspec_cli.logging.cli event \
        --category workflow.completed \
        --message "Completed /flow:implement"
"""

import argparse
import json
import sys
from typing import Optional

from flowspec_cli.logging.config import get_config
from flowspec_cli.logging.decision_logger import DecisionLogger
from flowspec_cli.logging.event_logger import EventLogger
from flowspec_cli.logging.schemas import DecisionImpact, EventCategory, LogSource


def log_session_start(details: Optional[dict] = None) -> None:
    """Log session start event."""
    logger = EventLogger()
    entry = logger.log_session_start(details=details or {})
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def log_session_end(details: Optional[dict] = None) -> None:
    """Log session end event."""
    logger = EventLogger()
    entry = logger.log_session_end(details=details or {})
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def log_decision(
    decision: str,
    context: str,
    rationale: str,
    alternatives: Optional[list[str]] = None,
    impact: str = "medium",
    reversible: bool = True,
    related_tasks: Optional[list[str]] = None,
    source: str = "agent",
) -> None:
    """Log a decision."""
    logger = DecisionLogger()

    # Map string to enum
    impact_enum = DecisionImpact(impact.lower())
    source_enum = LogSource(source.lower())

    entry = logger.log(
        decision=decision,
        context=context,
        rationale=rationale,
        alternatives=alternatives or [],
        impact=impact_enum,
        reversible=reversible,
        related_tasks=related_tasks or [],
        source=source_enum,
    )
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def log_event(
    category: str,
    message: str,
    details: Optional[dict] = None,
    task_id: Optional[str] = None,
    workflow_phase: Optional[str] = None,
    success: bool = True,
    source: str = "system",
) -> None:
    """Log a custom event."""
    logger = EventLogger()

    # Map string to enum
    category_enum = EventCategory(category)
    source_enum = LogSource(source.lower())

    entry = logger.log(
        category=category_enum,
        message=message,
        details=details or {},
        task_id=task_id,
        workflow_phase=workflow_phase,
        success=success,
        source=source_enum,
    )
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def log_git_commit(commit_hash: str, message: str, files_changed: int = 0) -> None:
    """Log a git commit event."""
    logger = EventLogger()
    entry = logger.log_git_commit(
        commit_hash=commit_hash,
        message=message,
        files_changed=files_changed,
    )
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def log_git_push(branch: str, remote: str = "origin", commits_pushed: int = 0) -> None:
    """Log a git push event."""
    logger = EventLogger()
    entry = logger.log_git_push(
        branch=branch,
        remote=remote,
        commits_pushed=commits_pushed,
    )
    print(json.dumps({"logged": True, "entry_id": entry.entry_id}))


def show_config() -> None:
    """Show current logging configuration."""
    config = get_config()
    print(
        json.dumps(
            {
                "project_root": str(config.project_root),
                "is_internal_dev": config.is_internal_dev,
                "events_dir": str(config.events_dir),
                "decisions_dir": str(config.decisions_dir),
            },
            indent=2,
        )
    )


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Flowspec logging CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # session-start command
    sp = subparsers.add_parser("session-start", help="Log session start event")
    sp.add_argument("--details", type=json.loads, default=None, help="JSON details")

    # session-end command
    sp = subparsers.add_parser("session-end", help="Log session end event")
    sp.add_argument("--details", type=json.loads, default=None, help="JSON details")

    # decision command
    sp = subparsers.add_parser("decision", help="Log a decision")
    sp.add_argument("--decision", required=True, help="The decision made")
    sp.add_argument("--context", required=True, help="Context for the decision")
    sp.add_argument("--rationale", required=True, help="Rationale for the decision")
    sp.add_argument("--alternatives", nargs="*", default=[], help="Alternatives")
    sp.add_argument(
        "--impact",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Impact level",
    )
    sp.add_argument(
        "--reversible",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Is reversible (use --no-reversible for False)",
    )
    sp.add_argument("--related-tasks", nargs="*", default=[], help="Related task IDs")
    sp.add_argument(
        "--source",
        choices=["agent", "human", "system"],
        default="agent",
        help="Decision source",
    )

    # event command
    sp = subparsers.add_parser("event", help="Log a custom event")
    sp.add_argument("--category", required=True, help="Event category")
    sp.add_argument("--message", required=True, help="Event message")
    sp.add_argument("--details", type=json.loads, default=None, help="JSON details")
    sp.add_argument("--task-id", help="Related task ID")
    sp.add_argument("--workflow-phase", help="Workflow phase")
    sp.add_argument(
        "--success",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Success flag (use --no-success for False)",
    )
    sp.add_argument(
        "--source",
        choices=["agent", "human", "hook", "backlog", "workflow", "system"],
        default="system",
        help="Event source",
    )

    # git-commit command
    sp = subparsers.add_parser("git-commit", help="Log a git commit event")
    sp.add_argument("--hash", required=True, dest="commit_hash", help="Commit hash")
    sp.add_argument("--message", required=True, help="Commit message")
    sp.add_argument("--files-changed", type=int, default=0, help="Number of files")

    # git-push command
    sp = subparsers.add_parser("git-push", help="Log a git push event")
    sp.add_argument("--branch", required=True, help="Branch name")
    sp.add_argument("--remote", default="origin", help="Remote name")
    sp.add_argument("--commits", type=int, default=0, help="Number of commits pushed")

    # config command
    subparsers.add_parser("config", help="Show logging configuration")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == "session-start":
            log_session_start(args.details)
        elif args.command == "session-end":
            log_session_end(args.details)
        elif args.command == "decision":
            log_decision(
                decision=args.decision,
                context=args.context,
                rationale=args.rationale,
                alternatives=args.alternatives,
                impact=args.impact,
                reversible=args.reversible,
                related_tasks=args.related_tasks,
                source=args.source,
            )
        elif args.command == "event":
            log_event(
                category=args.category,
                message=args.message,
                details=args.details,
                task_id=args.task_id,
                workflow_phase=args.workflow_phase,
                success=args.success,
                source=args.source,
            )
        elif args.command == "git-commit":
            log_git_commit(
                commit_hash=args.commit_hash,
                message=args.message,
                files_changed=args.files_changed,
            )
        elif args.command == "git-push":
            log_git_push(
                branch=args.branch,
                remote=args.remote,
                commits_pushed=args.commits,
            )
        elif args.command == "config":
            show_config()
        else:
            parser.print_help()
            return 1

        return 0

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
