# Job Tracker

A job application tracking system built with Python/Flask, React, and PostgreSQL. Users can manage job applications through a defined status lifecycle with full audit history.

---

## Quick Start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
flask db upgrade
flask run
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pytest
```

---

## Architecture

```
Request → Route → Schema (validate) → Service (business logic) → Model (data)
                                                                       ↓
                                                              StatusHistory (audit)
```

The system is split into four strict layers, each with a single responsibility:

* **Routes** handle HTTP only: parse the request, call the service, return the response. No business logic lives here.
* **Schemas** (Marshmallow) are the contract boundary — they validate all incoming data and serialize all outgoing data. Nothing reaches a service without passing through a schema.
* **Services** own all business logic: the state machine, transition rules, and database writes.
* **Models** are pure data definitions — no methods, no logic.

---

## Key Technical Decisions

### 1. Enforced State Machine

Job applications move through a fixed lifecycle:

```
APPLIED → SCREENING → INTERVIEW → OFFER → ACCEPTED
       ↘            ↘           ↘       ↘
        REJECTED    REJECTED   REJECTED  REJECTED
APPLIED → REJECTED (direct withdrawal)
```

Every status change goes through `application_service.transition_status()`. No route or model can directly set `application.status`. This is a hard rule enforced by architecture — the state is only reachable through one code path, making invalid transitions impossible rather than just unlikely.

**Tradeoff:** This makes the state machine slightly rigid. Adding a "Withdrawn" status later requires changing `VALID_TRANSITIONS` in one place — which is the intended design.

### 2. Schema-First Validation

All incoming request data is validated through Marshmallow schemas before touching any service or model. Separate schemas exist for creation (`ApplicationCreateSchema`), updates (`ApplicationUpdateSchema`), and status transitions (`StatusTransitionSchema`). This means:

* Invalid data is rejected at the boundary, not deep inside the stack
* Serialization (what goes  *out* ) is also schema-controlled — password hashes never appear in responses by design, not by caution

### 3. StatusHistory as an Audit Trail

Every status change — including the initial `APPLIED` state — is recorded in `StatusHistory` with `from_status`, `to_status`, and `changed_at`. This makes the full lifecycle of an application inspectable. It also means bugs in transitions are diagnosable after the fact.

### 4. JWT Authentication

Stateless JWT auth via `Flask-JWT-Extended`. Tokens are 24 hours, stored in `localStorage` on the frontend (acceptable for an assessment scope; in production, HttpOnly cookies would be preferable to reduce XSS risk).

### 5. Single Database, No Cache

Deliberately kept simple. One PostgreSQL database, no Redis, no background workers. The stats endpoint (`/applications/stats`) does a full table scan per request — fine at this scale, and a documented tradeoff.

---

## API Reference

| Method | Endpoint                     | Description                                     |
| ------ | ---------------------------- | ----------------------------------------------- |
| POST   | `/auth/register`           | Create account, returns JWT                     |
| POST   | `/auth/login`              | Login, returns JWT                              |
| GET    | `/applications`            | List applications (optional `?status=`filter) |
| POST   | `/applications`            | Create application                              |
| GET    | `/applications/:id`        | Get single application with history             |
| PATCH  | `/applications/:id`        | Update fields (company, role, notes, etc.)      |
| PATCH  | `/applications/:id/status` | Transition status (enforced by state machine)   |
| DELETE | `/applications/:id`        | Delete application                              |
| GET    | `/applications/stats`      | Counts by status                                |

---

## Tests

Tests use an in-memory SQLite database and exercise real business logic — no mocking of the service layer. Coverage includes:

* Auth: registration, duplicate email, invalid inputs, login, wrong password
* Applications: creation, validation, auth enforcement
* State machine: valid transitions, invalid transitions, terminal states
* Audit trail: status history is recorded correctly
* Stats endpoint

```bash
pytest -v
```

---

## AI Guidance

The `claude.md` file at the project root contains the constraints used to guide AI code generation throughout this project. Key rules enforced:

* Never bypass the state machine — status updates always go through `transition_status()`
* Never trust raw request data — all input passes through Marshmallow schemas
* Never expose password hashes — schemas are the enforcement point
* Never write raw SQL — SQLAlchemy ORM only
* Never silently swallow exceptions — all errors surface through centralized handlers in `errors.py`
* New endpoints require a corresponding schema and service method
* New model fields require a migration
* Tests must exercise real business logic, not mock the service layer away

AI-generated code was reviewed against these rules before being accepted. The state machine and schema validation patterns in particular were verified manually to ensure they enforce constraints rather than just suggest them.

---

## Known Tradeoffs & Weaknesses

| Area                  | Decision                         | Risk                                                   |
| --------------------- | -------------------------------- | ------------------------------------------------------ |
| Token storage         | `localStorage`                 | XSS exposure; HttpOnly cookies would be safer          |
| Stats query           | Full table scan                  | Slow at scale; add indexed counts or caching           |
| No pagination         | List returns all apps            | Will degrade with large datasets                       |
| No soft delete        | Hard delete only                 | No recovery path; acceptable at this scope             |
| No email verification | Out of scope                     | Not suitable for a multi-tenant production system      |
| SQLite in tests       | Schema differences vs PostgreSQL | Enum handling differs; some edge cases may not surface |

---

## Extending the System

**Adding a new status (e.g. "Withdrawn"):**

1. Add `WITHDRAWN` to `ApplicationStatus` enum in `models/application.py`
2. Update `VALID_TRANSITIONS` in `services/application_service.py`
3. Run `flask db migrate && flask db upgrade`
4. Tests covering the new transition

**Adding pagination:**

1. Accept `page` and `per_page` query params in `routes/applications.py`
2. Apply `.paginate()` to the query in `services/application_service.py`
3. Update `ApplicationResponseSchema` to include pagination metadata

**Adding email notifications:**

1. Hook into `transition_status()` in the service layer — the single transition point means notifications fire reliably for every state change

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── models/          # Data definitions only
│   │   │   ├── user.py
│   │   │   ├── application.py
│   │   │   └── status_history.py
│   │   ├── schemas/         # Marshmallow validation + serialization
│   │   │   ├── auth.py
│   │   │   └── application.py
│   │   ├── services/        # Business logic + state machine
│   │   │   ├── auth_service.py
│   │   │   └── application_service.py
│   │   ├── routes/          # HTTP handling only
│   │   │   ├── auth.py
│   │   │   └── applications.py
│   │   ├── errors.py        # Centralized error handlers
│   │   ├── extensions.py    # Flask extensions
│   │   └── config.py
│   ├── migrations/
│   ├── tests/
│   │   ├── test_auth.py
│   │   └── test_applications.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   └── Dashboard.jsx
│       ├── api.js           # Axios instance with JWT interceptor
│       └── App.jsx
└── claude.md                # AI guidance constraints
```
