# Technology Stack Catalog

## Overview

This directory contains comprehensive technology stack definitions for various types of software projects. Each stack includes architecture patterns, coding standards, best practices, and selection criteria to guide implementation decisions during the `/flow:plan` and `/flow:implement` workflows.

## Available Stacks

### Web Applications

#### [Full Stack React TypeScript](./full-stack-react-typescript.md)
Modern full-stack TypeScript using React frontend + Node.js/Bun backend
- **Languages:** TypeScript (frontend & backend)
- **Use Cases:** Web apps, SaaS products, rapid development
- **Team:** Full-stack JavaScript/TypeScript developers

#### [React Frontend + Go Backend](./react-frontend-go-backend.md)
High-performance web stack with React frontend + Go backend
- **Languages:** TypeScript (frontend), Go (backend)
- **Use Cases:** High-traffic apps, microservices, cloud-native
- **Team:** Frontend developers + Go backend engineers

#### [React Frontend + Python Backend](./react-frontend-python-backend.md)
Data-driven web stack with React frontend + Python backend
- **Languages:** TypeScript (frontend), Python (backend)
- **Use Cases:** Data-heavy apps, ML-powered features, analytics
- **Team:** Frontend developers + Python/data science team

### Mobile Applications

#### [Mobile Frontend + Go Backend](./mobile-frontend-go-backend.md)
Cross-platform mobile with React Native/Native + Go backend
- **Languages:** TypeScript/Swift/Kotlin (mobile), Go (backend)
- **Use Cases:** Mobile-first products, high-performance backends
- **Team:** Mobile developers + Go backend engineers

#### [Mobile Frontend + Python Backend](./mobile-frontend-python-backend.md)
Mobile apps with ML features using Python backend
- **Languages:** TypeScript/Swift/Kotlin (mobile), Python (backend)
- **Use Cases:** ML-powered mobile apps, data-driven features
- **Team:** Mobile developers + Python/data science team

### Data & ML

#### [Data / ML Pipeline - Python](./data-ml-pipeline-python.md)
Python-based data pipelines, ETL, and ML workflows
- **Language:** Python
- **Use Cases:** Data pipelines, ML training, ETL, analytics
- **Team:** Data engineers, data scientists, ML engineers

### Developer Tools

#### [VS Code Extension - TypeScript](./vscode-extension-typescript.md)
VS Code extensions using TypeScript
- **Language:** TypeScript
- **Use Cases:** Developer productivity tools, language support, linters
- **Team:** Frontend/TypeScript developers

#### [Chrome Extension - TypeScript](./chrome-extension-typescript.md)
Chrome browser extensions using TypeScript
- **Language:** TypeScript
- **Use Cases:** Browser tools, content modifiers, productivity apps
- **Team:** Frontend/TypeScript developers

### Desktop Applications

#### [Tray App - Cross Platform](./tray-app-cross-platform.md)
System tray/menu bar applications for Windows & macOS
- **Languages:** TypeScript (Electron/Tauri), Go, Swift, C#
- **Use Cases:** Background utilities, system monitors, quick-access tools
- **Team:** Depends on chosen platform

## Stack Selection

### Quick Selection Guide

**Start here:** [STACK-SELECTION-GUIDE.md](./STACK-SELECTION-GUIDE.md)

The selection guide provides:
- Decision trees for choosing the right stack
- Performance requirement matrices
- Team composition guidance
- Project characteristic matching
- Migration paths

### Selection Process

1. **Identify Project Type** (web, mobile, data pipeline, tool)
2. **Determine Requirements** (performance, scale, features)
3. **Assess Team** (skills, size, learning capacity)
4. **Consider Constraints** (timeline, budget, compliance)
5. **Choose Stack** using the selection guide
6. **Validate Decision** with architects and engineers

## Coding Standards by Language

Each stack references language-specific coding standards in `.languages/`:

- **Go:** `.languages/go/` - Go philosophy, idioms, patterns
- **Python:** `.languages/python/principles.md` - Python principles (Zen of Python, idioms)
- **TypeScript/JavaScript:** `.languages/ts-js/principles.md` - TS/JS principles and patterns
- **Mobile:** `.languages/mobile/` - iOS, Android, React Native principles
- **Swift:** `.languages/mobile/` - iOS development patterns
- **Kotlin:** `.languages/mobile/` - Android development patterns

## Integration with flowspec Workflow

These stacks are used during the `/flow:plan` workflow:

### 1. Specification Phase (`/flow:specify`)
- PM defines requirements
- Identifies general application type

### 2. Planning Phase (`/flow:plan`)
- **Project Architect** consults STACK-SELECTION-GUIDE.md
- Recommends appropriate stack(s) based on:
  - Requirements from `/speckit.tasks`
  - Team composition
  - Performance needs
  - Scalability requirements
- **Platform Engineer** validates:
  - Technical feasibility
  - Infrastructure requirements
  - Deployment strategy
- Both agents document stack decision in `/flowspec.constitution`

### 3. Implementation Phase (`/flow:implement`)
- Engineers follow the chosen stack documentation
- Apply language-specific coding standards
- Use architectural patterns from stack definition
- Reference best practices and examples

## Stack Evolution

Stacks will improve over time based on:
- New technology releases
- Community best practices
- Team learnings
- Performance benchmarks
- Security updates

## File Naming Convention

Stack files follow this naming pattern:
- `{frontend}-{backend}.md` for full-stack applications
- `{application-type}-{language}.md` for specialized stacks
- `STACK-SELECTION-GUIDE.md` for the selection guide
- `README.md` (this file) for catalog overview

## Contributing to Stacks

When updating stack definitions:

1. **Keep Consistent Structure:**
   - Overview
   - Use Cases (Ideal For / Not Ideal For)
   - Tech Stack Components
   - Architecture Patterns
   - Coding Standards (with references)
   - Selection Criteria
   - Best Practices
   - Testing Strategy
   - Deployment
   - Learning Resources

2. **Reference Language Standards:**
   - Always reference `.languages/` for detailed coding standards
   - Don't duplicate language-specific content

3. **Include Real Examples:**
   - Code samples should be production-ready
   - Show best practices, not just syntax
   - Include error handling and edge cases

4. **Update Selection Guide:**
   - Add new stack to decision trees
   - Update matrices and tables
   - Document when to choose the new stack

## Summary

This catalog provides:
- ✅ **10 comprehensive stack definitions**
- ✅ **Clear selection criteria** for each
- ✅ **Architecture patterns** and project structures
- ✅ **Best practices** and code examples
- ✅ **Integration** with flowspec workflow
- ✅ **References** to language-specific standards

For any questions about stack selection, consult the [STACK-SELECTION-GUIDE.md](./STACK-SELECTION-GUIDE.md) or reach out to your project architect or platform engineer.
