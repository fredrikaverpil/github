"""
Workflow sync script for fredrikaverpil/github

This script syncs workflow files from a central repository to a project repository
following these rules:
- Managed workflows are always updated
- Unmanaged workflows are only copied if they don't exist
- Appropriate headers are added to each file
"""

import os
import sys

MANAGED_HEADER = """# MANAGED BY fredrikaverpil/github - DO NOT EDIT
# This file is automatically updated during sync operations
# Source: https://github.com/fredrikaverpil/github
"""

MANAGED_HEADER_WITH_DATE = """# MANAGED BY fredrikaverpil/github - DO NOT EDIT
# This file is automatically updated during sync operations
# Source: https://github.com/fredrikaverpil/github
# Last synced: {date}
"""

UNMANAGED_HEADER = """# SAFE TO CUSTOMIZE - This file is copied once and not overwritten during sync
# Source: https://github.com/fredrikaverpil/github
"""


def add_header_to_file(src_path: str, dst_path: str, header: str) -> None:
    """Copy a file with a specific header prepended or replaced."""
    with open(src_path, "r") as src_file:
        content = src_file.read()

    # Check if the file already has a managed header
    import re

    header_pattern = r"^# MANAGED BY fredrikaverpil/github.*?(?=\n[^#]|\Z)"
    if re.search(header_pattern, content, re.DOTALL | re.MULTILINE):
        # Replace existing header with new header
        content = re.sub(
            header_pattern, header.rstrip(), content, flags=re.DOTALL | re.MULTILINE
        )
        with open(dst_path, "w") as dst_file:
            _ = dst_file.write(content)
    else:
        # Insert header at the beginning of the file
        with open(dst_path, "w") as dst_file:
            _ = dst_file.write(header)
            _ = dst_file.write(content)


def copy_managed_file(src_path: str, dst_path: str) -> None:
    """Copy a managed file with appropriate header."""
    # header = MANAGED_HEADER_WITH_DATE.format(date=datetime.now().strftime("%Y-%m-%d"))
    header = MANAGED_HEADER
    add_header_to_file(src_path, dst_path, header)
    print(f"  - Updated {os.path.basename(dst_path)}")


def copy_unmanaged_file(src_path: str, dst_path: str) -> None:
    """Copy an unmanaged file if it doesn't exist."""
    if os.path.exists(dst_path):
        print(f"  - Skipping {os.path.basename(dst_path)} (already exists)")
        return

    add_header_to_file(src_path, dst_path, UNMANAGED_HEADER)
    print(f"  - Added {os.path.basename(dst_path)}")


def main():
    # Get central repo path from environment variable
    tmp_repo_path = os.environ.get("TMP_REPO_PATH", ".tmp_repo")

    # Parse arguments
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    template_dir = sys.argv[2] if len(sys.argv) > 2 else f"{tmp_repo_path}/templates"

    # Ensure workflows directory exists
    workflows_dir = os.path.join(repo_dir, ".github", "workflows")
    os.makedirs(workflows_dir, exist_ok=True)

    # 1. Process managed templates (always update)
    managed_dir = os.path.join(template_dir, "managed")
    print("Processing managed workflow templates...")
    if os.path.isdir(managed_dir):
        for file in os.listdir(managed_dir):
            if file.endswith(".yml"):
                src_file = os.path.join(managed_dir, file)

                # Special handling for sync.yml to keep its name
                if file == "sync.yml":
                    dst_file = os.path.join(workflows_dir, file)
                else:
                    dst_file = os.path.join(workflows_dir, f"managed-{file}")

                copy_managed_file(src_file, dst_file)

    # 2. Process unmanaged/core templates (copy once)
    core_dir = os.path.join(template_dir, "unmanaged", "core")
    print("Processing core workflow templates...")
    if os.path.isdir(core_dir):
        for file in os.listdir(core_dir):
            if file.endswith(".yml"):
                src_file = os.path.join(core_dir, file)
                dst_file = os.path.join(workflows_dir, f"unmanaged-{file}")
                copy_unmanaged_file(src_file, dst_file)

    # 3. Process project-specific templates
    # Define workflow templates and their associated file indicators
    workflow_mapping = {
        "go": ["go.mod"],
        "python": ["pyproject.toml", "uv.lock", "requirements.txt"],
    }

    # Excluded directories for search
    exclude_dirs = {".git", "vendor", "node_modules"}

    # Process each project-specific template
    for project_type, indicators in workflow_mapping.items():
        # Check if any indicator file exists
        found = False

        for root, dirs, files in os.walk(repo_dir):
            # Skip excluded directories
            dirs[:] = [
                d for d in dirs if d not in exclude_dirs and not d.startswith(".")
            ]

            # Check if any indicator file exists in this directory
            if any(indicator in files for indicator in indicators):
                found = True
                break

        # If found, copy the corresponding workflow template
        if found:
            print(f"Found {project_type} project, copying workflow template...")
            project_dir = os.path.join(
                template_dir, "unmanaged", "project", project_type
            )

            if os.path.isdir(project_dir):
                for file in os.listdir(project_dir):
                    if file.endswith(".yml"):
                        src_file = os.path.join(project_dir, file)
                        dst_file = os.path.join(workflows_dir, f"unmanaged-{file}")
                        copy_unmanaged_file(src_file, dst_file)


if __name__ == "__main__":
    main()
