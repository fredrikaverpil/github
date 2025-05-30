import argparse
import json
import os
import sys

# Map of file indicators to ecosystems
FILE_ECOSYSTEM_MAP: dict[str, str] = {
    # Python ecosystem detection
    "uv.lock": "uv",
    # Go ecosystem detection
    "go.mod": "gomod",  # Only need go.mod, not go.sum
    # Node ecosystem detection
    "package.json": "npm",  # Primary specification file
    # Docker ecosystem detection
    "Dockerfile": "docker",
    "docker-compose.yml": "docker-compose",
    "docker-compose.yaml": "docker-compose",
    # Ruby ecosystem detection
    "Gemfile": "bundler",
    # PHP ecosystem detection
    "composer.json": "composer",
    # Rust ecosystem detection
    "Cargo.toml": "cargo",  # Only need Cargo.toml, not Cargo.lock
    # .NET ecosystem detection
    "packages.config": "nuget",
    "global.json": "dotnet-sdk",
    "Directory.Packages.props": "nuget",
    # Elixir ecosystem detection
    "mix.exs": "mix",
    # Elm ecosystem detection
    "elm.json": "elm",
    # Gradle ecosystem detection
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    # Maven ecosystem detection
    "pom.xml": "maven",
    # Dart/Flutter ecosystem detection
    "pubspec.yaml": "pub",
    # Swift ecosystem detection
    "Package.swift": "swift",
    # Terraform ecosystem detection
    "main.tf": "terraform",
    # Dev containers detection
    "devcontainer.json": "devcontainers",
    ".devcontainer.json": "devcontainers",
    # Git submodule detection
    ".gitmodules": "gitsubmodule",
}


def detect_package_ecosystems(directory: str) -> list[str]:
    """
    Detect all package ecosystems in a directory.
    Returns a list of detected ecosystem names.
    """
    # Set to track unique ecosystems
    found_ecosystems: set[str] = set()

    # Check for each file type
    for filename, ecosystem in FILE_ECOSYSTEM_MAP.items():
        if os.path.exists(os.path.join(directory, filename)):
            found_ecosystems.add(ecosystem)

    return list(found_ecosystems)


def recursively_scan_directories(root_dir: str) -> list[str]:
    """
    Recursively scan directories for dependency files and return directories
    that contain at least one dependency file.
    """
    directories_with_deps = set()

    for dirpath, _, filenames in os.walk(root_dir):
        if any(indicator in filenames for indicator in FILE_ECOSYSTEM_MAP.keys()):
            # Convert to relative path if root_dir is not "."
            if root_dir != "." and dirpath.startswith(root_dir):
                rel_path = os.path.relpath(dirpath, os.getcwd())
                directories_with_deps.add(rel_path)
            else:
                directories_with_deps.add(dirpath)

    return list(directories_with_deps)


def generate_dependabot_config(directory_matrix: dict[str, list[str]]) -> str:
    """
    Generate dependabot.yml configuration based on detected project types
    """
    directories: list[str] = directory_matrix.get("dir", [])

    # Map directories to ecosystems
    ecosystem_dirs: dict[str, list[str]] = {}

    for directory in directories:
        ecosystems = detect_package_ecosystems(directory)
        for ecosystem in ecosystems:
            if ecosystem not in ecosystem_dirs:
                ecosystem_dirs[ecosystem] = []
            ecosystem_dirs[ecosystem].append(directory)

    # Build dependabot.yml content
    config = """# This file was generated by https://github.com/fredrikaverpil/github
# Do not edit manually!

version: 2
updates:
  - package-ecosystem: "github-actions"
    directories: ["/", ".github/actions/*/*.yml", ".github/actions/*/*.yaml"]
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      github-actions:
        patterns: ["*"]
    labels:
      - "dependencies"
"""

    # Add ecosystem-specific configurations
    for ecosystem, dirs in ecosystem_dirs.items():
        if dirs == ["tools"]:
            # TODO: skip this for now, figure out later.
            # This should be its own entry, separate from production dependencies.
            continue

        if "tools" in dirs:
            dirs.remove("tools")  # do not mix dev tooling into production dependencies
        dir_entries = '["' + '", "'.join(dirs) + '"]'
        config += f"""
  - package-ecosystem: "{ecosystem}"
    directories: {dir_entries}
    schedule:
      interval: "weekly"
      day: "monday"
    groups:
      {ecosystem}-minor-patch:
        patterns: ["*"]
        update-types: ["minor", "patch"]
    labels:
      - "dependencies"
"""

    return config


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate dependabot.yml configuration"
    )

    # Create a mutually exclusive group for different input methods
    input_group = parser.add_mutually_exclusive_group(required=True)

    _ = input_group.add_argument(
        "--matrix",
        help='JSON matrix of directories from find-dirs action (e.g. \'{"dir": [".", "src", "packages/app"]})\'',
        type=str,
    )

    _ = input_group.add_argument(
        "--dirs",
        help="Comma-separated list of directories to scan (e.g. '.,src,packages/app')",
        type=str,
    )

    _ = input_group.add_argument(
        "--scan",
        help="Recursively scan for dependency files (default: .)",
        type=str,
        nargs="?",  # Makes the argument optional
        const=".",  # Default value if flag is provided without a value
        default=None,  # No default - still makes the parent group required
    )

    _ = input_group.add_argument(
        "--stdin",
        action="store_true",
        help="Read directories from stdin (one per line)",
    )

    _ = parser.add_argument(
        "--output",
        default=".github/dependabot.yml",
        help="Output file path (default: .github/dependabot.yml)",
        type=str,
    )

    args: argparse.Namespace = parser.parse_args()

    # Process directories based on input method
    matrix_data: dict[str, list[str]] = {}
    if args.matrix:
        try:
            matrix_data = json.loads(args.matrix)
        except json.JSONDecodeError:
            print("Error: Invalid JSON matrix input", file=sys.stderr)
            return 1
    elif args.dirs:
        dir_list = [d.strip() for d in args.dirs.split(",") if d.strip()]
        matrix_data = {"dir": dir_list}
    elif args.scan:
        dir_list = recursively_scan_directories(args.scan)
        matrix_data = {"dir": dir_list}
    elif args.stdin:
        dir_list = [line.strip() for line in sys.stdin if line.strip()]
        matrix_data = {"dir": dir_list}

    # Generate dependabot configuration
    config_content = generate_dependabot_config(matrix_data)

    # Create output directory if it doesn't exist
    output_path: str = args.output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write configuration to file
    with open(output_path, "w") as f:
        _ = f.write(config_content)

    print(f"Dependabot configuration generated at {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
