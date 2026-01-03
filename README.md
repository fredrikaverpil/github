# github

Central GitHub Actions repo, hosting
[reusable workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows),
[composite actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action)
and template workflows for my personal projects.

- [creosote](https://github.com/fredrikaverpil/creosote)
- [multipr](https://github.com/fredrikaverpil/multipr)
- [neotest-golang](https://github.com/fredrikaverpil/neotest-golang)
- [pr.nvim](https://github.com/fredrikaverpil/pr.nvim)
- [dependabot-generate](https://github.com/fredrikaverpil/dependabot-generate)

## Quick Start: setting up a new GitHub project

### Bootstrap

1. Copy `templates/managed/workflows/sync.yml` to the new repository's
   `.github/workflows/sync.yml`.
1. Run the workflow manually from the Actions tab.
1. Review the PR it creates and customize any unmanaged workflows.

<details>
<summary>A token is required for the sync, expand to see details.</summary>

1. Create a Personal Access Token (PAT) with required permissions:

- Go to GitHub → Settings → Developer settings → Personal access tokens.
- Create a fine-grained token with the following _Repository_ permissions:
  - "Actions: Read and write" (for triggering actions, workflows)
  - "Contents: Read and write" (for commits and releases)
  - "Pull requests: Read and write" (for sync PRs, release PRs)
  - "Metadata: Read-only" (required)
  - "Workflows: Read and write" (for updating GitHub Action workflow files)
- Set the repository access to include the desired repositories.

1. Add the token, to the GitHub project, as a repository secret to both Actions
   and Dependabot:
   - Go to your repository → Settings → Secrets and variables → Actions.
   - Create a new secret named `SYNC_TOKEN` with your token value.
   - Go to your repository → Settings → Secrets and variables → Dependabot.
   - Create a new secret named `SYNC_TOKEN` with your token value.

</details>

> [!NOTE]
>
> No need to remove any bootsrapping files, as they will serve the purpose of
> syncing workflows.

## Files and folders layout

### This repo

```text
.github/
  actions/           # Composite actions
  workflows/         # Reusable workflows
templates/
  managed/           # Workflows that are always updated by bootstrap/sync
  unmanaged/         # Workflows that are only copied if they do not already exist
```

For both `managed` and `unmanaged` folders:

```text
common/
  files/
    root/
      *.*            # Files and folders to be stored relative to root
  workflows/
    *.yml

project/
  <project-type>/    # Project folder (e.g. "go", "python" etc)
    files/
      project/       # Files and folders to be stored relative to project
        *.*
      root/
        *.*          # Files and folders to be stored relative to root
    workflows/
      *.yml
```

### Target repos

Workflows are synced over to the target project like so:

- `.github/workflows/sync.yml`
- `.github/workflows/managed-*.yml`
- `.github/workflows/unmanaged-*.yml`

Files are synced over with their filenames intact. Managed files will always be
updated while unmanaged files will only be copied to the target repo if they do
not already exist.

## Assumptions

- Churn and getting out of sync is avoided by storing managed workflows,
  actions, files and scripts centrally in this repo.
- CI is set up for local-first development. Everything that executes in the
  target project's CI must be invoked in a way so that it can also be reproduced
  locally.
- All dependency versions management is delegated to the target project.
- The user is expected to open their editor in the git repo root. This is where
  commandline tasks are carried out (e.g. `Taskfile.yml` commands).

## Tools setup

The reusable workflows and composite actions expects tooling in the GitHub
projects.

> [!NOTE]
>
> This will be handled by the bootstrap in the future.

### Go

Tools and their versions are managed directly in the managed `Taskfile.go.yml`
using `go run <package>@<version>`.

You can install all tools into your `~/go/bin` by running:

```sh
task -t Taskfile.go.yml install-tools
```

> [!NOTE]
>
> `gopls` is not included in `install-tools` but can be installed via
> `task -t Taskfile.go.yml install-gopls`.

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

By importance/priority:

- [ ] When Go has just been bumped, this error may be hit in CI if bumping Go
      (reason is actions/setup-go is not updated yet with the latest Go version
      and GOTOOLCHAIN enforces this version):
  ```sh
  Run go install tool
  go: go.mod requires go >= 1.24.5 (running go 1.24.4; GOTOOLCHAIN=local)
  Error: Process completed with exit code 1.
  ```
- [ ] Review `.golangci.yml`, compare against einride/sage's golangci-lint v2
      config.
- [ ] Add docs on that the managed `Taskfile.[lang].yml` contains all the
      possible tasks. The unmanaged `Taskfile.yml` then chooses what to use.
      Ideally, CI would call `Taskfile.yml` but this will add considerable
      amount of complexity, if we want to keep the CI optimizations in place,
      which runs each task as a separate job. **Done**: Documented in
      AGENTS.md - Taskfile Architecture section.
- [ ] Sync issue template to target repo.
- [ ] Sync PR template to target repo.
- [ ] Generate `Taskfile.yml` for projects.
- [ ] Make bootstrap setup up tooling?
- [ ] ~Make `task` part of default tooling.~ We can use the official GHA task
      instead for now.
