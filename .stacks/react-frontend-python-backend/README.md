# React Frontend - Python Backend Stack

## Overview

A versatile stack combining React (TypeScript) for the frontend with Python for the backend, ideal for data-driven applications, rapid development, and teams with Python expertise.

## Use Cases

- **Ideal For:**
  - Data-intensive web applications
  - Machine learning-powered applications
  - Data visualization dashboards
  - Admin panels and internal tools
  - API services with complex business logic
  - Applications requiring scientific computing
  - Prototypes and MVPs
  - Teams with strong Python background

- **Not Ideal For:**
  - Ultra-high performance requirements (consider Go/Rust)
  - Real-time applications with >10k concurrent users
  - CPU-bound operations requiring maximum efficiency
  - Applications with strict memory constraints

## Tech Stack Components

### Frontend
- **Framework:** React 18+ with TypeScript
- **Build Tool:** Vite or Next.js
- **State Management:** Zustand, Jotai, or React Query
- **Styling:** Tailwind CSS, Material-UI, or Chakra UI
- **Routing:** React Router
- **Forms:** React Hook Form + Zod
- **HTTP Client:** Axios or Fetch with React Query
- **Testing:** Vitest, React Testing Library, Playwright

### Backend
- **Language:** Python 3.11+
- **Framework:**
  - **FastAPI** (modern, async, automatic docs) - Recommended
  - **Django** + DRF (batteries included, ORM)
  - **Flask** (lightweight, flexible)
- **ORM:** SQLAlchemy, Django ORM, or Tortoise ORM
- **Database:** PostgreSQL, MongoDB, or SQLite
- **Validation:** Pydantic (FastAPI built-in)
- **Authentication:** FastAPI-Users, Django-AllAuth, or custom JWT
- **Task Queue:** Celery with Redis/RabbitMQ
- **Caching:** Redis
- **Testing:** pytest, pytest-asyncio
- **API Documentation:** OpenAPI/Swagger (auto-generated with FastAPI)

### Data & ML
- **Data Processing:** Pandas, NumPy, Polars
- **ML/AI:** scikit-learn, TensorFlow, PyTorch
- **Data Validation:** Pydantic, Great Expectations
- **Visualization:** Plotly, Matplotlib (backend generation)

### Infrastructure
- **ASGI Server:** Uvicorn or Hypercorn
- **WSGI Server:** Gunicorn (for Flask/Django)
- **Process Manager:** Supervisor or systemd
- **Containerization:** Docker, Docker Compose
- **Monitoring:** Sentry, Prometheus, Grafana

## Architecture Patterns

### Project Structure

```
project/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/
│   │   │   └── api-client.ts   # API client
│   │   ├── types/              # TypeScript types
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                    # Python application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app entry
│   │   │
│   │   ├── api/               # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── deps.py        # Dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── users.py   # User endpoints
│   │   │       └── auth.py    # Auth endpoints
│   │   │
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   │
│   │   ├── models/            # Database models
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   │
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   │
│   │   ├── db/                # Database
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   │
│   │   └── utils/             # Utilities
│   │       └── __init__.py
│   │
│   ├── tests/                 # Tests
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   └── test_services/
│   │
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   │
│   ├── pyproject.toml
│   ├── poetry.lock (if using Poetry)
│   └── Dockerfile
│
├── docker-compose.yml
└── README.md
```

### Key Architectural Decisions

1. **Type Safety with Pydantic**
   - Request/response validation
   - Automatic OpenAPI schema generation
   - Runtime type checking
   - Data serialization

2. **Async-First Design**
   - Async route handlers (FastAPI)
   - Async database operations
   - Efficient I/O handling
   - Better concurrent request handling

3. **Dependency Injection**
   - FastAPI's dependency injection system
   - Database session management
   - Authentication dependencies
   - Testable code structure

4. **API Documentation**
   - Auto-generated OpenAPI docs
   - Interactive API explorer (Swagger UI)
   - ReDoc documentation
   - Type-safe client generation

## Coding Standards

### Python Backend Standards
**Reference:** `.languages/python/principles.md`

```python
# app/api/v1/users.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_in: User creation data
        current_user: Currently authenticated user

    Returns:
        Created user

    Raises:
        HTTPException: If user already exists
    """
    user_service = UserService(db)

    # Check if user already exists
    existing_user = await user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    user = await user_service.create(user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """Get user by ID."""
    user_service = UserService(db)
    user = await user_service.get(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[User]:
    """List users with pagination."""
    user_service = UserService(db)
    users = await user_service.list(skip=skip, limit=limit)
    return users
```

