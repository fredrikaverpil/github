"""
Sync script for fredrikaverpil/github

This script syncs workflow files and configuration files from a central repository
to a project repository following these rules:
- Managed files are always updated (overwritten)
- Unmanaged files are only copied if they don't exist
- Appropriate headers are added to compatible file types
"""

import os
import sys
import shutil

MANAGED_HEADER = """# MANAGED BY fredrikaverpil/github - DO NOT EDIT
# This file is automatically updated during sync operations
# Source: https://github.com/fredrikaverpil/github

"""

UNMANAGED_HEADER = """# SAFE TO CUSTOMIZE - This file is copied once and not overwritten during sync
# Source: https://github.com/fredrikaverpil/github

"""

# Excluded directories for project search
EXCLUDE_DIRS = {".git", "vendor", "node_modules"}

# File extensions that support # comments and can safely have headers added
HEADER_COMPATIBLE_EXTENSIONS = {
    ".yml",
    ".yaml",
    ".toml",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".conf",
    ".gitignore",
    ".cfg",
}


def copy_with_header(src_path: str, dst_path: str, header: str) -> None:
    """
    Copy a file with a specific header, respecting shebangs in script files.
    """
    with open(src_path, "r") as src_file:
        content = src_file.read()

    # Check if the file already has a managed header
    import re

    header_pattern = r"^# MANAGED BY fredrikaverpil/github.*?(?=\n[^#]|\Z)"
    has_header = re.search(header_pattern, content, re.DOTALL | re.MULTILINE)

    # Check for shebang line
    has_shebang = content.startswith("#!")

    # Create destination file content
    with open(dst_path, "w") as dst_file:
        if has_header:
            # Replace existing header
            content = re.sub(
                header_pattern, header.rstrip(), content, flags=re.DOTALL | re.MULTILINE
            )
            _ = dst_file.write(content)
        elif has_shebang:
            # Keep shebang at the top, insert header after it
            shebang_line, rest_of_content = content.split("\n", 1)
            _ = dst_file.write(f"{shebang_line}\n{header}{rest_of_content}")
        else:
            # Insert header at the beginning
            _ = dst_file.write(f"{header}{content}")


def copy_file(
    src_path: str,
    dst_path: str,
    is_managed: bool,
    workflow_prefix: str | None = None,
) -> None:
    """
    Copy a file, adding header only for compatible file types.

    Args:
        src_path: Source file path
        dst_path: Destination file path
        is_managed: Whether the file is managed (always updated) or not
        workflow_prefix: If provided, add this prefix to the filename for workflows
    """
    # Handle workflow prefix if provided
    if workflow_prefix:
        filename = os.path.basename(dst_path)
        # Special handling for sync.yml to keep its name
        if filename != "sync.yml":
            dir_path = os.path.dirname(dst_path)
            dst_path = os.path.join(dir_path, f"{workflow_prefix}-{filename}")

    # If unmanaged and file exists, skip
    if not is_managed and os.path.exists(dst_path):
        print(f"  - Skipping {os.path.basename(dst_path)} (already exists)")
        return

    # Create destination directory if it doesn't exist
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    # Check if the file type supports headers
    _, ext = os.path.splitext(src_path)
    supports_header = ext.lower() in HEADER_COMPATIBLE_EXTENSIONS

    if supports_header:
        # Copy with appropriate header
        header = MANAGED_HEADER if is_managed else UNMANAGED_HEADER
        copy_with_header(src_path, dst_path, header)
    else:
        # Direct copy for files that don't support headers
        shutil.copy2(src_path, dst_path)

    action = "Updated" if is_managed else "Added"
    print(f"  - {action} {dst_path}")


def find_project_directories(repo_dir: str, indicators: list[str]) -> list[str]:
    """Find directories matching the given indicators."""
    project_dirs: list[str] = []

    for root, dirs, files in os.walk(repo_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]

        # Check if any indicator file exists in this directory
        file_indicators = [ind for ind in indicators if not ind.endswith("/")]
        if any(ind in files for ind in file_indicators):
            project_dirs.append(root)
            continue

        # Check for directory indicators
        dir_indicators = [ind.rstrip("/") for ind in indicators if ind.endswith("/")]
        if any(ind in dirs for ind in dir_indicators):
            project_dirs.append(root)

    return project_dirs


