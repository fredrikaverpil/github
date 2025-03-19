import os
import sys
import shutil


def main():
    # Get central repo path from environment variable
    tmp_repo_path = os.environ.get("TMP_REPO_PATH", ".tmp_repo")

    # Parse arguments
    repo_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    template_dir = sys.argv[2] if len(sys.argv) > 2 else f"{tmp_repo_path}/templates"

    # Define workflow templates and their associated file indicators
    workflow_mapping = {
        "go": ["go.mod"],
        "python": ["pyproject.toml", "uv.lock", "requirements.txt"],
    }

    # Ensure workflows directory exists
    workflows_dir = os.path.join(repo_dir, ".github", "workflows")
    os.makedirs(workflows_dir, exist_ok=True)

    # Copy common templates if they exist
    common_dir = os.path.join(template_dir, "common")
    print("Copying common workflow templates...")
    if os.path.isdir(common_dir):
        for file in os.listdir(common_dir):
            if file.endswith(".yml"):
                print(f"  - {file}")
                shutil.copy(
                    os.path.join(common_dir, file), os.path.join(workflows_dir, file)
                )

    # Excluded directories for search
    exclude_dirs = {".git", "vendor", "central", "node_modules"}

    # Process each workflow template
    for workflow_name, indicators in workflow_mapping.items():
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
            print(f"Found {workflow_name} project, copying workflow template...")
            template_file = os.path.join(template_dir, f"{workflow_name}.yml")
            if os.path.isfile(template_file):
                print(f"  - {workflow_name}.yml")
                shutil.copy(
                    template_file, os.path.join(workflows_dir, f"{workflow_name}.yml")
                )


if __name__ == "__main__":
    main()
