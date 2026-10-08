# Channel Radar — план розробки на три дні

**Мета:** робочий публічний Telegram-дашборд за вимогами тестового.
**Архітектура:** один FastAPI/React сервіс, Neon Postgres, зовнішній scheduler,
Gemini-дайджест. **Специфікація:** [spec.md](spec.md), GitHub [#1](https://github.com/virus231/channel-radar/issues/1).

Цей план описує наступну реалізацію. Наявність документації, skills і Issues
означає завершення підготовки, а не виконання задач нижче. День 1–3 відлічується
від початку розробки; це не календарний дедлайн, вигаданий із дати документа.

## Порядок роботи

| День | Задача | GitHub | Блокер | Демонстраційний результат |
|---|---|---|---|---|
| 1 | 01. Перший деплой | [#2](https://github.com/virus231/channel-radar/issues/2) | — | Відкривається порожній дашборд і health check |
| 1 | 02. Додавання каналу | [#3](https://github.com/virus231/channel-radar/issues/3) | #2 | Форма додає канал і показує реальні пости |
| 2 | 03. Оновлення й історія | [#4](https://github.com/virus231/channel-radar/issues/4) | #3 | Cron збирає нові пости й нові спостереження |
| 2 | 04. Аналітика | [#5](https://github.com/virus231/channel-radar/issues/5) | #4 | Працюють графіки, період і деталі поста |
| 3 | 05. AI-дайджест | [#6](https://github.com/virus231/channel-radar/issues/6) | #5 | Резюме з темами, посиланнями й кешем |
| 3 | 06. Перевірка здачі | [#7](https://github.com/virus231/channel-radar/issues/7) | #6 | Перевірений URL, доступ, тести й документація |

Кожна задача проходить через потрібні дані, API, UI і тести; код не розділяється
на незалежні «спочатку весь backend, потім весь frontend» етапи. Розклад щільний:
живий URL перевіряється в перший день, а необов’язкові можливості не додаються.

## Перед першою задачею

- Отримати доступ до Render, Neon, cron-job.org і Gemini key через приватні settings;
  ключі не надсилати в Issues і не комітити.
- Прочитати CLAUDE.md, словник, специфікацію й ADR. Skills уже налаштовані.
- Реалізовувати задачі в feature branches, зберігати main придатним до деплою.
- Узгоджені тестові межі: parser, collection/persistence, analytics і digest API.
  Мережа заборонена в pytest; SQLite test storage і in-process transport не
  доводять production PostgreSQL або фактичну доступність провайдерів.

## Кроки реалізації

### 01. Перший деплой

- [ ] Створити `backend/` із FastAPI, uv і Alembic та `frontend/` із Vite/React;
  зафіксувати Python 3.12 і lockfiles. Додати тільки базові channels/model/API.
- [ ] Додати offline test для `/healthz` і порожнього списку каналів; перевірити
  red/green у відповідній задачі, а не вигадувати тести для документації.
- [ ] Зібрати frontend, перевірити TypeScript, додати один Docker build і CI
  для фактично наявних перевірок. Vite proxy працює локально, static SPA — у Docker.
- [ ] Створити Neon/Render Free, перевірити migration на порожній БД, відкрити
  deployed URL. Додати в README лише реально перевірені commands та URL.

### 02. Додавання каналу

- [ ] Зберегти HTML fixtures і написати failing parser tests; реалізувати
  `parse_preview(html, username)` → нормалізовані дані без запису до БД.
- [ ] Реалізувати першу collection operation й POST/GET channels за контрактом;
  перевірити natural keys, null counters і повторний username offline.
- [ ] Додати форму, pending/error/empty стани й polling з UI tests. Один latest
  preview забезпечує початкові дані без архівного backfill.
- [ ] Додати `@durov` через живий UI, виміряти затримку теплого сервісу й
  перевірити дані проти PostgreSQL. Комітити завершений вертикальний зріз.

### 03. Оновлення та історія

- [ ] Розширити той самий collector інкрементальною пагінацією й серіалізацією;
  додати tests повтору спроби, нового часу й багатосторінкового catch-up.
- [ ] Перевірити partial failure/checkpoint і повтор після restart; snapshots
  постів/каналу зберігають історію. Не трактувати collecting у БД як вічний lock.
- [ ] Додати token-protected trigger, health без БД і два зовнішні cron jobs.
  Перевірити 202, відхилення token і фактичне завершення збору.
- [ ] Пройти live два збори та restart, описати cold-start/30-second timeout,
  квоти та межі оновлення старих постів у README.

### 04. Аналітика

- [ ] Написати failing arithmetic/date tests зі значеннями зі специфікації;
  додати запити до збережених даних без HTTP або AI.
- [ ] Реалізувати metrics/posts/detail API, фільтр і pagination; дані графіків
  враховують різницю published_at/observed_at та unknown counters.
- [ ] Додати overview/channel/post routes і графіки; UI tests фільтра й navigation.
- [ ] Перевірити desktop, mobile width, довгі пости, порожній період і reload
  detail route на deployed URL; оновити приклади в README.

### 05. AI-дайджест

- [ ] Додати failing tests для mocked success/cache hit/input change/empty input;
  реалізувати bounded slice і fingerprint за текстами та message IDs.
- [ ] Підключити Gemini лише через backend, перевірити response shape і IDs;
  зберегти cache/generation status та незалежну failure policy.
- [ ] Покрити 429/timeout/invalid IDs і працездатність загального API; додати
  UI generating/error/retry та явне неповне покриття зрізу.
- [ ] Окремо перевірити реальний дайджест, користь резюме й original links;
  задокументувати actual quota і поведінку при помилці.

### 06. Перевірка здачі

- [ ] Виконати повні suites, TypeScript/build, fresh-clone local startup і
  PostgreSQL migration/restart checks; не називати mocked tests live acceptance.
- [ ] Повторити браузерний сценарій із новим каналом, періодом, графіками,
  деталями й дайджестом; перевірити quota meters та cron execution history.
- [ ] Звірити кожну вимогу з таблицею нижче, оновити README/CLAUDE/ADR до фактів,
  перевірити відсутність секретів у файлах та історії Git.
- [ ] Надати рев’юеру доступ до приватного репо, підготувати два посилання,
  3–5 речень про рішення та сценарій дзвінка; закрити Issues після перевірки.

Критерії кожної задачі зберігаються окремо в [issues/](issues/) і GitHub; закривати
задачу тільки після її перевірок. Не створювати додаткових test suites для
оборотних змін документації. Використовувати `implement`/`tdd` для коду та
`code-review` проти базового commit і специфікації перед завершенням зрізу.

## Матриця вимог і перевірок

| Обов’язкова вимога | Задачі | Доказ виконання |
|---|---|---|
| Регулярний інкрементальний збір | #3, #4 | Fixtures пагінації/checkpoint; фактичний scheduler run |
| Ідемпотентність і natural key | #3, #4 | Повтор тієї самої спроби без duplicate posts/snapshots; PostgreSQL check |
| Хмарна БД та історія counters | #2, #4 | Migration на Neon; різні observed_at збережені після restart |
| Додавання каналу з UI | #3 | 202/polling/error tests; реальний новий username у браузері |
| Огляд, графіки, період, пост | #5 | Arithmetic/UTC tests; три deployed routes і mobile-width smoke |
| Змістовний AI й незалежні збої | #6 | Mocked cache/errors; live дайджест із коректними посиланнями |
| Безкоштовний живий деплой | #2, #4, #7 | Публічний URL, cold-start/cron check та актуальні квоти |
| Offline pytest, AI mocked | #2–#7 | Повна suite з мережею, заблокованою pytest-socket, без keys |
| README, CLAUDE.md, 1–3 ADR | #2–#7 | Перевірені instructions/URL та три актуальні ADR |
| Без секретів і придатність до здачі | #7 | Git/artifact check, reviewer access, два посилання й короткий handoff |

## Поточна підготовка

- [x] Збережено вихідні вимоги й затверджену специфікацію.
- [x] Підготовлено план, матрицю перевірок, словник і три ADR.
- [x] Локально встановлено 11 skills із зафіксованою ревізією та ліцензією.
- [x] Налаштовано GitHub tracker та single-context domain docs.
- [x] Опубліковано специфікацію й шість задач із native relationships.
- [ ] Початковий коміт відправлено в приватний GitHub repo й перевірено чистий клон.
