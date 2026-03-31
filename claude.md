# Claude Guidance — Job Tracker

## Project Purpose

A job application tracking system. Users can create and manage job applications,
transition them through a defined status lifecycle, and view their pipeline.

## Stack

- Backend: Python, Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Marshmallow
- Database: PostgreSQL
- Frontend: React + TypeScript
- Testing: pytest

---

## Hard Rules (Never Violate)

1. **Never bypass the state machine.** Status transitions must always go through
   `application_service.transition_status()`. Never update `application.status` directly
   in routes or anywhere outside the service layer.
2. **Never trust raw request data.** All incoming data must be validated through
   Marshmallow schemas before reaching the service or model layer.
3. **Never expose password hashes.** User serialization must never include
   `password_hash`. Schemas are the enforcement point.
4. **Never write raw SQL.** Use SQLAlchemy ORM only. No `db.engine.execute()` or
   `text()` calls unless explicitly approved.
5. **Never silently swallow exceptions.** All errors must surface through the
   centralized error handlers in `errors.py`. No bare `except: pass`.

---

## Architecture Boundaries

Request -> Route -> Schema (validate) -> Service (business logic) -> Model (data)
                                                                          |
                                                                   StatusHistory (audit)

- Routes handle HTTP only: parse request, call service, return response.
- Services own all business logic: state machine, rules, DB writes.
- Models are data definitions only — no business logic in models.
- Schemas are the contract boundary — validate in, serialize out.

---

## State Machine

Valid transitions only:

APPLIED -> SCREENING -> INTERVIEW -> OFFER -> ACCEPTED
                     \             
    REJECTED      REJECTED
APPLIED -> REJECTED (direct withdrawal)

Any other transition must raise a ValueError with a clear message.
The transition and previous state must be recorded in StatusHistory.

---

## What AI Should NOT Do

- Do not add new endpoints without a corresponding schema and service method.
- Do not add fields to models without a migration.
- Do not add convenience direct DB access in routes.
- Do not remove validation to make a feature faster to implement.
- Do not generate tests that mock the service layer away entirely —
  tests must exercise real business logic.

---

## Naming Conventions

- Models: PascalCase (JobApplication, StatusHistory)
- Routes: snake_case, plural nouns (/applications, /auth)
- Services: verb_noun (create_application, transition_status)
- Schemas: PascalCase with suffix (ApplicationCreateSchema, UserLoginSchema)

---

## Tradeoffs Made Intentionally

- Single PostgreSQL DB (no Redis) — scope kept small deliberately.
- No email verification — out of scope for assessment.
- Soft deletes not implemented — hard delete is fine at this scale.
- No pagination on list endpoint initially — can be added as extension.
