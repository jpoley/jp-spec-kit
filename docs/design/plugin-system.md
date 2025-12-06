# Plugin System Design Document

**Version**: 1.0
**Date**: 2025-12-06
**Author**: Architecture Team
**Status**: Draft

---

## Executive Summary

This document describes a plugin architecture for JP Spec Kit that enables pluggable **workflows**, **commands**, **agents/squads**, **stacks**, and **integrations** while preserving the spec-driven foundation and backlog.md workflow. The system builds on the existing layered extension model (`.specify-plugin.yml`) to create a full plugin ecosystem.

---

## 1. Goals and Non-Goals

### Goals

1. **Extensibility Without Forking**: Enable users to add custom workflows, commands, agents, stacks, and integrations without modifying core JP Spec Kit code.

2. **Spec-Driven Foundation**: Preserve the PRD → Plan → Implement → Validate workflow as the backbone; plugins extend but don't replace this flow.

3. **Backlog.md Integration**: Plugins can register tasks, emit events, and interact with the backlog system seamlessly.

4. **Enterprise Ready**: Support private registries, signing, policy enforcement, and audit trails for enterprise adoption.

5. **Python-First SDK**: Provide a Python SDK that makes plugin development straightforward with clear extension points.

6. **Safe and Secure**: Enforce trust boundaries with signing, sandboxing options, and declarative capability requests.

7. **Discoverable Ecosystem**: Enable marketplace-style discovery of public plugins and internal enterprise registries.

### Non-Goals

1. **Full Workflow Engine/BPM**: This is not Apache Airflow or Temporal. Plugins augment the Spec-Driven Development (SDD) workflow, not replace it with arbitrary DAGs.

2. **Multi-Language Plugin Runtime**: v1 focuses on Python plugins only. Other languages may be considered in future versions.

3. **Plugin Isolation via Containers**: v1 uses process-level sandboxing, not full container isolation.

4. **Automatic Plugin Migration**: Breaking changes require manual migration; no automatic code transformation.

5. **GUI Plugin Builder**: Plugins are code-first, defined via YAML manifests and Python modules.

---

## 2. Core Use Cases and Plugin Taxonomy

### 2.1 Plugin Types

| Type | Description | Examples |
|------|-------------|----------|
| **Workflows** | Custom workflow phases or alternative flows | `ml-training-workflow`, `data-pipeline-flow` |
| **Commands** | New slash commands for Claude Code or CLI | `jpspec:security-scan`, `jpspec:perf-test` |
| **Agents/Squads** | Custom AI agent personas or multi-agent squads | `security-auditor`, `ml-engineer-squad` |
| **Stacks** | Technology stack templates and configurations | `fastapi-stack`, `serverless-aws-stack` |
| **Integrations** | External tool connectors (CI/CD, notifications, etc.) | `jira-sync`, `slack-notifier`, `github-actions` |

### 2.2 Core Use Cases

**UC-1: Add Custom Security Scanning Workflow**
```
As a security engineer,
I want to install a security-scan plugin that adds a /jpspec:security-scan command,
So that security analysis is part of my spec-driven workflow.
```

**UC-2: Use Alternative Stack Template**
```
As a backend developer,
I want to install a FastAPI stack plugin,
So that my projects are scaffolded with FastAPI, SQLAlchemy, and Alembic.
```

**UC-3: Integrate with Jira for Task Sync**
```
As a project manager,
I want to install a Jira integration plugin,
So that backlog.md tasks sync bidirectionally with Jira issues.
```

**UC-4: Add ML-Specific Agent Personas**
```
As an ML engineer,
I want to install an ML-squad plugin that provides ml-engineer and data-scientist personas,
So that /jpspec:implement has ML-specific expertise.
```

**UC-5: Enterprise Private Registry**
```
As an enterprise admin,
I want to configure a private plugin registry,
So that my team uses only approved, signed plugins.
```

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JP Spec Kit Core                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Workflow Engine │  │  Backlog.md     │  │  CLI / Claude   │             │
│  │ (SDD Phases)    │  │  Integration    │  │  Commands       │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│           └────────────────────┼────────────────────┘                       │
│                                │                                            │
│                    ┌───────────▼───────────┐                                │
│                    │   Extension Points    │                                │
│                    │  (EP Registry)        │                                │
│                    └───────────┬───────────┘                                │
│                                │                                            │
│                    ┌───────────▼───────────┐                                │
│                    │     Event Bus         │                                │
│                    │  (Pub/Sub Events)     │                                │
│                    └───────────┬───────────┘                                │
└────────────────────────────────┼────────────────────────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Plugin Host         │
                    │  ┌──────────────────┐   │
                    │  │ Plugin Loader    │   │
                    │  │ Security Manager │   │
                    │  │ Lifecycle Mgr    │   │
                    │  └──────────────────┘   │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌────────▼────────┐  ┌───────────▼───────────┐  ┌───────▼────────┐
