#!/usr/bin/env bash
set -euo pipefail

# create-github-release.sh
# Create a GitHub release with all template zip files
# Usage: create-github-release.sh <version>

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi

VERSION="$1"

# Remove 'v' prefix from version for release title
VERSION_NO_V=${VERSION#v}

gh release create "$VERSION" \
  .genreleases/flowspec-template-copilot-sh-"$VERSION".zip \
  .genreleases/flowspec-template-copilot-ps-"$VERSION".zip \
  .genreleases/flowspec-template-claude-sh-"$VERSION".zip \
  .genreleases/flowspec-template-claude-ps-"$VERSION".zip \
  .genreleases/flowspec-template-gemini-sh-"$VERSION".zip \
  .genreleases/flowspec-template-gemini-ps-"$VERSION".zip \
  .genreleases/flowspec-template-cursor-agent-sh-"$VERSION".zip \
  .genreleases/flowspec-template-cursor-agent-ps-"$VERSION".zip \
  .genreleases/flowspec-template-opencode-sh-"$VERSION".zip \
  .genreleases/flowspec-template-opencode-ps-"$VERSION".zip \
  .genreleases/flowspec-template-qwen-sh-"$VERSION".zip \
  .genreleases/flowspec-template-qwen-ps-"$VERSION".zip \
  .genreleases/flowspec-template-windsurf-sh-"$VERSION".zip \
  .genreleases/flowspec-template-windsurf-ps-"$VERSION".zip \
  .genreleases/flowspec-template-codex-sh-"$VERSION".zip \
  .genreleases/flowspec-template-codex-ps-"$VERSION".zip \
  .genreleases/flowspec-template-kilocode-sh-"$VERSION".zip \
  .genreleases/flowspec-template-kilocode-ps-"$VERSION".zip \
  .genreleases/flowspec-template-auggie-sh-"$VERSION".zip \
  .genreleases/flowspec-template-auggie-ps-"$VERSION".zip \
  .genreleases/flowspec-template-roo-sh-"$VERSION".zip \
  .genreleases/flowspec-template-roo-ps-"$VERSION".zip \
  .genreleases/flowspec-template-codebuddy-sh-"$VERSION".zip \
  .genreleases/flowspec-template-codebuddy-ps-"$VERSION".zip \
  .genreleases/flowspec-template-q-sh-"$VERSION".zip \
  .genreleases/flowspec-template-q-ps-"$VERSION".zip \
  --title "flowspec - $VERSION_NO_V" \
  --notes-file release_notes.md
