"""Template placeholder detection and replacement.

This module provides utilities to detect project metadata and replace
placeholders in template files during project initialization.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def detect_project_name(project_path: Path) -> Optional[str]:
    """Detect project name from various config files.

    Priority order:
    1. pyproject.toml [project] name
    2. package.json name
    3. Cargo.toml [package] name
    4. go.mod module name
    5. Directory name as fallback

    Args:
        project_path: Path to project directory

    Returns:
        Project name or None if not detected
    """
    # Try pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        name = None
        try:
            import tomllib  # Python 3.11+ built-in

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                if "project" in data and "name" in data["project"]:
                    name = data["project"]["name"]
        except Exception:
            pass  # Will try regex fallback below

        # If tomllib didn't find the name, try regex fallback
        if not name:
            content = pyproject_path.read_text()
            match = re.search(r'^name\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                name = match.group(1)

        if name:
            return name

    # Try package.json
    package_json_path = project_path / "package.json"
    if package_json_path.exists():
        try:
            with open(package_json_path, "r") as f:
                data = json.load(f)
                if "name" in data:
                    return data["name"]
        except Exception:
            pass

    # Try Cargo.toml
    cargo_path = project_path / "Cargo.toml"
    if cargo_path.exists():
        try:
            content = cargo_path.read_text()
            match = re.search(r'^\s*name\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Try go.mod
    go_mod_path = project_path / "go.mod"
    if go_mod_path.exists():
        try:
            content = go_mod_path.read_text()
            match = re.search(r"^module\s+(\S+)", content, re.MULTILINE)
            if match:
                # Extract just the last part of the module path
                module_name = match.group(1)
                return module_name.split("/")[-1]
        except Exception:
            pass

    # Fallback to directory name
    return project_path.name


def detect_languages_and_frameworks(project_path: Path) -> str:
    """Detect programming languages and frameworks from project files.

    Args:
        project_path: Path to project directory

    Returns:
        Comma-separated list of detected languages/frameworks
    """
    detected = []

    # Python
    if (project_path / "pyproject.toml").exists() or (
        project_path / "requirements.txt"
    ).exists():
        detected.append("Python 3.11+")

        # Check for FastAPI
        pyproject = project_path / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "fastapi" in content.lower():
                detected.append("FastAPI")
            elif "flask" in content.lower():
                detected.append("Flask")

    # JavaScript/TypeScript
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, "r") as f:
                data = json.load(f)
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }

                if "typescript" in deps:
                    detected.append("TypeScript")
                elif not any("typescript" in d.lower() for d in detected):
                    detected.append("JavaScript")

                if "react" in deps:
                    detected.append("React")
                if "next" in deps:
                    detected.append("Next.js")
                if "vue" in deps:
                    detected.append("Vue.js")
        except Exception:
            detected.append("JavaScript/TypeScript")

    # Rust
    if (project_path / "Cargo.toml").exists():
        detected.append("Rust")

    # Go
    if (project_path / "go.mod").exists():
        detected.append("Go")

    return (
        ", ".join(detected) if detected else "<!-- TODO: Add languages/frameworks -->"
    )


def detect_linting_tools(project_path: Path) -> str:
    """Detect linting and formatting tools from config files.

    Args:
        project_path: Path to project directory

    Returns:
        Comma-separated list of detected linting tools
    """
    detected = []

    # Python tools
    if (project_path / "ruff.toml").exists():
        detected.append("ruff")
    elif (project_path / "pyproject.toml").exists():
        content = (project_path / "pyproject.toml").read_text()
        if "[tool.ruff]" in content:
            detected.append("ruff")

    if (project_path / ".flake8").exists():
        detected.append("flake8")

    if (project_path / "pyproject.toml").exists():
        content = (project_path / "pyproject.toml").read_text()
        if "[tool.black]" in content:
            detected.append("black")
        if "[tool.mypy]" in content:
            detected.append("mypy")

    # JavaScript/TypeScript tools
    if (project_path / ".eslintrc").exists() or (
        project_path / ".eslintrc.json"
    ).exists():
        detected.append("eslint")

    if (project_path / ".prettierrc").exists() or (
        project_path / ".prettierrc.json"
    ).exists():
        detected.append("prettier")

    if (project_path / "tsconfig.json").exists():
        detected.append("tsc")

    # Rust tools
    if (project_path / "Cargo.toml").exists():
        detected.extend(["rustfmt", "clippy"])

    # Go tools
    if (project_path / "go.mod").exists():
        detected.extend(["gofmt", "golangci-lint"])

    return ", ".join(detected) if detected else "<!-- TODO: Add linting tools -->"


def detect_project_metadata(
    project_path: Path, project_name_override: Optional[str] = None
) -> Dict[str, Any]:
    """Detect project metadata for placeholder replacement.

    Args:
        project_path: Path to project directory
        project_name_override: Optional project name to use instead of auto-detection

    Returns:
        Dictionary of placeholder values
    """
    metadata = {}

    # PROJECT_NAME
    if project_name_override:
        metadata["PROJECT_NAME"] = project_name_override
    else:
        detected_name = detect_project_name(project_path)
        metadata["PROJECT_NAME"] = detected_name if detected_name else project_path.name

    # LANGUAGES_AND_FRAMEWORKS
    metadata["LANGUAGES_AND_FRAMEWORKS"] = detect_languages_and_frameworks(project_path)

    # LINTING_TOOLS
    metadata["LINTING_TOOLS"] = detect_linting_tools(project_path)

    # DATE - current date in YYYY-MM-DD format
    metadata["DATE"] = datetime.now().strftime("%Y-%m-%d")

    return metadata


def replace_placeholders(content: str, metadata: Dict[str, Any]) -> str:
    """Replace placeholders in template content.

    Args:
        content: Template content with placeholders
        metadata: Dictionary of placeholder values

    Returns:
        Content with placeholders replaced
    """
    result = content

    # Replace detected placeholders
    for key, value in metadata.items():
        placeholder = f"[{key}]"
        result = result.replace(placeholder, str(value))

    # Mark remaining placeholders with TODO comments
    # Find all remaining [PLACEHOLDER] patterns
    remaining_placeholders = re.findall(r"\[([A-Z_0-9]+)\]", result)

    for placeholder in remaining_placeholders:
        # Check if this placeholder is already preceded by a TODO comment
        # Look for "TODO" within 100 characters before the placeholder
        pattern = f"\\[{placeholder}\\]"
        matches = list(re.finditer(pattern, result))

        for match in reversed(matches):  # Process from end to avoid offset issues
            start_pos = match.start()
            # Check 100 chars before for existing TODO
            check_start = max(0, start_pos - 100)
            preceding_text = result[check_start:start_pos]

            if "TODO" not in preceding_text:
                # No TODO comment found, add one
                result = (
                    result[:start_pos]
                    + f"<!-- TODO: Replace [{placeholder}] --> "
                    + result[start_pos:]
                )

    return result


def get_placeholder_prompts() -> Dict[str, str]:
    """Get prompts for interactive placeholder collection.

    Returns:
        Dictionary mapping placeholder names to user prompts
    """
    return {
        "PRINCIPLE_1_NAME": "Enter name for Principle 1 (e.g., 'Library-First'):",
        "PRINCIPLE_1_DESCRIPTION": "Enter description for Principle 1:",
        "PRINCIPLE_2_NAME": "Enter name for Principle 2 (e.g., 'CLI Interface'):",
        "PRINCIPLE_2_DESCRIPTION": "Enter description for Principle 2:",
        "PRINCIPLE_3_NAME": "Enter name for Principle 3 (e.g., 'Test-First'):",
        "PRINCIPLE_3_DESCRIPTION": "Enter description for Principle 3:",
        "PRINCIPLE_4_NAME": "Enter name for Principle 4 (e.g., 'Integration Testing'):",
        "PRINCIPLE_4_DESCRIPTION": "Enter description for Principle 4:",
        "PRINCIPLE_5_NAME": "Enter name for Principle 5 (e.g., 'Observability'):",
        "PRINCIPLE_5_DESCRIPTION": "Enter description for Principle 5:",
        "SECTION_2_NAME": "Enter name for Section 2 (e.g., 'Security Requirements'):",
        "SECTION_2_CONTENT": "Enter content for Section 2:",
        "SECTION_3_NAME": "Enter name for Section 3 (e.g., 'Development Workflow'):",
        "SECTION_3_CONTENT": "Enter content for Section 3:",
        "GOVERNANCE_RULES": "Enter governance rules:",
        "CONSTITUTION_VERSION": "Enter constitution version (e.g., '1.0.0'):",
        "RATIFICATION_DATE": "Enter ratification date (YYYY-MM-DD):",
        "LAST_AMENDED_DATE": "Enter last amended date (YYYY-MM-DD):",
    }


def prompt_for_placeholders(
    content: str, metadata: Dict[str, Any], interactive: bool = False
) -> Dict[str, Any]:
    """Prompt user for remaining placeholder values.

    Args:
        content: Template content to check for placeholders
        metadata: Existing metadata dictionary
        interactive: Whether to prompt user for values

    Returns:
        Updated metadata dictionary
    """
    if not interactive:
        return metadata

    # Find all placeholders in content
    placeholders = re.findall(r"\[([A-Z_0-9]+)\]", content)
    unique_placeholders = sorted(set(placeholders))

    # Filter out already-filled placeholders
    remaining = [p for p in unique_placeholders if p not in metadata]

    if not remaining:
        return metadata

    prompts = get_placeholder_prompts()

    # Simple prompting - in real implementation, would use typer.prompt or similar
    for placeholder in remaining:
        _ = prompts.get(
            placeholder, f"Enter value for {placeholder} (or leave empty for TODO):"
        )
        # For now, just mark as TODO - actual prompting would happen in CLI
        # This function is prepared for future interactive mode
        # metadata[placeholder] = typer.prompt(prompt_text, default="")

    return metadata
