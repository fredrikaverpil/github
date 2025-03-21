import os
import json
import sys
import argparse
from pathlib import Path


def detect_package_ecosystem(directory):
    """
    Detect the correct package ecosystem for a directory.
    Returns a tuple of (ecosystem_name, priority)
    Higher priority will override lower priority if multiple ecosystems found.
    """
    # Check for specific files with priority
    file_ecosystem_map = {
        # Python ecosystem detection
        "uv.lock": ("uv", 100),  # Highest priority for Python
        "poetry.lock": ("pip", 90),
        "pyproject.toml": ("pip", 80),
        "requirements.txt": ("pip", 70),
        "setup.py": ("pip", 60),
        # Go ecosystem detection
        "go.mod": ("gomod", 100),
        # Node ecosystem detection
        "package-lock.json": ("npm", 100),
        "yarn.lock": ("npm", 90),
        "package.json": ("npm", 80),
        # Docker ecosystem detection
        "Dockerfile": ("docker", 80),
        "docker-compose.yml": ("docker", 70),
        "docker-compose.yaml": ("docker", 70),
        # Other ecosystems can be added here
    }

    found_ecosystems = []

    # Check for each file type
    for filename, (ecosystem, priority) in file_ecosystem_map.items():
        if os.path.exists(os.path.join(directory, filename)):
            found_ecosystems.append((ecosystem, priority))

    if not found_ecosystems:
        return None

    # Return the highest priority ecosystem
    return sorted(found_ecosystems, key=lambda x: x[1], reverse=True)[0][0]


def generate_dependabot_config(directory_matrix):
    """
    Generate dependabot.yml configuration based on detected project types
    """
    directories = directory_matrix.get("dir", [])

    # Map directories to ecosystems
    ecosystem_dirs = {}

    for directory in directories:
        ecosystem = detect_package_ecosystem(directory)
        if ecosystem:
            if ecosystem not in ecosystem_dirs:
                ecosystem_dirs[ecosystem] = []
            ecosystem_dirs[ecosystem].append(directory)

    # Build dependabot.yml content
    config = """# Dependabot configuration generated automatically
version: 2
updates:
  # Keep GitHub Actions up to date
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      github-actions:
        patterns: ["*"]
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
"""

    # Add ecosystem-specific configurations
    for ecosystem, dirs in ecosystem_dirs.items():
        # Format directories as YAML list
        dir_entries = "\n".join(f"      - {d}" for d in dirs)

        config += f"""
  # {ecosystem.upper()} dependencies
  - package-ecosystem: "{ecosystem}"
    directories:
{dir_entries}
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      {ecosystem}-minor-patch:
        patterns: ["*"]
        update-types: ["minor", "patch"]
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
"""

    return config


def main():
    parser = argparse.ArgumentParser(
        description="Generate dependabot.yml configuration"
    )
    parser.add_argument(
        "--matrix",
        required=True,
        help="JSON matrix of directories from find-dirs action",
    )
    parser.add_argument(
        "--output",
        default=".github/dependabot.yml",
        help="Output file path (default: .github/dependabot.yml)",
    )

    args = parser.parse_args()

    try:
        matrix = json.loads(args.matrix)
    except json.JSONDecodeError:
        print("Error: Invalid JSON matrix input", file=sys.stderr)
        return 1

    # Generate dependabot configuration
    config_content = generate_dependabot_config(matrix)

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Write configuration to file
    with open(args.output, "w") as f:
        f.write(config_content)

    print(f"Dependabot configuration generated at {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