│   Plugin A      │  │   Plugin B            │  │   Plugin C     │
│   (Workflow)    │  │   (Stack + Commands)  │  │   (Integration)│
│   plugin.yaml   │  │   plugin.yaml         │  │   plugin.yaml  │
│   src/          │  │   src/                │  │   src/         │
└─────────────────┘  └───────────────────────┘  └────────────────┘
```

### 3.2 Core Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **Core** | SDD workflow execution, backlog management, CLI commands |
| **Extension Points (EPs)** | Well-defined hooks where plugins can inject behavior |
| **Event Bus** | Pub/sub mechanism for workflow events and plugin coordination |
| **Plugin Host** | Loading, validation, lifecycle management, security enforcement |
| **Plugin** | Self-contained package with manifest, code, and assets |

### 3.3 Extension Points (EPs)

Extension Points are named locations in the core system where plugins register handlers.

| EP Name | Type | Description |
|---------|------|-------------|
| `workflow.phase.before` | Hook | Called before each workflow phase |
| `workflow.phase.after` | Hook | Called after each workflow phase |
| `workflow.phase.replace` | Override | Replace a workflow phase entirely |
| `command.register` | Registration | Register new CLI/slash commands |
| `agent.persona` | Registration | Register new agent personas |
| `stack.template` | Registration | Register stack templates |
| `backlog.task.created` | Event | Triggered when task created |
| `backlog.task.updated` | Event | Triggered when task updated |
| `integration.sync` | Hook | Called during sync operations |

### 3.4 Event Bus

The event bus enables loose coupling between core and plugins:

```python
# Core emits events
event_bus.emit("workflow.implement.completed", {
    "feature": "user-auth",
    "task_id": "task-189",
    "artifacts": ["src/auth/"]
})

# Plugins subscribe
@event_bus.subscribe("workflow.implement.completed")
def on_implement_complete(event: Event):
    trigger_security_scan(event.artifacts)
```

**Event Categories**:
- `workflow.*`: Workflow phase events
- `backlog.*`: Task lifecycle events
- `plugin.*`: Plugin lifecycle events
- `system.*`: System-level events (init, shutdown)

---

## 4. Plugin Manifest Schema

Each plugin is defined by a `plugin.yaml` manifest:

```yaml
# plugin.yaml - Example Plugin Manifest
apiVersion: speckit.dev/v1
kind: Plugin
metadata:
  name: security-scanner
  version: 1.2.0
  author: security-team
  license: MIT
  repository: https://github.com/example/security-scanner-plugin
  description: Adds security scanning to the jpspec workflow
  keywords:
    - security
    - scanning
    - sast
    - dast

# What this plugin provides
provides:
  commands:
    - name: jpspec:security-scan
      description: Run security analysis on implementation
      entrypoint: src/commands/security_scan.py:run
      
  agents:
    - name: security-auditor
      description: Expert in application security review
      persona_file: agents/security-auditor.md
      
  workflows:
    - name: secure-implement
      description: Implementation with mandatory security gates
      phase: implement
      mode: wrap  # before | after | replace | wrap
      entrypoint: src/workflows/secure_implement.py:handler

  integrations:
    - name: snyk-connector
      description: Sync with Snyk vulnerability database
      entrypoint: src/integrations/snyk.py:connector

  hooks:
    - event: workflow.implement.completed
      handler: src/hooks/post_implement.py:on_complete

# What this plugin requires
requires:
  speckit: ">=0.0.20"
  python: ">=3.11"
  plugins:
    - name: base-security
      version: ">=1.0.0"
      optional: false
  capabilities:
    - network  # Requires network access
    - filesystem.read  # Read access to project files

# Compatibility declarations
compatibility:
  speckit:
    min: "0.0.18"
    max: "0.1.0"
    tested: ["0.0.20", "0.0.21"]
  platforms:
    - linux
    - macos
    - windows

# Security and signing
signatures:
  manifest: sha256:abc123...
  package: sha256:def456...
  signer: security-team@example.com
  timestamp: 2025-12-06T00:00:00Z

# Configuration schema (optional)
config:
  schema:
    type: object
    properties:
      severity_threshold:
        type: string
        enum: [low, medium, high, critical]
      scan_dependencies:
        type: boolean
  defaults:
    severity_threshold: medium
    scan_dependencies: true
```

### Manifest Sections Explained

| Section | Purpose |
|---------|---------|
| `metadata` | Identity, versioning, discoverability |
| `provides` | What the plugin adds (commands, agents, workflows, etc.) |
| `requires` | Dependencies on core version, Python, other plugins, capabilities |
| `compatibility` | Platform and version compatibility matrix |
| `signatures` | Cryptographic signatures for trust verification |
| `config` | User-configurable options with JSON Schema validation |

---

## 5. Lifecycle Flows

### 5.1 Plugin Lifecycle States

```
    ┌──────────┐
    │ Available│  (In registry, not installed)
    └────┬─────┘
         │ specify plugin install
         ▼
    ┌──────────┐
    │ Installed│  (Downloaded, verified, not enabled)
    └────┬─────┘
         │ specify plugin enable
         ▼
    ┌──────────┐
    │  Enabled │  (Active, loaded on startup)
    └────┬─────┘
         │ specify plugin disable
         ▼
    ┌──────────┐
    │ Disabled │  (Installed but not active)
    └────┬─────┘
         │ specify plugin remove
         ▼
    ┌──────────┐
    │ Removed  │  (Uninstalled, back to Available)
    └──────────┘
```

### 5.2 Install Flow

```bash
# Search for plugins
$ specify plugin search security
NAME              VERSION  AUTHOR          DESCRIPTION
security-scanner  1.2.0    security-team   Security scanning for jpspec
sast-analyzer     2.0.1    acme-tools      Static analysis integration

# Install a plugin
$ specify plugin install security-scanner

[1/5] Resolving dependencies...
      ✓ speckit >=0.0.20 (installed: 0.0.21)
      ✓ python >=3.11 (installed: 3.12.0)
      ✓ base-security >=1.0.0 (installing...)
      
