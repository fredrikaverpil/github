# github

Central GitHub Actions repo, hosting reusable workflows, composite actions and
template workflows for GitHub projects by
[@fredrikaverpil](https://github.com/fredrikaverpil).

## Quick Start: setting up a new GitHub project

### Add sync workflow

1. Copy `templates/common/sync.yml` to your repository's
   `.github/workflows/sync.yml`.
1. Run the workflow manually from the Actions tab.
1. Merge the PR it creates.

The sync workflow detects your project type and adds all relevant workflows
automatically.

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

1. Add the token, to the GitHub project, as a repository secret:

   - Go to your repository → Settings → Secrets and variables → Actions.
   - Create a new secret named `SYNC_TOKEN` with your token value.

</details>

## Repository Structure

- `.github/workflows` - Reusable workflows that can be called from other
  repositories.
- `.github/actions` - Composite actions that can be used in workflows.
- `templates` - Workflow templates organized by project type to be synced to
  other repositories.

## Tools setup

The reusable workflows and composite actions expects tooling in the GitHub
projects.

### Go

For each `go.mod` location, add tools:

```sh
go mod init example.com
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
> Perhaps I should store all tools in a `tools/go.mod` and have CI install those
> with `go install tool` which would put all binaries in `~/go/bin` and readily
> available for all CI steps... 🤔 That way I wouldn't need to mix production
> dependencies with CI dependencies in the same `go.mod` file, and Dependabot
> would be able to tend to all updates.

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
uv add ruff --group linting
uv add mypy --group typing
uv add pytest --group testing
uv sync --all-groups
```

See official [`uv tool` docs](https://docs.astral.sh/uv/concepts/tools/) for
more details.
