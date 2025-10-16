# Full Stack React TypeScript Stack

## Overview

A modern full-stack TypeScript architecture using React for frontend and Node.js (Bun/Node) for backend, sharing types and code between client and server.

## Use Cases

- **Ideal For:**
  - Web applications requiring strong type safety across the full stack
  - Teams that want a unified language across frontend and backend
  - Projects needing rapid development with excellent tooling
  - Applications with complex business logic that benefits from shared types
  - Real-time applications using WebSockets
  - Modern SaaS products and web platforms

- **Not Ideal For:**
  - CPU-intensive backend operations (consider Go or Rust)
  - Applications requiring extremely low latency (consider Go)
  - Simple static websites (consider static site generators)
  - Projects with strict memory constraints

## Tech Stack Components

### Frontend
- **Framework:** React 18+
- **Language:** TypeScript 5+
- **Build Tool:** Vite or Next.js
- **State Management:** Zustand, Jotai, or React Query
- **Styling:** Tailwind CSS, CSS Modules, or Styled Components
- **Routing:** React Router or Next.js routing
- **Form Handling:** React Hook Form + Zod validation
- **HTTP Client:** Axios or Fetch with React Query
- **Testing:** Vitest, React Testing Library, Playwright

### Backend
- **Runtime:** Bun (preferred) or Node.js 20+
- **Framework:** Express, Fastify, Hono, or tRPC
- **Language:** TypeScript 5+
- **ORM:** Prisma, Drizzle, or TypeORM
- **Database:** PostgreSQL, MongoDB, or SQLite
- **Validation:** Zod or Yup
- **Authentication:** Passport.js, Auth.js, or custom JWT
- **Testing:** Vitest or Jest
- **API Documentation:** OpenAPI/Swagger or tRPC

### Shared
- **Package Manager:** pnpm or npm workspaces
- **Monorepo:** Turborepo or Nx (optional)
- **Type Sharing:** Shared types package
- **Validation Schemas:** Zod schemas shared between frontend and backend
- **Code Quality:** ESLint, Prettier, TypeScript strict mode

## Architecture Patterns

### Project Structure (Monorepo)

```
project/
├── apps/
│   ├── web/                    # React frontend
│   │   ├── src/
│   │   │   ├── components/     # React components
│   │   │   ├── pages/          # Route pages
│   │   │   ├── hooks/          # Custom hooks
│   │   │   ├── lib/            # Utilities
│   │   │   ├── types/          # Frontend-specific types
│   │   │   └── App.tsx
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── api/                    # Node.js backend
│       ├── src/
│       │   ├── routes/         # API routes
│       │   ├── controllers/    # Request handlers
│       │   ├── services/       # Business logic
│       │   ├── models/         # Data models
│       │   ├── middleware/     # Express middleware
│       │   ├── db/             # Database connection
│       │   └── server.ts
│       ├── package.json
│       └── tsconfig.json
│
├── packages/
│   ├── shared/                 # Shared types and utilities
│   │   ├── src/
│   │   │   ├── types/          # Shared TypeScript types
│   │   │   ├── schemas/        # Zod validation schemas
│   │   │   └── utils/          # Shared utilities
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ui/                     # Shared UI components (optional)
│   │   └── src/
│   │       └── components/
│   │
│   └── config/                 # Shared configs
│       ├── eslint-config/
│       ├── typescript-config/
│       └── prettier-config/
│
├── package.json
├── pnpm-workspace.yaml
├── turbo.json (if using Turborepo)
└── README.md
```

### Key Architectural Decisions

1. **Type Safety First**
   - Strict TypeScript configuration across all packages
   - Shared types between frontend and backend
   - Runtime validation with Zod matching compile-time types

2. **API Design**
   - RESTful APIs with OpenAPI documentation, OR
   - tRPC for end-to-end type safety
   - Versioned APIs (/api/v1)
   - Consistent error handling

3. **State Management**
   - Server state: React Query (data fetching, caching)
   - Client state: Zustand or Jotai (minimal global state)
   - Form state: React Hook Form
   - URL state: React Router params/search

4. **Code Organization**
   - Feature-based folders for related code
   - Separation of concerns (presentation, logic, data)
   - Shared business logic in services
   - Reusable UI components

## Coding Standards

### TypeScript Standards
**Reference:** `.languages/ts-js/principles.md`

Key principles:
- Strict mode enabled
- No implicit any
- Explicit return types for functions
- Prefer interfaces for objects, types for unions
- Use utility types (Partial, Pick, Omit, etc.)

### React Standards

```typescript
// Component structure
import { useState, useEffect } from 'react';
import type { FC, PropsWithChildren } from 'react';

interface UserProfileProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

export const UserProfile: FC<UserProfileProps> = ({ userId, onUpdate }) => {
  // Hooks at the top
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Effects with dependencies
  }, [userId]);

  // Event handlers
  const handleUpdate = async () => {
    // Implementation
  };

  // Early returns for loading/error states
  if (loading) return <LoadingSpinner />;
  if (!user) return <NotFound />;

  // Main render
  return (
    <div>
      {/* JSX */}
    </div>
  );
};
```

### Backend Standards

```typescript
// Route handler with validation
import { Router } from 'express';
import { z } from 'zod';
import { validate } from '../middleware/validate';
import { UserService } from '../services/user';

const router = Router();

const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
  age: z.number().int().positive(),
});

router.post(
  '/users',
  validate(createUserSchema),
  async (req, res, next) => {
    try {
      const userData = req.body;
      const user = await UserService.create(userData);
      res.status(201).json({ data: user });
    } catch (error) {
      next(error);
    }
  }
);

export default router;
```

## Selection Criteria

