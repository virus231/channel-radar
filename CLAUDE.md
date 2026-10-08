# Project conventions

## Current stage

This repository contains the approved MVP specification, development plan and
project-local skills. Application implementation and cloud provisioning require
the next development task; preparation alone does not complete the test assignment.

Read `docs/spec.md` before implementation and `docs/development-plan.md` before
choosing a ticket. User instructions take precedence over skills; an approved plan
settles its choices without another setup interview.

## Module boundaries

- Future `backend/app/telegram.py`: Telegram preview HTTP access and HTML parsing.
  Parsing accepts HTML and produces normalized data; it does not write to storage.
- Future `backend/app/collection.py`: incremental collection, persistence and source
  health. The first collection and scheduled collection use the same operation.
- Future `backend/app/analytics.py`: queries and arithmetic over stored observations.
  It never fetches Telegram or calls the LLM.
- Future `backend/app/digests.py`: bounded input selection, Gemini calls and digest
  cache. LLM failures remain local to the digest operation.
- Future `backend/app/models.py` and Alembic migrations own the SQLAlchemy data model;
  FastAPI routes expose it through response models, not ORM objects.
- Future `frontend/src/`: React rendering, navigation and API requests. It receives
  normalized data; collection, analytics arithmetic and provider secrets stay on
  the backend. Vite development proxies `/api`; production uses one origin.

## Execution and verification

- Keep one application and one deployment; use normal functions and modules before
  adding abstractions. Build only the selected ticket's acceptance criteria.
- Preserve collected observations. The natural post key is `(channel_id, message_id)`;
  retries of one observation must not duplicate it. Unknown counters stay `null`.
- Validate usernames, Telegram HTML and LLM responses at their system boundaries.
- Pytest runs without network or credentials: local HTML fixtures, in-process API
  transport and a temporary SQLite database. Telegram/Gemini requests are mocked.
  Production PostgreSQL and live browser acceptance are separate checks.
- No runtime dependency files or application code exist yet. Add and lock them in
  the first implementation ticket; document commands when they actually run.
- Use `.env.example` as the configuration inventory. Keep real values in ignored
  local environment files or provider settings, never in issues, logs or frontend.

## Agent skills

### Issue tracker

Specs and tickets live in `virus231/channel-radar` GitHub Issues. See
`docs/agents/issue-tracker.md` for publication, dependencies and status conventions.

### Domain docs

Single context: root `GLOSSARY.md` and `docs/adr/`. See `docs/agents/domain.md`.

### Installed skills

Use the project-local copies in `.agents/skills`; source and exact revision are
recorded in `docs/agents/skills.md`. Upstream skills are unmodified.
