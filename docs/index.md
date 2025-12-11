# Flowspec

![Flowspec Logo](media/flowspec.png)

*Specification-driven development for AI-augmented teams.*

**An effort to allow organizations to focus on product scenarios rather than writing undifferentiated code with the help of Spec-Driven Development.**

## What is Spec-Driven Development?

Spec-Driven Development **flips the script** on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: **specifications become executable**, directly generating working implementations rather than just guiding them.

## Getting Started

- [Installation Guide](installation.md)
- [Quick Start Guide](quickstart.md)
- [Local Development](local-development.md)

## Workflow Configuration

Customize and extend the Spec-Driven Development workflow to match your organization's needs.

### Understanding Workflows

- [Workflow Architecture](guides/workflow-architecture.md) - Overall workflow system design and components
- [JP Spec Workflow Guide](guides/flowspec-workflow-guide.md) - Comprehensive guide to the workflow system
- [Workflow State Mapping](guides/workflow-state-mapping.md) - How workflow states map to backlog task states

### Customization

- [Workflow Customization Guide](guides/workflow-customization.md) - How to modify and extend workflows
- [Workflow Troubleshooting](guides/workflow-troubleshooting.md) - Common issues and solutions

### Examples

- [Minimal Workflow](examples/workflows/minimal-workflow.md) - Simple two-phase workflow (specify + implement)
- [Security Audit Workflow](examples/workflows/security-audit-workflow.md) - Extended workflow with security audit phase
- [Parallel Workflows](examples/workflows/parallel-workflows.md) - Multiple feature tracks running in parallel
- [Custom Agents Workflow](examples/workflows/custom-agents-workflow.md) - Adding organization-specific agents

### Reference

- [Workflow Schema](reference/workflow-schema.md) - Complete schema reference for flowspec_workflow.yml
- [Workflow Schema Validation](reference/workflow-schema-validation.md) - Validation rules and constraints
- [Workflow Artifact Flow](reference/workflow-artifact-flow.md) - How artifacts flow between workflow phases
- [Workflow Step Principles](reference/workflow-step-principles.md) - Design principles for workflow steps

## Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "_what_" before the "_how_"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## Development Phases

| Phase | Focus | Key Activities |
|-------|-------|----------------|
| **0-to-1 Development** ("Greenfield") | Generate from scratch | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration** | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul> |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul> |

## Experimental Goals

Our research and experimentation focus on:

### Technology Independence
- Create applications using diverse technology stacks
- Validate the hypothesis that Spec-Driven Development is a process not tied to specific technologies, programming languages, or frameworks

### Enterprise Constraints
- Demonstrate mission-critical application development
- Incorporate organizational constraints (cloud providers, tech stacks, engineering practices)
- Support enterprise design systems and compliance requirements

### User-Centric Development
- Build applications for different user cohorts and preferences
- Support various development approaches (from vibe-coding to AI-native development)

### Creative & Iterative Processes
- Validate the concept of parallel implementation exploration
- Provide robust iterative feature development workflows
- Extend processes to handle upgrades and modernization tasks

## Contributing

Please see our [Contributing Guide](CONTRIBUTING.md) for information on how to contribute to this project.

## Support

For support, please check our [Support Guide](SUPPORT.md) or open an issue on [GitHub](https://github.com/jpoley/flowspec/issues).

