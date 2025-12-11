# JP Spec Kit - Claude Code Plugin

A comprehensive Spec-Driven Development (SDD) toolkit designed specifically for Claude Code users. This plugin provides workflow commands, specialized agents, and integrated tools to streamline your entire software development lifecycle.

## 🎯 What This Plugin Provides

### Workflow Commands (6)
Execute complete development workflows with a single command:
- `/flow:specify` - Create comprehensive feature specifications
- `/flow:plan` - Architectural planning and design
- `/flow:research` - Research and business validation
- `/flow:implement` - Frontend + backend implementation with code review
- `/flow:validate` - QA, security, documentation, and release validation
- `/flow:operate` - SRE operations, CI/CD, Kubernetes, and observability

### Specialized Agents (15)
Purpose-built agents for every stage of development:
- **Planning**: Product Manager, Architect, Platform Engineer
- **Research**: Researcher, Business Validator
- **Development**: Frontend Engineer, Backend Engineer, AI/ML Engineer
- **Quality**: Frontend/Backend Code Reviewers, Quality Guardian
- **Security**: Secure-by-Design Engineer
- **Documentation**: Tech Writer
- **Operations**: SRE Agent, Release Manager

### Pre-configured MCP Servers (9)
Integrated tools ready to use:
- **GitHub** - Repository, issues, PRs, workflows
- **Serena** - LSP-grade code understanding
- **Context7** - Version-specific library docs
- **Playwright** - Browser automation and testing
- **Trivy** - Security scanning and SBOM generation
- **Semgrep** - SAST code scanning
- **Figma** - Design integration
- **shadcn-ui** - Component library
- **Chrome DevTools** - Browser inspection

### Multi-Language Support
Language-specific agent personas for:
C, C++, C#, Go, Java, Kotlin, Python, Rust, TypeScript/JavaScript, Dart/Flutter

## 📦 Installation

### Method 1: From GitHub (Recommended)
```bash
# Install directly from GitHub repository
/plugin install jpoley/jp-spec-kit
```

### Method 2: Add Marketplace First
```bash
# Add the marketplace
/plugin marketplace add jpoley/jp-spec-kit

# Then install the plugin
/plugin install jp-spec-kit
```

### Method 3: Local Development
```bash
# Clone the repository
git clone https://github.com/jpoley/jp-spec-kit.git
cd jp-spec-kit

# Install from local path
/plugin install /path/to/jp-spec-kit
```

## 🚀 Quick Start

### 1. Verify Installation
After installing, verify the plugin is working:
```bash
/plugin list
```

You should see `jp-spec-kit` in the list of installed plugins.

### 2. Start a New Feature
Begin with specification:
```bash
/flow:specify Add user authentication with OAuth2
```

### 3. Plan the Architecture
Design the system:
```bash
/flow:plan Design authentication system architecture
```

### 4. Research and Validate
Conduct research if needed:
```bash
/flow:research Evaluate OAuth2 providers and security best practices
```

### 5. Implement
Execute implementation:
```bash
/flow:implement Build OAuth2 authentication system
```

### 6. Validate
Run comprehensive validation:
```bash
/flow:validate Check authentication implementation for security and quality
```

### 7. Operate
Set up operations and monitoring:
```bash
/flow:operate Set up CI/CD pipeline and monitoring for auth service
```

## 📖 Command Details

### /flow:specify
**Purpose**: Create comprehensive Product Requirement Documents (PRDs)
**Agent**: product-requirements-manager-enhanced
**Outputs**:
- Executive summary
- User stories and acceptance criteria
- Functional and non-functional requirements
- Task breakdown for implementation
- Success metrics

**Example**:
```bash
/flow:specify Build a real-time chat feature with presence indicators
```

### /flow:plan
**Purpose**: Architectural planning and system design
**Agents**: software-architect-enhanced, platform-engineer-enhanced
**Outputs**:
- System architecture diagrams
- Component design
- Data models
- API specifications
- Infrastructure requirements

**Example**:
```bash
/flow:plan Design microservices architecture for chat system
```

### /flow:research
**Purpose**: Technical research and business validation
**Agents**: researcher, business-validator
**Outputs**:
- Technology evaluation
- Market analysis
- Competitive analysis
- Risk assessment
- Recommendations

**Example**:
```bash
/flow:research Compare WebSocket vs Server-Sent Events for real-time messaging
```

### /flow:implement
**Purpose**: Full-stack implementation with code review
**Agents**: frontend-engineer, backend-engineer, frontend-code-reviewer, backend-code-reviewer
**Outputs**:
- Production-ready code
- Unit and integration tests
- Code review reports
- Implementation documentation

**Example**:
```bash
/flow:implement Build chat WebSocket server and React frontend
```