### Choose This Stack When:

1. **Type Safety is Critical**
   - Need strong typing across frontend and backend
   - Want to catch errors at compile time
   - Require refactoring confidence

2. **Team Composition**
   - Team knows JavaScript/TypeScript well
   - Want single language across the stack
   - Don't have specialized backend engineers

3. **Development Speed**
   - Need rapid prototyping
   - Want to share code between frontend and backend
   - Require excellent IDE support and autocomplete

4. **Project Characteristics**
   - Modern web application
   - Real-time features (WebSockets)
   - CRUD operations with moderate complexity
   - Rapid iteration requirements

### Avoid This Stack When:

1. **Performance Requirements**
   - Need high-performance computing
   - CPU-intensive operations
   - Ultra-low latency requirements
   - High concurrency (>10k concurrent users)

2. **Resource Constraints**
   - Limited memory environment
   - Need minimal resource footprint
   - Serverless with cold start sensitivity

3. **Team Expertise**
   - Team is primarily Go/Python developers
   - No JavaScript/TypeScript experience
   - Prefer traditional OOP patterns

## Best Practices

### 1. Type Safety

```typescript
// Shared types package
// packages/shared/src/types/user.ts
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

export type CreateUserDto = Omit<User, 'id' | 'createdAt'>;
export type UpdateUserDto = Partial<CreateUserDto>;

// Zod schema for runtime validation
export const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
});

// Infer type from schema
export type CreateUserInput = z.infer<typeof createUserSchema>;
```

### 2. API Client with Type Safety

```typescript
// Frontend API client
import type { User, CreateUserDto } from '@project/shared';

class UserApi {
  async getUser(id: string): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  }

  async createUser(data: CreateUserDto): Promise<User> {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create user');
    return response.json();
  }
}

export const userApi = new UserApi();
```

### 3. Error Handling

```typescript
// Backend error handling
export class AppError extends Error {
  constructor(
    public statusCode: number,
    public message: string,
    public isOperational: boolean = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

// Error middleware
export const errorHandler: ErrorRequestHandler = (err, req, res, next) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.message,
    });
  }

  console.error('Unexpected error:', err);
  res.status(500).json({ error: 'Internal server error' });
};
```

### 4. Database Access with Prisma

```typescript
// Backend service layer
import { prisma } from '../db';
import type { CreateUserDto } from '@project/shared';

export class UserService {
  static async create(data: CreateUserDto) {
    return prisma.user.create({
      data: {
        ...data,
        createdAt: new Date(),
      },
    });
  }

  static async findById(id: string) {
    return prisma.user.findUnique({
      where: { id },
    });
  }
}
```

## Testing Strategy

### Frontend Testing

```typescript
// Component test
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('should display user name', async () => {
    render(<UserProfile userId="123" />);

    const name = await screen.findByText('John Doe');
    expect(name).toBeInTheDocument();
  });
});

// E2E test with Playwright
test('user can create account', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="name"]', 'Test User');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL('/dashboard');
});
```

### Backend Testing

```typescript
// API integration test
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../server';

describe('POST /api/users', () => {
  it('should create a new user', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({
        email: 'test@example.com',
        name: 'Test User',
      })
      .expect(201);

    expect(response.body.data).toMatchObject({
      email: 'test@example.com',
      name: 'Test User',
    });
    expect(response.body.data.id).toBeDefined();
  });
});
```

## Deployment Considerations

### Build Process

```json
{
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check"
  }
}
```

### Environment Configuration

```typescript
// Backend config
import { z } from 'zod';

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});

export const config = envSchema.parse(process.env);
```

### Deployment Options

1. **Vercel/Netlify** - Frontend + Serverless API
2. **Railway/Render** - Full stack with database
3. **AWS** - ECS/Lambda + S3 + CloudFront
4. **Docker** - Containerized deployment
5. **Fly.io** - Global edge deployment

## Performance Optimization

### Frontend
- Code splitting with React.lazy
- Memoization with useMemo/useCallback
- Virtual scrolling for long lists
- Image optimization (next/image or similar)
- Bundle analysis and tree shaking

### Backend
- Database query optimization
- Response caching (Redis)
- Connection pooling
- Compression middleware
- Rate limiting

## Security Considerations

- Input validation with Zod on both client and server
- CSRF protection
- Rate limiting
- Helmet.js for security headers
- SQL injection prevention (use ORM)
- XSS protection (React escapes by default)
- Authentication with secure JWT or sessions
- Environment variable management

## Ecosystem Tools

### Development
- TypeScript Language Server
- ESLint + Prettier
- Husky for git hooks
- Commitlint for commit messages
- Turbopack or Vite for fast builds

### Monitoring
- Sentry for error tracking
- LogRocket or FullStory for session replay
- Datadog or New Relic for APM
- PostHog or Mixpanel for analytics

## Learning Resources

- TypeScript Handbook: https://www.typescriptlang.org/docs/
- React Documentation: https://react.dev
- Refer to `.languages/ts-js/` for detailed principles
- tRPC Documentation: https://trpc.io
- Prisma Documentation: https://www.prisma.io

## Migration Path

### From JavaScript
1. Add TypeScript to build process
2. Rename files to .ts/.tsx incrementally
3. Enable strict mode gradually
4. Add types to critical paths first

### To This Stack
1. Set up monorepo structure
2. Create shared types package
3. Migrate frontend to React + TypeScript
4. Migrate backend to Node.js + TypeScript
5. Share types and validation schemas

## Success Metrics

- Type coverage >90%
- Test coverage >80%
- Build time <2 minutes
- First contentful paint <1.5s
- Time to interactive <3s
- API response time <200ms (p95)
- Zero runtime type errors in production
