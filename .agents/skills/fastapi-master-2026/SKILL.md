---
name: fastapi-master-2026
description: "Production-ready FastAPI Clean Architecture 2026: Service-Oriented, Async-First backend with SQLAlchemy 2.0, Pydantic V2, Redis caching, WebSockets, and JWT security. Optimized for high-load delivery/marketplace apps."
risk: safe
source: custom
date_added: "2026-04-27"
---

# ⚡ FastAPI Master Architecture Standard 2026

Production-ready FastAPI backend using Clean Architecture principles:
Service-Oriented design, 100% Async/Await, Pydantic V2 validation, SQLAlchemy 2.0
with full Async support, Redis caching, WebSocket real-time tracking, and JWT security.
Engineered for high-load delivery and marketplace applications.

## Use this skill when

- Designing or scaffolding a new FastAPI backend module or feature
- Creating API endpoints (router), business logic (service), database models, or schemas
- Implementing authentication and authorization (JWT, OAuth2)
- Setting up async database access with SQLAlchemy 2.0
- Building real-time features with WebSockets (e.g., driver location tracking)
- Adding Redis caching to list/detail endpoints
- Implementing background tasks (email, push notification, image processing)
- Handling global error responses and structured logging
- Designing wallet, payment, or transaction flows
- Reviewing backend code for architectural compliance

## Do not use this skill when

- The task is unrelated to Python or FastAPI
- You are working on a frontend, mobile app, or infrastructure task
- The project uses Flask, Django, or another Python framework

## Workflow: Order of Operations (MANDATORY)

When creating any new API feature, **always follow this order**:

1. **Schema first** → `/schemas/{module}.py` (Pydantic V2 Request/Response models)
2. **Model second** → `/models/{module}.py` (SQLAlchemy 2.0 Declarative Mapping)
3. **Service third** → `/services/{module}.py` (Business Logic, DB calls, caching)
4. **Router last** → `/api/v1/{module}.py` (Thin endpoint layer only)

> The Router MUST NOT contain business logic. It only calls the Service.

## Directory Structure (Strict Enforcement)

```
backend/
└── app/
    ├── api/
    │   ├── v1/                  # Versioned REST endpoints (thin routers only)
    │   │   ├── auth.py
    │   │   ├── orders.py
    │   │   ├── wallet.py
    │   │   └── restaurants.py
    │   └── ws/                  # WebSocket endpoints (real-time features)
    │       └── tracking.py
    ├── core/
    │   ├── config.py            # Pydantic BaseSettings (env vars)
    │   ├── security.py          # JWT encode/decode, password hashing
    │   ├── logging.py           # Structured JSON logging
    │   └── dependencies.py      # Shared FastAPI Depends() factories
    ├── models/
    │   └── *.py                 # SQLAlchemy 2.0 Declarative ORM models
    ├── schemas/
    │   └── *.py                 # Pydantic V2 Request / Response / Internal models
    ├── services/
    │   └── *.py                 # ALL business logic lives here
    ├── db/
    │   ├── session.py           # Async SQLAlchemy engine + session factory
    │   └── base.py              # Declarative Base
    ├── cache/
    │   └── redis.py             # Redis client + cache decorator
    └── main.py                  # FastAPI app factory, lifespan, global handlers
```

## Coding Standards

- **Strict Typing**: Use `typing` everywhere (`Optional`, `Annotated`, `Sequence`). Never use bare `dict`.
- **Async/Await**: 100% of DB IO and external HTTP calls must use `await`.
- **Dependency Injection**: Always use `Annotated[AsyncSession, Depends(get_db)]`.
- **Pydantic V2**: Use `model_config = ConfigDict(from_attributes=True)`. Use `field_validator` for business rules.
- **Schema Separation**: Distinct `CreateRequest`, `UpdateRequest`, `PublicResponse`, `InternalModel` classes per entity.

## Agent Instructions (Active Rules)

- **NEVER put DB queries or business logic in a Router file.**
- **ALWAYS generate Schema → Model → Service → Router in that order.**
- **ALWAYS check that Pydantic field types match SQLAlchemy column types.**
- **ALWAYS use `async def` for service methods that touch the database.**
- **ALWAYS wrap Router logic in `try/except`** to prevent unhandled runtime crashes. Catch `HTTPException` and re-raise, catch general `Exception`, log it with `logger.error(..., exc_info=True)`, and raise a generic 500 `HTTPException`.
- **ALWAYS wrap Service methods in `try/except`** with mandatory `await self._db.rollback()` on failure before re-raising or logging.
- **ALWAYS use structured Error Codes** (e.g., `USERNAME_TAKEN`, `INVALID_OTP`) instead of plain text messages in `HTTPException` detail. This allows the frontend to perform multi-language translation.
- **NEVER leak internal database error messages** to the client; always return sanitized error details.

## Resources

- `resources/implementation-playbook.md` for complete code patterns, examples, and checklists.

## Limitations

- Use this skill only for FastAPI Python backends.
- Do not apply these patterns to other frameworks without adaptation.
- Stop and ask for clarification if the module scope, DB schema, or auth strategy is unclear.
