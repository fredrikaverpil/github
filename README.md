# github

Central repository for GitHub Actions workflows and templates.

## Quick Start: setting up a new GitHub project

1. Create a Personal Access Token with required permissions:

   - Go to GitHub → Settings → Developer settings → Personal access tokens.
   - Create a fine-grained token with "Contents: Read and write" and "Workflows:
     Read and write" permissions.
   - Set the repository access to include your repositories

1. Add the token as a repository secret:

   - Go to your repository → Settings → Secrets and variables → Actions.
   - Create a new secret named `WORKFLOW_PAT` with your token value.

1. Copy `templates/sync/sync.yml` to your repository's
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
