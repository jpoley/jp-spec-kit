# JP Flowspec - Plugin Installation Guide

> **Transform your development workflow with Spec-Driven Development**
>
> JP Flowspec is a comprehensive Claude Code plugin that provides specialized agents, workflow commands, and integrated tools for the entire software development lifecycle.

---

## 🚀 Quick Install (Recommended)

The fastest way to get started:

```bash
/plugin install jpoley/flowspec
```

That's it! The plugin will be installed and ready to use immediately.

---

## 📦 Installation Methods

### Method 1: Direct from GitHub (Easiest)

Install directly from the GitHub repository:

```bash
/plugin install jpoley/flowspec
```

**Pros:**
- ✅ Single command installation
- ✅ Automatic updates available
- ✅ Always gets latest version
- ✅ No marketplace setup needed

---

### Method 2: Via Marketplace

If you prefer using the marketplace system:

```bash
# Step 1: Add the marketplace
/plugin marketplace add jpoley/flowspec

# Step 2: Install the plugin
/plugin install flowspec
```

**Pros:**
- ✅ Centralized plugin management
- ✅ Easy to browse available plugins
- ✅ Version control

---

### Method 3: Local Development

For development or testing local changes:

```bash
# Clone the repository
git clone https://github.com/jpoley/flowspec.git
cd flowspec

# Install from local directory
/plugin install /path/to/flowspec
```

**Use this method if:**
- 🔧 You're contributing to the project
- 🔧 Testing custom modifications
- 🔧 Working offline

---

## ✅ Verify Installation

After installation, verify everything is working:

```bash
# List installed plugins
/plugin list
```

You should see `flowspec` in the output.

**Test a command:**

```bash
/flow:specify Build a user authentication system
```

If the command runs without errors, you're all set!

---

## 🎯 What You Get

Once installed, you'll have access to:

### 6 Workflow Commands
- `/flow:specify` - Create feature specifications (PRDs)
- `/flow:plan` - Architectural planning and design
- `/flow:research` - Research and business validation
- `/flow:implement` - Full-stack implementation with code review
- `/flow:validate` - QA, security, and release validation
- `/flow:operate` - SRE operations, CI/CD, Kubernetes

### 15 Specialized Agents
Expert agents for every development phase:
- Product Manager, Architect, Platform Engineer
- Researcher, Business Validator
- Frontend/Backend Engineers, AI/ML Engineer
- Code Reviewers (Frontend/Backend)
- Quality Guardian, Security Engineer
- Tech Writer, Release Manager, SRE Agent

### 9 Pre-configured MCP Servers
Ready-to-use integrations:
- **GitHub** - Repository management
- **Serena** - Code understanding
- **Context7** - Library documentation
- **Playwright** - Browser testing
- **Trivy** - Security scanning
- **Semgrep** - SAST analysis
- **Figma** - Design integration
- **shadcn-ui** - Component library
- **Chrome DevTools** - Browser inspection

### Multi-Language Support
Specialized agent personas for:
C, C++, C#, Go, Java, Kotlin, Python, Rust, TypeScript/JavaScript, Dart/Flutter

---

## 🏃 Quick Start Guide

Follow this 7-step workflow for any new feature:

### 1. **Specify** - Define the Feature
```bash
/flow:specify Add OAuth2 authentication with Google and GitHub providers
```

**Output:** Comprehensive PRD with user stories, requirements, and acceptance criteria

---

### 2. **Plan** - Design the Architecture
```bash
/flow:plan Design authentication system with OAuth2 integration
```

**Output:** System architecture, component design, API specs, data models

---

### 3. **Research** - Validate Decisions (Optional)
```bash
/flow:research Compare OAuth2 libraries and security best practices
```

**Output:** Technology evaluation, recommendations, risk analysis

---

### 4. **Implement** - Build the Feature
```bash
/flow:implement Build OAuth2 authentication with Google and GitHub
```

**Output:** Production code, tests, code review reports

---

### 5. **Validate** - Quality Assurance
```bash
/flow:validate Check authentication implementation for security and quality
```

**Output:** Test coverage, security audit, documentation review

---

### 6. **Operate** - Production Readiness
```bash
/flow:operate Set up CI/CD pipeline and monitoring for auth service
```

