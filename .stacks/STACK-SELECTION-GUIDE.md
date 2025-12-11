# Stack Selection Guide

## Overview

This guide helps project architects and platform engineers choose the right technology stack based on project requirements, team composition, and business constraints. It should be used during the `/flow:plan` workflow to make informed architectural decisions.

## Selection Process

### 1. Identify Project Type

**Question:** What type of application are you building?

- **Web Application** → Continue to Web Application Decision Tree
- **Mobile Application** → Continue to Mobile Application Decision Tree
- **Data/ML Pipeline** → Select: `data-ml-pipeline-python.md`
- **Developer Tool (VS Code)** → Select: `vscode-extension-typescript.md`
- **Browser Extension** → Select: `chrome-extension-typescript.md`
- **System Tray App** → Select: `tray-app-cross-platform.md`

### 2. Web Application Decision Tree

#### Question A: Do you need a backend?

**No Backend Needed:**
- Static website or single-page app with external APIs
- **Recommendation:** Use frontend-only framework (Next.js static export, Vite)

**Backend Needed:** Continue to Question B

#### Question B: What's your primary requirement?

**Type Safety & Unified Language:**
- Team wants same language for frontend and backend
- **Select:** `full-stack-react-typescript.md`
- **Best For:** Rapid development, smaller teams, shared types

**Performance & Scalability:**
- Expecting >10k concurrent users
- Need low latency (<50ms p95)
- Microservices architecture
- **Select:** `react-frontend-go-backend.md`
- **Best For:** High-traffic, cloud-native, performance-critical

**Data Science & ML Integration:**
- ML models in production
- Heavy data processing
- Data analysis features
- **Select:** `react-frontend-python-backend.md`
- **Best For:** Data-driven apps, ML-powered features, data science team

### 3. Mobile Application Decision Tree

#### Question A: What platforms do you need?

**iOS Only:**
- Use native Swift + SwiftUI
- **Consider:** Go backend for high performance

**Android Only:**
- Use native Kotlin + Jetpack Compose
- **Consider:** Go backend for high performance

**Cross-Platform (iOS + Android):**
- Continue to Question B

#### Question B: What's your backend requirement?

**High Performance Backend Needed:**
- Expecting >10k concurrent users
- Real-time features
- Complex backend logic
- **Select:** `mobile-frontend-go-backend.md`

**ML/Data Processing Backend:**
- ML models in production
- Data analysis features
- Python team
- **Select:** `mobile-frontend-python-backend.md`

**Simple Backend:**
- Consider Firebase/Supabase or simple Node.js backend

### 4. Data & ML Pipeline Decision Tree

#### Question: What's your primary use case?

**Data Pipelines (ETL):**
- **Select:** `data-ml-pipeline-python.md`
- **Tools:** Apache Airflow, Prefect, or Dagster

**ML Training & Inference:**
- **Select:** `data-ml-pipeline-python.md`
- **Tools:** MLflow, Kedro, or Metaflow

**Real-time Streaming:**
- **Select:** `data-ml-pipeline-python.md`
- **Tools:** Kafka, Redis Streams, or AWS Kinesis

## Decision Matrix

### Performance Requirements

| Requirement | Recommended Stack |
|------------|-------------------|
| <1k concurrent users | Any stack works |
| 1k-10k concurrent users | Full Stack TypeScript or Python Backend |
| >10k concurrent users | **Go Backend Required** |
| Real-time features | **Go Backend Recommended** |
| Microsecond latency | **Go Backend or lower-level** |

### Team Composition

| Team Profile | Recommended Stack |
|-------------|-------------------|
| Full-stack JS/TS team | Full Stack React TypeScript |
| Backend Go experts | React/Mobile + Go Backend |
| Data science/Python team | Python Backend (FastAPI) |
| Mobile-first team | Mobile + Go/Python Backend |
| Mixed expertise | Full Stack TypeScript (easiest to learn) |

### Project Characteristics

| Characteristic | Recommended Stack |
|---------------|-------------------|
| MVP/Prototype | Full Stack TypeScript or Python Backend |
| ML-powered app | Python Backend |
| High-traffic production | Go Backend |
| Data visualization | Python Backend (Pandas, Plotly) |
| Microservices | Go Backend |
| Monolith | Full Stack TypeScript |

### Development Speed

| Priority | Recommended Stack |
|----------|-------------------|
| Fastest time to market | Full Stack TypeScript |
| Code sharing priority | Full Stack TypeScript |
| Type safety priority | Full Stack TypeScript or Go |
| Ecosystem/libraries | Python Backend |

## Language-Specific Considerations

### When to Choose Go

**Strengths:**
- Exceptional concurrency (goroutines)
- Low latency, high throughput
- Small memory footprint
- Fast compilation
- Cloud-native (Kubernetes, Docker)
- Strong standard library

**Choose Go When:**
- Performance is critical
- High concurrent connections
- Microservices architecture
- Cloud-native deployment
- Systems programming needs
- API gateways/proxies

**References:** `.languages/go/`

### When to Choose Python

**Strengths:**
- Rich data science ecosystem
- ML/AI libraries (TensorFlow, PyTorch, scikit-learn)
- Rapid development
- Data processing (Pandas, NumPy)
- Extensive libraries
- Easy to learn

**Choose Python When:**
- ML/AI integration required
- Data-intensive operations
- Data science team
- Rapid prototyping
- Complex data transformations
- Research-heavy projects

**References:** `.languages/python/`

### When to Choose TypeScript

**Strengths:**
- Full-stack type safety
- Excellent tooling
- Huge ecosystem (npm)
- Code sharing between frontend/backend
- Easy hiring
- Rich UI frameworks

