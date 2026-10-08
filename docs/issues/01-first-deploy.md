# 01: Перший деплой

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Публічний URL відкриває порожній React-дашборд, а FastAPI віддає
API та health check з того самого сервісу. Це перший перевірений наскрізний запуск.

**Blocked by:** None (can start immediately after authorization to implement).

**Status:** complete

## Acceptance criteria

- [x] Python 3.12/uv backend і React/TypeScript/Vite frontend мають lockfiles і працюють локально за задокументованими командами.
- [x] `/healthz` повертає 200 без БД й зовнішніх запитів; порожній `/api/channels` працює з Neon Postgres.
- [x] Offline health/API pytest і frontend TypeScript/build перевірки проходять; жоден тест не потребує ключів чи мережі.
- [x] Є початкова Alembic migration; її запуск проти порожнього PostgreSQL перевірений окремо від offline тестів.
- [x] Один Docker build містить React і backend; Render Free підключений до публічного репо й обслуговує обидві частини.
- [x] Публічний URL реально відкритий браузером; API 404 не підміняється React HTML.
- [x] README містить фактичний URL і перевірені local commands; DB credentials збережені тільки у provider environment.

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
- Code review: Standards — 0 порушень, Spec — 0 дефектів.

- [Живий застосунок](https://channel-radar-uibp.onrender.com): Render Docker Free,
  Frankfurt, service `srv-db3ugfmb7d7c739mdcug`, deploy `dep-db3ugg6b7d7c739mded0`.
- Render підтвердив Live для commit `5b6b4d68d4e91a35a02fc19f99fa64896b3bf47b`.
- Neon Free: PostgreSQL 17, Frankfurt, project `nameless-fire-16167879`,
  branch `production`, база `channel_radar`. Startup пройшов Alembic migration;
  API читає створену таблицю каналів. SSL credentials збережені в Render environment.
- HTTP: `/healthz` 200 JSON, `/api/channels` 200 `[]`, `/` 200 HTML;
  `/api/missing` і `/assets/missing.js` — 404 JSON.
- Живий UI: порожній стан на 1440 px і 390 px, без горизонтального overflow.