### /flow:validate
**Purpose**: Quality assurance, security, and release readiness
**Agents**: quality-guardian, secure-by-design-engineer, tech-writer, release-manager
**Outputs**:
- Test coverage reports
- Security audit results
- Documentation review
- Release checklist

**Example**:
```bash
/flow:validate Check chat feature for security vulnerabilities and test coverage
```

### /flow:operate
**Purpose**: Operations, CI/CD, and production readiness
**Agent**: sre-agent
**Outputs**:
- GitHub Actions workflows
- Kubernetes manifests
- Monitoring and alerting setup
- Runbooks and operational docs
- Security scanning configuration

**Example**:
```bash
/flow:operate Set up CI/CD pipeline with security scanning for chat service
```

## 🔧 Configuration

### MCP Servers
Some MCP servers require API keys. Set these environment variables:
- `CONTEXT7_API_KEY` - For Context7 server
- `FIGMA_API_KEY` - For Figma server

### Hooks
Pre-commit hook is included but disabled by default. To enable:
1. Edit `.claude/settings.json`
2. Set `hooks.pre-commit.enabled` to `true`

## 📚 Documentation

### Core Documentation
- **Main README**: [../README.md](../README.md)
- **Spec-Driven Development Guide**: [../spec-driven.md](../spec-driven.md)
- **Agent Guide**: [../AGENTS.md](../AGENTS.md)
- **Contributing**: [../CONTRIBUTING.md](../CONTRIBUTING.md)

### Reference Guides
- **Inner Loop Principles**: [../docs/reference/inner-loop.md](../docs/reference/inner-loop.md)
- **Outer Loop Principles**: [../docs/reference/outer-loop.md](../docs/reference/outer-loop.md)
- **Agent Loop Classification**: [../docs/reference/agent-loop-classification.md](../docs/reference/agent-loop-classification.md)

## 🆚 Plugin vs CLI Tool

### When to Use the Plugin (This)
✅ You exclusively use Claude Code
✅ You want the easiest installation
✅ You want automatic updates
✅ You prefer native integration

### When to Use the CLI Tool
✅ You use multiple AI agents (Copilot, Gemini, Cursor, etc.)
✅ You need the full template library
✅ You want GitHub Actions templates
✅ You need to bootstrap new projects

**CLI Installation**:
```bash
pip install specify-cli
# or
uvx specify-cli init my-project
```

Both distributions provide the same core functionality!

## 🔄 Updates

### Check for Updates
```bash
/plugin list
```

### Update the Plugin
```bash
/plugin update jp-spec-kit
```

## 🐛 Troubleshooting

### Plugin Not Found
```bash
# Reinstall from GitHub
/plugin remove jp-spec-kit
/plugin install jpoley/jp-spec-kit
```

### Commands Not Working
Verify the plugin is installed:
```bash
/plugin list
```

If installed but commands don't work, try:
```bash
# Reload Claude Code or restart the session
```

### MCP Servers Not Connecting
Check environment variables are set:
- `CONTEXT7_API_KEY`
- `FIGMA_API_KEY`

### Agent Not Responding
Agents are launched via the Task tool. Ensure:
1. The command includes the agent name correctly
2. You have sufficient context/memory available
3. No other agents are running concurrently (check with `/task list`)

## 💡 Tips and Best Practices

### 1. Follow the Workflow Order
For best results, follow the workflow sequence:
```
specify → plan → research → implement → validate → operate
```

### 2. Provide Context
When using commands, provide clear context:
```bash
/flow:specify [Feature Name]
Context: [Background information, user needs, constraints]
```

### 3. Iterate
Don't hesitate to re-run commands with refinements:
```bash
/flow:plan Update architecture to use event-driven design instead of polling
```

### 4. Use Research for Decisions
Before making major technical decisions:
```bash
/flow:research Evaluate trade-offs between PostgreSQL and MongoDB for chat persistence
```

### 5. Validate Early and Often
Run validation throughout development, not just at the end:
```bash
/flow:validate Check current implementation for security issues
```

## 🤝 Support

### Get Help
- **Issues**: [GitHub Issues](https://github.com/jpoley/jp-spec-kit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jpoley/jp-spec-kit/discussions)
- **Documentation**: [Main Docs](https://github.com/jpoley/jp-spec-kit)

### Contributing
Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- Claude Code Plugin System
- Model Context Protocol (MCP)
- Open source security tools (Trivy, Semgrep)
- Cloud Native Computing Foundation tools (Kubernetes, Prometheus, etc.)

---

**Version**: 0.0.20
**Author**: Jason Poley
**Repository**: [github.com/jpoley/jp-spec-kit](https://github.com/jpoley/jp-spec-kit)
