---
mode: agent
description: Execute operations workflow using SRE and operations management agents for CICD, DevSecOps, and resilience.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

This command executes the operations workflow using two specialized agents:

1. **SRE Agent**: Expert in CI/CD, Kubernetes, DevSecOps, and Observability
   - Sets up and maintains CI/CD pipelines (GitHub Actions)
   - Manages Kubernetes deployments and orchestration
   - Implements DevSecOps practices
   - Establishes comprehensive observability
   - Monitors system reliability and performance
   - Implements SRE best practices (SLIs, SLOs, SLAs)

2. **Operations Manager Agent**: Manages resilience and human escalations
   - Oversees operational resilience and reliability
   - Manages incident response and escalations
   - Coordinates cross-team operational issues
   - Ensures business continuity
   - **Requires Human Approval** for critical operational decisions
   - Manages operational runbooks and procedures

## Execution Flow

1. Parse user input and understand operational requirements

2. **CI/CD Setup**:
   - Dispatch SRE agent
   - Configure GitHub Actions workflows
   - Set up automated testing pipelines
   - Implement deployment automation
   - Configure release processes

3. **Infrastructure Operations**:
   - Configure Kubernetes clusters and deployments
   - Set up container orchestration
   - Implement auto-scaling and load balancing
   - Configure network policies and security

4. **DevSecOps Implementation**:
   - Integrate security scanning in CI/CD
   - Implement secret management
   - Configure security policies and compliance checks
   - Set up vulnerability scanning

5. **Observability & Monitoring**:
   - Implement logging and tracing
   - Set up metrics collection and dashboards
   - Configure alerting and notifications
   - Establish SLIs, SLOs, and error budgets

6. **Resilience Management**:
   - Dispatch Operations Manager agent
   - Review operational metrics and reliability
   - Identify potential resilience issues
   - Coordinate incident response procedures
   - **Request Human Approval** for critical operational changes
   - Update runbooks and operational documentation

7. **Output**:
   - Configured CI/CD pipelines
   - Kubernetes deployment manifests
   - Observability dashboards and alerts
   - Operational runbooks
   - Resilience and incident response procedures
   - Human approval checkpoints for critical decisions

## Notes

- This command is a placeholder for future agent implementation
- Full SRE and Operations Manager agent integration will be completed in a future task
- Operations Manager requires explicit human approval for critical operational decisions
