# GitHub Templates

Reusable GitHub configuration templates for project setup. These templates follow best practices from Viktor Farcic's DevOps AI Toolkit pattern.

## Usage

Copy templates to your project's `.github/` directory and customize as needed:

```bash
# Copy all templates
cp -r templates/github/* .github/

# Or copy specific templates
cp templates/github/PULL_REQUEST_TEMPLATE.md .github/
cp -r templates/github/ISSUE_TEMPLATE .github/
```

## Template Variables

Templates use `{{VARIABLE}}` syntax for customization. Replace with your project values:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{PROJECT_NAME}}` | Project name | `flowspec` |
| `{{PROJECT_OWNER}}` | GitHub owner/org | `jpoley` |
| `{{PROJECT_REPO}}` | Full repository path | `jpoley/flowspec` |
| `{{DEFAULT_BRANCH}}` | Main branch name | `main` |
| `{{MAINTAINER}}` | Primary maintainer | `@jpoley` |

## Templates Included

### Issue Templates

| File | Purpose |
|------|---------|
| `ISSUE_TEMPLATE/config.yml` | Disable blank issues, add contact links |
| `ISSUE_TEMPLATE/bug_report.yml` | Structured bug report form |
| `ISSUE_TEMPLATE/feature_request.yml` | Problem-focused feature request form |

### PR Template

| File | Purpose |
|------|---------|
| `PULL_REQUEST_TEMPLATE.md` | Comprehensive PR template with checklists |

### Code Ownership

| File | Purpose |
|------|---------|
| `CODEOWNERS` | Automatic reviewer assignment |
| `labeler.yml` | File path to label mappings |

### Workflows

| File | Purpose |
|------|---------|
| `workflows/labeler.yml` | Auto-label PRs based on files changed |
| `workflows/stale.yml` | Mark and close inactive issues/PRs |
| `workflows/scorecard.yml` | OpenSSF Scorecard security analysis |

### Release Configuration

| File | Purpose |
|------|---------|
| `release.yml` | Categorized release notes |

## Customization

### Updating Action SHAs

Action versions are pinned with full commit SHA for security. To update:

```bash
# Get latest SHA for an action
gh api repos/actions/checkout/commits/v4 --jq .sha
gh api repos/actions/labeler/commits/v5 --jq .sha
gh api repos/actions/stale/commits/v9 --jq .sha
gh api repos/ossf/scorecard-action/commits/v2 --jq .sha
```

### Required Labels

Create these labels in your repository before using the templates:

```bash
# Run from your project root
gh label create "stale" --color "eeeeee" --description "Marked stale"
gh label create "pinned" --color "0052cc" --description "Never stale"
gh label create "needs-triage" --color "d876e3" --description "Needs triage"
# ... see full list in quick-reference.md
```

## Security Considerations

- All action versions use full 40-character SHA (not tags)
- Workflows use least-privilege permissions
- `persist-credentials: false` on checkout steps
- Cron schedules avoid `:00` minute (load distribution)

## References

- [GitHub Issue Forms Documentation](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [GitHub CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [OpenSSF Scorecard](https://securityscorecards.dev/)
- [Viktor Farcic's DevOps AI Toolkit](https://github.com/vfarcic/dot-ai)
