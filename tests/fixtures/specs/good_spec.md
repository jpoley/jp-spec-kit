# Feature: User Authentication

## Description

Implement secure user authentication using JWT tokens with refresh token support. The system will authenticate users via username/password, issue access and refresh tokens, and provide endpoints for token refresh and revocation.

## User Story

As a user, I want to securely authenticate with the application so that I can access protected resources and maintain my session across multiple requests.

## Acceptance Criteria

1. User can authenticate with valid username/password
2. System issues JWT access token (15 min expiry) and refresh token (7 days)
3. User can refresh access token using valid refresh token
4. User can revoke refresh tokens on logout
5. System returns 401 for invalid/expired tokens
6. Password must meet complexity requirements (8 chars, 1 upper, 1 lower, 1 number)

## Technical Requirements

- Use `pytest` for testing with 80% coverage
- Format code with `ruff` before commit
- Manage dependencies with `uv`
- Use `typer` for CLI commands
- Display results with `rich` library
- All commits must include DCO sign-off (`git commit -s`)

## Implementation Details

Authentication flow:
1. User submits credentials to /auth/login endpoint
2. Server validates against database (bcrypt hashed passwords)
3. Server generates JWT access token (payload: user_id, roles, exp=900s)
4. Server generates refresh token (UUID v4, stored in Redis with 7-day TTL)
5. Return both tokens in response

Token refresh flow:
1. Client sends refresh token to /auth/refresh
2. Server validates token exists in Redis
3. Server generates new access token
4. Return new access token

## Testing Strategy

- Unit tests: Token generation, validation, password hashing
- Integration tests: Full authentication flow end-to-end
- Security tests: Token expiry, invalid credentials, SQL injection
- Performance tests: 1000 requests/sec authentication capacity
