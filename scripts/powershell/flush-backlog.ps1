#!/usr/bin/env pwsh

# Backlog flush script (PowerShell)
#
# This script archives Done tasks from the backlog and generates summary reports.
# It queries the backlog.md CLI for tasks with "Done" status, archives them,
# and optionally generates a timestamped summary markdown file.
#
# Usage: ./flush-backlog.ps1 [OPTIONS]
#
# OPTIONS:
#   -DryRun             Show what would be archived without making changes
#   -NoSummary          Skip generating the summary report
#   -AutoCommit         Automatically commit changes to git
#   -Help, -h           Show help message
#
# EXIT CODES:
#   0 - Success (tasks archived or no tasks to archive)
#   1 - Validation error (missing dependencies or invalid configuration)
#   2 - No Done tasks found
#   3 - Partial failures (some tasks failed to archive)

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$NoSummary,
    [switch]$AutoCommit,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'

# Configuration
$BacklogDir = "backlog"
$ArchiveDir = Join-Path $BacklogDir "archive"
$ArchiveTasksDir = Join-Path $ArchiveDir "tasks"

# Show help if requested
if ($Help) {
    Write-Output @"
Usage: flush-backlog.ps1 [OPTIONS]

Archives Done tasks from the backlog and generates summary reports.

OPTIONS:
  -DryRun             Show what would be archived without making changes
  -NoSummary          Skip generating the summary report
  -AutoCommit         Automatically commit changes to git
  -Help, -h           Show this help message

EXIT CODES:
  0 - Success (tasks archived or no tasks to archive)
  1 - Validation error (missing dependencies or invalid configuration)
  2 - No Done tasks found
  3 - Partial failures (some tasks failed to archive)

EXAMPLES:
  # Preview tasks that would be archived
  .\flush-backlog.ps1 -DryRun

  # Archive tasks and commit changes
  .\flush-backlog.ps1 -AutoCommit

  # Archive without generating summary
  .\flush-backlog.ps1 -NoSummary

"@
    exit 0
}

# Function to check prerequisites
function Test-Prerequisites {
    # Check backlog CLI
    try {
        $null = Get-Command backlog -ErrorAction Stop
    }
    catch {
        Write-Error "ERROR: backlog.md CLI not found. Install with: npm install -g backlog.md"
        exit 1
    }

    # Check backlog directory
    if (-not (Test-Path $BacklogDir -PathType Container)) {
        Write-Error "ERROR: No backlog directory found. Run from project root or initialize with 'backlog init'"
        exit 1
    }
}

# Function to get Done tasks from backlog
function Get-DoneTasks {
    Write-Verbose "Querying backlog for Done tasks..."

    $output = backlog task list -s Done --plain 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ERROR: Failed to query backlog: $output"
        exit 1
    }

    $tasks = @()
    $inDoneSection = $false

    foreach ($line in ($output -split "`r?`n")) {
        $line = $line.Trim()

        # Look for the "Done:" section header
        if ($line -match "^Done:") {
            $inDoneSection = $true
            continue
        }

        # Stop if we hit another section
        if ($inDoneSection -and $line -match "^[A-Za-z\s]+:$") {
            break
        }

        # Parse task lines in Done section
        # Format can be: "  [US1] task-42 - Some Title"
        if ($inDoneSection -and $line -match "^\s*(?:\[[\w\d]+\]\s*)?(task-\d+)\s*-\s*(.+)$") {
            $tasks += @{
                Id = $Matches[1]
                Title = $Matches[2].Trim()
            }
        }
    }

    return $tasks
}

# Function to extract task metadata from archived file
function Get-TaskMetadata {
    param([string]$TaskId)

    # Find the archived task file
    $pattern = "$TaskId - *.md"
    $taskFile = Get-ChildItem -Path $ArchiveTasksDir -Filter $pattern -ErrorAction SilentlyContinue | Select-Object -First 1

    if (-not $taskFile) {
        Write-Verbose "Metadata not found for $TaskId (file may not be archived yet)"
        return @{
            Title = "Unknown"
            Status = "Done"
            Priority = "None"
            Assignee = "None"
            Labels = @()
            AcCompleted = 0
            AcTotal = 0
        }
    }

    $content = Get-Content $taskFile.FullName -Raw

    # Parse YAML frontmatter
    $metadata = @{
        Title = "Unknown"
        Status = "Done"
        Priority = "None"
        Assignee = "None"
        Labels = @()
        AcCompleted = 0
        AcTotal = 0
    }

    # Extract title
    if ($content -match "(?m)^title:\s*(.+)$") {
        $metadata.Title = $Matches[1].Trim()
    }

    # Extract priority
    if ($content -match "(?m)^priority:\s*(.+)$") {
        $metadata.Priority = $Matches[1].Trim()
    }

    # Extract assignee
    if ($content -match "(?m)^assignee:\s*\[?(.+?)\]?\s*$") {
        $assigneeValue = $Matches[1].Trim()
        # Remove array brackets if present
        $assigneeValue = $assigneeValue -replace '^\[|\]$', ''
        $metadata.Assignee = $assigneeValue
    }

    # Extract labels
    if ($content -match "(?m)^labels:\s*\[(.+?)\]") {
        $labelsStr = $Matches[1].Trim()
        $metadata.Labels = ($labelsStr -split ',\s*' | ForEach-Object { $_.Trim() })
    }

    # Count acceptance criteria (both checked and unchecked)
    $acMatches = [regex]::Matches($content, '- \[([ x])\]')
    $metadata.AcTotal = $acMatches.Count
    $metadata.AcCompleted = ($acMatches | Where-Object { $_.Groups[1].Value -eq 'x' }).Count

    return $metadata
}