[2/5] Downloading security-scanner@1.2.0...
      Source: https://plugins.speckit.dev/security-scanner-1.2.0.tar.gz
      Size: 245 KB
      
[3/5] Verifying signatures...
      ✓ Manifest signature valid (signed by: security-team@example.com)
      ✓ Package signature valid
      ✓ Timestamp: 2025-12-06T00:00:00Z
      
[4/5] Checking capabilities...
      ⚠ Plugin requests: network, filesystem.read
      Accept capabilities? [y/N]: y
      
[5/5] Installing to .specify/plugins/security-scanner/
      ✓ Extracted plugin files
      ✓ Registered extension points
      ✓ Plugin installed successfully

Run 'specify plugin enable security-scanner' to activate.
```

### 5.3 Enable/Load Flow

```bash
$ specify plugin enable security-scanner

[1/3] Loading plugin configuration...
      ✓ Config validated against schema
      
[2/3] Registering extensions...
      ✓ Command: jpspec:security-scan
      ✓ Agent: security-auditor
      ✓ Workflow: secure-implement (wraps: implement)
      ✓ Hook: workflow.implement.completed
      
[3/3] Plugin enabled
      security-scanner is now active.
```

### 5.4 Execute Flow

When a plugin command or hook is invoked:

```python
# 1. Plugin Host receives invocation
plugin_host.invoke("security-scanner", "commands.security_scan", args)

# 2. Security Manager validates capabilities
security_manager.check_capabilities(plugin, requested=["network"])

# 3. Load plugin module (lazy)
module = plugin_loader.load_module("security-scanner", "src/commands/security_scan.py")

# 4. Execute with context
context = PluginContext(
    project_root=Path.cwd(),
    config=plugin_config,
    event_bus=event_bus,
    backlog=backlog_client
)
result = module.run(context, args)

# 5. Audit log
audit_logger.log_invocation(plugin="security-scanner", command="security_scan", result=result)
```

### 5.5 Update Flow

```bash
$ specify plugin update security-scanner

[1/4] Checking for updates...
      Current: 1.2.0
      Latest:  1.3.0
      
[2/4] Reviewing changes...
      - Added: CodeQL integration
      - Fixed: False positive in SQL injection detection
      - Breaking: Config schema changed (migration available)
      
[3/4] Running migration...
      ✓ Config migrated: severity_threshold → severity.threshold
      
[4/4] Installing update...
      ✓ Updated security-scanner to 1.3.0

Plugin will reload on next command.
```

### 5.6 Remove Flow

```bash
$ specify plugin remove security-scanner

[1/3] Checking dependencies...
      ⚠ advanced-security depends on security-scanner
      Remove anyway? [y/N]: y
      
[2/3] Unregistering extensions...
      ✓ Removed command: jpspec:security-scan
      ✓ Removed agent: security-auditor
      ✓ Removed workflow: secure-implement
      ✓ Removed hooks
      
[3/3] Removing files...
      ✓ Deleted .specify/plugins/security-scanner/
      ✓ Plugin removed successfully
```

---

## 6. Backlog.md Integration Rules

Plugins MUST follow these rules when interacting with backlog.md:

### 6.1 Task Creation Rules

```yaml
# Plugins can create tasks with plugin-specific labels
backlog_rules:
  task_creation:
    allowed: true
    required_labels:
      - "plugin:{plugin_name}"  # Auto-added
    allowed_statuses:
      - "To Do"
      - "Backlog"
    title_prefix: "[{plugin_name}]"  # Optional, configurable
```

**Example**:
```python
# Plugin creating a task
backlog.create_task(
    title="Security vulnerability detected in auth module",
    labels=["security", "high-priority"],  # "plugin:security-scanner" auto-added
    status="To Do",
    metadata={"scan_id": "scan-123", "severity": "high"}
)
```

### 6.2 Task Update Rules

```yaml
backlog_rules:
  task_updates:
    own_tasks_only: true  # Plugins can only update tasks they created
    allowed_fields:
      - status
      - labels
      - metadata
    forbidden_fields:
      - assignee  # Requires user permission
```

### 6.3 Event Emission Rules

Plugins MUST emit events when modifying backlog state:

```python
# Correct: Emit event when plugin creates task
task = backlog.create_task(...)
event_bus.emit("plugin.backlog.task.created", {
    "plugin": "security-scanner",
    "task_id": task.id,
    "reason": "Security scan detected vulnerability"
})
```

### 6.4 Validation Requirements

Before a plugin can interact with backlog:

1. **Capability Declared**: `backlog.read` or `backlog.write` in `requires.capabilities`
2. **Schema Compliance**: Task metadata must conform to backlog schema
3. **Audit Trail**: All backlog modifications logged with plugin attribution

---

## 7. SDK Surface (Python-First)

### 7.1 SDK Module Structure

```
speckit_sdk/
├── __init__.py              # Main exports
├── plugin.py                # Plugin base class
├── workflows/
│   ├── __init__.py
│   ├── phase.py             # Workflow phase hooks
│   └── context.py           # Workflow execution context
├── commands/
│   ├── __init__.py
│   ├── base.py              # Command base class
│   └── decorators.py        # @command, @argument, etc.
├── agents/
│   ├── __init__.py
│   ├── persona.py           # Agent persona registration
│   └── squad.py             # Multi-agent squad definition
├── stacks/
│   ├── __init__.py
│   ├── template.py          # Stack template base
│   └── scaffolder.py        # Project scaffolding utilities
├── events/
│   ├── __init__.py
│   ├── bus.py               # Event bus client
│   └── types.py             # Event type definitions
├── context/
│   ├── __init__.py
│   ├── plugin_context.py    # Runtime context
│   └── config.py            # Configuration access
└── security/
    ├── __init__.py
    ├── capabilities.py      # Capability declarations
    └── sandbox.py           # Sandbox utilities
