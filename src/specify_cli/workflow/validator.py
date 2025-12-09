"""Workflow semantic validation logic.

This module provides semantic validation for workflow configuration files,
checking for logical errors beyond JSON schema syntax validation:

- Cycle detection in state transitions (ensures DAG)
- Reachability analysis from initial state
- Reference validation (states, workflows, agents)
- Terminal state validation

Example:
    >>> config_data = {
    ...     "states": ["To Do", "In Progress", "Done"],
    ...     "workflows": {"start": {"input_states": ["To Do"], "output_state": "In Progress"}},
    ...     "transitions": [{"from": "To Do", "to": "In Progress", "via": "start"}],
    ... }
    >>> validator = WorkflowValidator(config_data)
    >>> result = validator.validate()
    >>> if not result.is_valid:
    ...     for error in result.errors:
    ...         print(error)
"""

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationSeverity(Enum):
    """Severity level for validation issues.

    ERROR: Blocks workflow execution - must be fixed
    WARNING: Non-blocking but should be addressed
    """

    ERROR = "error"
    WARNING = "warning"


@dataclass
class ValidationIssue:
    """A single validation issue found during workflow validation.

    Attributes:
        severity: Whether this issue blocks execution (ERROR) or is advisory (WARNING)
        code: Machine-readable error code (e.g., "CYCLE_DETECTED")
        message: Human-readable description of the issue
        context: Additional context data for debugging (e.g., cycle path, missing state)
    """

    severity: ValidationSeverity
    code: str
    message: str
    context: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """Format issue as [SEVERITY] CODE: message."""
        return f"[{self.severity.value.upper()}] {self.code}: {self.message}"

    def __repr__(self) -> str:
        """Include context in repr for debugging."""
        return (
            f"ValidationIssue(severity={self.severity!r}, code={self.code!r}, "
            f"message={self.message!r}, context={self.context!r})"
        )


@dataclass
class ValidationResult:
    """Result of workflow validation containing all issues found.

    Provides convenient accessors for errors vs warnings and overall validity.

    Example:
        >>> result = ValidationResult()
        >>> result.add_error("MISSING_STATE", "State 'Foo' not defined")
        >>> result.is_valid
        False
        >>> len(result.errors)
        1
    """

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if no errors found (warnings are acceptable)."""
        return not any(i.severity == ValidationSeverity.ERROR for i in self.issues)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get only error-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get only warning-level issues."""
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def add_error(self, code: str, message: str, **context: Any) -> None:
        """Add an error-level issue.

        Args:
            code: Machine-readable error code
            message: Human-readable description
            **context: Additional context data
        """
        self.issues.append(
            ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code=code,
                message=message,
                context=context,
            )
        )

    def add_warning(self, code: str, message: str, **context: Any) -> None:
        """Add a warning-level issue.

        Args:
            code: Machine-readable error code
            message: Human-readable description
            **context: Additional context data
        """
        self.issues.append(
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code=code,
                message=message,
                context=context,
            )
        )

    def __str__(self) -> str:
        """Format all issues for display."""
        if not self.issues:
            return "Validation passed: no issues found"
        return "\n".join(str(issue) for issue in self.issues)


