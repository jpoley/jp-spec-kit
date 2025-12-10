"""Comprehensive tests for workflow semantic validation logic.

Tests cover:
- Valid configuration passes validation
- Cycle detection catches various cycle types
- Unreachable states are properly reported
- Missing state references are caught
- Unknown agents generate warnings
- Empty/invalid configurations fail appropriately
- Edge cases (empty lists, self-loops, etc.)
"""

from specify_cli.workflow.validator import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    WorkflowValidator,
    validate_workflow,
)


class TestValidationSeverity:
    """Tests for ValidationSeverity enum."""

    def test_error_value(self):
        """ERROR severity has correct string value."""
        assert ValidationSeverity.ERROR.value == "error"

    def test_warning_value(self):
        """WARNING severity has correct string value."""
        assert ValidationSeverity.WARNING.value == "warning"


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_str_format(self):
        """Issue string format is [SEVERITY] CODE: message."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="TEST_CODE",
            message="Test message",
        )
        assert str(issue) == "[ERROR] TEST_CODE: Test message"

    def test_warning_str_format(self):
        """Warning issues use WARNING in string format."""
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            code="WARN_CODE",
            message="Warning message",
        )
        assert str(issue) == "[WARNING] WARN_CODE: Warning message"

    def test_context_included_in_repr(self):
        """Context is included in repr for debugging."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="TEST",
            message="msg",
            context={"key": "value"},
        )
        repr_str = repr(issue)
        assert "context=" in repr_str
        assert "'key': 'value'" in repr_str

    def test_empty_context_default(self):
        """Context defaults to empty dict."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            code="TEST",
            message="msg",
        )
        assert issue.context == {}


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_empty_result_is_valid(self):
        """Empty result (no issues) is valid."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_result_with_warning_is_valid(self):
        """Result with only warnings is still valid."""
        result = ValidationResult()
        result.add_warning("WARN", "A warning")
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert len(result.errors) == 0

    def test_result_with_error_is_invalid(self):
        """Result with any error is invalid."""
        result = ValidationResult()
        result.add_error("ERR", "An error")
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_add_error_with_context(self):
        """add_error accepts context kwargs."""
        result = ValidationResult()
        result.add_error("CODE", "message", state="foo", index=42)
        assert result.errors[0].context == {"state": "foo", "index": 42}

    def test_add_warning_with_context(self):
        """add_warning accepts context kwargs."""
        result = ValidationResult()
        result.add_warning("CODE", "message", agent="test-agent")
        assert result.warnings[0].context == {"agent": "test-agent"}

    def test_str_format_empty(self):
        """Empty result shows no issues message."""
        result = ValidationResult()
        assert "no issues" in str(result).lower()

    def test_str_format_with_issues(self):
        """Non-empty result shows all issues."""
        result = ValidationResult()
        result.add_error("ERR1", "First error")
        result.add_warning("WARN1", "First warning")
        str_output = str(result)
        assert "[ERROR] ERR1" in str_output
        assert "[WARNING] WARN1" in str_output