# Function to generate flush summary report
function New-FlushSummary {
    param([array]$ArchivedTasks)

    $timestamp = Get-Date -Format "yyyy-MM-dd-HHmmss"
    $summaryFile = Join-Path $ArchiveDir "flush-$timestamp.md"

    $triggerSource = if ($env:TRIGGER_SOURCE) { $env:TRIGGER_SOURCE } else { "manual" }
    $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

    # Start building summary content
    $summary = @"
# Backlog Flush Summary

**Date**: $dateStr UTC
**Archived Tasks**: $($ArchivedTasks.Count)
**Triggered By**: $triggerSource

## Tasks Archived

"@

    # Track statistics
    $priorityCounts = @{}
    $labelCounts = @{}

    foreach ($task in $ArchivedTasks) {
        $metadata = Get-TaskMetadata -TaskId $task.Id

        # Update priority counts
        $priority = $metadata.Priority
        if (-not $priorityCounts.ContainsKey($priority)) {
            $priorityCounts[$priority] = 0
        }
        $priorityCounts[$priority]++

        # Update label counts
        foreach ($label in $metadata.Labels) {
            if (-not $labelCounts.ContainsKey($label)) {
                $labelCounts[$label] = 0
            }
            $labelCounts[$label]++
        }

        # Format task entry
        $labelsStr = if ($metadata.Labels.Count -gt 0) {
            $metadata.Labels -join ", "
        } else {
            "None"
        }
        $acStr = "$($metadata.AcCompleted)/$($metadata.AcTotal) completed"

        # Construct relative link to archived task file
        $taskFileName = Get-ChildItem -Path $ArchiveTasksDir -Filter "$($task.Id) - *.md" -ErrorAction SilentlyContinue |
                        Select-Object -First 1 -ExpandProperty Name

        if ($taskFileName) {
            # URL encode the filename for markdown links
            $encodedFileName = [System.Uri]::EscapeDataString($taskFileName)
            $relativeLink = "tasks/$encodedFileName"
        } else {
            $relativeLink = "#"
        }

        $summary += @"

### [$($task.Id) - $($metadata.Title)]($relativeLink)
- **Status**: $($metadata.Status)
- **Priority**: $($metadata.Priority)
- **Assignee**: $($metadata.Assignee)
- **Labels**: $labelsStr
- **Acceptance Criteria**: $acStr

---
"@
    }

    # Add statistics section
    $summary += @"

## Statistics

- **Total archived**: $($ArchivedTasks.Count)
"@

    # Add priority breakdown
    if ($priorityCounts.Count -gt 0) {
        $priorityStr = ($priorityCounts.GetEnumerator() |
                       Sort-Object Value -Descending |
                       ForEach-Object { "$($_.Key) ($($_.Value))" }) -join ", "
        $summary += "`n- **By priority**: $priorityStr"
    }

    # Add common labels
    if ($labelCounts.Count -gt 0) {
        $labelStr = ($labelCounts.GetEnumerator() |
                    Sort-Object Value -Descending |
                    Select-Object -First 5 |
                    ForEach-Object { "$($_.Key) ($($_.Value))" }) -join ", "
        $summary += "`n- **Common labels**: $labelStr"
    }

    $summary += "`n"

    # Write summary file
    $summary | Out-File -FilePath $summaryFile -Encoding UTF8 -NoNewline

    return $summaryFile
}

# Main execution
function Invoke-Main {
    Test-Prerequisites

    $doneTasks = Get-DoneTasks

    if ($doneTasks.Count -eq 0) {
        Write-Output "No Done tasks to archive"
        exit 2
    }

    Write-Output "Found $($doneTasks.Count) Done task(s) to archive"

    # Dry run mode
    if ($DryRun) {
        Write-Output "`nDry run - would archive:"
        foreach ($task in $doneTasks) {
            Write-Output "  $($task.Id) - $($task.Title)"
        }
        exit 0
    }

    # Archive tasks
    $archived = @()
    $failed = @()

    foreach ($task in $doneTasks) {
        Write-Output "Archiving $($task.Id)..."

        $result = backlog task archive $task.Id 2>&1
        if ($LASTEXITCODE -eq 0) {
            $archived += $task
            Write-Verbose "Successfully archived $($task.Id)"
        }
        else {
            Write-Warning "Failed to archive $($task.Id): $result"
            $failed += $task
        }
    }

    Write-Output "`nArchived $($archived.Count) task(s)"

    # Generate summary report
    if (-not $NoSummary -and $archived.Count -gt 0) {
        Write-Verbose "Generating flush summary..."
        $summaryFile = New-FlushSummary -ArchivedTasks $archived
        Write-Output "Summary: $summaryFile"
    }

    # Auto-commit changes
    if ($AutoCommit -and $archived.Count -gt 0) {
        Write-Output "`nCommitting changes..."
        git add "$ArchiveDir/"
        git commit -m "chore: flush backlog - archived $($archived.Count) tasks"

        if ($LASTEXITCODE -eq 0) {
            Write-Output "Changes committed successfully"
        } else {
            Write-Warning "Failed to commit changes"
        }
    }

    # Exit with appropriate code
    if ($failed.Count -gt 0) {
        Write-Warning "$($failed.Count) task(s) failed to archive"
        exit 3
    }

    exit 0
}

# Execute main function
Invoke-Main
