# Command Objective: `flowspec version`

## Summary
Display detailed version information for all flowspec components.

## Objective
Provide users with a clear overview of installed vs available versions for all components in the flowspec ecosystem, enabling informed upgrade decisions.

## Features

### Core Features
1. **Multi-component version display** - Shows version info for:
   - flowspec CLI (installed vs available on GitHub)
   - backlog.md (installed via npm vs available)
   - beads (installed via npm vs available)

2. **Upgrade indicators** - Visual indicators when newer versions are available

3. **Concise output** - Table format for easy scanning

### Expected Behavior
```bash
# Show all component versions
flowspec version

# Expected output format:
Component     Installed    Available
flowspec      0.3.004      0.3.004
backlog.md    1.27.1       1.27.1
beads         0.30.0       0.30.0
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec version` | Shows version table | Shows version table | PASS |
| Network timeout | Graceful handling | Graceful (shows "-") | PASS |
| All components up-to-date | No upgrade notices | No upgrade notices | PASS |

## Acceptance Criteria
- [x] Shows installed version for flowspec CLI
- [x] Shows available version from GitHub releases
- [x] Shows backlog.md installed/available versions
- [x] Shows beads installed/available versions
- [x] Handles network timeouts gracefully
- [x] Works with no GitHub token
