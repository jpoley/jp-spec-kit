# SARIF Output Format Guide

This guide explains the SARIF (Static Analysis Results Interchange Format) output format used by `/flow:security` commands for GitHub Code Scanning integration.

## Overview

SARIF is a standard JSON format for static analysis tool output. GitHub Code Scanning, GitLab SAST, and other platforms use SARIF to display security findings.

**SARIF Version:** 2.1.0
**Schema:** https://json.schemastore.org/sarif-2.1.0.json

## Benefits of SARIF

1. **GitHub Integration** - Findings appear in GitHub Security tab
2. **Code Annotations** - Vulnerabilities annotated inline in PRs
3. **Trend Analysis** - Track security posture over time
4. **Standard Format** - Works with all SARIF-compatible tools
5. **Rich Metadata** - Severity, CWE, OWASP mappings included

## Generate SARIF Output

```bash
# Generate SARIF during security scan
flowspec security scan --format sarif --output security-results.sarif

# Upload to GitHub (via GitHub Actions)
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
```

## SARIF Structure

### Complete Example

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Flowspec Security Scanner",
          "version": "1.0.0",
          "informationUri": "https://github.com/jpoley/flowspec",
          "semanticVersion": "1.0.0",
          "rules": [
            {
              "id": "CWE-89",
              "name": "SQL Injection",
              "shortDescription": {
                "text": "SQL Injection vulnerability"
              },
              "fullDescription": {
                "text": "The application uses string concatenation to build SQL queries, allowing SQL injection attacks."
              },
              "help": {
                "text": "Use parameterized queries or prepared statements to prevent SQL injection."
              },
              "helpUri": "https://cwe.mitre.org/data/definitions/89.html",
              "properties": {
                "security-severity": "9.8",
                "precision": "high",
                "tags": ["security", "external/cwe/cwe-89"]
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "CWE-89",
          "ruleIndex": 0,
          "level": "error",
          "message": {
            "text": "SQL Injection vulnerability detected in login endpoint"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/auth/login.py",
                  "uriBaseId": "%SRCROOT%"
                },
                "region": {
                  "startLine": 45,
                  "startColumn": 10,
                  "endLine": 45,
                  "endColumn": 50,
                  "snippet": {
                    "text": "query = f\"SELECT * FROM users WHERE username = '{username}'\""
                  }
                }
              }
            }
          ],
          "properties": {
            "severity": "critical",
            "cvss": 9.8,
            "cwe": "CWE-89",
            "owasp": "A03"
          },
          "fixes": [
            {
              "description": {
                "text": "Use parameterized queries"
              },
              "artifactChanges": [
                {
                  "artifactLocation": {
                    "uri": "src/auth/login.py"
                  },
                  "replacements": [
                    {
                      "deletedRegion": {
                        "startLine": 45,
                        "startColumn": 10,
                        "endLine": 45,
                        "endColumn": 50
                      },
                      "insertedContent": {
                        "text": "query = \"SELECT * FROM users WHERE username = ?\"\nparams = (username,)"
                      }
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Key Components

### Tool Information

```json
"tool": {
  "driver": {
    "name": "Flowspec Security Scanner",
    "version": "1.0.0",
    "informationUri": "https://github.com/jpoley/flowspec",
    "semanticVersion": "1.0.0"
  }
}
```

**Fields:**
- `name` - Tool name displayed in GitHub
- `version` - Tool version
- `informationUri` - Link to tool documentation
- `semanticVersion` - Semantic versioning string

### Rules

```json
"rules": [
  {
    "id": "CWE-89",
    "name": "SQL Injection",
    "shortDescription": {
      "text": "SQL Injection vulnerability"
    },
    "fullDescription": {
      "text": "The application uses string concatenation to build SQL queries."
    },
    "help": {
      "text": "Use parameterized queries or prepared statements."
    },
    "helpUri": "https://cwe.mitre.org/data/definitions/89.html",
    "properties": {
      "security-severity": "9.8",
      "precision": "high",
      "tags": ["security", "external/cwe/cwe-89"]
    }
  }
]
```

**Fields:**
- `id` - Unique rule identifier (typically CWE ID)
- `name` - Human-readable rule name
- `shortDescription` - Brief description
- `fullDescription` - Detailed explanation
- `help` - Remediation guidance
- `helpUri` - Link to external documentation
- `properties.security-severity` - CVSS score string
- `properties.precision` - Detection accuracy (high/medium/low)
- `properties.tags` - Classification tags

### Results

```json
"results": [
  {
    "ruleId": "CWE-89",
    "ruleIndex": 0,
    "level": "error",
    "message": {
      "text": "SQL Injection vulnerability detected in login endpoint"
    },
    "locations": [...],
    "properties": {...},
    "fixes": [...]
  }
]
```

**Fields:**
- `ruleId` - Reference to rule in rules array
- `ruleIndex` - Index of rule in rules array
- `level` - Severity level (error/warning/note)
- `message` - Finding description
- `locations` - Where the issue was found
- `properties` - Additional metadata
- `fixes` - Suggested fixes (optional)

### Locations

```json
"locations": [
  {
    "physicalLocation": {
      "artifactLocation": {
        "uri": "src/auth/login.py",
        "uriBaseId": "%SRCROOT%"
      },
      "region": {
        "startLine": 45,
        "startColumn": 10,
        "endLine": 45,
        "endColumn": 50,
        "snippet": {
          "text": "query = f\"SELECT * FROM users WHERE username = '{username}'\""
        }
      }
    }
  }
]
```

**Fields:**
- `artifactLocation.uri` - File path relative to repository root
- `artifactLocation.uriBaseId` - Base ID (typically `%SRCROOT%`)
- `region.startLine` - Line number where issue starts
- `region.startColumn` - Column number where issue starts
- `region.endLine` - Line number where issue ends
- `region.endColumn` - Column number where issue ends
- `region.snippet` - Code snippet showing the issue

## Severity Levels

### SARIF Level Mapping

| Security Severity | SARIF Level | CVSS Range | GitHub Display |
|-------------------|-------------|------------|----------------|
| Critical | `error` | 9.0-10.0 | Red alert icon |
| High | `error` | 7.0-8.9 | Red alert icon |
| Medium | `warning` | 4.0-6.9 | Yellow warning icon |
| Low | `note` | 0.1-3.9 | Blue info icon |
| Info | `note` | 0.0 | Blue info icon |

### Security Severity Property

```json
"properties": {
  "security-severity": "9.8"
}
```

GitHub uses `security-severity` to determine visual priority in the Security tab.

## GitHub Code Scanning Integration

### Upload SARIF

```yaml
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
    category: flowspec-security
    wait-for-processing: true
```

**Parameters:**
- `sarif_file` - Path to SARIF file
- `category` - Tool identifier (appears in GitHub UI)
- `wait-for-processing` - Wait for GitHub to process results

### Viewing Results

**In GitHub Security Tab:**
1. Navigate to repository **Security** tab
2. Click **Code scanning alerts**
3. Filter by tool: `flowspec-security`
4. View findings by severity, status, branch

**In Pull Requests:**
1. Findings appear as annotations on changed lines
2. Click annotation to see full details
3. Dismiss false positives with reason
4. Track remediation in PR comments

### GitHub Features

- **Alerts** - Email/Slack notifications on new findings
- **Trends** - Historical security posture graphs
- **Filters** - By severity, tool, branch, status
- **Dismissal** - Mark false positives with reason
- **Integration** - Block PRs via branch protection rules

## GitLab SAST Integration

### Upload SARIF

```yaml
artifacts:
  reports:
    sast: gl-sast-report.json
```

GitLab automatically displays SARIF results in:
- Merge request security widget
- Security dashboard
- Vulnerability management

## Best Practices

### 1. Include Complete Rule Information

Always provide:
- Short and full descriptions
- Help text with remediation guidance
- Help URI linking to external documentation
- Security severity as string

### 2. Accurate Location Information

Ensure locations are precise:
- Correct line and column numbers
- Meaningful code snippets
- Relative paths from repository root

### 3. Rich Metadata

Include in `properties`:
- `severity` - Internal severity classification
- `cvss` - CVSS score (numeric)
- `cwe` - CWE identifier
- `owasp` - OWASP Top 10 category
- `confidence` - Detection confidence

### 4. Suggested Fixes

When possible, include fixes:
```json
"fixes": [
  {
    "description": {
      "text": "Use parameterized queries"
    },
    "artifactChanges": [...]
  }
]
```

### 5. Consistent Rule IDs

Use consistent IDs across scans:
- CWE IDs for vulnerability types
- Custom IDs for tool-specific rules
- Maintain backward compatibility

## Validation

### Validate SARIF Format

```bash
# Using jq
jq empty security-results.sarif

# Using schema validator
npx ajv-cli validate \
  -s https://json.schemastore.org/sarif-2.1.0.json \
  -d security-results.sarif
```

### Common Validation Errors

**Missing required fields:**
```
Error: Required property 'version' missing
Fix: Add "version": "2.1.0" at root level
```

**Invalid level:**
```
Error: Invalid value 'critical' for 'level'
Fix: Use 'error', 'warning', or 'note'
```

**Missing tool information:**
```
Error: Required property 'driver' missing
Fix: Add complete tool.driver object
```

## Example: Multiple Findings

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Flowspec Security Scanner",
          "version": "1.0.0",
          "rules": [
            {
              "id": "CWE-89",
              "name": "SQL Injection",
              "properties": {
                "security-severity": "9.8"
              }
            },
            {
              "id": "CWE-79",
              "name": "Cross-Site Scripting (XSS)",
              "properties": {
                "security-severity": "7.5"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "CWE-89",
          "level": "error",
          "message": {
            "text": "SQL Injection in login endpoint"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/auth/login.py"
                },
                "region": {
                  "startLine": 45
                }
              }
            }
          ]
        },
        {
          "ruleId": "CWE-79",
          "level": "error",
          "message": {
            "text": "XSS vulnerability in user profile"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/web/profile.js"
                },
                "region": {
                  "startLine": 102
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Troubleshooting

### GitHub Upload Fails

**Error: Invalid SARIF format**
```bash
# Validate format
jq . security-results.sarif

# Check schema compliance
npx ajv-cli validate -s https://json.schemastore.org/sarif-2.1.0.json -d security-results.sarif
```

**Error: Missing permissions**
```yaml
# Ensure workflow has correct permissions
permissions:
  security-events: write
```

**Error: File not found**
```bash
# Verify file exists
ls -l security-results.sarif

# Check path in upload step
cat $GITHUB_WORKSPACE/security-results.sarif
```

### Results Not Appearing

**Check processing status:**
1. Go to repository Settings > Code security and analysis
2. Verify Code scanning is enabled
3. Check Actions tab for upload job status

**Verify category:**
```yaml
# Ensure unique category per tool
category: flowspec-security
```

### Annotations Not Showing in PR

**Requirements:**
- PR must touch the files with findings
- Findings must be at changed lines
- SARIF upload must complete successfully

## References

- [SARIF 2.1.0 Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [GitLab SAST](https://docs.gitlab.com/ee/user/application_security/sast/)
- [SARIF Tutorials](https://github.com/microsoft/sarif-tutorials)

## See Also

- [Security Workflow Integration Guide](../../../docs/guides/security-workflow-integration.md)
- [CI/CD Integration Examples](../../../docs/platform/security-cicd-examples.md)
- [Security Commands Reference](../../../docs/reference/security-commands.md)
