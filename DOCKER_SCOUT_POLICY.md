# Docker Scout Policy Configuration

## Issue: Unapproved Base Images

Docker Scout reports "Unapproved Base Images" policy failure because we haven't configured which base images are approved.

## For Individual Docker Hub Accounts

Individual accounts (Personal/Pro) have limited Docker Scout features compared to Team/Business plans.

### Option 1: Docker Scout Dashboard (if available on your plan)

1. Go to **https://scout.docker.com/**
2. Sign in with your Docker Hub account
3. Click **Policies** in the header menu
4. Look for "Approved Base Images" or "Base images" policy
5. Configure approved patterns:
   ```
   docker.io/library/python:*
   docker.io/library/node:*
   docker.io/library/alpine:*
   ```

### Option 2: Accept the Policy Warning

For individual accounts without full policy configuration access, this policy warning can be safely ignored because:

- We use `python:3.13-alpine` which is an **official Docker Hub image**
- Official images have SLSA provenance and SBOM attestations
- The "Unapproved Base Images" is a policy preference, NOT a security vulnerability

### Option 3: Upgrade to Team/Business Plan

Full Docker Scout policy configuration is available on Team and Business plans with unlimited repositories.

## For Organization Accounts (Team/Business)

1. **Log in to Docker Hub**: https://hub.docker.com
2. **Navigate to Organization Settings**:
   - Click on your organization
   - Go to Settings → Docker Scout → Policies
3. **Configure Approved Base Images**:
   - Select "Approved Base Images" policy
   - Add the approved patterns listed above
4. **Save the policy**

## Base Image Details

Our current base image:
- **Image**: `python:3.13-alpine`
- **Digest**: `sha256:51b5354ed44df6e1a3b3faf6d3a3d40da129621046b6d5a707b7c1f44d258ed6`
- **Source**: Official Python image from Docker Hub

## Why This is Our Responsibility

This is **not a vulnerability** - it's a policy configuration issue.

We use `python:3.13-alpine` which is an official Docker Hub image with:
- SLSA provenance attestations
- SBOM (Software Bill of Materials)
- Regular security updates from Python maintainers

The policy failure simply means we haven't told Docker Scout that official Python images are approved for our organization.

## Verification After Configuration

After configuring the policy, run:
```bash
docker scout policy jpoley/flowspec-agents:latest
```

Expected result: "Approved Base Images" policy should now pass.

## Related Files

- `vulnerability-tracking.jsonl`: Entry POLICY-001
- `.devcontainer/Dockerfile`: Contains base image labels at lines 145-146
