# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Repository Purpose

This is a central GitHub Actions repository that provides reusable workflows,
composite actions, and template files for Fredrik's personal projects. It
follows a managed/unmanaged template system where:

- **Managed files**: Always updated during sync operations (overwritten)
- **Unmanaged files**: Only copied if they don't exist in target repositories

## Architecture Overview

### Template System Structure

```
templates/
  managed/           # Files that are always updated during sync
    common/          # Common files for all project types
      workflows/     # GitHub Actions workflows
      files/root/    # Files placed at repository root
    project/         # Language-specific templates
      go/            # Go-specific templates
      python/        # Python-specific templates
      lua/           # Lua-specific templates
  unmanaged/         # Files copied once, then left alone
    common/          # Common unmanaged files
    project/         # Language-specific unmanaged files
```

### Reusable Workflows

The `.github/workflows/` directory contains reusable workflows:

- `go.yml` - Go CI/CD pipeline with formatting, linting, testing, vulnerability
  checks
- `python.yml` - Python CI/CD pipeline with ruff, mypy, pytest
- `lua.yml` - Lua formatting with stylua
- `goreleaser.yml` - Go binary releases
- `opencode.yml` - AI coding assistant integration

### Composite Actions

- `find-dirs` - Discovers project directories by file patterns (e.g., find all
  Go projects by `go.mod`)
- `sync` - Syncs templates from this repository to target projects

### Key Design Patterns

1. **Matrix Strategy**: Workflows use the `find-dirs` action to create dynamic
   matrices for multi-project repos
2. **Language-Specific Taskfiles**: Each language gets its own
   `Taskfile.<lang>.yml` with conditional execution
3. **Skip Controls**: Workflows accept `skip-tests` and `skip-releases` inputs
   for project-specific control
4. **Tool Versioning**: Tools are managed in language-specific ways:
   - Go: `.tools/go.mod` with `go tool` commands
   - Python: `uv` dependency groups in `pyproject.toml`

## Common Development Commands

### Project Bootstrap

```bash
# Copy sync.yml to new repository's .github/workflows/
# Run workflow manually from Actions tab
# Review and customize the generated PR
```

### Testing This Repository

```bash
# Test the find-dirs action
python .github/actions/find-dirs/find_dirs.py --file-patterns "go.mod" --exclude-patterns "tools"

# Test sync functionality (run from target repository)
python .tmp_repo/.github/actions/sync/sync.py . .tmp_repo/templates
```

### Workflow Development

- Reusable workflows go in `.github/workflows/`
- Templates go in `templates/managed/` or `templates/unmanaged/`
- Use `actions/setup-go@v6` and `actions/checkout@v5` consistently
- All workflows should support matrix builds via `find-dirs` action

## Template System Details

### Managed vs Unmanaged Decision Matrix

- **Managed**: Core CI/CD workflows, language-specific Taskfiles, sync workflows
- **Unmanaged**: Project-specific configurations, root Taskfile.yml, project
  workflows that call reusable workflows

### File Headers

The sync system automatically adds headers:

- Managed files: `# MANAGED BY fredrikaverpil/github - DO NOT EDIT`
- Unmanaged files:
  `# SAFE TO CUSTOMIZE - This file is copied once and not overwritten`

### Taskfile Architecture

- **Root Taskfile.yml** (unmanaged): Orchestrates language-specific taskfiles
  using discovery
- **Language Taskfiles** (managed): Contain all possible tasks with conditional
  execution
- Uses `find . -name "Taskfile.*.yml"` pattern for auto-discovery

### Skip Controls Pattern

Workflows support skip inputs for project flexibility:

- `skip-tests: true` - Skip running tests in CI
- `skip-releases: true` - Skip running goreleaser
- `skip-golangci: true` - Skip golangci-lint job

## Tool Requirements for Target Projects

### Go Projects

```bash
mkdir .tools && cd .tools
go mod init github.com/fredrikaverpil/<project>/tools
go get -tool github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
go get -tool golang.org/x/vuln/cmd/govulncheck@latest
# ... additional tools as documented in README
```

### Python Projects

```bash
uv add ruff --group lint
uv add mypy --group types
uv add coverage pytest --group test
uv sync --all-groups
```

## Repository Secrets Required

Target repositories need:

- `SYNC_TOKEN` - Personal Access Token with appropriate permissions for sync
  operations
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `ANTHROPIC_API_KEY` - Optional, for opencode integration

