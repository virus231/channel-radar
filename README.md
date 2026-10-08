# Channel Radar

**Статус: перша задача розробки — базовий запуск. Публічного URL ще немає.**
Працюють FastAPI, порожній React-огляд і читання каналів із PostgreSQL.
Деплой на Render/Neon очікує налаштування доступів. Додавання каналів, збір,
аналітика, cron jobs і LLM-інтеграція — наступні задачі; MVP ще не завершений.

Живий дашборд аналітики публічних Telegram-каналів: додавання каналу з форми,
інкрементальний збір, історія метрик, перегляд постів і AI-дайджест за період.

## Документація та задачі

- [Вихідне тестове завдання](docs/TEST-TASK.md) — незмінена копія документа вимог.
- [Специфікація MVP](docs/spec.md) — поведінка, дані, API та критерії готовності;
  GitHub [#1](https://github.com/virus231/channel-radar/issues/1).
- [План на три дні](docs/development-plan.md) — порядок шести задач і матриця перевірок.
- [GitHub Issues](https://github.com/virus231/channel-radar/issues) — специфікація
  та шість відкритих задач із залежностями.
- [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md) — межі модулів і правила для агентів.
- [GLOSSARY.md](GLOSSARY.md), [ADR](docs/adr/) — терміни та три прийняті рішення.
- [Skills і ревізія джерела](docs/agents/skills.md) — 11 локальних skills Matt Pocock.

## Як відкрити локально

Репозиторій публічний за рішенням користувача. Для запуску потрібні Git,
Python 3.12, uv, Node.js 22.12+ і окремий PostgreSQL для розробки.

```sh
git clone https://github.com/virus231/channel-radar.git
cd channel-radar
cp .env.example .env
```

Відкрийте цю папку як проєкт у Codex. Skills уже збережені в `.agents/skills`
разом із допоміжними файлами та MIT-ліцензією; глобального встановлення не потрібно.
Вони стають доступними в новому сеансі/наступному ході агента з контекстом проєкту.

У `.env` задайте `DATABASE_URL` для окремої development БД, наприклад
`postgresql://USER:PASSWORD@localhost:5432/channel_radar`. Решта ключів для цього
етапу не потрібна. Production credentials зберігаються тільки в provider settings.
Не вставляйте credentials у Git, Issues чи frontend.

Backend, із кореня репозиторію:

```sh
cd backend
uv sync --frozen
uv run --env-file ../.env alembic upgrade head
uv run --env-file ../.env uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend, у другому терміналі з кореня:

```sh
cd frontend
npm ci
npm run dev
```

Відкрийте адресу, яку виведе Vite (за замовчуванням `http://127.0.0.1:5173`).
Vite передає `/api` до backend. Для перевірки з одного сервісу зупиніть backend,
виконайте `npm run build` у `frontend/` і запустіть backend знову. Зібраний UI
буде доступний на `http://127.0.0.1:8000` разом із `/api/channels` і `/healthz`.
Health не відкриває з’єднання з БД; невідомий API-маршрут повертає JSON 404.

Перевірки з кореня, без `.env`, ключів і зовнішньої мережі:

```sh
cd backend
uv run pytest
cd ../frontend
npm test
npm run build
```

Pytest блокує TCP-з’єднання, використовує SQLite та in-process HTTP transport.
Unix socket дозволений для внутрішньої роботи asyncio. PostgreSQL перевіряється
окремо: `uv run --env-file ../.env alembic upgrade head`, `alembic current` і
`alembic check` у `backend/` (останні дві команди з тим самим `uv run --env-file ../.env`).
CI також збирає Docker і запускає його з чистою PostgreSQL 17, перевіряючи UI/API
з одного origin. CI password — лише тестове значення для тимчасової БД runner.

Docker, із кореня репозиторію, за наявності Docker Engine і доступної PostgreSQL:

```sh
docker build -t channel-radar .
docker run --rm --env-file .env -p 8000:8000 channel-radar
```

У Docker `localhost` означає сам контейнер; задайте адресу БД, доступну контейнеру.
Startup застосовує Alembic migration і запускає один Uvicorn worker.

Перевірено 2026-10-08: 4 offline backend-тести, 4 frontend-тести, TypeScript/build,
міграція на окремій PostgreSQL 17, запуск із чистого клону та Vite proxy.
У браузері перевірено production UI на 1440 px і 390 px без горизонтального
прокручування. [CI](https://github.com/virus231/channel-radar/actions/runs/37794797772)
підтвердив також Docker build/start із PostgreSQL. Neon, Render і публічний URL
ще не перевірені; задача #2 залишається відкритою.

## Модель даних

Postgres зберігатиме канали, пости, часові спостереження й кеш дайджестів.
Пара `(channel_id, message_id)` є природним ключем поста. Перегляди, реакції та
підписники записуються з `observed_at`, тому новий збір зберігає динаміку, а повтор
тієї самої спроби не створює дублікатів. Відсутня метрика лишається `null`.
Деталі: [специфікація](docs/spec.md#дані-та-аналітика), [ADR 0002](docs/adr/0002-natural-key-and-observations.md).

Збір починається з останньої сторінки web-прев’ю та надалі додає нові доступні пости;
повного Telegram-архіву немає. Метрики оновлюються для постів із отриманих сторінок.
Історія починається з першого спостереження сервісом, без вигаданих старих значень.

## AI-рішення

Заплановано український дайджест збережених текстових постів за період через
Gemini `gemini-3.5-flash-lite`: теми, резюме й посилання на використані пости.
Cache fingerprint залежить від текстового входу, а не зміни counters. Обсяг входу
обмежений; неповне покриття явно показується. Timeout/429/невалідна відповідь
впливають тільки на дайджест; дашборд і збір працюють, користувач може повторити
спробу. Деталі: [ADR 0003](docs/adr/0003-gemini-period-digest.md).

## Безкоштовний деплой і його межі

Один Render Free service віддаватиме API й зібраний React, Neon Free — Postgres.
cron-job.org перевірятиме health без БД кожні 10 хвилин і запускатиме захищений
фоновий збір кожні 30 хвилин. На дату плану Render засинає після 15 хвилин без
трафіку, холодний старт може тривати близько хвилини, а зовнішній cron очікує
відповідь не довше 30 секунд. Health-розклад знижує ризик сну; uptime не гарантований.

Render дає спільні 750 free instance hours/workspace/month та додаткові квоти.
Neon Free має 1 GB storage/project і 100 CU-hours/project/month; health не будить
БД. На Render не зберігаємо production дані у локальній SQLite. Render cron jobs
платні, а його Free Postgres діє 30 днів, тому ці варіанти не використовуються.
Джерела й наслідки: [ADR 0001](docs/adr/0001-render-neon-external-schedule.md).
Перед реальним деплоєм повторно перевірити умови й квоти конкретних акаунтів.

## Перевірки та межі MVP

План передбачає pytest без мережі й ключів: HTML fixtures, ідемпотентність,
історію, арифметику та mocked AI. Frontend — TypeScript/build і тести асинхронних
UI-станів. PostgreSQL, scheduler, реальні провайдери й browser acceptance
перевіряються окремо; fixture або mock не є доказом живої інтеграції.

Не плануються auth/roles, microservices, Celery/Redis, платний хостинг, повний
архівний backfill, сотні каналів, порівняння каналів, алерти або `pulse` export.
Це зберігає триденний термін для обов’язкових вимог. Перед здачею рев’юеру потрібно
надати посилання на публічне репо й перевірений live URL.
