# github

Central GitHub Actions repo, hosting
[reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows),
[composite actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action)
and template workflows for my personal projects.

## Layout

### Folders

```text
.github/
  actions/                # Composite actions
  workflows/              # Reusable workflows
templates/
  managed/                # Workflow templates that are always updated by bootstrap/sync
    sync.yml              # The bootstrap/sync workflow itself
    sync-auto-*.yml       # Auto-updated workflows
  unmanaged/              # Workflow templates that are copied once by bootstrap and can be customized
    core/
      sync-once-*.yml     # Core workflows copied once
    project/
      go/
        sync-once-go.yml  # Project-specific workflows
      python/
        sync-once-python.yml
```

### File naming

```text
# Workflows from central repository
sync-*.yml               # Always synced/updated
sync-once-*.yml          # Copied once, safe to customize

# Generated files through central workflows
generated-*.yml

# Repository-specific custom workflows
*.yml                    # No prefix for custom workflows
```

### In destination repositories

```
.github/workflows/
  sync.yml               # Identical name to template
  sync-auto-*.yml        # Same names as in central repo
  sync-once-*.yml        # Same names as in central repo
  custom-workflow.yml    # Custom workflows with different naming pattern
```

## Quick Start: setting up a new GitHub project

### Bootstrap

1. Copy `templates/managed/sync.yml` to the new repository's
   `.github/workflows/sync.yml`.
1. Run the workflow manually from the Actions tab.
1. Review the PR it creates and customize any unmanaged workflows.

<details>
<summary>A token is required for the sync, expand to see details.</summary>

1. Create a Personal Access Token (PAT) with required permissions:

- Go to GitHub → Settings → Developer settings → Personal access tokens.
- Create a fine-grained token with:
  - "Contents: Read and write" (for commits and releases)
  - "Pull requests: Read and write" (for sync PRs, release PRs)
  - "Metadata: Read-only" (required)
  - "Workflows: Read and write" (for syncing of workflows)
- Set the repository access to include the desired repositories.

1. Add the token, to the GitHub project, as a repository secret to both Actions
   and Dependabot:

   - Go to your repository → Settings → Secrets and variables → Actions.
   - Create a new secret named `SYNC_TOKEN` with your token value.
   - Go to your repository → Settings → Secrets and variables → Dependabot.
   - Create a new secret named `SYNC_TOKEN` with your token value.

</details>

## Tools setup

The reusable workflows and composite actions expects tooling in the GitHub
projects.

> [!NOTE]
>
> This will be handled by the bootstrap in the future.

### Go

Add tools into the repo's `tools/go.mod`:

```sh
mkdir tools && cd tools
go mod init github.com/fredrikaverpil/<project>/tools

go get -tool github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go get -tool golang.org/x/vuln/cmd/govulncheck@latest
go get -tool github.com/securego/gosec/v2/cmd/gosec@latest
go get -tool golang.org/x/tools/cmd/goimports@latest
go get -tool github.com/daixiang0/gci@latest
go get -tool mvdan.cc/gofumpt@latest
go get -tool github.com/segmentio/golines@latest

go mod tidy
```

> [!NOTE]
>
> Experimental use of `golang.org/x/tools/gopls@latest` is done in CI without
> requiring `gopls` as a `go tool`.

<details>
<summary>More on Go tool usage.</summary>

```sh
# Initialize a go.tool.mod modfile
$ go mod init -modfile=go.tool.mod example.com

# Add a tool to the module
$ go get -tool -modfile=go.tool.mod golang.org/x/vuln/cmd/govulncheck

# Run the tool from the command line
$ go tool -modfile=go.tool.mod govulncheck

# List all tools added to the module
$ go list -modfile=go.tool.mod tool

# Install all tools into ~/go/bin
$ go install -modfile=go.tool.mod tool

# Verify the integrity of the tool dependencies
$ go mod verify -modfile=go.tool.mod

# Upgrade or downgrade a tool to a specific version
$ go get -tool -modfile=go.tool.mod golang.org/x/vuln/cmd/govulncheck@v1.1.2

# Upgrade all tools to their latest version
$ go get -modfile=go.tool.mod tool

# Remove a tool from the module
$ go get -tool -modfile=go.tool.mod golang.org/x/vuln/cmd/govulncheck@none
```

</details>

### Python

For each `uv.lock` file, add tools to the `pyproject.toml`'s
[PEP-735 `dependency-groups`](https://peps.python.org/pep-0735/):

```sh
uv init
uv add ruff --group lint
uv add mypy --group types
uv add coverage pytest --group test
uv sync --all-groups
```

See official [`uv tool` docs](https://docs.astral.sh/uv/concepts/tools/) for
more details.

## To do

- [ ] Add all jobs to python workflow.
- [ ] Sync issue template.
- [ ] Sync PR template.
- [ ] Generate `Taskfile.yml` for projects.
- [ ] Make bootstrap setup up tooling.
- [ ] Add `sync.yml` to this repo. Make sure dependabot.yml finds all workflow
      directories.
