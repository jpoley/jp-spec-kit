"""Workflow configuration loader and query API.

This module provides the WorkflowConfig class for loading, parsing, validating,
and querying flowspec workflow configuration files. It is the foundation for
workflow constraint enforcement in /flowspec commands.

Example:
    >>> config = WorkflowConfig.load()
    >>> agents = config.get_agents("implement")
    ['frontend-engineer', 'backend-engineer', 'code-reviewer']
    >>> next_state = config.get_next_state("Planned", "implement")
    'In Implementation'
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .exceptions import (
    WorkflowConfigError,
    WorkflowConfigNotFoundError,
    WorkflowConfigValidationError,
    WorkflowNotFoundError,
    WorkflowStateError,
)

# Default locations to search for config file (in order of priority)
# Version 2.0+ uses flowspec_workflow.yml, 1.x uses flowspec_workflow.yml
DEFAULT_CONFIG_NAMES = [
    "flowspec_workflow.yml",  # v2.0+ (preferred)
    "flowspec_workflow.yaml",
    "flowspec_workflow.yml",  # v1.x (legacy, still supported)
    "flowspec_workflow.yaml",
]

# Default locations for schema file
DEFAULT_SCHEMA_PATHS = [
    "schemas/flowspec_workflow.schema.json",  # v2.0+ (preferred)
    "memory/flowspec_workflow.schema.json",
    "memory/flowspec_workflow.schema.json",  # v1.x (legacy)
    ".specify/flowspec_workflow.schema.json",
]


class WorkflowConfig:
    """Loads and provides query API for flowspec workflow configuration.

    The workflow config defines:
    - States: Task progression stages (e.g., Specified, Planned, Validated)
    - Workflows: /flowspec commands with agent assignments
    - Transitions: Valid state changes between states
    - Agent loops: Inner/outer loop classification for agents

    This class implements the Singleton pattern for caching, ensuring that
    the configuration is loaded only once per session unless explicitly
    reloaded.

    Attributes:
        version: Configuration version string (e.g., "1.0").
        description: Human-readable description of the workflow.
        states: List of all defined state names.
        workflows: Dictionary mapping workflow names to their definitions.

    Example:
        >>> config = WorkflowConfig.load()
        >>> agents = config.get_agents("implement")
        >>> next_state = config.get_next_state("Planned", "implement")
        >>> valid_workflows = config.get_valid_workflows("Planned")

    Note:
        Configuration is cached in memory after first load. Use reload()
        or clear_cache() to force a fresh load during development.
    """

    _instance: WorkflowConfig | None = None
    _config_path: Path | None = None

    def __init__(
        self, config_data: dict[str, Any], config_path: Path | None = None
    ) -> None:
        """Initialize with validated config data.

        Args:
            config_data: Dictionary containing the parsed workflow configuration.
            config_path: Path to the config file (for reload support).

        Note:
            Use WorkflowConfig.load() instead of calling __init__ directly.
            This constructor is intended for internal use and testing.
        """
        if not isinstance(config_data, dict):
            raise WorkflowConfigError(
                f"Config data must be a dictionary, got {type(config_data).__name__}"
            )

        self._data = config_data
        self._config_path = config_path
        self._state_set: set[str] | None = None  # Lazy-loaded for performance

    @classmethod
    def load(
        cls,
        path: Path | str | None = None,
        schema_path: Path | str | None = None,
        validate: bool = True,
        cache: bool = True,
    ) -> WorkflowConfig:
        """Load workflow config from file.

        Searches for the config file in the following order:
        1. Explicit path (if provided)
        2. Current working directory (flowspec_workflow.yml)
        3. memory/ directory
        4. .specify/ directory

        Args:
            path: Explicit path to config file. If not provided, searches
                default locations.
            schema_path: Path to JSON schema for validation. If not provided,
                searches default locations.
            validate: Whether to validate against JSON schema (default: True).
            cache: Whether to cache the loaded config (default: True).

        Returns:
            WorkflowConfig instance with the loaded configuration.

        Raises:
            WorkflowConfigNotFoundError: If config file is not found.
            WorkflowConfigValidationError: If config fails schema validation.
            WorkflowConfigError: For other loading errors (invalid YAML, etc.).

        Example:
            >>> config = WorkflowConfig.load()  # Uses default locations
            >>> config = WorkflowConfig.load("/path/to/custom.yml")
            >>> config = WorkflowConfig.load(validate=False)  # Skip validation
        """
        # Return cached instance if available and caching is enabled
        if cache and cls._instance is not None:
            return cls._instance

        # Find config file
        config_path = cls._find_config_file(path)

        # Load YAML
        config_data = cls._load_yaml(config_path)

        # Validate against schema if requested
        if validate:
            schema = cls._load_schema(schema_path, config_path.parent)
            if schema is not None:
                cls._validate_schema(config_data, schema, config_path)

        # Create instance
        instance = cls(config_data, config_path)

        # Cache instance if caching is enabled
        if cache:
            cls._instance = instance
            cls._config_path = config_path

        return instance

    @classmethod
    def get_cached(cls) -> WorkflowConfig | None:
        """Get cached config instance if available.

        Returns:
            Cached WorkflowConfig instance, or None if not loaded.

        Example:
            >>> cached = WorkflowConfig.get_cached()
            >>> if cached is None:
            ...     config = WorkflowConfig.load()
        """
        return cls._instance

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached config instance.

        Call this method to force a fresh load on the next WorkflowConfig.load()
        call. Useful during development when modifying the config file.

        Example:
            >>> WorkflowConfig.clear_cache()
            >>> config = WorkflowConfig.load()  # Fresh load
        """
        cls._instance = None
        cls._config_path = None

    def reload(self) -> WorkflowConfig:
        """Reload config from file.

        Clears the cache and reloads the configuration from the original
        file path. Useful during development to pick up config changes.

        Returns:
            New WorkflowConfig instance with fresh data.

        Raises:
            WorkflowConfigError: If no config path is set (e.g., if the
                instance was created directly without load()).

        Example:
            >>> config = WorkflowConfig.load()
            >>> # ... modify flowspec_workflow.yml ...
            >>> config = config.reload()  # Pick up changes
        """
        if self._config_path is None:
            raise WorkflowConfigError(
                "Cannot reload: no config path set. "
                "Use WorkflowConfig.load() to load from a file."
            )
        self.clear_cache()
        return self.load(self._config_path)

    def get_agents(self, workflow: str) -> list[str]:
        """Get agents assigned to a workflow.

        Args:
            workflow: Name of the workflow (e.g., "implement", "validate").

        Returns:
            List of agent names assigned to the workflow.

        Raises:
            WorkflowNotFoundError: If the workflow is not defined.

        Example:
            >>> config.get_agents("implement")
            ['frontend-engineer', 'backend-engineer', 'code-reviewer']
        """
        self._validate_workflow_exists(workflow)
        workflow_def = self._data.get("workflows", {}).get(workflow, {})
        agents = workflow_def.get("agents", [])
        # Handle both simple list of strings and list of agent objects
        result = []
        for agent in agents:
            if isinstance(agent, dict):
                if "name" not in agent:
                    raise WorkflowConfigError(
                        f"Agent object in workflow '{workflow}' missing 'name' field"
                    )
                result.append(agent["name"])
            else:
                result.append(agent)
        return result

    def get_next_state(self, current_state: str, workflow: str) -> str:
        """Get the output state for a workflow.

        Given the current task state and workflow being executed, returns
        the state the task will transition to after the workflow completes.

        Args:
            current_state: The current task state (e.g., "Planned").
            workflow: The workflow being executed (e.g., "implement").

        Returns:
            The output state for the workflow.

        Raises:
            WorkflowNotFoundError: If the workflow is not defined.
            WorkflowStateError: If current_state is not a valid input state
                for this workflow.

        Example:
            >>> config.get_next_state("Planned", "implement")
            'In Implementation'
        """
        self._validate_workflow_exists(workflow)
        workflow_def = self._data.get("workflows", {}).get(workflow, {})

        # Check if current state is valid for this workflow
        input_states = workflow_def.get("input_states", [])
        if current_state not in input_states:
            raise WorkflowStateError(
                f"Cannot execute '{workflow}' from state '{current_state}'. "
                f"Valid input states: {input_states}",
                valid_states=input_states,
            )

        output_state = workflow_def.get("output_state", "")
        if not output_state:
            raise WorkflowConfigError(
                f"Workflow '{workflow}' has no output_state defined"
            )

        return output_state

    def get_input_states(self, workflow: str) -> list[str]:
        """Get valid input states for a workflow.

        Args:
            workflow: Name of the workflow.

        Returns:
            List of state names from which this workflow can be executed.

        Raises:
            WorkflowNotFoundError: If the workflow is not defined.

        Example:
            >>> config.get_input_states("implement")
            ['Planned']
        """
        self._validate_workflow_exists(workflow)
        workflow_def = self._data.get("workflows", {}).get(workflow, {})
        return list(workflow_def.get("input_states", []))

    def get_transitions(self) -> list[dict[str, str]]:
        """Get all valid state transitions.

        Returns:
            List of transition dictionaries, each containing:
            - "from": Source state name
            - "to": Destination state name
            - "via": Workflow name that triggers the transition

        Example:
            >>> transitions = config.get_transitions()
            >>> transitions[0]
            {'from': 'To Do', 'to': 'Specified', 'via': 'specify'}
        """
        return [dict(t) for t in self._data.get("transitions", [])]

    def get_valid_workflows(self, current_state: str) -> list[str]:
        """Get workflows that can be executed from current state.

        Args:
            current_state: The current task state.

        Returns:
            List of workflow names that accept this state as input.

        Example:
            >>> config.get_valid_workflows("Planned")
            ['implement']
            >>> config.get_valid_workflows("To Do")
            ['specify']
        """
        valid = []
        for workflow_name, workflow_def in self._data.get("workflows", {}).items():
            input_states = workflow_def.get("input_states", [])
            if current_state in input_states:
                valid.append(workflow_name)
        return valid

    def is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if a state transition is valid.

        A transition is valid if there exists a defined transition in the
        configuration from the source state to the destination state.

        Args:
            from_state: The source state name.
            to_state: The destination state name.

        Returns:
            True if the transition is valid, False otherwise.

        Example:
            >>> config.is_valid_transition("Planned", "In Implementation")
            True
            >>> config.is_valid_transition("To Do", "Done")
            False
        """
        for transition in self._data.get("transitions", []):
            if (
                transition.get("from") == from_state
                and transition.get("to") == to_state
            ):
                return True
        return False

    def get_workflow_for_transition(self, from_state: str, to_state: str) -> str | None:
        """Get the workflow that triggers a specific transition.

        Args:
            from_state: The source state name.
            to_state: The destination state name.

        Returns:
            The workflow name that triggers this transition, or None if
            the transition is not defined.

        Example:
            >>> config.get_workflow_for_transition("Planned", "In Implementation")
            'implement'
        """
        for transition in self._data.get("transitions", []):
            if (
                transition.get("from") == from_state
                and transition.get("to") == to_state
            ):
                return transition.get("via")
        return None

    def is_workflow_optional(self, workflow: str) -> bool:
        """Check if a workflow phase is optional.

        Args:
            workflow: Name of the workflow.

        Returns:
            True if the workflow is optional, False otherwise.

        Raises:
            WorkflowNotFoundError: If the workflow is not defined.

        Example:
            >>> config.is_workflow_optional("operate")
            True
            >>> config.is_workflow_optional("implement")
            False
        """
        self._validate_workflow_exists(workflow)
        workflow_def = self._data.get("workflows", {}).get(workflow, {})
        return workflow_def.get("optional", False)

    def get_agent_loop(self, agent: str) -> str | None:
        """Get the loop classification for an agent.

        Args:
            agent: Name of the agent.

        Returns:
            "inner_loop" or "outer_loop" if the agent is classified,
            None if not found.

        Example:
            >>> config.get_agent_loop("frontend-engineer")
            'inner_loop'
            >>> config.get_agent_loop("sre-agent")
            'outer_loop'
        """
        agent_loops = self._data.get("agent_loops", {})
        if agent in agent_loops.get("inner_loop", []):
            return "inner_loop"
        if agent in agent_loops.get("outer_loop", []):
            return "outer_loop"
        return None

    def get_agent_loops(self) -> dict[str, list[str]]:
        """Get all agent loop classifications.

        Returns:
            Dictionary with 'inner_loop' and 'outer_loop' keys,
            each containing a list of agent names. Returns a deep copy
            to prevent mutation of internal data.

        Example:
            >>> config.get_agent_loops()
            {'inner_loop': ['frontend-engineer', 'backend-engineer'],
             'outer_loop': ['sre-agent', 'security-engineer']}
        """
        agent_loops = self._data.get("agent_loops", {})
        return {key: list(agents) for key, agents in agent_loops.items()}

    @property
    def states(self) -> list[str]:
        """Get all defined states.

        Returns:
            List of all state names defined in the configuration.
            Includes built-in states "To Do" and "Done".

        Example:
            >>> config.states
            ['To Do', 'Specified', 'Researched', 'Planned', ...]
        """
        state_list = self._data.get("states", [])
        # Extract state names from state objects
        names = []
        for state in state_list:
            if isinstance(state, dict):
                name = state.get("name", "")
                if name:
                    names.append(name)
            elif isinstance(state, str):
                names.append(state)
        return names

    @property
    def all_states(self) -> list[str]:
        """Get all states including built-in To Do and Done.

        Returns:
            List of all state names, with "To Do" prepended if not present
            and "Done" appended if not present.

        Example:
            >>> config.all_states
            ['To Do', 'Specified', 'Researched', ..., 'Done']
        """
        states = self.states.copy()
        if "To Do" not in states:
            states.insert(0, "To Do")
        if "Done" not in states:
            states.append("Done")
        return states

    @property
    def workflows(self) -> dict[str, Any]:
        """Get all workflow definitions.

        Returns:
            Dictionary mapping workflow names to their definitions.

        Example:
            >>> config.workflows["implement"]
            {'command': '/flow:implement', 'agents': [...], ...}
        """
        return dict(self._data.get("workflows", {}))

    @property
    def version(self) -> str:
        """Get config version.

        Returns:
            Configuration version string (e.g., "1.0").

        Example:
            >>> config.version
            '1.0'
        """
        return str(self._data.get("version", "unknown"))

    @property
    def description(self) -> str:
        """Get config description.

        Returns:
            Human-readable description of the workflow configuration.

        Example:
            >>> config.description
            'Default Flowspec specification-driven development workflow'
        """
        return str(self._data.get("description", ""))

    @property
    def config_path(self) -> Path | None:
        """Get the path to the loaded config file.

        Returns:
            Path to the config file, or None if not loaded from a file.
        """
        return self._config_path

    # --- Private methods ---

    def _validate_workflow_exists(self, workflow: str) -> None:
        """Validate that a workflow exists in the configuration.

        Args:
            workflow: Name of the workflow to validate.

        Raises:
            WorkflowNotFoundError: If the workflow is not defined.
        """
        workflows = self._data.get("workflows", {})
        if workflow not in workflows:
            raise WorkflowNotFoundError(workflow, list(workflows.keys()))

    def _get_all_state_names(self) -> set[str]:
        """Get set of all state names for validation.

        Returns:
            Set of all state names (cached for performance).
        """
        if self._state_set is None:
            self._state_set = set(self.all_states)
        return self._state_set

    @classmethod
    def _find_config_file(cls, path: Path | str | None) -> Path:
        """Find the config file.

        Args:
            path: Explicit path, or None to search default locations.

        Returns:
            Path to the config file.

        Raises:
            WorkflowConfigNotFoundError: If config file is not found.
        """
        if path is not None:
            config_path = Path(path)
            if not config_path.exists():
                raise WorkflowConfigNotFoundError(str(config_path))
            return config_path

        # Search default locations
        cwd = Path.cwd()
        searched: list[str] = []

        for name in DEFAULT_CONFIG_NAMES:
            # Check current directory
            candidate = cwd / name
            searched.append(str(candidate))
            if candidate.exists():
                return candidate

            # Check memory/ directory
            candidate = cwd / "memory" / name
            searched.append(str(candidate))
            if candidate.exists():
                return candidate

            # Check .specify/ directory
            candidate = cwd / ".specify" / name
            searched.append(str(candidate))
            if candidate.exists():
                return candidate

        raise WorkflowConfigNotFoundError(
            "flowspec_workflow.yml", searched_paths=searched
        )

    @classmethod
    def _load_yaml(cls, path: Path) -> dict[str, Any]:
        """Load and parse YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed YAML as a dictionary.

        Raises:
            WorkflowConfigError: If YAML parsing fails.
        """
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowConfigError(
                f"Failed to parse YAML in {path}: {e}",
                details={"path": str(path), "error": str(e)},
            ) from e
        except OSError as e:
            raise WorkflowConfigError(
                f"Failed to read config file {path}: {e}",
                details={"path": str(path), "error": str(e)},
            ) from e

        if not isinstance(data, dict):
            raise WorkflowConfigError(
                f"Invalid config format in {path}: expected object, got {type(data).__name__}",
                details={"path": str(path), "type": type(data).__name__},
            )

        return data

    @classmethod
    def _load_schema(
        cls, schema_path: Path | str | None, config_dir: Path
    ) -> dict[str, Any] | None:
        """Load JSON schema for validation.

        Args:
            schema_path: Explicit path to schema, or None to search.
            config_dir: Directory containing the config file.

        Returns:
            Parsed JSON schema, or None if not found.
        """
        if schema_path is not None:
            path = Path(schema_path)
            if path.exists():
                try:
                    with open(path, encoding="utf-8") as f:
                        return json.load(f)
                except (json.JSONDecodeError, OSError):
                    return None
            return None

        # Search default locations relative to config directory
        cwd = Path.cwd()
        for rel_path in DEFAULT_SCHEMA_PATHS:
            # Check relative to cwd
            candidate = cwd / rel_path
            if candidate.exists():
                try:
                    with open(candidate, encoding="utf-8") as f:
                        return json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

            # Check relative to config directory
            candidate = config_dir / rel_path
            if candidate.exists():
                try:
                    with open(candidate, encoding="utf-8") as f:
                        return json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue

        return None

    @classmethod
    def _validate_schema(
        cls, config_data: dict[str, Any], schema: dict[str, Any], config_path: Path
    ) -> None:
        """Validate config against JSON schema.

        Args:
            config_data: Parsed config data.
            schema: JSON schema to validate against.
            config_path: Path to config file (for error messages).

        Raises:
            WorkflowConfigValidationError: If validation fails.
        """
        try:
            from jsonschema import Draft7Validator
        except ImportError:
            # jsonschema not installed, skip validation
            return

        validator = Draft7Validator(schema)
        errors: list[str] = []

        for error in validator.iter_errors(config_data):
            # Build readable error path
            path = ".".join(str(p) for p in error.absolute_path) or "(root)"
            errors.append(f"{path}: {error.message}")

        if errors:
            raise WorkflowConfigValidationError(
                f"Workflow config validation failed for {config_path}",
                errors=errors,
            )