class TestWorkflowValidatorValidConfig:
    """Tests for valid workflow configurations."""

    def test_minimal_valid_config(self):
        """Minimal valid config passes validation."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        # May have warnings but no errors
        assert result.is_valid is True, f"Unexpected errors: {result.errors}"

    def test_full_valid_config(self):
        """Complete valid config passes with no errors."""
        config = {
            "states": ["To Do", "In Progress", "Done"],
            "workflows": {
                "start": {
                    "input_states": ["To Do"],
                    "output_state": "In Progress",
                    "agents": ["PM Planner"],
                }
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid is True, f"Unexpected errors: {result.errors}"

    def test_state_objects_with_name_field(self):
        """States defined as objects with 'name' field work."""
        config = {
            "states": [
                {"name": "To Do", "description": "Initial state"},
                {"name": "Done", "description": "Final state"},
            ],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid is True

    def test_complex_workflow_graph(self):
        """Complex workflow with multiple paths validates."""
        config = {
            "states": [
                "To Do",
                "Specified",
                "Researched",
                "Planned",
                "Implemented",
                "Validated",
                "Done",
            ],
            "workflows": {
                "specify": {
                    "input_states": ["To Do"],
                    "output_state": "Specified",
                },
                "research": {
                    "input_states": ["Specified"],
                    "output_state": "Researched",
                },
            },
            "transitions": [
                {"from": "To Do", "to": "Specified", "via": "specify"},
                {"from": "Specified", "to": "Researched", "via": "research"},
                {"from": "Researched", "to": "Planned"},
                {"from": "Planned", "to": "Implemented"},
                {"from": "Implemented", "to": "Validated"},
                {"from": "Validated", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid is True


class TestWorkflowValidatorEmptyStates:
    """Tests for empty states validation."""

    def test_empty_states_list_error(self):
        """Empty states list produces EMPTY_STATES error."""
        config = {"states": [], "workflows": {}, "transitions": []}
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "EMPTY_STATES" in error_codes

    def test_missing_states_key_error(self):
        """Missing states key treated as empty."""
        config = {"workflows": {}, "transitions": []}
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "EMPTY_STATES" in error_codes

    def test_none_config_handled(self):
        """None config handled gracefully."""
        result = WorkflowValidator(None).validate()
        assert not result.is_valid
        assert "EMPTY_STATES" in [e.code for e in result.errors]


class TestWorkflowValidatorInitialState:
    """Tests for initial state validation."""

    def test_missing_initial_state_error(self):
        """Missing 'To Do' state produces error."""
        config = {
            "states": ["In Progress", "Done"],
            "workflows": {},
            "transitions": [],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "MISSING_INITIAL_STATE" in error_codes

    def test_initial_state_in_context(self):
        """Missing initial state error includes defined states in context."""
        config = {
            "states": ["Custom", "Done"],
            "workflows": {},
            "transitions": [],
        }
        result = WorkflowValidator(config).validate()
        errors = [e for e in result.errors if e.code == "MISSING_INITIAL_STATE"]
        assert len(errors) == 1
        assert "defined_states" in errors[0].context


class TestWorkflowValidatorCycleDetection:
    """Tests for cycle detection in state transition graph."""

    def test_simple_cycle_detected(self):
        """Simple A -> B -> A cycle is detected."""
        config = {
            "states": ["To Do", "A", "B"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "A", "to": "B"},
                {"from": "B", "to": "A"},  # Creates cycle A -> B -> A
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "CYCLE_DETECTED" in error_codes

    def test_self_loop_detected(self):
        """Self-loop (A -> A) is detected as cycle."""
        config = {
            "states": ["To Do", "A"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "A", "to": "A"},  # Self-loop
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "CYCLE_DETECTED" in error_codes

    def test_longer_cycle_detected(self):
        """Longer cycle (A -> B -> C -> D -> A) is detected."""
        config = {
            "states": ["To Do", "A", "B", "C", "D"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
                {"from": "C", "to": "D"},
                {"from": "D", "to": "A"},  # Creates cycle
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "CYCLE_DETECTED" in error_codes

    def test_no_cycle_in_dag(self):
        """DAG without cycles passes validation."""
        config = {
            "states": ["To Do", "A", "B", "C", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "To Do", "to": "B"},  # Multiple paths from To Do
                {"from": "A", "to": "C"},
                {"from": "B", "to": "C"},  # Convergence - not a cycle
                {"from": "C", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        # No cycle errors
        cycle_errors = [e for e in result.errors if e.code == "CYCLE_DETECTED"]
        assert len(cycle_errors) == 0

    def test_cycle_path_in_context(self):
        """Cycle detection includes cycle path in context."""
        config = {
            "states": ["To Do", "X", "Y"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "X"},
                {"from": "X", "to": "Y"},
                {"from": "Y", "to": "X"},
            ],
        }
        result = WorkflowValidator(config).validate()
        cycle_errors = [e for e in result.errors if e.code == "CYCLE_DETECTED"]
        assert len(cycle_errors) >= 1
        assert "cycle" in cycle_errors[0].context

    def test_cycle_path_is_correct(self):
        """Verify the cycle path correctly includes all states in the cycle."""
        # Path: A -> B -> C -> B (cycle is B -> C -> B)
        config = {
            "states": ["To Do", "A", "B", "C"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "A", "to": "B"},
                {"from": "B", "to": "C"},
                {"from": "C", "to": "B"},  # Back edge to B
            ],
        }
        result = WorkflowValidator(config).validate()
        cycle_errors = [e for e in result.errors if e.code == "CYCLE_DETECTED"]
        assert len(cycle_errors) == 1
        cycle_path = cycle_errors[0].context.get("cycle", [])
        # The cycle should be B -> C -> B (starts and ends at B)
        assert cycle_path[0] == cycle_path[-1], (
            "Cycle should start and end at same state"
        )
        assert "B" in cycle_path and "C" in cycle_path, "Cycle should include B and C"
        assert len(cycle_path) == 3, (
            f"Cycle B->C->B should have 3 elements, got {cycle_path}"
        )


class TestWorkflowValidatorReachability:
    """Tests for state reachability validation."""

    def test_unreachable_state_error(self):
        """Unreachable state produces error."""
        config = {
            "states": ["To Do", "Reachable", "Isolated", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "Reachable"},
                {"from": "Reachable", "to": "Done"},
                # "Isolated" has no incoming transition from To Do path
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNREACHABLE_STATE" in error_codes

        # Check that Isolated is identified
        unreachable_errors = [e for e in result.errors if e.code == "UNREACHABLE_STATE"]
        states_reported = [e.context.get("state") for e in unreachable_errors]
        assert "Isolated" in states_reported

    def test_all_states_reachable(self):
        """All reachable states pass validation."""
        config = {
            "states": ["To Do", "A", "B", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "A"},
                {"from": "A", "to": "B"},
                {"from": "B", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        unreachable_errors = [e for e in result.errors if e.code == "UNREACHABLE_STATE"]
        assert len(unreachable_errors) == 0

    def test_multiple_unreachable_states(self):
        """Multiple unreachable states all reported."""
        config = {
            "states": ["To Do", "Done", "Island1", "Island2", "Island3"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "Done"},
                {"from": "Island1", "to": "Island2"},
                {"from": "Island2", "to": "Island3"},
            ],
        }
        result = WorkflowValidator(config).validate()
        unreachable_errors = [e for e in result.errors if e.code == "UNREACHABLE_STATE"]
        # Island1, Island2, Island3 are all unreachable
        assert len(unreachable_errors) == 3


class TestWorkflowValidatorStateReferences:
    """Tests for state reference validation."""

    def test_undefined_input_state_error(self):
        """Workflow with undefined input state produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "bad_workflow": {
                    "input_states": ["NonExistent"],  # Not in states
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_INPUT_STATE" in error_codes

    def test_undefined_output_state_error(self):
        """Workflow with undefined output state produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "bad_workflow": {
                    "input_states": ["To Do"],
                    "output_state": "NonExistent",  # Not in states
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_OUTPUT_STATE" in error_codes

    def test_undefined_from_state_error(self):
        """Transition with undefined from state produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "NonExistent", "to": "Done"},
                {"from": "To Do", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_FROM_STATE" in error_codes

    def test_undefined_to_state_error(self):
        """Transition with undefined to state produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "NonExistent"},
                {"from": "To Do", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_TO_STATE" in error_codes


class TestWorkflowValidatorWorkflowReferences:
    """Tests for workflow reference validation."""

    def test_undefined_workflow_via_error(self):
        """Transition referencing undefined workflow produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},  # No workflows defined
            "transitions": [
                {"from": "To Do", "to": "Done", "via": "nonexistent_workflow"}
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_WORKFLOW_REFERENCE" in error_codes

    def test_valid_workflow_reference(self):
        """Valid workflow reference passes."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {"start": {"input_states": ["To Do"], "output_state": "Done"}},
            "transitions": [{"from": "To Do", "to": "Done", "via": "start"}],
        }
        result = WorkflowValidator(config).validate()
        workflow_ref_errors = [
            e for e in result.errors if e.code == "UNDEFINED_WORKFLOW_REFERENCE"
        ]
        assert len(workflow_ref_errors) == 0


class TestWorkflowValidatorAgentNames:
    """Tests for agent name validation."""

    def test_unknown_agent_warning(self):
        """Unknown agent produces warning (not error)."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "input_states": ["To Do"],
                    "output_state": "Done",
                    "agents": ["totally-unknown-agent"],
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        # Still valid (warnings don't block)
        assert result.is_valid is True
        # But has warning
        warning_codes = [w.code for w in result.warnings]
        assert "UNKNOWN_AGENT" in warning_codes

    def test_known_agent_no_warning(self):
        """Known agent produces no warning."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "input_states": ["To Do"],
                    "output_state": "Done",
                    "agents": ["PM Planner"],  # Known agent
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        agent_warnings = [w for w in result.warnings if w.code == "UNKNOWN_AGENT"]
        assert len(agent_warnings) == 0

    def test_multiple_agents_validated(self):
        """All agents in list are validated."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "input_states": ["To Do"],
                    "output_state": "Done",
                    "agents": [
                        "PM Planner",
                        "unknown1",
                        "Backend Engineer",
                        "unknown2",
                    ],
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        agent_warnings = [w for w in result.warnings if w.code == "UNKNOWN_AGENT"]
        # Should warn about unknown1 and unknown2
        assert len(agent_warnings) == 2

    def test_agent_loops_validated(self):
        """Agents in agent_loops are also validated."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
            "agent_loops": {
                "inner_loop": ["PM Planner", "unknown-inner"],
                "outer_loop": ["SRE", "unknown-outer"],
            },
        }
        result = WorkflowValidator(config).validate()
        loop_warnings = [
            w for w in result.warnings if w.code == "UNKNOWN_AGENT_IN_LOOP"
        ]
        assert len(loop_warnings) == 2


class TestWorkflowValidatorTerminalStates:
    """Tests for terminal state validation."""

    def test_no_terminal_states_warning(self):
        """Missing terminal states produces warning."""
        config = {
            "states": ["To Do", "In Progress", "Review"],  # No Done/Deployed
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "In Progress"},
                {"from": "In Progress", "to": "Review"},
            ],
        }
        result = WorkflowValidator(config).validate()
        warning_codes = [w.code for w in result.warnings]
        assert "NO_TERMINAL_STATES" in warning_codes

    def test_terminal_state_with_outgoing_warning(self):
        """Terminal state with outgoing transitions produces warning."""
        config = {
            "states": ["To Do", "Done", "After"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "Done"},
                {"from": "Done", "to": "After"},  # Done shouldn't have outgoing
            ],
        }
        result = WorkflowValidator(config).validate()
        warning_codes = [w.code for w in result.warnings]
        assert "TERMINAL_STATE_HAS_TRANSITIONS" in warning_codes


class TestWorkflowValidatorEdgeCases:
    """Tests for edge cases and defensive coding."""

    def test_invalid_workflow_format(self):
        """Non-dict workflow produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "bad": "not a dict",  # Should be dict
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        error_codes = [e.code for e in result.errors]
        assert "INVALID_WORKFLOW_FORMAT" in error_codes

    def test_invalid_transition_format(self):
        """Non-dict transition produces error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [
                "not a dict",  # Should be dict
                {"from": "To Do", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        error_codes = [e.code for e in result.errors]
        assert "INVALID_TRANSITION_FORMAT" in error_codes

    def test_non_list_states_handled(self):
        """Non-list states handled gracefully."""
        config = {
            "states": "not a list",
            "workflows": {},
            "transitions": [],
        }
        result = WorkflowValidator(config).validate()
        # Should treat as empty
        error_codes = [e.code for e in result.errors]
        assert "EMPTY_STATES" in error_codes

    def test_non_dict_workflows_handled(self):
        """Non-dict workflows handled gracefully."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": "not a dict",
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        # Should not crash
        result = WorkflowValidator(config).validate()
        assert isinstance(result, ValidationResult)

    def test_non_list_transitions_handled(self):
        """Non-list transitions handled gracefully."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": "not a list",
        }
        # Should not crash
        result = WorkflowValidator(config).validate()
        assert isinstance(result, ValidationResult)

    def test_missing_transition_fields(self):
        """Transitions with missing from/to fields handled."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do"},  # Missing 'to'
                {"to": "Done"},  # Missing 'from'
                {},  # Empty
            ],
        }
        # Should not crash
        result = WorkflowValidator(config).validate()
        assert isinstance(result, ValidationResult)

    def test_empty_agents_list(self):
        """Empty agents list is valid."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "input_states": ["To Do"],
                    "output_state": "Done",
                    "agents": [],  # Empty is OK
                }
            },
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        # No agent warnings for empty list
        agent_warnings = [w for w in result.warnings if "AGENT" in w.code]
        assert len(agent_warnings) == 0


class TestConvenienceFunction:
    """Tests for validate_workflow convenience function."""

    def test_validate_workflow_returns_result(self):
        """validate_workflow returns ValidationResult."""
        result = validate_workflow({"states": [], "workflows": {}, "transitions": []})
        assert isinstance(result, ValidationResult)

    def test_validate_workflow_none_input(self):
        """validate_workflow handles None input."""
        result = validate_workflow(None)
        assert isinstance(result, ValidationResult)
        assert not result.is_valid

    def test_validate_workflow_valid_config(self):
        """validate_workflow passes valid config."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = validate_workflow(config)
        assert result.is_valid


