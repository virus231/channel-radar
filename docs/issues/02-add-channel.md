# 02: Додавання каналу

Part of [#1](https://github.com/virus231/channel-radar/issues/1).

**What to build:** Користувач додає `@durov` у формі, відразу бачить стан збору,
а за секунди на теплому сервісі — збережені пости та counters із Telegram-прев’ю.

**Blocked by:** [#2](https://github.com/virus231/channel-radar/issues/2).

**Status:** complete

## Acceptance criteria

- [x] Username нормалізується; POST повертає 202 до завершення зовнішніх запитів, а повторний username — 200 з існуючим каналом.
- [x] Всі Telegram-запити спрямовані на `t.me/s/<username>` без Bot API, Telegram credentials і довільних URL.
- [x] Парсер нормалізує текст, message IDs, дати, підписників, перегляди й доступні реакції; відсутні counters залишаються null.
- [x] Збереження використовує природний ключ поста й timestamp спостереження; перший збір читає останню сторінку, без повного backfill.
- [x] React polling показує pending/collecting/ready/unavailable/error; порожній публічний канал відрізняється від недоступного.
- [x] Offline fixtures покривають K/M counters, multiline, media-only, ID gaps, missing metrics і сторінку без прев’ю.
- [x] Offline API та UI тести перевіряють повторне додавання, polling і недоступне джерело; текст постів рендериться без raw HTML.
- [x] На deployed URL додано реальний канал і виміряно час до перших даних; обмеження холодного старту описано чесно.

## Verification

Pytest із заблокованою мережею та mocked Telegram transport; Vitest/React Testing
Library з mocked API; реальне додавання `@durov` у deployed браузері й перевірка
збережених даних у PostgreSQL.

## Поточні докази — 2026-10-08

- 11 offline backend tests, 9 frontend tests, TypeScript/production build.
- PostgreSQL: migration `0002_first_collection`, Alembic check без drift.
- Локальний браузер: `@durov`, 20 реальних постів, mobile 390 px без overflow.
- Code review від `3705adb`: Standards — 0 порушень/зауважень; Spec — 0 дефектів коду.
- [Render](https://channel-radar-uibp.onrender.com) підтвердив Live для `f957b02d51460ee0cd4b5307ba924531e9633e02`,
  deploy `dep-db3v4ljl550s73ct866g`; [CI main](https://github.com/virus231/channel-radar/actions/runs/37834056448) — success.
- Через живу форму додано `@durov`: перші 20 постів з’явилися за 3280 ms після
  натискання. Це один замір на теплому сервісі; після сну Render може прокидатися
  50 секунд і довше, тож час не є гарантією для холодного старту.
- API застосунку прочитав із Neon: канал `id=1`, ready, 20 унікальних message IDs, підписники,
  перегляди й доступні реакції; останній успіх `2026-10-08T19:44:49.269357Z`.
- Повторний ` @Durov ` повернув HTTP 200, той самий ID і незмінний час спроби;
  залишився один канал і 20 постів. Браузерний reload також зберіг результат.
- Живий UI перевірено на 1440 px і 390 px без горизонтального прокручування.