```

### 7.2 SDK Examples

**Creating a Command Plugin**:

```python
# src/commands/security_scan.py
from speckit_sdk.commands import Command, argument, option
from speckit_sdk.context import PluginContext

class SecurityScanCommand(Command):
    """Run security analysis on the current feature."""
    
    name = "jpspec:security-scan"
    description = "Perform SAST/DAST security scanning"
    
    @argument("feature", help="Feature to scan")
    @option("--severity", default="medium", help="Minimum severity to report")
    def run(self, ctx: PluginContext, feature: str, severity: str):
        # Access plugin configuration
        config = ctx.config
        
        # Read project files (requires filesystem.read capability)
        source_files = ctx.project.glob("src/**/*.py")
        
        # Perform scan
        findings = self.scan(source_files, severity)
        
        # Create backlog tasks for findings (requires backlog.write capability)
        for finding in findings:
            ctx.backlog.create_task(
                title=f"[Security] {finding.title}",
                labels=["security", finding.severity],
                metadata={"finding_id": finding.id}
            )
        
        # Emit event
        ctx.events.emit("plugin.security.scan.completed", {
            "feature": feature,
            "findings_count": len(findings)
        })
        
        return {"findings": findings}
```

**Creating a Workflow Extension**:

```python
# src/workflows/secure_implement.py
from speckit_sdk.workflows import WorkflowPhase, phase_hook
from speckit_sdk.context import PluginContext

class SecureImplementPhase(WorkflowPhase):
    """Wrap implementation phase with security gates."""
    
    phase = "implement"
    mode = "wrap"  # Run before and after core phase
    
    @phase_hook("before")
    def pre_implement(self, ctx: PluginContext):
        """Pre-implementation security checklist."""
        ctx.console.print("🔒 Running pre-implementation security checks...")
        
        # Verify no known vulnerable dependencies
        vulnerabilities = self.check_dependencies(ctx)
        if vulnerabilities:
            ctx.console.print_warning(f"Found {len(vulnerabilities)} vulnerable dependencies")
            if ctx.config.get("block_on_vulnerabilities", True):
                raise SecurityGateError("Fix vulnerabilities before implementing")
    
    @phase_hook("after")
    def post_implement(self, ctx: PluginContext):
        """Post-implementation security scan."""
        ctx.console.print("🔍 Running post-implementation security scan...")
        
        # Scan new/modified files
        changed_files = ctx.workflow.get_changed_files()
        findings = self.scan_files(changed_files)
        
        # Report findings
        for finding in findings:
            ctx.console.print_finding(finding)
        
        # Emit event
        ctx.events.emit("plugin.security.post_implement", {
            "findings": [f.to_dict() for f in findings]
        })
```

**Creating an Agent Persona**:

```python
# src/agents/security_auditor.py
from speckit_sdk.agents import AgentPersona

class SecurityAuditorPersona(AgentPersona):
    """Security-focused code reviewer."""
    
    name = "security-auditor"
    description = "Expert in application security and vulnerability analysis"
    
    # Persona definition (can also be loaded from .md file)
    persona = """
    You are a senior application security engineer with expertise in:
    - OWASP Top 10 vulnerabilities
    - Secure coding practices
    - Threat modeling
    - Penetration testing
    
    When reviewing code, you:
    1. Identify potential security vulnerabilities
    2. Suggest secure alternatives
    3. Reference relevant security standards (CWE, CVE)
    4. Prioritize findings by severity
    
    You communicate findings clearly with:
    - Severity rating (Critical/High/Medium/Low)
    - Description of the vulnerability
    - Recommended fix
    - References to security standards
    """
    
    # Agent capabilities
    capabilities = [
        "code_review",
        "threat_analysis",
        "security_recommendations"
    ]
```

**Creating a Stack Template**:

```python
# src/stacks/fastapi_stack.py
from speckit_sdk.stacks import StackTemplate, file_template
from speckit_sdk.context import PluginContext

class FastAPIStack(StackTemplate):
    """FastAPI + SQLAlchemy + Alembic stack."""
    
    name = "fastapi-stack"
    description = "Production-ready FastAPI backend"
    
    # Dependencies to install
    dependencies = [
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "pydantic>=2.5.0",
    ]
    
    dev_dependencies = [
        "pytest>=8.0.0",
        "pytest-asyncio>=0.23.0",
        "httpx>=0.26.0",
    ]
    
    @file_template("src/main.py")
    def main_py(self, ctx: PluginContext) -> str:
        return '''
from fastapi import FastAPI
from {project_name}.api import router
from {project_name}.database import engine

app = FastAPI(title="{project_title}")
app.include_router(router)

@app.on_event("startup")
async def startup():
    # Initialize database
    pass
'''.format(
            project_name=ctx.project.name,
            project_title=ctx.project.title
        )
    
    def scaffold(self, ctx: PluginContext):
        """Generate project structure."""
        ctx.files.create_directory("src")
        ctx.files.create_directory("tests")
        ctx.files.create_directory("alembic")
        
        # Generate files from templates
        self.generate_templates(ctx)
        
        # Initialize alembic
        ctx.shell.run("alembic init alembic")