class TestWorkflowValidatorKnownAgents:
    """Tests for KNOWN_AGENTS constant."""

    def test_known_agents_includes_common_agents(self):
        """KNOWN_AGENTS includes commonly used agent names."""
        expected_agents = [
            "PM Planner",
            "Researcher",
            "Backend Engineer",
            "Frontend Engineer",
            "Quality Guardian",
            "SRE",
        ]
        for agent in expected_agents:
            assert agent in WorkflowValidator.KNOWN_AGENTS

    def test_known_agents_includes_file_based_names(self):
        """KNOWN_AGENTS includes kebab-case file-based names."""
        file_based_agents = [
            "product-requirements-manager",
            "researcher",
            "backend-engineer",
            "frontend-engineer",
            "quality-guardian",
            "sre-agent",
        ]
        for agent in file_based_agents:
            assert agent in WorkflowValidator.KNOWN_AGENTS


class TestWorkflowValidatorConstants:
    """Tests for validator constants."""

    def test_initial_state_is_to_do(self):
        """INITIAL_STATE is 'To Do'."""
        assert WorkflowValidator.INITIAL_STATE == "To Do"

    def test_terminal_states_include_done(self):
        """TERMINAL_STATES includes 'Done'."""
        assert "Done" in WorkflowValidator.TERMINAL_STATES

    def test_terminal_states_include_deployed(self):
        """TERMINAL_STATES includes 'Deployed'."""
        assert "Deployed" in WorkflowValidator.TERMINAL_STATES

    def test_terminal_states_include_cancelled(self):
        """TERMINAL_STATES includes 'Cancelled'."""
        assert "Cancelled" in WorkflowValidator.TERMINAL_STATES

    def test_terminal_states_include_archived(self):
        """TERMINAL_STATES includes 'Archived'."""
        assert "Archived" in WorkflowValidator.TERMINAL_STATES


