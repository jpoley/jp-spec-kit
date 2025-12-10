# TypeScript Next.js Project Constitution Example

This example shows a customized constitution for a TypeScript Next.js web application.

## Before: Template

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->
```

## After: Customized

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: TypeScript 5.0+
- **Framework**: Next.js 15 (App Router)
- **Package Manager**: pnpm
- **UI Library**: React 18+ with Tailwind CSS
- **State Management**: React Context + Server Actions
- **Runtime**: Node.js 20 LTS
<!-- SECTION:TECH_STACK:END -->

## Quality Standards
<!-- SECTION:QUALITY:BEGIN -->
- Test coverage minimum: 75%
- TypeScript strict mode enabled
- No `any` types in production code
- All React components must have prop types
- Accessibility: WCAG 2.1 Level AA compliance
<!-- SECTION:QUALITY:END -->

## Testing
<!-- SECTION:TESTING:BEGIN -->
- Framework: Jest + React Testing Library
- E2E: Playwright for critical user flows
- Coverage: Jest with 75% threshold
- Component tests for all UI components
- Integration tests for API routes
<!-- SECTION:TESTING:END -->

## Code Quality
<!-- SECTION:CODE_QUALITY:BEGIN -->
- Linter: ESLint with Next.js config
- Formatter: Prettier
- Type checker: TypeScript compiler (strict)
- Pre-commit hooks: Husky + lint-staged
- Bundle analyzer: @next/bundle-analyzer
<!-- SECTION:CODE_QUALITY:END -->

## CI/CD
<!-- SECTION:CICD:BEGIN -->
- Platform: GitHub Actions
- Workflows: test.yml, deploy.yml
- Deploy: Vercel (preview + production)
- Environment variables: Vercel secrets
- Lighthouse CI for performance monitoring
<!-- SECTION:CICD:END -->

## Frontend Standards
<!-- SECTION:FRONTEND:BEGIN -->
- Use Server Components by default
- Client Components only when necessary
- Optimize images with next/image
- Implement loading states and error boundaries
- Follow Next.js routing conventions
- Use Server Actions for mutations
<!-- SECTION:FRONTEND:END -->

## Performance
<!-- SECTION:PERFORMANCE:BEGIN -->
- Lighthouse score minimum: 90 (all categories)
- First Contentful Paint: < 1.5s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Time to Interactive: < 3.5s
<!-- SECTION:PERFORMANCE:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
- Environment variables never in client bundle
- CSP headers configured
- CORS policies defined
- Input sanitization on all forms
- Rate limiting on API routes
- Authentication via NextAuth.js
<!-- SECTION:SECURITY:END -->
```

## repo-facts.md Generated

```yaml
---
detected_at: "2025-12-04T10:30:00"
languages:
  - TypeScript
  - JavaScript
frameworks:
  - Next.js
  - React
  - Tailwind CSS
package_manager: pnpm
ci_cd: GitHub Actions
test_framework: Jest
e2e_framework: Playwright
linter: ESLint
formatter: Prettier
deployment: Vercel
---
```

## Key Customization Points

1. **Technology Stack**: Next.js 15 App Router, pnpm, Tailwind CSS
2. **Quality Standards**: TypeScript strict mode, no `any` types, WCAG compliance
3. **Testing**: Jest for unit/integration, Playwright for E2E
4. **Frontend Standards**: Server Components first, Server Actions for mutations
5. **Performance**: Specific Lighthouse score thresholds
6. **Deployment**: Vercel-specific configuration

## Usage

```bash
# After running /speckit:constitution
specify constitution validate

# Apply customizations from this example
# Edit .specify/memory/constitution.md
# Replace template sections with customized versions
```

## Common Customizations

### API Routes

If your Next.js app includes API routes:

```markdown
## API Standards
<!-- SECTION:API:BEGIN -->
- Use route handlers (app/api/)
- Validate inputs with Zod schemas
- Return consistent error formats
- Implement request logging
- Rate limiting with Upstash Redis
<!-- SECTION:API:END -->
```

### Authentication

If using authentication:

```markdown
## Authentication
<!-- SECTION:AUTH:BEGIN -->
- Provider: NextAuth.js v5
- Session: Database sessions (Prisma)
- Protected routes: Middleware-based
- CSRF protection enabled
<!-- SECTION:AUTH:END -->
```
