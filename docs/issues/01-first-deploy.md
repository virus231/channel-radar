# 01: Перший деплой

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Публічний URL відкриває порожній React-дашборд, а FastAPI віддає
API та health check з того самого сервісу. Це перший перевірений наскрізний запуск.

**Blocked by:** None (can start immediately after authorization to implement).

**Status:** ready-for-agent

## Acceptance criteria

- [ ] Python 3.12/uv backend і React/TypeScript/Vite frontend мають lockfiles і працюють локально за задокументованими командами.
- [ ] `/healthz` повертає 200 без БД й зовнішніх запитів; порожній `/api/channels` працює з Neon Postgres.
- [ ] Offline health/API pytest і frontend TypeScript/build перевірки проходять; жоден тест не потребує ключів чи мережі.
- [ ] Є початкова Alembic migration; її запуск проти порожнього PostgreSQL перевірений окремо від offline тестів.
- [ ] Один Docker build містить React і backend; Render Free підключений до приватного репо й обслуговує обидві частини.
- [ ] Публічний URL реально відкритий браузером; API 404 не підміняється React HTML.
- [ ] README містить фактичний URL і перевірені local commands; DB credentials збережені тільки у provider environment.

## Verification

Offline health/API tests, TypeScript check, production frontend build; локальний
контейнер із PostgreSQL; браузер і HTTP-запит до deployed URL. Хмарні акаунти й
доступи потрібні саме на цьому етапі, а не під час підготовки репозиторію.