**Output:** GitHub Actions workflows, Kubernetes manifests, monitoring setup

---

### 7. **Deploy** - Ship It! 🚢
Use the CI/CD pipeline created in step 6 to deploy to production.

---

## 🔧 Configuration (Optional)

### MCP Server API Keys

Some MCP servers require API keys. Set these as environment variables:

```bash
# Required for Context7 (library docs)
export CONTEXT7_API_KEY="your-key-here"

# Required for Figma integration
export FIGMA_API_KEY="your-key-here"
```

**Don't have these?** The plugin works fine without them! You just won't have access to Context7 and Figma integrations.

---

### Enable Pre-commit Hook (Optional)

The plugin includes a pre-commit hook (disabled by default).

**To enable:**
1. Edit `.claude/settings.json` in your project
2. Set `hooks.pre-commit.enabled` to `true`

```json
{
  "hooks": {
    "pre-commit": {
      "enabled": true,
      "command": "ruff check . && ruff format . && pytest tests/"
    }
  }
}
```

---

## 📖 Usage Examples

### Example 1: Build a REST API

```bash
# Define the API
/flow:specify Build a REST API for a task management system with CRUD operations

# Design the architecture
/flow:plan Design RESTful API with PostgreSQL and Redis caching

# Implement
/flow:implement Build task management REST API with authentication

# Validate
/flow:validate Check API for security, performance, and test coverage

# Set up operations
/flow:operate Create CI/CD pipeline and monitoring for task API
```

---

### Example 2: Add a New Feature to Existing App

```bash
# Research first
/flow:research Evaluate real-time notification solutions (WebSocket vs SSE)

# Specify the feature
/flow:specify Add real-time notifications using WebSocket

# Plan the integration
/flow:plan Design notification system integration with existing architecture

# Implement
/flow:implement Add WebSocket-based real-time notifications

# Validate
/flow:validate Test notification system for reliability and security
```

---

### Example 3: Improve Existing Code

```bash
# Validate current state
/flow:validate Review current authentication implementation

# Research improvements
/flow:research Investigate modern authentication patterns and security best practices

# Plan refactoring
/flow:plan Design improved authentication architecture with MFA support

# Implement
/flow:implement Refactor authentication with multi-factor authentication

# Validate changes
/flow:validate Verify refactored authentication meets security standards
```

---

## 🔄 Updates

### Check for Updates

```bash
/plugin list
```

Look for any update notifications next to `flowspec`.

### Update the Plugin

```bash
/plugin update flowspec
```

Updates are typically non-breaking and include:
- New features
- Bug fixes
- Documentation improvements
- Security patches

---

## 🆘 Troubleshooting

### Plugin Not Found After Installation

**Solution 1: Verify Installation**
```bash
/plugin list
```

If not listed, reinstall:
```bash
/plugin install jpoley/flowspec
```

---

### Commands Not Working

**Problem:** `/flow:specify` shows "command not found"

**Solution 1: Reload Claude Code**
- Restart your Claude Code session
- Try the command again

**Solution 2: Reinstall Plugin**
```bash
/plugin remove flowspec
/plugin install jpoley/flowspec
```

---

### MCP Servers Not Connecting

**Problem:** Error messages about MCP servers

**Solution 1: Check Prerequisites**
- Node.js 18+ installed: `node --version`
- Python 3.11+ installed: `python --version`

**Solution 2: Check API Keys**
```bash
# For Context7
echo $CONTEXT7_API_KEY

# For Figma
echo $FIGMA_API_KEY
```

**Solution 3: Skip Optional Servers**
Most MCP servers work without API keys. Only Context7 and Figma require keys.

---

### Agent Not Responding

**Problem:** Command hangs or doesn't produce output

**Solution 1: Check Active Agents**
```bash
/task list
```

**Solution 2: Provide More Context**
Agents work better with clear, detailed prompts:

❌ Bad: `/flow:implement build auth`
✅ Good: `/flow:implement Build OAuth2 authentication with Google and GitHub providers, including JWT token management and refresh token rotation`

---

### Installation Fails

**Problem:** Error during installation

**Solution 1: Check Network**
Ensure you have internet connection and can access GitHub.

**Solution 2: Try Direct Install**
```bash
/plugin install jpoley/flowspec
```

**Solution 3: Check Claude Code Version**
Requires Claude Code 2.0.0 or higher.

