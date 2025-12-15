---
id: task-311.02
title: Delete branch after PR creation failure
status: To Do
assignee:
  - '@galway'
created_date: '2025-12-08 01:43'
updated_date: '2025-12-15 02:17'
labels:
  - bug
  - ci
  - github-actions
dependencies: []
parent_task_id: task-311
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When PR creation fails in the release workflow, the orphaned branch should be deleted.

**Current behavior** (lines 108-114):
```yaml
else
  echo "⚠️ Could not create PR automatically."
  echo "📌 Manual action needed..."
  # Branch is left orphaned!
fi
```

**Proposed fix**:
```yaml
else
  echo "⚠️ Could not create PR automatically."
  echo "Cleaning up orphaned branch..."
  git push origin --delete "$BRANCH_NAME" || true
  echo "📌 Manual action needed: version files need to be updated"
fi
```

**Location**: `.github/workflows/release.yml:108-114`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Branch is deleted when PR creation fails
- [ ] #2 Deletion failure is non-fatal (|| true)
<!-- AC:END -->