class TestWorkflowValidatorStateExtraction:
    """Tests for state extraction with validation warnings."""

    def test_state_object_missing_name_warning(self):
        """State object without 'name' key produces warning."""
        config = {
            "states": [
                "To Do",
                {"description": "Missing name key"},  # No 'name' key
                "Done",
            ],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        # Should still be valid (warning not error)
        assert result.is_valid
        warning_codes = [w.code for w in result.warnings]
        assert "STATE_MISSING_NAME" in warning_codes

    def test_state_name_not_string_warning(self):
        """State with non-string 'name' value produces warning."""
        config = {
            "states": [
                "To Do",
                {"name": 123},  # name is int, not string
                "Done",
            ],
            "workflows": {},
            "transitions": [{"from": "To Do", "to": "Done"}],
        }
        result = WorkflowValidator(config).validate()
        # Should still be valid (warning not error)
        assert result.is_valid
        warning_codes = [w.code for w in result.warnings]
        assert "STATE_NAME_NOT_STRING" in warning_codes

    def test_valid_state_object_no_warning(self):
        """Valid state object with 'name' key produces no warning."""
        config = {
            "states": [
                "To Do",
                {"name": "In Progress", "description": "Working on it"},
                "Done",
            ],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "In Progress"},
                {"from": "In Progress", "to": "Done"},
            ],
        }
        result = WorkflowValidator(config).validate()
        state_warnings = [w for w in result.warnings if w.code.startswith("STATE_")]
        assert len(state_warnings) == 0