**Choose TypeScript When:**
- Type safety across full stack
- Web application primary target
- Team knows JavaScript
- Need rapid iteration
- Want code sharing
- Modern web features

**References:** `.languages/ts-js/`

## Integration Patterns

### Multi-Stack Projects

Sometimes projects need multiple stacks:

#### Example 1: E-commerce Platform
- **Web Frontend:** React + TypeScript
- **Mobile Apps:** React Native + TypeScript
- **Core API:** Go (high performance)
- **ML Recommendations:** Python microservice
- **Data Pipeline:** Python (Airflow)

#### Example 2: Data Platform
- **Admin Dashboard:** React + TypeScript
- **Backend API:** Python (FastAPI)
- **Data Pipeline:** Python (Airflow)
- **Real-time Processing:** Go service

#### Example 3: SaaS Product
- **Web App:** Full Stack TypeScript (Next.js)
- **Mobile Apps:** React Native
- **Background Jobs:** Go or Python
- **Analytics:** Python

## Red Flags & Warning Signs

### Don't Choose Go If:
- ❌ Team has zero Go experience and tight deadline
- ❌ Prototype/MVP phase (unless team knows Go)
- ❌ Need extensive data science libraries
- ❌ Simple CRUD with low traffic

### Don't Choose Python If:
- ❌ Need ultra-high performance (>10k rps)
- ❌ Real-time gaming or trading system
- ❌ Microsecond latency requirements
- ❌ Minimal memory footprint needed

### Don't Choose Full Stack TypeScript If:
- ❌ CPU-intensive backend operations
- ❌ Need maximum performance
- ❌ Team prefers compiled languages
- ❌ >10k concurrent connections

## Stack Migration Paths

### From Prototype to Production

**Phase 1: MVP (Fastest)**
- Full Stack TypeScript
- Single monolith
- SQLite or PostgreSQL

**Phase 2: Scale (More Users)**
- Separate frontend/backend deployment
- Add caching (Redis)
- Database optimization

**Phase 3: High Scale (>10k users)**
- Migrate critical paths to Go
- Microservices architecture
- Load balancing
- CDN for static assets

### From Monolith to Microservices

1. **Identify bottlenecks** (profiling, monitoring)
2. **Extract high-traffic services** to Go
3. **Keep data pipelines** in Python
4. **Maintain frontend** in TypeScript
5. **Use API gateway** for routing

## Questions to Ask

### Technical Questions

1. What's the expected traffic? (users/requests per second)
2. What's the acceptable latency? (p50, p95, p99)
3. Do we need ML/AI features?
4. Is data processing a core feature?
5. What platforms must we support? (web, iOS, Android)
6. What are the real-time requirements?
7. What's the data scale? (MB, GB, TB, PB)

### Team Questions

1. What languages does the team know best?
2. How large is the team?
3. Can we hire for specific skills?
4. What's the team's learning capacity?
5. Do we have separate frontend/backend teams?

### Business Questions

1. How fast do we need to launch?
2. What's the budget?
3. What's the expected growth?
4. What are the compliance requirements?
5. What's the maintenance plan?
6. What's the scaling timeline?

## Default Recommendations

### Startup MVP
**Recommendation:** `full-stack-react-typescript.md`
- Fastest development
- One team can build everything
- Easy to find developers
- Can scale to moderate traffic

### Enterprise Internal Tool
**Recommendation:** `react-frontend-python-backend.md` (if data-heavy) or `full-stack-react-typescript.md`
- Rapid development
- Good for internal users (<1k concurrent)
- Easy integration with data sources

### High-Traffic Public API
**Recommendation:** `react-frontend-go-backend.md`
- Performance at scale
- Low latency
- Cost-effective at high traffic

### Mobile-First Product
**Recommendation:** `mobile-frontend-go-backend.md`
- Native mobile experience
- Scalable backend
- Push notifications built-in

### Data/ML Platform
**Recommendation:** `data-ml-pipeline-python.md`
- ML/Data science ecosystem
- Rich libraries
- Workflow orchestration

## Validation Checklist

Before finalizing stack selection, validate:

- [ ] Team has required skills or can acquire them
- [ ] Stack meets performance requirements
- [ ] Stack supports all required platforms
- [ ] Stack fits within budget
- [ ] Stack allows meeting timeline
- [ ] Stack has good hiring market
- [ ] Stack has good community support
- [ ] Stack integrates with existing systems
- [ ] Stack meets compliance requirements
- [ ] Stack has clear migration path if needed

## References

All stack definitions are in `.stacks/`:
- `full-stack-react-typescript.md`
- `react-frontend-go-backend.md`
- `mobile-frontend-go-backend.md`
- `react-frontend-python-backend.md`
- `mobile-frontend-python-backend.md`
- `data-ml-pipeline-python.md`
- `vscode-extension-typescript.md`
- `chrome-extension-typescript.md`
- `tray-app-cross-platform.md`

Coding standards by language:
- `.languages/go/` - Go principles and idioms
- `.languages/python/` - Python principles and idioms
- `.languages/ts-js/` - TypeScript/JavaScript principles
- `.languages/mobile/` - Mobile development principles

## Usage in flowspec Workflow

This guide should be consulted during the `/flow:plan` workflow:

1. **Project Architect** uses this guide to recommend stack(s)
2. **Platform Engineer** validates technical feasibility
3. Both agents document the decision rationale in `/flowspec.constitution`
4. Stack choice influences the implementation approach in `/flow:implement`

The selected stack(s) become part of the project's architectural decisions and guide all subsequent development work.