class WorkflowValidator:
    """Validates workflow configuration for semantic correctness.

    Performs checks beyond JSON schema validation:
    - Cycle detection in state transitions (no cycles in DAG)
    - Reachability analysis from initial state
    - Reference validation (states, workflows, agents)
    - Terminal state validation

    The validator is designed for defensive coding:
    - Handles None/missing values gracefully
    - Uses .get() with defaults throughout
    - Uses defensive type checking and None-safe operations throughout
    - Provides detailed context in error messages

    Example:
        >>> config_data = {
        ...     "states": ["To Do", "In Progress", "Done"],
        ...     "workflows": {},
        ...     "transitions": [],
        ... }
        >>> validator = WorkflowValidator(config_data)
        >>> result = validator.validate()
        >>> if not result.is_valid:
        ...     for error in result.errors:
        ...         print(error)

    Attributes:
        KNOWN_AGENTS: Set of valid agent names from /jpspec command implementations
        INITIAL_STATE: The expected starting state ("To Do")
        TERMINAL_STATES: Valid ending states for workflows
    """

    # Known valid agents from agent definition files in .agents/
    # These map to the agent names used in /jpspec commands
    KNOWN_AGENTS: set[str] = {
        # Assessment & Planning
        "workflow-assessor",
        # Product & Planning
        "PM Planner",
        "product-requirements-manager",
        "product-requirements-manager-enhanced",
        # Research
        "Researcher",
        "researcher",
        "Business Validator",
        "business-validator",
        # Architecture
        "Software Architect",
        "software-architect",
        "software-architect-enhanced",
        "Platform Engineer",
        "platform-engineer",
        "platform-engineer-enhanced",
        # Engineering
        "Frontend Engineer",
        "frontend-engineer",
        "Backend Engineer",
        "backend-engineer",
        "AI/ML Engineer",
        "ai-ml-engineer",
        # Review
        "frontend-code-reviewer",
        "backend-code-reviewer",
        # Quality & Security
        "Quality Guardian",
        "quality-guardian",
        "Security Engineer",
        "secure-by-design-engineer",
        # Documentation & Release
        "Tech Writer",
        "tech-writer",
        "Release Manager",
        "release-manager",
        # Operations
        "SRE",
        "sre-agent",
    }

    # Initial state where all tasks begin
    INITIAL_STATE = "To Do"

    # Valid terminal/end states for workflows
    TERMINAL_STATES: set[str] = {"Done", "Deployed", "Cancelled", "Archived"}

    # Special transition types that are not workflows (manual state changes, rework, rollback)
    SPECIAL_TRANSITIONS: set[str] = {"manual", "rework", "rollback"}

    def __init__(self, config_data: dict[str, Any] | None = None):
        """Initialize validator with workflow configuration data.

        Args:
            config_data: Workflow configuration dictionary. If None, creates
                         empty configuration (useful for testing).
        """
        if config_data is None:
            config_data = {}

        self._data = config_data

        # Track issues found during initialization
        self._init_issues: list[ValidationIssue] = []

        # Extract and normalize states to a set
        states_raw = config_data.get("states", [])
        if isinstance(states_raw, list):
            # Handle both simple strings and state objects with 'name' key
            self._states: set[str] = set()
            for state in states_raw:
                if isinstance(state, str):
                    self._states.add(state)
                elif isinstance(state, dict):
                    if "name" not in state:
                        self._init_issues.append(
                            ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                code="STATE_MISSING_NAME",
                                message="State object missing 'name' key and was ignored.",
                                context={"state": state},
                            )
                        )
                        continue
                    name = state["name"]
                    if not isinstance(name, str):
                        self._init_issues.append(
                            ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                code="STATE_NAME_NOT_STRING",
                                message="State 'name' value is not a string and was ignored.",
                                context={"state": state},
                            )
                        )
                        continue
                    self._states.add(name)
        else:
            self._states = set()

        # Extract workflows dictionary
        self._workflows = config_data.get("workflows", {})
        if not isinstance(self._workflows, dict):
            self._workflows = {}

        # Extract transitions list
        self._transitions = config_data.get("transitions", [])
        if not isinstance(self._transitions, list):
            self._transitions = []

        # Extract agent loops if present
        self._agent_loops = config_data.get("agent_loops", {})
        if not isinstance(self._agent_loops, dict):
            self._agent_loops = {}

        # Cached graph - built lazily on first access
        self._graph: dict[str, list[str]] | None = None

    def _build_graph(self) -> dict[str, list[str]]:
        """Build adjacency list from transitions (cached).

        Returns a graph mapping each state to its list of successor states.
        The graph is built once and cached for reuse across validation methods.

        Returns:
            Dictionary mapping state names to lists of successor state names
        """
        if self._graph is not None:
            return self._graph

        self._graph = {state: [] for state in self._states}
        # Exclude special transitions (manual, rework, rollback) from graph
        # These are exception paths and shouldn't count towards cycle detection
        for transition in self._transitions:
            if not isinstance(transition, dict):
                continue
            via = transition.get("via")
            # Skip special transitions - they're allowed to create cycles
            if via in self.SPECIAL_TRANSITIONS:
                continue
            from_state = transition.get("from")
            to_state = transition.get("to")
            if from_state in self._graph and to_state in self._states:
                self._graph[from_state].append(to_state)

        return self._graph

    def validate(self) -> ValidationResult:
        """Run all validation checks and return combined result.

        Performs the following checks in order:
        1. States are defined and include initial state
        2. State references in workflows exist in states list
        3. Workflow references in transitions exist in workflows dict
        4. Agent names are valid/known
        5. No cycles in state transition graph
        6. All states reachable from initial state
        7. Terminal states are properly configured

        Returns:
            ValidationResult containing all errors and warnings found
        """
        result = ValidationResult()

        # Include any issues found during initialization
        for issue in self._init_issues:
            result.issues.append(issue)

        # Run all checks - each method adds issues to result
        self._check_states_defined(result)
        self._check_state_references(result)
        self._check_workflow_references(result)
        self._check_agent_names(result)
        self._check_cycles(result)
        self._check_reachability(result)
        self._check_terminal_states(result)

        return result

    def _check_states_defined(self, result: ValidationResult) -> None:
        """Check that states list is not empty and has initial state.

        Validates:
        - At least one state is defined
        - The initial state ("To Do") exists in states list
        """
        if not self._states:
            result.add_error(
                "EMPTY_STATES",
                "No states defined in configuration. At least one state is required.",
            )
            return

        if self.INITIAL_STATE not in self._states:
            result.add_error(
                "MISSING_INITIAL_STATE",
                f"Initial state '{self.INITIAL_STATE}' not in states list. "
                f"All workflows must start from '{self.INITIAL_STATE}'.",
                defined_states=sorted(self._states),
            )

    def _check_state_references(self, result: ValidationResult) -> None:
        """Check all states referenced in workflows exist in states list.

        Validates:
        - input_states in each workflow reference existing states
        - output_state in each workflow references an existing state
        - from/to states in transitions reference existing states
        """
        # Check workflow state references
        for workflow_name, workflow in self._workflows.items():
            if not isinstance(workflow, dict):
                result.add_error(
                    "INVALID_WORKFLOW_FORMAT",
                    f"Workflow '{workflow_name}' must be a dictionary, "
                    f"got {type(workflow).__name__}.",
                    workflow=workflow_name,
                )
                continue

            # Check input_states
            input_states = workflow.get("input_states", [])
            if isinstance(input_states, list):
                for state in input_states:
                    if state not in self._states:
                        result.add_error(
                            "UNDEFINED_INPUT_STATE",
                            f"Workflow '{workflow_name}' references undefined "
                            f"input state '{state}'.",
                            workflow=workflow_name,
                            state=state,
                            defined_states=sorted(self._states),
                        )

            # Check output_state
            output_state = workflow.get("output_state")
            if output_state and output_state not in self._states:
                result.add_error(
                    "UNDEFINED_OUTPUT_STATE",
                    f"Workflow '{workflow_name}' references undefined "
                    f"output state '{output_state}'.",
                    workflow=workflow_name,
                    state=output_state,
                    defined_states=sorted(self._states),
                )

        # Check transition state references
        for i, transition in enumerate(self._transitions):
            if not isinstance(transition, dict):
                result.add_error(
                    "INVALID_TRANSITION_FORMAT",
                    f"Transition at index {i} must be a dictionary.",
                    index=i,
                )
                continue

            from_state = transition.get("from")
            to_state = transition.get("to")

            if from_state and from_state not in self._states:
                result.add_error(
                    "UNDEFINED_FROM_STATE",
                    f"Transition references undefined 'from' state '{from_state}'.",
                    from_state=from_state,
                    defined_states=sorted(self._states),
                )

            if to_state and to_state not in self._states:
                result.add_error(
                    "UNDEFINED_TO_STATE",
                    f"Transition references undefined 'to' state '{to_state}'.",
                    to_state=to_state,
                    defined_states=sorted(self._states),
                )

    def _check_workflow_references(self, result: ValidationResult) -> None:
        """Check all workflow references in transitions exist in workflows dict.

        Validates:
        - 'via' field in transitions references a defined workflow
        """
        for i, transition in enumerate(self._transitions):
            if not isinstance(transition, dict):
                continue  # Already reported in state_references check

            via = transition.get("via")
            # Allow special transition types that are not workflows
            if (
                via
                and via not in self.SPECIAL_TRANSITIONS
                and via not in self._workflows
            ):
                result.add_error(
                    "UNDEFINED_WORKFLOW_REFERENCE",
                    f"Transition references undefined workflow '{via}'.",
                    via=via,
                    defined_workflows=sorted(self._workflows.keys()),
                    transition_index=i,
                )

    def _check_agent_names(self, result: ValidationResult) -> None:
        """Check all agent names are valid/defined.

        Validates:
        - Agents in workflows are in KNOWN_AGENTS set
        - Agents in agent_loops are in KNOWN_AGENTS set

        Uses warnings (not errors) for unknown agents to allow custom agents.
        """
        # Check agents in workflows
        for workflow_name, workflow in self._workflows.items():
            if not isinstance(workflow, dict):
                continue

            agents = workflow.get("agents", [])
            if isinstance(agents, list):
                for agent in agents:
                    # Handle both string agents and agent objects with 'name' field
                    if isinstance(agent, dict):
                        agent_name = agent.get("name")
                        if not agent_name:
                            continue
                    elif isinstance(agent, str):
                        agent_name = agent
                    else:
                        continue

                    if agent_name and agent_name not in self.KNOWN_AGENTS:
                        result.add_warning(
                            "UNKNOWN_AGENT",
                            f"Workflow '{workflow_name}' references unknown "
                            f"agent '{agent_name}'. This may be a custom agent or typo.",
                            workflow=workflow_name,
                            agent=agent_name,
                            known_agents=sorted(self.KNOWN_AGENTS),
                        )

        # Check agents in agent_loops
        for loop_type, agents in self._agent_loops.items():
            if isinstance(agents, list):
                for agent in agents:
                    # Handle both string agents and agent objects with 'name' field
                    if isinstance(agent, dict):
                        agent_name = agent.get("name")
                        if not agent_name:
                            continue
                    elif isinstance(agent, str):
                        agent_name = agent
                    else:
                        continue

                    if agent_name and agent_name not in self.KNOWN_AGENTS:
                        result.add_warning(
                            "UNKNOWN_AGENT_IN_LOOP",
                            f"Agent loop '{loop_type}' references unknown "
                            f"agent '{agent_name}'.",
                            loop_type=loop_type,
                            agent=agent_name,
                        )

    def _check_cycles(self, result: ValidationResult) -> None:
        """Check for cycles in state transition graph using DFS.

        A cycle would mean a task could loop forever through states,
        which is not valid for a workflow DAG.

        Uses depth-first search with recursion stack tracking to detect back edges.
        """
        if not self._states:
            return  # No states to check

        graph = self._build_graph()

        # DFS cycle detection
        visited: set[str] = set()
        rec_stack: set[str] = set()  # States in current DFS path
        cycles_found: list[list[str]] = []

        def _find_cycle(state: str, path: list[str]) -> bool:
            """DFS helper to find cycles. Returns True if cycle found.

            Args:
                state: Current state being visited
                path: Path from initial state to current state (inclusive)
            """
            visited.add(state)
            rec_stack.add(state)

            for next_state in graph.get(state, []):
                if next_state not in visited:
                    if _find_cycle(next_state, path + [next_state]):
                        rec_stack.discard(state)  # Clean up before returning
                        return True
                elif next_state in rec_stack:
                    # Found a back edge - extract cycle path
                    # path already includes current state, find where cycle starts
                    try:
                        cycle_start = path.index(next_state)
                        cycle_path = path[cycle_start:] + [next_state]
                    except ValueError:
                        # Shouldn't happen if next_state is in rec_stack
                        cycle_path = [state, next_state]
                    cycles_found.append(cycle_path)
                    rec_stack.discard(state)  # Clean up before returning
                    return True

            rec_stack.discard(state)
            return False

        # Check for cycles starting from each unvisited state
        for state in self._states:
            if state not in visited:
                _find_cycle(state, [state])

        # Report all cycles found
        for cycle in cycles_found:
            cycle_display = " -> ".join(cycle)
            result.add_error(
                "CYCLE_DETECTED",
                f"Cycle detected in state transitions: {cycle_display}. "
                "Workflows must be acyclic (DAG).",
                cycle=cycle,
            )

    def _build_complete_graph(self) -> dict[str, list[str]]:
        """Build adjacency list including ALL transitions (including special ones).

        This is used for reachability checks where we want to ensure all states
        are reachable (including via special manual/rework/rollback transitions).

        Returns:
            Dictionary mapping state names to lists of successor state names
        """
        graph = {state: [] for state in self._states}
        for transition in self._transitions:
            if not isinstance(transition, dict):
                continue
            from_state = transition.get("from")
            to_state = transition.get("to")
            if from_state in graph and to_state in self._states:
                graph[from_state].append(to_state)
        return graph

    def _check_reachability(self, result: ValidationResult) -> None:
        """Check all states are reachable from initial state using BFS.

        Unreachable states indicate dead code in the workflow - states that
        can never be entered because there's no path from the initial state.
        """
        if not self._states:
            return  # No states to check

        if self.INITIAL_STATE not in self._states:
            return  # Already reported in states_defined check

        # Use complete graph (including special transitions) for reachability
        graph = self._build_complete_graph()

        # BFS from initial state
        reachable: set[str] = {self.INITIAL_STATE}
        queue: deque[str] = deque([self.INITIAL_STATE])

        while queue:
            state = queue.popleft()
            for next_state in graph.get(state, []):
                if next_state not in reachable:
                    reachable.add(next_state)
                    queue.append(next_state)

        # Report unreachable states
        unreachable = self._states - reachable
        for state in sorted(unreachable):
            result.add_error(
                "UNREACHABLE_STATE",
                f"State '{state}' is not reachable from initial state "
                f"'{self.INITIAL_STATE}'. Add a transition path or remove "
                "this state.",
                state=state,
                reachable_states=sorted(reachable),
            )

    def _check_terminal_states(self, result: ValidationResult) -> None:
        """Check terminal state configuration.

        Validates:
        - At least one terminal state exists if states are defined
        - Warns if common terminal states are missing
        """
        if not self._states:
            return  # No states to check

        # Find which terminal states are present
        present_terminals = self.TERMINAL_STATES & self._states

        if not present_terminals:
            result.add_warning(
                "NO_TERMINAL_STATES",
                f"No terminal states found in configuration. "
                f"Expected at least one of: {sorted(self.TERMINAL_STATES)}. "
                "Tasks may not have a clear completion state.",
                expected_terminals=sorted(self.TERMINAL_STATES),
                defined_states=sorted(self._states),
            )

        # Check if states have outgoing transitions (non-terminal behavior)
        graph = self._build_graph()

        # Terminal states shouldn't have outgoing transitions
        for terminal in present_terminals:
            if graph.get(terminal):
                result.add_warning(
                    "TERMINAL_STATE_HAS_TRANSITIONS",
                    f"Terminal state '{terminal}' has outgoing transitions. "
                    "Terminal states typically should not transition to other states.",
                    state=terminal,
                    outgoing_transitions=graph[terminal],
                )


def validate_workflow(config_data: dict[str, Any] | None) -> ValidationResult:
    """Convenience function to validate workflow configuration.

    Args:
        config_data: Workflow configuration dictionary

    Returns:
        ValidationResult with all issues found

    Example:
        >>> result = validate_workflow({"states": [], "workflows": {}, "transitions": []})
        >>> result.is_valid
        False
    """
    validator = WorkflowValidator(config_data)
    return validator.validate()