---

## 🆚 Plugin vs CLI Tool

### Should I Use the Plugin or CLI Tool?

| Use the **Plugin** if: | Use the **CLI Tool** if: |
|------------------------|--------------------------|
| ✅ You only use Claude Code | ✅ You use multiple AI tools |
| ✅ You want easiest installation | ✅ You need project templates |
| ✅ You want automatic updates | ✅ You need GitHub Actions templates |
| ✅ You prefer native integration | ✅ You bootstrap many projects |

### Install the CLI Tool

```bash
# Install via pip
pip install flowspec-cli

# Or use uvx (recommended)
uvx flowspec-cli init my-project
```

**Both provide the same core workflow commands!** Choose based on your needs.

---

## 💡 Tips for Success

### 1. Follow the Workflow Order
Best results come from following the natural sequence:
```
specify → plan → research → implement → validate → operate
```

### 2. Provide Rich Context
The more context you provide, the better the output:

```bash
/flow:specify Build a user dashboard

Context:
- Users need to view their activity history
- Should display real-time notifications
- Must support dark mode
- Target load time: < 2 seconds
- Accessibility: WCAG 2.1 AA compliant
```

### 3. Iterate Freely
Don't hesitate to re-run commands with refinements:

```bash
# First pass
/flow:plan Design REST API

# Refine
/flow:plan Update API design to use GraphQL instead of REST
```

### 4. Use Research for Decisions
Before committing to a technology or approach:

```bash
/flow:research Compare PostgreSQL vs MongoDB for time-series data storage
```

### 5. Validate Throughout
Don't wait until the end to validate:

```bash
# After implementing a feature
/flow:validate Check user authentication implementation

# After adding tests
/flow:validate Review test coverage for payment processing module
```

---

## 📚 Additional Resources

### Documentation
- **Plugin README**: `.claude-plugin/README.md` (detailed plugin docs)
- **Main Project**: [github.com/jpoley/flowspec](https://github.com/jpoley/flowspec)
- **Spec-Driven Development**: `spec-driven.md` (methodology guide)
- **Agent Guide**: `AGENTS.md` (agent details)
- **Contributing**: `CONTRIBUTING.md` (contribution guide)

### Reference Guides
- **Inner Loop Principles**: `docs/reference/inner-loop.md`
- **Outer Loop Principles**: `docs/reference/outer-loop.md`
- **Agent Classification**: `docs/reference/agent-loop-classification.md`

### Support
- **Issues**: [GitHub Issues](https://github.com/jpoley/flowspec/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jpoley/flowspec/discussions)

---

## 🎓 Learning Path

### Beginner: Your First Feature

1. **Install the plugin** (see Quick Install above)
2. **Start with specify**: `/flow:specify Add a contact form to the website`
3. **Review the output**: Read the generated PRD
4. **Try plan**: `/flow:plan Design contact form architecture`
5. **Explore other commands** as you get comfortable

### Intermediate: Full Workflow

1. **Complete a feature end-to-end** using all 6 commands
2. **Experiment with different prompts** to see how outputs change
3. **Use research** to evaluate technology choices
4. **Set up operations** for a real project

### Advanced: Custom Workflows

1. **Combine commands** in creative ways
2. **Use agents directly** via the Task tool
3. **Integrate with your existing tools** and processes
4. **Contribute improvements** back to the project

---

## 🤝 Contributing

Love the plugin? Want to help improve it?

1. **Report issues**: [GitHub Issues](https://github.com/jpoley/flowspec/issues)
2. **Suggest features**: [GitHub Discussions](https://github.com/jpoley/flowspec/discussions)
3. **Submit PRs**: See [CONTRIBUTING.md](CONTRIBUTING.md)
4. **Share feedback**: Let us know what's working and what's not!

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🎉 You're Ready!

Installation is complete. Start building with Spec-Driven Development:

```bash
/flow:specify Build something amazing!
```

**Questions?** Check the [troubleshooting section](#-troubleshooting) or [open an issue](https://github.com/jpoley/flowspec/issues).

---

**Version**: 0.0.20
**Last Updated**: 2025-10-16
**Author**: Jason Poley
**Repository**: [github.com/jpoley/flowspec](https://github.com/jpoley/flowspec)
