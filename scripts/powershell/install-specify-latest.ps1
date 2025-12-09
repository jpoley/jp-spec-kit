#!/usr/bin/env pwsh
param(
  [ValidateSet('ssh','https')][string]$Method = 'https',
  [string]$Owner = 'jpoley',
  [string]$Repo = 'jp-spec-kit'
)

$ErrorActionPreference = 'Stop'

function Require-Cmd($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    throw "$name not found"
  }
}

Require-Cmd git
Require-Cmd uv

$RepoSsh   = "git@github.com:$Owner/$Repo.git"
$RepoHttps = "https://github.com/$Owner/$Repo.git"

function Resolve-TagViaGh() {
  if (Get-Command gh -ErrorAction SilentlyContinue) {
    try {
      gh auth status -h github.com | Out-Null
      $out = gh release view -R "$Owner/$Repo" --json tagName --jq .tagName 2>$null
      if ($LASTEXITCODE -eq 0 -and $out) { return $out }
    } catch { }
  }
  return $null
}

function Resolve-TagViaApi() {
  $token = $env:GITHUB_TOKEN
  if (-not $token) { return $null }
  $headers = @{ 'Authorization' = "Bearer $token"; 'Accept' = 'application/vnd.github+json' }
  try {
    $resp = Invoke-RestMethod -Method GET -Uri "https://api.github.com/repos/$Owner/$Repo/releases/latest" -Headers $headers -ErrorAction Stop
    return $resp.tag_name
  } catch { return $null }
}

function Resolve-TagViaLsRemoteSsh() {
  try {
    $out = git ls-remote --tags $RepoSsh 2>$null
    if (-not $out) { return $null }
    $tags = $out | ForEach-Object {
      if ($_ -match 'refs/tags/(.+)$') {
        $m = $Matches[1] -replace '\^\{\}$',''
        $m
      }
    }
    return ($tags | Sort-Object {[Version]($_ -replace '^v','0.')} | Select-Object -Last 1)
  } catch { return $null }
}

function Resolve-TagViaLsRemoteHttps() {
  $token = $env:GITHUB_TOKEN
  if (-not $token) { return $null }
  $authed = "https://x-access-token:$token@github.com/$Owner/$Repo.git"
  try {
    $out = git ls-remote --tags $authed 2>$null
    if (-not $out) { return $null }
    $tags = $out | ForEach-Object {
      if ($_ -match 'refs/tags/(.+)$') {
        $m = $Matches[1] -replace '\^\{\}$',''
        $m
      }
    }
    return ($tags | Sort-Object {[Version]($_ -replace '^v','0.')} | Select-Object -Last 1)
  } catch { return $null }
}

$tag = Resolve-TagViaGh
if (-not $tag) { $tag = Resolve-TagViaApi }
if (-not $tag -and $Method -eq 'ssh') { $tag = Resolve-TagViaLsRemoteSsh }
if (-not $tag -and $Method -eq 'https') { $tag = Resolve-TagViaLsRemoteHttps }

if (-not $tag) {
  Write-Error "Failed to resolve latest tag for $Owner/$Repo. Configure SSH or set GITHUB_TOKEN (repo scope), or run 'gh auth login'."
  exit 1
}

Write-Host "Installing specflow-cli @ $tag from $Owner/$Repo via $Method"

if ($Method -eq 'ssh') {
  $from = "git+ssh://git@github.com/$Owner/$Repo.git@$tag"
  uv tool install specflow-cli --from $from
} else {
  if (-not $env:GITHUB_TOKEN) {
    Write-Error "GITHUB_TOKEN not set for private HTTPS access. Export it and retry, or use -Method ssh."
    exit 1
  }
  $from = "git+https://x-access-token:$($env:GITHUB_TOKEN)@github.com/$Owner/$Repo.git@$tag"
  uv tool install specflow-cli --from $from
}

Write-Host "Done. Run: specflow --help"
