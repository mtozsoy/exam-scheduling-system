# Repository Guidelines


## Learning First

This project is educational.

Explain every important design decision before implementing it.

Assume the user wants to understand the code rather than simply receive it.

## Project Structure & Module Organization

This repository contains a React client and a FastAPI service.

- `frontend/src/` contains React code and styles; `src/assets/` and `public/` hold static assets.
- `backend/app/` contains the API code. Keep database setup in `db/`, SQLAlchemy mappings in `models/`, and use the existing `api/`, `schemas/`, `crud/`, and `services/` directories as features grow.
- `backend/app/db/migrations/` is Alembic's migration environment.
- `database/` is reserved for database-related source material. The SQL Server schema is the source of truth.

## Build, Test, and Development Commands

Run frontend commands from `frontend/`:

```powershell
npm install          # install client dependencies
npm run dev          # start the Vite development server
npm run build        # type-check and produce a production build
npm run lint         # run Oxlint
```

Run backend commands from `backend/`:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
alembic upgrade head
```

`DATABASE_URL` must be set in a local `.env` file before importing the database module or running migrations. Never commit that file or credentials.

## Coding Style & Naming Conventions

Use TypeScript with 2-space indentation, `PascalCase` components, and `camelCase` functions, props, and variables. Keep styles near components when practical.

Use Python with 4-space indentation, `snake_case` for modules, functions, and fields, and `PascalCase` for classes. Add type annotations to new Python code. Run `npm run lint` and `npm run build` after frontend edits.

SQLAlchemy model attributes may use English names, but must map precisely to the existing SQL Server table and column names (for example, `Ogrenci` and `Ad`). Do not add model fields, constraints, or migrations for columns that are absent from the established schema.

## Testing Guidelines

No automated test framework is currently configured. Add focused tests alongside the relevant application area when introducing a framework; use descriptive names such as `student.test.tsx` or `test_student.py`. Until then, validate client changes with lint/build and manually exercise affected API endpoints.

## Commit & Pull Request Guidelines

This checkout has no Git history available; use concise imperative subjects, such as `Add student list endpoint`. Keep commits narrowly scoped. Pull requests should state intent, affected client/API/database areas, validation run, and include screenshots for UI changes. Link the relevant issue when one exists.

## Collaboration Workflow

Before implementation, agree on a short plan. Change one file at a time, explain the intended edit before writing code, and avoid unnecessary abstraction.

## Git Workflow

- Create a new branch for every feature.
- Never commit directly to main.
- Keep commits small and focused.
- Ask before changing project structure.
## Architecture

Follow a layered architecture.

Request
↓

API
↓

Service

↓

Database

Business logic belongs in services.

Database access belongs in db or services.

Keep routes thin.


## FastAPI

Prefer dependency injection.

Reuse get_db().

Avoid global state.

Keep endpoints RESTful.


## React

Prefer functional components.

Prefer composition over inheritance.

Avoid unnecessary global state.

Keep components small.

## SQLAlchemy

Use SQLAlchemy 2.x style.

Always use mapped_column().

Prefer explicit relationships.

Never create tables automatically.

The SQL Server database already exists.