```

---

## 8. Security and Trust Model

### 8.1 Trust Levels

| Level | Description | Requirements |
|-------|-------------|--------------|
| **Unsigned** | No verification | Warning on install, blocked by policy |
| **Self-Signed** | Author signature | Manual trust approval |
| **Verified** | Registry-verified author | Author identity confirmed |
| **Certified** | JP Spec Kit certified | Security audit passed |

### 8.2 Signing and Verification

```yaml
# Plugin signing workflow
# 1. Author generates key pair
$ specify plugin keygen
Generated keypair:
  Public:  ~/.specify/keys/public.pem
  Private: ~/.specify/keys/private.pem

# 2. Sign plugin package
$ specify plugin sign ./my-plugin/
Signing with: ~/.specify/keys/private.pem
Package signed: my-plugin-1.0.0.tar.gz.sig

# 3. Upload to registry (includes signature)
$ specify plugin publish
Uploading my-plugin@1.0.0...
✓ Package uploaded
✓ Signature verified
✓ Published to registry
```

### 8.3 Capability System

Plugins must declare required capabilities:

```yaml
requires:
  capabilities:
    - network              # Make HTTP requests
    - filesystem.read      # Read project files
    - filesystem.write     # Write to project directory
    - subprocess           # Execute external commands
    - backlog.read         # Read backlog tasks
    - backlog.write        # Create/update backlog tasks
    - environment          # Access environment variables
```

**Capability Enforcement**:

```python
# Plugin Host enforces capabilities at runtime
class CapabilityManager:
    def check(self, plugin: Plugin, capability: str) -> bool:
        if capability not in plugin.manifest.requires.capabilities:
            raise CapabilityDeniedError(
                f"Plugin '{plugin.name}' does not have '{capability}' capability. "
                f"Add to plugin.yaml requires.capabilities to request."
            )
        return True
```

### 8.4 Policy Enforcement

Enterprise admins can set policies:

```yaml
# .specify/policy.yaml
plugin_policy:
  # Trust requirements
  trust:
    minimum_level: verified  # unsigned | self-signed | verified | certified
    allowed_signers:
      - security-team@company.com
      - approved-vendor@example.com
    
  # Capability restrictions
  capabilities:
    blocked:
      - subprocess  # No shell access
    require_approval:
      - network     # Require admin approval
    
  # Registry restrictions
  registries:
    allowed:
      - https://plugins.speckit.dev
      - https://internal.company.com/plugins
    blocked:
      - "*"  # Block all others
    
  # Specific plugin rules
  plugins:
    allowed:
      - security-scanner
      - jira-sync
    blocked:
      - experimental-*
```

### 8.5 Sandboxing Options

**Process-Level Sandbox (v1)**:
- Plugins run in subprocess with limited environment
- Timeout enforcement
- Working directory restrictions

**Enhanced Sandbox (v2+)**:
- seccomp filtering (Linux)
- App Sandbox/sandbox-exec (macOS)
- Job Objects/AppContainers (Windows)
- File system namespaces
- Network restrictions

*Note: Platform-specific sandboxing uses native OS mechanisms where available, with graceful fallback to process-level restrictions on unsupported platforms.*

```python
# Sandbox configuration
sandbox_config = {
    "timeout": 300,  # 5 minute max execution
    "working_dir": project_root,
    "env_passthrough": ["HOME", "PATH", "LANG"],
    "network": {
        "allowed_hosts": ["api.snyk.io", "plugins.speckit.dev"],
        "blocked_ports": [22, 3306, 5432]  # No SSH, DB direct access
    },
    "filesystem": {
        "read": [project_root, "/usr/lib"],
        "write": [project_root / ".specify"],
        "blocked": ["/etc", "/root", "~/.ssh"]
    }
}
```

### 8.6 Telemetry and Privacy

```yaml
# Plugin telemetry configuration
telemetry:
  enabled: true  # User can disable
  
  # What we collect
  collect:
    - plugin_name
    - plugin_version
    - command_invoked
    - success/failure
    - execution_duration
    
  # What we never collect
  never_collect:
    - source_code
    - file_contents
    - credentials
    - user_identity (without consent)
    
  # Where data goes
  endpoint: https://telemetry.speckit.dev
  
  # User controls
  user_consent:
    required: true
    opt_out_command: "specify telemetry disable"
```

---

## 9. Marketplace and Registry Design

### 9.1 Public Registry (plugins.speckit.dev)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Spec Kit Plugin Registry                      │
│                     plugins.speckit.dev                          │
├─────────────────────────────────────────────────────────────────┤
│  Search: [security scanning________________] [Search]            │
│                                                                  │
│  Categories: [All] [Workflows] [Commands] [Stacks] [Integrations]│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 🔒 security-scanner           ⭐ 4.8  ⬇️ 12.5k  ✓ Certified │ │
│  │    Security scanning for jpspec workflow                    │ │
│  │    by security-team • v1.2.0 • Updated 2 days ago          │ │
│  │    Tags: security, sast, dast                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 🚀 fastapi-stack              ⭐ 4.6  ⬇️ 8.2k   ✓ Verified  │ │
│  │    FastAPI + SQLAlchemy + Alembic stack template           │ │
│  │    by backend-guild • v2.1.0 • Updated 1 week ago          │ │
│  │    Tags: fastapi, python, backend                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Load more...]                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Enterprise Registry

```yaml
# Enterprise registry configuration
# .specify/registry.yaml

