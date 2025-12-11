#!/usr/bin/env python3
"""Validate flowspec_workflow.yml against the JSON Schema.

This script validates the workflow configuration file to ensure it conforms
to the expected structure, types, and constraints defined in the schema.

Usage:
    python scripts/validate-workflow-config.py [workflow_file] [schema_file]

    If not specified:
    - workflow_file defaults to: flowspec_workflow.yml
    - schema_file defaults to: memory/flowspec_workflow.schema.json

Examples:
    # Validate default workflow config
    python scripts/validate-workflow-config.py

    # Validate custom workflow config
    python scripts/validate-workflow-config.py custom_workflow.yml

    # Validate with custom schema
    python scripts/validate-workflow-config.py workflow.yml schema.json

Exit codes:
    0 - Validation passed
    1 - Validation failed
    2 - File not found or other error
"""

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator


def load_json(path: Path) -> dict:
    """Load JSON file."""
    with open(path) as f:
        return json.load(f)


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    with open(path) as f:
        return yaml.safe_load(f)


def validate_workflow(workflow_path: Path, schema_path: Path) -> tuple[bool, list]:
    """Validate workflow configuration against schema.

    Args:
        workflow_path: Path to workflow YAML file
        schema_path: Path to JSON schema file

    Returns:
        Tuple of (is_valid, errors_list)
    """
    try:
        schema = load_json(schema_path)
        workflow = load_yaml(workflow_path)
    except FileNotFoundError as e:
        print(f"❌ Error: File not found - {e.filename}")
        return False, [str(e)]
    except Exception as e:
        print(f"❌ Error loading files: {e}")
        return False, [str(e)]

    # Validate schema itself
    try:
        Draft7Validator.check_schema(schema)
    except Exception as e:
        print(f"❌ Error: Invalid JSON Schema - {e}")
        return False, [str(e)]

    # Validate workflow against schema
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(workflow))

    return len(errors) == 0, errors


def print_validation_errors(errors: list, verbose: bool = True) -> None:
    """Print validation errors in a readable format.

    Args:
        errors: List of validation errors from jsonschema
        verbose: If True, print detailed error information
    """
    print(f"\n❌ Found {len(errors)} validation error(s):\n")

    for i, error in enumerate(errors, 1):
        # Build path string
        path_parts = [str(p) for p in error.absolute_path]
        path_str = " → ".join(path_parts) if path_parts else "(root)"

        print(f"{i}. {error.message}")
        print(f"   Path: {path_str}")

        if verbose and error.schema_path:
            schema_path = " → ".join(str(p) for p in error.schema_path)
            print(f"   Schema constraint: {schema_path}")

        if verbose and error.instance is not None:
            # Limit instance display to avoid huge output
            instance_str = str(error.instance)
            if len(instance_str) > 100:
                instance_str = instance_str[:97] + "..."
            print(f"   Value: {instance_str}")

        print()


def main() -> int:
    """Main entry point."""
    # Parse arguments
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    workflow_file = args[0] if len(args) > 0 else "flowspec_workflow.yml"
    schema_file = args[1] if len(args) > 1 else "memory/flowspec_workflow.schema.json"

    workflow_path = Path(workflow_file)
    schema_path = Path(schema_file)

    # Print validation info
    print("=" * 70)
    print("flowspec_workflow.yml Validation")
    print("=" * 70)
    print(f"Workflow config: {workflow_path}")
    print(f"JSON Schema:     {schema_path}")
    print()

    # Check files exist
    if not workflow_path.exists():
        print(f"❌ Error: Workflow file not found: {workflow_path}")
        return 2

    if not schema_path.exists():
        print(f"❌ Error: Schema file not found: {schema_path}")
        return 2

    # Validate
    is_valid, errors = validate_workflow(workflow_path, schema_path)

    if is_valid:
        print("✅ Validation PASSED")
        print()
        print("Configuration is valid and conforms to the schema.")
        print()
        print("Validated:")
        print("  • Version format")
        print("  • States structure")
        print("  • Workflows (commands, agents, states)")
        print("  • Transitions (states, artifacts)")
        print("  • Agent loops classification")
        print("  • Metadata section")
        return 0
    else:
        print_validation_errors(errors, verbose=True)
        print("Fix the errors above and run validation again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