class TestSpecialTransitions:
    """Tests for special transition types (manual, rework, rollback).

    Special transitions are exception paths that:
    - Don't require workflow definitions
    - Are excluded from cycle detection (allowed to create "cycles")
    - Are included in reachability analysis
    """

    def test_manual_transition_no_workflow_required(self):
        """Transitions with via='manual' don't need a workflow definition."""
        config = {
            "states": ["To Do", "In Progress", "Done"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Done", "via": "manual"},  # No workflow
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_WORKFLOW_REFERENCE" not in error_codes

    def test_rework_transition_no_workflow_required(self):
        """Transitions with via='rework' don't need a workflow definition."""
        config = {
            "states": ["To Do", "In Progress", "Review", "Done"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
                "review": {
                    "command": "/jpspec:review",
                    "input_states": ["In Progress"],
                },
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Review", "via": "review"},
                {"from": "Review", "to": "In Progress", "via": "rework"},  # No workflow
                {"from": "Review", "to": "Done", "via": "manual"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_WORKFLOW_REFERENCE" not in error_codes

    def test_rollback_transition_no_workflow_required(self):
        """Transitions with via='rollback' don't need a workflow definition."""
        config = {
            "states": ["To Do", "In Progress", "Deployed", "Done"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
                "deploy": {
                    "command": "/jpspec:deploy",
                    "input_states": ["In Progress"],
                },
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Deployed", "via": "deploy"},
                {
                    "from": "Deployed",
                    "to": "In Progress",
                    "via": "rollback",
                },  # No workflow
                {"from": "Deployed", "to": "Done", "via": "manual"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_WORKFLOW_REFERENCE" not in error_codes

    def test_rollback_transition_no_cycle_detected(self):
        """Rollback transitions (backward) don't trigger cycle detection."""
        config = {
            "states": ["To Do", "Validated", "Deployed"],
            "workflows": {
                "validate": {"command": "/jpspec:validate", "input_states": ["To Do"]},
                "deploy": {"command": "/jpspec:deploy", "input_states": ["Validated"]},
            },
            "transitions": [
                {"from": "To Do", "to": "Validated", "via": "validate"},
                {"from": "Validated", "to": "Deployed", "via": "deploy"},
                # This would be a cycle, but rollback is special
                {"from": "Deployed", "to": "Validated", "via": "rollback"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "CYCLE_DETECTED" not in error_codes

    def test_rework_transition_no_cycle_detected(self):
        """Rework transitions (backward) don't trigger cycle detection."""
        config = {
            "states": ["To Do", "In Progress", "Review"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
                "review": {
                    "command": "/jpspec:review",
                    "input_states": ["In Progress"],
                },
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Review", "via": "review"},
                # This would be a cycle, but rework is special
                {"from": "Review", "to": "In Progress", "via": "rework"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "CYCLE_DETECTED" not in error_codes

    def test_state_reachable_via_special_transition(self):
        """States reachable only via special transitions are not flagged as unreachable."""
        config = {
            "states": ["To Do", "In Progress", "Done"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                # Done is only reachable via manual
                {"from": "In Progress", "to": "Done", "via": "manual"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNREACHABLE_STATE" not in error_codes

    def test_undefined_non_special_via_still_errors(self):
        """Non-special via values that aren't defined workflows still error."""
        config = {
            "states": ["To Do", "Done"],
            "workflows": {},
            "transitions": [
                {"from": "To Do", "to": "Done", "via": "undefined_workflow"},
            ],
        }
        result = WorkflowValidator(config).validate()
        assert not result.is_valid
        error_codes = [e.code for e in result.errors]
        assert "UNDEFINED_WORKFLOW_REFERENCE" in error_codes

    def test_special_transitions_class_constant(self):
        """SPECIAL_TRANSITIONS is defined as a class constant."""
        assert hasattr(WorkflowValidator, "SPECIAL_TRANSITIONS")
        assert WorkflowValidator.SPECIAL_TRANSITIONS == {"manual", "rework", "rollback"}

    def test_all_special_transitions_in_one_config(self):
        """Config using all special transition types validates successfully."""
        config = {
            "states": ["To Do", "In Progress", "Review", "Deployed", "Done"],
            "workflows": {
                "start": {"command": "/jpspec:start", "input_states": ["To Do"]},
                "review": {
                    "command": "/jpspec:review",
                    "input_states": ["In Progress"],
                },
                "deploy": {"command": "/jpspec:deploy", "input_states": ["Review"]},
            },
            "transitions": [
                {"from": "To Do", "to": "In Progress", "via": "start"},
                {"from": "In Progress", "to": "Review", "via": "review"},
                {"from": "Review", "to": "In Progress", "via": "rework"},  # rework
                {"from": "Review", "to": "Deployed", "via": "deploy"},
                {"from": "Deployed", "to": "Review", "via": "rollback"},  # rollback
                {"from": "Deployed", "to": "Done", "via": "manual"},  # manual
            ],
        }
        result = WorkflowValidator(config).validate()
        assert result.is_valid
        assert len(result.errors) == 0