registries:
  - name: company-internal
    url: https://plugins.company.com
    priority: 1  # Check first
    auth:
      type: oauth
      provider: company-sso
    
  - name: speckit-public
    url: https://plugins.speckit.dev
    priority: 2  # Fallback
    filter:
      trust_level: certified  # Only certified plugins
      categories:
        - security
        - integrations
```

### 9.3 CLI Discovery UX

```bash
# Browse categories
$ specify plugin browse
Categories:
  workflows (12 plugins)
  commands (45 plugins)
  agents (8 plugins)
  stacks (23 plugins)
  integrations (31 plugins)

# Search with filters
$ specify plugin search security --category commands --trust certified
NAME                  VERSION  DOWNLOADS  TRUST
security-scanner      1.2.0    12.5k      certified
code-audit            2.0.1    8.1k       certified
vulnerability-check   1.0.5    3.2k       certified

# View plugin details
$ specify plugin info security-scanner

security-scanner v1.2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Security scanning for jpspec workflow

Author:      security-team
License:     MIT
Repository:  https://github.com/example/security-scanner-plugin
Downloads:   12,547
Trust Level: ✓ Certified
Last Update: 2025-12-04

Provides:
  • Command: jpspec:security-scan
  • Agent: security-auditor
  • Workflow: secure-implement (wraps implement)

Requires:
  • speckit >= 0.0.20
  • python >= 3.11
  • Capabilities: network, filesystem.read

$ specify plugin install security-scanner
```

### 9.4 Registry API

```yaml
# Registry API specification
openapi: 3.0.0
info:
  title: Spec Kit Plugin Registry API
  version: 1.0.0

paths:
  /plugins:
    get:
      summary: Search plugins
      parameters:
        - name: q
          in: query
          schema:
            type: string
        - name: category
          in: query
          schema:
            type: string
            enum: [workflows, commands, agents, stacks, integrations]
        - name: trust
          in: query
          schema:
            type: string
            enum: [unsigned, self-signed, verified, certified]
      responses:
        200:
          description: Plugin list
          
  /plugins/{name}:
    get:
      summary: Get plugin details
      
  /plugins/{name}/versions/{version}:
    get:
      summary: Get specific version
      
  /plugins/{name}/versions/{version}/download:
    get:
      summary: Download plugin package
```

---

## 10. CLI UX and Commands

### 10.1 Command Reference

```bash
# Plugin Management
specify plugin search <query>           # Search registry
specify plugin browse                   # Browse categories
specify plugin info <name>              # View plugin details
specify plugin install <name>[@version] # Install plugin
specify plugin update <name>            # Update plugin
specify plugin remove <name>            # Remove plugin
specify plugin list                     # List installed plugins
specify plugin enable <name>            # Enable plugin
specify plugin disable <name>           # Disable plugin

# Plugin Development
specify plugin init <name>              # Scaffold new plugin
specify plugin validate                 # Validate plugin manifest
specify plugin test                     # Run plugin tests
specify plugin build                    # Build plugin package
specify plugin sign                     # Sign plugin package
specify plugin publish                  # Publish to registry

# Registry Management
specify plugin registry add <url>       # Add registry
specify plugin registry remove <url>    # Remove registry
specify plugin registry list            # List registries

# Security
specify plugin keygen                   # Generate signing keys
specify plugin verify <package>         # Verify plugin signature
specify plugin audit                    # Audit installed plugins
```

### 10.2 Interactive Installation

```bash
$ specify plugin install jira-sync

╭─ Installing jira-sync@2.1.0 ─────────────────────────────────────╮
│                                                                   │
│  📦 Package Information                                           │
│     Name:    jira-sync                                           │
│     Version: 2.1.0                                               │
│     Author:  integration-team                                    │
│     Trust:   ✓ Verified                                          │
│                                                                   │
│  🔐 Capabilities Requested                                        │
│     • network        Connect to Jira API                         │
│     • backlog.read   Read task information                       │
│     • backlog.write  Sync tasks to backlog                       │
│                                                                   │
│  📋 What This Plugin Does                                         │
│     • Syncs Jira issues to backlog.md                           │
│     • Creates Jira issues from backlog tasks                     │
│     • Updates status bidirectionally                             │
│                                                                   │
│  ⚠️  Review the capabilities before proceeding.                   │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯

Accept and install? [y/N]: y

[████████████████████████████████████████] 100%

✓ jira-sync installed successfully

Next steps:
  1. Configure: specify plugin config jira-sync
  2. Enable:    specify plugin enable jira-sync
  3. Use:       /jpspec:jira-sync
```

---

## 11. Versioning and Compatibility

### 11.1 Semantic Versioning

Plugins MUST follow semantic versioning:

- **MAJOR**: Breaking changes (config schema, removed features)
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, no API changes

### 11.2 Compatibility Matrix

```yaml
# In plugin.yaml
compatibility:
  speckit:
    min: "0.0.18"   # Minimum supported core version
    max: "0.1.0"    # Maximum tested core version
    tested:         # Explicitly tested versions
      - "0.0.20"
      - "0.0.21"
      - "0.0.22"
```

### 11.3 Migration and Deprecation

**Deprecation Process**:
1. Mark feature deprecated in minor version
2. Log deprecation warning on use
3. Remove feature in next major version
4. Provide migration guide

**Migration Example**:

```python
# migrations/1.2.0_to_2.0.0.py
from speckit_sdk.migrations import Migration