def main() -> None:
    # Get central repo path from environment variable
    tmp_repo_path = os.environ.get("TMP_REPO_PATH", ".tmp_repo")

    # Parse arguments
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    template_dir = sys.argv[2] if len(sys.argv) > 2 else f"{tmp_repo_path}/templates"

    # Define project types and their indicators
    project_mapping: dict[str, list[str]] = {
        "go": ["go.mod"],
        "python": ["pyproject.toml", "uv.lock", "requirements.txt"],
        "lua": ["lua/", "stylua.toml"],
    }

    # Detect project types once
    detected_projects: dict[str, list[str]] = {}
    for project_type, indicators in project_mapping.items():
        project_dirs = find_project_directories(repo_dir, indicators)
        if project_dirs:
            detected_projects[project_type] = project_dirs
            print(f"Found {project_type} project in: {', '.join(project_dirs)}")

    # Ensure workflows directory exists
    workflows_dir = os.path.join(repo_dir, ".github", "workflows")
    os.makedirs(workflows_dir, exist_ok=True)

    # Process workflow files
    print("\nSyncing workflow files...")

    # Simple list of (source_dir, dest_dir, is_managed, prefix)
    workflow_mappings: list[tuple[str, str, bool, str]] = [
        # Managed common workflows
        (
            os.path.join(template_dir, "managed", "common", "workflows"),
            workflows_dir,
            True,
            "managed",
        ),
        # Unmanaged common workflows
        (
            os.path.join(template_dir, "unmanaged", "common", "workflows"),
            workflows_dir,
            False,
            "unmanaged",
        ),
    ]

    # Add project-specific workflow mappings
    for project_type in detected_projects:
        # Managed project workflows
        workflow_mappings.append(
            (
                os.path.join(
                    template_dir, "managed", "project", project_type, "workflows"
                ),
                workflows_dir,
                True,
                "managed",
            )
        )
        # Unmanaged project workflows
        workflow_mappings.append(
            (
                os.path.join(
                    template_dir, "unmanaged", "project", project_type, "workflows"
                ),
                workflows_dir,
                False,
                "unmanaged",
            )
        )

    # Process workflow mappings
    for source_dir, dest_dir, is_managed, prefix in workflow_mappings:
        if not os.path.isdir(source_dir):
            continue

        print(
            f"Processing {'managed' if is_managed else 'unmanaged'} {prefix} workflows..."
        )
        for file in os.listdir(source_dir):
            # Skip .gitkeep files
            if file == ".gitkeep":
                continue

            if file.endswith(".yml"):
                src_file = os.path.join(source_dir, file)
                dst_file = os.path.join(dest_dir, file)
                copy_file(src_file, dst_file, is_managed, prefix)

    # Process configuration files
    print("\nSyncing configuration files...")

    # List of (source_dir, dest_dir, is_managed)
    file_mappings: list[tuple[str, str, bool]] = [
        # Common files
        (
            os.path.join(template_dir, "managed", "common", "files", "root"),
            repo_dir,
            True,
        ),
        (
            os.path.join(template_dir, "unmanaged", "common", "files", "root"),
            repo_dir,
            False,
        ),
    ]

    # Add project-specific file mappings
    for project_type, project_dirs in detected_projects.items():
        # Root files (both managed and unmanaged)
        file_mappings.append(
            (
                os.path.join(
                    template_dir, "managed", "project", project_type, "files", "root"
                ),
                repo_dir,
                True,
            )
        )
        file_mappings.append(
            (
                os.path.join(
                    template_dir, "unmanaged", "project", project_type, "files", "root"
                ),
                repo_dir,
                False,
            )
        )

        # Project directory files
        managed_project_files = os.path.join(
            template_dir, "managed", "project", project_type, "files", "project"
        )
        unmanaged_project_files = os.path.join(
            template_dir, "unmanaged", "project", project_type, "files", "project"
        )

        # Add mappings for each project directory
        for project_dir in project_dirs:
            if os.path.isdir(managed_project_files):
                file_mappings.append((managed_project_files, project_dir, True))
            if os.path.isdir(unmanaged_project_files):
                file_mappings.append((unmanaged_project_files, project_dir, False))

    # Process file mappings
    for source_dir, dest_dir, is_managed in file_mappings:
        if not os.path.isdir(source_dir):
            continue

        print(
            f"Processing {'managed' if is_managed else 'unmanaged'} files from {source_dir}..."
        )
        for file in os.listdir(source_dir):
            # Skip .gitkeep files
            if file == ".gitkeep":
                continue

            src_file = os.path.join(source_dir, file)
            dst_file = os.path.join(dest_dir, file)
            copy_file(src_file, dst_file, is_managed)

    print("\nSync completed successfully!")


if __name__ == "__main__":
    main()
