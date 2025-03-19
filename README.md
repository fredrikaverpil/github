# github

Central GitHub Actions repo, hosting reusable workflows, composite actions and
template workflows for GitHub projects by
[@fredrikaverpil](https://github.com/fredrikaverpil).

## Quick Start: setting up a new GitHub project

### Add token

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

### Add sync workflow

1. Copy `templates/common/sync.yml` to your repository's
   `.github/workflows/sync.yml`.
1. Run the workflow manually from the Actions tab.
1. Merge the PR it creates.

The sync workflow detects your project type and adds all relevant workflows
automatically.

## Repository Structure

- `.github/workflows` - Reusable workflows that can be called from other
  repositories.
- `.github/actions` - Composite actions that can be used in workflows.
- `templates` - Workflow templates organized by project type to be synced to
  other repositories.