class Migration_1_2_to_2_0(Migration):
    """Migrate config schema from 1.2.x to 2.0.0."""
    
    from_version = "1.2.0"
    to_version = "2.0.0"
    
    def migrate_config(self, old_config: dict) -> dict:
        """Transform configuration."""
        new_config = old_config.copy()
        
        # Rename: severity_threshold → severity.threshold
        if "severity_threshold" in old_config:
            new_config["severity"] = {
                "threshold": old_config.pop("severity_threshold")
            }
        
        return new_config
    
    def migrate_data(self, plugin_dir: Path):
        """Transform stored data."""
        # Migrate any plugin-specific data files
        pass
```

**CLI Migration**:

```bash
$ specify plugin update security-scanner

Updates available:
  security-scanner: 1.2.0 → 2.0.0 (major)

⚠️  Major version update detected. Changes:
  • Config schema changed (migration available)
  • Removed: --legacy-mode flag
  • New: --scan-mode option

View full changelog? [y/N]: y

Run migration? [y/N]: y

[1/3] Backing up current config...
[2/3] Running migration 1.2.0 → 2.0.0...
      ✓ Config migrated: severity_threshold → severity.threshold
[3/3] Installing security-scanner@2.0.0...

✓ Update complete

Review migrated config:
  cat .specify/plugins/security-scanner/config.yaml
```

---

## 12. Testing and Quality Gates

### 12.1 Plugin Testing Framework

```bash
# Run plugin tests
$ specify plugin test

Running tests for: security-scanner

tests/test_commands.py
  ✓ test_security_scan_basic (0.5s)
  ✓ test_security_scan_with_severity (0.3s)
  ✓ test_security_scan_file_not_found (0.1s)

tests/test_workflows.py
  ✓ test_pre_implement_hook (0.8s)
  ✓ test_post_implement_hook (1.2s)