### Pydantic Schemas

```python
# app/schemas/user.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # For SQLAlchemy models
```

### React Frontend Standards
**Reference:** `.languages/ts-js/principles.md`

```typescript
// services/api/users.ts
import type { User, CreateUserRequest, UpdateUserRequest } from '@/types/api';

class UserApi {
  private baseURL = import.meta.env.VITE_API_URL;

  async getAll(): Promise<User[]> {
    const response = await fetch(`${this.baseURL}/api/v1/users`);
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
  }

  async getById(id: number): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/users/${id}`);
    if (!response.ok) throw new Error('Failed to fetch user');
    return response.json();
  }

  async create(data: CreateUserRequest): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create user');
    }
    return response.json();
  }

  async update(id: number, data: UpdateUserRequest): Promise<User> {
    const response = await fetch(`${this.baseURL}/api/v1/users/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update user');
    return response.json();
  }
}

export const userApi = new UserApi();
```

## Selection Criteria

### Choose This Stack When:

1. **Data-Centric Applications**
   - Heavy data processing requirements
   - Machine learning integration
   - Scientific computing needs
   - Data analysis and visualization

2. **Team Composition**
   - Team has strong Python expertise
   - Data scientists on the team
   - Rapid development priority
   - Prefer Python ecosystem

3. **Development Speed**
   - MVP or prototype phase
   - Fast iteration required
   - Rich library ecosystem needed
   - Admin tools and internal dashboards

4. **ML/AI Integration**
   - Machine learning models in production
   - Real-time predictions
   - Data pipelines
   - NLP or computer vision features

### Avoid This Stack When:

1. **Performance Critical**
   - Ultra-high throughput required (>10k req/s)
   - Microsecond latency requirements
   - CPU-intensive operations
   - Minimal resource footprint needed

2. **Concurrency Requirements**
   - Extremely high concurrent connections
   - Real-time gaming or trading systems
   - Systems programming needs

3. **Team Constraints**
   - Team lacks Python experience
   - Prefer compiled languages
   - Need strong static typing guarantees

## Best Practices

### 1. Dependency Injection

```python
# app/api/deps.py
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import async_session_maker
from app.models.user import User

security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Get user from database
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user
```

### 2. Background Tasks with Celery

```python
# app/worker/celery_app.py
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


# app/worker/tasks.py
from app.worker.celery_app import celery_app
from app.core.email import send_email


@celery_app.task
def send_welcome_email(user_email: str, user_name: str) -> None:
    """Send welcome email to new user."""
    send_email(
        to=user_email,
        subject="Welcome!",
        body=f"Hello {user_name}, welcome to our platform!",
    )


# Usage in API
from app.worker.tasks import send_welcome_email

@router.post("/users/", response_model=UserResponse)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_service.create(user_in)

    # Send welcome email asynchronously
    send_welcome_email.delay(user.email, user.name)

    return user
```

### 3. Database Migrations with Alembic

```python
# alembic/versions/001_create_users_table.py
"""create users table

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('users')
```

## Testing Strategy

### Backend Testing

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.db.base import Base


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=True,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create test client."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# tests/test_api/test_users.py
@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test creating a user."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
```

## Deployment Considerations

### Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copy application
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Compose

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  celery_worker:
    build: ./backend
    command: celery -A app.worker.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres

volumes:
  postgres_data:
```

## Performance Optimization

### Backend
- Use async/await for I/O operations
- Connection pooling for database
- Redis caching for frequent queries
- Background tasks with Celery
- Response compression (GZip)
- Database query optimization
- Uvicorn with multiple workers

### Frontend
- Code splitting and lazy loading
- React Query for efficient data fetching
- Memoization and optimization
- Image optimization
- CDN for static assets

## Security Considerations

- Input validation with Pydantic
- SQL injection prevention (use ORM)
- CORS configuration
- Rate limiting
- JWT authentication
- Password hashing (bcrypt/argon2)
- HTTPS only
- Security headers
- Environment variable management
- Dependency security scanning

## Learning Resources

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Refer to `.languages/python/principles.md`
- Refer to `.languages/ts-js/principles.md`

## Success Metrics

- API response time <200ms (p95)
- Test coverage >85%
- Type coverage 100% (Pydantic)
- Zero security vulnerabilities
- Uptime >99.9%
- Build time <3 minutes
