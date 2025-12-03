---
mode: agent
description: Execute implementation using specialized frontend and backend engineer agents with code review.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Output Artifacts

All artifacts are written to standardized locations:

| Artifact Type | Output Location | Description |
|---------------|-----------------|-------------|
| AC Coverage Report | `./tests/ac-coverage.json` | JSON mapping acceptance criteria to test files |
| Implementation Code | Per project structure | Feature implementation in appropriate directories |
| Test Files | Per project structure | Unit, integration, and e2e tests |

## Feature Naming

The `{feature}` slug is derived from the feature name:
- Convert to lowercase
- Replace spaces with hyphens
- Remove special characters
- Example: "User Authentication" → "user-authentication"

## AC Coverage Report Format

The `./tests/ac-coverage.json` file must follow this structure:

```json
{
  "feature": "user-authentication",
  "generated": "2025-11-30T12:00:00Z",
  "acceptance_criteria": [
    {
      "id": "AC-001",
      "description": "User can log in with email and password",
      "test_files": [
        "tests/unit/auth/test_login.py",
        "tests/integration/test_auth_flow.py"
      ],
      "coverage": "complete"
    },
    {
      "id": "AC-002",
      "description": "Invalid credentials return error",
      "test_files": [
        "tests/unit/auth/test_login.py"
      ],
      "coverage": "partial"
    }
  ]
}
```

Coverage values: `complete`, `partial`, `none`

## Outline

This command executes the implementation workflow using multiple specialized engineering agents:

1. **Frontend Engineer Agent**: React or mobile development
   - Implements user interfaces using React or mobile frameworks
   - Follows UI/UX best practices
   - Ensures responsive and accessible designs
   - Implements client-side state management

2. **Frontend Code Reviewer Agent**: Expert reviews of React or mobile code
   - Conducts thorough code reviews of frontend implementations
   - Ensures code quality and best practices
   - Validates accessibility and performance
   - Provides actionable feedback

3. **Backend Engineer Agent**: CLI, API, middleware development
   - Implements backend services in Go, TypeScript, or Python
   - Develops CLI tools and command interfaces
   - Creates RESTful APIs and GraphQL endpoints
   - Implements middleware and business logic

4. **Backend Code Reviewer Agent**: Expert reviews of backend code
   - Reviews Go, TypeScript, and Python implementations
   - Ensures backend code quality and patterns
   - Validates API contracts and error handling
   - Checks performance and security considerations

5. **AI/ML Engineer Agent**: MLOps and AI engineering
   - Implements machine learning models and pipelines
   - Sets up MLOps infrastructure
   - Integrates AI/ML capabilities into applications
   - Ensures model versioning and monitoring

## Execution Flow

1. Parse user input and load implementation plan

2. **Frontend Implementation**:
   - Dispatch Frontend Engineer agent for UI/mobile development
   - Implement components, pages, and client logic
   - Dispatch Frontend Code Reviewer for quality assurance
   - Address review feedback

3. **Backend Implementation**:
   - Dispatch Backend Engineer agent for services and APIs
   - Implement CLI, API endpoints, and middleware
   - Dispatch Backend Code Reviewer for quality assurance
   - Address review feedback

4. **AI/ML Implementation** (if applicable):
   - Dispatch AI/ML Engineer agent
   - Implement ML models and pipelines
   - Set up MLOps infrastructure
   - Integrate with application systems

5. **Integration**:
   - Coordinate frontend and backend integration
   - Ensure end-to-end functionality
   - Validate complete feature implementation

6. **AC Coverage Generation**:
   - Map all acceptance criteria from PRD to test files
   - Generate `./tests/ac-coverage.json` report
   - Verify all ACs have test coverage

7. **Output**:
   - Fully implemented feature code
   - Frontend and backend implementations
   - AI/ML components (if applicable)
   - Code review reports
   - AC coverage report at `./tests/ac-coverage.json`
   - Integration documentation

## Completion Checklist

Before completing this command, verify:

- [ ] `./tests/` directory exists
- [ ] AC coverage report generated at `./tests/ac-coverage.json`
- [ ] All acceptance criteria from PRD are mapped to tests
- [ ] Test coverage meets project standards (typically >80%)
- [ ] All tests pass successfully
- [ ] Code reviews are complete and feedback addressed
- [ ] Integration testing validates end-to-end functionality
- [ ] Code follows project coding standards and conventions

## Transition Validation

This command transitions workflow state: **"Planned" → "Implemented"**

**Validation Mode**: Configured per project (see `.specify/workflow/transition-validation.yml`)

See task-175 for validation mode implementation details.

## Notes

- This command is a placeholder for future agent implementation
- Full engineer and reviewer agent integration will be completed in a future task
- Coordinates multiple specialist agents for comprehensive implementation

### Post-Completion: Emit Workflow Event

After successfully completing this command, emit the workflow event to trigger any configured hooks:

```bash
# Emit the implement.completed event
specify hooks emit implement.completed \
  --spec-id "$FEATURE_NAME" \
  --task-id "$TASK_ID" \
  -f "src/**/*.{ts,tsx,py,go}"
```

This triggers any configured hooks in `.specify/hooks/hooks.yaml`. Common use cases:
- Auto-run test suites
- Trigger code quality analysis
- Update CI/CD pipelines
- Notify QA team implementation is ready for validation

**Note**: If the `specify` CLI is not available or hooks are not configured, this step can be skipped without affecting the workflow.