tests/test_integration.py
  ✓ test_backlog_task_creation (0.4s)
  ✓ test_event_emission (0.2s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Results: 7 passed, 0 failed, 0 skipped
Coverage: 87%
Time: 3.5s
```

### 12.2 Quality Gates for Publishing

Before a plugin can be published to the registry:

| Gate | Requirement |
|------|-------------|
| **Manifest Valid** | `plugin.yaml` passes schema validation |
| **Tests Pass** | All tests pass with `specify plugin test` |
| **Coverage** | Minimum 85% code coverage |
| **No Vulnerabilities** | No known CVEs in dependencies |
| **Signed** | Package signed with valid key |
| **Documentation** | README.md exists with usage examples |
| **License** | Valid OSI-approved license declared |

```bash
$ specify plugin publish

Pre-publish checks:
  ✓ Manifest valid
  ✓ Tests pass (7/7)
  ✓ Coverage: 87% (≥80% required)
  ✓ No vulnerabilities detected
  ✓ Package signed
  ✓ README.md present
  ✓ License: MIT (approved)

All checks passed. Publishing...

Published: security-scanner@1.2.0
  Registry: https://plugins.speckit.dev
  URL: https://plugins.speckit.dev/packages/security-scanner/1.2.0
```

### 12.3 Testing SDK

```python
# tests/test_commands.py
from speckit_sdk.testing import PluginTestCase, mock_context

class TestSecurityScanCommand(PluginTestCase):
    """Test security scan command."""
    
    def test_security_scan_basic(self):
        """Test basic security scan."""
        with mock_context() as ctx:
            # Setup
            ctx.project.create_file("src/auth.py", "password = 'hardcoded'")
            
            # Execute
            from src.commands.security_scan import SecurityScanCommand
            cmd = SecurityScanCommand()
            result = cmd.run(ctx, feature="auth", severity="medium")
            
            # Assert
            assert len(result["findings"]) == 1
            assert result["findings"][0].severity == "high"
            assert "hardcoded" in result["findings"][0].description
            
            # Verify backlog task created
            tasks = ctx.backlog.get_tasks(labels=["security"])
            assert len(tasks) == 1
            assert "hardcoded" in tasks[0].title
    
    def test_security_scan_no_issues(self):
        """Test scan with no findings."""
        with mock_context() as ctx:
            ctx.project.create_file("src/auth.py", "# Clean code")
            
            cmd = SecurityScanCommand()
            result = cmd.run(ctx, feature="auth", severity="medium")
            
            assert len(result["findings"]) == 0
```

---

## 13. Phased Implementation Plan

### Phase 1: MVP (Weeks 1-4)

**Goal**: Core plugin infrastructure with local plugins.

| Task | Description | Estimate |
|------|-------------|----------|
| Plugin manifest schema | Define `plugin.yaml` schema and validator | 3d |
| Plugin loader | Load plugins from `.specify/plugins/` | 4d |
| Extension point registry | Register and invoke extension points | 3d |
| Basic CLI commands | `install`, `list`, `enable`, `disable`, `remove` | 4d |
| Local plugin support | Install from local directory | 2d |
| Documentation | Plugin authoring guide | 2d |

**Deliverables**:
- Users can create local plugins with `plugin.yaml`
- Basic CLI: `specify plugin install ./my-plugin`
- Extension points: `command.register`, `workflow.phase.after`

### Phase 2: Registry and Security (Weeks 5-8)

**Goal**: Public registry and security features.

| Task | Description | Estimate |
|------|-------------|----------|
| Registry API | Build plugin registry service | 5d |
| CLI registry integration | Search, browse, download from registry | 4d |
| Signing and verification | Plugin signing workflow | 4d |
| Capability system | Declare and enforce capabilities | 3d |
| Policy enforcement | Enterprise policy configuration | 3d |
| Telemetry (opt-in) | Basic usage analytics | 2d |

**Deliverables**:
- Public registry at plugins.speckit.dev
- Signed plugins with verification
- Capability-based security

### Phase 3: SDK and Ecosystem (Weeks 9-12)

**Goal**: Full SDK and ecosystem growth.

| Task | Description | Estimate |
|------|-------------|----------|
| Python SDK | `speckit_sdk` package with full API | 5d |
| Testing framework | `specify plugin test` command | 3d |
| Plugin scaffolding | `specify plugin init` command | 2d |
| Example plugins | 5+ official plugins | 5d |
| Quality gates | Automated pre-publish checks | 3d |
| Developer documentation | SDK reference, tutorials | 3d |

**Deliverables**:
- Published `speckit_sdk` package
- Official plugins: security-scanner, jira-sync, slack-notifier, fastapi-stack, ml-squad
- Complete plugin authoring documentation

### Phase 4: Enterprise and Polish (Weeks 13-16)

**Goal**: Enterprise features and polish.

| Task | Description | Estimate |
|------|-------------|----------|
| Enterprise registry | Private registry support | 4d |
| Advanced sandboxing | Enhanced isolation options | 4d |
| Migration system | Version migration framework | 3d |
| Audit logging | Comprehensive audit trails | 2d |
| Performance optimization | Plugin loading, caching | 3d |
| Beta testing | External beta with 10+ users | 4d |

**Deliverables**:
- Enterprise-ready plugin system
- Private registry support
- Production-hardened security

---

## 14. Open Questions and Risks

### Open Questions

| # | Question | Options | Recommendation |
|---|----------|---------|----------------|
| 1 | Should plugins run in-process or subprocess? | In-process (fast), Subprocess (isolated) | Subprocess for v1, in-process option for v2 |
| 2 | How do we handle plugin dependency conflicts? | Fail fast, Virtual environments, Bundled deps | Fail fast with clear error messages |
| 3 | Should we support plugin composition? | Yes (complex), No (simple) | No for v1, add in v2 based on demand |
| 4 | How do we certify plugins? | Manual review, Automated analysis, Both | Automated + manual for certified level |
| 5 | Should stack plugins include full codegen? | Yes (powerful), No (templates only) | Templates + hooks for v1, codegen v2 |

### Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Security vulnerabilities in plugins** | High | Medium | Capability system, signing, sandboxing |
| **Plugin compatibility breaks on core updates** | Medium | High | Compatibility matrix, deprecation policy |
| **Low plugin ecosystem adoption** | Medium | Medium | Official plugins, SDK, documentation |
| **Performance degradation from plugins** | Medium | Low | Lazy loading, caching, timeouts |
| **Registry availability/reliability** | High | Low | CDN, redundancy, fallback to local |

---

## 15. Success Criteria

### Launch Criteria (MVP)

- [ ] 5+ official plugins published and functional
- [ ] Plugin installation works on Linux, macOS, Windows
- [ ] Security: No critical vulnerabilities in plugin system
- [ ] Performance: Plugin loading adds <100ms to startup
- [ ] Documentation: Complete plugin authoring guide
- [ ] Testing: >85% code coverage on plugin host

### 3-Month Success Metrics

| Metric | Target |
|--------|--------|
| Plugins in registry | 25+ |
| Plugin installations (total) | 5,000+ |
| Active plugins per project | 2.5 average |
| Plugin author satisfaction | >4.0/5 |
| Security incidents | 0 critical |

### 6-Month Success Metrics

| Metric | Target |
|--------|--------|
| Plugins in registry | 100+ |
| Community contributors | 20+ |
| Enterprise adoptions | 5+ |
| Third-party integrations | 15+ |
| Plugin system stability | 99.9% uptime |

---

## Appendix A: Plugin Directory Structure

```
my-plugin/
├── plugin.yaml           # Plugin manifest (required)
├── README.md             # Documentation (required)
├── LICENSE               # License file (required)
├── src/
│   ├── __init__.py
│   ├── commands/         # Command implementations
│   │   └── my_command.py
│   ├── workflows/        # Workflow phase handlers
│   │   └── my_workflow.py
│   ├── agents/           # Agent persona definitions
│   │   └── my_agent.md
│   ├── stacks/           # Stack templates
│   │   └── templates/
│   └── integrations/     # Integration connectors
│       └── my_integration.py
├── tests/
│   ├── __init__.py
│   ├── test_commands.py
│   └── test_workflows.py
├── migrations/           # Version migrations
│   └── 1_0_to_2_0.py
└── pyproject.toml        # Python project config
```

---

## Appendix B: Event Reference

| Event | Payload | When Emitted |
|-------|---------|--------------|
| `plugin.installed` | `{plugin, version}` | After plugin installed |
| `plugin.enabled` | `{plugin}` | After plugin enabled |
| `plugin.disabled` | `{plugin}` | After plugin disabled |
| `plugin.removed` | `{plugin}` | After plugin removed |
| `plugin.command.invoked` | `{plugin, command, args}` | Before command runs |
| `plugin.command.completed` | `{plugin, command, result}` | After command completes |
| `plugin.hook.invoked` | `{plugin, hook, event}` | Before hook runs |
| `plugin.hook.completed` | `{plugin, hook, result}` | After hook completes |
| `plugin.error` | `{plugin, error, context}` | On plugin error |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-06 | Architecture Team | Initial design document |

---

*This design document was created as part of the JP Spec Kit Spec-Driven Development process. For questions or feedback, please open an issue in the repository.*
