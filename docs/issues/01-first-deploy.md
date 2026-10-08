# 01: Перший деплой

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Публічний URL відкриває порожній React-дашборд, а FastAPI віддає
API та health check з того самого сервісу. Це перший перевірений наскрізний запуск.

**Blocked by:** None (can start immediately after authorization to implement).

**Status:** ready-for-agent

## Acceptance criteria

- [x] Python 3.12/uv backend і React/TypeScript/Vite frontend мають lockfiles і працюють локально за задокументованими командами.
- [ ] `/healthz` повертає 200 без БД й зовнішніх запитів; порожній `/api/channels` працює з Neon Postgres.
- [x] Offline health/API pytest і frontend TypeScript/build перевірки проходять; жоден тест не потребує ключів чи мережі.
- [x] Є початкова Alembic migration; її запуск проти порожнього PostgreSQL перевірений окремо від offline тестів.
- [ ] Один Docker build містить React і backend; Render Free підключений до публічного репо й обслуговує обидві частини.
- [ ] Публічний URL реально відкритий браузером; API 404 не підміняється React HTML.
- [ ] README містить фактичний URL і перевірені local commands; DB credentials збережені тільки у provider environment.

## Verification

Offline health/API tests, TypeScript check, production frontend build; локальний
контейнер із PostgreSQL (локально або в CI); браузер і HTTP-запит до deployed URL. Хмарні акаунти й
доступи потрібні саме на цьому етапі, а не під час підготовки репозиторію.

## Поточні докази — 2026-10-08

- Python 3.12.2: 4 offline pytest; frontend: 4 tests і TypeScript/production build.
- PostgreSQL 17.6: upgrade до `0001_channels`, current і Alembic check без drift.
- Чистий клон: uv sync, npm ci, migration, запуск backend і Vite proxy.
- Браузер: production UI на 1440 px і 390 px, порожній список із реальної локальної БД.
- [CI](https://github.com/virus231/channel-radar/actions/runs/37794797772): усі 3 jobs успішні; Docker build/start із чистою PostgreSQL та HTTP-перевіркою UI/API/404.
- Code review: Standards — 0 порушень, Spec — 0 дефектів; live acceptance очікує доступів.

Render workspace потребує вибору користувача; Neon integration ще не підключена.
Створення Docker-сервісу потребує входу в Render Dashboard через обмеження інтеграції.
Задача відкрита до Neon/Render deployment і перевірки фактичного URL.
