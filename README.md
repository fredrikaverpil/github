# github

Central repository for GitHub Actions workflows and templates.

## Quick Start

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
